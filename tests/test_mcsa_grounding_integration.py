"""Exercise staged MCSA support through the real central resolver and promoter."""

import copy
import csv
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
ground = importlib.import_module("ground_uniprot_examples")
provider = importlib.import_module("mcsa_native_grounding")
validator = importlib.import_module("validate_uniprot_grounding")
installed_source = importlib.import_module("test_mcsa_native_grounding").installed_source


def _jsonl(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def _rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def _approve(pipeline):
    with pipeline["review"].open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        row.update(decision="APPROVED", reviewer="Fixture curator", reviewed_at="2026-09-17",
                   review_notes="Complete native catalytic site and exact existing reference verified.")
    with pipeline["approved"].open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def pipeline(installed_source, tmp_path, monkeypatch):
    path, record, reference, _ = installed_source
    monkeypatch.setattr(ground, "REPO_ROOT", tmp_path)
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
        "schema_version": 1, "batch": "mcsa-fixture", "candidate_status": "CANDIDATE_PROTEIN",
        "trait_id": record["identifier"], "source_trait_id": record["identifier"],
        "source_namespace": "MCSA", "record_path": path, "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_ACTIVE_SITE", "protein_id": reference["protein_id"],
        "scope": "LOCALIZED", "mapping_method": "SOURCE_NATIVE_COORDINATES", "evidence_tier": "B",
        "residue_positions": [2, 4, 7], "coordinate_frame": "UNIPROT_CANONICAL",
        "evidence_source": "M-CSA", "source_release": provider.SOURCE_RELEASE,
        "uniprot_release": reference["uniprot_release"],
        "sequence_sha256": reference["sequence_sha256"],
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    result["candidate"] = candidate
    _jsonl(result["queue"], [candidate])
    result["resolve_args"] = [
        "resolve", "--providers", "protein-registry,mcsa-native", "--allow-unreceipted-inputs",
        "--queue", str(result["queue"]), "--traits", str(result["traits"]),
        "--protein-registry", str(result["source_registry"]),
        "--residue-frame", str(out / "unused-residue.json"),
        "--profiles", str(out / "unused-profiles.jsonl"),
        "--out", str(result["resolved"]), "--review", str(result["review"]),
        "--registry-out", str(result["registry"]), "--evidence-out", str(result["evidence"]),
        "--batch", "mcsa-fixture",
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
    assert row["trait_occurrence"]["residue_positions"] == [2, 4, 7]
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
    ("inheritance_path", ["MCSA:11", "MCSA:10"]), ("scope", "WHOLE_PROTEIN"),
    ("evidence_source", "InterPro"), ("source_release", "old"),
    ("source_trait_id", "MCSA:11"), ("expected_residues", "ACDEF"),
    ("residue_positions", [2, 4]), ("residue_positions", [2, 4, 6, 7]),
    ("residue_positions", [102, 104, 107]), ("evidence_source", "MCSA"),
    ("structure_id", "PDB:1abc"), ("chain_id", "A"),
    ("mapping_completeness", "COMPLETE"), ("source_residue_count", 3),
    ("mapped_residue_count", 3),
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
    assert row["trait_occurrence"]["residue_positions"] == [2, 4, 7]
    assert row["grounding_evidence"]["provider_entry_sha256"] != "f" * 64


def test_unidentified_candidate_receives_its_id_after_coordinate_resolution(pipeline):
    pipeline["candidate"].pop("candidate_id")
    pipeline["candidate"].pop("residue_positions")
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
    proof = next(e for e in row["provider_evidence"] if e["kind"] == "mcsa_native")
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


def test_narrow_mcsa_hook_leaves_unrelated_source_database_contract_closed(pipeline):
    assert ground.main(pipeline["resolve_args"]) == 0
    evidence = _rows(pipeline["evidence"])[0]
    evidence.update(trait_id="Other:10", source_trait_id="Other:10", evidence_source="Other")
    evidence["evidence_id"] = validator.compute_evidence_id(evidence)
    findings = validator.validate_grounding_evidence(evidence, path=Path("<fixture>"), line=0)
    assert "source_database_contract_required" in {f.code for f in findings}


def test_source_preparation_is_dry_by_default_and_idempotent(pipeline):
    source_path = provider.source_path()
    source_bytes = source_path.read_bytes()
    staged = pipeline["output"] / "reviewed_source.json"
    staged.write_bytes(source_bytes)
    source_path.unlink()
    before = pipeline["record"].read_bytes()
    args = ["mcsa-prepare-source", "--snapshot", str(staged)]
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
    staged.write_bytes(source_bytes.replace(b"Fixture enzyme", b"Forged! enzyme"))
    assert ground.main(["mcsa-prepare-source", "--snapshot", str(staged), "--apply"]) != 0
    if target_exists:
        assert source_path.read_bytes() == source_bytes
    else:
        assert not source_path.exists()


def test_source_preparation_never_overwrites_a_different_existing_artifact(pipeline):
    source_path = provider.source_path()
    staged = pipeline["output"] / "reviewed_source.json"
    staged.write_bytes(source_path.read_bytes())
    source_path.write_text("another curator's source artifact")
    assert ground.main(["mcsa-prepare-source", "--snapshot", str(staged), "--apply"]) != 0
    assert source_path.read_text() == "another curator's source artifact"


def test_record_meaning_change_before_resolution_cannot_reuse_a_native_fact(pipeline):
    record = yaml.safe_load(pipeline["record"].read_text())
    record["xrefs"].append("EC:9.9.9.9")
    pipeline["record"].write_text(yaml.safe_dump(record, sort_keys=False))
    assert ground.main(pipeline["resolve_args"]) == 0
    row = _rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "REJECTED"
    assert any("record meaning differs" in reason for reason in row["reasons"])


@pytest.mark.parametrize("change", ["source_alias", "trait_alias", "pdb_mapping"])
def test_only_the_exact_native_contract_can_discharge_the_mcsa_lock(pipeline, change):
    assert ground.main(pipeline["resolve_args"]) == 0
    evidence = _rows(pipeline["evidence"])[0]
    if change == "source_alias":
        evidence["evidence_source"] = "MCSA"
    elif change == "trait_alias":
        evidence.update(trait_id="M-CSA:1", source_trait_id="M-CSA:1")
    else:
        evidence.update(mapping_method="SIFTS_RESIDUE_MAPPING", provider_kind="SIFTS",
                        structure_id="PDB:1abc", chain_id="A", mapping_completeness="COMPLETE",
                        source_residue_count=3, mapped_residue_count=3)
    evidence["evidence_id"] = validator.compute_evidence_id(evidence)
    findings = validator.validate_grounding_evidence(evidence, path=Path("fixture"), line=1)
    assert "mcsa_provider_receipt_required" in {finding.code for finding in findings}


def test_failed_trait_write_restores_every_registry_and_record(pipeline, monkeypatch):
    assert ground.main(pipeline["resolve_args"]) == 0
    _approve(pipeline)
    before = pipeline["record"].read_bytes()
    source_before = provider.source_path().read_bytes()
    reached = []

    def fail_after_registries(*args, **kwargs):
        assert pipeline["durable_registry"].is_file()
        assert pipeline["durable_evidence"].is_file()
        assert pipeline["durable_bindings"].is_file()
        reached.append(True)
        raise OSError("Injected trait write failure")

    monkeypatch.setattr(ground, "write_validated_record", fail_after_registries)
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert reached == [True]
    assert pipeline["record"].read_bytes() == before
    assert provider.source_path().read_bytes() == source_before
    assert not pipeline["durable_registry"].exists()
    assert not pipeline["durable_evidence"].exists()
    assert not pipeline["durable_bindings"].exists()
