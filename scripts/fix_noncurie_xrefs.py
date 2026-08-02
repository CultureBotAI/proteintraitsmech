#!/usr/bin/env python3
"""Move non-CURIE citation `xrefs` into `evidence`; drop the rest — issue #90.

  python3 scripts/fix_noncurie_xrefs.py            # dry run, lists every change
  python3 scripts/fix_noncurie_xrefs.py --apply

28 records fail closed-mode validation because an `xrefs` value does not match the
schema's `^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$`:

  * 27 DOIs across `function/{pathway,localization,molecular_function}/go`. A DOI
    always contains `/`, so **no DOI can ever be a valid xref** — a category error,
    not 27 malformed strings. These are **moved to `evidence`**, whose `reference`
    range accepts a DOI.
  * 1 literal placeholder `CATH:???????`, which is a data bug and is **dropped**.

WHY MOVED AND NOT DROPPED — A CORRECTION
-----------------------------------------
An earlier version of this script dropped the DOIs, arguing that the current GO
release carries none and that `seed_obo.py` already discards them, so nothing was
lost and a re-seed would not recreate them. **Both halves of that were wrong.**

`seed_obo.py` discards DOIs found on `xref:` lines, but these came from the `def:`
source brackets. `normalise_source()` does apply a CURIE check — but only after an
early return for `DOI:`/`PMID:`, so a DOI reached `xrefs` unchecked. And the release
the GO seeder actually reads, `go-basic.obo` (not `go.obo`), still carries them —
35 DOI definition sources, of which 27 are on routed non-obsolete terms, exactly
matching the 27 records here. Including GO:0072324:

    def: "Ascus cytoplasm that is not packaged into ascospores." [DOI:10.1016/S0953-7562(96)80057-8, GOC:mcc]

So a re-seed would have recreated every one of these failures, and dropping them
discarded live provenance that GO still asserts. `seed_obo.py` now routes citation
def-sources (DOI/PMID) to `evidence` instead of `xrefs`, and this migration brings
existing records to the same shape.

SCOPE OF THE "RE-SEED REPRODUCES THIS" CLAIM — STATED PRECISELY
---------------------------------------------------------------
It holds for the fields the seeder owns: identifier, label, definition,
definition_source, axis/category, term_kind, mapping_status, parent_traits,
synonyms, xrefs and evidence. Verified byte-for-byte on GO:0072324.

It does NOT mean a forced re-seed reproduces a whole record. `seed_obo.py` and
`seed_cath.py` rebuild only seed-owned fields and their `--force` path overwrites
the file, so any later curation — `definitions`, `canonical_examples`,
`trait_relations`, `causal_graphs`, `curation_history` — is lost. That is
long-standing seeder behaviour, not introduced here, and it affects far more than
these 28 records (10 of the 27 migrated GO records carry such enrichment). Do not
run any seeder with `--force` over curated records expecting a no-op.

Idempotent; dry-run unless --apply. Stdlib-only. Rewrites only the lines it must,
leaving the rest of each hand-formatted record untouched.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")
# `EvidenceItem.reference` documents its range as "PMID:…, DOI:…, a database CURIE,
# or an opaque URL", so a URL is relocatable evidence, not junk to discard.
RELOCATABLE = re.compile(r"^(DOI:|PMID:|https?://)", re.I)


def _source_labels() -> dict[str, str]:
    """identifier prefix -> the seeder's own release_prefix (`GO:` -> `GO`).

    Imported from `seed_obo.py` rather than hardcoded: the migration previously
    wrote "GO definition source" for every record it touched, but it walks all of
    `data/traits`, so an ARO or PSI-MI record would have been mislabelled as GO —
    and would then differ from what a re-seed emits, which is the whole property
    this migration exists to restore.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from seed_obo import SOURCES
    except ImportError:
        return {}
    return {s.id_prefix: s.release_prefix for s in SOURCES.values()}
# Both list styles occur in the corpus at scale — a record may write `- x` at
# column 0 or `  - x` indented — so the item pattern must capture the indent rather
# than assume one. Assuming two spaces made the migration silently skip offenders in
# the majority of records; it only worked because all 28 happened to be indented.
_ITEM = re.compile(r"^(\s*)- (.+?)\s*$")
_TOP_KEY = re.compile(r"^[A-Za-z_]")


def offenders(lines: list[str]) -> list[int]:
    """Indices of `xrefs:` list items whose value is not a CURIE."""
    out, inx = [], False
    for i, ln in enumerate(lines):
        if ln.startswith("xrefs:"):
            inx = True
            continue
        if not inx:
            continue
        m = _ITEM.match(ln)
        if not m:
            if ln.strip() and _TOP_KEY.match(ln):
                inx = False
            continue
        if not CURIE.match(m.group(2).strip().strip("\"'")):
            out.append(i)
    return out


