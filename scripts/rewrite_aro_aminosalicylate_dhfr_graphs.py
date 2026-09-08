#!/usr/bin/env python3
"""Ground aminosalicylate-resistant DHFR target-replacement graphs.

The aminosalicylate-resistant DHFR branch inherited an abstract target-
replacement graph whose shared function was deliberately unnamed. These records
do name the relevant replacement function: dihydrofolate reductase activity.

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
HISTORY_ACTION = "Grounded aminosalicylate-resistant DHFR graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_REPLACEMENT_EVIDENCE = {
    "reference": "ARO:3000381",
    "snippet": (
        "Alternate proteins that have the same functions as other antibiotic "
        "target proteins, but are structurally different and thus resistant to "
        "antibiotics. These can replace the activity of other "
        "antibiotic-sensitive proteins in the presence of antibiotics."
    ),
    "notes": "CARD definition for antibiotic target replacement proteins.",
}

DHFR_EVIDENCE = {
    "reference": "ARO:3003425",
    "snippet": (
        "Key enzyme in folate metabolism. Catalyzes an essential reaction for "
        "de novo glycine and purine synthesis, and for DNA precursor synthesis."
    ),
    "notes": "CARD definition for antibiotic resistant dihydrofolate reductase.",
}

AMINOSALICYLATE_DHFR_EVIDENCE = {
    "reference": "ARO:3004183",
    "snippet": (
        "Antibiotic target replacement dihydrofolate reductase enzymes or "
        "domains with catalytic activity that confer resistance to "
        "aminosalicylates, esp. p-aminosalicylic acid."
    ),
    "notes": "CARD definition for aminosalicylate resistant dihydrofolate reductase.",
}

SALICYLIC_ACID_EVIDENCE = {
    "reference": "ARO:3007159",
    "snippet": "salicylic acid antibiotic",
    "notes": "ARO drug-class term for salicylic acid antibiotics.",
}

GO_DHFR_EVIDENCE = {
    "reference": "GO:0004146",
    "snippet": (
        "Catalysis of the reaction: 5,6,7,8-tetrahydrofolate + NADP+ = "
        "7,8-dihydrofolate + NADPH + H+."
    ),
    "notes": "GO definition for dihydrofolate reductase activity.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target replacement",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001002",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "salicylic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007159",
}

DHFR_ACTIVITY_NODE = {
    "node_id": "shared_function",
    "label": "dihydrofolate reductase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004146",
}

STRUCTURAL_DIFFERENCE_NODE = {
    "node_id": "structural_difference",
    "label": "structural difference from the sensitive target",
    "node_type": "STATE",
    "description": (
        "Local state representing the replacement dihydrofolate reductase "
        "structure that differs from antibiotic-sensitive target proteins."
    ),
}

RIBD_OVEREXPRESSION_NODE = {
    "node_id": "ribd_overexpression",
    "label": "ribD enzyme overexpression",
    "node_type": "STATE",
    "description": (
        "Local state for the ribD overexpression caused by PAS-resistance "
        "mutations in Mycobacterium tuberculosis."
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

INPUT_ALLOWED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002327", "shared_function"),
    ("determinant", "RO:0000086", "structural_difference"),
    ("determinant", "RO:0000086", "ribd_overexpression"),
    ("structural_difference", "RO:0002212", "drug0"),
    ("structural_difference", "RO:0002411", "resistance"),
    ("ribd_overexpression", "RO:0002213", "shared_function"),
    ("shared_function", "RO:0002411", "resistance"),
}

CORE_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002327", "shared_function"),
}

PARENT_OUTPUT_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    ("determinant", "RO:0000086", "structural_difference"),
    ("structural_difference", "RO:0002411", "resistance"),
}

RIBD_OUTPUT_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    ("determinant", "RO:0000086", "ribd_overexpression"),
    ("ribd_overexpression", "RO:0002213", "shared_function"),
    ("shared_function", "RO:0002411", "resistance"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: str


_TARGET_ROWS = """
ARO:3004183 parent aminosalicylate-resistant-dihydrofolate-reductase-aro3004183.yaml
ARO:3004184 ribd mycobacterium-tuberculosis-ribd-with-mutation-conferring-resistance-to-para-amin-aro3004184.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename=filename, kind=kind)
    for identifier, kind, filename in (
        line.split(maxsplit=2) for line in _TARGET_ROWS.strip().splitlines()
    )
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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _drug_relation_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    relation_evidence: list[dict[str, Any]] = []
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) != ("determinant", "ARO:2000001", "drug0"):
            continue
        relation_evidence.extend(
            item
            for item in _dicts(edge.get("evidence"))
            if str(item.get("snippet", "")).startswith(
                "relationship: confers_resistance_to_drug_class "
            )
        )
    if not relation_evidence:
        raise ValueError("missing drug relationship evidence")
    return copy.deepcopy(relation_evidence)


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "shared_function", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_ALLOWED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(CORE_INPUT_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


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


def _drug_edge(
    record: dict[str, Any],
    old_graph: dict[str, Any],
    *extra_evidence: dict[str, Any],
) -> dict[str, Any]:
    return _edge(
        "determinant",
        "confers resistance to",
        "ARO:2000001",
        "drug0",
        "ARO maps this PAS-resistant DHFR determinant to salicylic acid antibiotics.",
        *_drug_relation_evidence(old_graph),
        _record_evidence(record),
        SALICYLIC_ACID_EVIDENCE,
        *extra_evidence,
    )


def _parent_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    replacement_evidence = (
        record_evidence,
        DHFR_EVIDENCE,
        TARGET_REPLACEMENT_EVIDENCE,
    )
    function_evidence = (
        record_evidence,
        DHFR_EVIDENCE,
        TARGET_REPLACEMENT_EVIDENCE,
        GO_DHFR_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → DHFR target replacement → PAS resistance",
        "description": (
            "Conservative graph for aminosalicylate-resistant dihydrofolate "
            "reductase target replacement. The graph grounds the replacement "
            "activity to GO:0004146 and links the branch to salicylic acid "
            "antibiotics."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(DHFR_ACTIVITY_NODE),
            copy.deepcopy(STRUCTURAL_DIFFERENCE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies aminosalicylate-resistant DHFR under target replacement.",
                *replacement_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "DHFR target replacement preserves folate metabolism under PAS pressure.",
                *function_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    "A resistant DHFR activity replaces a PAS-sensitive folate "
                    "metabolism target to confer aminosalicylate resistance."
                ),
                *function_evidence,
            ),
            _drug_edge(record, old_graph, DHFR_EVIDENCE, TARGET_REPLACEMENT_EVIDENCE),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "shared_function",
                (
                    "The determinant enables dihydrofolate reductase activity, "
                    "the replacement function named by this ARO branch."
                ),
                *function_evidence,
            ),
            _edge(
                "determinant",
                "has quality (structurally unlike the sensitive target)",
                "RO:0000086",
                "structural_difference",
                (
                    "The target-replacement determinant is structurally "
                    "different from antibiotic-sensitive target proteins."
                ),
                *replacement_evidence,
            ),
            _edge(
                "structural_difference",
                "causally upstream of (target replacement resists inhibition)",
                "RO:0002411",
                "resistance",
                (
                    "Structural difference from PAS-sensitive target proteins "
                    "allows the replacement DHFR to resist inhibition."
                ),
                *replacement_evidence,
            ),
        ],
    }


