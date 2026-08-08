"""Which DRAFTS would an existing config accept, and which does one nearly accept? (#316)

Two defects this session were invisible to every gate:

  tet(34)  a draft an existing config would ACCEPT, contradicting an earlier round's
           deliberate exclusion (round 60 vs round 70's factory)
  3x gyrB  drafts a configured ancestor REFUSED for a too-narrow reason, stranded for
           34 rounds

Neither is a failure. A precondition skip is expected behaviour by design -- the vanR/vanS
configs refuse each other's records every run -- so nothing is red, nothing is missing, and
nothing draws the eye. `audit-fit` (#267) asks the inverse question about CURATED records.
Nothing was asking about drafts.

Two sections:

  ACCEPTED   a draft some config would take. Either promotion has not been run, or an
             earlier round excluded it deliberately and a later config undid that.
  REFUSED    a draft whose family IS configured. Expected in bulk -- most are genuinely
             other chemistries -- so the output is capped and sorted by family, to be
             skimmed for a family that should not be there.

Exit code is always 0. This is a reading aid, not a gate; the session that built it made
five over-broad-pattern mistakes, and a red gate here would be ignored within a week.
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import enrich_aro_resistance as E  # noqa: E402
import promote_family_drafts as P  # noqa: E402

ARO_DIR = pathlib.Path(__file__).resolve().parent.parent / "data/traits/function/resistance/aro"


def main() -> int:
    terms = E.parse_obo(E.OBO)
    accepted, refused = [], collections.Counter()
    drafts = 0
    for p in sorted(ARO_DIR.rglob("*.yaml")):
        text = p.read_text(encoding="utf-8")
        if "graph_id: resistance-draft" not in text:
            continue
        drafts += 1
        m = re.search(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', text, re.M)
        if not m:
            continue
        ident = m.group(1)
        lm = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M)
        label = lm.group(1) if lm else ""
        # ARO:3000000 is excluded: it is the root, every record has it, and the configs
        # keyed on it (resistance-by-absence, host-nutrient bypass, sequestration) are
        # mechanism-keyed with exact preconditions. Their refusals are correct and carry
        # no signal, and including them put 223 of 288 records in one meaningless bucket.
        fams = [f for f in set(E.ancestry(terms, ident))
                if f in P.FAMILY_SNIPPETS and f != "ARO:3000000"]
        if not fams:
            continue
        hit = next((f for f in fams
                    if P.config_for(f, ident, label, text) is not None), None)
        if hit:
            accepted.append((ident, label[:44], hit))
        else:
            # Report the MOST SPECIFIC configured ancestor, not an arbitrary one. The
            # first version used fams[0] and put 229 of 288 under ARO:3000000, the root
            # -- true, useless, and exactly the kind of output nobody reads twice.
            # Specificity is approximated by ancestry depth: the deepest configured
            # ancestor is the one whose config actually had a chance.
            deepest = max(fams, key=lambda f: len(E.ancestry(terms, f)))
            refused[deepest] += 1

    print(f"drafts scanned: {drafts:,}")
    print(f"\nACCEPTED by an existing config ({len(accepted)}) "
          f"-- promotion not run, or an earlier exclusion undone:")
    for ident, label, fam in accepted[:20]:
        print(f"  {ident:14} {label:46} via {fam}")
    if len(accepted) > 20:
        print(f"  ... and {len(accepted) - 20:,} more")

    print(f"\nREFUSED under a configured family ({sum(refused.values()):,}) "
          f"-- expected in bulk; skim for a family that should not be here:")
    for fam, n in refused.most_common(12):
        print(f"  {n:5}  {fam:14} {terms.get(fam, {}).get('name', '?')[:52]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
