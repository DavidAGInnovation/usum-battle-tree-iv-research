# Battle AI: script selection and tactical evaluation

This note documents what the source and the analyzed US retail build establish
about the Battle Tree battle AI. It separates the engine behavior that is
directly visible in C++ from the tactical rules stored in the retail Pawn/AMX
programs.

## Bottom line

For the ordinary Battle Tree trainer path, the constructor-side base mask is:

```text
0x107 = 0x001 BASIC
      | 0x002 STRONG
      | 0x004 EXPERT
      | 0x100 POKECHANGE_BASIC
```

This is not one scalar “AI level”. It enables three move-scoring programs and
one switching program. The engine runs every enabled program in the relevant
judge, adds their returned scores, and chooses the highest-scoring action. The
source labels `BASIC` (basic), `STRONG` (攻撃型AI, attack-oriented), and
`EXPERT` (expert) establish their intended roles, but do not make either one a
strict superset of Basic. The command-set interpretation is disproved below,
and the stronger score-dominance claims are disproved by legal ROM-derived
counterexamples in [`recovered/ai-score-witnesses.json`](../recovered/ai-score-witnesses.json).
An action comparison remains a separate utility-and-tie-policy question.

The current Battle Tree evidence also does not show a trainer-ID-specific AI
upgrade. `SetVsTrainer` applies the same base mask to the trainer data and has
no branch that selects a different mask for a featured character. Battle mode
and phase overrides are separate: Double/Multi adds the Double script, Royal
uses the Royal script, and intrusion/reinforcement code can replace the mask.

## Recovery status for the remaining evidence

The actual decrypted US retail ROM and the complete Momiji source archive are
now available as analysis inputs. `scripts/extract-retail-battle-ai.py`
reproduces the extraction without copying either input into the repository. It
recovers:

- RomFS `/a/0/8/4`, a 410,792-byte GARC with eleven valid AMX members, hash
  `91bcf5119e76ee06ac55d081b14c1951ecfd7c9d59152548c9478750be33c28d`;
- the raw ExeFS `.code` section, 5,914,624 bytes at VA base `0x100000`, hash
  `b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09`; and
- the standard Pawn VM (`amx.c`/`amx.h`), the Game Freak Pawn host
  (`gfl2_PawnBase.*`), and the complete native AI dispatcher and command
  handler (`btl_AiScript.cpp`, `btl_BattleAiCommand.cpp`,
  `btl_AiScriptCommandHandler.cpp`, and `tr_ai_cmd.h`) from the source archive.

This removes “missing input files” as the reason the VM/native analysis could
not proceed. The source archive still omits the generated `BattleAi.gaix`
file itself, but its archived Pawn project history and archived
`GFArchiver.exe` resolve the numeric member order: the project lists the
scripts in ascending name order, the archiver exposes the corresponding
`name_up` sort mode, and the tracked resource build rules invoke that mode.
The retail member order is exactly
`allowance, band, basic, double, expert, intrude, item, moving, pokechange,
royal, strong`. Thus the numeric `BattleAi.gaix` map is reconstructed exactly
from independent source/tool and retail-archive evidence; only the original
generated file bytes and a direct runtime `datIdx` observation remain absent.
The recovered source shows exactly how the VM is initialized, how `AI_CMD` is
dispatched, and how `p_Score` and `p_PokeChangeEnable` are read; proving every
concrete score for every battle state still requires a VM execution/model of
the native battle-state queries.

### Retail `ai_bit` writer candidate sweep

The recovered source has two `ai_bit` layouts: `BSP_TRAINER_DATA::CORE_DATA::ai_bit`
at offset `0x4` and `MainModule::TRAINER_DATA::ai_bit` at offset `0x1c`. The new
read-only scanner
[`scripts/audit-retail-ai-mask-writers.py`](../scripts/audit-retail-ai-mask-writers.py)
enumerates scalar, double-word, and register-list stores whose effective
address reaches either source-layout displacement in the exact extracted
build. It covers all 132 extracted CRO code segments and both linear ARM and
Thumb over-approximations of the executable `.code` text region from the
retail ExHeader. On the hashed inputs
above it found:

| Image region | Store candidates |
| --- | ---: |
| ExeFS `.code` text, ARM sweep | 25,604 |
| ExeFS `.code` text, Thumb sweep | 19,703 |
| 132 CRO code segments, ARM sweep | 22,338 |
| **Total** | **67,645** |

