#!/usr/bin/env python3
"""MECHANISTIC layer for molecular-interaction traits beyond enzyme reactions
(mechanistic-layer-covers-interactions-not-just-reactions):

  • FUNC_TRANSPORT — the transport mechanism: which molecule(s) the transporter
    moves across the membrane. Composed from the record's TRANSPORTED
    `chemical_participants` (ChEBI ids → names via docs/data/chebi.json), which is
    additive over the TCDB *family* classification in the main definition.
  • SEQ_PTM_SITE / SEQ_MODIFIED_RESIDUE / SEQ_CROSSLINK_SITE / SEQ_LIPIDATION_SITE /
    SEQ_GLYCOSYLATION_SITE whose definition is a clean modification description
    ("A protein modification that …", from PSI-MOD/dbPTM) — the modification IS a
    molecular-level mechanism, so the description is typed verbatim as MECHANISTIC.
    Records whose definition is instead a PROSITE/InterPro *signature* blurb (an
    enzyme-family paragraph mis-carrying a PTM category) are skipped — no faithful
    modification mechanism to lift.

The heterogeneous InterPro SEQ_ACTIVE_SITE / SEQ_BINDING_SITE prose is left to a
later, cleaner pass (their definitions are enzyme-family descriptions, not crisp
interaction statements).

Idempotent; appends into any existing `definitions:` list via deflib. Dry-run
unless --apply. Stdlib-only (reads chebi.json if present).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deflib import add_layer, def_body  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
CHEBI_JSON = REPO_ROOT / "docs" / "data" / "chebi.json"

MOD_CATS = {"SEQ_PTM_SITE", "SEQ_MODIFIED_RESIDUE", "SEQ_CROSSLINK_SITE",
            "SEQ_LIPIDATION_SITE", "SEQ_GLYCOSYLATION_SITE"}
_CAT = re.compile(r"(?m)^trait_category:\s*(\S+)")
_DEFSRC = re.compile(r"(?m)^definition_source:\s*(.+?)\s*$")


def load_chebi_names() -> dict:
    if not CHEBI_JSON.exists():
        return {}
    try:
        raw = json.loads(CHEBI_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for k, v in raw.items():
        nm = v if isinstance(v, str) else (v or {}).get("name", "")
        out[k] = re.sub(r"<[^>]+>", "", nm)  # ChEBI names carry <em>…</em> markup
    return out


# ChEBI classes too generic to be a meaningful transport substrate — a
# "transports a molecule" statement carries no mechanism, so drop these and skip
# the record if nothing specific remains.
_GENERIC_CHEBI = {
    "molecule", "protein", "polypeptide chain", "protein polypeptide chain",
    "chemical entity", "molecular entity", "ion", "cation", "anion",
    "inorganic ion", "solute", "substance", "group", "polyatomic entity",
    "chemical substance", "macromolecule",
}


def transported_names(text: str, chebi: dict) -> list[str]:
    """Names of the specific molecules the record transports (TRANSPORTED role),
    in order, deduped, generic classes dropped, capped."""
    names, seen = [], set()
    for m in re.finditer(
            r"(?ms)^\s*-\s*chebi:\s*(CHEBI:\d+)\s*\n\s*role:\s*(\w+)", text):
        cid, role = m.group(1), m.group(2)
        if role != "TRANSPORTED":
            continue
        nm = chebi.get(cid, "")
        low = nm.lower().strip()
        if nm and low not in seen and low not in _GENERIC_CHEBI:
            seen.add(low)
            names.append(nm)
    return names[:5]


def compose(text: str, cat: str, chebi: dict) -> tuple[str, str] | None:
    """(mechanistic_text, source) or None."""
    if cat == "FUNC_TRANSPORT":
        names = transported_names(text, chebi)
        if not names:
            return None
        joined = names[0] if len(names) == 1 else \
            ", ".join(names[:-1]) + " and " + names[-1]
        return f"Mediates the transmembrane transport of {joined}.", "TCDB / ChEBI"
    if cat in MOD_CATS:
        body = def_body(text)
        if body.lower().startswith("a protein modification"):
            src = (_DEFSRC.search(text) or [0, "PSI-MOD"])[1].strip().strip('"')
            return body, src
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    chebi = load_chebi_names()
    counts = {"FUNC_TRANSPORT": 0, "modification": 0}
    skipped = na = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        cm = _CAT.search(text)
        if not cm:
            continue
        cat = cm.group(1)
        if cat != "FUNC_TRANSPORT" and cat not in MOD_CATS:
            continue
        if "kind: MECHANISTIC" in text:
            skipped += 1
            continue
        got = compose(text, cat, chebi)
        if not got:
            na += 1
            continue
        mtext, source = got
        new, changed = add_layer(text, "MECHANISTIC", mtext, source)
        if not changed:
            skipped += 1
            continue
        counts["FUNC_TRANSPORT" if cat == "FUNC_TRANSPORT" else "modification"] += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")
    total = sum(counts.values())
    print(f"interaction MECHANISTIC: {'added' if args.apply else 'would add'} "
          f"{total:,} ({counts}); already had {skipped:,}; no core {na:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
