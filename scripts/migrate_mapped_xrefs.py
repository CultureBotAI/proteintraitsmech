#!/usr/bin/env python3
"""Migrate mapping-derived cross-references out of `xrefs` into the
provenance-bearing `mapped_xrefs` slot.

Direct `xrefs` are equivalences asserted by a trait's own source. Several
seeders instead folded *mapping-product* associations into `xrefs`:

  InterPro record  GO xref present in interpro2go[IPR]   → mapping: interpro2go
  Pfam record      GO xref present in pfam2go[PF]        → mapping: pfam2go
  Pfam record      InterPro xref in pfam2interpro[PF]    → mapping: pfam2interpro
  EC record        GO xref present in ec2go[EC]          → mapping: ec2go

This script uses the mapping files themselves as ground truth: a GO/InterPro
xref only migrates if the relevant mapping actually asserts it for that
record's id — so curator-added or source-direct xrefs are left in `xrefs`.

Idempotent. Dry-run (review) by default; --apply to rewrite. Scope with
--source {interpro,pfam,ec} (repeatable); default all three. Stdlib + PyYAML.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
RAW = REPO_ROOT / "data" / "raw"

INTERPRO2GO = RAW / "interpro" / "interpro2go"
PFAM2GO = RAW / "mappings" / "pfam2go"
PFAM2IPR = RAW / "mappings" / "pfam2interpro.tsv"
EC2GO = RAW / "mappings" / "ec2go"

_GO_RE = re.compile(r"(GO:\d{7})")


def _lines(p):
    return p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else []


def load_interpro2go() -> dict[str, set[str]]:
    m: dict[str, set[str]] = {}
    for line in _lines(INTERPRO2GO):
        if line.startswith("!"):
            continue
        # 'InterPro:IPRnnnnnn name > GO:term ; GO:nnnnnnn'
        im = re.match(r"InterPro:(IPR\d+)", line)
        gm = _GO_RE.search(line.split(";")[-1]) if ";" in line else None
        if im and gm:
            m.setdefault(im.group(1), set()).add(gm.group(1))
    return m


def load_pfam2go() -> dict[str, set[str]]:
    m: dict[str, set[str]] = {}
    for line in _lines(PFAM2GO):
        if line.startswith("!"):
            continue
        pm = re.search(r"Pfam:(PF\d+)", line)
        gm = _GO_RE.search(line.split(";")[-1]) if ";" in line else None
        if pm and gm:
            m.setdefault(pm.group(1), set()).add(gm.group(1))
    return m


def load_pfam2interpro() -> dict[str, set[str]]:
    m: dict[str, set[str]] = {}
    for line in _lines(PFAM2IPR):
        parts = re.split(r"[\t ]+", line.strip())
        pf = next((p for p in parts if p.startswith("PF")), None)
        ipr = next((p for p in parts if p.startswith("IPR")), None)
        if pf and ipr:
            m.setdefault(pf, set()).add(f"InterPro:{ipr}")
    return m


def load_ec2go() -> dict[str, set[str]]:
    m: dict[str, set[str]] = {}
    ec_re = re.compile(r"EC:(\d+\.\d+\.\d+\.\d+)")
    for line in _lines(EC2GO):
        if line.startswith("!"):
            continue
        em = ec_re.search(line)
        gm = _GO_RE.search(line.split(";")[-1]) if ";" in line else None
        if em and gm:
            m.setdefault(em.group(1), set()).add(gm.group(1))
    return m


# ---- YAML round-trip preserving key order + folded definition ----

def read_trait(path: Path) -> dict:
    import yaml
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def write_trait(path: Path, data: dict) -> None:
    import yaml

    class Folded(str):
        pass

    yaml.add_representer(Folded, lambda d, s: d.represent_scalar(
        "tag:yaml.org,2002:str", s, style=">"))

    order = ["identifier", "label", "definition", "definition_source",
             "trait_axis", "trait_category", "term_kind", "mapping_status",
             "parent_traits", "synonyms", "sequence_pattern",
             "residue_sequence", "xrefs", "mapped_xrefs", "canonical_examples",
             "evidence", "curation_history", "causal_graphs"]
    ordered = {k: data[k] for k in order if k in data}
    for k in data:
        if k not in ordered:
            ordered[k] = data[k]
    if isinstance(ordered.get("definition"), str):
        ordered["definition"] = Folded(ordered["definition"])
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(ordered, fh, default_flow_style=False, sort_keys=False,
                  allow_unicode=True, width=100000)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--source", action="append",
                    choices=["interpro", "pfam", "ec"], default=None)
    args = ap.parse_args()
    sources = set(args.source or ["interpro", "pfam", "ec"])

    ipr2go = load_interpro2go() if "interpro" in sources else {}
    pf2go = load_pfam2go() if "pfam" in sources else {}
    pf2ipr = load_pfam2interpro() if "pfam" in sources else {}
    ec2go = load_ec2go() if "ec" in sources else {}
    print(f"maps: interpro2go={len(ipr2go)} pfam2go={len(pf2go)} "
          f"pfam2interpro={len(pf2ipr)} ec2go={len(ec2go)}")

    touched = moved = 0
    per_map: dict[str, int] = {}
    for path in TRAITS.rglob("*.yaml"):
        # Cheap pre-filter: only records that even have GO/InterPro xrefs.
        head = path.read_text(encoding="utf-8", errors="replace")
        if "xrefs:" not in head:
            continue
        ident = ""
        for ln in head.splitlines():
            if ln.startswith("identifier:"):
                ident = ln.split(":", 1)[1].strip()
                break
        want = None  # (object → mapping_source)
        if ident.startswith("InterPro:") and "interpro" in sources:
            key = ident.split(":", 1)[1]
            want = {g: "interpro2go" for g in ipr2go.get(key, ())}
        elif ident.startswith("Pfam:") and "pfam" in sources:
            key = ident.split(":", 1)[1]
            want = {g: "pfam2go" for g in pf2go.get(key, ())}
            want.update({i: "pfam2interpro" for i in pf2ipr.get(key, ())})
        elif ident.startswith("EC:") and "ec" in sources:
            key = ident.split(":", 1)[1]
            want = {g: "ec2go" for g in ec2go.get(key, ())}
        if not want:
            continue

        data = read_trait(path)
        xrefs = list(data.get("xrefs") or [])
        existing_mapped = {m.get("object") for m in (data.get("mapped_xrefs") or [])}
        keep, migrate = [], []
        for x in xrefs:
            if x in want and x not in existing_mapped:
                migrate.append((x, want[x]))
            else:
                keep.append(x)
        if not migrate:
            continue
        mapped = list(data.get("mapped_xrefs") or [])
        for obj, src in migrate:
            mapped.append({"object": obj, "mapping_source": src})
            per_map[src] = per_map.get(src, 0) + 1
        if keep:
            data["xrefs"] = keep
        else:
            data.pop("xrefs", None)
        data["mapped_xrefs"] = mapped
        touched += 1
        moved += len(migrate)
        if args.apply:
            write_trait(path, data)

    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: "
          f"{moved} xref(s) → mapped_xrefs across {touched} record(s).")
    for src, n in sorted(per_map.items()):
        print(f"  {src}: {n}")
    if not args.apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
