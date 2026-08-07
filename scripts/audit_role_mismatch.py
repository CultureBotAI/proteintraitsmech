"""Flag records whose OWN definition names a role their curated mechanism contradicts.

The scale-safe version of a check that has so far only ever been done by reading. Three
times this session a record sat under a family whose mechanism its own definition
contradicted, and each was caught by eye:

  #251  MecI  -- a REPRESSOR carrying a target-replacement mechanism id
  #254  pilQ  -- an outer-membrane SECRETIN under "beta-lactam resistant PBPs"
  #260  ahpC  -- CARD asserting activation-loss and overexpression for one gene

Reading works at 20 records. The remaining efflux/regulator block is 565, where it does
not. This finds the same shape mechanically: a determinant whose definition says it
REGULATES something, while its curated graph says it DOES something.

Current output: 1 candidate out of 39,647 -- vanS, which on reading is CORRECT. Its
predicate is "positively regulates (phosphorylates the partner regulator)": a regulatory
act, properly typed, whose parenthetical gloss happens to contain an effector verb. That
is the expected steady state for a triage tool, not a defect to suppress -- a filter tuned
until it returns exactly zero is a filter that has been tuned to agree with itself.

Deliberately narrow. It reports candidates for a human to read, not defects -- an
antirepressor like ArmR defeated three keyword patterns before, so the output is a
shortlist, not a verdict. Exit code is always 0 for that reason.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"

# Roles that mean "this thing controls another gene's expression"...
REGULATORY = re.compile(
    r"\b(repressor|activator|transcriptional regulator|response regulator|"
    r"sensor kinase|histidine kinase|two-component|antirepressor)\b", re.I)
# ...versus edges that assert the determinant itself performs the resisting act.
#
# `enables` is deliberately ABSENT. The first version included it and flagged 74 records,
# of which the two I read were both false: "enables (represses the pump operon)" is a
# repressor correctly enabling its own REGULATORY function. `enables` is too polymorphic
# to discriminate -- it is the right predicate for both a hydrolase and a repressor.
# Same over-broad-keyword defect as #252, caught the same way: by reading before claiming.
EFFECTOR_PREDICATE = re.compile(
    r"\b(hydrolyz\w*|inactivat\w*|transport\w*|acetylat\w*|phosphorylat\w*|"
    r"molecularly interacts with)", re.I)


def own_definition(text: str) -> str:
    m = re.search(r"^definition:\s*(.*?)(?=\n\w)", text, re.M | re.S)
    return " ".join(m.group(1).split()).lstrip(">- ") if m else ""


def main() -> int:
    scanned = flagged = 0
    rows = []
    for p in sorted(TRAITS.rglob("*.yaml")):
        text = p.read_text(encoding="utf-8")
        if "causal_graphs:" not in text:
            continue
        scanned += 1
        own = own_definition(text)
        if not REGULATORY.search(own):
            continue
        # its graph asserts the determinant DOES the resisting act
        hits = [ln.strip() for ln in text.splitlines()
                if ln.strip().startswith("predicate:") and EFFECTOR_PREDICATE.search(ln)]
        if not hits:
            continue
        flagged += 1
        ident = (re.search(r"^identifier:\s*(\S+)", text, re.M) or [0, "?"])[1]
        role = REGULATORY.search(own).group(0)
        rows.append((ident, p.name, role, len(hits)))

    for ident, name, role, n in rows[:25]:
        print(f"  {ident:16} {role:24} {n:>3} effector edge(s)  {name[:52]}")
    if len(rows) > 25:
        print(f"  ... and {len(rows) - 25:,} more")
    print(f"role-mismatch audit: {scanned:,} records with graphs, "
          f"{flagged:,} flagged for reading (shortlist, not a verdict)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
