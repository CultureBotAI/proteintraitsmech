#!/usr/bin/env python3
"""Closed LinkML and cross-object validation for biophysical descriptors/observations."""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import sys

import yaml
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml.validator.report import Severity

from biophysical import ALPHABET, disorder_segments, observation_id, sha256

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml"
CATALOG = ROOT / "data/biophysical/descriptors.yaml"
REGISTRY = ROOT / "data/grounding/protein_registry.jsonl"


@lru_cache(maxsize=1)
def validator():
    return Validator(schema=str(SCHEMA),
                     validation_plugins=[JsonschemaValidationPlugin(closed=True)])


def schema_errors(obj, target):
    try:
        return [r.message for r in validator().validate(obj, target_class=target).results
                if r.severity == Severity.ERROR]
    except Exception as exc:
        return [f"schema validation failed: {exc}"]


def read_jsonl(path):
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected an object")
            yield row


def load_registry(path=REGISTRY):
    rows = {}
    for row in read_jsonl(path):
        key = row.get("protein_id")
        errors = schema_errors(row, "ProteinReference")
        if errors:
            raise ValueError(f"{key}: {errors}")
        if key in rows:
            raise ValueError(f"duplicate protein reference: {key}")
        if sha256(row["sequence"]) != row["sequence_sha256"] or len(row["sequence"]) != row["sequence_length"]:
            raise ValueError(f"{key}: registry sequence hash/length mismatch")
        isoform = int(key.rsplit("-", 1)[1]) if "-" in key else None
        if row.get("isoform") != isoform:
            raise ValueError(f"{key}: isoform metadata does not match the accession")
        rows[key] = row
    if not rows:
        raise ValueError("empty protein registry")
    return rows


def load_catalog(path=CATALOG):
    data = yaml.safe_load(path.read_text())
    errors = schema_errors(data, "BiophysicalDescriptorCatalog")
    if errors:
        raise ValueError(f"invalid descriptor catalog: {errors}")
    rows = {}
    inventory_ids = set()
    for row in data["descriptors"]:
        key = row["descriptor_id"]
        if key in rows or row["inventory_id"] in inventory_ids:
            raise ValueError(f"duplicate descriptor: {key}")
        if not row.get("references"):
            raise ValueError(f"{key}: missing references")
        rows[key] = row
        inventory_ids.add(row["inventory_id"])
    if not rows:
        raise ValueError("empty descriptor catalog")
    return rows


def finite_numbers(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_numbers(v) for v in value.values())
    if isinstance(value, list):
        return all(finite_numbers(v) for v in value)
    return True


