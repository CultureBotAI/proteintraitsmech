#!/usr/bin/env python3
"""Curate FabG triclosan-resistance mutation graphs.

The FabG records state that FabG is a 3-oxoacyl-ACP reductase, that
Triclosan blocks the final reduction step in fatty-acid elongation, and that
fabG point mutations can confer Triclosan resistance.  This updater rewrites
the two seeded drafts to the same conservative target-alteration shape used by
FabI while grounding the FabG reductase step to GO:0004316 and NCBIfam's FabG
family.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Curated FabG triclosan-resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004284"
PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "fabG is a 3-oxoacyl-acyl carrier protein reductase involved in "
        "lipid metabolism and fatty acid biosynthesis. The bacterial biocide "
        "Triclosan blocks the final reduction step in fatty acid elongation, "
        "inhibiting biosynthesis. Point mutations in fabG can confer "
        "resistance to Triclosan."
    ),
    "notes": "CARD definition for the antibiotic-resistant FabG parent.",
}
MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}
GO_FABG_EVIDENCE = {
    "reference": "GO:0004316",
    "snippet": (
        "Catalysis of the reaction: (3R)-3-hydroxyacyl-[acyl-carrier "
        "protein] + NADP+ = 3-oxoacyl-[acyl-carrier protein] + NADPH + H+."
    ),
    "notes": "GO 3-oxoacyl-[acyl-carrier-protein] reductase activity term.",
}
NCBIFAM_FABG_EVIDENCE = {
    "reference": "NCBIfam:NF004197",
    "snippet": (
        "3-oxoacyl-ACP reductase FabG — a functionally conserved protein "
        "family grouped by the NCBIfam full-length profile-HMM NF004197 "
        "(equivalog); catalyses 3-oxoacyl-[acyl-carrier-protein] reductase."
    ),
    "notes": "Local NCBIfam FabG-family record mapped to GO:0004316.",
}
DISINFECTANT_EVIDENCE = {
    "reference": "ARO:3005386",
    "snippet": "disinfecting agents and antiseptics",
    "notes": "ARO drug-class term inherited by FabG records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}
DISINFECTANT_NODE = {
    "node_id": "drug0",
    "label": "disinfecting agents and antiseptics",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3005386",
}
FABG_REDUCTION_NODE = {
    "node_id": "fabg_reduction",
    "label": "3-oxoacyl-[acyl-carrier-protein] reductase (NADPH) activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004316",
    "description": "NADPH-dependent 3-oxoacyl-ACP reductase activity enabled by FabG.",
}
INHIBITION_NODE = {
    "node_id": "inhibition",
    "label": "Triclosan inhibition of FabG 3-oxoacyl-ACP reduction",
    "node_type": "STATE",
    "description": (
        "Local state for Triclosan blocking the final FabG-catalyzed "
        "reduction step in bacterial fatty-acid elongation."
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

INITIAL_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}
EXPECTED_EDGE_KEYS = INITIAL_EDGE_KEYS | {
    ("determinant", "RO:0002327", "fabg_reduction"),
    ("drug0", "RO:0002411", "inhibition"),
    ("determinant", "RO:0002212", "inhibition"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies these FabG records under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The FabG mechanism is a resistance-conferring gene variant caused by "
        "mutation."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Point mutations in FabG can confer Triclosan resistance by "
        "counteracting inhibition of the FabG reduction step."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the antibiotic-resistant FabG parent to disinfecting agents "
        "and antiseptics."
    ),
    ("determinant", "RO:0002327", "fabg_reduction"): (
        "FabG enables the GO-grounded 3-oxoacyl-ACP reductase activity used "
        "in fatty-acid biosynthesis."
    ),
    ("drug0", "RO:0002411", "inhibition"): (
        "Triclosan blocks the final FabG reduction step in bacterial "
        "fatty-acid elongation."
    ),
    ("determinant", "RO:0002212", "inhibition"): (
        "Resistance-conferring FabG mutations reduce the inhibitory effect of "
        "Triclosan on the FabG-catalyzed reduction step."
    ),
}

_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*\S+[ \t]*$", re.M)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    "ARO:3004284": Target(
        identifier="ARO:3004284",
        filename="antibiotic-resistant-fabg-aro3004284.yaml",
    ),
    "ARO:3004049": Target(
        identifier="ARO:3004049",
        filename="escherichia-coli-fabg-mutations-conferring-resistance-to-triclosan-aro3004049.yaml",
    ),
}
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS.values()}


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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
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


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = "ARO drug-class relationship asserted directly on antibiotic resistant fabG."
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3004284 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3005386 ! "
            "disinfecting agents and antiseptics"
        ),
        "notes": notes,
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
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
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    if "determinant" not in nodes:
        raise ValueError(f"{target.identifier}: missing determinant node")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if found_edges != INITIAL_EDGE_KEYS and found_edges != EXPECTED_EDGE_KEYS:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(INITIAL_EDGE_KEYS - found_edges)
        )
        raise ValueError(f"{target.identifier}: missing initial edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)
    mutation_resistance_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    fabg_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        GO_FABG_EVIDENCE,
        NCBIFAM_FABG_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → FabG 3-oxoacyl-ACP reduction → resistance",
        "description": (
            "Conservative graph for FabG-mediated Triclosan resistance. The "
            "graph grounds the FabG 3-oxoacyl-ACP reductase activity and "
            "models Triclosan inhibition of that activity as a local state."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DISINFECTANT_NODE),
            copy.deepcopy(FABG_REDUCTION_NODE),
            copy.deepcopy(INHIBITION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_resistance_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                (
                    target_evidence,
                    _drug_relation_evidence(target),
                    DISINFECTANT_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "fabg_reduction",
                fabg_evidence,
            ),
            _edge(
                "drug0",
                "causally upstream of",
                "RO:0002411",
                "inhibition",
                fabg_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "inhibition",
                fabg_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") not in {"resistance", "resistance-draft"}:
        raise ValueError(f"{target.identifier}: expected exactly one FabG graph")

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_canonical_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"not a FabG target: {path}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _MAPPING_STATUS.sub("mapping_status: REVIEWED", out, count=1)

    history = list(_dicts(enriched.get("curation_history")))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [ARO_DIR / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one FabG YAML file",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
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
