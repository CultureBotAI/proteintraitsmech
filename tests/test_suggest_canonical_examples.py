"""Candidate-first safeguards for suggest_canonical_examples.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path


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


def test_apply_is_refused_before_profiles_are_loaded():
    assert S.main(["--apply"]) == 2
