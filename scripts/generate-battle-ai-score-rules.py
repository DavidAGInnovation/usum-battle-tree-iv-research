#!/usr/bin/env python3
"""Generate a condition-to-score index from the derived Battle AI listing.

The full Battle AI specification contains the authoritative normalized
function bodies.  This companion report collects the score-producing bodies
and the complete Pokechange decision path in one place, so every score write
is shown together with the guards that lead to it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ACTIVE_ROLES = ("Basic", "Strong", "Expert", "Double", "Pokechange")

RETAIL_DELTAS = {
    "Basic": "−20, −12, −10, −8, −6, −5, −1",
    "Strong": "−3, −1, +2, +3, +4, +5",
    "Expert": "−12, −10, −8, −7, −5, −4, −3, −2, −1, +1, +2, +3, +4",
    "Double": "−30, −20, −12, −11, −10, −8, −7, −5, −4, −3, −2, −1, +1, +2, +3, +4, +5, +8, +20",
    "Pokechange": "computed reserve score; see the exact formula below",
}

FUNCTION_HEADING_RE = re.compile(r"^#### `([^`]+)`(?: \(source lines ([^)]+)\))?$")

COMMAND_TOPICS = {
    "CMD_CHECK_BTL_RULE": "battle-rule state",
    "CMD_CHECK_DAMAGE_WAZA": "damage/status classification",
    "CMD_CHECK_FORMNO": "forms",
    "CMD_CHECK_MONSNO": "species",
    "CMD_CHECK_STATUS": "status conditions",
    "CMD_CHECK_STATUS_DIFF": "status differences",
    "CMD_CHECK_STATUS_UP": "stat-stage state",
    "CMD_CHECK_TOKUSEI": "abilities",
    "CMD_CHECK_TYPE": "types",
    "CMD_CHECK_WAZA_AISYOU": "type effectiveness",
    "CMD_CHECK_WAZA_KIND": "move category",
    "CMD_CHECK_WAZA_SEQNO": "move sequence numbers",
    "CMD_CHECK_WAZA_USABLE": "move usability",
    "CMD_CHECK_WEATHER": "weather",
    "CMD_COMP_POWER": "simulated power/damage comparisons",
    "CMD_COMP_POWER_WITH_PARTNER": "partner-aware power comparisons",
    "CMD_FLDEFF_CHECK": "field effects",
    "CMD_GET_BATTLEROYAL_RANKING": "Battle Royal ranking",
    "CMD_GET_CLIENT_KILL_COUNT": "KO counts",
    "CMD_GET_CURRENT_ITEMNO": "held items",
    "CMD_GET_CURRENT_WAZANO": "current move",
    "CMD_GET_LAST_DAMAGED_WAZA_AT_PREV_TURN": "previous-turn damage",
    "CMD_GET_MAX_WAZA_POWER_INCLUDE_AFFINITY": "maximum effective move power",
    "CMD_IF_BENCH_DAMAGE_MAX": "reserve damage potential",
    "CMD_IF_BENCH_HPDEC": "reserve HP loss",
    "CMD_IF_BENCH_PPDEC": "reserve PP loss",
    "CMD_IF_CAN_MEGAEVOLVE": "Mega Evolution state",
    "CMD_IF_COMMONRND_EQUAL": "shared partner randomness",
    "CMD_IF_COMMONRND_OVER": "shared partner randomness",
    "CMD_IF_COMMONRND_UNDER": "shared partner randomness",
    "CMD_IF_DMG_PHYSIC_EQUAL": "physical/special damage type",
    "CMD_IF_DMG_PHYSIC_OVER": "physical/special damage type",
    "CMD_IF_DMG_PHYSIC_UNDER": "physical/special damage type",
    "CMD_IF_FIRST": "speed/order state",
    "CMD_IF_HAVE_BATSUGUN": "available super-effective attacks",
    "CMD_IF_HAVE_ITEM": "held items",
    "CMD_IF_HAVE_WAZA": "available moves",
    "CMD_IF_HAVE_WAZA_AISYOU_EQUAL": "bench type effectiveness",
    "CMD_IF_HAVE_WAZA_AISYOU_OVER": "bench type effectiveness",
    "CMD_IF_HP_EQUAL": "HP thresholds",
    "CMD_IF_HP_OVER": "HP thresholds",
    "CMD_IF_HP_UNDER": "HP thresholds",
    "CMD_IF_I_AM_SENARIO_TRAINER": "scenario-trainer state",
    "CMD_IF_LAST_WAZA_DAMAGE_CHECK": "previous damage comparison",
    "CMD_IF_MIKATA_ATTACK": "ally attack state",
    "CMD_IF_MULTI": "multi-battle state",
    "CMD_IF_RND_EQUAL": "random gates",
    "CMD_IF_RND_OVER": "random gates",
    "CMD_IF_RND_UNDER": "random gates",
    "CMD_IF_WAZA_HINSHI": "KO potential",
    "CMD_IF_WAZA_NO_EFFECT_BY_TOKUSEI": "ability-based immunity",
    "CMD_IFN_WAZASICK": "move lock/status state",
    "CMD_IFN_HINSHI": "fainted state",
    "CMD_IFN_SIDEEFF": "side effects",
    "CMD_IFN_WAZA_HINSHI": "move KO potential",
    "CMD_IFN_CHOUHATSU": "Taunt state",
    "CMD_IFN_CONTFLG": "continuous-effect state",
    "CMD_IFN_HAVE_DAMAGE_WAZA": "available damaging moves",
    "CMD_IFN_HAVE_WAZA": "available moves",
    "CMD_IFN_HAVE_WAZA_SEQNO": "available move sequences",
    "CMD_IFN_POKESICK": "status conditions",
}

DESCRIPTIONS = {
    ("Basic", "main()"): "Trigger: every Basic evaluation. It records the current move's AI sequence identifier and then enters the Basic decision procedure.",
    ("Basic", "main_proc()"): "Trigger: every move candidate reaching Basic. In Double or Triple Battles, the procedure skips a candidate when its selected target is an ally. It then checks powder immunities first; if one handles the move, the procedure stops. Otherwise it classifies the move as damaging, including the two one-hit-KO moves Fissure and Horn Drill, runs the damaging-move immunity checks when appropriate, and finally runs the selected general move-sequence rules.",
    ("Basic", "Basic_ConaHoushi()"): "Penalizes powder moves when Bulletproof blocks them or when the defender is Grass-type; applies −10 and reports that the move was handled.",
    ("Basic", "Calc_BasicDamage()"): "Checks direct damage immunities and ability/type exceptions; applies the initial ineffective-damage penalty and selects the appropriate ability-specific damage check.",
    ("Basic", "BasicDmg_00_1()"): "Penalizes Electric moves against Volt Absorb, Motor Drive, or Lightning Rod by −12.",
    ("Basic", "BasicDmg_00_2()"): "Penalizes Water moves against Water Absorb, Storm Drain, or Dry Skin by −12.",
    ("Basic", "BasicDmg_00_3()"): "Penalizes Fire moves against Flash Fire by −12.",
    ("Basic", "BasicDmg_00_4()"): "Penalizes moves against Wonder Guard unless the move is at least super-effective; applies −10.",
    ("Basic", "BasicDmg_00_5()"): "Penalizes Ground moves against Levitate or Flying-type targets unless Gravity removes the immunity; applies −10.",
    ("Basic", "BasicDmg_00_7()"): "Penalizes Grass moves against Sap Sipper by −12.",
    ("Basic", "Calc_BasicAll()"): "Trigger: the damaging-move checks did not terminate Basic evaluation. It checks Soundproof first and stops if that helper handles the move; then it checks Bulletproof and stops if that helper handles the move. If neither applies, it selects the general rule set associated with the current move's AI sequence identifier.",
    ("Basic", "Bouon_Check()"): "Penalizes sound-based moves against Soundproof when the attacker lacks an ability that bypasses defensive abilities; applies −10.",
    ("Basic", "Boudan_Check()"): "Penalizes ball- and bomb-based moves against Bulletproof when the attacker lacks an ability that bypasses defensive abilities; applies −10.",
    ("Basic", "BaciAI_Seq_226()"): "Basic AI sequence 226 has an empty body: it performs no checks, calls, or direct score writes.",
    ("Basic", "BaciAI_Seq_240()"): "Basic AI sequence 240 has an empty body: it performs no checks, calls, or direct score writes.",
    ("Basic", "BaciAI_Seq_259()"): "Basic AI sequence 259 has an empty body: it performs no checks, calls, or direct score writes.",
    ("Basic", "BaciAI_Seq_301()"): "Basic AI sequence 301 has an empty body: it performs no checks, calls, or direct score writes.",
    ("Basic", "BaciAI_Seq_010()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, if the attacking Pokémon's native PARA_POW parameter equals 12, adds −10.",
    ("Basic", "BaciAI_Seq_011()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, if the attacking Pokémon's native PARA_DEF parameter equals 12, adds −10.",
    ("Basic", "BaciAI_Seq_012()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, if the attacking Pokémon's native PARA_AGI parameter equals 12, adds −10 and stops; if that test fails but the field effect is Trick Room, adds −5.",
    ("Basic", "BaciAI_Seq_013()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, if the attacking Pokémon's native PARA_SPEPOW parameter equals 12, adds −10.",
    ("Basic", "BaciAI_Seq_014()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, if the attacking Pokémon's native PARA_SPEDEF parameter equals 12, adds −10.",
    ("Basic", "BaciAI_Seq_015()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, adds −10 and stops if either the defending or attacking Pokémon has No Guard. If neither has No Guard, adds −10 when the attacking Pokémon's native PARA_HIT parameter equals 12.",
    ("Basic", "BaciAI_Seq_016()"): "If the attacking Pokémon has Contrary, adds −12 and stops. Otherwise, adds −10 and stops if either the defending or attacking Pokémon has No Guard. If neither has No Guard, adds −10 when the attacking Pokémon's native PARA_AVOID parameter equals 12.",
    ("Strong", "main()"): "Entry point: reads the current move sequence and calls the attack-oriented evaluator.",
    ("Strong", "main_proc()"): "Rewards selected finishing moves, avoids moves that compare poorly in power, and gives a randomized bonus to strongly favorable matchups; skips ally attacks in multi battles.",
    ("Strong", "Strong_exception()"): "Suppresses normal power scoring for special species/ability combinations where the generic comparison would be misleading.",
    ("Strong", "Strong_KinomiCheck()"): "Detects type-resist Berries and selected Ground-immunity cases so the normal attack-power evaluation can be bypassed or penalized.",
    ("Pokechange", "main()"): "Tests seven switch-enabling situations in priority order and stops after the first successful reason.",
    ("Pokechange", "PokeChangeOK(scoreOffset)"): "Adds the computed reserve score plus the supplied offset and enables switching.",
    ("Pokechange", "CalcBaseScore()"): "Computes the reserve baseline from scenario-trainer Mega Evolution state and maximum effective bench move power.",
    ("Pokechange", "IsHorobinoutaLastTurn()"): "Detects whether the active Pokémon is on the final turn of Perish Song.",
    ("Pokechange", "CanHusiginamamoriBreak()"): "Randomly permits switching when a reserve can hit a Wonder Guard target that the active side cannot hit super-effectively.",
    ("Pokechange", "CanAisyou0BaiBreak()"): "Permits switching when a reserve improves a zero-effect matchup, using randomized thresholds for strictly better or equal matchups.",
    ("Pokechange", "CanKodawariBadAisyouBreak()"): "Permits escape from a bad Choice-locked matchup when the bench has a usable improvement, subject to randomized thresholds.",
    ("Pokechange", "CanNoEffectPrevDamageByTokusei()"): "Permits switching to exploit an ability that would nullify the opponent's previous damage move, with scenario-trainer and random exceptions.",
    ("Pokechange", "CanRepairSickBySizenkaihuku()"): "Permits switching to a Natural Cure Pokémon that can recover sleep or freeze and has a favorable matchup against the previous move.",
    ("Pokechange", "CanAisyouMakeBetter()"): "Permits switching when the active side was damaged by a poor matchup and a reserve offers a better matchup, with status, Mega, and random checks.",
}
SCRIPT_HEADING_RE = re.compile(r"^## (Basic|Strong|Expert|Double|Pokechange) \(")
SECTION_HEADING_RE = re.compile(r"^## ")


def extract_sections(lines: list[str]) -> dict[str, list[str]]:
    starts: list[tuple[str, int, int]] = []
    for index, line in enumerate(lines):
        match = SCRIPT_HEADING_RE.match(line)
        if match:
            starts.append((match.group(1), index, index))

    sections: dict[str, list[str]] = {}
    for role, start, _ in starts:
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if SECTION_HEADING_RE.match(lines[index]):
                end = index
                break
        sections[role] = lines[start:end]
    return sections


def reachable_functions(metadata: dict[str, dict[str, object]]) -> set[str]:
    """Return every function reachable from the script entry point."""
    if "main" not in metadata:
        return set()
    reachable: set[str] = set()
    pending = ["main"]
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        for called in metadata[name].get("local_calls", []) or []:
            if called in metadata:
                pending.append(called)
    return reachable


def score_influence_closure(metadata: dict[str, dict[str, object]]) -> set[str]:
    """Return direct writers plus their local-call ancestors."""
    direct = {
        name for name, row in metadata.items()
        if row.get("score_effects")
    }
    closure = set(direct)
    changed = True
    while changed:
        changed = False
        for name, row in metadata.items():
            if name in closure:
                continue
            if any(called in closure for called in row.get("local_calls", []) or []):
                closure.add(name)
                changed = True
    return closure


def extract_functions(
    section: list[str],
    role: str,
    metadata: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    headings: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(section):
        match = FUNCTION_HEADING_RE.match(line)
        if match:
            headings.append((index, match))

    functions: list[dict[str, str]] = []
    for position, (start, match) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(section)
        body_start = None
        for index in range(start + 1, end):
            if section[index].strip().startswith("```text"):
                body_start = index + 1
                break
        if body_start is None:
            continue
        body_end = None
        for index in range(body_start, end):
            if section[index].strip() == "```":
                body_end = index
                break
        if body_end is None:
            continue

        body = "\n".join(section[body_start:body_end]).rstrip()
        raw_name = match.group(1)
        name = raw_name.split("(", 1)[0]
        metadata_row = metadata.get(name, {})
        score_effects = list(metadata_row.get("score_effects") or [])
        if not score_effects:
            score_effects = re.findall(r"SCORE \+=\s*([^;]+)", body)
        reachable = reachable_functions(metadata)
        include = name in reachable
        if not include:
            continue
        influence_closure = score_influence_closure(metadata)
        if score_effects:
            influence_class = "direct score writer"
        elif name in influence_closure:
            influence_class = "indirect caller/helper on a score path"
        elif role == "Pokechange":
            influence_class = "indirect switch predicate/helper"
        else:
            influence_class = "reachable dispatcher/predicate support"
        functions.append({
            "name": raw_name,
            "source_lines": match.group(2) or "not stated",
            "body": body,
            "score_effects": ", ".join(dict.fromkeys(score_effects)) or "indirect/dynamic",
            "description": describe_function(role, raw_name, body, score_effects),
            "influence_class": influence_class,
            "local_calls": ", ".join(metadata_row.get("local_calls", []) or []) or "—",
        })
    return functions


def _clean_source_body(body: str) -> str:
    """Remove generated source-line prefixes and repair known implicit semicolons."""
    lines: list[str] = []
    for raw_line in body.splitlines():
        line = re.sub(r"^\s*\d+\s+\|\s?", "", raw_line)
        stripped = line.strip()
        if (
            stripped.startswith("Call ")
            or (
                not stripped.startswith(("if", "else", "switch"))
                and re.match(
                    r"^(?:[A-Za-z_][A-Za-z0-9_]*\s*=\s*)?[A-Za-z_][A-Za-z0-9_]*\s*\([^;]*\)\s*$",
                    stripped,
                )
            )
            or re.match(r"^return\b", stripped)
        ) and not stripped.endswith((";", "{")):
            line += ";"
        lines.append(line)
    return "\n".join(lines)


class _ScorePathParser:
    """Small parser for the recovered C-like Pawn bodies.

    It records the enclosing `if`/`else if`/`else` conditions for each direct
    SCORE write.  The normalized body remains authoritative for exact boolean
    complements and early-return behavior.
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0
        self.paths: list[tuple[list[str], str]] = []

    def skip_space(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

    def starts_word(self, word: str) -> bool:
        self.skip_space()
        end = self.position + len(word)
        if not self.source.startswith(word, self.position):
            return False
        return end == len(self.source) or not (
            self.source[end].isalnum() or self.source[end] == "_"
        )

    def consume_word(self, word: str) -> None:
        if not self.starts_word(word):
            raise ValueError(f"expected {word!r} at offset {self.position}")
        self.position += len(word)

    def parse_parenthesized(self) -> str:
        self.skip_space()
        if self.position >= len(self.source) or self.source[self.position] != "(":
            raise ValueError(f"expected '(' at offset {self.position}")
        start = self.position
        depth = 0
        quote: str | None = None
        while self.position < len(self.source):
            char = self.source[self.position]
            if quote:
                if char == quote and self.source[self.position - 1] != "\\":
                    quote = None
            elif char in "'\"":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    result = self.source[start + 1:self.position].strip()
                    self.position += 1
                    return result
            self.position += 1
        raise ValueError("unclosed parenthesized expression")

    def parse_simple_statement(self) -> str:
        self.skip_space()
        start = self.position
        depth = 0
        while self.position < len(self.source):
            char = self.source[self.position]
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and char == ";":
                self.position += 1
                return self.source[start:self.position].strip()
            elif depth == 0 and char == "}":
                return self.source[start:self.position].strip()
            self.position += 1
        return self.source[start:self.position].strip()

    def parse_block(self, context: list[str]) -> None:
        self.skip_space()
        if self.position >= len(self.source) or self.source[self.position] != "{":
            raise ValueError(f"expected '{{' at offset {self.position}")
        self.position += 1
        self.parse_sequence(context, stop="}")
        self.skip_space()
        if self.position >= len(self.source) or self.source[self.position] != "}":
            raise ValueError(f"expected '}}' at offset {self.position}")
        self.position += 1

    def parse_if(self, context: list[str], label: str = "if") -> None:
        self.consume_word("if")
        condition = self.parse_parenthesized()
        branch = f"{label}({condition})"
        self.skip_space()
        if self.position < len(self.source) and self.source[self.position] == "{":
            self.parse_block(context + [branch])
        else:
            self.parse_statement(context + [branch])

        self.skip_space()
        if not self.starts_word("else"):
            return
        self.consume_word("else")
        self.skip_space()
        if self.starts_word("if"):
            self.parse_if(context, label="else if")
        elif self.position < len(self.source) and self.source[self.position] == "{":
            self.parse_block(context + ["else"])
        else:
            self.parse_statement(context + ["else"])

    def parse_switch(self, context: list[str]) -> None:
        self.consume_word("switch")
        condition = self.parse_parenthesized()
        self.skip_space()
        switch_context = context + [f"switch({condition})"]
        if self.position < len(self.source) and self.source[self.position] == "{":
            self.parse_block(switch_context)
        else:
            self.parse_statement(switch_context)

    def parse_statement(self, context: list[str]) -> None:
        self.skip_space()
        if self.position >= len(self.source):
            return
        if self.starts_word("if"):
            self.parse_if(context)
            return
        if self.starts_word("switch"):
            self.parse_switch(context)
            return
        if self.starts_word("else"):
            self.consume_word("else")
            self.skip_space()
            if self.starts_word("if"):
                self.parse_if(context, label="else if")
            elif self.position < len(self.source) and self.source[self.position] == "{":
                self.parse_block(context + ["else"])
            else:
                self.parse_statement(context + ["else"])
            return
        if self.source[self.position] == "{":
            self.parse_block(context)
            return

        statement = self.parse_simple_statement()
        if statement.startswith("SCORE +="):
            self.paths.append((context, statement))
        elif not statement and self.position < len(self.source):
            self.position += 1

    def parse_sequence(self, context: list[str], stop: str | None = None) -> None:
        while True:
            self.skip_space()
            if self.position >= len(self.source):
                return
            if stop and self.source[self.position] == stop:
                return
            self.parse_statement(context)

    def run(self) -> list[tuple[list[str], str]]:
        self.parse_sequence([])
        return self.paths


def extract_score_paths(body: str) -> list[tuple[list[str], str]]:
    """Return source-level condition stacks for every direct SCORE write."""
    return _ScorePathParser(_clean_source_body(body)).run()


def _compact_expression(expression: str) -> str:
    return " ".join(expression.split())


def _markdown_safe_expression(expression: str) -> str:
    """Keep logical pipes from being interpreted as Markdown table separators."""
    return (
        _compact_expression(expression)
        .replace("|", "&#124;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# These names are used only in the human-readable Basic descriptions below.
# The normalized source bodies retain the original symbols, so translating a
# token here does not change the authoritative source-level evidence.
ABILITY_NAMES = {
    "TOKUSEI_AMANOZYAKU": "Contrary",
    "TOKUSEI_AROMABEERU": "Aroma Veil",
    "TOKUSEI_ATODASI": "Aftermath",
    "TOKUSEI_BATORUSUITTI": "Stance Change",
    "TOKUSEI_BOUDAN": "Bulletproof",
    "TOKUSEI_BOUON": "Soundproof",
    "TOKUSEI_BOUZIN": "Overcoat",
    "TOKUSEI_DARUMAMOODO": "Zen Mode",
    "TOKUSEI_DENKIENZIN": "Motor Drive",
    "TOKUSEI_DONKAN": "Oblivious",
    "TOKUSEI_GANZYOU": "Sturdy",
    "TOKUSEI_HATOMUNE": "Big Pecks",
    "TOKUSEI_HEVHIMETARU": "Heavy Metal",
    "TOKUSEI_HIRAISIN": "Lightning Rod",
    "TOKUSEI_HUMIN": "Insomnia",
    "TOKUSEI_HURAWAABEERU": "Flower Veil",
    "TOKUSEI_HUSIGINAMAMORI": "Wonder Guard",
    "TOKUSEI_HUYUU": "Levitate",
    "TOKUSEI_IRYUUZYON": "Illusion",
    "TOKUSEI_ITAZURAGOKORO": "Prankster",
    "TOKUSEI_KAGEHUMI": "Shadow Tag",
    "TOKUSEI_KAIRIKIBASAMI": "Hyper Cutter",
    "TOKUSEI_KANSOUHADA": "Dry Skin",
    "TOKUSEI_KATAYABURI": "Mold Breaker",
    "TOKUSEI_KATIKI": "Competitive",
    "TOKUSEI_KURIABODHI": "Clear Body",
    "TOKUSEI_KYUUBAN": "Suction Cups",
    "TOKUSEI_MAINASU": "Minus",
    "TOKUSEI_MAIPEESU": "Own Tempo",
    "TOKUSEI_MAKENKI": "Defiant",
    "TOKUSEI_MARUTITAIPU": "Multitype",
    "TOKUSEI_MAZIKKUGAADO": "Magic Guard",
    "TOKUSEI_MAZIKKUMIRAA": "Magic Bounce",
    "TOKUSEI_MENEKI": "Immunity",
    "TOKUSEI_MITUATUME": "Keen Eye",
    "TOKUSEI_MIZUNOBEERU": "Water Veil",
    "TOKUSEI_MORAIBI": "Flash Fire",
    "TOKUSEI_NAMAKE": "Truant",
    "TOKUSEI_NENTYAKU": "Sticky Hold",
    "TOKUSEI_NIGEASI": "Run Away",
    "TOKUSEI_NOOGAADO": "No Guard",
    "TOKUSEI_POIZUNHIIRU": "Poison Heal",
    "TOKUSEI_PURASU": "Plus",
    "TOKUSEI_RIIHUGAADO": "Leaf Guard",
    "TOKUSEI_SEISINRYOKU": "Inner Focus",
    "TOKUSEI_SIMERIKE": "Damp",
    "TOKUSEI_SIROIKEMURI": "White Smoke",
    "TOKUSEI_SOUSYOKU": "Sap Sipper",
    "TOKUSEI_SUIITOBEERU": "Sweet Veil",
    "TOKUSEI_SURINUKE": "Infiltrator",
    "TOKUSEI_SUROOSUTAATO": "Slow Start",
    "TOKUSEI_SURUDOIME": "Shield Dust",
    "TOKUSEI_TAABOBUREIZU": "Teravolt",
    "TOKUSEI_TANZYUN": "Simple",
    "TOKUSEI_TERABORUTEEZI": "Turboblaze",
    "TOKUSEI_TIKUDEN": "Volt Absorb",
    "TOKUSEI_TOREESU": "Trace",
    "TOKUSEI_TYOSUI": "Water Absorb",
    "TOKUSEI_YARUKI": "Vital Spirit",
    "TOKUSEI_YOBIMIZU": "Storm Drain",
    "TOKUSEI_YOWAKI": "Defeatist",
    "TOKUSEI_ZYUUNAN": "Limber",
}

TYPE_NAMES = {
    "POKETYPE_DENKI": "Electric",
    "POKETYPE_DOKU": "Poison",
    "POKETYPE_GHOST": "Ghost",
    "POKETYPE_HAGANE": "Steel",
    "POKETYPE_HIKOU": "Flying",
    "POKETYPE_HONOO": "Fire",
    "POKETYPE_JIMEN": "Ground",
    "POKETYPE_KUSA": "Grass",
    "POKETYPE_MIZU": "Water",
}

MOVE_NAMES = {
    "WAZANO_AISUBOORU": "Ice Ball",
    "WAZANO_AKUUSETUDAN": "Octazooka",
    "WAZANO_BAAKUAUTO": "Hyper Voice",
    "WAZANO_DENZIHA": "Thunder Wave",
    "WAZANO_DOKUNOKONA": "Poison Powder",
    "WAZANO_DOROBAKUDAN": "Mud Bomb",
    "WAZANO_EKOOBOISU": "Echoed Voice",
    "WAZANO_ENAZIIBOORU": "Energy Ball",
    "WAZANO_EREKIBOORU": "Electro Ball",
    "WAZANO_HADOUDAN": "Aura Sphere",
    "WAZANO_HEDOROBAKUDAN": "Sludge Bomb",
    "WAZANO_HOERU": "Roar",
    "WAZANO_HUNZIN": "Powder",
    "WAZANO_IBIKI": "Snore",
    "WAZANO_IKARINOKONA": "Rage Powder",
    "WAZANO_INISIENOUTA": "Relic Song",
    "WAZANO_IYANAOTO": "Screech",
    "WAZANO_KAENDAN": "Fire Blast",
    "WAZANO_KIAIDAMA": "Focus Blast",
    "WAZANO_KINOKONOHOUSI": "Spore",
    "WAZANO_KINZOKUON": "Metal Sound",
    "WAZANO_KUSABUE": "Grass Whistle",
    "WAZANO_MISUTOBOORU": "Mist Ball",
    "WAZANO_MUSINOSAZAMEKI": "Bug Buzz",
    "WAZANO_NAKIGOE": "Growl",
    "WAZANO_NEGAIGOTO": "Wish",
    "WAZANO_NEMURIGONA": "Sleep Powder",
    "WAZANO_OSYABERI": "Chatter",
    "WAZANO_RINSYOU": "Round",
    "WAZANO_SAWAGU": "Uproar",
    "WAZANO_SIBIREGONA": "Stun Spore",
    "WAZANO_SYADOOBOORU": "Shadow Ball",
    "WAZANO_TAMAGOBAKUDAN": "Egg Bomb",
    "WAZANO_TAMANAGE": "Rock Throw",
    "WAZANO_TANEBAKUDAN": "Seed Bomb",
    "WAZANO_TUNODORIRU": "Horn Drill",
    "WAZANO_TYOUONPA": "Supersonic",
    "WAZANO_UTAU": "Sing",
    "WAZANO_WHEZAABOORU": "Weather Ball",
    "WAZANO_ZIWARE": "Fissure",
    "WAZANO_ZYAIROBOORU": "Gyro Ball",
}

SIDE_EFFECT_NAMES = {
    "BTL_SIDEEFF_DOKUBISI": "Toxic Spikes",
    "BTL_SIDEEFF_HIKARINOKABE": "Light Screen",
    "BTL_SIDEEFF_MAKIBISI": "Spikes",
    "BTL_SIDEEFF_NEBANEBANET": "Sticky Web",
    "BTL_SIDEEFF_OIKAZE": "Tailwind",
    "BTL_SIDEEFF_REFRECTOR": "Reflect",
    "BTL_SIDEEFF_SINPINOMAMORI": "Safeguard",
    "BTL_SIDEEFF_SIROIKIRI": "Mist",
    "BTL_SIDEEFF_STEALTHROCK": "Stealth Rock",
}

FIELD_EFFECT_NAMES = {
    "EFF_DOROASOBI": "Mud Sport",
    "EFF_FUIN": "Imprison",
    "EFF_JURYOKU": "Gravity",
    "EFF_MAGICROOM": "Magic Room",
    "EFF_MIZUASOBI": "Water Sport",
    "EFF_TRICKROOM": "Trick Room",
    "EFF_WONDERROOM": "Wonder Room",
}

GROUND_EFFECT_NAMES = {
    "BTL_GROUND_ELEKI": "Electric Terrain",
    "BTL_GROUND_GRASS": "Grassy Terrain",
    "BTL_GROUND_MIST": "Misty Terrain",
}

STATUS_NAMES = {
    "WAZASICK_AKUMU": "Nightmare",
    "WAZASICK_AQUARING": "Aqua Ring",
    "WAZASICK_DOKU": "the poison move-state",
    "WAZASICK_ENCORE": "Encore",
    "WAZASICK_FLYING": "the semi-invulnerable Flying state",
    "WAZASICK_HOROBINOUTA": "Perish Song",
    "WAZASICK_ICHAMON": "Torment",
    "WAZASICK_IEKI": "Gastro Acid",
    "WAZASICK_KAIHUKUHUUJI": "Heal Block",
    "WAZASICK_KANASIBARI": "Disable",
    "WAZASICK_KONRAN": "Confusion",
    "WAZASICK_MAHI": "Paralysis",
    "WAZASICK_MEROMERO": "Infatuation",
    "WAZASICK_MIYABURU": "Miracle Eye",
    "WAZASICK_MUSTHIT_TARGET": "the sure-hit target state",
    "WAZASICK_NEMURI": "Sleep",
    "WAZASICK_NEWOHARU": "the internal move-state flag NEWOHARU",
    "WAZASICK_NOROI": "Curse",
    "WAZASICK_SASIOSAE": "the internal move-state flag SASIOSAE",
    "WAZASICK_TELEKINESIS": "Telekinesis",
    "WAZASICK_TOOSENBOU": "Soak",
    "WAZASICK_TYOUHATSU": "Taunt",
    "WAZASICK_YADORIGI": "Leech Seed",
}

SPECIES_NAMES = {
    "MONSNO_AAKEOSU": "Archeops",
    "MONSNO_ARUSEUSU": "Arceus",
    "MONSNO_GENOSEKUTO": "Genesect",
    "MONSNO_GIRATHINA": "Giratina",
    "MONSNO_GIRUGARUDO": "Aegislash",
    "MONSNO_KEKKINGU": "Slaking",
    "MONSNO_METAMON": "Ditto",
    "MONSNO_NUKENIN": "Shedinja",
    "MONSNO_POWARUN": "Castform",
    "MONSNO_REZIGIGASU": "Regigigas",
    "MONSNO_THERIMU": "Cherrim",
    "MONSNO_ZOROAAKU": "Zoroark",
}

PARAMETER_NAMES = {
    "PARA_AGI": "Speed",
    "PARA_AVOID": "evasion",
    "PARA_DEF": "Defense",
    "PARA_HIT": "accuracy",
    "PARA_POW": "Attack",
    "PARA_SPEDEF": "Special Defense",
    "PARA_SPEPOW": "Special Attack",
}

BATTLE_RULE_NAMES = {
    "BTL_RULE_DOUBLE": "Double Battles",
    "BTL_RULE_ROTATION": "Rotation Battles",
    "BTL_RULE_SINGLE": "Single Battles",
    "BTL_RULE_TRIPLE": "Triple Battles",
}

SEX_NAMES = {
    "PTL_SEX_FEMALE": "female",
    "PTL_SEX_MALE": "male",
}

ITEM_NAMES = {
    "ITEM_HAKKINDAMA": "the held item associated with Giratina's Origin Forme",
}

EQUIPMENT_NAMES = {
    "SOUBI_HIRUMASERU": "a flinch-causing held-item effect",
}

ROLE_NAMES = {
    "CHECK_ATTACK": "the attacking Pokémon",
    "CHECK_ATTACK_FRIEND": "the attacking Pokémon's ally",
    "CHECK_DEFENCE": "the defending Pokémon",
    "CHECK_DEFENCE_FRIEND": "the defending Pokémon's ally",
}


def _split_top_level(text: str, delimiter: str) -> list[str]:
    """Split a boolean expression without splitting nested function calls."""
    pieces: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            if char == quote and (index == 0 or text[index - 1] != "\\"):
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and text.startswith(delimiter, index):
            pieces.append(text[start:index].strip())
            index += len(delimiter)
            start = index
            continue
        index += 1
    pieces.append(text[start:].strip())
    return pieces


def _strip_outer_parens(text: str) -> str:
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        balanced = True
        for index, char in enumerate(text):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and index != len(text) - 1:
                    balanced = False
                    break
        if not balanced or depth != 0:
            break
        text = text[1:-1].strip()
    return text


def _enum_name(token: str, mapping: dict[str, str]) -> str:
    token = token.strip()
    if token in mapping:
        return mapping[token]
    if token == "0":
        return "zero"
    if token == "1":
        return "one"
    if token == "2":
        return "two"
    if token == "3":
        return "three"
    return token.replace("_", " ").lower().capitalize()


def _actor_phrase(token: str) -> str:
    token = token.strip()
    return ROLE_NAMES.get(token, {
        "ATK": "the attacking Pokémon",
        "DEF": "the defending Pokémon",
        "FRD": "the defending Pokémon's ally",
    }.get(token, "the relevant Pokémon"))


def _variable_phrase(token: str) -> str:
    token = token.strip()
    direct = {
        "ATK_tokusei": "the attacking Pokémon's ability",
        "atk_tokusei": "the attacking Pokémon's ability",
    "Atk_tokusei": "the attacking Pokémon's ability",
        "tokusei": "the attacking Pokémon's ability",
        "DEF_tokusei": "the defending Pokémon's ability",
        "def_tokusei": "the defending Pokémon's ability",
        "Def_Tokusei": "the defending Pokémon's ability",
        "FRD_tokusei": "the defending Pokémon's ally's ability",
        "ATK_type1": "the attacking Pokémon's first type",
        "ATK_type2": "the attacking Pokémon's second type",
        "DEF_type1": "the defending Pokémon's first type",
        "DEF_type2": "the defending Pokémon's second type",
        "FRD_type1": "the defending Pokémon's ally's first type",
        "FRD_type2": "the defending Pokémon's ally's second type",
        "ATK_sex": "the attacking Pokémon's sex",
        "DEF_sex": "the defending Pokémon's sex",
        "DefMonsNo": "the defending Pokémon's species",
        "wazaNo": "the current move",
        "MyWazaNo": "the current move",
        "CHK_rule": "the battle format",
        "CHK_turn": "the current battle turn",
        "CHK_weather": "the current weather",
        "CHK_nekodamashi": "the attacking Pokémon's Fake Out/action-used flag",
        "CHK_recycle": "the attacking Pokémon's Recycle state",
        "CHK_soubi": "the attacking Pokémon's held-item state",
        "CHK_takuwaeru": "the attacking Pokémon's Stockpile count",
        "DOKUBISHI_count": "the number of Toxic Spikes layers",
        "MAKIBISHI_count": "the number of Spikes layers",
        "HIKAE_count": "the number of usable reserves",
        "Weight": "the attacking Pokémon's weight",
        "Atk_SoubiEquip": "the attacking Pokémon's held-item effect",
    }
    if token in direct:
        return direct[token]
    return token.replace("_", " ").lower().capitalize()


def _value_phrase(token: str, left: str = "") -> str:
    token = token.strip()
    if token in ABILITY_NAMES:
        return ABILITY_NAMES[token]
    if token in TYPE_NAMES:
        return TYPE_NAMES[token]
    if token in MOVE_NAMES:
        return MOVE_NAMES[token]
    if token in SIDE_EFFECT_NAMES:
        return SIDE_EFFECT_NAMES[token]
    if token in FIELD_EFFECT_NAMES:
        return FIELD_EFFECT_NAMES[token]
    if token in GROUND_EFFECT_NAMES:
        return GROUND_EFFECT_NAMES[token]
    if token in STATUS_NAMES:
        return STATUS_NAMES[token]
    if token in SPECIES_NAMES:
        return SPECIES_NAMES[token]
    if token in BATTLE_RULE_NAMES:
        return BATTLE_RULE_NAMES[token]
    if token in SEX_NAMES:
        return SEX_NAMES[token]
    if token in ITEM_NAMES:
        return ITEM_NAMES[token]
    if token in EQUIPMENT_NAMES:
        return EQUIPMENT_NAMES[token]
    if token in PARAMETER_NAMES:
        return PARAMETER_NAMES[token]
    if token == "AISYOU_0BAI":
        return "no effect"
    if token == "AISYOU_1BAI":
        return "neutral effectiveness"
    if token == "AISYOU_2BAI":
        return "2× effectiveness"
    if token == "AISYOU_4BAI":
        return "4× effectiveness"
    if token == "LEVEL_ATTACK":
        return "higher attacker level"
    if token == "LEVEL_DEFENCE":
        return "higher defender level"
    if token == "LEVEL_EQUAL":
        return "equal levels"
    if token == "IF_FIRST_ATTACK":
        return "the attacker moves first"
    if token == "IF_FIRST_DEFENCE":
        return "the defender moves first"
    if token == "IF_FIRST_EQUAL":
        return "the Pokémon act at the same speed"
    if token == "0":
        if "count" in left.lower() or "state" in left.lower():
            return "zero"
        return "0"
    return token.replace("_", " ").lower().capitalize()


def _parse_ai_call(expression: str) -> tuple[str, list[str]] | None:
    match = re.fullmatch(r"AI_CMD\((.*)\)", expression.strip(), flags=re.S)
    if not match:
        return None
    args = _split_top_level(match.group(1), ",")
    if not args:
        return None
    return args[0].strip(), args[1:]


def _call_measurement(call: str, args: list[str]) -> str:
    target = _actor_phrase(args[0]) if args else "the relevant Pokémon"
    if call == "CMD_CHECK_TOKUSEI":
        return f"{target}'s ability"
    if call == "CMD_CHECK_TYPE":
        type_subjects = {
            "CHECK_WAZA": "the current move's type",
            "CHECK_ATTACK_TYPE1": "the attacking Pokémon's first type",
            "CHECK_ATTACK_TYPE2": "the attacking Pokémon's second type",
            "CHECK_DEFENCE_TYPE1": "the defending Pokémon's first type",
            "CHECK_DEFENCE_TYPE2": "the defending Pokémon's second type",
            "CHECK_ATTACK_FRIEND_TYPE1": "the attacking Pokémon's ally's first type",
            "CHECK_ATTACK_FRIEND_TYPE2": "the attacking Pokémon's ally's second type",
            "CHECK_DEFENCE_FRIEND_TYPE1": "the defending Pokémon's ally's first type",
            "CHECK_DEFENCE_FRIEND_TYPE2": "the defending Pokémon's ally's second type",
        }
        return type_subjects.get(args[0].strip(), f"{target}'s type") if args else "the relevant type"
    if call == "CMD_CHECK_MONSNO":
        return f"{target}'s species"
    if call == "CMD_CHECK_BTL_RULE":
        return "the battle format"
    if call == "CMD_CHECK_LAST_WAZA":
        return f"the last move used by {target}"
    if call == "CMD_CHECK_WAZA_AISYOU":
        return "the current move's effectiveness against the target"
    if call == "CMD_IF_SIDEEFF":
        return f"the side belonging to {target}"
    if call == "CMD_CHECK_SOUBI_ITEM":
        return f"{target}'s held item"
    if call == "CMD_CHECK_SOUBI_EQUIP":
        return f"{target}'s held-item effect"
    if call == "CMD_CHECK_POKESEX":
        return f"{target}'s sex"
    if call == "CMD_CHECK_TAKUWAERU":
        return f"{target}'s Stockpile count"
    if call == "CMD_CHECK_BENCH_COUNT":
        return f"{target}'s usable reserve count"
    if call == "CMD_CHECK_WEATHER":
        return "the current weather"
    if call == "CMD_FLDEFF_CHECK":
        return "the active field effect"
    return f"the result of {call.replace('CMD_', '').replace('_', ' ').lower()}"


def _describe_ai_call(call: str, args: list[str]) -> str:
    target = _actor_phrase(args[0]) if args else "the relevant Pokémon"
    if call in {"CMD_IF_POKESICK", "CMD_IFN_POKESICK"}:
        present = "has a status condition"
        return f"{target} {present}" if call == "CMD_IF_POKESICK" else f"{target} has no status condition"
    if call in {"CMD_IF_DOKUDOKU", "CMD_IFN_DOKUDOKU"}:
        present = "is badly poisoned"
        return f"{target} {present}" if call == "CMD_IF_DOKUDOKU" else f"{target} is not badly poisoned"
    if call in {"CMD_IF_WAZASICK", "CMD_IFN_WAZASICK"} and len(args) >= 2:
        status = _value_phrase(args[1])
        if call == "CMD_IF_WAZASICK":
            return f"{target} is affected by {status}"
        return f"{target} is not affected by {status}"
    if call in {"CMD_IF_SIDEEFF", "CMD_IFN_SIDEEFF"} and len(args) >= 2:
        effect = _value_phrase(args[1])
        subject = f"the side belonging to {target}"
        return f"{subject} has {effect}" if call == "CMD_IF_SIDEEFF" else f"{subject} does not have {effect}"
    if call in {"CMD_IF_MIGAWARI"}:
        return f"{target} has a Substitute"
    if call in {"CMD_IFN_BENCH_COND"}:
        return f"{target} has no reserve Pokémon with the checked condition"
    if call in {"CMD_IF_BENCH_COND"}:
        return f"{target} has a reserve Pokémon with the checked condition"
    if call in {"CMD_IF_EXIST_GROUND"} and args:
        return f"the field has {_value_phrase(args[0])}"
    if call == "CMD_FLDEFF_CHECK" and args:
        return f"the field has {_value_phrase(args[0])}"
    if call == "CMD_IF_FIRST" and args:
        return _value_phrase(args[0])
    if call == "CMD_IF_MULTI":
        return "the battle is in Multi mode"
    if call == "CMD_IF_MEGAEVOLVED":
        return f"{target} is Mega-Evolved"
    if call == "CMD_IF_LEVEL" and args:
        return _value_phrase(args[0])
    if call in {"CMD_IF_HP_UNDER", "CMD_IF_HP_OVER", "CMD_IF_HP_EQUAL"} and len(args) >= 2:
        relation = {
            "CMD_IF_HP_UNDER": "below",
            "CMD_IF_HP_OVER": "above",
            "CMD_IF_HP_EQUAL": "exactly",
        }[call]
        return f"{target}'s HP is {relation} {args[1]}%"
    if call in {"CMD_IF_PARA_UNDER", "CMD_IF_PARA_OVER", "CMD_IF_PARA_EQUAL", "CMD_IFN_PARA_EQUAL"} and len(args) >= 3:
        parameter = _value_phrase(args[1])
        relation = {
            "CMD_IF_PARA_UNDER": "below",
            "CMD_IF_PARA_OVER": "above",
            "CMD_IF_PARA_EQUAL": "exactly",
            "CMD_IFN_PARA_EQUAL": "not exactly",
        }[call]
        return f"{target}'s {parameter} parameter is {relation} {args[2]} in the native AI value scale"
    if call in {"CMD_IF_TYPE_EX"} and len(args) >= 2:
        return f"{target} has {_value_phrase(args[1])} as its special/ex type"
    if call in {"CMD_IF_HAVE_ITEM"} and len(args) >= 2:
        return f"{target} holds {_value_phrase(args[1])}"
    if call in {"CMD_IF_HAVE_WAZA", "CMD_IFN_HAVE_WAZA"} and len(args) >= 2:
        move = _value_phrase(args[1])
        return f"{target} has {move}" if call == "CMD_IF_HAVE_WAZA" else f"{target} does not have {move}"
    if call in {"CMD_IF_HAVE_WAZA_AISYOU_OVER", "CMD_IF_HAVE_WAZA_AISYOU_EQUAL"}:
        return "the checked reserve has the required type effectiveness"
    if call in {"CMD_IF_RND_UNDER", "CMD_IF_RND_OVER", "CMD_IF_RND_EQUAL"} and args:
        relation = {
            "CMD_IF_RND_UNDER": "below",
            "CMD_IF_RND_OVER": "above",
            "CMD_IF_RND_EQUAL": "equal to",
        }[call]
        return f"the AI random roll is {relation} {args[0]}"
    if call in {"CMD_IF_COMMONRND_UNDER", "CMD_IF_COMMONRND_OVER", "CMD_IF_COMMONRND_EQUAL"} and args:
        relation = {
            "CMD_IF_COMMONRND_UNDER": "below",
            "CMD_IF_COMMONRND_OVER": "above",
            "CMD_IF_COMMONRND_EQUAL": "equal to",
        }[call]
        return f"the shared partner random roll is {relation} {args[0]}"
    if call == "CMD_CHECK_WAZA_AISYOU" and len(args) >= 4:
        expected = _value_phrase(args[3])
        if args[3].strip() == "AISYOU_0BAI":
            return "the current move has no effect against the target"
        return f"the current move has {expected} against the target"
    if call == "CMD_IF_WAZA_HINSHI" and args:
        return f"the current move would KO {target}"
    if call == "CMD_IFN_WAZA_HINSHI" and args:
        return f"the current move would not KO {target}"
    if call == "CMD_IF_LAST_WAZA_DAMAGE_CHECK" and len(args) >= 2:
        return "the previous damage comparison meets the requested threshold"
    if call == "CMD_IF_HAVE_BATSUGUN" and len(args) >= 2:
        return f"{_actor_phrase(args[0])} has a super-effective move against {_actor_phrase(args[1])}"
    if call == "CMD_IF_HAVE_ITEM" and len(args) >= 2:
        return f"{target} holds {_value_phrase(args[1])}"
    if call == "CMD_IF_CAN_MEGAEVOLVE":
        return f"{target} can Mega Evolve"
    if call == "CMD_IF_MIRAIYOCHI":
        return f"{target} is under a delayed-action effect"
    if call == "CMD_IF_CONTFLG" and len(args) >= 2:
        return f"{target} has the checked continuous-effect flag"
    if call == "CMD_IFN_CONTFLG" and len(args) >= 2:
        return f"{target} does not have the checked continuous-effect flag"
    if call == "CMD_IF_DMG_PHYSIC_OVER":
        return f"{target}'s Attack is higher than its Special Attack"
    if call == "CMD_IF_DMG_PHYSIC_UNDER":
        return f"{target}'s Attack is lower than its Special Attack"
    if call == "CMD_IF_DMG_PHYSIC_EQUAL":
        return f"{target}'s Attack equals its Special Attack"
    if call == "CMD_IF_ATE_KINOMI":
        return f"{target} has already eaten its relevant Berry"
    if call == "CMD_IFN_HINSHI":
        return f"{target} is not fainted"
    if call == "CMD_IF_HINSHI":
        return f"{target} is fainted"
    if call == "CMD_IFN_WAZASICK":
        return f"{target} is not in the checked move-state"
    return _call_measurement(call, args)


def _describe_operand(operand: str) -> str:
    operand = _strip_outer_parens(operand.strip())
    call = _parse_ai_call(operand)
    if call:
        return _describe_ai_call(*call)
    if operand in ABILITY_NAMES:
        return ABILITY_NAMES[operand]
    if operand in TYPE_NAMES:
        return TYPE_NAMES[operand]
    if operand in MOVE_NAMES:
        return MOVE_NAMES[operand]
    if operand in SIDE_EFFECT_NAMES:
        return SIDE_EFFECT_NAMES[operand]
    if operand in FIELD_EFFECT_NAMES:
        return FIELD_EFFECT_NAMES[operand]
    if operand in GROUND_EFFECT_NAMES:
        return GROUND_EFFECT_NAMES[operand]
    if operand in STATUS_NAMES:
        return STATUS_NAMES[operand]
    if operand in SPECIES_NAMES:
        return SPECIES_NAMES[operand]
    if operand in BATTLE_RULE_NAMES:
        return BATTLE_RULE_NAMES[operand]
    if operand in SEX_NAMES:
        return SEX_NAMES[operand]
    if operand in ITEM_NAMES:
        return ITEM_NAMES[operand]
    if operand in EQUIPMENT_NAMES:
        return EQUIPMENT_NAMES[operand]
    if re.fullmatch(r"-?\d+", operand):
        return operand
    return _variable_phrase(operand)


def _negate_clause(clause: str) -> str:
    replacements = {
        " has ": " does not have ",
        " is ": " is not ",
        " are ": " are not ",
        " moves first": " does not move first",
        " is Mega-Evolved": " is not Mega-Evolved",
    }
    for old, new in replacements.items():
        if old in clause:
            return clause.replace(old, new, 1)
    return f"it is not the case that {clause}"


def _describe_expression(expression: str) -> str:
    expression = _strip_outer_parens(" ".join(expression.split()))
    or_parts = _split_top_level(expression, "||")
    if len(or_parts) > 1:
        descriptions = [_describe_expression(part) for part in or_parts]
        return "at least one of the following is true: " + "; ".join(descriptions)
    and_parts = _split_top_level(expression, "&&")
    if len(and_parts) > 1:
        descriptions = [_describe_expression(part) for part in and_parts]
        return "all of the following are true: " + "; ".join(descriptions)

    comparison = re.match(r"^(.*?)\s*(==|!=|>=|<=|>|<)\s*(.*?)$", expression)
    if comparison:
        left, operator, right = comparison.groups()
        left = left.strip()
        right = right.strip()
        call = _parse_ai_call(left)
        if call:
            call_name, args = call
            if call_name == "CMD_CHECK_WAZA_AISYOU" and len(args) >= 4:
                if right == "AISYOU_0BAI":
                    phrase = "the current move has no effect against the target"
                else:
                    phrase = f"the current move has {_value_phrase(right)} against the target"
                return _negate_clause(phrase) if operator == "!=" else phrase
            if call_name == "CMD_FLDEFF_CHECK":
                phrase = f"the field has {_value_phrase(right)}"
                return _negate_clause(phrase) if operator == "!=" else phrase
            if call_name == "CMD_IF_SIDEEFF":
                phrase = f"the side belonging to {_actor_phrase(args[0]) if args else 'the relevant Pokémon'} has {_value_phrase(right)}"
                return _negate_clause(phrase) if operator == "!=" else phrase
            measurement = _call_measurement(call_name, args)
            value = _value_phrase(right, measurement)
            if operator == "==":
                return f"{measurement} is {value}"
            if operator == "!=":
                return f"{measurement} is not {value}"
            if operator == ">=":
                return f"{measurement} is at least {value}"
            if operator == "<=":
                return f"{measurement} is at most {value}"
            if operator == ">":
                return f"{measurement} is above {value}"
            return f"{measurement} is below {value}"

        measurement = _variable_phrase(left)
        value = _value_phrase(right, measurement)
        if operator == "==":
            return f"{measurement} is {value}"
        if operator == "!=":
            return f"{measurement} is not {value}"
        if operator == ">=":
            return f"{measurement} is at least {value}"
        if operator == "<=":
            return f"{measurement} is at most {value}"
        if operator == ">":
            return f"{measurement} is above {value}"
        return f"{measurement} is below {value}"

    return _describe_operand(expression)


def _describe_path(context: list[str]) -> str:
    conditions: list[str] = []
    for branch in context:
        branch = " ".join(branch.split())
        if branch == "else":
            conditions.append("the preceding branch in this if/else chain did not match")
            continue
        match = re.match(r"^(else )?if\((.*)\)$", branch, flags=re.S)
        if not match:
            conditions.append(_describe_expression(branch))
            continue
        prefix, expression = match.groups()
        description = _describe_expression(expression)
        if prefix:
            conditions.append("the preceding branch in this if/else chain did not match, and " + description)
        else:
            conditions.append(description)
    if not conditions:
        return "unconditionally"
    if len(conditions) == 1:
        return conditions[0]
    return " and ".join(conditions)


def _score_effect_phrase(statement: str) -> str:
    match = re.match(r"SCORE\s*\+=\s*(-?\d+)", statement.strip())
    if not match:
        return "changes the score as shown in the source"
    amount = int(match.group(1))
    if amount < 0:
        unit = "point" if abs(amount) == 1 else "points"
        return f"subtracts {abs(amount)} {unit} from the move's score"
    if amount > 0:
        unit = "point" if amount == 1 else "points"
        return f"adds {amount} {unit} to the move's score"
    return "does not change the move's score"


def _score_write_returns_immediately(body: str) -> list[bool]:
    """Report whether each source-level score write is followed by return."""
    source = _clean_source_body(body)
    results: list[bool] = []
    for match in re.finditer(r"SCORE\s*\+=\s*[^;]+;", source):
        tail = source[match.end():]
        results.append(bool(re.match(r"\s*return\b", tail)))
    return results


def _basic_special_description(name: str) -> str | None:
    descriptions = {
        "Basic_ConaHoushi()": (
            "Trigger: called before the other Basic checks for the current move. "
            "If the move is Stun Spore, Sleep Powder, Poison Powder, Rage Powder, Spore, or Powder "
            "and the defender has Overcoat, the move is penalized by 10 points unless the attacker has "
            "Mold Breaker, Teravolt, or Turboblaze. If that first penalty is applied, the helper returns "
            "immediately. Otherwise, if the defender is Grass-type, it subtracts 10 points and returns. "
            "If neither condition applies, it returns without changing the score."
        ),
        "Calc_BasicDamage()": (
            "Trigger: called for a damaging move before the general Basic sequence checks. "
            "If the move has no effect against the defender, it subtracts 10 points and stops this damage "
            "evaluation. The exception is a Ground-type move against Levitate when the attacker has Mold "
            "Breaker, Teravolt, or Turboblaze; that immunity is treated as bypassed, so the initial penalty "
            "is skipped. If the attacker has any of those three ability-bypassing abilities, the helper then "
            "skips the listed defensive-ability checks. Otherwise it dispatches to the matching ability helper: "
            "Volt Absorb, Motor Drive, or Lightning Rod checks Electric moves; Water Absorb, Storm Drain, or "
            "Dry Skin checks Water moves; Flash Fire checks Fire moves; Wonder Guard checks whether the move "
            "is at least super-effective; Levitate checks Ground moves unless Gravity is active; and Sap Sipper "
            "checks Grass moves. If a helper handles the move, this function returns immediately; otherwise the "
            "caller continues to the general Basic rules."
        ),
        "BasicDmg_00_1()": (
            "Trigger: called when the defender's ability is Volt Absorb, Motor Drive, or Lightning Rod. "
            "Condition: the current move is Electric-type. Effect: subtracts 12 points and reports the move "
            "as handled; for any other move type it makes no score change and reports that it did not handle it."
        ),
        "BasicDmg_00_2()": (
            "Trigger: called when the defender's ability is Water Absorb, Storm Drain, or Dry Skin. "
            "Condition: the current move is Water-type. Effect: subtracts 12 points and reports the move "
            "as handled; for any other move type it makes no score change and reports that it did not handle it."
        ),
        "BasicDmg_00_3()": (
            "Trigger: called when the defender has Flash Fire. Condition: the current move is Fire-type. "
            "Effect: subtracts 12 points and reports the move as handled; for any other move type it makes "
            "no score change and reports that it did not handle it."
        ),
        "BasicDmg_00_4()": (
            "Trigger: called when the defender has Wonder Guard. If the current move is 2× effective or 4× "
            "effective, it makes no score change and reports that it did not handle the move. Otherwise it "
            "subtracts 10 points and reports the move as handled."
        ),
        "BasicDmg_00_5()": (
            "Trigger: called when the defender has Levitate. Condition: the current move is Ground-type and "
            "Gravity is not active. Effect: subtracts 10 points and reports the move as handled. Ground moves "
            "are not penalized when Gravity is active, and other move types are not handled."
        ),
        "BasicDmg_00_7()": (
            "Trigger: called when the defender has Sap Sipper. Condition: the current move is Grass-type. "
            "Effect: subtracts 12 points and reports the move as handled; other move types are not handled."
        ),
        "Bouon_Check()": (
            "Trigger: checked before the selected Basic move-sequence evaluator. If the defender has Soundproof, "
            "the attacker does not have Mold Breaker, Teravolt, or Turboblaze, and the current move is one of "
            "the sound-based moves in the source list, subtracts 10 points and reports the move as handled. "
            "Otherwise it leaves the score unchanged."
        ),
        "Boudan_Check()": (
            "Trigger: checked after the sound-move check and before the selected Basic move-sequence evaluator. "
            "If the defender has Bulletproof, the attacker does not have Mold Breaker, Teravolt, or Turboblaze, "
            "and the current move is one of the ball- or bomb-based moves in the source list, subtracts 10 points "
            "and reports the move as handled. Otherwise it leaves the score unchanged."
        ),
    }
    return descriptions.get(name)


def basic_human_score_description(name: str, body: str) -> str | None:
    special = _basic_special_description(name)
    if special:
        return special
    paths = extract_score_paths(body)
    if not paths:
        return None

    sequence_match = re.search(r"(?:Seq_|Seq)(\d+)", name)
    if sequence_match:
        trigger = f"the Basic dispatcher selects move sequence {sequence_match.group(1)}"
    else:
        trigger = "this Basic helper is reached on the current move's evaluation path"

    immediate_returns = _score_write_returns_immediately(body)
    rules: list[str] = []
    for index, (context, statement) in enumerate(paths, start=1):
        return_note = " The function then returns immediately." if immediate_returns[index - 1] else " Evaluation continues after this adjustment."
        condition = _describe_path(context)
        condition_intro = condition if condition == "unconditionally" else f"when {condition}"
        rules.append(
            f"Rule {index}: {condition_intro}, the AI {_score_effect_phrase(statement)}.{return_note}"
        )
    behavior = ""
    if any("else" in branch for context, _ in paths for branch in context):
        behavior += " Within an if/else chain, only the first matching branch is reached."
    return f"Trigger: {trigger}. " + " ".join(rules) + behavior


def basic_exact_score_description(name: str, body: str) -> str | None:
    paths = extract_score_paths(body)
    if not paths:
        return None

    sequence_match = re.search(r"(?:Seq_|Seq)(\d+)", name)
    subject = f"Basic AI sequence {sequence_match.group(1)}" if sequence_match else "This Basic helper"
    rendered_paths: list[str] = []
    for context, statement in paths:
        score_match = re.match(r"SCORE\s*\+=\s*(.*?);?$", statement)
        score = score_match.group(1).strip() if score_match else statement
        if context:
            guard = " / ".join(
                _markdown_safe_expression(part) for part in context
            )
        else:
            guard = "unconditional"
        rendered_paths.append(f"{guard} ⇒ SCORE += {score}")

    return (
        f"{subject}. Exact source-level score paths, in source order "
        f"(nested conditions separated by `/`; `else` branches are preserved): "
        + "; ".join(rendered_paths)
        + ". The complete normalized body below is authoritative for branch "
        "complements, early returns, and called helpers."
    )


def describe_function(role: str, name: str, body: str, score_effects: list[str]) -> str:
    if role == "Basic":
        human = basic_human_score_description(name, body)
        if human:
            return human

    specific = DESCRIPTIONS.get((role, name))
    if specific:
        return specific

    sequence_match = re.search(r"(?:Seq_|Seq)(\d+)", name)
    topics: list[str] = []
    for command in re.findall(r"CMD_[A-Z0-9_]+", body):
        topic = COMMAND_TOPICS.get(command)
        if topic and topic not in topics:
            topics.append(topic)
    topic_text = ", ".join(topics[:5])
    if len(topics) > 5:
        topic_text += ", and other state"
    effect_text = ", ".join(dict.fromkeys(score_effects)) or "no direct score write"

    if sequence_match:
        sequence = sequence_match.group(1)
        subject = "move sequence " + sequence
        if role == "Double":
            subject = "Double-battle sequence " + sequence
        elif role == "Expert":
            subject = "Expert move sequence " + sequence
        elif role == "Basic":
            subject = "Basic move sequence " + sequence
        if topic_text:
            return f"Evaluates {subject}; uses {topic_text} and applies {effect_text} when the guarded conditions below succeed."
        return f"Evaluates {subject} and applies {effect_text} when the guarded conditions below succeed."

    if name.endswith("_Main()") or name.endswith("_Main"):
        return f"Main {role.lower()} evaluator for the branch shown below; applies {effect_text}."
    if role == "Pokechange":
        return f"Evaluates a switching condition using {topic_text or 'the native battle-state interface'}; its exact return path is shown below."
    return f"Evaluates a {role.lower()} rule using {topic_text or 'the native battle-state interface'}; applies {effect_text} under the guarded conditions below."


def render(input_path: Path) -> str:
    lines = input_path.read_text(encoding="utf-8").splitlines()
    sections = extract_sections(lines)
    manifest_path = input_path.with_suffix(".json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata_by_role: dict[str, dict[str, dict[str, object]]] = {}
    for script in manifest["manifest"]["scripts"]:
        metadata_by_role[script["role"]] = {
            function["name"]: function for function in script["functions"]
        }

    output: list[str] = [
        "# USUM Battle AI score-rule index",
        "",
        "> This is a derived condition-to-score index for the active USUM Battle Tree programs. It is generated from the normalized source-level specification; the retail-only Intrude and Royal bytecode listings remain in [battle-ai-full-spec.md](battle-ai-full-spec.md).",
        "",
        "## How to read this document",
        "",
        "For a move/target candidate, the C++ judge starts at `100`. Each enabled Pawn program starts its own `p_Score` at `0`, evaluates native `AI_CMD` predicates, and applies the `SCORE +=` writes shown below. The returned script scores are added together. A condition that is not met contributes nothing; multiple writes can accumulate unless the function returns first.",
        "Names such as `BaciAI_Seq_011()` are AI/move-sequence identifiers selected by the dispatcher; they are not move names. The complete specification shows which dispatcher cases call each sequence function and preserves the native enum names when their exact semantic expansion is not established.",
        "",
        "The table's `What it does` column is a plain-language translation of each reachable rule: it names the trigger, the battle conditions, the score adjustment, and any immediate return or branch-order behavior. The entries also show complete normalized function bodies, not only the final score line. Therefore the `if`, `else`, `switch`, random threshold, and early-return conditions surrounding every source-level score write remain available as authoritative evidence. Helper functions called by a dispatcher are listed separately, so the caller's move-sequence selection must also be followed.",
        "",
        "## Influence-closure definition",
        "",
        "For each active script, this index starts at `main` and follows every recovered local function call. It therefore includes every entry point, dispatcher, caller, and predicate/helper reachable during that script's evaluation. Functions are classified as direct score writers, indirect callers/helpers on a score path, or reachable dispatcher/predicate support. Pokechange predicates are included even when they do not call the score helper themselves, because their boolean return values gate the call to `PokeChangeOK(20)`.",
        "",
        "The local-call graph is conservative: it records which functions are referenced, while the exact bodies below determine which branch and return value actually controls a score write. Expert has 17 source functions that are not reachable from `main`; they remain documented in the full specification but are not presented as active score-influence functions here.",
        "",
        "## Retail adjustment inventory",
        "",
        "| Program | Retail score-delta constants observed |",
        "|---|---|",
    ]
    for role in ACTIVE_ROLES:
        output.append(f"| {role} | {RETAIL_DELTAS[role]} |")

    output.extend([
        "",
        "The retail inventory is the set of constants observed in the extracted US AMX members. The source listings below provide the conditions for the recovered source programs. A few retail members contain inlined or computed score expressions whose bytecode constants are broader than the direct source-literal inventory; those exact retail listings are retained in the full specification rather than silently re-labelled as source rules.",
        "",
        "## Pokechange score formula",
        "",
        "Switching is different from move scoring. One of seven switch reasons can call `PokeChangeOK(20)`, which enables switching and adds:",
        "",
        "```text",
        "SwitchScriptScore = 20",
        "                    − 10  if the trainer is a scenario trainer and the bench can Mega Evolve",
        "                    + 2   if maximum effective bench power is at least 160",
        "                    + 3   if maximum effective bench power is at least 200",
        "                    + 4   if maximum effective bench power is at least 240",
        "```",
        "",
        "The seven enabling reasons are: the last turn of Perish Song; a reserve that can break Wonder Guard; a reserve that improves a zero-effect matchup; escaping a bad Choice-locked matchup; exploiting an ability that nullifies the previous damage move; curing sleep or freeze through Natural Cure; and improving the matchup after the previous damage move. The exact guards are included in the Pokechange functions below. Only the first successful reason is used because the main procedure returns immediately.",
        "",
    ])

    for role in ACTIVE_ROLES:
        functions = extract_functions(
            sections.get(role, []),
            role,
            metadata_by_role.get(role, {}),
        )
        output.extend([f"## {role}: exact guarded score rules", ""])
        if not functions:
            output.append("No score-producing function was extracted.")
            output.append("")
            continue
        output.append("| Function | Source lines | Influence role | What it does | Direct score writes | Calls |")
        output.append("|---|---:|---|---|---|---|")
        for function in functions:
            output.append(
                f"| `{function['name']}` | {function['source_lines']} | {function['influence_class']} | {function['description']} | {function['score_effects']} | {function['local_calls']} |"
            )
        output.append("")
        output.append("The complete guarded bodies follow:")
        output.append("")
        for function in functions:
            output.append(
                f"### `{function['name']}` (source lines {function['source_lines']})"
            )
            output.append("")
            output.append("```text")
            output.append(function["body"])
            output.append("```")
            output.append("")

    output.extend([
        "## What this does and does not establish",
        "",
        "This index documents the exact source-level conditions and score writes represented in the recovered programs. It does not collapse native queries into universal weights: for example, `CHECK_WAZA_AISYOU`, `IF_HP_UNDER`, and damage queries return runtime values, and different scripts use those values in different branches. Random predicates can make the same candidate receive different contributions on different executions.",
        "",
        "For the exact native return contracts, command IDs, retail AMX disassembly, and source line provenance, see [battle-ai-full-spec.md](battle-ai-full-spec.md).",
        "",
    ])
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="derived battle-ai-full-spec.md")
    parser.add_argument("output", type=Path, help="score-rule index to write")
    args = parser.parse_args()
    args.output.write_text(render(args.input), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
