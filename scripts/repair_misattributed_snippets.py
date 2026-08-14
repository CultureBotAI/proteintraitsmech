#!/usr/bin/env python3
r"""Rewrite evidence snippets that are not verbatim in the source they cite (#422, #425).

The sibling of #423's truncation repair, for the two classes that repair deliberately
declined:

  * **MISATTRIBUTION** (#422) -- the snippet is real prose from somewhere else, so the
    source does not contain even its prefix and a truncation repair cannot touch it.
  * **ARCHETYPE REUSE** (#425) -- the snippet IS verbatim in the term it cites, so no
    snippet audit can see it, but that term is one specific gene in one specific organism
    and the record carrying it is neither.

Both are table-driven and both are curation calls, so the table states the reasoning per
entry rather than deriving it. Nothing here infers a repair.

TWO GUARDS, because a bulk rewrite of 7.4k hand-and-machine-written records is exactly
where a repair produces the defect it repairs (the repo's recorded pathology, four rounds
of it):

1. **Re-dump is a pure re-wrap.** Every `causal_graphs:` block this touches was emitted by
   `promote_family_drafts._dump`, so re-dumping it should give back what is on disk. 54 of
   the corpus's 7,399 blocks do NOT come back byte-identical -- and the first version of
   this guard refused all of them, which would have stranded every record #425 is about.

   Measured rather than assumed: all 54 differ in ONE way, the column a folded `snippet:`
   wraps at, and all 54 are snippets #423 rewrote with a hand-rolled folder rather than
   PyYAML's. So the guard is not "was this hand-formatted" (none of them were) but "does
   the re-dump change anything a reader would call content". That is checkable exactly:
   **the disk block and its re-dump must be identical after collapsing whitespace.** A
   fold moved inside a folded scalar survives that; a reordered key, a changed quoting
   style, a dropped comment or an altered value does not. Over all 7,399 blocks, 54 differ
   byte-wise and 0 differ under it.

   A block that fails THAT is skipped and reported, never rewritten.

2. **Verbatim-in-source.** Every replacement is checked to be a verbatim substring of the
   stanza it will cite, against `data/raw/aro/aro.obo` or the KB record, using the same
   normaliser `audit_snippets.py` gates with. A repair that would not pass the gate it
   exists to satisfy is refused before the run starts, not discovered after it.

Dry-run by default; `--apply` writes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_snippets as A

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"


def _norm(text: str) -> str:
    return " ".join(text.split())


# ---------------------------------------------------------------------------------------
# The repairs. `old` and `new` are matched/emitted whitespace-insensitively; `ref_from` is
# the reference the item currently carries and `ref_to` the one it should, which is the
# same in every entry here except where the text was never CARD's at all.
#
# Optional keys:
#   `on_edge`   (subject, object) -- required when the SAME (reference, snippet) pair sits
#               on more than one edge and the repairs differ. Both carO sites quote the
#               identical sentence and need different replacements, so without this the
#               first matching entry would win on both and one edge would get evidence for
#               the other edge's claim.
#   `notes`     replacement for the item's `notes`. A repair that changes what a snippet
#               SAYS while leaving a note that describes the old text ("CARD's definition
#               of carO, the archetype") swaps a false quote for a false gloss.
#
# Each entry mirrors a config literal changed in `promote_family_drafts.py` in the same
# commit. They must stay in step: the config decides what a NEW record gets, this decides
# what the existing ones get, and a divergence is invisible until the next promotion.
# ---------------------------------------------------------------------------------------
_CARO = ("carO is a transmembrane beta-barrel involved in the influx of carbapenem "
         "antibiotics in Acinetobacter baumannii. Disruption of the carO gene by distinct "
         "insertion elements results in a loss of carO expression causing resistance to "
         "carbapenem antibiotics. Homologs of carO have been identified in genera "
         "Acinetobacter, Moraxella and Psychrobacter.")

REPAIRS = [
    {
        "issue": "#422",
        "ref_from": "ARO:3000187",
        "ref_to": "ARO:3000187",
        "old": ("Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of "
                "an amide bond in the beta-lactam ring of antibiotics belonging to the "
                "penicillin/cephalosporin family."),
        "new": ("Mechanism of enzymatic degradation common to Ambler Class A, C and D "
                "beta-lactamases. A serine residue located in the active site is used to "
                "form an acyl-enzyme intermediate and subsequent hydrolysis renders the "
                "beta-lactam inactive."),
        "why": ("The cited text is PROSITE's, not ARO's -- it is the shared preamble of "
                "PROSITE:PS00146/PS00336/PS00337/PS00743 and appears nowhere in aro.obo. "
                "A repoint to one PROSITE record was not available: which one is right "
                "depends on the record's Ambler class. ARO:3000187's own definition is "
                "general over classes A, C and D, is what the notes on these edges already "
                "claim to quote, and names the acyl-enzyme intermediate the edges assert. "
                "All five affected records are class D (ARO:3005394 / ARO:3005396 / "
                "ARO:3005441 are all is_a ARO:3000075), so nothing is lost by staying at "
                "the mechanism term rather than descending to a class-specific signature."),
    },
    {
        "issue": "#422",
        "ref_from": "Pfam:PF04563",
        "ref_to": "Pfam:PF04563",
        "old": ("RNA polymerases catalyse the DNA dependent polymerisation of RNA. "
                "Prokaryotes contain a single RNA polymerase compared to three in "
                "eukaryotes. This domain forms one of the two distinctive lobes of the "
                "Rpb2 structure."),
        "new": ("RNA polymerases catalyse the DNA dependent polymerisation of RNA. "
                "Prokaryotes contain a single RNA polymerase compared to three in "
                "eukaryotes (not including mitochondrial and chloroplast polymerases). "
                "This domain forms one of the two distinctive lobes of the Rpb2 structure."),
        "why": ("An ELISION, not a truncation: the parenthetical was dropped from the "
                "middle of the quote, so the source contains the cited prefix and then "
                "diverges -- which is why #423's guard declined it. Restored verbatim from "
                "the KB record's definition (the InterPro:IPR007644 abstract). The claim "
                "the edge makes is unchanged."),
    },
    {
        "issue": "#425",
        "ref_from": "ARO:3003808",
        "ref_to": "ARO:3000270",
        "on_edge": ("determinant", "resistance"),
        "old": _CARO,
        "new": ("Enzymes or other proteins either directly or indirectly reducing overall "
                "permeability to antibiotics."),
        "notes": ("CARD's definition of the family term these records sit under -- the "
                  "claim at exactly the level this config makes it. Each record's own "
                  "definition names the channel and the drug class IT admits."),
        "why": ("carO's own definition, used as the archetype for all 42 records this "
                "config promotes, 2 of which are carO. It names Acinetobacter baumannii, "
                "the carO gene and three genera, and sat on two fungal permeases, a fungal "
                "nucleobase transporter, MarA and a Ser/Thr kinase. ARO:3000270 is the "
                "family term and an is_a ancestor of every record here, and names no gene "
                "and no organism. The general claim carO was illustrating is the Nikaido "
                "2003 item already on this edge, which is untouched."),
    },
    {
        "issue": "#425",
        "ref_from": "ARO:3003808",
        "ref_to": "ARO:3000244",
        "on_edge": ("determinant", "influx"),
        "old": _CARO,
        "new": ("Reduction in permeability to antibiotic, generally through reduced "
                "production of porins, can provide resistance."),
        "notes": ("CARD's mechanism term, stated as the loss: permeability falls when the "
                  "channel does, which is this edge read backwards. General to every "
                  "record here; each names its own channel and drug."),
        "why": ("The second carO site, and the one carrying the ONLY evidence on its edge, "
                "so it needed a replacement rather than a deletion. ARO:3000244 is the "
                "mechanism term these records participate in and states the inverse of "
                "this edge -- which is the claim, since the edge exists to be negated by "
                "the channel's loss."),
    },
]


def _resolve_sources() -> tuple[dict, dict]:
    """(obo stanzas, KB definitions) for exactly the references the repairs cite."""
    obo = A.load_obo_stanzas()
    wanted = {r["ref_to"] for r in REPAIRS
              if not r["ref_to"].startswith("ARO:")
              and r["ref_to"].split(":")[0] in A.ON_DISK_PREFIXES}
    return obo, A.load_kb_definitions(wanted)


def check_repairs(obo: dict, kb: dict) -> list[str]:
    """Refuse the whole run if any replacement would not be verbatim in its source.

    Deliberately a PRE-pass over the table rather than a per-record check: a repair that
    is wrong is wrong for every record, and finding that out after 40 files were rewritten
    is the failure mode this whole script is shaped around.
    """
    problems = []
    for rep in REPAIRS:
        ref = rep["ref_to"]
        if ref.split(":")[0] not in A.ON_DISK_PREFIXES:
            continue                    # PMID/DOI: a real citation we cannot check offline
        body = obo.get(ref) if ref.startswith("ARO:") else kb.get(ref)
        if body is None:
            problems.append(f"{ref}: not resolvable on disk (run `just fetch-aro`?)")
        elif _norm(rep["new"]) not in body:
            problems.append(f"{ref}: the replacement text is NOT verbatim in that source")

    # AMBIGUITY. `_match` returns the first entry that fits, so two entries that can both
    # fit the same item make list ORDER decide what an edge ends up claiming -- and the
    # two carO entries are exactly that pair, separated only by `on_edge`. Checked here
    # rather than trusted, because the failure is silent: both edges get valid-looking
    # evidence and one of them gets the other's.
    for i, a in enumerate(REPAIRS):
        for b in REPAIRS[i + 1:]:
            if a["ref_from"] != b["ref_from"] or _norm(a["old"]) != _norm(b["old"]):
                continue
            ea, eb = a.get("on_edge"), b.get("on_edge")
            if ea is None or eb is None or tuple(ea) == tuple(eb):
                problems.append(
                    f"{a['ref_from']}: two repairs match the same (reference, snippet) "
                    f"and are not separated by a distinct `on_edge` -- list order would "
                    f"decide which edge gets which replacement")
    return problems


def _match(edge: dict, ev: dict) -> dict | None:
    """The repair that applies to this evidence item, or None.

    At most one can: `check_repairs` refuses the run if two entries could both match, so
    "first hit wins" is never load-bearing here.
    """
    for rep in REPAIRS:
        if ev.get("reference") != rep["ref_from"]:
            continue
        if _norm(ev.get("snippet") or "") != _norm(rep["old"]):
            continue
        on_edge = rep.get("on_edge")
        if on_edge and (edge.get("subject"), edge.get("object")) != tuple(on_edge):
            continue
        return rep
    return None


def _graph_block(text: str) -> tuple[int, int] | None:
    """(start, end) line indices of the top-level `causal_graphs:` block, or None.

    Ends at the next line that starts a top-level key -- a column-0 non-space, non-dash
    character -- which is how every record in this corpus is laid out.
    """
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith("causal_graphs:")), None)
    if start is None:
        return None
    for i in range(start + 1, len(lines)):
        if lines[i][:1].strip() and not lines[i].startswith(("-", " ")):
            return start, i
    return start, len(lines)


def _dump(obj) -> str:
    """Byte-for-byte the promoter's emitter (`promote_family_drafts._dump`)."""
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100,
                          default_flow_style=False)


