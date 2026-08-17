#!/usr/bin/env python3
"""Verify the concrete examples used to delimit the two proof obligations.

The check is intentionally small and reproducible: it validates the exact
retail `.code`/Battle.cro bytes, the two `str [...,#4]` instructions, and the
absence of a CRO relocation at the CRO instruction.  It does not infer an
object type from the displacement; that non-inference is the point of the
separation artifact.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs
from capstone.arm import ARM_OP_MEM, ARM_INS_STR


def load_audit():
    path = Path(__file__).with_name("audit-retail-ai-mask-writers.py")
    spec = importlib.util.spec_from_file_location("retail_mask_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load retail mask audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_str(code: bytes, address: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.detail = True
    md.skipdata = True
    for ins in md.disasm(code, 0):
        if ins.address != address:
            continue
        if ins.id != ARM_INS_STR or len(ins.operands) < 2:
            break
        mem = ins.operands[1]
        if mem.type == ARM_OP_MEM and mem.mem.disp == 4:
            return {
                "address": hex(ins.address),
                "mnemonic": ins.mnemonic,
                "operands": ins.op_str,
                "bytes": ins.bytes.hex(),
            }
        break
    raise ValueError(f"expected str [base,#4] at {address:#x}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("code", type=Path)
    ap.add_argument("cro_dir", type=Path)
    args = ap.parse_args()

    audit = load_audit()
    code = args.code.read_bytes()
    code_row = find_str(code, 0x45EC)
    cro_path = args.cro_dir / "Battle.cro"
    name, cro_code, metadata = audit.cro_code(cro_path)
    if name != "Battle":
        raise ValueError(f"unexpected CRO name: {name}")
    cro_row = find_str(cro_code, 0x1E80)
    relocations = set(metadata["_relocation_file_offsets"])
    if int(metadata["code_offset"]) + 0x1E80 in relocations:
        raise ValueError("Battle.cro candidate unexpectedly has a relocation")

    result = {
        "main_code": code_row,
        "battle_cro": {
            **cro_row,
            "code_offset": hex(int(metadata["code_offset"])),
            "relocation_at_instruction": False,
        },
        "verdict": "Both exact stores are displacement candidates; neither instruction identifies an ai_bit object.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
