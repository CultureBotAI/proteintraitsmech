#!/usr/bin/env python3
"""Seed the protean-segment (ProS) trait from IDEAL (Osaka Univ., CC-BY 4.0)
→ SEQUENCE / SEQ_DISORDER.

IDEAL catalogues intrinsically disordered proteins and their **ProS** (protean
segments) — disordered regions that fold upon binding a partner (a named
binding motif per protein). ProS is IDEAL's distinctive, reusable concept, so
— per the pivot model — we seed ONE ProS trait class (a specialisation of the
IDPO "disorder to order" transition, parent IDPO:0000011, already materialised
by DisProt) and attach IDEAL proteins as `canonical_examples`, each carrying
its ProS motif as a feature. IDEAL's plain disorder regions overlap DisProt's
IDPO:0000002 and are not re-seeded here.

Input (fetch via `just fetch-ideal`, gitignored): data/raw/ideal/IDEAL.xml.gz
Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "ideal" / "IDEAL.xml.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "disorder"
IDENT = "proteintraitsmech:IDEAL_PROS"
PARENT = "IDPO:0000011"  # disorder to order (structural transition) — ProS is protean
LICENSE = "CC-BY 4.0"
EXAMPLES_CAP = 50


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


def build_yaml(n_prot, examples):
    definition = (
        "Protean segment (ProS) — an intrinsically disordered protein region "
        "that folds upon binding a partner (disorder-to-order coupled folding); "
        "the reusable concept curated by IDEAL. "
        f"{n_prot} IDEAL protein(s) annotated (examples below capped).")
    lines = [f"identifier: {IDENT}", "label: protean segment (ProS)"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: IDEAL (Osaka University)",
              "trait_axis: SEQUENCE", "trait_category: SEQ_DISORDER",
              "term_kind: CLASS", "mapping_status: SEEDED",
              "parent_traits:", f"  - {PARENT}"]
    if examples:
        lines.append("canonical_examples:")
        for ex in examples:
            lines.append(f"  - protein_id: UniProtKB:{ex['acc']}")
            lines.append(f"    protein_label: {yaml_escape(ex['name'])}")
            if ex.get("organism"):
                lines.append(f"    taxon_label: {yaml_escape(ex['organism'])}")
            if ex.get("seq"):
                lines.append(f"    sequence_length: {len(ex['seq'])}")
            lines.append(f"    note: {yaml_escape('IDEAL entry ' + ex['idp'] + '; ProS motif(s): ' + ex['motifs'])}")
            lines.append("    source: CURATOR")
            if ex.get("seq"):
                lines.append(f"    sequence: {ex['seq']}")
            if ex.get("feats"):
                lines.append("    features:")
                for s, e in ex["feats"]:
                    lines.append(f"      - start: {s}")
                    lines.append(f"        end: {e}")
                    lines.append("        feature_type: BINDING_MOTIF")
                    lines.append("        trait_axis: SEQUENCE")
                    lines.append("        trait_category: SEQ_DISORDER")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/ideal/IDEAL.xml.gz; run `just fetch-ideal`",
              file=sys.stderr)
        return 2

    root = ET.parse(gzip.open(RAW)).getroot()
    examples = []
    n_prot = 0
    for e in root.findall("IDEAL_entry"):
        g = e.find("General")
        if g is None:
            continue
        motifs = g.findall("motif")
        if not motifs:
            continue
        acc = g.findtext("uniprot")
        if not acc:
            continue
        feats, names = [], []
        for m in motifs:
            names.append(m.findtext("motif_name") or "motif")
            reg = m.find("motif_region")
            if reg is not None:
                s, en = reg.findtext("motif_region_start"), reg.findtext("motif_region_end")
                try:
                    feats.append((int(s), int(en)))
                except (TypeError, ValueError):
                    pass
        n_prot += 1
        examples.append({
            "acc": acc, "name": g.findtext("name") or acc,
            "organism": g.findtext("source_organism"),
            "seq": (g.findtext("sequence") or "").strip(),
            "idp": e.findtext("idp_id") or "",
            "motifs": "; ".join(dict.fromkeys(names))[:200],
            "feats": feats,
        })

    # richest-annotated first for the capped example set
    examples.sort(key=lambda x: (-len(x["feats"]), x["acc"]))
    path = OUT_DIR / "protean-segment-pros-ideal.yaml"
    exists = path.exists()
    if args.apply and (not exists or args.force):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_yaml(n_prot, examples[:EXAMPLES_CAP]), encoding="utf-8")

    print(f"IDEAL: 1 ProS trait ({IDENT}); {n_prot} IDEAL proteins with a ProS "
          f"motif (examples capped at {EXAMPLES_CAP}).")
    if args.apply:
        print("Wrote 1." if not exists or args.force else "Skipped (exists).")
    else:
        print(f"Dry-run — would write 1 ({'exists' if exists else 'new'}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
