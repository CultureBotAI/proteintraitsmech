#!/usr/bin/env python3
"""Validate the shipped biophysical pilot as one reproducible publication bundle.

Checks the registry, catalog, selected cohort, manifest, numerical replay, TSV,
map bindings/sidecar and analysis together. No writes or network access. Numeric
replay allows 1e-10 roundoff across Python/libm platforms; identities and metadata
must match exactly, and stored observation content hashes still validate exactly.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

from analyze_biophysical import summarize
from biophysical import PILOT, VERSION, calculate, descriptor_id
from build_biophysical_overlay import build_overlay
from calculate_biophysical import digest, read_protein_selection, summary_tsv
from validate_biophysical import load_catalog, load_registry, read_jsonl, validate_collection

ROOT = Path(__file__).resolve().parents[1]
OPTIONS = {"ph", "window", "moment_window", "angle", "threshold", "start", "end",
           "region_termini", "max_scd_length"}


def equal_with_roundoff(actual, expected):
    if type(expected) is float:
        return type(actual) in (int, float) and math.isfinite(actual) and math.isclose(
            actual, expected, rel_tol=1e-10, abs_tol=1e-10)
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(
            equal_with_roundoff(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            equal_with_roundoff(a, b) for a, b in zip(actual, expected))
    return type(actual) is type(expected) and actual == expected


def check_pilot(root=ROOT, disorder_path=None):
    folder = root / "data/biophysical"
    observations_path = folder / "pilot.observations.jsonl"
    registry_path = root / "data/grounding/protein_registry.jsonl"
    catalog_path = folder / "descriptors.yaml"
    map_path = root / "docs/data/sequence_map.json"
    bindings_path = folder / "pilot.embedding-proteins.jsonl"
    registry, catalog = load_registry(registry_path), load_catalog(catalog_path)
    observations = list(read_jsonl(observations_path))
    errors = validate_collection(observations, registry, catalog)
    if errors:
        return errors
    selected = read_protein_selection(folder / "pilot.proteins.txt")
    if not selected or len(selected) != len(set(selected)) or set(selected) - registry.keys():
        return ["pilot protein selection must be nonempty, unique and resolve in the registry"]
    map_data = json.loads(map_path.read_text())
    map_counts = Counter(point[3] for point in map_data["points"])
    missing_or_repeated = [pid for pid in selected if map_counts[pid] != 1]
    if missing_or_repeated:
        return ["pilot proteins must appear exactly once in the sequence map: " +
                ", ".join(sorted(missing_or_repeated))]
    expected_descriptors = {descriptor_id(code) for code in PILOT}
    if catalog.keys() != expected_descriptors:
        errors.append("pilot catalog must contain exactly the twelve implemented descriptor families")
    expected_pairs = {(pid, did) for pid in selected for did in expected_descriptors}
    pairs = [(o["protein_id"], o["descriptor_id"]) for o in observations]
    if set(pairs) != expected_pairs or len(pairs) != len(expected_pairs):
        return errors + ["pilot requires exactly one observation per selected protein/descriptor"]
    manifest = json.loads(observations_path.with_suffix(".manifest.json").read_text())
    expected_manifest = {
        "calculator_version": VERSION, "registry_sha256": digest(registry_path),
        "catalog_sha256": digest(catalog_path), "observation_file_sha256": digest(observations_path),
        "protein_ids": sorted(selected), "observation_count": len(observations),
        "statuses": dict(Counter(o["status"] for o in observations)),
        "input_disorder_sha256": digest(disorder_path) if disorder_path else None,
        "sequence_license": "CC-BY-4.0; UniProt Consortium", "selection": "explicit protein list",
    }
    if not isinstance(manifest, dict) or manifest.keys() != expected_manifest.keys() | {"options"}:
        return errors + ["pilot manifest has missing or unexpected fields"]
    for name, value in expected_manifest.items():
        if manifest[name] != value:
            errors.append(f"pilot manifest {name} does not match its inputs/observations")
    options = manifest["options"]
    if not isinstance(options, dict) or options.keys() != OPTIONS:
        return errors + ["pilot manifest options do not match the calculator contract"]
    if options["start"] is not None or options["end"] is not None:
        return errors + ["shipped map pilot requires whole-protein calculations"]
    predictions = {}
    for prediction in read_jsonl(disorder_path) if disorder_path else []:
        pid = prediction.get("protein_id")
        if pid not in selected or pid in predictions:
            return errors + ["disorder predictions must be unique and in the selected cohort"]
        predictions[pid] = prediction
    stored = {(o["protein_id"], o["descriptor_id"]): o for o in observations}
    for pid in sorted(selected):
        for expected in calculate(registry[pid], disorder=predictions.get(pid), **options):
            actual = stored[(pid, expected["descriptor_id"])]
            # Stored content IDs are checked exactly by validate_collection. Replayed
            # floats may vary in their last bits across platforms, so do not compare
            # the newly generated ID (a hash of those slightly different floats).
            results = {"value", "components", "profile"}
            actual_metadata = {k: v for k, v in actual.items() if k not in results | {"observation_id"}}
            expected_metadata = {k: v for k, v in expected.items() if k not in results | {"observation_id"}}
            actual_results = {k: v for k, v in actual.items() if k in results}
            expected_results = {k: v for k, v in expected.items() if k in results}
            if actual_metadata != expected_metadata or not equal_with_roundoff(actual_results, expected_results):
                errors.append(f"{pid} / {expected['descriptor_id']}: numerical replay or provenance differs")
    if observations_path.with_suffix(".tsv").read_text() != summary_tsv(observations):
        errors.append("pilot TSV differs from its observations")
    bindings = list(read_jsonl(bindings_path))
    if {r.get("accession") for r in bindings} != set(selected):
        errors.append("pilot embedding bindings must cover exactly the selected cohort")
    expected_overlay = build_overlay(map_data, bindings,
        json.loads((folder / "pilot.embedding-meta.json").read_text()), observations, catalog)
    expected_overlay.update(map_sha256=digest(map_path), observations_sha256=digest(observations_path),
                            embedding_proteins_sha256=digest(bindings_path))
    actual_overlay = json.loads((root / "docs/data/sequence_biophysical.json").read_text())
    if actual_overlay != expected_overlay:
        errors.append("published biophysical overlay is stale or differs from its validated inputs")
    expected_analysis = summarize(observations, registry, catalog)
    expected_analysis["observations_sha256"] = digest(observations_path)
    if not equal_with_roundoff(json.loads((folder / "pilot.analysis.json").read_text()), expected_analysis):
        errors.append("pilot analysis is stale or differs from its observations")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--disorder", type=Path, help="Required when the pilot manifest names disorder inputs")
    args = parser.parse_args(argv)
    try:
        errors = check_pilot(args.root, args.disorder)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
        errors = [f"pilot bundle validation failed: {exc}"]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Biophysical pilot verified: observation schema/semantics, cohort, input hashes, "
          "numerical replay, TSV, map overlay and analysis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
