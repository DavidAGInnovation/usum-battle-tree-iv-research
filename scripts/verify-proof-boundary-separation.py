#!/usr/bin/env python3
"""Verify the two stores that bounded the retail writer audit.

The earlier pass stopped at displacement-only evidence.  This verifier adds
the missing field-sensitive facts: the main-image store receives a pointer
computed from a read-only literal, and the Battle CRO store is a relocated
entry in the ``gfl2::Effect::Config`` vtable.  Neither can write the
``BSP_TRAINER_DATA::CORE_DATA::ai_bit`` field.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs
from capstone.arm import ARM_OP_MEM, ARM_INS_STR


EXPECTED_MAIN_SHA256 = "b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09"
EXPECTED_BATTLE_SHA256 = "334ab92012b8dd9179ba27e0faeeb6d1fd21113e13812ec065e68309dae8396c"


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


def arm(code: bytes, address: int):
    """Decode one ARM instruction at a raw image offset."""
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    decoded = list(md.disasm(code[address : address + 4], address))
    if len(decoded) != 1:
        raise ValueError(f"cannot decode ARM instruction at {address:#x}")
    return decoded[0]


def parse_cro_relocations(data: bytes, segments: list[dict[str, object]]):
    """Yield CRO relocation rows with output and target segment offsets."""
    tables = (("import", 0xF8, 0xFC), ("internal", 0x128, 0x12C), ("unknown", 0x130, 0x134))
    for table, offset_field, count_field in tables:
        table_offset, count = struct.unpack_from("<II", data, offset_field)
        for index in range(count):
            entry = table_offset + index * 12
            output, reloc_type, target_segment, flags, padding, addend = struct.unpack_from(
                "<IBBBB I", data, entry
            )
            output_segment = output & 0xF
            output_offset = output >> 4
            if output_segment >= len(segments):
                continue
            segment = segments[output_segment]
            if output_offset >= int(segment["size"]):
                continue
            yield {
                "table": table,
                "index": index,
                "output_segment": output_segment,
                "output_offset": output_offset,
                "target_segment": target_segment,
                "addend": addend,
                "type": reloc_type,
                "file_offset": int(segment["offset"]) + output_offset,
            }


def find_relocation(rows, output_segment: int, output_offset: int):
    matches = [
        row
        for row in rows
        if row["output_segment"] == output_segment and row["output_offset"] == output_offset
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected one relocation at segment {output_segment}+{output_offset:#x}, "
            f"found {len(matches)}"
        )
    return matches[0]


def verify_main_pointer(code: bytes):
    """Prove the 0x45ec value is a data-tail pointer, not a mask."""
    digest = hashlib.sha256(code).hexdigest()
    if digest != EXPECTED_MAIN_SHA256:
        raise ValueError(f"unexpected main .code SHA-256: {digest}")
    expected = {
        0x45d8: ("mov", "r1, #0"),
        0x45dc: ("mov", "r0, r1"),
        0x45e0: ("bl", "#0x4a50"),
        0x45e4: ("add", "r0, r0, #1"),
        0x45ec: ("str", "r0, [r4, #4]"),
    }
    decoded = {}
    for address, (mnemonic, operands) in expected.items():
        instruction = arm(code, address)
        if instruction.mnemonic != mnemonic or instruction.op_str != operands:
            raise ValueError(
                f"unexpected instruction at {address:#x}: "
                f"{instruction.mnemonic} {instruction.op_str}"
            )
        decoded[address] = {
            "address": hex(address),
            "mnemonic": instruction.mnemonic,
            "operands": instruction.op_str,
            "bytes": instruction.bytes.hex(),
        }

    branch = arm(code, 0x4a58)
    if (branch.mnemonic, branch.op_str) != ("beq", "#0x4a84"):
        raise ValueError("0x4a50 does not take its zero-argument pointer path")
    literal_load = arm(code, 0x4a84)
    literal_add = arm(code, 0x4a88)
    if (literal_load.mnemonic, literal_load.op_str) != ("ldr", "r0, [pc, #8]"):
        raise ValueError("unexpected pointer literal load in 0x4a50")
    if (literal_add.mnemonic, literal_add.op_str) != ("add", "r0, pc, r0"):
        raise ValueError("unexpected pointer construction in 0x4a50")
    literal_offset = 0x4A84 + 8 + 8
    literal = struct.unpack_from("<I", code, literal_offset)[0]
    pointer = literal + (0x4A88 + 8)
    stored_value = pointer + 1
    if not (0x4BA000 <= pointer < len(code)):
        raise ValueError(f"computed pointer {pointer:#x} is not in the read-only tail")
    return {
        "sha256": digest,
        "function_start": "0x45bc",
        "store": decoded[0x45ec],
        "pointer_origin": {
            "zero_argument_call": "bl 0x4a50",
            "literal_offset": hex(literal_offset),
            "literal_value": hex(literal),
            "add_pc": hex(0x4A88 + 8),
            "computed_pointer": hex(pointer),
            "stored_value": hex(stored_value),
            "region": "retail .code read-only/data tail",
        },
        "ai_bit_value_disjoint": stored_value > 0x127,
    }


def verify_battle_type(cro_path: Path):
    """Resolve Battle.cro:0x1e80 through its CRO vtable/RTTI relocations."""
    audit = load_audit()
    name, code, metadata = audit.cro_code(cro_path)
    if name != "Battle":
        raise ValueError(f"unexpected CRO name: {name}")
    store = find_str(code, 0x1E80)
    data = cro_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_BATTLE_SHA256:
        raise ValueError(f"unexpected Battle.cro SHA-256: {digest}")
    segments = metadata["segments"]
    rows = list(parse_cro_relocations(data, segments))
    code_segment = next(row for row in segments if int(row["type"]) == 0)
    data_segment = next(row for row in segments if int(row["type"]) == 1)

    # The vtable is preceded by offset-to-top at +0xe0c8.  Its typeinfo entry
    # is at +0xe0cc, and +0xe0d8 is the third virtual slot.
    vtable_typeinfo = find_relocation(rows, 1, 0xE0CC)
    slot_target = find_relocation(rows, 1, 0xE0D8)
    if slot_target["target_segment"] != 0 or slot_target["addend"] != 0x1E80:
        raise ValueError("vtable slot does not resolve to Battle.cro:0x1e80")
    typeinfo_offset = vtable_typeinfo["addend"]
    name_pointer = find_relocation(rows, 1, typeinfo_offset + 4)
    if name_pointer["target_segment"] != 1:
        raise ValueError("typeinfo name does not point into Battle.cro data")
    name_offset = name_pointer["addend"]
    data_file_offset = int(data_segment["offset"]) + name_offset
    rtti_name = data[data_file_offset :].split(b"\0", 1)[0].decode("ascii")
    expected_name = "N4gfl26Effect6ConfigE"
    if rtti_name != expected_name:
        raise ValueError(f"unexpected RTTI name: {rtti_name!r}")
    instruction_file_offset = int(code_segment["offset"]) + 0x1E80
    if any(row["file_offset"] == instruction_file_offset for row in rows):
        raise ValueError("candidate instruction unexpectedly has a relocation")
    return {
        "file": cro_path.name,
        "sha256": digest,
        "code_offset": hex(int(metadata["code_offset"])),
        "store": store,
        "relocation_at_store": False,
        "vtable": {
            "segment": 1,
            "offset": "0xe0c8",
            "typeinfo_offset": hex(typeinfo_offset),
            "virtual_slot_offset": "0xe0d8",
            "virtual_slot_index": 2,
            "target_code_offset": "0x1e80",
            "rtti_name": rtti_name,
            "source_type": "gfl2::Effect::Config (inherits nw::eft::Config)",
            "source_header": "gflib2/Effect/include/gfl2_EffectConfig.h",
        },
        "ai_bit_type_disjoint": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("code", type=Path)
    ap.add_argument("cro_dir", type=Path)
    args = ap.parse_args()

    code = args.code.read_bytes()
    main = verify_main_pointer(code)
    cro_path = args.cro_dir / "Battle.cro"
    battle = verify_battle_type(cro_path)

    result = {
        "main_code": main,
        "battle_cro": battle,
        "verdict": "Residual stores closed: the main store writes a data-tail pointer and Battle.cro:0x1e80 is gfl2::Effect::Config virtual code, so neither writes BSP_TRAINER_DATA::CORE_DATA::ai_bit.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
