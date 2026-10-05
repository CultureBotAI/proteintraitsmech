#!/usr/bin/env python3
"""Build validated SLC10 research evidence, without trait/grounding promotion.

Dry-run by default. The only durable destination is data/molecular/slc10/pilot.json.
The curated input is deliberately separate from calculated contact/comparison data.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile

import yaml

from molecular_evidence import build_structural_bundle, canonical, sha256
from slc10_model_comparison import build_model_comparisons
from validate_molecular_evidence import ROOT, validate_bundle

CURATION = ROOT / "data/molecular/slc10/curation.yaml"
OUTPUT = ROOT / "data/molecular/slc10/pilot.json"


def build(snapshot, curation_path=CURATION, model_snapshot=None):
    bundle = build_structural_bundle(snapshot)
    if model_snapshot is not None:
        artifacts, comparisons = build_model_comparisons(snapshot, model_snapshot, bundle["protein_references"])
        bundle["sources"].extend(artifacts)
        bundle["model_comparisons"] = comparisons
    curation = yaml.safe_load(curation_path.read_text())
    allowed = {"functional_observations", "explanations", "mechanisms"}
    if not isinstance(curation, dict) or set(curation) != allowed:
        raise ValueError("curation requires exactly observations, explanations, and mechanisms")
    proteins = {r["protein_id"]: r for r in bundle["protein_references"]}
    for kind in sorted(allowed):
        if not isinstance(curation[kind], list):
            raise ValueError(f"curation {kind} must be a list")
        rows = deepcopy(curation[kind])
        if kind != "mechanisms":
            for row in rows:
                if "sequence_sha256" in row:
                    raise ValueError("curation must not override a calculated sequence binding")
                row["sequence_sha256"] = proteins[row["protein_id"]]["sequence_sha256"]
        else:
            for row in rows:
                for binding in row.get("residue_bindings", []):
                    if "sequence_sha256" in binding:
                        raise ValueError("curation must not override a residue sequence binding")
                    binding["sequence_sha256"] = proteins[binding["protein_id"]]["sequence_sha256"]
        bundle[kind] = rows
    errors = validate_bundle(bundle)
    if errors:
        raise ValueError("\n".join(errors))
    return bundle


def write_bundle(bundle):
    # Fixed destination prevents a CLI argument becoming a trait/registry writer.
    parent = OUTPUT.parent
    if any(p.is_symlink() for p in (OUTPUT, parent, parent.parent, parent.parent.parent)):
        raise ValueError("refusing symlinked molecular output")
    parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=parent,
                                         prefix=".pilot-", suffix=".json", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(canonical(bundle) + "\n")
        temporary.replace(OUTPUT)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--model-snapshot", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true", help="replay inputs and compare durable bytes")
    args = parser.parse_args(argv)
    if args.apply and args.check:
        parser.error("--apply and --check are mutually exclusive")
    try:
        bundle = build(args.snapshot, model_snapshot=args.model_snapshot)
        expected = canonical(bundle) + "\n"
        if args.check and OUTPUT.read_text() != expected:
            raise ValueError("durable pilot differs from input replay")
        if args.apply:
            write_bundle(bundle)
        print(json.dumps({"bundle_sha256": sha256(expected),
                          "protein_count": len(bundle["protein_references"]),
                          "site_count": len(bundle["sites"]),
                          "comparison_count": len(bundle["comparisons"]),
                          "functional_observation_count": len(bundle["functional_observations"]),
                          "mechanism_count": len(bundle["mechanisms"]),
                          "mode": "apply" if args.apply else "check" if args.check else "dry-run",
                          "qualification": "NONE_RESEARCH_EVIDENCE_ONLY"}, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        print(f"SLC10 pilot build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
