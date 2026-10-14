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
    with pytest.raises(DL.DufLeadError, match="not an ancestor of the local origin/main"):
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


# ------------------------------------------------- grouped InterPro locations (#1078)


def _localized_frame(**overrides):
    frame = {
        "A0A000AAA1": {},
        "P12345": {},
        "A0A000AAA2": {"Pfam:PF00002": [[20, 60], [80, 120]]},
        "A0A000AAA4": {},
    }
    frame.update(overrides)
    return frame


@pytest.mark.parametrize(
    ("groups", "reason"),
    [
        ([[[20, 60]], [[80, 260]]], "INTERPRO_GROUPED_LOCATION_OUT_OF_BOUNDS"),  # past 200
        ([[[0, 60]], [[80, 120]]], "INTERPRO_GROUPED_LOCATION_OUT_OF_BOUNDS"),
        ([[[20, 60]], [[80, 121]]], "INTERPRO_GROUPED_LOCATION_NOT_IN_FLAT_MATCH"),
        ([[[20, 60], [81, 120]]], "INTERPRO_GROUPED_LOCATION_NOT_IN_FLAT_MATCH"),
        ([[[20, 60]], [["80", 120]]], "MALFORMED_INTERPRO_GROUPED_LOCATION"),
        ({"not": "a list"}, "MALFORMED_INTERPRO_GROUPED_LOCATION"),
    ],
)
def test_grouped_locations_get_flat_bounds_and_containment_checks(tmp_path, groups, reason):
    grouped = {"A0A000AAA2": {"Pfam:PF00002": groups}}
    candidates, rejected = _stage(tmp_path, frame=_localized_frame(), grouped=grouped)
    assert not [row for row in candidates if row["trait_id"] == "Pfam:PF00002"]
    assert ("UniProtKB:A0A000AAA2", reason) in {
        (row["protein_id"], row["reason"]) for row in rejected
    }


def test_a_discontinuous_grouped_location_inside_the_flat_match_is_one_candidate(tmp_path):
    grouped = {"A0A000AAA2": {"Pfam:PF00002": [[[20, 60], [80, 120]]]}}
    candidates, _ = _stage(tmp_path, frame=_localized_frame(), grouped=grouped)
    located = [row for row in candidates if row["trait_id"] == "Pfam:PF00002"]
    assert len(located) == 1
    assert located[0]["intervals"] == [{"start": 20, "end": 60}, {"start": 80, "end": 120}]


@pytest.mark.parametrize(
    ("frame", "grouped", "message"),
    [
        ({"A0A000AAA2": [[20, 60]]}, {}, "DUF InterPro frame entry for A0A000AAA2"),
        ({}, {"A0A000AAA2": [[[20, 60]]]}, "grouped DUF InterPro frame entry for A0A000AAA2"),
    ],
)
def test_non_object_frame_entries_are_errors_not_attribute_errors(
    tmp_path, frame, grouped, message
):
    with pytest.raises(DL.DufLeadError, match=message):
        _stage(tmp_path, frame=_localized_frame(**frame), grouped=grouped)


# ------------------------------------------------------------- command line (#1069)


def _traits_repo(tmp_path):
    """The audit fixture's records in a git work tree, as build_identifier_index reads."""
    traits = tmp_path / "traits"
    _fixture_audit(tmp_path)  # writes the records under tmp_path / "traits"
    _git(traits, "init", "-q")
    _git(traits, "add", "-A")
    _git(traits, "commit", "-q", "-m", "traits")
    return traits


class _Response:
    def __init__(self, url, body, release="2026_03"):
        self._url, self._body, self.status = url, body, 200
        self.headers = {"x-uniprot-release": release}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self._url

    def read(self):
        return self._body


def _uniprot_opener(calls, *, release="2026_03", length=200):
    accessions = sorted({row["uniprot_accession"] for row in ROWS})

    def opener(request, timeout):
        calls.append(request.full_url)
        results = [
            {"primaryAccession": accession, "sequence": {"value": "M" * length, "length": length}}
            for accession in accessions
        ]
        return _Response(request.full_url, json.dumps({"results": results}).encode(), release)

    return opener


