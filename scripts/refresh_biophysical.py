#!/usr/bin/env python3
"""Stage, validate and publish one complete biophysical sequence bundle.

This does not run a predictor or change map coordinates. Refresh the cohort and
retained prediction run explicitly first. A marker makes an interrupted publish
fail the publication gate until a complete refresh succeeds.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile

from analyze_biophysical import summarize
from biophysical import canonical_json
from build_biophysical_overlay import main as overlay_main
from calculate_biophysical import atomic_write, digest, main as calculate_main
from check_biophysical_pilot import check_pilot
from select_biophysical_cohort import cohort_artifacts
from validate_biophysical import load_catalog, load_registry, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ["data/biophysical/" + name for name in (
    "pilot.proteins.txt", "pilot.embedding-proteins.jsonl", "pilot.embedding-meta.json",
    "cohort.manifest.json", "pilot.observations.jsonl", "pilot.observations.manifest.json",
    "pilot.observations.tsv", "pilot.analysis.json")]
OUTPUTS.append("docs/data/sequence_biophysical.json")


def publish_outputs(root, stage, hashes):
    marker = root / "data/biophysical/.refresh-incomplete"
    atomic_write(marker, canonical_json(hashes) + "\n")
    # An interruption between replacements leaves a marker that fails the gate.
    for name in hashes:
        atomic_write(root / name, (stage / name).read_text())
    if any(digest(root / name) != expected for name, expected in hashes.items()):
        raise ValueError("published files differ from the validated stage; marker retained")
    marker.unlink()


def refresh(root=ROOT, apply=False):
    folder = root / "data/biophysical"
    marker = folder / ".refresh-incomplete"
    sources = [p for p in folder.rglob("*") if p.is_file()
               and str(p.relative_to(root)) not in OUTPUTS and p != marker]
    sources += [root / "data/grounding/protein_registry.jsonl", root / "docs/data/sequence_map.json"]
    before = {p: digest(p) for p in sources}
    with tempfile.TemporaryDirectory(prefix="ptm-biophysical-stage-") as tmp:
        stage = Path(tmp)
        shutil.copytree(folder, stage / "data/biophysical")
        (stage / "data/biophysical/.refresh-incomplete").unlink(missing_ok=True)
        for relative in ("data/grounding/protein_registry.jsonl", "docs/data/sequence_map.json"):
            (stage / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, stage / relative)
        for path, text in cohort_artifacts(stage).items():
            atomic_write(path, text)
        sf = stage / "data/biophysical"
        registry_path = stage / "data/grounding/protein_registry.jsonl"
        catalog_path = sf / "descriptors.yaml"
        observations_path = sf / "pilot.observations.jsonl"
        with redirect_stdout(io.StringIO()):
            result = calculate_main(["--registry", str(registry_path), "--catalog", str(catalog_path),
                                    "--proteins", str(sf / "pilot.proteins.txt"),
                                    "--disorder", str(sf / "disorder/predictions.jsonl"),
                                    "--output", str(observations_path), "--apply"])
            if result:
                raise ValueError("staged calculation failed")
            result = overlay_main(["--map", str(stage / "docs/data/sequence_map.json"),
                                   "--embedding-proteins", str(sf / "pilot.embedding-proteins.jsonl"),
                                   "--embedding-meta", str(sf / "pilot.embedding-meta.json"),
                                   "--registry", str(registry_path), "--catalog", str(catalog_path),
                                   "--observations", str(observations_path),
                                   "--output", str(stage / "docs/data/sequence_biophysical.json"), "--apply"])
            if result:
                raise ValueError("staged map overlay failed")
        observations = list(read_jsonl(observations_path))
        analysis = summarize(observations, load_registry(registry_path), load_catalog(catalog_path))
        analysis["observations_sha256"] = digest(observations_path)
        atomic_write(sf / "pilot.analysis.json", json.dumps(analysis, indent=2, allow_nan=False) + "\n")
        errors = check_pilot(stage, require_input_provenance=True)
        if errors:
            raise ValueError("\n".join(errors))
        if any(digest(p) != expected for p, expected in before.items()):
            raise ValueError("inputs changed during refresh; nothing published")
        hashes = {name: digest(stage / name) for name in OUTPUTS}
        if apply:
            publish_outputs(root, stage, hashes)
        return {"proteins": analysis["proteins"], "observations": len(observations),
                "statuses": analysis["statuses"], "output_bytes": sum((stage / name).stat().st_size for name in OUTPUTS),
                "applied": apply, "map_sha256": before[root / "docs/data/sequence_map.json"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(refresh(args.root, args.apply), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"biophysical refresh failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
