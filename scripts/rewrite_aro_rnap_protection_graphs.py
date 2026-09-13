#!/usr/bin/env python3
"""Ground and correct RNA-polymerase target-protection graphs.

The HelR and RbpA RNA-polymerase target-protection records carried an
ungrounded local RNAP protein node and, for RbpA, stale HelR-specific
rifamycin-displacement evidence. This updater removes the ungrounded side
node, keeps rifamycin-mediated RNAP inhibition as a described local state, and
adds branch-specific CARD evidence and edge descriptions throughout.

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

HISTORY_ACTION = "Grounded RNA polymerase target-protection causal graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

HEL_PARENT = "ARO:3007207"
HELR = "ARO:3007208"
RBPA_PARENT = "ARO:3004243"
RBPA = "ARO:3000245"

HEL_PARENT_DEFINITION = (
    "Helicase-like proteins that confer resistance to antibiotics such as rifamycins "
    "by preventing or disrupting their binding to RNA polymerase."
)
HELR_DEFINITION = (
    "HelR is a helicase-like protein that confers resistance to rifamycins by "
    "displacing them from the RNA polymerase complex. The protein forces the "
    "antibiotic away from the polymerase by binding in its place. It then ejects "
    "itself from the complex, allowing the polymerase to resume normal function."
)
RBPA_PARENT_DEFINITION = (
    "RbpA is a family of bacterial RNA polymerase-binding proteins, which acts as a "
    "transcription factor and binds to the sigma subunit of RNA polymerase."
)
RBPA_DEFINITION = "RNA-polymerase binding protein which confers resistance to rifampin."

PARENT_EVIDENCE = {
    HEL_PARENT: {
        "reference": HEL_PARENT,
        "snippet": HEL_PARENT_DEFINITION,
        "notes": (
            "CARD definition for helicase-like RNA polymerase protection proteins."
        ),
    },
    RBPA_PARENT: {
        "reference": RBPA_PARENT,
        "snippet": RBPA_PARENT_DEFINITION,
        "notes": "CARD definition for the RbpA RNA polymerase-binding protein family.",
    },
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, which "
        "process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target protection.",
}

RIFAMYCIN_EVIDENCE = {
    "reference": "ARO:3000157",
    "snippet": "rifamycin antibiotic",
    "notes": "ARO drug class inherited by the RNA-polymerase target-protection records.",
}

HEL_DISPLACEMENT_EVIDENCE = {
    "reference": "PMID:35907401",
    "snippet": (
        "HelR protects RNA polymerase by displacing bound rifamycins and allowing "
        "inhibited transcription to resume."
    ),
    "notes": "Surette et al. 2022; HelR-specific rifamycin displacement evidence.",
}

DRUG_RELATION_SNIPPET = (
    "relationship: confers_resistance_to_drug_class ARO:3000157 ! "
    "rifamycin antibiotic"
)

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target protection",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001003",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "rifamycin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000157",
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
    ("drug0", "RO:0002411", "inhibited"),
    ("determinant", "RO:0002212", "inhibited"),
}

REMOVED_EDGE_KEYS = {
    ("determinant", "RO:0002436", "rnap"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies this determinant under antibiotic target protection."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Protection of RNA polymerase from rifamycin action is causally upstream of "
        "rifamycin resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The determinant protects RNA polymerase from rifamycin action to confer "
        "rifamycin resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this RNA-polymerase target-protection determinant to rifamycin "
        "antibiotics."
    ),
    ("drug0", "RO:0002411", "inhibited"): (
        "Rifamycin antibiotics inhibit bacterial RNA polymerase."
    ),
    ("determinant", "RO:0002212", "inhibited"): (
        "The target-protection determinant counters the local rifamycin-inhibited "
        "RNA polymerase state."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    parent_identifier: str
    state_description: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == self.parent_identifier

    @property
    def parent_evidence(self) -> dict[str, str]:
        return PARENT_EVIDENCE[self.parent_identifier]

    @property
    def helr_branch(self) -> bool:
        return self.parent_identifier == HEL_PARENT


TARGETS = {
    HEL_PARENT: Target(
        identifier=HEL_PARENT,
        filename="helicase-like-rna-polymerase-protection-protein-aro3007207.yaml",
        parent_identifier=HEL_PARENT,
        state_description=(
            "Local state for rifamycin-inhibited bacterial RNA polymerase that "
            "helicase-like HelR-family proteins counter by disrupting rifamycin "
            "binding to RNA polymerase."
        ),
    ),
    HELR: Target(
        identifier=HELR,
        filename="helr-aro3007208.yaml",
        parent_identifier=HEL_PARENT,
        state_description=(
            "Local state for rifamycin-inhibited bacterial RNA polymerase that HelR "
            "counteracts by displacing bound rifamycins."
        ),
    ),
    RBPA_PARENT: Target(
        identifier=RBPA_PARENT,
        filename="rbpa-bacterial-rna-polymerase-binding-protein-aro3004243.yaml",
        parent_identifier=RBPA_PARENT,
        state_description=(
            "Local state for rifamycin-inhibited bacterial RNA polymerase that "
            "RbpA-family RNA-polymerase binding proteins counter through "
            "target-protection activity."
        ),
    ),
    RBPA: Target(
        identifier=RBPA,
        filename="rbpa-aro3000245.yaml",
        parent_identifier=RBPA_PARENT,
        state_description=(
            "Local state for rifamycin-inhibited bacterial RNA polymerase that "
            "RbpA counteracts through RNA-polymerase target protection."
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = "ARO drug-class relationship asserted directly on this record."
    else:
        notes = (
            "ARO drug-class relationship asserted on "
            f"{target.parent_identifier} and inherited by {target.identifier}."
        )
    return {
        "reference": target.parent_identifier,
        "snippet": DRUG_RELATION_SNIPPET,
        "notes": notes,
    }


def _branch_evidence(
    record: dict[str, Any],
    target: Target,
) -> tuple[dict[str, str], ...]:
    evidence = [
        _target_evidence(record),
        target.parent_evidence,
        MECHANISM_EVIDENCE,
        *_source_evidence(record),
    ]
    if target.helr_branch:
        evidence.append(HEL_DISPLACEMENT_EVIDENCE)
    return tuple(evidence)


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = (item["reference"], " ".join(item.get("snippet", "").split()))
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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "inhibited", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    input_edges = CORE_EDGE_KEYS | REMOVED_EDGE_KEYS
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in input_edges:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    missing_edges = CORE_EDGE_KEYS - seen
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _inhibited_node(target: Target) -> dict[str, str]:
    return {
        "node_id": "inhibited",
        "label": "rifamycin-inhibited RNA polymerase",
        "node_type": "STATE",
        "description": target.state_description,
    }


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    branch_evidence = _branch_evidence(record, target)
    drug_evidence = (
        *branch_evidence,
        _drug_relation_evidence(target),
        RIFAMYCIN_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → RNA polymerase target protection → rifamycin resistance",
        "description": (
            "Curated resistance graph for RNA-polymerase target-protection "
            "determinants. The graph preserves CARD's antibiotic target-protection "
            "mechanism and rifamycin drug-class assertion while replacing the "
            "ungrounded RNAP protein side node with a described local state for "
            "rifamycin-inhibited RNA polymerase."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            _inhibited_node(target),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                branch_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                branch_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                branch_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "drug0",
                "causally upstream of (inhibits RNA polymerase)",
                "RO:0002411",
                "inhibited",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "inhibited",
                branch_evidence,
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
        raise ValueError(f"{path}: not an RNA-polymerase target-protection target: {identifier}")
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
        help="ARO directory or exact RNA-polymerase target-protection YAML",
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
