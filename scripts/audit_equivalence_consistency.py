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

COVERAGE, IN BOTH DIRECTIONS, because the first version reported one of them and framed
the other away. It printed "41% comparable" over a denominator that included 14,949
subjects which can NEVER be comparable, and said nothing at all about the reverse gap.
Measured, and now printed per run:

    17,970  comparable          every one of them Pfam
    11,135  record asserts an xref, no overlay row      (the InterPro record is not seeded)
    14,949  source outside the overlay's vocabulary     PANTHER/HAMAP/PRINTS/SFLD (#450)
     6,329  overlay row, record asserts no xref         CDD 3,749 / PROSITE 2,334 / NCBIfam 246

So the honest headline is not 41%: of the 29,105 Pfam signatures this gate COULD compare,
it compares 17,970 — **61.7%**. The 14,949 are not a gap this check could close, because
`build_equivalence.member_curie` maps five member DBs and PANTHER is not among them; they
were padding the denominator. And the 6,329 are a real hole in the opposite direction that
went unmentioned: those records cite InterPro in prose and co-occurrence lists but assert
no `mapped_xrefs`, so the overlay makes a claim about them that nothing checks.

`audit-pfam-interpro` covers the 11,135 against the release. Nothing covers the 6,329.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
TSV = ROOT / "data" / "equivalence" / "cross_source.tsv"

IDENT = re.compile(r"^identifier: (\S+)$", re.M)
# `predicate:` is optional because `MappedXref` has the slot. Measured: the branch matches
# NOTHING today -- with and without it the sweep finds the same 44,054 -- so it is
# future-proofing, not a live matcher. The 127 three-key xrefs that do exist carry
# `object: CAZy:*`, which this pattern could never match anyway. Kept because the shape is
# schema-legal and a miss here is silent (see `load_records`).
XREF = re.compile(r"^[ ]*- object: (InterPro:IPR\d+)[ \t]*\n"
                  r"(?:[ ]*  predicate: .*\n)?"
                  r"[ ]*  mapping_source: (\S+)[ \t]*$", re.M)

# `mapping_source` values that assert "this signature IS that InterPro entry" -- the claim
# the overlay also makes. Both labels name the same derivation from `member_list`; they
# differ for historical reasons (#446).
#
# A SET, not a dict. It was a dict mapping to the TSV's `relation_source`, and the values
# were never read -- `load_tsv` filters on the object prefix alone. Worse than dead: the
# `interpro-member-list -> None` entry asserted a correspondence that does not exist,
# since no PANTHER/HAMAP/PRINTS/SFLD subject can appear in the overlay at all today.
ACCEPTED_SOURCES = frozenset({"pfam2interpro", "interpro-member-list"})


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

    Errors are re-raised NAMING THE PATH. Unhandled, a pool worker gives a 20-line
    traceback whose deepest frame is inside `concurrent.futures` -- verified by putting a
    directory called `x.yaml` under a traits root -- and in CI that is indistinguishable
    from the disagreement this gate exists to report.
    """
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise OSError(f"could not read {path}: {exc}") from exc
    return raw if b"InterPro:" in raw else None


def load_records(traits: Path, workers: int = 8) -> dict[str, set[str]]:
    """subject CURIE -> {InterPro objects} asserted by that record's mapped_xrefs.

    Threaded because this is pure I/O over 429k small files and #416 is an open complaint
    about full-corpus tests being slow. Roughly halves it -- 62s to 32s at 8 workers here,
    nothing past 8 -- though the absolutes move a lot with cache state.

    WHY THE WHOLE CORPUS, stated correctly on the second attempt. The first version said a
    `*/pfam/`-style filter "would silently stop checking" 2,334 subjects that live outside
    a directory named after their CURIE prefix. Those 2,334 are all PROSITE, and PROSITE
    contributes ZERO comparisons today -- every one of the 17,970 comparable subjects is
    under a `pfam/` directory, so the filter would in fact give the identical result far
    faster. The honest reason is future-proofing: the moment #450 widens the overlay to
    PANTHER, or a CDD record starts asserting `mapped_xrefs`, a prefix filter starts
    hiding real work, and a gate that narrows silently is the failure this file exists to
    prevent. Walking everything costs ~30s and cannot go stale.
    """
    out: dict[str, set[str]] = defaultdict(set)
    missed = 0
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
                if src in ACCEPTED_SOURCES:
                    out[ident.group(1)].add(obj)
            # FAIL LOUD, NOT OPEN. `XREF` is a regex over YAML text, so it silently
            # returns nothing for shapes it was not written for -- `mapping_source` before
            # `object`, a quoted object, CRLF, flow style. Every one of those makes an
            # xref invisible and the gate green, which is the worst direction for a check
            # whose whole output is "0 disagreements". Nothing in the corpus uses them
            # today; this counts the difference so a serializer change is reported rather
            # than absorbed.
            missed += (text.count("mapping_source: pfam2interpro")
                       + text.count("mapping_source: interpro-member-list")
                       - sum(1 for _o, s in XREF.findall(text) if s in ACCEPTED_SOURCES))
    if missed:
        raise ValueError(
            f"{missed} `mapping_source` line(s) naming an accepted source were not matched "
            f"by XREF. The records use a mapped_xrefs shape this check cannot read, so its "
            f"'0 disagreements' would be meaningless. Fix the pattern, do not raise the "
            f"threshold.")
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

    # Which CURIE prefixes the overlay can represent AT ALL, derived from the overlay
    # rather than hardcoded: `build_equivalence.member_curie` maps five member DBs, and if
    # #450 extends it this report widens by itself instead of going stale.
    overlay_prefixes = {k.split(":", 1)[0] for k in tsv}
    rec_only = set(rec) - set(tsv)
    unrepresentable = {k for k in rec_only if k.split(":", 1)[0] not in overlay_prefixes}
    absent_from_overlay = rec_only - unrepresentable
    tsv_only = set(tsv) - set(rec)

    def _by_prefix(keys):
        c = Counter(k.split(":", 1)[0] for k in keys)
        return " ".join(f"{p} {n:,}" for p, n in c.most_common())

    print(f"overlay subjects:             {len(tsv):,}   ({_by_prefix(tsv)})")
    print(f"records asserting an xref:    {len(rec):,}   ({_by_prefix(rec)})")
    print(f"COMPARABLE (in both):         {len(common):,}")
    if not common:
        # A gate that compared nothing must not report a clean corpus (#418, #432).
        print("FAIL: nothing was comparable. Either the overlay or the records lost their "
              "InterPro assertions; both are a defect, and 0 disagreements is not.")
        return 1
    achievable = len(common) + len(absent_from_overlay)
    print(f"  of the {achievable:,} this check COULD compare, it compares "
          f"{100 * len(common) / achievable:.1f}%")
    print("\nNOT compared, and why -- both directions, because reporting one of them and "
          "framing the other away is how a partial gate reads as a complete one:")
    print(f"  {len(absent_from_overlay):,}  record asserts an xref, no overlay row "
          f"(the InterPro record is not seeded) -- `just audit-pfam-interpro` covers these")
    print(f"  {len(unrepresentable):,}  source outside the overlay's vocabulary "
          f"({_by_prefix(unrepresentable)}) -- NOTHING covers these (#450)")
    print(f"  {len(tsv_only):,}  overlay row, record asserts no xref "
          f"({_by_prefix(tsv_only)}) -- NOTHING covers these either")

    bad = [(s, sorted(tsv[s]), sorted(rec[s])) for s in common if tsv[s] != rec[s]]
    print(f"\nDISAGREE:                     {len(bad):,}")
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
