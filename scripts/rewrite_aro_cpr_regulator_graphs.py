#!/usr/bin/env python3
"""Rewrite cprR/cprS graphs from stale efflux activation to Arn induction.

The cprR and cprS records were seeded as positive efflux regulators, but their
CARD definitions describe induction of the Arn operon in the presence of
cationic peptides. This updater replaces the AdeR-shaped pump scaffold with
that regulatory route and links the Arn operon to the existing Ara4N lipid-A
charge-alteration mechanism.

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
        "Rewrote cprR/cprS from stale efflux activation to cationic peptide "
        "sensing, Arn induction, and charge-alteration resistance"
    ),
    "llm_assisted": True,
}

CPRRS_EVIDENCE = {
    "reference": "ARO:3005065",
    "snippet": (
        "cprRS is a two-component regulatory system. In the presence of cationic "
        "peptides, it induces the Arn operon to confer resistance."
    ),
    "notes": (
        "CARD definition for the cprRS system: induction of the Arn operon, not "
        "direct drug efflux."
    ),
}

PMRF_EVIDENCE = {
    "reference": "ARO:3003578",
    "snippet": (
        "PmrF is required for the synthesis and transfer of "
        "4-amino-4-deoxy-L-arabinose (Ara4N) to Lipid A, which allows "
        "gram-negative bacteria to resist the antimicrobial activity of cationic "
        "antimicrobial peptides and antibiotics such as polymyxin."
    ),
    "notes": "CARD definition for the Arn/PmrF Ara4N synthesis and transfer route.",
}

CHARGE_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall of "
        "gram negative bacteria is a mechanism of resistance for cationic "
        "antimicrobials that depend on the negative charge for binding to the "
        "surface."
    ),
    "notes": (
        "CARD definition for charge alteration, the downstream resistance mechanism "
        "driven by Ara4N lipid-A modification."
    ),
}

TARGET_EVIDENCE = {
    "ARO:3005063": {
        "reference": "ARO:3005063",
        "snippet": (
            "cprR is one part of a two-component regulatory system. It with its "
            "counterpart cprS induce the Arn operon to confer resistance to peptide "
            "antibiotics."
        ),
        "notes": "CARD definition for the cprR regulator.",
    },
    "ARO:3005064": {
        "reference": "ARO:3005064",
        "snippet": (
            "cprS is part of a two-component regulatory system that, with its "
            "counterpart cprR, induces the Arn operon in the presence of cationic "
            "peptides to confer resistance."
        ),
        "notes": "CARD definition for the cprS regulator.",
    },
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "charge alteration conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003588",
    "description": (
        "Grounded to CARD's charge-alteration resistance mechanism; cprRS induces "
        "the Ara4N route that reduces the negative charge of lipid A."
    ),
}

SENSING_NODE = {
    "node_id": "sensing",
    "label": "sensing of cationic peptides",
    "node_type": "STATE",
    "description": "Local state for the cationic-peptide exposure that induces cprRS.",
}

ARN_OPERON_NODE = {
    "node_id": "arn_operon",
    "label": "Arn operon (Ara4N synthesis and transfer)",
    "node_type": "NUCLEIC_ACID",
    "grounding": "ARO:3003578",
    "description": (
        "Grounded to PmrF, the CARD record for the Arn/PmrF Ara4N synthesis and "
        "transfer route."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the nearest "
        "available superclass: ARO models determinants and mechanisms but has no "
        "term for the resistance phenotype itself."
    ),
}


@dataclass(frozen=True)
class EdgeUpdate:
    predicate: str
    predicate_id: str
    object: str
    description: str
    evidence: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def evidence(self) -> dict[str, str]:
        return TARGET_EVIDENCE[self.identifier]

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        return {
            ("sensing", "determinant"): EdgeUpdate(
                predicate="causally upstream of (activates the two-component system)",
                predicate_id="RO:0002411",
                object="determinant",
                description="Cationic peptides are the inducing signal for cprRS.",
                evidence=(self.evidence, CPRRS_EVIDENCE),
            ),
            ("determinant", "arn_operon"): EdgeUpdate(
                predicate="positively regulates (induces the Arn operon)",
                predicate_id="RO:0002213",
                object="arn_operon",
                description=(
                    "The cpr regulator induces the Arn operon; Ara4N synthesis and "
                    "transfer are modeled by the downstream Arn/PmrF records."
                ),
                evidence=(self.evidence, CPRRS_EVIDENCE, PMRF_EVIDENCE),
            ),
            ("arn_operon", "mech0"): EdgeUpdate(
                predicate="causally upstream of (drives Ara4N charge alteration)",
                predicate_id="RO:0002411",
                object="mech0",
                description=(
                    "Arn/PmrF-mediated Ara4N synthesis and transfer modifies lipid A "
                    "and reduces the negative envelope charge."
                ),
                evidence=(self.evidence, CPRRS_EVIDENCE, PMRF_EVIDENCE, CHARGE_EVIDENCE),
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                object="resistance",
                description=(
                    "Charge alteration is the downstream resistance mechanism induced "
                    "through the Arn operon."
                ),
                evidence=(self.evidence, CPRRS_EVIDENCE, CHARGE_EVIDENCE),
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                object="resistance",
                description=(
                    "The cpr regulator induces the Arn operon to confer resistance to "
                    "cationic peptide antibiotics."
                ),
                evidence=(self.evidence, CPRRS_EVIDENCE, PMRF_EVIDENCE),
            ),
        }

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


TARGETS = {
    "ARO:3005063": Target(
        identifier="ARO:3005063",
        filename="cprr-aro3005063.yaml",
    ),
    "ARO:3005064": Target(
        identifier="ARO:3005064",
        filename="cprs-aro3005064.yaml",
    ),
}

EXPECTED_INPUT_EDGES = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "activation"),
    ("activation", "pump"),
} | set().union(*(target.expected_edges for target in TARGETS.values()))


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
    found = {node.get("node_id") for node in nodes if isinstance(node, dict)}
    if "determinant" not in found:
        msg = f"{target.identifier}: missing node(s): determinant"
        raise ValueError(msg)

    determinant = copy.deepcopy(
        next(node for node in nodes if isinstance(node, dict) and node.get("node_id") == "determinant")
    )
    graph["nodes"] = [
        determinant,
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(SENSING_NODE),
        copy.deepcopy(ARN_OPERON_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _enrich_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.get("edges") or []
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_INPUT_EDGES:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    graph["edges"] = [
        _ordered_edge(
            {
                "subject": subject,
                "predicate": update.predicate,
                "predicate_id": update.predicate_id,
                "object": object_,
                "description": update.description,
                "evidence": [copy.deepcopy(item) for item in update.evidence],
            }
        )
        for (subject, object_), update in target.edge_updates.items()
    ]


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

    graph["description"] = (
        "Curated resistance-causation graph for cprRS-mediated Arn induction. The "
        "graph replaces the seeded AdeR efflux-activation scaffold with cationic "
        "peptide sensing, induction of the Arn operon, and downstream Ara4N lipid-A "
        "charge alteration."
    )
    _enrich_nodes(graph, target)
    _enrich_edges(graph, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a cpr regulator target: {identifier}")
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
        help="ARO directory or one of the two cpr regulator target YAML files",
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
