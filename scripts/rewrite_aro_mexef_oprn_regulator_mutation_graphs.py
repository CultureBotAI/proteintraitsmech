#!/usr/bin/env python3
"""Rewrite MexEF-OprN regulator-mutation ARO graphs.

These records describe MexEF-OprN efflux caused by regulator mutations rather
than the pump alone. The curated graphs retain the inherited MexEF-OprN
drug-class edge and route each composite determinant through the named MexT,
MexS, or MvaT regulatory path that raises MexEF-OprN efflux.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
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

HISTORY_ACTION = "Completed MexEF-OprN regulator-mutation graphs"
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

REGULATORY_EFFLUX_EVIDENCE = {
    "reference": "ARO:3000451",
    "snippet": (
        "This resistance mechanism occurs as a result of modulating the expression "
        "of proteins involved in antibiotic efflux."
    ),
    "notes": "CARD definition for proteins modulating antibiotic efflux.",
}

MEXS_EVIDENCE = {
    "reference": "ARO:3000813",
    "snippet": (
        "MexS is a suppressor of MexT, which is an activator of the multidrug pump "
        "MexEF-OprN. Mutations in MexS lead to multidrug resistance."
    ),
    "notes": "CARD definition for the MexS suppressor determinant.",
}

MEXT_EVIDENCE = {
    "reference": "ARO:3000814",
    "snippet": (
        "MexT is a LysR-type transcriptional activator that positively regulates "
        "the expression of MexEF-OprN, OprD, and MexS."
    ),
    "notes": "CARD definition for the MexT activator.",
}

MVAT_EVIDENCE = {
    "reference": "ARO:3004069",
    "snippet": (
        "MvaT, a global regulator of virulence genes in P. aeruginosa, has also "
        "shown to be able to repress the expression of the MexEF-OprN pump."
    ),
    "notes": "CARD definition for the MvaT repressor determinant.",
}

MEXEF_OPRN_EVIDENCE = {
    "reference": "ARO:3000798",
    "snippet": (
        "MexEF-OprN is a multidrug efflux protein expressed in the Gram-negative "
        "Pseudomonas aeruginosa. MexE is the membrane fusion protein; MexF is "
        "the inner membrane transporter; and OprN is the outer membrane "
        "channel. MexEF-OprN is associated with resistance to fluoroquinolones, "
        "chloramphenicol, and trimethoprim."
    ),
    "notes": "CARD definition for the MexEF-OprN pump.",
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent "
        "of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for transcriptional activation.",
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or "
        "extent of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for transcriptional repression.",
}

GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE = {
    "reference": "GO:0044092",
    "snippet": "Any process that stops, prevents, or reduces the activity of a molecular function.",
    "notes": "GO definition for negative regulation of molecular function.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "MexEF-OprN",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000798",
    "description": "Grounded to CARD's MexEF-OprN RND efflux pump.",
}

ACTIVATOR_NODE = {
    "node_id": "activator",
    "label": "MexT",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000814",
    "description": "Grounded to CARD's MexT activator of MexEF-OprN expression.",
}

SUPPRESSOR_NODE = {
    "node_id": "suppressor",
    "label": "MexS",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000813",
    "description": "Grounded to CARD's MexS suppressor of MexT.",
}

REPRESSOR_NODE = {
    "node_id": "repressor",
    "label": "MvaT",
    "node_type": "PROTEIN",
    "grounding": "ARO:3004069",
    "description": "Grounded to CARD's MvaT repressor of MexEF-OprN expression.",
}

ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of MexEF-OprN expression",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": "Broad transcriptional activation process for MexEF-OprN expression.",
}

REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of MexEF-OprN expression",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": "Broad transcriptional repression process for MexEF-OprN expression.",
}

SUPPRESSION_NODE = {
    "node_id": "suppression",
    "label": "negative regulation of MexT molecular function",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0044092",
    "description": "Broad process for MexS-mediated suppression of MexT.",
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


class GraphKind(Enum):
    MEXS_LOSS = "MEXS_LOSS"
    MEXT_ACTIVATION = "MEXT_ACTIVATION"
    MVAT_LOSS = "MVAT_LOSS"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: GraphKind


_TARGET_ROWS = """
ARO:3004068 MEXS_LOSS mexef-oprn-with-mexs-mutations-conferring-resistance-to-chloramphenicol-ciproflo-aro3004068.yaml
ARO:3004066 MEXT_ACTIVATION mexef-oprn-with-mext-mutation-conferring-resistance-to-chloramphenicol-ciproflox-aro3004066.yaml
ARO:3004070 MVAT_LOSS mexef-oprn-with-mvat-deletion-conferring-resistance-to-chloramphenicol-and-norfl-aro3004070.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename, GraphKind(kind))
    for identifier, kind, filename in (
        line.split() for line in _TARGET_ROWS.strip().splitlines()
    )
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

