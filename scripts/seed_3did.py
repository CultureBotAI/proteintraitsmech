#!/usr/bin/env python3
"""Seed domain–domain interaction interfaces from 3did → STRUCTURE /
STRUCT_INTERFACE.

3did catalogues the structural interfaces between Pfam domain families observed in
PDB structures — each domain–domain interaction (a Pfam pair) is a reusable,
class-level structural interface. This fills the near-empty STRUCT_INTERFACE
category (structure-derived, so STRUCTURE axis; complements the functional
FUNC_INTERACTION_PARTNER view from Complex Portal).

One STRUCT_INTERFACE class per Pfam-pair interaction: grounded to both Pfam
domains (xrefs), with a few representative PDB structures as
`structural_geometry_representations`.

Input (fetch via `just fetch-3did`, gitignored):
  data/raw/3did/3did_flat.gz — blocks per interaction:
    #=ID <name1> <name2> (PF#.v@Pfam  PF#.v@Pfam)
    #=3D <pdb> <chain:range> <chain:range> <score> <z> <n:n>   (representatives)
    <residue-residue contact lines>

Licence: 3did (IRB Barcelona) — no explicit open licence (FLAGGED), like BioLiP2 /
MetalPDB. Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "3did" / "3did_flat.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure" / "interface" / "3did"
LICENSE = "3did (IRB Barcelona) — no explicit open license (FLAGGED)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_PF = re.compile(r"(PF\d+)")


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:40]) or "dom"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}
            or re.fullmatch(r"-?\d+(?:\.\d+)?", text)):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


def build_yaml(name1, name2, pf1, pf2, pdbs):
    pdbs = list(dict.fromkeys(pdbs))             # dedupe (a pair has many #=3D per PDB)
    ident = "proteintraitsmech:INTERFACE_" + "_".join(sorted([pf1, pf2]))
    label = f"{name1}–{name2} domain interface"
    defn = (f"The structural interface between the {name1} and {name2} domains "
            f"(Pfam {pf1}–{pf2}), observed in {len(pdbs)} PDB "
            f"structure{'s' if len(pdbs) != 1 else ''} — a domain–domain "
            f"interaction interface from 3did.")
    lines = [f"identifier: {ident}", f"label: {yaml_escape(label)}"]
    f = folded(defn)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: 3did", "trait_axis: STRUCTURE",
              "trait_category: STRUCT_INTERFACE", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    xr = list(dict.fromkeys([pf1, pf2]))
    lines += ["xrefs:"] + [f"  - Pfam:{x}" for x in xr]
    if pdbs:
        lines.append("structural_geometry_representations:")
        for pdb in pdbs[:5]:
            lines += [f"  - structure_ref: PDB:{pdb}", "    structure_source: 3did"]
    lines.append(f"license: {yaml_escape(LICENSE)}")
    return ident, "_".join(sorted([pf1, pf2])), "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/3did/3did_flat.gz; run `just fetch-3did`")
        return 2

    written = skipped = total = 0
    seen: set = set()
    cur = None                                   # (name1, name2, pf1, pf2, [pdbs])

    def flush():
        nonlocal written, skipped, total
        if not cur:
            return
        name1, name2, pf1, pf2, pdbs = cur
        key = tuple(sorted([pf1, pf2]))
        if key in seen:                          # A-B and B-A → one class
            return
        seen.add(key)
        total += 1
        ident, pairslug, text = build_yaml(name1, name2, pf1, pf2, pdbs)
        path = OUT_DIR / f"{slug(name1)}-{slug(name2)}-{pairslug.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    with gzip.open(RAW, "rt", errors="replace") as fh:
        for line in fh:
            if line.startswith("#=ID"):
                flush()
                c = line.split("\t")
                pfs = _PF.findall(line)
                if len(c) >= 3 and len(pfs) >= 2:
                    cur = (c[1].strip(), c[2].strip(), pfs[0], pfs[1], [])
                else:
                    cur = None
            elif line.startswith("#=3D") and cur:
                parts = line.split("\t")
                if len(parts) >= 2:
                    cur[4].append(parts[1].strip())
    flush()

    print(f"3did: {total} domain–domain interface classes → STRUCT_INTERFACE.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
