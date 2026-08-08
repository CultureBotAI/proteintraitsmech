"""Canary for the refused-drafts audit (#316).

It currently reports 0 accepted, which is the correct steady state and also
indistinguishable from a broken scan. Round 68's `hydrolyz\\b` bug reported 0 while
structurally broken and was nearly shipped as "the corpus is clean", so the firing
case is pinned rather than assumed.
"""
from __future__ import annotations

import importlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
audit = importlib.import_module("audit_refused_drafts")
promote = importlib.import_module("promote_family_drafts")


def test_the_scan_finds_drafts_at_all():
    """A scan that reads no files would also report 0 accepted."""
    assert audit.ARO_DIR.is_dir()
    drafts = [p for p in audit.ARO_DIR.rglob("*.yaml")
              if "graph_id: resistance-draft" in p.read_text(encoding="utf-8")]
    assert len(drafts) > 100, "expected hundreds of drafts; a near-empty scan proves nothing"


def test_tet34_would_no_longer_be_accepted():
    """The defect that motivated this audit (#310) must stay fixed.

    tet(34) carries ARO:3000450 and describes target protection; round 70's factory
    accepted it by id until #310 added the definition check.
    """
    rec = ("identifier: ARO:3002870\n"
           "definition: >-\n  tet(34) causes the activation of Mg2+-dependent purine"
           " nucleotide synthesis, which protects the protein synthesis pathway.\n"
           "term_kind: CLASS\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000450\n"
           "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    assert promote.config_for("ARO:3000557", "ARO:3002870", "tet(34)", rec) is None


def test_the_root_is_excluded_from_refusal_reporting():
    """Including ARO:3000000 put 223 of 288 records in one meaningless bucket."""
    src = (pathlib.Path(__file__).resolve().parent.parent
           / "scripts" / "audit_refused_drafts.py").read_text(encoding="utf-8")
    assert 'f != "ARO:3000000"' in src


def test_the_audit_reports_unconfigured_families_too():
    """Round 102's ESX-5 records were under a family with no config AND no mechanism id.

    The first two sections only see records under a CONFIGURED family, so nothing pointed
    at them; finding them took a hand-written query. That is the shape of thing that gets
    run once and forgotten, so it is now a section of the recipe.
    """
    src = (pathlib.Path(__file__).resolve().parent.parent
           / "scripts" / "audit_refused_drafts.py").read_text(encoding="utf-8")
    assert "UNCONFIGURED families with drafts" in src
    assert "unconfigured = collections.Counter()" in src
