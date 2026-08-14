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

## Scope

- Game: Pokémon Ultra Sun, USA retail executable (`CTR-P-A2AA`), analyzed from a decrypted 3DS image.
- Source comparison: the Momiji source snapshot identified in [docs/sources.md](docs/sources.md). The source archive, password, ROM, and extracted binaries are **not** copied into this repository.
- Analysis type: source cross-reference plus ARM32 static disassembly of the retail `.code` section.
- This is documentation of the result, not a redistribution of Nintendo code or of the source archive.

## Trainers covered

The English trainer names are used throughout this repository. The category, constructor path, and IV result are explicit below; no exact name-to-ID mapping is inferred when the executable only exposes the numeric trainer ID.

| English trainer | Category | Constructor/ID class | IVs (HP/Atk/Def/SpA/SpD/Spe) |
| --- | --- | --- | --- |
| Colress | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Grimsley | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Wally | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Cynthia | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Anabel | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Dexio | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Plumeria | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Guzma | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Kiawe | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Kukui | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Mallow | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Sina | Featured Trainer | Normal trainer path; special ID (`90+`) | `31/31/31/31/31/31` |
| Rada | Default Multi Battle partner | Partner constructor; hardcoded `31` | `31/31/31/31/31/31` |
| Lillie | USUM Multi Battle partner | Scouted-partner constructor; hardcoded `31` | `31/31/31/31/31/31` |
| Red | Battle Legend | Special/super-boss ID (`90+`) | `31/31/31/31/31/31` |
| Blue | Battle Legend | Special/super-boss ID (`90+`) | `31/31/31/31/31/31` |

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
