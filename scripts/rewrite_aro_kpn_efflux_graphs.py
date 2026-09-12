#!/usr/bin/env python3
"""Rewrite Klebsiella Kpn efflux ARO graphs.

These low-scoring Kpn records describe two multi-component secondary
transporters:

* KpnE and KpnF are subunits of the KpnEF SMR-like efflux complex.
* KpnG and KpnH are components of the KpnGH-TolC efflux complex.
* KpnGH-TolC is the complete KpnGH/TolC-containing MFS efflux system.

The old KpnE/KpnF graphs projected EmrE homodimer details onto individual
KpnEF subunits, and the old KpnG/KpnH/KpnGH-TolC graphs projected MFS domain
and EmrD structural details onto the whole complex or one of its non-MFS
subunits. The replacement graphs keep the Kpn-specific determinant and direct
CARD drug-class assertions, while using local complex nodes for the causal
transport step.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed Klebsiella Kpn efflux causal graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

EFFLUX_SUBUNIT_EVIDENCE = {
    "reference": "ARO:3000748",
    "snippet": "Subunits of efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump subunits.",
}

SMR_EVIDENCE = {
    "reference": "ARO:0010003",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Small multidrug resistance (SMR) proteins are a relatively small "
        "family of transporters, restricted to prokaryotic cells."
    ),
    "notes": "CARD definition for SMR antibiotic efflux pumps.",
}

MFS_EVIDENCE = {
    "reference": "ARO:0010002",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Major facilitator superfamily (MFS) transporters and ABC "
        "transporters comprise the two largest and most functionally diverse "
        "of the transporter superfamilies. However, MFS transporters are "
        "distinct from ABC transporters in both their primary sequence and "
        "structure and in the mechanism of energy coupling. As secondary "
        "transporters they are, like RND and SMR transporters, energized by "
        "the electrochemical proton gradient."
    ),
    "notes": "CARD definition for MFS antibiotic efflux pumps.",
}

MFS_TRANSPORT_EVIDENCE = {
    "reference": "PMID:38974671",
    "snippet": (
        "The antimicrobial antiport transport cycle in bacteria is driven by "
        "the ion-motive force, an energy mode associated with changes in "
        "transporter conformations and gating during efflux across the "
        "membrane."
    ),
    "notes": "Evidence for ion-motive-force-driven MFS efflux.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

KPN_EF_COMPLEX_NODE = {
    "node_id": "pump_complex",
    "label": "Klebsiella pneumoniae KpnEF",
    "node_type": "PROTEIN",
    "grounding": "ARO:3004585",
    "description": "ARO determinant for the complete KpnEF efflux complex.",
}

KPN_GH_TOLC_COMPLEX_NODE = {
    "node_id": "pump_complex",
    "label": "Klebsiella pneumoniae KpnGH-TolC",
    "node_type": "PROTEIN",
    "grounding": "ARO:3004598",
    "description": (
        "ARO determinant for the KpnGH-TolC efflux complex rather than an MFS "
        "domain asserted on every component of the complex."
    ),
}

EXPORT_NODE = {
    "node_id": "export",
    "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1990961",
}

EXTRUDED_DRUG_NODE = {
    "node_id": "extruded_drug",
    "label": "drug outside the cell",
    "node_type": "STATE",
    "description": "Local state for antibiotic exported from the cell by a Kpn efflux complex.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}

DRUG_ID = re.compile(r"^drug\d+$")


class GraphKind(Enum):
    KPN_EF_SUBUNIT = "KPN_EF_SUBUNIT"
    KPN_GH_SUBUNIT = "KPN_GH_SUBUNIT"
    KPN_GH_TOLC_COMPLEX = "KPN_GH_TOLC_COMPLEX"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: GraphKind


TARGETS: tuple[Target, ...] = (
    Target("ARO:3004580", "klebsiella-pneumoniae-kpne-aro3004580.yaml", GraphKind.KPN_EF_SUBUNIT),
    Target("ARO:3004583", "klebsiella-pneumoniae-kpnf-aro3004583.yaml", GraphKind.KPN_EF_SUBUNIT),
    Target("ARO:3004588", "klebsiella-pneumoniae-kpng-aro3004588.yaml", GraphKind.KPN_GH_SUBUNIT),
    Target("ARO:3004597", "klebsiella-pneumoniae-kpnh-aro3004597.yaml", GraphKind.KPN_GH_SUBUNIT),
    Target(
        "ARO:3004598",
        "klebsiella-pneumoniae-kpngh-tolc-aro3004598.yaml",
        GraphKind.KPN_GH_TOLC_COMPLEX,
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


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


def _is_drug_node_id(node_id: str) -> bool:
    return DRUG_ID.fullmatch(node_id) is not None


def _drug_sort_key(node: dict[str, Any]) -> int:
    match = DRUG_ID.fullmatch(str(node["node_id"]))
    if match is None:
        raise ValueError(f"unexpected drug node_id: {node['node_id']}")
    return int(str(node["node_id"])[len("drug") :])


def _drug_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    drug_nodes = [
        node
        for node in _dicts(graph.get("nodes"))
        if _is_drug_node_id(str(node.get("node_id", "")))
    ]
    if not drug_nodes:
        raise ValueError("missing drug node")
    return [copy.deepcopy(node) for node in sorted(drug_nodes, key=_drug_sort_key)]


def _drug_relation_evidence(
    graph: dict[str, Any],
    drug_node_ids: set[str],
) -> dict[str, list[dict[str, Any]]]:
    by_object: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in drug_node_ids}
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
        ):
            object_ = str(edge.get("object", ""))
            if object_ in by_object:
                by_object[object_].extend(
                    item
                    for item in _dicts(edge.get("evidence"))
                    if str(item.get("snippet", "")).startswith(
                        "relationship: confers_resistance_to_drug_class "
                    )
                )
    return by_object


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["reference"]), str(item.get("snippet", "")))
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
    *evidence: dict[str, Any],
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


def _canonical_drug_edges(
    record: dict[str, Any],
    old_graph: dict[str, Any],
    *evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

    return [
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            str(drug_node["node_id"]),
            f"CARD asserts that this determinant confers resistance to {drug_node['label']}.",
            *relation_evidence[str(drug_node["node_id"])],
            _record_evidence(record),
            *evidence,
        )
        for drug_node in drug_nodes
    ]


def _drug_input_edges(
    old_graph: dict[str, Any],
    *evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

    return [
        _edge(
            "export",
            "has input (the drug)",
            "RO:0002233",
            str(drug_node["node_id"]),
            f"The efflux process exports this CARD-linked {drug_node['label']} class.",
            *evidence,
            *relation_evidence[str(drug_node["node_id"])],
        )
        for drug_node in drug_nodes
    ]


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _validate_direct_drug_edges(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    drug_node_ids = {node_id for node_id in nodes if _is_drug_node_id(node_id)}
    if not drug_node_ids:
        raise ValueError(f"{target.identifier}: missing drug node(s)")

    seen: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in seen:
            subject, _, object_ = key
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)

        subject, predicate_id, object_ = key
        if (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        ):
            direct_drug_edges.add(object_)

    missing_drug_edges = sorted(drug_node_ids - direct_drug_edges)
    if missing_drug_edges:
        missing = ", ".join(missing_drug_edges)
        raise ValueError(f"{target.identifier}: missing drug edge(s): {missing}")


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    _validate_direct_drug_edges(graphs[0], target)


def _subunit_graph(
    record: dict[str, Any],
    old_graph: dict[str, Any],
    target: Target,
) -> dict[str, Any]:
    is_kpnef = target.kind == GraphKind.KPN_EF_SUBUNIT
    family_evidence = SMR_EVIDENCE if is_kpnef else MFS_EVIDENCE
    pump_complex = KPN_EF_COMPLEX_NODE if is_kpnef else KPN_GH_TOLC_COMPLEX_NODE
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        EFFLUX_SUBUNIT_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        family_evidence,
    )
    complex_evidence = (record_evidence, EFFLUX_SUBUNIT_EVIDENCE, family_evidence)

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → {pump_complex['label']} → resistance",
        "description": (
            "Curated resistance-causation graph for Klebsiella secondary-transporter "
            "efflux-pump subunits. The determinant is modeled as part of its "
            "Kpn efflux complex rather than as a complete single-protein transporter."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            *_drug_nodes(old_graph),
            copy.deepcopy(pump_complex),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(EXTRUDED_DRUG_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this efflux-pump subunit under the antibiotic "
                "efflux resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting "
                "antibiotics out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "This Kpn subunit contributes to an efflux complex that pumps "
                "antibiotic out of the cell.",
                *efflux_evidence,
            ),
            *_canonical_drug_edges(
                record,
                old_graph,
                EFFLUX_SUBUNIT_EVIDENCE,
                family_evidence,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "pump_complex",
                "The determinant is a subunit of the modeled Kpn efflux complex.",
                *complex_evidence,
            ),
            _edge(
                "pump_complex",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The complete Kpn efflux complex exports antibiotics from the cell.",
                *efflux_evidence,
            ),
            *_drug_input_edges(old_graph, *efflux_evidence),
            _edge(
                "export",
                "causally upstream of (moves drug out of the cell)",
                "RO:0002411",
                "extruded_drug",
                "Antibiotic export moves intracellular drug outside the cell.",
                *efflux_evidence,
            ),
            _edge(
                "extruded_drug",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Moving drug outside the cell lowers intracellular drug "
                "exposure and causes the modeled resistance phenotype.",
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                family_evidence,
            ),
        ],
    }


def _complex_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        MFS_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        MFS_TRANSPORT_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → MFS antibiotic efflux → resistance",
        "description": (
            "Curated resistance-causation graph for the KpnGH-TolC efflux "
            "complex. The determinant is modeled as a complete Kpn "
            "secondary-transporter efflux system without projecting a single "
            "MFS domain or fold onto the whole complex."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            *_drug_nodes(old_graph),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(EXTRUDED_DRUG_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies KpnGH-TolC under the antibiotic efflux "
                "resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting "
                "antibiotics out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The KpnGH-TolC efflux complex exports antibiotic from the cell.",
                *efflux_evidence,
            ),
            *_canonical_drug_edges(
                record,
                old_graph,
                MFS_EVIDENCE,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "export",
                "KpnGH-TolC is modeled as a complete efflux system that exports "
                "antibiotics from the cell.",
                *efflux_evidence,
            ),
            *_drug_input_edges(old_graph, *efflux_evidence),
            _edge(
                "export",
                "causally upstream of (moves drug out of the cell)",
                "RO:0002411",
                "extruded_drug",
                "Antibiotic export moves intracellular drug outside the cell.",
                *efflux_evidence,
            ),
            _edge(
                "extruded_drug",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Moving drug outside the cell lowers intracellular drug "
                "exposure and causes the modeled resistance phenotype.",
                MFS_EVIDENCE,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    old_graph = record["causal_graphs"][0]
    if target.kind == GraphKind.KPN_GH_TOLC_COMPLEX:
        graph = _complex_graph(record, old_graph)
    else:
        graph = _subunit_graph(record, old_graph, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Klebsiella Kpn efflux target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the five Klebsiella Kpn YAML files",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
