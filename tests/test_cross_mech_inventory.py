"""Protein-first coverage does not turn discovery or generic tracks into evidence."""
import hashlib
import json
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_cross_mech_inventory as inventory  # noqa: E402


@pytest.fixture
def reference():
    sequence = "ACDEFG"
    return {"protein_id": "UniProtKB:P12345", "protein_label": "Test protein",
            "taxon_id": "NCBITaxon:9606", "taxon_label": "Homo sapiens",
            "sequence": sequence, "sequence_length": len(sequence),
            "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
            "uniprot_release": "2026_03", "reviewed": True}


def test_frame_tracks_require_same_sequence_and_release(reference):
    frame = {"P12345": {"seq": reference["sequence"], "ft": [[2, 3, "SEQ_DOMAIN"]]}}
    row = inventory.sequence_payload(reference["protein_id"], reference, frame, {"release": "2026_02"})
    assert not row["generic_features"]
    assert row["annotation_limitations"] == ["residue_frame_sequence_or_release_mismatch"]
    row = inventory.sequence_payload(reference["protein_id"], reference, frame, {"release": "2026_03"})
    assert row["generic_features"][0]["evidence_role"] == "GENERIC_ANNOTATION_NOT_TRAIT_EVIDENCE"
    assert "trait_occurrences" not in row
    frame["P12345"]["seq"] = "AAAAAA"
    assert not inventory.sequence_payload(reference["protein_id"], reference, frame, {"release": "2026_03"})["generic_features"]


def test_discovery_sequence_does_not_get_a_qualified_label():
    row = inventory.sequence_payload("UniProtKB:P12345", None,
                                     {"P12345": {"seq": "ACD", "ft": [[0, 10, "BAD"]]}},
                                     {"release": "2026_03"})
    assert row["sequence_source"] == "UniProt residue-frame discovery"
    assert not row["generic_features"]
    assert row["annotation_limitations"] == ["invalid_residue_frame_feature"]
    assert "qualification_status" not in row
    assert inventory.sequence_payload("UniProtKB:P12345-2", None, {"P12345": {"seq": "ACD"}}, {}) is None


def test_exact_entry_annotations_preserve_evidence_and_reject_uncertain_bounds(reference):
    exact = {"type": "Active site", "location": {
        "start": {"value": 2, "modifier": "EXACT"}, "end": {"value": 2, "modifier": "EXACT"}},
        "evidences": [{"evidenceCode": "ECO:0000269", "source": "PubMed", "id": "123"}]}
    uncertain = {"type": "Region", "location": {
        "start": {"value": 1, "modifier": "OUTSIDE"}, "end": {"value": 6}}}
    entry = {**reference, "entry": {"sequence": {"value": reference["sequence"]},
                                   "features": [exact, uncertain]}}
    result = inventory.add_discovery_annotations(reference["protein_id"], None, entry)
    assert result["sequence_source"] == "UniProt exact-entry discovery"
    assert len(result["generic_features"]) == 1
    assert result["generic_features"][0]["source_feature"] == exact
    assert result["annotation_limitations"] == ["uncertain_or_invalid_exact_entry_feature"]
    assert "qualification_status" not in result
    result["uniprot_release"] = "2026_02"
    result["generic_features"] = []
    inventory.add_discovery_annotations(reference["protein_id"], result, entry)
    assert not result["generic_features"]
    assert "exact_entry_sequence_or_release_mismatch" in result["annotation_limitations"]


def test_discovery_entry_loader_requires_receipt_and_exact_accession(tmp_path, reference):
    path = tmp_path / "discovery.entries.json"
    receipt = tmp_path / "discovery.receipt.json"
    row = {**reference, "entry": {"primaryAccession": "P12345", "sequence": {
        "value": reference["sequence"], "length": len(reference["sequence"])}}}
    document = {"kind": "cross-mech-uniprot-discovery-entries", "schema_version": 1,
                "uniprot_release": "2026_03", "entries": [row],
                "requested": [reference["protein_id"]], "missing": [], "unavailable": [], "responses": []}
    provenance = {key: document[key] for key in ("requested", "missing", "unavailable", "responses")}
    path.write_text(json.dumps(document))
    receipt.write_text(json.dumps({**provenance, "discovered": 1,
        "expected_release": "2026_03", "entries_sha256": inventory.digest(path)}))
    assert set(inventory.load_discovery_entries(path)) == {reference["protein_id"]}
    row["entry"]["primaryAccession"] = "Q12345"
    path.write_text(json.dumps(document))
    with pytest.raises(inventory.cm.CrossMechError, match="fetch receipt"):
        inventory.load_discovery_entries(path)
    receipt.write_text(json.dumps({**provenance, "discovered": 1,
        "expected_release": "2026_03", "entries_sha256": inventory.digest(path)}))
    with pytest.raises(inventory.cm.CrossMechError, match="identity/sequence/release"):
        inventory.load_discovery_entries(path)
    row["entry"]["primaryAccession"] = "P12345"
    document["missing"] = [reference["protein_id"]]
    path.write_text(json.dumps(document))
    receipt.write_text(json.dumps({**provenance, "missing": document["missing"], "discovered": 1,
        "expected_release": "2026_03", "entries_sha256": inventory.digest(path)}))
    with pytest.raises(inventory.cm.CrossMechError, match="close over"):
        inventory.load_discovery_entries(path)


