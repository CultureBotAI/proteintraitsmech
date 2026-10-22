#!/usr/bin/env python3
"""Apply the 10 reviewed NCBI CDD source-definition errata (#1171, Stage 4 F3-F12).

Dry-run by default. Refuses curated, unexpected, qualified-occurrence or
partially repaired records; preflights the full target set before writing any
file; preserves all non-target text and writes through the atomic closed-schema
gate. `seed_cdd.py` consumes the same errata module so regeneration cannot
revive the upstream source errors.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdd_errata as errata  # noqa: E402
from record_io import (  # noqa: E402
    RecordValidationError,
    append_to_section,
    extract_block,
    is_curated,
    replace_block,
    top_level_keys,
    write_validated_record,
)
from yaml_emit import yaml_escape  # noqa: E402

TRAITS_ROOT = Path(__file__).resolve().parent.parent / "data" / "traits"
TARGETS: dict[str, Path] = {
    acc: TRAITS_ROOT / item.rel_path for acc, item in errata.ERRATA.items()
}


def should_enrich(text: str) -> bool:
    return not is_curated(text)


def _has_qualified_examples(data: dict) -> bool:
    summary = data.get("protein_example_summary")
    if isinstance(summary, dict) and summary.get("qualified_occurrence_count", 0) != 0:
        return True
    examples = data.get("canonical_examples") or []
    if not isinstance(examples, list):
        return True
    return any(
        isinstance(ex, dict) and ex.get("qualification_status") == "QUALIFIED"
        for ex in examples
    )


def repair_record_text(text: str) -> str:
    keys = top_level_keys(text)
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate top-level keys")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("record is not a YAML mapping")
    identifier = data.get("identifier")
    if not isinstance(identifier, str) or not identifier.startswith("CDD:"):
        raise ValueError(f"not a CDD record: {identifier!r}")
    acc = identifier.removeprefix("CDD:")
    erratum = errata.ERRATA.get(acc)
    if erratum is None:
        raise ValueError(f"not a reviewed CDD erratum target: {identifier}")
    if (data.get("trait_axis"), data.get("trait_category")) != (
        "SEQUENCE",
        "SEQ_DOMAIN",
    ):
        raise ValueError(f"{identifier}: unexpected trait scope")
    if data.get("label") != erratum.label:
        raise ValueError(f"{identifier}: unexpected label; re-review required")
    if data.get("parent_traits") != [f"CDD:{erratum.parent}"]:
        raise ValueError(f"{identifier}: unexpected parent_traits; re-review required")
    if _has_qualified_examples(data):
        raise ValueError(
            f"{identifier}: qualified protein examples require preimage re-binding (#1172)"
        )
    corrected = errata.correct_description(
        acc, erratum.source_description, erratum.parent
    )
    blocks = errata.metadata_blocks(acc)
    # No-op must verify the provenance too; a partial repair is not success.
    if (
        data.get("definition") == corrected
        and data.get("definition_source") == erratum.definition_source
        and data.get("mapping_status") in {"PROPOSED", "REVIEWED"}
        and all(
            item in (data.get(key) or [])
            for key, block in blocks.items()
            for item in yaml.safe_load(block)[key]
        )
    ):
        return text
    if not should_enrich(text):
        raise ValueError(f"{identifier}: curated target requires explicit re-review")
    if (
        data.get("definition") != erratum.source_description
        or data.get("definition_source") != "NCBI CDD"
    ):
        raise ValueError(
            f"{identifier}: unexpected definition/source; re-review required"
        )
    block = extract_block(text, "definition")
    if block is None:
        raise ValueError(f"{identifier}: missing definition block")
    new_block = block
    for old_phrase, new_phrase in erratum.replacements:
        if new_block.count(old_phrase) != 1:
            raise ValueError(
                f"{identifier}: definition is not text-preservingly repairable"
            )
        new_block = new_block.replace(old_phrase, new_phrase)
    out = replace_block(text, "definition", new_block)
    out = replace_block(
        out,
        "definition_source",
        f"definition_source: {yaml_escape(erratum.definition_source)}\n",
    )
    out = replace_block(out, "mapping_status", "mapping_status: PROPOSED\n")
    for key, payload in blocks.items():
        updated = append_to_section(out, key, payload)
        if updated == out:
            raise ValueError(
                f"{identifier}: cannot append {key} without changing formatting"
            )
        out = updated
    expected = dict(data)
    expected.update(
        definition=corrected,
        definition_source=erratum.definition_source,
        mapping_status="PROPOSED",
    )
    for key, payload in blocks.items():
        expected[key] = (data.get(key) or []) + yaml.safe_load(payload)[key]
    if yaml.safe_load(out) != expected:
        raise ValueError(f"{identifier}: repair changed unexpected fields")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        from validate_strict import validate_one

        planned: list[tuple[str, Path, str, bool]] = []
        for acc, target in TARGETS.items():
            text = target.read_text(encoding="utf-8")
            # The writer validates changed output, but preview and no-op paths
            # never reach it. Reject invalid inputs before claiming success.
            errors = validate_one(target)
            if errors:
                raise RecordValidationError(target, errors)
            out = repair_record_text(text)
            if out == text:
                planned.append((acc, target, out, False))
                continue
            if not should_enrich(text):
                raise ValueError(f"CDD:{acc}: refusing curated target")
            planned.append((acc, target, out, True))

        for acc, target, out, changed in planned:
            if not changed:
                print(f"CDD:{acc}: already corrected; no history appended")
                continue
            if args.apply:
                write_validated_record(target, out)
            print(
                f"CDD:{acc}: {'wrote' if args.apply else 'would write'} "
                f"source-definition erratum ({errata.ERRATA[acc].finding_id})"
            )
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