def _no_network(request, timeout):
    raise AssertionError(f"unexpected network request: {request.full_url}")


@pytest.fixture
def cli(tmp_path, monkeypatch):
    repo, commit, pins = _dufmech(tmp_path, ROWS)
    monkeypatch.setattr(DL, "PINNED_COMMIT", commit)
    monkeypatch.setattr(DL, "SNAPSHOT_SHA256", pins["expected_sha256"])
    monkeypatch.setattr(DL, "MANIFEST_SHA256", pins["expected_manifest_sha256"])
    monkeypatch.setattr(DL, "default_content_gate", _Gate)
    out = tmp_path / "out"
    return {
        "repo": repo,
        "traits": _traits_repo(tmp_path),
        "out": out,
        "frame": tmp_path / "frames" / "interpro_frame.json",
        "grouped": tmp_path / "frames" / "interpro_grouped_locations.json",
    }


def _audit_argv(cli, *extra):
    return ["audit", "--dufmech-repo", str(cli["repo"]), "--traits", str(cli["traits"]),
            "--out", str(cli["out"]), *extra]


def _candidates_argv(cli, *extra, interpro_release="110.0"):
    return ["candidates", "--uniprot-release", "2026_03", "--interpro-release",
            interpro_release, "--interpro-frame", str(cli["frame"]),
            "--interpro-grouped-frame", str(cli["grouped"]), "--out", str(cli["out"]), *extra]


def _write_frames(cli, frame, grouped, release="110.0"):
    sidecar = _load("sidecar", REPO / "scripts" / "sidecar.py")
    cli["frame"].parent.mkdir(parents=True, exist_ok=True)
    cli["frame"].write_text(json.dumps(sidecar.wrap("proteins", frame, "InterPro", release)))
    cli["grouped"].write_text(json.dumps(sidecar.wrap("proteins", grouped, "InterPro", release)))


def test_cli_audit_is_a_dry_run_until_apply(cli, capsys):
    assert DL.main(_audit_argv(cli), opener=_no_network) == 0
    assert not cli["out"].exists()
    assert "dry run" in capsys.readouterr().out
    assert DL.main(_audit_argv(cli, "--apply"), opener=_no_network) == 0
    summary = json.loads((cli["out"] / "summary.json").read_text())
    assert summary["content_gate"] is True
    assert summary["snapshot"] == DL.pinned_provenance()
    assert summary["leads_by_status"]["RECORD_CONTENT_BLOCKED"] == 1
    leads = DL._read_jsonl(cli["out"] / "leads.jsonl")
    assert len(leads) == len(ROWS)


def test_cli_audit_fails_closed_with_exit_2_on_a_changed_snapshot(cli, monkeypatch, capsys):
    monkeypatch.setattr(DL, "SNAPSHOT_SHA256", "0" * 64)
    assert DL.main(_audit_argv(cli, "--apply"), opener=_no_network) == 2
    assert "ERROR: snapshot SHA-256" in capsys.readouterr().err
    assert not cli["out"].exists()