The displacement is not an object identity: it is also common in stack frames
and unrelated C++ structures. For example, `Battle.cro` contributes candidate
stores at both offsets, including an initializer-like pair and a loop over
an array-of-structures. The scanner now parses all 132
CRO relocation tables: 45,221 import and 56,581 internal records, all 101,802
recognized as `R_ARM_ABS32`, with 58,255 executable-segment targets and no
malformed entries. None of the candidate stores is itself a relocation
patch site. The expanded pass recognizes scalar, double-word, and register-list
stores. The retail ExHeader gives the executable text boundary as `0x4ba000`
bytes; the raw `.code` tail is not instruction text and is excluded from the
main image sweep. On that section-aware input it classifies 67,645 candidates
in total: 25,604 ARM and 19,703 Thumb `.code` candidates plus 22,338 ARM
candidates across the 132 CRO segments.
It also confirms three direct source-mapped writers in the main image:
`0x58260` (`stm r5,{r4,r7}`) and `0x582d4` (`str r7,[r5,#4]`) write the
ordinary `0x107`/Double `0x10f` mask at `+0x4` on the two `SetVsTrainer`
branches, while `0x59370` (`str r1,[r2,#4]`) writes Royal `0x127`. The
remaining base classifications are 5,447 function-argument, 534
immediate-constant, 2,109 literal-constant, 586 memory-derived, 5,036
relocation-derived, 11,740 stack-relative, and 42,193 unknown; the exact
counts are recorded in
[`recovered/retail-ai-mask-provenance.json`](../recovered/retail-ai-mask-provenance.json).
The ExHeader values and the exact section-boundary calculation are preserved in
[`recovered/retail-code-layout.json`](../recovered/retail-code-layout.json).
The scan reports 325 mask-valued candidates: 321 immediate values, 2
literal-pool values, and 2 computed values. Most are same-offset collisions
with `0x7`, `0x8`, or `0xf`; only the three `0x10f`/`0x127` stores are mapped
to the source. Of the two executable Thumb constants, one (`0x3d3600`) is an
ARM-code overlap. The other (`0x688`) is real Thumb code, but its surrounding
sequence ORs a flag into offset `0`, writes `8` at `+0x1c`, and then consumes a
separate `+0x24` payload. That behavior is incompatible with both recovered
source layouts: `MainModule::TRAINER_DATA` has a pointer at `+0x0`, while
`BSP_TRAINER_DATA::CORE_DATA` has `tr_id` at `+0x0` and `ai_bit` at `+0x4`.
It is therefore disproved as either source-defined `ai_bit` writer. The
remaining ARM mask-valued candidate is a stack temporary. The two exact stores
that survived those local checks are now closed by
[`scripts/verify-proof-boundary-separation.py`](../scripts/verify-proof-boundary-separation.py):
`.code:0x45ec` stores the read-only/data-tail pointer `0x565e1d`, and
`Battle.cro:0x1e80` is the third virtual slot of RTTI
`N4gfl26Effect6ConfigE` (`gfl2::Effect::Config`). They are not AI-mask
writers. The source-complete field-sensitive lift, including the source/project
topology and PM_DEBUG exclusions, is reproduced by
[`scripts/verify-retail-ai-writer-whole-program.py`](../scripts/verify-retail-ai-writer-whole-program.py)
and recorded in
[`recovered/retail-ai-writer-whole-program.json`](../recovered/retail-ai-writer-whole-program.json).
At the `MainModule::TRAINER_DATA` layout, the source separately specifies
aggregate initialization, `trainerParam_StoreCore` zeroing, and
`trainerParam_StoreNPCTrainer` copying `GetAIBit()` into `+0x1c`. The source
inventory also includes the serialized `BSP_TRAINER_DATA::Deserialize` copy and
the `BattleFes::setAiBit` Basic-only reduction. The residual value/type checks
remain preserved in
[`recovered/proof-boundary-separation.json`](../recovered/proof-boundary-separation.json).

## Runtime flow

The source-level flow is:

1. Battle setup stores an `ai_bit` mask in the trainer/client parameters. The
   ordinary Battle Tree trainer path uses `AI_BIT`; `SetAiBit` adds the Double
   bit for Double/Multi rules.
2. `BattleAi` constructs three judges—item, Pokémon-change, and move—with the
   same script-bit mask.
3. Each `AiJudge` scans its permitted script-number range from low to high and
   runs every enabled bit. The mask therefore selects a set of scripts, not a
   single branch.
4. `AiScript` loads the selected archive member into the Pawn VM, registers the
   native `AI_CMD` dispatcher, initializes `p_Score` to zero, and passes the
   `AiScriptCommandHandler` as `p_AIHandler`.
5. The Pawn program calls native battle queries and writes its score (and, for
   switching, `p_PokeChangeEnable`). C++ reads the result and accumulates it.
6. Forced actions are handled first. Otherwise the item, switch, move, or
   fallback action with the highest score is selected; ties are resolved with
   the AI random generator.

The relevant source files are `battle_def.h`, `btl_AiJudge.cpp`,
`btl_BattleAi.cpp`, `btl_AiWazaJudge.cpp`, `btl_AiPokeChangeJudge.cpp`,
`btl_AiScript.cpp`, and `btl_BattleAiCommand.cpp` in the Momiji snapshot.

## Mask writers and mode/phase overrides

