"""Failure cases for cohort selection, retained predictions and experimental evidence."""
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from biophysical import canonical_json, descriptor_id, observation_id, sha256  # noqa: E402
from calculate_biophysical import digest  # noqa: E402
from check_biophysical_pilot import check_pilot  # noqa: E402
from import_biophysical_experiments import artifacts, check_experiments, experimental_tsv, references, source_tables  # noqa: E402
from predict_biophysical_disorder import REFERENCE_SEQUENCE, check_reference, normalize_raw  # noqa: E402
import predict_biophysical_disorder as disorder  # noqa: E402
import refresh_biophysical as refresh  # noqa: E402
from select_biophysical_cohort import check_cohort, cohort_artifacts, select_cohort  # noqa: E402
from validate_biophysical import load_catalog, validate_collection  # noqa: E402


def protein(pid, sequence, taxon="NCBITaxon:9606"):
    return dict(protein_id=pid, protein_label="Synthetic fixture", sequence=sequence,
                sequence_sha256=sha256(sequence), sequence_length=len(sequence), reviewed=True,
                sequence_version=1, uniprot_release="2026_03", taxon_id=taxon, taxon_label="Fixture")


@pytest.fixture
def selection():
    registry = {f"UniProtKB:P{i:05}": protein(f"UniProtKB:P{i:05}", "ACDEFGHIKLMNPQRSTVWY" + "A" * i,
                "NCBITaxon:9606" if i % 2 else "NCBITaxon:10090") for i in range(8)}
    points = [[0, 0, 0, pid] for pid in registry]
    bindings = [dict(accession=pid, sequence_sha256=p["sequence_sha256"], length=p["sequence_length"],
                     axes={"SEQ": []}) for pid, p in registry.items()]
    policy = dict(version=1, maximum_proteins=4, minimum_length=1, maximum_length=2000,
                  seed="test", anchors=["UniProtKB:P00000"])
    return registry, {"points": points}, bindings, policy


def test_cohort_is_order_invariant_bounded_and_stratified(selection):
    registry, mapped, bindings, policy = selection
    selected, report = select_cohort(*selection)
    assert len(selected) == 4 and policy["anchors"][0] in selected
    assert len(report["selected_strata"]["taxon"]) == 2
    assert report["resource_estimate"]["residues"] == sum(registry[p]["sequence_length"] for p in selected)
    assert select_cohort(dict(reversed(list(registry.items()))), {"points": mapped["points"][::-1]},
                         bindings[::-1], policy) == (selected, report)


@pytest.mark.parametrize("case,reason", [
    ("hash", "embedding_sequence_mismatch"), ("length", "embedding_sequence_mismatch"),
    ("missing", "missing_embedding_binding"), ("registry", "no_release_pinned_registry_reference"),
    ("reviewed", "unreviewed_reference"), ("budget", "outside_length_budget"),
    ("residue", "nonstandard_residues_not_masked"),
])
def test_cohort_reports_identity_and_resource_exclusions(selection, case, reason):
    registry, _, bindings, policy = selection
    pid = bindings[-1]["accession"]
    if case == "hash":
        bindings[-1]["sequence_sha256"] = "0" * 64
    elif case == "length":
        bindings[-1]["length"] += 1
    elif case == "missing":
        bindings.pop()
    elif case == "registry":
        del registry[pid]
    elif case == "reviewed":
        registry[pid]["reviewed"] = False
    elif case == "budget":
        policy["maximum_length"] = 25
    else:
        registry[pid] = protein(pid, "AX")
        bindings[-1].update(sequence_sha256=sha256("AX"), length=2)
    selected, report = select_cohort(*selection)
    assert pid not in selected and pid in report["exclusions"][reason]["protein_ids"]


