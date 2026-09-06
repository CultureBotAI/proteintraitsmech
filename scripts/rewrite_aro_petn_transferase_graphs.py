#!/usr/bin/env python3
"""Ground and complete phosphoethanolamine-transferase ARO causal graphs.

The seven records handled here share the ARO:3003580 phosphoethanolamine route:
PEtN transfer to lipid A reduces the negative cell-surface charge used by
cationic polymyxins for binding. This updater grounds the transferase activity
to the exact local GO term, describes every edge, and adds the missing
charge-to-resistance edge while leaving the lipid-A molecule and local charge
state ungrounded.

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
    "timestamp": "2026-09-05T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Grounded phosphoethanolamine-transferase activity, described the PEtN lipid A "
        "charge-alteration edges, and linked reduced charge to resistance"
    ),
    "llm_assisted": True,
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall of gram "
        "negative bacteria is a mechanism of resistance for cationic antimicrobials "
        "that depend on the negative charge for binding to the surface."
    ),
    "notes": (
        "CARD's charge-alteration mechanism term connects reduced negative surface "
        "charge to resistance against cationic antimicrobials."
    ),
}

PMR_PETN_EVIDENCE = {
    "reference": "ARO:3004269",
    "snippet": (
        "This family of phosphoethanolamine transferase catalyze the addition of "
        "4-amino-4-deoxy-L-arabinose (L-Ara4N) and phosphoethanolamine to lipid A, "
        "which impedes the binding of colistin to the cell membrane."
    ),
    "notes": (
        "CARD's pmr phosphoethanolamine-transferase family term connects "
        "phosphoethanolamine transfer to lipid A with impaired colistin binding."
    ),
}

PETN_GROUP_EVIDENCE = {
    "reference": "ARO:3004112",
    "snippet": (
        "This group of enzymes catalyzes the addition of a phosphoethanolamine group "
        "to another molecule. The addition of this moiety to lipid A in bacterial "
        "species is often associated with polymyxin (otherwise known as colistin) "
        "resistance."
    ),
    "notes": (
        "CARD's parent PEtN-transferase definition is used for the transfer chemistry; "
        "the hedged resistance wording is not used as the sole causal resistance claim."
    ),
}

GO_PETN_TRANSFER_EVIDENCE = {
    "reference": "GO:0043838",
    "snippet": (
        "Catalysis of the reaction: Kdo2-lipid A + phosphatidylethanolamine = "
        "phosphoethanolamine-Kdo2-lipid A + diacylglycerol."
    ),
    "notes": (
        "GO reaction definition for the exact phosphatidylethanolamine:Kdo2-lipid A "
        "phosphoethanolamine transferase activity."
    ),
}

SHARED_NODE_UPDATES = {
    "petn_transfer": {
        "node_id": "petn_transfer",
        "label": "phosphatidylethanolamine:Kdo2-lipid A phosphoethanolamine transferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0043838",
        "description": (
            "Grounded to the GO molecular-function class for transfer of "
            "phosphoethanolamine from phosphatidylethanolamine to Kdo2-lipid A."
        ),
    },
    "lipid_a": {
        "node_id": "lipid_a",
        "label": "lipid A of the outer membrane",
        "node_type": "CHEMICAL",
        "description": (
            "Modified lipid A surface substrate; left label-only because no exact "
            "lipid A chemical class was verified in the local trait corpus."
        ),
    },
    "charge": {
        "node_id": "charge",
        "label": "reduced net negative surface charge",
        "node_type": "STATE",
        "description": (
            "Local state representing the reduced negative envelope charge produced by "
            "lipid A modification."
        ),
    },
}

CHARGE_RESISTANCE_EDGE = {
    "subject": "charge",
    "predicate": "causally upstream of (reduces polymyxin binding)",
    "predicate_id": "RO:0002411",
    "object": "resistance",
}

ALL_EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this determinant under charge alteration because PEtN "
        "addition to lipid A reduces the negative surface charge used by polymyxins "
        "for binding."
    ),
    ("mech0", "resistance"): (
        "Charge alteration is the broad resistance mechanism represented by the PEtN "
        "transfer route below."
    ),
    ("determinant", "resistance"): (
        "The determinant's PEtN-transferase activity modifies lipid A and reduces "
        "cationic antimicrobial binding."
    ),
    ("determinant", "drug0"): (
        "CARD asserts peptide-antibiotic resistance for this PEtN-transferase family "
        "or an ancestor of the determinant."
    ),
    ("determinant", "petn_transfer"): (
        "The determinant enables PEtN transfer to lipid A, the chemical modification "
        "that reduces polymyxin binding."
    ),
    ("petn_transfer", "lipid_a"): (
        "Kdo2-lipid A is the acceptor substrate for the grounded PEtN-transferase "
        "activity."
    ),
    ("lipid_a", "charge"): (
        "Addition of PEtN to lipid A is represented as the lipid A modification that "
        "reduces the net negative bacterial surface charge."
    ),
    ("charge", "drug0"): (
        "Lower negative surface charge impedes binding by cationic peptide antibiotics "
        "such as colistin."
    ),
    ("charge", "resistance"): (
        "The same charge reduction is modeled as the terminal causal state for the "
        "polymyxin-resistance phenotype."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    expected_edges: set[tuple[str, str]]


PARENT_EDGES = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "petn_transfer"),
    ("petn_transfer", "lipid_a"),
    ("lipid_a", "charge"),
    ("charge", "resistance"),
}

CHILD_EDGES = PARENT_EDGES | {
    ("determinant", "drug0"),
    ("charge", "drug0"),
}

TARGETS = {
    "ARO:3004112": Target(
        identifier="ARO:3004112",
        filename="phosphoethanolamine-transferase-conferring-colistin-resistance-aro3004112.yaml",
        expected_edges=PARENT_EDGES,
    ),
    "ARO:3004269": Target(
        identifier="ARO:3004269",
        filename="pmr-phosphoethanolamine-transferase-aro3004269.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3004465": Target(
        identifier="ARO:3004465",
        filename="intrinsic-colistin-resistant-phosphoethanolamine-transferase-aro3004465.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3004466": Target(
        identifier="ARO:3004466",
        filename="icr-mc-aro3004466.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3004569": Target(
        identifier="ARO:3004569",
        filename="icr-mo-aro3004569.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3003576": Target(
        identifier="ARO:3003576",
        filename="epta-aro3003576.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3005047": Target(
        identifier="ARO:3005047",
        filename="eptb-aro3005047.yaml",
        expected_edges=CHILD_EDGES,
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


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


def _petn_transfer_evidence() -> list[dict[str, str]]:
    return [
        copy.deepcopy(PETN_GROUP_EVIDENCE),
        copy.deepcopy(GO_PETN_TRANSFER_EVIDENCE),
    ]


def _charge_resistance_evidence() -> list[dict[str, str]]:
    return [
        copy.deepcopy(CHARGE_ALTERATION_EVIDENCE),
        copy.deepcopy(PMR_PETN_EVIDENCE),
    ]


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id not in SHARED_NODE_UPDATES:
            continue
        nodes[index] = copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        found.add(node_id)

    missing = sorted(set(SHARED_NODE_UPDATES) - found)
    if missing:
        missing_ids = ", ".join(missing)
        msg = f"{target.identifier}: missing node(s): {missing_ids}"
        raise ValueError(msg)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{target.identifier}: missing resistance causal graph"
        raise ValueError(msg)

    _enrich_nodes(graph, target)

    edges = graph.setdefault("edges", [])
    if not any(_edge_key(edge) == ("charge", "resistance") for edge in edges):
        edges.append(copy.deepcopy(CHARGE_RESISTANCE_EDGE))

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in target.expected_edges:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        edge["description"] = ALL_EDGE_DESCRIPTIONS[key]
        if key == ("determinant", "petn_transfer"):
            edge["evidence"] = _petn_transfer_evidence()
        elif key == ("petn_transfer", "lipid_a"):
            edge["evidence"] = [copy.deepcopy(PMR_PETN_EVIDENCE), copy.deepcopy(GO_PETN_TRANSFER_EVIDENCE)]
        elif key == ("charge", "resistance"):
            edge["evidence"] = _charge_resistance_evidence()
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(target.expected_edges - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    graph["edges"] = enriched_edges
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a phosphoethanolamine-transferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
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
        help="ARO directory or one of the seven target YAML files",
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
