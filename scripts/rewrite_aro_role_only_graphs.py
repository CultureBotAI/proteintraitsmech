#!/usr/bin/env python3
"""Ground and describe intentionally shallow role-only ARO causal graphs.

The three records handled here are CARD parent classes whose definitions name a
protein role and a broad resistance class, but do not support a concrete
drug-action mechanism. This updater keeps those graphs shallow, adds exact local
GO groundings for the biological roles, and makes each edge description explicit
about what is and is not asserted.

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
HISTORY_ACTION = "Supplemented role-only pgsA mutation evidence"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_MECHANISM_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

GO_PGP_SYNTHASE_EVIDENCE = {
    "reference": "GO:0008444",
    "snippet": (
        "Catalysis of the reaction: sn-glycerol 3-phosphate + CDP-diacylglycerol = "
        "3-(3-sn-phosphatidyl)-sn-glycerol 1-phosphate + CMP + H+."
    ),
    "notes": "GO reaction definition for the grounded pgsA transferase activity node.",
}

GO_PHOSPHOLIPID_EVIDENCE = {
    "reference": "GO:0008654",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of a "
        "phospholipid, a lipid containing phosphoric acid as a mono- or diester."
    ),
    "notes": "GO process definition for the grounded phospholipid biosynthetic process node.",
}

GO_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0006351",
    "snippet": "The synthesis of an RNA transcript from a DNA template.",
    "notes": "GO process definition for the grounded transcription node.",
}

PGSA_NODES = {
    "pgp_synthase": {
        "node_id": "pgp_synthase",
        "label": "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008444",
        "description": (
            "Grounded to the GO molecular-function class whose synonyms include "
            "phosphatidylglycerophosphate synthase activity."
        ),
    },
    "phospholipid": {
        "node_id": "phospholipid",
        "label": "phospholipid biosynthetic process",
        "node_type": "BIOLOGICAL_PROCESS",
        "grounding": "GO:0008654",
        "description": (
            "Grounded to the GO pathway class for formation of phospholipids; "
            "phospholipid biosynthesis is an exact GO synonym."
        ),
    },
}

RNA_TRANSCRIPTION_NODE = {
    "node_id": "transcription",
    "label": "DNA-templated transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006351",
    "description": (
        "Grounded to the GO DNA-templated transcription process named generically in "
        "the ARO RNA-polymerase parent definition."
    ),
}

ACTIVE_CENTER_NODES = {
    "ARO:3003276": {
        "node_id": "active_center",
        "label": "RNA polymerase active center and template/transcript binding sites",
        "node_type": "PROTEIN",
        "description": (
            "Structural RNA-polymerase region formed by the beta subunit in this ARO "
            "parent record; left label-only because the local corpus lacks a precise "
            "class for the active center plus template/transcript-binding sites."
        ),
    },
    "ARO:3003289": {
        "node_id": "active_center",
        "label": "RNA polymerase active center and template/transcript binding sites",
        "node_type": "PROTEIN",
        "description": (
            "Structural RNA-polymerase region formed by the beta prime subunit in this "
            "ARO parent record; left label-only because the local corpus lacks a precise "
            "class for the active center plus template/transcript-binding sites."
        ),
    },
}

PGSA_EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "The ARO hierarchy classifies antibiotic resistant pgsA under mutation "
        "conferring antibiotic resistance, while this parent record only identifies the "
        "enzyme and pathway roles."
    ),
    ("mech0", "resistance"): (
        "The inherited mutation mechanism links the parent determinant class to the "
        "resistance phenotype without specifying a drug-specific biochemical route."
    ),
    ("determinant", "resistance"): (
        "The ARO parent class records pgsA as antibiotic resistant; no drug-specific "
        "edge is asserted from its enzyme annotation alone."
    ),
    ("determinant", "pgp_synthase"): (
        "The ARO definition identifies pgsA as a "
        "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase."
    ),
    ("pgp_synthase", "phospholipid"): (
        "The transferase activity is represented as part of the phospholipid "
        "biosynthesis role named in the ARO definition."
    ),
}

RPOB_EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "The ARO hierarchy classifies antibiotic resistant rpoB under mutation "
        "conferring antibiotic resistance, while this parent record does not name a "
        "specific mutation or drug."
    ),
    ("mech0", "resistance"): (
        "The inherited mutation mechanism links the parent rpoB determinant class to "
        "the resistance phenotype without specifying a drug-binding or transcriptional "
        "failure route."
    ),
    ("determinant", "resistance"): (
        "The ARO definition states that mutations in rpoB can confer antibiotic "
        "resistance, but does not resolve the resistant drug class or molecular change."
    ),
    ("determinant", "active_center"): (
        "The ARO definition describes the RNA-polymerase beta subunit as forming the "
        "enzyme active center and template/transcript-binding sites."
    ),
    ("active_center", "transcription"): (
        "The active-center role remains label-only and is linked only to the "
        "GO-grounded transcription process that the ARO definition names."
    ),
}

RPOC_EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "The ARO hierarchy classifies antibiotic resistant rpoC under mutation "
        "conferring antibiotic resistance, while this parent record does not name a "
        "specific mutation or drug."
    ),
    ("mech0", "resistance"): (
        "The inherited mutation mechanism links the parent rpoC determinant class to "
        "the resistance phenotype without specifying a drug-binding or transcriptional "
        "failure route."
    ),
    ("determinant", "resistance"): (
        "The ARO definition states that mutations in rpoC can confer antibiotic "
        "resistance, but does not resolve the resistant drug class or molecular change."
    ),
    ("determinant", "active_center"): (
        "The ARO definition describes the RNA-polymerase beta prime subunit as forming "
        "the enzyme active center and template/transcript-binding sites."
    ),
    ("active_center", "transcription"): (
        "The active-center role remains label-only and is linked only to the "
        "GO-grounded transcription process that the ARO definition names."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    node_updates: dict[str, dict[str, str]]
    edge_descriptions: dict[tuple[str, str], str]
    extra_evidence: dict[tuple[str, str], list[dict[str, str]]]


TARGETS = {
    "ARO:3003420": Target(
        identifier="ARO:3003420",
        filename="antibiotic-resistant-pgsa-aro3003420.yaml",
        node_updates=PGSA_NODES,
        edge_descriptions=PGSA_EDGE_DESCRIPTIONS,
        extra_evidence={
            ("determinant", "mech0"): [MUTATION_MECHANISM_EVIDENCE],
            ("mech0", "resistance"): [MUTATION_MECHANISM_EVIDENCE],
            ("determinant", "resistance"): [MUTATION_MECHANISM_EVIDENCE],
            ("determinant", "pgp_synthase"): [GO_PGP_SYNTHASE_EVIDENCE],
            ("pgp_synthase", "phospholipid"): [GO_PHOSPHOLIPID_EVIDENCE],
        },
    ),
    "ARO:3003276": Target(
        identifier="ARO:3003276",
        filename="antibiotic-resistant-rpob-aro3003276.yaml",
        node_updates={
            "transcription": RNA_TRANSCRIPTION_NODE,
            "active_center": ACTIVE_CENTER_NODES["ARO:3003276"],
        },
        edge_descriptions=RPOB_EDGE_DESCRIPTIONS,
        extra_evidence={
            ("active_center", "transcription"): [GO_TRANSCRIPTION_EVIDENCE],
        },
    ),
    "ARO:3003289": Target(
        identifier="ARO:3003289",
        filename="antibiotic-resistant-rpoc-aro3003289.yaml",
        node_updates={
            "transcription": RNA_TRANSCRIPTION_NODE,
            "active_center": ACTIVE_CENTER_NODES["ARO:3003289"],
        },
        edge_descriptions=RPOC_EDGE_DESCRIPTIONS,
        extra_evidence={
            ("active_center", "transcription"): [GO_TRANSCRIPTION_EVIDENCE],
        },
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


def _aro_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    return {
        "reference": target.identifier,
        "snippet": record["definition"],
        "notes": "Exact ARO definition of this role-only parent determinant.",
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


def _evidence_for_edge(
    edge: dict[str, Any],
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, str]]:
    evidence = [_aro_evidence(record, target)]
    evidence.extend(copy.deepcopy(target.extra_evidence.get(_edge_key(edge), [])))
    return evidence


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


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id not in target.node_updates:
            continue
        nodes[index] = copy.deepcopy(target.node_updates[node_id])
        found.add(node_id)

    missing = sorted(set(target.node_updates) - found)
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

    _enrich_nodes(graph, target)

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in target.edge_descriptions:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        edge["description"] = target.edge_descriptions[key]
        edge["evidence"] = _evidence_for_edge(edge, out, target)
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(set(target.edge_descriptions) - seen)
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
        raise ValueError(f"{path}: not a role-only pgsA/rpoB/rpoC target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = record.get("curation_history") or []
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
        help="ARO directory or one of the three target YAML files",
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
