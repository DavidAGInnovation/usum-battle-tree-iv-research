#!/usr/bin/env python3
"""Refresh the committed retail AI-mask provenance summary.

The scanner intentionally emits a large raw ledger.  The committed summary
also contains manually reviewed source/type closure metadata, so this tool
preserves that reviewed section while replacing every value derived from the
latest scanner run.  The default input/output paths support an in-place
refresh after running ``audit-retail-ai-mask-writers.py``.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = ROOT / "recovered/retail-ai-mask-provenance.json"


def refresh(template: dict[str, object], audit: dict[str, object]) -> dict[str, object]:
    modules = audit["modules"]
    assert isinstance(modules, list)
    main_modules = [row for row in modules if row.get("module") == ".code"]
    cro_modules = [row for row in modules if row.get("module") != ".code"]
    main_arm = next(row for row in main_modules if row.get("mode") == "arm")
    main_thumb = next(row for row in main_modules if row.get("mode") == "thumb")
    reviewed_ledger = template["field_sensitive_residual_lift"]["candidate_ledger"]
    if reviewed_ledger["candidate_count"] != audit["ai_mask_constant_candidate_count"]:
        raise ValueError(
            "raw audit candidate count does not match the reviewed closure ledger"
        )
    observed_offsets = {
        hex(int(row["offset"]))
        for row in main_arm["hits"]
        if row["ai_mask_constant"]
    }
    expected_offsets = {"0x58260", "0x582d4", "0x59370"}
    if not expected_offsets.issubset(observed_offsets):
        raise ValueError("raw audit is missing one or more canonical source writers")

    result = dict(template)
    inputs = dict(result["inputs"])
    inputs.update(
        {
            "main_code_sha256": main_arm["code_sha256"],
            "main_code_size": main_arm["code_size"],
            "main_code_text_size": main_arm["instruction_size"],
            "cro_count": len(cro_modules),
        }
    )
    result["inputs"] = inputs
    result["candidate_counts"] = audit["candidate_counts"]
    result["provenance_counts"] = audit["provenance_counts"]
    result["store_kind_counts"] = audit["store_kind_counts"]
    result["mask_constant_candidates"] = audit["ai_mask_constant_candidate_count"]
    result["mask_constant_candidates_by_value"] = audit["ai_mask_constant_by_value"]
    result["mask_constant_candidates_by_value_provenance"] = audit[
        "ai_mask_constant_by_provenance"
    ]

    disposition = dict(result["additional_candidate_disposition"])
    disposition["main_thumb_constant_candidates"] = main_thumb[
        "ai_mask_constant_candidates"
    ]
    result["additional_candidate_disposition"] = disposition

    relocation_types = Counter()
    import_and_internal = 0
    for row in cro_modules:
        metadata = row["cro_metadata"]
        import_and_internal += sum(
            metadata["relocation_counts"].get(name, 0)
            for name in ("import", "internal")
        )
        relocation_types.update(metadata["relocation_type_counts"])
    cro_relocations = dict(result["cro_relocations"])
    cro_relocations["import_and_internal"] = import_and_internal
    cro_relocations["type_counts"] = dict(sorted(relocation_types.items()))
    result["cro_relocations"] = cro_relocations
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit",
        type=Path,
        required=True,
        help="raw JSON produced by audit-retail-ai-mask-writers.py",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="reviewed summary to refresh (default: recovered/retail-ai-mask-provenance.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="summary JSON to write (default: recovered/retail-ai-mask-provenance.json)",
    )
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    template = json.loads(args.template.read_text(encoding="utf-8"))
    refreshed = refresh(template, audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(refreshed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
