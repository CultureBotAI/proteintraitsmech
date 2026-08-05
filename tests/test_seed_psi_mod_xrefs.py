"""PSI-MOD cross-reference parsing (#102).

PSI-MOD writes some xrefs with the WHOLE CURIE inside OBO's quoted-description
slot:

    xref: Unimod: "Unimod:162"

so the prefix is `Unimod` and the local part is the quoted string
`"Unimod:162"`. A guard meant for `Origin: "S"`-style pseudo-xrefs rejected
these too, silently dropping **all 825 Unimod lines** — and nine non-obsolete
terms had no duplicate anywhere else, so they lost their only reference.

The tests below exist in pairs: for every shape that must now be ACCEPTED there
is one that must still be REJECTED, because the fix is a narrowing of an
over-broad guard and the risk is widening it too far.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from seed_psi_mod import parse_xref  # noqa: E402


@pytest.mark.parametrize("raw,want", [
    ('Unimod: "Unimod:162"', "Unimod:162"),
    ('Unimod: "Unimod:425"', "Unimod:425"),
    ('GNOme: "GNO:G29068FM"', "GNO:G29068FM"),
    ("RESID:AA0001", "RESID:AA0001"),
    ('RESID:AA0001 "standard description"', "RESID:AA0001"),
])
def test_a_real_cross_reference_survives(raw, want):
    assert parse_xref(raw) == want


@pytest.mark.parametrize("raw", [
    'Origin: "S"',                    # the guard's original purpose
    'TermSpec: "N-term"',
    'Formula: "C 2 H 2 O 1"',
    'DiffMono: "42.010565"',
    'Comment: "see also"',
])
def test_an_internal_annotation_key_is_still_rejected(raw):
    assert parse_xref(raw) is None


def test_remap_is_rejected_even_though_its_value_is_a_valid_curie():
    """THE BUG THE FIRST DRAFT INTRODUCED. `Remap` is an internal PSI-MOD
    directive whose value happens to be a quoted CURIE:

        xref: Remap: "MOD:00599"

    Unwrapping before applying the internal-key filter rewrote the prefix to
    `MOD` and walked straight past the filter — 28 records gained MOD xrefs that
    are remapping directives, not cross-references. The filter must precede the
    unwrap, and this is the test that says so.
    """
    assert parse_xref('Remap: "MOD:00599"') is None


def test_a_quoted_non_curie_is_still_rejected():
    """The unwrap is deliberately narrow: it fires only when the quoted content
    is itself well-formed. Widening it to "strip quotes and hope" would readmit
    exactly the pseudo-xrefs the guard exists for."""
    assert parse_xref('Something: "not a curie"') is None
    assert parse_xref('Something: "S"') is None


@pytest.mark.parametrize("raw,want", [
    ('unimod: "Unimod:1"', "Unimod:1"),
    ('UniMod: "Unimod:1"', "Unimod:1"),
])
def test_prefix_casing_is_canonicalised(raw, want):
    assert parse_xref(raw) == want


def test_the_nine_terms_named_in_the_issue_have_their_reference():
    """#102 listed the nine non-obsolete terms whose only reference was lost.
    Asserted against the corpus, not the parser, because the parser being right
    and the records being stale is a distinct failure."""
    want = {"MOD:01603": "Unimod:995", "MOD:01823": "Unimod:985",
            "MOD:02100": "Unimod:1917", "MOD:02102": "Unimod:35",
            "MOD:02104": "Unimod:35", "MOD:02112": "Unimod:425",
            "MOD:02113": "Unimod:425", "MOD:02114": "Unimod:425",
            "MOD:02115": "Unimod:425"}
    traits = REPO / "data" / "traits" / "sequence"
    if not traits.is_dir():
        pytest.skip("corpus not present")
    found = {}
    for p in traits.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8")
        for mod, uni in want.items():
            if f"identifier: {mod}\n" in t:
                found[mod] = uni in t
    missing = [m for m in want if not found.get(m)]
    assert not missing, f"still missing their only reference: {missing}"
