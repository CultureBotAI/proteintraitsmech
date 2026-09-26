#!/usr/bin/env python3
"""Select a bounded, reproducible cohort from exact registry/map/embedding joins.

Existing pilot proteins are retained. Remaining slots are filled round-robin
over release, taxon, length and embedding-axis strata, in SHA-256 order within
each stratum. No inferred sequence, new qualification or embedding is created.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path
import sys

from biophysical import ALPHABET, canonical_json
from calculate_biophysical import atomic_write, digest
from validate_biophysical import load_registry, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
POLICY_KEYS = {"version", "maximum_proteins", "minimum_length", "maximum_length", "seed", "anchors"}
EMBEDDING_KEYS = ("model", "revision", "pooling", "window", "overlap")


def length_bin(length):
    for maximum in (100, 300, 600, 1000, 2000):
        if length <= maximum:
            return f"<={maximum}"
    return ">2000"


def stratum(protein, binding):
    return ("UniProtKB:" + protein["uniprot_release"], protein["taxon_id"],
            length_bin(protein["sequence_length"]), "+".join(sorted(binding.get("axes", {}))) or "unknown")


def summarize_members(ids, registry, bindings):
    counts = defaultdict(Counter)
    for pid in ids:
        values = stratum(registry[pid], bindings[pid])
        for key, value in zip(("sequence_source_release", "taxon", "length", "embedding_axes"), values):
            counts[key][value] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(counts.items())}


def select_cohort(registry, map_data, embedding_rows, policy):
    if (not isinstance(policy, dict) or policy.keys() != POLICY_KEYS
            or type(policy["version"]) is not int or policy["version"] != 1):
        raise ValueError("cohort policy must use the closed version-1 contract")
    for field in ("maximum_proteins", "minimum_length", "maximum_length"):
        if type(policy[field]) is not int or policy[field] < 1:
            raise ValueError(f"cohort {field} must be a positive integer")
    if policy["minimum_length"] > policy["maximum_length"] or policy["maximum_length"] > 5000:
        raise ValueError("cohort lengths must be ordered and respect the 5000-residue SCD budget")
    if not isinstance(policy["seed"], str) or not policy["seed"].strip():
        raise ValueError("cohort seed must be a nonempty string")
    anchors = policy["anchors"]
    if (not isinstance(anchors, list) or any(not isinstance(p, str) for p in anchors)
            or len(set(anchors)) != len(anchors) or len(anchors) > policy["maximum_proteins"]):
        raise ValueError("cohort anchors must be unique IDs within the cohort budget")
    points = [point[3] for point in map_data["points"]]
    if len(set(points)) != len(points):
        raise ValueError("duplicate sequence-map protein")
    bindings = {}
    for row in embedding_rows:
        if row["accession"] in bindings:
            raise ValueError("duplicate embedding protein")
        bindings[row["accession"]] = row
    eligible, excluded = [], defaultdict(list)
    for pid in sorted(points):
        protein, embedded = registry.get(pid), bindings.get(pid)
        if protein is None:
            reason = "no_release_pinned_registry_reference"
        elif protein.get("reviewed") is not True:
            reason = "unreviewed_reference"
        elif embedded is None:
            reason = "missing_embedding_binding"
        elif (embedded.get("sequence_sha256") != protein["sequence_sha256"]
              or embedded.get("length") != protein["sequence_length"]):
            reason = "embedding_sequence_mismatch"
        elif not policy["minimum_length"] <= protein["sequence_length"] <= policy["maximum_length"]:
            reason = "outside_length_budget"
        elif set(protein["sequence"]) - set(ALPHABET):
            reason = "nonstandard_residues_not_masked"
        else:
            eligible.append(pid)
            continue
        excluded[reason].append(pid)
    if set(anchors) - set(eligible):
        raise ValueError("retained pilot proteins are no longer eligible; review the refresh policy explicitly")
    # Keep separate accessions for the same exact sequence visible in the report,
    # while preventing them from inflating exploratory association sample sizes.
    by_sequence = defaultdict(list)
    for pid in eligible:
        by_sequence[registry[pid]["sequence_sha256"]].append(pid)
    representatives, duplicate_groups = [], []
    for group in by_sequence.values():
        retained = sorted(set(group) & set(anchors))
        representative = retained[0] if retained else min(group)
        representatives.append(representative)
        if len(group) > 1:
            duplicate_groups.append({"representative": representative, "protein_ids": sorted(group)})
    selected = set(anchors)
    groups = defaultdict(list)
    for pid in representatives:
        if pid not in selected:
            groups[stratum(registry[pid], bindings[pid])].append(pid)

    def rank(pid):
        return hashlib.sha256((policy["seed"] + "\0" + pid).encode()).hexdigest(), pid

    queues = {key: deque(sorted(values, key=rank)) for key, values in sorted(groups.items())}
    while len(selected) < policy["maximum_proteins"] and any(queues.values()):
        for queue in queues.values():
            if queue and len(selected) < policy["maximum_proteins"]:
                selected.add(queue.popleft())
    selected = sorted(selected)
    if not selected:
        raise ValueError("no eligible proteins")
    residues = sum(registry[pid]["sequence_length"] for pid in selected)
    charged = [sum(aa in "KRDE" for aa in registry[pid]["sequence"]) for pid in selected]
    pairs = sum(n * (n - 1) // 2 for n in charged)
    report = {
        "policy": policy,
        "interpretation": "Stratified engineering sample of reviewed, exact map matches; not a representative proteome sample.",
        "map_proteins": len(points), "registry_proteins": len(registry),
        "eligible_proteins": len(eligible), "unique_eligible_sequences": len(by_sequence),
        "selected_proteins": len(selected), "protein_ids": selected,
        "eligible_strata": summarize_members(eligible, registry, bindings),
        "selected_strata": summarize_members(selected, registry, bindings),
        "exclusions": {reason: {"count": len(ids), "protein_ids": ids}
                       for reason, ids in sorted(excluded.items())},
        "not_sampled_eligible": sorted(set(eligible) - set(selected)),
        "duplicate_sequence_groups": sorted(duplicate_groups, key=lambda g: g["representative"]),
        "scope_policy": "Whole pinned reference sequences only; no mature-chain or isoform inference.",
        "resource_estimate": {
            "residues": residues, "scd_charged_pairs": pairs,
            "maximum_profile_entries": 3 * residues,
            "estimated_bundle_bytes_upper_bound": 240 * residues + 50000 * len(selected),
            "scd_seconds_at_1_to_10_million_pairs_per_second": [pairs / 10000000, pairs / 1000000],
            "runtime_basis": "Planning range for the quadratic SCD inner loop only; excludes validation, I/O and predictor setup.",
        },
    }
    return selected, report


def cohort_artifacts(root=ROOT, registry=None):
    folder = root / "data/biophysical"
    paths = {
        "registry": root / "data/grounding/protein_registry.jsonl",
        "map": root / "docs/data/sequence_map.json",
        "embedding_proteins": folder / "cohort.embedding-proteins.jsonl",
        "embedding_meta": folder / "cohort.embedding-meta.json",
        "policy": folder / "cohort.policy.json",
    }
    registry = load_registry(paths["registry"]) if registry is None else registry
    map_data = json.loads(paths["map"].read_text())
    meta = json.loads(paths["embedding_meta"].read_text())
    if meta.get("source_proteins_sha256") != digest(paths["embedding_proteins"]):
        raise ValueError("cohort embedding snapshot differs from its recorded source hash")
    if any(meta.get(k) != map_data.get("embedding", {}).get(k) or meta.get(k) is None
           for k in EMBEDDING_KEYS):
        raise ValueError("cohort embedding model/revision/settings differ from the map")
    rows = list(read_jsonl(paths["embedding_proteins"]))
    ids, report = select_cohort(registry, map_data, rows, json.loads(paths["policy"].read_text()))
    report["input_sha256"] = {key: digest(path) for key, path in paths.items()}
    selected = set(ids)
    bindings = sorted((row for row in rows if row["accession"] in selected), key=lambda row: row["accession"])
    return {
        folder / "pilot.proteins.txt": "# Reproduce with just select-biophysical-cohort\n" + "\n".join(ids) + "\n",
        folder / "pilot.embedding-proteins.jsonl": "".join(canonical_json(row) + "\n" for row in bindings),
        folder / "pilot.embedding-meta.json": json.dumps(meta, indent=2, sort_keys=True) + "\n",
        folder / "cohort.manifest.json": json.dumps(report, indent=2, sort_keys=True) + "\n",
    }


def check_cohort(root=ROOT, registry=None):
    errors = []
    for path, expected in cohort_artifacts(root, registry).items():
        if path.read_text() != expected:
            errors.append(f"cohort artifact differs from its selection policy/inputs: {path.name}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        artifacts = cohort_artifacts(args.root)
        manifest = json.loads(artifacts[args.root / "data/biophysical/cohort.manifest.json"])
        print(json.dumps({k: manifest[k] for k in ("eligible_proteins", "selected_proteins", "selected_strata", "resource_estimate")}, indent=2))
        if args.apply:
            for path, text in artifacts.items():
                atomic_write(path, text)
        else:
            print("Dry run; --apply refreshes selection artifacts. Rebuild and check the entire bundle before publishing.")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"cohort selection failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
