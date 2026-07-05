#!/usr/bin/env python3
"""Backfill real PROSITE prose into definitions from prosite.doc (the PDOC
documentation) — record-sample-review-1 S1 for PROSITE, unblocked once
prosite.doc is fetched (fetch-prosite). In place, so record enrichment
(sequence_pattern, parents, license, examples) is preserved.

  PDOC group records (SEQ_FAMILY)   identifier PROSITE:PDOC…  -> its prose
  PS pattern/profile records         identifier PROSITE:PS…    -> its PDOC's prose
  ProRule records (SEQ_DOMAIN/site)  identifier PROSITE:PRU…   -> PRU→PS→PDOC prose

The definition = the PDOC title + its first prose paragraph (capped at a sentence
boundary), replacing the old label-restated / boilerplate definitions. Idempotent;
dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
DOC = REPO_ROOT / "data" / "raw" / "prosite.doc"
PRORULE = REPO_ROOT / "data" / "raw" / "prorule.dat"

ID_RE = re.compile(r"^identifier:\s*(\S+)", re.M)
MAXLEN = 700


def build_maps() -> tuple[dict[str, str], dict[str, str]]:
    """Return (pdoc_id -> definition prose, ps_id -> pdoc_id)."""
    txt = DOC.read_text(encoding="utf-8", errors="replace")
    pdoc_prose, ps_to_pdoc = {}, {}
    for b in re.split(r"^\{PDOC", txt, flags=re.M)[1:]:
        pid = "PDOC" + b[:8].split("}")[0]
        for ps in re.findall(r"^\{(PS\d+);", b, re.M):
            ps_to_pdoc[ps] = pid
        m = re.search(r"\{BEGIN\}(.*?)\{END\}", b, re.S)
        if not m:
            continue
        title, prose, started = "", [], False
        for l in m.group(1).split("\n"):
            s = l.strip()
            if s and set(s) <= {"*"}:                 # banner ***
                continue
            if s.startswith("*") and s.endswith("*"):  # * Title *
                title = s.strip("* ").strip()
                continue
            if not started and not s:
                continue
            if started and not s:                      # end of first paragraph
                break
            started = True
            prose.append(s)
        definition = ((title + ". ") if title else "") + " ".join(prose)
        definition = re.sub(r"\s*\[[0-9E][0-9E,\s]*(?:to\s*[0-9E]+)?\]", "", definition)  # drop [1]/[E1]/[1 to 5] refs
        definition = " ".join(definition.split())
        if len(definition) > MAXLEN:                   # trim to last sentence < cap
            cut = definition.rfind(". ", 0, MAXLEN)
            definition = definition[:cut + 1] if cut > 200 else definition[:MAXLEN].rstrip() + "…"
        pdoc_prose[pid] = definition
    return pdoc_prose, ps_to_pdoc


def pru_to_ps() -> dict[str, str]:
    """ProRule AC -> a representative PROSITE PS id, from prorule.dat TR lines."""
    out = {}
    if not PRORULE.exists():
        return out
    ac = None
    for line in PRORULE.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("AC "):
            ac = line.split()[1].rstrip(";")
        elif line.startswith("TR ") and ac and ac not in out:
            m = re.search(r"(PS\d+)", line)
            if m:
                out[ac] = m.group(1)
    return out


def set_definition(text: str, new_def: str) -> str:
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("definition:"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                j += 1
            block = ["definition: >-", "  " + " ".join(new_def.split())]
            return "\n".join(lines[:i] + block + lines[j:])
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not DOC.exists():
        print("missing data/raw/prosite.doc; run `just fetch-prosite`", file=sys.stderr)
        return 2

    pdoc_prose, ps_to_pdoc = build_maps()
    pru_ps = pru_to_ps()

    def prose_for(ident: str) -> str | None:
        kind = ident.split(":", 1)[1]
        if kind.startswith("PDOC"):
            return pdoc_prose.get(kind)
        if kind.startswith("PS"):
            return pdoc_prose.get(ps_to_pdoc.get(kind, ""))
        if kind.startswith("PRU"):
            return pdoc_prose.get(ps_to_pdoc.get(pru_ps.get(kind, ""), ""))
        return None

    dirs = ["sequence/family/prosite", "sequence/pattern", "sequence/profile",
            "sequence/domain/prosite", "sequence/prorule"]
    counts = {}
    for sub in dirs:
        base = TRAITS / sub
        if not base.exists():
            continue
        n = 0
        for path in base.rglob("*.yaml"):
            text = path.read_text(encoding="utf-8", errors="replace")
            m = ID_RE.search(text)
            if not m or not m.group(1).startswith("PROSITE:"):
                continue
            prose = prose_for(m.group(1))
            if not prose:
                continue
            new = set_definition(text, prose)
            if new != text:
                n += 1
                if args.apply:
                    path.write_text(new, encoding="utf-8")
        counts[sub] = n

    verb = "updated" if args.apply else "would update"
    print(f"{verb} ({sum(counts.values()):,} total):")
    for s, n in counts.items():
        print(f"  {s:28s} {n:>6,}")
    if not args.apply:
        print("dry-run; pass --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
