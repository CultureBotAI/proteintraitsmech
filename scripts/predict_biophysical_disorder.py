#!/usr/bin/env python3
"""Run pinned metapredict locally and preserve full-sequence scores and provenance.

Inference is optional and never runs in CI. The publication gate verifies the
retained raw output, exact inputs, upstream reference check and normalized
adapter input without requiring PyTorch or contacting a prediction service.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import platform
import sys
import tempfile

from biophysical import ALPHABET, canonical_json, sha256, validate_prediction

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.2"
REVISION = "34ddeefba8285c57fb5307792ce5f6789f860bef"
MODEL = "backend/networks/metameta_2_7_22_nl2_hs20_b32_V3.pt"
MODEL_SHA256 = "32de116ad8e2edefc3abf96ea3495e90527323c6108db91dd7866391b77341bd"
MODE = "V3; CPU; normalized=True; round_values=True; single-sequence"
REFERENCE = "https://doi.org/10.1016/j.bpj.2021.08.039"
REFERENCE_SEQUENCE = "RDCAPNNGKKMDNQQHGDVSNQSDNRDSVQQQPPQMAGSQERQKSTESQQSPRSKENKQQAGHSHPESMPRSMSEKEPEMQHDESTGMQNHNRGMQSQDP"
UPSTREAM_HASHES = {
    "model.pt": MODEL_SHA256,
    "local_data.py": "3f698a7b513f5a334b76339e13240c6557d386a6a13fa2a6bd6c0a16b7d6386a",
    "test_metapredict.py.txt": "4c80031656129c24edcd6e4ca9a662425d76e5a805bfb13ae8e4ce37bfeebaa6",
    "LICENSE": "707213dfaf4b49b9a13dc6b6494e70134581f5c24f136bed13c07cb4da6e12c4",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("prediction artifacts must contain JSON objects")
    return rows


def inputs(root):
    folder = root / "data/biophysical"
    rows = read_rows(root / "data/grounding/protein_registry.jsonl")
    registry = {row["protein_id"]: row for row in rows}
    ids = [line for raw in (folder / "pilot.proteins.txt").read_text().splitlines()
           if (line := raw.strip()) and not line.startswith("#")]
    if len(registry) != len(rows) or not ids or len(set(ids)) != len(ids) or set(ids) - registry.keys():
        raise ValueError("prediction inputs require unique registry references and a nonempty resolved cohort")
    for pid in ids:
        protein = registry[pid]
        sequence = protein["sequence"]
        if not sequence or sha256(sequence) != protein["sequence_sha256"] or len(sequence) != protein["sequence_length"]:
            raise ValueError(f"{pid}: invalid full sequence hash/length")
    return registry, sorted(ids)


def reference_scores(folder):
    for name, expected in UPSTREAM_HASHES.items():
        if digest(folder / "upstream" / name) != expected:
            raise ValueError(f"pinned upstream predictor fixture differs: {name}")
    # Parse a literal only: never execute the acquired upstream fixture as code.
    tree = ast.parse((folder / "upstream/local_data.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "S2" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("upstream S2 reference scores are missing")


def check_reference(actual, expected):
    if len(actual) != len(expected) or len(actual) != len(REFERENCE_SEQUENCE):
        raise ValueError("predictor reference example has an incorrect score count")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in actual):
        raise ValueError("predictor reference example must be finite")
    error = max(abs(a - b) for a, b in zip(actual, expected))
    if error > 0.001:
        raise ValueError("predictor fails its upstream reference example (absolute tolerance 0.001)")
    return error


def normalize_raw(rows, registry, ids):
    predictions, seen = [], set()
    for row in rows:
        if row.keys() != {"protein_id", "sequence", "scores"}:
            raise ValueError("raw predictions require exactly protein_id, sequence and scores")
        pid = row["protein_id"]
        if pid in seen or pid not in ids:
            raise ValueError("raw predictions must be unique members of the selected cohort")
        protein = registry[pid]
        if row["sequence"] != protein["sequence"]:
            raise ValueError(f"{pid}: predictor input sequence differs from the full reference")
        if set(row["sequence"]) - set(ALPHABET):
            raise ValueError(f"{pid}: unsupported residues must not be silently normalized")
        prediction = {"protein_id": pid, "sequence_sha256": protein["sequence_sha256"],
                      "predictor": "metapredict", "version": VERSION, "mode": MODE,
                      "reference": REFERENCE, "scores": row["scores"]}
        validate_prediction(prediction, protein)
        predictions.append(prediction)
        seen.add(pid)
    supported = {pid for pid in ids if not set(registry[pid]["sequence"]) - set(ALPHABET)}
    if seen != supported:
        raise ValueError("raw output must cover every supported cohort sequence exactly once")
    return sorted(predictions, key=lambda p: p["protein_id"])


def check_disorder_bundle(root=ROOT):
    folder = root / "data/biophysical/disorder"
    registry, ids = inputs(root)
    raw = folder / "predictions.raw.jsonl"
    normalized = folder / "predictions.jsonl"
    manifest = json.loads((folder / "run.json").read_text())
    expected = reference_scores(folder)
    actual = json.loads((folder / "reference-result.json").read_text())
    error = check_reference(actual["scores"], expected)
    if actual["sequence"] != REFERENCE_SEQUENCE or actual["maximum_absolute_error"] != error:
        raise ValueError("predictor reference provenance differs")
    predictions = normalize_raw(read_rows(raw), registry, ids)
    if normalized.read_text() != "".join(canonical_json(p) + "\n" for p in predictions):
        raise ValueError("normalized disorder scores differ from retained raw output")
    expected_inputs = {
        "registry_sha256": digest(root / "data/grounding/protein_registry.jsonl"),
        "selection_sha256": digest(root / "data/biophysical/pilot.proteins.txt"),
        "runner_sha256": digest(Path(__file__)),
        "raw_output_sha256": digest(raw), "normalized_output_sha256": digest(normalized),
        "reference_result_sha256": digest(folder / "reference-result.json"),
        "dependencies_sha256": digest(folder / "requirements.txt"),
        "model_sha256": MODEL_SHA256, "upstream_revision": REVISION,
        "predictor": "metapredict", "version": VERSION, "mode": MODE,
        "protein_ids": ids, "predicted_proteins": len(predictions),
        "unavailable_proteins": sorted(set(ids) - {p["protein_id"] for p in predictions}),
        "upstream_fixture_sha256": UPSTREAM_HASHES,
    }
    if manifest.keys() != expected_inputs.keys() | {"completed_at", "python", "platform", "license", "limitations"}:
        raise ValueError("disorder run manifest has missing or unexpected fields")
    if any(manifest.get(key) != value for key, value in expected_inputs.items()):
        raise ValueError("disorder run provenance does not match retained inputs/outputs")
    for key in ("completed_at", "python", "platform", "license", "limitations"):
        if not isinstance(manifest[key], str) or not manifest[key].strip():
            raise ValueError(f"missing disorder run {key}")
    return []


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, encoding="utf-8", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(text)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        registry, ids = inputs(args.root)
        folder = args.root / "data/biophysical/disorder"
        expected = reference_scores(folder)
        if not args.apply:
            print(f"Would predict {len(ids)} full reference sequences using metapredict {VERSION} / {MODE}. Use --apply.")
            return 0
        if importlib.metadata.version("metapredict") != VERSION:
            raise ValueError(f"install metapredict=={VERSION} in the optional predictor environment")
        package = Path(importlib.util.find_spec("metapredict").origin).parent
        if digest(package / MODEL) != MODEL_SHA256:
            raise ValueError("installed predictor model differs from the pinned checkpoint")
        import torch
        from metapredict import meta
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)

        def predict(sequence):
            scores = meta.predict_disorder(sequence, version=3, device="cpu", normalized=True,
                                           round_values=True, return_numpy=False)
            return [float(value) for value in scores]

        reference = predict(REFERENCE_SEQUENCE)
        error = check_reference(reference, expected)
        rows = [{"protein_id": pid, "sequence": registry[pid]["sequence"],
                 "scores": predict(registry[pid]["sequence"])}
                for pid in ids if not set(registry[pid]["sequence"]) - set(ALPHABET)]
        normalized = normalize_raw(rows, registry, ids)
        write(folder / "predictions.raw.jsonl", "".join(canonical_json(row) + "\n" for row in rows))
        write(folder / "predictions.jsonl", "".join(canonical_json(row) + "\n" for row in normalized))
        write(folder / "reference-result.json", canonical_json({"sequence": REFERENCE_SEQUENCE,
              "scores": reference, "maximum_absolute_error": error}) + "\n")
        dependencies = sorted(f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions())
        write(folder / "requirements.txt", "\n".join(dependencies) + "\n")
        manifest = {
            "registry_sha256": digest(args.root / "data/grounding/protein_registry.jsonl"),
            "selection_sha256": digest(args.root / "data/biophysical/pilot.proteins.txt"),
            "runner_sha256": digest(Path(__file__)),
            "raw_output_sha256": digest(folder / "predictions.raw.jsonl"),
            "normalized_output_sha256": digest(folder / "predictions.jsonl"),
            "reference_result_sha256": digest(folder / "reference-result.json"),
            "dependencies_sha256": digest(folder / "requirements.txt"),
            "model_sha256": MODEL_SHA256, "upstream_revision": REVISION,
            "predictor": "metapredict", "version": VERSION, "mode": MODE,
            "protein_ids": ids, "predicted_proteins": len(normalized),
            "unavailable_proteins": sorted(set(ids) - {p["protein_id"] for p in normalized}),
            "upstream_fixture_sha256": UPSTREAM_HASHES,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(), "platform": platform.platform(),
            "license": "MIT (metapredict code, model and fixtures); CC-BY-4.0 (UniProt sequences)",
            "limitations": "Predicted disorder, not experimental evidence. V3 trained on hybrid disorder/pLDDT targets. Standard uppercase residues only; unsupported sequences remain unavailable. No domain gap-closing or independent embedding validation.",
        }
        write(folder / "run.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        check_disorder_bundle(args.root)
        print(f"Recorded {len(normalized)} predictions; upstream reference maximum absolute error {error:.6g}.")
    except (ValueError, OSError, KeyError, TypeError, ImportError) as exc:
        print(f"disorder prediction failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
