#!/usr/bin/env python3
"""Report definitions that do not read as prose, split by who can fix them (#149).

Sibling of `audit_text_quality.py`. That one checks how bytes were DECODED; this one
checks whether the resulting sentence is a sentence. Neither is a unit test: both walk
all 424k records, so they live behind a `just audit-*` recipe rather than `just test`.

WHY THIS EXISTS
---------------
`compose_definition` assembled clauses that each ended in a period and then joined them
with a space, using leads written as continuations ("and participate in"). Every
PANTHER family with a biological-process or cellular-component annotation was seeded
with a sentence beginning with a lowercase "and":

    ... modelled by the PANTHER 19.0 profile HMM PTHR36562. and localise to nucleus ...

That sat in **1,707 records**. It passed closed-mode `linkml-validate`, passed
`audit-text`, and was found by eye while measuring something else (#147). Nothing in
the repo had an opinion about whether a definition reads as English.

TWO CLASSES, AND ONLY ONE IS A DEFECT
-------------------------------------
* **composed** — `definition_source` says we assembled it. A broken sentence here is
  our bug and always fixable, so it FAILS the gate (exit 1).
* **source-derived** — text we did not compose. A curator-written InterPro/UniProt
  abstract we reproduce: `PANTHER:PTHR12465` really does contain "... part of the
  head. and related to the TATA-binding protein". Rewriting an upstream abstract is a
  curation decision, not a gate's call, so these are REPORTED and do not fail.

  READ THAT CATEGORY CAREFULLY. "We did not compose it" is not "we did not damage
  it" -- we also TRANSFORM source text, and the first full run showed the difference
  matters. 1,088 records report an empty clause, and they are our doing:
  `seed_panther.clean_abstract` strips inline `<db_xref/>` citations, so InterPro's

      This domain is usually find associated with <db_xref db="PFAM" dbkey="PF07730"/> .

  reaches the corpus as "... usually find associated with ." -- a deleted cross
  reference and a dangling preposition. Tracked separately; the gate reports it rather
  than failing because the fix belongs in the cleaner, not here.

Same reversible-vs-lossy split `audit_text_quality.py` already makes, for the same
reason: one is a bug to fix, the other a fact to decide about.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TRAITS = REPO / "data" / "traits"

_IDENT = re.compile(r"^identifier:\s*([A-Za-z0-9_.]+):", re.M)
_DEF = re.compile(r"^definition: >-\n((?:  .*\n)+)", re.M)
_DEF_INLINE = re.compile(r"^definition:[ \t]+(?!>)(.+)$", re.M)
_SRC = re.compile(r"^definition_source:[ \t]*(.*)$", re.M)
_LABEL = re.compile(r"^label:[ \t]*(.*)$", re.M)

# `definition_source` values naming something we assembled rather than quoted.
COMPOSED_MARKERS = ("composed from", "composed ", "(composed")

# A period ending one of these does not end a sentence. Without the check, 80 of the
# 82 hits on the PANTHER tree were false: "i.e. having", "subsp. japonica", "et al.
# has", "aff. pseudonarcissus", "Synechocystis sp. carboxysome". The first attempt used
# a LOOKAHEAD for the abbreviation, which tests the word AFTER the period -- the wrong
# side entirely, and it matched every one of them.
_ABBREV = frozenset("""
e.g i.e etc cf vs sp spp subsp aff al var str no fig ref approx ca pp resp
""".split())
# DIGITS ARE ALLOWED IN THE PRECEDING TOKEN, and that is not incidental: the defect
# this gate exists for ends in one. "... profile HMM PTHR36562. and localise to ..."
# has "2" immediately before the period, so a letters-only pattern matched nothing and
# the gate was blind to the exact 1,707-record bug it was written to catch. Caught by
# its own test before it shipped.
_SENTENCE_END = re.compile(r"([A-Za-z0-9.]+)\.\s+([a-z]{2,})")
# "i.e", "e.g", "U.S.A" -- letters separated by dots. Matched structurally rather than
# by listing them, and deliberately NOT matching "19.0", which really can end a
# sentence ("... the PANTHER 19.0. and localise to ...").
_DOTTED_ABBREV = re.compile(r"(?:[A-Za-z]\.)+[A-Za-z]?$")


def sentence_starts_lowercase(text: str, exempt: str = "") -> bool:
    """The #147 defect: a real sentence boundary followed by a lowercase word.

    `exempt` is source-provided text quoted verbatim inside `text` -- in practice the
    record's `label`. A boundary that falls inside it is the source's prose, not ours,
    even though the surrounding definition is composed. The one composed failure on the
    first full corpus run was exactly this: NCBIfam names a domain
    "Chloroflexota. gingipain-like propeptide domain", and the composer embeds that
    name unchanged. Failing the gate on it would have meant either rewriting a source's
    label or leaving the gate permanently red, and a red gate gets switched off.
    """
    for m in _SENTENCE_END.finditer(text):
        before = m.group(1).lower()
        if (before in _ABBREV or len(before) == 1
                or _DOTTED_ABBREV.match(before)):
            continue                       # abbreviation or an initial, not a boundary
        if exempt and m.group(0) in exempt:
            continue                       # the source's own text, quoted verbatim
        return True
    return False


CHECKS: dict[str, object] = {
    "sentence starts lowercase": sentence_starts_lowercase,
    # `clean_abstract` strips an inline <db_xref/> citation and can leave the colon
    # that introduced it: "... relevant reference:." with nothing between.
    "dangling colon-period": re.compile(r":\s*\."),
    # A clause whose list came out empty: "PANTHER protein class: ." or "localise to ."
    # WORD-BOUNDED, and that matters: without \b, "in" matched the tail of "domain",
    # so "...catalytic core domain ." was reported as an empty clause. That was most
    # of the 733 hits on the first full run.
    "empty clause": re.compile(r"\b(?:class|function|in|to|with)\b:?\s+\.(?:\s|$)"),
    # Double space inside a folded scalar means the value was assembled with a gap.
    "double space": re.compile(r"\S {2,}\S"),
}


def definition_of(text: str) -> str | None:
    m = _DEF.search(text)
    if m:
        return " ".join(m.group(1).split())
    m = _DEF_INLINE.search(text)
    return m.group(1).strip().strip('"') if m else None


def label_of(text: str) -> str:
    m = _LABEL.search(text)
    return m.group(1).strip().strip('"') if m else ""


def is_composed(text: str) -> bool:
    m = _SRC.search(text)
    if not m:
        return False
    src = m.group(1).lower()
    return any(mark in src for mark in COMPOSED_MARKERS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default=str(TRAITS))
    ap.add_argument("--list", action="store_true", help="print every affected record")
    ap.add_argument("--check", help="restrict to one check by name")
    args = ap.parse_args()

    checks = CHECKS
    if args.check:
        if args.check not in CHECKS:
            print(f"unknown check {args.check!r}; have {sorted(CHECKS)}", file=sys.stderr)
            return 2
        checks = {args.check: CHECKS[args.check]}

    root = pathlib.Path(args.path)
    composed: dict[str, collections.Counter] = {k: collections.Counter() for k in checks}
    sourced: dict[str, collections.Counter] = {k: collections.Counter() for k in checks}
    hits: list[tuple[str, str, str, pathlib.Path]] = []
    scanned = with_def = 0

    for p in root.rglob("*.yaml"):
        scanned += 1
        text = p.read_text(encoding="utf-8")
        definition = definition_of(text)
        if not definition:
            continue
        with_def += 1
        ours = is_composed(text)
        src = (_IDENT.search(text) or [0, "?"])[1]
        label = label_of(text)
        for name, check in checks.items():
            hit = (check(definition, label) if callable(check)
                   else bool(check.search(definition)))
            if hit:
                (composed if ours else sourced)[name][src] += 1
                hits.append(("composed" if ours else "source", name, src, p))

    print(f"prose-quality audit: {scanned:,} records scanned, "
          f"{with_def:,} with a definition")
    print(f"\n  {'check':<28}{'composed':>10}{'source-derived':>16}")
    for name in checks:
        c, s = sum(composed[name].values()), sum(sourced[name].values())
        print(f"  {name:<28}{c:>10,}{s:>16,}")
    for label, table in (("composed", composed), ("source-derived", sourced)):
        for name, counts in table.items():
            if counts:
                detail = "  ".join(f"{k}={v}" for k, v in counts.most_common(5))
                print(f"    [{label}] {name}: {detail}")
    if args.list:
        for kind, name, src, p in sorted(hits):
            print(f"    {kind:<10}{name:<28}{src:<14}{p.relative_to(REPO)}")

    bad = sum(sum(c.values()) for c in composed.values())
    other = sum(sum(c.values()) for c in sourced.values())
    if bad:
        print(f"\n  {bad} composed definition(s) do not read as prose — this is our "
              "text and is always fixable", file=sys.stderr)
        return 1
    tail = f" ({other} source-derived reported, not failed)" if other else ""
    print(f"\n  no composed definition fails a check{tail}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
