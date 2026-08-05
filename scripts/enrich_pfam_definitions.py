#!/usr/bin/env python3
"""Backfill rich Pfam definitions from InterPro abstracts (record-sample-review-1
S1 for Pfam). Pfam merged into InterPro, and the '#=GF CC' prose that Pfam-A.hmm.dat
lacks is now the InterPro entry ABSTRACT. pfam2interpro maps ~29.7k Pfam families
to an InterPro entry; interpro.xml.gz (already fetched) carries the abstracts.

For each Pfam record whose family maps to an InterPro entry with a non-trivial
abstract, replace the boilerplate definition ('<name>. Pfam <type> family …')
with that abstract. In place (preserves sequence_pattern / clan member_of /
mapped_xrefs / license). Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
PF2IPR = REPO_ROOT / "data" / "raw" / "mappings" / "pfam2interpro.tsv"
XML_GZ = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
ID_RE = re.compile(r"^identifier:\s*(Pfam:PF\d+)", re.M)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import is_curated  # noqa: E402
from interpro_text import clean_abstract_element  # noqa: E402

DEF_CAP = 1800


def clean_abstract(el) -> str:
    """Delegates to the shared cleaner (#159, #171); only the cap is local.

    This was the FOURTH copy of the abstract cleaning, and the last to be found.
    It had both of the defects the others had, and its own variant of the second:

      * `el.itertext()` cannot see attributes, so every inline
        `<db_xref db=... dbkey=.../>` lost the accession it carried -- 16,699
        across the release, including 5,521 EC numbers;
      * it swept only `[ ]` husks, never `( )`. That is precisely why Pfam
        records carried the empty-paren tell while InterPro's own did not, and
        why 3,431 remained after #170 fixed the other three copies.
    """
    text = clean_abstract_element(el)
    if len(text) > DEF_CAP:
        text = text[:DEF_CAP - 1].rstrip() + "…"
    return text


def load_pf2ipr() -> dict[str, str]:
    out = {}
    for line in PF2IPR.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].startswith("PF"):
            out[parts[0]] = parts[1].strip()
    return out


def load_ipr_abstracts(wanted: set[str]) -> dict[str, str]:
    out = {}
    with gzip.open(XML_GZ, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = el.get("id", "")
            if ipr in wanted:
                ab = clean_abstract(el.find("abstract"))
                if len(ab) >= 40:                        # skip empty/near-empty
                    out[ipr] = ab
            el.clear()
    return out


def borrowed_source(ipr: str, pf: str) -> str:
    """What `definition_source` must say once the definition is InterPro's prose.

    This script replaces a Pfam record's definition with the ABSTRACT OF THE
    INTERPRO ENTRY Pfam maps to, and used to leave `definition_source: Pfam`
    untouched (#173). The text's real origin was then unrecoverable from the
    record, which cost real time twice:

      * #171 could not identify which script wrote these definitions, because
        the source label pointed at Pfam; it took `git log --follow` on an
        individual record to find out.
      * `repair_interpro_abstracts` keys on the source naming an InterPro
        abstract, so it skipped every one of these -- which is why #170 shipped
        with 3,431 records still carrying deleted cross-references.

    `mapped_xrefs: {object: InterPro:…, mapping_source: pfam2interpro}` is not a
    substitute: that asserts a signature-to-entry MAPPING, which is a different
    claim from "this definition's text is that entry's abstract".

    Matches the convention the member-DB seeders already use.
    """
    return (f'"InterPro:{ipr} abstract '
            f'(Pfam {pf} maps to this entry via pfam2interpro)"')


def set_definition(text: str, new_def: str, new_src: str | None = None) -> str:
    """Replace the definition block, and its `definition_source` when given.

    Both together: a definition and a source that disagree is the defect this
    fixes, so they are never written apart.

    (`startswith("definition:")` already excludes `definition_source:` -- ":"
    against "_" -- so no extra guard is needed. An earlier version added one;
    mutation testing showed no test could tell it apart, because it was dead.)
    """
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("definition:"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                j += 1
            block = ["definition: >-", "  " + " ".join(new_def.split())]
            if new_src is not None and j < len(lines) and \
                    lines[j].startswith("definition_source:"):
                block.append(f"definition_source: {new_src}")
                j += 1
            return "\n".join(lines[:i] + block + lines[j:])
    return text


def enrich_record(text: str, ipr: str, pf: str, abstract: str) -> str:
    """One record's new content: the abstract AND the source that names it.

    Extracted so the wiring is testable. Mutation testing found that tests
    calling `set_definition` directly could not catch the main loop dropping the
    source argument -- which is the original defect, restored.
    """
    return set_definition(text, abstract, borrowed_source(ipr, pf))



def should_enrich(text: str) -> bool:
    """False for a record showing curation.

    This script REPLACES a record's definition in place. Without this, a
    curator's rewrite is silently overwritten on the next run -- no warning, no
    counter, nothing outside git (#175). `record_io.merge_on_reseed` gives
    seeders that protection for free, but only on the re-seed path; an in-place
    editor has to ask.

    Exposed as a function, not inlined, so the CALLER is testable. Mutation
    testing on #173 showed that tests exercising a helper directly cannot catch
    the main loop failing to call it -- which is the failure that matters.
    """
    return not is_curated(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N updated records (canary runs)")
    args = ap.parse_args()
    for f in (PF2IPR, XML_GZ):
        if not f.exists():
            print(f"missing {f}; run `just fetch-pfam` / `just fetch-interpro`", file=sys.stderr)
            return 2

    pf2ipr = load_pf2ipr()
    pfam_dirs = [TRAITS / "sequence" / d / "pfam" for d in
                 ("domain", "family", "homologous_superfamily", "repeat", "disorder", "motif")]
    pfam_dirs.append(TRAITS / "mixed" / "coiled_coil" / "pfam")
    records = []
    for d in pfam_dirs:
        for path in d.rglob("*.yaml") if d.exists() else []:
            m = ID_RE.search(path.read_text(encoding="utf-8", errors="replace"))
            if m:
                records.append((path, m.group(1).split(":", 1)[1]))

    wanted = {pf2ipr[pf] for _, pf in records if pf in pf2ipr}
    print(f"{len(records):,} Pfam records; {len(wanted):,} distinct InterPro targets — reading abstracts…")
    abstracts = load_ipr_abstracts(wanted)
    print(f"{len(abstracts):,} InterPro entries have a usable abstract")

    updated = relabelled = curated = 0
    for path, pf in records:
        ipr = pf2ipr.get(pf, "")
        ab = abstracts.get(ipr)
        if not ab:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not should_enrich(text):
            curated += 1
            continue
        new = enrich_record(text, ipr, pf, ab)
        if new != text:
            # A record whose definition was already ours and only the SOURCE
            # moves is the #173 backfill; one whose text changes too is the
            # ordinary enrichment. Counted apart so a re-run is readable.
            if " ".join(ab.split()) in text:
                relabelled += 1
            else:
                updated += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")
            if args.limit and updated + relabelled >= args.limit:
                break

    verb = "updated" if args.apply else "would update"
    print(f"{verb} {updated:,} Pfam definitions from InterPro abstracts"
          + ("" if args.apply else "  (dry-run; pass --apply)"))
    if relabelled:
        print(f"  {'relabelled' if args.apply else 'would relabel'} "
              f"{relabelled:,} whose text was already correct but whose "
              f"definition_source still said 'Pfam' (#173)")
    if curated:
        print(f"  skipped {curated:,} showing curation (definition left alone, #175)")
    if args.limit and updated + relabelled >= args.limit:
        print(f"  PARTIAL: stopped at --limit {args.limit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
