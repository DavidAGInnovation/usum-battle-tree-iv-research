# Retail IV-generation routine

## Executive conclusion

The analyzed Pokémon Ultra Sun retail executable contains the following normal trainer-ID selection at virtual address `0x159790` (raw `.code` offset `0x59790`, assuming the static `.code` mapping base `0x100000`):

```asm
uxth    r0, [sp, #0x90]   ; saved incoming trainer ID
cmp     r0, #0x32         ; 50
movlo   r2, #0x13         ; 19
cmp     r0, #0x46         ; 70
movlo   r2, #0x17         ; 23
cmp     r0, #0x5a         ; 90
movlo   r2, #0x1b         ; 27
movhs   r2, #0x1f         ; 31
mov     r1, #0x32         ; level 50
bl      0x15faf4          ; common Pokémon-parameter helper
```

Because `movlo`/`movhs` use the unsigned comparison flags produced by `cmp`, the effective ranges are:

| Trainer ID range | Value loaded into `r2` | Decimal IV value |
| --- | ---: | ---: |
| `0–49` | `0x13` | `19` |
| `50–69` | `0x17` | `23` |
| `70–89` | `0x1b` | `27` |
| `90+` | `0x1f` | `31` |

`r2` is the `pow`/talent-power argument used by the common constructor. The source implementation writes that value into every one of the six `talentPower` entries, not just one stat.

## Complete numeric-ID coverage

This is a complete rule for the normal trainer constructor, rather than a lookup limited to special-trainer records:

| Normal-constructor input | IV value for HP, Attack, Defense, Special Attack, Special Defense, and Speed |
| --- | ---: |
| Unsigned trainer ID `0–49` | `19` |
| Unsigned trainer ID `50–69` | `23` |
| Unsigned trainer ID `70–89` | `27` |
| Unsigned trainer ID `90–65535` | `31` |

The `uxth` instruction makes the comparison domain an unsigned 16-bit trainer ID. There is no upper-bound branch after the `90` comparison, so every value at or above `90` selects `31`. The retail selector emits special/super-boss IDs in the `190–205` range; those IDs therefore fall in the final row automatically. Partner and Lillie/scouted construction routes do not depend on this range lookup: they pass `31` directly. The complete archive-level mapping, including every ID from `0` through `209` and its resolved trainer class, is in the [trainer-ID table](trainer-id-table.md).

## Separate partner and scouted paths

The normal trainer branch is not the only constructor in use:

| Path | Retail virtual address | Raw `.code` offset | Relevant operation | Result |
| --- | ---: | ---: | --- | ---: |
| Generic partner branch in `SetVsPokemon` | `0x1581a8` | `0x581a8` | `mov r2, #0x1f` before the common helper | 31 in all six stats |
| `ScoutLilie` (USUM scouted partner) | `0x157a1c` | `0x57a1c` | `mov r2, #0x1f` before the common helper | 31 in all six stats |
| Common helper call | `0x15faf4` | `0x5faf4` | receives level `50` and `pow` | materializes the Pokémon parameters |

The source-side enum identifies the generic partner mode as `BTL_INST_PARTNER_NO = 2`. `MakeAiPartner` reconstructs a partner from the saved trainer ID, two set IDs, and ability indices; the save record does not contain IV arrays. This explains why the scouted partner must receive IVs during reconstruction rather than by restoring an IV field from the save.

## Special-trainer selection

The retail selector contains the special/super-boss constants at these locations:

| Retail VA | Raw offset | Constant(s) | Meaning in the selector |
| ---: | ---: | --- | --- |
| `0x158778`, `0x158784` | `0x58778`, `0x58784` | `0xbf` (191), `0xbe` (190) | Super 50th-battle boss slots |
| `0x158844`, `0x158854` | `0x58844`, `0x58854` | `0xcb` (203), `0xcc` (204) | Normal 20th-battle boss slots |

The source `SelectSuperBoss` tables identify the 50th-battle slots as IDs `190`/`191`; the normal-course boss selector identifies IDs `203`/`204`. The featured-trainer records occupy IDs `192–202` and `205`. All of these are at or above the `90` cutoff. Therefore a Pokémon created through the normal special-trainer constructor receives `0x1f`/31 as well. The direct partner/scouted branches independently hardcode the same value.

## Retail trainer archive and trainer-class codes

The retail RomFS archive `/a/2/8/2` is the `battle_tree_trainer` GARC. It contains exactly 210 records (IDs `0–209`), each encoded as a `u16 tr_type`, a `u16 use_poke_cnt`, and that many `u16` set IDs. The selection code reads the record and copies `tr_type` into `NPC_SELECT_ITEM.type` (`trainer::TrType`). This is the internal trainer-class/category code used to resolve the class labels in the [complete table](trainer-id-table.md); it is not the Battle Tree trainer ID. The numeric field itself is omitted from that table.

The English retail message archive `/a/0/3/2`, entry `104`, contains the corresponding 210 trainer-name strings. The same archive’s entry `111` contains the localized trainer-class/category string for each `tr_type`; `TrainerTypeName::GetTrainerTypeName` passes the numeric `tr_type` directly as that message index. The table therefore reports decoded retail names and class labels rather than guessing from executable constants. The archive is zero-based: ordinary public roster lists numbered `001–190` correspond to archive IDs `0–189`.

