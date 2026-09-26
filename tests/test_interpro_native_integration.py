"""Complete native sets through real central resolution, review and promotion."""

import copy
import csv
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
ground = importlib.import_module("ground_uniprot_examples")
provider = importlib.import_module("interpro_native_grounding")
source = importlib.import_module("interpro_native_snapshot")
validator = importlib.import_module("validate_uniprot_grounding")
fixture = importlib.import_module("test_interpro_native_snapshot")
inputs = fixture.inputs


def write_rows(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def approve(pipeline):
    rows = read_rows(pipeline["resolved"])
    with pipeline["approved"].open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_id", "resolution_digest", "decision",
                                                   "reviewer", "reviewed_at", "review_notes"], delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({"candidate_id": row["candidate_id"], "resolution_digest": row["resolution_digest"],
                             "decision": "APPROVED", "reviewer": "Synthetic fixture curator",
                             "reviewed_at": "2026-09-18", "review_notes": "Complete native set checked."})


@pytest.fixture
def pipeline(inputs, tmp_path, monkeypatch, request):
    envelopes, pins, records, pairs = inputs
    ref = records["data/traits/sequence/domain/discontinuous.yaml"]["canonical_examples"][0]
    cath_path = "data/traits/structure/homologous_superfamily/cath.yaml"
    cath = fixture.record("CATH:1.10.10.1230", ref)
    cath.update(trait_axis="STRUCTURE", trait_category="STRUCT_HOMOLOGOUS_SUPERFAMILY")
    records[cath_path] = cath
    pairs.append((cath_path, ref["protein_id"]))
    snapshot = source.build_snapshot(envelopes, pins, records, pairs)
    raw = source.snapshot_bytes(snapshot)
    pin = source.sha(raw)
    name = provider.SOURCE_DIRECTORY + pin + ".json"
    monkeypatch.setattr(provider, "ROOT", tmp_path)
    monkeypatch.setattr(provider, "SOURCES", {name: (pin, tuple(sorted(pins.items())))})
    monkeypatch.setattr(ground, "REPO_ROOT", tmp_path)
    provider._load.cache_clear()
    installed = provider.source_path(name)
    installed.parent.mkdir(parents=True)
    installed.write_bytes(raw)
    trait = getattr(request, "param", "InterPro:IPR000055")
    path, record = next((p, r) for p, r in records.items() if r["identifier"] == trait)
    reference = copy.deepcopy(record["canonical_examples"][0])
    record["canonical_examples"][0].update(source="CURATOR", features=[
        {"feature_type": "DOMAIN", "start": 3, "end": 6, "note": "Preserve generic feature"}])
    record["canonical_examples"].append({"protein_id": "UniProtKB:Q12345",
                                          "protein_label": "Other existing example", "source": "CURATOR"})
    record_path = tmp_path / path
    record_path.parent.mkdir(parents=True)
    record_path.write_text(yaml.safe_dump(record, sort_keys=False))
    output = tmp_path / "staging"
    output.mkdir()
    result = {"root": tmp_path, "record": record_path, "before": copy.deepcopy(record),
              "source": name, "reference": reference, "output": output}
    for key in ("queue", "resolved", "registry", "evidence", "source_registry"):
        result[key] = output / (key + ".jsonl")
    result["review"] = output / "review.tsv"
    result["approved"] = output / "approved.tsv"
    for key in ("registry", "evidence", "bindings", "membership"):
        result["durable_" + key] = tmp_path / "durable" / (key + ".jsonl")
    write_rows(result["source_registry"], [reference])
    fact, occurrences, evidence = provider.resolve_occurrences(record, reference, path, name)
    candidate = {"schema_version": 1, "batch": "native-fixture", "candidate_status": "CANDIDATE_PROTEIN",
                 "record_path": path, "trait_axis": record["trait_axis"],
                 "trait_category": record["trait_category"], "source_namespace": trait.split(":")[0],
                 "evidence_tier": "A", "uniprot_release": reference["uniprot_release"],
                 **{k: v for k, v in occurrences[0].items() if k != "intervals"},
                 **provider.candidate_fields(evidence[0])}
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    result.update(candidate=candidate, expected_occurrences=occurrences, expected_evidence=evidence)
    write_rows(result["queue"], [candidate])
    xml = output / "interpro.xml.gz"
    xml.write_bytes(gzip.compress(b'<interprodb><interpro id="IPR000055" type="Domain" short_name="Synthetic">'
                                  b'<name>Synthetic native trait</name><abstract><p>Synthetic source definition '
                                  b'retained for comparison.</p></abstract></interpro></interprodb>'))
    source_args = ["--interpro-xml", str(xml), "--interpro-xml-sha256", source.sha(xml.read_bytes())]
    result["resolve_args"] = [
        "resolve", "--providers", "protein-registry,interpro-native", "--allow-unreceipted-inputs",
        "--queue", str(result["queue"]), "--traits", str(tmp_path / "data/traits"),
        "--protein-registry", str(result["source_registry"]), "--residue-frame", str(output / "unused.json"),
        "--profiles", str(output / "unused.jsonl"), "--out", str(result["resolved"]),
        "--review", str(result["review"]), "--registry-out", str(result["registry"]),
        "--evidence-out", str(result["evidence"]), "--batch", "native-fixture", "--replace-staging-outputs",
        *source_args,
    ]
    result["promote_args"] = [
        "promote", "--resolved", str(result["resolved"]), "--approved", str(result["approved"]),
        "--traits", str(tmp_path / "data/traits"), "--protein-registry", str(result["registry"]),
        "--evidence-registry", str(result["evidence"]),
        "--durable-protein-registry", str(result["durable_registry"]),
        "--durable-evidence-registry", str(result["durable_evidence"]),
        "--durable-qualified-record-bindings", str(result["durable_bindings"]),
        "--durable-membership-registry", str(result["durable_membership"]),
        "--enrich-existing-examples", *source_args,
    ]
    yield result
    provider._load.cache_clear()


