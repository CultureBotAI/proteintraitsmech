#!/usr/bin/env python3
"""Attach continuous biophysical values to an existing sequence map via a checked sidecar.

Coordinates are never recomputed. Exact embedding sequence hashes and embedding
model/revision must agree. The browser refuses a sidecar from a different map.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from biophysical import canonical_json, comparison_context
from calculate_biophysical import atomic_write, digest
from validate_biophysical import CATALOG, REGISTRY, load_catalog, load_registry, read_jsonl, validate_collection


def build_overlay(map_data, embedding_proteins, embedding_meta, observations, catalog):
    for name in ("model", "revision", "pooling", "window", "overlap"):
        value = embedding_meta.get(name)
        present = type(value) is int and value >= 0 if name == "overlap" else bool(value)
        if not present or value != map_data.get("embedding", {}).get(name):
            raise ValueError(f"embedding {name} does not match the map")
    points = {p[3] for p in map_data["points"]}
    if len(points) != len(map_data["points"]):
        raise ValueError("duplicate map protein IDs")
    embeddings = {}
    for row in embedding_proteins:
        if row["accession"] in embeddings:
            raise ValueError("duplicate embedding protein ID")
        embeddings[row["accession"]] = row
    groups, signatures = {}, {}
    # Summarize a series using an available result's method when possible.
    # Missing rows carry their own observation IDs but contribute no values to
    # pool, so an absent predictor must not conflict with a supplied predictor.
    for obs in sorted(observations, key=lambda o: o["status"] != "OK"):
        key = obs["protein_id"]
        desc = catalog[obs["descriptor_id"]]
        if key not in points or obs["scope"] != "WHOLE_PROTEIN" or desc["value_kind"] not in {"SCALAR", "SCALAR_PROFILE"}:
            continue
        embedded = embeddings.get(key, {})
        if embedded.get("sequence_sha256") != obs["sequence_sha256"] or embedded.get("length") != obs["sequence_length"]:
            raise ValueError(f"{key}: observation differs from the embedded sequence")
        did = obs["descriptor_id"]
        context = comparison_context(obs)
        method = context["method"]
        signature = canonical_json(context)
        if obs["status"] == "OK":
            if did in signatures and signatures[did] != signature:
                raise ValueError(f"{did}: incompatible methods or conditions; build separate overlays")
            signatures[did] = signature
        series = groups.setdefault(did, {"descriptor_id": did, "label": desc["label"],
                  "unit": obs["unit"], "method": method, "conditions": obs.get("conditions", {}),
                  "interpretation_limits": desc["interpretation_limits"], "values": {}})
        if key in series["values"]:
            raise ValueError(f"duplicate whole-protein observation for {key} / {did}")
        series["values"][key] = {"value": obs.get("value"), "status": obs["status"],
                                  "observation_id": obs["observation_id"],
                                  "sequence_sha256": obs["sequence_sha256"]}
    if not groups:
        raise ValueError("no scalar observations matched the map")
    for series in groups.values():
        values = [r["value"] for r in series["values"].values() if r["status"] == "OK"]
        series["available"] = len(values)
        series["minimum"] = min(values) if values else None
        series["maximum"] = max(values) if values else None
    return {"series": [groups[k] for k in sorted(groups)], "map_proteins": len(points),
            "interpretation": "Continuous sequence descriptors; exploratory overlays, not independent validation of the embedding."}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map", type=Path, default=Path("docs/data/sequence_map.json"))
    ap.add_argument("--embedding-proteins", type=Path, default=Path("data/biophysical/pilot.embedding-proteins.jsonl"))
    ap.add_argument("--embedding-meta", type=Path, default=Path("data/biophysical/pilot.embedding-meta.json"))
    ap.add_argument("--observations", type=Path, default=Path("data/biophysical/pilot.observations.jsonl"))
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    ap.add_argument("--catalog", type=Path, default=CATALOG)
    ap.add_argument("--output", type=Path, default=Path("docs/data/sequence_biophysical.json"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    try:
        observations = list(read_jsonl(args.observations))
        catalog = load_catalog(args.catalog)
        errors = validate_collection(observations, load_registry(args.registry), catalog)
        if errors:
            raise ValueError("\n".join(errors[:20]))
        overlay = build_overlay(json.loads(args.map.read_text()), list(read_jsonl(args.embedding_proteins)),
                                json.loads(args.embedding_meta.read_text()), observations, catalog)
        overlay.update(map_sha256=digest(args.map), observations_sha256=digest(args.observations),
                       embedding_proteins_sha256=digest(args.embedding_proteins))
        if args.apply:
            if args.output.resolve() in {p.resolve() for p in (args.map, args.embedding_proteins,
                args.embedding_meta, args.observations, args.registry, args.catalog)}:
                raise ValueError("overlay output must not overwrite an input")
            atomic_write(args.output, canonical_json(overlay) + "\n")
        print(f"{'Wrote' if args.apply else 'Would write'} {len(overlay['series'])} continuous overlays; map coordinates unchanged.")
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
