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

The source `SelectSuperBoss` tables use IDs 192–205 (with 190/191 for the 50th-battle slots), and the normal boss selector uses 203/204. All of these are at or above the `90` cutoff. Therefore a Pokémon created through the normal special-trainer constructor receives `0x1f`/31 as well. The direct partner/scouted branches independently hardcode the same value.

This is an executable-level statement about the ID and constructor branches. It does not require assuming that the trainer’s localized display name is embedded in the code. The English-name trainer list and each trainer’s constructor/ID class are documented in the [README table](../README.md#trainers-covered); all entries resolve to 31 IVs in all six stats.

## Source cross-reference

The Momiji source snapshot agrees with the retail instructions:

- `Field/FieldStatic/source/BattleInst/BattleInst.cpp`: `GetPowerRndNormal` returns 19/23/27/31 by trainer-ID range; `MakePartnerPokemon` passes `0x1f`; `MakeTrainerPokemon` calls the range function; `ScoutLilie` passes `0x1f`.
- `Field/FieldStatic/source/BattleInst/BattleInstTool.cpp`: `CreatePokemon` copies the selected `pow` into all six `initSpec.talentPower` entries.
- `Field/FieldStatic/include/BattleInst/BattleInstData.h`: Battle Tree set data contains species, four moves, EV flag, nature, item, and form, but no IV field.
- `Savedata/include/BattleInstSave.h` and `Savedata/source/BattleInstSave.cpp`: the scouted-partner save block stores the trainer ID, two set IDs, and two ability indices, but no IV array.

The source archive is referenced for auditability only and is not redistributed here.

## Limitations

1. The retail trace was performed on a US USA decrypted image. A different regional revision or update could move addresses or change code, even if the logic remains equivalent.
2. The static mapping used here is the extracted `.code` file with VA base `0x100000`; raw offsets are provided so the result can be checked without the original ROM image.
3. The result proves the construction logic. It does not by itself prove that a later battle-time transformation cannot modify a Pokémon after construction; no such IV mutation was observed in the traced paths.
