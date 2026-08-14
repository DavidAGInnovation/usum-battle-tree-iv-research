# Sources and attribution

## Primary analysis inputs

1. Pokémon Ultra Sun (USA) decrypted 3DS image used for the retail trace. The image is deliberately not included in this repository.
2. Momiji source snapshot (`momiji_git_program.zip`, commit `3f7c94593424a6afddcd9f92a293a3786c9f6425`, dated 2017-07-13). The archive and password note are deliberately not included in this repository.

## Retail archive evidence

- RomFS `/a/2/8/2` (`battle_tree_trainer`) — 210 zero-based trainer records. Each record supplies `tr_type`, the numeric `trainer::TrType` trainer-class/category code, plus the Pokémon set IDs.
- English message archive `/a/0/3/2`, entry `104` — the 210 English trainer-name strings used to label the records in [docs/trainer-id-table.md](trainer-id-table.md).
- English message archive `/a/0/3/2`, entry `111` — the localized trainer-class/category strings indexed directly by `tr_type` (`TrainerTypeName::GetTrainerTypeName`).
- The archive-level IDs, roster categories, internal class labels, constructor paths, category codes, and six-stat IV results are reproduced in [docs/trainer-id-table.md](trainer-id-table.md) and [data/battle-tree-trainer-ids.csv](../data/battle-tree-trainer-ids.csv).

## Public prior art

- [Smogon Battle Tree Discussion and Records, page 83](https://www.smogon.com/forums/threads/battle-tree-discussion-and-records.3587215/page-83) — public discussion of the 19/23/27/31 trainer-ID ranges and the then-unconfirmed special-trainer expectation. The post describes the special-trainer conclusion as an educated guess; this repository supplies the executable trace.
- [Bulbapedia: Battle Tree](https://bulbapedia.bulbagarden.net/wiki/Battle_Tree) — describes special trainers, multi-battle partners, and the all-31-IV behavior reported for scouted partners.
- [Bulbapedia: List of Battle Tree Trainers](https://bulbapedia.bulbagarden.net/wiki/List_of_Battle_Tree_Trainers) — public roster cross-check; its ordinary trainer numbers are one-based (`001–190`), while the retail archive records are zero-based (`0–189`).
- [WikiDex: Guía de Pokémon Ultrasol y Pokémon Ultraluna / Árbol de Combate](https://www.wikidex.net/wiki/Gu%C3%ADa_de_Pok%C3%A9mon_Ultrasol_y_Pok%C3%A9mon_Ultraluna/%C3%81rbol_de_Combate) — source for the Battle Tree categories and trainer roster documented in the README using English names.

## WikiDex attribution

The WikiDex trainer/category reference is credited to WikiDex contributors and linked above. WikiDex’s [copyright page](https://www.wikidex.net/wiki/WikiDex%3ACopyrights) states that its text is published under Creative Commons Attribution-ShareAlike 3.0; the link to the original article is provided here for attribution. This repository does not reproduce the WikiDex article.

## Related open-source reference implementations

- [pk3DS `Maison7.cs`](https://github.com/kwsch/pk3DS/blob/master/pk3DS.Core/Structures/Gen7/Maison7.cs) — Battle Tree set schema/reference.
- [PKHeX `BattleTree7.cs`](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen7/BattleTree7.cs) — scouted-partner save-block layout/reference.
