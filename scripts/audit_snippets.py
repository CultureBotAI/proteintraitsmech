#!/usr/bin/env python3
r"""Does every cited snippet actually appear in the source it names? (#365)

Every `EvidenceItem` claims a `snippet` is verbatim from its `reference`. Nothing checked
that. This checks the part that CAN be checked offline.

SCOPE, stated plainly because the first version of this docstring overclaimed it: this
catches **#400's class** -- a snippet under the wrong ARO/KB CURIE. It does NOT catch #348
(a sentence attributed to the wrong PMID) or #382 (evidence that survived a removal),
because both are PMID-attributed and PMIDs cannot be verified offline. 40,270 of 69,749
ARO evidence items -- 58% -- are PMIDs or DOIs this tool never checks, and 7,119 of 7,211
promoted ARO records carry one. **The dominant citation vector in this corpus sits outside
this gate.**

What no gate did before this, and still does not for PMIDs:

  * `--verify` (#201) checks that a cited CURIE RESOLVES to a record;
  * `audit-graphs` checks that a snippet is PRESENT on the edge;
  * `validate` treats snippets as opaque strings.

None of them compares a snippet to its source. This does, for on-disk sources.

Only references that are resolvable ON DISK are checked -- ARO ids against
`data/raw/aro/aro.obo`, KB CURIEs against their own record's definition. PMIDs and DOIs are
skipped and counted: they are valid citations we cannot verify offline, and treating them
as failures would drown the real signal (7,119 of 7,211 promoted ARO records carry one).

An ARO snippet may legitimately come from the term's `def:` OR from one of its
`relationship:` lines -- `_drug_assertion` quotes the latter -- so both are searched.

Exit code is 0 unless --strict, or a gate is breached.

TWO gates, because a scalar count is not enough. `--max N` pins a ceiling, and a ceiling
masks a SWAP: #411 demonstrated fixing one pre-existing mismatch while reintroducing #400
in the same tree, leaving the total unchanged and the gate green. In a repo whose recorded
pathology is four rounds of "a fix produced the defect it was fixing", that is the wrong
shape.

`--baseline FILE` pins the IDENTITY of every known mismatch -- (record, reference,
snippet) -- so a new one fails even when an old one is fixed in the same change. Write it
with --update-baseline, and read the diff it prints: FIXED lines are progress, NEW lines
are the thing this exists to catch.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

try:                                    # 5-10x on this workload; the audit parses 7.4k files
    _Loader = yaml.CSafeLoader
except AttributeError:                  # pure-python fallback
    _Loader = yaml.SafeLoader

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
OBO = ROOT / "data" / "raw" / "aro" / "aro.obo"

# References we can resolve without network access. Anything else (PMID, DOI, URL) is
# counted as unverifiable rather than failed.
# Prefixes whose text we actually hold: ARO via aro.obo, the rest as KB trait records.
# `UniProtKB`, `CHEBI`, `RHEA`, `EC` and `MCSA` are deliberately ABSENT -- they are cited as
# external identifiers, not as records whose prose we can quote-check. Including them made
# the first run report 127,286 "unresolvable" references as failures, which was the audit's
# bug and not the corpus's.
ON_DISK_PREFIXES = ("ARO", "Pfam", "GO", "CATH", "PROSITE", "NCBIfam", "InterPro",
                    "PANTHER", "HAMAP", "SFLD", "TED")


def _norm(text: str) -> str:
    """Whitespace-insensitive, so a YAML fold does not read as a mismatch."""
    return " ".join(text.split())


def load_obo_stanzas() -> dict[str, str]:
    """ARO id -> the whole stanza body, normalised.

    The stanza is everything until the next `[Term]`/`[Typedef]` header. Searching the
    WHOLE body, not just `def:`, is deliberate: `_drug_assertion` quotes `relationship:`
    lines verbatim and those are legitimate sources.
    """
    if not OBO.exists():
        return {}
    out: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []
    for line in OBO.read_text(encoding="utf-8").splitlines():
        if line.startswith("["):
            if current:
                out[current] = _norm(" ".join(body))
            current, body = None, []
        elif line.startswith("id: ARO:"):
            current = line[4:].strip()
        elif current:
            body.append(line)
    if current:
        out[current] = _norm(" ".join(body))
    return out


KB_HEAD_BYTES = 8000


def load_kb_definitions(wanted: set[str]) -> dict[str, str]:
    """KB CURIE -> the first KB_HEAD_BYTES of that record's RAW YAML, normalised.

    NOT just its `definition:` -- `label:`, `description:` and `notes:` are in range too,
    so the KB side of this check is laxer than the ARO side. Measured: 5,901 of 12,544
    KB-side passes match outside the definition block, mostly the `label:` line. Stated
    because the first version's docstring said "definition" and did not do that.

    Collect-then-resolve: indexing all 429k records' heads to answer a few hundred
    lookups reads ~1.7 GB. This walks once and keeps only what was asked for.
    """
    if not wanted:
        return {}
    out: dict[str, str] = {}
    ident = re.compile(r'^identifier:\s*"?(\S+?)"?\s*$', re.M)
    for path in TRAITS.rglob("*.yaml"):
        raw = path.read_text(encoding="utf-8")
        head = raw[:KB_HEAD_BYTES]
        m = ident.search(head)
        if m and m.group(1) in wanted and m.group(1) not in out:
            # A record longer than the cut would silently turn real quotes into
            # "mismatches". Read the whole file for those rather than guess.
            out[m.group(1)] = _norm(raw if len(raw) > KB_HEAD_BYTES else head)
            if len(out) == len(wanted):
                break
    return out


def iter_evidence(paths):
    """(record path, graph_id, subject, object, reference, snippet) for every item."""
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if "causal_graphs:" not in text:
            continue
        try:
            doc = yaml.load(text, Loader=_Loader)
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        for graph in doc.get("causal_graphs") or []:
            for edge in graph.get("edges") or []:
                for ev in edge.get("evidence") or []:
                    ref, snip = ev.get("reference"), ev.get("snippet")
                    if ref and snip:
                        yield (path, graph.get("graph_id"), edge.get("subject"),
                               edge.get("object"), ref, snip)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default="", help="restrict to a subtree of data/traits")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any snippet mismatches")
    ap.add_argument("--max", type=int, default=None,
                    help="exit 1 if mismatches exceed N (pins a known backlog)")
    ap.add_argument("--show", type=int, default=12, help="how many examples to print")
    ap.add_argument("--baseline", default="",
                    help="JSON of known mismatches; fails on any NEW one even if the total "
                         "is unchanged (#411). A ceiling cannot see a swap.")
    ap.add_argument("--update-baseline", action="store_true",
                    help="rewrite --baseline from the current state")
    ap.add_argument("--require-aro", action="store_true",
                    help="exit 1 if aro.obo is absent, instead of reporting a meaningless "
                         "small number (#365)")
    args = ap.parse_args()

    if args.require_aro and not OBO.exists():
        print(f"FAIL: --require-aro and {OBO.relative_to(ROOT)} is absent; run `just fetch-aro`")
        return 1
    root = TRAITS / args.path if args.path else TRAITS
    paths = sorted(root.rglob("*.yaml"))
    items = list(iter_evidence(paths))

    wanted = {ref for *_, ref, _ in items
              if ref.split(":")[0] in ON_DISK_PREFIXES and not ref.startswith("ARO:")}
    obo = load_obo_stanzas()
    if not obo:
        print(f"NOTE: {OBO.relative_to(ROOT)} is absent (data/raw is gitignored), so every "
              f"ARO reference is unverifiable here. Run `just fetch-aro` first -- otherwise "
              f"this reports a small number and means nothing (#365).")
    kb = load_kb_definitions(wanted)

    checked = unresolved = skipped = 0
    bad: list[tuple] = []
    by_ref: dict[str, int] = defaultdict(int)
    by_ref_unresolved: dict[str, int] = defaultdict(int)
    for path, gid, subj, obj, ref, snip in items:
        prefix = ref.split(":")[0]
        if prefix not in ON_DISK_PREFIXES:
            skipped += 1                      # PMID / DOI / URL -- valid, not verifiable here
            continue
        body = obo.get(ref) if ref.startswith("ARO:") else kb.get(ref)
        if body is None:
            # Not a failure: a prefix we hold text for, but this particular id is not a
            # record here. Reported so it cannot hide, never counted as a mismatch --
            # an unverifiable citation and a false one are different things (#365).
            unresolved += 1
            by_ref_unresolved[ref] += 1
            continue
        checked += 1
        if _norm(snip) not in body:
            bad.append((path, gid, subj, obj, ref, snip, "snippet not in that source"))
            by_ref[ref] += 1

    records = {b[0] for b in bad}
    print(f"evidence items:            {len(items):,}")
    print(f"  checked against disk:    {checked:,}")
    print(f"  skipped (PMID/DOI/URL):  {skipped:,}  -- valid, not verifiable offline")
    print(f"  not on disk (not a fail): {unresolved:,}"
          f"{'  e.g. ' + ', '.join(sorted(by_ref_unresolved)[:3]) if by_ref_unresolved else ''}")
    print(f"MISMATCHED:                {len(bad):,}  across {len(records):,} records, "
          f"{len(by_ref):,} distinct references")

    # Classify: is the snippet verbatim in some OTHER term? Then the text is real CARD
    # prose under the wrong attribution -- a mechanical repoint. If it is nowhere on disk,
    # it was truncated or reworded when quoted, and a human has to read the source.
    if bad:
        misattributed, unfindable = [], []
        for entry in bad:
            snip = _norm(entry[5])
            owners = [tid for tid, body in obo.items() if snip in body]
            if len(owners) == 1:
                misattributed.append((entry, owners[0]))
            elif owners:
                unfindable.append((entry, f"ambiguous: {len(owners)} terms contain it"))
            else:
                unfindable.append((entry, "verbatim in no term on disk"))
        print(f"\n  misattributed (snippet IS verbatim in exactly one other term -- "
              f"a repoint): {len(misattributed):,}")
        print(f"  needs reading (truncated, reworded, or ambiguous): "
              f"{len(unfindable):,}")
        if misattributed:
            print("\n  repoint suggestions:")
            seen = set()
            for (path, gid, subj, obj, ref, snip, why), owner in misattributed:
                key = (ref, owner)
                if key in seen:
                    continue
                seen.add(key)
                n = sum(1 for e, ow in misattributed if e[4] == ref and ow == owner)
                print(f"    {n:>5}x  {ref}  ->  {owner}")
        if unfindable:
            print("\n  needs reading, by reference:")
            counts: dict[str, int] = defaultdict(int)
            for entry, _ in unfindable:
                counts[entry[4]] += 1
            for ref, n in sorted(counts.items(), key=lambda kv: -kv[1])[:args.show]:
                print(f"    {n:>5}  {ref}")

        print("\nworst references:")
        for ref, n in sorted(by_ref.items(), key=lambda kv: -kv[1])[:args.show]:
            print(f"  {n:>5}  {ref}")
        print("\nexamples:")
        for path, gid, subj, obj, ref, snip, why in bad[:args.show]:
            rel = path.relative_to(ROOT)
            print(f"  {rel}")
            print(f"    {gid}: {subj} -> {obj}  cites {ref} ({why})")
            print(f"    snippet: {_norm(snip)[:110]}")

    # --- identity gate (#411) -------------------------------------------------------
    if args.baseline:
        bpath = Path(args.baseline)
        current = sorted({f"{p.relative_to(ROOT)}|{r}|{_norm(s)}"
                          for p, _g, _su, _o, r, s, _w in bad})
        if args.update_baseline:
            bpath.parent.mkdir(parents=True, exist_ok=True)
            bpath.write_text(json.dumps(current, indent=1) + "\n", encoding="utf-8")
            print(f"\nbaseline written: {len(current):,} known mismatches -> {bpath}")
            return 0
        if not bpath.exists():
            print(f"\nFAIL: --baseline {bpath} does not exist; run --update-baseline")
            return 1
        known = set(json.loads(bpath.read_text(encoding="utf-8")))
        new = [k for k in current if k not in known]
        fixed = [k for k in known if k not in set(current)]
        print(f"\nbaseline: {len(known):,} known · {len(fixed):,} FIXED · {len(new):,} NEW")
        for k in fixed[:args.show]:
            rec, ref, snip = k.split("|", 2)
            print(f"  FIXED  {rec.rsplit('/', 1)[-1]}  {ref}")
        for k in new[:args.show]:
            rec, ref, snip = k.split("|", 2)
            print(f"  NEW    {rec.rsplit('/', 1)[-1]}  {ref}\n         {snip[:100]}")
        if new:
            print(f"\nFAIL: {len(new)} snippet(s) cite a source that does not contain them. "
                  f"If they are intentional, re-run with --update-baseline.")
            return 1
        if fixed:
            print("Progress: re-run with --update-baseline to lock it in.")

    if args.strict and bad:
        return 1
    if args.max is not None and len(bad) > args.max:
        print(f"\nFAIL: {len(bad)} mismatches exceeds --max {args.max}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
