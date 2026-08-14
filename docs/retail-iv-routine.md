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

## Limitations

1. The retail trace was performed on a US USA decrypted image. A different regional revision or update could move addresses or change code, even if the logic remains equivalent.
2. The static mapping used here is the extracted `.code` file with VA base `0x100000`; raw offsets are provided so the result can be checked without the original ROM image.
3. The result proves the construction logic. It does not by itself prove that a later battle-time transformation cannot modify a Pokémon after construction; no such IV mutation was observed in the traced paths.
