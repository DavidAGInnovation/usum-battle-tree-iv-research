# Sources and attribution

## Primary analysis inputs

1. Pokémon Ultra Sun (USA) decrypted 3DS image supplied by the researcher. The image is deliberately not included in this repository.
2. Momiji source snapshot supplied by the researcher (`momiji_git_program.zip`, commit `3f7c94593424a6afddcd9f92a293a3786c9f6425`, dated 2017-07-13). The archive and password note are deliberately not included in this repository.

## Public prior art

- [Smogon Battle Tree Discussion and Records, page 83](https://www.smogon.com/forums/threads/battle-tree-discussion-and-records.3587215/page-83) — public discussion of the 19/23/27/31 trainer-ID ranges and the then-unconfirmed special-trainer expectation. The post describes the special-trainer conclusion as an educated guess; this repository supplies the executable trace.
- [Bulbapedia: Battle Tree](https://bulbapedia.bulbagarden.net/wiki/Battle_Tree) — describes special trainers, multi-battle partners, and the all-31-IV behavior reported for scouted partners.
- [WikiDex: Guía de Pokémon Ultrasol y Pokémon Ultraluna / Árbol de Combate](https://www.wikidex.net/wiki/Gu%C3%ADa_de_Pok%C3%A9mon_Ultrasol_y_Pok%C3%A9mon_Ultraluna/%C3%81rbol_de_Combate) — source for the Spanish category and trainer names used in the research scope: Acromo, Aza, Blasco, Cintia, Destra, Dexio, Francine, Guzmán, Kiawe, Kukui, Lulú, Sina, Nuria, Lylia, Rojo, and Azul.

## WikiDex attribution

The WikiDex trainer/category reference is credited to WikiDex contributors and linked above. WikiDex’s [copyright page](https://www.wikidex.net/wiki/WikiDex%3ACopyrights) states that its text is published under Creative Commons Attribution-ShareAlike 3.0; the link to the original article is provided here for attribution. This repository does not reproduce the WikiDex article.

## Related open-source reference implementations

- [pk3DS `Maison7.cs`](https://github.com/kwsch/pk3DS/blob/master/pk3DS.Core/Structures/Gen7/Maison7.cs) — Battle Tree set schema/reference.
- [PKHeX `BattleTree7.cs`](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen7/BattleTree7.cs) — scouted-partner save-block layout/reference.
