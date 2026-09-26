"""Synthetic snapshot tests, independent of network and real source files."""

import copy
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import fetch_interpro_native as fetch  # noqa: E402
from interpro_native_groups import NativeCaptureError, digest  # noqa: E402
from test_fetch_interpro_native import Opener  # noqa: E402
from test_interpro_native_capture import paginated, synthetic_bundles  # noqa: E402
import interpro_native_snapshot as source  # noqa: E402


def record(identifier, reference):
    return {"identifier": identifier, "label": "Synthetic native trait",
            "definition": "Synthetic source definition retained for comparison.",
            "definition_source": "Synthetic source", "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DOMAIN", "term_kind": "CLASS", "mapping_status": "SEEDED",
            "license": "Synthetic fixture only", "canonical_examples": [copy.deepcopy(reference)]}


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "RAW_ROOT", tmp_path / "raw")
    natives = synthetic_bundles()
    registry = tmp_path / "registry.jsonl"
    registry.write_text("".join(json.dumps(b[4]) + "\n" for b in natives.values()))
    envelopes, pins = {}, {}
    for accession, native in natives.items():
        if accession == "P05719":
            native = paginated(native)
        plan = fetch.request_plan(registry, native[4]["protein_id"], tmp_path / "raw" / accession,
                                  release="110.0", minor="0")
        result = fetch.acquire(plan, opener=Opener(native))
        protein = native[4]["protein_id"]
        pins[protein] = result["bundle_sha256"]
        envelopes[protein] = source.capture_envelope(Path(result["output"]), pins[protein])
    records = {
        "data/traits/sequence/domain/repeated.yaml": record("InterPro:IPR000055", natives["P05719"][4]),
        "data/traits/sequence/domain/discontinuous.yaml": record("SUPERFAMILY:SSF56519", natives["Q796K8"][4]),
        "data/traits/sequence/domain/integrated.yaml": record("InterPro:IPR036138", natives["Q796K8"][4]),
    }
    pairs = [(p, r["canonical_examples"][0]["protein_id"]) for p, r in records.items()]
    return envelopes, pins, records, pairs


def check(snapshot, pins):
    raw = source.snapshot_bytes(snapshot)
    return source.verify_snapshot(raw, source.sha(raw), pins)


def reidentify(snapshot):
    payload = {k: v for k, v in snapshot.items() if k != "snapshot_id"}
    snapshot["snapshot_id"] = "interpro-native-snapshot:" + digest(payload)
    return snapshot


def test_complete_sets_preserve_independent_and_discontinuous_locations(inputs):
    before = copy.deepcopy(inputs)
    built = source.build_snapshot(*inputs)
    verified = check(built, inputs[1])
    by_trait = {s.trait_id: s for s in verified.sets.values()}
    repeated = by_trait["InterPro:IPR000055"]
    assert [x["intervals"] for x in repeated.locations] == [
        [{"start": 7, "end": 190}], [{"start": 348, "end": 403}]]
    discontinuous = by_trait["SUPERFAMILY:SSF56519"]
    assert len(discontinuous.locations) == 1
    assert discontinuous.locations[0]["intervals"] == [{"start": 59, "end": 121},
                                                       {"start": 212, "end": 341}]
    assert [x["intervals"] for x in by_trait["InterPro:IPR036138"].locations] == [
        [{"start": 59, "end": 341}]]
    assert inputs == before
    assert len(verified.sets) == 3


def test_portable_snapshot_replays_after_original_raw_directory_is_removed(inputs, tmp_path):
    built = source.build_snapshot(*inputs)
    shutil.rmtree(tmp_path / "raw")
    assert len(check(built, inputs[1]).sets) == 3


def test_exact_complete_snapshot_pin_is_independent_of_internal_digests(inputs):
    built = source.build_snapshot(*inputs)
    raw = source.snapshot_bytes(built)
    built["records"][next(iter(built["records"]))]["definition"] = "Forged replacement"
    altered = source.snapshot_bytes(reidentify(built))
    with pytest.raises(NativeCaptureError, match="independently reviewed byte checksum"):
        source.verify_snapshot(altered, source.sha(raw), inputs[1])


