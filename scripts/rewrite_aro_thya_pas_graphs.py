#!/usr/bin/env python3
"""Ground and evidence thyA/PAS resistance graphs.

The aminosalicylate-resistant thymidylate synthase graphs already have the
right loss-of-function topology. This updater grounds thymidylate synthase
activity to GO:0004799, retains the disrupted-binding/catalysis node as a
described local state, and attaches descriptions plus multi-reference evidence
to every edge.

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
HISTORY_ACTION = "Grounded thyA/PAS loss-of-function graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004152"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Antibiotic resistant form of thymidylate synthase (synthetase), an "
        "enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide "
        "biosynthesis. Loss-of-function mutations in thymidylate synthase "
        "confer resistance to p-aminosalicylic acid by disrupting the "
        "substrate-binding affinity and catalytic activity."
    ),
    "notes": "CARD definition for the aminosalicylate-resistant thymidylate synthase parent.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

THYMIDYLATE_SYNTHASE_EVIDENCE = {
    "reference": "GO:0004799",
    "snippet": (
        "Catalysis of the reaction: 5,10-methylenetetrahydrofolate + dUMP = "
        "7,8-dihydrofolate + thymidylate."
    ),
    "notes": "GO definition for thymidylate synthase activity.",
}

SALICYLIC_ACID_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3007159",
    "snippet": "salicylic acid antibiotic",
    "notes": "ARO drug-class term inherited by PAS-resistant thyA records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "salicylic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007159",
}

TS_ACTIVITY_NODE = {
    "node_id": "ts_activity",
    "label": "thymidylate synthase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004799",
}

DEFECT_NODE = {
    "node_id": "defect",
    "label": "disrupted substrate binding and catalysis",
    "node_type": "STATE",
    "description": (
        "Local state for loss of thymidylate synthase substrate-binding "
        "affinity and catalytic activity."
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

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002327", "ts_activity"),
    ("determinant", "RO:0000086", "defect"),
    ("defect", "RO:0002212", "ts_activity"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies these thyA records under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Loss-of-function point mutations in thyA are a "
        "mutation-mediated resistance mechanism."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Loss-of-function thymidylate synthase mutations confer PAS "
        "resistance by disrupting substrate binding and catalysis."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps aminosalicylate-resistant thymidylate synthase to salicylic "
        "acid antibiotics."
    ),
    ("determinant", "RO:0002327", "ts_activity"): (
        "The determinant normally enables thymidylate synthase activity."
    ),
    ("determinant", "RO:0000086", "defect"): (
        "The resistance-conferring loss-of-function mutation gives the "
        "thymidylate synthase altered substrate-binding affinity and "
        "catalytic activity."
    ),
    ("defect", "RO:0002212", "ts_activity"): (
        "The substrate-binding and catalytic defect inhibits thymidylate "
        "synthase activity."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="aminosalicylate-resistant-thymidylate-synthase-aro3004152.yaml",
    ),
    "ARO:3004153": Target(
        identifier="ARO:3004153",
        filename=(
            "mycobacterium-tuberculosis-thya-with-mutation-conferring-"
            "resistance-to-para-amin-aro3004153.yaml"
        ),
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = (
            "ARO drug-class relationship asserted directly on the "
            "aminosalicylate-resistant thymidylate synthase parent."
        )
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3004152 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3007159 ! "
            "salicylic acid antibiotic"
        ),
        "notes": notes,
    }


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


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "drug0", "ts_activity", "defect", "resistance"}
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)

    mutation_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    thymidylate_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        THYMIDYLATE_SYNTHASE_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        _drug_relation_evidence(target),
        SALICYLIC_ACID_ANTIBIOTIC_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → loss of thymidylate synthase activity → resistance",
        "description": (
            "Conservative graph for PAS resistance caused by thymidylate "
            "synthase loss of function. The graph grounds thymidylate "
            "synthase activity to GO:0004799 and keeps the disrupted "
            "substrate-binding and catalytic activity defect as a described "
            "local state."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(TS_ACTIVITY_NODE),
            copy.deepcopy(DEFECT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "ts_activity",
                thymidylate_evidence,
            ),
            _edge(
                "determinant",
                "has quality",
                "RO:0000086",
                "defect",
                mutation_evidence,
            ),
            _edge(
                "defect",
                "negatively regulates",
                "RO:0002212",
                "ts_activity",
                thymidylate_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an aminosalicylate-resistant thyA target: {identifier}")
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
        help="ARO directory or one exact aminosalicylate-resistant thyA YAML file",
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
