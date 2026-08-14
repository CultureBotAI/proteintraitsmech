#!/usr/bin/env python3
"""Backfill rich Pfam definitions from InterPro abstracts (record-sample-review-1
S1 for Pfam). Pfam merged into InterPro, and the '#=GF CC' prose that Pfam-A.hmm.dat
lacks is now the InterPro entry ABSTRACT. interpro.xml.gz carries both the mapping
and the abstracts: 29,105 Pfam signatures appear in exactly one entry's member_list.

WHICH entry is the whole question (#344). This used pfam2interpro.tsv, which conflates
"PF is a member of IPR" with "IPR's abstract mentions PF", and last-wins over its
duplicate rows picked the mention for 407 records. See `interpro_text
.load_member_integration`.

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
XML_GZ = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
ID_RE = re.compile(r"^identifier:\s*(Pfam:PF\d+)", re.M)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import is_curated  # noqa: E402
from interpro_text import clean_abstract_element, load_member_integration  # noqa: E402

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
    """Pfam -> the entry that INTEGRATES it, from interpro.xml's member_list (#344).

    This read `pfam2interpro.tsv` last-wins. That file was derived by taking every
    `db_xref db="PFAM"` in the release, including the ones inside OTHER entries' abstract
    prose, so 467 accessions have more than one row and last-wins picked the prose mention
    for 407 of them. Each of those records then received an abstract describing a
    different domain -- and, because the abstract mentions the Pfam accession, one that
    reads plausibly enough to survive review.

    The TSV is no longer consulted. It cannot be filtered into correctness: by the time a
    row exists the distinction between "member of" and "mentioned by" has been discarded.
    """
    return load_member_integration(XML_GZ)


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

    (That `mapping_source` VALUE is now stale -- the mapping comes from member_list,
    and `seed_interpro_members`/`seed_panther` already write the accurate
    `interpro-member-list` for the same relation. Renaming it rewrites 29k records,
    so it is filed rather than done here; `build_docs_index` maps both labels to
    `biolink:close_match` so the export does not diverge in the meantime.)

    Matches the convention the member-DB seeders already use.
    """
    # #344 kept this wording deliberately. The obvious edit -- "is a member signature of
    # this entry", naming what we now read -- is TRUE, and would have rewritten the
    # `definition_source` line of all 28,606 correctly-mapped records to say something
    # they already implied, burying 407 real content fixes in 29k lines of relabelling
    # (#180's complaint, exactly). It is also unnecessary: `pfam2interpro.tsv` is a
    # SUPERSET, verified -- it contains the correct member_list entry for 29,105 of
    # 29,105 signatures, alongside the prose mentions that made it ambiguous. So the
    # sentence stays true for every record, including the repaired ones.
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



# The `definition_source` this script writes, so a record carrying ANOTHER entry's
# abstract can be recognised and which entry it names can be read back (#344).
borrowed_re = re.compile(r'^definition_source: "InterPro:(IPR\d+) abstract', re.M)

PFAM_CLANS = REPO_ROOT / "data" / "raw" / "pfam" / "Pfam-A.clans.tsv.gz"
PFAM_TYPES = REPO_ROOT / "data" / "raw" / "pfam" / "pfam_types.tsv"
_PFAM_META: dict[str, tuple[str, str, str]] | None = None