def test_duplicate_sequences_prefer_anchor_and_drifted_anchor_fails(selection):
    registry, _, bindings, _ = selection
    duplicate = bindings[-1]["accession"]
    registry[duplicate] = {**registry[bindings[0]["accession"]], "protein_id": duplicate}
    bindings[-1].update(sequence_sha256=bindings[0]["sequence_sha256"], length=bindings[0]["length"])
    selected, report = select_cohort(*selection)
    assert duplicate not in selected and report["duplicate_sequence_groups"][0]["representative"] in selected
    bindings[0]["sequence_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="no longer eligible"):
        select_cohort(*selection)


@pytest.mark.parametrize("key,value", [("maximum_proteins", True), ("maximum_length", 5001),
                                      ("version", 2), ("version", True), ("seed", ""), ("extra", 1)])
def test_invalid_cohort_policy_fails(selection, key, value):
    selection[-1][key] = value
    with pytest.raises(ValueError):
        select_cohort(*selection)


@pytest.mark.parametrize("case", ["sequence", "truncated", "nan", "range", "boolean", "duplicate", "missing", "unknown", "extra"])
def test_raw_prediction_rejects_identity_coverage_and_score_errors(case):
    pid = "UniProtKB:P12345"
    registry = {pid: protein(pid, "ACDE")}
    rows = [{"protein_id": pid, "sequence": "ACDE", "scores": [0.1, 0.5, 0.6, 0.9]}]
    if case == "sequence":
        rows[0]["sequence"] = "ACDF"
    elif case == "truncated":
        rows[0]["scores"].pop()
    elif case in {"nan", "range", "boolean"}:
        rows[0]["scores"][0] = {"nan": float("nan"), "range": 1.1, "boolean": True}[case]
    elif case == "duplicate":
        rows.append(deepcopy(rows[0]))
    elif case == "missing":
        rows.clear()
    elif case == "unknown":
        rows[0]["protein_id"] = "UniProtKB:P99999"
    else:
        rows[0]["unexpected"] = True
    with pytest.raises(ValueError):
        normalize_raw(rows, registry, [pid])


def test_unsupported_sequences_are_unavailable_and_not_masked():
    pid = "UniProtKB:P12345"
    registry = {pid: protein(pid, "AX")}
    assert normalize_raw([], registry, [pid]) == []
    with pytest.raises(ValueError, match="unsupported residues"):
        normalize_raw([{"protein_id": pid, "sequence": "AX", "scores": [0.5, 0.5]}], registry, [pid])


def test_reference_prediction_has_numerical_tolerance():
    expected = [0.5] * len(REFERENCE_SEQUENCE)
    assert check_reference([0.5001] * len(expected), expected) < 0.001
    with pytest.raises(ValueError, match="reference example"):
        check_reference([0.502] * len(expected), expected)
    with pytest.raises(ValueError, match="finite"):
        check_reference([float("nan")] * len(expected), expected)


@pytest.fixture
def retained_disorder(tmp_path):
    folder = tmp_path / "data/biophysical/disorder"
    source = ROOT / "data/biophysical/disorder"
    shutil.copytree(source, folder)
    row = json.loads((source / "predictions.raw.jsonl").read_text().splitlines()[0])
    pid = row["protein_id"]
    registry = {pid: protein(pid, row["sequence"])}
    registry_path = tmp_path / "data/grounding/protein_registry.jsonl"
    registry_path.parent.mkdir()
    registry_path.write_text(canonical_json(registry[pid]) + "\n")
    selection = folder.parent / "pilot.proteins.txt"
    selection.write_text(pid + "\n")
    raw, normalized = folder / "predictions.raw.jsonl", folder / "predictions.jsonl"
    raw.write_text(canonical_json(row) + "\n")
    normalized.write_text(canonical_json(normalize_raw([row], registry, [pid])[0]) + "\n")
    manifest = json.loads((folder / "run.json").read_text())
    manifest.update(registry_sha256=digest(registry_path), selection_sha256=digest(selection),
                    raw_output_sha256=digest(raw), normalized_output_sha256=digest(normalized),
                    protein_ids=[pid], predicted_proteins=1, unavailable_proteins=[])
    (folder / "run.json").write_text(json.dumps(manifest))
    assert disorder.check_disorder_bundle(tmp_path) == []
    return tmp_path


@pytest.mark.parametrize("case", ["version", "mode", "raw_hash", "license", "extra", "dependencies", "checkpoint"])
def test_retained_prediction_gate_rejects_provenance_drift(retained_disorder, case):
    folder = retained_disorder / "data/biophysical/disorder"
    path = folder / "run.json"
    manifest = json.loads(path.read_text())
    if case == "dependencies":
        (folder / "requirements.txt").write_text("metapredict==0.0.0\n")
    elif case == "checkpoint":
        (folder / "upstream/model.pt").write_bytes(b"changed")
    elif case == "raw_hash":
        manifest["raw_output_sha256"] = "0" * 64
    else:
        manifest[case] = "" if case == "license" else "wrong"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        disorder.check_disorder_bundle(retained_disorder)


def test_cohort_snapshot_hash_and_selection_replay(tmp_path, selection):
    registry, mapped, bindings, policy = selection
    folder = tmp_path / "data/biophysical"
    folder.mkdir(parents=True)
    registry_path = tmp_path / "data/grounding/protein_registry.jsonl"
    registry_path.parent.mkdir()
    registry_path.write_text("".join(canonical_json(p) + "\n" for p in registry.values()))
    snapshot = folder / "cohort.embedding-proteins.jsonl"
    snapshot.write_text("".join(canonical_json(p) + "\n" for p in bindings))
    meta = dict(model="fixture", revision="v1", pooling="mean", window=1022, overlap=256,
                source_proteins_sha256=digest(snapshot))
    (folder / "cohort.embedding-meta.json").write_text(json.dumps(meta))
    (folder / "cohort.policy.json").write_text(json.dumps(policy))
    map_path = tmp_path / "docs/data/sequence_map.json"
    map_path.parent.mkdir(parents=True)
    map_path.write_text(json.dumps({**mapped, "embedding": meta}))
    for path, value in cohort_artifacts(tmp_path).items():
        path.write_text(value)
    assert check_cohort(tmp_path) == []
    selected = folder / "pilot.proteins.txt"
    selected.write_text(selected.read_text() + "UniProtKB:P99999\n")
    assert check_cohort(tmp_path)
    snapshot.write_text(snapshot.read_text() + "\n")
    with pytest.raises(ValueError, match="recorded source hash"):
        cohort_artifacts(tmp_path)


def test_interrupted_publish_fails_gate_until_complete_replacement(tmp_path, monkeypatch):
    stage, root = tmp_path / "stage", tmp_path / "root"
    stage.mkdir()
    names = ["one.json", "two.json"]
    for name in names:
        (stage / name).write_text(name)
    hashes = {name: digest(stage / name) for name in names}
    original = refresh.atomic_write

    def interrupted(path, value):
        if path.name == "two.json":
            raise OSError("simulated interruption")
        original(path, value)

    monkeypatch.setattr(refresh, "atomic_write", interrupted)
    with pytest.raises(OSError, match="simulated interruption"):
        refresh.publish_outputs(root, stage, hashes)
    assert "interrupted" in check_pilot(root)[0]
    monkeypatch.setattr(refresh, "atomic_write", original)
    refresh.publish_outputs(root, stage, hashes)
    assert not (root / "data/biophysical/.refresh-incomplete").exists()
    assert all((root / name).read_bytes() == (stage / name).read_bytes() for name in names)


@pytest.fixture
def experiments():
    folder = ROOT / "data/biophysical/experimental"
    output = artifacts(ROOT)
    observations = [json.loads(line) for line in output[folder / "observations.jsonl"].splitlines()]
    return observations, references(folder), load_catalog(folder / "descriptors.yaml")


def test_publication_values_constructs_and_sign_conversion(experiments):
    observations, registry, catalog = experiments
    assert len(observations) == 14 and validate_collection(observations, registry, catalog) == []
    def values(code):
        return [o["value"] for o in observations if o["descriptor_id"] == descriptor_id(code)]
    assert values("B25") == [54.9, 56.9, 58.5, 64.2, 68.3, 73.3, 75.4, 78.6]
    assert values("B26") == [26.16]
    assert values("B27") == [3.33, 4.09]
    assert values("B30") == [3.68, 4.22, 2.30]
    assert all(o["scope"] == "REGION" for o in observations)
    assert {(o["region"]["start"], o["region"]["end"]) for o in observations} == {(1, 76), (19, 147)}
    dg = next(o for o in observations if o["descriptor_id"] == descriptor_id("B26"))
    assert {p["name"]: p["value"] for p in dg["method"]["parameters"]}["source_value_kj_per_mol"] == "-26.16"
    assert all(len(o["evidence"]) == 2 for o in observations if o["descriptor_id"] == descriptor_id("B30"))
    exported = list(csv.DictReader(io.StringIO(experimental_tsv(observations)), delimiter="\t"))
    sol = next(o for o in exported if o["descriptor_id"] == descriptor_id("B30"))
    assert json.loads(sol["method_parameters"])["salt_composition"] == "NaCl 4% w/v (40 g/L)"
    assert sol["normalization"] == "mass concentration of dissolved protein"


@pytest.mark.parametrize("code,case", [
    ("B25", "ph"), ("B25", "mode"), ("B25", "source"), ("B25", "unit"), ("B25", "negative"),
    ("B26", "temperature"), ("B26", "normalization"), ("B26", "equilibrium_model"),
    ("B27", "denaturant"), ("B27", "negative"), ("B30", "buffer"), ("B30", "temperature"),
    ("B30", "solid_phase"), ("B30", "negative"), ("B30", "normalization"), ("B30", "comparator"),
    ("B30", "scope"),
])
def test_experiments_reject_missing_context_and_incompatible_values(experiments, code, case):
    observations, registry, catalog = experiments
    row = deepcopy(next(o for o in observations if o["descriptor_id"] == descriptor_id(code)))
    if case in {"ph", "buffer", "temperature"}:
        row["conditions"].pop("temperature_celsius" if case == "temperature" else case)
    elif case == "mode":
        row["evidence_mode"] = "MODEL_PREDICTION"
    elif case == "source":
        row["method"].pop("source_artifact_sha256")
    elif case == "unit":
        row["unit"] = "K"
    elif case == "negative":
        row["value"] = -300
    elif case == "normalization":
        row["normalization"] = "unspecified"
    elif case == "comparator":
        row["comparator"] = {"value": 1.0}
    elif case == "scope":
        row["scope"] = "WHOLE_PROTEIN"
    else:
        row["method"]["parameters"] = [p for p in row["method"]["parameters"] if p["name"] != case]
    row["observation_id"] = observation_id(row)
    assert validate_collection([row], registry, catalog)


def test_experimental_replay_rejects_rehashed_values_and_changed_sources(tmp_path):
    folder = tmp_path / "data/biophysical/experimental"
    shutil.copytree(ROOT / "data/biophysical/experimental", folder)
    for path, value in artifacts(tmp_path).items():
        path.write_text(value)
    assert check_experiments(tmp_path) == []
    rows = [json.loads(line) for line in (folder / "observations.jsonl").read_text().splitlines()]
    rows[0]["value"] += 1
    rows[0]["observation_id"] = observation_id(rows[0])
    (folder / "observations.jsonl").write_text("".join(canonical_json(o) + "\n" for o in rows))
    assert check_experiments(tmp_path)
    source = folder / "sources/crespo2011.xml"
    source.write_text(source.read_text().replace("54.9", "55.9"))
    with pytest.raises(ValueError, match="reviewed snapshot"):
        source_tables(folder)