The source-level mask inventory is more informative than the trainer labels.
`BattleAi::ChangeScript` replaces the target mask in all three judges; it does
not add a bit to the previous mask. The reachable writes and effective
selection branches are:

| Writer or selector | Context | Mask written/returned | Consequence |
| --- | --- | --- | --- |
| `BattleInst::SetVsTrainer` + `SetAiBit` | Ordinary NPC trainer or AI partner | `AI_BIT = 0x107`; `0x10f` in Double/Multi | Basic + Strong + Expert + Pokechange, with Double added for the two multi-Pokémon rules. No trainer-ID branch appears here. |
| `BattleInst::SetVsTrainerRoyal` | Royal setup data | Stored `AI_BIT + ROYAL = 0x127` | The later Royal selector below is the effective runtime branch. |
| `MainModule::GetClientAIBit` | `BTL_RULE_ROYAL` | `0x125` (`BASIC + EXPERT + ROYAL + POKECHANGE`) | Royal omits Strong in the effective selector and uses the Royal script. |
| `MainModule::GetClientAIBit` | Ultra Beast, or wild Nūṣi/Nekurozuma | `0x007` | Basic + Strong + Expert only; no Pokechange bit. |
| `MainModule::GetClientAIBit` | Ordinary wild Double | `0x008` | Double-only wild AI branch. |
| `MainModule::GetClientAIBit` | Record-fight NPC data | `0x107`, plus `DOUBLE` for Double | Uses the fixed record-fight mask rather than the stored NPC mask. |
| `BTL_CLIENT::SetIntrudeAI` | Intrusion phase | `0x040` | Replaces the mask with Intrude only. |
| `BTL_CLIENT::SetReinforceAI` | Reinforcement phase | `0x00f` (`BASIC + STRONG + EXPERT + DOUBLE`) | Replaces the mask; Pokechange is not enabled. |

For ordinary non-record NPC battles, `GetClientAIBit` returns the stored
`m_trainerParam[clientID].ai_bit` (and clears an invalid Double bit in a
single battle). Thus a trainer record can carry a mode bit, but the supplied
`SetVsTrainer` constructor gives every ordinary trainer the same base mask.
The apparent Royal `0x127`/effective `0x125` difference is not a contradiction:
the Royal rule branch in `GetClientAIBit` supersedes the stored value when the
AI object is constructed.

This closes the source-level question about special trainers: there is no
ordinary trainer-ID-specific upgrade, while non-Tree modes and phase changes
are explicitly allowed to use different masks. The residual retail stores
identified by the candidate sweep are separately closed by value/type
provenance in [`recovered/proof-boundary-separation.json`](../recovered/proof-boundary-separation.json).

## What each enabled component does

| Component | Judge range | Candidate being scored | Proven engine behavior |
| --- | --- | --- | --- |
| `WAZA_BASIC` | Move scripts | Every usable move/target pair | Runs the basic move-scoring program and adds its returned score. |
| `WAZA_STRONG` | Move scripts | Every usable move/target pair | Runs a separate attack-oriented move-scoring program. |
| `WAZA_EXPERT` | Move scripts | Every usable move/target pair | Runs a separate expert move-scoring program. |
| `POKECHANGE_BASIC` | Switch scripts | Every eligible reserve Pokémon | Decides whether switching is enabled and scores each reserve candidate. |

The move judge starts each candidate at the flat score of 100, rejects illegal
moves/targets, adds each enabled script result, and retains the best move and
target. The switching judge does the analogous per-bench evaluation and then
randomly chooses among equal best candidates. These judges do not execute the
three move scripts as “pick one difficulty”; they accumulate all enabled move
passes.

The item script is a separate capability (`ITEM_BASIC`) and is not part of the
ordinary Battle Tree `0x107` mask. Items are still evaluated in the general
action-selection loop when item use is allowed.

## Tactical information available to the scripts

`tr_ai_cmd.h` declares 124 native AI commands, all dispatched by
`BattleAiCommand::AI_CMD`. The following categories are therefore available
to the retail scripts. Availability of a command does not, by itself, prove
that every script uses it; script-specific use requires decoding or tracing
the AMX body.

### Randomness and coordination

- Random branches use a 0–255 draw.
- A separate common random value is shared during a turn; the source comments
  identify this as a way for Double-battle partners to coordinate.

### Legality, damage, and move quality

- Move learned/usable/PP checks, damage-vs-status classification, base power,
  move sequence number, move kind, and remaining PP.
- Type matchup and exact affinity thresholds, including immunity and
  super-effective checks.
- Simulated damage comparisons, maximum effective power, and whether a move
  can KO the target.
- Ability-based immunity checks, held-item checks, recoil/utility cases, and
  special move conditions such as Protect counters, Fake Out, Last Resort,
  Endeavor, Future Sight, and Z-move-related state.

### Battle state and tempo

- HP thresholds, fainted status, status ailments, Taunt/Encore-like state,
  stat stages, speed-order checks, weather, terrain/field effects, side
  conditions, and the last move/damage received.
