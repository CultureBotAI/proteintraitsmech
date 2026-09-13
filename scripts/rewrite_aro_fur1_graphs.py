#!/usr/bin/env python3
"""Ground FUR1 pyrimidine-salvage resistance graphs.

The ARO FUR1 branch has a fungal uracil phosphoribosyltransferase parent that
links to pyrimidine antifungal resistance plus Candida and Saccharomyces
children that explicitly name FUR1/UPRT as an enzyme in pyrimidine salvage.
This updater promotes the exact three-record branch and adds the UPRT side
path only to the child records whose ARO definitions support it.

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
HISTORY_ACTION = "Grounded FUR1 pyrimidine-salvage resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of repressors "
        "that result in increased expression of genes that inactivate or pump out "
        "antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

FUR1_PARENT_EVIDENCE = {
    "reference": "ARO:3007556",
    "snippet": (
        "Fungal uracil phosphoribosyltransferases which include mutations to confer "
        "resistance to 5-flucytosine antibiotic."
    ),
    "notes": "CARD definition for the fungal uracil phosphoribosyltransferase parent.",
}

UPRT_EVIDENCE = {
    "reference": "GO:0004845",
    "snippet": (
        "Catalysis of the reaction: diphosphate + UMP = "
        "5-phospho-alpha-D-ribose 1-diphosphate + uracil."
    ),
    "notes": "GO definition for uracil phosphoribosyltransferase activity.",
}

PYRIMIDINE_SALVAGE_EVIDENCE = {
    "reference": "GO:0008655",
    "snippet": (
        "Any process that generates a pyrimidine-containing compound, a nucleobase, "
        "nucleoside, nucleotide or nucleic acid that contains a pyrimidine base, "
        "from derivatives of them without de novo synthesis."
    ),
    "notes": (
        "GO definition for pyrimidine-containing compound salvage; the same GO "
        "record lists pyrimidine salvage as a related synonym."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "pyrimidine antifungal drug",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007560",
}

UPRT_NODE = {
    "node_id": "uprt",
    "label": "uracil phosphoribosyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004845",
}

PYRIMIDINE_SALVAGE_NODE = {
    "node_id": "salvage",
    "label": "pyrimidine-containing compound salvage",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0008655",
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

DRUG_RELATION_REFERENCE = "ARO:3007556"
DRUG_RELATION_OBJECT = "ARO:3007560"
DRUG_RELATION_LABEL = "pyrimidine antifungal drug"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_description: str
    has_activity: bool = False


TARGETS = {
    "ARO:3007556": Target(
        identifier="ARO:3007556",
        filename="fungal-uracil-phosphoribosyltransferase-aro3007556.yaml",
        graph_description=(
            "Conservative graph for the fungal uracil phosphoribosyltransferase "
            "parent. The graph keeps the broad mutation-resistance claim and "
            "pyrimidine-antifungal drug-class edge but omits the pyrimidine-salvage "
            "side path, which only the child ARO definitions name."
        ),
    ),
    "ARO:3007557": Target(
        identifier="ARO:3007557",
        filename=(
            "candida-spp-fur1-with-mutations-conferring-resistance-to-"
            "5-flucytosine-aro3007557.yaml"
        ),
        graph_description=(
            "Conservative graph for Candida FUR1 mutations conferring "
            "5-flucytosine resistance. The graph grounds the FUR1 UPRT activity "
            "and pyrimidine-salvage pathway named by ARO, keeps the inherited "
            "pyrimidine-antifungal drug-class edge, and does not add an "
            "unsupported 5-flucytosine activation edge."
        ),
        has_activity=True,
    ),
    "ARO:3007559": Target(
        identifier="ARO:3007559",
        filename=(
            "saccharomyces-spp-fur1-with-mutations-conferring-resistance-to-"
            "5-flucytosine-aro3007559.yaml"
        ),
        graph_description=(
            "Conservative graph for Saccharomyces FUR1 mutations conferring "
            "5-flucytosine resistance. The graph grounds the FUR1 UPRT activity "
            "and pyrimidine-salvage pathway named by ARO, keeps the inherited "
            "pyrimidine-antifungal drug-class edge, and does not add an "
            "unsupported 5-flucytosine activation edge."
        ),
        has_activity=True,
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


def _mutation_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == FUR1_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record), MUTATION_EVIDENCE)
    return (_target_evidence(record), FUR1_PARENT_EVIDENCE, MUTATION_EVIDENCE)


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3007556; modeled here as a "
            "determinant-to-pyrimidine-antifungal edge and inherited by its "
            "child FUR1 records."
        ),
    }


def _drug_edge_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == FUR1_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record), _drug_evidence(), MUTATION_EVIDENCE)
    return (_target_evidence(record), FUR1_PARENT_EVIDENCE, _drug_evidence(), MUTATION_EVIDENCE)


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


def _canonical_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }
    if target.has_activity:
        expected.update(
            {
                ("determinant", "RO:0002327", "uprt"),
                ("uprt", "BFO:0000050", "salvage"),
            }
        )
    return expected


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "resistance"}
    if target.has_activity:
        required_nodes.update({"uprt", "salvage"})
    elif "uprt" in nodes or "salvage" in nodes:
        raise ValueError(f"{target.identifier}: unexpected FUR1 activity side-path node")

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    required_edges = _canonical_edge_keys(target)

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _canonical_edge_keys(target):
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(required_edges - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    ordered = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
    ]
    if target.has_activity:
        ordered.extend(
            [
                copy.deepcopy(UPRT_NODE),
                copy.deepcopy(PYRIMIDINE_SALVAGE_NODE),
            ]
        )
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    return ordered


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    mutation_evidence = _mutation_evidence(record)
    drug_evidence = _drug_edge_evidence(record)

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies resistant FUR1 variants under point mutations.",
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The inherited point-mutation mechanism links FUR1 determinants to resistance.",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The ARO hierarchy links FUR1 mutation records to antifungal resistance.",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "The ARO hierarchy links this FUR1 determinant to pyrimidine antifungal drugs.",
            drug_evidence,
        ),
    ]

    if target.has_activity:
        edges.extend(
            [
                _edge(
                    "determinant",
                    "enables",
                    "RO:0002327",
                    "uprt",
                    "ARO identifies FUR1 as a fungal UPRT enzyme.",
                    (target_evidence, UPRT_EVIDENCE),
                ),
                _edge(
                    "uprt",
                    "part of (pyrimidine salvage)",
                    "BFO:0000050",
                    "salvage",
                    "ARO places FUR1 UPRT in pyrimidine salvage.",
                    (target_evidence, PYRIMIDINE_SALVAGE_EVIDENCE),
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
    graph["title"] = f"{record['label']} → FUR1 mutation → resistance"
    graph["description"] = target.graph_description
    graph["nodes"] = _canonical_nodes(graph, target)
    graph["edges"] = _canonical_edges(out, target)
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
        raise ValueError(f"{path}: not a FUR1 target: {identifier}")
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
        help="ARO directory or one of the three target YAML files",
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
