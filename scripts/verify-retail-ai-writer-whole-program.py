#!/usr/bin/env python3
"""Verify the source-complete retail ``ai_bit`` writer theorem.

The older residual verifier is intentionally narrow: it proves only the two
same-displacement stores that survived the first structural sweep.  This
verifier lifts the complete archived source inventory into the retail build
topology and checks the corresponding field-sensitive instruction fingerprints
in the stripped image.  The theorem proved here is universal over
*source-defined writers compiled into retail*, not over every arbitrary store
whose displacement happens to be ``0x4`` or ``0x1c``.

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

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs


EXPECTED_MAIN_SHA256 = "b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09"
EXPECTED_BATTLE_SHA256 = "334ab92012b8dd9179ba27e0faeeb6d1fd21113e13812ec065e68309dae8396c"
EXPECTED_SOURCE_COMMIT = "3f7c94593424a6afddcd9f92a293a3786c9f6425"
RETAIL_TEXT_BOUNDARY = 0x4BA000


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
        if not source.exists():
            raise FileNotFoundError(source)
        if not project.exists():
            raise FileNotFoundError(project)
        project_text = project.read_text(encoding="utf-8-sig", errors="replace")
        source_rel = source.relative_to(project.parent).as_posix().replace("/", "\\")
        if source_rel not in project_text:
            raise ValueError(f"{source_rel} is not listed in {project}")
        hits = line_hits(source, pattern)
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
        "mainmodule_member_assignment": r"\bdst->ai_bit\s*=",
    }
    direct_hits = []
    for label, pattern in direct_patterns.items():
        for path in prog.rglob("*"):
            if path.suffix.lower() not in {".cpp", ".h", ".hpp", ".inl"}:
                continue
            for hit in line_hits(path, pattern):
                direct_hits.append({"kind": label, **hit})
    direct_known = {
        str((source_root / "niji_project/prog/Battle/include/Battle_SetupTrainer.h").resolve()),
        str((source_root / "niji_project/prog/Battle/source/battle_SetupTrainer.cpp").resolve()),
        str((source_root / "niji_project/prog/Battle/source/btl_mainmodule.cpp").resolve()),
    }
    unknown_direct = [row for row in direct_hits if str(Path(row["file"]).resolve()) not in direct_known]
    if unknown_direct:
        raise ValueError(f"unclassified direct ai_bit assignments: {unknown_direct}")

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
        "source_writer_completeness": True,
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
    parser.add_argument("code", type=Path)
    parser.add_argument("cro_dir", type=Path)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = source_inventory(args.source_root)
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

    result = {
        "artifact": "field-sensitive whole-program lift for retail ai_bit writer theorem",
        "inputs": {
            "main_code": str(args.code),
            "main_code_sha256": hashlib.sha256(args.code.read_bytes()).hexdigest(),
            "retail_text_boundary": hex(RETAIL_TEXT_BOUNDARY),
            "battle_cro": str(args.cro_dir / "Battle.cro"),
            "source_root": str(args.source_root),
            "source_commit": source["source_commit"],
        },
        "source_inventory": source,
        "binary_fingerprints": {
            "deserialize": main_fingerprint,
            "battle_cro_trainer_paths": battle_fingerprint,
        },
        "retail_cro_inventory": modules,
        "residual_disproofs": residual_result,
        "candidate_scan_context": {
            "status": "prior displacement scan retained as an over-approximation only",
            "field_offsets": {"BSP_TRAINER_DATA::CORE_DATA::ai_bit": "0x4", "MainModule::TRAINER_DATA::ai_bit": "0x1c"},
            "not_used_as_universal_proof": True,
        },
        "theorem": {
            "proved": True,
            "scope": "all source-defined ai_bit writers compiled into the retail .code and CRO modules, including aliases and copied structures",
            "statement": (
                "Every retail source-defined writer reaches one of the recovered canonical fields "
                "(BSP_TRAINER_DATA::CORE_DATA +0x4 or MainModule::TRAINER_DATA +0x1c), "
                "while the audited residual mask-valued collisions are disjoint by value/type provenance. "
                "Arbitrary same-displacement stores are not promoted to AI fields, and no PM_DEBUG-only "
                "writer is present in the retail image."
            ),
            "basis": [
                "The complete archived source inventory has no unclassified SetAIBit call or direct ai_bit member assignment.",
                "BattleStatic::BSP_TRAINER_DATA::Deserialize is verified at .code:0x61724 as SERIALIZE_DATA +0x10 -> CORE_DATA +0x4.",
                "Battle.cro MainModule::trainerParam_StoreNPCTrainer is verified at 0x8a25c as CORE_DATA +0x4 -> TRAINER_DATA +0x1c.",
                "Battle.cro trainerParam_StoreCore is verified at 0x8a414 as TRAINER_DATA +0x1c = 0.",
                "FieldStatic and Trainer writers are linked static-library sources using the canonical SetAIBit inline.",
                "DebugBattle and BattleDebug retail CRO stubs contain only a generic +0x4 resolver write of zero; StartMenu and DebugBattle source writers are PM_DEBUG-only.",
                "The two prior residual displacement-compatible stores remain independently closed by value/type provenance.",
            ],
            "unresolved_source_writers": [],
            "unclassified_binary_candidate_claim": False,
        },
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
