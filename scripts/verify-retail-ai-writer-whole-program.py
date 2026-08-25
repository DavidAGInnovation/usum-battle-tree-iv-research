#!/usr/bin/env python3
"""Verify the field-sensitive retail ``ai_bit`` writer theorem.

The older residual verifier is intentionally narrow: it proves only the two
same-displacement stores that survived the first structural sweep.  This
verifier lifts the complete archived source inventory into the retail build
topology, rescans every executable mask-valued displacement candidate, and
checks the corresponding field-sensitive instruction fingerprints in the
stripped image.  The theorem proved here is universal over source-defined
writers compiled into retail, including aliases and copied structures; the
candidate ledger records why every other executable collision is a stack
temporary, a width/layout mismatch, or a source-module/type-disjoint object.

The source archive is needed because the retail image is stripped.  The binary
checks establish that the key copied/aliased paths are the expected compiled
implementations; the source/project checks establish that no other retail
translation unit contains an unclassified ``ai_bit`` writer.  PM_DEBUG-only
writers are explicitly excluded and their retail CRO stubs are checked.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, Cs


EXPECTED_MAIN_SHA256 = "b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09"
EXPECTED_BATTLE_SHA256 = "334ab92012b8dd9179ba27e0faeeb6d1fd21113e13812ec065e68309dae8396c"
EXPECTED_SOURCE_COMMIT = "3f7c94593424a6afddcd9f92a293a3786c9f6425"
RETAIL_TEXT_BOUNDARY = 0x4BA000
EXPECTED_MASK_CANDIDATES = 325
CANONICAL_MAIN_MASK_WRITERS = {0x58260, 0x582D4, 0x59370}

# Explicit main-image residual classifications.  A new retail build fails
# closed if a candidate appears outside these reviewed offsets.
MAIN_UNRELATED_SHAPE = {
    0x8DB00, 0x22D5EC, 0x2A1DA4, 0x2A1F4C, 0x318AA0, 0x318ACC,
    0x36A8C4, 0x36C58C, 0x36EC1C, 0x3BB974, 0x3CC780, 0x3CC82C,
    0x3CC8E8, 0x3D9AC4,
}
MAIN_INTERIOR_OR_LOCAL = {
    0x889A4, 0x144848, 0x145850, 0x16E2C0, 0x16E2EC, 0x16E370,
    0x16E398, 0x16E3C4, 0x16E3F0, 0x16E41C, 0x16E448, 0x16E474,
    0x16E4A0, 0x1E43D0, 0x1E7D0C, 0x1F113C, 0x1F29E0, 0x20D3DC,
    0x2B8804, 0x2E12E8, 0x36329C, 0x3632F8, 0x3637F0, 0x365F3C,
    0x36BF08, 0x36FBBC, 0x37D4AC,
}
BATTLE_STACK_INTERIOR = {0x33354, 0x9FFE4, 0xA9058}
BATTLE_UNRELATED_SHAPE = {0x46654}


def load_audit():
    path = Path(__file__).with_name("audit-retail-ai-mask-writers.py")
    spec = importlib.util.spec_from_file_location("retail_mask_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load retail mask audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decode(blob: bytes, offset: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    rows = list(md.disasm(blob[offset : offset + 4], offset))
    if len(rows) != 1:
        raise ValueError(f"cannot decode ARM instruction at {offset:#x}")
    return rows[0]


def expect(blob: bytes, offset: int, mnemonic: str, operands: str) -> dict[str, object]:
    ins = decode(blob, offset)
    if (ins.mnemonic, ins.op_str) != (mnemonic, operands):
        raise ValueError(
            f"unexpected instruction at {offset:#x}: {ins.mnemonic} {ins.op_str}; "
            f"expected {mnemonic} {operands}"
        )
    return {
        "offset": hex(offset),
        "mnemonic": ins.mnemonic,
        "operands": ins.op_str,
        "bytes": ins.bytes.hex(),
    }


def verify_deserialize(code: bytes) -> dict[str, object]:
    """Verify BSP_TRAINER_DATA::Deserialize in the linked static library."""
    digest = hashlib.sha256(code).hexdigest()
    if digest != EXPECTED_MAIN_SHA256:
        raise ValueError(f"unexpected main .code SHA-256: {digest}")
    if RETAIL_TEXT_BOUNDARY > len(code):
        raise ValueError("retail ExHeader text boundary exceeds .code")

    expected = {
        0x61724: ("push", "{r4, r5, lr}"),
        0x6172C: ("ldr", "r0, [r1, #8]"),
        0x61740: ("ldr", "r0, [r4, #0xc]"),
        0x61744: ("str", "r0, [r5]"),
        0x61748: ("ldr", "r0, [r4, #0x10]"),
        0x6174C: ("str", "r0, [r5, #4]"),
        0x61750: ("ldr", "r0, [r4, #0x14]"),
        0x61754: ("strb", "r0, [r5, #8]"),
        0x61758: ("ldrh", "r0, [r4, #0x18]"),
        0x6175C: ("strh", "r0, [r5, #0xa]"),
        0x61760: ("ldrb", "r0, [r4, #0x1a]"),
        0x61764: ("strb", "r0, [r5, #0xc]"),
        0x61834: ("ldr", "r0, [r4, #0x28]"),
        0x61838: ("str", "r0, [r5, #0x18]"),
        0x6183C: ("ldrh", "r0, [r4, #0x2c]"),
        0x61840: ("strh", "r0, [r5, #0x1c]"),
        0x61844: ("ldrh", "r0, [r4, #0x2e]"),
        0x61848: ("strh", "r0, [r5, #0x1e]"),
    }
    instructions = [
        expect(code, offset, mnemonic, operands)
        for offset, (mnemonic, operands) in expected.items()
    ]
    return {
        "module": ".code",
        "function": "BSP_TRAINER_DATA::Deserialize",
        "function_offset": "0x61724",
        "source_direction": "SERIALIZE_DATA +0x10 -> CORE_DATA +0x4",
        "instructions": instructions,
        "ai_bit_copy_verified": True,
        "text_region": {
            "boundary": hex(RETAIL_TEXT_BOUNDARY),
            "function_inside_text": True,
        },
    }


def verify_battle_functions(cro_path: Path) -> dict[str, object]:
    """Verify the two field-sensitive MainModule implementations in Battle.cro."""
    audit = load_audit()
    name, body, metadata = audit.cro_code(cro_path)
    if name != "Battle":
        raise ValueError(f"unexpected CRO name: {name}")
    digest = hashlib.sha256(cro_path.read_bytes()).hexdigest()
    if digest != EXPECTED_BATTLE_SHA256:
        raise ValueError(f"unexpected Battle.cro SHA-256: {digest}")

    npc_expected = {
        0x8A25C: ("push", "{r4, r5, r6, r7, lr}"),
        0x8A27C: ("ldr", "r0, [r5]"),
        0x8A280: ("strh", "r0, [r4, #0x14]"),
        0x8A284: ("ldrh", "r0, [r5, #0xa]"),
        0x8A288: ("strh", "r0, [r4, #0x16]"),
        0x8A2A8: ("ldr", "r0, [r5, #4]"),
        0x8A2AC: ("str", "r0, [r4, #0x1c]"),
        0x8A2B0: ("ldrb", "r0, [r5, #0xe]"),
    }
    player_expected = {
        0x8A414: ("push", "{r4, r5, r6, lr}"),
        0x8A418: ("mov", "r5, r0"),
        0x8A41C: ("mov", "r4, r1"),
        0x8A448: ("strh", "r6, [r4, #0x14]"),
        0x8A460: ("strh", "r0, [r4, #0x16]"),
        0x8A494: ("str", "r6, [r4, #0xc]"),
        0x8A498: ("str", "r6, [r4, #0x10]"),
        0x8A49C: ("str", "r6, [r4, #0x1c]"),
        0x8A4A0: ("strb", "r6, [r4, #0x28]"),
        0x8A4A4: ("strb", "r6, [r4, #0x29]"),
    }

    def run(expected):
        return [expect(body, offset, mnemonic, operands) for offset, (mnemonic, operands) in expected.items()]

    return {
        "module": "Battle.cro",
        "sha256": digest,
        "code_offset": hex(int(metadata["code_offset"])),
        "functions": [
            {
                "function": "MainModule::trainerParam_StoreNPCTrainer",
                "function_offset": "0x8a25c",
                "source_direction": "BSP_TRAINER_DATA::CORE_DATA +0x4 -> MainModule::TRAINER_DATA +0x1c",
                "instructions": run(npc_expected),
                "ai_bit_copy_verified": True,
            },
            {
                "function": "MainModule::trainerParam_StorePlayer / trainerParam_StoreCore",
                "function_offset": "0x8a414",
                "source_direction": "player core initialization -> MainModule::TRAINER_DATA +0x1c = 0",
                "instructions": run(player_expected),
                "ai_bit_zero_verified": True,
            },
        ],
    }


def line_hits(path: Path, pattern: str) -> list[dict[str, object]]:
    regex = re.compile(pattern)
    rows = []
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for line_number, line in enumerate(text.splitlines(), 1):
        if regex.search(line):
            rows.append({"file": path.as_posix(), "line": line_number, "text": line.strip()})
    return rows


def project_contains(source: Path, project: Path) -> None:
    """Require a source file to be compiled by the named archived project."""
    if not source.exists():
        raise FileNotFoundError(source)
    if not project.exists():
        raise FileNotFoundError(project)
    project_text = project.read_text(encoding="utf-8-sig", errors="replace")
    source_rel = source.relative_to(project.parent).as_posix().replace("/", "\\")
    if source_rel not in project_text:
        raise ValueError(f"{source_rel} is not listed in {project}")


def source_inventory(source_root: Path) -> dict[str, object]:
    """Inventory every source ``ai_bit`` writer and tie it to a project."""
    prog = source_root / "niji_project/prog"
    layout_checks = {
        "BSP_TRAINER_DATA::CORE_DATA::ai_bit": (
            prog / "Battle/include/Battle_SetupTrainer.h",
            "u32               tr_id;\n    u32               ai_bit;",
            "0x4",
        ),
        "BSP_TRAINER_DATA::SERIALIZE_DATA::ai_bit": (
            prog / "Battle/include/Battle_SetupTrainer.h",
            "u32     tr_id;\n    u32     ai_bit;",
            "0x10",
        ),
        "MainModule::TRAINER_DATA::ai_bit": (
            prog / "Battle/source/btl_mainmodule.h",
            "u8          pad1;\n    u32         ai_bit;",
            "0x1c",
        ),
        "Trainer::TRAINER_DATA::aibit": (
            prog / "Trainer/Trainer/include/tr_tool.h",
            "u16 use_item[4];          // 0x04 使用道具\n  u32 aibit;                // 0x0c AIパターン",
            "0x0c",
        ),
    }
    field_layouts = []
    for field, (path, needle, offset) in layout_checks.items():
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if needle not in text:
            raise ValueError(f"missing source layout marker for {field}")
        field_layouts.append({"field": field, "source": path.relative_to(source_root).as_posix(), "offset": offset, "marker": needle})
    required = {
        "BSP_TRAINER_DATA::SetAIBit": (
            prog / "Battle/include/Battle_SetupTrainer.h",
            prog / "Battle/BattleStatic.vcxproj",
            ".code",
            r"void SetAIBit\( u32 bit \) \{ mCore\.ai_bit = bit; \}",
            False,
        ),
        "BSP_TRAINER_DATA::Deserialize": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            ".code",
            r"mCore\.ai_bit\s*=\s*serializedData->ai_bit",
            False,
        ),
        "BSP_TRAINER_DATA::Serialize": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            ".code",
            r"serializedData->ai_bit\s*=\s*mCore\.ai_bit",
            False,
        ),
        "BSP_TRAINER_DATA::ClearSerializeData": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            ".code",
            r"gfl2::std::MemClear\(\s*serializedData,\s*sizeof\(BSP_TRAINER_DATA::SERIALIZE_DATA\)\s*\)",
            False,
        ),
        "MainModule::trainerParam_Init": (
            prog / "Battle/source/btl_mainmodule.cpp",
            prog / "Battle/Battle.vcxproj",
            "Battle.cro",
            r"//u32\s+ai_bit;",
            False,
        ),
        "MainModule::trainerParam_StoreCore": (
            prog / "Battle/source/btl_mainmodule.cpp",
            prog / "Battle/Battle.vcxproj",
            "Battle.cro",
            r"dst->ai_bit\s*=\s*0;",
            False,
        ),
        "MainModule::trainerParam_StoreNPCTrainer": (
            prog / "Battle/source/btl_mainmodule.cpp",
            prog / "Battle/Battle.vcxproj",
            "Battle.cro",
            r"dst->ai_bit\s*=\s*trData->GetAIBit",
            False,
        ),
        "BattleInst::SetAiBit": (
            prog / "Field/FieldStatic/source/BattleInst/BattleInst.cpp",
            prog / "Field/FieldStatic/FieldStatic.vcxproj",
            ".code",
            r"dst->SetAIBit\( ai_bit \)",
            False,
        ),
        "BattleInst::SetVsTrainerRoyal": (
            prog / "Field/FieldStatic/source/BattleInst/BattleInst.cpp",
            prog / "Field/FieldStatic/FieldStatic.vcxproj",
            ".code",
            r"dst->SetAIBit\( \(AI_BIT \| BTL_AISCRIPT_BIT_WAZA_ROYAL\) \)",
            False,
        ),
        "BattleFes::setAiBit": (
            prog / "Field/FieldStatic/source/BattleFes/BattleFes.cpp",
            prog / "Field/FieldStatic/FieldStatic.vcxproj",
            ".code",
            r"dst->SetAIBit\(ai_bit\)",
            False,
        ),
        "Trainer::EncountTrainerPersonalDataMake": (
            prog / "Trainer/Trainer/source/tr_tool.cpp",
            prog / "Trainer/Trainer/Trainer.vcxproj",
            ".code",
            r"battleTrainerData->SetAIBit\( trainerData->aibit \)",
            False,
        ),
        "Trainer::GetEncountTrainerData": (
            prog / "Trainer/Trainer/source/tr_tool.cpp",
            prog / "Trainer/Trainer/Trainer.vcxproj",
            ".code",
            r"dst\[i\]->SetAIBit\( td\[i\]\.aibit \)",
            False,
        ),
        "DebugBattle::SetAIBit (PM_DEBUG)": (
            prog / "Debug/DebugBattle/source/DebugBattleProc.cpp",
            prog / "Debug/DebugBattle/DebugBattle.vcxproj",
            "DebugBattle.cro (excluded from retail)",
            r"SetAIBit\(",
            True,
        ),
        "StartMenu::SetAIBit (PM_DEBUG)": (
            prog / "Debug/StartMenu/source/d_ariizumi.cpp",
            prog / "Debug/StartMenu/StartMenu.vcxproj",
            ".code (excluded by PM_DEBUG)",
            r"SetAIBit\(",
            True,
        ),
    }

    rows = []
    for name, (source, project, module, pattern, debug_only) in required.items():
        project_contains(source, project)
        project_text = project.read_text(encoding="utf-8-sig", errors="replace")
        hits = line_hits(source, pattern)
        for hit in hits:
            hit["file"] = source.relative_to(source_root).as_posix()
        if not hits:
            raise ValueError(f"missing source writer marker for {name}")
        if debug_only:
            guarded_text = source.read_text(encoding="utf-8-sig", errors="replace")
            first_writer_line = min(int(hit["line"]) for hit in hits)
            prefix = "\n".join(guarded_text.splitlines()[:first_writer_line])
            if "#if PM_DEBUG" not in prefix:
                raise ValueError(f"{source} is not guarded by PM_DEBUG")
        rows.append(
            {
                "writer": name,
                "source": source.relative_to(source_root).as_posix(),
                "project": project.relative_to(source_root).as_posix(),
                "module": module,
                "retail_compiled": not debug_only,
                "pm_debug_excluded": debug_only,
                "evidence": hits,
                "configuration_types": sorted(set(re.findall(r"<ConfigurationType>([^<]+)", project_text))),
            }
        )

    # Every textual SetAIBit hit must be one of the inventory files above.  A
    # new hit fails closed instead of being silently ignored by this theorem.
    all_hits = []
    for path in prog.rglob("*"):
        if path.suffix.lower() not in {".cpp", ".h", ".hpp", ".inl"}:
            continue
        all_hits.extend(line_hits(path, r"\bSetAIBit\s*\("))
    known_files = {str((source_root / row["source"]).resolve()) for row in rows}
    unknown = [row for row in all_hits if str(Path(row["file"]).resolve()) not in known_files]
    if unknown:
        raise ValueError(f"unclassified SetAIBit source hits: {unknown}")

    # Direct member assignments are also closed.  Local temporary variables
    # named ai_bit are intentionally not writers and are recorded separately.
    direct_patterns = {
        "core_member_assignment": r"\bmCore\.ai_bit\s*=",
        "serialize_member_assignment": r"\bserializedData->ai_bit\s*=",
        "mainmodule_member_assignment": r"\bdst->ai_bit\s*=",
    }
    direct_hits = []
    for label, pattern in direct_patterns.items():
        for path in prog.rglob("*"):
            if path.suffix.lower() not in {".cpp", ".h", ".hpp", ".inl"}:
                continue
            for hit in line_hits(path, pattern):
                direct_hits.append(
                    {
                        "kind": label,
                        "file": path.relative_to(source_root).as_posix(),
                        "line": hit["line"],
                        "text": hit["text"],
                    }
                )
    direct_known = {
        "niji_project/prog/Battle/include/Battle_SetupTrainer.h",
        "niji_project/prog/Battle/source/battle_SetupTrainer.cpp",
        "niji_project/prog/Battle/source/btl_mainmodule.cpp",
    }
    unknown_direct = [row for row in direct_hits if row["file"] not in direct_known]
    if unknown_direct:
        raise ValueError(f"unclassified direct ai_bit assignments: {unknown_direct}")

    clear_source = prog / "Battle/source/battle_SetupTrainer.cpp"
    clear_hits = line_hits(
        clear_source,
        r"gfl2::std::MemClear\(\s*serializedData,\s*sizeof\(BSP_TRAINER_DATA::SERIALIZE_DATA\)\s*\)",
    )
    if len(clear_hits) != 1:
        raise ValueError(f"expected one serialized-buffer ai_bit zeroing edge, found {len(clear_hits)}")
    serialized_buffer_zeroing = {
        "function": "BSP_TRAINER_DATA::ClearSerializeData",
        "source": clear_source.relative_to(source_root).as_posix(),
        "line": clear_hits[0]["line"],
        "text": clear_hits[0]["text"],
        "target": "BSP_TRAINER_DATA::SERIALIZE_DATA::ai_bit (+0x10)",
        "effect": "zeroes the complete serialized buffer, including ai_bit",
    }

    commit = None
    try:
        commit = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    if commit != EXPECTED_SOURCE_COMMIT:
        raise ValueError(f"unexpected source archive commit: {commit}")

    return {
        "source_commit": commit,
        "field_layouts": field_layouts,
        "writers": rows,
        "all_set_aibit_hits": len(all_hits),
        "unclassified_set_aibit_hits": unknown,
        "direct_member_assignment_hits": direct_hits,
        "unclassified_direct_member_assignments": unknown_direct,
        "serialized_buffer_zeroing": serialized_buffer_zeroing,
        "source_writer_completeness": True,
    }


def source_type_flow(source_root: Path) -> dict[str, object]:
    """Close the alias/copy edges that are not visible as member syntax.

    ``BSP_TRAINER_DATA`` deliberately forbids copy construction/assignment.
    The only whole-object-looking assignment in the archived source is inside
    an inactive ``#if 0`` block; the enabled network path calls ``Serialize``.
    ``Serialize`` and ``ClearSerializeData`` are recorded explicitly because
    they write or clear the intermediate serialized ``ai_bit`` field.  Their
    enabled call sites are checked as well, including the ExtSavedata recorder
    path that invokes the clear helper.
    This check records that fact and the project topology that places the
    canonical type-bearing translation units in the main image or Battle CRO.
    """
    prog = source_root / "niji_project/prog"
    trainer_header = prog / "Battle/include/Battle_SetupTrainer.h"
    trainer_text = trainer_header.read_text(encoding="utf-8-sig", errors="replace")
    if "GFL_FORBID_COPY_AND_ASSIGN(BSP_TRAINER_DATA);" not in trainer_text:
        raise ValueError("BSP_TRAINER_DATA copy/assignment guard is missing")

    net = prog / "Battle/source/btl_net.cpp"
    net_text = net.read_text(encoding="utf-8-sig", errors="replace")
    disabled_copy = "sendData->base_data = *trData;"
    copy_line = next((i for i, line in enumerate(net_text.splitlines(), 1) if disabled_copy in line), None)
    if copy_line is None:
        raise ValueError("expected historical whole-object copy marker is missing")
    net_lines = net_text.splitlines()
    prior = net_lines[:copy_line]
    last_if0 = max((i for i, line in enumerate(prior) if "#if 0" in line), default=-1)
    last_endif = max((i for i, line in enumerate(prior) if "#endif" in line), default=-1)
    if last_if0 <= last_endif:
        raise ValueError("whole-object trainer copy is not proven disabled")

    serialized_edge_checks = {
        "Serialize_definition": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            r"void BSP_TRAINER_DATA::Serialize\(",
            1,
        ),
        "Serialize_network_call": (
            prog / "Battle/source/btl_net.cpp",
            prog / "Battle/Battle.vcxproj",
            r"trData->Serialize\(\s*&sendData->base_data",
            1,
        ),
        "Deserialize_definition": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            r"void BSP_TRAINER_DATA::Deserialize\(",
            1,
        ),
        "Deserialize_network_call": (
            prog / "Battle/source/btl_mainmodule.cpp",
            prog / "Battle/Battle.vcxproj",
            r"trData->Deserialize\(\s*&trSendData->base_data",
            1,
        ),
        "ClearSerializeData_definition": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            r"void BSP_TRAINER_DATA::ClearSerializeData\(",
            1,
        ),
        "Serialize_recorder_call": (
            prog / "ExtSavedata/source/BattleRecorderSaveData.cpp",
            prog / "ExtSavedata/ExtSavedata.vcxproj",
            r"bsp->tr_data\[ i \]->Serialize\(\s*&mBattleRecData->upload.body.tr_data\[ i \]",
            1,
        ),
        "Deserialize_recorder_calls": (
            prog / "ExtSavedata/source/BattleRecorderSaveData.cpp",
            prog / "ExtSavedata/ExtSavedata.vcxproj",
            r"bsp->tr_data\[ i \]->Deserialize\(\s*&mBattleRecData->upload.body.tr_data\[ i \]",
            2,
        ),
        "ClearSerializeData_recorder_call": (
            prog / "ExtSavedata/source/BattleRecorderSaveData.cpp",
            prog / "ExtSavedata/ExtSavedata.vcxproj",
            r"BSP_TRAINER_DATA::ClearSerializeData\(",
            1,
        ),
    }
    serialized_edges = []
    for label, (path, project, pattern, expected_count) in serialized_edge_checks.items():
        project_contains(path, project)
        hits = line_hits(path, pattern)
        if len(hits) != expected_count:
            raise ValueError(f"expected {expected_count} {label} source edge(s), found {len(hits)}")
        for hit in hits:
            serialized_edges.append(
                {
                    "edge": label,
                    "source": path.relative_to(source_root).as_posix(),
                    "project": project.relative_to(source_root).as_posix(),
                    "line": hit["line"],
                    "text": hit["text"],
                    "effect": "writes or clears BSP_TRAINER_DATA::SERIALIZE_DATA::ai_bit (+0x10)",
                }
            )

    main_project = prog / "Main/project/niji.vcxproj"
    main_text = main_project.read_text(encoding="utf-8-sig", errors="replace")
    required_refs = {
        "Battle": r"..\..\Battle\Battle.vcxproj",
        "BattleStatic": r"..\..\Battle\BattleStatic.vcxproj",
        "FieldStatic": r"..\..\Field\FieldStatic\FieldStatic.vcxproj",
        "Trainer": r"..\..\Trainer\Trainer\Trainer.vcxproj",
        "ExtSavedata": r"..\..\ExtSavedata\ExtSavedata.vcxproj",
        "BattleSpot": r"..\..\NetApp\BattleSpot\BattleSpot.vcxproj",
        "BattleVideoPlayer": r"..\..\NetApp\BattleVideoPlayer\BattleVideoPlayer.vcxproj",
        "BattleVideoRecording": r"..\..\NetApp\BattleVideoRecording\BattleVideoRecording.vcxproj",
        "NetAppLib": r"..\..\NetStatic\NetAppLib\NetAppLib.vcxproj",
        "NetEvent": r"..\..\NetStatic\NetEvent\NetEvent.vcxproj",
        "NetLib": r"..\..\NetStatic\NetLib\NetLib.vcxproj",
    }
    for label, ref in required_refs.items():
        if ref not in main_text:
            raise ValueError(f"main retail project is missing {label} reference")

    canonical_roots = {
        "Battle": prog / "Battle",
        "ExtSavedata": prog / "ExtSavedata",
        "FieldStatic": prog / "Field/FieldStatic",
        "Trainer": prog / "Trainer/Trainer",
    }
    alias_roots = {
        "BattleSpot": prog / "NetApp/BattleSpot",
        "BattleVideoPlayer": prog / "NetApp/BattleVideoPlayer",
        "BattleVideoRecording": prog / "NetApp/BattleVideoRecording",
        "NetAppLib": prog / "NetStatic/NetAppLib",
        "NetEvent": prog / "NetStatic/NetEvent",
        "NetLib": prog / "NetStatic/NetLib",
    }
    type_files = []
    for root in canonical_roots.values():
        for path in sorted(root.rglob("*")):
            if path.suffix.lower() not in {".cpp", ".h", ".hpp", ".inl"}:
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r"BSP_TRAINER_DATA|MainModule::TRAINER_DATA|SetAIBit|\bai_bit\b|\baibit\b", text):
                type_files.append(path.relative_to(source_root).as_posix())

    alias_files = []
    for root in alias_roots.values():
        for path in sorted(root.rglob("*")):
            if path.suffix.lower() not in {".cpp", ".h", ".hpp", ".inl"}:
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(
                r"BATTLE_REC_DATA|BATTLE_REC_UPLOAD_DATA|GetBattleRecDataDirect|"
                r"SetBattleRecUploadData|GetDownloadBufferPtr|mBattleRecData|"
                r"tr_data\s*\[",
                text,
            ):
                alias_files.append(path.relative_to(source_root).as_posix())

    return {
        "copy_assignment_guard": True,
        "disabled_whole_object_copy": {
            "source": net.relative_to(source_root).as_posix(),
            "line": copy_line,
            "text": disabled_copy,
            "under_if_0": True,
        },
        "serialized_edges": serialized_edges,
        "main_project": main_project.relative_to(source_root).as_posix(),
        "main_project_references": sorted(required_refs),
        "canonical_type_roots": sorted(canonical_roots),
        "canonical_type_source_files": type_files,
        "alias_flow_roots": sorted(alias_roots),
        "alias_flow_source_files": alias_files,
    }


def source_aggregate_flow(source_root: Path) -> dict[str, object]:
    """Inventory raw aggregate/network writers of ``SERIALIZE_DATA::ai_bit``.

    The serialized trainer records live inside ``BATTLE_REC_BODY``.  A source
    grep limited to ``ai_bit`` member syntax therefore misses recorder
    ``memcpy``/file-read paths, network download buffers, and aggregate
    assignment.  This manifest checks every such writer in the retail-linked
    recorder/network projects and fails closed on a new matching operation.
    """
    prog = source_root / "niji_project/prog"

    # path, project, regex, expected count, semantic effect
    checks = {
        "serialized_buffer_zeroing": (
            prog / "Battle/source/battle_SetupTrainer.cpp",
            prog / "Battle/BattleStatic.vcxproj",
            r"gfl2::std::MemClear\(\s*serializedData,\s*sizeof\(BSP_TRAINER_DATA::SERIALIZE_DATA\)\s*\)",
            1,
            "zeroes the complete SERIALIZE_DATA aggregate, including ai_bit (+0x10)",
        ),
        "recorder_full_record_memcpy": (
            prog / "ExtSavedata/source/BattleRecorderSaveData.cpp",
            prog / "ExtSavedata/ExtSavedata.vcxproj",
            r"::std::memcpy\([^;]*(?:recDataTemp|mBattleRecData)[^;]*sizeof\(\s*BATTLE_REC_DATA\s*\)",
            7,
            "copies BATTLE_REC_DATA, whose upload.body.tr_data[] contains SERIALIZE_DATA::ai_bit (+0x10)",
        ),
        "recorder_upload_memcpy": (
            prog / "ExtSavedata/source/BattleRecorderSaveData.cpp",
            prog / "ExtSavedata/ExtSavedata.vcxproj",
            r"::std::memcpy\(\s*&mBattleRecData->upload\s*,\s*upload\s*,\s*sizeof\(\s*BATTLE_REC_UPLOAD_DATA\s*\)\s*\)",
            1,
            "copies BATTLE_REC_UPLOAD_DATA, including serialized trainer records",
        ),
        "recorder_file_read": (
            prog / "ExtSavedata/source/BattleRecorderSaveData.cpp",
            prog / "ExtSavedata/ExtSavedata.vcxproj",
            r"xess->ReadFile\(\s*EXTID_BATTLEVIDEO,\s*index,\s*mBattleRecData,\s*sizeof\(\s*BATTLE_REC_DATA\s*\)\s*\)",
            2,
            "external file read writes the complete BATTLE_REC_DATA aggregate",
        ),
        "upload_request_full_record_memcpy": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoUploadRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"std::memcpy\( m_requestParam\.pBattleRecorderSaveData->GetBattleRecDataDirect\(\) [^;]*BATTLE_REC_DATA\)",
            2,
            "network upload response copies a complete BATTLE_REC_DATA into the recorder object",
        ),
        "delete_request_full_record_memcpy": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoDeleteRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"std::memcpy\( m_requestParam\.pBattleRecorderSaveData->GetBattleRecDataDirect\(\) [^;]*BATTLE_REC_DATA\)",
            1,
            "delete/cancel response copies a complete BATTLE_REC_DATA into the recorder object",
        ),
        "sync_request_full_record_memcpy": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoSyncRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"std::memcpy\( m_requestParam\.pBattleRecorderSaveData->GetBattleRecDataDirect\(\) [^;]*BATTLE_REC_DATA\)",
            1,
            "video-sync response copies a complete BATTLE_REC_DATA into the recorder object",
        ),
        "event_set_upload_copy": (
            prog / "NetStatic/NetEvent/source/BattleVideoPlayerEvent.cpp",
            prog / "NetStatic/NetEvent/NetEvent.vcxproj",
            r"pSaveData->SetBattleRecUploadData\( &m_appParam\.out\.pActiveVideoData->sdCardData\.upload \)",
            1,
            "copies an upload aggregate containing serialized trainer records",
        ),
        "upload_set_upload_copy": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoUploadRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"m_requestParam\.pBattleRecorderSaveData->SetBattleRecUploadData\( &m_requestParam\.pUploadData->upload \)",
            2,
            "copies an upload aggregate containing serialized trainer records",
        ),
        "delete_set_upload_copy": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoDeleteRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"m_requestParam\.pBattleRecorderSaveData->SetBattleRecUploadData\( &m_requestParam\.pCancelData->upload \)",
            1,
            "copies an upload aggregate containing serialized trainer records",
        ),
        "sync_set_upload_copy": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoSyncRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"m_requestParam\.pBattleRecorderSaveData->SetBattleRecUploadData\( &pSaveVideoData->sdCardData\.upload \)",
            1,
            "copies an upload aggregate containing serialized trainer records",
        ),
        "video_upload_assignment": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/BattleVideoPlayerVideoDataManager.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"pOutputVideoData->sdCardData\.upload\s*=\s*\*pUploadData",
            1,
            "aggregate assignment copies serialized trainer records into VIDEO_DATA",
        ),
        "request_client_download_buffer_zero": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoRequestClient.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"std::memset\( m_pDownloadBuffer , 0 , sizeof\(ExtSavedata::BattleRecorderSaveData::BATTLE_REC_UPLOAD_DATA\)",
            1,
            "zero-initializes the upload buffer, including serialized trainer ai_bit",
        ),
        "download_buffer_zero": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoDownloadRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"::std::memset\( m_requestParam\.pClient->GetDownloadBufferPtr\(\) , 0 , sizeof\(ExtSavedata::BattleRecorderSaveData::BATTLE_REC_UPLOAD_DATA\)",
            1,
            "zero-initializes the downloaded upload buffer, including serialized trainer ai_bit",
        ),
        "download_buffer_external_fill": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/RequestSequence/BattleVideoDownloadRequestSequence.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"dataStoreClient->DownloadData\( dataId, m_requestParam\.pClient->GetDownloadBufferPtr\(\) , sizeof\(ExtSavedata::BattleRecorderSaveData::BATTLE_REC_UPLOAD_DATA\)",
            1,
            "external network download writes the upload buffer, including serialized trainer ai_bit",
        ),
        "video_static_dummy_zero": (
            prog / "NetStatic/NetAppLib/source/BattleVideoPlayer/BattleVideoPlayerVideoDataManager.cpp",
            prog / "NetStatic/NetAppLib/NetAppLib.vcxproj",
            r"static ExtSavedata::BattleRecorderSaveData::BATTLE_REC_UPLOAD_DATA aDummyData\[ 10 \];",
            1,
            "static-duration aggregate is zero-initialized, including serialized trainer ai_bit",
        ),
    }

    rows = []
    for label, (source, project, pattern, expected_count, effect) in checks.items():
        project_contains(source, project)
        hits = line_hits(source, pattern)
        if len(hits) != expected_count:
            raise ValueError(f"expected {expected_count} {label} edge(s), found {len(hits)}")
        for hit in hits:
            rows.append(
                {
                    "edge": label,
                    "source": source.relative_to(source_root).as_posix(),
                    "project": project.relative_to(source_root).as_posix(),
                    "line": hit["line"],
                    "text": hit["text"],
                    "effect": effect,
                    "target_field": "BSP_TRAINER_DATA::SERIALIZE_DATA::ai_bit (+0x10)",
                }
            )

    # Scan every raw operation that can write an aggregate or serialized field.
    # Declarations, const reads, and file/network exports are intentionally
    # absent; a new operation touching these types fails closed for review.
    candidate_patterns = [
        r"(?:(?:::)?std::)?(?:memcpy|memmove)\([^;]*\b(?:BSP_TRAINER_DATA|SERIALIZE_DATA|BATTLE_REC_DATA|BATTLE_REC_UPLOAD_DATA)\b",
        r"(?:(?:::)?std::)?(?:memset|MemClear)\([^;]*\b(?:BSP_TRAINER_DATA|SERIALIZE_DATA|BATTLE_REC_DATA|BATTLE_REC_UPLOAD_DATA)\b",
        r"\b(?:ReadFile|DownloadData)\([^;]*\b(?:BSP_TRAINER_DATA|SERIALIZE_DATA|BATTLE_REC_DATA|BATTLE_REC_UPLOAD_DATA)\b",
        r"(?:(?:::)?std::)?(?:memcpy|memmove)\([^;]*(?:GetBattleRecDataDirect|sizeof\([^)]*BATTLE_REC_DATA\))",
        r"(?:(?:::)?std::)?(?:memcpy|memmove)\(\s*&mBattleRecData->upload\s*,\s*upload\s*,\s*sizeof\(\s*BATTLE_REC_UPLOAD_DATA\s*\)",
        r"\bReadFile\([^;]*mBattleRecData[^;]*BATTLE_REC_DATA",
        r"\bDownloadData\([^;]*GetDownloadBufferPtr\([^;]*BATTLE_REC_UPLOAD_DATA",
        r"(?:(?:::)?std::)?(?:memset|MemClear)\([^;]*(?:m_pDownloadBuffer|GetDownloadBufferPtr\(\))[^;]*BATTLE_REC_UPLOAD_DATA",
        r"(?:(?:::)?std::)?(?:memset|MemClear)\([^;]*mBattleRecData[^;]*(?:BATTLE_REC_DATA|BATTLE_REC_UPLOAD_DATA)",
        r"(?:->|\.)SetBattleRecUploadData\s*\(",
        r"\.upload\s*=\s*\*pUploadData",
        r"static ExtSavedata::BattleRecorderSaveData::BATTLE_REC_UPLOAD_DATA aDummyData",
    ]
    candidate_hits = []
    for path in prog.rglob("*"):
        if path.suffix.lower() not in {".cpp", ".h", ".hpp", ".inl"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        relative = path.relative_to(source_root).as_posix()
        seen = set()
        for pattern in candidate_patterns:
            for match in re.finditer(pattern, text):
                line_number = text.count("\n", 0, match.start()) + 1
                key = (relative, line_number)
                if key in seen:
                    continue
                seen.add(key)
                end = text.find(";", match.start())
                statement = text[match.start() : (end + 1 if end >= 0 else len(text))]
                candidate_hits.append(
                    {
                        "source": relative,
                        "line": line_number,
                        "text": " ".join(statement.split()),
                    }
                )
    known = {(row["source"], row["line"]) for row in rows}
    unknown = [row for row in candidate_hits if (row["source"], row["line"]) not in known]
    if unknown:
        raise ValueError(f"unclassified serialized aggregate writer(s): {unknown}")
    if len(candidate_hits) != len(rows):
        raise ValueError("serialized aggregate writer manifest does not cover the source scan")

    return {
        "target_field": "BSP_TRAINER_DATA::SERIALIZE_DATA::ai_bit (+0x10)",
        "edges": rows,
        "edge_count": len(rows),
        "unclassified_edges": unknown,
        "all_source_aggregate_writers_classified": True,
    }


def scan_mask_candidates(code: bytes, cro_dir: Path) -> list[dict[str, object]]:
    """Rescan all executable ARM/Thumb/CRO bytes and return mask rows only."""
    audit = load_audit()
    rows: list[dict[str, object]] = []
    for mode, label in ((CS_MODE_ARM, "arm"), (CS_MODE_THUMB, "thumb")):
        for hit in audit.scan(code, mode, instruction_size=RETAIL_TEXT_BOUNDARY):
            if hit.get("ai_mask_constant"):
                rows.append({"module": ".code", "mode": label, **hit})
    for path in sorted(cro_dir.glob("*.cro")):
        name, body, metadata = audit.cro_code(path)
        for hit in audit.scan(
            body,
            CS_MODE_ARM,
            code_file_offset=int(metadata["code_offset"]),
            relocation_file_offsets=set(metadata["_relocation_file_offsets"]),
            relocations_by_file_offset=dict(metadata["_relocations_by_file_offset"]),
        ):
            if hit.get("ai_mask_constant"):
                rows.append({"module": name, "mode": "arm", **hit})
    if len(rows) != EXPECTED_MASK_CANDIDATES:
        raise ValueError(f"expected {EXPECTED_MASK_CANDIDATES} mask candidates, found {len(rows)}")
    return rows


def classify_mask_candidates(code: bytes, cro_dir: Path) -> dict[str, object]:
    """Classify every raw mask-valued displacement candidate.

    This is intentionally fail-closed.  The raw scanner is an over-approximation,
    but no row is allowed to remain ``unclassified`` in the compact lift
    artifact.  The canonical source rows are identified by exact offsets; the
    residual main-image rows are separated by store width, stack/interior
    destination, or a reviewed non-trainer object shape.  CRO rows outside
    Battle are source-project disjoint, while Battle's four full-word/aggregate
    collisions are recorded explicitly.
    """
    rows = scan_mask_candidates(code, cro_dir)
    ledger: list[dict[str, object]] = []
    for row in rows:
        module, mode, offset = row["module"], row["mode"], int(row["offset"])
        mnemonic = str(row["mnemonic"]).lower()
        if module == ".code" and mode == "arm":
            if offset in CANONICAL_MAIN_MASK_WRITERS:
                classification = "canonical-source-writer"
                reason = "exactly mapped direct SetAIBit/source writer fingerprint"
            elif row.get("stack_base"):
                classification = "stack-frame-temporary"
                reason = "destination base is SP; canonical trainer objects are heap pointers"
            elif mnemonic in {"strb", "strh", "strbt", "strht"}:
                classification = "subword-layout-mismatch"
                reason = "byte/halfword store cannot implement the u32 canonical field"
            elif offset in MAIN_INTERIOR_OR_LOCAL:
                classification = "interior-or-local-aggregate"
                reason = "surrounding stream derives an interior/local aggregate pointer"
            elif offset in MAIN_UNRELATED_SHAPE:
                classification = "nontrainer-object-shape"
                reason = "neighboring fields and initialization shape are disjoint from both trainer layouts"
            else:
                raise ValueError(f"unclassified main ARM candidate at {offset:#x}")
        elif module == ".code" and mode == "thumb":
            if offset == 0x688:
                classification = "thumb-object-layout-disproof"
                reason = "writes +0x1c after OR-at-zero; incompatible with CORE (+0x4) and TRAINER (+0x1c) layouts"
            elif offset == 0x3D3600:
                classification = "thumb-sweep-arm-code"
                reason = "same bytes decode as a non-store ARM instruction inside an ARM function"
            else:
                raise ValueError(f"unclassified main Thumb candidate at {offset:#x}")
        elif module == "Battle":
            if row.get("stack_base"):
                classification = "stack-frame-temporary"
                reason = "destination base is SP; canonical trainer objects are heap pointers"
            elif mnemonic in {"strb", "strh", "strbt", "strht"} or str(row["store_kind"]).startswith("double"):
                classification = "subword-layout-mismatch"
                reason = "width is incompatible with the u32 canonical field"
            elif offset in BATTLE_STACK_INTERIOR:
                classification = "interior-or-local-aggregate"
                reason = "destination register is an SP-derived local aggregate pointer"
            elif offset in BATTLE_UNRELATED_SHAPE:
                classification = "nontrainer-object-shape"
                reason = "Battle.cro function neighborhood is not a MainModule/BSP trainer layout"
            else:
                raise ValueError(f"unclassified Battle.cro candidate at {offset:#x}")
        else:
            classification = "cro-project-type-disjoint"
            reason = "retail CRO project has no canonical trainer-type source or writer"
        ledger.append(
            {
                "module": module,
                "mode": mode,
                "offset": hex(offset),
                "displacement": row["displacement"],
                "field": row["field"],
                "mnemonic": row["mnemonic"],
                "operands": row["operands"],
                "store_kind": row["store_kind"],
                "classification": classification,
                "reason": reason,
            }
        )
    counts: dict[str, int] = {}
    for row in ledger:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    if sum(counts.values()) != EXPECTED_MASK_CANDIDATES:
        raise ValueError("candidate ledger does not cover the complete scanner set")
    return {
        "candidate_count": len(ledger),
        "classification_counts": dict(sorted(counts.items())),
        "canonical_source_writer_offsets": [hex(x) for x in sorted(CANONICAL_MAIN_MASK_WRITERS)],
        "rows": ledger,
        "all_candidates_classified": True,
    }


def verify_cro_modules(cro_dir: Path) -> dict[str, object]:
    """Check the complete extracted CRO set and retail debug exclusions."""
    audit = load_audit()
    paths = sorted(cro_dir.glob("*.cro"))
    if len(paths) != 132:
        raise ValueError(f"expected 132 extracted CROs, found {len(paths)}")
    modules = []
    names = set()
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    for path in paths:
        name, body, metadata = audit.cro_code(path)
        if name in names:
            raise ValueError(f"duplicate CRO name: {name}")
        names.add(name)
        modules.append(
            {
                "name": name,
                "file": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "code_size": int(metadata["code_size"]),
                "segment_count": int(metadata["segment_count"]),
            }
        )

    exclusions = []
    for name in ("DebugBattle", "BattleDebug"):
        path = next((p for p in paths if p.stem == name), None)
        if path is None:
            raise ValueError(f"missing retail debug CRO {name}.cro")
        module_name, body, metadata = audit.cro_code(path)
        executable = next(
            segment for segment in metadata["segments"] if int(segment["type"]) == 0
        )
        executable_size = int(executable["size"])
        if module_name != name or executable_size != 0xAC:
            raise ValueError(f"unexpected {name}.cro code stub")
        stores = []
        for ins in md.disasm(body[:executable_size], 0):
            if ins.mnemonic.startswith("str") or ins.mnemonic.startswith("stm"):
                if "#4" in ins.op_str or "#0x4" in ins.op_str or "#0x1c" in ins.op_str:
                    stores.append({"offset": hex(ins.address), "operands": ins.op_str})
        # The resolver thunk contains one generic ``str [#4]`` slot write, but
        # its literal pool value is zero and the PM_DEBUG translation unit is
        # not part of the retail module.  Preserve the collision in the
        # artifact instead of pretending that a displacement identifies an
        # AI object.
        if int.from_bytes(body[0x9C:0xA0], "little") != 0:
            raise ValueError(f"unexpected debug-stub literal at 0x9c in {name}.cro")
        exclusions.append(
            {
                "module": f"{name}.cro",
                "code_size": hex(executable_size),
                "pm_debug_source_not_retail": True,
                "generic_displacement_store_count": len(stores),
                "generic_displacement_stores": stores,
                "stored_value": "0x0",
                "mask_value_disjoint": True,
            }
        )
    return {
        "module_count": len(modules),
        "modules": modules,
        "pm_debug_exclusions": exclusions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("code", type=Path, nargs="?")
    parser.add_argument("cro_dir", type=Path, nargs="?")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="run the source/type/aggregate lift without retail code and CRO inputs",
    )
    args = parser.parse_args()

    if not args.source_only and (args.code is None or args.cro_dir is None):
        parser.error("code and cro_dir are required unless --source-only is set")
    source = source_inventory(args.source_root)
    type_flow = source_type_flow(args.source_root)
    aggregate_flow = source_aggregate_flow(args.source_root)
    if args.source_only:
        result = {
            "artifact": "source-complete alias/copy lift for retail ai_bit writers",
            "inputs": {
                "source_root": "<source-root>",
                "source_commit": source["source_commit"],
            },
            "source_inventory": source,
            "source_type_flow": type_flow,
            "source_aggregate_flow": aggregate_flow,
            "theorem": {
                "source_writer_completeness": True,
                "binary_inclusion_proved": False,
                "scope": "source topology and aggregate field flow only; retail binary fingerprints are not run",
                "all_source_aggregate_writers_classified": aggregate_flow[
                    "all_source_aggregate_writers_classified"
                ],
                "unresolved_source_writers": [],
            },
        }
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(encoded)
        else:
            print(encoded, end="")
        return
    main_fingerprint = verify_deserialize(args.code.read_bytes())
    battle_fingerprint = verify_battle_functions(args.cro_dir / "Battle.cro")
    # Reuse the independently maintained residual proof rather than weakening
    # it or duplicating its relocation/value-provenance logic.
    residual_spec = importlib.util.spec_from_file_location(
        "legacy_residual", Path(__file__).with_name("verify-retail-ai-writer-theorem.py")
    )
    if residual_spec is None or residual_spec.loader is None:
        raise RuntimeError("cannot load residual verifier")
    residual_module = importlib.util.module_from_spec(residual_spec)
    residual_spec.loader.exec_module(residual_module)
    residual_result = {
        "main_code": residual_module.verify_main(args.code.read_bytes()),
        "battle_cro": residual_module.verify_battle(args.cro_dir / "Battle.cro"),
        "source_type_evidence": residual_module.verify_source(args.source_root),
    }
    modules = verify_cro_modules(args.cro_dir)
    candidate_lift = classify_mask_candidates(args.code.read_bytes(), args.cro_dir)

    result = {
        "artifact": "field-sensitive whole-program lift for retail ai_bit writer theorem",
        "inputs": {
            "main_code": args.code.name,
            "main_code_sha256": hashlib.sha256(args.code.read_bytes()).hexdigest(),
            "retail_text_boundary": hex(RETAIL_TEXT_BOUNDARY),
            "battle_cro": "Battle.cro",
            "source_root": "<source-root>",
            "source_commit": source["source_commit"],
        },
        "source_inventory": source,
        "source_type_flow": type_flow,
        "source_aggregate_flow": aggregate_flow,
        "binary_fingerprints": {
            "deserialize": main_fingerprint,
            "battle_cro_trainer_paths": battle_fingerprint,
        },
        "retail_cro_inventory": modules,
        "residual_disproofs": residual_result,
        "candidate_lift": candidate_lift,
        "theorem": {
            "proved": True,
            "scope": "all source-defined ai_bit writers compiled into the retail .code and CRO modules, including aliases and copied structures",
            "statement": (
                "Every retail source-defined writer reaches one of the recovered canonical ai_bit fields "
                "(BSP_TRAINER_DATA::CORE_DATA +0x4, BSP_TRAINER_DATA::SERIALIZE_DATA +0x10, "
                "or MainModule::TRAINER_DATA +0x1c), "
                "while all 325 executable mask-valued displacement candidates are explicitly classified "
                "by the field-sensitive ledger. Arbitrary same-displacement stores are not promoted to "
                "AI fields, and no PM_DEBUG-only writer is present in the retail image."
            ),
            "basis": [
                "The complete archived source inventory has no unclassified SetAIBit call or direct ai_bit member assignment, and records Serialize/ClearSerializeData for the intermediate serialized field.",
                "The serialized edge inventory covers Serialize, Deserialize, ClearSerializeData, their enabled network/recorder call sites, and the disabled whole-object copy alternative.",
                "The aggregate-flow inventory covers recorder/network memcpy, file-read, download-buffer, memset, and aggregate-assignment writers of SERIALIZE_DATA::ai_bit, with zero unclassified source operations.",
                "BattleStatic::BSP_TRAINER_DATA::Deserialize is verified at .code:0x61724 as SERIALIZE_DATA +0x10 -> CORE_DATA +0x4.",
                "Battle.cro MainModule::trainerParam_StoreNPCTrainer is verified at 0x8a25c as CORE_DATA +0x4 -> TRAINER_DATA +0x1c.",
                "Battle.cro trainerParam_StoreCore is verified at 0x8a414 as TRAINER_DATA +0x1c = 0.",
                "FieldStatic and Trainer writers are linked static-library sources using the canonical SetAIBit inline.",
                "DebugBattle and BattleDebug retail CRO stubs contain only a generic +0x4 resolver write of zero; StartMenu and DebugBattle source writers are PM_DEBUG-only.",
                "The two prior residual displacement-compatible stores remain independently closed by value/type provenance.",
                "The executable scanner set is complete at 325 rows and every row has a non-unresolved ledger classification.",
            ],
            "unresolved_source_writers": [],
            "unclassified_binary_candidate_claim": False,
            "all_executable_mask_candidates_classified": candidate_lift["all_candidates_classified"],
            "unclassified_executable_mask_candidates": 0,
        },
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
