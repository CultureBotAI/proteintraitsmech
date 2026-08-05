#!/usr/bin/env python3
"""Give annotation-free PANTHER families a definition from their subfamilies (#150).

3,596 PANTHER families carry a name-only stub definition, because their row in
`PANTHER19.0_HMM_classifications` has no GO, protein-class or pathway annotation.
That is a property of the source, not a gap in the ingest -- the seeder already
consumes every annotation column the release offers.

But PANTHER annotates *subfamilies* far more often than families, and the seeder
skips subfamilies as out of scope. So for some of those families the release does
say something; it just says it one level down. `seed_panther.subfamily_consensus`
collects the terms that EVERY annotated subfamily of a family shares, requiring at
least MIN_SUBFAMILIES of them, and this script writes that consensus into the
family's stub.

WHAT THIS ASSERTS, AND HOW IT IS KEPT HONEST
--------------------------------------------
A family-level definition composed from subfamily rows states something the source
does not state directly. Three things keep that from being laundered:

  * intersection, not majority -- a term carried by 2 of 10 subfamilies describes
    those two, not the family (see subfamily_consensus for the coverage this costs);
  * the prose says "Subfamilies are annotated with ...", never "Members are ...";
  * `definition_source` names the derivation, so it is greppable and reversible.

Deliberately NOT done: the consensus GO terms are not added to `mapped_xrefs`. An
xref would assert a family-to-GO mapping that PANTHER never made; the prose is a
description, which is a weaker and truthful claim.

The safety gate is exact-match, as in `repair_panther_definitions.py`: a record is
rewritten only where its definition is byte-identical to the name-only stub the
seeder composes today. Anything a curator has touched no longer matches.

Dry-run by default; --apply writes.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section  # noqa: E402
from seed_panther import (  # noqa: E402
    _UNNAMED, OUT_DIR, RAW, SUBFAMILY_SOURCE, compose_definition,
    compose_from_subfamilies, has_annotations, parse_annotations,
    subfamily_consensus,
)
from yaml_emit import yaml_escape  # noqa: E402

from repair_panther_definitions import _collapse, _record_label, load_raw  # noqa: E402

_IDENT = re.compile(r"^identifier:\s*PANTHER:(\S+)\s*$", re.M)
_DEF = re.compile(r"^definition: >-\n  (.*)$", re.M)
_DEF_SRC = re.compile(r"^definition_source: (.*)$", re.M)
COMPOSED_SOURCE_MARK = "(composed from the family name and its GO"

# Fixed rather than "now": a re-run must not produce a diff of nothing but timestamps.
STAMP = "2026-08-04T00:00:00Z"


def curation_event() -> str:
    return ("  - timestamp: \"%s\"\n"
            "    curator: enrich-panther-from-subfamilies\n"
            "    action: %s\n"
            "    llm_assisted: false\n"
            % (STAMP, yaml_escape(
                "Replaced the name-only stub with a definition composed from the GO / "
                "protein-class annotations shared by all of the family's annotated "
                "subfamilies (#150); PANTHER annotates no terms on the family row")))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write the enrichments")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N enriched records (canary runs)")
    args = ap.parse_args()

    if not RAW.exists():
        print(f"missing {RAW} -- run `just fetch-panther`", file=sys.stderr)
        return 2

    raw = load_raw()
    consensus = subfamily_consensus()
    print(f"families with a subfamily consensus: {len(consensus):,}", file=sys.stderr)

    enriched = 0
    counts = {"not a stub": 0, "stub, no subfamily consensus": 0,
              "stub, but definition is not the seeder's (curated)": 0,
              "curation_history could not be spliced": 0}
    for path in sorted(OUT_DIR.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        m = _IDENT.search(text)
        src = _DEF_SRC.search(text)
        if not m or not src or COMPOSED_SOURCE_MARK not in src.group(1):
            counts["not a stub"] += 1
            continue
        pid = m.group(1)
        parts = raw.get(pid)
        if parts is None:
            counts["not a stub"] += 1
            continue
        ann = parse_annotations(parts)
        if has_annotations(ann):
            counts["not a stub"] += 1     # the family row carries its own terms
            continue
        hit = consensus.get(pid)
        if hit is None:
            counts["stub, no subfamily consensus"] += 1
            continue

        label = (parts[1] if len(parts) > 1 else "").strip()
        if label.upper() in _UNNAMED:
            label = _record_label(text) or label
        stub = _collapse(compose_definition(pid, label, ann))
        if stub not in text:
            counts["stub, but definition is not the seeder's (curated)"] += 1
            continue

        agreed, n_sub = hit
        new = _collapse(compose_from_subfamilies(pid, label, agreed, n_sub))
        out = text.replace(stub, new)
        # The stub's source string appears twice: `definition_source:` and the
        # `definitions[]` GENERATED entry's `source:`. Both describe the same
        # derivation, so both move.
        out = out.replace(src.group(1), yaml_escape(SUBFAMILY_SOURCE))
        # The payload must carry its own `curation_history:` line -- append_to_section
        # drops it when the section exists and inserts the block whole when it does
        # not, so one call covers both. Passing a key-less payload silently ate the
        # `- timestamp:` line and over-indented the rest; the canary caught it.
        out = append_to_section(out, "curation_history",
                                "curation_history:\n" + curation_event())
        if out == text:
            counts["curation_history could not be spliced"] += 1
            continue

        if args.apply:
            # Not write_record(): merge_on_reseed would restore the stub's
            # CURATED_SCALARS and append rather than replace (#148).
            path.write_text(out, encoding="utf-8")
        enriched += 1
        if args.limit and enriched >= args.limit:
            break

    verb = "enriched" if args.apply else "would enrich"
    print(f"{verb}: {enriched:,} records")
    if args.limit and enriched >= args.limit:
        print(f"PARTIAL: stopped at --limit {args.limit}")
    for k, v in counts.items():
        if v:
            print(f"  {k}: {v:,}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
