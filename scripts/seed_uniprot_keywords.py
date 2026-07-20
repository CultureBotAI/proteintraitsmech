#!/usr/bin/env python3
"""Seed class-level trait records from the UniProtKB controlled-vocabulary
**Keywords** (keywlist.txt) — one ProteinTraitRecord CLASS per keyword.

seed_uniprot.py ingests UniProt FT features + CC/GO blocks at the *instance*
level (per protein); it does NOT consume keywords. Keywords are the orthogonal
controlled vocabulary, and each keyword is inherently a reusable trait class. This
seeder routes the three round-4 target subtrees (research/protein-trait-sources-
round4.md):
  • `CA Ligand`                       → FUNC_BINDING_CAPACITY  (fills the empty
                                        category: Metal-binding, Heme, DNA-binding…)
  • `CA Biological process` matching an environmental-response term
                                      → FUNC_ENVIRONMENTAL_RESPONSE
  • the canonical targeting-signal keywords (Signal / Transit peptide /
    Signal-anchor)                    → SEQ_TARGETING_SIGNAL
Other keyword subtrees are out of scope for this round.

Hierarchy comes from the `HI` path lines (Category: parent; …; this-keyword);
`parent_traits` points to the immediate parent keyword when it is also seeded.

Input (fetch via `just fetch-uniprot-keywords`, gitignored):
  data/raw/uniprot_keywords/keywlist.txt  — one keyword per `//`-terminated block
  (ID name, AC KW-####, DE definition, CA category, HI hierarchy, SY synonyms,
  GO GO-xref).

Licence: CC-BY 4.0 (UniProt). Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "uniprot_keywords" / "keywlist.txt"
TRAITS = REPO_ROOT / "data" / "traits"
LICENSE = "CC-BY 4.0 (UniProt)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

# Biological-process keyword names that denote an environmental / stress response.
_ENV_RE = re.compile(
    r"stress|heat shock|cold|osmotic|oxidative|starvation|hypox|"
    r"antibiotic resistance|antiviral defense|virulence|response to|"
    r"sporulation|desiccation|radiation|salt|acid resistance", re.I)
# Canonical targeting-signal keywords (they live under CA Domain, not a
# targeting category, so an explicit allow-list is required).
_TARGETING = {"Signal", "Transit peptide", "Signal-anchor"}


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "kw"


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


def route(cat: str, name: str):
    """(trait_axis, trait_category, subdir) for a keyword, or None to skip."""
    if cat == "Ligand":
        return "FUNCTION", "FUNC_BINDING_CAPACITY", "function/binding_capacity"
    if cat == "Biological process" and _ENV_RE.search(name):
        return ("FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                "function/environmental_response")
    if name in _TARGETING:
        return "SEQUENCE", "SEQ_TARGETING_SIGNAL", "sequence/targeting_signal"
    return None


def parse_blocks(text: str):
    """[{ac, name, defn, cat, hi:[paths], syn:[...], go:[GO:…]}] for real keyword
    entries (skip the documentation header + category `IC` entries)."""
    out = []
    for b in text.split("//\n"):
        idm = re.search(r"(?m)^ID   (.+?)\.?\s*$", b)
        acm = re.search(r"(?m)^AC   (KW-\d+)", b)
        cam = re.search(r"(?m)^CA   (.+?)\.?\s*$", b)
        if not (idm and acm and cam):
            continue
        de = " ".join(re.findall(r"(?m)^DE   (.+)$", b))
        hi = [h.strip().rstrip(".") for h in re.findall(r"(?m)^HI   (.+)$", b)]
        sy = []
        for s in re.findall(r"(?m)^SY   (.+)$", b):
            sy += [x.strip().rstrip(".") for x in s.split(";") if x.strip()]
        go = re.findall(r"(?m)^GO   (GO:\d+)", b)
        out.append({"ac": acm.group(1), "name": idm.group(1).strip(),
                    "defn": de, "cat": cam.group(1).strip(),
                    "hi": hi, "syn": sy, "go": go})
    return out


def immediate_parent(kw, name2ac):
    """AC of the keyword's immediate parent, from the HI path in its category."""
    for path in kw["hi"]:
        if ":" not in path:
            continue
        cat, chain = path.split(":", 1)
        if cat.strip() != kw["cat"]:
            continue
        parts = [p.strip() for p in chain.split(";") if p.strip()]
        # last part is this keyword; the one before it is the parent
        if len(parts) >= 2 and parts[-2] in name2ac:
            return name2ac[parts[-2]]
    return None


def build_yaml(kw, axis, cat, parent_ac):
    lines = [f"identifier: UniProtKB-KW:{kw['ac']}",
             f"label: {yaml_escape(kw['name'])}"]
    f = folded(kw["defn"] or kw["name"])
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: UniProt Keywords (keywlist.txt)",
              f"trait_axis: {axis}", f"trait_category: {cat}",
              "term_kind: CLASS", "mapping_status: SEEDED"]
    if parent_ac:
        lines += ["parent_traits:", f"  - UniProtKB-KW:{parent_ac}"]
    if kw["syn"]:
        lines.append("synonyms:")
        for s in dict.fromkeys(kw["syn"]):
            lines += [f"  - synonym_text: {yaml_escape(s)}",
                      "    synonym_type: EXACT_SYNONYM", "    source: UniProt"]
    if kw["go"]:
        lines += ["xrefs:"] + [f"  - {g}" for g in dict.fromkeys(kw["go"])]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/uniprot_keywords/keywlist.txt; run "
              "`just fetch-uniprot-keywords`", file=sys.stderr)
        return 2
    kws = parse_blocks(RAW.read_text(encoding="utf-8", errors="replace"))
    routed = {kw["ac"]: (kw, *r) for kw in kws if (r := route(kw["cat"], kw["name"]))}
    name2ac = {kw["name"]: kw["ac"] for kw in kws}
    seeded = set(routed)

    written = skipped = 0
    by_cat: dict[str, int] = {}
    for ac, (kw, axis, cat, subdir) in sorted(routed.items()):
        parent = immediate_parent(kw, name2ac)
        parent = parent if parent in seeded else None    # only link seeded parents
        path = TRAITS / subdir / "uniprot_keywords" / f"{slug(kw['name'])}-{ac.lower()}.yaml"
        by_cat[cat] = by_cat.get(cat, 0) + 1
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(kw, axis, cat, parent), encoding="utf-8")
            written += 1

    print(f"UniProt Keywords: {len(routed)} keyword classes → {dict(sorted(by_cat.items()))}")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {len(routed) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
