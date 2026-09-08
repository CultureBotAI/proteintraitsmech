#!/usr/bin/env python3
"""Rewrite APH aminoglycoside phosphotransferase ARO causal graphs.

The rank-77 APH group records already ground the ARO antibiotic inactivation
and phosphorylation mechanism nodes plus the APH Pfam/CATH structural nodes,
but every mechanistic edge carries only the old APH structural-paper title and
most edges have no description. This updater keeps the APH structural nodes
and routes phosphorylation through broad alcohol-acceptor phosphotransferase
activity plus the phosphorylated inactive aminoglycoside product state.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed APH aminoglycoside phosphotransferase causal graphs",
    "llm_assisted": True,
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

PHOSPHORYLATION_EVIDENCE = {
    "reference": "ARO:3000105",
    "snippet": "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
    "notes": "CARD definition for phosphorylation of antibiotic conferring resistance.",
}

APH_PARENT_EVIDENCE = {
    "reference": "ARO:3000114",
    "snippet": (
        "Kinases that modify aminoglycoside antibiotics by phosphorylation "
        "using NTPs as cofactor."
    ),
    "notes": "CARD definition for aminoglycoside phosphotransferase (APH).",
}

AMINOGLYCOSIDE_MODIFYING_EVIDENCE = {
    "reference": "ARO:3007380",
    "snippet": (
        "Resistance-conferring genetic elements encoding proteins involved in "
        "the enzymatic inactivation of aminoglycoside antibiotics through "
        "chemical modification."
    ),
    "notes": "CARD definition for aminoglycoside-modifying enzymes.",
}

GO_PHOSPHOTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016773",
    "snippet": (
        "Catalysis of the transfer of a phosphorus-containing group from one "
        "compound to an alcohol group acceptor."
    ),
    "notes": "GO grounding for broad phosphotransferase activity on hydroxyl acceptors.",
}

PFAM_EVIDENCE = {
    "reference": "Pfam:PF01636",
    "snippet": "Phosphotransferase enzyme family",
    "notes": "Pfam family for aminoglycoside phosphotransferases.",
}

CATH_EVIDENCE = {
    "reference": "CATH:3.90.1200",
    "snippet": "Aminoglycoside 3'-phosphotransferase; Chain: A, domain 2",
    "notes": "CATH grounding for the protein-kinase-like APH fold.",
}

APH_STRUCTURE_EVIDENCE = {
    "reference": "PMID:9200607",
    "snippet": (
        "Structure of an enzyme required for aminoglycoside antibiotic "
        "resistance reveals homology to eukaryotic protein kinases."
    ),
    "notes": "Structural support for the APH protein-kinase-like fold.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MECH1_NODE = {
    "node_id": "mech1",
    "label": "phosphorylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000105",
}

TRANSFER_NODE = {
    "node_id": "transfer",
    "label": "phosphotransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016773",
    "description": (
        "Grounded to the broad GO alcohol-acceptor phosphotransferase "
        "activity term and scoped here to APH-mediated aminoglycoside "
        "phosphorylation."
    ),
}

PHOSPHORYLATED_NODE = {
    "node_id": "phosphorylated",
    "label": "phosphorylated inactive aminoglycoside antibiotic",
    "node_type": "STATE",
    "description": (
        "Local state for an aminoglycoside antibiotic after APH-mediated "
        "phosphorylation."
    ),
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "aminoglycoside phosphotransferase domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF01636",
    "description": "Aminoglycoside phosphotransferase catalytic domain found in APH enzymes.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "aminoglycoside phosphotransferase protein-kinase-like fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.90.1200",
    "description": "Protein-kinase-like aminoglycoside phosphotransferase fold.",
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
}

LEGACY_EDGE_KEYS = {
    ("domain", "RO:0002327", "mech1"),
}

CANONICAL_EDGE_KEYS = {
    ("determinant", "RO:0002327", "transfer"),
    ("transfer", "RO:0002411", "phosphorylated"),
    ("phosphorylated", "RO:0002411", "resistance"),
    ("domain", "RO:0002327", "transfer"),
}

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3000128 aph-2-aro3000128.yaml
ARO:3002634 aph-2-ie-aro3002634.yaml
ARO:3004191 aph-2-if-aro3004191.yaml
ARO:3002669 aph-2-ig-aro3002669.yaml
ARO:3002635 aph-2-iia-aro3002635.yaml
ARO:3002636 aph-2-iiia-aro3002636.yaml
ARO:3002637 aph-2-iva-aro3002637.yaml
ARO:3000126 aph-3-aro3000126.yaml
ARO:3000127 aph-3-aro3000127.yaml
ARO:3007406 aph-3-i-aro3007406.yaml
ARO:3007414 aph-3-i-aro3007414.yaml
ARO:3002638 aph-3-ia-aro3002638.yaml
ARO:3002641 aph-3-ia-aro3002641.yaml
ARO:3002639 aph-3-ib-aro3002639.yaml
ARO:3002642 aph-3-ib-aro3002642.yaml
ARO:3002640 aph-3-ic-aro3002640.yaml
ARO:3007408 aph-3-ii-aro3007408.yaml
ARO:3002644 aph-3-iia-aro3002644.yaml
ARO:3002645 aph-3-iib-aro3002645.yaml
ARO:3002646 aph-3-iic-aro3002646.yaml
ARO:3007409 aph-3-iii-aro3007409.yaml
ARO:3002647 aph-3-iiia-aro3002647.yaml
ARO:3007410 aph-3-iv-aro3007410.yaml
ARO:3002648 aph-3-iva-aro3002648.yaml
ARO:3004087 aph-3-ixa-aro3004087.yaml
ARO:3007411 aph-3-v-aro3007411.yaml
ARO:3002649 aph-3-va-aro3002649.yaml
ARO:3002650 aph-3-vb-aro3002650.yaml
ARO:3002651 aph-3-vc-aro3002651.yaml
ARO:3007412 aph-3-vi-aro3007412.yaml
ARO:3002652 aph-3-via-aro3002652.yaml
ARO:3002653 aph-3-vib-aro3002653.yaml
ARO:3007413 aph-3-vii-aro3007413.yaml
ARO:3002654 aph-3-viia-aro3002654.yaml
ARO:3004680 aph-3-viiia-aro3004680.yaml
ARO:3004086 aph-3-viiib-aro3004086.yaml
ARO:3000155 aph-4-aro3000155.yaml
ARO:3007418 aph-4-i-aro3007418.yaml
ARO:3002655 aph-4-ia-aro3002655.yaml
ARO:3002656 aph-4-ib-aro3002656.yaml
ARO:3000151 aph-6-aro3000151.yaml
ARO:3007415 aph-6-i-aro3007415.yaml
ARO:3002657 aph-6-ia-aro3002657.yaml
ARO:3002658 aph-6-ib-aro3002658.yaml
ARO:3002659 aph-6-ic-aro3002659.yaml
ARO:3002660 aph-6-id-aro3002660.yaml
ARO:3000154 aph-7-aro3000154.yaml
ARO:3007417 aph-7-i-aro3007417.yaml
ARO:3002661 aph-7-ia-aro3002661.yaml
ARO:3000153 aph-9-aro3000153.yaml
ARO:3007416 aph-9-i-aro3007416.yaml
ARO:3002662 aph-9-ia-aro3002662.yaml
ARO:3002663 aph-9-ib-aro3002663.yaml
ARO:3007539 aph-9-ic-aro3007539.yaml
ARO:3004675 apha15-aro3004675.yaml
ARO:3003918 apma-aro3003918.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _is_drug_node_id(node_id: str) -> bool:
    return DRUG_ID.fullmatch(node_id) is not None


def _drug_sort_key(node: dict[str, Any]) -> int:
    match = DRUG_ID.fullmatch(str(node["node_id"]))
    if match is None:
        raise ValueError(f"unexpected drug node_id: {node['node_id']}")
    return int(str(node["node_id"])[len("drug") :])


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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


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
        if edge.get("subject") != "determinant":
            continue
        if edge.get("predicate_id") != "ARO:2000001":
            continue
        object_ = str(edge.get("object", ""))
        if object_ not in by_object:
            continue
        by_object[object_].extend(
            item
            for item in _dicts(edge.get("evidence"))
            if str(item.get("snippet", "")).startswith(
                "relationship: confers_resistance_to_drug_class "
            )
        )
    return by_object


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    drug_node_ids = {node_id for node_id in nodes if _is_drug_node_id(node_id)}
    required_nodes = {"determinant", "mech0", "mech1", "domain", "fold", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")
    if not drug_node_ids:
        raise ValueError(f"{target.identifier}: missing drug node(s)")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        subject, predicate_id, object_ = key
        transfer_drug_edge = (
            subject == "transfer"
            and predicate_id == "RO:0002233"
            and object_ in drug_node_ids
        )
        direct_drug_edge = (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        )
        allowed = (
            key in CORE_EDGE_KEYS
            or key in LEGACY_EDGE_KEYS
            or key in CANONICAL_EDGE_KEYS
            or transfer_drug_edge
            or direct_drug_edge
        )
        if not allowed:
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)
        if direct_drug_edge:
            direct_drug_edges.add(object_)

    missing_edges = sorted(CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

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
    _validate_graph(graphs[0], target)


def _canonical_drug_edges(
    record: dict[str, Any],
    old_graph: dict[str, Any],
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
            f"CARD asserts that APH determinants confer resistance to {drug_node['label']}.",
            *relation_evidence[str(drug_node["node_id"])],
            _record_evidence(record),
            APH_PARENT_EVIDENCE,
            PHOSPHORYLATION_EVIDENCE,
            AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
        )
        for drug_node in drug_nodes
    ]


def _drug_input_edges(drug_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _edge(
            "transfer",
            "has input",
            "RO:0002233",
            str(drug_node["node_id"]),
            "APH-mediated phosphotransfer modifies this aminoglycoside drug class.",
            APH_PARENT_EVIDENCE,
            PHOSPHORYLATION_EVIDENCE,
            AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
            GO_PHOSPHOTRANSFERASE_EVIDENCE,
        )
        for drug_node in drug_nodes
    ]


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    drug_nodes = _drug_nodes(old_graph)
    common_evidence = (
        record_evidence,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        APH_PARENT_EVIDENCE,
        PHOSPHORYLATION_EVIDENCE,
        AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
    )
    catalytic_evidence = (
        record_evidence,
        APH_PARENT_EVIDENCE,
        PHOSPHORYLATION_EVIDENCE,
        GO_PHOSPHOTRANSFERASE_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → aminoglycoside phosphorylation → resistance",
        "description": (
            "Curated resistance-causation graph for APH-mediated "
            "aminoglycoside phosphorylation and inactivation."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(MECH1_NODE),
            *drug_nodes,
            copy.deepcopy(TRANSFER_NODE),
            copy.deepcopy(PHOSPHORYLATED_NODE),
            copy.deepcopy(DOMAIN_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies APH enzymes under antibiotic inactivation.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "APH antibiotic inactivation results from enzymatic aminoglycoside phosphorylation.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies APH enzymes under antibiotic phosphorylation.",
                *common_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The APH phosphorylation mechanism modifies aminoglycosides and inactivates them.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "transfer",
                "APH enzymes catalyze NTP-dependent aminoglycoside phosphorylation.",
                *catalytic_evidence,
            ),
            *_drug_input_edges(drug_nodes),
            _edge(
                "transfer",
                "causally upstream of",
                "RO:0002411",
                "phosphorylated",
                "APH-mediated phosphotransfer produces a phosphorylated aminoglycoside state.",
                *catalytic_evidence,
            ),
            _edge(
                "phosphorylated",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Phosphorylated aminoglycoside is the inactive drug state that causes resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "APH determinants confer resistance by phosphorylating aminoglycosides.",
                *common_evidence,
            ),
            *_canonical_drug_edges(record, old_graph),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The APH Pfam domain is part of the aminoglycoside phosphotransferase.",
                record_evidence,
                APH_PARENT_EVIDENCE,
                PFAM_EVIDENCE,
                PHOSPHORYLATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "APH determinants adopt the APH protein-kinase-like fold.",
                record_evidence,
                APH_PARENT_EVIDENCE,
                CATH_EVIDENCE,
                APH_STRUCTURE_EVIDENCE,
            ),
            _edge(
                "domain",
                "enables",
                "RO:0002327",
                "transfer",
                "The APH catalytic domain enables aminoglycoside phosphorylation.",
                record_evidence,
                APH_PARENT_EVIDENCE,
                PFAM_EVIDENCE,
                GO_PHOSPHOTRANSFERASE_EVIDENCE,
                PHOSPHORYLATION_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an APH target: {identifier}")
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
        help="ARO directory or one of the 56 APH YAML files",
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