def test_frame_rejects_unstamped_or_missing_inputs(tmp_path):
    path = tmp_path / "frame.json"
    with pytest.raises(FileNotFoundError):
        inventory.load_frame(path)
    path.write_text('{"P12345":{"seq":"ACD"}}')
    with pytest.raises(inventory.cm.CrossMechError, match="release-stamped"):
        inventory.load_frame(path)


def test_search_includes_ignored_and_hidden_records(tmp_path):
    (tmp_path / ".gitignore").write_text("ignored.yaml\n.hidden/\n")
    (tmp_path / ".hidden").mkdir()
    paths = [tmp_path / "ignored.yaml", tmp_path / ".hidden/a.yaml"]
    for path in paths:
        path.write_text("protein_id: UniProtKB:P12345\n")
    assert inventory.matching_records(tmp_path, {"UniProtKB:P12345"}) == sorted(paths)


def test_inventory_keeps_targets_and_legacy_separate(tmp_path, monkeypatch, reference):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "manifest.json").write_text("{}")
    registry = tmp_path / "registry.jsonl"
    registry.write_text(json.dumps(reference) + "\n")
    traits = tmp_path / "traits"
    traits.mkdir()
    record = {"identifier": "GO:0000001", "label": "Test trait", "trait_axis": "FUNCTION",
              "canonical_examples": [{"protein_id": reference["protein_id"]}]}
    (traits / "example.yaml").write_text(yaml.safe_dump(record))
    before = (traits / "example.yaml").read_bytes()
    mentions = [{"protein_id": protein, "mech": "a", "record_path": "data/one.yaml",
                 "pointer": "/target", "text_span": None, "role": "TARGET",
                 "relation": "target", "annotations": []}
                for protein in ["UniProtKB:P12345", "UniProtKB:P12345-2"]]
    manifest = {"mechs": [{"key": "a", "github": "owner/repo", "commit": "a" * 40}],
                "mentions_sha256": "b" * 64}
    monkeypatch.setattr(inventory.cm, "load_snapshot", lambda path: (mentions, manifest))
    monkeypatch.setattr(inventory.cm, "audit", lambda *a, **k: {
        "pairs": [], "summary": {"pairs_by_status": {}}})
    result = inventory.build(snapshot, traits, registry, None)
    rows = [json.loads(line) for line in result["protein_inventory.jsonl"].splitlines()]
    assert len(rows) == 2
    assert rows[0]["status"] == "LEGACY_EXAMPLES_ONLY"
    assert rows[0]["ptm_examples"][0]["qualification_status"] == "LEGACY_UNVERIFIED"
    assert rows[0]["ptm_examples"][0]["label"] == "Test trait"
    assert rows[1]["status"] == "DISCOVERY_ONLY" and rows[1]["sequence_key"] is None
    assert "/blob/" + "a" * 40 + "/" in rows[0]["sibling_mentions"][0]["url"]
    assert (traits / "example.yaml").read_bytes() == before
    assert inventory.build(snapshot, traits, registry, None) == result


def test_current_inactive_resolution_does_not_substitute_a_sequence(reference):
    reason = {"inactiveReasonType": "DEMERGED", "mergeDemergeTo": ["Q12345", "Q12346"]}
    receipt = {"expected_release": "2026_03", "missing": [reference["protein_id"]],
               "unavailable": [{"protein_id": reference["protein_id"],
                                "reason": "INACTIVE_ACCESSION", "inactive_reason": reason}]}
    assert inventory.discovery_resolution(reference["protein_id"], {}, receipt) == {
        "status": "INACTIVE_ACCESSION", "release": "2026_03", "inactive_reason": reason}
    assert inventory.sequence_payload(reference["protein_id"], reference, {}, {})["sequence"] == reference["sequence"]
    assert inventory.discovery_resolution("UniProtKB:Q12345", {}, receipt)["status"] == "NOT_FETCHED"
    receipt["unavailable"] = []
    assert inventory.discovery_resolution(reference["protein_id"], {}, receipt)["status"] == "NOT_RETURNED"


