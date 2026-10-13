"""Tests for repair_assembled_enzyme_notes (#1026)."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = _load("repair_assembled_enzyme_notes")
A = _load("audit_writers")


def test_registered_in_audit_writers_bypass():
    assert "repair_assembled_enzyme_notes" in A.BYPASS
    reason = A.BYPASS["repair_assembled_enzyme_notes"]
    assert "1026" in reason
    assert len(reason) > 12


def test_repair_record_text_adds_note_to_q8gbw6():
    sample_text = """identifier: GO:0047154
label: "methylmalonyl-CoA carboxytransferase activity"
canonical_examples:
- protein_id: UniProtKB:Q8GBW6
  protein_label: Methylmalonyl-CoA carboxyltransferase 12S subunit
  sequence_length: 524
  reviewed: true
  source: UNIPROT_GROUNDING
  qualification_status: QUALIFIED
  trait_occurrences:
  - evidence_source: UniProtKB
"""
    repaired, status = R.repair_record_text(sample_text, "GO:0047154")
    assert status == "repaired"
    assert repaired is not None
    assert "Assembled-enzyme context: recombinant 12S subunit" in repaired

    data = yaml.safe_load(repaired)
    ex = data["canonical_examples"][0]
    assert ex["protein_id"] == "UniProtKB:Q8GBW6"
    assert "recombinant 12S subunit catalyses the carboxyl-transfer" in ex["note"]

    # Running again on repaired text returns "already correct"
    again, status2 = R.repair_record_text(repaired, "GO:0047154")
    assert status2 == "already correct"
    assert again == repaired


def test_repair_record_text_adds_note_to_q04507():
    sample_text = """identifier: GO:0018597
label: "ammonia monooxygenase activity"
canonical_examples:
- protein_id: UniProtKB:Q04507
  protein_label: Ammonia monooxygenase alpha subunit
  sequence_length: 276
  reviewed: true
  source: UNIPROT_GROUNDING
  qualification_status: QUALIFIED
  trait_occurrences:
  - evidence_source: UniProtKB
"""
    repaired, status = R.repair_record_text(sample_text, "GO:0018597")
    assert status == "repaired"
    assert repaired is not None
    assert "Assembled-enzyme context: experimental evidence" in repaired

    data = yaml.safe_load(repaired)
    ex = data["canonical_examples"][0]
    assert ex["protein_id"] == "UniProtKB:Q04507"
    assert "measures an active multi-subunit AMO preparation" in ex["note"]

    # Running again on repaired text returns "already correct"
    again, status2 = R.repair_record_text(repaired, "GO:0018597")
    assert status2 == "already correct"
    assert again == repaired


def test_repair_record_text_missing_example():
    sample_text = """identifier: GO:0018597
label: "ammonia monooxygenase activity"
canonical_examples:
- protein_id: UniProtKB:P12345
  qualification_status: QUALIFIED
"""
    repaired, status = R.repair_record_text(sample_text, "GO:0018597")
    assert repaired is None
    assert "not found" in status


def test_repair_assembled_enzyme_notes_parser_refuses_abbreviated_flags():
    with pytest.raises(SystemExit):
        R.main(["--app"])
