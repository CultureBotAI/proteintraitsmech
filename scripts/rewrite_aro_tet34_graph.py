#!/usr/bin/env python3
"""Rewrite the tet(34) purine-synthesis protection graph.

tet(34) inherits tetracycline-inactivation terms in ARO, but its CARD
definition does not assert a tetracycline hydroxylase.  It states that tet(34)
activates Mg2+-dependent purine nucleotide synthesis, which protects the
protein synthesis pathway.  This updater models that stated route directly and
keeps the inherited tetracycline drug-class edge as a CARD relationship.

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
IDENTIFIER = "ARO:3002870"
FILENAME = "tet-34-aro3002870.yaml"

HISTORY_ACTION = "Completed tet(34) purine-synthesis protection graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TET34_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "tet(34) causes the activation of Mg2+-dependent purine nucleotide "
        "synthesis, which protects the protein synthesis pathway. It is found "
        "in Gram-negative Vibrio."
    ),
    "notes": "CARD definition for tet(34).",
}

PURINE_SYNTHESIS_EVIDENCE = {
    "reference": "GO:0006164",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of a "
        "purine nucleotide."
    ),
    "notes": "GO definition for purine nucleotide biosynthetic process.",
}

TRANSLATION_EVIDENCE = {
    "reference": "GO:0006412",
    "snippet": "The cellular metabolic process in which a protein is formed.",
    "notes": "GO definition for translation, used as the grounded protein-synthesis process.",
}

TETRACYCLINE_RELATION_EVIDENCE = {
    "reference": "ARO:3000036",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000050 ! tetracycline antibiotic",
    "notes": (
        "Tetracycline drug-class relation asserted on ARO:3000036 and inherited "
        "by the tet(34) record."
    ),
}

TETRACYCLINE_EVIDENCE = {
    "reference": "ARO:3000050",
    "snippet": "tetracycline antibiotic",
    "notes": "CARD drug-class term inherited by tet(34).",
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
        TET34_EVIDENCE,
        PURINE_SYNTHESIS_EVIDENCE,
        TRANSLATION_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": "tet(34) → purine nucleotide synthesis → protein-synthesis protection",
        "description": (
            "Curated resistance-causation graph for the Mg2+-dependent purine "
            "nucleotide synthesis route named in the tet(34) CARD definition. "
            "The graph deliberately avoids asserting unsupported tetracycline "
            "hydroxylation chemistry."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            {
                "node_id": "drug0",
                "label": "tetracycline antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000050",
            },
            {
                "node_id": "purine_synthesis",
                "label": "Mg2+-dependent purine nucleotide synthesis",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0006164",
                "description": (
                    "Grounded to the broad purine nucleotide biosynthetic process "
                    "because CARD does not provide a narrower Mg2+-dependent term."
                ),
            },
            {
                "node_id": "protected_translation",
                "label": "protected protein synthesis pathway",
                "node_type": "STATE",
                "grounding": "GO:0006412",
                "description": (
                    "Local state representing protection of the protein synthesis "
                    "pathway; grounded to the broad GO translation term."
                ),
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
                "description": (
                    "Resistance phenotype conferred by this determinant. "
                    "Grounded to the nearest available superclass: ARO models "
                    "determinants and mechanisms but has no term for the "
                    "resistance phenotype itself."
                ),
            },
        ],
        "edges": [
            _edge(
                "determinant",
                "positively regulates",
                "RO:0002213",
                "purine_synthesis",
                "CARD states that tet(34) activates Mg2+-dependent purine nucleotide synthesis.",
                *core_evidence,
            ),
            _edge(
                "purine_synthesis",
                "causally upstream of",
                "RO:0002411",
                "protected_translation",
                "CARD links Mg2+-dependent purine nucleotide synthesis to protection of the protein synthesis pathway.",
                *core_evidence,
            ),
            _edge(
                "protected_translation",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The protected protein synthesis pathway is the asserted causal route to resistance.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "tet(34) confers resistance through activation of purine nucleotide synthesis and downstream protection of protein synthesis.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "ARO maps the tet(34) record to tetracycline antibiotic resistance through an inherited drug-class relation.",
                TET34_EVIDENCE,
                TETRACYCLINE_RELATION_EVIDENCE,
                TETRACYCLINE_EVIDENCE,
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
        raise ValueError(f"{path}: not tet(34): {record.get('identifier')}")
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
        help="ARO directory or the tet(34) YAML file",
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