def _pfam_meta() -> dict[str, tuple[str, str, str]]:
    """PF accession -> (Pfam ID, description, type), from the files `seed_pfam` reads.

    Loaded once and lazily: only the revert path needs it, and that path fired on 35 of
    30,134 records -- 4 whose correct entry has an empty abstract, 31 integrated into no
    entry at all.

    THE SAME SOURCE THE SEEDER USES, on purpose. The first version recovered the
    description by reading the record's own `label:` line and calling `.strip()` with a
    quote set, which is not a YAML parse. 1,276 Pfam labels are quoted and two decode
    wrong under it: PF00313's description really is

        'Cold-shock' DNA-binding domain

    which YAML writes with the single quotes DOUBLED -- that is how YAML escapes one --
    so stripping quote characters off the ends leaves a stray doubled quote in the middle.
    A description legitimately ending in a quote loses that character outright. Reading the
    release makes "byte-identical to build_yaml" true instead of nearly true.
    """
    global _PFAM_META
    if _PFAM_META is not None:
        return _PFAM_META
    types = {}
    if PFAM_TYPES.exists():
        for line in PFAM_TYPES.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                types[parts[0].strip()] = parts[1].strip()
    meta: dict[str, tuple[str, str, str]] = {}
    if PFAM_CLANS.exists():
        with gzip.open(PFAM_CLANS, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                cols = line.rstrip("\n").split("\t")
                if len(cols) < 5:
                    continue
                meta[cols[0]] = (cols[3], cols[4], types.get(cols[0], "Family"))
    _PFAM_META = meta
    return meta


def pfam_boilerplate(pf: str) -> str | None:
    """`seed_pfam`'s own definition string for this family, or None if unrecoverable.

    The same expression as `seed_pfam.build_yaml`:
    `f"{desc or pid}. Pfam {typ.lower()} family {pid} (Pfam:{pf})."` -- the point of the
    revert is to land exactly where the seeder would have, so a re-seed is a no-op rather
    than a third variant of the same sentence. (`set_definition` collapses whitespace on
    the way out, exactly as `folded()` does for the seeder, so descriptions carrying
    trailing spaces in the release -- there are some -- match too.)

    Returns None rather than guessing when the release does not have the family, so the
    caller can report a stranded record instead of inventing prose.
    """
    meta = _pfam_meta().get(pf)
    if not meta:
        return None
    pid, desc, typ = meta
    if not typ:
        return None
    return f"{desc or pid}. Pfam {typ.lower()} family {pid} (Pfam:{pf})."


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
    # PF2IPR is deliberately NOT required any more (#344): the mapping now comes from
    # interpro.xml's member_list, which is the only place the release states it
    # unambiguously.
    if not XML_GZ.exists():
        print(f"missing {XML_GZ}; run `just fetch-interpro`", file=sys.stderr)
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

    updated = relabelled = curated = reverted = stranded = 0
    for path, pf in records:
        ipr = pf2ipr.get(pf, "")
        ab = abstracts.get(ipr)
        text = path.read_text(encoding="utf-8", errors="replace")
        if not ab:
            # #344: `continue` here was right while the mapping could only be right or
            # absent. It is not right now. A record can be carrying ANOTHER entry's
            # abstract while its own entry has none -- 4 of the 407, and they are the worst
            # of them: `hlh-pf00010` holds IPR025610's text, which says in so many words
            # "The DNA-binding HLH domain is further downstream, Pfam:PF00010" -- an
            # abstract stating it is not about this family.
            #
            # Skipping them would leave the confidently wrong definition in place and
            # report the run as complete. Revert to the Pfam boilerplate instead: a thin
            # true definition beats a fluent false one, and `definition_source: Pfam` puts
            # the record back where the seeder would have left it.
            wrong = borrowed_re.search(text)
            if not wrong or wrong.group(1) == ipr:
                continue
            if not should_enrich(text):
                curated += 1
                continue
            boiler = pfam_boilerplate(pf)
            if boiler is None:
                stranded += 1
                print(f"  STRANDED {path.name}: cites {wrong.group(1)}, should be "
                      f"{ipr or '(unmapped)'}, which has no abstract -- and no Pfam "
                      f"boilerplate could be rebuilt for it")
                continue
            new = set_definition(text, boiler, "Pfam")
            if new != text:
                reverted += 1
                if args.apply:
                    path.write_text(new, encoding="utf-8")
                # #344: reverts count toward --limit too. They did not at first, so
                # `--limit 1` -- the documented canary -- would have written one
                # enrichment and all 35 reverts, which is the opposite of a canary.
                if args.limit and updated + relabelled + reverted >= args.limit:
                    break
            continue
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
            if args.limit and updated + relabelled + reverted >= args.limit:
                break

    verb = "updated" if args.apply else "would update"
    print(f"{verb} {updated:,} Pfam definitions from InterPro abstracts"
          + ("" if args.apply else "  (dry-run; pass --apply)"))
    if relabelled:
        print(f"  {'relabelled' if args.apply else 'would relabel'} "
              f"{relabelled:,} whose text was already correct but whose "
              f"definition_source still said 'Pfam' (#173)")
    if reverted:
        print(f"  {'reverted' if args.apply else 'would revert'} {reverted:,} to the Pfam "
              f"boilerplate: they carried a DIFFERENT entry's abstract and their own entry "
              f"has none (#344)")
    if stranded:
        print(f"  STRANDED {stranded:,}: wrong abstract, no replacement, no boilerplate "
              f"rebuildable -- listed above, and still wrong")
    if curated:
        print(f"  skipped {curated:,} showing curation (definition left alone, #175)")
    if args.limit and updated + relabelled + reverted >= args.limit:
        print(f"  PARTIAL: stopped at --limit {args.limit} -- the rest of the corpus was "
              f"not examined, so the counts above are not a survey")
    # A run that knowingly leaves a record wrong is not a success. It printed the record
    # and then returned 0, so `just repair-pfam-interpro` would have exited clean while
    # announcing its own failure.
    return 1 if stranded else 0


if __name__ == "__main__":
    sys.exit(main())
