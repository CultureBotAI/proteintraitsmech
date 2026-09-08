#!/usr/bin/env python3
"""Rewrite chloramphenicol acetyltransferase ARO causal graphs.

The CAT graphs already carry the ARO antibiotic-inactivation/acylation nodes and
Pfam/CATH CAT structural nodes, but most edges reuse one legacy Shaw review
snippet and the graph omits the acetyl-CoA/chloramphenicol acyl-transfer route.
This updater adds edge-specific descriptions and routes the grounded acylation
mechanism through acetyl-CoA, the phenicol drug class, and an acetylated inactive
chloramphenicol product state.

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
    "action": "Completed chloramphenicol acetyltransferase causal graphs",
    "llm_assisted": True,
}

CAT_PARENT_ID = "ARO:3000122"

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

ACYLATION_EVIDENCE = {
    "reference": "ARO:3000106",
    "snippet": "Addition of an acyl group to an antibiotic, often via acetylation by acetylCoA.",
    "notes": "CARD definition for acylation of antibiotic conferring resistance.",
}

CAT_PARENT_EVIDENCE = {
    "reference": CAT_PARENT_ID,
    "snippet": "Inactivates chloramphenicol by addition of an acyl group.",
    "notes": "CARD definition for chloramphenicol acetyltransferases.",
}

SHAW_REVIEW_EVIDENCE = {
    "reference": "PMID:1364583",
    "snippet": (
        "CAT, which catalyses O-acetylation of the antibiotic, using acetyl-CoA "
        "as the acyl donor."
    ),
    "notes": "Shaw review of chloramphenicol acetyltransferase enzymology.",
}

KINETIC_MECHANISM_EVIDENCE = {
    "reference": "PMID:8527461",
    "snippet": (
        "Chloramphenicol acetyltransferase (CAT) catalyzes the "
        "acetyl-CoA-dependent acetylation of chloramphenicol (Cm) by a ternary "
        "complex mechanism."
    ),
    "notes": "Kinetic evidence for CAT acetyl-CoA-dependent chloramphenicol acetylation.",
}

PFAM_CAT_EVIDENCE = {
    "reference": "Pfam:PF00302",
    "snippet": "Chloramphenicol acetyltransferase",
    "notes": "Pfam family for chloramphenicol acetyltransferase domains.",
}

CATH_CAT_EVIDENCE = {
    "reference": "CATH:3.30.559",
    "snippet": "Chloramphenicol Acetyltransferase",
    "notes": "CATH fold for chloramphenicol acetyltransferases.",
}

ACETYL_COA_EVIDENCE = {
    "reference": "CHEBI:15351",
    "snippet": "acetyl-CoA",
    "notes": "Acetyl donor named by the CAT family mechanism.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MECH1_NODE = {
    "node_id": "mech1",
    "label": "acylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000106",
}

CAT_DOMAIN_NODE = {
    "node_id": "domain",
    "label": "chloramphenicol acetyltransferase domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00302",
    "description": (
        "Chloramphenicol acetyltransferase domain that catalyzes "
        "acetyl-CoA-dependent chloramphenicol acetylation."
    ),
}

CAT_FOLD_NODE = {
    "node_id": "fold",
    "label": "chloramphenicol acetyltransferase fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.30.559",
    "description": "Structural fold adopted by chloramphenicol acetyltransferases.",
}

ACETYL_COA_NODE = {
    "node_id": "acetyl_coa",
    "label": "acetyl-CoA",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15351",
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "acetylated inactive chloramphenicol",
    "node_type": "STATE",
    "description": (
        "Local state for chloramphenicol after CAT-mediated "
        "acetyl-CoA-dependent O-acetylation."
    ),
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

BASE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech1"),
}

CAT_ROUTE_EDGE_KEYS = {
    ("mech1", "RO:0002233", "acetyl_coa"),
    ("mech1", "RO:0002233", "drug0"),
    ("mech1", "RO:0002411", "modified"),
    ("modified", "RO:0002212", "drug0"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004451",
        "agrobacterium-fabrum-chloramphenicol-acetyltransferase-aro3004451.yaml",
    ),
    Target(
        "ARO:3004452",
        "alkalihalobacillus-clausii-chloramphenicol-acetyltransferase-aro3004452.yaml",
    ),
    Target("ARO:3002672", "bacillus-pumilus-cat86-aro3002672.yaml"),
    Target(
        "ARO:3004454",
        "campylobacter-coli-chloramphenicol-acetyltransferase-aro3004454.yaml",
    ),
    Target("ARO:3002670", "cat-aro3002670.yaml"),
    Target("ARO:3002683", "cata1-aro3002683.yaml"),
    Target("ARO:3004657", "cata4-aro3004657.yaml"),
    Target("ARO:3004658", "cata8-aro3004658.yaml"),
    Target("ARO:3003110", "catb10-aro3003110.yaml"),
    Target("ARO:3004660", "catb11-aro3004660.yaml"),
    Target("ARO:3002675", "catb2-aro3002675.yaml"),
    Target("ARO:3002676", "catb3-aro3002676.yaml"),
    Target("ARO:3002680", "catb8-aro3002680.yaml"),
    Target("ARO:3002681", "catb9-aro3002681.yaml"),
    Target("ARO:3002682", "catd-aro3002682.yaml"),
    Target("ARO:3002684", "catii-aro3002684.yaml"),
    Target("ARO:3004656", "catii-from-escherichia-coli-k-12-aro3004656.yaml"),
    Target("ARO:3002685", "catiii-aro3002685.yaml"),
    Target("ARO:3002686", "catp-aro3002686.yaml"),
    Target("ARO:3002687", "catq-aro3002687.yaml"),
    Target("ARO:3002688", "cats-aro3002688.yaml"),
    Target("ARO:3003983", "catu-aro3003983.yaml"),
    Target("ARO:3004357", "catv-aro3004357.yaml"),
    Target("ARO:3000122", "chloramphenicol-acetyltransferase-cat-aro3000122.yaml"),
    Target("ARO:3002674", "clostridium-butyricum-catb-aro3002674.yaml"),
    Target(
        "ARO:3004458",
        "enterococcus-faecalis-chloramphenicol-acetyltransferase-aro3004458.yaml",
    ),
    Target(
        "ARO:3004456",
        "enterococcus-faecium-chloramphenicol-acetyltransferase-aro3004456.yaml",
    ),
    Target("ARO:3002671", "limosilactobacillus-reuteri-cat-tc-aro3002671.yaml"),
    Target("ARO:3002689", "plasmid-encoded-cat-pp-cat-aro3002689.yaml"),
    Target("ARO:3002678", "pseudomonas-aeruginosa-catb6-aro3002678.yaml"),
    Target("ARO:3002679", "pseudomonas-aeruginosa-catb7-aro3002679.yaml"),
    Target(
        "ARO:3004457",
        "staphylococcus-intermedius-chloramphenicol-acetyltransferase-aro3004457.yaml",
    ),
    Target(
        "ARO:3004455",
        "streptococcus-suis-chloramphenicol-acetyltransferase-aro3004455.yaml",
    ),
    Target(
        "ARO:3004460",
        "vibrio-anguillarum-chloramphenicol-acetyltransferase-aro3004460.yaml",
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

    drug_route_edge_keys = {
        ("mech1", "RO:0002233", drug_node_id)
        for drug_node_id in drug_node_ids
    } | {
        ("modified", "RO:0002212", drug_node_id)
        for drug_node_id in drug_node_ids
    }
    allowed_edge_keys = BASE_EDGE_KEYS | {
        ("mech1", "RO:0002233", "acetyl_coa"),
        ("mech1", "RO:0002411", "modified"),
        *drug_route_edge_keys,
    }
    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        subject, predicate_id, object_ = key
        direct_drug_edge = (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        )
        if key not in allowed_edge_keys and not direct_drug_edge:
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)
        if direct_drug_edge:
            direct_drug_edges.add(object_)

    missing_edges = sorted(BASE_EDGE_KEYS - found)
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
            f"CARD asserts that CAT determinants confer resistance to {drug_node['label']}.",
            *relation_evidence[str(drug_node["node_id"])],
            _record_evidence(record),
            CAT_PARENT_EVIDENCE,
            ACYLATION_EVIDENCE,
            ANTIBIOTIC_INACTIVATION_EVIDENCE,
            SHAW_REVIEW_EVIDENCE,
        )
        for drug_node in drug_nodes
    ]


def _cat_route_edges(drug_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _edge(
            "mech1",
            "has input",
            "RO:0002233",
            "acetyl_coa",
            "CAT-mediated O-acetylation uses acetyl-CoA as the acyl donor.",
            CAT_PARENT_EVIDENCE,
            SHAW_REVIEW_EVIDENCE,
            KINETIC_MECHANISM_EVIDENCE,
            ACYLATION_EVIDENCE,
            ACETYL_COA_EVIDENCE,
        ),
        *[
            _edge(
                "mech1",
                "has input",
                "RO:0002233",
                str(drug_node["node_id"]),
                "CAT-mediated O-acetylation modifies chloramphenicol phenicol antibiotics.",
                CAT_PARENT_EVIDENCE,
                SHAW_REVIEW_EVIDENCE,
                KINETIC_MECHANISM_EVIDENCE,
                ACYLATION_EVIDENCE,
            )
            for drug_node in drug_nodes
        ],
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "modified",
            "CAT-mediated O-acetylation produces acetylated chloramphenicol.",
            CAT_PARENT_EVIDENCE,
            SHAW_REVIEW_EVIDENCE,
            KINETIC_MECHANISM_EVIDENCE,
            ACYLATION_EVIDENCE,
        ),
        *[
            _edge(
                "modified",
                "negatively regulates",
                "RO:0002212",
                str(drug_node["node_id"]),
                (
                    "The acetylated chloramphenicol state represents enzymatic "
                    "inactivation of the drug."
                ),
                CAT_PARENT_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
                SHAW_REVIEW_EVIDENCE,
                KINETIC_MECHANISM_EVIDENCE,
            )
            for drug_node in drug_nodes
        ],
    ]


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    drug_nodes = _drug_nodes(old_graph)
    common_evidence = (
        record_evidence,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        CAT_PARENT_EVIDENCE,
        SHAW_REVIEW_EVIDENCE,
        KINETIC_MECHANISM_EVIDENCE,
    )
    acylation_evidence = (
        record_evidence,
        CAT_PARENT_EVIDENCE,
        ACYLATION_EVIDENCE,
        SHAW_REVIEW_EVIDENCE,
        KINETIC_MECHANISM_EVIDENCE,
    )
    catalytic_evidence = (
        record_evidence,
        CAT_PARENT_EVIDENCE,
        PFAM_CAT_EVIDENCE,
        SHAW_REVIEW_EVIDENCE,
        KINETIC_MECHANISM_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → chloramphenicol O-acetylation → resistance",
        "description": (
            "Curated resistance-causation graph for chloramphenicol "
            "acetyltransferase antibiotic inactivation. The determinant "
            "participates in broad antibiotic inactivation and in the narrower "
            "acetyl-CoA-dependent O-acetylation of chloramphenicol."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(MECH1_NODE),
            *drug_nodes,
            copy.deepcopy(CAT_DOMAIN_NODE),
            copy.deepcopy(CAT_FOLD_NODE),
            copy.deepcopy(ACETYL_COA_NODE),
            copy.deepcopy(MODIFIED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies CAT determinants under antibiotic inactivation.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "CAT-mediated antibiotic inactivation acetylates chloramphenicol.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies CAT determinants under antibiotic acylation.",
                *acylation_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "O-acetylation inactivates chloramphenicol and thereby causes resistance.",
                *acylation_evidence,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "CAT determinants confer resistance by acetylating chloramphenicol.",
                *common_evidence,
                ACYLATION_EVIDENCE,
            ),
            *_canonical_drug_edges(record, old_graph),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The CAT Pfam domain is part of the chloramphenicol acetyltransferase.",
                *catalytic_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "CAT determinants adopt the chloramphenicol acetyltransferase fold.",
                record_evidence,
                CAT_PARENT_EVIDENCE,
                CATH_CAT_EVIDENCE,
                SHAW_REVIEW_EVIDENCE,
            ),
            _edge(
                "domain",
                "enables (chloramphenicol acetylation)",
                "RO:0002327",
                "mech1",
                (
                    "The CAT domain enables acetyl-CoA-dependent O-acetylation "
                    "of chloramphenicol."
                ),
                *catalytic_evidence,
                ACYLATION_EVIDENCE,
            ),
            *_cat_route_edges(drug_nodes),
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
        raise ValueError(f"{path}: not a chloramphenicol acetyltransferase target: {identifier}")
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
        help="ARO directory or one of the 34 chloramphenicol acetyltransferase YAML files",
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
