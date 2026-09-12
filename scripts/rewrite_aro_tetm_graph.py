#!/usr/bin/env python3
"""Supplement the Tet(M) tetracycline ribosomal-protection graph.

The existing graph already captures the Tet(M)-specific target-protection
mechanism. This pass keeps that topology and adds independent CARD, Pfam, and
literature support so every edge has at least two evidence sources.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TARGET = (
    ROOT
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "tet-m-aro3000186.yaml"
)

HISTORY_ACTION = "Supplemented Tet(M) ribosomal-protection graph evidence"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TETM_EVIDENCE = {
    "reference": "ARO:3000186",
    "snippet": (
        "Tet(M) is a ribosomal protection protein that confers tetracycline "
        "resistance."
    ),
    "notes": "CARD definition for tet(M).",
}

RPP_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection protein.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, "
        "which process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target protection.",
}

BURDETT_EVIDENCE = {
    "reference": "PMID:8655505",
    "snippet": (
        "Burdett showed Tet(M)-promoted release of ribosome-bound "
        "tetracycline depends on GTP."
    ),
    "notes": "Primary biochemical support for GTP-dependent tetracycline release.",
}

DONHOFER_EVIDENCE = {
    "reference": "PMID:23027944",
    "snippet": (
        "Dönhöfer et al. resolved a TetM-70S ribosome complex and modeled "
        "domain-IV displacement of tetracycline."
    ),
    "notes": "Cryo-EM support for TetM-mediated ribosomal protection.",
}

PFAM_GTPASE_EVIDENCE = {
    "reference": "Pfam:PF00009",
    "snippet": "Elongation factor Tu GTP binding domain.",
    "notes": "KB trait Pfam:PF00009 (SEQ_DOMAIN).",
}

PFAM_EFG_DOMAIN2_EVIDENCE = {
    "reference": "Pfam:PF03144",
    "snippet": "Elongation factor Tu domain 2.",
    "notes": "KB trait Pfam:PF03144 (SEQ_DOMAIN).",
}

SUPPLEMENTAL_EVIDENCE: dict[tuple[str, str], tuple[dict[str, str], ...]] = {
    ("tetm", "rpp_family"): (TETM_EVIDENCE, RPP_EVIDENCE, DONHOFER_EVIDENCE),
    ("tetm", "protection"): (
        TETM_EVIDENCE,
        TARGET_PROTECTION_EVIDENCE,
        BURDETT_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("gtp", "protection"): (
        PFAM_GTPASE_EVIDENCE,
        BURDETT_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("protection", "tetracycline"): (
        TARGET_PROTECTION_EVIDENCE,
        BURDETT_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("protection", "resistance"): (
        TETM_EVIDENCE,
        RPP_EVIDENCE,
        TARGET_PROTECTION_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("tetm", "resistance"): (
        TETM_EVIDENCE,
        RPP_EVIDENCE,
        TARGET_PROTECTION_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("gtpase_domain", "tetm"): (
        PFAM_GTPASE_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("efg_domain2", "tetm"): (
        PFAM_EFG_DOMAIN2_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
    ("gtpase_domain", "protection"): (
        PFAM_GTPASE_EVIDENCE,
        BURDETT_EVIDENCE,
        DONHOFER_EVIDENCE,
    ),
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        key = str(item["reference"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3000186":
        raise ValueError(f"expected ARO:3000186, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    graphs = _dicts(out.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError("ARO:3000186: expected exactly one causal graph")

    graph = graphs[0]
    edges = _dicts(graph.get("edges"))
    if len(edges) != len(SUPPLEMENTAL_EVIDENCE):
        raise ValueError(
            "ARO:3000186: expected "
            f"{len(SUPPLEMENTAL_EVIDENCE)} edges, found {len(edges)}"
        )

    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        key = (str(edge.get("subject")), str(edge.get("object")))
        try:
            supplemental = SUPPLEMENTAL_EVIDENCE[key]
        except KeyError as exc:
            raise ValueError(f"ARO:3000186: unexpected edge {key}") from exc

        seen_edges.add(key)
        edge["evidence"] = _unique_evidence(
            *_dicts(edge.get("evidence")),
            *supplemental,
        )

    missing_edges = set(SUPPLEMENTAL_EVIDENCE).difference(seen_edges)
    if missing_edges:
        raise ValueError(f"ARO:3000186: missing edges {sorted(missing_edges)}")

    out["causal_graphs"] = graphs
    return out, out["causal_graphs"] != record.get("causal_graphs")


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def run(apply: bool) -> bool:
    before = TARGET.read_text(encoding="utf-8")
    after, changed = enrich_text(before)
    if changed:
        print(f"  {'wrote' if apply else 'would write'} {TARGET.name}")
        if apply:
            TARGET.write_text(after, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
