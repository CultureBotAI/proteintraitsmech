#!/usr/bin/env python3
"""Re-base the `resistance -> drug` edges on CARD/ARO's own assertion.

  python3 scripts/fix_resistance_drug_edges.py            # dry run
  python3 scripts/fix_resistance_drug_edges.py --apply

THE DEFECT
----------
12,581 drug edges — 100% of that edge type — were written as
`resistance --related to--> drug` with **no `predicate_id`**, and evidenced by a
snippet about class chemistry. A sampling audit found that essentially none of
those snippets name the gene the edge is attached to; one typical case cited
generic acylation chemistry ("the beta-lactam antibiotic forms an acyl-enzyme
intermediate") as support for a drug-*spectrum* claim, which it cannot establish.

WHAT THE EVIDENCE ACTUALLY IS
-----------------------------
The claim is not unsupported — it was cited to the wrong place. **CARD asserts
it directly**, via `confers_resistance_to_antibiotic` (ARO:2000000) and
`confers_resistance_to_drug_class` (ARO:2000001). Checked against the ARO release
in `data/raw/aro/aro.obo`, every one of the 12,581 edges is asserted: 808 on the
record's own term and 11,773 on an `is_a` ancestor — the family term the variant
inherits from.

That inheritance is why the old snippets were class-level: the assertion itself
is class-level. So the fix is to cite the assertion and *say* it is inherited,
naming the term it comes from, rather than to quote a paper about the chemistry.

WHAT CHANGES PER EDGE
---------------------
- subject `resistance` -> `determinant`. ARO's subject is the gene product, not
  the phenotype; the old direction did not match the relation being asserted.
- `predicate_id` ARO:2000000 / ARO:2000001 (was absent).
- evidence -> the asserting ARO term, snippet = the **verbatim OBO relationship
  line**, notes naming the term and whether it was inherited.

The `resistance` node keeps its incoming edges (`determinant`/`mech -> resistance`)
and is grounded to GO:0046677. ARO models determinants and mechanisms but has no
term for the resistance phenotype itself, so that is the nearest real superclass
rather than an exact match, and the node description says so.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
OBO = REPO / "data" / "raw" / "aro" / "aro.obo"
ROOT = REPO / "data" / "traits" / "function" / "resistance"
CARD_URL = "https://card.mcmaster.ca/ontology/{num}"

REL_ID = {"confers_resistance_to_antibiotic": ("confers resistance to (antibiotic)",
                                               "ARO:2000000"),
          "confers_resistance_to_drug_class": ("confers resistance to (drug class)",
                                               "ARO:2000001")}
PHENO = "GO:0046677"


def parse_obo():
    rel = collections.defaultdict(list)
    parents = collections.defaultdict(list)
    names = {}
    cur = None
    for line in OBO.open(encoding="utf-8"):
        line = line.rstrip("\n")
        if line == "[Term]":
            cur = None
            continue
        m = re.match(r"^id: (ARO:\d+)$", line)
        if m:
            cur = m.group(1)
            continue
        if not cur:
            continue
        m = re.match(r"^name: (.+)$", line)
        if m:
            names[cur] = m.group(1)
        m = re.match(r"^is_a: (ARO:\d+)", line)
        if m:
            parents[cur].append(m.group(1))
        m = re.match(r"^relationship: (confers_resistance_to_\w+) (ARO:\d+)", line)
        if m and m.group(1) in REL_ID:
            rel[cur].append((m.group(1), m.group(2), line.strip()))
    return rel, parents, names


def ancestors(term, parents):
    seen, stack = set(), [term]
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(parents.get(x, []))
    return seen


def block_bounds(text):
    """(start, end) of the `causal_graphs:` block, so the rest of the record is
    written back byte-identical instead of being re-serialised."""
    m = re.search(r"^causal_graphs:\s*$", text, re.M)
    if not m:
        return None
    start = m.start()
    nxt = re.search(r"^[a-z_]+:", text[m.end():], re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return start, end


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    rel, parents, names = parse_obo()
    stat = collections.Counter()
    done = 0

    for f in sorted(ROOT.rglob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        bounds = block_bounds(text)
        if not bounds:
            continue
        start, end = bounds
        graphs = yaml.safe_load(text[start:end])["causal_graphs"]
        aro = (re.search(r"^identifier:\s*(ARO:\d+)", text, re.M) or [None, ""])[1]
        anc = ancestors(aro, parents)
        asserted = {}
        for a in anc:
            for typ, tgt, line in rel.get(a, []):
                asserted.setdefault(tgt, (a, typ, line))

        changed = False
        for g in graphs:
            nodes = {n["node_id"]: n for n in g["nodes"]}
            for n in g["nodes"]:
                if n["node_id"] == "resistance" and not n.get("grounding"):
                    n["grounding"] = PHENO
                    n["description"] = (
                        "Resistance phenotype conferred by this determinant. "
                        "Grounded to the nearest available superclass: ARO models "
                        "determinants and mechanisms but has no term for the "
                        "resistance phenotype itself.")
                    stat["resistance nodes grounded"] += 1
                    changed = True
            for e in g["edges"]:
                if e.get("subject") != "resistance" or not e.get("object", "").startswith("drug"):
                    continue
                stat["drug edges seen"] += 1
                gr = nodes.get(e["object"], {}).get("grounding")
                hit = asserted.get(gr)
                if not hit:
                    stat["left alone (no ARO assertion)"] += 1
                    continue
                src, typ, line = hit
                label, pid = REL_ID[typ]
                e["subject"] = "determinant"
                e["predicate"] = label
                e["predicate_id"] = pid
                drug = names.get(gr, gr)
                if src == aro:
                    note = (f"Asserted directly on {src} ({names.get(src, '')}) in the "
                            f"CARD/ARO release in data/raw/aro/aro.obo.")
                    stat["re-based (direct assertion)"] += 1
                else:
                    note = (f"Asserted on {src} ({names.get(src, '')}), an is_a ancestor "
                            f"of this record's {aro}; inherited by this variant. "
                            f"CARD/ARO release in data/raw/aro/aro.obo.")
                    stat["re-based (inherited from family term)"] += 1
                e["description"] = (f"CARD asserts that this determinant confers "
                                    f"resistance to {drug}.")
                e["evidence"] = [{
                    "reference": src,
                    "snippet": line,
                    "notes": note,
                }]
                changed = True

        if not changed:
            continue
        stat["records changed"] += 1
        new_block = yaml.safe_dump({"causal_graphs": graphs}, sort_keys=False,
                                   allow_unicode=True, width=100,
                                   default_flow_style=False)
        out = text[:start] + new_block + text[end:]
        if args.apply:
            f.write_text(out, encoding="utf-8")
        done += 1
        if args.limit and done >= args.limit:
            break

    for k, v in stat.most_common():
        print(f"  {k:<40} {v:>8,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
