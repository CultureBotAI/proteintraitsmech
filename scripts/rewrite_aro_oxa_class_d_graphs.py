#!/usr/bin/env python3
"""Describe and evidence OXA class D beta-lactamase graphs.

These OXA leaves already carry the class D inactivation skeleton plus grounded
PROSITE class-D active-site and CATH fold nodes. Their edges are
single-evidenced and lack descriptions. This updater rewrites a bounded exact
set of low-scoring OXA leaves with multi-evidenced, described edges.

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

HISTORY_ACTION = "Completed OXA class D beta-lactamase causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CLASS_D_EVIDENCE = {
    "reference": "ARO:3000075",
    "snippet": (
        "Class D beta-lactamases are one of the subgroups of "
        "beta-lactamases that are classified as serine enzymes."
    ),
    "notes": "CARD definition for the class D beta-lactamase parent term.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the inherited antibiotic inactivation mechanism.",
}

SERINE_HYDROLYSIS_EVIDENCE = {
    "reference": "ARO:3000187",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class A, C and D "
        "beta-lactamases. A serine residue located in the active site is used "
        "to form an acyl-enzyme intermediate and subsequent hydrolysis renders "
        "the beta-lactam inactive."
    ),
    "notes": "CARD definition for serine beta-lactamase hydrolysis.",
}

PROSITE_SERINE_HYDROLASE_EVIDENCE = {
    "reference": "PROSITE:PS00337",
    "snippet": (
        "Class-B enzymes are zinc containing proteins whilst class -A, C and D "
        "enzymes are serine hydrolases."
    ),
    "notes": "PROSITE assigns Ambler class D beta-lactamases to the serine hydrolases.",
}

PROSITE_CLASS_D_ACTIVE_SITE_EVIDENCE = {
    "reference": "PROSITE:PRU10103",
    "snippet": "Beta-lactamase class-D active site",
    "notes": "PROSITE class-D beta-lactamase active-site profile.",
}

CATH_FOLD_EVIDENCE = {
    "reference": "CATH:3.40.710.10",
    "snippet": "DD-peptidase/beta-lactamase superfamily",
    "notes": "CATH superfamily for serine beta-lactamases.",
}

CARBAMYLATED_LYSINE_EVIDENCE = {
    "reference": "PMID:16121396",
    "snippet": (
        "carboxylated lysines in the active sites of OXA-10 and OXA-1 "
        "beta-lactamases and the sensor domain of BlaR signal-transducer "
        "protein serve in proton transfer events required for the functions "
        "of these proteins"
    ),
    "notes": "Evidence for the class D active-site lysine used in OXA catalysis.",
}

BROAD_INACTIVATION_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

SERINE_HYDROLYSIS_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000187",
}

ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "class D beta-lactamase active site",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PRU10103",
    "description": (
        "Grounded to the PROSITE class D beta-lactamase active-site profile "
        "for the catalytic site that carries the serine beta-lactamase "
        "mechanism."
    ),
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "DD-peptidase/beta-lactamase superfamily fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.710.10",
    "description": "CATH superfamily containing serine beta-lactamase folds.",
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

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies this OXA class D beta-lactamase under antibiotic "
        "inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Serine beta-lactam hydrolysis enzymatically inactivates "
        "beta-lactam antibiotics, reaching the inherited antibiotic "
        "inactivation mechanism."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO classifies this OXA class D beta-lactamase under serine "
        "beta-lactam hydrolysis."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Hydrolysis renders the beta-lactam inactive and produces the "
        "resistance phenotype."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "This OXA determinant inherits the class D serine beta-lactamase "
        "mechanism that inactivates beta-lactam antibiotics."
    ),
    ("active_site", "BFO:0000050", "determinant"): (
        "The PROSITE PRU10103 class-D active-site profile is part of OXA "
        "class D beta-lactamases."
    ),
    ("determinant", "RO:0002350", "fold"): (
        "The OXA determinant adopts the DD-peptidase/beta-lactamase "
        "superfamily fold used by serine beta-lactamases."
    ),
    ("active_site", "RO:0002327", "mech1"): (
        "The class D beta-lactamase active site supplies catalytic residues "
        "for the serine beta-lactam hydrolysis mechanism."
    ),
}
EXPECTED_EDGE_KEYS = set(EDGE_DESCRIPTIONS)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3008427", "oxa-1006-aro3008427.yaml"),
    Target("ARO:3008432", "oxa-1011-aro3008432.yaml"),
    Target("ARO:3001706", "oxa-102-aro3001706.yaml"),
    Target("ARO:3008457", "oxa-1036-aro3008457.yaml"),
    Target("ARO:3008458", "oxa-1037-aro3008458.yaml"),
    Target("ARO:3008460", "oxa-1041-aro3008460.yaml"),
    Target("ARO:3008462", "oxa-1043-aro3008462.yaml"),
    Target("ARO:3001708", "oxa-105-aro3001708.yaml"),
    Target("ARO:3008507", "oxa-1089-aro3008507.yaml"),
    Target("ARO:3008508", "oxa-1090-aro3008508.yaml"),
    Target("ARO:3008509", "oxa-1091-aro3008509.yaml"),
    Target("ARO:3008526", "oxa-1108-aro3008526.yaml"),
    Target("ARO:3008560", "oxa-1142-aro3008560.yaml"),
    Target("ARO:3008561", "oxa-1143-aro3008561.yaml"),
    Target("ARO:3008571", "oxa-1153-aro3008571.yaml"),
    Target("ARO:3008572", "oxa-1154-aro3008572.yaml"),
    Target("ARO:3008573", "oxa-1155-aro3008573.yaml"),
    Target("ARO:3008574", "oxa-1156-aro3008574.yaml"),
    Target("ARO:3008576", "oxa-1158-aro3008576.yaml"),
    Target("ARO:3008577", "oxa-1159-aro3008577.yaml"),
    Target("ARO:3001441", "oxa-116-aro3001441.yaml"),
    Target("ARO:3008578", "oxa-1160-aro3008578.yaml"),
    Target("ARO:3008579", "oxa-1161-aro3008579.yaml"),
    Target("ARO:3008581", "oxa-1163-aro3008581.yaml"),
    Target("ARO:3008618", "oxa-1206-aro3008618.yaml"),
    Target("ARO:3008648", "oxa-1238-aro3008648.yaml"),
    Target("ARO:3008649", "oxa-1239-aro3008649.yaml"),
    Target("ARO:3008661", "oxa-1251-aro3008661.yaml"),
    Target("ARO:3008668", "oxa-1258-aro3008668.yaml"),
    Target("ARO:3008669", "oxa-1259-aro3008669.yaml"),
    Target("ARO:3008670", "oxa-1260-aro3008670.yaml"),
    Target("ARO:3008671", "oxa-1261-aro3008671.yaml"),
    Target("ARO:3001452", "oxa-140-aro3001452.yaml"),
    Target("ARO:3001411", "oxa-16-aro3001411.yaml"),
    Target("ARO:3001413", "oxa-18-aro3001413.yaml"),
    Target("ARO:3001697", "oxa-187-aro3001697.yaml"),
    Target("ARO:3001698", "oxa-188-aro3001698.yaml"),
    Target("ARO:3001699", "oxa-189-aro3001699.yaml"),
    Target("ARO:3001700", "oxa-190-aro3001700.yaml"),
    Target("ARO:3001701", "oxa-191-aro3001701.yaml"),
    Target("ARO:3001415", "oxa-20-aro3001415.yaml"),
    Target("ARO:3001809", "oxa-209-aro3001809.yaml"),
    Target("ARO:3001490", "oxa-220-aro3001490.yaml"),
    Target("ARO:3001491", "oxa-221-aro3001491.yaml"),
    Target("ARO:3001492", "oxa-222-aro3001492.yaml"),
    Target("ARO:3001494", "oxa-227-aro3001494.yaml"),
    Target("ARO:3001497", "oxa-238-aro3001497.yaml"),
    Target("ARO:3001610", "oxa-243-aro3001610.yaml"),
    Target("ARO:3001503", "oxa-258-aro3001503.yaml"),
    Target("ARO:3001734", "oxa-279-aro3001734.yaml"),
    Target("ARO:3001744", "oxa-289-aro3001744.yaml"),
    Target("ARO:3001424", "oxa-29-aro3001424.yaml"),
    Target("ARO:3001745", "oxa-290-aro3001745.yaml"),
    Target("ARO:3001751", "oxa-296-aro3001751.yaml"),
    Target("ARO:3001754", "oxa-299-aro3001754.yaml"),
    Target("ARO:3001763", "oxa-308-aro3001763.yaml"),
    Target("ARO:3001505", "oxa-310-aro3001505.yaml"),
    Target("ARO:3001506", "oxa-311-aro3001506.yaml"),
    Target("ARO:3001507", "oxa-318-aro3001507.yaml"),
    Target("ARO:3001508", "oxa-319-aro3001508.yaml"),
    Target("ARO:3001509", "oxa-321-aro3001509.yaml"),
    Target("ARO:3001427", "oxa-33-aro3001427.yaml"),
    Target("ARO:3001428", "oxa-34-aro3001428.yaml"),
    Target("ARO:3001777", "oxa-347-aro3001777.yaml"),
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
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


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(*evidence),
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {
        "determinant",
        "mech0",
        "mech1",
        "active_site",
        "fold",
        "resistance",
    }
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found_edges: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    broad_evidence = (
        record_evidence,
        CLASS_D_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        SERINE_HYDROLYSIS_EVIDENCE,
        PROSITE_SERINE_HYDROLASE_EVIDENCE,
    )
    active_site_evidence = (
        record_evidence,
        CLASS_D_EVIDENCE,
        SERINE_HYDROLYSIS_EVIDENCE,
        PROSITE_CLASS_D_ACTIVE_SITE_EVIDENCE,
        CARBAMYLATED_LYSINE_EVIDENCE,
    )
    fold_evidence = (
        record_evidence,
        CLASS_D_EVIDENCE,
        CATH_FOLD_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → class D beta-lactam hydrolysis → resistance",
        "description": (
            "Conservative OXA class D beta-lactamase graph. The graph "
            "grounds the inherited antibiotic-inactivation and serine "
            "beta-lactamase mechanisms to ARO, the class D active site to "
            "PROSITE:PRU10103, and the DD-peptidase/beta-lactamase fold to "
            "CATH:3.40.710.10."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(BROAD_INACTIVATION_NODE),
            copy.deepcopy(SERINE_HYDROLYSIS_NODE),
            copy.deepcopy(ACTIVE_SITE_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                *broad_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                *broad_evidence,
            ),
            _edge(
                "active_site",
                "part of",
                "BFO:0000050",
                "determinant",
                *active_site_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                *fold_evidence,
            ),
            _edge(
                "active_site",
                "enables",
                "RO:0002327",
                "mech1",
                *active_site_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
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
        raise ValueError(f"{path}: not an OXA class D target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = _dicts(enriched.get("curation_history"))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
        help="ARO directory or one of the OXA class D beta-lactamase YAML files",
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
