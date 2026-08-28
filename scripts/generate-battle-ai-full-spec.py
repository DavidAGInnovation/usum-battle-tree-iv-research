#!/usr/bin/env python3
"""Generate a derived, source-level specification of the Battle AI scripts.

The original Pawn files were removed from the working source tree, but their
Git objects survive in the supplied source repository.  This generator takes
an externally recovered directory containing those files and emits a readable
specification without copying the original comments, logging, includes, or
project metadata.

The output is deliberately a derived specification rather than a replacement
source distribution.  It keeps the executable control structure, symbolic
constants, native command calls, score effects, and source line provenance.
It does not silently repair source-level quirks: the specification describes
the recovered program as written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


SCRIPT_ORDER = [
    ("btl_ai_allowance.p", "Allowance", "move", "0x001"),
    ("btl_ai_band.p", "Band", "archive-only", "—"),
    ("btl_ai_basic.p", "Basic", "move", "0x001"),
    ("btl_ai_double.p", "Double", "move", "0x008"),
    ("btl_ai_expert.p", "Expert", "move", "0x004"),
    ("btl_ai_item.p", "Item", "item", "0x040"),
    ("btl_ai_moving.p", "Moving", "archive-only", "—"),
    ("btl_ai_pokechange.p", "Pokechange", "switch", "0x100"),
    ("btl_ai_strong.p", "Strong", "move", "0x002"),
]

RETAIL_ROLES = {
    0: ("Allowance", "functional"),
    1: ("Band", "archive-only legacy"),
    2: ("Basic", "functional"),
    3: ("Double", "functional"),
    4: ("Expert", "functional"),
    5: ("Intrude", "retail-only source gap"),
    6: ("Item", "functional"),
    7: ("Moving", "archive-only legacy"),
    8: ("Pokechange", "functional"),
    9: ("Royal", "retail-only source gap"),
    10: ("Strong", "functional"),
}

KEYWORDS = {
    "if", "else", "switch", "case", "default", "return", "new", "sizeof",
    "while", "for", "do", "break", "continue", "ScoreCtrl", "Call",
    "PRINTF", "CurrentWazaNo", "SetPokeChangeEnable",
}

COMMAND_ENUM_RE = re.compile(r"^\s*(CMD_[A-Z0-9_]+)\s*(?:,|$)")
COMMAND_HANDLER_RE = re.compile(
    r"^\s*cell\s+BattleAiCommand::(CMDFUNC_[A-Z0-9_]+)\s*\("
)
FUNCTION_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)")


@dataclass
class Function:
    name: str
    args: str
    start: int
    end: int
    lines: list[str]


def decode(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "shift_jis", "cp932", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remove_comments(line: str) -> str:
    # The recovered files use line comments.  Keeping strings intact matters
    # only for diagnostics, which are removed later; this simple split is
    # therefore sufficient and avoids carrying Japanese comments forward.
    return line.split("//", 1)[0]


def brace_delta(line: str) -> int:
    code = remove_comments(line)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    return code.count("{") - code.count("}")


def parse_functions(path: Path) -> list[Function]:
    raw_lines = decode(path).replace("\r\n", "\n").replace("\r", "\n").splitlines()
    functions: list[Function] = []
    index = 0
    while index < len(raw_lines):
        line = remove_comments(raw_lines[index]).strip()
        match = FUNCTION_RE.match(line)
        if not match or line.startswith(("if", "else", "switch", "while", "for")):
            index += 1
            continue
        name, args = match.groups()
        if name in KEYWORDS:
            index += 1
            continue

        # Pawn permits the opening brace on the following line.
        open_index = index
        while open_index < len(raw_lines) and "{" not in remove_comments(raw_lines[open_index]):
            open_index += 1
        if open_index >= len(raw_lines):
            index += 1
            continue

        depth = 0
        end = open_index
        while end < len(raw_lines):
            depth += brace_delta(raw_lines[end])
            if depth == 0:
                break
            end += 1
        if depth != 0:
            raise ValueError(f"unbalanced function {name} in {path}")
        functions.append(Function(name, args.strip(), index + 1, end + 1, raw_lines[index:end + 1]))
        index = end + 1
    return functions


def matching_paren(text: str, start: int) -> int:
    depth = 0
    quote = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
            continue
        if char == '"':
            quote = True
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(f"unclosed parenthesis in {text!r}")


def split_top_level(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote = False
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
            continue
        if char == '"':
            quote = True
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return parts


def replace_calls(line: str, function_name: str, replacement) -> str:
    needle = function_name + "("
    output: list[str] = []
    cursor = 0
    while True:
        start = line.find(needle, cursor)
        if start < 0:
            output.append(line[cursor:])
            return "".join(output)
        output.append(line[cursor:start])
        open_index = start + len(function_name)
        close_index = matching_paren(line, open_index)
        output.append(replacement(line[open_index + 1:close_index]))
        cursor = close_index + 1


def normalize(line: str) -> str:
    line = remove_comments(line).strip()
    if not line or line.startswith("#"):
        return ""
    if re.match(r"PRINTF\s*\(", line):
        return ""

    def call_replacement(inner: str) -> str:
        args = split_top_level(inner)
        if not args:
            return "AI_CMD()"
        command = args[0]
        rest = ", ".join(args[1:])
        return f"AI_CMD({command}{', ' + rest if rest else ''})"

    def score_replacement(inner: str) -> str:
        return f"SCORE += {inner.strip()}"

    line = replace_calls(line, "Call", call_replacement)
    line = replace_calls(line, "ScoreCtrl", score_replacement)
    line = replace_calls(line, "CurrentWazaNo", lambda _inner: "CURRENT_MOVE()")
    line = replace_calls(line, "SetPokeChangeEnable", lambda _inner: "ENABLE_SWITCHING()")
    line = re.sub(r"\bnew\s+", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def commands_in(text: str) -> list[str]:
    return re.findall(r"\bCMD_[A-Z0-9_]+\b", text)


def score_effects(text: str) -> list[str]:
    effects = []
    for match in re.finditer(r"ScoreCtrl\s*\(", text):
        close = matching_paren(text, match.end() - 1)
        effects.append(text[match.end():close].strip())
    return effects


def local_calls(text: str, function_names: set[str]) -> list[str]:
    calls = []
    for name in function_names:
        if re.search(rf"\b{re.escape(name)}\s*\(", text):
            calls.append(name)
    return sorted(calls)


def case_values(text: str) -> list[str]:
    values: list[str] = []
    for match in re.finditer(r"\bcase\s+([^:]+):", text):
        values.append(match.group(1).strip())
    return values


def summarize_function(function: Function, all_names: set[str]) -> dict[str, object]:
    text = "\n".join(remove_comments(line) for line in function.lines)
    effects = score_effects(text)
    commands = commands_in(text)
    return {
        "name": function.name,
        "args": function.args,
        "source_lines": [function.start, function.end],
        "score_effects": effects,
        "score_literals": sorted({int(x) for x in effects if re.fullmatch(r"-?\d+", x)}),
        "commands": sorted(set(commands)),
        "command_calls": len(commands),
        "local_calls": local_calls(text, all_names - {function.name}),
        "switch_cases": case_values(text),
    }


def parse_command_header(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    commands: list[str] = []
    in_enum = False
    for raw in decode(path).splitlines():
        if re.search(r"enum\s+AICmd\b", raw):
            in_enum = True
            continue
        if in_enum and "NUM_AI_CMD" in raw:
            break
        if in_enum:
            match = COMMAND_ENUM_RE.match(remove_comments(raw))
            if match:
                commands.append(match.group(1))
    return commands


def parse_handlers(path: Path | None) -> dict[str, dict[str, object]]:
    if path is None or not path.exists():
        return {}
    lines = decode(path).splitlines()
    handlers: dict[str, dict[str, object]] = {}
    index = 0
    while index < len(lines):
        match = COMMAND_HANDLER_RE.match(lines[index])
        if not match:
            index += 1
            continue
        name = match.group(1)
        depth = 0
        end = index
        while end < len(lines):
            depth += brace_delta(lines[end])
            if depth == 0 and end > index:
                break
            end += 1
        body = "\n".join(lines[index:end + 1])
        handlers[name] = {
            "source_lines": [index + 1, end + 1],
            "arg_indices": sorted({int(x) for x in re.findall(r"args\[(\d+)\]", body)}),
            "calls": sorted(set(re.findall(r"\b(?:Get|Hnd|Calc|Check|Is|WAZA|PokeType)[A-Za-z0-9_]*\b", body))),
            "lines": lines[index:end + 1],
        }
        index = end + 1
    return handlers


def normalize_cpp(line: str) -> str:
    line = remove_comments(line).strip()
    if not line or line.startswith("#"):
        return ""
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def parse_lst(path: Path) -> list[str]:
    """Return the exact code/data-independent instruction text from a Pawn listing."""
    lines: list[str] = []
    for raw in decode(path).splitlines():
        if raw.startswith(";DATA"):
            break
        if not raw.strip() or raw.startswith(";"):
            continue
        if raw.startswith("                  "):
            # Preserve case-table rows; they are part of the exact control
            # structure even though they are not ordinary instructions.
            lines.append(re.sub(r"\s+", " ", raw.strip()))
            continue
        if re.match(r"^[0-9a-fA-F]{8}\s+", raw):
            lines.append(re.sub(r"\s+", " ", raw.strip()))
    return lines


def retail_program_summary(path: Path) -> dict[str, object]:
    instructions = parse_lst(path)
    proc_count = sum(1 for line in instructions if re.search(r"\bproc$", line))
    branches = sum(1 for line in instructions if re.search(r"\b(?:jzer|jnz|jeq|jneq|jsless|jsleq|jsgrtr|jsgeq|jump|switch)\b", line))
    wrapper_calls = sum(1 for line in instructions if re.search(r"\bcall 00000008$", line))
    score_calls = sum(1 for line in instructions if re.search(r"\bcall 0000005c$", line))
    return {
        "file": path.name,
        "sha256": source_hash(path),
        "instruction_lines": len(instructions),
        "procedures": proc_count,
        "branch_instructions": branches,
        "ai_wrapper_calls": wrapper_calls,
        "score_helper_calls": score_calls,
        "listing": instructions,
    }


def source_manifest(source_dir: Path) -> dict[str, object]:
    rows = []
    for filename, role, judge, bit in SCRIPT_ORDER:
        path = source_dir / filename
        if not path.exists():
            continue
        functions = parse_functions(path)
        names = {function.name for function in functions}
        rows.append({
            "file": filename,
            "role": role,
            "judge": judge,
            "mask_bit": bit,
            "sha256": source_hash(path),
            "line_count": len(decode(path).splitlines()),
            "function_count": len(functions),
            "functions": [summarize_function(function, names) for function in functions],
        })
    return {"scripts": rows}


def render_function(function: Function) -> list[str]:
    lines = [f"#### `{function.name}({function.args})` (source lines {function.start}–{function.end})", ""]
    lines.append("```text")
    for offset, raw in enumerate(function.lines):
        normalized = normalize(raw)
        if normalized:
            lines.append(f"{function.start + offset:5d} | {normalized}")
    lines.extend(["```", ""])
    return lines


def render_script(row: dict[str, object], source_dir: Path) -> list[str]:
    filename = str(row["file"])
    path = source_dir / filename
    functions = parse_functions(path)
    out = [f"## {row['role']} (`{filename}`)", ""]
    out.append(f"Judge: **{row['judge']}**. Mask bit: `{row['mask_bit']}`.")
    out.append(f"Source SHA-256: `{row['sha256']}`; {row['line_count']} lines; {row['function_count']} functions.")
    out.append("")
    out.append("The following is a normalized derived listing. `AI_CMD` is the native dispatcher, `SCORE +=` is the script score accumulator, and `CURRENT_MOVE()` is the current move under evaluation. Logging and comments are omitted; symbolic constants are intentionally retained.")
    out.append("")
    for function in functions:
        out.extend(render_function(function))
    return out


def render_command_table(commands: list[str], handlers: dict[str, dict[str, object]]) -> list[str]:
    out = ["## Native command contract index", ""]
    out.append("The Pawn programs call these commands through `AI_CMD`. The table is an exact index of the recovered enum and native handler; the handler source remains the authority for detailed battle-engine semantics.")
    out.append("")
    out.append("| ID | Pawn command | Native handler | `args[]` indices observed in handler |")
    out.append("|---:|---|---|---|")
    for index, command in enumerate(commands):
        handler = handlers.get("CMDFUNC_" + command.removeprefix("CMD_"), {})
        name = "CMDFUNC_" + command.removeprefix("CMD_")
        args = ", ".join(str(x) for x in handler.get("arg_indices", [])) or "—"
        out.append(f"| {index} | `{command}` | `{name}` | {args} |")
    out.append("")
    out.append("The handler implementations also call the battle engine for HP ratios, status flags, type affinity, simulation damage, move metadata, bench state, field state, and mode-specific state. A script’s command list is not a claim that it uses every command in this table.")
    out.append("")
    return out


def render_native_handlers(handlers: dict[str, dict[str, object]]) -> list[str]:
    out = ["## Native handler specifications", ""]
    out.append("Each handler below is a normalized derived listing of the recovered C++ implementation. It retains the executable source-level logic while omitting comments, includes, logging, and unrelated project scaffolding.")
    out.append("")
    for name in sorted(handlers):
        handler = handlers[name]
        start, end = handler["source_lines"]
        out.append(f"### `{name}` (source lines {start}–{end})")
        out.append("")
        out.append("```text")
        for offset, raw in enumerate(handler["lines"]):
            normalized = normalize_cpp(raw)
            if normalized:
                out.append(f"{start + offset:5d} | {normalized}")
        out.extend(["```", ""])
    return out


def render_retail_inventory(manifest_path: Path | None) -> list[str]:
    out = ["## Retail AMX inventory", ""]
    out.append("The retail archive contains eleven AMX members. The two members marked `retail-only source gap` have no corresponding Pawn source path in the recovered Git history; their exact retail disassembly is included later in this document.")
    out.append("")
    manifest = {}
    if manifest_path is not None and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    members = {int(row["index"]): row for row in manifest.get("members", [])}
    out.append("| Member | Role | Status | Retail bytes | SHA-256 |")
    out.append("|---:|---|---|---:|---|")
    for index in range(11):
        role, status = RETAIL_ROLES[index]
        row = members.get(index, {})
        size = row.get("raw_size", "—")
        digest = row.get("sha256", "—")
        out.append(f"| {index} | {role} | {status} | {size} | `{digest}` |")
    out.append("")
    out.append("The exact reconstructed archive order is `allowance, band, basic, double, expert, intrude, item, moving, pokechange, royal, strong`. The original generated index bytes are absent, but this numeric mapping is forced by the archived project ordering, the archiver sort rule, and the retail member inventory.")
    out.append("")
    return out


def render_retail_program(role: str, status: str, summary: dict[str, object]) -> list[str]:
    out = [f"## {role} retail program (AMX member {summary['file'][:2]})", ""]
    out.append(f"Status: **{status}**. No source-level function names are asserted for this member.")
    out.append(f"Listing SHA-256: `{summary['sha256']}`; {summary['instruction_lines']} listing lines; {summary['procedures']} Pawn procedures; {summary['branch_instructions']} branch/control instructions; {summary['ai_wrapper_calls']} native-wrapper calls; {summary['score_helper_calls']} score-helper calls.")
    out.append("")
    out.append("This is the exact normalized retail AMX disassembly. `call 0x08` is the recovered `AI_CMD` wrapper, `call 0x5c` is the recovered score helper, and the native command/argument contract is indexed above. Unlike the source-backed sections, this listing cannot restore the deleted source comments or original helper names.")
    out.append("")
    out.append("```text")
    for line in summary["listing"]:
        out.append(line)
    out.extend(["```", ""])
    return out


def render_summary(manifest: dict[str, object]) -> list[str]:
    out = ["## Source-level inventory", ""]
    out.append("| Script | Functions | Source score literals | Unique native commands |")
    out.append("|---|---:|---|---:|")
    for row in manifest["scripts"]:
        functions = row["functions"]
        literals = sorted({literal for function in functions for literal in function["score_literals"]})
        commands = sorted({command for function in functions for command in function["commands"]})
        out.append(f"| {row['role']} | {row['function_count']} | {', '.join(str(x) for x in literals) or 'none'} | {len(commands)} |")
    out.append("")
    return out


def render_common_contract(source_dir: Path) -> list[str]:
    path = source_dir / "btl_ai_common.inc"
    if not path.exists():
        return []
    out = ["## Shared Pawn contract (`btl_ai_common.inc`)", ""]
    out.append(f"Source SHA-256: `{source_hash(path)}`.")
    out.append("")
    out.append("The shared include defines the exact interface used by all scripts:")
    out.append("")
    out.append("- `Call(cmd, a1, a2, a3, a4)` invokes native `AI_CMD(p_AIHandler, cmd, a1, a2, a3, a4)` and returns the native result.")
    out.append("- `ScoreCtrl(value)` performs `p_Score += value`.")
    out.append("- `SetPokeChangeEnable()` sets `p_PokeChangeEnable = true`.")
    out.append("- `CurrentWazaNo()` invokes `CMD_GET_CURRENT_WAZANO`.")
    out.append("- Each AMX program receives the same public variables, but each script has its own VM score execution and the host reads the result after the program returns.")
    out.append("")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path, help="directory containing recovered btl_ai_*.p files")
    parser.add_argument("output", type=Path, help="derived Markdown specification to write")
    parser.add_argument("--command-header", type=Path)
    parser.add_argument("--command-source", type=Path)
    parser.add_argument("--disassembly-dir", type=Path)
    parser.add_argument("--retail-manifest", type=Path)
    args = parser.parse_args()

    manifest = source_manifest(args.source_dir)
    if not manifest["scripts"]:
        parser.error("no recovered AI script files found")
    commands = parse_command_header(args.command_header)
    handlers = parse_handlers(args.command_source)

    lines = [
        "# Pokémon USUM Battle AI: full source-level specification",
        "",
        "> This is a derived specification of the recovered Battle AI Pawn programs and their native command boundary. It is generated from the source snapshot immediately before the AI scripts were removed from Git and cross-referenced against the US retail AMX archive. It intentionally does not redistribute the original source files.",
        "",
        "## Exact execution model",
        "",
        "For a move/target candidate `c`, the engine computes:",
        "",
        "```text",
        "MoveScore(c) = 100 + Σ ScriptScore(s, state, c, random_trace)",
        "```",
        "",
        "where the sum contains the enabled move scripts for the current AI mask. Each script starts with `p_Score = 0`; its Pawn program calls native `AI_CMD` queries and changes `p_Score` through signed `ScoreCtrl` operations. The C++ judge adds that returned script score to the candidate’s running score. Illegal moves and targets are rejected before comparison.",
        "",
        "Switch evaluation is separate: the Pokechange program evaluates each eligible reserve candidate, may set `p_PokeChangeEnable`, and returns a reserve score. The final action-selection layer handles forced actions first, compares the permitted action categories, and randomizes equal best candidates according to the AI random generator. Double-battle scripts use a separate common random value for coordination.",
        "",
        "The ordinary Battle Tree mask is `0x107` (`BASIC | STRONG | EXPERT | POKECHANGE_BASIC`); Double/Multi adds `DOUBLE`, producing `0x10f`. The mask selects a set of programs; it is not a scalar difficulty value.",
        "",
        "## Completeness and interpretation",
        "",
        "This document is source-complete at the Pawn-program level: every recovered function body is represented below as normalized control structure, every score mutation is retained, and every symbolic native command call is retained. The native command index records the handler boundary and source argument usage.",
        "",
        "It is not a closed-form table of final move choices. The native handlers depend on the live battle engine, damage simulation, object relationships, and random state. To reproduce a concrete battle decision, supply those native query results and execute the normalized program or the retail AMX through the recovered Pawn VM. Apparent source quirks are preserved as written because changing them would no longer describe the retail program.",
        "",
    ]
    lines.extend(render_summary(manifest))
    lines.extend(render_common_contract(args.source_dir))
    lines.extend(render_retail_inventory(args.retail_manifest))
    if commands:
        lines.extend(render_command_table(commands, handlers))
        if handlers:
            lines.extend(render_native_handlers(handlers))
    lines.extend(["## Normalized script specifications", ""])
    for row in manifest["scripts"]:
        lines.extend(render_script(row, args.source_dir))

    if args.disassembly_dir is not None:
        lines.extend(["## Retail-only program specifications", ""])
        for index in (5, 9):
            path = args.disassembly_dir / f"{index:02d}.lst"
            if path.exists():
                role, status = RETAIL_ROLES[index]
                lines.extend(render_retail_program(role, status, retail_program_summary(path)))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    json_path = args.output.with_suffix(".json")
    json_handlers = {
        name: {key: value for key, value in data.items() if key != "lines"}
        for name, data in handlers.items()
    }
    json_path.write_text(json.dumps({"manifest": manifest, "commands": commands, "handlers": json_handlers}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "json": str(json_path), "scripts": len(manifest["scripts"]), "commands": len(commands)}, indent=2))


if __name__ == "__main__":
    main()
