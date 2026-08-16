#!/usr/bin/env python3
"""Audit control-flow coverage of the retail Battle AI Pawn disassemblies.

This is deliberately an abstract audit.  It follows every statically encoded
branch and call target, but treats native return values and computed Pawn
values as unknown.  It therefore proves coverage of the decoded control-flow
graph, not the concrete tactical result for every battle state.
"""

from __future__ import annotations

import argparse
import re
from collections import deque
from pathlib import Path


LINE = re.compile(r"^([0-9a-f]+)\s+([a-z0-9_.]+)(?:\s+([0-9a-f]+))?\s*$", re.I)

COND = {
    "jzer", "jnz", "jeq", "jneq", "jsless", "jsleq", "jsgrtr", "jsgeq",
}
TERMINAL = {"halt", "ret", "retn", "retn.ovl"}


TABLE_ROW = re.compile(r"^\s+([0-9a-f]+)\s+([0-9a-f]+)\s*$", re.I)


def parse(path: Path):
    ins = {}
    table_targets = set()
    in_code = True
    for raw in path.read_text(errors="replace").splitlines():
        if raw.startswith(";DATA"):
            in_code = False
        if not in_code:
            continue
        row = TABLE_ROW.match(raw.rstrip())
        if row:
            # casetbl rows contain (case value, absolute target).  Including
            # every row is a sound may-reachability approximation when the
            # selector value is not symbolically known.
            table_targets.add(int(row.group(2), 16))
            continue
        # Case-table rows are indented and look like two hexadecimal numbers;
        # only the left-margin instruction rows are code.
        m = LINE.match(raw.rstrip())
        if not m:
            continue
        addr, op, arg = m.groups()
        ins[int(addr, 16)] = (op.lower(), int(arg, 16) if arg else None)
    return ins, table_targets


def successors(addr, op, arg, ins, procs, table_targets):
    ordered = sorted(ins)
    nxt = ordered[ordered.index(addr) + 1] if addr != ordered[-1] else None
    if op in TERMINAL:
        return []
    if op == "jump":
        return [arg] if arg in ins else []
    if op in COND:
        out = [arg] if arg in ins else []
        if nxt is not None:
            out.append(nxt)
        return out
    if op == "switch":
        out = [x for x in table_targets if x in ins]
        if arg in ins:
            out.append(arg)
        return out
    # Calls are represented as an interprocedural edge plus the return edge.
    # This is a may-reachability graph, so it is sound for finding any decoded
    # branch or writer reachable from the script entry point.
    if op in {"call", "call.ovl"}:
        out = [arg] if arg in ins else []
        if nxt is not None:
            out.append(nxt)
        return out
    if op == "call.pri":
        # The target is held in a Pawn register.  Without evaluating the
        # preceding expression, conservatively connect it to every procedure
        # entry.  This is an over-approximation, but it prevents an indirect
        # dispatch from hiding a branch or writer from the audit.
        out = list(procs)
        if nxt is not None:
            out.append(nxt)
        return out
    if nxt is not None:
        return [nxt]
    return []


def audit(path: Path):
    ins, table_targets = parse(path)
    if not ins:
        raise ValueError(f"no code instructions in {path}")
    procs = [a for a, (op, _) in ins.items() if op == "proc"]
    entry = procs[3] if len(procs) > 3 else procs[0]
    seen = set()
    queue = deque([entry])
    while queue:
        addr = queue.popleft()
        if addr in seen or addr not in ins:
            continue
        seen.add(addr)
        op, arg = ins[addr]
        queue.extend(successors(addr, op, arg, ins, procs, table_targets))

    branch_ops = COND | {"jump"}
    branches = {a: ins[a] for a in seen if ins[a][0] in branch_ops}
    all_branches = {a: ins[a] for a in ins if ins[a][0] in branch_ops}
    ai_cmd_calls = [a for a in seen if ins[a] == ("call", 0x8)]
    score_calls = [a for a in seen if ins[a] == ("call", 0x5C)]
    poke_writes = [a for a in seen if ins[a] == ("stor.pri", 8)]
    native_calls = [a for a in seen if ins[a][0].startswith("sysreq")]
    unreachable = sorted(set(ins) - seen)
    return {
        "file": path.name,
        "entry": entry,
        "instructions": len(ins),
        "reachable": len(seen),
        "unreachable": unreachable,
        "branches": len(branches),
        "conditional": sum(ins[a][0] in COND for a in branches),
        "unconditional": sum(ins[a][0] == "jump" for a in branches),
        "static_conditional": sum(ins[a][0] in COND for a in all_branches),
        "static_unconditional": sum(ins[a][0] == "jump" for a in all_branches),
        "ai_cmd_calls": len(ai_cmd_calls),
        "score_calls": len(score_calls),
        "poke_writes": len(poke_writes),
        "native_calls": len(native_calls),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lst_dir", type=Path)
    args = ap.parse_args()
    rows = [audit(p) for p in sorted(args.lst_dir.glob("*.lst"), key=lambda p: int(p.stem))]
    if not rows:
        ap.error("no numbered .lst files found")
    print("member entry instructions reachable static_conditional static_unconditional reachable_conditional reachable_unconditional ai_cmd_calls score_calls poke_writes native_calls unreachable")
    for r in rows:
        print(r["file"], f"0x{r['entry']:x}", r["instructions"], r["reachable"],
              r["static_conditional"], r["static_unconditional"],
              r["conditional"], r["unconditional"],
              r["ai_cmd_calls"], r["score_calls"], r["poke_writes"], r["native_calls"],
              len(r["unreachable"]))
        if r["unreachable"]:
            print("  unreachable:", ", ".join(f"0x{x:x}" for x in r["unreachable"][:12]))


if __name__ == "__main__":
    main()
