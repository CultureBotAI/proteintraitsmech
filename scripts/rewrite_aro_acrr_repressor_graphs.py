#!/usr/bin/env python3
"""Ground and complete AcrR loss-of-repression ARO causal graphs.

The four records handled here share the CARD AcrR mechanism: AcrR represses the
AcrAB-TolC multidrug efflux complex, and acrR mutations raise pump expression
and cause resistance. This updater grounds the AcrAB-TolC and repressor-process
nodes, removes the obsolete wild-type AcrR-to-repression role edge from the
mutant causal path, adds the missing pump-to-efflux edge, and describes every
remaining edge.

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
HISTORY_EVENT = {
    "timestamp": "2026-09-05T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Grounded AcrR derepression graphs, removed the obsolete wild-type repressor "
        "edge, and linked AcrAB-TolC to antibiotic efflux"
    ),
    "llm_assisted": True,
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": (
        "GO definition for the broad transcriptional repression process used for "
        "AcrR-mediated repression of AcrAB-TolC expression."
    ),
}

ACRAB_TOLC_EVIDENCE = {
    "reference": "ARO:3000384",
    "snippet": (
        "AcrAB-TolC is a tripartite RND efflux system that confers resistance to "
        "tetracycline, chloramphenicol, ampicillin, nalidixic acid, and rifampin in "
        "Gram-negative bacteria."
    ),
    "notes": (
        "CARD's AcrAB-TolC definition identifies the efflux pump derepressed by AcrR "
        "mutations and states its resistance role."
    ),
}

SPECIFIC_ACRR_EVIDENCE = {
    "ARO:3003373": {
        "reference": "ARO:3003373",
        "snippet": (
            "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR "
            "mutations result in high level antibiotic resistance."
        ),
        "notes": "CARD definition of this Klebsiella pneumoniae acrR mutant class.",
    },
    "ARO:3003374": {
        "reference": "ARO:3003374",
        "snippet": (
            "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR "
            "mutations result in high level antibiotic resistance."
        ),
        "notes": "CARD definition of this Enterobacter aerogenes acrR mutant class.",
    },
    "ARO:3003807": {
        "reference": "ARO:3003807",
        "snippet": (
            "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR "
            "mutations result in high level antibiotic resistance. The mutations "
            "associated with this model are specific to E. coli."
        ),
        "notes": "CARD definition of this Escherichia coli acrR mutant model.",
    },
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "AcrAB-TolC multidrug efflux complex",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000384",
    "description": (
        "Grounded to CARD's AcrAB-TolC tripartite RND efflux system, the pump complex "
        "repressed by AcrR."
    ),
}

REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of AcrAB-TolC transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional repression process "
        "because AcrR represses AcrAB-TolC expression."
    ),
}

OBSOLETE_EDGE = ("determinant", "RO:0002327", "repression")

PUMP_EFFLUX_EDGE = {
    "subject": "pump",
    "predicate": "enables (drug efflux)",
    "predicate_id": "RO:0002327",
    "object": "mech0",
}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies AcrR mutant determinants under antibiotic efflux because loss "
        "of AcrR repression raises AcrAB-TolC expression."
    ),
    ("mech0", "resistance"): (
        "The broad efflux mechanism represents increased AcrAB-TolC activity lowering "
        "intracellular antibiotic exposure."
    ),
    ("determinant", "mech1"): (
        "CARD also classifies AcrR mutant determinants under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech1", "resistance"): (
        "The inherited mutation mechanism links loss-of-repressor variants to the "
        "resistance phenotype."
    ),
    ("determinant", "resistance"): (
        "Mutant AcrR reduces repression of AcrAB-TolC, increasing efflux-pump "
        "expression and causing high-level antibiotic resistance."
    ),
    ("repression", "pump"): (
        "Normal AcrR-dependent transcriptional repression keeps AcrAB-TolC expression "
        "low."
    ),
    ("determinant", "repression"): (
        "Resistance-conferring acrR mutations are represented as loss of the normal "
        "AcrR repression of AcrAB-TolC."
    ),
    ("pump", "mech0"): (
        "AcrAB-TolC is the RND efflux system whose derepressed expression supplies "
        "antibiotic efflux."
    ),
}

EXPECTED_EDGES = set(EDGE_DESCRIPTIONS)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    "ARO:3000702": Target(
        identifier="ARO:3000702",
        filename="acrr-aro3000702.yaml",
    ),
    "ARO:3003373": Target(
        identifier="ARO:3003373",
        filename="klebsiella-pneumoniae-acrr-with-mutation-conferring-multidrug-antibiotic-resista-aro3003373.yaml",
    ),
    "ARO:3003374": Target(
        identifier="ARO:3003374",
        filename="enterobacter-aerogenes-acrr-with-mutation-conferring-multidrug-antibiotic-resist-aro3003374.yaml",
    ),
    "ARO:3003807": Target(
        identifier="ARO:3003807",
        filename="escherichia-coli-acrab-tolc-with-acrr-mutation-conferring-resistance-to-ciproflo-aro3003807.yaml",
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


def _full_edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return edge.get("subject", ""), edge.get("predicate_id", ""), edge.get("object", "")


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _extend_evidence(
    evidence: list[dict[str, Any]], extra: list[dict[str, str]]
) -> list[dict[str, Any]]:
    extra_references = {item["reference"] for item in extra}
    out = [
        copy.deepcopy(item)
        for item in evidence
        if item.get("reference") not in extra_references
    ]
    out.extend(copy.deepcopy(item) for item in extra)
    return out


def _extra_evidence(target: Target, edge_key: tuple[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    if edge_key in {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("repression", "pump"),
        ("pump", "mech0"),
    }:
        evidence.append(ACRAB_TOLC_EVIDENCE)
    if edge_key in {
        ("determinant", "repression"),
        ("repression", "pump"),
    }:
        evidence.append(GO_NEGATIVE_TRANSCRIPTION_EVIDENCE)
    if target.identifier in SPECIFIC_ACRR_EVIDENCE:
        evidence.append(SPECIFIC_ACRR_EVIDENCE[target.identifier])
    return evidence


def _enrich_shared_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id == "pump":
            nodes[index] = copy.deepcopy(PUMP_NODE)
            found.add(node_id)
        elif node_id == "repression":
            nodes[index] = copy.deepcopy(REPRESSION_NODE)
            found.add(node_id)

    missing = sorted({"pump", "repression"} - found)
    if missing:
        missing_ids = ", ".join(missing)
        msg = f"{target.identifier}: missing node(s): {missing_ids}"
        raise ValueError(msg)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{target.identifier}: missing resistance causal graph"
        raise ValueError(msg)

    _enrich_shared_nodes(graph, target)

    edges = graph.setdefault("edges", [])
    if not any(_edge_key(edge) == ("pump", "mech0") for edge in edges):
        edges.append(copy.deepcopy(PUMP_EFFLUX_EDGE))

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in edges:
        if _full_edge_key(edge) == OBSOLETE_EDGE:
            continue

        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_EDGES:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)

        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _extend_evidence(
            edge.get("evidence") or [],
            _extra_evidence(target, key),
        )
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(EXPECTED_EDGES - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    graph["edges"] = enriched_edges
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an AcrR repressor target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
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
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the four AcrR target YAML files",
    )
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
