#!/usr/bin/env python3
r"""Does each Pfam record cite the InterPro entry that actually integrates it? (#344)

A Pfam record borrows two things from InterPro, and both name an entry:

    definition_source: "InterPro:IPR000834 abstract (Pfam PF00246 maps to this entry …)"
    mapped_xrefs:      - object: InterPro:IPR000834
                         mapping_source: pfam2interpro

If that entry is not the one whose `member_list` contains the signature, the record has
borrowed a DIFFERENT domain's prose. Which is not a hypothetical: 407 records had exactly
that, because `pfam2interpro.tsv` conflates two relations —

    <member_list><db_xref db="PFAM" dbkey="PF00575" name="S1"/></member_list>
        IPR003029 IS the integration of PF00575

    <abstract>… associated with <db_xref db="PFAM" dbkey="PF00575"/> …</abstract>
        IPR059328 merely MENTIONS PF00575 in prose

— and the readers took the last row. The resulting definitions are the worst kind of
wrong: fluent, on-topic, and self-consistent, because the abstract that mentions a Pfam
accession is usually about its NEIGHBOUR. `Pfam:PF13646` ("HEAT repeats") received *"This
domain is found in conserved virulence factors. It is often found in association with
Pfam:PF13646"* — an abstract stating, in the record's own definition field, that it is
about something else.

WHY NOTHING CAUGHT IT. `validate-all` sees a well-formed string. `audit-prose` asks
whether a definition reads as prose, and this reads beautifully. The InterPro accession
resolves, so any link check passes. The only way to see it is to compare the cited entry
against the release's own member list, which is what this does.

Exit 1 on any mismatch. There is no baseline and no ceiling, deliberately: unlike the
archetype question (#425), this one has no legitimate instances — either the release says
a signature integrates into an entry or it does not.
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
DEF_SRC = re.compile(r'^definition_source: "InterPro:(IPR\d+) abstract', re.M)
# `predicate:` is OPTIONAL between the two (MappedXref has the slot), so it must be
# tolerated here. No `pfam2interpro` xref uses the 3-key shape today -- but 127 xrefs in
# this very field already do (the Pfam->InterPro->CAZY ones), so it is one curation step
# away, and the failure is silent: the audit would print 0 and exit 0 while the record
# stayed wrong. `[ \t]*$` for the same reason -- a trailing space must not hide a record.
XREF = re.compile(
    r"^(?P<indent>[ ]*)- object: InterPro:(?P<ipr>IPR\d+)[ \t]*\n"
    r"(?:(?P=indent)  predicate: .*\n)?"
    r"(?P=indent)  mapping_source: pfam2interpro[ \t]*$", re.M)


def audit(traits: Path, member_of: dict[str, str]):
    """(definition failures, xref failures, records examined)."""
    bad_def, bad_xref, seen = [], [], 0
    for path in sorted(p for p in traits.rglob("*.yaml") if "/pfam/" in str(p)):
        text = path.read_text(encoding="utf-8")
        m = IDENT.search(text)
        if not m:
            continue
        seen += 1
        pf = m.group(1)
        real = member_of.get(pf)          # None => InterPro integrates it nowhere
        ds = DEF_SRC.search(text)
        if ds and ds.group(1) != real:
            bad_def.append((path, pf, ds.group(1), real))
        for x in XREF.finditer(text):
            if x.group("ipr") != real:
                bad_xref.append((path, pf, x.group("ipr"), real))
    return bad_def, bad_xref, seen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", type=int, default=12)
    ap.add_argument("--traits-root", default="", help="override data/traits (for tests)")
    ap.add_argument("--xml", default="", help="override interpro.xml.gz (for tests)")
    args = ap.parse_args()

    xml = Path(args.xml).resolve() if args.xml else XML_GZ
    if not xml.exists():
        # NOT a pass. The whole check is "compare against the release", so without the
        # release there is nothing to compare and reporting 0 would be a lie of exactly
        # the kind #432 was filed for.
        print(f"FAIL: {xml} is absent (data/raw is gitignored); run `just fetch-interpro`. "
              f"Without it this check has no reference and cannot report anything.")
        return 1
    traits = Path(args.traits_root).resolve() if args.traits_root else TRAITS
    if not traits.is_dir():
        print(f"FAIL: --traits-root {traits} is not a directory")
        return 1

    member_of = load_member_integration(xml)
    bad_def, bad_xref, seen = audit(traits, member_of)
    print(f"Pfam records examined:        {seen:,}")
    if not seen:
        # #418's silent bypass, one axis over: `is_dir()` was ported but "0 records" was
        # not, so `--traits-root data/traits/function` -- a real directory with no Pfam
        # records -- printed "0 examined, 0 wrong" and exited 0. The recipe forwards
        # {{args}}, which makes that a one-flag pass through a merge gate.
        print(f"FAIL: no Pfam records found under {traits}. A check that examined nothing "
              f"must not report a clean corpus.")
        return 1
    print(f"InterPro entries with a Pfam member: {len(member_of):,}")
    print(f"definition_source names a non-integrating entry: {len(bad_def):,}")
    print(f"mapped_xrefs assert a non-integrating entry:     {len(bad_xref):,}")
    for path, pf, got, real in (bad_def + bad_xref)[:args.show]:
        print(f"  {path.name}  {pf}  cites {got}  but member_list says "
              f"{real or '(no entry integrates it)'}")
    if bad_def or bad_xref:
        print("\nFAIL: run `just repair-pfam-interpro` (definitions and xrefs, in that "
              "order) — both are deterministic from the release.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
