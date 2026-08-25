# USUM Battle Tree Pokémon-build catalogue

The machine-readable catalogue is [data/battle-tree-pokemon-builds.csv](../data/battle-tree-pokemon-builds.csv). It contains every record in the retail Battle Tree Pokémon archive, in archive order:

- records `0–995`: the 996 standard USUM/shared Battle Tree configurations;
- records `996–998`: three Battle Agency tutorial configurations that are present in the retail archive but omitted from the public Battle Tree list.

The public reference layout is the same compact build shape used by the [BW2 PWT rental-build CSV](https://raw.githubusercontent.com/DavidAGInnovation/bw2-pwt-research/main/data/rental-pokemon-builds.csv): tier, species, form, item, four moves, nature, EV spread, and IV context. The tournament column is intentionally omitted. The USUM file adds provenance and constructor fields so that the game rules are not lost in a presentation-oriented table.

## What is authoritative

The set rows come from retail RomFS `/a/2/8/1`, the Battle Tree Pokémon GARC. The source declaration is `BINST_POKEMON_ROM_DATA` in `BattleInstData.h`: species, four move IDs, an EV bit mask, nature ID, item ID, and form number. It has no IV field, ability field, gender field, or friendship field. The source cross-check uses snapshot commit `3f7c94593424a6afddcd9f92a293a3786c9f6425`; the exact source paths and archive hashes are recorded in the provenance JSON.

The generator independently checks all first 996 species IDs and EV masks against the [USUM Battle Tree Pokémon list](https://bulbapedia.bulbagarden.net/wiki/List_of_Battle_Tree_Pok%C3%A9mon). The table supplies English display names and the public build presentation; the retail archive supplies the exact IDs and archive order. The three tutorial records use the retail IDs plus fixed English names for the small set of records not listed on that page.

The trainer references come from RomFS `/a/2/8/2`, the 210-record Battle Tree trainer GARC. When exactly one trainer references a set, Tier shows that decoded trainer name and category, for example `Florian (Youngster)` or `Cynthia (Pokémon Trainer)`. Shared sets show `Multiple trainers` in Tier; the exact trainer IDs, categories, and IV classes remain in the provenance columns.

One retail set record has no reference in the trainer archive; its Tier is explicitly `No trainer reference`.

## Field interpretation

The first columns (`tier` through `friendship`) are the reference-style build fields. The additional columns are:

- `tier`: the decoded trainer name/category when exactly one trainer references the set, otherwise `Multiple trainers`;
- `availability`: standard NPC/Battle Agency availability or tutorial-only availability;
- `trainer_ids`: exact zero-based trainer archive IDs that reference the set;
- `trainer_id_classes`: readable constructor classes for those IDs;
- `ability_slots`: the three English ability names in personal-data slot order;
- `sex_vector`: the Gen VII personal-data sex byte;

The raw EV mask, form number, and National Dex ID are used internally for validation and name/form resolution but are intentionally omitted from the presentation CSV. The exported file keeps the expanded EV columns, readable form, and species name instead.

The presentation values are intentionally compact so GitHub can render the file’s interactive table (GitHub’s CSV renderer supports files up to 512 KB): `31 all` means 31 IVs in every stat, `19/23 all` means the possible opponent IV values in every stat, `Not NPC` marks a tutorial-only record, and `NPC + Agency` / `Agency tutorial` are the availability labels. The full semantics remain documented below and in the provenance columns.

The constructor semantics are:

- **EVs:** the retail builder divides `510` by the number of selected bits and caps each selected stat at `255`. Thus the file intentionally reports `255/255` for a two-stat mask, while the public page commonly displays `252/252`.
- **Opponent IVs:** ordinary Battle Tree construction chooses one value for all six stats from the trainer ID: `0–49 → 19`, `50–69 → 23`, `70–89 → 27`, and `90+ → 31`. IDs `190–205` are featured/Battle Legend records; `206` is the Lillie scouted-partner record; `207–208` are Battle Agency event records; and `209` selects the three tutorial sets. The partner/event constructors use `31` directly.
- **Player/rental IVs:** `31 all` means Battle Agency/rental construction passes `31` for all six stats.
- **Opponent IVs:** compact values such as `19 all`, `19/23 all`, or `31 all` mean the listed value(s) apply to every stat; the values are trainer-ID dependent.
- **Ability:** the set builder selects one of the three personal-data ability slots at random for the ordinary Battle Tree constructor. `ability_slots` shows the English names in slot order, while `ability_rule` groups duplicate names into effective probabilities. For example, `Clear Body / Clear Body / Sturdy` is summarized as `Clear Body (2/3) / Sturdy (1/3)`.
- **Gender:** the builder requests an unspecified sex, so the game derives sex from the species’ personal-data sex vector and generated PID. The CSV reports the exact vector and a readable rule (`Male-only`, `Female-only`, `Genderless`, or the species-ratio rule).
- **Friendship:** the constructor sets `0` for a set containing Frustration and `255` otherwise. The current archive contains no Frustration set, so every row is `255`.
- **Forms:** static form numbers are resolved through the personal-data form table; dynamic icon conventions are labelled explicitly (`School`, `Meteor`, Oricorio forms, Rotom forms, Lycanroc forms, and Alolan forms).

There is no independent weak/strong flag in either the set record or trainer record. Tier is deliberately concise: it names the trainer only when the set has one trainer reference, and otherwise says `Multiple trainers`. `trainer_ids`, `trainer_id_classes`, and `opponent_ivs` retain the complete selection and constructor details.

## Reproduction

The generator is [scripts/generate-battle-tree-pokemon-csv.py](../scripts/generate-battle-tree-pokemon-csv.py). With the external decrypted US retail image and a saved copy of the public table:

```sh
python scripts/generate-battle-tree-pokemon-csv.py \
  --rom "/path/to/Pokemon Ultra Sun (USA) Decrypted.3ds" \
  --pokemon-html /path/to/battle-tree-pokemon.html \
  --trainer-metadata data/battle-tree-trainer-ids.csv
```

The script verifies the expected archive member counts and SHA-256 values, the public species/order/EV cross-check, the personal-data aggregate layout, and deterministic CSV field order. The generated provenance record is [recovered/battle-tree-pokemon-provenance.json](../recovered/battle-tree-pokemon-provenance.json).
