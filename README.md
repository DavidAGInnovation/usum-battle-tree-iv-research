# Pokémon Ultra Sun/Ultra Moon Battle Tree IV research

This repository records a static-analysis result for the Battle Tree Pokémon constructor in the US retail executable. It answers the previously open question: which individual-value (IV) value is assigned when Battle Tree Pokémon are created?

## Result

For the normal trainer-construction path, the retail executable selects one IV value from the trainer ID:

| Trainer ID | IV value for each of the six stats |
| --- | ---: |
| `0–49` | `19` |
| `50–69` | `23` |
| `70–89` | `27` |
| `90+` | `31` |

The value is passed to the common Pokémon-construction helper, so it is applied to HP, Attack, Defense, Special Attack, Special Defense, and Speed. The Battle Tree set record itself has no IV field.

The generic Battle Tree partner path and the USUM Lillie/scouted-partner path both pass the constant `0x1f` (`31`) to the same helper. The special-trainer selector uses IDs in the `90+` range (including the special/super-boss slots), so the named featured trainers and champions in the research scope resolve to 31 IVs in all six stats. See the evidence table and caveats in [the detailed report](docs/retail-iv-routine.md).

### Complete numeric-ID coverage

The range table applies to every normal trainer ID passed to `MakeTrainerPokemon`, not only to the named trainers listed below. The executable first narrows the input to an unsigned 16-bit value (`uxth`), then uses no upper-bound check after the `90` comparison. Thus `90+` means every unsigned trainer ID from `90` through `65535`; the game’s special/super-boss IDs (including `190–205`) are a subset of that final row.

The [complete trainer-ID table](docs/trainer-id-table.md) inventories every retail Battle Tree trainer record (`0–209`) with its decoded English name, roster category, internal trainer class, constructor/ID class, and numeric internal category code (`trainer::TrType`). A machine-readable copy is available as [data/battle-tree-trainer-ids.csv](data/battle-tree-trainer-ids.csv). The archive uses zero-based IDs; public ordinary-roster lists numbered `001–190` are one-based. The `tr_type` value indexes the localized trainer-class string table and is separate from the Battle Tree trainer ID.

## Scope

- Game: Pokémon Ultra Sun, USA retail executable (`CTR-P-A2AA`), analyzed from a decrypted 3DS image.
- Source comparison: the Momiji source snapshot identified in [docs/sources.md](docs/sources.md). The source archive, password, ROM, and extracted binaries are **not** copied into this repository.
- Analysis type: source cross-reference plus ARM32 static disassembly of the retail `.code` section.
- This is documentation of the result, not a redistribution of Nintendo code or of the source archive.

## Trainers covered

The English trainer names are used throughout this repository. The table below is a quick summary of the requested named categories; the full archive-level name-to-ID and trainer-class-code mapping is in the [complete trainer-ID table](docs/trainer-id-table.md).

| English trainer | Archive ID(s) | Roster category | Internal trainer class | Constructor/ID class | Internal category code (`tr_type`) | IVs (HP/Atk/Def/SpA/SpD/Spe) |
| --- | --- | --- | --- | --- | ---: | --- |
| Colress | `195` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `169` | `31/31/31/31/31/31` |
| Grimsley | `192` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `167` | `31/31/31/31/31/31` |
| Wally | `194` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `168` | `31/31/31/31/31/31` |
| Cynthia | `196` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `170` | `31/31/31/31/31/31` |
| Anabel | `193` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `171` | `31/31/31/31/31/31` |
| Dexio | `202` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `98` | `31/31/31/31/31/31` |
| Plumeria | `197` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `128` | `31/31/31/31/31/31` |
| Guzma | `198` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `140` | `31/31/31/31/31/31` |
| Kiawe | `199` | Featured Trainer | Captain | Normal trainer path; special ID (`90+`) | `43` | `31/31/31/31/31/31` |
| Kukui | `205` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `188` | `31/31/31/31/31/31` |
| Mallow | `200` | Featured Trainer | Captain | Normal trainer path; special ID (`90+`) | `45` | `31/31/31/31/31/31` |
| Sina | `201` | Featured Trainer | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `166` | `31/31/31/31/31/31` |
| Rada | `80` | Default Multi Battle partner | Pokémon Breeder | Partner constructor; hardcoded `31` | `27` | `31/31/31/31/31/31` |
| Lillie | `206` | USUM Multi Battle partner | Pokémon Trainer | Scouted-partner constructor; hardcoded `31` | `189` | `31/31/31/31/31/31` |
| Red | `190` (super), `203` (normal) | Battle Legend | Battle Legend | Special/super-boss ID (`90+`) | `183` | `31/31/31/31/31/31` |
| Blue | `191` (super), `204` (normal) | Battle Legend | Battle Legend | Special/super-boss ID (`90+`) | `184` | `31/31/31/31/31/31` |

Rada is archive trainer ID `80`, so the ordinary archive record uses the `70–89` row (`27` IVs). The separate default-partner constructor is not that ordinary record: it hardcodes `31`, which is why the partner summary row above reports all 31s. Lillie is archive ID `206` and likewise uses the dedicated scouted-partner constructor.

The range rule itself is:

| Trainer ID | IV value for each of the six stats |
| --- | ---: |
| `0–49` | `19` |
| `50–69` | `23` |
| `70–89` | `27` |
| `90+` | `31` |

## Reproduce

Read [docs/reproduction.md](docs/reproduction.md) for the address map, raw offsets, and commands that operate on an external extracted `.code` file. The repository intentionally keeps large/proprietary artifacts out of Git; `.gitignore` blocks common ROM, executable, and archive extensions.

## Prior art and attribution

The IV ranges and the 31-IV special/scouted-partner expectation were discussed publicly before this executable trace. What this repository adds is executable-level confirmation for the analyzed US retail build and the separate partner/scouted construction paths. Sources and required attribution are listed in [docs/sources.md](docs/sources.md).
