#!/usr/bin/env python3
"""Give the 1,219 resistance drafts' edges a verbatim snippet from ARO.

  python3 scripts/cite_resistance_draft_edges.py            # dry run
  python3 scripts/cite_resistance_draft_edges.py --apply

4,117 edges — every one of them in a `resistance-draft` graph — carry a CARD
literature `reference` (a DOI or PMID) but **no snippet**, because nobody has
read those papers. Round 11 called these the un-batchable tail and stopped, which
was right for *promotion*: their mechanisms genuinely differ and no family config
fits them.

Citation is a different problem from promotion, and it is batchable, because ARO
already states in prose what each of the three edge shapes claims. Each edge gains
a second `EvidenceItem` quoting the relevant ARO definition verbatim. The existing
DOI/PMID item is kept, not replaced — it is CARD's own literature pointer and
still the thing a curator should read when promoting the draft.

WHAT BACKS WHICH EDGE
---------------------
`mech -> resistance`   the mechanism class definition, which states the causal
                       link directly: "Enzymatic inactivation of antibiotic to
                       confer drug resistance." (ARO:0001004)

`determinant -> resistance`
                       the `confers_resistance_to_*` relationship line already
                       used for the drug edges — ARO asserting this determinant
                       confers resistance. Falls back to the determinant's own
                       definition where no such line exists.

`determinant -> mech`  the determinant's ARO definition, which describes how it
                       works. **This one is labelled honestly**: the mechanism
                       class is CARD's categorisation of the determinant and
                       `aro.obo` does not assert it as an is_a axiom — checked,
                       and no mech node is in its determinant's ancestor closure.
                       The note says so rather than implying an axiom.
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


def parse_obo():
    defs, names = {}, {}
    parents = collections.defaultdict(list)
    confers = collections.defaultdict(list)
    participates = collections.defaultdict(set)
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
        m = re.match(r'^def: "(.*)"', line)
        if m:
            defs[cur] = m.group(1)
        m = re.match(r"^is_a: (ARO:\d+)", line)
        if m:
            parents[cur].append(m.group(1))
        m = re.match(r"^relationship: (confers_resistance_to_\w+) (ARO:\d+)", line)
        if m:
            confers[cur].append(line.strip())
        m = re.match(r"^relationship: participates_in (ARO:\d+)", line)
        if m:
            participates[cur].add(m.group(1))
    return defs, names, parents, confers, participates


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
    m = re.search(r"^causal_graphs:\s*$", text, re.M)
    if not m:
        return None
    nxt = re.search(r"^[a-z_]+:", text[m.end():], re.M)
    return m.start(), (m.end() + nxt.start() if nxt else len(text))


def has_snippet(edge) -> bool:
    return any((e or {}).get("snippet") for e in (edge.get("evidence") or []))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    defs, names, parents, confers, participates = parse_obo()
    stat = collections.Counter()

    for f in sorted(ROOT.rglob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        bounds = block_bounds(text)
        if not bounds:
            continue
        start, end = bounds
        graphs = yaml.safe_load(text[start:end])["causal_graphs"]
        if not any(g.get("graph_id") == "resistance-draft" for g in graphs):
            continue
        aro = (re.search(r"^identifier:\s*(ARO:\d+)", text, re.M) or [None, ""])[1]
        anc = ancestors(aro, parents)
        # the nearest term (self first) that actually asserts a resistance relation
        assert_src = next((a for a in [aro] + sorted(anc - {aro}) if confers.get(a)), None)

        changed = False
        for g in graphs:
            if g.get("graph_id") != "resistance-draft":
                continue
            nodes = {n["node_id"]: n for n in g["nodes"]}
            for e in g["edges"]:
                # Correct a false provenance note the drafter left behind. 1,409
                # of 1,449 notes read "Auto-drafted from ARO participates_in
                # ARO:x" for a term where aro.obo asserts no such relationship —
                # only 40 are real. The note is a claim about the source and has
                # to be true, so the ones that are not are rewritten to say what
                # actually assigned the mechanism.
                for evi in e.get("evidence") or []:
                    n = (evi or {}).get("notes") or ""
                    m = re.search(r"Auto-drafted from ARO participates_in (ARO:\d+)", n)
                    if not m:
                        continue
                    tgt = m.group(1)
                    if tgt in participates.get(aro, set()):
                        stat["participates_in note verified"] += 1
                        continue
                    evi["notes"] = n.replace(
                        m.group(0),
                        f"Auto-drafted: mechanism class {tgt} assigned by CARD's "
                        f"categorisation (aro.obo asserts no participates_in "
                        f"between this determinant and {tgt})")
                    stat["false participates_in note corrected"] += 1
                    changed = True
                if has_snippet(e):
                    continue
                subj, obj = e.get("subject"), e.get("object")
                item = None
                if subj.startswith("mech") and obj == "resistance":
                    mg = nodes.get(subj, {}).get("grounding")
                    if defs.get(mg):
                        item = {"reference": mg, "snippet": defs[mg],
                                "notes": (f"ARO definition of the resistance mechanism "
                                          f"class {mg} ({names.get(mg, '')}), which "
                                          f"states the causal link to resistance.")}
                        stat["mech -> resistance"] += 1
                elif subj == "determinant" and obj == "resistance":
                    if assert_src and confers.get(assert_src):
                        line = confers[assert_src][0]
                        where = ("this record's own ARO term"
                                 if assert_src == aro
                                 else f"{assert_src} ({names.get(assert_src, '')}), an "
                                      f"is_a ancestor of {aro}")
                        item = {"reference": assert_src, "snippet": line,
                                "notes": (f"CARD asserts a resistance relation on "
                                          f"{where}.")}
                    elif defs.get(aro):
                        item = {"reference": aro, "snippet": defs[aro],
                                "notes": (f"ARO definition of this determinant "
                                          f"({names.get(aro, '')}).")}
                    if item:
                        stat["determinant -> resistance"] += 1
                elif subj == "determinant" and obj.startswith("mech"):
                    mg = nodes.get(obj, {}).get("grounding")
                    if defs.get(aro):
                        item = {"reference": aro, "snippet": defs[aro],
                                "notes": (f"ARO definition of this determinant. The "
                                          f"mechanism class {mg} "
                                          f"({names.get(mg, '')}) is CARD's mechanism "
                                          f"categorisation for it; aro.obo does not "
                                          f"assert that link as an is_a axiom.")}
                        stat["determinant -> mech"] += 1
                if item:
                    e.setdefault("evidence", []).append(item)
                    changed = True
                else:
                    stat["left without a snippet"] += 1

        if not changed:
            continue
        stat["records changed"] += 1
        block = yaml.safe_dump({"causal_graphs": graphs}, sort_keys=False,
                               allow_unicode=True, width=100,
                               default_flow_style=False)
        if args.apply:
            f.write_text(text[:start] + block + text[end:], encoding="utf-8")

    for k, v in stat.most_common():
        print(f"  {k:<30} {v:>7,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
