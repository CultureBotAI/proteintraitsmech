#!/usr/bin/env python3
"""Ground gidB ribosomal-alteration resistance graphs.

The ARO gidB branch contains a broad aminoglycoside parent and a
Mycobacterium tuberculosis streptomycin child. Both records currently carry a
generic acquired-16S-rRNA-methyltransferase subgraph that is not specific to
gidB loss-of-function resistance. This updater rewrites the exact two-record
branch to the three grounded ARO mechanism routes plus the aminoglycoside
drug-class edge.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
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
HISTORY_ACTION = "Grounded gidB ribosomal-alteration resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

GIDB_PARENT_EVIDENCE = {
    "reference": "ARO:3003466",
    "snippet": (
        "GidB is a m7G methyltransferase specific for 16S rRNA. Mutations within "
        "the gidB gene causes changes in the structure or 16s rRNA, leading to "
        "resistance to aminoglycosides."
    ),
    "notes": "CARD definition for the antibiotic-resistant gidB parent.",
}

MECHANISM_EVIDENCE = {
    "target_alteration": {
        "reference": "ARO:0001001",
        "snippet": (
            "Mutational alteration or enzymatic modification of antibiotic target "
            "which results in antibiotic resistance."
        ),
        "notes": "CARD definition for antibiotic target alteration.",
    },
    "ribosomal_alteration": {
        "reference": "ARO:3000211",
        "snippet": (
            "Chemical alteration of the ribosome results in modification of an "
            "antibiotic's target leading to resistance."
        ),
        "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
    },
    "mutation": {
        "reference": "ARO:3000212",
        "snippet": (
            "Point mutations in the DNA may lead to an altered gene product that "
            "may result in antibiotic resistance. Examples included modified "
            "antibiotic targets with lower binding affinities and the deactivation "
            "of repressors that result in increased expression of genes that "
            "inactivate or pump out antibiotics."
        ),
        "notes": "CARD definition for mutation conferring antibiotic resistance.",
    },
}

MECHANISM_NODES = [
    (
        "mech0",
        "target_alteration",
        {
            "node_id": "mech0",
            "label": "antibiotic target alteration",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001001",
        },
    ),
    (
        "mech1",
        "ribosomal_alteration",
        {
            "node_id": "mech1",
            "label": "ribosomal alteration conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000211",
        },
    ),
    (
        "mech2",
        "mutation",
        {
            "node_id": "mech2",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
    ),
]

DRUG_NODE = {
    "node_id": "drug0",
    "label": "aminoglycoside antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000016",
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

DRUG_RELATION_REFERENCE = "ARO:3003466"
DRUG_RELATION_OBJECT = "ARO:0000016"
DRUG_RELATION_LABEL = "aminoglycoside antibiotic"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_title: str
    graph_description: str


TARGETS = {
    "ARO:3003466": Target(
        identifier="ARO:3003466",
        filename="antibiotic-resistant-gidb-aro3003466.yaml",
        graph_title="antibiotic resistant gidB → ribosomal alteration → resistance",
        graph_description=(
            "Conservative graph for the antibiotic-resistant gidB parent. The "
            "graph keeps the ARO target-alteration, ribosomal-alteration, "
            "mutation, and aminoglycoside drug-class routes and drops the former "
            "generic 16S rRNA methyltransferase subgraph."
        ),
    ),
    "ARO:3003470": Target(
        identifier="ARO:3003470",
        filename=(
            "mycobacterium-tuberculosis-gidb-mutation-conferring-resistance-to-"
            "streptomycin-aro3003470.yaml"
        ),
        graph_title=(
            "Mycobacterium tuberculosis gidB mutation → ribosomal alteration → resistance"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis gidB mutations. "
            "The graph keeps the inherited ARO target-alteration, "
            "ribosomal-alteration, mutation, and aminoglycoside drug-class "
            "routes and avoids asserting the generic acquired "
            "aminoglycoside-resistance methyltransferase pathway."
        ),
    ),
}

LEGACY_METHYLATION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "methyltransferase"),
    ("methyltransferase", "RO:0002411", "methylated"),
    ("methylated", "RO:0002212", "decoding_site"),
    ("drug0", "RO:0002436", "decoding_site"),
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


def _gidb_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == GIDB_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record),)
    return (_target_evidence(record), GIDB_PARENT_EVIDENCE)


def _mechanism_evidence(
    record: dict[str, Any],
    mechanism_key: str,
) -> tuple[dict[str, str], ...]:
    return _gidb_evidence(record) + (MECHANISM_EVIDENCE[mechanism_key],)


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3003466; modeled here as a "
            "determinant-to-aminoglycoside-antibiotic edge and inherited by "
            "the Mycobacterium tuberculosis gidB child."
        ),
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item["snippet"],
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


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    keys = {
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }
    for node_id, _, _ in MECHANISM_NODES:
        keys.add(("determinant", "RO:0000056", node_id))
        keys.add((node_id, "RO:0002411", "resistance"))
    return keys


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | LEGACY_METHYLATION_EDGE_KEYS


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "mech1", "mech2", "drug0", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(_canonical_edge_keys() - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        *(copy.deepcopy(node) for _, _, node in MECHANISM_NODES),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for node_id, mechanism_key, node in MECHANISM_NODES:
        edges.extend(
            [
                _edge(
                    "determinant",
                    "participates in (resistance mechanism)",
                    "RO:0000056",
                    node_id,
                    f"The ARO hierarchy classifies gidB determinants under {node['label']}.",
                    _mechanism_evidence(record, mechanism_key),
                ),
                _edge(
                    node_id,
                    "causally upstream of",
                    "RO:0002411",
                    "resistance",
                    f"The inherited {node['label']} mechanism links gidB to resistance.",
                    _mechanism_evidence(record, mechanism_key),
                ),
            ]
        )

    drug_evidence = _gidb_evidence(record) + (_drug_evidence(), MECHANISM_EVIDENCE["mutation"])
    edges.extend(
        [
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The ARO hierarchy links gidB mutations to aminoglycoside resistance.",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "The ARO hierarchy links this gidB determinant to aminoglycoside antibiotics.",
                drug_evidence,
            ),
        ]
    )
    return edges


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next(
        (item for item in graphs if item.get("graph_id") in {"resistance", "resistance-draft"}),
        None,
    )
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["graph_id"] = "resistance"
    graph["title"] = target.graph_title
    graph["description"] = target.graph_description
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def _promote_to_reviewed(text: str) -> str:
    return re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED", text, count=1, flags=re.M)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a gidB target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases and record.get("mapping_status") == "REVIEWED":
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _promote_to_reviewed(out)
    if HISTORY_ACTION not in out:
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
        help="ARO directory or one of the two target YAML files",
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
