#!/usr/bin/env python3
"""Verify the residual component of the retail ``ai_bit`` writer theorem.

The displacement scan intentionally over-approximates ARM stores.  This check
does the interprocedural work for the two exact residual sites that survived
that scan:

* ``.code:0x45ec`` is reached with a fixed pointer-producing call chain and
  stores a read-only/data-tail pointer, not an AI mask.
* ``Battle.cro:0x1e80`` is referenced exactly once, as a virtual-table slot
  whose RTTI is ``gfl2::Effect::Config``.  ``BSP_TRAINER_DATA`` is a
  non-polymorphic class in the archived source, so this virtual slot cannot be
  an invocation on trainer data.

This is deliberately a component verifier for the two residual sites.  The
source-complete theorem, including aliased/copied writers and PM_DEBUG
exclusions, is verified by ``verify-retail-ai-writer-whole-program.py``.
This component does not claim that every same-displacement store in unrelated
game objects is an AI field.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs


EXPECTED_MAIN_SHA256 = "b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09"
EXPECTED_BATTLE_SHA256 = "334ab92012b8dd9179ba27e0faeeb6d1fd21113e13812ec065e68309dae8396c"
AI_MASK_VALUES = {0x7, 0x8, 0xF, 0x40, 0x107, 0x10F, 0x125, 0x127}


def load_audit():
    path = Path(__file__).with_name("audit-retail-ai-mask-writers.py")
    spec = importlib.util.spec_from_file_location("retail_mask_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load retail mask audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def arm(code: bytes, address: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    decoded = list(md.disasm(code[address : address + 4], address))
    if len(decoded) != 1:
        raise ValueError(f"cannot decode ARM instruction at {address:#x}")
    return decoded[0]


def parse_relocations(data: bytes, segments: list[dict[str, object]]):
    """Return all CRO relocation rows with their output locations."""
    rows = []
    for table, offset_field, count_field in (
        ("import", 0xF8, 0xFC),
        ("internal", 0x128, 0x12C),
        ("unknown", 0x130, 0x134),
    ):
        table_offset, count = struct.unpack_from("<II", data, offset_field)
        for index in range(count):
            entry = table_offset + index * 12
            output, reloc_type, target_segment, _flags, _padding, addend = struct.unpack_from(
                "<IBBBB I", data, entry
            )
            output_segment = output & 0xF
            output_offset = output >> 4
            if output_segment >= len(segments):
                continue
            segment = segments[output_segment]
            if output_offset >= int(segment["size"]):
                continue
            rows.append(
                {
                    "table": table,
                    "index": index,
                    "output_segment": output_segment,
                    "output_offset": output_offset,
                    "target_segment": target_segment,
                    "addend": addend,
                    "type": reloc_type,
                    "file_offset": int(segment["offset"]) + output_offset,
                }
            )
    return rows


def branch_target(ins) -> int | None:
    """Decode an ARM B/BL target without relying on a relocated symbol."""
    if not ins.mnemonic.lower().startswith("b") or len(ins.operands) != 1:
        return None
    operand = ins.operands[0]
    if operand.type != 2:  # ARM_OP_IMM
        return None
    return int(operand.imm)


def verify_main(code: bytes) -> dict[str, object]:
    digest = hashlib.sha256(code).hexdigest()
    if digest != EXPECTED_MAIN_SHA256:
        raise ValueError(f"unexpected main .code SHA-256: {digest}")

    expected = {
        0x45D0: ("bl", "#0x1ff914"),
        0x45D4: ("mov", "r4, r0"),
        0x45E0: ("bl", "#0x4a50"),
        0x45E4: ("add", "r0, r0, #1"),
        0x45EC: ("str", "r0, [r4, #4]"),
        0x45F8: ("str", "r0, [r4, #0xc]"),
    }
    decoded = {}
    for address, (mnemonic, operands) in expected.items():
        ins = arm(code, address)
        if (ins.mnemonic, ins.op_str) != (mnemonic, operands):
            raise ValueError(
                f"unexpected instruction at {address:#x}: {ins.mnemonic} {ins.op_str}"
            )
        decoded[hex(address)] = {
            "mnemonic": ins.mnemonic,
            "operands": ins.op_str,
            "bytes": ins.bytes.hex(),
        }

    # The zero-argument helper at 0x1ff914 loads a fixed global pointer.
    helper_load = arm(code, 0x1FF914)
    helper_return = arm(code, 0x1FF918)
    if (helper_load.mnemonic, helper_load.op_str) != ("ldr", "r0, [pc]"):
        raise ValueError("0x1ff914 is not the expected literal-load helper")
    if (helper_return.mnemonic, helper_return.op_str) != ("bx", "lr"):
        raise ValueError("0x1ff914 does not return through lr")
    global_pointer = struct.unpack_from("<I", code, 0x1FF91C)[0]

    # The caller passes r1=0.  The first branch in 0x4a50 therefore selects
    # the deterministic literal path, independent of any runtime object.
    zero_path = arm(code, 0x4A54)
    zero_branch = arm(code, 0x4A58)
    literal_load = arm(code, 0x4A84)
    literal_add = arm(code, 0x4A88)
    if (zero_path.mnemonic, zero_path.op_str) != ("cmp", "r1, #0"):
        raise ValueError("0x4a50 does not test the null input")
    if (zero_branch.mnemonic, zero_branch.op_str) != ("beq", "#0x4a84"):
        raise ValueError("0x4a50 null path does not reach the fixed literal")
    if (literal_load.mnemonic, literal_load.op_str) != ("ldr", "r0, [pc, #8]"):
        raise ValueError("unexpected fixed literal load in 0x4a50")
    if (literal_add.mnemonic, literal_add.op_str) != ("add", "r0, pc, r0"):
        raise ValueError("unexpected PC-relative add in 0x4a50")
    literal = struct.unpack_from("<I", code, 0x4A94)[0]
    pointer = literal + (0x4A88 + 8)
    stored_value = pointer + 1
    if not (0x4BA000 <= pointer < len(code)):
        raise ValueError(f"fixed pointer {pointer:#x} is outside the read-only tail")
    if stored_value in AI_MASK_VALUES or stored_value <= 0x127:
        raise ValueError("residual store value unexpectedly overlaps an AI mask")

    # Confirm that this function's only object stores are pointer-slot writes;
    # there is no +0x1c write in the function body.
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.detail = True
    stores = []
    for ins in md.disasm(code[0x45BC:0x45FC], 0x45BC):
        if ins.mnemonic.startswith("str") and len(ins.operands) >= 2:
            mem = ins.operands[1]
            if getattr(mem, "type", None) == 3:
                stores.append({"address": hex(ins.address), "operands": ins.op_str})
    if any("#0x1c" in row["operands"] for row in stores):
        raise ValueError("0x45bc function writes the MainModule ai_bit displacement")

    return {
        "sha256": digest,
        "function_start": "0x45bc",
        "instructions": decoded,
        "receiver_origin": {
            "call": "bl 0x1ff914",
            "literal_at": "0x1ff91c",
            "global_pointer": hex(global_pointer),
        },
        "value_provenance": {
            "call": "bl 0x4a50 with r1=0",
            "literal_offset": "0x4a94",
            "literal_value": hex(literal),
            "pc_add": "0x4a90",
            "computed_pointer": hex(pointer),
            "stored_value": hex(stored_value),
            "region": "retail .code read-only/data tail",
        },
        "stores": stores,
        "ai_bit_value_disjoint": True,
        "ai_bit_field_write_present": False,
    }


def verify_battle(cro_path: Path) -> dict[str, object]:
    audit = load_audit()
    name, code, metadata = audit.cro_code(cro_path)
    if name != "Battle":
        raise ValueError(f"unexpected CRO name: {name}")
    digest = hashlib.sha256(cro_path.read_bytes()).hexdigest()
    if digest != EXPECTED_BATTLE_SHA256:
        raise ValueError(f"unexpected Battle.cro SHA-256: {digest}")
    data = cro_path.read_bytes()
    segments = metadata["segments"]
    rows = parse_relocations(data, segments)
    targets = [
        row
        for row in rows
        if row["target_segment"] == 0 and row["addend"] == 0x1E80
    ]
    if len(targets) != 1:
        raise ValueError(f"expected one relocation to code+0x1e80, found {len(targets)}")
    target = targets[0]
    if (target["output_segment"], target["output_offset"]) != (1, 0xE0D8):
        raise ValueError("0x1e80 is not the expected vtable slot")

    typeinfo = [
        row for row in rows if row["output_segment"] == 1 and row["output_offset"] == 0xE0CC
    ]
    if len(typeinfo) != 1:
        raise ValueError("missing unique typeinfo relocation")
    typeinfo_offset = typeinfo[0]["addend"]
    name_rows = [
        row
        for row in rows
        if row["output_segment"] == 1 and row["output_offset"] == typeinfo_offset + 4
    ]
    if len(name_rows) != 1 or name_rows[0]["target_segment"] != 1:
        raise ValueError("typeinfo name relocation is not internal to Battle.cro")
    data_segment = next(row for row in segments if int(row["type"]) == 1)
    name_offset = name_rows[0]["addend"]
    file_offset = int(data_segment["offset"]) + name_offset
    rtti_name = data[file_offset:].split(b"\0", 1)[0].decode("ascii")
    if rtti_name != "N4gfl26Effect6ConfigE":
        raise ValueError(f"unexpected RTTI name: {rtti_name!r}")

    # No direct ARM branch reaches this body.  It is a virtual slot, not an
    # ordinary helper that callers can pass a trainer-data pointer to.
    code_segment = next(row for row in segments if int(row["type"]) == 0)
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.detail = True
    direct_branches = []
    for ins in md.disasm(code[int(code_segment["offset"]) : int(code_segment["offset"]) + int(code_segment["size"])], 0):
        target_address = branch_target(ins)
        if target_address == 0x1E80:
            direct_branches.append(hex(ins.address))
    if direct_branches:
        raise ValueError(f"unexpected direct branches to 0x1e80: {direct_branches}")

    return {
        "file": cro_path.name,
        "sha256": digest,
        "code_offset": hex(int(metadata["code_offset"])),
        "instruction": "str r1, [r0, #4]",
        "direct_branch_references": direct_branches,
        "relocation_reference_count": len(targets),
        "vtable": {
            "segment": 1,
            "offset": "0xe0c8",
            "typeinfo_offset": hex(typeinfo_offset),
            "virtual_slot_offset": "0xe0d8",
            "virtual_slot_index": 2,
            "target_code_offset": "0x1e80",
            "rtti_name": rtti_name,
            "source_type": "gfl2::Effect::Config",
        },
        "ai_bit_type_disjoint": True,
    }


def verify_source(source_root: Path) -> dict[str, object]:
    trainer = source_root / "niji_project/prog/Battle/include/Battle_SetupTrainer.h"
    setup = source_root / "niji_project/prog/Battle/source/battle_SetupTrainer.cpp"
    main = source_root / "niji_project/prog/Battle/source/btl_mainmodule.cpp"
    fes = source_root / "niji_project/prog/Field/FieldStatic/source/BattleFes/BattleFes.cpp"
    for path in (trainer, setup, main, fes):
        if not path.exists():
            raise FileNotFoundError(path)
    trainer_text = trainer.read_text(errors="replace")
    class_start = trainer_text.index("class BSP_TRAINER_DATA")
    class_window = trainer_text[class_start : class_start + 6000]
    if "virtual" in class_window:
        raise ValueError("BSP_TRAINER_DATA unexpectedly contains a virtual member")
    setup_text = setup.read_text(errors="replace")
    main_text = main.read_text(errors="replace")
    fes_text = fes.read_text(errors="replace")
    required = {
        "core_ai_bit_field": "u32               ai_bit;",
        "deserialize_copy": "mCore.ai_bit          = serializedData->ai_bit;",
        "npc_copy": "dst->ai_bit       = trData->GetAIBit();",
        "core_zero": "dst->ai_bit = 0;",
        "fes_selector": "dst->SetAIBit(ai_bit);",
    }
    haystacks = {
        "core_ai_bit_field": trainer_text,
        "deserialize_copy": setup_text,
        "npc_copy": main_text,
        "core_zero": main_text,
        "fes_selector": fes_text,
    }
    missing = [name for name, needle in required.items() if needle not in haystacks[name]]
    if missing:
        raise ValueError(f"source writer evidence missing: {missing}")
    return {
        "trainer_header": "niji_project/prog/Battle/include/Battle_SetupTrainer.h",
        "bsp_trainer_data_polymorphic": False,
        "source_writer_evidence": {name: needle for name, needle in required.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("code", type=Path)
    parser.add_argument("cro_dir", type=Path)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()

    result = {
        "artifact": "field-sensitive residual lift for retail ai_bit writer theorem",
        "inputs": {
            "main_code": str(args.code),
            "battle_cro": str(args.cro_dir / "Battle.cro"),
            "source_root": str(args.source_root),
        },
        "main_code_residual": verify_main(args.code.read_bytes()),
        "battle_cro_residual": verify_battle(args.cro_dir / "Battle.cro"),
        "source_type_evidence": verify_source(args.source_root),
        "theorem": {
            "scope": "the two exact residual displacement-compatible stores left by the retail candidate audit",
            "proved": True,
            "statement": "Neither residual store can write BSP_TRAINER_DATA::CORE_DATA::ai_bit; the only source-mapped direct stores remain the three SetAIBit inlines.",
            "basis": [
                ".code:0x45ec has fixed pointer value provenance and no +0x1c store in its function",
                "Battle.cro:0x1e80 is a unique RTTI-backed virtual slot for gfl2::Effect::Config",
                "BSP_TRAINER_DATA is non-polymorphic in the archived source",
            ],
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
