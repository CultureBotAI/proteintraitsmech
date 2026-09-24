#!/usr/bin/env python3
"""Exploratory pilot redundancy summary; never changes embedding coordinates or trait labels."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import itertools
import json
import math
from pathlib import Path
import sys

from biophysical import canonical_json, comparison_context
from calculate_biophysical import atomic_write, digest
from validate_biophysical import CATALOG, REGISTRY, load_catalog, load_registry, read_jsonl, validate_collection


def ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        for k in order[i:j]:
            result[k] = (i + j - 1) / 2
        i = j
    return result


def spearman(x, y):
    if len(x) != len(y) or len(x) < 4:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    dx, dy = [v - mx for v in rx], [v - my for v in ry]
    denominator = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    return sum(a * b for a, b in zip(dx, dy)) / denominator if denominator else None


def summarize(observations, registry, catalog):
    values, versions = defaultdict(dict), defaultdict(set)
    for o in observations:
        if o["scope"] != "WHOLE_PROTEIN":
            raise ValueError("pilot analysis accepts whole-protein observations only")
        if "value" not in o or o["status"] != "OK":
            continue
        code, pid = catalog[o["descriptor_id"]]["inventory_id"], o["protein_id"]
        if pid in values[code]:
            raise ValueError("analysis requires one result per descriptor/protein")
        values[code][pid] = o["value"]
        versions[code].add(canonical_json(comparison_context(o)))
    if any(len(v) > 1 for v in versions.values()):
        raise ValueError("analysis cannot pool different methods/versions/conditions")
    ids = sorted({o["protein_id"] for o in observations})
    groups = {"all": set(ids)}
    for pid in ids:
        p = registry[pid]
        size = "<=300" if p["sequence_length"] <= 300 else "301..600" if p["sequence_length"] <= 600 else ">600"
        for stratum in ("length:" + size, "source:UniProtKB:" + p["uniprot_release"], "taxon:" + p["taxon_id"]):
            groups.setdefault(stratum, set()).add(pid)
    output = {}
    for group, members in sorted(groups.items()):
        correlations = []
        for a, b in itertools.combinations(sorted(values), 2):
            paired = sorted(members & values[a].keys() & values[b].keys())
            rho = spearman([values[a][k] for k in paired], [values[b][k] for k in paired])
            correlations.append({"a": a, "b": b, "n": len(paired), "spearman_rho": rho})
        output[group] = {"proteins": len(members), "correlations": correlations}
    complete = set(values["B03"]) & values["B04"].keys() & values["B05"].keys()
    return {"proteins": len(ids), "observation_count": len(observations),
            "statuses": dict(Counter(o["status"] for o in observations)),
            "fcr_identity": {"n": len(complete), "maximum_absolute_error": max((
                abs(values["B05"][k] - values["B03"][k] - values["B04"][k]) for k in complete), default=None)},
            "strata": output,
            "interpretation": "Selected pilot only. Correlations are descriptive, not mechanism or independent embedding validation. Null means fewer than four paired values or a constant vector. Length bins are analysis strata, not trait classes. Source strata are UniProt releases, not independent assay or database sources."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--observations", type=Path, default=Path("data/biophysical/pilot.observations.jsonl"))
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    ap.add_argument("--catalog", type=Path, default=CATALOG)
    ap.add_argument("--output", type=Path, default=Path("data/biophysical/pilot.analysis.json"))
    args = ap.parse_args()
    try:
        observations = list(read_jsonl(args.observations))
        registry, catalog = load_registry(args.registry), load_catalog(args.catalog)
        errors = validate_collection(observations, registry, catalog)
        if errors:
            raise ValueError("\n".join(errors[:20]))
        if args.output.resolve() in {p.resolve() for p in (args.observations, args.registry, args.catalog)}:
            raise ValueError("analysis output must not overwrite an input")
        result = summarize(observations, registry, catalog)
        result["observations_sha256"] = digest(args.observations)
        atomic_write(args.output, json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(f"Analyzed {result['proteins']} proteins in {len(result['strata'])} strata.")
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
