#!/usr/bin/env python3
"""Seed protease cleavage-site specificity from MEROPS → SEQUENCE /
SEQ_CLEAVAGE_SITE.

MEROPS is already seeded as peptidase *families* (SEQ_FAMILY, seed_merops.py); its
observed substrate cleavages (`Substrate_search.txt`) are the missing recognition
motif — the sequence a protease cleaves. This aggregates the ~108k cleavages into
**one SEQ_CLEAVAGE_SITE class per peptidase's specificity** (not per cleavage
instance): the P4–P4′ residue-preference consensus (scissile bond between P1 and
P1′), grounded to the peptidase's `MEROPS:` id, with a few observed cleavages as
canonical examples.

Scope: peptidases with `--min-cleavages` (default 3) non-synthetic cleavages, so
the consensus is meaningful. Fills SEQ_CLEAVAGE_SITE (only ~11 ELM SLiMs today).

Input (fetch via `just fetch-merops`, gitignored):
  data/raw/merops/Substrate_search.txt — tab table (latin-1); cols: 1 peptidase
  MEROPS id, 2 substrate, 4-11 P4..P4′ residues, 13 UniProt acc, 14 position,
  16 peptidase name, 22 physiology.

Licence: MEROPS (EBI; free for academic use). Idempotent; dry-run unless --apply.
Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "merops" / "Substrate_search.txt"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "cleavage_site" / "merops"
LICENSE = "MEROPS (EBI; free for academic use)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
AA3 = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q",
       "Glu": "E", "Gly": "G", "His": "H", "Ile": "I", "Leu": "L", "Lys": "K",
       "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W",
       "Tyr": "Y", "Val": "V"}
POS = ["P4", "P3", "P2", "P1", "P1'", "P2'", "P3'", "P4'"]   # cols 4..11


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "cleav"


_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def clean_name(name: str) -> str:
    """Strip MEROPS organism tags + latin-1 control chars, e.g.
    'trypsin ({Homo sapiens}-type)' → 'trypsin'."""
    name = _CTRL.sub("", name or "")                       # latin-1 control bytes
    name = re.sub(r"\s*\([^)]*\{[^)]*\)", "", name)        # ({Homo sapiens}-type)
    name = re.sub(r"\s*\{[^}]*\}", "", name)                # bare {…}
    return " ".join(name.split())


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


def consensus(counters):
    """Per-position [residue set] / x pattern from P4..P4′ 1-letter counters.
    A position dominated by a few residues (top ≥20%, cumulative ≥50%, ≤4 set)
    becomes [XYZ]; a variable position becomes x."""
    parts = []
    for ctr in counters:
        tot = sum(ctr.values())
        if not tot or ctr.most_common(1)[0][1] / tot < 0.20:
            parts.append("x")
            continue
        chosen, cum = [], 0
        for aa, n in ctr.most_common():
            chosen.append(aa)
            cum += n
            if cum / tot >= 0.50 or len(chosen) >= 4:
                break
        parts.append(chosen[0] if len(chosen) == 1 else "[" + "".join(sorted(chosen)) + "]")
    # scissile bond marker between P1 (index 3) and P1' (index 4)
    return "-".join(parts[:4]) + " | " + "-".join(parts[4:])


def one_letter(three): return AA3.get(three, None)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--min-cleavages", type=int, default=3)
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/merops/Substrate_search.txt; run `just fetch-merops`")
        return 2

    # peptidase id -> {name, counters[8], n, n_phys, examples[]}
    pep = defaultdict(lambda: {"name": "", "ctr": [Counter() for _ in POS],
                               "n": 0, "phys": 0, "ex": []})
    for line in RAW.open(encoding="latin-1"):
        c = [x.strip().strip("'") for x in line.rstrip("\n").split("\t")]
        if len(c) < 23:
            continue
        physio = c[22]
        if physio == "synthetic":
            continue
        mid = c[1]
        if not mid:
            continue
        d = pep[mid]
        d["name"] = d["name"] or c[16]
        d["n"] += 1
        d["phys"] += physio == "physiological"
        site1 = []
        for i, col in enumerate(range(4, 12)):
            aa = one_letter(c[col]) if col < len(c) else None
            if aa:
                d["ctr"][i][aa] += 1
            site1.append(one_letter(c[col]) or "-" if col < len(c) else "-")
        # col 13 may hold several accessions ("P0CG47/Q13114") — take the first
        # and only keep a schema-valid UniProt accession.
        acc = (c[13] if len(c) > 13 else "").split("/")[0].strip()
        if (acc and acc != "NULL" and re.fullmatch(r"[A-Z0-9]+(?:-[0-9]+)?", acc)
                and len(d["ex"]) < 5):
            d["ex"].append((acc, c[14] if len(c) > 14 else "",
                            clean_name(c[2]), "".join(site1)))

    written = skipped = 0
    for mid, d in sorted(pep.items()):
        if d["n"] < args.min_cleavages:
            continue
        name = clean_name(d["name"]) or mid
        pat = consensus(d["ctr"])
        ident = "proteintraitsmech:MEROPS_CLEAVAGE_" + mid.replace(".", "_")
        defn = (f"The cleavage-site specificity of {name} (MEROPS {mid}): the "
                f"consensus of cleaved peptide bonds is {pat} (scissile bond "
                f"between P1 and P1'). From {d['n']} observed substrate cleavages "
                f"({d['phys']} physiological) in MEROPS.")
        lines = [f"identifier: {ident}", f"label: {yaml_escape(name + ' cleavage specificity')}"]
        f = folded(defn)
        lines += [f"definition: {f[0]}", *f[1:]]
        lines += ["definition_source: MEROPS (Substrate_search)", "trait_axis: SEQUENCE",
                  "trait_category: SEQ_CLEAVAGE_SITE", "term_kind: CLASS",
                  "mapping_status: SEEDED",
                  f"sequence_pattern: {yaml_escape(pat)}",
                  "xrefs:", f"  - MEROPS:{mid}"]
        if d["ex"]:
            lines.append("canonical_examples:")
            for acc, pos, sub, site in d["ex"]:
                lines += [f"  - protein_id: UniProtKB:{acc}"]
                if sub:
                    lines.append(f"    protein_label: {yaml_escape(sub)}")
                note = f"MEROPS cleavage {site}" + (f" at position {pos}" if pos and pos != "NULL" else "")
                lines += [f"    note: {yaml_escape(note)}", "    source: CURATOR"]
        lines.append(f"license: {yaml_escape(LICENSE)}")
        path = OUT_DIR / f"{slug(name)}-{slug(mid)}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            written += 1

    total = sum(1 for d in pep.values() if d["n"] >= args.min_cleavages)
    print(f"MEROPS cleavage: {total} peptidase cleavage-specificity classes "
          f"(>= {args.min_cleavages} cleavages, synthetic excluded) → SEQ_CLEAVAGE_SITE.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