- Battle rule and competitor checks, including Multi and Battle Royal context.

### Team and partner awareness

- Bench count and reserve conditions, bench HP/PP loss, whether a reserve can
  deal damage, and whether a reserve has a better matchup.
- Partner-aware power comparison and ally/enemy position checks for Double or
  Multi battles.
- Species/form checks, Mega Evolution state/capability, expanded type/ground
  checks, and the target's known ability state.

### Battle Royal and event-specific state

- Current Battle Royal ranking and per-client KO counts.
- Intrusion/reinforcement and scenario-trainer checks are exposed as separate
  event/mode mechanisms; they are not evidence of a special Battle Tree
  trainer tier.

This command surface shows that the AI can reason about much more than raw
move power: it can compare simulated damage, type effectiveness, status and
field state, reserves, partners, and mode-specific conditions. The weighting
and thresholds live in the AMX programs.

## Retail AMX archive evidence

The analyzed US retail RomFS contains a GARC at `/a/0/8/4` that is consistent
with the `ARCID_BATTLE_AI` archive opened by `AiScript`. It contains 11 valid
Pawn AMX members. Each member has the standard `0xF1E0` AMX magic and Pawn
version bytes `10/10`.

| Member index | Raw payload bytes | AMX declared size |
| ---: | ---: | ---: |
| 0 | 1,024 | 1,022 |
| 1 | 1,220 | 1,220 |
| 2 | 112,696 | 112,693 |
| 3 | 70,036 | 70,034 |
| 4 | 204,568 | 204,567 |
| 5 | 1,164 | 1,162 |
| 6 | 2,052 | 2,050 |
| 7 | 440 | 439 |
| 8 | 3,964 | 3,961 |
| 9 | 8,228 | 8,225 |
| 10 | 5,108 | 5,107 |

The extracted GARC SHA-256 is:

```text
91bcf5119e76ee06ac55d081b14c1951ecfd7c9d59152548c9478750be33c28d
```

The source names nine functional script roles (Basic, Strong, Expert, Double,
Allowance, Royal, Intrude, Item Basic, and Pokechange Basic), while this retail
archive has eleven members. The generated `arc_index/BattleAi.gaix` file that
assigns the symbolic constants to numeric archive members is not present in the
supplied source snapshot. Its numeric map is nevertheless recoverable: the
archived `btl_ai.pprj`/`btl_ai.files` list is name-ordered, `GFArchiver.exe`
and the tracked archiver build rules document/use the `name_up` sort rule, and
the retail AMX members follow that ascending order. The AMX labels identify every member except the copied label
on slot 5; the C++ enum supplies the only remaining functional role
(`intrude`). The resulting exact numeric map is:

| Member | Embedded label | Symbolic role | Status |
| ---: | --- | --- | --- |
| 0 | `allowanceAI` | `btl_ai_allowance_AMX` | Directly identified. |
| 1 | `bandAI` | archive-only `band` | Legacy/archive-only member; not referenced by the supplied C++ enum. |
| 2 | `basicAI` | `btl_ai_basic_AMX` | Directly identified. |
| 3 | `doubleAI` | `btl_ai_double_AMX` | Directly identified. |
| 4 | `expertAI` | `btl_ai_expert_AMX` | Directly identified. |
| 5 | `bandAI` | `btl_ai_intrude_AMX` | Exact lexical slot; embedded debug label is stale/copy-pasted from `band`. |
| 6 | item-number checks | `btl_ai_item_AMX` | Directly identified by item-focused code. |
| 7 | `movingAI` | archive-only `moving` | Legacy/archive-only member; not referenced by the supplied C++ enum. |
| 8 | `pokechangeAI` | `btl_ai_pokechange_AMX` | Directly identified. |
| 9 | `royalAI` | `btl_ai_royal_AMX` | Directly identified. |
| 10 | `strongAI` | `btl_ai_strong_AMX` | Directly identified. |

The `intrude` assignment is no longer an unconstrained inference. Members 1
and 7 already account for the two archive-only legacy names (`band` and
`moving`); every other member is directly labeled, and `intrude` is the only
remaining role named by the C++ `BtlAiScriptNo`/`GetArcDataIndex` switch. Its
slot 5 position is also forced by the ascending-name order between `expert` and
`item`. The copied `bandAI` debug label is therefore a stale script label, not
the archive-index identity. Members 1 and 7 are real, valid AMX programs but
are not reachable through any script number in the supplied `BtlAiScriptNo`
enum.

The retail executable was also extracted from the supplied decrypted US ROM and
matches the `.code` hash used by the IV audit:

```text
b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09
```

The VA base is `0x100000`. That confirms the build identity. The retail binary
is stripped, so it does not contain the generated `BattleAi.gaix` text and the
static inspection did not recover a symbolic `datIdx` trace at the archive-load
call; those are provenance gaps, not unresolved numeric slots. A
debugger/emulator hook at `ArcFileLoadDataBuf` (or an equivalent trace of
`AiScript::GetArcDataIndex`) would be useful corroboration, but is not required
to establish the map above.

