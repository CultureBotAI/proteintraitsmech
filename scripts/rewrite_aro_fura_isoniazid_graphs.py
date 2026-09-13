#!/usr/bin/env python3
"""Rewrite FurA isoniazid-resistance causal graphs.

The reviewed FurA score-78 records retain an older promoter-regulation graph.
This rewrite keeps the curated regulatory branch -- FurA binding represses
katG transcription -- but grounds katG transcription to a broad GO term and
adds explicit multi-reference evidence to every edge.

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
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed FurA isoniazid regulatory causal graphs",
    "llm_assisted": True,
}

FURA_PARENT_EVIDENCE = {
    "reference": "ARO:3004896",
    "snippet": (
        "Mutations that occur in furA which is in the regulatory region of katG. "
        "Mutations within the gene contribute to antibiotic resistance."
    ),
    "notes": "CARD definition for the antibiotic resistant furA parent term.",
}

FURA_ISONIAZID_EVIDENCE = {
    "reference": "ARO:3004897",
    "snippet": (
        "Transcriptional regulator furA, represses the transcription of the "
        "catalase-peroxidase gene katG and its own transcription by binding "
        "to the promoter region."
    ),
    "notes": "CARD definition for the isoniazid resistant furA term.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0006351",
    "snippet": "DNA-templated transcription",
    "notes": "GO grounding for the katG transcription process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

KATG_TRANSCRIPTION_NODE = {
    "node_id": "katg_transcription",
    "label": "transcription of the catalase-peroxidase gene katG",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006351",
    "description": (
        "Grounded to the broad GO DNA-templated transcription term because no "
        "stable term is available for transcription of the specific katG locus."
    ),
}

PROMOTER_BINDING_NODE = {
    "node_id": "promoter_binding",
    "label": "transcription cis-regulatory region binding",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0000976",
    "description": (
        "Grounded to the broad GO cis-regulatory-region binding term because no "
        "stable term is available for FurA binding to the katG promoter."
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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004897",
        "isoniazid-resistant-fura-aro3004897.yaml",
    ),
    Target(
        "ARO:3004923",
        "mycobacterium-tuberculosis-fura-mutations-confer-resistance-to-isoniazid-"
        "aro3004923.yaml",
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


def _drug_node(graph: dict[str, Any], target: Target) -> dict[str, Any]:
    drug_nodes = [
        node
        for node in _dicts(graph.get("nodes"))
        if str(node.get("node_id", "")).startswith("drug")
    ]
    if len(drug_nodes) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one drug node")
    return copy.deepcopy(drug_nodes[0])


def _drug_relation_evidence(
    graph: dict[str, Any],
    drug_node: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
            and edge.get("object") == drug_node["node_id"]
        ):
            evidence.extend(
                item
                for item in _dicts(edge.get("evidence"))
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class "
                )
            )

    if not evidence:
        raise ValueError(f"missing direct drug-class evidence for {drug_node['node_id']}")
    return evidence


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    drug_node = _drug_node(old_graph, TARGET_BY_ID[str(record["identifier"])])
    relation_evidence = _drug_relation_evidence(old_graph, drug_node)
    mutation_evidence = (
        record_evidence,
        FURA_PARENT_EVIDENCE,
        FURA_ISONIAZID_EVIDENCE,
        MUTATION_EVIDENCE,
    )
    repression_evidence = (
        FURA_ISONIAZID_EVIDENCE,
        FURA_PARENT_EVIDENCE,
        TRANSCRIPTION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → FurA katG transcriptional repression",
        "description": (
            "Curated resistance-causation graph for FurA mutations linked to "
            "isoniazid resistance, preserving CARD's FurA katG transcriptional "
            "repression mechanism."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            drug_node,
            copy.deepcopy(PROMOTER_BINDING_NODE),
            copy.deepcopy(KATG_TRANSCRIPTION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies FurA variants under mutation conferring "
                "antibiotic resistance.",
                *mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism captures furA sequence "
                "changes that contribute to antibiotic resistance.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "CARD links furA mutations to antibiotic resistance and links "
                "this branch to isoniazid-like antibiotics.",
                *mutation_evidence,
                *relation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                str(drug_node["node_id"]),
                (
                    "CARD asserts that this FurA mutation class confers "
                    f"resistance to {drug_node['label']}."
                ),
                *relation_evidence,
                record_evidence,
                FURA_PARENT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (katG promoter binding)",
                "RO:0000056",
                "promoter_binding",
                "FurA represses katG transcription by binding the katG promoter region.",
                FURA_ISONIAZID_EVIDENCE,
                FURA_PARENT_EVIDENCE,
            ),
            _edge(
                "promoter_binding",
                "negatively regulates",
                "RO:0002212",
                "katg_transcription",
                "The promoter-bound FurA regulator represses katG transcription.",
                *repression_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, graphs[0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a FurA isoniazid target: {identifier}")
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
        help="ARO directory or one of the FurA isoniazid YAML files",
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
