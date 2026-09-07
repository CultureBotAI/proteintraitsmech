#!/usr/bin/env python3
"""Rewrite secondary-transporter efflux subunit ARO graphs.

These records are subunits of MFS-family secondary-transporter efflux systems.
They are not complete MFS pumps with a grounded domain/fold node, and they are
not RND subunits with a tripartite RND complex. The graph therefore keeps a
described local transporter state and links the subunit to antibiotic export.

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

HISTORY_ACTION = "Completed secondary-transporter efflux subunit causal graphs"
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

EFFLUX_SUBUNIT_EVIDENCE = {
    "reference": "ARO:3000748",
    "snippet": "Subunits of efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump subunits.",
}

SECONDARY_TRANSPORT_EVIDENCE = {
    "reference": "PMID:16675700",
    "snippet": (
        "EmrD is a multidrug transporter from the Major Facilitator Superfamily "
        "that expels amphipathic compounds across the inner membrane of "
        "Escherichia coli."
    ),
    "notes": "Evidence for secondary-transporter multidrug efflux.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

TRANSPORTER_NODE = {
    "node_id": "transporter",
    "label": "secondary-transporter efflux system",
    "node_type": "STATE",
    "description": (
        "Local state for an electrochemical-gradient-driven efflux system "
        "containing this efflux-pump subunit."
    ),
}

EXPORT_NODE = {
    "node_id": "export",
    "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1990961",
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
    Target("ARO:3000027", "emra-aro3000027.yaml"),
    Target("ARO:3000074", "emrb-aro3000074.yaml"),
    Target("ARO:3000206", "emrk-aro3000206.yaml"),
    Target("ARO:3000254", "emry-aro3000254.yaml"),
    Target("ARO:3003961", "fara-aro3003961.yaml"),
    Target("ARO:3003962", "farb-aro3003962.yaml"),
    Target("ARO:3003548", "mdtn-aro3003548.yaml"),
    Target("ARO:3003549", "mdto-aro3003549.yaml"),
    Target("ARO:3003550", "mdtp-aro3003550.yaml"),
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
        EFFLUX_SUBUNIT_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        SECONDARY_TRANSPORT_EVIDENCE,
    )
    subunit_evidence = (
        record_evidence,
        EFFLUX_SUBUNIT_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → secondary-transporter efflux → resistance",
        "description": (
            "Curated resistance-causation graph for secondary-transporter "
            "efflux-pump subunits. The determinant is modeled as part of a "
            "local efflux system that exports antibiotics from the cell."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(TRANSPORTER_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this efflux-pump subunit under the antibiotic "
                "efflux resistance mechanism.",
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
                "The subunit contributes to a secondary-transporter efflux "
                "system that pumps antibiotic out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "transporter",
                "The determinant is a subunit of the modeled "
                "secondary-transporter efflux system.",
                *subunit_evidence,
            ),
            _edge(
                "transporter",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The complete efflux system exports antibiotics from the cell.",
                *efflux_evidence,
            ),
            _edge(
                "export",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic export lowers intracellular drug exposure and "
                "causes the modeled resistance phenotype.",
                EFFLUX_SUBUNIT_EVIDENCE,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                SECONDARY_TRANSPORT_EVIDENCE,
            ),
        ],
    }


REQUIRED_NODES = {"determinant", "mech0", "transporter", "export", "resistance"}


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
    missing_nodes = sorted(REQUIRED_NODES - node_ids)
    if missing_nodes:
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
        raise ValueError(f"{path}: not a secondary efflux subunit target: {identifier}")
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
        help="ARO directory or one of the secondary efflux subunit target YAML files",
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
