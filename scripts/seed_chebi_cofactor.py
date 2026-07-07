#!/usr/bin/env python3
"""Seed cofactor-requirement traits from the ChEBI `cofactor` role subtree
(CHEBI:23357) → FUNCTION / FUNC_COFACTOR_REQUIREMENT.

A protein/enzyme family's requirement for a specific cofactor is a reusable
functional trait ("requires FAD", "requires heme"). ChEBI supplies the reusable
CLASSES: the `cofactor` role (CHEBI:23357) and its is_a subtree (coenzyme,
prosthetic group, siderophore, …) are the abstract cofactor classes, and every
molecular entity that `has_role` one of those roles (FAD, FMN, heme, coenzyme A,
enterobactin, …) is a concrete cofactor. We emit one FUNC_COFACTOR_REQUIREMENT
record per role class and per cofactor molecule, ChEBI-grounded and parent-linked
(molecule → its role class → cofactor). UniProtKB `CC COFACTOR` is the per-protein
evidence layer (not seeded here — the class + ChEBI grounding is the deliverable).

Inputs (fetch via `just fetch-chebi`, gitignored):
  data/raw/chebi/relation.tsv.gz   (id, relation_type_id, init_id, final_id, …)
  data/raw/chebi/compounds.tsv.gz  (id, name, …, definition, ascii_name, …)
Relation types: 4 = has_role, 5 = is_a.

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "chebi"
REL = RAW / "relation.tsv.gz"
CMP = RAW / "compounds.tsv.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "cofactor_requirement" / "chebi"
LICENSE = "CC-BY 4.0 (ChEBI)"
COFACTOR_ROOT = "23357"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_TAG_RE = re.compile(r"<[^>]+>")


def slug(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "cofactor"


def clean(t: str) -> str:
    return " ".join(_TAG_RE.sub("", t or "").split())


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = clean(text)
    return [">-", f"  {text}"] if text else [">-", '  ""']


def load_relations():
    """(role_parent, role_children, mol_roles) restricted to the cofactor subtree."""
    isa_child: dict[str, list[str]] = {}
    isa_parent: dict[str, str] = {}
    hasrole: dict[str, list[str]] = {}
    with gzip.open(REL, "rt", errors="replace") as fh:
        next(fh)
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) < 4:
                continue
            t, init, final = c[1], c[2], c[3]
            if t == "5":
                isa_child.setdefault(final, []).append(init)
                isa_parent[init] = final
            elif t == "4":
                hasrole.setdefault(init, []).append(final)
    # role subtree under COFACTOR_ROOT
    sub, stack = set(), [COFACTOR_ROOT]
    while stack:
        r = stack.pop()
        if r in sub:
            continue
        sub.add(r)
        stack += isa_child.get(r, [])
    role_parent = {r: isa_parent.get(r) for r in sub
                   if isa_parent.get(r) in sub}
    mol_roles = {m: [r for r in rs if r in sub]
                 for m, rs in hasrole.items() if any(r in sub for r in rs)}
    return sub, role_parent, mol_roles


def load_names():
    name: dict[str, str] = {}
    defn: dict[str, str] = {}
    with gzip.open(CMP, "rt", errors="replace") as fh:
        h = next(fh).rstrip("\n").split("\t")
        ix = {k: i for i, k in enumerate(h)}
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) < len(h):
                continue
            i = c[ix["id"]]
            nm = clean(c[ix["name"]] or c[ix["ascii_name"]])
            if nm and nm.lower() != "null":
                name[i] = nm
            d = clean(c[ix["definition"]])
            if d and d.lower() != "null":
                defn[i] = d
    return name, defn


def rid(chid): return f"proteintraitsmech:COFACTOR_REQ_CHEBI_{chid}"


def build(chid, name, defn, parent_curie, is_role, roles=()):
    lab = f"{name} cofactor class" if is_role else f"requires {name}"
    if is_role:
        d = f"The requirement for a {name} — a cofactor class."
    else:
        rn = ", ".join(r for r in roles) if roles else "cofactor"
        d = f"The functional requirement for {name} (CHEBI:{chid}) as a {rn}."
    extra = defn.get(chid, "")
    if extra:
        d = f"{d} {extra}"
    lines = [f"identifier: {rid(chid)}", f"label: {yaml_escape(lab)}"]
    f = folded(d)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: ChEBI", "trait_axis: FUNCTION",
              "trait_category: FUNC_COFACTOR_REQUIREMENT", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent_curie:
        lines += ["parent_traits:", f"  - {parent_curie}"]
    lines += ["xrefs:", f"  - CHEBI:{chid}"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not REL.exists() or not CMP.exists():
        print("missing ChEBI relation/compounds; run `just fetch-chebi`",
              file=sys.stderr)
        return 2
    sub, role_parent, mol_roles = load_relations()
    name, defn = load_names()

    written = skipped = 0

    def emit(chid, text):
        nonlocal written, skipped
        nm = name.get(chid, chid)
        path = OUT_DIR / f"{slug(nm)}-chebi{chid}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    n_roles = n_mols = 0
    # role classes (parent = its parent role in the subtree, if any)
    for r in sorted(sub, key=int):
        if r not in name:
            continue
        parent = rid(role_parent[r]) if r in role_parent and role_parent[r] in name else ""
        emit(r, build(r, name[r], defn, parent, is_role=True))
        n_roles += 1
    # cofactor molecules (parent = its most specific role class)
    for m, roles in mol_roles.items():
        if m not in name:
            continue
        prole = min(roles, key=lambda r: len(role_parent.get(r, "")) or 0) if roles else None
        parent = rid(prole) if prole in name else rid(COFACTOR_ROOT)
        rn = [name.get(r, r) for r in roles]
        emit(m, build(m, name[m], defn, parent, is_role=False, roles=rn))
        n_mols += 1

    print(f"ChEBI cofactor: {n_roles} role classes + {n_mols} cofactor molecules "
          f"→ FUNC_COFACTOR_REQUIREMENT.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {n_roles + n_mols - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
