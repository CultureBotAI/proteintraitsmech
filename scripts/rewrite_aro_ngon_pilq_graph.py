#!/usr/bin/env python3
"""Curate the Neisseria gonorrhoeae pilQ beta-lactam resistance graph.

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
ARO = ROOT / "data" / "traits" / "function" / "resistance" / "aro"
TARGET = ARO / "neisseria-gonorrhoeae-pilq-gene-conferring-resistance-to-beta-lactam-aro3004835.yaml"

HISTORY_ACTION = "Curated Neisseria gonorrhoeae pilQ beta-lactam influx graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PILQ_EVIDENCE = {
    "reference": "ARO:3004835",
    "snippet": (
        "PilQ is an important gonococcal outer membrane component, member of "
        "secretin protein family, and involved in Type IV pilus formation."
    ),
    "notes": "CARD definition for the N. gonorrhoeae pilQ beta-lactam resistance determinant.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

PILQ_SECRETIN_EVIDENCE = {
    "reference": "PMID:16101998",
    "snippet": (
        "Zhao et al. found that the penC resistance mutation changes PilQ Glu-666 "
        "to Lys and interferes with the SDS-resistant high-molecular-mass PilQ "
        "secretin complex."
    ),
    "notes": "Experimental evidence that penC is a pilQ mutation disrupting PilQ multimer stability.",
}

PILQ_INFLUX_EVIDENCE = {
    "reference": "PMID:16101998",
    "snippet": (
        "Zhao et al. showed that pilQ deletion gives the same antibiotic-resistance "
        "level as penC and proposed that a functional PilQ secretin complex "
        "enhances antibiotic entry into the gonococcal cell."
    ),
    "notes": "Experimental evidence for PilQ-mediated antibiotic influx.",
}

XENOBIOTIC_TRANSPORT_EVIDENCE = {
    "reference": "GO:0042908",
    "snippet": "The directed movement of a xenobiotic into, out of or within a cell.",
    "notes": "GO grounding for broad antibiotic transport.",
}

CEFTRIAXONE_RELATION_EVIDENCE = {
    "reference": "ARO:3004835",
    "snippet": "relationship: confers_resistance_to_antibiotic ARO:0000062 ! ceftriaxone",
    "notes": "CARD asserts this ceftriaxone resistance relation on the pilQ ARO term.",
}

CEPHALOSPORIN_RELATION_EVIDENCE = {
    "reference": "ARO:3003938",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000032 ! cephalosporin",
    "notes": (
        "CARD links the pilQ record to cephalosporins through a beta-lactam "
        "resistance parent."
    ),
}

PENICILLIN_RELATION_EVIDENCE = {
    "reference": "ARO:3003938",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000008 ! penicillin beta-lactam",
    "notes": (
        "CARD links the pilQ record to penicillin beta-lactams through a beta-lactam "
        "resistance parent."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

SECRETIN_STATE_NODE = {
    "node_id": "secretin",
    "label": "destabilized PilQ secretin complex",
    "node_type": "STATE",
    "description": (
        "Local state for penC/pilQ mutations that interfere with the SDS-resistant "
        "high-molecular-mass PilQ multimer."
    ),
}

INFLUX_NODE = {
    "node_id": "influx",
    "label": "reduced beta-lactam diffusion through PilQ",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0042908",
    "description": (
        "Grounded to broad GO xenobiotic transport and scoped here to PilQ-mediated "
        "beta-lactam influx across the gonococcal outer membrane."
    ),
}

DRUG0_NODE = {
    "node_id": "drug0",
    "label": "cephalosporin",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000032",
}

DRUG1_NODE = {
    "node_id": "drug1",
    "label": "penicillin beta-lactam",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000008",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "beta-lactam resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Beta-lactam resistance phenotype conferred by reduced PilQ-mediated "
        "drug influx."
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item["reference"], item["snippet"])
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _drug_edge(
    drug_node: dict[str, str],
    relation_evidence: dict[str, str],
    record_evidence: dict[str, str],
) -> dict[str, Any]:
    return _edge(
        "determinant",
        "confers resistance to (drug class)",
        "ARO:2000001",
        drug_node["node_id"],
        f"CARD asserts that this pilQ determinant confers resistance to {drug_node['label']}.",
        record_evidence,
        relation_evidence,
        PILQ_INFLUX_EVIDENCE,
    )


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    core_evidence = (
        record_evidence,
        PILQ_EVIDENCE,
        MUTATION_EVIDENCE,
        PILQ_SECRETIN_EVIDENCE,
        PILQ_INFLUX_EVIDENCE,
    )
    influx_evidence = (
        record_evidence,
        PILQ_EVIDENCE,
        PILQ_SECRETIN_EVIDENCE,
        PILQ_INFLUX_EVIDENCE,
        XENOBIOTIC_TRANSPORT_EVIDENCE,
    )
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced PilQ beta-lactam influx",
        "description": (
            "Curated resistance-causation graph for gonococcal penC/pilQ mutation. "
            "The graph models PilQ as an outer-membrane secretin whose destabilization "
            "reduces antibiotic influx, not as a penicillin-binding-protein target mutation."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(SECRETIN_STATE_NODE),
            copy.deepcopy(INFLUX_NODE),
            copy.deepcopy(DRUG0_NODE),
            copy.deepcopy(DRUG1_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies penC/pilQ resistance under mutation conferring antibiotic resistance.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "secretin",
                "The penC PilQ mutation interferes with the stable PilQ secretin multimer.",
                *core_evidence,
            ),
            _edge(
                "secretin",
                "causally upstream of",
                "RO:0002411",
                "influx",
                "Destabilization of the PilQ secretin reduces antibiotic diffusion into the cell.",
                *influx_evidence,
            ),
            _edge(
                "influx",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Reduced PilQ-mediated antibiotic entry contributes to beta-lactam resistance.",
                *influx_evidence,
                CEFTRIAXONE_RELATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The pilQ mutation confers the modeled beta-lactam resistance phenotype.",
                *core_evidence,
                CEFTRIAXONE_RELATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "penC/pilQ connects PilQ secretin destabilization to reduced beta-lactam influx.",
                *core_evidence,
                CEFTRIAXONE_RELATION_EVIDENCE,
            ),
            _drug_edge(DRUG0_NODE, CEPHALOSPORIN_RELATION_EVIDENCE, record_evidence),
            _drug_edge(DRUG1_NODE, PENICILLIN_RELATION_EVIDENCE, record_evidence),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3004835":
        raise ValueError(f"expected ARO:3004835, found {record.get('identifier')}")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError("ARO:3004835: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(out)]
    return out, out["causal_graphs"] != before or out != record


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed or out != text


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
