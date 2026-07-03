#!/usr/bin/env python3
"""Seed intrinsic-disorder traits from DisProt (Tosatto lab, CC-BY 4.0)
→ SEQUENCE / SEQ_DISORDER.

PIVOTED model (2026-07): DisProt entries are per-protein disorder profiles —
instance-level, not trait classes. Instead of one record per protein, we seed
the **IDPO disorder classes** each region is annotated with (structural state,
structural transition, disorder function — 32 terms), and attach the annotated
proteins as `canonical_examples` on the relevant class. Three namespace-group
nodes are materialized as parents so the hierarchy has no dangling parents.

The 367 GO annotations (function / process / localisation of disordered
proteins) are out of scope here — they belong to the FUNCTION axis.

Input (fetched on first run; cached): data/raw/disprot.entries.json
Each protein appears (capped) as an example on every IDPO class it carries.
Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
CACHE_PATH = RAW_DIR / "disprot.entries.json"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "disorder"
API = "https://disprot.org/api/search?release=current&format=json&namespace=all&get_consensus=false"
LICENSE = "CC-BY-4.0"
DEF_SOURCE = "DisProt (Tosatto lab, U. Padova; IDPO-classed, proteins as examples)"
EXAMPLES_CAP = 30
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

# The three IDPO namespaces → a materialized grouping trait (no dangling parent).
NAMESPACE_GROUP = {
    "Structural state": ("proteintraitsmech:IDPO_STRUCTURAL_STATE",
                         "disorder structural state",
                         "A structural state of an intrinsically disordered region "
                         "(disorder, order, molten globule, pre-molten globule)."),
    "Structural transition": ("proteintraitsmech:IDPO_STRUCTURAL_TRANSITION",
                              "disorder structural transition",
                              "A conformational transition of a disordered region "
                              "(e.g. disorder-to-order upon binding)."),
    "Disorder function": ("proteintraitsmech:IDPO_DISORDER_FUNCTION",
                          "disorder-based function",
                          "A function performed by an intrinsically disordered region "
                          "(flexible linker/tail, PTM display site, self-regulation, "
                          "molecular recognition, assembly)."),
}


def slugify(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "idpo"


def yaml_escape(text) -> str:
    text = str(text)
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


def load_entries():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    print("fetching DisProt (first run)…", file=sys.stderr)
    with urllib.request.urlopen(API, timeout=120) as r:
        payload = json.loads(r.read().decode("utf-8"))
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def group_node_yaml(ident, label, definition):
    lines = [f"identifier: {ident}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {yaml_escape(DEF_SOURCE)}",
              "trait_axis: SEQUENCE", "trait_category: SEQ_DISORDER",
              "term_kind: CLASS", "mapping_status: SEEDED",
              f"license: {LICENSE}"]
    return "\n".join(lines) + "\n"


def term_yaml(tid, name, namespace, n_prot, examples):
    grp = NAMESPACE_GROUP[namespace][0]
    definition = (f"{name} — an IDPO disorder class ({namespace}, {tid}); a "
                  f"protein region with this intrinsic-disorder property. "
                  f"{n_prot} DisProt protein(s) annotated (examples below capped).")
    lines = [f"identifier: {tid}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {yaml_escape(DEF_SOURCE)}",
              "trait_axis: SEQUENCE", "trait_category: SEQ_DISORDER",
              "term_kind: CLASS", "mapping_status: SEEDED",
              "parent_traits:", f"  - {grp}"]
    if examples:
        lines.append("canonical_examples:")
        for ex in examples:
            lines.append(f"  - protein_id: UniProtKB:{ex['acc']}")
            lines.append(f"    protein_label: {yaml_escape(ex['name'])}")
            if ex.get("taxon_id"):
                lines.append(f"    taxon_id: NCBITaxon:{ex['taxon_id']}")
            if ex.get("organism"):
                lines.append(f"    taxon_label: {yaml_escape(ex['organism'])}")
            if ex.get("seq"):
                lines.append(f"    sequence_length: {len(ex['seq'])}")
            lines.append(f"    note: {yaml_escape('DisProt entry ' + ex['dp'])}")
            lines.append("    source: CURATOR")
            if ex.get("seq"):
                lines.append(f"    sequence: {ex['seq']}")
            if ex.get("feats"):
                lines.append("    features:")
                for s, e in ex["feats"]:
                    lines.append(f"      - start: {s}")
                    lines.append(f"        end: {e}")
                    lines.append("        feature_type: DISORDER")
                    lines.append("        trait_axis: SEQUENCE")
                    lines.append("        trait_category: SEQ_DISORDER")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    data = load_entries()
    entries = data if isinstance(data, list) else data.get("data", [])

    terms: dict[str, dict] = {}
    hits: dict[str, dict] = defaultdict(dict)
    for e in entries:
        acc = e.get("acc")
        if not acc:
            continue
        base = {"acc": acc, "name": e.get("name") or acc,
                "taxon_id": e.get("ncbi_taxon_id"), "organism": e.get("organism"),
                "dp": e.get("disprot_id") or "", "seq": e.get("sequence") or ""}
        for r in (e.get("regions") or []):
            if r.get("term_ontology") != "IDPO":
                continue
            tid, name, ns = r.get("term_id"), r.get("term_name"), r.get("term_namespace")
            if not tid or ns not in NAMESPACE_GROUP:
                continue
            terms[tid] = {"name": name, "namespace": ns}
            ex = hits[tid].setdefault(acc, {**base, "feats": []})
            try:
                ex["feats"].append((int(r["start"]), int(r["end"])))
            except (KeyError, TypeError, ValueError):
                pass

    written = skipped = 0

    def emit(path: Path, text: str):
        nonlocal written, skipped
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    for ns, (ident, label, defn) in NAMESPACE_GROUP.items():
        emit(OUT_DIR / f"{slugify(label)}.yaml", group_node_yaml(ident, label, defn))

    for tid, meta in sorted(terms.items()):
        prots = list(hits[tid].values())
        prots.sort(key=lambda p: (-len(p["feats"]), p["acc"]))
        text = term_yaml(tid, meta["name"], meta["namespace"], len(prots),
                         prots[:EXAMPLES_CAP])
        emit(OUT_DIR / f"{slugify(meta['name'])}-{tid.replace(':', '-').lower()}.yaml", text)

    print(f"DisProt pivot: {len(NAMESPACE_GROUP)} namespace groups + {len(terms)} "
          f"IDPO disorder classes; {sum(len(h) for h in hits.values())} protein "
          f"annotations over {len(entries)} DisProt proteins (examples capped at "
          f"{EXAMPLES_CAP}/class).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(terms) + len(NAMESPACE_GROUP) - skipped}; "
              f"{skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
