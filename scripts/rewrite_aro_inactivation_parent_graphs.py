#!/usr/bin/env python3
"""Describe broad antibiotic-inactivation ARO causal graphs.

The five records handled here assert enzymatic inactivation by chemical
modification without choosing one specific reaction. This updater keeps the
modification node label-only, makes that conservative modeling choice explicit,
describes every edge, and adds the missing terminal edge from the chemically
inactive drug state to antibiotic resistance.

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
        "Described broad antibiotic-inactivation edges and linked chemically "
        "inactivated drug states to resistance"
    ),
    "llm_assisted": True,
}

INACTIVATED_RESISTANCE_EDGE = {
    "subject": "inactivated",
    "predicate": "causally upstream of (drug is inactive)",
    "predicate_id": "RO:0002411",
    "object": "resistance",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    drug_name: str
    evidence: dict[str, str]

    @property
    def modification_node(self) -> dict[str, str]:
        return {
            "node_id": "modification",
            "label": f"enzymatic modification of {self.drug_name}",
            "node_type": "MOLECULAR_FUNCTION",
            "local": True,
            "description": (
                "Local broad modification node; left label-only because this ARO parent "
                "does not specify which chemical group is added or which bond is broken."
            ),
        }

    @property
    def inactivated_node(self) -> dict[str, str]:
        return {
            "node_id": "inactivated",
            "label": f"chemically modified, inactive {self.drug_name}",
            "node_type": "STATE",
            "description": (
                "Local state representing the chemically modified antibiotic after "
                "enzymatic inactivation."
            ),
        }


TARGETS = {
    "ARO:3007380": Target(
        identifier="ARO:3007380",
        filename="aminoglycoside-modifying-enzyme-aro3007380.yaml",
        drug_name="aminoglycoside antibiotic",
        evidence={
            "reference": "ARO:3007380",
            "snippet": (
                "Resistance-conferring genetic elements encoding proteins involved in "
                "the enzymatic inactivation of aminoglycoside antibiotics through "
                "chemical modification."
            ),
            "notes": (
                "CARD definition for aminoglycoside-modifying enzymes; the specific "
                "phosphorylation, nucleotidylation, or acetylation chemistry is not "
                "specified by this parent term."
            ),
        },
    ),
    "ARO:3000342": Target(
        identifier="ARO:3000342",
        filename="fosfomycin-inactivation-enzyme-aro3000342.yaml",
        drug_name="fosfomycin",
        evidence={
            "reference": "ARO:3000342",
            "snippet": "Enzymes that inactivate fosfomycin by chemical modification.",
            "notes": (
                "CARD definition for fosfomycin inactivation enzymes without specifying "
                "one conjugation chemistry."
            ),
        },
    ),
    "ARO:3000201": Target(
        identifier="ARO:3000201",
        filename="macrolide-inactivation-enzyme-aro3000201.yaml",
        drug_name="macrolide antibiotic",
        evidence={
            "reference": "ARO:3000201",
            "snippet": (
                "Enzymes shown to inactivate macrolide antibiotics by chemical "
                "modification, thereby conferring resistance to macrolides."
            ),
            "notes": (
                "CARD definition for macrolide inactivation enzymes without choosing "
                "phosphotransferase or esterase chemistry."
            ),
        },
    ),
    "ARO:3000576": Target(
        identifier="ARO:3000576",
        filename="rifampin-inactivation-enzyme-aro3000576.yaml",
        drug_name="rifampin antibiotic",
        evidence={
            "reference": "ARO:3000576",
            "snippet": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
            "notes": (
                "CARD definition for rifampin inactivation enzymes without specifying "
                "one chemical-modification route."
            ),
        },
    ),
    "ARO:3000233": Target(
        identifier="ARO:3000233",
        filename="streptogramin-inactivation-enzyme-aro3000233.yaml",
        drug_name="streptogramin antibiotic",
        evidence={
            "reference": "ARO:3000233",
            "snippet": (
                "Resistance to streptogramin antibiotics may be conferred through "
                "enzymatic inactivation. There are two known mechanisms of "
                "streptogramin inactivation shown clinically to confer resistance: 1) "
                "vgB lyase enzymes linearize type B streptogramin antibiotics by "
                "breaking the ester linkage; 2) vat acetyltransferase enzymes modify "
                "type A streptogramin antibiotics by transferring an acetyl group from "
                "acetyl-CoA to the secondary streptogramin hydroxyl. Both mechanisms "
                "result in antibiotic inactivation thus conferring resistance."
            ),
            "notes": (
                "CARD definition for streptogramin inactivation enzymes; both named "
                "chemistries are left to child terms."
            ),
        },
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this determinant under antibiotic inactivation by chemical "
        "modification."
    ),
    ("mech0", "resistance"): (
        "Antibiotic inactivation is the broad mechanism produced by the modification "
        "route below."
    ),
    ("determinant", "resistance"): (
        "The determinant encodes an enzyme that chemically modifies the drug, leaving "
        "the antibiotic inactive."
    ),
    ("determinant", "modification"): (
        "The determinant enables an unspecified chemical modification of the drug."
    ),
    ("modification", "inactivated"): (
        "The modification step is represented as producing the inactive antibiotic "
        "state."
    ),
    ("inactivated", "resistance"): (
        "The chemically inactivated drug is the terminal modeled cause of resistance "
        "for this broad parent record."
    ),
}

EXPECTED_EDGES = set(EDGE_DESCRIPTIONS)


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


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id == "modification":
            nodes[index] = target.modification_node
            found.add(node_id)
        elif node_id == "inactivated":
            nodes[index] = target.inactivated_node
            found.add(node_id)

    missing = sorted({"modification", "inactivated"} - found)
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
    if not any(_edge_key(edge) == ("inactivated", "resistance") for edge in edges):
        new_edge = copy.deepcopy(INACTIVATED_RESISTANCE_EDGE)
        new_edge["evidence"] = [copy.deepcopy(target.evidence)]
        edges.append(new_edge)

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_EDGES:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)

        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = [copy.deepcopy(target.evidence)]
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(EXPECTED_EDGES - seen)
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
        raise ValueError(f"{path}: not a broad inactivation target: {identifier}")
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
        help="ARO directory or one of the five broad inactivation target YAML files",
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