## Static AMX audit

The following counts come from the Pawn disassemblies of the 11 extracted
members. “Wrapper calls” are static calls to the shared helper that invokes
`AI_CMD`; “current-move calls” are calls through the helper for
`CMD_GET_CURRENT_WAZANO` (117). The ID sets are exact static command IDs found
at those call sites; argument values that are computed at runtime are covered by
the remaining caveat below.

| Member / role | Wrapper calls | Current-move calls | Unique `AI_CMD` IDs | Score-delta constants observed |
| --- | ---: | ---: | ---: | --- |
| 0 Allowance | 7 | 2 | 5 | −1, +1 |
| 1 archive-only band | 15 | 2 | 5 | −20, −10, +1 |
| 2 Basic | 599 | 12 | 55 | −20, −12, −10, −8, −6, −5, −1 |
| 3 Double | 626 | 45 | 43 | −30, −20, −12, −11, −10, −8, −7, −5, −4, −3, −2, −1, +1, +2, +3, +4, +5, +8, +20 |
| 4 Expert | 1,855 | 144 | 59 | −12, −10, −8, −7, −5, −4, −3, −2, −1, +1, +2, +3, +4 |
| 5 Intrude | 12 | 2 | 5 | −20, −10, +1 |
| 6 Item | 47 | 0 | 6 | −20, +1, +2, +10 |
| 7 archive-only moving | 2 | 2 | 2 | −10, +1 |
| 8 Pokechange | 63 | 1 | 24 | dynamic reserve score; literal +180/+220 random bonuses appear in the code/data |
| 9 Royal | 76 | 3 | 15 | −5, −3, −1, +1, +2, +3, +5, +7 |
| 10 Strong | 55 | 3 | 18 | −3, −1, +2, +3, +4, +5 |

The exact numeric ID sets are:

```text
0  : 0,4,26,55,117
1  : 0,62,67,94,117
2  : 0,4,5,6,8,9,10,11,12,13,14,16,23,24,26,29,30,31,33,34,38,39,40,41,42,43,52,53,54,55,56,57,59,60,62,64,67,71,72,73,74,75,78,79,93,94,100,104,105,106,107,108,109,117,122
3  : 0,1,4,5,6,7,8,9,10,11,16,17,24,26,28,29,30,31,33,34,40,41,42,46,47,48,49,55,62,67,70,71,72,80,81,89,94,96,97,101,102,111,117
4  : 0,4,5,6,8,9,10,11,12,13,16,22,23,24,26,29,30,31,33,34,38,40,41,42,43,47,49,52,53,55,56,57,62,63,64,67,71,72,73,79,80,81,82,83,84,88,93,94,96,97,101,102,105,106,107,109,112,117,119
5  : 0,62,67,94,117
6  : 0,4,10,12,31,118
7  : 67,117
8  : 0,4,11,18,19,20,22,26,29,33,34,35,36,37,84,86,94,110,113,114,115,116,117,123
9  : 0,24,26,28,31,33,34,45,62,71,72,93,94,117,120
10 : 0,24,26,28,33,34,45,57,62,67,71,72,81,93,94,96,97,117
```

The disassembly also gives an exhaustive *opcode* inventory of the control
flow, but not an exhaustive semantic execution. The following counts are
static Pawn opcodes (`jzer`, `jnz`, `jeq`, `jneq`, signed comparisons, and
related conditional jumps; then unconditional `jump`). They are included to
make the remaining symbolic-execution work measurable:

| Member | Conditional jumps | Unconditional jumps |
| ---: | ---: | ---: |
| 0 | 6 | 1 |
| 1 | 21 | 11 |
| 2 | 1,272 | 501 |
| 3 | 1,620 | 301 |
| 4 | 3,200 | 762 |
| 5 | 18 | 13 |
| 6 | 49 | 14 |
| 7 | 4 | 1 |
| 8 | 88 | 19 |
| 9 | 203 | 49 |
| 10 | 148 | 36 |

These counts cover every branch opcode in all eleven extracted programs. They
do not quantify the values flowing through every branch: Pawn locals/stack
temporaries, native-query results, random draws, and computed score arguments
still require a VM-aware symbolic interpreter or a live trace.

### Abstract path-coverage audit

To tighten that boundary, `scripts/audit-battle-ai-flow.py` builds a
may-reachability graph from each disassembly. It follows both outcomes of
every conditional jump, every direct call, every `switch` case-table target,
and (conservatively) every possible target of an indirect Pawn call. Native
returns remain unconstrained. This proves which decoded instructions and
branches are reachable in the abstract control-flow graph; it does not claim
that every native predicate is satisfiable in a real battle state.

Run it against the extracted disassemblies with:

```text
python3 scripts/audit-battle-ai-flow.py /tmp/pawn.KeuKRY
```

