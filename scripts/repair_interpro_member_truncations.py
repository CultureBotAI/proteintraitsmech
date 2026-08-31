#!/usr/bin/env python3
"""Diagnose curated InterPro abstracts that member seeders head-truncated.

``seed_interpro_members.py`` historically stored only the first 1,800 characters
of a curated InterPro abstract.  That produced definitions ending mid-word and,
for subtype signatures, could remove the only entry-specific sentences at the
end while retaining a generic family preamble.

This is an exact-match repair, not a re-seed.  A record is eligible only when:

* its definition source names an InterPro abstract for a member signature;
* the current definition is byte-equivalent (after the emitter's whitespace
  folding) to the historical 1,800-character slice of the current release text;
* the matching ``definitions[]`` entry contains the same old text; and
* the record has no curation marker.

This tool's write path is intentionally retired.  Source review established
that every PRINTS 42.0 entry has its own non-empty ``gd;`` description and that
borrowing the integrating InterPro abstract can conflate distinct fingerprints.
Completing that borrowed abstract would preserve the deeper identity error.
The exact-match plan remains useful as a diagnostic, but PRINTS records must be
reseeded from the pinned source-native KDAT model instead.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import is_curated  # noqa: E402
from seed_interpro_members import (  # noqa: E402
    interpro_entries,
    is_curated_abstract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
DEFAULT_PATHS = (
    TRAITS_ROOT / "sequence" / "domain" / "prints",
    TRAITS_ROOT / "sequence" / "family" / "prints",
    TRAITS_ROOT / "sequence" / "ptm_ontology" / "prints",
    TRAITS_ROOT / "sequence" / "repeat" / "prints",
)
OLD_CAP = 1_800

_SOURCE = re.compile(r"^InterPro:(IPR\d+) abstract \([^()]+ [^()]+ is a member signature\)$")


class RepairError(ValueError):
    """An apparent truncation cannot be repaired without changing other content."""


@dataclass(frozen=True)
class PlannedRepair:
    path: Path
    identifier: str
    interpro_id: str
    old_length: int
    new_length: int
    original_sha256: str
    text: str


def _collapse(text: str) -> str:
    """Mirror ``yaml_emit.folded`` exactly."""

    return " ".join((text or "").split())


def _structural_expected(record: dict[str, Any], source: str, full: str) -> dict[str, Any]:
    expected = copy.deepcopy(record)
    expected["definition"] = full
    matches = [
        item
        for item in expected.get("definitions", [])
        if isinstance(item, dict) and item.get("source") == source
    ]
    if len(matches) != 1:
        raise RepairError(f"expected one definitions[] row for {source!r}, found {len(matches)}")
    matches[0]["text"] = full
    return expected


def plan_one(
    path: Path,
    text: str,
    entries: dict[str, dict[str, Any]],
) -> tuple[str, PlannedRepair | None]:
    """Classify one record and, when safe, return its exact repaired bytes."""

    try:
        record = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise RepairError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(record, dict):
        raise RepairError(f"{path}: record is not a YAML mapping")
    identifier = str(record.get("identifier") or "")
    if not identifier.startswith("PRINTS:"):
        return "NOT_PRINTS", None
    source = str(record.get("definition_source") or "")
    source_match = _SOURCE.fullmatch(source)
    if source_match is None:
        return "NOT_MEMBER_ABSTRACT", None
    interpro_id = source_match.group(1)
    entry = entries.get(interpro_id)
    if not is_curated_abstract(entry):
        return "SOURCE_NOT_CURATED_OR_MISSING", None
    assert entry is not None
    full = _collapse(str(entry["abstract"]))
    if len(full) <= OLD_CAP:
        return "SOURCE_WITHIN_OLD_CAP", None
    current = record.get("definition")
    if not isinstance(current, str):
        raise RepairError(f"{path}: definition is not text")
    if current == full:
        return "ALREADY_FULL", None
    if is_curated(text):
        return "PROTECTED_CURATED_RECORD", None
    historical = _collapse(full[:OLD_CAP])
    if current != historical:
        return "PROTECTED_NONMATCHING_DEFINITION", None

    expected = _structural_expected(record, source, full)
    matching_rows = [
        item
        for item in record.get("definitions", [])
        if isinstance(item, dict) and item.get("source") == source
    ]
    if matching_rows[0].get("text") != current:
        raise RepairError(f"{path}: definition and matching definitions[] text disagree")
    if text.count(current) != 2:
        raise RepairError(
            f"{path}: historical definition occurs {text.count(current)} times, expected 2"
        )
    updated = text.replace(current, full)
    try:
        parsed_updated = yaml.safe_load(updated)
    except yaml.YAMLError as exc:
        raise RepairError(f"{path}: repaired YAML does not parse: {exc}") from exc
    if parsed_updated != expected:
        raise RepairError(f"{path}: repair would change fields beyond the paired definitions")
    return (
        "REPAIR",
        PlannedRepair(
            path=path,
            identifier=identifier,
            interpro_id=interpro_id,
            old_length=len(current),
            new_length=len(full),
            original_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            text=updated,
        ),
    )


def _paths(values: Iterable[Path]) -> list[Path]:
    found: set[Path] = set()
    for value in values:
        path = value.resolve()
        try:
            path.relative_to(TRAITS_ROOT.resolve())
        except ValueError as exc:
            raise RepairError(f"input must be under {TRAITS_ROOT}: {value}") from exc
        if path.is_dir():
            found.update(path.rglob("*.yaml"))
        elif path.is_file() and path.suffix == ".yaml":
            found.add(path)
        else:
            raise RepairError(f"input is not a YAML file or directory: {value}")
    return sorted(found)


def run(args: argparse.Namespace) -> int:
    if args.apply:
        print(
            "error: --apply is disabled: PRINTS must be reseeded from its pinned "
            "source-native KDAT description and ordered fingerprint model, not from "
            "a borrowed InterPro abstract; no files written",
            file=sys.stderr,
        )
        return 2
    entries = interpro_entries()
    counts: Counter[str] = Counter()
    repairs: list[PlannedRepair] = []
    errors: list[str] = []
    for path in _paths(args.paths or DEFAULT_PATHS):
        try:
            status, repair = plan_one(path, path.read_text(encoding="utf-8"), entries)
        except (OSError, RepairError) as exc:
            errors.append(str(exc))
            continue
        counts[status] += 1
        if repair is not None:
            repairs.append(repair)

    if errors:
        print(f"error: {len(errors)} unsafe record(s); no files written", file=sys.stderr)
        for error in errors[:20]:
            print(f"  {error}", file=sys.stderr)
        return 2
    if args.limit is not None:
        repairs = repairs[: args.limit]
    print(f"would repair {len(repairs):,} exact historical truncation(s)")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count:,}")
    print(
        "diagnostic dry run: no trait records written; --apply is intentionally disabled"
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="PRINTS YAML files/directories")
    parser.add_argument("--limit", type=int, help="show only the first N planned repairs")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="retired safety switch; always refuses without writing",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        print("error: --limit must be positive", file=sys.stderr)
        return 2
    try:
        return run(args)
    except RepairError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
