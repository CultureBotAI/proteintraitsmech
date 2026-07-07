#!/usr/bin/env python3
"""Seed macromolecular-complex traits from the EBI Complex Portal (ComplexTAB) →
FUNCTION / FUNC_INTERACTION_PARTNER.

A curated stable complex is a reusable, class-level interaction trait ("is a
subunit of complex X, whose partners are …") — unlike raw pairwise PPIs
(IntAct/BioGRID/STRING), which are per-protein-pair instances and are NOT seeded
(protein-trait-sources-round3). One FUNC_INTERACTION_PARTNER record per complex;
its member molecules become `trait_relations` (biolink:has_part) edges — UniProt
subunits, subcomplexes (ComplexPortal), and RNAs (RNAcentral) — and its GO
"complex" annotation becomes the parent trait.

Inputs (fetch via `just fetch-complexportal`, gitignored): one ComplexTAB TSV per
species under data/raw/complexportal/<taxon>.tsv. Columns: 1 Complex ac,
2 Recommended name, 4 Taxonomy id, 5 members (with stoichiometry), 8 GO
annotations, 9 cross references, 10 Description.

Licence: CC0 (EBI Complex Portal / IntAct). Idempotent; dry-run unless --apply.
Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "complexportal"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "interaction_partner" / "complexportal"
LICENSE = "CC0 (EBI Complex Portal)"
GENERIC_COMPLEX = "GO:0032991"          # protein-containing complex
MAX_MEMBERS = 60
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "complex"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


_OBJ_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")


def member_curie(token: str) -> str | None:
    """Map a ComplexTAB member accession to a CURIE for a has_part edge."""
    t = token.strip()
    if not t:
        return None
    if t.startswith("CHEBI:"):
        return None                         # ligands handled elsewhere / skipped
    if t.startswith("CPX-"):
        c = f"ComplexPortal:{t}"
    elif t.startswith("URS"):
        c = f"RNAcentral:{t}"
    elif t.startswith("EBI-"):
        return None                         # internal interactor id
    else:
        c = f"UniProtKB:{t}"                # UniProt accession (maybe isoform/chain)
    return c if _OBJ_RE.match(c) else None


def parse_go(field: str):
    """[(id, name), …] from 'GO:xxxx(name)|GO:yyyy(name)'."""
    out = []
    for m in re.finditer(r"(GO:\d+)\(([^)]*)\)", field or ""):
        out.append((m.group(1), m.group(2)))
    return out


def complex_parent(gos):
    """Most-specific GO complex term (name contains 'complex'), else generic."""
    cand = [gid for gid, nm in gos if "complex" in nm.lower()]
    return cand[0] if cand else GENERIC_COMPLEX


def build_yaml(ac, name, taxon_name, members, subparts, gos, description):
    label = name or ac
    n = len(members) + len(subparts)
    d = description.strip() if description and description.strip() != "-" else \
        f"The {label}."
    tail = f" A curated stable macromolecular complex (Complex Portal) with {n} " \
           f"subunit{'s' if n != 1 else ''}"
    tail += f", from {taxon_name}." if taxon_name else "."
    d = d.rstrip(".") + "." + tail
    lines = [f"identifier: ComplexPortal:{ac}", f"label: {yaml_escape(label)}"]
    f = folded(d)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: Complex Portal", "trait_axis: FUNCTION",
              "trait_category: FUNC_INTERACTION_PARTNER", "term_kind: CLASS",
              "mapping_status: SEEDED",
              "parent_traits:", f"  - {complex_parent(gos)}"]
    rels = ([("biolink:has_part", c) for c in members]
            + [("biolink:has_part", c) for c in subparts])[:MAX_MEMBERS]
    if rels:
        lines.append("trait_relations:")
        for pred, obj in rels:
            lines += [f"  - predicate: {pred}", f"    object: {obj}",
                      "    relation_source: Complex Portal"]
    xr = [gid for gid, _ in gos][:8]
    if xr:
        lines += ["xrefs:"] + [f"  - {x}" for x in xr]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    tsvs = sorted(RAW.glob("*.tsv"))
    if not tsvs:
        print("missing data/raw/complexportal/*.tsv; run `just fetch-complexportal`",
              file=sys.stderr)
        return 2

    written = skipped = total = 0
    for tsv in tsvs:
        for line in tsv.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            c = line.split("\t")
            if len(c) < 10 or not c[0].startswith("CPX-"):
                continue
            ac, name = c[0].strip(), c[1].strip()
            taxon = c[3].strip()
            taxon_name = (re.search(r"\(([^)]+)\)", taxon) or [None, ""])[1]
            members, subparts = [], []
            for tok in c[4].split("|"):
                acc = tok.split("(")[0].strip()
                cur = member_curie(acc)
                if not cur:
                    continue
                (subparts if cur.startswith("ComplexPortal:") else members).append(cur)
            gos = parse_go(c[7])
            total += 1
            path = OUT_DIR / f"{slug(name or ac)}-{ac.lower()}.yaml"
            if path.exists() and not args.force:
                skipped += 1
                continue
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    build_yaml(ac, name, taxon_name, members, subparts, gos, c[9]),
                    encoding="utf-8")
                written += 1

    print(f"Complex Portal: {total} complexes across {len(tsvs)} species → "
          f"FUNC_INTERACTION_PARTNER.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
