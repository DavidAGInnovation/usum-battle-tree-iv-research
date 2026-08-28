#!/usr/bin/env python3
"""Run repository-only consistency checks, with optional retail checks.

The default mode is dependency-light and validates the committed catalogue,
metadata, JSON artifacts, local Markdown links, and the derived score-rule
document.  ``--rom`` additionally extracts the retail inputs to a temporary
directory and runs the two binary proof checks.  ``--source-root`` can be
provided with ``--rom`` to run the source-complete theorem as well.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_json_files() -> None:
    for path in sorted(ROOT.glob("**/*.json")):
        if ".git" in path.parts:
            continue
        json.loads(path.read_text(encoding="utf-8"))


def check_catalogue() -> None:
    csv_path = ROOT / "data/battle-tree-pokemon-builds.csv"
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    expected_fields = [
        "tier", "archive_index", "species", "form", "held_item", "move_1",
        "move_2", "move_3", "move_4", "nature", "ev_distribution", "ev_hp",
        "ev_attack", "ev_defense", "ev_speed", "ev_sp_attack", "ev_sp_defense",
        "player_ivs", "opponent_ivs", "ability_rule", "gender_rule", "friendship",
        "availability", "trainer_ids", "trainer_id_classes", "ability_slots", "sex_vector",
    ]
    if list(rows[0]) != expected_fields or len(rows) != 999:
        raise ValueError("catalogue schema or row count is invalid")
    indices = [int(row["archive_index"]) for row in rows]
    if indices != list(range(999)):
        raise ValueError("catalogue archive indices are not contiguous 0-998")
    for row in rows:
        values = [
            int(row[field])
            for field in ("ev_hp", "ev_attack", "ev_defense", "ev_speed", "ev_sp_attack", "ev_sp_defense")
        ]
        selected = [value for value in values if value]
        if not selected or len(set(selected)) != 1:
            raise ValueError(f"invalid EV row at archive index {row['archive_index']}")
        expected = min(255, 510 // len(selected))
        if selected[0] != expected:
            raise ValueError(f"invalid EV value at archive index {row['archive_index']}")


def check_metadata_hashes() -> None:
    provenance_path = ROOT / "recovered/battle-tree-pokemon-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    for key, path in (
        ("trainer_metadata_sha256", ROOT / "data/battle-tree-trainer-ids.csv"),
        ("ability_metadata_sha256", ROOT / "data/battle-tree-ability-names.json"),
    ):
        if sha256(path) != provenance[key]:
            raise ValueError(f"metadata hash mismatch for {path}")


def check_local_links() -> None:
    link_re = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
    files = [ROOT / "README.md", ROOT / "recovered/README.md", *sorted((ROOT / "docs").glob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in link_re.finditer(text):
            target = match.group(1).split("#", 1)[0].replace("%20", " ")
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                line = text.count("\n", 0, match.start()) + 1
                raise ValueError(f"missing local link at {path}:{line}: {target}")


def check_score_rules() -> None:
    with tempfile.TemporaryDirectory(prefix="usum-score-check-") as directory:
        output = Path(directory) / "battle-ai-score-rules.md"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/generate-battle-ai-score-rules.py"),
                str(ROOT / "docs/battle-ai-full-spec.md"),
                str(output),
            ],
            check=True,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )
        if output.read_bytes() != (ROOT / "docs/battle-ai-score-rules.md").read_bytes():
            raise ValueError("battle-ai-score-rules.md is not reproducible from the full spec")


def run_retail_checks(rom: Path, source_root: Path | None) -> None:
    with tempfile.TemporaryDirectory(prefix="usum-retail-check-") as directory:
        artifact_dir = Path(directory) / "extracted"
        cros_dir = artifact_dir / "cros"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/extract-retail-battle-ai.py"),
                str(rom),
                str(artifact_dir),
                "--cros-output",
                str(cros_dir),
            ],
            check=True,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )
        code = artifact_dir / "code.bin"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/verify-proof-boundary-separation.py"),
                str(code),
                str(cros_dir),
            ],
            check=True,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/verify-retail-mask-layout-disproof.py"),
                str(code),
            ],
            check=True,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )
        if source_root is not None:
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/verify-retail-ai-writer-whole-program.py"),
                    str(code),
                    str(cros_dir),
                    "--source-root",
                    str(source_root),
                ],
                check=True,
                cwd=ROOT,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, help="optional decrypted US retail ROM for binary checks")
    parser.add_argument("--source-root", type=Path, help="optional recovered source tree for the full theorem")
    args = parser.parse_args()
    if args.source_root is not None and args.rom is None:
        parser.error("--source-root requires --rom")
    check_json_files()
    check_catalogue()
    check_metadata_hashes()
    check_local_links()
    check_score_rules()
    if args.rom is not None:
        run_retail_checks(args.rom, args.source_root)
    print("repository verification passed")


if __name__ == "__main__":
    main()
