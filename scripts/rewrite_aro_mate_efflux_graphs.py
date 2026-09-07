#!/usr/bin/env python3
"""Rewrite MATE cation-gradient efflux ARO graphs.

MATE transporters use a cationic gradient as an energy source. The coupling ion
is intentionally left generic because CARD scopes this family to a cationic,
not specifically proton or sodium, gradient.

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

HISTORY_ACTION = "Completed MATE cation-gradient efflux causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

MATE_EVIDENCE = {
    "reference": "ARO:3000112",
    "snippet": (
        "Multidrug and toxic compound extrusion (MATE) transporters utilize "
        "the cationic gradient across the membrane as an energy source."
    ),
    "notes": "CARD definition for MATE transporters.",
}

MATE_SUBSTRATE_EVIDENCE = {
    "reference": "ARO:3000112",
    "snippet": (
        "Although there is a diverse substrate specificity, almost all MATE "
        "transporters recognize fluoroquinolones."
    ),
    "notes": "CARD definition for MATE antibiotic substrates.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

CATION_GRADIENT_NODE = {
    "node_id": "cation_gradient",
    "label": "transmembrane cationic gradient",
    "node_type": "STATE",
    "description": (
        "Local state for the cationic gradient that powers MATE-family drug "
        "antiport. The ion is kept generic because CARD does not specialize "
        "the family to proton or sodium coupling."
    ),
}

EXPORT_NODE = {
    "node_id": "export",
    "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1990961",
}

EXTRUDED_NODE = {
    "node_id": "extruded_drug",
    "label": "drug outside the cell",
    "node_type": "STATE",
    "description": "Local state for drug exported from the cytoplasm by a MATE transporter.",
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
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3000112",
        "multidrug-and-toxic-compound-extrusion-mate-transporter-aro3000112.yaml",
    ),
    Target("ARO:3003551", "emea-aro3003551.yaml"),
    Target("ARO:3003953", "hmrm-aro3003953.yaml"),
    Target("ARO:3003965", "hp1184-aro3003965.yaml"),
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        MATE_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → MATE cation-gradient efflux → resistance",
        "description": (
            "Curated resistance-causation graph for MATE antibiotic efflux "
            "pumps. The determinant uses a generic transmembrane cationic "
            "gradient to export antibiotic from the cell."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(CATION_GRADIENT_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(EXTRUDED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies MATE pumps under the antibiotic efflux "
                "resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting "
                "antibiotics out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "MATE transporters confer resistance by cation-gradient-driven "
                "antibiotic efflux.",
                *efflux_evidence,
            ),
            _edge(
                "cation_gradient",
                "causally upstream of (drives efflux)",
                "RO:0002411",
                "export",
                "A transmembrane cationic gradient powers MATE-family drug "
                "antiport across the membrane.",
                record_evidence,
                MATE_EVIDENCE,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                MATE_SUBSTRATE_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The MATE transporter exports drug from the cell.",
                *efflux_evidence,
            ),
            _edge(
                "export",
                "causally upstream of (moves drug out of the cell)",
                "RO:0002411",
                "extruded_drug",
                "Antibiotic export moves intracellular drug outside the cell.",
                *efflux_evidence,
            ),
            _edge(
                "extruded_drug",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Moving drug outside the cell lowers intracellular drug exposure "
                "and causes the modeled resistance phenotype.",
                *efflux_evidence,
            ),
        ],
    }


REQUIRED_NODE_SETS = (
    {
        "determinant",
        "mech0",
        "extrusion",
        "cation_gradient",
        "extruded",
        "resistance",
    },
    {
        "determinant",
        "mech0",
        "export",
        "cation_gradient",
        "extruded_drug",
        "resistance",
    },
)


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

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_by_shape = [sorted(required - node_ids) for required in REQUIRED_NODE_SETS]
    if all(missing_by_shape):
        missing_nodes = min(missing_by_shape, key=len)
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a MATE efflux target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one of the MATE target YAML files",
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