def validate_observation(obs, registry, catalog, occurrence_evidence=None):
    errors = schema_errors(obs, "BiophysicalObservation")
    if errors:
        return errors
    if not finite_numbers(obs):
        return ["all numerical values must be finite"]
    if obs["observation_id"] != observation_id(obs):
        errors.append("observation_id does not match its canonical content hash")
    protein = registry.get(obs["protein_id"])
    descriptor = catalog.get(obs["descriptor_id"])
    if protein is None:
        errors.append("protein_id does not resolve in the registry")
    if descriptor is None:
        errors.append("descriptor_id does not resolve in the catalog")
    if protein is None or descriptor is None:
        return errors
    for name in ("sequence_sha256", "sequence_length", "uniprot_release", "sequence_version"):
        if obs.get(name) != protein.get(name):
            errors.append(f"{name} does not match the ProteinReference")
    if obs["scope"] == "WHOLE_PROTEIN":
        if "region" in obs:
            errors.append("WHOLE_PROTEIN must not carry a region")
        start, end = 1, len(protein["sequence"])
    else:
        if "region" not in obs:
            return errors + ["REGION requires coordinates"]
        start, end = obs["region"]["start"], obs["region"]["end"]
    if not 1 <= start <= end <= len(protein["sequence"]):
        return errors + ["region is outside the reference sequence"]
    sequence = protein["sequence"][start - 1:end]
    if sha256(sequence) != obs["analyzed_sequence_sha256"]:
        errors.append("analyzed sequence hash does not match the selected scope")
    if obs.get("region", {}).get("expected_sequence", sequence) != sequence:
        errors.append("region expected_sequence does not match")
    evidence_id = obs.get("trait_occurrence_evidence_id")
    if evidence_id:
        evidence = (occurrence_evidence or {}).get(evidence_id)
        if not evidence or any(evidence.get(k) != obs[k] for k in ("protein_id", "sequence_sha256")):
            errors.append("trait occurrence evidence does not resolve to this protein and hash")
        elif (obs["scope"] == "WHOLE_PROTEIN" and evidence.get("scope") != "WHOLE_PROTEIN") or (
            obs["scope"] == "REGION" and (evidence.get("scope") != "LOCALIZED" or
            evidence.get("intervals") != [{"start": start, "end": end}])):
            errors.append("trait occurrence evidence scope differs from the observation")
    if obs["unit"] != descriptor["unit"]:
        errors.append("unit differs from the operational descriptor")
    if not obs.get("evidence"):
        errors.append("evidence must not be empty")
    params = obs["method"]["parameters"]
    if not params or len({p["name"] for p in params}) != len(params):
        errors.append("method parameters must be nonempty and uniquely named")
    if any(not p["name"].strip() or not p["value"].strip() for p in params):
        errors.append("method parameter names and values must not be blank")
    if not all(obs["method"][k].strip() for k in ("name", "version", "reference", "implementation")):
        errors.append("method identity and provenance must not be blank")
    if not obs["proteoform"].strip():
        errors.append("proteoform assumptions must not be blank")
    parameters = {p["name"]: p["value"] for p in params}
    if obs["evidence_mode"] == "STRUCTURE_CALCULATION" and not all(
        obs["method"].get(k) for k in ("structure_id", "chain_id", "conformer")
    ):
        errors.append("structure calculations require structure_id, chain_id and conformer")
    uncertainty = obs.get("uncertainty", {})
    if uncertainty:
        if not ("value" in uncertainty or {"lower", "upper"} <= uncertainty.keys()):
            errors.append("uncertainty requires a value or both bounds")
        if ("lower" in uncertainty) != ("upper" in uncertainty) or (
            "lower" in uncertainty and uncertainty["lower"] > uncertainty["upper"]
        ):
            errors.append("invalid uncertainty interval")
    if obs.get("comparator") and not any(k in obs["comparator"] for k in ("value", "observation_id")):
        errors.append("comparator requires a value or observation_id")
    present = {k for k in ("value", "components", "profile", "intervals") if k in obs}
    if obs["status"] != "OK":
        if present or not obs.get("missing_reason", "").strip():
            errors.append("missing results require a reason and must not carry numerical payloads")
        return errors
    if "missing_reason" in obs:
        errors.append("OK results must not carry missing_reason")
    expected = {"SCALAR": {"value"}, "VECTOR": {"components"}, "PROFILE": {"profile"},
                "SCALAR_PROFILE": {"value", "profile", "intervals"}}[descriptor["value_kind"]]
    if present != expected:
        return errors + [f"descriptor requires result fields {sorted(expected)}"]
    code = descriptor["inventory_id"]
    if obs["evidence_mode"] == "SEQUENCE_CALCULATION" and set(sequence) - set(ALPHABET):
        errors.append("sequence calculations on nonstandard residues must be undefined")
    if code == "B01" and "ph" not in obs.get("conditions", {}):
        errors.append("net charge requires pH")
    if code in {"B01", "B02"} and obs["evidence_mode"] == "SEQUENCE_CALCULATION":
        if not {"pka_set", "n_terminus", "c_terminus"} <= parameters.keys():
            errors.append("charge/pI calculations require pKa and terminal-group parameters")
    if code in {"B03", "B04", "B05", "B22"} and not 0 <= obs["value"] <= 1:
        errors.append("fraction must be in [0,1]")
    if code == "B02" and not 0 <= obs["value"] <= 14:
        errors.append("pI must be in the declared range [0,14]")
    if code == "B16" and not 0 <= obs["value"] <= math.log2(20) + 1e-12:
        errors.append("20-residue entropy must be in [0,log2(20)]")
    if code == "B13":
        components = obs["components"]
        if (sorted(v["label"] for v in components) != sorted(ALPHABET)
            or any(not 0 <= v["value"] <= 1 for v in components)
            or not math.isclose(sum(v["value"] for v in components), 1.0, abs_tol=1e-10)):
            errors.append("composition must contain each standard residue exactly once and sum to 1")
    profile = obs.get("profile", [])
    if "profile" in obs and not profile:
        errors.append("OK profiles must not be empty")
    previous = 0
    for point in profile:
        if not start <= point["start"] <= point["end"] <= end or point["start"] <= previous:
            errors.append("profile windows must be ordered and within the analyzed scope")
            break
        previous = point["start"]
    if code in {"B08", "B09", "B10"} and obs.get("scale") != "AAindex:KYTJ820101":
        errors.append("pilot hydropathy requires AAindex:KYTJ820101")
    if code == "B10":
        try:
            angle = float(parameters["rotation_degrees"])
            if not math.isfinite(angle) or not 0 < angle <= 180 or not parameters.get("geometry"):
                errors.append("hydrophobic moment requires an explicit geometry and rotation in (0,180]")
        except (KeyError, ValueError):
            errors.append("hydrophobic moment requires rotation_degrees")
        if any(p["value"] < 0 for p in profile):
            errors.append("hydrophobic moment magnitude must be nonnegative")
    if code in {"B09", "B10"}:
        try:
            width = int(parameters["window"])
            if width < 1 or [(p["start"], p["end"]) for p in profile] != [
                (s, s + width - 1) for s in range(start, end - width + 2)
            ]:
                errors.append("profile must contain every valid window at stride 1")
        except (KeyError, ValueError):
            errors.append("window profile requires an integer window parameter")
    if code == "B22":
        if obs["evidence_mode"] not in {"MODEL_PREDICTION", "EXPERIMENT"}:
            errors.append("disorder requires a predictor or experiment")
        try:
            threshold = float(parameters["threshold"])
            scores = [p["value"] for p in profile]
            if (not math.isfinite(threshold) or not 0 <= threshold <= 1 or
                parameters.get("comparison") != ">" or not obs["method"].get("source_artifact_sha256")):
                errors.append("disorder requires a threshold in [0,1], > comparison and source hash")
            if [(p["start"], p["end"]) for p in profile] != [(i, i) for i in range(start, end + 1)]:
                errors.append("disorder scores must cover every residue of the analyzed scope")
            if any(not 0 <= v <= 1 for v in scores):
                errors.append("disorder scores must be in [0,1]")
            if not scores or not math.isclose(obs["value"], sum(v > threshold for v in scores) / len(scores), abs_tol=1e-12):
                errors.append("disorder fraction disagrees with the thresholded scores")
            if obs["intervals"] != disorder_segments(scores, start, threshold):
                errors.append("disorder intervals disagree with the thresholded scores")
        except (KeyError, ValueError):
            errors.append("disorder requires a numerical threshold")
    return errors


def validate_collection(observations, registry, catalog):
    errors, seen = [], set()
    for index, obs in enumerate(observations, 1):
        errors.extend(f"row {index}: {e}" for e in validate_observation(obs, registry, catalog))
        key = obs.get("observation_id")
        if key in seen:
            errors.append(f"row {index}: duplicate observation_id")
        seen.add(key)
    if not seen:
        errors.append("empty observation collection")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    args = parser.parse_args()
    try:
        rows = list(read_jsonl(args.observations))
        errors = validate_collection(rows, load_registry(args.registry), load_catalog(args.catalog))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(rows)} biophysical observations (closed schema + registry + semantics).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
