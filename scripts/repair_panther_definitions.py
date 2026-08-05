#!/usr/bin/env python3
"""Repair the ungrammatical composed definitions PANTHER records were seeded with.

`seed_panther.compose_definition` built its annotation clauses with the leads
"Members are annotated with the molecular function" / "and participate in" /
"and localise to", then joined the bits with a space *after each already ended in
a period*. The "and" leads therefore never continued anything -- every record
carrying a biological-process or cellular-component clause got a sentence
beginning with a lowercase "and":

    SERINE/ARGININE REPETITIVE MATRIX 2 -- a full-length protein family modelled
    by the PANTHER 19.0 profile HMM PTHR36562. and localise to nucleus, ...

The seeder is fixed (standalone sentences, correct for all eight present/absent
combinations of MF/BP/CC). This script repairs the records already on disk.

Why not just re-seed with --force: a re-seed rewrites the whole record and would
discard curation applied since ingest -- promoted definitions, PROPOSED status,
curation_history. This edits only the composed string, in place.

The safety gate is exact-match. For each record the buggy text is recomputed
from data/raw/panther and rewritten ONLY where the file contains that exact
string. Anything a curator has touched no longer matches and is left alone.

The composed text can appear twice in one record: as `definition:` and again as
the `definitions[]` entry with `method: GENERATED`. Where an LLM abstract was
later promoted to `definition:`, only the `definitions[]` copy is malformed.
Both are repaired.

Dry-run by default; --apply writes.

    python3 scripts/repair_panther_definitions.py            # report only
    python3 scripts/repair_panther_definitions.py --apply
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


from seed_panther import (  # noqa: E402
    _UNNAMED, OUT_DIR, RAW, compose_definition, parse_annotations,
)

_IDENT = re.compile(r"^identifier:\s*PANTHER:(\S+)\s*$", re.M)
COMPOSED_SOURCE = "(composed from the family name"


_LABEL = re.compile(r"^label:[ \t]*(.*)$", re.M)


def _record_label(text: str) -> str | None:
    """The record's own `label:`, unquoted -- what compose_definition was handed."""
    m = _LABEL.search(text)
    if not m:
        return None
    raw = m.group(1).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        # yaml_escape emits double-quoted scalars with backslash escapes.
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return raw


def _collapse(text: str) -> str:
    """What `folded()` will have written -- whitespace collapsed to single spaces."""
    return " ".join(text.split())


def compose_definition_buggy(pid: str, label: str, ann: dict) -> str:
    """The pre-fix composer, kept verbatim so repairs match only untouched text."""
    bits = [f"{label} — a full-length protein family modelled by the "
            f"PANTHER 19.0 profile HMM {pid}."]
    if ann["classes"]:
        bits.append("PANTHER protein class: " + ", ".join(ann["classes"][:3]) + ".")
    for key, lead in (("mf", "Members are annotated with the molecular function"),
                      ("bp", "and participate in"),
                      ("cc", "and localise to")):
        names = [n for n, _ in ann[key]][:3]
        if names:
            bits.append(f"{lead} {', '.join(names)}.")
    return " ".join(bits)


def load_raw() -> dict[str, list[str]]:
    rows = {}
    for line in RAW.open(encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        pid = parts[0].strip()
        if pid and ":SF" not in pid:
            rows[pid] = parts
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write the repairs")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N repaired records (canary runs)")
    args = ap.parse_args()

    if not RAW.exists():
        print(f"missing {RAW} -- run `just fetch-panther`", file=sys.stderr)
        return 2
    raw = load_raw()

    repaired = occurrences = skipped_no_raw = never_composed = already = 0
    unmatched: list[str] = []
    for path in sorted(OUT_DIR.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        m = _IDENT.search(text)
        if not m:
            continue
        pid = m.group(1)
        parts = raw.get(pid)
        if parts is None:
            skipped_no_raw += 1
            continue
        ann = parse_annotations(parts)
        label = (parts[1] if len(parts) > 1 else "").strip()
        if label.upper() in _UNNAMED:
            # PANTHER declines to name these; the seeder borrowed InterPro's name,
            # so the raw column is not what compose_definition was handed. Read the
            # name the record actually carries. (4 records.)
            label = _record_label(text) or label
        # Compare against the COLLAPSED form: definitions are written through
        # `folded()`, which does `" ".join(text.split())`, so a label carrying a
        # double space ("ARMC5  ARMADILLO ...") reaches disk single-spaced. 54
        # records matched on nothing else.
        buggy = _collapse(compose_definition_buggy(pid, label, ann))
        fixed = _collapse(compose_definition(pid, label, ann))
        if buggy == fixed:
            continue                      # nothing malformed for this record
        n = text.count(buggy)
        if n == 0:
            if fixed in text:
                already += 1              # idempotent: a prior run repaired it
            elif COMPOSED_SOURCE not in text:
                # Expected: this family got a curated InterPro abstract, so
                # build_yaml never stored a composed string to be malformed.
                never_composed += 1
            else:
                unmatched.append(pid)     # genuine mismatch -- report loudly
            continue
        if args.apply:
            # NOT write_record(): that is the re-seed choke point (#100) and runs
            # merge_on_reseed, which treats the incoming text as a fresh record --
            # it APPENDS a repaired definitions[] entry beside the malformed one
            # instead of replacing it, and restores CURATED_SCALARS so the primary
            # `definition:` reverts to the buggy string on curated records. A first
            # --apply run through it left 566 records still malformed and added
            # 1,707 duplicate definitions[] blocks. This is an in-place edit of an
            # existing record, not a re-seed, so it writes directly.
            path.write_text(text.replace(buggy, fixed), encoding="utf-8")
        repaired += 1
        occurrences += n
        if args.limit and repaired >= args.limit:
            break

    verb = "repaired" if args.apply else "would repair"
    print(f"{verb}: {repaired:,} records ({occurrences:,} occurrences of the "
          f"composed string)")
    if already:
        print(f"already repaired by a prior run: {already:,}")
    if never_composed:
        print(f"no composed string to repair (definition came from a curated "
              f"InterPro abstract): {never_composed:,}")
    if unmatched:
        print(f"UNMATCHED -- record has a composed definition but the recomputed "
              f"string is not in it: {len(unmatched):,} {unmatched[:5]}")
    if skipped_no_raw:
        print(f"record has no row in the raw release: {skipped_no_raw:,}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
