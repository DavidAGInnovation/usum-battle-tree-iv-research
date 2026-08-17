#!/usr/bin/env python3
"""Enumerate ARM store candidates using source-defined ``ai_bit`` offsets.

This is a deliberately conservative *candidate* audit.  In the retail
source, ``BSP_TRAINER_DATA::CORE_DATA::ai_bit`` is at offset ``0x4`` and
``MainModule::TRAINER_DATA::ai_bit`` is at offset ``0x1c``. A literal
``str/strb/strh``, ``strd``, or register-list store whose effective address
reaches either value is therefore worth reviewing, but the displacement alone
does not identify the pointee: both offsets occur in stack frames and unrelated
structures. The script reports all such candidates in the extracted CRO code
segments and in the raw ExeFS ``.code`` section. It never silently classifies a
candidate as an AI-mask writer.

The output is evidence for the boundary of a whole-binary data-flow proof,
not that proof itself.  The CRO pass records relocation-backed literal loads
and a deliberately local register-provenance class; aliases, copied
structures, and the ARM/Thumb interprocedural function graph still have to be
resolved before a writer can be declared (or ruled out) as an ``ai_bit``
writer.  For the main image, ``--main-text-size`` can be set from the retail
NCCH ExHeader so read-only/data bytes appended to the raw ExeFS ``.code`` do
not inflate the executable candidate set.
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
    ARM_INS_STRD,
    ARM_INS_STREX,
    ARM_INS_STREXB,
    ARM_INS_STREXH,
    ARM_INS_STM,
    ARM_INS_STMDA,
    ARM_INS_STMDB,
    ARM_INS_STMIB,
    ARM_INS_STRH,
    ARM_INS_STRHT,
    ARM_INS_STRT,
    ARM_OP_MEM,
    ARM_REG_PC,
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
STORE_MULTI_IDS = {ARM_INS_STM, ARM_INS_STMDA, ARM_INS_STMDB, ARM_INS_STMIB}

FIELDS = {
    "BSP_TRAINER_DATA::CORE_DATA::ai_bit": 0x4,
    "MainModule::TRAINER_DATA::ai_bit": 0x1C,
}
FIELD_BY_OFFSET = {offset: name for name, offset in FIELDS.items()}
# Composite values emitted by the source-level selectors.  Single-bit values
# are deliberately excluded: they occur too often in unrelated structures to
# be useful as an AI-mask discriminator.
AI_MASK_VALUES = {0x107, 0x10F, 0x125, 0x127, 0x007, 0x008, 0x040, 0x00F}


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
    relocations_by_file_offset = {
        int(row["target_file_offset"]): {
            "type": row["type"],
            "referred_segment": row["referred_segment"],
            "addend": row["addend"],
        }
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
        "_relocations_by_file_offset": relocations_by_file_offset,
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
    instruction_size: int | None = None,
    limit: int | None = None,
    code_file_offset: int = 0,
    relocation_file_offsets: set[int] | None = None,
    relocations_by_file_offset: dict[int, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    md = Cs(CS_ARCH_ARM, mode)
    md.detail = True
    # The main ExeFS section is a stripped mixed code/data image.  Continue
    # across undecodable bytes so a bad decode at one veneer does not make the
    # rest of the candidate sweep silently disappear.
    md.skipdata = True
    rows: list[dict[str, object]] = []
    instruction_bytes = code if instruction_size is None else code[:instruction_size]
    instructions = list(md.disasm(instruction_bytes, 0))

    def reg_name(reg: int) -> str:
        return md.reg_name(reg).lower()

    def provenance(index: int) -> dict[str, dict[str, object]]:
        """Track only local ARM register copies and literal relocations.

        This intentionally stops at calls/branches and treats unknown loads,
        globals, and incoming arguments as opaque.  It is a sound *classifier*
        for the evidence boundary, not an alias analysis: ``arg0`` and a
        relocation-derived pointer still do not identify a C++ object type.
        """
        start = max(0, index - 96)
        # Incoming argument facts are sound only when the local window starts
        # at the image boundary.  At an arbitrary interior instruction the
        # preceding prologue/call may have reassigned every register, so start
        # with no facts and report ``unknown`` instead of guessing.
        state: dict[str, dict[str, object]] = (
            {f"r{i}": {"kind": "function-arg", "arg": i} for i in range(4)}
            if start == 0 else {}
        )
        for j in range(start, index + 1):
            ins = instructions[j]
            if ins.id == 0:  # Capstone skipdata pseudo-instruction.
                continue
            mnemonic = ins.mnemonic.lower()
            ops = ins.operands
            if mnemonic == "push" and any(reg_name(op.reg) == "lr" for op in ops if op.type == 1):
                # A conventional ARM/Thumb prologue starts a function with
                # PUSH {...,lr}; restore the incoming argument facts here.
                state = {f"r{i}": {"kind": "function-arg", "arg": i} for i in range(4)}
                continue
            if j < index and mnemonic in {"bl", "blx"}:
                # A conforming ARM call preserves r4-r11; invalidate only
                # caller-saved facts while retaining constants held in the
                # callee-saved registers used by compiler-generated structs.
                state = {name: value for name, value in state.items() if name not in {"r0", "r1", "r2", "r3", "r12", "lr"}}
                continue
            if j < index and mnemonic in {"b", "bx"}:
                # Conditional branches preserve register facts on the local
                # fall-through path.  Unconditional transfers/calls may leave
                # the local block, so discard facts rather than inventing a
                # cross-block alias.
                state = {}
                continue
            if j < index and mnemonic == "pop":
                # A linear sweep can encounter a return block before a
                # conditional sibling that shares the same prologue. Keep the
                # facts here as an over-approximation so that sibling stores
                # are not lost; the resulting rows remain candidates until
                # object identity is established.
                continue
            if (mnemonic in {"mov", "movs"} or (mnemonic.startswith("mov") and mnemonic not in {"movw", "movt", "mvn", "mvns"})) and len(ops) >= 2 and ops[0].type == 1:
                dst = reg_name(ops[0].reg)
                src = reg_name(ops[1].reg) if ops[1].type == 1 else None
                if src is not None and src in state:
                    state[dst] = {**state[src], "via": f"{mnemonic} {src}"}
                elif ops[1].type == 2:
                    state[dst] = {
                        "kind": "immediate-constant",
                        "value": ops[1].imm & 0xFFFFFFFF,
                    }
                else:
                    state.pop(dst, None)
                continue
            if mnemonic in {"mvn", "mvns"} and len(ops) >= 2 and ops[0].type == 1:
                dst = reg_name(ops[0].reg)
                if ops[1].type == 2:
                    state[dst] = {"kind": "immediate-constant", "value": (~ops[1].imm) & 0xFFFFFFFF}
                else:
                    state.pop(dst, None)
                continue
            if mnemonic in {"movw", "movt"} and len(ops) >= 2 and ops[0].type == 1:
                dst = reg_name(ops[0].reg)
                if ops[1].type == 2:
                    old = int(state.get(dst, {}).get("value", 0))
                    value = ((old & 0xFFFF) | (ops[1].imm << 16)) if mnemonic == "movt" else ((old & 0xFFFF0000) | ops[1].imm)
                    state[dst] = {"kind": "immediate-constant", "value": value & 0xFFFFFFFF}
                else:
                    state.pop(dst, None)
                continue
            if mnemonic in {"add", "adds", "sub", "subs"} and len(ops) >= 3 and ops[0].type == 1 and ops[1].type == 1:
                dst, src = reg_name(ops[0].reg), reg_name(ops[1].reg)
                if src in state and ops[2].type == 2:
                    state[dst] = {**state[src], "via": f"{mnemonic} {ops[2].imm}"}
                else:
                    state.pop(dst, None)
                continue
            if mnemonic in {"orr", "orrs", "add", "adds", "sub", "subs", "and", "ands", "bic", "bics"} and len(ops) >= 3 and ops[0].type == 1 and ops[1].type == 1:
                dst, left = reg_name(ops[0].reg), state.get(reg_name(ops[1].reg), {}).get("value")
                right = ops[2].imm if ops[2].type == 2 else state.get(reg_name(ops[2].reg), {}).get("value")
                if right is not None and ops[2].type == 1 and ops[2].shift.type:
                    if ops[2].shift.type == 2:  # LSL
                        right = (right << ops[2].shift.value) & 0xFFFFFFFF
                    elif ops[2].shift.type == 3:  # LSR
                        right = (right & 0xFFFFFFFF) >> ops[2].shift.value
                    elif ops[2].shift.type == 1:  # ASR
                        signed = right if right < 0x80000000 else right - 0x100000000
                        right = (signed >> ops[2].shift.value) & 0xFFFFFFFF
                if left is None or right is None:
                    state.pop(dst, None)
                elif mnemonic.startswith("orr"):
                    state[dst] = {"kind": "computed-constant", "value": (left | right) & 0xFFFFFFFF}
                elif mnemonic.startswith("add"):
                    state[dst] = {"kind": "computed-constant", "value": (left + right) & 0xFFFFFFFF}
                elif mnemonic.startswith("sub"):
                    state[dst] = {"kind": "computed-constant", "value": (left - right) & 0xFFFFFFFF}
                elif mnemonic.startswith("and"):
                    state[dst] = {"kind": "computed-constant", "value": left & right}
                else:
                    state[dst] = {"kind": "computed-constant", "value": left & (~right)}
                continue
            if mnemonic in {"ldr", "ldrb", "ldrh"} and len(ops) >= 2 and ops[0].type == 1 and ops[1].type == 3:
                dst = reg_name(ops[0].reg)
                mem = ops[1].mem
                if mem.base == ARM_REG_PC:  # ARM PC; literal pool load.
                    literal = (ins.address + 8 + mem.disp) if mode == CS_MODE_ARM else (((ins.address + 4) & ~3) + mem.disp)
                    file_offset = code_file_offset + literal
                    rel = (relocations_by_file_offset or {}).get(file_offset)
                    if rel is not None:
                        state[dst] = {
                            "kind": "relocation-derived",
                            "literal_file_offset": hex(file_offset),
                            **rel,
                        }
                    elif 0 <= literal <= len(code) - 4:
                        state[dst] = {
                            "kind": "literal-constant",
                            "value": struct.unpack_from("<I", code, literal)[0],
                            "literal_file_offset": hex(file_offset),
                        }
                    else:
                        state.pop(dst, None)
                elif reg_name(mem.base) in state:
                    state[dst] = {
                        "kind": "memory-derived",
                        "base": reg_name(mem.base),
                        "displacement": hex(mem.disp),
                    }
                else:
                    state.pop(dst, None)
                continue
            # A write to a register from any other instruction invalidates its
            # local fact.  Keep this conservative and avoid modelling flags,
            # register lists, or compiler-specific idioms here.
            if ops and ops[0].type == 1 and mnemonic not in {"str", "strb", "strh", "strd", "strex", "strexb", "strexh", "stm", "stmia", "stmib", "stmda", "stmdb"}:
                state.pop(reg_name(ops[0].reg), None)
        return state

    for index, ins in enumerate(instructions):
        # Normalize scalar stores, double-word stores, and register-list stores
        # into (base register, field displacement, value register) tuples.
        candidates: list[tuple[int, int, int, str]] = []
        if ins.id in STORE_IDS and len(ins.operands) >= 2:
            mem = ins.operands[1]
            if mem.type == ARM_OP_MEM:
                candidates.append((mem.mem.base, mem.mem.disp, ins.operands[0].reg, "scalar"))
        elif ins.id == ARM_INS_STRD and len(ins.operands) >= 3:
            mem = ins.operands[2]
            if mem.type == ARM_OP_MEM:
                # STRD writes the first register at disp and the second at
                # disp+4 on the little-endian ARM retail target.
                candidates.append((mem.mem.base, mem.mem.disp, ins.operands[0].reg, "double-low"))
                candidates.append((mem.mem.base, mem.mem.disp + 4, ins.operands[1].reg, "double-high"))
        elif ins.id in STORE_MULTI_IDS and len(ins.operands) >= 2:
            base_reg = ins.operands[0].reg
            regs = sorted(op.reg for op in ins.operands[1:] if op.type == 1)
            mnemonic = ins.mnemonic.lower()
            if "ib" in mnemonic:
                first_offset = 4
            elif "db" in mnemonic:
                first_offset = -4 * len(regs)
            elif "da" in mnemonic:
                first_offset = -4 * (len(regs) - 1)
            else:  # STM/IA: increment after.
                first_offset = 0
            candidates.extend(
                (base_reg, first_offset + 4 * slot, reg, "register-list")
                for slot, reg in enumerate(regs)
            )
        else:
            continue

        for base_reg, displacement, value_reg, store_kind in candidates:
            if displacement not in FIELD_BY_OFFSET:
                continue
            mem_base = base_reg
            field = FIELD_BY_OFFSET[displacement]
            state = provenance(index)
            source = state.get(reg_name(value_reg), {"kind": "unknown"})
            base = {"kind": "stack-pointer"} if mem_base == ARM_REG_SP else state.get(reg_name(mem_base), {"kind": "unknown"})
            rows.append(
                {
                    "offset": ins.address,
                    "displacement": hex(displacement),
                    "field": field,
                    "mnemonic": ins.mnemonic,
                    "operands": ins.op_str,
                    "store_kind": store_kind,
                    "stack_base": mem_base == ARM_REG_SP,
                    "bytes": ins.bytes.hex(),
                    "relocation_at_instruction": (
                        relocation_file_offsets is not None
                        and code_file_offset + ins.address in relocation_file_offsets
                    ),
                    "base_provenance": base,
                    "value_provenance": source,
                    "ai_mask_constant": (
                        source.get("value") in AI_MASK_VALUES
                        if source.get("kind") in {"immediate-constant", "literal-constant", "computed-constant"}
                        else False
                    ),
                }
            )
            if limit is not None and len(rows) >= limit:
                return rows
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("code", type=Path, help="extracted raw ExeFS .code")
    parser.add_argument("cro_dir", type=Path, help="directory of extracted CRO files")
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--main-text-size",
        type=lambda value: int(value, 0),
        default=None,
        help="scan only this many bytes as executable text in the main .code image",
    )
    args = parser.parse_args()

    code = args.code.read_bytes()
    rows: list[dict[str, object]] = []

    # The main ExeFS section is mixed ARM/Thumb and stripped.  Both linear
    # sweeps are retained as over-approximations and labelled by mode.
    for mode, label in ((CS_MODE_ARM, "arm"), (CS_MODE_THUMB, "thumb")):
        hits = scan(
            code,
            mode,
            instruction_size=args.main_text_size,
            limit=args.limit,
        )
        rows.append(
            {
                "module": ".code",
                "mode": label,
                "code_sha256": sha256(code),
                "code_size": len(code),
                "instruction_size": args.main_text_size,
                "hits": hits,
                "hit_count": len(hits),
                "stack_base_hits": sum(bool(x["stack_base"]) for x in hits),
                "field_counts": {
                    field: sum(x["field"] == field for x in hits) for field in FIELDS
                },
                "ai_mask_constant_candidates": sum(bool(x["ai_mask_constant"]) for x in hits),
                "ai_mask_constant_by_value": dict(
                    sorted(
                        Counter(
                            hex(int(x["value_provenance"]["value"]))
                            for x in hits
                            if x["ai_mask_constant"]
                        ).items()
                    )
                ),
                "ai_mask_constant_by_provenance": dict(
                    sorted(
                        Counter(
                            x["value_provenance"]["kind"]
                            for x in hits
                            if x["ai_mask_constant"]
                        ).items()
                    )
                ),
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
            relocations_by_file_offset=dict(metadata["_relocations_by_file_offset"]),
        )
        metadata.pop("_relocation_file_offsets", None)
        metadata.pop("_relocations_by_file_offset", None)
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
                "ai_mask_constant_candidates": sum(bool(x["ai_mask_constant"]) for x in hits),
                "ai_mask_constant_by_value": dict(
                    sorted(
                        Counter(
                            hex(int(x["value_provenance"]["value"]))
                            for x in hits
                            if x["ai_mask_constant"]
                        ).items()
                    )
                ),
                "ai_mask_constant_by_provenance": dict(
                    sorted(
                        Counter(
                            x["value_provenance"]["kind"]
                            for x in hits
                            if x["ai_mask_constant"]
                        ).items()
                    )
                ),
                "truncated": args.limit is not None and len(hits) >= args.limit,
            }
        )

    result = {
        "fields": {name: hex(offset) for name, offset in FIELDS.items()},
        "mode": "relocation-aware local provenance classification; not alias-complete",
        "main_code_relocations": "unavailable: ExeFS .code is a stripped mapped image, not a CRO",
        "main_code_text_size": args.main_text_size,
        "provenance_counts": dict(
            sorted(
                Counter(
                    hit["base_provenance"]["kind"]
                    for module in rows
                    for hit in module["hits"]
                ).items()
            )
        ),
        "ai_mask_constant_candidate_count": sum(
            bool(hit["ai_mask_constant"]) for module in rows for hit in module["hits"]
        ),
        "ai_mask_constant_by_value": dict(
            sorted(
                Counter(
                    hex(int(hit["value_provenance"]["value"]))
                    for module in rows
                    for hit in module["hits"]
                    if hit["ai_mask_constant"]
                ).items()
            )
        ),
        "ai_mask_constant_by_provenance": dict(
            sorted(
                Counter(
                    hit["value_provenance"]["kind"]
                    for module in rows
                    for hit in module["hits"]
                    if hit["ai_mask_constant"]
                ).items()
            )
        ),
        "candidate_counts": {
            "main_code_arm": rows[0]["hit_count"],
            "main_code_thumb": rows[1]["hit_count"],
            "cro_arm": sum(row["hit_count"] for row in rows[2:]),
            "all_store_forms": sum(row["hit_count"] for row in rows),
        },
        "store_kind_counts": dict(
            sorted(
                Counter(
                    hit["store_kind"] for module in rows for hit in module["hits"]
                ).items()
            )
        ),
        "modules": rows,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_path:
        args.json_path.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
