"""Tests for the DUF discovery-lead lane (scripts/duf_leads.py).

Offline: the DUFMech checkout is a throwaway git repository under ``tmp_path``; the
trait tree, identifier index, content gate, sequences and InterPro frames are fixtures.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DL = _load("duf_leads", REPO / "scripts" / "duf_leads.py")
from ground_uniprot_examples import derive_candidate_id, derive_interpro_location_id  # noqa: E402

GIT_IDENTITY = ["-c", "user.name=duf-leads-test", "-c", "user.email=duf-leads-test"]


def _lead(pfam: str, accession: str, rank: int = 1, *, reviewed: bool = False, reasons=None):
    return {
        "annotation_score": 1.0,
        "family_members": 10,
        "length": 120,
        "organism": "Lead organism (never copied)",
        "pfam_id": pfam,
        "protein_name": "Lead name (never copied)",
        "rank": rank,
        "reviewed": reviewed,
        "selection_reasons": reasons or [DL.GAP_REASON],
        "source_url": f"https://rest.uniprot.org/uniprotkb/{accession}",
        "taxon_id": "NCBITaxon:1",
        "uniprot_accession": accession,
    }


def _encode(rows):
    raw = json.dumps(rows, indent=2).encode()
    manifest = {
        "files": {"json": {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}},
        "rows": {"total": len(rows)},
        "source": {"uniprot_releases": ["2026_03"]},
    }
    manifest_raw = json.dumps(manifest, indent=2).encode()
    return raw, manifest_raw


def _pins(raw, manifest_raw):
    return {
        "expected_sha256": hashlib.sha256(raw).hexdigest(),
        "expected_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
    }


ROWS = [
    _lead("PF00001", "A0A000AAA1", 1, reviewed=True),
    _lead("PF00001", "P12345", 2),
    _lead("PF00002", "A0A000AAA2"),
    _lead("PF00003", "A0A000AAA3"),
    _lead("PF00004", "A0A000AAA4"),
    _lead("PF00005", "A0A000AAA5"),
    _lead("PF00006", "A0A000AAA6", reasons=["traitmech_named_renamed_family"]),
]


# ------------------------------------------------------------------ snapshot


def test_verify_snapshot_accepts_pinned_bytes_and_rejects_any_change():
    raw, manifest_raw = _encode(ROWS)
    rows, manifest = DL.verify_snapshot(raw, manifest_raw, **_pins(raw, manifest_raw))
    assert len(rows) == len(ROWS) and manifest["rows"]["total"] == len(ROWS)
    with pytest.raises(DL.DufLeadError, match="snapshot SHA-256"):
        DL.verify_snapshot(raw + b" ", manifest_raw, **_pins(raw, manifest_raw))
    with pytest.raises(DL.DufLeadError, match="manifest SHA-256"):
        DL.verify_snapshot(raw, manifest_raw + b" ", **_pins(raw, manifest_raw))


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda rows: rows.append(dict(rows[0])), "duplicate lead"),
        (lambda rows: rows[0].update(pfam_id="PFX"), "invalid pfam_id"),
        (lambda rows: rows[0].update(extra=1), "unexpected fields"),
        (lambda rows: rows[0].update(uniprot_accession="not-an-acc"), "invalid accession"),
    ],
)
def test_verify_snapshot_rejects_malformed_rows(mutate, message):
    rows = json.loads(json.dumps(ROWS))
    mutate(rows)
    raw, manifest_raw = _encode(rows)
    with pytest.raises(DL.DufLeadError, match=message):
        DL.verify_snapshot(raw, manifest_raw, **_pins(raw, manifest_raw))


def test_verify_snapshot_requires_the_single_2026_03_release():
    raw, _ = _encode(ROWS)
    manifest = {
        "files": {"json": {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}},
        "rows": {"total": len(ROWS)},
        "source": {"uniprot_releases": ["2026_02", "2026_03"]},
    }
    manifest_raw = json.dumps(manifest).encode()
    with pytest.raises(DL.DufLeadError, match="single-release"):
        DL.verify_snapshot(raw, manifest_raw, **_pins(raw, manifest_raw))


def _git(repo, *args):
    return subprocess.run(
        ["git", *GIT_IDENTITY, *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _dufmech(tmp_path, rows, *, origin="https://github.com/CultureBotAI/DUFMech.git"):
    repo = tmp_path / "DUFMech"
    (repo / "data" / "worklists").mkdir(parents=True)
    raw, manifest_raw = _encode(rows)
    (repo / DL.SNAPSHOT_PATH).write_bytes(raw)
    (repo / DL.MANIFEST_PATH).write_bytes(manifest_raw)
    _git(repo, "init", "-q")
    _git(repo, "remote", "add", "origin", origin)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "freeze")
    commit = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo, commit, _pins(raw, manifest_raw)


def test_load_snapshot_reads_git_objects_at_the_pinned_commit_not_the_working_tree(tmp_path):
    repo, commit, pins = _dufmech(tmp_path, ROWS)
    (repo / DL.SNAPSHOT_PATH).write_text("[]")  # a dirty working tree is ignored
    snapshot = DL.load_snapshot(repo, commit, **pins)
    assert len(snapshot.rows) == len(ROWS)
    assert snapshot.provenance()["commit"] == commit
    assert snapshot.provenance()["snapshot_sha256"] == pins["expected_sha256"]


def test_load_snapshot_refuses_a_foreign_origin_and_an_unpublished_commit(tmp_path):
    repo, commit, pins = _dufmech(tmp_path, ROWS, origin="https://github.com/someone/fork.git")
    with pytest.raises(DL.DufLeadError, match="origin"):
        DL.load_snapshot(repo, commit, **pins)
    _git(repo, "remote", "set-url", "origin", "https://github.com/CultureBotAI/DUFMech.git")
    (repo / "extra").write_text("x")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "local only")
    local = _git(repo, "rev-parse", "HEAD")
    with pytest.raises(DL.DufLeadError, match="not on"):
        DL.load_snapshot(repo, local, **pins)
    with pytest.raises(DL.DufLeadError, match="not in"):
        DL.load_snapshot(repo, "0" * 40, **pins)


# --------------------------------------------------------------------- audit


def _record(root, rel, identifier, category, examples=None):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "identifier": identifier,
        "label": f"Domain of unknown function ({identifier})",
        "definition": "A family of uncharacterized proteins.",
        "trait_axis": "SEQUENCE",
        "trait_category": category,
    }
    if examples:
        document["canonical_examples"] = examples
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return rel


def _fixture_audit(tmp_path, *, gate=None):
    traits = tmp_path / "traits"
    index = {
        "Pfam:PF00001": [
            _record(
                traits,
                "sequence/family/pfam/a.yaml",
                "Pfam:PF00001",
                "SEQ_FAMILY",
                [{"protein_id": "UniProtKB:P12345"}],
            )
        ],
        "Pfam:PF00002": [
            _record(traits, "sequence/domain/pfam/b.yaml", "Pfam:PF00002", "SEQ_DOMAIN")
        ],
        "Pfam:PF00003": [
            _record(
                traits,
                "sequence/family/pfam/c.yaml",
                "Pfam:PF00003",
                "SEQ_FAMILY",
                [{"protein_id": "UniProtKB:Q99999", "qualification_status": "QUALIFIED"}],
            )
        ],
        "Pfam:PF00004": [
            _record(traits, "sequence/domain/pfam/d.yaml", "Pfam:PF00004", "SEQ_DOMAIN")
        ],
        "Pfam:PF00006": [
            _record(traits, "sequence/family/pfam/f.yaml", "Pfam:PF00006", "SEQ_FAMILY")
        ],
    }
    snapshot = DL.Snapshot(ROWS, {}, "c" * 40, "a" * 64, "b" * 64)
    return DL.audit(snapshot, traits_root=traits, index=index, make_gate=gate)


class _Finding:
    def __init__(self, code):
        self.code, self.severity, self.detail = code, "HARD", ""


class _Gate:
    """Hard-blocks PF00004 only; records every document it was asked about."""

    seen: list[str] = []

    def __init__(self, documents):
        _Gate.seen = sorted(document["identifier"] for document in documents)

    def evaluate(self, document):
        return (
            [_Finding("source_scope_conflict")] if document["identifier"] == "Pfam:PF00004" else []
        )


def test_audit_gives_every_lead_exactly_one_status(tmp_path):
    result = _fixture_audit(tmp_path, gate=_Gate)
    status = {(lead["trait_id"], lead["protein_id"]): lead["status"] for lead in result["leads"]}
    assert status == {
        ("Pfam:PF00001", "UniProtKB:A0A000AAA1"): "TARGET_ABSENT_FROM_TRAIT",
        ("Pfam:PF00001", "UniProtKB:P12345"): "TARGET_LEGACY_ON_TRAIT",
        ("Pfam:PF00002", "UniProtKB:A0A000AAA2"): "TARGET_ABSENT_FROM_TRAIT",
        ("Pfam:PF00003", "UniProtKB:A0A000AAA3"): "RECORD_ALREADY_QUALIFIED",
        ("Pfam:PF00004", "UniProtKB:A0A000AAA4"): "RECORD_CONTENT_BLOCKED",
        ("Pfam:PF00005", "UniProtKB:A0A000AAA5"): "TRAIT_NOT_IN_PTM",
        ("Pfam:PF00006", "UniProtKB:A0A000AAA6"): "OUT_OF_SCOPE_REASON",
    }
    # A record that already has a QUALIFIED example is never sent to the content gate.
    assert "Pfam:PF00003" not in _Gate.seen
    blocked = next(lead for lead in result["leads"] if lead["status"] == "RECORD_CONTENT_BLOCKED")
    assert blocked["content_gate_reasons"] == ["unqualifiable:record_content:source_scope_conflict"]
    summary = result["summary"]
    assert summary["target_records"] == 2
    assert summary["target_records_by_scope"] == {"LOCALIZED": 1, "WHOLE_PROTEIN": 1}
    assert summary["target_records_with_reviewed_lead"] == 1


def test_audit_scope_follows_the_record_category(tmp_path):
    leads = {lead["trait_id"]: lead for lead in _fixture_audit(tmp_path)["leads"]}
    assert leads["Pfam:PF00001"]["scope"] == "WHOLE_PROTEIN"
    assert leads["Pfam:PF00002"]["scope"] == "LOCALIZED"


def test_discovery_records_are_bounded_and_reviewed_first(tmp_path):
    leads = _fixture_audit(tmp_path)["leads"]
    assert DL.discovery_records(leads, 1) == ["Pfam:PF00001"]  # has the reviewed lead
    assert DL.discovery_records(leads, 10) == ["Pfam:PF00001", "Pfam:PF00002", "Pfam:PF00004"]
    with pytest.raises(DL.DufLeadError):
        DL.discovery_records(leads, 0)


# ---------------------------------------------------------------- candidates


def _identity(protein_id, length=200):
    return {
        "protein_id": protein_id,
        "sequence_length": length,
        "sequence_sha256": hashlib.sha256(protein_id.encode()).hexdigest(),
        "uniprot_release": "2026_03",
    }


def _stage(tmp_path, *, frame, grouped=None, sequences=None, max_records=10):
    leads = _fixture_audit(tmp_path)["leads"]
    plan = DL.discovery_plan(leads, max_records=max_records, snapshot={"commit": "c" * 40})
    if sequences is None:
        sequences = {lead["protein_id"]: _identity(lead["protein_id"]) for lead in plan["leads"]}
    return DL.candidate_rows(
        leads,
        plan,
        sequences,
        frame,
        grouped or {},
        uniprot_release="2026_03",
        interpro_release="110.0",
        frame_release="110.0",
    )


def test_whole_protein_candidates_copy_frame_coordinates_and_never_lead_identity(tmp_path):
    frame = {
        "A0A000AAA1": {"Pfam:PF00001": [[10, 50], [70, 90]], "Pfam:PF99999": [[1, 5]]},
        "P12345": {"Pfam:PF00001": [[5, 100]]},
        "A0A000AAA2": {"Pfam:PF00002": [[20, 60]]},
        "A0A000AAA4": {},  # crawled, no matches
    }
    candidates, rejected = _stage(tmp_path, frame=frame)
    by_protein = {row["protein_id"]: row for row in candidates}
    whole = by_protein["UniProtKB:A0A000AAA1"]
    assert whole["scope"] == "WHOLE_PROTEIN" and "coordinate_frame" not in whole
    assert whole["intervals"] == [{"start": 10, "end": 50}, {"start": 70, "end": 90}]
    assert whole["mapping_method"] == "INTERPRO_MATCH" and whole["source_release"] == "110.0"
    assert whole["candidate_id"] == derive_candidate_id(whole)
    assert whole["duf_lead_provenance"]["lead_status"] == "TARGET_ABSENT_FROM_TRAIT"
    assert whole["other_interpro_signatures"] == ["Pfam:PF99999"]
    assert by_protein["UniProtKB:P12345"]["other_interpro_signatures"] == []
    assert by_protein["UniProtKB:P12345"]["duf_lead_provenance"]["lead_status"] == (
        "TARGET_LEGACY_ON_TRAIT"
    )
    for row in candidates:
        # organism, label and review status come only from the release-pinned fetch
        assert not {"protein_label", "taxon_id", "taxon_label", "reviewed"} & set(row)
    localized = by_protein["UniProtKB:A0A000AAA2"]
    assert localized["scope"] == "LOCALIZED"
    assert localized["coordinate_frame"] == "UNIPROT_CANONICAL"
    assert "interpro_location_id" not in localized
    assert [row["reason"] for row in rejected] == ["NO_EXACT_INTERPRO_MATCH"]  # AAA4


def test_localized_leads_need_one_grouped_location_or_a_single_interval(tmp_path):
    frame = {
        "A0A000AAA2": {"Pfam:PF00002": [[20, 60], [80, 120]]},
        "A0A000AAA4": {"Pfam:PF00004": [[1, 30], [40, 70]]},
        "A0A000AAA1": {},
        "P12345": {},
    }
    grouped = {"A0A000AAA2": {"Pfam:PF00002": [[[20, 60]], [[80, 120]]]}}
    candidates, rejected = _stage(tmp_path, frame=frame, grouped=grouped)
    located = [row for row in candidates if row["trait_id"] == "Pfam:PF00002"]
    assert len(located) == 2
    expected = {
        derive_interpro_location_id(
            "UniProtKB:A0A000AAA2", "Pfam:PF00002", [{"start": 20, "end": 60}]
        ),
        derive_interpro_location_id(
            "UniProtKB:A0A000AAA2", "Pfam:PF00002", [{"start": 80, "end": 120}]
        ),
    }
    assert {row["interpro_location_id"] for row in located} == expected
    reasons = {(row["protein_id"], row["reason"]) for row in rejected}
    assert ("UniProtKB:A0A000AAA4", "UNGROUPED_INTERPRO_LOCATIONS") in reasons


def test_grouped_interpro_locations_bounds_and_containment(tmp_path):
    frame = {
        "A0A000AAA2": {"Pfam:PF00002": [[20, 60], [80, 120]]},
        "A0A000AAA1": {},
        "P12345": {},
        "A0A000AAA4": {},
    }
    # Out of bounds: start < 1
    grouped_bad_start = {"A0A000AAA2": {"Pfam:PF00002": [[[0, 50]]]}}
    _, rejected = _stage(tmp_path, frame=frame, grouped=grouped_bad_start)
    assert any(
        row["protein_id"] == "UniProtKB:A0A000AAA2"
        and row["reason"] == "MALFORMED_INTERPRO_GROUPED_LOCATION"
        for row in rejected
    )

    # Out of bounds: end > length (sequence length is 120)
    grouped_bad_end = {"A0A000AAA2": {"Pfam:PF00002": [[[20, 150]]]}}
    _, rejected = _stage(tmp_path, frame=frame, grouped=grouped_bad_end)
    assert any(
        row["protein_id"] == "UniProtKB:A0A000AAA2"
        and row["reason"] == "MALFORMED_INTERPRO_GROUPED_LOCATION"
        for row in rejected
    )

    # Not contained in flat intervals (1 to 15 is outside [[20, 60], [80, 120]])
    grouped_not_contained = {"A0A000AAA2": {"Pfam:PF00002": [[[1, 15]]]}}
    _, rejected = _stage(tmp_path, frame=frame, grouped=grouped_not_contained)
    assert any(
        row["protein_id"] == "UniProtKB:A0A000AAA2"
        and row["reason"] == "MALFORMED_INTERPRO_GROUPED_LOCATION"
        for row in rejected
    )

    # Non-list raw groups
    grouped_non_list = {"A0A000AAA2": {"Pfam:PF00002": "not-a-list"}}
    _, rejected = _stage(tmp_path, frame=frame, grouped=grouped_non_list)
    assert any(
        row["protein_id"] == "UniProtKB:A0A000AAA2"
        and row["reason"] == "MALFORMED_INTERPRO_GROUPED_LOCATION"
        for row in rejected
    )


def test_grouped_interpro_non_dict_entry_raises_duf_lead_error(tmp_path):
    frame = {
        "A0A000AAA2": {"Pfam:PF00002": [[20, 60], [80, 120]]},
        "A0A000AAA1": {},
        "P12345": {},
        "A0A000AAA4": {},
    }
    grouped = {"A0A000AAA2": "not-a-dict"}
    with pytest.raises(DL.DufLeadError, match="must be an object"):
        _stage(tmp_path, frame=frame, grouped=grouped)


def test_rejections_are_reported_not_guessed(tmp_path):
    frame = {
        "A0A000AAA1": {"Pfam:PF12345": [[1, 10]]},  # another signature only
        "P12345": {"Pfam:PF00001": [[150, 260]]},  # past the 200-residue sequence
        "A0A000AAA2": {"Pfam:PF00002": [[20, 60]]},
        "A0A000AAA4": {"Pfam:PF00002": [[1, 10]]},  # another record's signature
    }
    sequences = {
        protein: _identity(protein)
        for protein in ("UniProtKB:A0A000AAA1", "UniProtKB:P12345", "UniProtKB:A0A000AAA4")
    }
    candidates, rejected = _stage(tmp_path, frame=frame, sequences=sequences)
    assert candidates == []
    assert {(row["protein_id"], row["reason"]) for row in rejected} == {
        ("UniProtKB:A0A000AAA1", "NO_EXACT_INTERPRO_MATCH"),
        ("UniProtKB:P12345", "INTERPRO_INTERVAL_OUT_OF_BOUNDS"),
        ("UniProtKB:A0A000AAA2", "NOT_RETURNED_BY_PINNED_UNIPROT"),
        ("UniProtKB:A0A000AAA4", "NO_EXACT_INTERPRO_MATCH"),
    }


def test_an_incomplete_sidecar_fails_closed_instead_of_rejecting(tmp_path):
    # A canary (--limit 1) or failed crawl leaves planned accessions out of the sidecar.
    frame = {"A0A000AAA1": {"Pfam:PF00001": [[10, 50]]}}
    with pytest.raises(DL.DufLeadError, match=r"does not cover 3 planned accession"):
        _stage(tmp_path, frame=frame)


def test_staging_refuses_leads_changed_since_discovery(tmp_path):
    leads = _fixture_audit(tmp_path)["leads"]
    plan = DL.discovery_plan(leads, max_records=10, snapshot={})
    planned = {(lead["trait_id"], lead["protein_id"]) for lead in plan["leads"]}
    index = next(
        i for i, lead in enumerate(leads) if (lead["trait_id"], lead["protein_id"]) in planned
    )
    leads[index] = dict(leads[index], lead_rank=leads[index]["lead_rank"] + 1)
    with pytest.raises(DL.DufLeadError, match="changed since discovery"):
        DL.candidate_rows(
            leads,
            plan,
            {},
            {},
            {},
            uniprot_release="2026_03",
            interpro_release="110.0",
            frame_release="110.0",
        )


def test_later_stages_refuse_an_ungated_or_unpinned_audit(tmp_path):
    def write(summary):
        (tmp_path / "summary.json").write_text(json.dumps(summary), encoding="utf-8")

    write({"content_gate": True, "snapshot": DL.pinned_provenance()})
    assert DL.read_gated_summary(tmp_path)["snapshot"]["commit"] == DL.PINNED_COMMIT
    write({"content_gate": False, "snapshot": DL.pinned_provenance()})
    with pytest.raises(DL.DufLeadError, match="no-content-gate"):
        DL.read_gated_summary(tmp_path)
    write({"content_gate": True, "snapshot": dict(DL.pinned_provenance(), commit="0" * 40)})
    with pytest.raises(DL.DufLeadError, match="pinned DUFMech snapshot"):
        DL.read_gated_summary(tmp_path)


def test_release_mismatches_fail_closed(tmp_path):
    leads = _fixture_audit(tmp_path)["leads"]
    plan = DL.discovery_plan(leads, max_records=1, snapshot={})
    sequences = {lead["protein_id"]: _identity(lead["protein_id"]) for lead in plan["leads"]}
    arguments = dict(uniprot_release="2026_03", interpro_release="110.0", frame_release="109.0")
    with pytest.raises(DL.DufLeadError, match="not the pinned"):
        DL.candidate_rows(leads, plan, sequences, {}, {}, **arguments)
    stale = {key: dict(value, uniprot_release="2026_02") for key, value in sequences.items()}
    arguments["frame_release"] = "110.0"
    with pytest.raises(DL.DufLeadError, match="discovered in 2026_02"):
        DL.candidate_rows(leads, plan, stale, {"A0A000AAA1": {}}, {}, **arguments)


def test_a_plan_that_disagrees_with_the_audit_is_refused(tmp_path):
    leads = _fixture_audit(tmp_path)["leads"]
    plan = DL.discovery_plan(leads, max_records=1, snapshot={})
    plan["leads"].append({"trait_id": "Pfam:PF00002", "protein_id": "UniProtKB:Q00000"})
    with pytest.raises(DL.DufLeadError, match="plan names leads"):
        DL.candidate_rows(
            leads,
            plan,
            {},
            {},
            {},
            uniprot_release="2026_03",
            interpro_release="110.0",
            frame_release="110.0",
        )


# ------------------------------------------------------------------- recipes


def _recipe(name: str) -> str:
    text = (REPO / "justfile").read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}\b.*?(?=^\S)", text, flags=re.M | re.S)
    assert match, name
    return match.group(0)


def test_duf_resolver_recipe_pins_the_lane_sidecars_and_forbids_overrides():
    body = _recipe("resolve-duf-review-batch")
    assert "--interpro-frame data/raw/align_cache/duf-leads/interpro_frame.json" in body
    assert (
        "--interpro-grouped-frame data/raw/align_cache/duf-leads/interpro_grouped_locations.json"
        in body
    )
    assert "--interpro-frame|--interpro-frame=*|" in body
    assert "--expect-uniprot-release {{uniprot_grounding_release}}" in body
    assert "promote" not in body and "--apply" not in body


def test_duf_crawl_never_writes_the_organism_panel_frame():
    body = _recipe("fetch-duf-interpro-frame")
    assert "--out data/raw/align_cache/duf-leads/interpro_frame.json" in body
    assert "--grouped-out data/raw/align_cache/duf-leads/interpro_grouped_locations.json" in body


@pytest.mark.parametrize(
    ("recipe", "argument"),
    [
        ("fetch-duf-interpro-frame", "--out=data/raw/align_cache/interpro_frame.json"),
        ("fetch-duf-interpro-frame", "--grouped-out"),
        ("fetch-duf-interpro-frame", "--accessions"),
        ("stage-duf-candidates", "--interpro-frame=data/raw/align_cache/interpro_frame.json"),
        ("stage-duf-candidates", "--interpro-release"),
        ("stage-duf-candidates", "--uniprot-release=2026_02"),
    ],
)
def test_duf_crawl_and_staging_recipes_refuse_fixed_path_overrides(recipe, argument):
    if shutil.which("just") is None:
        pytest.skip("just is not installed")
    completed = subprocess.run(
        ["just", recipe, argument], cwd=REPO, capture_output=True, text=True, check=False
    )
    assert completed.returncode == 2
    assert "is fixed by the recipe" in completed.stderr


def test_duf_parsers_refuse_abbreviated_flags():
    with pytest.raises(SystemExit):
        DL.build_parser().parse_args(
            ["candidates", "--uniprot-release", "x", "--interpro-release", "y", "--interpro-f", "z"]
        )


def test_pinned_input_is_a_full_commit_and_sha256():
    assert re.fullmatch(r"[0-9a-f]{40}", DL.PINNED_COMMIT)
    assert re.fullmatch(r"[0-9a-f]{64}", DL.SNAPSHOT_SHA256)
    assert re.fullmatch(r"[0-9a-f]{64}", DL.MANIFEST_SHA256)


def test_discovery_receipt_must_bind_the_plan_and_cover_it(tmp_path):
    leads = _fixture_audit(tmp_path)["leads"]
    plan = DL.discovery_plan(leads, max_records=1, snapshot={})
    raw = json.dumps(plan).encode()
    sequences = {f"UniProtKB:{a}": _identity(f"UniProtKB:{a}") for a in plan["accessions"]}
    receipt = {
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "expected_release": "2026_03",
        "missing": [],
        "discovered": len(sequences),
    }
    DL.verify_discovery_receipt(receipt, raw, plan, sequences, uniprot_release="2026_03")
    with pytest.raises(DL.DufLeadError, match="does not bind"):
        DL.verify_discovery_receipt(receipt, raw + b" ", plan, sequences, uniprot_release="2026_03")
    with pytest.raises(DL.DufLeadError, match="another UniProt release"):
        DL.verify_discovery_receipt(receipt, raw, plan, sequences, uniprot_release="2026_04")
    short = dict(list(sequences.items())[:-1])
    with pytest.raises(DL.DufLeadError, match="cover exactly"):
        DL.verify_discovery_receipt(receipt, raw, plan, short, uniprot_release="2026_03")


class _FakeResponse:
    def __init__(self, url: str, body: bytes, *, release: str = "2026_03", link: str = ""):
        self.url = url
        self.body = body
        self.status = 200
        self.headers = {"x-uniprot-release": release, "link": link}

    def geturl(self) -> str:
        return self.url

    def read(self) -> bytes:
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_cli_subcommands_dry_run_apply_and_error_codes(tmp_path, monkeypatch):
    traits = tmp_path / "traits"
    _record(
        traits,
        "sequence/family/pfam/a.yaml",
        "Pfam:PF00001",
        "SEQ_FAMILY",
        [{"protein_id": "UniProtKB:P12345"}],
    )
    _record(traits, "sequence/domain/pfam/b.yaml", "Pfam:PF00002", "SEQ_DOMAIN")

    snapshot = DL.Snapshot(ROWS, {}, DL.PINNED_COMMIT, DL.SNAPSHOT_SHA256, DL.MANIFEST_SHA256)
    monkeypatch.setattr(DL, "load_snapshot", lambda repo, commit=None, **kwargs: snapshot)
    monkeypatch.setattr(DL, "default_content_gate", lambda records: _Gate(records))
    monkeypatch.setattr(
        DL.cm,
        "build_identifier_index",
        lambda root: {
            "Pfam:PF00001": ["sequence/family/pfam/a.yaml"],
            "Pfam:PF00002": ["sequence/domain/pfam/b.yaml"],
        },
    )

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    # 1. Audit dry-run: returns 0, writes nothing
    exit_code = DL.main(["audit", "--traits", str(traits), "--out", str(out_dir)])
    assert exit_code == 0
    assert not (out_dir / "leads.jsonl").exists()
    assert not (out_dir / "summary.json").exists()

    # 2. Audit apply: returns 0, writes leads.jsonl and summary.json
    exit_code = DL.main(["audit", "--traits", str(traits), "--out", str(out_dir), "--apply"])
    assert exit_code == 0
    assert (out_dir / "leads.jsonl").exists()
    assert (out_dir / "summary.json").exists()
    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["content_gate"] is True

    # 3. Discover dry-run: returns 0, opener not called, writes nothing
    opener_called = []

    def fake_opener(request, timeout=120):
        opener_called.append(request)
        return _FakeResponse(request.full_url, b"{}")

    exit_code = DL.main(
        ["discover", "--uniprot-release", "2026_03", "--out", str(out_dir)],
        opener=fake_opener,
    )
    assert exit_code == 0
    assert not opener_called
    assert not (out_dir / "discovery-plan.json").exists()

    # 4. Discover apply: returns 0, opener called, writes expected files
    def fake_opener_results(request, timeout=120):
        opener_called.append(request)
        results = [
            {"primaryAccession": "A0A000AAA1", "sequence": {"value": "M" * 120, "length": 120}},
            {"primaryAccession": "P12345", "sequence": {"value": "M" * 120, "length": 120}},
            {"primaryAccession": "A0A000AAA2", "sequence": {"value": "M" * 120, "length": 120}},
        ]
        return _FakeResponse(request.full_url, json.dumps({"results": results}).encode())

    exit_code = DL.main(
        ["discover", "--uniprot-release", "2026_03", "--out", str(out_dir), "--apply"],
        opener=fake_opener_results,
    )
    assert exit_code == 0
    assert opener_called
    assert (out_dir / "discovery-plan.json").exists()
    assert (out_dir / "accessions.txt").exists()
    assert (out_dir / "discovery.jsonl").exists()
    assert (out_dir / "discovery.receipt.json").exists()

    # Prepare InterPro frames for candidates
    frame_path = tmp_path / "interpro_frame.json"
    frame_data = {
        "_meta": {"source": "InterPro", "release": "110.0"},
        "proteins": {
            "A0A000AAA1": {"Pfam:PF00001": [[10, 50]]},
            "P12345": {"Pfam:PF00001": [[5, 50]]},
            "A0A000AAA2": {"Pfam:PF00002": [[20, 60]]},
        },
    }
    frame_path.write_text(json.dumps(frame_data), encoding="utf-8")

    grouped_path = tmp_path / "interpro_grouped_locations.json"
    grouped_data = {
        "_meta": {"source": "InterPro", "release": "110.0"},
        "proteins": {
            "A0A000AAA2": {"Pfam:PF00002": [[[20, 60]]]},
        },
    }
    grouped_path.write_text(json.dumps(grouped_data), encoding="utf-8")

    # 5. Candidates dry-run: returns 0, writes nothing
    exit_code = DL.main([
        "candidates",
        "--uniprot-release",
        "2026_03",
        "--interpro-release",
        "110.0",
        "--interpro-frame",
        str(frame_path),
        "--interpro-grouped-frame",
        str(grouped_path),
        "--out",
        str(out_dir),
    ])
    assert exit_code == 0
    assert not (out_dir / "candidates.jsonl").exists()

    # 6. Candidates apply: returns 0, writes candidates.jsonl, rejected.jsonl, candidates.summary.json
    exit_code = DL.main([
        "candidates",
        "--uniprot-release",
        "2026_03",
        "--interpro-release",
        "110.0",
        "--interpro-frame",
        str(frame_path),
        "--interpro-grouped-frame",
        str(grouped_path),
        "--out",
        str(out_dir),
        "--apply",
    ])
    assert exit_code == 0
    assert (out_dir / "candidates.jsonl").exists()
    assert (out_dir / "rejected.jsonl").exists()
    assert (out_dir / "candidates.summary.json").exists()

    # 7. Error cases return exit code 2
    # Missing repo for audit
    monkeypatch.undo()
    err_code = DL.main(["audit", "--dufmech-repo", str(tmp_path / "nonexistent")])
    assert err_code == 2

    # Ungated summary for discover
    (out_dir / "summary.json").write_text(json.dumps({"content_gate": False}), encoding="utf-8")
    err_code = DL.main(["discover", "--uniprot-release", "2026_03", "--out", str(out_dir)])
    assert err_code == 2

    # Frame release mismatch for candidates
    frame_data["_meta"]["release"] = "109.0"
    frame_path.write_text(json.dumps(frame_data), encoding="utf-8")
    err_code = DL.main([
        "candidates",
        "--uniprot-release",
        "2026_03",
        "--interpro-release",
        "110.0",
        "--interpro-frame",
        str(frame_path),
        "--interpro-grouped-frame",
        str(grouped_path),
        "--out",
        str(out_dir),
    ])
    assert err_code == 2


def test_load_frame_rejects_incomplete_sidecars(tmp_path: pathlib.Path):
    p = tmp_path / "frame.json"
    # complete: False
    p.write_text(json.dumps({
        "_meta": {"source": "InterPro", "complete": False, "count": 1, "targets": 10},
        "proteins": {"P12345": {}},
    }), encoding="utf-8")
    with pytest.raises(DL.DufLeadError, match="incomplete"):
        DL._load_frame(p, "InterPro frame")

    # count < targets
    p.write_text(json.dumps({
        "_meta": {"source": "InterPro", "complete": True, "count": 1, "targets": 2},
        "proteins": {"P12345": {}},
    }), encoding="utf-8")
    with pytest.raises(DL.DufLeadError, match="incomplete"):
        DL._load_frame(p, "InterPro frame")


