# USUM Battle Tree Pokémon-build catalogue

The machine-readable catalogue is [data/battle-tree-pokemon-builds.csv](../data/battle-tree-pokemon-builds.csv). It contains every record in the retail Battle Tree Pokémon archive, in archive order:

- records `0–995`: the 996 standard USUM/shared Battle Tree configurations;
- records `996–998`: three Battle Agency tutorial configurations that are present in the retail archive but omitted from the public Battle Tree list.

The public reference layout is the same compact build shape used by the [BW2 PWT rental-build CSV](https://raw.githubusercontent.com/DavidAGInnovation/bw2-pwt-research/main/data/rental-pokemon-builds.csv): tier, species, form, item, four moves, nature, EV spread, and IV context. The tournament column is intentionally omitted. The USUM file adds provenance and constructor fields so that the game rules are not lost in a presentation-oriented table.

## What is authoritative

The set rows come from retail RomFS `/a/2/8/1`, the Battle Tree Pokémon GARC. The source declaration is `BINST_POKEMON_ROM_DATA` in `BattleInstData.h`: species, four move IDs, an EV bit mask, nature ID, item ID, and form number. It has no IV field, ability field, gender field, or friendship field. The source cross-check uses snapshot commit `3f7c94593424a6afddcd9f92a293a3786c9f6425`; the exact source paths and archive hashes are recorded in the provenance JSON.

The generator independently checks all first 996 species IDs and EV masks against the [USUM Battle Tree Pokémon list](https://bulbapedia.bulbagarden.net/wiki/List_of_Battle_Tree_Pok%C3%A9mon). The table supplies English display names and the public build presentation; the retail archive supplies the exact IDs and archive order. The three tutorial records use the retail IDs plus fixed English names for the small set of records not listed on that page.

The trainer references come from RomFS `/a/2/8/2`, the 210-record Battle Tree trainer GARC. Tier values use the decoded retail trainer name and category, for example `Florian (Youngster)` or `Cynthia (Pokémon Trainer)`. A set can be referenced by multiple trainers, so all `Name (Category)` labels are retained and separated by ` / ` rather than forcing a single difficulty label.

One retail set record has no reference in the trainer archive; its Tier is explicitly `No trainer reference`.

## Field interpretation

The first columns (`tier` through `friendship`) are the reference-style build fields. The additional columns are:

- `tier`: decoded retail trainer name and category for every trainer that references the set;
- `availability`: standard NPC/Battle Agency availability or tutorial-only availability;
- `trainer_ids`: exact zero-based trainer archive IDs that reference the set;
- `trainer_id_classes`: readable constructor classes for those IDs;
- `ability_slots`: the three numeric personal-data ability IDs in slot order;
- `sex_vector`: the Gen VII personal-data sex byte;
- `ev_mask` and `record_form_no`: the raw retail values;
- `national_dex`: the numeric species ID used by the set record.

The constructor semantics are:

- **EVs:** the retail builder divides `510` by the number of selected bits and caps each selected stat at `255`. Thus the file intentionally reports `255/255` for a two-stat mask, while the public page commonly displays `252/252`.
- **Opponent IVs:** ordinary Battle Tree construction chooses one value for all six stats from the trainer ID: `0–49 → 19`, `50–69 → 23`, `70–89 → 27`, and `90+ → 31`. IDs `190–205` are featured/Battle Legend records; `206` is the Lillie scouted-partner record; `207–208` are Battle Agency event records; and `209` selects the three tutorial sets. The partner/event constructors use `31` directly.
- **Player/rental IVs:** Battle Agency/rental construction passes `31` for all six stats.
- **Ability:** the set builder passes a random ability index `0/1/2`; the CSV retains the exact three personal-data ability IDs for the resolved species/form. A species with an unused third slot still retains the retail slot value.
- **Gender:** the builder requests an unspecified sex, so the game derives sex from the species’ personal-data sex vector and generated PID. The CSV reports the exact vector and a readable rule (`Male-only`, `Female-only`, `Genderless`, or the species-ratio rule).
- **Friendship:** the constructor sets `0` for a set containing Frustration and `255` otherwise. The current archive contains no Frustration set, so every row is `255`.
- **Forms:** static form numbers are resolved through the personal-data form table; dynamic icon conventions are labelled explicitly (`School`, `Meteor`, Oricorio forms, Rotom forms, Lycanroc forms, and Alolan forms).

There is no independent weak/strong flag in either the set record or trainer record. The readable `tier` column reports every trainer name/category that can select a set; `trainer_id_classes` and `opponent_ivs` retain the constructor classes and resulting possible IV values. Overlapping trainers are expected and are retained.

## Reproduction

The generator is [scripts/generate-battle-tree-pokemon-csv.py](../scripts/generate-battle-tree-pokemon-csv.py). With the external decrypted US retail image and a saved copy of the public table:

```sh
python scripts/generate-battle-tree-pokemon-csv.py \
  --rom "/path/to/Pokemon Ultra Sun (USA) Decrypted.3ds" \
  --pokemon-html /path/to/battle-tree-pokemon.html \
  --trainer-metadata data/battle-tree-trainer-ids.csv
```

The script verifies the expected archive member counts and SHA-256 values, the public species/order/EV cross-check, the personal-data aggregate layout, and deterministic CSV field order. The generated provenance record is [recovered/battle-tree-pokemon-provenance.json](../recovered/battle-tree-pokemon-provenance.json).
