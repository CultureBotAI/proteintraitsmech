#!/usr/bin/env python3
"""Restore the cross-references `clean_abstract` deleted from definitions (#159).

Every seeder that reads an InterPro abstract stripped inline `<db_xref/>`
elements along with the markup, deleting the accession the sentence was about:

    This domain is usually find associated with <db_xref db="PFAM" dbkey="PF07730"/> .
    ->  This domain is usually find associated with .

`interpro_text.clean_abstract` now substitutes those as CURIEs. This rewrites the
records already on disk.

WHY NOT JUST RE-SEED
--------------------
A `--force` re-seed goes through `record_io.write_record` -> `merge_on_reseed`,
which for a curated record restores `CURATED_SCALARS` from the file -- so
`definition` reverts to the damaged text -- and drops the fresh `definitions[]`
entry as a same-source restatement (#148). The re-seed would report success and
change nothing. This is an in-place edit and writes directly.

THE SAFETY GATE
---------------
A record is rewritten only when its stored definition is byte-identical to what
the OLD cleaner produced from the same abstract. That proves the text is
untouched seeder output; anything a curator has edited no longer matches and is
skipped. The old cleaner is reproduced here verbatim rather than imported,
because the point is to compare against behaviour that no longer exists.

Dry-run by default; --apply writes.
"""
from __future__ import annotations

import argparse
import gzip
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from interpro_text import clean_abstract  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
INTERPRO = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
TRAITS = REPO_ROOT / "data" / "traits"
DEF_CAP = 1800

_IPR_IN_SOURCE = re.compile(r"(IPR\d{6})")
_DEF = re.compile(r"^definition: >-\n  (.*)$", re.M)
_SRC = re.compile(r"^definition_source: (.*)$", re.M)
_IDENT = re.compile(r"^identifier: (\S+)", re.M)


def old_clean_string(raw: str) -> str:
    """seed_panther / seed_interpro_members, before #159."""
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"\[\s*(,\s*)*\]", "", txt)
    txt = re.sub(r"\s+([.,;:])", r"\1", txt)
    return " ".join(txt.split())


def old_clean_element(raw: str) -> str:
    """seed_interpro, before #159: itertext() plus a wider bracket sweep.

    `itertext()` yields only text nodes, so an empty `<db_xref/>` contributed
    nothing at all -- which is why InterPro's own records show no empty-paren
    tell while PANTHER's do. Same deletion, different leftovers.
    """
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    txt = " ".join(txt.split())
    txt = re.sub(r"\s*[\[(]\s*(?:,\s*)*[\])]", "", txt)
    return " ".join(txt.split())


def interpro_abstracts() -> dict[str, str]:
    """InterPro accession -> the RAW abstract XML, so both cleaners can run."""
    if not INTERPRO.exists():
        print(f"missing {INTERPRO} — run `just fetch-interpro`", file=sys.stderr)
        raise SystemExit(2)
    out: dict[str, str] = {}
    cur = None
    inabs = False
    buf: list[str] = []
    ent = re.compile(r'<interpro id="(IPR\d+)"')
    with gzip.open(INTERPRO, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = ent.search(line)
            if m:
                cur, inabs, buf = m.group(1), False, []
                continue
            if cur is None:
                continue
            a = re.search(r"<abstract[^>]*>", line)
            if a:
                inabs = "</abstract>" not in line
                body = ([] if inabs
                        else [line[a.end():].split("</abstract>", 1)[0]])
                buf = body
                if not inabs:
                    out[cur] = " ".join(buf)
                continue
            if inabs:
                if "</abstract>" in line:
                    inabs = False
                    out[cur] = " ".join(buf)
                else:
                    buf.append(line)
    return out


def _cap(text: str) -> str:
    """seed_interpro's cap: truncate and mark it."""
    return text[: DEF_CAP - 1].rstrip() + "…" if len(text) > DEF_CAP else text


def _slice(text: str) -> str:
    """seed_panther's and seed_interpro_members' cap: a plain slice, no marker.

    Two different truncations of the same abstract, so a repair that models only
    one silently skips every long record seeded by the other -- 271 of 2,394 in
    HAMAP alone, which is what surfaced this.
    """
    return text[:DEF_CAP]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("path", nargs="?", default=str(TRAITS))
    args = ap.parse_args()

    abstracts = interpro_abstracts()
    print(f"InterPro abstracts indexed: {len(abstracts):,}", file=sys.stderr)

    repaired = already = unchanged = skipped = 0
    restored = 0
    for path in sorted(Path(args.path).rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        sm, dm = _SRC.search(text), _DEF.search(text)
        if not (sm and dm):
            continue
        src = sm.group(1)
        if "InterPro" not in src:
            continue
        # Two shapes. Member-DB seeders name the entry in the source
        # ("InterPro:IPR012345 abstract (...)"); seed_interpro writes a bare
        # `definition_source: InterPro` and the accession is the record's own
        # identifier. Keying only on the source excluded all 21,357 of the
        # latter -- the largest single group of affected records.
        ipr_m = _IPR_IN_SOURCE.search(src)
        if ipr_m is None:
            im = _IDENT.search(text)
            ipr_m = _IPR_IN_SOURCE.search(im.group(1)) if im else None
        raw = abstracts.get(ipr_m.group(1)) if ipr_m else None
        if raw is None:
            continue

        new = clean_abstract(raw)
        current = dm.group(1)
        # Two old cleaners produced two different strings from one abstract;
        # a record could have come from either.
        olds = (old_clean_string(raw), old_clean_element(raw))
        candidates = {f(o) for o in olds for f in (_cap, _slice, str)}
        # Reproduce the cap the record was written with, so a repaired long
        # definition keeps the same length policy it had.
        capped_new = _slice(new) if current == _slice(olds[0]) or \
            current == _slice(olds[1]) else _cap(new)
        if current in (capped_new, new, _cap(new), _slice(new)):
            already += 1
            continue
        if current not in candidates:
            skipped += 1                  # curated, or from a different release
            continue
        if capped_new == current:
            unchanged += 1
            continue

        out = text.replace(current, capped_new)
        if out == text:
            skipped += 1
            continue
        if args.apply:
            # In-place edit, not a re-seed: merge_on_reseed would revert it (#148).
            path.write_text(out, encoding="utf-8")
        repaired += 1
        restored += len(re.findall(r'<db_xref\s', raw))
        if args.limit and repaired >= args.limit:
            break

    verb = "repaired" if args.apply else "would repair"
    print(f"{verb}: {repaired:,} records; ~{restored:,} cross-references restored")
    print(f"  already correct                 : {already:,}")
    if unchanged:
        print(f"  no change once re-cleaned       : {unchanged:,}")
    if skipped:
        print(f"  skipped (curated or unmatched)  : {skipped:,}")
    if args.limit and repaired >= args.limit:
        print(f"  PARTIAL: stopped at --limit {args.limit}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
