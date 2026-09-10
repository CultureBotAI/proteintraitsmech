#!/usr/bin/env python3
"""Ground and complete the pncA prodrug-activation-loss graph.

pncA resistance is caused by losing pyrazinamidase activity: pyrazinamide is no
longer converted to pyrazinoic acid.  This updater preserves that inverted
causal shape, grounds the local loss and pyrazinoic-acid nodes, and connects
the loss state to resistance explicitly.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"
IDENTIFIER = "ARO:3004267"
FILENAME = "antibiotic-resistant-pnca-aro3004267.yaml"

HISTORY_ACTION = "Completed pncA prodrug-activation-loss causal graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PNCA_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "Point mutations in pncA prevent the enzyme from activating antibiotics, "
        "such as pyrazinamide."
    ),
    "notes": "CARD definition for the antibiotic resistant pncA parent.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

PNCA_LOSS_EVIDENCE = {
    "reference": "ARO:3003394",
    "snippet": (
        "Some mutation within pncA are associated with loss of enzyme activity, "
        "resulting in pyrazinamide resistance."
    ),
    "notes": "CARD child record tying pncA mutation to pyrazinamidase-activity loss.",
}

PYRAZINAMIDE_ACTIVATION_EVIDENCE = {
    "reference": "ARO:3003418",
    "snippet": (
        "pncA is a pyrazinamidase/nicotinamidase. It catalyzes the activation of "
        "pyrazinamide to pyrazinoic acid. Mutations arise within the pncA gene "
        "that caused the loss of pyrazinamidase activity is the major mechanism "
        "of antibiotic resistance."
    ),
    "notes": (
        "CARD child record naming the blocked pyrazinamide-to-pyrazinoic-acid "
        "activation step."
    ),
}

POA_EVIDENCE = {
    "reference": "CHEBI:71311",
    "snippet": "pyrazine-2-carboxylic acid",
    "notes": "ChEBI preferred name for pyrazinoic acid.",
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item["reference"], item.get("snippet", ""))
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
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    source_evidence = _source_evidence(record)
    core_evidence = (
        PNCA_EVIDENCE,
        PNCA_LOSS_EVIDENCE,
        PYRAZINAMIDE_ACTIVATION_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": "pncA mutation → loss of pyrazinamidase activity → pyrazinamide resistance",
        "description": (
            "Curated resistance-causation graph for pyrazinamide resistance caused "
            "by loss of pncA pyrazinamidase activity. The graph models resistance "
            "as the absence of prodrug activation rather than as a new catalytic "
            "activity."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            {
                "node_id": "pzase",
                "label": "pyrazinamidase / nicotinamidase activity",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0008936",
                "description": (
                    "Grounded to the nicotinamidase activity term that matches "
                    "the EC 3.5.1.19 function CARD names for pncA."
                ),
            },
            {
                "node_id": "loss",
                "label": "loss of pyrazinamidase activity",
                "node_type": "STATE",
                "grounding": "GO:0008936",
                "description": (
                    "Local absence state for the grounded pyrazinamidase activity."
                ),
            },
            {
                "node_id": "poa",
                "label": "pyrazinoic acid",
                "node_type": "CHEMICAL",
                "grounding": "CHEBI:71311",
                "description": (
                    "The active pyrazinamide metabolite produced by pncA "
                    "pyrazinamidase activity."
                ),
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
                "description": (
                    "Resistance phenotype conferred by this determinant. Grounded "
                    "to the nearest available superclass: ARO models determinants "
                    "and mechanisms but has no term for the resistance phenotype "
                    "itself."
                ),
            },
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies antibiotic resistant pncA under mutation conferring antibiotic resistance.",
                PNCA_EVIDENCE,
                MUTATION_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "pncA point mutations confer resistance by eliminating pyrazinamide activation.",
                MUTATION_EVIDENCE,
                *core_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "pncA mutation confers pyrazinamide resistance by causing pyrazinamidase-activity loss.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "has quality (loss of pyrazinamidase activity)",
                "RO:0000086",
                "loss",
                "The resistant pncA variant carries the loss of pyrazinamidase activity.",
                *core_evidence,
            ),
            _edge(
                "loss",
                "negatively regulates (abolishes the activating activity)",
                "RO:0002212",
                "pzase",
                "Loss of pyrazinamidase activity removes the enzymatic activity that activates pyrazinamide.",
                PNCA_LOSS_EVIDENCE,
                PYRAZINAMIDE_ACTIVATION_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "pzase",
                "has output (the active form)",
                "RO:0002234",
                "poa",
                "pncA pyrazinamidase activity catalyzes pyrazinamide activation to pyrazinoic acid.",
                PYRAZINAMIDE_ACTIVATION_EVIDENCE,
                POA_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "loss",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Loss of the activating pyrazinamidase activity is the immediate modeled cause of resistance.",
                PNCA_LOSS_EVIDENCE,
                PYRAZINAMIDE_ACTIVATION_EVIDENCE,
                *source_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not pncA: {record.get('identifier')}")
    if path.name != FILENAME:
        raise ValueError(f"{path}: {IDENTIFIER} must be in {FILENAME}")

    enriched, changed = enrich_record(record)
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
    return [path / FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the pncA YAML file",
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
