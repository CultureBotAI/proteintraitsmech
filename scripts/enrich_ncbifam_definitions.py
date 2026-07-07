#!/usr/bin/env python3
"""Round 1 of edison-trait-definitions: recompose NCBIfam definitions.

NCBIfam's seeded definition is a template stub —
  "<product> — an NCBIfam protein family (NF…, equivalog); members share this
   conserved family signature."
— informative only in the product name, and identical in shape for 38k records
with the function (EC/GO) it already carries left unsaid. This recomposes the
main `definition` from the source's own hmm_PGAP metadata (product · family_type ·
EC · GO · gene), resolving EC/GO to names, in ONE consistent pattern per axis:

  FUNCTION (FUNC_PROTEIN_FAMILY, whole-protein equivalog/subfamily):
    "<product> (<gene>) — a functionally conserved protein family grouped by the
     NCBIfam full-length profile-HMM <acc> (<family_type>); catalyses <EC names>;
     associated with <GO names>."
  SEQUENCE (SEQ_DOMAIN/REPEAT/…, sequence region):
    "<product> (<gene>) — a protein domain modelled by the NCBIfam sequence-profile
     HMM <acc> (<family_type>); associated with <function>."

method: SOURCED (composed from source metadata, no LLM). Idempotent (re-writes are
detected by definition_source); dry-run unless --apply. Stdlib-only.

Follow-up: seed_ncbifam.py should adopt the same composition so a re-seed matches.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw"
TSV = RAW / "ncbifam" / "hmm_PGAP.tsv"
GO_OBO = RAW / "go-basic.obo"
EC_DAT = RAW / "ec" / "enzyme.dat"
TRAITS = REPO_ROOT / "data" / "traits"

# NB: no ": " (colon-space) — it must be a valid plain YAML scalar.
SOURCE = "NCBIfam PGAP (composed from product and EC/GO annotations)"
GENERIC_TAXA = {"", "bacteria", "archaea", "eukaryota", "bacteria/archaea", "cellular organisms"}
_SPLIT = re.compile(r"[,\s;]+")


def load_go_names() -> dict[str, str]:
    out = {}
    for block in GO_OBO.read_text(encoding="utf-8", errors="replace").split("\n\n"):
        if "[Term]" not in block:
            continue
        i = re.search(r"^id: (GO:\d+)", block, re.M)
        n = re.search(r"^name: (.+)", block, re.M)
        if i and n:
            out[i.group(1)] = n.group(1).strip()
    return out


def load_ec_names() -> dict[str, str]:
    out, cur = {}, None
    for line in EC_DAT.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("ID "):
            cur = line[5:].strip()
        elif line.startswith("DE ") and cur:
            out[cur] = line[5:].strip().rstrip(".")
            cur = None
    return out


def load_meta() -> dict[str, dict]:
    out = {}
    with open(TSV, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            m = {
                "product": (row.get("product_name") or "").strip(),
                "gene": (row.get("gene_symbol") or "").strip(),
                "ftype": (row.get("family_type") or "").strip(),
                "ec": [e for e in _SPLIT.split((row.get("ec_numbers") or "").strip())
                       if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", e)],
                "go": [f"GO:{g}" for g in re.findall(r"\d{7}", row.get("go_terms") or "")],
                "taxon": (row.get("taxonomic_range_name") or "").strip(),
            }
            for col in ("#ncbi_accession", "source_identifier"):
                v = (row.get(col) or "").strip()
                if v:
                    out[re.sub(r"\.\d+$", "", v)] = m
    return out


def compose(m: dict, acc: str, axis: str, ecn: dict, gon: dict) -> str:
    prod = m["product"] or acc
    lead = prod + (f" ({m['gene']})" if m["gene"] and m["gene"].lower() not in prod.lower() else "")
    ft = (m["ftype"] or "model").lower()
    fn = []
    ecs = [ecn.get(e, f"EC {e}") for e in m["ec"]]
    gos = [gon[g] for g in m["go"] if g in gon]
    if ecs:
        fn.append("catalyses " + ", ".join(ecs[:4]))
    if gos:
        fn.append("associated with " + ", ".join(gos[:4]))
    fn_txt = ("; " + "; ".join(fn)) if fn else ""
    if axis == "FUNCTION":
        s = (f"{lead} — a functionally conserved protein family grouped by the NCBIfam "
             f"full-length profile-HMM {acc} ({ft}){fn_txt}.")
        if m["taxon"].lower() not in GENERIC_TAXA:
            s += f" Members occur in {m['taxon']}."
    else:
        kind = "region" if "repeat" in ft else "domain"
        s = (f"{lead} — a protein {kind} modelled by the NCBIfam sequence-profile HMM "
             f"{acc} ({ft}){fn_txt}.")
    return " ".join(s.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    for f in (TSV, GO_OBO, EC_DAT):
        if not f.exists():
            print(f"missing {f.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 2

    meta = load_meta()
    gon = load_go_names()
    ecn = load_ec_names()
    print(f"{len(meta):,} NCBIfam accessions | {len(gon):,} GO names | {len(ecn):,} EC names")

    # Only the ncbifam directories (not a full-corpus rglob).
    files = []
    for sub in ("function/protein_family/ncbifam", "sequence/domain/ncbifam",
                "sequence/repeat/ncbifam", "sequence/homologous_superfamily/ncbifam"):
        d = TRAITS / sub
        if d.is_dir():
            files += sorted(d.glob("*.yaml"))

    done = skip = nometa = 0
    # Replace the definition folded-block + its definition_source line ONLY.
    # MULTILINE only (NO DOTALL) so `.` never crosses a newline — a DOTALL `.*$`
    # would eat the rest of the file.
    DEF_RE = re.compile(r"(?m)^definition:[ \t]*>-\n(?:[ \t]+.*\n)+?definition_source:.*$")
    for p in files:
        text = p.read_text(encoding="utf-8")
        if SOURCE in text:
            skip += 1
            continue
        idm = re.search(r"(?m)^identifier:\s*NCBIfam:(\S+)", text)
        axm = re.search(r"(?m)^trait_axis:\s*(\S+)", text)
        if not idm or not axm or idm.group(1) not in meta:
            nometa += 1
            continue
        new_def = compose(meta[idm.group(1)], idm.group(1), axm.group(1), ecn, gon)
        block = f"definition: >-\n  {new_def}\ndefinition_source: {SOURCE}"
        new, n = DEF_RE.subn(lambda _m: block, text, count=1)   # lambda → no escape interpretation
        if not n:
            nometa += 1
            continue
        done += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"NCBIfam definitions: {'recomposed' if args.apply else 'would recompose'} {done:,} "
          f"| already done {skip:,} | no metadata/def {nometa:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
