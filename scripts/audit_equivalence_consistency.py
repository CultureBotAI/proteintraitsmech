#!/usr/bin/env python3
r"""Do the records agree with the equivalence overlay they were built from? (#447)

`data/equivalence/cross_source.tsv` and a record's `mapped_xrefs` say the same thing in
two places — *this member signature is the same entry as that InterPro entry* — and both
are derived from `interpro.xml`'s `member_list`. Nothing compared them.

They disagreed for the whole life of #344. `build_equivalence.py` parsed `member_list`
correctly from the start, so the committed TSV held the right answer while **335 Pfam
records asserted a different InterPro entry**, taken from the abstract that merely
mentions them. A checked-in file in this repo contradicted the corpus for months.

WHY THIS GATE AND NOT `audit-pfam-interpro`. That one is stronger — it compares against
the release itself — and it **cannot run in CI**, because `data/raw/` is gitignored. This
one reads only committed files, so it runs everywhere, on every push. Verified: it reports
335 disagreements on the pre-#344 tree and 0 after.

SCOPE, stated because it is easy to over-read. This is a CONSISTENCY check, not a
correctness one: it proves the two derived artefacts agree, and if both were regenerated
from a bad parse it would pass. It is the cheap gate; `audit-pfam-interpro` is the true
one. Run both locally.

It also only sees the INTERSECTION. `build_equivalence` emits a pair only when BOTH the
member record and the InterPro record exist in the corpus, so of 44,054 subjects asserting
an InterPro xref, 17,970 are comparable and 26,084 are not. That is 41% coverage, printed
on every run — a gate that silently covers part of its subject is how "0 failures" comes
to mean nothing. `audit-pfam-interpro` covers the remainder, against the release.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
TSV = ROOT / "data" / "equivalence" / "cross_source.tsv"

IDENT = re.compile(r"^identifier: (\S+)$", re.M)
# `predicate:` is optional -- MappedXref has the slot and 127 xrefs in this field use it.
XREF = re.compile(r"^[ ]*- object: (InterPro:IPR\d+)[ \t]*\n"
                  r"(?:[ ]*  predicate: .*\n)?"
                  r"[ ]*  mapping_source: (\S+)[ \t]*$", re.M)

# Which `mapping_source` on a record corresponds to which `relation_source` in the TSV.
# Both name the same derivation; the labels differ for historical reasons (#446).
SOURCE_PAIRS = {
    "pfam2interpro": "interpro:pfam",
    "interpro-member-list": None,        # written by seed_interpro_members / seed_panther
}


def load_tsv(path: Path) -> dict[str, set[str]]:
    """subject CURIE -> {InterPro objects} from the committed overlay."""
    out: dict[str, set[str]] = defaultdict(set)
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) >= 3 and cols[2].startswith("InterPro:"):
            out[cols[0]].add(cols[2])
    return out


def _read(path: Path) -> bytes | None:
    """The file's bytes if it could possibly matter, else None.

    Bytes, and the marker test before any decode: 309,177 of the corpus's 429,271 records
    mention no InterPro entry at all, and decoding them to throw them away is most of the
    work.
    """
    raw = path.read_bytes()
    return raw if b"InterPro:" in raw else None


def load_records(traits: Path, workers: int = 8) -> dict[str, set[str]]:
    """subject CURIE -> {InterPro objects} asserted by that record's mapped_xrefs.

    Threaded because this is pure I/O over 429k small files and #416 is an open complaint
    about full-corpus tests being slow: 81s serial, 50s at 8 threads, no better beyond.

    A directory filter would be far faster and is WRONG -- measured: 2,334 of the overlay's
    subjects live outside a directory named after their CURIE prefix, so restricting the
    walk to `*/pfam/`, `*/cdd/` and friends would silently stop checking them. The point of
    this gate is that it is not silently partial.
    """
    out: dict[str, set[str]] = defaultdict(set)
    paths = list(traits.rglob("*.yaml"))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for raw in pool.map(_read, paths, chunksize=256):
            if raw is None:
                continue
            text = raw.decode("utf-8", errors="replace")
            ident = IDENT.search(text)
            if not ident:
                continue
            for obj, src in XREF.findall(text):
                if src in SOURCE_PAIRS:
                    out[ident.group(1)].add(obj)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", type=int, default=12)
    ap.add_argument("--traits-root", default="")
    ap.add_argument("--tsv", default="")
    args = ap.parse_args()

    traits = Path(args.traits_root).resolve() if args.traits_root else TRAITS
    tsv_path = Path(args.tsv).resolve() if args.tsv else TSV
    for p, what in ((traits, "traits root"), (tsv_path, "equivalence TSV")):
        if not p.exists():
            print(f"FAIL: {what} {p} does not exist")
            return 1

    tsv, rec = load_tsv(tsv_path), load_records(traits)
    common = sorted(set(tsv) & set(rec))
    print(f"subjects in the overlay:      {len(tsv):,}")
    print(f"subjects asserting an xref:   {len(rec):,}")
    print(f"comparable (in both):         {len(common):,}")
    if not common:
        # A gate that compared nothing must not report a clean corpus (#418, #432).
        print("FAIL: nothing was comparable. Either the overlay or the records lost their "
              "InterPro assertions; both are a defect, and 0 disagreements is not.")
        return 1
    only_rec = len(set(rec) - set(tsv))
    print(f"not comparable (no overlay row): {only_rec:,}  -- these are UNCHECKED here; "
          f"`just audit-pfam-interpro` covers them against the release")

    bad = [(s, sorted(tsv[s]), sorted(rec[s])) for s in common if tsv[s] != rec[s]]
    print(f"DISAGREE:                     {len(bad):,}")
    for subj, want, got in bad[:args.show]:
        print(f"  {subj}  overlay says {', '.join(want)}  record says {', '.join(got)}")
    if bad:
        print("\nFAIL: a record and the equivalence overlay disagree about the same "
              "mapping. Both derive from interpro.xml's member_list, so one of them was "
              "written from something else — run `just audit-pfam-interpro` to find out "
              "which.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