def resolve(pipeline):
    assert ground.main(pipeline["resolve_args"]) == 0
    row = read_rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "QUALIFIED", row["reasons"]
    assert row["candidate_id"] == ground.derive_candidate_id(row)
    return row


@pytest.mark.parametrize("pipeline", ["InterPro:IPR000055", "SUPERFAMILY:SSF56519", "CATH:1.10.10.1230"],
                         indirect=True)
def test_complete_native_sets_install_separate_evidence_and_are_idempotent(pipeline):
    row = resolve(pipeline)
    assert "trait_occurrence" not in row and "grounding_evidence" not in row
    assert [o["intervals"] for o in row["trait_occurrences"]] == pipeline["candidate"]["native_locations"]
    assert len(read_rows(pipeline["evidence"])) == len(pipeline["expected_occurrences"])
    review = next(csv.DictReader(pipeline["review"].open(), delimiter="\t"))
    assert json.loads(review["native_locations"]) == pipeline["candidate"]["native_locations"]
    approve(pipeline)
    before_bytes = pipeline["record"].read_bytes()
    assert ground.main(pipeline["promote_args"]) == 0
    assert pipeline["record"].read_bytes() == before_bytes
    assert not pipeline["durable_registry"].exists()
    assert ground.main(pipeline["promote_args"] + ["--apply"]) == 0
    after = yaml.safe_load(pipeline["record"].read_text())
    before = pipeline["before"]
    assert {k: v for k, v in after.items() if k != "canonical_examples"} == {
        k: v for k, v in before.items() if k != "canonical_examples"}
    assert [e["protein_id"] for e in after["canonical_examples"]] == [e["protein_id"] for e in before["canonical_examples"]]
    assert after["canonical_examples"][1] == before["canonical_examples"][1]
    assert after["canonical_examples"][0]["features"] == before["canonical_examples"][0]["features"]
    assert after["canonical_examples"][0]["source"] == "CURATOR"
    refs, findings = validator.load_registry(pipeline["durable_registry"])
    assert not findings
    evidence = {e["evidence_id"]: e for e in read_rows(pipeline["durable_evidence"])}
    assert not validator.validate_record(after, refs, evidence_registry=evidence)
    bindings = read_rows(pipeline["durable_bindings"])
    assert len(bindings) == len(row["trait_occurrences"])
    assert {b["evidence_id"] for b in bindings} == set(evidence)
    assert {b["candidate_id"] for b in bindings} == {row["candidate_id"]}
    for binding in bindings:
        assert binding["record_sha256"] == hashlib.sha256(pipeline["record"].read_bytes()).hexdigest()
        assert binding["content_gate_projection"]["candidate"]["intervals"] == evidence[binding["evidence_id"]]["intervals"]
    frozen = {p: p.read_bytes() for p in (pipeline["record"], pipeline["durable_registry"],
                                        pipeline["durable_evidence"], pipeline["durable_bindings"])}
    assert ground.main(pipeline["promote_args"] + ["--apply"]) == 0
    assert all(p.read_bytes() == raw for p, raw in frozen.items())


@pytest.mark.parametrize("field,value", [
    ("native_locations", [[{"start": 7, "end": 190}]]),
    ("native_locations", [[{"start": 7, "end": 190}, {"start": 348, "end": 403}]]),
    ("native_location_set_sha256", "0" * 64), ("intervals", [{"start": 7, "end": 190}]),
    ("scope", "WHOLE_PROTEIN"), ("source_release", "109.0"),
    ("evidence_source", "Pfam"), ("coordinate_frame", "UNIPROT_ISOFORM"),
    ("inheritance_path", ["InterPro:IPR000055", "InterPro:IPR000001"]),
    ("structure_id", "PDB:1abc"),
])
def test_candidate_conflicts_never_produce_qualified_staging(pipeline, field, value):
    pipeline["candidate"][field] = value
    write_rows(pipeline["queue"], [pipeline["candidate"]])
    assert ground.main(pipeline["resolve_args"]) == 0
    row = read_rows(pipeline["resolved"])[0]
    assert row["qualification_status"] == "REJECTED" and row["reasons"]
    assert read_rows(pipeline["evidence"]) == []


