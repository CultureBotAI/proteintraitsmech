#!/usr/bin/env python3
"""Seed the complete Enzyme Commission (EC) hierarchy from ExPASy ENZYME
→ FUNCTION / FUNC_ENZYMATIC_ACTIVITY.

Supersedes the earlier trait-onto-map EC subset: seeds every EC **leaf**
(enzyme.dat) plus the internal class / subclass / sub-subclass nodes
(enzclass.txt), parent-chained (1.1.1.2 → 1.1.1.- → 1.1.-.- → 1.-.-.-).

Groundings / provenance:
  - DE name = label; AN = synonyms; CA reaction → definition.
  - ec2go GO           → mapped_xrefs (mapping_source ec2go)
  - rhea2ec RHEA        → mapped_xrefs (mapping_source rhea2ec)
  - KEGG (folded from the trait-onto-map records this replaces) → xrefs (direct)
  - up to 3 Swiss-Prot DR accessions → canonical_examples (sequence-refreshable
    later by fetch_uniprot_examples).

"Transferred entry" / "Deleted entry" stubs are skipped. Idempotent; dry-run
unless --apply. Stdlib-only.

Inputs (fetch via `just fetch-ec`, gitignored):
  data/raw/ec/enzyme.dat, data/raw/ec/enzclass.txt
  data/raw/mappings/ec2go, data/raw/rhea/rhea2ec.tsv (optional groundings)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "ec"
ENZYME = RAW / "enzyme.dat"
ENZCLASS = RAW / "enzclass.txt"
EC2GO = REPO_ROOT / "data" / "raw" / "mappings" / "ec2go"
RHEA2EC = REPO_ROOT / "data" / "raw" / "rhea" / "rhea2ec.tsv"
TOM_DIR = REPO_ROOT / "data" / "traits" / "function" / "enzymatic_activity" / "traitontomap"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "enzymatic_activity" / "ec"
LICENSE = "CC-BY 4.0"
DEF_CAP = 900
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "ec"


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
    if len(text) > DEF_CAP:
        text = text[:DEF_CAP - 1].rstrip() + "…"
    return [">-", f"  {text}"]


def ec_parent(ec: str) -> str | None:
    """1.1.1.2 → 1.1.1.- ; 1.1.1.- → 1.1.-.- ; 1.-.-.- → None."""
    a, b, c, d = (ec.split(".") + ["-", "-", "-", "-"])[:4]
    if d != "-":
        return f"{a}.{b}.{c}.-"
    if c != "-":
        return f"{a}.{b}.-.-"
    if b != "-":
        return f"{a}.-.-.-"
    return None


def load_ec2go() -> dict[str, list[str]]:
    m: dict[str, list[str]] = {}
    if EC2GO.exists():
        ec_re = re.compile(r"EC:(\d+\.\d+\.\d+\.\d+)")
        go_re = re.compile(r"(GO:\d{7})")
        for line in EC2GO.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("!"):
                continue
            em, gm = ec_re.search(line), (go_re.search(line.split(";")[-1]) if ";" in line else None)
            if em and gm:
                m.setdefault(em.group(1), []).append(gm.group(1))
    return m


def load_rhea2ec() -> dict[str, list[str]]:
    m: dict[str, list[str]] = {}
    if RHEA2EC.exists():
        for i, line in enumerate(RHEA2EC.read_text(encoding="utf-8", errors="replace").splitlines()):
            if i == 0:
                continue
            cols = line.split("\t")
            if len(cols) >= 4 and re.match(r"^\d+\.\d+\.\d+\.\d+$", cols[3].strip()):
                m.setdefault(cols[3].strip(), []).append(f"RHEA:{cols[2].strip()}")
    return m


def load_tom_kegg() -> dict[str, list[str]]:
    """EC → [KEGG:…] harvested from the trait-onto-map records this seeder
    supersedes, so their direct KEGG links survive the migration."""
    import yaml
    m: dict[str, list[str]] = {}
    if not TOM_DIR.exists():
        return m
    for p in TOM_DIR.rglob("*.yaml"):
        try:
            d = yaml.safe_load(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        ident = str(d.get("identifier", ""))
        if not ident.startswith("EC:"):
            continue
        kegg = [x for x in (d.get("xrefs") or []) if str(x).startswith("KEGG:")]
        if kegg:
            m[ident.split(":", 1)[1]] = kegg
    return m


def parse_enzclass() -> dict[str, str]:
    nodes: dict[str, str] = {}
    if not ENZCLASS.exists():
        return nodes
    rx = re.compile(r"^\s*(\d+)\.\s*([0-9-]+)\.\s*([0-9-]+)\.\s*([0-9-]+)\s+(.+?)\.?\s*$")
    for line in ENZCLASS.read_text(encoding="utf-8", errors="replace").splitlines():
        m = rx.match(line)
        if m:
            ec = f"{m.group(1)}.{m.group(2)}.{m.group(3)}.{m.group(4)}"
            nodes[ec] = m.group(5).strip()
    return nodes


def parse_enzyme():
    """Yield dicts for each non-obsolete EC leaf in enzyme.dat."""
    if not ENZYME.exists():
        return
    cur = None
    for line in ENZYME.read_text(encoding="utf-8", errors="replace").splitlines():
        tag, _, rest = line.partition("   ")
        if tag == "ID":
            cur = {"ec": rest.strip(), "de": [], "an": [], "ca": [], "dr": []}
        elif cur is None:
            continue
        elif tag == "DE":
            cur["de"].append(rest.strip())
        elif tag == "AN":
            cur["an"].append(rest.strip().rstrip("."))
        elif tag == "CA":
            cur["ca"].append(rest.strip())
        elif tag == "DR":
            for pair in rest.split(";"):
                pair = pair.strip()
                if "," in pair:
                    acc, name = pair.split(",", 1)
                    cur["dr"].append((acc.strip(), name.strip()))
        elif line.startswith("//"):
            if cur and cur["ec"]:
                de = " ".join(cur["de"]).strip().rstrip(".")
                if not de.startswith("Transferred entry") and not de.startswith("Deleted entry"):
                    cur["name"] = de
                    yield cur
            cur = None


def build_node_yaml(ec, name, parent):
    definition = f"{name} — EC {ec}, an Enzyme Commission classification node."
    lines = [f"identifier: EC:{ec}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: ExPASy ENZYME", "trait_axis: FUNCTION",
              "trait_category: FUNC_ENZYMATIC_ACTIVITY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - EC:{parent}"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def build_leaf_yaml(rec, parent, go, rhea, kegg):
    ec, name = rec["ec"], rec["name"]
    reaction = " ".join(rec["ca"]).strip()
    definition = (f"Enzymatic activity — {name} (EC {ec})."
                  + (f" Catalysed reaction: {reaction}" if reaction else ""))
    lines = [f"identifier: EC:{ec}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: ExPASy ENZYME", "trait_axis: FUNCTION",
              "trait_category: FUNC_ENZYMATIC_ACTIVITY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - EC:{parent}"]
    syns = list(dict.fromkeys(rec["an"]))
    if syns:
        lines.append("synonyms:")
        for s in syns:
            lines.append(f"  - synonym_text: {yaml_escape(s)}")
            lines.append("    synonym_type: EXACT_SYNONYM")
    if kegg:
        lines.append("xrefs:")
        lines.extend(f"  - {k}" for k in kegg)
    mapped = [(g, "ec2go") for g in dict.fromkeys(go)] + \
             [(r, "rhea2ec") for r in dict.fromkeys(rhea)]
    if mapped:
        lines.append("mapped_xrefs:")
        for obj, src in mapped:
            lines += [f"  - object: {obj}", f"    mapping_source: {src}"]
    ex = rec["dr"][:3]
    if ex:
        lines.append("canonical_examples:")
        for acc, entry in ex:
            lines += [f"  - protein_id: UniProtKB:{acc}",
                      f"    protein_label: {yaml_escape(entry)}",
                      "    note: ExPASy ENZYME DR cross-reference",
                      "    source: CURATOR"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not ENZYME.exists():
        print("missing data/raw/ec/enzyme.dat; run `just fetch-ec`", file=sys.stderr)
        return 2

    ec2go, rhea2ec, tom_kegg = load_ec2go(), load_rhea2ec(), load_tom_kegg()
    nodes = parse_enzclass()

    written = skipped = n_nodes = n_leaves = 0

    def emit(ec, text):
        nonlocal written, skipped
        path = OUT_DIR / f"{slugify(ec.replace('.', '-'))}-ec{ec.replace('.', '-')}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    for ec, name in sorted(nodes.items()):
        n_nodes += 1
        emit(ec, build_node_yaml(ec, name, ec_parent(ec)))

    for rec in parse_enzyme():
        ec = rec["ec"]
        n_leaves += 1
        emit(ec, build_leaf_yaml(rec, ec_parent(ec), ec2go.get(ec, []),
                                 rhea2ec.get(ec, []), tom_kegg.get(ec, [])))

    print(f"{n_nodes + n_leaves} EC records ({n_nodes} classification nodes, "
          f"{n_leaves} enzyme leaves; {len(tom_kegg)} KEGG folded from trait-onto-map).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {n_nodes + n_leaves - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
