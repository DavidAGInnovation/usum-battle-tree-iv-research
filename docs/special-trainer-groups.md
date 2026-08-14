# Special-trainer internal groups

The Battle Tree stores two different kinds of trainer classification:

1. the localized display class resolved from message entry `111` (for example,
   `Pokémon Trainer`, `Captain`, or `Battle Legend`); and
2. the `group` byte in the trainer-type record loaded for the record's
   `tr_type`.

The second field is a functional game-internal grouping. It is not a
retranslation of the character's story biography. In particular, a character
who is a Champion in the story is not necessarily stored in the Champion
group for every battle mode.

## Group codes

The supplied source defines the group enum as follows:

| Group byte | Source enum | Meaning used by the source |
| ---: | --- | --- |
| `0` | `TRTYPE_GRP_NORA` | Normal/non-boss group |
| `1` | `TRTYPE_GRP_RIVAL` | Rival |
| `2` | `TRTYPE_GRP_SUPPORT` | Support |
| `3` | `TRTYPE_GRP_LEADER` | Leader |
| `4` | `TRTYPE_GRP_BIGFOUR` | Elite Four |
| `5` | `TRTYPE_GRP_CHAMPION` | Champion |

`TrainerTypeData::IsBossGroup` treats only `LEADER`, `BIGFOUR`, and
`CHAMPION` as boss groups. The group is therefore a gameplay classification,
not a guarantee about the character's narrative rank.

## Battle Tree records 190–209

The table below decodes the group byte for each requested special, partner, and
event record. The display class is retained separately so that a generic
`Pokémon Trainer` label is not mistaken for the group value.

| Archive ID | English trainer | Display class | Group byte | Internal group | IVs (HP/Atk/Def/SpA/SpD/Spe) |
| ---: | --- | --- | ---: | --- | --- |
| `190` | Red | Battle Legend | `5` | `TRTYPE_GRP_CHAMPION` | `31/31/31/31/31/31` |
| `191` | Blue | Battle Legend | `5` | `TRTYPE_GRP_CHAMPION` | `31/31/31/31/31/31` |
| `192` | Grimsley | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `193` | Anabel | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `194` | Wally | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `195` | Colress | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `196` | Cynthia | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `197` | Plumeria | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `198` | Guzma | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `199` | Kiawe | Captain | `3` | `TRTYPE_GRP_LEADER` | `31/31/31/31/31/31` |
| `200` | Mallow | Captain | `3` | `TRTYPE_GRP_LEADER` | `31/31/31/31/31/31` |
| `201` | Sina | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `202` | Dexio | Pokémon Trainer | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |
| `203` | Red | Battle Legend | `5` | `TRTYPE_GRP_CHAMPION` | `31/31/31/31/31/31` |
| `204` | Blue | Battle Legend | `5` | `TRTYPE_GRP_CHAMPION` | `31/31/31/31/31/31` |
| `205` | Kukui | Pokémon Trainer | `3` | `TRTYPE_GRP_LEADER` | `31/31/31/31/31/31` |
| `206` | Lillie | Pokémon Trainer | `3` | `TRTYPE_GRP_LEADER` | `31/31/31/31/31/31` |
| `207` | Sophocles | Pokémon Trainer | `3` | `TRTYPE_GRP_LEADER` | `31/31/31/31/31/31` |
| `208` | Giovanni | Pokémon Trainer | `3` | `TRTYPE_GRP_LEADER` | `31/31/31/31/31/31` |
| `209` | Grunt | Team Rainbow Rocket | `0` | `TRTYPE_GRP_NORA` | `31/31/31/31/31/31` |

The direct answer for Cynthia is therefore: her Battle Tree `tr_type` record
has group byte `0`, not `TRTYPE_GRP_CHAMPION`. Red and Blue are the records in
this set that use the internal Champion group. Grimsley is not stored in the
internal Elite Four group (`TRTYPE_GRP_BIGFOUR`) in these Battle Tree records.

## Named `TrType` identifiers in the source

The supplied Momiji source also contains character-specific `TrType` names in
`TrainerTypeData::GetMegaItemId`. The switch includes the following comments:

| Source identifier | Character named by the source comment |
| --- | --- |
| `TRTYPE_GIMA` | Grimsley |
| `TRTYPE_LIRA` | Anabel |
| `TRTYPE_MITSURU` | Wally |
| `TRTYPE_AKUROMA` | Colress |
| `TRTYPE_SIRONA` | Cynthia |
| `TRTYPE_RED` | Red |
| `TRTYPE_GREEN` | Blue in the English localization |
| `TRTYPE_DEKUSIO` / `TRTYPE_DEKUSIO2` | Dexio |

These identifiers are a separate identity layer used by source behavior such
as the Mega Evolution item selection. They do not replace the localized display
class, and they do not change the group-byte results above. The generated
current `trtype_def.h` is not part of the supplied source snapshot, so the
source names are recorded here as named identifiers rather than inventing a
new numeric enum mapping for every Battle Tree row.

## Retail/source evidence

- RomFS `/a/2/8/2` is the 210-record `battle_tree_trainer` GARC. Each record
  begins with the little-endian `u16 tr_type` used to select the trainer-type
  record.
- RomFS `/a/1/0/5` contains 223 fixed 20-byte records matching the
  `TRTYPE_DATA` layout in `TrainerTypeData.h`; byte `0x01` is the `group`
  field. The group bytes in the table were read from the record indexed by
  each Battle Tree record's `tr_type`.
- `TrainerTypeName::GetTrainerTypeName` uses `tr_type` as the message-entry
  index for the localized display class, which is why the display class can be
  `Pokémon Trainer` while the trainer-type group is `CHAMPION` or `LEADER`.
- `TrainerTypeData::GetGroup` returns the binary group field, and
  `TrainerTypeData::IsBossGroup` identifies `LEADER`, `BIGFOUR`, and
  `CHAMPION` as boss groups.

The IV column follows the executable constructor trace documented in
[retail-iv-routine.md](retail-iv-routine.md); every ID in this table is in the
normal constructor's `90+` branch, while Lillie and the event records also have
dedicated paths that pass `31` directly.