def test_candidate_links_are_snapshot_bound_discovery_only(tmp_path):
    path = tmp_path / "candidates.jsonl"
    row = {"candidate_id": "ug-test", "protein_id": "UniProtKB:P12345", "trait_id": "GO:0000001",
           "record_path": "data/traits/test.yaml", "qualification_status": "CANDIDATE_PROTEIN",
           "scope": "WHOLE_PROTEIN", "mapping_method": "SOURCE_ANNOTATION", "source_release": "2026_03",
           "cross_mech_provenance": {"snapshot_mentions_sha256": "a" * 64,
                                     "trait_link_origin": "UNIPROT_EXACT_ENTRY_DISCOVERY"}}
    path.write_text(json.dumps(row) + "\n")
    manifest = {"mentions_sha256": "a" * 64}
    result = inventory.discovery_candidates(path, manifest, {"UniProtKB:P12345"})
    candidate = result["UniProtKB:P12345"][0]
    assert candidate["status"] == "DISCOVERY_CANDIDATE_NOT_CANONICAL"
    assert candidate["url"].endswith("data/traits/test.yaml")
    assert "qualification_status" not in candidate
    row["qualification_status"] = "QUALIFIED"
    path.write_text(json.dumps(row) + "\n")
    with pytest.raises(inventory.cm.CrossMechError, match="does not match"):
        inventory.discovery_candidates(path, manifest, {"UniProtKB:P12345"})


def test_review_dispositions_use_native_digests_but_do_not_prove_installation(tmp_path):
    import ground_uniprot_examples as ground
    import finalize_uniprot_review_batch as finalizer

    prefix = tmp_path / "batch"
    resolved = tmp_path / "batch.resolved.jsonl"
    decisions = tmp_path / "batch.review-decisions.jsonl"
    row = {"candidate_id": "ug-test", "protein_id": "UniProtKB:P12345", "trait_id": "GO:0000001",
           "record_path": "data/traits/test.yaml", "source_namespace": "GO",
           "source_release": "2026_03", "qualification_status": "QUALIFIED"}
    row["resolution_digest"] = ground._resolution_digest(row)
    resolved.write_text(json.dumps(row) + "\n")
    decision = {"candidate_id": "ug-test", "resolution_digest": row["resolution_digest"],
                "record_key": {"trait_id": row["trait_id"], "record_path": row["record_path"]},
                "decision": "APPROVED", "primary_review_candidate_id": "ug-test",
                "reviewer": "synthetic test", "reviewed_at": "2026-10-10", "review_notes": "Test only"}
    decisions.write_text(json.dumps(decision) + "\n")
    result, inputs = inventory.review_dispositions([prefix])
    disposition = result["UniProtKB:P12345"][0]
    assert disposition["decision"] == "APPROVED"
    assert disposition["evidence_role"] == "REVIEW_DISPOSITION_NOT_INSTALLATION_PROOF"
    assert "qualification_status" not in disposition
    assert len(inputs) == 2
    row["source_release"] = "2026_02"
    resolved.write_text(json.dumps(row) + "\n")
    with pytest.raises(finalizer.FinalizationError, match="stale resolution_digest"):
        inventory.review_dispositions([prefix])


def test_rebuild_cannot_silently_drop_annotations_or_review_history(tmp_path):
    (tmp_path / "coverage.json").write_text(json.dumps({
        "uniprot_discovery_sha256": "a" * 64,
        "review_input_sha256": {"reports/b.resolved.jsonl": "b" * 64,
                               "reports/b.review-decisions.jsonl": "c" * 64}}))
    with pytest.raises(inventory.cm.CrossMechError, match="refusing to discard"):
        inventory.preserve_projection_inputs(tmp_path, set(), [])
    with pytest.raises(inventory.cm.CrossMechError, match="previous review batches"):
        inventory.preserve_projection_inputs(tmp_path, {"uniprot_discovery_sha256"}, [])
    inventory.preserve_projection_inputs(tmp_path, {"uniprot_discovery_sha256"}, [Path("reports/b")])