EXPECTED_NODES = {
    GraphKind.MEXS_LOSS: {
        "determinant",
        "mech0",
        "suppressor",
        "activator",
        "suppression",
        "activation",
        "pump",
        "resistance",
    },
    GraphKind.MEXT_ACTIVATION: {
        "determinant",
        "mech0",
        "activator",
        "activation",
        "pump",
        "resistance",
    },
    GraphKind.MVAT_LOSS: {
        "determinant",
        "mech0",
        "repressor",
        "repression",
        "pump",
        "resistance",
    },
}

COMMON_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("activation", "RO:0002213", "pump"),
    ("pump", "RO:0002327", "mech0"),
}

KIND_EDGE_KEYS = {
    GraphKind.MEXS_LOSS: COMMON_EDGE_KEYS
    | {
        ("determinant", "RO:0002212", "suppression"),
        ("suppressor", "RO:0002327", "suppression"),
        ("suppression", "RO:0002212", "activator"),
        ("activator", "RO:0002327", "activation"),
    },
    GraphKind.MEXT_ACTIVATION: COMMON_EDGE_KEYS
    | {
        ("determinant", "RO:0002411", "activation"),
        ("activator", "RO:0002327", "activation"),
    },
    GraphKind.MVAT_LOSS: {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0002212", "repression"),
        ("repressor", "RO:0002327", "repression"),
        ("repression", "RO:0002212", "pump"),
        ("pump", "RO:0002327", "mech0"),
    },
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


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in evidence:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        unique.append(copy.deepcopy(item))
    return unique


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
        "evidence": _unique_evidence(evidence),
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
    )


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        copy.deepcopy(node)
        for node in _dicts(graph.get("nodes"))
        if str(node.get("node_id", "")).startswith("drug")
    ]


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


def _drug_edges(record: dict[str, Any], old_graph: dict[str, Any]) -> list[dict[str, Any]]:
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
            MEXEF_OPRN_EVIDENCE,
        )
        for drug_node in drug_nodes
    ]


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "TRAIT",
        "grounding": str(record["identifier"]),
        "description": "Grounded composite CARD determinant for a MexEF-OprN regulatory variant.",
    }


def _common_edges(
    record: dict[str, Any],
    evidence: tuple[dict[str, str], ...],
) -> list[dict[str, Any]]:
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies this composite determinant under antibiotic efflux.",
            *evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "MexEF-OprN antibiotic efflux causes the modeled resistance phenotype.",
            *evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The regulatory variant increases MexEF-OprN efflux and thereby "
            "confers antibiotic resistance.",
            *evidence,
        ),
        _edge(
            "pump",
            "enables (drug efflux)",
            "RO:0002327",
            "mech0",
            "MexEF-OprN is the multidrug pump that supplies antibiotic efflux.",
            _record_evidence(record),
            MEXEF_OPRN_EVIDENCE,
            ANTIBIOTIC_EFFLUX_EVIDENCE,
        ),
    ]


def _mexs_nodes() -> list[dict[str, Any]]:
    return [
        copy.deepcopy(SUPPRESSOR_NODE),
        copy.deepcopy(ACTIVATOR_NODE),
        copy.deepcopy(SUPPRESSION_NODE),
        copy.deepcopy(ACTIVATION_NODE),
    ]


def _mexs_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = (
        _record_evidence(record),
        MEXS_EVIDENCE,
        MEXT_EVIDENCE,
        MEXEF_OPRN_EVIDENCE,
        REGULATORY_EFFLUX_EVIDENCE,
        *_source_evidence(record),
    )
    return [
        *_common_edges(record, evidence),
        _edge(
            "determinant",
            "negatively regulates (loss relieves MexT suppression)",
            "RO:0002212",
            "suppression",
            "Resistance-associated MexS mutations are represented as loss of "
            "normal MexT suppression.",
            _record_evidence(record),
            MEXS_EVIDENCE,
            GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE,
        ),
        _edge(
            "suppressor",
            "enables (suppresses MexT)",
            "RO:0002327",
            "suppression",
            "MexS enables the normal suppression of the MexT activator.",
            MEXS_EVIDENCE,
            GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE,
        ),
        _edge(
            "suppression",
            "negatively regulates (suppresses MexT)",
            "RO:0002212",
            "activator",
            "Normal MexS-mediated suppression inhibits MexT activity.",
            _record_evidence(record),
            MEXS_EVIDENCE,
            MEXT_EVIDENCE,
            GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE,
        ),
        _edge(
            "activator",
            "enables (activates MexEF-OprN expression)",
            "RO:0002327",
            "activation",
            "MexT participates in positive regulation of MexEF-OprN expression.",
            MEXT_EVIDENCE,
            GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
        ),
        _edge(
            "activation",
            "positively regulates (raises MexEF-OprN expression)",
            "RO:0002213",
            "pump",
            "MexT-mediated transcriptional activation raises MexEF-OprN expression.",
            _record_evidence(record),
            MEXT_EVIDENCE,
            GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
            MEXEF_OPRN_EVIDENCE,
        ),
    ]


def _mext_nodes() -> list[dict[str, Any]]:
    return [
        copy.deepcopy(ACTIVATOR_NODE),
        copy.deepcopy(ACTIVATION_NODE),
    ]