def _unescape(value: str) -> str:
    """Reuse the seeder's OBO unescaper so migrated and re-seeded values match.

    GO:0016087 shipped `DOI:...35\\:1` — an OBO-escaped colon copied through
    verbatim, producing a DOI that does not resolve.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from seed_obo import _unescape_obo
    except ImportError:
        return value
    return _unescape_obo(value)


def evidence_block(citations: list[str], label: str, indent: str = "  ") -> list[str]:
    """Byte-identical to what `seed_obo.py` now emits for a citation def-source.

    This matters more than the note reading nicely: if the migration and the seeder
    disagree by even the wording or the quoting, the next re-seed rewrites all 27
    records — which is precisely the seeder-equals-data property this fix exists to
    restore. The provenance of *why* they moved lives in the commit and in issue #90,
    not in 27 copies of a sentence.
    """
    # Emit in the record's own list style. Always writing two spaces would mix
    # indentation into a column-0 record — the same class of corruption the graph
    # helper hit, where appending column-0 items into an indented list produced
    # unparseable YAML.
    out = ["evidence:\n"]
    for c in citations:
        out.append(f"{indent}- reference: {c}\n")
        # Must match seed_obo.py's wording exactly, including the honesty caveat:
        # two of these migrated GO DOIs are truncated SICI/journal fragments that
        # 404. They are what GO asserts, so they are preserved rather than dropped,
        # but they are not claimed as resolved.
        out.append(f'{indent}  notes: "{label} definition source '
                   f'(verbatim; not independently resolved)"\n')
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    labels = _source_labels()
    n_files = n_moved = n_dropped = 0
    for f in sorted(TRAITS.rglob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        if "xrefs:" not in text:
            continue
        lines = text.splitlines(keepends=True)
        bad = offenders(lines)
        if not bad:
            continue
        rel = f.relative_to(REPO_ROOT)
        ident = next((ln.split(":", 1)[1].strip() for ln in lines
                      if ln.startswith("identifier:")), "")
        label = labels.get(ident.split(":", 1)[0] + ":", "") if ident else ""
        bad_set = set(bad)
        citations, dropped = [], []
        for i in bad:
            v = _ITEM.match(lines[i]).group(2).strip().strip("\"'")
            v = _unescape(v)
            (citations if RELOCATABLE.match(v) else dropped).append(v)
        for c in citations:
            print(f"  {rel}\n      move to evidence: {c}")
        for d in dropped:
            print(f"  {rel}\n      drop:             {d}")

        # the record's own list style, taken from the xrefs items we just read
        indent = next((_ITEM.match(lines[i]).group(1) for i in bad), "  ")
        kept = [ln for i, ln in enumerate(lines) if i not in bad_set]
        # An xrefs: key whose every item was invalid must go too, or it is left as an
        # empty mapping value and stops parsing as a list.
        xi = next((i for i, ln in enumerate(kept) if ln.startswith("xrefs:")), None)
        if xi is not None and not _ITEM.match(kept[xi + 1] if xi + 1 < len(kept) else ""):
            kept.pop(xi)

        if citations:
            # `evidence` belongs before `license:`, the record's last key by
            # convention; merge into an existing block if the record already has one.
            ei = next((i for i, ln in enumerate(kept) if ln.startswith("evidence:")), None)
            if ei is not None:
                end = ei + 1
                while end < len(kept) and not _TOP_KEY.match(kept[end]):
                    end += 1
                # The existing evidence list's OWN indent, which need not match the
                # xrefs one — 10k+ records write the two keys in different styles,
                # and reusing the xrefs indent produced unparseable YAML.
                ev_indent = next((m.group(1) for m in
                                  (_ITEM.match(ln) for ln in kept[ei + 1:end]) if m),
                                 indent)
                kept = (kept[:end]
                        + evidence_block(citations, label, ev_indent)[1:]
                        + kept[end:])
            else:
                lic = next((i for i, ln in enumerate(kept)
                            if ln.startswith("license:")), len(kept))
                kept = kept[:lic] + evidence_block(citations, label, indent) + kept[lic:]

        n_files += 1
        n_moved += len(citations)
        n_dropped += len(dropped)
        if args.apply:
            f.write_text("".join(kept), encoding="utf-8")

    print(f"\n  {n_moved} citation(s) moved to evidence, {n_dropped} dropped, "
          f"across {n_files} record(s)", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
