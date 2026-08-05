#!/usr/bin/env python3
"""Revert the subfamily-derived definitions a second model judged WRONG (#151).

#154 composed definitions for 228 annotation-free PANTHER families from the GO /
protein-class terms every annotated subfamily shares. `review_subfamily_definitions.py`
then asked codex whether each borrowed claim is defensible for that family:

    OK            156
    QUESTIONABLE   61
    WRONG          11

This reverts the WRONG ones to the name-only stub they had before, and records why.

WHY ONLY THE WRONG ONES
------------------------
QUESTIONABLE almost always means "true of part of the family, misleading as a
family-wide statement" -- which is exactly what the composed prose already discloses
by naming its basis ("shared by all 3 of its annotated subfamilies"). Reverting those
would throw away defensible information to avoid a risk the reader has already been
handed. WRONG is different: the terms contradict what the family is, and no amount of
attribution makes "Immunoglobulins ... catalytic protein kinases" useful.

The reverted records go back to being honest stubs. That is the outcome #115 already
describes as acceptable: a stub says what the record is and where it came from, and
does not pretend to knowledge nobody verified.

The revert is gated on exact match against the text #154 wrote, so a record edited
since is skipped rather than clobbered. Dry-run by default.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section  # noqa: E402
from seed_panther import (  # noqa: E402
    _UNNAMED, OUT_DIR, RAW, SUBFAMILY_SOURCE, compose_definition,
)
from yaml_emit import yaml_escape  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
REVIEW = REPO / "research" / "subfamily-definition-review.jsonl"
STAMP = "2026-08-04T00:00:00Z"
COMPOSED_SOURCE = ("PANTHER 19.0 (composed from the family name and its GO / "
                   "protein-class annotations)")

_IDENT = re.compile(r"^identifier: PANTHER:(\S+)\s*$", re.M)
_LABEL = re.compile(r"^label:[ \t]*(.*)$", re.M)
_DEF = re.compile(r"^definition: >-\n  (.*)$", re.M)


def _record_label(text: str) -> str | None:
    m = _LABEL.search(text)
    if not m:
        return None
    raw = m.group(1).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return raw


def _collapse(text: str) -> str:
    return " ".join(text.split())


def curation_event(reason: str) -> str:
    action = ("Reverted the subfamily-derived definition to the name-only stub: LLM "
              "review (codex) judged the borrowed terms wrong for this family "
              f"(#151). Reason given: {reason}")
    return ('  - timestamp: "%s"\n'
            "    curator: review-subfamily-definitions\n"
            "    action: %s\n"
            "    llm_assisted: true\n" % (STAMP, yaml_escape(action)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verdict", default="WRONG",
                    help="which verdict to revert (default WRONG)")
    args = ap.parse_args()

    if not REVIEW.exists():
        print(f"missing {REVIEW} -- run review_subfamily_definitions.py first",
              file=sys.stderr)
        return 2
    rows = [json.loads(x) for x in REVIEW.read_text(encoding="utf-8").splitlines() if x]
    targets = {r["id"]: r for r in rows if r["verdict"] == args.verdict}
    print(f"{args.verdict} verdicts: {len(targets)}", file=sys.stderr)
    if not targets:
        return 0

    raw = {}
    for line in RAW.open(encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if p[0].strip() and ":SF" not in p[0]:
            raw[p[0].strip()] = p

    reverted = skipped = 0
    for path in sorted(OUT_DIR.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        m = _IDENT.search(text)
        if not m or m.group(1) not in targets:
            continue
        pid = m.group(1)
        dm = _DEF.search(text)
        if not dm or "of its annotated subfamilies" not in dm.group(1):
            skipped += 1                 # already reverted, or edited since
            continue
        parts = raw.get(pid)
        if parts is None:
            skipped += 1
            continue
        label = (parts[1] if len(parts) > 1 else "").strip()
        if label.upper() in _UNNAMED:
            label = _record_label(text) or label
        # The stub is what compose_definition produces with NO annotations, which is
        # exactly the family's own (empty) row -- the state before #154.
        stub = _collapse(compose_definition(
            pid, label, {"mf": [], "bp": [], "cc": [], "classes": [], "pathways": []}))
        current = dm.group(1)
        out = text.replace(current, stub)
        out = out.replace(yaml_escape(SUBFAMILY_SOURCE), yaml_escape(COMPOSED_SOURCE))
        out = append_to_section(out, "curation_history",
                                "curation_history:\n"
                                + curation_event(targets[pid]["reason"]))
        if out == text:
            skipped += 1
            continue
        if args.apply:
            # In-place edit, not a re-seed: merge_on_reseed would restore the very
            # definition being reverted (#148).
            path.write_text(out, encoding="utf-8")
        reverted += 1
        print(f"  {pid} {targets[pid]['label'][:44]}", file=sys.stderr)

    print(f"{'reverted' if args.apply else 'would revert'}: {reverted}"
          + (f"; skipped {skipped}" if skipped else ""))
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
