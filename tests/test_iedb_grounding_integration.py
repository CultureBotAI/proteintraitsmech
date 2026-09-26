"""Exercise staged IEDB support through the real central resolver and promoter."""

import copy
import csv
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
ground = importlib.import_module("ground_uniprot_examples")
provider = importlib.import_module("iedb_peptide_grounding")
validator = importlib.import_module("validate_uniprot_grounding")
native_inputs = importlib.import_module("test_iedb_peptide_snapshot").native_inputs
installed_source = importlib.import_module("test_iedb_peptide_grounding").installed_source


def _jsonl(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def _rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def _approve(pipeline):
    with pipeline["review"].open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        row.update(decision="APPROVED", reviewer="Fixture curator", reviewed_at="2026-09-17",
                   review_notes="Native peptide and exact existing parent verified.")
    with pipeline["approved"].open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def pipeline(installed_source, tmp_path, monkeypatch):
    path, record, reference, _ = installed_source
    monkeypatch.setattr(ground, "REPO_ROOT", tmp_path)
    record["mapping_status"] = "SEEDED"
    record["canonical_examples"][0]["source"] = "CURATOR"
    record["canonical_examples"][0]["features"] = [
        {"feature_type": "DOMAIN", "start": 3, "end": 6, "note": "Preserve generic feature"}
    ]
    record["canonical_examples"].append({
        "protein_id": "UniProtKB:Q12345", "protein_label": "Other existing example",
        "source": "CURATOR",
    })
    record_path = tmp_path / path
    record_path.parent.mkdir(parents=True)
    record_path.write_text(yaml.safe_dump(record, sort_keys=False))
    out = tmp_path / "staging"
    out.mkdir()
    result = {"root": tmp_path, "record": record_path, "before": copy.deepcopy(record),
              "traits": tmp_path / "data/traits", "output": out}
    for key in ("queue", "resolved", "registry", "evidence", "source_registry"):
        result[key] = out / (key + ".jsonl")
    for key in ("review", "approved"):
        result[key] = out / (key + ".tsv")
    for key in ("registry", "evidence", "bindings", "membership"):
        result["durable_" + key] = tmp_path / "durable" / (key + ".jsonl")
    _jsonl(result["source_registry"], [reference])
    candidate = {
        "schema_version": 1, "batch": "iedb-fixture", "candidate_status": "CANDIDATE_PROTEIN",
        "trait_id": record["identifier"], "source_trait_id": record["identifier"],
        "source_namespace": "IEDB", "record_path": path, "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_EPITOPE", "protein_id": reference["protein_id"],
        "scope": "LOCALIZED", "mapping_method": "PATTERN_MATCH", "evidence_tier": "B",
        "intervals": [{"start": 2, "end": 6}], "coordinate_frame": "UNIPROT_CANONICAL",
        "evidence_source": "IEDB", "source_release": provider.SOURCE_RELEASE,
        "uniprot_release": reference["uniprot_release"],
        "sequence_sha256": reference["sequence_sha256"],
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    result["candidate"] = candidate
    _jsonl(result["queue"], [candidate])
    result["resolve_args"] = [
        "resolve", "--providers", "protein-registry,iedb-peptide", "--allow-unreceipted-inputs",
        "--queue", str(result["queue"]), "--traits", str(result["traits"]),
        "--protein-registry", str(result["source_registry"]),
        "--residue-frame", str(out / "unused-residue.json"),
        "--profiles", str(out / "unused-profiles.jsonl"),
        "--out", str(result["resolved"]), "--review", str(result["review"]),
        "--registry-out", str(result["registry"]), "--evidence-out", str(result["evidence"]),
        "--batch", "iedb-fixture",
    ]
    result["promote_args"] = [
        "promote", "--resolved", str(result["resolved"]), "--approved", str(result["approved"]),
        "--traits", str(result["traits"]), "--protein-registry", str(result["registry"]),
        "--evidence-registry", str(result["evidence"]),
        "--durable-protein-registry", str(result["durable_registry"]),
        "--durable-evidence-registry", str(result["durable_evidence"]),
        "--durable-qualified-record-bindings", str(result["durable_bindings"]),
        "--durable-membership-registry", str(result["durable_membership"]),
    ]
    return result


def test_existing_example_gains_qualified_coordinates_and_a_record_binding(pipeline):
    assert ground.main(pipeline["resolve_args"]) == 0
    row = _rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "QUALIFIED", row["reasons"]
    assert row["trait_occurrence"]["intervals"] == [{"start": 2, "end": 6}]
    _approve(pipeline)
    before_bytes = pipeline["record"].read_bytes()
    assert ground.main(pipeline["promote_args"]) == 0
    assert pipeline["record"].read_bytes() == before_bytes
    assert not pipeline["durable_registry"].exists()
    assert ground.main(pipeline["promote_args"] + ["--apply"]) == 0
    after = yaml.safe_load(pipeline["record"].read_text())
    before = pipeline["before"]
    assert {k: v for k, v in after.items() if k != "canonical_examples"} == {
        k: v for k, v in before.items() if k != "canonical_examples"
    }
    assert [e["protein_id"] for e in after["canonical_examples"]] == [
        e["protein_id"] for e in before["canonical_examples"]
    ]
    assert after["canonical_examples"][1] == before["canonical_examples"][1]
    assert after["canonical_examples"][0]["features"] == before["canonical_examples"][0]["features"]
    assert after["canonical_examples"][0]["source"] == "CURATOR"
    refs, findings = validator.load_registry(pipeline["durable_registry"])
    assert not findings
    evidence = {row["evidence_id"]: row for row in _rows(pipeline["durable_evidence"])}
    assert not validator.validate_record(after, refs, evidence_registry=evidence)
    selected_only = {**after, "canonical_examples": after["canonical_examples"][:1]}
    assert not validator.validate_record(selected_only, refs, evidence_registry=evidence,
                                         require_qualified=True)
    binding = _rows(pipeline["durable_bindings"])[0]
    assert binding["record_sha256"] == hashlib.sha256(pipeline["record"].read_bytes()).hexdigest()
    assert binding["evidence_id"] in evidence
    installed_bytes = {p: p.read_bytes() for p in (
        pipeline["record"], pipeline["durable_registry"], pipeline["durable_evidence"],
        pipeline["durable_bindings"],
    )}
    assert ground.main(pipeline["promote_args"] + ["--apply"]) == 0
    assert all(path.read_bytes() == raw for path, raw in installed_bytes.items())


@pytest.mark.parametrize("change", ["record", "source"])
def test_stale_inputs_fail_before_any_durable_installation(pipeline, change):
    assert ground.main(pipeline["resolve_args"]) == 0
    _approve(pipeline)
    if change == "record":
        pipeline["record"].write_text(pipeline["record"].read_text() + "# later curator change\n")
    else:
        provider.source_path().write_text("{}")
    record_bytes = pipeline["record"].read_bytes()
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert pipeline["record"].read_bytes() == record_bytes
    assert not pipeline["durable_registry"].exists()
    assert not pipeline["durable_evidence"].exists()
    assert not pipeline["durable_bindings"].exists()


@pytest.mark.parametrize(("field", "value"), [
    ("intervals", [{"start": 3, "end": 7}]), ("coordinate_frame", "UNIPROT_ISOFORM"),
    ("inheritance_path", ["IEDB:11", "IEDB:10"]), ("scope", "WHOLE_PROTEIN"),
    ("evidence_source", "InterPro"), ("source_release", "old"),
    ("source_trait_id", "IEDB:11"), ("expected_residues", "ACDEF"),
])
def test_candidate_coordinate_or_source_conflicts_remain_rejected(pipeline, field, value):
    pipeline["candidate"][field] = value
    _jsonl(pipeline["queue"], [pipeline["candidate"]])
    assert ground.main(pipeline["resolve_args"]) == 0
    row = _rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"]
    assert not row.get("trait_occurrence")
    assert not pipeline["evidence"].read_text().strip()


def test_embedded_producer_claims_are_recomputed_from_the_trusted_source(pipeline):
    pipeline["candidate"]["trait_occurrence"] = {"intervals": [{"start": 200, "end": 204}]}
    pipeline["candidate"]["grounding_evidence"] = {"provider_entry_sha256": "f" * 64}
    _jsonl(pipeline["queue"], [pipeline["candidate"]])
    assert ground.main(pipeline["resolve_args"]) == 0
    row = _rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "QUALIFIED", row["reasons"]
    assert row["trait_occurrence"]["intervals"] == [{"start": 2, "end": 6}]
    assert row["grounding_evidence"]["provider_entry_sha256"] != "f" * 64


def test_unidentified_candidate_receives_its_id_after_coordinate_resolution(pipeline):
    pipeline["candidate"].pop("candidate_id")
    pipeline["candidate"].pop("intervals")
    _jsonl(pipeline["queue"], [pipeline["candidate"]])
    assert ground.main(pipeline["resolve_args"]) == 0
    row = _rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "QUALIFIED", row["reasons"]
    assert row["candidate_id"] == ground.derive_candidate_id(row)
    _approve(pipeline)
    assert ground.main(pipeline["promote_args"]) == 0


def test_source_change_during_promotion_preflight_is_rejected_before_writes(pipeline, monkeypatch):
    assert ground.main(pipeline["resolve_args"]) == 0
    _approve(pipeline)
    before = pipeline["record"].read_bytes()
    original = ground._promotion_qualified_record_preflight

    def changed_source(**kwargs):
        result = original(**kwargs)
        provider.source_path().write_text("{}")
        return result

    monkeypatch.setattr(ground, "_promotion_qualified_record_preflight", changed_source)
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert pipeline["record"].read_bytes() == before
    assert not pipeline["durable_registry"].exists()
    assert not pipeline["durable_evidence"].exists()
    assert not pipeline["durable_bindings"].exists()


@pytest.mark.parametrize("change", ["path", "missing", "key", "release"])
def test_provider_replay_rejects_consistently_rehashed_ledger_tampering(pipeline, change):
    assert ground.main(pipeline["resolve_args"]) == 0
    row = _rows(pipeline["resolved"])[0]
    proof = next(e for e in row["provider_evidence"] if e["kind"] == "iedb_peptide")
    if change == "missing":
        row["provider_evidence"].remove(proof)
    else:
        proof[{"path": "path", "key": "key", "release": "release"}[change]] = "forged"
    row["resolution_digest"] = ground._resolution_digest(row)
    _jsonl(pipeline["resolved"], [row])
    _approve(pipeline)
    approved = pipeline["approved"].read_text()
    original_digest = next(csv.DictReader(pipeline["review"].open(), delimiter="\t"))["resolution_digest"]
    pipeline["approved"].write_text(approved.replace(original_digest, row["resolution_digest"]))
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert not pipeline["durable_registry"].exists()


def test_narrow_iedb_hook_leaves_unrelated_source_database_contract_closed(pipeline):
    assert ground.main(pipeline["resolve_args"]) == 0
    evidence = _rows(pipeline["evidence"])[0]
    evidence.update(trait_id="Other:10", source_trait_id="Other:10", evidence_source="Other")
    evidence["evidence_id"] = validator.compute_evidence_id(evidence)
    findings = validator.validate_grounding_evidence(evidence, path=Path("<fixture>"), line=0)
    assert "source_database_contract_required" in {f.code for f in findings}


@pytest.mark.parametrize("control", ["\n", "\r", "\t", " ", "\x00", "\x7f"])
def test_raw_uri_controls_are_rejected_before_url_normalization(control):
    source = importlib.import_module("iedb_peptide_source")
    uri = "http://www.uniprot.org/uniprot/P12345"
    assert source.uniprot_id(control + uri) is None
    assert source.uniprot_id(uri.replace("P12345", "P12" + control + "345")) is None


def test_source_preparation_is_dry_by_default_and_idempotent(pipeline):
    source_path = provider.source_path()
    source_bytes = source_path.read_bytes()
    staged = pipeline["output"] / "reviewed_source.json"
    staged.write_bytes(source_bytes)
    source_path.unlink()
    before = pipeline["record"].read_bytes()
    args = ["iedb-prepare-source", "--snapshot", str(staged)]
    assert ground.main(args) == 0
    assert not source_path.exists()
    assert ground.main(args + ["--apply"]) == 0
    assert source_path.read_bytes() == source_bytes
    assert ground.main(args + ["--apply"]) == 0
    assert source_path.read_bytes() == source_bytes
    assert pipeline["record"].read_bytes() == before
    assert not pipeline["durable_registry"].exists()
    assert not pipeline["durable_evidence"].exists()
    assert not pipeline["durable_bindings"].exists()


@pytest.mark.parametrize("target_exists", [True, False])
def test_source_preparation_rejects_unreviewed_input_without_writing(pipeline, target_exists):
    source_path = provider.source_path()
    source_bytes = source_path.read_bytes()
    if not target_exists:
        source_path.unlink()
    staged = pipeline["output"] / "forged_source.json"
    staged.write_bytes(source_bytes.replace(b"Fixture antigen", b"Forged! antigen"))
    assert ground.main(["iedb-prepare-source", "--snapshot", str(staged), "--apply"]) != 0
    if target_exists:
        assert source_path.read_bytes() == source_bytes
    else:
        assert not source_path.exists()


def test_source_preparation_never_overwrites_a_different_existing_artifact(pipeline):
    source_path = provider.source_path()
    staged = pipeline["output"] / "reviewed_source.json"
    staged.write_bytes(source_path.read_bytes())
    source_path.write_text("another curator's source artifact")
    assert ground.main(["iedb-prepare-source", "--snapshot", str(staged), "--apply"]) != 0
    assert source_path.read_text() == "another curator's source artifact"
