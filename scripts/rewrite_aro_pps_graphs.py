#!/usr/bin/env python3
"""Rewrite ppsA/ppsC/ppsD pyrazinamide-resistance causal graphs.

The ppsA/ppsC/ppsD records inherited an evidence-limited graph that captured
the local CARD relationship to phthiocerol dimycocerosate biosynthesis but did
not assert the resistance bridge. Gopal et al. 2016 explicitly identify
pyrazinoic-acid/pyrazinamide resistance from the ppsA-E/mas PDIM pathway, so
this updater models the conservative bridge as loss of PDIM biosynthesis.

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
HISTORY_ACTION = "Grounded pps PDIM-loss pyrazinamide graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

PPS_PARENT_EVIDENCE = {
    "reference": "ARO:3005002",
    "snippet": (
        "Genes ppsA-E constitute an operon encoding enzymes involved in the "
        "biosynthesis of phthiocerol dimycocerosate and other lipids in "
        "Mycobacterium tuberculosis. Mutations within this region can result "
        "in resistance to pyrazinamide."
    ),
    "notes": "CARD definition for antibiotic resistant polyketide synthase genes.",
}

PZA_PDIM_PATHWAY_EVIDENCE = {
    "reference": "PMID:27759369",
    "snippet": (
        "ppsA-E, involved in the synthesis of the virulence factor "
        "phthiocerol dimycocerosate (PDIM)"
    ),
    "notes": (
        "Gopal et al. 2016 identified ppsA-E in the PDIM pathway among "
        "pyrazinoic-acid-resistant mycobacterial mutants."
    ),
}

PZA_LOSS_OF_VIRULENCE_EVIDENCE = {
    "reference": "PMID:27759369",
    "snippet": "Loss of Virulence Factor Synthesis",
    "notes": (
        "Gopal et al. 2016 named loss of virulence-factor synthesis as one "
        "of two distinct pyrazinamide-resistance mechanisms."
    ),
}

PYRAZINE_EVIDENCE = {
    "reference": "ARO:3007155",
    "snippet": "pyrazine antibiotic",
    "notes": "ARO drug-class term for pyrazine antibiotics.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "pyrazine antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007155",
}

PDIM_LOSS_NODE = {
    "node_id": "pdim_loss",
    "label": "loss of phthiocerol dimycocerosate biosynthesis",
    "node_type": "STATE",
    "description": (
        "Local state for ppsA-E/mas pathway mutations that disrupt production "
        "of the virulence factor phthiocerol dimycocerosate."
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
    ("determinant", "RO:0000056", "pdim_synthesis"),
    ("determinant", "RO:0000086", "pdim_loss"),
    ("pdim_loss", "RO:0002411", "resistance"),
}

CORE_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

OUTPUT_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    ("determinant", "RO:0000086", "pdim_loss"),
    ("pdim_loss", "RO:0002411", "resistance"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3005002 antibiotic-resistant-polyketide-synthase-genes-aro3005002.yaml
ARO:3004972 antibiotic-resistant-ppsa-aro3004972.yaml
ARO:3004973 pyrazinamide-resistant-ppsa-aro3004973.yaml
ARO:3004883 antibiotic-resistant-ppsc-aro3004883.yaml
ARO:3004884 pyrazinamide-resistant-ppsc-aro3004884.yaml
ARO:3004975 mycobacterium-tuberculosis-ppsc-mutations-confer-resistance-to-pyrazinamide-aro3004975.yaml
ARO:3004885 antibiotic-resistant-ppsd-aro3004885.yaml
ARO:3004886 pyrazinamide-resistant-ppsd-aro3004886.yaml
ARO:3004976 mycobacterium-tuberculosis-ppsd-mutations-confer-resistance-to-pyrazinamide-aro3004976.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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
    required_nodes = {"determinant", "mech0", "drug0", "resistance"}
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


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    mutation_evidence = (
        record_evidence,
        MUTATION_EVIDENCE,
        PPS_PARENT_EVIDENCE,
    )
    pdim_evidence = (
        record_evidence,
        MUTATION_EVIDENCE,
        PPS_PARENT_EVIDENCE,
        PZA_PDIM_PATHWAY_EVIDENCE,
        PZA_LOSS_OF_VIRULENCE_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → loss of PDIM biosynthesis → pyrazinamide resistance",
        "description": (
            "Conservative graph for pyrazinamide resistance from ppsA-E "
            "polyketide-synthase mutations. The graph keeps the PDIM "
            "biosynthetic defect as a described local state instead of "
            "guessing a pathway grounding."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(PDIM_LOSS_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies ppsA-E resistance under mutation conferring antibiotic resistance.",
                *mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "ppsA-E mutations are the mutation-mediated source of pyrazinamide resistance.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    "Mutations in this ppsA-E branch confer pyrazinamide "
                    "resistance through loss of PDIM virulence-factor synthesis."
                ),
                *pdim_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                "ARO maps the ppsA-E branch to pyrazine antibiotics.",
                *_drug_relation_evidence(old_graph),
                record_evidence,
                PPS_PARENT_EVIDENCE,
                PYRAZINE_EVIDENCE,
            ),
            _edge(
                "determinant",
                "has quality",
                "RO:0000086",
                "pdim_loss",
                (
                    "Resistance-conferring ppsA-E mutations disrupt the "
                    "PDIM-biosynthetic polyketide-synthase pathway."
                ),
                *pdim_evidence,
            ),
            _edge(
                "pdim_loss",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                (
                    "Loss of the PDIM virulence-factor synthesis pathway "
                    "confers pyrazinamide resistance."
                ),
                *pdim_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a ppsA-E target: {identifier}")
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
        help="ARO directory or one of the nine ppsA-E YAML files",
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
