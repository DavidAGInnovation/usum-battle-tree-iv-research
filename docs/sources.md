# Sources and attribution

## Primary analysis inputs

1. Pokémon Ultra Sun (USA) decrypted 3DS image used for the retail trace. The image is not included in the repository.
2. Momiji source snapshot (`momiji_git_program.zip`, commit `3f7c94593424a6afddcd9f92a293a3786c9f6425`, dated 2017-07-13). The archive and password note are not included in the repository.

## Retail archive evidence

- RomFS `/a/2/8/2` (`battle_tree_trainer`) — 210 zero-based trainer records. Each record supplies `tr_type`, the numeric `trainer::TrType` trainer-class/category code, plus the Pokémon set IDs. The extracted GARC SHA-256 is `56e35c8f448283b17952557c500f6ee4a7e2f5cb37f8f9bcd2a0f8b90a7e90dc`.
- RomFS `/a/1/0/5` — 223 fixed 20-byte trainer-type records matching the `TRTYPE_DATA` layout. The `group` byte is decoded for the special records in [special-trainer-groups.md](special-trainer-groups.md). The extracted GARC SHA-256 is `05478939a9b901ff072dd854fff999b1574256e8d22f282b75e80ccc260e5bf9`.
- English message archive `/a/0/3/2`, entry `104` — the 210 English trainer-name strings used to label the records in [docs/trainer-id-table.md](trainer-id-table.md).
- English message archive `/a/0/3/2`, entry `111` — the localized trainer-class/category strings indexed directly by `tr_type` (`TrainerTypeName::GetTrainerTypeName`).
- The archive-level IDs, English names, internal class labels, constructor paths, and six-stat IV results are reproduced in [docs/trainer-id-table.md](trainer-id-table.md) and [data/battle-tree-trainer-ids.csv](../data/battle-tree-trainer-ids.csv).

## Source-level battle-state audit

The source snapshot was also used to check the proof boundary after Pokémon
construction:

- `poke_lib/pml/src/pokepara/pml_PokemonParamLocal.h` — the six persistent
  talent/IV fields are packed at `CoreDataBlockB + 0x38`.
- `poke_lib/pml/src/pokepara/pml_PokemonCoreParam.cpp` and
  `pml_PokemonParamAccessor.cpp` — `ChangeTalentPower` and the six
  `SetTalent*` accessors are the canonical IV mutator.
- `niji_project/prog/Battle/source/btl_IntrudeSystem.cpp` — the one
  non-debug Battle call site found for that mutator, used for SOS/intrusion
  bonuses.
- `niji_project/prog/Battle/source/btl_ServerFlow.cpp` and
  `btl_BattleRule.cpp` — the intrusion-system construction and the
  `BTL_COMPETITOR_WILD` eligibility guard.
- `niji_project/prog/Battle/source/battle_SetupParam.cpp` and
  `Field/FieldStatic/source/BattleInst/BattleInst.cpp` — Battle Tree setup uses
  the Battle House trainer path and assigns `BTL_COMPETITOR_INST`.

This is a source-level path-exclusion audit, not a claim that every retail
instruction or compiler-generated alias has been exhaustively classified.

## Battle-AI source and retail archive evidence

The battle-AI note in [battle-ai.md](battle-ai.md) uses the following source
files from the same Momiji snapshot:

- `niji_project/prog/Battle/include/battle_def.h` — script IDs and bit flags.
- `niji_project/prog/Field/FieldStatic/include/BattleInst/BattleInst.h` and
  `.../source/BattleInst/BattleInst.cpp` — the `0x107` Battle Tree base mask
  and Double/Multi addition.
- `niji_project/prog/Battle/source/tr_ai/btl_BattleAi.cpp` — action-selection
  order and cross-action score comparison.
- `niji_project/prog/Battle/source/tr_ai/btl_AiJudge.cpp` — bitmask iteration.
- `niji_project/prog/Battle/source/tr_ai/btl_AiWazaJudge.cpp` and
  `btl_AiPokeChangeJudge.cpp` — move and switching score accumulation.
