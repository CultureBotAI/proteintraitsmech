#!/usr/bin/env python3
"""Ground and describe macrolide glycosyltransferase ARO causal graphs.

These eight records share the same CARD macrolide-glycosyltransferase graph
shape. The promoted graph already captures drug inactivation by glycosylation;
this updater adds conservative descriptions to every edge, grounds the
glycosyltransferase activity to the local generic GO superclass, and leaves the
macrolide product/site nodes label-only where no exact corpus class exists.

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
        "Grounded the macrolide glycosyltransferase activity node and described the "
        "shared macrolide glycosylation causal-graph edges"
    ),
    "llm_assisted": True,
}

FAMILY_PMID_EVIDENCE = {
    "reference": "PMID:17376874",
    "snippet": (
        "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, "
        "glycosylate and inactivate oleandomycin and diverse macrolides including "
        "erythromycin, respectively."
    ),
    "notes": "OleI and OleD glycosylate and inactivate macrolides.",
}

GO_GLYCOSYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016757",
    "snippet": (
        "Catalysis of the transfer of a glycosyl group from one compound (donor) to "
        "another (acceptor)."
    ),
    "notes": (
        "GO definition for the broad glycosyltransferase activity superclass; no "
        "macrolide-specific GO activity is available locally."
    ),
}

SHARED_NODE_UPDATES = {
    "glycosyl": {
        "node_id": "glycosyl",
        "label": "macrolide glycosyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0016757",
        "description": (
            "Grounded to the broad GO glycosyltransferase activity superclass because "
            "no macrolide-specific glycosyltransferase class is available locally."
        ),
    },
    "glyco_drug": {
        "node_id": "glyco_drug",
        "label": "glycosylated inactive macrolide",
        "node_type": "CHEMICAL",
        "description": (
            "Macrolide after enzymatic glycosyl-group transfer; left label-only because "
            "the exact inactive product differs by drug substrate."
        ),
    },
    "ribosome_site": {
        "node_id": "ribosome_site",
        "label": "23S rRNA macrolide binding site",
        "node_type": "NUCLEIC_ACID",
        "description": (
            "Ribosomal RNA site normally occupied by macrolide antibiotics; left "
            "label-only because the graph models a binding site rather than a complete "
            "23S rRNA molecule."
        ),
    },
}

ALL_EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this determinant under antibiotic inactivation because "
        "macrolide glycosyltransferases chemically modify and inactivate macrolides."
    ),
    ("mech0", "resistance"): (
        "Macrolide inactivation is the broad resistance mechanism produced by the "
        "glycosylation branch represented below."
    ),
    ("determinant", "mech1"): (
        "CARD also classifies this determinant under glycosylation of antibiotic "
        "conferring resistance, the specific inactivation chemistry."
    ),
    ("mech1", "resistance"): (
        "Glycosylation inactivates the macrolide substrate and thereby supports the "
        "resistance phenotype."
    ),
    ("determinant", "resistance"): (
        "The determinant's glycosyltransferase activity is the record-level causal "
        "route to macrolide resistance."
    ),
    ("determinant", "drug0"): (
        "CARD asserts macrolide-antibiotic resistance for this glycosyltransferase "
        "family or an ancestor of the determinant."
    ),
    ("determinant", "glycosyl"): (
        "The determinant enables macrolide glycosylation, the activity that modifies "
        "and inactivates the drug substrate."
    ),
    ("glycosyl", "glyco_drug"): (
        "Macrolide glycosyltransferase activity transfers a sugar onto the macrolide "
        "substrate, yielding a glycosylated inactive product."
    ),
    ("glyco_drug", "ribosome_site"): (
        "Glycosylation occurs on the macrolide surface used for 23S rRNA binding, "
        "which explains why the modified drug can no longer act at that site."
    ),
    ("drug0", "ribosome_site"): (
        "Unmodified erythromycin can bind the 23S rRNA target site that glycosylation "
        "blocks."
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
    ("determinant", "mech1"),
    ("mech1", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "glycosyl"),
    ("glycosyl", "glyco_drug"),
    ("glyco_drug", "ribosome_site"),
}

CHILD_EDGES = PARENT_EDGES | {
    ("determinant", "drug0"),
    ("drug0", "ribosome_site"),
}

TARGETS = {
    "ARO:3000458": Target(
        identifier="ARO:3000458",
        filename="macrolide-glycosyltransferase-aro3000458.yaml",
        expected_edges=PARENT_EDGES,
    ),
    "ARO:3000463": Target(
        identifier="ARO:3000463",
        filename="gima-aro3000463.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3004236": Target(
        identifier="ARO:3004236",
        filename="gima-family-macrolide-glycosyltransferase-aro3004236.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3000462": Target(
        identifier="ARO:3000462",
        filename="mgta-aro3000462.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3004237": Target(
        identifier="ARO:3004237",
        filename="mgt-macrolide-glycotransferase-aro3004237.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3000465": Target(
        identifier="ARO:3000465",
        filename="ole-glycosyltransferase-aro3000465.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3000865": Target(
        identifier="ARO:3000865",
        filename="oled-aro3000865.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3000866": Target(
        identifier="ARO:3000866",
        filename="olei-aro3000866.yaml",
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


def _aro_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    return {
        "reference": target.identifier,
        "snippet": record["definition"],
        "notes": "Exact ARO definition of this determinant.",
    }


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


def _glycosylation_evidence(record: dict[str, Any], target: Target) -> list[dict[str, str]]:
    return [
        copy.deepcopy(FAMILY_PMID_EVIDENCE),
        _aro_evidence(record, target),
        copy.deepcopy(GO_GLYCOSYLTRANSFERASE_EVIDENCE),
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

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in target.expected_edges:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        edge["description"] = ALL_EDGE_DESCRIPTIONS[key]
        if key == ("determinant", "glycosyl"):
            edge["evidence"] = _glycosylation_evidence(out, target)
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
        raise ValueError(f"{path}: not a macrolide glycosyltransferase target: {identifier}")
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
        help="ARO directory or one of the eight target YAML files",
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
