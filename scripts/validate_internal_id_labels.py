#!/usr/bin/env python3
"""Gate corpus-internal causal-node (grounding, label) correspondence.

proteintraitsmech: groundings resolve against records committed in this same
repository, so this check needs no OAK database, network, or gitignored data/raw.
The baseline pins both mismatch count and SHA-256 identity: fixing one label while
breaking another cannot pass merely because the count stayed flat.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
BASELINE = ROOT / "conf" / "internal_id_label_baseline.yaml"
SELF_PREFIX = "proteintraitsmech:"
_IDENT = re.compile(r'^identifier:\s*"?(\S+?)"?\s*$', re.M)
_LABEL = re.compile(r'^label:\s*"?(.+?)"?\s*$', re.M)


def normalize(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def collect(root: Path) -> tuple[list[dict[str, str]], int, int]:
    """Return mismatches, checked-pair count, and committed-record count."""
    labels: dict[str, str] = {}
    candidates: list[tuple[Path, str]] = []
    records = 0
    for path in root.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        records += 1
        identifier, label = _IDENT.search(text), _LABEL.search(text)
        if identifier and label:
            curie = identifier.group(1)
            value = label.group(1)
            if curie in labels and normalize(labels[curie]) != normalize(value):
                raise ValueError(f"duplicate identifier with conflicting labels: {curie}")
            labels[curie] = value
        # Broad prefilter only; the YAML walk below decides whether this is a
        # grounding. This catches plain, single-quoted, double-quoted, and future
        # formatting shapes rather than letting quoting shrink the checked set.
        if SELF_PREFIX in text and "grounding:" in text:
            candidates.append((path, text))

    mismatches: list[dict[str, str]] = []
    checked = 0
    for path, text in candidates:
        try:
            record = yaml.safe_load(text) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"cannot parse candidate {path}: {exc}") from exc
        for graph in record.get("causal_graphs") or []:
            graph_id = str(graph.get("graph_id") or "")
            for node in graph.get("nodes") or []:
                grounding = str(node.get("grounding") or "")
                if not grounding.startswith(SELF_PREFIX):
                    continue
                checked += 1
                actual = str(node.get("label") or "")
                canonical = labels.get(grounding)
                if canonical is not None and normalize(actual) == normalize(canonical):
                    continue
                mismatches.append(
                    {
                        "file": str(path.relative_to(root)),
                        "graph_id": graph_id,
                        "node_id": str(node.get("node_id") or ""),
                        "grounding": grounding,
                        "actual": actual,
                        "canonical": canonical or "<ID NOT FOUND>",
                    }
                )
    mismatches.sort(
        key=lambda row: (
            row["grounding"],
            row["file"],
            row["graph_id"],
            row["node_id"],
            row["actual"],
            row["canonical"],
        )
    )
    return mismatches, checked, records


def fingerprint(rows: list[dict[str, str]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(
            json.dumps(
                row, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode()
        )
        digest.update(b"\n")
    return digest.hexdigest()


def load_baseline(path: Path) -> dict[str, Any]:
    baseline = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(baseline, dict):
        raise ValueError(f"baseline must be a mapping: {path}")
    if baseline.get("version") != 1:
        raise ValueError(f"unsupported baseline version: {baseline.get('version')!r}")
    for key in ("records", "checked_pairs", "mismatches"):
        if not isinstance(baseline.get(key), int):
            raise ValueError(f"baseline requires integer {key}")
    if not baseline.get("sha256"):
        raise ValueError("baseline requires sha256")
    return baseline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=TRAITS)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--show", type=int, default=8)
    args = parser.parse_args(argv)

    rows, checked, records = collect(args.path)
    if records == 0 or checked == 0:
        print(
            f"FAIL: examined {records:,} records and {checked:,} internal pairs; "
            "this cannot certify the corpus."
        )
        return 1

    current_hash = fingerprint(rows)
    baseline = load_baseline(args.baseline)
    print(f"records examined                 : {records:,}")
    print(f"internal grounded+labelled nodes : {checked:,}")
    print(f"mismatches                       : {len(rows):,}")
    print(f"mismatch identity sha256         : {current_hash}")

    for row in rows[: args.show]:
        print(
            f"  {row['grounding']} in {row['file']} [{row['graph_id']}/{row['node_id']}]\n"
            f"    node={row['actual']!r}; record={row['canonical']!r}"
        )

    expected_count = baseline["mismatches"]
    expected_hash = str(baseline["sha256"])
    if (
        records != baseline["records"]
        or checked != baseline["checked_pairs"]
        or len(rows) != expected_count
        or current_hash != expected_hash
    ):
        print(
            "FAIL: internal id-label baseline changed: "
            f"expected records={baseline['records']:,} checked={baseline['checked_pairs']:,} "
            f"mismatches={expected_count:,} sha256={expected_hash}; observed "
            f"records={records:,} checked={checked:,} mismatches={len(rows):,} "
            f"sha256={current_hash}"
        )
        return 1
    print("OK: internal id-label mismatch count and identity match the baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