- `niji_project/prog/Battle/source/tr_ai/btl_AiScript.cpp` — Pawn loading,
  result variables, and symbolic script-to-archive mapping.
- `niji_project/prog/Battle/source/tr_ai/tr_ai_cmd.h` and
  `btl_BattleAiCommand.cpp` — the native tactical query surface.

For the analyzed US retail ROM, RomFS `/a/0/8/4` is the compact GARC candidate
for `ARCID_BATTLE_AI`; it contains eleven valid Pawn AMX members. Its extracted
GARC SHA-256 is `91bcf5119e76ee06ac55d081b14c1951ecfd7c9d59152548c9478750be33c28d`.
The generated `BattleAi.gaix` archive-index file is absent from the source
snapshot, so the note records the member inventory without assigning numeric
member indices to the named scripts as a fully recovered fact. The AMX members
were validated with the bundled Pawn disassembler; embedded debug labels and
lexical member ordering provide the documented direct/inferred assignments, and
the static command-ID/score-delta and branch-opcode audit is explicitly marked
where the archive index is still missing. The extracted retail `.code` also
matches the analyzed build hash `b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09`
at VA base `0x100000`; that build identity check did not recover a symbolic
`datIdx` trace, so it does not replace the missing `BattleAi.gaix`.

## Retail-binary state audit

The retail `.code` write-set audit is reported in the [retail writer
inventory](retail-iv-routine.md#retail-binary-writer-inventory-for-the-analyzed-build).
It resolves the randomized `CoreDataBlockB` accessor, identifies the packed IV
word and six masks/stores, records the separate bit-30/31 flag writes, and
enumerates direct callers of both `ChangeTalentPower` and the whole-core
initializer. The audit uses the same VA base (`0x100000`) and `.code` hash
listed in [reproduction.md](reproduction.md); it is specific to that US retail
build and does not claim to eliminate arbitrary pointer aliases or unmodeled
copies.

## Public prior art

- [Smogon Battle Tree Discussion and Records, page 83](https://www.smogon.com/forums/threads/battle-tree-discussion-and-records.3587215/page-83) — public discussion of the 19/23/27/31 trainer-ID ranges and the then-unconfirmed special-trainer expectation. The post describes the special-trainer conclusion as an educated guess; the retail executable trace provides the code-level confirmation.
- [Bulbapedia: Battle Tree](https://bulbapedia.bulbagarden.net/wiki/Battle_Tree) — describes special trainers, multi-battle partners, and the all-31-IV behavior reported for scouted partners.
- [Bulbapedia: List of Battle Tree Trainers](https://bulbapedia.bulbagarden.net/wiki/List_of_Battle_Tree_Trainers) — public roster cross-check; its ordinary trainer numbers are one-based (`001–190`), while the retail archive records are zero-based (`0–189`).
- [WikiDex: Guía de Pokémon Ultrasol y Pokémon Ultraluna / Árbol de Combate](https://www.wikidex.net/wiki/Gu%C3%ADa_de_Pok%C3%A9mon_Ultrasol_y_Pok%C3%A9mon_Ultraluna/%C3%81rbol_de_Combate) — source for the Battle Tree categories and trainer roster documented in the README using English names.

## WikiDex attribution

The WikiDex trainer/category reference is credited to WikiDex contributors and linked above. WikiDex’s [copyright page](https://www.wikidex.net/wiki/WikiDex%3ACopyrights) states that its text is published under Creative Commons Attribution-ShareAlike 3.0; the original article is linked for attribution and is not reproduced here.

## Related open-source reference implementations

- [pk3DS `Maison7.cs`](https://github.com/kwsch/pk3DS/blob/master/pk3DS.Core/Structures/Gen7/Maison7.cs) — Battle Tree set schema/reference.
- [PKHeX `BattleTree7.cs`](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen7/BattleTree7.cs) — scouted-partner save-block layout/reference.
