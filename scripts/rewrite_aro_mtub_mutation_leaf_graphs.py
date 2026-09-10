#!/usr/bin/env python3
"""Rewrite low-score Mycobacterium tuberculosis mutation leaf graphs.

This targets four score-77 ARO records that sit under already curated
Mycobacterium mutation parents.  The graphs stay conservative when CARD only
asserts broad mutation-mediated resistance, but keep local causal routes where
the leaf definition itself asserts overexpression or MmpL5/MmpS5 efflux.

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

HISTORY_ACTION = "Curated Mycobacterium tuberculosis mutation leaf graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
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

NUDC_PARENT_EVIDENCE = {
    "reference": "ARO:3004911",
    "snippet": (
        "nudC is a NADH pyrophosphatase that is involved in nicotinate and "
        "nicotinamide metabolism. Mutations that occur on the nudC gene "
        "resulting in the inability for isoniazid to function."
    ),
    "notes": "CARD definition for the isoniazid-resistant nudC parent.",
}

RV2535C_PARENT_EVIDENCE = {
    "reference": "ARO:3007690",
    "snippet": (
        "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new "
        "genetic determinant of low-level bedaquiline and clofazimine "
        "cross-resistance in Mycobacterium tuberculosis when mutated."
    ),
    "notes": "CARD definition for the antibiotic-resistant Rv2535c parent.",
}

BEDAQUILINE_RV2535C_EVIDENCE = {
    "reference": "ARO:3007691",
    "snippet": "Loss-of-function mutations in Rv2535c are a common mechanism of resistance.",
    "notes": "CARD definition for the bedaquiline-resistant Rv2535c parent.",
}

PYRAZINE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3007155",
    "snippet": "pyrazine antibiotic",
    "notes": "ARO drug-class term inherited by pyrazinamide-resistance records.",
}

ISONIAZID_LIKE_EVIDENCE = {
    "reference": "ARO:3007152",
    "snippet": "isoniazid-like antibiotic",
    "notes": "ARO drug-class term inherited by isoniazid-resistance records.",
}

DIARYLQUINOLINE_EVIDENCE = {
    "reference": "ARO:3004491",
    "snippet": "diarylquinoline antibiotic",
    "notes": "ARO drug-class term inherited by bedaquiline-resistance records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

PYRAZINE_NODE = {
    "node_id": "drug0",
    "label": "pyrazine antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007155",
}

ISONIAZID_NODE = {
    "node_id": "drug0",
    "label": "isoniazid-like antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007152",
}

DIARYLQUINOLINE_NODE = {
    "node_id": "drug0",
    "label": "diarylquinoline antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3004491",
}

AMINOPEPTIDASE_NODE = {
    "node_id": "aminopeptidase",
    "label": "putative Xaa-Pro aminopeptidase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004177",
    "description": (
        "Grounded to the generic GO aminopeptidase activity. ARO calls the "
        "Rv2535c Xaa-Pro aminopeptidase assignment putative, and the graph "
        "keeps that uncertainty in the label."
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
class PzaTarget:
    identifier: str
    filename: str
    label: str
    drug_ancestor: str


PZA_TARGETS = {
    "ARO:3004957": PzaTarget(
        identifier="ARO:3004957",
        filename=(
            "mycobacterium-tuberculosis-clpc1-with-mutation-conferring-"
            "resistance-to-pyrazina-aro3004957.yaml"
        ),
        label="clpC1",
        drug_ancestor="ARO:3004878",
    ),
    "ARO:3004978": PzaTarget(
        identifier="ARO:3004978",
        filename=(
            "mycobacterium-tuberculosis-mas-mutations-confer-resistance-to-"
            "pyrazinamide-aro3004978.yaml"
        ),
        label="mas",
        drug_ancestor="ARO:3004882",
    ),
}

NUDC_TARGET_IDENTIFIER = "ARO:3004931"
NUDC_TARGET_FILENAME = (
    "mycobacterium-tuberculosis-nudc-mutations-conferring-resistance-to-"
    "isoniazid-aro3004931.yaml"
)

RV2535C_TARGET_IDENTIFIER = "ARO:3007692"
RV2535C_TARGET_FILENAME = (
    "mycobacterium-tuberculosis-rv2535c-with-mutation-conferring-resistance-"
    "to-bedaqu-aro3007692.yaml"
)

TARGET_FILENAMES = {
    *(target.filename for target in PZA_TARGETS.values()),
    NUDC_TARGET_FILENAME,
    RV2535C_TARGET_FILENAME,
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _own_definition_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(
    ancestor: str,
    target: str,
    drug_id: str,
    drug_label: str,
) -> dict[str, str]:
    return {
        "reference": ancestor,
        "snippet": f"relationship: confers_resistance_to_drug_class {drug_id} ! {drug_label}",
        "notes": (
            f"ARO drug-class relationship asserted on {ancestor} and "
            f"inherited by {target}."
        ),
    }


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(evidence),
    }


def _resistance_graph(record: dict[str, Any]) -> dict[str, Any]:
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{record.get('identifier')}: expected exactly one resistance graph")
    return graphs[0]


def _validate_core_graph(graph: dict[str, Any], identifier: str) -> None:
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - _nodes_by_id(graph).keys())
    if missing_nodes:
        raise ValueError(f"{identifier}: missing node(s): {', '.join(missing_nodes)}")

    required_edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }
    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in seen:
            raise ValueError(f"{identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(required_edges - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{identifier}: missing edge(s): {missing}")


def _pza_graph(
    record: dict[str, Any],
    target: PzaTarget,
    old_graph: dict[str, Any],
) -> dict[str, Any]:
    own_evidence = _own_definition_evidence(record)
    source_evidence = _source_evidence(record)
    mutation_evidence = (
        own_evidence,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        own_evidence,
        _drug_relation_evidence(
            target.drug_ancestor,
            target.identifier,
            "ARO:3007155",
            "pyrazine antibiotic",
        ),
        PYRAZINE_ANTIBIOTIC_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → pyrazinamide-resistance mutation",
        "description": (
            f"Conservative graph for a pyrazinamide-resistant {target.label} "
            "mutation record. The leaf definition states that the mutation can "
            "confer pyrazinamide resistance, so the graph keeps the broad ARO "
            "mutation mechanism and the inherited pyrazine-antibiotic edge "
            "without asserting a route through the protein's native activity."
        ),
        "nodes": [
            copy.deepcopy(_nodes_by_id(old_graph)["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PYRAZINE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                f"ARO classifies pyrazinamide-resistant {target.label} under "
                "mutation conferring antibiotic resistance.",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The broad ARO point-mutation mechanism covers altered gene "
                "products that may result in antibiotic resistance.",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The leaf ARO definition states that this Mycobacterium "
                "tuberculosis mutation confers or contributes to pyrazinamide "
                "resistance.",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                f"The {target.label} branch inherits an ARO "
                "confers-resistance-to relationship to pyrazine antibiotic.",
                drug_evidence,
            ),
        ],
    }


def _nudc_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    own_evidence = _own_definition_evidence(record)
    source_evidence = _source_evidence(record)
    mutation_evidence = (
        own_evidence,
        NUDC_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → NudC overexpression → isoniazid resistance",
        "description": (
            "Conservative graph for an isoniazid-resistant nudC mutation "
            "record. This leaf states that nudC mutations confer resistance "
            "through overexpression of the enzyme, and the graph stops before "
            "an unstated NADH-pyrophosphatase-to-isoniazid route."
        ),
        "nodes": [
            copy.deepcopy(_nodes_by_id(old_graph)["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(ISONIAZID_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies isoniazid-resistant nudC under mutation "
                "conferring antibiotic resistance.",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited point-mutation mechanism covers altered nudC "
                "expression that can result in antibiotic resistance.",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (via overexpression)",
                "RO:0002411",
                "resistance",
                "The leaf ARO definition links nudC mutation-driven "
                "overexpression to isoniazid resistance.",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                "The nudC branch inherits an ARO confers-resistance-to "
                "relationship to isoniazid-like antibiotic.",
                (
                    own_evidence,
                    _drug_relation_evidence(
                        "ARO:3004911",
                        NUDC_TARGET_IDENTIFIER,
                        "ARO:3007152",
                        "isoniazid-like antibiotic",
                    ),
                    ISONIAZID_LIKE_EVIDENCE,
                    *source_evidence,
                ),
            ),
        ],
    }


def _rv2535c_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    own_evidence = _own_definition_evidence(record)
    source_evidence = _source_evidence(record)
    mutation_evidence = (
        own_evidence,
        RV2535C_PARENT_EVIDENCE,
        BEDAQUILINE_RV2535C_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → increased MmpL5/MmpS5 efflux",
        "description": (
            "Conservative graph for the Rv2535c bedaquiline-resistance leaf. "
            "The leaf definition states that pepQ/Rv2535c mutations increase "
            "efflux through the MmpL5/MmpS5 transporter; the graph keeps the "
            "putative aminopeptidase role as a grounded side path and uses the "
            "MmpL5/MmpS5 efflux statement as the resistance route."
        ),
        "nodes": [
            copy.deepcopy(_nodes_by_id(old_graph)["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DIARYLQUINOLINE_NODE),
            copy.deepcopy(AMINOPEPTIDASE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies resistant Rv2535c variants under mutation "
                "conferring antibiotic resistance.",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The broad ARO point-mutation mechanism covers Rv2535c "
                "mutations that increase MmpL5/MmpS5 efflux.",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (via increased MmpL5/MmpS5 efflux)",
                "RO:0002411",
                "resistance",
                "The Rv2535c leaf definition states that pepQ/Rv2535c "
                "mutations increase efflux and reduce bedaquiline "
                "susceptibility.",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                "The bedaquiline-resistant Rv2535c branch inherits an ARO "
                "confers-resistance-to relationship to diarylquinoline "
                "antibiotic.",
                (
                    own_evidence,
                    BEDAQUILINE_RV2535C_EVIDENCE,
                    _drug_relation_evidence(
                        "ARO:3007691",
                        RV2535C_TARGET_IDENTIFIER,
                        "ARO:3004491",
                        "diarylquinoline antibiotic",
                    ),
                    DIARYLQUINOLINE_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "aminopeptidase",
                "The parent ARO definition states that Rv2535c/pepQ encodes a "
                "putative Xaa-Pro aminopeptidase.",
                (RV2535C_PARENT_EVIDENCE, *source_evidence),
            ),
        ],
    }


def enrich_record(record: dict[str, Any], path: Path) -> tuple[dict[str, Any], bool]:
    identifier = record.get("identifier")
    graph = _resistance_graph(record)
    _validate_core_graph(graph, str(identifier))

    if identifier in PZA_TARGETS:
        target = PZA_TARGETS[str(identifier)]
        if path.name != target.filename:
            raise ValueError(f"{path}: target {identifier} must be in {target.filename}")
        new_graph = _pza_graph(record, target, graph)
    elif identifier == NUDC_TARGET_IDENTIFIER:
        if path.name != NUDC_TARGET_FILENAME:
            raise ValueError(f"{path}: target {identifier} must be in {NUDC_TARGET_FILENAME}")
        new_graph = _nudc_graph(record, graph)
    elif identifier == RV2535C_TARGET_IDENTIFIER:
        if path.name != RV2535C_TARGET_FILENAME:
            raise ValueError(f"{path}: target {identifier} must be in {RV2535C_TARGET_FILENAME}")
        new_graph = _rv2535c_graph(record, graph)
    else:
        raise ValueError(f"{path}: not a Mycobacterium mutation leaf target: {identifier}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    out["causal_graphs"] = [new_graph]
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    enriched, changed = enrich_record(record, path)
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
    return [path / filename for filename in sorted(TARGET_FILENAMES)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one Mycobacterium mutation leaf YAML file",
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
