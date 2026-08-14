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

## Scope

- Game: Pokémon Ultra Sun, USA retail executable (`CTR-P-A2AA`), decrypted 3DS image supplied for this research.
- Source comparison: the Momiji source snapshot supplied separately by the user. The source archive, password, ROM, and extracted binaries are **not** copied into this repository.
- Analysis type: source cross-reference plus ARM32 static disassembly of the retail `.code` section.
- This is documentation of the result, not a redistribution of Nintendo code or of the supplied source archive.

## Trainers covered

The requested WikiDex categories are included in the scope: Acromo, Aza, Blasco, Cintia, Destra, Dexio, Francine, Guzmán, Kiawe, Kukui, Lulú, Sina, Nuria, Lylia, Rojo, and Azul. The result for each is 31 IVs in all six stats; the executable evidence is category/constructor based rather than a claim that every localized name is stored as a literal in the executable.

## Reproduce

Read [docs/reproduction.md](docs/reproduction.md) for the address map, raw offsets, and commands that operate on an externally supplied extracted `.code` file. The repository intentionally keeps large/proprietary artifacts out of Git; `.gitignore` blocks common ROM, executable, and archive extensions.

## Prior art and attribution

The IV ranges and the 31-IV special/scouted-partner expectation were discussed publicly before this executable trace. What this repository adds is executable-level confirmation for the supplied US retail build and the separate partner/scouted construction paths. Sources and required attribution are listed in [docs/sources.md](docs/sources.md).
