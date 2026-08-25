#!/usr/bin/env python3
"""Generate the USUM Battle Tree Pokémon-set catalogue.

The retail ``battle_tree_poke`` archive is the authoritative source for set
order, species, moves, EV-mask, nature, held item, and form number.  The
Bulbapedia table is used only for the English display names and the public
cross-check of the first 996 records.  The three records after index 995 are
the Battle Agency tutorial records; they are retained instead of silently
discarding them.

The ROM and the page HTML are external inputs.  Nothing proprietary is copied
into the repository.  Either pass ``--rom`` (a decrypted 3DS image) or pass
already extracted GARC files with ``--pokemon-garc`` and ``--trainer-garc``.
The ROM path is normally the most reproducible route for this project.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import struct
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Iterable


POKEMON_TABLE_URL = (
    "https://bulbapedia.bulbagarden.net/wiki/"
    "List_of_Battle_Tree_Pok%C3%A9mon"
)
POKEMON_ROMFS_PATH = "/a/2/8/1"
TRAINER_ROMFS_PATH = "/a/2/8/2"
POKEMON_GARC_SHA256 = "ba5546094bdace0cd3a8bc52040b1e993c3e062c8763e58bf2ce7fce6775af75"
TRAINER_GARC_SHA256 = "56e35c8f448283b17952557c500f6ee4a7e2f5cb37f8f9bcd2a0f8b90a7e90dc"
SOURCE_SNAPSHOT_COMMIT = "3f7c94593424a6afddcd9f92a293a3786c9f6425"
LEGAL_SET_COUNT = 996
ARCHIVE_SET_COUNT = 999

# These records are present in the retail archive but are not in the public
# NPC list: they are used by the Battle Agency tutorial.  Their names are
# stable Gen VII game names, and all other names are decoded from the public
# table in the normal path below.
TUTORIAL_SPECIES = {20: "Raticate", 24: "Arbok", 42: "Golbat"}
TUTORIAL_MOVES = {17: "Wing Attack", 40: "Poison Sting"}
TUTORIAL_ITEMS = {155: "Oran Berry"}

CSV_FIELDS = [
    "tournament",
    "tier",
    "archive_index",
    "species",
    "form",
    "held_item",
    "move_1",
    "move_2",
    "move_3",
    "move_4",
    "nature",
    "ev_distribution",
    "ev_hp",
    "ev_attack",
    "ev_defense",
    "ev_speed",
    "ev_sp_attack",
    "ev_sp_defense",
    "player_ivs",
    "opponent_ivs",
    "ability_rule",
    "gender_rule",
    "friendship",
    # Extra fields retain the information that is not represented by the
    # reference CSV's compact schema.
    "availability",
    "trainer_ids",
    "trainer_id_classes",
    "ability_slots",
    "sex_vector",
    "ev_mask",
    "record_form_no",
    "national_dex",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_garc_members(payload: bytes) -> list[bytes]:
    """Split a standard little-endian GARC into raw members."""
    if payload[:4] != b"CRAG":
        raise ValueError(f"expected GARC CRAG header, got {payload[:4]!r}")
    btaf = payload.find(b"BTAF")
    bmif = payload.find(b"BMIF")
    if btaf < 0 or bmif < 0:
        raise ValueError("GARC is missing BTAF or BMIF")
    count = struct.unpack_from("<I", payload, btaf + 8)[0]
    data_start = bmif + 12
    members: list[bytes] = []
    for index in range(count):
        flags, start, end, declared_size = struct.unpack_from(
            "<IIII", payload, btaf + 12 + index * 16
        )
        if not flags or end < start:
            raise ValueError(f"invalid GARC record {index}")
        member = payload[data_start + start : data_start + end]
        # ``declared_size`` is the embedded file size used by some GARC
        # consumers; the BTAF start/end span is the authoritative member
        # extent (the retail trainer records include a trailing padding span).
        if len(member) != end - start:
            raise ValueError(f"truncated GARC record {index}")
        members.append(member)
    return members


def read_romfs_path(rom: Path, path: str) -> bytes:
    """Read one RomFS file using the existing project ROM opener."""
    extractor = Path(__file__).with_name("extract-retail-battle-ai.py")
    spec = importlib.util.spec_from_file_location("retail_extractor", extractor)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {extractor}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handle, ncch, romfs, exefs = module.open_romfs_and_exefs(rom)
    try:
        return romfs.open(path).read()
    finally:
        romfs.close()
        ncch.close()
        handle.close()


def load_table_html(path: Path | None) -> tuple[bytes, str]:
    if path is None:
        with urllib.request.urlopen(POKEMON_TABLE_URL, timeout=60) as response:
            payload = response.read()
        return payload, POKEMON_TABLE_URL
    payload = path.read_bytes()
    return payload, str(path)


def parse_pokemon_table(payload: bytes) -> list[dict[str, object]]:
    """Parse the sortable Pokémon table and retain USUM rows only."""
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise SystemExit("beautifulsoup4 is required to parse the source table") from exc

    soup = BeautifulSoup(payload, "html.parser")
    tables = [
        table
        for table in soup.find_all("table")
        if "sortable" in (table.get("class") or [])
        and "Pokémon" in table.get_text(" ", strip=True)
    ]
    if len(tables) != 1:
        raise ValueError(f"expected exactly one sortable Pokémon table, found {len(tables)}")

    rows: list[dict[str, object]] = []
    for tr in tables[0].find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) != 15:
            continue
        links = [a.get("href", "") for a in tr.find_all("a")]
        # The page has 17 SM and 17 USUM replacement rows.  Rows without a
        # region superscript are shared by both versions and are retained.
        if any("Pok%C3%A9mon_Sun_and_Moon" in href for href in links):
            continue
        dex = int(clean_text(cells[0].get_text(" ", strip=True)))
        species_link = cells[2].find("a")
        species = clean_text(
            species_link.get_text(" ", strip=True)
            if species_link is not None
            else cells[2].get_text(" ", strip=True)
        )
        image = cells[1].find("img")
        icon = ""
        if image is not None:
            icon = Path(image.get("src", "")).name.rsplit(".", 1)[0]
        values = [clean_text(cell.get_text(" ", strip=True)) for cell in cells]
        rows.append(
            {
                "dex": dex,
                "species": species,
                "icon": icon,
                "item": values[3],
                "moves": values[4:8],
                "nature": values[8],
                # Page order: HP, Atk, Def, SpA, SpD, Speed.
                "evs": values[9:15],
            }
        )
    if len(rows) != LEGAL_SET_COUNT:
        raise ValueError(f"expected {LEGAL_SET_COUNT} USUM rows, found {len(rows)}")
    return rows


def decode_pokemon_record(member: bytes) -> dict[str, int | tuple[int, ...]]:
    if len(member) != 16:
        raise ValueError(f"Battle Tree Pokémon record is {len(member)} bytes, expected 16")
    mons_no, move1, move2, move3, move4, ev_mask, nature, item, form = struct.unpack(
        "<HHHHHBBHH", member
    )
    return {
        "mons_no": mons_no,
        "moves": (move1, move2, move3, move4),
        "ev_mask": ev_mask,
        "nature": nature,
        "item": item,
        "form": form,
    }


def parse_trainer_members(members: list[bytes]) -> dict[int, list[int]]:
    by_set: dict[int, list[int]] = defaultdict(list)
    for trainer_id, member in enumerate(members):
        if len(member) < 4:
            raise ValueError(f"trainer record {trainer_id} is truncated")
        trainer_type, count = struct.unpack_from("<HH", member, 0)
        del trainer_type  # The class label is derived from the archive ID here.
        expected = 4 + count * 2
        if len(member) < expected:
            raise ValueError(f"trainer record {trainer_id} has truncated set table")
        set_ids = struct.unpack_from("<" + "H" * count, member, 4)
        for set_id in set_ids:
            by_set[set_id].append(trainer_id)
    return by_set


def trainer_class_label(trainer_id: int) -> str:
    # These are the exact constructor-ID classes established in this repo's
    # retail audit.  They are not a claim that the set record stores a
    # difficulty field; they describe which trainer classes can select it.
    if trainer_id <= 49:
        return "Trainer IDs 0-49 (19 IV)"
    if trainer_id <= 69:
        return "Trainer IDs 50-69 (23 IV)"
    if trainer_id <= 89:
        return "Trainer IDs 70-89 (27 IV)"
    if trainer_id <= 189:
        return "Trainer IDs 90-189 (31 IV)"
    if trainer_id <= 205:
        return "Battle Legend/featured IDs 190-205 (31 IV)"
    if trainer_id == 206:
        return "Lillie scouted-partner ID 206 (31 IV)"
    if trainer_id <= 208:
        return "Battle Agency event IDs 207-208 (31 IV)"
    return "Battle Agency tutorial ID 209"


def trainer_iv_values(trainer_ids: Iterable[int]) -> list[int]:
    values: set[int] = set()
    for trainer_id in trainer_ids:
        if trainer_id <= 49:
            values.add(19)
        elif trainer_id <= 69:
            values.add(23)
        elif trainer_id <= 89:
            values.add(27)
        else:
            values.add(31)
    return sorted(values)


def form_name(species: int, icon: str, form_no: int) -> str:
    """Convert the retail form number/icon convention to a readable label."""
    # Dynamic forms are represented by a special icon even when the ROM form
    # number remains zero.
    if species == 746 and "Sc" in icon:
        return "School"
    if species == 774:
        return "Meteor"
    if species == 741:
        return {0: "Baile", 1: "Pom-Pom", 2: "Pa'u", 3: "Sensu"}.get(
            form_no, f"Form {form_no}"
        )
    if species == 479:
        return {
            0: "Default",
            1: "Heat",
            2: "Wash",
            3: "Fan",
            4: "Frost",
            5: "Mow",
        }.get(form_no, f"Form {form_no}")
    if species == 745:
        return {0: "Midday", 1: "Midnight"}.get(form_no, f"Form {form_no}")
    if "AMS6" in icon:
        return "Alolan"
    return "Default"


def sex_rule(sex_vector: int) -> str:
    if sex_vector == 0:
        return "Male-only"
    if sex_vector == 254:
        return "Female-only"
    if sex_vector == 255:
        return "Genderless"
    return f"PID-derived species ratio (sex_vector={sex_vector})"


def personal_data(rom: Path, records: list[dict[str, int | tuple[int, ...]]]) -> dict[tuple[int, int], bytes]:
    """Read the aggregate 84-byte Gen VII personal-data member."""
    payload = read_romfs_path(rom, "/a/0/1/7")
    members = parse_garc_members(payload)
    if len(members) != 977 or len(members[-1]) != 976 * 84:
        raise ValueError("unexpected USUM personal-data archive layout")
    aggregate = members[-1]
    result: dict[tuple[int, int], bytes] = {}
    for record in records:
        species = int(record["mons_no"])
        form = int(record["form"])
        data_id = species
        base = aggregate[species * 84 : (species + 1) * 84]
        if form:
            form_index = int.from_bytes(base[0x1C:0x1E], "little")
            form_max = base[0x20]
            if form_index and form < form_max:
                data_id = form_index + form - 1
        result[(species, form)] = aggregate[data_id * 84 : (data_id + 1) * 84]
    return result


def ev_values(mask: int) -> tuple[dict[str, int], str]:
    # The BattleInst constructor uses 510 / selected-stat-count, capped at
    # 255, while the public table conventionally prints 252 for a two-stat
    # spread.  This output keeps the exact game-constructor values.
    names = (
        (0, "HP", "ev_hp"),
        (1, "Attack", "ev_attack"),
        (2, "Defense", "ev_defense"),
        (3, "Speed", "ev_speed"),
        (4, "Sp. Atk", "ev_sp_attack"),
        (5, "Sp. Def", "ev_sp_defense"),
    )
    selected = [entry for entry in names if mask & (1 << entry[0])]
    if not selected:
        raise ValueError(f"empty EV mask 0x{mask:02x}")
    value = min(255, 510 // len(selected))
    fields = {entry[2]: (value if entry in selected else 0) for entry in names}
    distribution = " / ".join(f"{value} {entry[1]}" for entry in selected)
    return fields, distribution


def build_rows(
    pokemon_members: list[bytes],
    trainer_by_set: dict[int, list[int]],
    table_rows: list[dict[str, object]],
    personal: dict[tuple[int, int], bytes],
) -> list[dict[str, object]]:
    if len(pokemon_members) != ARCHIVE_SET_COUNT:
        raise ValueError(f"expected {ARCHIVE_SET_COUNT} Pokémon records, found {len(pokemon_members)}")
    decoded = [decode_pokemon_record(member) for member in pokemon_members]

    # Build collision-free numeric-to-English maps from the 996 rows.  The
    # species/dex order is independently checked below; these maps let the
    # three tutorial rows use the same display format without external name
    # tables.
    move_names: dict[int, str] = {}
    item_names: dict[int, str] = {}
    nature_names: dict[int, str] = {}
    species_names: dict[int, str] = {}
    for index, (record, source) in enumerate(zip(decoded[:LEGAL_SET_COUNT], table_rows)):
        if int(record["mons_no"]) != int(source["dex"]):
            raise ValueError(f"species/order mismatch at archive index {index}")
        species_names.setdefault(int(source["dex"]), str(source["species"]))
        for move_id, move_name in zip(record["moves"], source["moves"]):
            old = move_names.setdefault(int(move_id), str(move_name))
            if old != move_name:
                raise ValueError(f"move ID {move_id} has conflicting names")
        for mapping, key, name in (
            (item_names, int(record["item"]), str(source["item"])),
            (nature_names, int(record["nature"]), str(source["nature"])),
        ):
            old = mapping.setdefault(key, name)
            if old != name:
                raise ValueError(f"numeric ID {key} has conflicting names")
        # Only the selected-stat mask matters in the retail constructor; the
        # public page's 252/255 convention is checked for selected positions.
        selected_page = [value != "-" for value in source["evs"]]
        selected_record = [bool(int(record["ev_mask"]) & (1 << bit)) for bit in (0, 1, 2, 4, 5, 3)]
        if selected_page != selected_record:
            raise ValueError(f"EV-mask mismatch at archive index {index}")

    move_names.update(TUTORIAL_MOVES)
    item_names.update(TUTORIAL_ITEMS)
    species_names.update(TUTORIAL_SPECIES)

    output: list[dict[str, object]] = []
    for index, record in enumerate(decoded):
        species_id = int(record["mons_no"])
        if species_id not in species_names:
            raise ValueError(f"no English species name for National Dex {species_id}")
        source = table_rows[index] if index < LEGAL_SET_COUNT else None
        move_labels = [move_names.get(int(move_id), f"Move {move_id}") for move_id in record["moves"]]
        item_label = item_names.get(int(record["item"]), f"Item {record['item']}")
        nature_label = nature_names.get(int(record["nature"]), f"Nature {record['nature']}")
        ev_fields, distribution = ev_values(int(record["ev_mask"]))
        trainer_ids = sorted(trainer_by_set.get(index, []))
        class_labels = sorted({trainer_class_label(trainer_id) for trainer_id in trainer_ids})
        if index >= LEGAL_SET_COUNT:
            availability = "Battle Agency tutorial only"
            tier = "Battle Agency tutorial only"
            opponent_ivs = "Not an NPC trainer set"
        else:
            availability = "Battle Tree NPC / Battle Agency"
            tier = " / ".join(class_labels) if class_labels else "No trainer reference"
            ivs = trainer_iv_values(trainer_ids)
            opponent_ivs = (
                f"{','.join(str(value) for value in ivs)} in every stat (trainer-ID dependent)"
                if ivs
                else "Trainer-dependent"
            )
        personal_record = personal[(species_id, int(record["form"]))]
        sex_vector = personal_record[0x12]
        ability_values = tuple(personal_record[0x18:0x1B])
        friendship = 0 if "Frustration" in move_labels else 255
        row: dict[str, object] = {
            "tournament": "Battle Tree",
            "tier": tier,
            "archive_index": index,
            "species": species_names[species_id],
            "form": form_name(species_id, str(source["icon"]) if source else "", int(record["form"])),
            "held_item": item_label,
            "move_1": move_labels[0],
            "move_2": move_labels[1],
            "move_3": move_labels[2],
            "move_4": move_labels[3],
            "nature": nature_label,
            "ev_distribution": distribution,
            **ev_fields,
            "player_ivs": "31 in every stat (Battle Agency/rental constructor)",
            "opponent_ivs": opponent_ivs,
            "ability_rule": (
                "Random ability index 0/1/2 "
                f"(personal slots {ability_values[0]}/{ability_values[1]}/{ability_values[2]})"
            ),
            "gender_rule": sex_rule(sex_vector),
            "friendship": friendship,
            "availability": availability,
            "trainer_ids": ",".join(str(trainer_id) for trainer_id in trainer_ids),
            "trainer_id_classes": "; ".join(class_labels),
            "ability_slots": "/".join(str(value) for value in ability_values),
            "sex_vector": sex_vector,
            "ev_mask": f"0x{int(record['ev_mask']):02x}",
            "record_form_no": int(record["form"]),
            "national_dex": species_id,
        }
        output.append(row)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, help="decrypted US retail .3ds image")
    parser.add_argument("--pokemon-garc", type=Path, help="extracted battle_tree_poke GARC")
    parser.add_argument("--trainer-garc", type=Path, help="extracted battle_tree_trainer GARC")
    parser.add_argument("--pokemon-html", type=Path, help="saved Bulbapedia Pokémon table HTML")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/battle-tree-pokemon-builds.csv"),
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("recovered/battle-tree-pokemon-provenance.json"),
    )
    args = parser.parse_args()
    if args.rom is None and (args.pokemon_garc is None or args.trainer_garc is None):
        parser.error("pass --rom, or pass both --pokemon-garc and --trainer-garc")

    table_payload, table_source = load_table_html(args.pokemon_html)
    table_rows = parse_pokemon_table(table_payload)

    if args.rom is not None:
        pokemon_payload = read_romfs_path(args.rom, POKEMON_ROMFS_PATH)
        trainer_payload = read_romfs_path(args.rom, TRAINER_ROMFS_PATH)
    else:
        pokemon_payload = args.pokemon_garc.read_bytes()
        trainer_payload = args.trainer_garc.read_bytes()
    pokemon_members = parse_garc_members(pokemon_payload)
    trainer_members = parse_garc_members(trainer_payload)
    if len(pokemon_members) != ARCHIVE_SET_COUNT:
        raise ValueError(f"expected {ARCHIVE_SET_COUNT} Battle Tree Pokémon members")
    if len(trainer_members) != 210:
        raise ValueError(f"expected 210 Battle Tree trainer members")

    records = [decode_pokemon_record(member) for member in pokemon_members]
    if args.rom is None:
        raise ValueError("--rom is required to read the exact personal-data archive")
    personal = personal_data(args.rom, records)
    trainer_by_set = parse_trainer_members(trainer_members)
    rows = build_rows(pokemon_members, trainer_by_set, table_rows, personal)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    provenance = {
        "pokemon_table_source": table_source,
        "pokemon_table_sha256": sha256(table_payload),
        "pokemon_romfs_path": POKEMON_ROMFS_PATH,
        "pokemon_garc_sha256": sha256(pokemon_payload),
        "expected_pokemon_garc_sha256": POKEMON_GARC_SHA256,
        "trainer_romfs_path": TRAINER_ROMFS_PATH,
        "trainer_garc_sha256": sha256(trainer_payload),
        "expected_trainer_garc_sha256": TRAINER_GARC_SHA256,
        "personal_romfs_path": "/a/0/1/7",
        "personal_record_size": 84,
        "personal_species_record_count": 976,
        "source_snapshot_commit": SOURCE_SNAPSHOT_COMMIT,
        "source_definition": "niji_project/prog/Field/FieldStatic/include/BattleInst/BattleInstData.h",
        "source_constructor": "niji_project/prog/Field/FieldStatic/source/BattleInst/BattleInstTool.cpp",
        "legal_set_count": LEGAL_SET_COUNT,
        "archive_set_count": ARCHIVE_SET_COUNT,
        "tutorial_only_indices": [996, 997, 998],
        "csv_rows": len(rows),
        "notes": [
            "The retail set record stores a six-stat EV bit mask, not six EV integers; the CSV expands the constructor result (510/count, capped at 255).",
            "The set record stores no IV field. NPC opponent IVs come from the selecting trainer ID; Battle Agency/rental construction uses 31 in every stat.",
            "The game has no per-set weak/strong flag. tier records the trainer-ID constructor classes that reference each set; overlapping classes are retained.",
            "Ability slots are numeric personal-data IDs because the set record stores an ability index, not an English ability name.",
        ],
    }
    args.provenance.parent.mkdir(parents=True, exist_ok=True)
    args.provenance.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "rows": len(rows), "provenance": str(args.provenance)}, indent=2))


if __name__ == "__main__":
    main()
