#!/usr/bin/env python3
"""Enrich class D beta-lactamase descendant graphs.

The BAT/BPU/BSU/CDD/LRA/MSI-OXA class D beta-lactamase records already carry
curated ARO drug-class edges. Their mechanism skeletons still contain the
pre-parent ungrounded beta-lactam amide node and single-reference edge
evidence. This updater reuses the simplified class D parent graph, preserves
the drug-class edges, and attaches class D / serine-hydrolysis / PROSITE
evidence.

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

HISTORY_ACTION = "Completed class D beta-lactamase descendant causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CLASS_D_EVIDENCE = {
    "reference": "ARO:3000075",
    "snippet": (
        "Class D beta-lactamases are one of the subgroups of "
        "beta-lactamases that are classified as serine enzymes."
    ),
    "notes": "CARD definition for the class D beta-lactamase parent term.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the inherited antibiotic inactivation mechanism.",
}

SERINE_HYDROLYSIS_EVIDENCE = {
    "reference": "ARO:3000187",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class A, C and D "
        "beta-lactamases. A serine residue located in the active site is used "
        "to form an acyl-enzyme intermediate and subsequent hydrolysis renders "
        "the beta-lactam inactive."
    ),
    "notes": "CARD definition for serine beta-lactamase hydrolysis.",
}

PROSITE_SERINE_HYDROLASE_EVIDENCE = {
    "reference": "PROSITE:PS00337",
    "snippet": (
        "Class-B enzymes are zinc containing proteins whilst class -A, C and D "
        "enzymes are serine hydrolases."
    ),
    "notes": (
        "PROSITE assigns Ambler class D beta-lactamases to the serine "
        "hydrolase classes."
    ),
}

PROSITE_BETA_LACTAM_HYDROLYSIS_EVIDENCE = {
    "reference": "PROSITE:PS00337",
    "snippet": (
        "Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the "
        "hydrolysis of an amide bond in the beta-lactam ring of antibiotics "
        "belonging to the penicillin/cephalosporin family."
    ),
    "notes": "PROSITE description of the beta-lactamase reaction.",
}

PROSITE_ACTIVE_SITE_EVIDENCE = {
    "reference": "PROSITE:PS00337",
    "snippet": (
        "All these proteins contain a Ser-x-x-Lys motif, where the serine is "
        "the active site residue."
    ),
    "notes": "PROSITE description of the class A/C/D active-site signature.",
}

BROAD_INACTIVATION_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

SERINE_HYDROLYSIS_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000187",
}

ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "beta-lactamase class A/C/D active-site signature (S-x-x-K)",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PS00337",
    "description": (
        "Grounded to the PROSITE class A/C/D beta-lactamase active-site "
        "signature, which carries the shared Ser-x-x-Lys catalytic motif."
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

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies this class D beta-lactamase family under antibiotic "
        "inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Serine beta-lactam hydrolysis enzymatically inactivates "
        "beta-lactam antibiotics, reaching the inherited antibiotic "
        "inactivation mechanism."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO classifies this class D beta-lactamase family under serine "
        "beta-lactam hydrolysis."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Hydrolysis renders the beta-lactam inactive and produces the "
        "resistance phenotype."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "This class D beta-lactamase family inherits the class D serine "
        "beta-lactamase mechanism that inactivates beta-lactam antibiotics."
    ),
    ("active_site", "BFO:0000050", "determinant"): (
        "The PROSITE PS00337 motif is the beta-lactamase class A/C/D "
        "active-site signature for the class D serine-hydrolase mechanism."
    ),
    ("active_site", "RO:0002327", "mech1"): (
        "The class D Ser-x-x-Lys active-site motif supplies the catalytic "
        "serine used in the serine beta-lactam hydrolysis mechanism."
    ),
}

EXPECTED_CORE_KEYS = set(EDGE_DESCRIPTIONS)
DRUG_CLASS_PREDICATE_ID = "ARO:2000001"
ACTIVE_SITE_EDGE_KEYS = {
    ("active_site", "BFO:0000050", "determinant"),
    ("active_site", "RO:0002327", "mech1"),
}
REQUIRED_INPUT_CORE_KEYS = EXPECTED_CORE_KEYS - ACTIVE_SITE_EDGE_KEYS
OLD_AMIDE_EDGE = ("mech0", "RO:0002233", "amide")
OLD_LOCAL_EDGE_KEYS = {
    OLD_AMIDE_EDGE,
    ("determinant", "RO:0002327", "transfer"),
    ("transfer", "RO:0002233", "drug0"),
    ("transfer", "RO:0002411", "modified"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3004746", "bat-beta-lactamase-aro3004746.yaml"),
    Target("ARO:3004747", "bat-1-aro3004747.yaml"),
    Target("ARO:3004758", "bpu-beta-lactamase-aro3004758.yaml"),
    Target("ARO:3004759", "bpu-1-aro3004759.yaml"),
    Target("ARO:3005394", "bsu-beta-lactamase-aro3005394.yaml"),
    Target("ARO:3006902", "bsu-1-aro3006902.yaml"),
    Target("ARO:3005396", "cdd-beta-lactamase-aro3005396.yaml"),
    Target("ARO:3006904", "cdd-1-aro3006904.yaml"),
    Target("ARO:3006905", "cdd-2-aro3006905.yaml"),
    Target("ARO:3004241", "class-d-lra-beta-lactamase-aro3004241.yaml"),
    Target("ARO:3004242", "msi-oxa-family-beta-lactamase-aro3004242.yaml"),
    Target("ARO:3003719", "msi-oxa-aro3003719.yaml"),
    Target("ARO:3007482", "rad-beta-lactamase-aro3007482.yaml"),
    Target("ARO:3007483", "rad-1-aro3007483.yaml"),
    Target("ARO:3007879", "rsd1-aro3007879.yaml"),
    Target("ARO:3009042", "rsd1-1-aro3009042.yaml"),
    Target("ARO:3005441", "rsd2-beta-lactamase-aro3005441.yaml"),
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
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
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(*evidence),
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _drug_edges(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in _dicts(graph.get("edges"))
        if edge.get("subject") == "determinant"
        and edge.get("predicate_id") == DRUG_CLASS_PREDICATE_ID
        and str(edge.get("object", "")).startswith("drug")
    ]


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "mech1", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    drug_edges = _drug_edges(graph)
    if not drug_edges:
        raise ValueError(f"{target.identifier}: missing ARO drug-class edge")

    drug_node_ids = {edge["object"] for edge in drug_edges}
    missing_drug_nodes = sorted(drug_node_ids - set(nodes))
    if missing_drug_nodes:
        missing = ", ".join(missing_drug_nodes)
        raise ValueError(f"{target.identifier}: missing drug node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found_core_edges: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if (
            key not in EXPECTED_CORE_KEYS
            and key not in OLD_LOCAL_EDGE_KEYS
            and edge.get("predicate_id") != DRUG_CLASS_PREDICATE_ID
        ):
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        if key in EXPECTED_CORE_KEYS:
            found_core_edges.add(key)

    missing_core_edges = sorted(REQUIRED_INPUT_CORE_KEYS - found_core_edges)
    if missing_core_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _drug_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [copy.deepcopy(nodes[edge["object"]]) for edge in _drug_edges(graph)]


def _copied_drug_edges(
    graph: dict[str, Any],
    *evidence: dict[str, str],
) -> list[dict[str, Any]]:
    out = []
    for edge in _drug_edges(graph):
        copied = copy.deepcopy(edge)
        copied["description"] = (
            str(edge.get("description"))
            if edge.get("description")
            else "CARD asserts that this determinant confers resistance to this beta-lactam drug class."
        )
        copied["evidence"] = _unique_evidence(
            *_dicts(edge.get("evidence")),
            *evidence,
        )
        out.append(copied)
    return out


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)

    target_evidence = _record_evidence(record)
    broad_evidence = (
        target_evidence,
        CLASS_D_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        SERINE_HYDROLYSIS_EVIDENCE,
        PROSITE_BETA_LACTAM_HYDROLYSIS_EVIDENCE,
    )
    serine_evidence = (
        target_evidence,
        CLASS_D_EVIDENCE,
        SERINE_HYDROLYSIS_EVIDENCE,
        PROSITE_SERINE_HYDROLASE_EVIDENCE,
        PROSITE_BETA_LACTAM_HYDROLYSIS_EVIDENCE,
    )
    active_site_evidence = (
        target_evidence,
        CLASS_D_EVIDENCE,
        SERINE_HYDROLYSIS_EVIDENCE,
        PROSITE_SERINE_HYDROLASE_EVIDENCE,
        PROSITE_ACTIVE_SITE_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → class D beta-lactam hydrolysis → resistance",
        "description": (
            "Conservative class D beta-lactamase graph. The graph reuses "
            "ARO:3000187 for the inherited serine beta-lactam hydrolysis "
            "mechanism, grounds the shared class A/C/D Ser-x-x-Lys "
            "active-site signature to PROSITE:PS00337, omits the former local "
            "amide-bond input node because ARO:3000187 already captures "
            "beta-lactam hydrolysis, and preserves curated CARD/ARO "
            "drug-class edges."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(BROAD_INACTIVATION_NODE),
            copy.deepcopy(SERINE_HYDROLYSIS_NODE),
            *_drug_nodes(graph),
            copy.deepcopy(ACTIVE_SITE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                *serine_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *serine_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                *broad_evidence,
                PROSITE_SERINE_HYDROLASE_EVIDENCE,
            ),
            *_copied_drug_edges(
                graph,
                target_evidence,
                CLASS_D_EVIDENCE,
                SERINE_HYDROLYSIS_EVIDENCE,
                PROSITE_BETA_LACTAM_HYDROLYSIS_EVIDENCE,
            ),
            _edge(
                "active_site",
                "part of (active site of the protein)",
                "BFO:0000050",
                "determinant",
                *active_site_evidence,
            ),
            _edge(
                "active_site",
                "enables (catalysis)",
                "RO:0002327",
                "mech1",
                *active_site_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
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

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a class D descendant target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = _dicts(enriched.get("curation_history"))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
        help="ARO directory or one of the class D descendant YAML files",
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
