#!/usr/bin/env python3
"""Ground and complete the singleton AxyZ efflux-regulator graph.

AxyZ is the local regulator of the AxyXY-OprZ efflux system. The existing graph
had the right broad mechanism shape but left pump expression as an ungrounded
biological process and ended at a second, process-typed antibiotic-efflux node.
This updater keeps the ARO:3000212 mutation and ARO:0010000 efflux mechanisms,
models increased AxyXY-OprZ expression as a described local state, and grounds
the named pump that carries the efflux mechanism.

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

HISTORY_ACTION = "Grounded the AxyZ AxyXY-OprZ efflux-regulator graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_IDENTIFIER = "ARO:3004145"
TARGET_FILENAME = "axyz-aro3004145.yaml"

AXYZ_DEFINITION = "AxyZ is a transcriptional regulator of the AxyXY-OprZ efflux pump system."
AXYXY_OPRZ_DEFINITION = (
    "In-frame axyZ gene deletion assay led to increased MICs of antibiotic substrates "
    "of the efflux system: aminoglycosides, cefepime, fluoroquinolones, tetracyclines "
    "and erythromycin, indicating that the product of axyZ negatively regulates "
    "expression of axyXY-oprZ. Moreover a 45 amino-acid substitution at position 29 of "
    "AxyZ (V29G) was identified in a clinical Achromobacter strain that occurred during "
    "the course of chronic respiratory tract colonization in a cystic fibrosis (CF) "
    "patient. This substitution, also detected in 3 other strains exposed in vitro to "
    "tobramycin, led to the increase in axyY transcription level (5 to 17-fold) together "
    "with the increase in antibiotic resistance level."
)

AXYZ_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": AXYZ_DEFINITION,
    "notes": "CARD definition for the AxyZ regulator.",
}

AXYXY_OPRZ_EVIDENCE = {
    "reference": "ARO:3004141",
    "snippet": AXYXY_OPRZ_DEFINITION,
    "notes": (
        "CARD definition for AxyXY-OprZ, recording the axyZ deletion and AxyZ V29G "
        "observations that increased axyY transcription and substrate MICs."
    ),
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

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic-efflux resistance mechanism.",
}

REGULATOR_EVIDENCE = {
    "reference": "ARO:3000451",
    "snippet": (
        "Protein(s) and two component regulatory systems that directly or indirectly "
        "change rates of antibiotic efflux."
    ),
    "notes": "CARD parent class for regulators that modulate antibiotic efflux.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

MUTATION_NODE = {
    "node_id": "mech1",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "AxyXY-OprZ",
    "node_type": "PROTEIN",
    "grounding": "ARO:3004141",
    "description": "Grounded to CARD's AxyXY-OprZ, the efflux system regulated by AxyZ.",
}

PUMP_EXPRESSION_NODE = {
    "node_id": "pump_expression",
    "label": "increased AxyXY-OprZ efflux pump expression",
    "node_type": "STATE",
    "description": (
        "Local state for the elevated axyXY-oprZ expression observed when AxyZ "
        "repression is disrupted."
    ),
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
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002213", "pump_expression"),
    ("pump_expression", "RO:0002411", "mech0"),
    ("pump", "RO:0002327", "mech0"),
}

INPUT_EDGE_KEYS = EXPECTED_EDGE_KEYS | {
    ("pump_expression", "RO:0002411", "efflux_process"),
    ("efflux_process", "RO:0002411", "resistance"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies AxyZ under antibiotic efflux because resistance-associated "
        "AxyZ variants increase expression of the AxyXY-OprZ efflux system."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "AxyXY-OprZ-mediated antibiotic efflux is the downstream resistance mechanism."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO also classifies AxyZ under mutation conferring antibiotic resistance."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "AxyZ deletion or substitution variants derepress AxyXY-OprZ and increase "
        "resistance to efflux substrates."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Resistance-associated AxyZ variants increase AxyXY-OprZ expression, raising "
        "efflux of antibiotic substrates."
    ),
    ("determinant", "RO:0002213", "pump_expression"): (
        "AxyZ variants are represented as positively regulating the local elevated "
        "AxyXY-OprZ expression state."
    ),
    ("pump_expression", "RO:0002411", "mech0"): (
        "Increased AxyXY-OprZ expression increases antibiotic efflux activity."
    ),
    ("pump", "RO:0002327", "mech0"): (
        "AxyXY-OprZ is the efflux system whose expression is increased when AxyZ is "
        "deleted or carries resistance-associated substitutions."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    TARGET_IDENTIFIER: Target(
        identifier=TARGET_IDENTIFIER,
        filename=TARGET_FILENAME,
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
    missing_nodes = sorted({"determinant", "mech0", "mech1", "pump_expression", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    required = {
        ("determinant", "RO:0000056", "mech0"),
        ("determinant", "RO:0000056", "mech1"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0002213", "pump_expression"),
    }
    missing_edges = required - seen
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

    efflux_evidence = (
        AXYZ_EVIDENCE,
        AXYXY_OPRZ_EVIDENCE,
        MUTANT_REGULATOR_EVIDENCE,
        REGULATOR_EVIDENCE,
        EFFLUX_EVIDENCE,
        *source_evidence,
    )
    mutation_evidence = (
        AXYZ_EVIDENCE,
        AXYXY_OPRZ_EVIDENCE,
        MUTANT_REGULATOR_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    pump_expression_evidence = (
        AXYZ_EVIDENCE,
        AXYXY_OPRZ_EVIDENCE,
        MUTANT_REGULATOR_EVIDENCE,
        *source_evidence,
    )
    pump_evidence = (
        AXYXY_OPRZ_EVIDENCE,
        EFFLUX_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": "AxyZ → AxyXY-OprZ derepression → antibiotic efflux",
        "description": (
            "Curated AxyZ graph for variants that increase AxyXY-OprZ efflux-pump "
            "expression. The graph keeps CARD's mutation and antibiotic-efflux "
            "mechanism classes, models elevated AxyXY-OprZ expression as a described "
            "local state, and grounds the downstream efflux pump to ARO:3004141."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(MUTATION_NODE),
            copy.deepcopy(PUMP_NODE),
            copy.deepcopy(PUMP_EXPRESSION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (efflux mechanism)",
                "RO:0000056",
                "mech0",
                efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                efflux_evidence,
            ),
            _edge(
                "determinant",
                "participates in (mutation mechanism)",
                "RO:0000056",
                "mech1",
                mutation_evidence,
            ),
            _edge(
                "mech1",
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
                (*mutation_evidence, EFFLUX_EVIDENCE),
            ),
            _edge(
                "determinant",
                "positively regulates (variant raises pump expression)",
                "RO:0002213",
                "pump_expression",
                pump_expression_evidence,
            ),
            _edge(
                "pump_expression",
                "causally upstream of (more pump, more efflux)",
                "RO:0002411",
                "mech0",
                (*pump_expression_evidence, EFFLUX_EVIDENCE),
            ),
            _edge(
                "pump",
                "enables (drug efflux)",
                "RO:0002327",
                "mech0",
                pump_evidence,
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
        raise ValueError(f"{path}: not an AxyZ target: {identifier}")
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or exact AxyZ YAML")
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