The resulting branch coverage is:

| Member | Static conditional/unconditional | May-reachable conditional/unconditional | Unreachable decoded instructions |
| ---: | ---: | ---: | ---: |
| 0 | 6 / 1 | 6 / 1 | 1 (`halt`) |
| 1 | 21 / 11 | 9 / 2 | 168 |
| 2 Basic | 1,272 / 501 | 1,272 / 501 | 1 (`halt`) |
| 3 Double | 1,620 / 301 | 1,618 / 300 | 47 |
| 4 Expert | 3,200 / 762 | 3,200 / 762 | 1 (`halt`) |
| 5 Intrude | 18 / 13 | 9 / 2 | 133 |
| 6 Item | 49 / 14 | 9 / 0 | 539 |
| 7 | 4 / 1 | 4 / 1 | 1 (`halt`) |
| 8 Pokechange | 88 / 19 | 88 / 19 | 1 (`halt`) |
| 9 Royal | 203 / 49 | 203 / 49 | 1 (`halt`) |
| 10 Strong | 148 / 36 | 148 / 36 | 1 (`halt`) |

For Basic and Expert, every decoded branch is in the abstract may-reachable
graph (apart from the file's initial `halt`). Double has three branch opcodes
inside statically decoded but unreachable helper paths; the smaller allowance,
intrude, and item members contain more dead or archive-only helper code. The
audit therefore closes the *control-flow coverage* part of the proof for the
major move programs, while preserving the semantic caveat: an unconstrained
native result can take either branch in the model, and the model does not
derive the concrete score from the live battle state.

### Direct Pawn-VM execution check (execution validation only)

The recovered `amx.c` was compiled with the extracted retail members and the
`AI_CMD` callback interface. With a zero-return callback, members 02 (Basic),
04 (Expert), and 10 (Strong) all return successfully with score zero. The
same smoke run returns normally for all eleven archive members (the small
allowance helper at member 07 returns its documented `+1` zero-callback
adjustment). The
same exact VM then executes the two ROM-derived legal witnesses: member 02
returns `0` against both vectors, member 10 returns `−1` for the Strong vector,
and member 04 returns `−1` for the Expert vector. The member hashes, native
call counts, and callback vectors are preserved in
[`recovered/ai-score-witnesses.json`](../recovered/ai-score-witnesses.json).
This is now a reproducible concrete execution and a legal counterexample to
both score-dominance claims. It still is not a value-complete symbolic
execution: the callback does not enumerate every native-state valuation or
prove that all queried fields are mutually realizable in every legal battle
object graph. The all-`σ` positive score/action theorem therefore remains
unproved even though the two universal dominance claims are disproved.

The IDs resolve through `tr_ai_cmd.h`; for example, Basic and Expert use the
HP/status/type/field/ability/reserve families, Double adds partner and shared
random commands (`96`, `97`, `101`, `102`, `111`), Royal uses ranking command
`120`, and Pokechange uses reserve-specific commands such as `113`, `114`,
`115`, `116`, and `123`. Strong is much smaller and concentrates on power,
type, KO, status, item, speed, and partner-target checks. This is a structural
difference in the retail programs, not proof of a total difficulty ordering.

Literal random thresholds also differ by program. Expert contains a broad set
including 50, 80, 100, 128, 150, 160, 170, 180, 200, 220, 230, 240, and 250;
Double uses shared-random thresholds including 50, 70, 100, 128, 150, 160,
180, 200, 210, 220, 230, and 240; Strong uses 128, 180, and 230; Royal uses
128, 180, 220, and 240; and Pokechange uses 85, 128, 170, 180, 200, 220, and
230. Basic has thresholds computed through intermediate values rather than
appearing as a single literal at every call site.

The score helper is a Pawn routine that adds a signed delta to `p_Score`; the
listed constants are the literal deltas observed in its call sites. Pokechange
uses an additional helper to compute reserve-dependent scores before applying
the delta, and it writes `p_PokeChangeEnable` directly. The C++ judge then adds
the script result to the candidate's running score.

## What the scripts actually prioritize

- **Allowance** is a deliberately shallow move modifier: random and HP gates,
  damage-move and Fake Out checks, then small ±1 adjustments.
- **Basic** is the broad baseline evaluator. It checks move legality, damage,
  type, status, weather, stat stages, field effects, abilities, items, move
  sequences, partner targeting, forms, Mega state, and mode flags. Its many
  small negative deltas are accumulated against the flat candidate score.
- **Strong** is a compact finishing/power evaluator. It emphasizes type,
  damage, KO checks, move power, status, item interactions, speed, partner
  targeting, and a few shared-random branches.
- **Expert** is the largest evaluator. Its disassembly contains the widest
  mix of HP thresholds, status and side effects, ability/item interactions,
  move-sequence tables, stat-stage comparisons, weather/terrain, weight,
  Mega/Z-move state, and many randomized score adjustments.
- **Double** is a partner-aware overlay. It checks ally/enemy targeting,
  partner power comparisons, common-random coordination, speed and damage
  type, field state, and moves that are temporarily hidden or protected.
- **Pokechange** is not a move scorer. It checks the active Pokémon's status,
  item, move lock, weather/field, matchup, reserve damage potential, scenario
  trainer state, and special species/form cases; it enables switching and
  scores each reserve candidate.
- **Royal** uses Battle Royal rank and KO-count state to favor attacks that can
  finish high-ranked opponents, with additional type, damage, item, and
  substitute checks.

This gives a concrete script-level explanation of how the battle AI works. It
also shows why the labels cannot be read as a strict `Basic < Strong < Expert`
ladder: the programs have different command surfaces and different scoring
objectives, and all enabled scripts are accumulated rather than selected as a
single level.

### Why the command surface is not a monotone tier proof

The static command sets make the non-monotonicity concrete. Strong uses five
commands that Basic does not (`28`, `45`, `81`, `96`, `97`):
`CMD_COMP_POWER`, `CMD_IF_WAZA_HINSHI`, `CMD_CHECK_AGI_RANK`, and the two
common-random comparisons. Basic uses 42 commands that Strong does not. Expert
also has 16 commands absent from Basic (`22`, `47`, `49`, `63`, `80`, `81`,
`82`, `83`, `84`, `88`, `96`, `97`, `101`, `102`, `112`, `119`), while Basic
has 12 commands absent from Expert (`14`, `39`, `54`, `59`, `60`, `74`, `75`,
`78`, `100`, `104`, `108`, `122`).

Thus neither `Strong ⊇ Basic` nor `Expert ⊇ Basic` holds even at the native
query surface. This disproves a simple structural “strict superset” reading.
It does not, by itself, prove or disprove a behavioral score ordering, because
command arguments, branch conditions, score deltas, and the live battle state
still determine the final action. Since the ordinary mask enables Basic,
Strong, and Expert together, the engine does not select one of these labels as
a level.

### A behavioral ordering is now a precise theorem

Let `Q(s)` be the set of native command IDs used by script `s`. The structural
relation is `s1 >=struct s0` iff `Q(s0) ⊆ Q(s1)`; the command-set witnesses
above disprove `Strong >=struct Basic` and `Expert >=struct Basic`.

To avoid smuggling a difficulty assumption into the word “capable”, define
`F_s(σ,c,r)` as the score and switch-enable output returned by script `s` for
legal live state `σ`, candidate `c`, and random trace `r`. Score dominance is
the quantified relation:

```text
s1 >=score s0  iff  for every (σ,c,r), F_s1(σ,c,r) >= F_s0(σ,c,r)
```

An action-dominance claim additionally needs a utility function over actions
and the tie/randomness policy used by the judges. The recovered native
dispatcher and Pawn VM first validated execution with synthetic callbacks. The
stronger result is now a legal retail-state counterexample: the ROM's Ninjask
records provide the species, ability, learnable current/stronger moves, AI
sequence numbers, and damage types. With those values instantiated, the exact
members return Basic `0` and Strong `−1`, and a second legal state returns
Basic `0` and Expert `−1` (full vectors are in
[`recovered/ai-score-witnesses.json`](../recovered/ai-score-witnesses.json)).
Therefore both universal score-dominance claims are disproved. The separate
action-dominance question still requires an explicit utility function and the
judge's tie/randomness policy.

## What is proven, and what is not

### Proven by the current evidence

- The Battle Tree trainer path supplies the `0x107` base mask.
- Basic, Strong, and Expert are separate move-scoring script slots; Pokechange
  Basic is a separate switching slot.
- Enabled scripts are iterated and their scores accumulated.
- The scripts execute as Pawn programs and call a native C++ battle-query
  interface.
- Action and candidate ties are randomized.
- No per-special-trainer AI mask branch appears in the ordinary `SetVsTrainer`
  path; the source-level writer inventory identifies the explicit Royal, wild,
  record-fight, intrusion, and reinforcement overrides.
- The retail AMX archive has been fully inventoried and all branch opcodes,
  direct command IDs, and direct score-delta literals have been counted for all
  eleven members.

### Formerly reported as “not yet proven” (superseded)

The bullets below preserve the original scope wording for traceability. Their
current verdicts are in the [proof-closure.md](proof-closure.md) ledger below;
they are not an additional unresolved list.

- A value-complete symbolic execution of every condition/score/threshold
  branch. The retail Pawn VM, host lifecycle, and native `AI_CMD` dispatcher
  sources have now been recovered, and the extracted members execute through
  that VM interface. No all-state symbolic model of native results, object
  aliases, random traces, and host scheduling has been completed, so the
  execution path is validated but no universal score/action theorem is
  claimed.
- That Strong or Expert is monotonically more capable than Basic. The native
  command sets are not nested, and the ROM-derived legal-state witnesses now
  disprove both universal score-dominance relations. A positive all-state
  branch/value theorem remains a separate, stronger analysis goal.
- The original generated `BattleAi.gaix` file bytes and a direct retail
  `datIdx` trace have not been recovered. The numeric map itself is established
  by the archived project/tool ordering plus the retail member inventory above.
- Retail-binary completeness of the mask-writer set. The matching retail
  `.code` section has now been extracted and hash-verified. The three direct
  source-mapped stores are confirmed, and the two formerly unresolved exact
  stores are closed by value/type provenance in the verifier and closure
  artifact. At source scope, the universal claim that every special trainer
  uses one mask is disproved by the explicit Royal, wild, record-fight,
  intrusion, and reinforcement branches listed above.

## Historical proof boundary (superseded)

The earlier report named two possible extensions for an end-to-end retail
result: a Pawn-VM execution with the retail native dispatcher modeled, and a
stripped-binary write-set audit. They remain requirements only for the two
stronger theorems described in [proof-closure.md](proof-closure.md), not for
the already settled Battle-AI claims. Recovering the original `BattleAi.gaix`
bytes or tracing `datIdx` is corroboration of the reconstructed map, not a
remaining numeric-assignment proof obligation.

## Decisive results for the former proof boundary

The complete closure ledger, including the precise verdict for each former
open item and the two stronger theorems that are intentionally out of scope,
is maintained in [proof-closure.md](proof-closure.md).

The four former open items do not all have the same status. The structural and
behavioral ordering claims admit direct counterexamples, one is an
artifact-recovery negative, and the retail source-defined writer theorem is now
closed by the source-complete field-sensitive lift.

### The static audit is not value-complete

This is disproved as a claim about the current audit. The recovered native
dispatcher returns values from live battle state: `CMDFUNC_IF_RND_UNDER`
compares a fresh 0--255 random draw with its argument, `CMDFUNC_IF_HP_UNDER`
reads the active HP ratio, and `CMDFUNC_GET_MAX_WAZA_POWER_INCLUDE_AFFINITY`
computes a state-dependent maximum power. The Pawn host reads
`p_Score`/`p_PokeChangeEnable` only after execution. Therefore two legal live
states can take different branches and produce different scores while having
the same decoded opcode graph. Branch-opcode coverage is proven; a concrete
score/action theorem for every state is not.

### A strict Strong/Expert difficulty ladder is disproved

The native command sets are not nested. Strong uses commands absent from Basic
(`28`, `45`, `81`, `96`, `97`), while Basic uses 42 commands absent from
Strong. Expert and Basic are also mutually non-subsuming. Thus “Strong” or
“Expert” as a strict structural superset of Basic is false. The behavioral score
relation is explicit (`F_s(σ,c,r)` quantified over legal states, candidates,
and random traces), and the two legal-state witnesses disprove both
`F_Strong >=score F_Basic` and `F_Expert >=score F_Basic`. An action relation
additionally requires a utility function and tie policy.

### The original `BattleAi.gaix` bytes are absent from the supplied artifacts

The complete archived Git object database contains zero objects named
`BattleAi.gaix`; the encrypted source archive's visible paths contain zero
such files; and the retail RomFS has no matching `BattleAi`, `btl_ai`, or
`.gaix` path. The retail GARC and the C++ `GetArcDataIndex` switch still force
the numeric map, but the generated source file bytes cannot be recovered from
these inputs. A direct `datIdx` observation would require an emulator or
debugger hook at the archive-load call.

The logically equivalent enum header has been reconstructed at
[`recovered/BattleAi.gaix`](../recovered/BattleAi.gaix). It preserves the
retail member indices and the identifiers consumed by `btl_AiScript.cpp`; it
is an equivalent reconstruction, not a byte-identical recovery of the missing
generated file.

### “One mask for every special trainer/mode” is disproved at source scope

The source contains explicit, mutually different masks: ordinary trainers use
`0x107`; Royal selects `0x125`; Ultra Beast and special wild paths use
`0x007`; ordinary wild Double uses `0x008`; intrusion replaces the mask with
`0x040`; reinforcement replaces it with `0x00f`; and the Battle Festival
helper can deliberately reduce non-boss trainers to Basic only. This falsifies
the universal same-mask claim. The source-defined writer theorem is closed for
all retail aliases and copies: `.code:0x61724` verifies the serialized copy,
`Battle.cro:0x8a25c` verifies the NPC copy, and `Battle.cro:0x8a414` verifies
the player zeroing path. The residual binary stores `.code:0x45ec` and
`Battle.cro:0x1e80` remain disjoint by value/type provenance. The full source,
project, CRO, and relocation checks are in
[`scripts/verify-retail-ai-writer-whole-program.py`](../scripts/verify-retail-ai-writer-whole-program.py)
and recorded in
[`recovered/retail-ai-writer-whole-program.json`](../recovered/retail-ai-writer-whole-program.json).
