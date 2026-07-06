#!/usr/bin/env python3
"""Seed CAZy family classes → SEQUENCE / SEQ_FAMILY.

CAZy (Carbohydrate-Active enZymes, © CNRS / Aix-Marseille Université / INRAE,
AFMB) is a sequence-based family classification of carbohydrate-active enzymes in
six classes — GH, GT, PL, CE, AA, CBM — grouped into clans that share a fold and
catalytic machinery. Because the classification is defined by amino-acid sequence
similarity, CAZy families are a SEQUENCE trait (SEQ_FAMILY), per the
axis-follows-representation convention.

⚠ LICENSE: CAZy content is © AFMB, academic-use, NOT openly licensed. This corpus
is otherwise CC0-1.0, so every CAZy record is stamped with the CAZy license and
FLAGGED. See download.yaml.

Hierarchy emitted:
  CAZy:<CLASS>            e.g. CAZy:GH   (6 class nodes)
    └ CAZy:<CLAN>         e.g. CAZy:GH-A (clans that share fold + machinery)
        └ CAZy:<FAMILY>   e.g. CAZy:GH1  (~537 families)
Families with no clan hang directly under their class node.

Content per family (from cazy.org via fetch_cazy_families.py): clan, mechanism,
catalytic 3D fold, and the "Activities in Family" table → EC numbers (as direct
`xrefs`, CAZy being the asserting source) and activity names (in the definition).
InterPro entries that cross-reference the family (from interpro.xml, public
domain) are added as `mapped_xrefs`.

Inputs (gitignored):
  data/raw/cazy/families.json          (just fetch-cazy-families)
  data/raw/interpro/interpro.xml.gz    (just fetch-interpro)

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw"
FAMILIES = RAW / "cazy" / "families.json"
INTERPRO_XML = RAW / "interpro" / "interpro.xml.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "family" / "cazy"

LICENSE = "CAZy (© CNRS - Aix-Marseille Université - INRAE, AFMB) — academic use, not openly licensed"
EC_CAP = 25

CLASS_INFO = {
    "GH":  ("Glycoside hydrolase",       "Glycoside Hydrolases",
            "Enzymes that hydrolyse the glycosidic bond between two or more carbohydrates, "
            "or between a carbohydrate and a non-carbohydrate moiety."),
    "GT":  ("Glycosyltransferase",       "Glycosyltransferases",
            "Enzymes that transfer sugar moieties from activated donor molecules to specific "
            "acceptors, forming glycosidic bonds."),
    "PL":  ("Polysaccharide lyase",      "Polysaccharide Lyases",
            "Enzymes that cleave uronic-acid-containing polysaccharides via a β-elimination "
            "mechanism to generate an unsaturated hexenuronic-acid residue."),
    "CE":  ("Carbohydrate esterase",     "Carbohydrate Esterases",
            "Enzymes that catalyse the de-O- or de-N-acylation of substituted saccharides."),
    "AA":  ("Auxiliary activity",        "Auxiliary Activities",
            "Redox enzymes that act in concert with other CAZymes (e.g. lytic polysaccharide "
            "monooxygenases and ligninolytic enzymes)."),
    "CBM": ("Carbohydrate-binding module", "Carbohydrate-Binding Modules",
            "Non-catalytic modules that bind carbohydrate, potentiating the activity of the "
            "catalytic modules to which they are appended."),
}

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:60]) or "cazy"


def yesc(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


def norm_mech(m: str | None) -> str:
    if not m:
        return ""
    low = m.lower()
    if low.startswith("retaining"):
        return "retaining"
    if low.startswith("inverting"):
        return "inverting"
    return m.strip()


def clean_fold(f: str | None) -> str:
    return " ".join((f or "").split()).replace("( ", "(").replace(" )", ")") if f else ""


def parse_interpro_cazy():
    """(fam -> [(ipr,name,type)], fam -> best name)."""
    fam2ipr: dict[str, list] = {}
    fam_name: dict[str, str] = {}
    if not INTERPRO_XML.exists():
        return fam2ipr, fam_name
    with gzip.open(INTERPRO_XML, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = el.get("id"); typ = el.get("type", "")
            ne = el.find("name"); name = (ne.text or "").strip() if ne is not None else ""
            for x in el.iter("db_xref"):
                if x.get("db") == "CAZY" and x.get("dbkey"):
                    f = x.get("dbkey")
                    fam2ipr.setdefault(f, []).append((ipr, name, typ))
                    if f not in fam_name or (typ == "Family" and "family" in name.lower()):
                        fam_name[f] = name
            el.clear()
    return fam2ipr, fam_name


def build_family_yaml(fam, cls, meta, parent, ipr_entries, ipr_name):
    single = CLASS_INFO[cls][0]
    num = fam[len(cls):]
    label = f"{single} family {num} ({fam})"
    clan = meta.get("clan"); mech = norm_mech(meta.get("mechanism"))
    fold = clean_fold(meta.get("fold")); acts = meta.get("activities") or []
    ec = (meta.get("ec") or [])[:EC_CAP]
    n_act = meta.get("n_activities") or 0

    parts = [f"CAZy {single.lower()} family {num} ({fam}) — a sequence-based family in the "
             f"CAZy (Carbohydrate-Active enZymes) classification."]
    if clan and clan not in ("None", "-"):
        parts.append(f"Clan {clan} (shared fold and catalytic machinery).")
    if mech:
        parts.append(f"Mechanism: {mech}.")
    if fold:
        parts.append(f"Catalytic 3D fold: {fold}.")
    if acts:
        more = f" (+{n_act - len(acts)} more)" if n_act > len(acts) else ""
        parts.append(f"Representative activities: {', '.join(acts[:8])}{more}.")
    if ipr_name:
        parts.append(f"Corresponds to InterPro '{ipr_name}'.")
    definition = " ".join(parts)

    lines = [f"identifier: CAZy:{fam}", f"label: {yesc(label)}"]
    f = folded(definition); lines.append(f"definition: {f[0]}"); lines.extend(f[1:])
    lines.append("definition_source: CAZy")
    lines.append("trait_axis: SEQUENCE")
    lines.append("trait_category: SEQ_FAMILY")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    lines.append("parent_traits:")
    lines.append(f"  - CAZy:{parent}")
    if ipr_name and (fname := ipr_name):
        lines.append("synonyms:")
        lines.append(f"  - synonym_text: {yesc(fname)}")
        lines.append("    synonym_type: RELATED_SYNONYM")
    if ec:  # EC asserted by CAZy's Activities-in-Family → direct xrefs
        lines.append("xrefs:")
        for e in ec:
            lines.append(f"  - EC:{e}")
    seen_ipr: list[str] = []
    for iprid, _n, _t in ipr_entries:  # dedupe (an entry can list CAZY twice)
        if iprid not in seen_ipr:
            seen_ipr.append(iprid)
    if seen_ipr:  # InterPro's cross-reference → mapped_xrefs (mapping-derived)
        lines.append("mapped_xrefs:")
        for iprid in seen_ipr:
            lines.append(f"  - object: InterPro:{iprid}")
            lines.append("    predicate: skos:relatedMatch")
            lines.append("    mapping_source: InterPro CAZY cross-reference")
    lines.append(f"license: {yesc(LICENSE)}")
    return "\n".join(lines) + "\n"


def build_group_yaml(ident, label, definition, parent=None):
    lines = [f"identifier: CAZy:{ident}", f"label: {yesc(label)}"]
    f = folded(definition); lines.append(f"definition: {f[0]}"); lines.extend(f[1:])
    lines.append("definition_source: CAZy")
    lines.append("trait_axis: SEQUENCE")
    lines.append("trait_category: SEQ_FAMILY")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if parent:
        lines.append("parent_traits:")
        lines.append(f"  - CAZy:{parent}")
    lines.append(f"license: {yesc(LICENSE)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    if not FAMILIES.exists():
        print("missing data/raw/cazy/families.json; run `just fetch-cazy-families`", file=sys.stderr)
        return 2
    fams = json.loads(FAMILIES.read_text())
    fam2ipr, fam_name = parse_interpro_cazy()

    written = skipped = 0
    files: list[tuple[str, str]] = []  # (path, content)

    # 1) class nodes
    classes_present = sorted({m["class"] for m in fams.values()})
    for cls in classes_present:
        single, plural, desc = CLASS_INFO[cls]
        files.append((f"class-{cls.lower()}.yaml",
                      build_group_yaml(cls, plural,
                          f"CAZy class {cls}: {desc} Sequence-based family classification.")))
    # 2) clan nodes (distinct clans across families)
    clans = sorted({(m.get("clan") or "").strip() for m in fams.values()
                    if (m.get("clan") or "").strip() not in ("", "None", "-")})
    for clan in clans:
        cls = clan.split("-")[0]
        if cls not in CLASS_INFO:
            continue
        files.append((f"clan-{slugify(clan)}.yaml",
                      build_group_yaml(clan, f"CAZy clan {clan}",
                          f"CAZy clan {clan}: a group of {CLASS_INFO[cls][0].lower()} families "
                          f"that share a common three-dimensional fold and catalytic machinery.",
                          parent=cls)))
    # 3) family nodes
    for fam in sorted(fams, key=lambda f: (re.match(r"[A-Z]+", f).group(0), int(re.search(r"\d+", f).group()))):
        cls = re.match(r"[A-Z]+", fam).group(0)
        if cls not in CLASS_INFO or int(re.search(r"\d+", fam).group()) == 0:
            continue
        meta = fams[fam]
        clan = (meta.get("clan") or "").strip()
        parent = clan if clan and clan not in ("None", "-") and clan.split("-")[0] in CLASS_INFO else cls
        single = CLASS_INFO[cls][0]
        yaml = build_family_yaml(fam, cls, meta, parent, fam2ipr.get(fam, []), fam_name.get(fam))
        files.append((f"{slugify(single)}-{fam.lower()}.yaml", yaml))

    for name, content in files:
        path = OUT_DIR / name
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written += 1

    n_class = len(classes_present); n_clan = len(clans)
    n_fam = len(files) - n_class - n_clan
    print(f"CAZy: {n_class} class nodes, {n_clan} clan nodes, {n_fam} family records "
          f"({sum(1 for f in fams if fam2ipr.get(f))} families carry InterPro mapped_xrefs)")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {len(files) - skipped}; {skipped} exist. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