The trainer-type record has another classification field that is not the
localized display class. RomFS `/a/1/0/5` contains the fixed 20-byte records
matching `TrainerTypeData::TRTYPE_DATA`; byte `0x01` is the group value returned
by `TrainerTypeData::GetGroup`. The special-record group mapping, including the
fact that Red and Blue are `TRTYPE_GRP_CHAMPION` while Cynthia is
`TRTYPE_GRP_NORA`, is documented in [special-trainer-groups.md](special-trainer-groups.md).

The final three records (`207` Sophocles, `208` Giovanni, and `209` Grunt) are Battle Agency event trainers. Their event constructor calls the common Pokémon builder with `BattleFesDefine::POWER`, defined as `0x1f`; they are consequently 31-IV records even though they are not part of the ordinary `0–189` roster. Rada is archive ID `80` (27 IVs on the ordinary path), while the separate default-partner constructor hardcodes 31.

This is an executable-level statement about the ID and constructor branches. It does not require assuming that the trainer’s localized name or class label is embedded in the executable code; both are read from the retail message archive. The English-name trainer list, archive IDs, resolved trainer classes, and constructor/ID classes are documented in the [complete trainer-ID table](trainer-id-table.md).

## Source cross-reference

The Momiji source snapshot agrees with the retail instructions:

- `Field/FieldStatic/source/BattleInst/BattleInst.cpp`: `GetPowerRndNormal` returns 19/23/27/31 by trainer-ID range; `MakePartnerPokemon` passes `0x1f`; `MakeTrainerPokemon` calls the range function; `ScoutLilie` passes `0x1f`.
- `Field/FieldStatic/source/BattleInst/BattleInstTool.cpp`: `CreatePokemon` copies the selected `pow` into all six `initSpec.talentPower` entries.
- `Field/FieldStatic/include/BattleInst/BattleInstData.h`: Battle Tree set data contains species, four moves, EV flag, nature, item, and form, but no IV field.
- `Field/FieldStatic/source/Script/ScriptFuncSetAppCall.cpp`: trainer selection reads `tr_type` from the archive record and assigns it to `NPC_SELECT_ITEM.type` for display.
- `Trainer/Trainer/source/TrainerTypeName.cpp`: `TrainerTypeName::GetTrainerTypeName` uses `tr_type` as the message index for the localized trainer-class/category string (`GARC_message_trtype_DAT`).
- `Trainer/Trainer/include/TrainerTypeData.h`: the binary trainer-type record separates sex/group/icon/model data from the `TrType` code; the code is a category/class identifier, not a trainer-instance ID.
- `Field/FieldStatic/source/BattleFes/BattleFes.cpp` and `BattleFesDefine.h`: the archive has 210 records; IDs `207–209` are Battle Agency event trainers and `BattleFesDefine::POWER` is `0x1f` (31).
- `Savedata/include/BattleInstSave.h` and `Savedata/source/BattleInstSave.cpp`: the scouted-partner save block stores the trainer ID, two set IDs, and two ability indices, but no IV array.

The source archive is referenced for auditability only and is not redistributed here.

## Proof boundary: construction versus battle-time state

The trace proves a postcondition at the end of each traced constructor, not a
global invariant for the rest of the battle. Let `p(id)` be the value selected
by the normal trainer-ID branches (or the explicit `31` used by the partner,
scouted, and event branches). The proof at the constructor boundary is:

1. The normal branch computes `p(id)` in `r2`; the other traced branches load
   `31` directly.
2. Each branch passes that value to the common Pokémon-parameter helper.
3. `CreatePokemon` copies the helper's `pow` argument into all six
   `initSpec.talentPower` entries.
4. The helper therefore returns a Pokémon whose six IV inputs are all
   `p(id)`.

That conclusion is conditional on reaching the traced helper and is about the
object immediately after construction. It does not imply that every later
operation preserves those fields. In particular, a hypothetical battle-time
function that writes an IV after the helper returns would leave every
constructor instruction and source cross-reference above unchanged while
changing the Pokémon observed in battle. The construction evidence therefore
cannot distinguish that program from one in which no such writer exists.

“No IV mutation was observed” is consequently a statement about the finite
paths that were traced, not an exhaustive proof of non-reachability. To promote
it to an end-to-end immutability result, the analysis would need to identify
the runtime IV-field offsets, enumerate every direct or indirect write (and
copy) to those fields on every path from construction through battle setup and
transformation, and inspect each reachable writer. Dynamic watchpoints over
those fields would be useful corroboration, but observations alone still do
not quantify over untraced paths.

### Source-level reachability check

The Momiji snapshot lets us tighten the result for the Battle Tree without
claiming more than the source supports. The persistent IV representation is
the packed word at `CoreDataBlockB + 0x38`: six five-bit fields
(`talent_hp`, `talent_atk`, `talent_def`, `talent_agi`, `talent_spatk`, and
`talent_spdef`). `CoreParam::ChangeTalentPower` is the canonical mutator; it
selects one of those fields through `Accessor::SetTalent*` and then recalculates
the corresponding derived stat.