def _ribd_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    branch_evidence = (
        record_evidence,
        AMINOSALICYLATE_DHFR_EVIDENCE,
        DHFR_EVIDENCE,
        TARGET_REPLACEMENT_EVIDENCE,
    )
    function_evidence = (*branch_evidence, GO_DHFR_EVIDENCE)

    return {
        "graph_id": "resistance",
        "title": (
            "Mycobacterium tuberculosis ribD mutation → RibD overexpression → "
            "alternative DHFR activity → PAS resistance"
        ),
        "description": (
            "Conservative graph for PAS resistance from mutated M. tuberculosis "
            "ribD. CARD states that point mutations cause RibD overexpression, "
            "allowing its C-terminal reductase domain to act as an alternative "
            "dihydrofolate reductase."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(RIBD_OVEREXPRESSION_NODE),
            copy.deepcopy(DHFR_ACTIVITY_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies PAS-resistant ribD under DHFR target replacement.",
                *branch_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The overexpressed RibD reductase domain supplies alternative DHFR activity.",
                *function_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    "PAS-resistance mutations in ribD cause overexpression "
                    "that permits alternative DHFR activity."
                ),
                *function_evidence,
            ),
            _drug_edge(record, old_graph, AMINOSALICYLATE_DHFR_EVIDENCE),
            _edge(
                "determinant",
                "has quality",
                "RO:0000086",
                "ribd_overexpression",
                "The resistance-conferring point mutations in ribD cause enzyme overexpression.",
                record_evidence,
                AMINOSALICYLATE_DHFR_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "shared_function",
                (
                    "Overexpressed RibD contains a C-terminal reductase domain "
                    "that can act as an alternative dihydrofolate reductase."
                ),
                *function_evidence,
            ),
            _edge(
                "ribd_overexpression",
                "positively regulates",
                "RO:0002213",
                "shared_function",
                (
                    "ribD overexpression allows the C-terminal reductase "
                    "domain to provide alternative DHFR activity."
                ),
                *function_evidence,
            ),
            _edge(
                "shared_function",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                (
                    "Alternative DHFR activity confers resistance to PAS and "
                    "other DHFR-inhibiting salicylic acid antibiotics."
                ),
                *function_evidence,
            ),
        ],
    }


def _graph(record: dict[str, Any], old_graph: dict[str, Any], target: Target) -> dict[str, Any]:
    if target.kind == "parent":
        return _parent_graph(record, old_graph)
    if target.kind == "ribd":
        return _ribd_graph(record, old_graph)
    raise ValueError(f"{target.identifier}: unknown target kind {target.kind}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0], target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an aminosalicylate DHFR target: {identifier}")
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
        help="ARO directory or one of the two aminosalicylate DHFR YAML files",
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
