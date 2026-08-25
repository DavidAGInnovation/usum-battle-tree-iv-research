# Pokémon Ultra Sun/Ultra Moon Battle Tree IV research

This document records a static-analysis result for the Battle Tree Pokémon constructor in the US retail executable. The analysis determines which individual-value (IV) value is assigned when Battle Tree Pokémon are created.

## Result

For the normal trainer-construction path, the retail executable selects one IV value from the trainer ID:

| Trainer ID | IV value for each of the six stats |
| --- | ---: |
| `0–49` | `19` |
| `50–69` | `23` |
| `70–89` | `27` |
| `90+` | `31` |

The value is passed to the common Pokémon-construction helper, so it is applied to HP, Attack, Defense, Special Attack, Special Defense, and Speed. The Battle Tree set record itself has no IV field.

For the analyzed US retail build, the follow-on binary audit resolves the
packed runtime IV word, enumerates the six direct field writers and the
whole-core initializer, and finds no reachable writer on the audited Battle
Tree construction-to-transformation path. See the [retail writer inventory](docs/retail-iv-routine.md#retail-binary-writer-inventory-for-the-analyzed-build)
for the build-specific scope and remaining alias/copy caveat.

The generic Battle Tree partner path and the USUM Lillie/scouted-partner path both pass the constant `0x1f` (`31`) to the same helper. The special-trainer selector uses IDs in the `90+` range (including the special/super-boss slots), so the featured trainers and champions listed in the trainer table resolve to 31 IVs in all six stats. See the evidence table and the [construction-proof boundary](docs/retail-iv-routine.md#proof-boundary-construction-versus-battle-time-state) in [the detailed report](docs/retail-iv-routine.md).

### Complete numeric-ID coverage

The range table applies to every normal trainer ID passed to `MakeTrainerPokemon`, including every trainer record listed below. The executable first narrows the input to an unsigned 16-bit value (`uxth`), then uses no upper-bound check after the `90` comparison. Thus `90+` means every unsigned trainer ID from `90` through `65535`; the game’s special/super-boss IDs (including `190–205`) are a subset of that final row.

The [complete trainer-ID table](docs/trainer-id-table.md) inventories every retail Battle Tree trainer record (`0–209`) with its decoded English name, internal trainer class, constructor/ID class, and six-stat IV result. A machine-readable copy is available as [data/battle-tree-trainer-ids.csv](data/battle-tree-trainer-ids.csv). The archive uses zero-based IDs; public ordinary-roster lists numbered `001–190` are one-based.

The display class and the lower-level trainer-type group are separate fields.
The group bytes for the special, partner, and event records (`190–209`) are
decoded in [special-trainer-groups.md](docs/special-trainer-groups.md). That
table shows, for example, that Red and Blue use the internal Champion group,
whereas Cynthia's Battle Tree record uses the normal/non-boss group despite
her story role.

## Complete Pokémon-build catalogue

The retail archive-level catalogue is available as [data/battle-tree-pokemon-builds.csv](data/battle-tree-pokemon-builds.csv). It contains all 996 standard Battle Tree configurations plus the three Battle Agency tutorial records, with species/form, item, moves, exact constructor EVs, nature, IV context, ability and gender rules, friendship, and the trainer-ID classes that can select each set. The full field definitions, provenance, and reproduction command are in [docs/battle-tree-pokemon-data.md](docs/battle-tree-pokemon-data.md); the generator is [scripts/generate-battle-tree-pokemon-csv.py](scripts/generate-battle-tree-pokemon-csv.py).

## Scope

- Game: Pokémon Ultra Sun, USA retail executable (`CTR-P-A2AA`), analyzed from a decrypted 3DS image.
- Source comparison: the Momiji source snapshot documented in [docs/sources.md](docs/sources.md). The source archive, password, ROM, and extracted binaries are **not** included here.
- Analysis type: source cross-reference plus ARM32 static disassembly of the retail `.code` section.
- This is documentation of the result, not a redistribution of Nintendo code or of the source archive.

## Special trainers and partners

This section summarizes featured trainers, Battle Tree partners, and Battle Legends. The complete archive-level name-to-ID and trainer-class mapping is in the [complete trainer-ID table](docs/trainer-id-table.md), and the separate internal group field is decoded in [special-trainer-groups.md](docs/special-trainer-groups.md).

| English trainer | Archive ID(s) | Internal trainer class | Constructor/ID class | IVs (HP/Atk/Def/SpA/SpD/Spe) |
| --- | --- | --- | --- | --- |
| Colress | `195` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Grimsley | `192` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Wally | `194` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Cynthia | `196` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Anabel | `193` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Dexio | `202` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Plumeria | `197` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Guzma | `198` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Kiawe | `199` | Captain | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Kukui | `205` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Mallow | `200` | Captain | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Sina | `201` | Pokémon Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Rada | `80` | Pokémon Breeder | Partner constructor; hardcoded `31` | `31/31/31/31/31/31` |
| Lillie | `206` | Pokémon Trainer | Scouted-partner constructor; hardcoded `31` | `31/31/31/31/31/31` |
| Red | `190` (super), `203` (normal) | Battle Legend | Special/super-boss ID (`90+`) | `31/31/31/31/31/31` |
| Blue | `191` (super), `204` (normal) | Battle Legend | Special/super-boss ID (`90+`) | `31/31/31/31/31/31` |

Rada is archive trainer ID `80`, so the ordinary archive record uses the `70–89` row (`27` IVs). The separate default-partner constructor is not that ordinary record: it hardcodes `31`, which is why the partner summary row above reports all 31s. Lillie is archive ID `206` and likewise uses the dedicated scouted-partner constructor.

The range rule itself is:

| Trainer ID | IV value for each of the six stats |
| --- | ---: |
| `0–49` | `19` |
| `50–69` | `23` |
| `70–89` | `27` |
| `90+` | `31` |

## Reproduce

Read [docs/reproduction.md](docs/reproduction.md) for the address map, raw offsets, and commands that operate on an external extracted `.code` file. Large/proprietary artifacts are intentionally kept out of Git; `.gitignore` blocks common ROM, executable, and archive extensions.

The battle-AI architecture and the current retail AMX evidence are documented
in [docs/battle-ai.md](docs/battle-ai.md). That note distinguishes the proven
score-selection engine from the static per-script AMX command and score audit,
and records the exact reconstructed numeric `BattleAi.gaix` map (the original
generated file bytes are not included in the supplied source snapshot).
The final verdict for every former proof-boundary item is in
[docs/proof-closure.md](docs/proof-closure.md); no item is left unclassified.

## Prior art and attribution

The IV ranges and the 31-IV special/scouted-partner expectation were discussed publicly before this executable trace. The analysis provides executable-level confirmation for the analyzed US retail build and the separate partner/scouted construction paths. Sources and required attribution are listed in [docs/sources.md](docs/sources.md).
