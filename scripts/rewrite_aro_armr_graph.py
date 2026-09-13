#!/usr/bin/env python3
"""Ground and connect the ArmR antirepression causal graph.

ArmR inhibits MexR dimer-DNA binding and upregulates MexAB-OprM.  This updater
keeps that antirepressor shape explicit, grounds the broad MexR-DNA-binding and
MexAB-OprM-expression nodes, and links pump expression to the broad ARO
antibiotic-efflux mechanism.

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
IDENTIFIER = "ARO:3004056"
FILENAME = "armr-aro3004056.yaml"

HISTORY_ACTION = "Completed ArmR antirepression efflux graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ARMR_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "ArmR, a 53-amino-acid antirepressor, allosterically inhibits MexR "
        "dimer-DNA binding by occupying a hydrophobic binding cavity within the "
        "center of the MexR dimer. ArmR up-regulation and MexR-ArmR complex "
        "formation have previously been shown to upregulate MexAB-OprM."
    ),
    "notes": "CARD definition for ArmR.",
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the broad antibiotic-efflux mechanism.",
}

GO_DNA_BINDING_EVIDENCE = {
    "reference": "GO:0003677",
    "snippet": "Binding to DNA.",
    "notes": "GO definition for the broad DNA-binding function used to ground MexR-DNA binding.",
}

GO_GENE_EXPRESSION_EVIDENCE = {
    "reference": "GO:0010467",
    "snippet": (
        "Gene expression is the process in which a gene's coding sequence is "
        "converted into a mature gene product or products."
    ),
    "notes": "GO definition for the broad gene-expression process used to ground MexAB-OprM expression.",
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
        ARMR_EVIDENCE,
        EFFLUX_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": "ArmR antirepression → MexAB-OprM expression → antibiotic efflux",
        "description": (
            "Curated resistance-causation graph for ArmR antirepression. ArmR "
            "blocks MexR dimer-DNA binding and increases MexAB-OprM expression; "
            "the graph preserves those events instead of collapsing the double "
            "negative into generic pump activation."
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
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
            },
            {
                "node_id": "mexr_dna_binding",
                "label": "MexR dimer binding to DNA",
                "node_type": "STATE",
                "grounding": "GO:0003677",
                "description": (
                    "Local state for MexR dimer-DNA binding, grounded to broad "
                    "GO DNA binding."
                ),
            },
            {
                "node_id": "pump_expression",
                "label": "MexAB-OprM expression",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0010467",
                "description": (
                    "Grounded to broad GO gene expression because CARD names the "
                    "MexAB-OprM pump but does not provide a pump-specific "
                    "expression term."
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
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies ArmR under antibiotic efflux through its upregulation of MexAB-OprM.",
                *core_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The upregulated MexAB-OprM pump acts through antibiotic efflux to cause resistance.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ArmR increases antibiotic efflux by blocking the MexR repressor and upregulating MexAB-OprM.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates (allosterically blocks MexR-DNA binding)",
                "RO:0002212",
                "mexr_dna_binding",
                "ArmR allosterically inhibits MexR dimer-DNA binding by occupying the MexR dimer cavity.",
                ARMR_EVIDENCE,
                GO_DNA_BINDING_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "determinant",
                "positively regulates (upregulates MexAB-OprM)",
                "RO:0002213",
                "pump_expression",
                "ArmR upregulation and MexR-ArmR complex formation upregulate MexAB-OprM expression.",
                ARMR_EVIDENCE,
                GO_GENE_EXPRESSION_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "pump_expression",
                "positively regulates (increases efflux)",
                "RO:0002213",
                "mech0",
                "Higher MexAB-OprM expression is causally upstream of the antibiotic-efflux mechanism.",
                *core_evidence,
                GO_GENE_EXPRESSION_EVIDENCE,
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
        raise ValueError(f"{path}: not ArmR: {record.get('identifier')}")
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
        help="ARO directory or the ArmR YAML file",
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
