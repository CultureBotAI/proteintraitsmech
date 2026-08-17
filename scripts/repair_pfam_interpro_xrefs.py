#!/usr/bin/env python3
r"""Repoint the `pfam2interpro` mapped_xrefs that name an entry Pfam is not a member of (#344).

The definition side of #344 is repaired by re-running `enrich_pfam_definitions.py`, which
rewrites a definition it owns. The XREF side cannot be: `mapped_xrefs` is UNIONED on
re-seed and a re-seed cannot REMOVE a stale entry (#120, by design). So the 438 wrong
assertions need an explicit, targeted rewrite. This is it.

Two shapes, and they need opposite treatments:

  * **407 integrated families.** The record asserts `InterPro:<a mention>` and lacks
    `InterPro:<its member_list entry>`. Repoint: the wrong object is replaced by the right
    one, in place, so ordering and neighbouring xrefs are untouched.

  * **31 unintegrated families.** `PF13589` is in NO entry's `member_list` -- confirmed
    against the live InterPro API, `integrated: null` -- so the correct number of
    `pfam2interpro` xrefs is ZERO. The one it carries came from an abstract that mentions
    it. Remove, do not repoint: there is nothing to point at, and inventing a "closest"
    entry is how a mapping error becomes permanent.

GUARDS, in the shape the sibling repair (#431) settled on:

  1. Every target is read from `interpro.xml`'s `member_list` at run time, never from
     `pfam2interpro.tsv` -- the file whose ambiguity caused this.
  2. Only `mapping_source: pfam2interpro` xrefs are touched. A record's own
     `InterPro:` xrefs from any other source, and every non-InterPro xref, are left alone.
  3. The rewrite must change `mapped_xrefs` and NOTHING else: the emitted text is compared
     to the original with the `mapped_xrefs` block masked out, and a record that would
     differ anywhere else is skipped and reported.

Dry-run by default; `--apply` writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from interpro_text import load_member_integration  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
XML_GZ = ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"

IDENT = re.compile(r"^identifier: Pfam:(PF\d{5})$", re.M)
# One `- object: InterPro:X` line and the `mapping_source: pfam2interpro` line under it.
# Anchored to the pair so an InterPro xref from a DIFFERENT source is never matched.
# `predicate:` is OPTIONAL between the two (MappedXref has the slot), so it must be
# tolerated here. No `pfam2interpro` xref uses the 3-key shape today -- but 127 xrefs in
# this very field already do (the Pfam->InterPro->CAZY ones), so it is one curation step
# away, and the failure is silent: the audit would print 0 and exit 0 while the record
# stayed wrong. `[ \t]*$` for the same reason -- a trailing space must not hide a record.
XREF = re.compile(
    r"^(?P<indent>[ ]*)- object: InterPro:(?P<ipr>IPR\d+)[ \t]*\n"
    r"(?:(?P=indent)  predicate: (?P<pred>.*)\n)?"
    r"(?P=indent)  mapping_source: pfam2interpro[ \t]*\n", re.M)


# DETECTION, and deliberately looser than XREF (#462).
#
# `XREF` was both the finder and the fixer: a record whose xref it could not parse returned
# "no pfam2interpro InterPro xref" -- the same answer as a record that genuinely has none.
# A miss was therefore indistinguishable from nothing to do, which is the standing shape
# this repo keeps rediscovering: #461's `[^)]*` skipped 11 notes while printing "repaired:
# 0", and the acceptance test used the same function as its oracle so the gate agreed.
#
# This asks only "does the record assert a pfam2interpro mapping at all?", which no
# reasonable layout can hide. If it says yes and `XREF` sees fewer, the record is STRANDED
# and said so, rather than filed under silence.
#
# 0 of the corpus's 29,105 pfam2interpro xrefs are stranded today -- `XREF` handles every
# shape on disk. That is the point: this exists to make the NEXT shape loud, not to fix a
# present miss.
# THIS PATTERN HAS NOW BEEN TOO NARROW TWICE, which is worth recording because the whole
# point of it is to be the broad one.
#
#   1. `[ \t]*mapping_source:` could not see `- mapping_source: pfam2interpro`, the shape a
#      reordered mapping puts it in -- the first case its own test tried.
#   2. It could not see a QUOTED value (`mapping_source: "pfam2interpro"`), which is what
#      several routine dumper settings emit, nor a flow mapping `- {object: ..., mapping_
#      source: pfam2interpro}`, nor CRLF line endings. A review found all four.
#
# So the second alternative is now just the bare token anywhere in the record. That is
# maximally loose on purpose: this pattern's only job is to answer "does this record
# mention a pfam2interpro mapping at all", and every false positive it produces is a record
# a human then looks at, while every false NEGATIVE is a record nobody ever looks at again.
# The asymmetry is the entire argument for splitting finder from fixer.
LOOSE = re.compile(r"""mapping_source:[ \t]*['"]?pfam2interpro\b""")


def repair_text(text: str, real: str | None) -> tuple[str | None, str]:
    """(new text or None, reason). `real` is the member_list entry, or None if unintegrated."""
    hits = list(XREF.finditer(text))
    loose = len(LOOSE.findall(text))
    if loose > len(hits):
        return None, (f"STRANDED: asserts {loose} pfam2interpro mapping(s) but the "
                      f"rewrite pattern parses only {len(hits)}")
    if not hits:
        return None, "no pfam2interpro InterPro xref"
    wrong = [m for m in hits if m.group("ipr") != real]
    if not wrong:
        return None, "already correct"

    out = text
    if real is None:
        # Unintegrated: drop the assertion entirely, last match first so the earlier
        # spans stay valid.
        for m in reversed(wrong):
            out = out[:m.start()] + out[m.end():]
    else:
        have_real = any(m.group("ipr") == real for m in hits)
        for i, m in enumerate(reversed(wrong)):
            if have_real or i > 0:
                out = out[:m.start()] + out[m.end():]        # a duplicate; just drop it
            else:
                pred = (f"{m.group('indent')}  predicate: {m.group('pred')}\n"
                        if m.group("pred") else "")
                out = (out[:m.start()]
                       + f"{m.group('indent')}- object: InterPro:{real}\n"
                       + pred
                       + f"{m.group('indent')}  mapping_source: pfam2interpro\n"
                       + out[m.end():])

    # A `mapped_xrefs:` key whose every entry was removed leaves a dangling key with no
    # sequence under it -- unparseable YAML, and the exact failure `record_io`'s docstring
    # lists first among "the three mistakes this exists to prevent".
    #
    # For all 31 unintegrated families this is not an edge case, it is the normal outcome:
    # the bogus InterPro xref is their ONLY mapped_xref, because they have no pfam2go
    # terms either. So the key goes with it. Removing the key is CORRECT and not merely
    # convenient -- `mapped_xrefs` is a list of asserted mappings, and after the repair
    # these records assert none.
    if re.search(r"^mapped_xrefs:\n(?![ ]*-)", out, re.M):
        out = re.sub(r"^mapped_xrefs:\n(?![ ]*-)", "", out, count=1, flags=re.M)
        if re.search(r"^mapped_xrefs:", out, re.M):
            return None, "more than one mapped_xrefs key; refusing to guess"
    return out, "repaired"


def _mask(text: str) -> str:
    """The record with its whole `mapped_xrefs` block REMOVED.

    Guard 3: everything outside that block must be byte-identical afterwards. Written as a
    mask-and-compare rather than a diff count so it cannot pass by being approximately
    right.

    Removed rather than replaced by a marker. A marker has to be present on both sides to
    compare, and a record whose last xref was dropped loses the key entirely -- so the
    first version tried to re-insert the marker before `license:`, which worked for 4 of
    the 31 and silently mis-skipped the other 27 as "would change something outside
    mapped_xrefs". Deleting the block on both sides makes "key with entries" and "no key"
    normalise to the same string, which is the actual invariant.
    """
    return re.sub(r"^mapped_xrefs:\n(?:[ ]+.*\n|[ ]*-.*\n)*", "", text, flags=re.M)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N repaired records (the canary)")
    args = ap.parse_args()
    if not XML_GZ.exists():
        print(f"missing {XML_GZ}; run `just fetch-interpro`", file=sys.stderr)
        return 2

    member_of = load_member_integration(XML_GZ)
    print(f"{len(member_of):,} Pfam signatures have an integrating InterPro entry\n")

    paths = sorted(p for p in TRAITS.rglob("*.yaml") if "/pfam/" in str(p))
    repointed = removed = collateral = stranded = 0
    limited = False
    for i, path in enumerate(paths):
        text = path.read_text(encoding="utf-8")
        m = IDENT.search(text)
        if not m:
            continue
        real = member_of.get(m.group(1))
        new, reason = repair_text(text, real)
        if new is None:
            if reason.startswith("STRANDED"):
                # NOT counted with the collateral skips: that number means "wrong, and I
                # can see why". This one means "I cannot even read it", which is worse and
                # must not be averaged into the same line (#462).
                stranded += 1
                print(f"  STRANDED {path.name}: {reason}")
            elif reason.startswith("more than one mapped_xrefs"):
                collateral += 1
                print(f"  SKIPPED {path.name}: {reason}")
            continue
        if _mask(new) != _mask(text):
            collateral += 1
            print(f"  SKIPPED {path.name}: the rewrite would change something outside "
                  f"mapped_xrefs")
            continue
        if real is None:
            removed += 1
        else:
            repointed += 1
        if args.apply:
            path.write_text(new, encoding="utf-8")
        if args.limit and repointed + removed >= args.limit:
            print(f"\n--limit {args.limit} reached; {len(paths) - i - 1:,} record(s) were "
                  f"not examined. The counts below are not a survey.")
            limited = True
            break

    verb = "" if args.apply else "would "
    print(f"\n{verb}repoint {repointed:,} xref(s) to the member_list entry")
    print(f"{verb}remove  {removed:,} xref(s) from families InterPro does not integrate")
    if collateral:
        print(f"SKIPPED {collateral:,} whose rewrite would have touched more than "
              f"mapped_xrefs -- still wrong, and listed above")
    if stranded:
        print(f"FAIL: {stranded:,} record(s) assert a pfam2interpro mapping in a shape "
              f"the rewrite pattern cannot parse. They are unexamined, not clean -- "
              f"widen XREF or fix them by hand.")
    if not args.apply and not limited:
        print("\ndry run -- nothing written. Re-run with --apply.")
    return 1 if (collateral or stranded) else 0


if __name__ == "__main__":
    raise SystemExit(main())
