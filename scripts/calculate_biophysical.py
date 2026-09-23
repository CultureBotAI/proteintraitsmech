#!/usr/bin/env python3
"""Calculate the 12-family biophysical pilot from release-pinned ProteinReferences.

Dry-run unless --apply. Full JSONL output is validated before atomic replacement.
A manifest records the exact inputs/options and a continuous-value summary TSV
supports analysis without promoting canonical examples or qualitative classes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile

from biophysical import VERSION, calculate, canonical_json
from validate_biophysical import CATALOG, REGISTRY, load_catalog, load_registry, read_jsonl, validate_collection


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, encoding="utf-8", delete=False) as f:
            name = Path(f.name)
            f.write(text)
        name.replace(path)
    finally:
        if name and name.exists():
            name.unlink()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--proteins", type=Path, help="One exact UniProtKB CURIE per line; omit for all registry proteins")
    parser.add_argument("--disorder", type=Path, help="JSONL of predictor provenance and full-sequence scores")
    parser.add_argument("--output", type=Path, default=Path("data/biophysical/observations.jsonl"))
    parser.add_argument("--ph", type=float, default=7.0)
    parser.add_argument("--window", type=int, default=19)
    parser.add_argument("--moment-window", type=int, default=11)
    parser.add_argument("--angle", type=float, default=100.0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--start", type=int)
    parser.add_argument("--end", type=int)
    parser.add_argument("--region-termini", choices=["native", "cleaved"], default="native")
    parser.add_argument("--max-scd-length", type=int, default=5000)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.output.suffix != ".jsonl":
            raise ValueError("observation output must have the .jsonl suffix")
        registry, catalog = load_registry(args.registry), load_catalog(args.catalog)
        ids = args.proteins.read_text().splitlines() if args.proteins else sorted(registry)
        ids = [p.strip() for p in ids if p.strip() and not p.startswith("#")]
        if not ids or len(ids) != len(set(ids)) or set(ids) - registry.keys():
            raise ValueError("selection must be nonempty, unique and present in the registry")
        if (args.start is not None or args.end is not None) and len(ids) != 1:
            raise ValueError("region calculations require exactly one selected protein")
        predictions = {}
        for p in read_jsonl(args.disorder) if args.disorder else []:
            key = p.get("protein_id")
            if key in predictions or key not in ids:
                raise ValueError("disorder inputs must be unique and belong to the selected proteins")
            predictions[key] = p
        options = {key: getattr(args, key) for key in ("ph", "window", "moment_window", "angle", "threshold",
                   "start", "end", "region_termini", "max_scd_length")}
        observations = [obs for key in sorted(ids) for obs in
                        calculate(registry[key], disorder=predictions.get(key), **options)]
        errors = validate_collection(observations, registry, catalog)
        if errors:
            raise ValueError("\n".join(errors[:20]))
        text = "".join(canonical_json(obs) + "\n" for obs in observations)
        manifest = {"calculator_version": VERSION, "options": options,
                    "registry_sha256": digest(args.registry), "catalog_sha256": digest(args.catalog),
                    "observation_file_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "protein_ids": sorted(ids), "observation_count": len(observations),
                    "statuses": dict(Counter(o["status"] for o in observations)),
                    "input_disorder_sha256": digest(args.disorder) if args.disorder else None,
                    "sequence_license": "CC-BY-4.0; UniProt Consortium",
                    "selection": "explicit protein list" if args.proteins else "all registry proteins"}
        print(json.dumps(manifest, indent=2))
        if args.apply:
            input_paths = [args.registry, args.catalog, args.proteins, args.disorder]
            paths = [args.output, args.output.with_suffix(".manifest.json"), args.output.with_suffix(".tsv")]
            if any(p.resolve() == source.resolve() for p in paths for source in input_paths if source):
                raise ValueError("output must not overwrite an input")
            lines = ["protein_id\tdescriptor_id\tstatus\tvalue\tunit\tsequence_sha256\tobservation_id"]
            lines.extend("\t".join(str(o.get(k, "")) for k in lines[0].split("\t")) for o in observations)
            atomic_write(paths[0], text)
            atomic_write(paths[1], json.dumps(manifest, indent=2) + "\n")
            atomic_write(paths[2], "\n".join(lines) + "\n")
        else:
            print("Dry run; use --apply to write the validated observations and manifest.")
    except (OSError, ValueError, KeyError) as exc:
        print(f"biophysical calculation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