@pytest.mark.parametrize("mutation,match", [
    ("missing_capture", "pin coverage"),
    ("missing_raw_file", "raw-file set"),
    ("raw_body", "raw-file digest mismatch"),
    ("raw_header", "raw-file digest mismatch"),
    ("manifest", "reviewed pin"),
    ("source_pin", "source bundle pins changed"),
    ("fact_subset", "location-set fact fields"),
    ("fact_entry", "native signature entry"),
    ("record_meaning", "record meaning mismatch"),
    ("duplicate_fact", "duplicate native location set"),
    ("extra_record", "record meanings differ"),
    ("unsafe_path", "canonical and repo-relative"),
])
def test_rejects_self_consistent_outer_wrappers_with_altered_source(inputs, mutation, match):
    snapshot = source.build_snapshot(*inputs)
    envelope = snapshot["captures"]["UniProtKB:P05719"]
    fact = snapshot["facts"][0]
    if mutation == "missing_capture":
        del snapshot["captures"]["UniProtKB:P05719"]
    elif mutation == "missing_raw_file":
        del envelope["files"]["page-0000.body.json"]
    elif mutation in {"raw_body", "raw_header"}:
        key = "page-0000.body.json" if mutation == "raw_body" else "page-0000.capture.json"
        envelope["files"][key] += " "
    elif mutation == "manifest":
        envelope["bundle_json"] += " "
    elif mutation == "source_pin":
        snapshot["source_bundle_sha256"]["UniProtKB:P05719"] = "0" * 64
    elif mutation == "fact_subset":
        fact["locations"] = [{"intervals": [{"start": 7, "end": 190}]}]
    elif mutation == "fact_entry":
        fact["native_accession"] = "IPR999999"
        fact["location_set_sha256"] = digest({k: v for k, v in fact.items() if k != "location_set_sha256"})
    elif mutation == "record_meaning":
        snapshot["records"][fact["record_path"]]["definition"] += " Altered."
    elif mutation == "duplicate_fact":
        snapshot["facts"].append(copy.deepcopy(fact))
    elif mutation == "extra_record":
        snapshot["records"]["data/traits/sequence/domain/extra.yaml"] = copy.deepcopy(
            snapshot["records"][fact["record_path"]])
    elif mutation == "unsafe_path":
        fact["record_path"] = "data/traits/../elsewhere.yaml"
        fact["location_set_sha256"] = digest({k: v for k, v in fact.items() if k != "location_set_sha256"})
    with pytest.raises(NativeCaptureError, match=match):
        check(reidentify(snapshot), inputs[1])


@pytest.mark.parametrize("mutation,match", [
    ("missing_example", "already occur once"),
    ("duplicate_example", "already occur once"),
    ("sequence", "sequence differs"),
    ("taxon", "taxon_id differs"),
    ("length", "sequence_length differs"),
    ("reviewed", "reviewed differs"),
    ("definition", "incomplete record meaning"),
    ("trait", "entry missing or ambiguous"),
    ("duplicate_pair", "duplicate selected"),
])
def test_snapshot_requires_existing_exact_examples_and_record_meaning(inputs, mutation, match):
    envelopes, pins, records, pairs = copy.deepcopy(inputs)
    rec = records[pairs[0][0]]
    example = rec["canonical_examples"][0]
    if mutation == "missing_example":
        rec["canonical_examples"] = []
    elif mutation == "duplicate_example":
        rec["canonical_examples"].append(copy.deepcopy(example))
    elif mutation == "sequence":
        example["sequence"] = "A" + example["sequence"][1:]
    elif mutation == "taxon":
        example["taxon_id"] = "NCBITaxon:9606"
    elif mutation == "length":
        example["sequence_length"] += 1
    elif mutation == "reviewed":
        example["reviewed"] = False
    elif mutation in {"definition", "license"}:
        del rec[mutation]
    elif mutation == "trait":
        rec["identifier"] = "InterPro:IPR999999"
    elif mutation == "duplicate_pair":
        pairs.append(pairs[0])
    with pytest.raises(NativeCaptureError, match=match):
        source.build_snapshot(envelopes, pins, records, pairs)


def test_defensive_verified_projection_does_not_modify_source(inputs):
    built = source.build_snapshot(*inputs)
    original = source.snapshot_bytes(built)
    verified = check(built, inputs[1])
    first = next(iter(verified.sets.values()))
    first.locations[0]["intervals"][0]["start"] = 999
    assert source.snapshot_bytes(built) == original
    assert all(s.locations[0]["intervals"][0]["start"] != 999 for s in check(built, inputs[1]).sets.values())


@pytest.mark.parametrize("entry", [
    {"native_database": "prints", "native_accession": "PR00001"},
    {"native_database": "sfld", "native_accession": "SFLDF00001"},
    {"native_database": "cathgene3d", "native_accession": "G3DSA:1.10.10"},
    {"native_database": "cathgene3d", "native_accession": "1.10.10.1230"},
    {"native_database": "interpro", "native_accession": "InterPro:IPR000055"},
])
def test_no_implicit_source_alias_or_inheritance(entry):
    with pytest.raises(NativeCaptureError):
        source.canonical_trait(entry)


def test_absent_license_is_preserved_for_publication_review_not_invented(inputs):
    envelopes, pins, records, pairs = copy.deepcopy(inputs)
    for record in records.values():
        record.pop("license")
    snapshot = source.build_snapshot(envelopes, pins, records, pairs)
    verified = check(snapshot, pins)
    assert len(verified.sets) == 3
    assert all("license" not in meaning for meaning in verified.records.values())
    assert all("license" not in record for record in records.values())
    assert "license" in snapshot["scope"]
