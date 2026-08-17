#!/usr/bin/env python3
"""Enumerate literal ARM stores using source-defined ``ai_bit`` offsets.

This is a deliberately conservative *candidate* audit.  In the retail
source, ``BSP_TRAINER_DATA::CORE_DATA::ai_bit`` is at offset ``0x4`` and
``MainModule::TRAINER_DATA::ai_bit`` is at offset ``0x1c``. A literal
``str/strb/strh`` displacement of either value is therefore worth reviewing,
but the displacement alone does not identify the pointee: both offsets occur
in stack frames and unrelated structures. The script reports all such
candidates in the extracted CRO code segments and in the raw ExeFS ``.code``
section. It never silently classifies a candidate as an AI-mask writer.

The output is evidence for the boundary of a whole-binary data-flow proof,
not that proof itself.  Relocations, aliases, copied structures, and the
ARM/Thumb function graph still have to be resolved before a writer can be
declared (or ruled out) as an ``ai_bit`` writer.
"""

from __future__ import annotations

import argparse
from collections import Counter
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

FIELDS = {
    "BSP_TRAINER_DATA::CORE_DATA::ai_bit": 0x4,
    "MainModule::TRAINER_DATA::ai_bit": 0x1C,
}
FIELD_BY_OFFSET = {offset: name for name, offset in FIELDS.items()}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def cro_metadata(data: bytes) -> dict[str, object]:
    """Decode the relocation-bearing parts of a CRO header.

    CRO segment offsets encode the segment index in their low nibble and the
    byte offset within that segment in the remaining bits.  Keeping the raw
    relocation sites alongside the candidate scan makes it possible to tell
    whether a store is in a relocatable code word, without pretending that a
    relocation alone identifies a C++ object or field.
    """

    def pair(offset: int) -> tuple[int, int]:
        return struct.unpack_from("<II", data, offset)

    if len(data) < 0x138 or data[0x80:0x84] != b"CRO0":
        raise ValueError("invalid CRO header")
    segment_offset, segment_count = pair(0xC8)
    segments: list[dict[str, object]] = []
    for index in range(segment_count):
        offset, size, segment_type = struct.unpack_from(
            "<III", data, segment_offset + index * 12
        )
        segments.append(
            {
                "index": index,
                "offset": offset,
                "size": size,
                "type": segment_type,
            }
        )

    relocations: list[dict[str, object]] = []
    relocation_types: Counter[str] = Counter()
    code_relocations = 0
    invalid_relocations = 0
    relocation_tables = (
        ("import", 0xF8, 0xFC),
        ("internal", 0x128, 0x12C),
        ("unknown", 0x130, 0x134),
    )
    type_names = {
        0: "R_ARM_NONE",
        2: "R_ARM_ABS32",
        3: "R_ARM_REL32",
        10: "R_ARM_THM_PC22",
        28: "R_ARM_CALL",
        29: "R_ARM_JUMP24",
        38: "R_ARM_TARGET1",
        42: "R_ARM_PREL31",
    }
    for table_name, offset_field, count_field in relocation_tables:
        table_offset, table_count = pair(offset_field)
        for index in range(table_count):
            entry_offset = table_offset + index * 12
            if entry_offset + 12 > len(data):
                invalid_relocations += 1
                continue
            output, reloc_type, target_segment, flags, padding, addend = struct.unpack_from(
                "<IBBBB I", data, entry_offset
            )
            segment_index = output & 0xF
            segment_byte_offset = output >> 4
            valid_target = segment_index < len(segments)
            target_file_offset = None
            target_in_code = False
            if valid_target:
                segment = segments[segment_index]
                if segment_byte_offset < int(segment["size"]):
                    target_file_offset = int(segment["offset"]) + segment_byte_offset
                    target_in_code = int(segment["type"]) == 0
                    if target_in_code:
                        code_relocations += 1
                else:
                    invalid_relocations += 1
            else:
                invalid_relocations += 1
            type_name = type_names.get(reloc_type, f"R_ARM_{reloc_type}")
            relocation_types[type_name] += 1
            relocations.append(
                {
                    "table": table_name,
                    "index": index,
                    "output": hex(output),
                    "segment": segment_index,
                    "segment_offset": hex(segment_byte_offset),
                    "type": type_name,
                    "referred_segment": target_segment,
                    "addend": hex(addend),
                    "target_file_offset": target_file_offset,
                    "target_in_code": target_in_code,
                }
            )

    code_offset, code_size = pair(0xB0)
    relocation_file_offsets = {
        int(row["target_file_offset"])
        for row in relocations
        if row["target_file_offset"] is not None
    }
    return {
        "code_offset": code_offset,
        "code_size": code_size,
        "data_offset": u32(data, 0xB8),
        "data_size": u32(data, 0xBC),
        "segment_count": segment_count,
        "segments": segments,
        "relocation_counts": {
            name: u32(data, count_field) for name, _, count_field in relocation_tables
        },
        "relocation_type_counts": dict(sorted(relocation_types.items())),
        "code_relocation_count": code_relocations,
        "invalid_relocation_count": invalid_relocations,
        # Internal use by the scanner; omitted before JSON serialization.
        "_relocation_file_offsets": relocation_file_offsets,
    }


