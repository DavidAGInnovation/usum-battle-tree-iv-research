#!/usr/bin/env python3
"""Enumerate literal ARM stores using the TRAINER_DATA ``ai_bit`` offset.

This is a deliberately conservative *candidate* audit.  In the retail
source, ``MainModule::TRAINER_DATA::ai_bit`` is at offset ``0x1c``.  A literal
``str/strb/strh`` displacement of ``0x1c`` is therefore worth reviewing, but
the displacement alone does not identify the pointee: the same offset occurs
in stack frames and unrelated structures.  The script reports all such
candidates in the extracted CRO code segments and in the raw ExeFS ``.code``
section.  It never silently classifies a candidate as an AI-mask writer.

The output is evidence for the boundary of a whole-binary data-flow proof,
not that proof itself.  Relocations, aliases, copied structures, and the
ARM/Thumb function graph still have to be resolved before a writer can be
declared (or ruled out) as an ``ai_bit`` writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, Cs
from capstone.arm import (
    ARM_INS_STR,
    ARM_INS_STRB,
    ARM_INS_STRBT,
    ARM_INS_STREX,
    ARM_INS_STREXB,
    ARM_INS_STREXH,
    ARM_INS_STRH,
    ARM_INS_STRHT,
    ARM_INS_STRT,
    ARM_OP_MEM,
    ARM_REG_SP,
)


# Capstone exposes aliases for conditional STR instructions through the same
# instruction id.  Keep the mnemonic allow-list broad but reject loads and
# arithmetic instructions explicitly through the id check.
STORE_IDS = {
    ARM_INS_STR,
    ARM_INS_STRB,
    ARM_INS_STRH,
    ARM_INS_STRT,
    ARM_INS_STRBT,
    ARM_INS_STRHT,
    ARM_INS_STREX,
    ARM_INS_STREXB,
    ARM_INS_STREXH,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def cro_code(path: Path) -> tuple[str, bytes]:
    data = path.read_bytes()
    if data[0x80:0x84] != b"CRO0":
        raise ValueError(f"{path}: missing CRO0 header")
    name_offset = u32(data, 0x84)
    end = data.find(b"\0", name_offset)
    name = data[name_offset:end].decode("ascii", "replace")
    offset, size = u32(data, 0xB0), u32(data, 0xB4)
    return name, data[offset : offset + size]


def scan(code: bytes, mode: int, *, limit: int | None = None) -> list[dict[str, object]]:
    md = Cs(CS_ARCH_ARM, mode)
    md.detail = True
    # The main ExeFS section is a stripped mixed code/data image.  Continue
    # across undecodable bytes so a bad decode at one veneer does not make the
    # rest of the candidate sweep silently disappear.
    md.skipdata = True
    rows: list[dict[str, object]] = []
    for ins in md.disasm(code, 0):
        if ins.id not in STORE_IDS or len(ins.operands) < 2:
            continue
        mem = ins.operands[1]
        if mem.type != ARM_OP_MEM or mem.mem.disp != 0x1C:
            continue
        rows.append(
            {
                "offset": ins.address,
                "mnemonic": ins.mnemonic,
                "operands": ins.op_str,
                "stack_base": mem.mem.base == ARM_REG_SP,
                "bytes": ins.bytes.hex(),
            }
        )
        if limit is not None and len(rows) >= limit:
            break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("code", type=Path, help="extracted raw ExeFS .code")
    parser.add_argument("cro_dir", type=Path, help="directory of extracted CRO files")
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    code = args.code.read_bytes()
    rows: list[dict[str, object]] = []

    # The main ExeFS section is mixed ARM/Thumb and stripped.  Both linear
    # sweeps are retained as over-approximations and labelled by mode.
    for mode, label in ((CS_MODE_ARM, "arm"), (CS_MODE_THUMB, "thumb")):
        hits = scan(code, mode, limit=args.limit)
        rows.append(
            {
                "module": ".code",
                "mode": label,
                "code_sha256": sha256(code),
                "code_size": len(code),
                "hits": hits,
                "hit_count": len(hits),
                "stack_base_hits": sum(bool(x["stack_base"]) for x in hits),
                "truncated": args.limit is not None and len(hits) >= args.limit,
            }
        )

    for path in sorted(args.cro_dir.glob("*.cro")):
        name, cro_text = cro_code(path)
        hits = scan(cro_text, CS_MODE_ARM, limit=args.limit)
        rows.append(
            {
                "module": name,
                "file": path.name,
                "mode": "arm",
                "file_sha256": sha256(path.read_bytes()),
                "code_size": len(cro_text),
                "hits": hits,
                "hit_count": len(hits),
                "stack_base_hits": sum(bool(x["stack_base"]) for x in hits),
                "truncated": args.limit is not None and len(hits) >= args.limit,
            }
        )

    result = {
        "field": "MainModule::TRAINER_DATA::ai_bit",
        "offset": "0x1c",
        "mode": "candidate enumeration; not alias-complete",
        "modules": rows,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_path:
        args.json_path.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