@pytest.mark.parametrize("mutation", ["omit", "duplicate", "flatten", "drop_all", "proof", "path", "group"])
def test_rehashed_review_cannot_install_an_incomplete_or_forged_set(pipeline, mutation):
    row = resolve(pipeline)
    if mutation == "omit":
        row["trait_occurrences"].pop()
        row["grounding_evidence_rows"].pop()
    elif mutation == "duplicate":
        row["trait_occurrences"].append(copy.deepcopy(row["trait_occurrences"][0]))
        row["grounding_evidence_rows"].append(copy.deepcopy(row["grounding_evidence_rows"][0]))
    elif mutation == "flatten":
        row["trait_occurrences"][0]["intervals"] += row["trait_occurrences"].pop()["intervals"]
        row["grounding_evidence_rows"].pop()
    elif mutation == "drop_all":
        row["trait_occurrences"] = []
        row["grounding_evidence_rows"] = []
    elif mutation == "proof":
        row["provider_evidence"] = [e for e in row["provider_evidence"] if e["kind"] != "interpro_native"]
    elif mutation == "path":
        row["native_source"] = "data/grounding/interpro_native/forged.json"
    elif mutation == "group":
        row["native_locations"] = row["native_locations"][:1]
    row["candidate_id"] = ground.derive_candidate_id(row)
    row["resolution_digest"] = ground._resolution_digest(row)
    write_rows(pipeline["resolved"], [row])
    approve(pipeline)
    before = pipeline["record"].read_bytes()
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert pipeline["record"].read_bytes() == before
    assert not pipeline["durable_registry"].exists()


def test_standalone_validator_rejects_removing_a_member_from_the_installed_record(pipeline):
    resolve(pipeline)
    approve(pipeline)
    assert ground.main(pipeline["promote_args"] + ["--apply"]) == 0
    record = yaml.safe_load(pipeline["record"].read_text())
    refs, _ = validator.load_registry(pipeline["durable_registry"])
    evidence = {e["evidence_id"]: e for e in read_rows(pipeline["durable_evidence"])}
    record["canonical_examples"][0]["trait_occurrences"].pop()
    codes = {f.code for f in validator.validate_record(record, refs, evidence_registry=evidence)}
    assert "interpro_native_incomplete_location_set" in codes


def test_source_preparation_requires_registered_bytes_and_is_dry_and_idempotent(pipeline):
    path = provider.source_path(pipeline["source"])
    raw = path.read_bytes()
    staged = pipeline["output"] / "snapshot.json"
    staged.write_bytes(raw)
    path.unlink()
    args = ["interpro-native-prepare-source", "--snapshot", str(staged)]
    assert ground.main(args) == 0 and not path.exists()
    assert ground.main(args + ["--apply"]) == 0 and path.read_bytes() == raw
    assert ground.main(args + ["--apply"]) == 0 and path.read_bytes() == raw
    staged.write_bytes(raw + b" ")
    assert ground.main(args + ["--apply"]) != 0 and path.read_bytes() == raw
    path.write_text("different existing source")
    staged.write_bytes(raw)
    assert ground.main(args + ["--apply"]) != 0
    assert path.read_text() == "different existing source"


def test_source_change_during_preflight_is_caught_before_any_write(pipeline, monkeypatch):
    resolve(pipeline)
    approve(pipeline)
    original = ground._promotion_qualified_record_preflight
    before = pipeline["record"].read_bytes()

    def change(**kwargs):
        result = original(**kwargs)
        provider.source_path(pipeline["source"]).write_text("{}")
        return result

    monkeypatch.setattr(ground, "_promotion_qualified_record_preflight", change)
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert pipeline["record"].read_bytes() == before
    assert not pipeline["durable_registry"].exists()


def test_transaction_failure_restores_all_member_evidence_and_bindings(pipeline, monkeypatch):
    resolve(pipeline)
    approve(pipeline)
    before = pipeline["record"].read_bytes()
    reached = []

    def fail(*args, **kwargs):
        assert len(read_rows(pipeline["durable_evidence"])) == 2
        assert len(read_rows(pipeline["durable_bindings"])) == 2
        reached.append(True)
        raise OSError("Injected trait write failure")

    monkeypatch.setattr(ground, "write_validated_record", fail)
    assert ground.main(pipeline["promote_args"] + ["--apply"]) != 0
    assert reached == [True] and pipeline["record"].read_bytes() == before
    assert all(not pipeline["durable_" + key].exists() for key in ("registry", "evidence", "bindings"))


def test_durable_outputs_cannot_replace_the_registered_native_source(pipeline):
    resolve(pipeline)
    approve(pipeline)
    path = provider.source_path(pipeline["source"])
    before = path.read_bytes()
    args = pipeline["promote_args"] + ["--durable-evidence-registry", str(path), "--apply"]
    assert ground.main(args) != 0 and path.read_bytes() == before
    assert not pipeline["durable_registry"].exists()
