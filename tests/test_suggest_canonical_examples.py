"""Candidate-first safeguards for suggest_canonical_examples.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import suggest_canonical_examples as S  # noqa: E402


def _profile() -> dict:
    return {
        "accession": "UniProtKB:P17433",
        "name": "Transcription factor PU.1",
        "taxon": "NCBITaxon:10090",
        "taxon_label": "Mus musculus",
        "length": 272,
        "reviewed": True,
        "_traits": {"CATH:1.10.10.10", "Pfam:PF00178"},
    }


def _ranked(accession: str, taxon: str, score: float = 0.5) -> tuple[tuple, dict]:
    return (
        (score, 0.0, 0, 0),
        {"accession": accession, "taxon": taxon},
    )


def test_profile_pick_stays_evidence_tier_d_candidate():
    row = S.profile_candidate(
        _profile(),
        "CATH:1.10.10.10",
        "STRUCTURE",
        "STRUCT_HOMOLOGOUS_SUPERFAMILY",
        "data/traits/structure/example.yaml",
        0.5,
        0.25,
        2,
        8,
    )

    assert row["candidate_status"] == "PROTEIN_RESOLVED"
    assert row["qualification_status"] == "CANDIDATE_PROTEIN"
    assert row["evidence_tier"] == "D"
    assert row["scope"] == "LOCALIZED"
    assert "sequence" not in row
    assert row["candidate_id"].startswith("ug-")


def test_profile_ledger_is_deterministic(tmp_path):
    first = S.profile_candidate(
        _profile(), "Pfam:PF00178", "SEQUENCE", "SEQ_DOMAIN", "a.yaml", 0.4, 0.1, 1, 4
    )
    second = S.profile_candidate(
        _profile(), "CATH:1.10.10.10", "STRUCTURE",
        "STRUCT_HOMOLOGOUS_SUPERFAMILY", "b.yaml", 0.5, 0.2, 2, 6
    )
    out = tmp_path / "profile.jsonl"

    S.write_candidate_ledger(out, [first, second])
    before = out.read_bytes()
    S.write_candidate_ledger(out, [second, first])

    assert out.read_bytes() == before
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert [row["trait_id"] for row in rows] == sorted(row["trait_id"] for row in rows)


def test_select_ranked_carriers_includes_completion_taxa_beyond_cap():
    ranked = [
        _ranked("UniProtKB:HUMAN1", "NCBITaxon:9606", 0.9),
        _ranked("UniProtKB:MOUSE1", "NCBITaxon:10090", 0.8),
        _ranked("UniProtKB:ECOLI1", "NCBITaxon:83333", 0.7),
        _ranked("UniProtKB:YEAST1", "NCBITaxon:559292", 0.6),
        _ranked("UniProtKB:MOUSE2", "NCBITaxon:10090", 0.5),
    ]

    selected = S.select_ranked_carriers(
        ranked,
        max_examples=2,
        include_taxa={"NCBITaxon:9606", "NCBITaxon:83333", "NCBITaxon:559292"},
    )

    assert [prot["accession"] for _score, prot in selected] == [
        "UniProtKB:HUMAN1",
        "UniProtKB:MOUSE1",
        "UniProtKB:ECOLI1",
        "UniProtKB:YEAST1",
    ]


def test_select_ranked_carriers_allows_completion_taxa_without_ranked_exemplars():
    ranked = [
        _ranked("UniProtKB:MOUSE1", "NCBITaxon:10090", 0.9),
        _ranked("UniProtKB:ECOLI1", "NCBITaxon:83333", 0.8),
        _ranked("UniProtKB:MOUSE2", "NCBITaxon:10090", 0.7),
        _ranked("UniProtKB:YEAST1", "NCBITaxon:559292", 0.6),
    ]

    selected = S.select_ranked_carriers(
        ranked,
        max_examples=0,
        include_taxa={"NCBITaxon:83333", "NCBITaxon:559292"},
    )

    assert [prot["accession"] for _score, prot in selected] == [
        "UniProtKB:ECOLI1",
        "UniProtKB:YEAST1",
    ]


def test_completion_carriers_are_detected_by_taxon():
    pool = [
        {"accession": "UniProtKB:MOUSE1", "taxon": "NCBITaxon:10090"},
        {"accession": "UniProtKB:ECOLI1", "taxon": "NCBITaxon:83333"},
    ]

    assert S.has_completion_carrier(pool, {"NCBITaxon:83333"})
    assert not S.has_completion_carrier(pool, {"NCBITaxon:9606"})


def test_qualified_records_are_revisited_for_taxon_completion():
    text = """
identifier: Pfam:PF00000
canonical_examples:
  - protein_id: UniProtKB:P12345
    qualification_status: QUALIFIED
license: CC0-1.0
"""

    assert S.skip_qualified_record(text, include_taxa=set(), force=False)
    assert not S.skip_qualified_record(text, include_taxa={"NCBITaxon:83333"}, force=False)
    assert not S.skip_qualified_record(text, include_taxa=set(), force=True)


def test_apply_is_refused_before_profiles_are_loaded():
    assert S.main(["--apply"]) == 2


def test_invalid_include_taxon_is_rejected_before_profiles_are_loaded():
    with pytest.raises(SystemExit) as excinfo:
        S.main(["--include-taxon", "9606"])

    assert excinfo.value.code == 2