def cro_code(path: Path) -> tuple[str, bytes, dict[str, object]]:
    data = path.read_bytes()
    if data[0x80:0x84] != b"CRO0":
        raise ValueError(f"{path}: missing CRO0 header")
    name_offset = u32(data, 0x84)
    end = data.find(b"\0", name_offset)
    name = data[name_offset:end].decode("ascii", "replace")
    offset, size = u32(data, 0xB0), u32(data, 0xB4)
    return name, data[offset : offset + size], cro_metadata(data)


def scan(
    code: bytes,
    mode: int,
    *,
    limit: int | None = None,
    code_file_offset: int = 0,
    relocation_file_offsets: set[int] | None = None,
) -> list[dict[str, object]]:
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
        if mem.type != ARM_OP_MEM or mem.mem.disp not in FIELD_BY_OFFSET:
            continue
        field = FIELD_BY_OFFSET[mem.mem.disp]
        rows.append(
            {
                "offset": ins.address,
                "displacement": hex(mem.mem.disp),
                "field": field,
                "mnemonic": ins.mnemonic,
                "operands": ins.op_str,
                "stack_base": mem.mem.base == ARM_REG_SP,
                "bytes": ins.bytes.hex(),
                "relocation_at_instruction": (
                    relocation_file_offsets is not None
                    and code_file_offset + ins.address in relocation_file_offsets
                ),
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
                "field_counts": {
                    field: sum(x["field"] == field for x in hits) for field in FIELDS
                },
                "truncated": args.limit is not None and len(hits) >= args.limit,
            }
        )

    for path in sorted(args.cro_dir.glob("*.cro")):
        name, cro_text, metadata = cro_code(path)
        hits = scan(
            cro_text,
            CS_MODE_ARM,
            limit=args.limit,
            code_file_offset=int(metadata["code_offset"]),
            relocation_file_offsets=set(metadata["_relocation_file_offsets"]),
        )
        metadata.pop("_relocation_file_offsets", None)
        rows.append(
            {
                "module": name,
                "file": path.name,
                "mode": "arm",
                "file_sha256": sha256(path.read_bytes()),
                "code_size": len(cro_text),
                "hits": hits,
                "cro_metadata": metadata,
                "hit_count": len(hits),
                "stack_base_hits": sum(bool(x["stack_base"]) for x in hits),
                "field_counts": {
                    field: sum(x["field"] == field for x in hits) for field in FIELDS
                },
                "truncated": args.limit is not None and len(hits) >= args.limit,
            }
        )

    result = {
        "fields": {name: hex(offset) for name, offset in FIELDS.items()},
        "mode": "relocation-aware candidate enumeration; not alias-complete",
        "main_code_relocations": "unavailable: ExeFS .code is a stripped mapped image, not a CRO",
        "modules": rows,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_path:
        args.json_path.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
