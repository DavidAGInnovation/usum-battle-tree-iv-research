#!/usr/bin/env python3
"""Verify the structural disproof for the Thumb collision at 0x688.

The check verifies the exact retail instruction sequence: the candidate's
function treats offset 0 as a bitfield, stores 8 at +0x1c, and branches to a
helper that consumes a +0x24 payload.  That behavior is incompatible with the
two recovered source layouts, whose offset-0 fields are respectively a pointer
and ``tr_id``.  The separate residual-store verifier closes the two exact
stores that survived this local layout check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs


EXPECTED_CODE_SHA256 = "b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09"


def disassemble(code: bytes, start: int, end: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    return list(md.disasm(code[start:end], start))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("code", type=Path, help="raw extracted retail ExeFS .code")
    args = ap.parse_args()

    code = args.code.read_bytes()
    digest = hashlib.sha256(code).hexdigest()
    if digest != EXPECTED_CODE_SHA256:
        raise SystemExit(
            f"unexpected .code SHA-256: {digest}; expected {EXPECTED_CODE_SHA256}"
        )

    rows = disassemble(code, 0x67C, 0x690)
    by_address = {ins.address: ins for ins in rows}
    required = {
        0x67C: ("ldr", "r3, [r0]"),
        0x682: ("orrs", "r3, r4"),
        0x684: ("str", "r3, [r0]"),
        0x686: ("movs", "r3, #8"),
        0x688: ("str", "r3, [r0, #0x1c]"),
        0x68E: ("b", "#0x5fc"),
    }
    for address, (mnemonic, operands) in required.items():
        ins = by_address.get(address)
        if ins is None or ins.mnemonic != mnemonic or ins.op_str != operands:
            got = None if ins is None else (ins.mnemonic, ins.op_str)
            raise SystemExit(
                f"unexpected Thumb instruction at {address:#x}: {got!r}; "
                f"expected {(mnemonic, operands)!r}"
            )

    helper_rows = disassemble(code, 0x614, 0x634)
    helper_text = [(ins.address, ins.mnemonic, ins.op_str) for ins in helper_rows]
    if not any(
        address == 0x616 and mnemonic == "adds" and operands == "r5, #0x24"
        for address, mnemonic, operands in helper_text
    ):
        raise SystemExit("the branch target does not show the expected +0x24 payload")

    result = {
        "code_sha256": digest,
        "candidate": {
            "offset": "0x688",
            "function_start": "0x5fc",
            "store": "str r3, [r0, #0x1c]",
            "surrounding_behavior": [
                "[r0] is loaded, ORed with 0x20, and written back",
                "8 is stored at +0x1c",
                "the branch target builds a payload at +0x24",
            ],
        },
        "source_layouts": {
            "MainModule::TRAINER_DATA": {
                "offset_0": "playerStatus pointer",
                "ai_bit": "+0x1c",
            },
            "BSP_TRAINER_DATA::CORE_DATA": {
                "offset_0": "tr_id",
                "ai_bit": "+0x4",
            },
        },
        "verdict": (
            "0x688 is not a writer for either source-defined ai_bit layout; "
            "the remaining exact displacement stores are classified by "
            "verify-proof-boundary-separation.py."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
