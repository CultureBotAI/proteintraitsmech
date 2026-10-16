#!/usr/bin/env python3
"""Apply the reviewed CPX-2267 source erratum to the existing seeded record.

Dry-run by default. Refuses curated, unexpected or partially repaired records;
preserves all non-target text and writes through the atomic closed-schema gate.
The seeder consumes the same erratum, so regeneration cannot revive the error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import complexportal_errata as errata  # noqa: E402
from record_io import (  # noqa: E402
    append_to_section,
    extract_block,
    is_curated,
    replace_block,
    top_level_keys,
    write_validated_record,
)
from yaml_emit import yaml_escape  # noqa: E402

TRAITS_ROOT = Path(__file__).resolve().parent.parent / "data" / "traits"
TARGET = TRAITS_ROOT / (
    "function/interaction_partner/complexportal/"
    "sod1-ccs1-superoxide-dismutase-heterodimer-cpx-2267.yaml"
)
TAIL = " A curated stable macromolecular complex (Complex Portal) with 2 subunits."


def should_enrich(text: str) -> bool:
    return not is_curated(text)


def repair_record_text(text: str) -> str:
    keys = top_level_keys(text)
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate top-level keys")
    data = yaml.safe_load(text)
    if not isinstance(data, dict) or data.get("identifier") != errata.IDENTIFIER:
        raise ValueError("not the CPX-2267 target")
    if (data.get("trait_axis"), data.get("trait_category")) != (
        "FUNCTION", "FUNC_INTERACTION_PARTNER"
    ):
        raise ValueError("unexpected trait scope")
    relations = data.get("trait_relations") or []
    if not isinstance(relations, list) or not all(isinstance(r, dict) for r in relations):
        raise ValueError("unexpected trait relations")
    members = [r.get("object") for r in relations if r.get("predicate") == "biolink:has_part"]
    errata.correct_description(errata.ACCESSION, errata.SOURCE_DESCRIPTION, members, [])
    blocks = errata.metadata_blocks()
    corrected = errata.CORRECTED_DESCRIPTION + TAIL
    # No-op must verify the provenance too; a partial repair is not success.
    if (data.get("definition") == corrected
            and data.get("definition_source") == errata.DEFINITION_SOURCE
            and data.get("mapping_status") in {"PROPOSED", "REVIEWED"}
            and all(item in (data.get(key) or [])
                    for key, block in blocks.items()
                    for item in yaml.safe_load(block)[key])):
        return text
    if not should_enrich(text):
        raise ValueError("curated target requires explicit re-review")
    if (data.get("definition") != errata.SOURCE_DESCRIPTION + TAIL
            or data.get("definition_source") != "Complex Portal"):
        raise ValueError("unexpected definition/source; re-review required")
    block = extract_block(text, "definition")
    old_phrase = "water and hydrogen peroxide"
    if block is None or block.count(old_phrase) != 1:
        raise ValueError("definition is not text-preservingly repairable")
    out = replace_block(text, "definition", block.replace(old_phrase, "oxygen and hydrogen peroxide"))
    out = replace_block(out, "definition_source",
                        f"definition_source: {yaml_escape(errata.DEFINITION_SOURCE)}\n")
    out = replace_block(out, "mapping_status", "mapping_status: PROPOSED\n")
    for key, payload in blocks.items():
        updated = append_to_section(out, key, payload)
        if updated == out:
            raise ValueError(f"cannot append {key} without changing formatting")
        out = updated
    expected = dict(data)
    expected.update(definition=corrected, definition_source=errata.DEFINITION_SOURCE,
                    mapping_status="PROPOSED")
    for key, payload in blocks.items():
        expected[key] = (data.get(key) or []) + yaml.safe_load(payload)[key]
    if yaml.safe_load(out) != expected:
        raise ValueError("repair changed unexpected fields")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        text = TARGET.read_text(encoding="utf-8")
        out = repair_record_text(text)
        if out == text:
            print("CPX-2267: already corrected; no history appended")
            return 0
        if not should_enrich(text):
            raise ValueError("refusing curated target")
        if args.apply:
            write_validated_record(TARGET, out)
        print(f"CPX-2267: {'wrote' if args.apply else 'would write'} reaction-product erratum")
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