def test_cli_end_to_end_audit_discover_candidates_with_stubbed_uniprot(cli, capsys):
    assert DL.main(_audit_argv(cli, "--apply"), opener=_no_network) == 0

    # discover: the dry run plans without any request
    assert DL.main(["discover", "--uniprot-release", "2026_03", "--max-records", "10",
                    "--out", str(cli["out"])], opener=_no_network) == 0
    assert not (cli["out"] / "discovery-plan.json").exists()
    calls: list[str] = []
    assert DL.main(["discover", "--uniprot-release", "2026_03", "--max-records", "10",
                    "--out", str(cli["out"]), "--apply"], opener=_uniprot_opener(calls)) == 0
    assert len(calls) == 1 and calls[0].startswith("https://rest.uniprot.org/")
    plan = json.loads((cli["out"] / "discovery-plan.json").read_text())
    assert (cli["out"] / "accessions.txt").read_text().split() == plan["accessions"]
    receipt = json.loads((cli["out"] / "discovery.receipt.json").read_text())
    assert receipt["discovered"] == len(plan["accessions"]) and receipt["missing"] == []

    frame = {accession: {} for accession in plan["accessions"]}
    frame["A0A000AAA1"] = {"Pfam:PF00001": [[10, 50]]}
    frame["A0A000AAA2"] = {"Pfam:PF00002": [[20, 60]]}
    _write_frames(cli, frame, {})
    capsys.readouterr()
    assert DL.main(_candidates_argv(cli), opener=_no_network) == 0
    assert not (cli["out"] / "candidates.jsonl").exists()
    report = json.loads(capsys.readouterr().out.split("\ndry run")[0])
    assert report["candidates"] == 2 and report["interpro_release"] == "110.0"

    assert DL.main(_candidates_argv(cli, "--apply"), opener=_no_network) == 0
    candidates = DL._read_jsonl(cli["out"] / "candidates.jsonl")
    assert {row["protein_id"] for row in candidates} == {
        "UniProtKB:A0A000AAA1", "UniProtKB:A0A000AAA2",
    }
    assert all(row["sequence_length"] == 200 for row in candidates)
    rejected = DL._read_jsonl(cli["out"] / "rejected.jsonl")
    assert {row["reason"] for row in rejected} == {"NO_EXACT_INTERPRO_MATCH"}
    written = json.loads((cli["out"] / "candidates.summary.json").read_text())
    assert written == report


def test_cli_discover_and_candidates_refuse_an_ungated_audit(cli, capsys):
    assert DL.main(_audit_argv(cli, "--no-content-gate", "--apply"), opener=_no_network) == 0
    assert DL.main(["discover", "--uniprot-release", "2026_03", "--out", str(cli["out"]),
                    "--apply"], opener=_no_network) == 2
    assert "no-content-gate" in capsys.readouterr().err


def test_cli_discover_fails_closed_on_another_uniprot_release(cli, capsys):
    assert DL.main(_audit_argv(cli, "--apply"), opener=_no_network) == 0
    calls: list[str] = []
    assert DL.main(["discover", "--uniprot-release", "2026_03", "--out", str(cli["out"]),
                    "--apply"], opener=_uniprot_opener(calls, release="2026_04")) == 2
    assert "is not the pinned '2026_03'" in capsys.readouterr().err
    assert not (cli["out"] / "discovery-plan.json").exists()


@pytest.mark.parametrize("case", ["frame_release", "pinned_release", "uncovered"])
def test_cli_candidates_exit_2_on_release_or_coverage_failures(cli, capsys, case):
    assert DL.main(_audit_argv(cli, "--apply"), opener=_no_network) == 0
    assert DL.main(["discover", "--uniprot-release", "2026_03", "--out", str(cli["out"]),
                    "--apply"], opener=_uniprot_opener([])) == 0
    plan = json.loads((cli["out"] / "discovery-plan.json").read_text())
    frame = {accession: {} for accession in plan["accessions"]}
    if case == "uncovered":
        frame.pop(plan["accessions"][0])
    _write_frames(cli, frame, {}, release="109.0" if case == "frame_release" else "110.0")
    argv = _candidates_argv(cli, "--apply",
                            interpro_release="1.0" if case == "pinned_release" else "110.0")
    assert DL.main(argv, opener=_no_network) == 2
    expected = {
        "frame_release": "is not the pinned '110.0'",
        "pinned_release": "DUF InterPro frame release '110.0' is not the pinned '1.0'",
        "uncovered": "does not cover 1 planned accession",
    }[case]
    assert expected in capsys.readouterr().err
    assert not (cli["out"] / "candidates.jsonl").exists()
