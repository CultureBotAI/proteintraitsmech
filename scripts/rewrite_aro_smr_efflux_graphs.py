#!/usr/bin/env python3
"""Rewrite low-scoring SMR proton-antiport efflux ARO graphs.

The targeted records already model SMR-family antibiotic efflux, but their
promoted graphs predate the stricter score and lack fully described,
multi-evidenced edges and an explicit export-to-resistance terminal edge.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed SMR proton-antiport efflux causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
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

SMR_EVIDENCE = {
    "reference": "ARO:0010003",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Small multidrug resistance (SMR) proteins are a relatively small "
        "family of transporters, restricted to prokaryotic cells."
    ),
    "notes": "CARD definition for SMR antibiotic efflux pumps.",
}

SMR_ANTIPORT_EVIDENCE = {
    "reference": "ARO:3000264",
    "snippet": (
        "EmrE is a small multidrug transporter that functions as a homodimer "
        "and that couples the efflux of small polyaromatic cations from the "
        "cell with the import of protons down an electrochemical gradient."
    ),
    "notes": "CARD definition for EmrE proton/drug antiport.",
}

SMR_EXPORT_EVIDENCE = {
    "reference": "PMID:22178925",
    "snippet": (
        "EmrE is one such transporter in Escherichia coli. It exports a broad "
        "class of polyaromatic cation substrates, thus conferring resistance "
        "to drug compounds matching this chemical description."
    ),
    "notes": "Evidence for SMR multidrug export by an EmrE-family transporter.",
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

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

ANTIPORT_NODE = {
    "node_id": "antiport",
    "label": "drug/proton antiporter activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0015297",
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
    "description": "Local state for antibiotic exported from the cell by an SMR efflux pump.",
}

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:0010003", "small-multidrug-resistance-smr-antibiotic-efflux-pump-aro0010003.yaml"),
    Target("ARO:3000264", "emre-aro3000264.yaml"),
    Target("ARO:3000768", "abes-aro3000768.yaml"),
    Target("ARO:3003062", "ykkcd-aro3003062.yaml"),
    Target("ARO:3003836", "qach-aro3003836.yaml"),
    Target("ARO:3004038", "pseudomonas-aeruginosa-emre-aro3004038.yaml"),
    Target("ARO:3004039", "escherichia-coli-emre-aro3004039.yaml"),
    Target("ARO:3004585", "klebsiella-pneumoniae-kpnef-aro3004585.yaml"),
    Target("ARO:3005098", "qacl-aro3005098.yaml"),
    Target("ARO:3007012", "sepa-aro3007012.yaml"),
    Target("ARO:3007014", "qacj-aro3007014.yaml"),
    Target("ARO:3007015", "qacg-aro3007015.yaml"),
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
    return [copy.deepcopy(node) for node in sorted(drug_nodes, key=_drug_sort_key)]


def _drug_edges_by_object(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    edges = {}
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
            and _is_drug_node_id(str(edge.get("object", "")))
        ):
            edges[str(edge["object"])] = copy.deepcopy(edge)
    return edges


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
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


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        SMR_EVIDENCE,
        SMR_ANTIPORT_EVIDENCE,
        SMR_EXPORT_EVIDENCE,
    )
    drug_nodes = _drug_nodes(old_graph)
    drug_edges = _drug_edges_by_object(old_graph)
    missing_drug_edges = {
        str(node["node_id"])
        for node in drug_nodes
        if str(node["node_id"]) not in drug_edges
    }
    if missing_drug_edges:
        missing = ", ".join(sorted(missing_drug_edges))
        raise ValueError(f"{record['identifier']}: missing determinant→drug edge(s): {missing}")

    confers_edges = [
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            str(node["node_id"]),
            f"CARD asserts that this SMR determinant confers resistance to {node['label']}.",
            record_evidence,
            SMR_EVIDENCE,
            *tuple(_dicts(drug_edges[str(node["node_id"])].get("evidence"))),
        )
        for node in drug_nodes
    ]
    input_edges = [
        _edge(
            "antiport",
            "has input (exported drug)",
            "RO:0002233",
            str(node["node_id"]),
            "The drug class is the exported substrate of the SMR proton antiporter.",
            record_evidence,
            ANTIBIOTIC_EFFLUX_EVIDENCE,
            SMR_EVIDENCE,
            SMR_ANTIPORT_EVIDENCE,
            *tuple(_dicts(drug_edges[str(node["node_id"])].get("evidence"))),
        )
        for node in drug_nodes
    ]

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → SMR proton antiport → resistance",
        "description": (
            "Curated resistance-causation graph for SMR antibiotic efflux pumps. "
            "The determinant enables proton-coupled antiport that exports "
            "antibiotic from the cell and lowers intracellular drug exposure."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(ANTIPORT_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(EXTRUDED_DRUG_NODE),
            *drug_nodes,
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies SMR pumps under the antibiotic efflux resistance mechanism.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting antibiotics out of the cell.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The SMR determinant exports antibiotic from the cell by proton-coupled antiport.",
                *common_evidence,
            ),
            *confers_edges,
            _edge(
                "determinant",
                "enables (drug/proton antiport)",
                "RO:0002327",
                "antiport",
                "The SMR determinant enables proton-coupled export of drug substrates.",
                record_evidence,
                SMR_EVIDENCE,
                SMR_ANTIPORT_EVIDENCE,
                SMR_EXPORT_EVIDENCE,
            ),
            *input_edges,
            _edge(
                "antiport",
                "causally upstream of",
                "RO:0002411",
                "export",
                "Proton-coupled antiport exports antibiotic across the plasma membrane.",
                record_evidence,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                SMR_EVIDENCE,
                SMR_ANTIPORT_EVIDENCE,
                SMR_EXPORT_EVIDENCE,
            ),
            _edge(
                "export",
                "causally upstream of",
                "RO:0002411",
                "extruded_drug",
                "Transmembrane export moves antibiotic outside the cell.",
                record_evidence,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                SMR_EVIDENCE,
                SMR_EXPORT_EVIDENCE,
            ),
            _edge(
                "extruded_drug",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Moving antibiotic outside the cell lowers intracellular drug exposure.",
                record_evidence,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                SMR_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> dict[str, Any]:
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
    return graphs[0]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    old_graph = _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, old_graph)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an SMR proton-antiport efflux target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one of the SMR proton-antiport YAML files",
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
