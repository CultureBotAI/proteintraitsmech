#!/usr/bin/env python3
"""Extract a GO → ChEBI mapping from the go-plus logical-definition cross-products
→ data/mappings/go2chebi.tsv. This is the source of MAPPING-DERIVED chemistry for
records grounded to a GO molecular-function term (a GO "X binding" / "X metabolic
process" term carries `has_input/has_output CHEBI:X` in its logical definition).

go-plus's .obo/current/snapshot endpoints 403 to bots; the OBO-Graphs JSON at
https://purl.obolibrary.org/obo/go/extensions/go-plus.json serves fine — fetch it
to data/raw/go-plus.json (`just build-go2chebi`), then run this. The tiny output
TSV is tracked, so the docs build never needs the 135 MB source. Stdlib-only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "data" / "raw" / "go-plus.json"
OUT = REPO_ROOT / "data" / "mappings" / "go2chebi.tsv"


def main() -> int:
    if not SRC.exists():
        print("missing data/raw/go-plus.json; run `just build-go2chebi`", file=sys.stderr)
        return 2
    graph = json.loads(SRC.read_text(encoding="utf-8"))["graphs"][0]
    go2chebi: dict[str, list[str]] = {}
    for ax in graph.get("logicalDefinitionAxioms", []):
        cls = ax.get("definedClassId", "")
        if "GO_" not in cls:
            continue
        chebis = ["CHEBI:" + r["fillerId"].split("CHEBI_")[1]
                  for r in (ax.get("restrictions") or []) if "CHEBI_" in (r.get("fillerId") or "")]
        if chebis:
            go2chebi.setdefault("GO:" + cls.split("GO_")[1], []).extend(chebis)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("# GO term\tChEBI(s)  — logical-definition cross-products from go-plus.json\n")
        for gid in sorted(go2chebi):
            fh.write(f"{gid}\t{';'.join(dict.fromkeys(go2chebi[gid]))}\n")
    print(f"wrote {len(go2chebi):,} GO→ChEBI rows → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
