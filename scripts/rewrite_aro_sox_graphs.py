#!/usr/bin/env python3
"""Ground and complete Sox-family mutant efflux-regulator graphs.

The SoxR/S branch records all inherited a generic mutant-efflux-regulator
graph. This updater keeps the mutation-to-efflux shape, replaces the borrowed
family-only edge evidence with exact Sox evidence, and models increased
Sox-dependent efflux-pump expression as a described local state.

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

HISTORY_ACTION = "Grounded Sox efflux-regulator causal graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

SOXR_PARENT = "ARO:3000836"
SOXS_PARENT = "ARO:3000837"

SOXR_DEFINITION = (
    "SoxR is a sensory protein that upregulates soxS expression in the presence "
    "of redox-cycling drugs. This stress response leads to the expression many "
    "multidrug efflux pumps. In Pseudomonas aeruginosa, which lacks SoxS, SoxR "
    "is able to directly upregulate the expression of the MexGHI-OpmD efflux pump."
)

SOXS_DEFINITION = (
    "SoxS is a global regulator that up-regulates the expression of AcrAB efflux "
    "genes. It also reduces OmpF expression to decrease cell membrane permeability."
)

PARENT_EVIDENCE = {
    SOXR_PARENT: {
        "reference": SOXR_PARENT,
        "snippet": SOXR_DEFINITION,
        "notes": "CARD definition for the soxR mutant-efflux-regulator parent.",
    },
    SOXS_PARENT: {
        "reference": SOXS_PARENT,
        "snippet": SOXS_DEFINITION,
        "notes": "CARD definition for the soxS mutant-efflux-regulator parent.",
    },
}

MUTANT_REGULATOR_EVIDENCE = {
    "reference": "ARO:3000219",
    "snippet": (
        "Efflux regulatory proteins with mutations that result in increased expression "
        "of efflux proteins."
    ),
    "notes": "CARD definition for mutant efflux regulators that increase efflux-protein expression.",
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

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic-efflux resistance mechanism.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

EFFLUX_PROCESS_NODE = {
    "node_id": "efflux_process",
    "label": "antibiotic efflux",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "ARO:0010000",
    "description": "Antibiotic efflux downstream of increased Sox-dependent pump expression.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms but "
        "has no term for the resistance phenotype itself."
    ),
}

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002213", "pump_expression"),
    ("pump_expression", "RO:0002411", "efflux_process"),
    ("efflux_process", "RO:0002411", "resistance"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies this Sox regulator variant under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Sox mutations increase expression of efflux pumps, which can increase "
        "antibiotic resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The Sox determinant promotes multidrug efflux-pump expression upstream "
        "of the resistance phenotype."
    ),
    ("determinant", "RO:0002213", "pump_expression"): (
        "Sox activity is represented as positively regulating the local elevated "
        "efflux-pump-expression state."
    ),
    ("pump_expression", "RO:0002411", "efflux_process"): (
        "Increased Sox-dependent pump expression increases antibiotic efflux."
    ),
    ("efflux_process", "RO:0002411", "resistance"): (
        "Antibiotic efflux contributes to the multidrug-resistance phenotype."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    parent_identifier: str
    expression_label: str

    @property
    def parent_evidence(self) -> dict[str, str]:
        return PARENT_EVIDENCE[self.parent_identifier]

    @property
    def pump_expression_node(self) -> dict[str, str]:
        return {
            "node_id": "pump_expression",
            "label": self.expression_label,
            "node_type": "STATE",
            "description": (
                "Local state for increased Sox-dependent multidrug efflux-pump "
                "expression."
            ),
        }


TARGETS = {
    SOXR_PARENT: Target(
        identifier=SOXR_PARENT,
        filename="soxr-aro3000836.yaml",
        parent_identifier=SOXR_PARENT,
        expression_label="increased SoxR/SoxS-dependent efflux pump expression",
    ),
    "ARO:3003381": Target(
        identifier="ARO:3003381",
        filename="escherichia-coli-soxr-with-mutation-conferring-antibiotic-resistance-aro3003381.yaml",
        parent_identifier=SOXR_PARENT,
        expression_label="increased Escherichia coli SoxR/SoxS-dependent efflux pump expression",
    ),
    "ARO:3003382": Target(
        identifier="ARO:3003382",
        filename="salmonella-enterica-soxr-with-mutation-conferring-antibiotic-resistance-aro3003382.yaml",
        parent_identifier=SOXR_PARENT,
        expression_label="increased Salmonella SoxR/SoxS-dependent efflux pump expression",
    ),
    "ARO:3004107": Target(
        identifier="ARO:3004107",
        filename="pseudomonas-aeruginosa-soxr-aro3004107.yaml",
        parent_identifier=SOXR_PARENT,
        expression_label="increased Pseudomonas aeruginosa MexGHI-OpmD expression",
    ),
    SOXS_PARENT: Target(
        identifier=SOXS_PARENT,
        filename="soxs-aro3000837.yaml",
        parent_identifier=SOXS_PARENT,
        expression_label="increased AcrAB efflux gene expression",
    ),
    "ARO:3003511": Target(
        identifier="ARO:3003511",
        filename="escherichia-coli-soxs-with-mutation-conferring-antibiotic-resistance-aro3003511.yaml",
        parent_identifier=SOXS_PARENT,
        expression_label="increased Escherichia coli AcrAB efflux gene expression",
    ),
    "ARO:3003383": Target(
        identifier="ARO:3003383",
        filename="salmonella-serovars-soxs-with-mutation-conferring-antibiotic-resistance-aro3003383.yaml",
        parent_identifier=SOXS_PARENT,
        expression_label="increased Salmonella AcrAB efflux gene expression",
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
    missing_nodes = sorted(
        {"determinant", "mech0", "pump_expression", "efflux_process", "resistance"} - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    missing_edges = EXPECTED_EDGE_KEYS - seen
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)

    mutation_evidence = (
        _target_evidence(record),
        target.parent_evidence,
        MUTANT_REGULATOR_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    efflux_evidence = (
        _target_evidence(record),
        target.parent_evidence,
        MUTANT_REGULATOR_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → Sox-dependent efflux → resistance",
        "description": (
            "Curated resistance graph for Sox-family mutant efflux regulators. "
            "The graph keeps CARD's mutation mechanism, models increased "
            "Sox-dependent efflux-pump expression as a described local state, "
            "and terminates the expression cascade at the antibiotic-efflux "
            "process."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(target.pump_expression_node),
            copy.deepcopy(EFFLUX_PROCESS_NODE),
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
                efflux_evidence,
            ),
            _edge(
                "determinant",
                "positively regulates (raises pump expression)",
                "RO:0002213",
                "pump_expression",
                efflux_evidence,
            ),
            _edge(
                "pump_expression",
                "causally upstream of (more pump, more efflux)",
                "RO:0002411",
                "efflux_process",
                efflux_evidence,
            ),
            _edge(
                "efflux_process",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                efflux_evidence,
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
        raise ValueError(f"{path}: not a Sox target: {identifier}")
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or exact Sox YAML")
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