An exhaustive search of the source snapshot's `Battle/` subtree finds one
non-debug call site for that mutator:
`IntrudeSystem::ApplyIntrudeCountBonus_TalentPower`. It is reached only after
`SetupAppearPokeParam_ByEncountData` creates an SOS/intrusion Pokémon. The
server constructs `IntrudeSystem` only when `MainModule::CanIntrudeBattle()` is
true, and `BattleRule::CanIntrudeBattle` rejects every competitor that is not
`BTL_COMPETITOR_WILD`.

The Battle Tree `BattleInst::StartBattle` path calls
`BTL_SETUP_BattleHouseTrainer` (or its multi-battle variant); those setup
functions set `bp->competitor = BTL_COMPETITOR_INST`. Thus the intrusion writer
is unreachable on the source-defined Battle Tree setup path, and no other
battle-source call to `ChangeTalentPower` or `SetTalent*` was found. This is a
source-level path-exclusion result, stronger than merely not seeing a write in
a handful of dynamic traces.

### Retail-binary writer inventory for the analyzed build

The same conclusion can be checked against the US retail `.code` rather than
only against source names. The block-position helpers at `0x4ad588`,
`0x4ad608`, `0x4ad68c`, and `0x4ad710` resolve the randomized core-data blocks;
`0x4ad608` is the runtime `CoreDataBlockB` accessor. In that returned block
pointer, the six persistent IV fields occupy the word at `+0x34` (the source
layout's `CoreDataBlockB + 0x38` comment includes the enclosing layout
adjustment). The masks and stores are:

| Field | Mask | Store VA (raw `.code` offset) |
| --- | ---: | ---: |
| HP | `0x0000001f` | `0x3214c4` (`0x2214c4`) |
| Attack | `0x000003e0` | `0x321620` (`0x221620`) |
| Defense | `0x00007c00` | `0x321660` (`0x221660`) |
| Speed | `0x000f8000` | `0x3215e0` (`0x2215e0`) |
| Special Attack | `0x01f00000` | `0x321ab8` (`0x221ab8`) |
| Special Defense | `0x3e000000` | `0x321af8` (`0x221af8`) |

Each is a read-modify-write, so it changes only one five-bit field and
preserves the other five. The adjacent writes at `0x3218f8` and `0x321c50`
modify only bits 30 and 31 of the same word; those are the separate egg/name
flags, not IV fields.

An aligned ARM branch scan of the retail `.code` found the six setters called
in two places: the six-value parameter-materialization sequence at
`0x3209d4–0x320a24`, and the switch body at `0x324d84` that clamps its value to
`0x1f` and dispatches by `PowerID`. The latter is the retail
`CoreParam::ChangeTalentPower`. Its only direct caller is `0x380388` (raw
offset `0x280388`), reached from the intrusion-bonus dispatch; no Battle Tree
setup call reaches that writer in the source-defined competitor path.

The binary also contains a whole-core initializer at `0x320528` that copies
the packed word as part of initialization. Its only three callers are
`0x320c70`, `0x320e28`, and `0x320f00`, all in the adjacent construction/
initialization routines; there is no battle-time caller in the analyzed
executable. This accounts for the statically visible bulk-copy write in
addition to the six field setters.

Consequently, for this exact retail build, the evidence establishes a much
stronger result than finite trace observations: no field-level IV writer, and
no reachable whole-core initializer, is present on the Battle Tree
construction-to-transformation path identified above. The source
`BTL_POKEPARAM::HENSIN_Set` path is consistent with that result: it copies
transient battle state and preserves/restores `m_coreParam`, which contains the
persistent IV-bearing parameter.

This is still a build-specific static write-set result, not a mathematical
proof over arbitrary machine aliases. A raw pointer alias, an unrecognized
bulk copy, or a different regional/update binary would require re-running the
inventory. Dynamic watchpoints over the resolved `CoreDataBlockB + 0x34` word
would be useful corroboration, but no emulator/debugger watchpoint trace is
included here. The defensible claim is therefore “no IV mutation is reachable
on the audited Battle Tree path in this retail build under the stated static
analysis,” rather than absolute immutability of every possible execution.

## Limitations

1. The retail trace was performed on a US USA decrypted image. A different regional revision or update could move addresses or change code, even if the logic remains equivalent.
2. The static mapping used here is the extracted `.code` file with VA base `0x100000`; raw offsets are provided so the result can be checked without the original ROM image.
3. The constructor proof is now supplemented by a retail-binary writer inventory: the resolved packed IV word, six field-level stores, the whole-core initializer, and the `ChangeTalentPower` call graph are enumerated above. This establishes that no IV mutation is reachable on the audited Battle Tree path in this exact build under the stated static-analysis assumptions. It still does not quantify over arbitrary aliases, unrecognized bulk copies, different builds, or executions outside that path; dynamic watchpoints would be corroboration, not a substitute for the static inventory. No such IV mutation was observed in the traced paths.
