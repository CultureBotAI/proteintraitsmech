#!/usr/bin/env python3
"""Ground and describe Ara4N lipid-A modification graphs.

The four Ara4N branch records share the same curated topology: arn/pmr
determinants participate in beta-L-Ara4N-lipid A biosynthesis, which modifies
lipid A and reduces the net negative surface charge used by cationic peptide
antibiotics for binding. The existing graphs leave the pathway and lipid-A
nodes ungrounded and only partly describe the edges.

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
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Grounded Ara4N lipid-A modification graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall "
        "of gram negative bacteria is a mechanism of resistance for cationic "
        "antimicrobials that depend on the negative charge for binding to the "
        "surface."
    ),
    "notes": "CARD definition for the shared charge-alteration resistance mechanism.",
}

PMRF_EVIDENCE = {
    "reference": "ARO:3003578",
    "snippet": (
        "PmrF is required for the synthesis and transfer of "
        "4-amino-4-deoxy-L-arabinose (Ara4N) to Lipid A, which allows "
        "gram-negative bacteria to resist the antimicrobial activity of "
        "cationic antimicrobial peptides and antibiotics such as polymyxin."
    ),
    "notes": "CARD definition connecting the Ara4N route to polymyxin resistance.",
}

ARNA_EVIDENCE = {
    "reference": "ARO:3002985",
    "snippet": (
        "arnA modifies lipid A with 4-amino-4-deoxy-L-arabinose (Ara4N) which "
        "allows gram-negative bacteria to resist the antimicrobial activity of "
        "cationic antimicrobial peptides and antibiotics such as polymyxin."
    ),
    "notes": "CARD definition connecting arnA to lipid-A Ara4N modification.",
}

ARA4N_GO_EVIDENCE = {
    "reference": "GO:1901760",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "beta-L-Ara4N-lipid A which occurs as a result of modification of the "
        "lipid A moiety of lipopolysaccharide by the addition of the sugar "
        "4-amino-4-deoxy-L-arabinose (L-Ara4N)."
    ),
    "notes": "GO definition for beta-L-Ara4N-lipid A biosynthetic process.",
}

CHEBI_LIPID_A_EVIDENCE = {
    "reference": "CHEBI:47040",
    "snippet": "The glycolipid moiety of bacterial lipopolysaccharide.",
    "notes": "ChEBI definition for lipid A.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "charge alteration conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003588",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

ARA4N_PATHWAY_NODE = {
    "node_id": "ara4n_pathway",
    "label": "beta-L-Ara4N-lipid A biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1901760",
    "description": (
        "Grounded to the GO biological-process term for lipid A modification by "
        "addition of 4-amino-4-deoxy-L-arabinose."
    ),
}

LIPID_A_NODE = {
    "node_id": "lipid_a",
    "label": "lipid A",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:47040",
    "description": (
        "Grounded to the ChEBI class for the glycolipid moiety of bacterial "
        "lipopolysaccharide that receives Ara4N modification."
    ),
}

CHARGE_NODE = {
    "node_id": "charge",
    "label": "reduced net negative surface charge",
    "node_type": "STATE",
    "description": (
        "Local state representing the reduced negative surface charge produced "
        "by Ara4N modification of lipid A."
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0000056", "ara4n_pathway"),
    ("ara4n_pathway", "RO:0002411", "lipid_a"),
    ("lipid_a", "RO:0002411", "charge"),
    ("charge", "RO:0002212", "drug0"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    "ARO:3002985": Target(
        identifier="ARO:3002985",
        filename="arna-aro3002985.yaml",
    ),
    "ARO:3005053": Target(
        identifier="ARO:3005053",
        filename="arnt-aro3005053.yaml",
    ),
    "ARO:3003578": Target(
        identifier="ARO:3003578",
        filename="pmrf-aro3003578.yaml",
    ),
    "ARO:3003577": Target(
        identifier="ARO:3003577",
        filename="ugd-aro3003577.yaml",
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
    )


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": description,
            "evidence": _unique_evidence(evidence),
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {
            "determinant",
            "mech0",
            "drug0",
            "ara4n_pathway",
            "lipid_a",
            "charge",
            "resistance",
        }
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in CORE_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(ARA4N_PATHWAY_NODE),
        copy.deepcopy(LIPID_A_NODE),
        copy.deepcopy(CHARGE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _branch_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    evidence = [_target_evidence(record)]
    if record["identifier"] != "ARO:3003578":
        evidence.append(PMRF_EVIDENCE)
    if record["identifier"] != "ARO:3002985":
        evidence.append(ARNA_EVIDENCE)
    return tuple(evidence)


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)
    branch_evidence = _branch_evidence(record)
    route_evidence = (*branch_evidence, ARA4N_GO_EVIDENCE, *source_evidence)
    charge_evidence = (
        *branch_evidence,
        ARA4N_GO_EVIDENCE,
        CHEBI_LIPID_A_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
        *source_evidence,
    )
    resistance_evidence = (
        target_evidence,
        CHARGE_ALTERATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        {
            "reference": "ARO:3004269",
            "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
            "notes": (
                "Asserted on ARO:3004269 and inherited by this Ara4N branch "
                f"record {record['identifier']}."
            ),
        },
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies this Ara4N determinant under charge alteration.",
            resistance_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "Charge alteration is the broad mechanism by which Ara4N lipid-A "
                "modification confers peptide-antibiotic resistance."
            ),
            charge_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "This Ara4N branch determinant is modeled as conferring "
                "resistance through lipid-A modification and charge alteration."
            ),
            (*branch_evidence, CHARGE_ALTERATION_EVIDENCE, *source_evidence),
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            (
                "CARD asserts peptide-antibiotic resistance on the parent "
                "class inherited by this Ara4N branch record."
            ),
            drug_evidence,
        ),
        _edge(
            "determinant",
            "participates in (Ara4N synthesis and transfer)",
            "RO:0000056",
            "ara4n_pathway",
            (
                "These determinants participate in the Ara4N lipid-A "
                "biosynthesis route, which spans Ara4N synthesis and transfer."
            ),
            route_evidence,
        ),
        _edge(
            "ara4n_pathway",
            "causally upstream of (modifies lipid A)",
            "RO:0002411",
            "lipid_a",
            (
                "The beta-L-Ara4N-lipid A biosynthetic process modifies lipid A "
                "by adding 4-amino-4-deoxy-L-arabinose."
            ),
            (ARA4N_GO_EVIDENCE, CHEBI_LIPID_A_EVIDENCE, *branch_evidence, *source_evidence),
        ),
        _edge(
            "lipid_a",
            "causally upstream of (reduces surface negative charge)",
            "RO:0002411",
            "charge",
            (
                "Ara4N-modified lipid A lowers the net negative cell-envelope "
                "charge modeled by the shared charge-alteration mechanism."
            ),
            charge_evidence,
        ),
        _edge(
            "charge",
            "negatively regulates (impedes drug binding)",
            "RO:0002212",
            "drug0",
            (
                "Reduced negative surface charge impedes binding by cationic "
                "peptide antibiotics such as polymyxin."
            ),
            (
                CHARGE_ALTERATION_EVIDENCE,
                *branch_evidence,
                *source_evidence,
            ),
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["title"] = f"{record['label']} → beta-L-Ara4N-lipid A → reduced charge"
    graph["description"] = (
        "Conservative Ara4N lipid-A modification graph. The determinant "
        "participates in beta-L-Ara4N-lipid A biosynthesis, which modifies "
        "lipid A and reduces the net negative surface charge required by "
        "cationic peptide antibiotics for binding."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an Ara4N target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

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
    return out, True


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one exact Ara4N target YAML file",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            out, did_change = enrich_text(text, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
