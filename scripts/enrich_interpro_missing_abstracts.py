#!/usr/bin/env python3
r"""Give InterPro records a definition when the release ships them without one (#445).

The Pfam half of #445 lives in `enrich_pfam_definitions`, because that script owns Pfam
definitions and a second writer would fight it for the same field. This is the other half:
the 209 entries themselves.

`seed_interpro` writes `definition:` from the release's `<abstract>`, and falls back to the
entry NAME when there is none. So `InterPro:IPR006076` reads

    definition: FAD dependent oxidoreductase
    definition_source: InterPro

— 28 characters, which restates the label and defines nothing — while the InterPro API has
848 characters of curator-written description for that exact entry. 60 records are in that
state.

WHY AN ENRICHER AND NOT A FIX TO THE SEEDER. `seed_interpro` skips records that already
exist (every seeder here does), so fixing it changes nothing for the 60 already on disk;
they need an in-place rewrite. `enrich_pfam_definitions` is the same pattern for the same
reason. The seeder is not wrong, either — it correctly reports what the release contains.

Two refusals, both borrowed from the sibling:

  * a record showing curation is left alone (#175) -- this REPLACES a definition;
  * an LLM-generated description is never promoted (#92). None of the 209 is LLM-written
    today; the check is what keeps that true after the next fetch.

Dry-run by default; `--apply` writes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from interpro_text import clean_api_description  # noqa: E402
from record_io import is_curated, write_validated_record  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
MISSING = ROOT / "data" / "raw" / "interpro" / "missing_abstracts.json"

IDENT = re.compile(r"^identifier: (InterPro:IPR\d+)$", re.M)
DEF_BLOCK = re.compile(r"^definition: >-\n((?:  .*\n)+)", re.M)
DEF_CAP = 1800
MIN_LEN = 40


def api_source(ipr: str) -> str:
    """The provenance line. Deliberately NOT "abstract".

    Saying `InterPro:IPR006076 abstract` would cite a document that does not contain the
    text -- the release ships none for this entry. That is #344's defect in a new place,
    and #344 cost 407 records their definition.
    """
    return (f'"InterPro:{ipr} description (InterPro API; this entry ships no abstract in '
            f'the interpro.xml release)"')


def load_descriptions() -> dict[str, str]:
    """InterPro id -> cleaned description, for the entries worth promoting."""
    if not MISSING.exists():
        return {}
    out = {}
    for ipr, rec in json.loads(MISSING.read_text(encoding="utf-8")).items():
        blocks = rec.get("description") or []
        if any(b.get("llm") for b in blocks):        # #92
            continue
        # The cap is passed IN so it keeps the last paragraph whole -- InterPro puts the
        # entry-specific sentence there, and a head-truncation made IPR019794 (active site)
        # and IPR019793 (haem-binding site) byte-identical (#454 review).
        text = clean_api_description(blocks, DEF_CAP)
        if len(text) < MIN_LEN:
            # 87 of the 209 are this short -- "DUF2252 has no known function." -- and are
            # no better than what the record already says. Left alone rather than churned.
            continue
        out[ipr] = text
    return out


def should_enrich(text: str) -> bool:
    """False for a record showing curation (#175).

    This script REPLACES a definition in place, so it bypasses `merge_on_reseed` -- the
    choke point that protects a curator's edit on the seeder path -- and has to ask
    instead. Exposed as a named function and called from `main` because
    `tests/test_inplace_editor_guards.py` asserts BOTH against the AST: mutation testing
    on #173 showed that tests exercising the helper directly cannot catch a main loop that
    never calls it, which was the entire defect.

    That test caught this script the first time it ran, when the check was an inline
    `is_curated(text)`.
    """
    return not is_curated(text)


def set_definition(text: str, new_def: str, new_src: str) -> str:
    """Replace `definition:` and `definition_source:` together.

    The same shape as `enrich_pfam_definitions.set_definition`, and together for the same
    reason: a definition and a source that disagree is the defect being fixed.
    """
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("definition:"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                j += 1
            block = ["definition: >-", "  " + " ".join(new_def.split())]
            if j < len(lines) and lines[j].startswith("definition_source:"):
                block.append(f"definition_source: {new_src}")
                j += 1
            return "\n".join(lines[:i] + block + lines[j:])
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="stop after N (the canary)")
    args = ap.parse_args()

    desc = load_descriptions()
    if not desc:
        print(f"no usable descriptions in {MISSING}; run "
              f"`just fetch-interpro-missing-abstracts`", file=sys.stderr)
        return 2
    print(f"{len(desc):,} InterPro entries have an API description worth promoting")

    updated = curated = already = 0
    for path in sorted(TRAITS.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        m = IDENT.search(text)
        if not m:
            continue
        new_def = desc.get(m.group(1).split(":", 1)[1])
        if not new_def:
            continue
        if not should_enrich(text):
            curated += 1
            continue
        cur = DEF_BLOCK.search(text)
        if cur and " ".join(cur.group(1).split()) == " ".join(new_def.split()):
            already += 1
            continue
        new = set_definition(text, new_def, api_source(m.group(1).split(":", 1)[1]))
        if new == text:
            continue
        updated += 1
        print(f"  {'wrote' if args.apply else 'would write'}  {path.name}  "
              f"({len(' '.join(cur.group(1).split())) if cur else 0} -> {len(new_def)} chars)")
        if args.apply:
            write_validated_record(path, new, encoding="utf-8")
        if args.limit and updated >= args.limit:
            print(f"\n--limit {args.limit} reached; the rest was not examined.")
            break

    print(f"\n{'updated' if args.apply else 'would update'} {updated:,} InterPro definitions")
    if already:
        print(f"  {already:,} already carry it (idempotent)")
    if curated:
        print(f"  skipped {curated:,} showing curation (#175)")
    if not args.apply:
        print("\ndry run -- nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
