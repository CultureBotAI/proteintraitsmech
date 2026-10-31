#!/usr/bin/env python3
"""Seed the bounded 2026-10-28 structural-discovery catalog through native validation.

Dry-run is the default. --apply creates only absent records; byte-identical prior
outputs are a no-op, and changed destinations are refused. This is a maintained
new-record seeder, not an in-place editor. Its ID check includes ignored corpus
files but is not a cross-worker reservation or a global transaction.

Purpose/date/reference: standalone structural discovery, 2026-10-29 UTC;
conversation 01a183c4-7ea5-7943-9580-927303425d81, PTM #1200/#1201 context.
Inputs: data/curation/structural_trait_discovery.yaml and current data/traits.
Outputs: validated PROPOSED records at the exact manifest paths; JSON summary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

import yaml

from record_io import write_record
from validate_strict import validate_one

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/curation/structural_trait_discovery.yaml"
TRAITS = ROOT / "data/traits"


def load_candidates(manifest: Path, root: Path) -> list[tuple[Path, dict, str]]:
    doc = yaml.safe_load(manifest.read_text())
    if not isinstance(doc, dict) or doc.get("version") != 1:
        raise ValueError("Unsupported discovery manifest")
    rows = doc.get("records")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 10:
        raise ValueError("Discovery batch must contain 1..10 records")
    prepared = []
    identifiers, destinations = set(), set()
    for row in rows:
        rec = row["record"]
        relative = Path(row["path"])
        destination = root / relative
        if (relative.is_absolute() or ".." in relative.parts
                or relative.parts[:3] != ("data", "traits", "structure")
                or relative.suffix != ".yaml"
                or destination.resolve() != root.resolve() / relative):
            raise ValueError(f"Unsafe or non-structural destination: {relative}")
        identifier = rec["identifier"]
        if identifier in identifiers or destination in destinations:
            raise ValueError("Duplicate manifest ID or destination")
        identifiers.add(identifier)
        destinations.add(destination)
        if (rec.get("term_kind") != "CLASS" or rec.get("trait_axis") != "STRUCTURE"
                or rec.get("mapping_status") != "PROPOSED"):
            raise ValueError(f"Discovery class/axis/status invariant: {identifier}")
        if rec.get("license") not in ("CC-BY-4.0", "CC0-1.0"):
            raise ValueError(f"Unapproved record redistribution license: {identifier}")
        if rec.get("canonical_examples") or rec.get("qualified_occurrences"):
            raise ValueError("Carrier promotion is outside this new-class seeder")
        if not rec.get("definition_source") or not rec.get("evidence"):
            raise ValueError(f"Missing source evidence: {identifier}")
        methods = rec.get("detection_methods") or []
        if not any(str(m.get("recipe", "")).strip()
                   and not str(m.get("recipe", "")).lstrip().startswith("#") for m in methods):
            raise ValueError(f"Missing record-specific executable detection recipe: {identifier}")
        text = yaml.safe_dump(rec, sort_keys=False, allow_unicode=True, width=100)
        prepared.append((destination, rec, text))
    return prepared


def preflight(prepared: list[tuple[Path, dict, str]], root: Path) -> dict:
    """Validate the whole selected batch and identity collisions before any write."""
    expected = {r["identifier"]: path for path, r, _ in prepared}
    pattern = "|".join(re.escape(identifier) for identifier in expected)
    result = subprocess.run(
        ["rg", "--no-ignore", "--hidden", "--files-with-matches", "--glob", "*.yaml",
         "--glob", "*.yml", "--", pattern, str(root / "data/traits")],
        text=True, capture_output=True, check=False,
    )
    if result.returncode not in (0, 1):
        raise ValueError(f"Corpus identity scan failed: {result.stderr}")
    for name in result.stdout.splitlines():
        path = Path(name)
        record = yaml.safe_load(path.read_text())
        if not isinstance(record, dict):
            raise ValueError(f"Cannot inspect corpus identity: {path}")
        for identifier in {record.get("identifier"), *(record.get("xrefs") or [])}:
            if identifier in expected and path.resolve() != expected[identifier].resolve():
                raise ValueError(f"ID/xref already present in another record: {identifier} ({path})")
    with tempfile.TemporaryDirectory(prefix="ptm-structural-discovery-") as temp:
        for index, (path, _, text) in enumerate(prepared):
            if path.exists() and path.read_text() != text:
                raise ValueError(f"Existing destination differs; refusing replacement: {path}")
            candidate = Path(temp) / f"{index}.yaml"
            candidate.write_text(text)
            errors = validate_one(candidate)
            if errors:
                raise ValueError(f"Strict validation refused {path}: {errors}")
    return {"ignored_corpus_included": True, "identity_hit_files": len(result.stdout.splitlines()),
            "limits": "ID/xref check, not semantic alias review or cross-worker reservation; see retained prewrite discovery review."}


def seed(*, manifest: Path = MANIFEST, root: Path = ROOT, only: str | None = None,
         apply: bool = False) -> dict:
    prepared = load_candidates(manifest, root)
    if only is not None:
        prepared = [row for row in prepared if row[1]["identifier"] == only]
        if not prepared:
            raise ValueError(f"Unknown selected candidate: {only}")
    inspection = preflight(prepared, root)
    rows = []
    for path, rec, text in prepared:
        exists = path.exists()
        if apply and not exists:
            # Native per-record closed validation and atomic replacement. The
            # isolated worktree has one writer; no global exclusivity is claimed.
            write_record(path, text, validate=True)
        rows.append({"identifier": rec["identifier"], "path": str(path.relative_to(root)),
                     "sha256": hashlib.sha256(text.encode()).hexdigest(),
                     "action": "unchanged" if exists else ("created" if apply else "would_create")})
    return {"apply": apply, "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "preflight": inspection, "records": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only", help="Exact identifier for the first complete canary")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = json.dumps(seed(only=args.only, apply=args.apply), indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report)
    print(report, end="")


if __name__ == "__main__":
    main()