def _mext_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = (
        _record_evidence(record),
        MEXT_EVIDENCE,
        MEXEF_OPRN_EVIDENCE,
        REGULATORY_EFFLUX_EVIDENCE,
        *_source_evidence(record),
    )
    return [
        *_common_edges(record, evidence),
        _edge(
            "determinant",
            "causally upstream of (activates MexEF-OprN expression)",
            "RO:0002411",
            "activation",
            "The MexT mutation is modeled as raising MexEF-OprN expression.",
            _record_evidence(record),
            MEXT_EVIDENCE,
            GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
        ),
        _edge(
            "activator",
            "enables (activates MexEF-OprN expression)",
            "RO:0002327",
            "activation",
            "MexT participates in positive regulation of MexEF-OprN expression.",
            MEXT_EVIDENCE,
            GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
        ),
        _edge(
            "activation",
            "positively regulates (raises MexEF-OprN expression)",
            "RO:0002213",
            "pump",
            "Transcriptional activation raises MexEF-OprN expression.",
            _record_evidence(record),
            MEXT_EVIDENCE,
            GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
            MEXEF_OPRN_EVIDENCE,
        ),
    ]


def _mvat_nodes() -> list[dict[str, Any]]:
    return [
        copy.deepcopy(REPRESSOR_NODE),
        copy.deepcopy(REPRESSION_NODE),
    ]


def _mvat_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = (
        _record_evidence(record),
        MVAT_EVIDENCE,
        MEXEF_OPRN_EVIDENCE,
        REGULATORY_EFFLUX_EVIDENCE,
        *_source_evidence(record),
    )
    return [
        *_common_edges(record, evidence),
        _edge(
            "determinant",
            "negatively regulates (deletion relieves repression)",
            "RO:0002212",
            "repression",
            "The MvaT deletion is modeled as loss of normal MexEF-OprN repression.",
            _record_evidence(record),
            MVAT_EVIDENCE,
            GO_NEGATIVE_TRANSCRIPTION_EVIDENCE,
        ),
        _edge(
            "repressor",
            "enables (represses MexEF-OprN expression)",
            "RO:0002327",
            "repression",
            "MvaT participates in repression of MexEF-OprN expression.",
            MVAT_EVIDENCE,
            GO_NEGATIVE_TRANSCRIPTION_EVIDENCE,
        ),
        _edge(
            "repression",
            "negatively regulates (holds MexEF-OprN down)",
            "RO:0002212",
            "pump",
            "Normal MvaT-dependent transcriptional repression keeps MexEF-OprN "
            "expression low.",
            _record_evidence(record),
            MVAT_EVIDENCE,
            GO_NEGATIVE_TRANSCRIPTION_EVIDENCE,
            MEXEF_OPRN_EVIDENCE,
        ),
    ]


def _nodes(record: dict[str, Any], old_graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    kind_nodes = {
        GraphKind.MEXS_LOSS: _mexs_nodes,
        GraphKind.MEXT_ACTIVATION: _mext_nodes,
        GraphKind.MVAT_LOSS: _mvat_nodes,
    }[target.kind]()
    return [
        _determinant_node(record),
        copy.deepcopy(MECHANISM_NODE),
        *_drug_nodes(old_graph),
        copy.deepcopy(PUMP_NODE),
        *kind_nodes,
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _edges(record: dict[str, Any], old_graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    kind_edges = {
        GraphKind.MEXS_LOSS: _mexs_edges,
        GraphKind.MEXT_ACTIVATION: _mext_edges,
        GraphKind.MVAT_LOSS: _mvat_edges,
    }[target.kind](record)
    return [
        *kind_edges,
        *_drug_edges(record, old_graph),
    ]


def _graph(record: dict[str, Any], old_graph: dict[str, Any], target: Target) -> dict[str, Any]:
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → regulated MexEF-OprN efflux → resistance",
        "description": (
            "Curated resistance-causation graph for a MexEF-OprN regulatory "
            "variant. The graph grounds the named MexEF-OprN pump and routes "
            "the determinant through the specific regulatory branch that "
            "increases efflux."
        ),
        "nodes": _nodes(record, old_graph, target),
        "edges": _edges(record, old_graph, target),
    }


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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }
    expected_nodes = EXPECTED_NODES[target.kind]
    missing_nodes = sorted(expected_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    drug_node_ids = {node_id for node_id in nodes if node_id.startswith("drug")}
    expected_edge_keys = KIND_EDGE_KEYS[target.kind] | {
        ("determinant", "ARO:2000001", drug_node_id)
        for drug_node_id in drug_node_ids
    }

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in expected_edge_keys:
            subject, _, object_ = key
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            subject, _, object_ = key
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(expected_edge_keys - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"][0])
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0], target)]
    _validate_graph(out["causal_graphs"][0], target)
    return out, out["causal_graphs"][0] != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a MexEF-OprN regulator-mutation target: {identifier}")
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
        help="ARO directory or one of the MexEF-OprN regulator-mutation YAML files",
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
