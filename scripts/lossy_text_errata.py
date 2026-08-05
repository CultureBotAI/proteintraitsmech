#!/usr/bin/env python3
"""Restore characters that upstream sources lost to U+FFFD (#139).

DIFFERENT FROM `yaml_emit.repair_mojibake`, AND THE DIFFERENCE IS THE POINT
---------------------------------------------------------------------------
Mojibake is UTF-8 read as cp1252 — a pure byte round trip, so it is *reversible*: encode
by the wrong table, decode by the right one, and the original character comes back. No
judgement involved.

U+FFFD is **lossy**. The bytes are already gone when the text reaches us; a re-fetch of
BV-BRC confirmed the damage is upstream, not ours. So nothing can decode it back and every
replacement here is an *inference from context*, which is why they are written down
explicitly rather than derived by a rule that looks clever.

362 occurrences across 97 records. They fall into two kinds:

* **typographic** — apostrophes, primes, quotes, en dashes, hyphens. Inferable from the
  characters either side with high confidence, so these are rules.
* **accented letters in author surnames** — inferable only by recognising the name, so
  these are an explicit table. A rule that guessed at them would write a wrong name into a
  curated record, which is worse than leaving the U+FFFD visible.

ANYTHING NOT COVERED IS LEFT ALONE. `just audit-text` still counts it, so the residue
stays visible rather than being quietly declared fixed.
"""

from __future__ import annotations

import re

FFFD = "�"

# Author surnames as they appear in the cited literature. Each key is the damaged form
# with FFFD written as `_`; each value is the restored word. Only names that are
# unambiguous in their citation context are listed — see UNRESOLVED at the bottom.
SURNAMES = {
    "Hyyryl_inen": "Hyyryläinen",     # Finnish; B. subtilis secretion literature
    "Wahlstr_m": "Wahlström",
    "K_ster": "Köster",
    "K_hler": "Köhler",
    "Schw_r": "Schwär",
    "Oppeg_rd": "Oppegård",           # Norwegian; bacteriocin structure papers
    "S_rensen": "Sørensen",
    "H_chard": "Héchard",             # French; class IIa bacteriocin literature
    "Pr_vost": "Prévost",
    "Lund_n": "Lundén",
    "Cr_cy": "Crécy",                 # de Crécy-Lagard, comparative genomics
    "Mr_zek": "Mrázek",
    "M_nck": "Münck",                 # Eckard Münck, Fe-S spectroscopy
    "Calder_n": "Calderón",
    "G_mez": "Gómez",
    "Garc_a": "García",
    "Rodr_guez": "Rodríguez",
    "Mu_oz": "Muñoz",
    "Ca_as": "Cañas",
    "Quino_es": "Quiñones",
    "A_nsa": "Aínsa",                 # Aínsa, mycobacterial transporters
    # these two are followed by a space, so the "accented letter mid-word" survey missed
    # them; found only in the residue after the first pass
    "Leskel_ ": "Leskelä ",           # Finnish; B. subtilis secretion, with Hyyryläinen
    "Massengo-Tiass_ ": "Massengo-Tiassé ",
}

# Damaged forms whose restoration is NOT confident enough to write into a record.
# Left as U+FFFD deliberately; `just audit-text` keeps counting them.
UNRESOLVED = {
    "H_chler",     # Hächler / Höchler / Hüchler all plausible
    "M_rtl",       # Märtl / Mörtl
    "Cu_v",        # likely Ó Cuív, but the given-name context is missing
}

# Specific strings whose restoration is unambiguous but which no general rule catches.
LITERALS = {
    "C_est": "C’est",                       # "Plus Ca Change de Plus C'est la Meme Chose"
    "plastoquinol_plastocyanin": "plastoquinol–plastocyanin",
    "TPP _dependent": "TPP-dependent",
}

_APOSTROPHE = re.compile(rf"([A-Za-z])\{FFFD}(s|t|re|ve|ll|d)\b")
_PRIME = re.compile(rf"([35])\{FFFD}")
# a page range, with or without a space before the mark: `1169 <F>1174`
_RANGE_DASH = re.compile(rf"([0-9]) ?\{FFFD}([0-9])")
_ARROW = re.compile(rf"([0-9]')\{FFFD}([0-9]')")
_CHEM_HYPHEN = re.compile(rf"([0-9]),?([0-9])?\{FFFD}([a-z])")
_SPACED_DASH = re.compile(rf" \{FFFD} ")
_WORD_DASH = re.compile(rf"([A-Za-z]{{2,}})\{FFFD}([A-Z][a-z])")


def repair(text: str) -> str:
    """Restore what can be inferred; leave the rest as U+FFFD.

    Order matters: the specific patterns run before the general ones, so a prime in
    `3<FFFD>-5<FFFD>` is not first eaten by the range-dash rule.
    """
    if FFFD not in text:
        return text

    for damaged, restored in LITERALS.items():
        text = text.replace(damaged.replace("_", FFFD), restored)

    for damaged, restored in SURNAMES.items():
        text = text.replace(damaged.replace("_", FFFD), restored)

    text = _ARROW.sub(r"\1→\2", text)              # 3'<F>5' -> 3'->5'
    text = _APOSTROPHE.sub(r"\1’\2", text)         # Earth<F>s -> Earth's
    text = _PRIME.sub(r"\1′", text)                # 3<F>-5<F> -> 3'-5'
    text = _RANGE_DASH.sub(r"\1–\2", text)         # 16402<F>16403 -> en dash
    text = _CHEM_HYPHEN.sub(
        lambda m: f"{m.group(1)}{m.group(2) or ''}-{m.group(3)}", text)
    text = _WORD_DASH.sub(r"\1–\2", text)          # Methylglyoxal<F>GSH
    text = _curly_quotes(text)
    text = _SPACED_DASH.sub("—", text)             # clause dash, spaced
    return text


_QUOTE_PAIR = re.compile(
    rf"(?<=[\s(])\{FFFD}([^\{FFFD}\n]{{1,80}}?)\{FFFD}(?=[\s,.;)])")


def _curly_quotes(text: str) -> str:
    """Restore a matched pair of quotes around a short phrase.

    Only rewrites when BOTH marks are present on the same line with plausible text
    between them, so a lone U+FFFD that merely looks like an opening quote is left for
    a human. That pairing requirement is what makes this safe to apply blind: an
    unmatched mark is far more likely to be a dash than a quote.
    """
    return _QUOTE_PAIR.sub(lambda m: f"\u201c{m.group(1)}\u201d", text)
