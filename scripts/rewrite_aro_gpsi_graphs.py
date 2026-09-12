#!/usr/bin/env python3
"""Curate gpsI/Rv2783c pyrazinamide-resistance graphs.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Curated gpsI/Rv2783c pyrazinamide-resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

PZA_RV2783_RESISTANCE_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.00070-17",
    "snippet": (
        "Njire et al. found two PZA-resistant clinical isolates with the same "
        "Rv2783c G199A/Asp67Asn substitution and showed that expressing "
        "Rv2783c-Asp67Asn increased the pyrazinamide MIC in M. tuberculosis."
    ),
    "notes": "Experimental evidence that an Rv2783c/gpsI missense mutation confers PZA resistance.",
}

POA_BINDING_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.00070-17",
    "snippet": (
        "Wild-type Rv2783 bound pyrazinoic acid, whereas Rv2783-Asp67Asn did "
        "not bind pyrazinoic acid detectably in the titration assay."
    ),
    "notes": "Experimental evidence that the gpsI resistance mutation reduces active-drug binding.",
}

POA_ACTIVITY_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.00070-17",
    "snippet": (
        "Pyrazinoic acid significantly inhibited wild-type Rv2783 RNA "
        "polymerization and phosphorolysis activities but not those of the "
        "Rv2783-Asp67Asn mutant protein."
    ),
    "notes": "Experimental evidence that the mutant gpsI activity withstands POA inhibition.",
}

PNPASE_EVIDENCE = {
    "reference": "GO:0004654",
    "snippet": (
        "Catalysis of the reaction: RNA(n+1) + phosphate = RNA(n) + a "
        "nucleoside diphosphate."
    ),
    "notes": "Gene Ontology definition for polyribonucleotide nucleotidyltransferase activity.",
}

PYRAZINE_RELATION_EVIDENCE = {
    "reference": "ARO:3004880",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007155 ! pyrazine antibiotic",
    "notes": "CARD asserts this drug-class relation on the pyrazinamide resistant gpsI parent.",
}

PYRAZINAMIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3004977",
    "snippet": "relationship: confers_resistance_to_antibiotic ARO:3003413 ! pyrazinamide",
    "notes": "CARD asserts this direct pyrazinamide resistance relation on the M. tuberculosis leaf.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

POA_BINDING_NODE = {
    "node_id": "poa_binding",
    "label": "reduced pyrazinoic acid binding to Rv2783",
    "node_type": "STATE",
    "description": (
        "Local state for gpsI/Rv2783c resistance mutations that reduce binding "
        "of the active pyrazinamide metabolite pyrazinoic acid."
    ),
}

PNPASE_NODE = {
    "node_id": "pnpase",
    "label": "POA-insensitive polyribonucleotide nucleotidyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004654",
    "description": (
        "Grounded to Rv2783 polyribonucleotide nucleotidyltransferase activity "
        "and scoped here to the mutant activity that withstands pyrazinoic acid."
    ),
}

PYRAZINE_NODE = {
    "node_id": "drug0",
    "label": "pyrazine antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007155",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "pyrazinamide resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Pyrazinamide resistance phenotype conferred by an Rv2783/gpsI mutation "
        "that reduces pyrazinoic-acid binding."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    has_pyrazine_class: bool = False
    has_direct_pyrazinamide: bool = False


TARGETS = (
    Target("ARO:3004879", "antibiotic-resistant-gpsi-aro3004879.yaml"),
    Target(
        "ARO:3004880",
        "pyrazinamide-resistant-gpsi-aro3004880.yaml",
        has_pyrazine_class=True,
    ),
    Target(
        "ARO:3004977",
        (
            "mycobacterium-tuberculosis-gpsi-with-mutations-conferring-resistance-to-"
            "pyrazina-aro3004977.yaml"
        ),
        has_pyrazine_class=True,
        has_direct_pyrazinamide=True,
    ),
)
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS}


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


def _drug_edge(record_evidence: dict[str, str]) -> dict[str, Any]:
    return _edge(
        "determinant",
        "confers resistance to (drug class)",
        "ARO:2000001",
        "drug0",
        "CARD links pyrazinamide-resistant gpsI to the pyrazine antibiotic drug class.",
        record_evidence,
        PYRAZINE_RELATION_EVIDENCE,
        PZA_RV2783_RESISTANCE_EVIDENCE,
    )


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    core_evidence = (
        record_evidence,
        MUTATION_EVIDENCE,
        PZA_RV2783_RESISTANCE_EVIDENCE,
        POA_BINDING_EVIDENCE,
        POA_ACTIVITY_EVIDENCE,
    )
    activity_evidence = (
        record_evidence,
        POA_BINDING_EVIDENCE,
        POA_ACTIVITY_EVIDENCE,
        PNPASE_EVIDENCE,
    )
    resistance_evidence = (
        *core_evidence,
        PYRAZINAMIDE_RELATION_EVIDENCE,
    ) if target.has_direct_pyrazinamide else core_evidence

    nodes = [
        _determinant_node(record),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(POA_BINDING_NODE),
        copy.deepcopy(PNPASE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]
    if target.has_pyrazine_class:
        nodes.append(copy.deepcopy(PYRAZINE_NODE))

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies gpsI resistance under mutation conferring antibiotic resistance.",
            *core_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of",
            "RO:0002411",
            "poa_binding",
            "The Rv2783c Asp67Asn mutation reduces binding of pyrazinoic acid to Rv2783.",
            *core_evidence,
        ),
        _edge(
            "poa_binding",
            "causally upstream of",
            "RO:0002411",
            "pnpase",
            "Reduced pyrazinoic-acid binding lets the mutant Rv2783 PNPase remain active.",
            *activity_evidence,
        ),
        _edge(
            "pnpase",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Retention of Rv2783 PNPase activity despite pyrazinoic acid contributes to PZA resistance.",
            *activity_evidence,
            PZA_RV2783_RESISTANCE_EVIDENCE,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The gpsI/Rv2783c mutation confers the modeled pyrazinamide-resistance phenotype.",
            *resistance_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "gpsI/Rv2783c mutation reduces active-drug binding to support pyrazinamide resistance.",
            *resistance_evidence,
        ),
    ]
    if target.has_pyrazine_class:
        edges.append(_drug_edge(record_evidence))

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → POA-insensitive Rv2783 PNPase activity",
        "description": (
            "Curated gpsI/Rv2783c resistance-causation graph. The graph models "
            "pyrazinamide resistance as mutation-driven loss of pyrazinoic-acid "
            "binding to Rv2783, leaving the mutant polyribonucleotide "
            "nucleotidyltransferase activity tolerant of the active drug metabolite."
        ),
        "nodes": nodes,
        "edges": edges,
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(out, target)]
    return out, out["causal_graphs"] != before or out != record


def enrich_text(text: str, target: Target) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed or out != text


def run(apply: bool) -> int:
    changed_count = 0
    enriched_count = 0
    for target in TARGETS:
        path = ARO / target.filename
        before = path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, target)
        if changed:
            print(f"  {'wrote' if apply else 'would write'} {path.name}")
            changed_count += 1
            if apply:
                path.write_text(after, encoding="utf-8")
        else:
            enriched_count += 1

    print(f"{'changed' if apply else 'would change'}: {changed_count}")
    print(f"already enriched: {enriched_count}")
    if not apply:
        print("dry run -- pass --apply to write")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)
    return run(args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
