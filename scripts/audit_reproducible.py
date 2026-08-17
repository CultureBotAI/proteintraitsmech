#!/usr/bin/env python3
r"""Does each promoter-owned record still match what its config would emit today? (#408)

Nothing related a record on disk to the config that claims it. `--verify-all` checks that a
config's CURIEs RESOLVE -- that it grounds nodes to things that are records -- and never
that the records it owns match what it would write. So config edits landed without a
`--repromote` and the corpus drifted silently: at filing, 443 of 1,142 records no longer
reproduced.

That gap is the read-side of #204 (re-promotion overwriting a curator's later edits).
Together they bracket the same hole, and this is the half that can be measured.

WHY BUCKETS AND NOT A COUNT
---------------------------
A scalar would have been useless here, and measurably so. When #408 was first classified,
449 records differed by TEXT and only 78 differed once parsed -- the other 371 were pure
YAML layout from records written before the dumper was standardised (#194). A single number
mixes those, so re-promoting 371 no-ops would have looked like progress and a real semantic
drift could hide inside the same total.

So this compares PARSED graphs and reports what differs:

    reproduces          the config would emit exactly this graph
    description         only the graph-level prose moved (config text evolved)
    evidence            an edge's evidence differs -- a snippet, reference or note
    structure           nodes or edges differ: the graph itself is not the same
    uncovered           the config has no snippet for this record's mechanism id
    multi-config        more than one config claims it, so "reproduces" is undefined

`structure` is the bucket that matters. `mdfA` and `tet(M)` sit in it because a curator
added literature the config does not have -- re-promoting them would DESTROY that (#204),
which is why this reports rather than repairs.

THREE GATES, for the reasons the sibling audits already record:
  --max-drift    a ceiling, so the number cannot grow
  --baseline     the IDENTITY of each known drifted record, because a ceiling masks a swap
                 (#411: fix one, break one, total unchanged, gate green)
  and a refusal to report a clean corpus when it examined nothing (#418, #432)

LOCAL ONLY -- needs `data/raw/aro/aro.obo`. Without it there is nothing to rebuild against
and this exits 1 rather than reporting 0 drift over 0 records.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import promote_family_drafts as P  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

IDENT = re.compile(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', re.M)
LABEL = re.compile(r'^label:\s*"?(.+?)"?\s*$', re.M)

# The promoter identifies its own output STRUCTURALLY, by the graph id it writes and the
# curator it stamps, and this must use the same test or the two disagree about what is
# owned. Both are short single-token lines, so PyYAML cannot fold either -- which is what
# makes a raw substring check safe HERE and not in general. #462: the same reasoning
# applied to a long phrase silently skipped 28 records, so the distinction is written down
# rather than assumed.
OWNED = ("graph_id: resistance\n", "curator: edison-causal-graphs")

BUCKETS = ("reproduces", "description", "evidence", "structure", "uncovered", "multi-config")


def classify(old: dict, new: dict) -> str:
    """Which bucket a record's difference falls in. `old`/`new` are parsed graphs."""
    if old == new:
        return "reproduces"
    differing = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
    if differing <= {"description", "title"}:
        return "description"
    if differing == {"edges"}:
        oe, ne = old.get("edges") or [], new.get("edges") or []
        if len(oe) == len(ne) and all(
                {f for f in set(a) | set(b) if a.get(f) != b.get(f)} <= {"evidence"}
                for a, b in zip(oe, ne)):
            return "evidence"
    return "structure"


