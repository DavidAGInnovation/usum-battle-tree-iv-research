#!/usr/bin/env python3
"""Recover the deleted Battle AI Pawn files from an external Git object store.

This helper writes the source files to a caller-selected directory, normally a
temporary directory outside this repository.  It is intentionally separate
from the derived specification generator so the repository does not need to
contain the original source archive or a checked-out copy of the source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


DEFAULT_COMMIT = "6451021a8219e6726491675aff0189c31a2fcc46"
SOURCE_ROOT = "niji_project/prog/Battle/source/tr_ai_script"
FILES = [
    "btl_ai_common.inc",
    "btl_ai_allowance.p",
    "btl_ai_band.p",
    "btl_ai_basic.p",
    "btl_ai_double.p",
    "btl_ai_expert.p",
    "btl_ai_item.p",
    "btl_ai_moving.p",
    "btl_ai_pokechange.p",
    "btl_ai_strong.p",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("git_dir", type=Path, help="external source repository .git directory")
    parser.add_argument("output", type=Path, help="directory outside this repository to receive source files")
    parser.add_argument("--commit", default=DEFAULT_COMMIT, help="pre-deletion commit containing the scripts")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in FILES:
        path = f"{SOURCE_ROOT}/{name}"
        result = subprocess.run(
            ["git", f"--git-dir={args.git_dir}", "show", f"{args.commit}:{path}"],
            check=True,
            capture_output=True,
        )
        destination = args.output / name
        destination.write_bytes(result.stdout)
        rows.append({
            "file": name,
            "git_path": path,
            "sha256": hashlib.sha256(result.stdout).hexdigest(),
            "bytes": len(result.stdout),
        })

    manifest = {"commit": args.commit, "files": rows}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