def repair_record(text: str) -> tuple[str | None, str, int]:
    """(new text or None, reason, number of snippets changed).

    None with a reason means "left alone": either nothing matched, or re-dumping the block
    would change more than where its folded scalars wrap.
    """
    span = _graph_block(text)
    if span is None:
        return None, "no causal_graphs block", 0
    lines = text.splitlines(keepends=True)
    block = "".join(lines[span[0]:span[1]])
    try:
        doc = yaml.safe_load(block)
    except Exception as exc:                                   # pragma: no cover
        return None, f"unparseable causal_graphs block: {exc}", 0
    # Count the matches BEFORE deciding whether the block may be rewritten, so a record
    # that both needs a repair and cannot take one is reported rather than filed under the
    # same silent "skipped" as the 54 that need nothing. A skip that reads as "nothing to
    # do" when the truth is "could not do it" is how a repair run reports success at 41 of
    # 47.
    matches = sum(1 for graph in doc.get("causal_graphs") or []
                  for edge in graph.get("edges") or []
                  for ev in edge.get("evidence") or []
                  if _match(edge, ev) is not None)
    # Whitespace-collapsed, not byte-for-byte: see the module docstring. Byte equality
    # rejects the 54 blocks #423 re-wrapped by hand, which is every record #425 concerns.
    if _norm(_dump(doc)) != _norm(block):
        reason = "re-dump would change content, not just wrapping"
        if matches:
            reason += f" -- AND CARRIES {matches} MATCHING SNIPPET(S)"
        return None, reason, matches

    changed = 0
    for graph in doc.get("causal_graphs") or []:
        for edge in graph.get("edges") or []:
            for ev in edge.get("evidence") or []:
                rep = _match(edge, ev)
                if rep is None:
                    continue
                ev["reference"] = rep["ref_to"]
                ev["snippet"] = _norm(rep["new"])
                if rep.get("notes"):
                    ev["notes"] = _norm(rep["notes"])
                changed += 1
    if not changed:
        return None, "no matching snippet", 0
    out = "".join(lines[:span[0]]) + _dump(doc) + "".join(lines[span[1]:])
    return out, "repaired", changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write; default is a dry run")
    ap.add_argument("--path", default=str(ARO_DIR), help="directory of records to repair")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N repaired records -- the canary: run `--limit 1 "
                         "--apply` and read the diff before the other 15")
    args = ap.parse_args()

    obo, kb = _resolve_sources()
    problems = check_repairs(obo, kb)
    if problems:
        print("REFUSING: a replacement is not verbatim in the source it will cite.")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"{len(REPAIRS)} repair(s), each verified verbatim in its source.\n")

    root = Path(args.path)
    repaired = skipped_handformatted = 0
    total_snippets = 0
    stranded: list[tuple[str, int]] = []
    for path in sorted(root.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        if "causal_graphs:" not in text:
            continue
        out, reason, n = repair_record(text)
        if out is None:
            if reason.startswith("re-dump would change content"):
                skipped_handformatted += 1
                if n:
                    stranded.append((path.name, n))
            continue
        repaired += 1
        total_snippets += n
        print(f"  {'wrote' if args.apply else 'would write'}  {path.name}  ({n} snippet(s))")
        if args.apply:
            path.write_text(out, encoding="utf-8")
        if args.limit and repaired >= args.limit:
            print(f"\n--limit {args.limit} reached; stopping.")
            break

    print(f"\nrecords repaired: {repaired:,}   snippets rewritten: {total_snippets:,}")
    if skipped_handformatted:
        # Reported even at zero-relevance, because a silent skip here reads as "nothing
        # needed repairing" and means the opposite.
        print(f"skipped, re-dump would change content: {skipped_handformatted:,}  "
              f"(repair these by hand or not at all)")
    if stranded:
        print(f"\nFAIL: {len(stranded)} record(s) NEED a repair this script cannot make -- "
              f"re-dumping their block would change more than line wrapping. Fix these "
              f"by hand; the gate will still see them.")
        for name, n in stranded:
            print(f"  {n} snippet(s)  {name}")
        return 1
    if not args.apply:
        print("\ndry run -- nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
