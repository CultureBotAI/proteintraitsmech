"""`repair_mojibake` — undoing a UTF-8-decoded-as-cp1252 round trip (#123).

Two source dumps arrive already damaged: CAZy serves a hyphen (U+2010, bytes `E2 80 90`)
as `â€` + U+0090, and TCDB serves a non-breaking hyphen (U+2011) as `â€‘`. The seeders
copied that faithfully into records, so the fix is at the point the text enters, not on
the records.

The damage is reversible precisely because it is a pure byte round trip: re-encode by the
wrong table, decode by the right one. Everything here guards the two ways that goes wrong
— repairing text that was never damaged, and declining to repair text that was.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from yaml_emit import repair_mojibake  # noqa: E402

# the real damaged strings, written as escapes so this file holds no control characters
CAZY = "b-N\u00e2\u20ac\u0090acetyl-lactosaminidase"
TCDB = "Chondroitin Sulphate\u00e2\u20ac\u2018Gold Nanoparticle"
NOTE = "Created after Z\u00c3\u00bchlke et al."


def test_repairs_the_two_real_cases():
    assert repair_mojibake(CAZY) == "b-N\u2010acetyl-lactosaminidase"
    assert repair_mojibake(TCDB) == "Chondroitin Sulphate\u2011Gold Nanoparticle"
    assert repair_mojibake(NOTE) == "Created after Z\u00fchlke et al."


@pytest.mark.parametrize("text", [
    "b-N-acetylhexosaminidase",              # ascii
    "( \u03b2 / \u03b1 ) 8 barrel",   # Greek, correctly encoded
    "Z\u00fchlke",                     # already-correct umlaut
    "an em\u2014dash and a \u2011hyphen",   # already-correct punctuation
    "",
])
def test_leaves_undamaged_text_alone(text):
    """The repair runs over every incoming string, so a false positive corrupts data.

    It only rewrites when the re-encoded bytes are valid UTF-8, which correctly-encoded
    text is not — `ü` alone is byte `FC`, not a UTF-8 sequence.
    """
    assert repair_mojibake(text) == text


def test_repairs_run_by_run_when_good_and_bad_text_are_mixed():
    """The bug that made the first version silently do nothing.

    A CAZy definition carries correctly encoded Greek beside the damaged hyphen. Greek
    has no cp1252 byte, so a whole-string re-encode raises and an all-or-nothing repair
    returns the text unchanged — the seeder ran, the record was rewritten, and the
    mojibake was still there. GH20 is exactly that shape.
    """
    mixed = "fold: ( \u03b2 / \u03b1 ) 8 barrel. activities: " + CAZY
    out = repair_mojibake(mixed)
    assert "\u03b2" in out and "\u03b1" in out          # Greek survives
    assert "\u00e2\u20ac" not in out                    # mojibake gone
    assert out.endswith("b-N\u2010acetyl-lactosaminidase")
