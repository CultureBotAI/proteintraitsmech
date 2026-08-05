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


# --- #135: a stray backslash where BV-BRC meant a slash ---------------------------

def test_stray_backslash_before_a_letter_becomes_a_slash():
    """BV-BRC prose has `\\` where `/` was meant — the keys are adjacent.

    Determinate rather than guessed: the one affected description carries TWO, and the
    second settles the first. `tertiary\\quaternary` can only be `tertiary/quaternary`,
    so `amino acid\\nucleotide` is `amino acid/nucleotide`.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_seed_subsystems",
        pathlib.Path(__file__).resolve().parent.parent / "scripts" / "seed_seed_subsystems.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_seed_subsystems"] = mod
    spec.loader.exec_module(mod)
    fn = mod._slash_for_backslash
    assert fn("amino acid\\nucleotide sequence") == "amino acid/nucleotide sequence"
    assert fn("tertiary\\quaternary structural") == "tertiary/quaternary structural"


@pytest.mark.parametrize("text", [
    "C:\\\\Users\\\\path",        # a doubled separator, not a typo
    "ends with a backslash\\\\",
    "backslash then digit \\\\1",
    "backslash then space \\\\ x",
    "no backslash at all",
])
def test_it_only_touches_a_backslash_before_a_letter(text):
    """Scoped so it cannot rewrite a path, a separator, or a regex-looking token.

    The rule is defensible only because it is narrow: after JSON decoding, a backslash
    still followed by a letter in BV-BRC prose is a literal one, and this dump contains
    exactly two — both the typo.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_seed_subsystems2",
        pathlib.Path(__file__).resolve().parent.parent / "scripts" / "seed_seed_subsystems.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_seed_subsystems2"] = mod
    spec.loader.exec_module(mod)
    assert mod._slash_for_backslash(text) == text


# --- #139: restoring characters the SOURCE lost -----------------------------------

from lossy_text_errata import UNRESOLVED, repair as repair_lossy  # noqa: E402

FFFD = "�"


@pytest.mark.parametrize("damaged,restored", [
    ("Earth" + FFFD + "s homeostasis", "Earth’s homeostasis"),
    ("it doesn" + FFFD + "t occur", "it doesn’t occur"),
    ("acyl-CoA" + FFFD + "s, which", "acyl-CoA’s, which"),
])
def test_apostrophes(damaged, restored):
    assert repair_lossy(damaged) == restored


def test_primes_and_arrow():
    assert repair_lossy("3" + FFFD + "-5" + FFFD + " helicase") == "3′-5′ helicase"
    assert repair_lossy("The 3'" + FFFD + "5'-exonuclease") == "The 3'→5'-exonuclease"


def test_paired_quotes_only():
    """A MATCHED pair becomes quotes; a lone mark is left alone.

    That asymmetry is the safety property: an unmatched mark is far more likely to be a
    dash than an opening quote, and guessing wrong rewrites prose.
    """
    assert repair_lossy("protein with " + FFFD + "double-wing" + FFFD + " motif") == \
        "protein with “double-wing” motif"
    lone = "see " + FFFD + "The phylogenetic tree of CobN"
    assert repair_lossy(lone) == lone


def test_page_ranges_become_en_dashes():
    assert repair_lossy("109(41):16402" + FFFD + "16403") == "109(41):16402–16403"
    assert repair_lossy("PNAS, 102:1169 " + FFFD + "1174") == "PNAS, 102:1169–1174"


@pytest.mark.parametrize("damaged,restored", [
    # the two real corpus cases (#139): a word joined to an all-caps acronym. The mark
    # sits between two chemical/protein names, where a dash is the only reading.
    ("Methylglyoxal" + FFFD + "GSH hemithioacetal", "Methylglyoxal–GSH hemithioacetal"),
    ("ferredoxin" + FFFD + "NADP+ reductase", "ferredoxin–NADP+ reductase"),
    # a CamelCase second word still works — the case the rule already handled
    ("some" + FFFD + "Domain protein", "some–Domain protein"),
])
def test_word_to_capitalised_word_becomes_en_dash(damaged, restored):
    """A word before a capitalised word or acronym: the mark is a dash.

    The rule used to require a lowercase second letter, so it silently missed acronyms
    like GSH and NADP even though its own example named `Methylglyoxal<F>GSH`.
    """
    assert repair_lossy(damaged) == restored


@pytest.mark.parametrize("damaged,restored", [
    ("Hyyryl" + FFFD + "inen H", "Hyyryläinen H"),
    ("Oppeg" + FFFD + "rd C", "Oppegård C"),
    ("S" + FFFD + "rensen", "Sørensen"),
    ("Rodr" + FFFD + "guez", "Rodríguez"),
    ("Leskel" + FFFD + " S", "Leskelä S"),
])
def test_surnames_come_from_the_table_not_a_rule(damaged, restored):
    """Accented letters in names are inferred by RECOGNISING the name.

    No rule can do this — `Schw?r` is Schwär, `Mu?oz` is Muñoz, and the letter differs
    per name. A rule that guessed would write a wrong name into a curated record, which
    is worse than leaving the damage visible.
    """
    assert repair_lossy(damaged) == restored


@pytest.mark.parametrize("damaged", sorted(UNRESOLVED))
def test_names_that_are_not_confident_are_left_alone(damaged):
    """The three surnames with more than one plausible spelling stay damaged.

    Deliberate: `just audit-text` keeps counting them, so the residue is visible rather
    than quietly declared fixed.
    """
    text = "author " + damaged.replace("_", FFFD) + " et al."
    assert repair_lossy(text) == text
    assert FFFD in repair_lossy(text)


def test_undamaged_text_is_untouched():
    for s in ["plain ascii text", "already curly “quoted”", "3′-5′ helicase",
              "Hyyryläinen H", ""]:
        assert repair_lossy(s) == s
