"""The role-mismatch audit's canary.

It currently reports 0 flagged records across the corpus. A probe that returns zero
proves nothing unless it can be shown to fire, so these pin both directions: the shape
it must catch (#251's MecI) and the shape it must NOT (a regulator enabling its own
regulatory function, which is correct modelling and was the first version's false hit).
"""
from __future__ import annotations

import importlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
audit = importlib.import_module("audit_role_mismatch")


def test_flags_a_repressor_asserting_a_direct_effector_act():
    """#251's shape: a repressor whose graph says it hydrolyses the drug."""
    assert audit.REGULATORY.search("MecI is a methicillin resistance repressor.")
    assert audit.EFFECTOR_PREDICATE.search("predicate: hydrolyzes the beta-lactam ring")


def test_does_not_flag_a_regulator_enabling_its_own_regulation():
    """The first version's false positive, kept as a test so it cannot come back.

    "enables (represses the pump operon)" is a repressor doing exactly what a repressor
    should. `enables` is the right predicate for both a hydrolase and a repressor, so it
    cannot discriminate and is deliberately absent from the pattern.
    """
    assert not audit.EFFECTOR_PREDICATE.search("predicate: enables (represses the pump operon)")
    assert not audit.EFFECTOR_PREDICATE.search("predicate: enables (activates the pump operon)")


def test_own_definition_ignores_inherited_prose():
    """Same rule as #253: read the record's own claim, not the whole YAML."""
    text = ("identifier: ARO:1\n"
            "definition: >-\n  A multidrug efflux pump subunit.\n"
            "drug_class_note: deactivation of repressors\n")
    assert "repressor" not in audit.own_definition(text).lower()


def test_vans_is_the_known_benign_hit():
    """The audit's one current candidate, read and found correct.

    Pinned so that if it ever stops matching, someone checks WHY rather than assuming
    the corpus got cleaner. A regulatory predicate whose gloss names phosphorylation is
    correct modelling; the audit surfaces it because the gloss contains an effector verb.
    """
    gloss = "predicate: positively regulates (phosphorylates the partner regulator)"
    assert audit.EFFECTOR_PREDICATE.search(gloss), (
        "vanS should still surface; if not, the pattern changed and needs re-reading"
    )
