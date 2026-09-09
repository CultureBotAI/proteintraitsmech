#!/usr/bin/env python3
"""Rewrite remaining Mex RND efflux-subunit graphs.

MexA and MexB are subunits of MexAB-OprM, while MexG is part of the
MexGHI-OpmD efflux system. These records should route through their grounded
CARD pump records instead of an ungrounded local complex placeholder.

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

HISTORY_ACTION = "Completed Mex RND efflux-subunit graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
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

RND_EVIDENCE = {
    "reference": "ARO:0010004",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Resistance-nodulation-division (RND) proteins are found in both "
        "prokaryotic and eukaryotic cells and have diverse substrate "
        "specificities and physiological roles."
    ),
    "notes": "CARD definition for RND antibiotic efflux pumps.",
}

RND_TRANSPORT_EVIDENCE = {
    "reference": "PMID:16915237",
    "snippet": (
        "The structures indicate that drugs are exported by a three-step "
        "functionally rotating mechanism in which substrates undergo ordered "
        "binding change."
    ),
    "notes": "Evidence for RND pump-mediated drug export.",
}

COMPLEX_EVIDENCE = {
    "ARO:3000386": {
        "reference": "ARO:3000386",
        "snippet": (
            "MexAB-OprM is a multidrug efflux protein expressed in the Gram-negative "
            "Pseudomonas aeruginosa. MexA is the membrane fusion protein; MexB is "
            "the inner membrane transporter; and OprM is the outer membrane channel."
        ),
        "notes": "CARD definition for the MexAB-OprM pump.",
    },
    "ARO:3000799": {
        "reference": "ARO:3000799",
        "snippet": (
            "MexGHI-OpmD is an efflux complex expressed in Pseudomonas aeruginosa. "
            "MexG is a membrane protein required for drug export; MexH is the "
            "membrane fusion protein; MexI is the inner membrane transporter; "
            "and MexJ is the outer membrane channel protein."
        ),
        "notes": "CARD definition for the MexGHI-OpmD pump.",
    },
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
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
    complex_id: str
    complex_label: str

    @property
    def complex_evidence(self) -> dict[str, str]:
        return COMPLEX_EVIDENCE[self.complex_id]


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000377", "mexa-aro3000377.yaml", "ARO:3000386", "MexAB-OprM"),
    Target("ARO:3000378", "mexb-aro3000378.yaml", "ARO:3000386", "MexAB-OprM"),
    Target("ARO:3000806", "mexg-aro3000806.yaml", "ARO:3000799", "MexGHI-OpmD"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "BFO:0000050", "pump_complex"),
    ("pump_complex", "RO:0000056", "mech0"),
    ("pump_complex", "RO:0002411", "export"),
    ("export", "RO:0002411", "resistance"),
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


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in evidence:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        unique.append(copy.deepcopy(item))
    return unique


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


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
        "evidence": _unique_evidence(evidence),
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _pump_node(target: Target) -> dict[str, str]:
    return {
        "node_id": "pump_complex",
        "label": f"{target.complex_label} efflux pump",
        "node_type": "PROTEIN",
        "grounding": target.complex_id,
        "description": f"Grounded CARD record for the {target.complex_label} RND efflux pump.",
    }


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    subunit_evidence = (
        record_evidence,
        EFFLUX_SUBUNIT_EVIDENCE,
        target.complex_evidence,
    )
    efflux_evidence = (
        record_evidence,
        target.complex_evidence,
        RND_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        RND_TRANSPORT_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → {target.complex_label} RND efflux → resistance",
        "description": (
            "Curated resistance-causation graph for a Mex RND efflux-pump "
            "subunit. The determinant is modeled as part of the exact grounded "
            "Mex pump that carries out RND antibiotic efflux."
        ),
        "nodes": [
            _determinant_node(record),
            _pump_node(target),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this Mex efflux-pump subunit under the "
                "antibiotic efflux resistance mechanism.",
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
                "The subunit contributes to a Mex RND efflux pump that exports "
                "antibiotics from the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "pump_complex",
                f"{record['label']} is modeled as part of the "
                f"{target.complex_label} efflux pump.",
                *subunit_evidence,
            ),
            _edge(
                "pump_complex",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                f"{target.complex_label} is an RND efflux pump that participates "
                "in antibiotic efflux.",
                *efflux_evidence,
            ),
            _edge(
                "pump_complex",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The complete Mex RND pump exports antibiotic from the cell.",
                *efflux_evidence,
            ),
            _edge(
                "export",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic export lowers intracellular drug exposure and "
                "causes the modeled resistance phenotype.",
                *efflux_evidence,
            ),
        ],
    }


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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }
    expected_nodes = {"determinant", "pump_complex", "mech0", "export", "resistance"}
    missing_nodes = sorted(expected_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            subject, _, object_ = key
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            subject, _, object_ = key
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"][0])
    out["causal_graphs"] = [_canonical_graph(record, target)]
    _validate_graph(out["causal_graphs"][0], target)
    return out, out["causal_graphs"][0] != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a remaining Mex subunit target: {identifier}")
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
        help="ARO directory or one of the remaining Mex subunit YAML files",
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