def audit(terms: dict, names: dict, aro_dir: Path):
    """(rows, counts). One row per examined record: (bucket, identifier, path).

    `promoted_graph_dict` narrates per record -- "edge skipped ... endpoint not on this
    record" -- which is right when it is WRITING and pure noise when it is being asked a
    question. 7,452 records of it buried the report, so it is captured and dropped. The
    exception path still classifies, so nothing is silently swallowed: a record whose
    rebuild fails lands in `uncovered` and is counted.
    """
    families = list(P.FAMILY_SNIPPETS)
    rows, counts = [], Counter()
    for path in sorted(aro_dir.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        if not all(marker in text for marker in OWNED):
            continue
        m = IDENT.search(text)
        if not m:
            continue
        ident = m.group(1)
        lm = LABEL.search(text)
        label = lm.group(1) if lm else ""
        ancestry = P.E.ancestry(terms, ident)
        claimed = [f for f in families if f in ancestry
                   and P.config_for(f, ident, label, text) is not None]
        if len(claimed) != 1:
            rows.append(("multi-config", ident, path))
            counts["multi-config"] += 1
            continue
        cfg = P.config_for(claimed[0], ident, label, text)
        try:
            mech, drug = P.D.parse_relations(text)
            with contextlib.redirect_stdout(io.StringIO()):
                new = P.promoted_graph_dict(ident, label, mech, drug, names, cfg, terms)
        except Exception:
            # An uncovered mechanism is the config declining to write evidence it does not
            # have -- the honest outcome, not drift.
            rows.append(("uncovered", ident, path))
            counts["uncovered"] += 1
            continue
        try:
            doc = yaml.safe_load(text) or {}
            old = next(g for g in (doc.get("causal_graphs") or [])
                       if g.get("graph_id") == "resistance")
        except Exception:
            rows.append(("uncovered", ident, path))
            counts["uncovered"] += 1
            continue
        bucket = classify(old, new)
        rows.append((bucket, ident, path))
        counts[bucket] += 1
    return rows, counts


def baseline_key(bucket: str, ident: str, path: Path) -> str:
    """One key per drifted record. The BUCKET is in the key deliberately: a record moving
    from `description` to `structure` is a new fact, not the same one."""
    try:
        rel = str(path.relative_to(ROOT))
    except ValueError:
        rel = str(path)
    return f"{bucket}|{ident}|{rel}"


def diff_baseline(current: dict, known: dict) -> tuple[list, list]:
    """(fixed, new) by key. Same shape as `audit_snippets.diff_baseline`."""
    return (sorted(k for k in known if k not in current),
            sorted(k for k in current if k not in known))



def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-drift", type=int, default=None,
                    help="exit 1 if description+evidence+structure exceed N (a CEILING)")
    ap.add_argument("--baseline", default="",
                    help="JSON pinning each known drifted record, so a swap fails at an "
                         "unchanged count (#411)")
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--show", type=int, default=12)
    ap.add_argument("--aro-dir", default="", help="override (for tests)")
    args = ap.parse_args()

    if not P.E.OBO.exists():
        # Not a pass: with no release there is nothing to rebuild against, and reporting
        # 0 drift over 0 records is the lie #432 was filed for.
        print(f"FAIL: {P.E.OBO} is absent (data/raw is gitignored); run `just fetch-aro`. "
              f"Without it there is nothing to rebuild a graph from.")
        return 1
    aro_dir = Path(args.aro_dir).resolve() if args.aro_dir else P.ARO_DIR
    if not aro_dir.is_dir():
        print(f"FAIL: {aro_dir} is not a directory")
        return 1

    terms = P.E.parse_obo(P.E.OBO)
    names = P.D.obo_names(P.D.OBO)
    rows, counts = audit(terms, names, aro_dir)

    examined = sum(counts.values())
    print(f"promoter-owned records examined: {examined:,}")
    if not examined:
        print(f"FAIL: no promoter-owned records under {aro_dir}. A check that examined "
              f"nothing must not report a reproducing corpus.")
        return 1
    for bucket in BUCKETS:
        if counts.get(bucket):
            print(f"  {counts[bucket]:>6}  {bucket}")

    drift = counts["description"] + counts["evidence"] + counts["structure"]
    comparable = drift + counts["reproduces"]
    print(f"\nDRIFTED: {drift:,} of {comparable:,} comparable "
          f"({100 * drift / comparable:.1f}%)" if comparable else "\nDRIFTED: 0")
    for bucket in ("structure", "evidence", "description"):
        shown = [r for r in rows if r[0] == bucket][:args.show]
        for b, ident, path in shown:
            print(f"  {b:<12} {ident}  {path.name}")

    current = {baseline_key(b, i, p): 1 for b, i, p in rows
               if b in ("description", "evidence", "structure")}
    rc = 0
    if args.max_drift is not None and drift > args.max_drift:
        print(f"\nFAIL: {drift} drifted, exceeding --max-drift {args.max_drift}")
        rc = 1

    if args.baseline:
        bpath = Path(args.baseline)
        if args.update_baseline:
            was = json.loads(bpath.read_text(encoding="utf-8")) if bpath.exists() else {}
            fixed, new = diff_baseline(current, was)
            print(f"\nbaseline: {len(was):,} -> {len(current):,}  "
                  f"({len(fixed):,} FIXED, {len(new):,} NEW)")
            for k in new[:args.show]:
                print(f"  NEW    {k}")
            bpath.parent.mkdir(parents=True, exist_ok=True)
            bpath.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8")
            print(f"baseline written -> {bpath}")
            if new:
                print("NOTE: newly-blessed drift above. `git diff` the baseline before "
                      "committing -- this command can launder a regression.")
            return rc
        if not bpath.exists():
            print(f"\nFAIL: --baseline {bpath} does not exist; run --update-baseline")
            return 1
        known = json.loads(bpath.read_text(encoding="utf-8"))
        fixed, new = diff_baseline(current, known)
        print(f"\nbaseline: {len(known):,} known · {len(fixed):,} FIXED · {len(new):,} NEW")
        for k in new[:args.show]:
            print(f"  NEW    {k}")
        if new:
            print(f"\nFAIL: {len(new)} record(s) newly differ from the config that claims "
                  f"them. Re-promote them, or bless them with --update-baseline and say "
                  f"why in the commit.")
            rc = 1
        elif fixed:
            print("Progress: re-run with --update-baseline to lock it in.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
