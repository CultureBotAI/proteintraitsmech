#!/usr/bin/env python3
"""Ground and correct DnaA rifamycin resistance graphs.

The existing DnaA graphs borrowed the HelR/RNAP target-protection mechanism.
This updater replaces those edges with a conservative DnaA-specific graph that
keeps rifamycin-inhibited RNA polymerase as a described local state and grounds
DnaA's native replication-initiation and RNA-polymerase-binding functions to GO.

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
HISTORY_ACTION = "Grounded DnaA rifamycin target-protection graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004244"
CHILD_IDENTIFIER = "ARO:3000248"

PARENT_DEFINITION = (
    "The DnaA family of replication initiation proteins interact with RNA "
    "polymerase to confer resistance against rifampicin anitibiotics."
)
CHILD_DEFINITION = (
    "DnaA is a chromosomal replication initiation protein which binds and "
    "interacts with RNA polymerase in Escherichia coli. A surplus of DnaA "
    "present in a cell has been shown to confer resistance to the antibiotic "
    "Rifampicin. Normally, rifampicin inhibits initiation of transcription by "
    "RNA polymerase, but a surplus of DnaA available at the origin has been "
    "shown to disrupt Rifampicin activity and confer resistance."
)

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": PARENT_DEFINITION,
    "notes": "CARD definition for the DnaA chromosomal replication initiation protein family.",
}

SURPLUS_EVIDENCE = {
    "reference": CHILD_IDENTIFIER,
    "snippet": CHILD_DEFINITION,
    "notes": (
        "CARD definition for DnaA, the family child that records the "
        "surplus-at-origin rifampicin-resistance mechanism."
    ),
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": "antibiotic target protection",
    "notes": "ARO mechanism term asserted on DnaA records.",
}

DRUG_RELATION_SNIPPET = (
    "relationship: confers_resistance_to_drug_class ARO:3000157 ! "
    "rifamycin antibiotic"
)
RIFAMYCIN_EVIDENCE = {
    "reference": "ARO:3000157",
    "snippet": "rifamycin antibiotic",
    "notes": "ARO drug-class term inherited by DnaA records.",
}

DNA_REPLICATION_EVIDENCE = {
    "reference": "GO:0006270",
    "snippet": (
        "The process in which DNA-dependent DNA replication is started; it "
        "begins when specific sequences, known as origins of replication, are "
        "recognized and bound by the origin recognition complex, followed by "
        "DNA unwinding."
    ),
    "notes": "GO DNA replication initiation term for DnaA's native process.",
}

RNAP_BINDING_EVIDENCE = {
    "reference": "GO:0043175",
    "snippet": (
        "Binding to an RNA polymerase core enzyme, containing a specific "
        "subunit composition defined as the core enzyme."
    ),
    "notes": "GO RNA polymerase core enzyme binding term.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target protection",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001003",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "rifamycin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000157",
}

DNA_REPLICATION_NODE = {
    "node_id": "dna_replication",
    "label": "DNA replication initiation",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006270",
}

RNAP_BINDING_NODE = {
    "node_id": "rnap_binding",
    "label": "RNA polymerase core enzyme binding",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0043175",
}

SURPLUS_NODE = {
    "node_id": "surplus",
    "label": "surplus DnaA at the origin",
    "node_type": "STATE",
    "description": (
        "Local state for the excess DnaA available at the origin that disrupts "
        "rifampicin activity."
    ),
}

INHIBITED_NODE = {
    "node_id": "inhibited",
    "label": "rifamycin-inhibited RNA polymerase",
    "node_type": "STATE",
    "description": (
        "Local state for rifamycin-mediated inhibition of bacterial RNA "
        "polymerase during transcription initiation."
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

OLD_DNAA_EDGE_KEYS = {
    ("drug0", "RO:0002411", "inhibited"),
    ("determinant", "RO:0002436", "rnap"),
    ("determinant", "RO:0002212", "inhibited"),
}

NEW_DNAA_EDGE_KEYS = {
    ("determinant", "RO:0002327", "dna_replication"),
    ("determinant", "RO:0002327", "rnap_binding"),
    ("determinant", "RO:0000086", "surplus"),
    ("drug0", "RO:0002411", "inhibited"),
    ("surplus", "RO:0002212", "inhibited"),
    ("rnap_binding", "RO:0002212", "inhibited"),
    ("surplus", "RO:0002411", "resistance"),
}

EXPECTED_EDGE_KEYS = CORE_EDGE_KEYS | NEW_DNAA_EDGE_KEYS
INPUT_EDGE_KEYS = CORE_EDGE_KEYS | OLD_DNAA_EDGE_KEYS | NEW_DNAA_EDGE_KEYS

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies DnaA as an antibiotic target-protection determinant."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "DnaA-mediated target protection is the rifamycin-resistance mechanism."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "DnaA surplus at the origin counters rifamycin activity and confers "
        "rifamycin resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the DnaA family to rifamycin antibiotics."
    ),
    ("determinant", "RO:0002327", "dna_replication"): (
        "DnaA normally enables DNA replication initiation."
    ),
    ("determinant", "RO:0002327", "rnap_binding"): (
        "DnaA binds and interacts with RNA polymerase."
    ),
    ("determinant", "RO:0000086", "surplus"): (
        "The rifamycin-resistance state is excess DnaA available at the origin."
    ),
    ("drug0", "RO:0002411", "inhibited"): (
        "Rifamycin antibiotics inhibit bacterial RNA polymerase."
    ),
    ("surplus", "RO:0002212", "inhibited"): (
        "Surplus DnaA disrupts rifamycin-mediated RNA polymerase inhibition."
    ),
    ("rnap_binding", "RO:0002212", "inhibited"): (
        "DnaA/RNA-polymerase interaction is the physical target-protection "
        "activity that counters rifamycin inhibition."
    ),
    ("surplus", "RO:0002411", "resistance"): (
        "Excess DnaA at the origin is the local state associated with "
        "rifamycin resistance."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="dnaa-chromosomal-replication-initiation-protein-aro3004244.yaml",
    ),
    CHILD_IDENTIFIER: Target(
        identifier=CHILD_IDENTIFIER,
        filename="dnaa-aro3000248.yaml",
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
        notes = "ARO drug-class relationship asserted directly on the DnaA parent."
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3004244 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": DRUG_RELATION_SNIPPET,
        "notes": notes,
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = (item["reference"], " ".join(item.get("snippet", "").split()))
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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "inhibited", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    required = CORE_EDGE_KEYS | {("drug0", "RO:0002411", "inhibited")}
    missing_edges = required - found_edges
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)

    target_protection_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MECHANISM_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        SURPLUS_EVIDENCE,
        _drug_relation_evidence(target),
        RIFAMYCIN_EVIDENCE,
        *source_evidence,
    )
    replication_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        DNA_REPLICATION_EVIDENCE,
        *source_evidence,
    )
    rnap_binding_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        RNAP_BINDING_EVIDENCE,
        *source_evidence,
    )
    surplus_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        SURPLUS_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → RNA polymerase protection → rifamycin resistance",
        "description": (
            "Conservative graph for DnaA-mediated rifamycin resistance. The "
            "graph replaces the prior HelR-specific target-protection seed with "
            "DnaA RNA-polymerase binding, DnaA's native DNA-replication "
            "initiation process, and a described local state for surplus DnaA "
            "countering rifamycin inhibition of RNA polymerase."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(DNA_REPLICATION_NODE),
            copy.deepcopy(RNAP_BINDING_NODE),
            copy.deepcopy(SURPLUS_NODE),
            copy.deepcopy(INHIBITED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                target_protection_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                target_protection_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                surplus_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "dna_replication",
                replication_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "rnap_binding",
                rnap_binding_evidence,
            ),
            _edge(
                "determinant",
                "has quality",
                "RO:0000086",
                "surplus",
                surplus_evidence,
            ),
            _edge(
                "drug0",
                "causally upstream of",
                "RO:0002411",
                "inhibited",
                drug_evidence,
            ),
            _edge(
                "surplus",
                "negatively regulates",
                "RO:0002212",
                "inhibited",
                surplus_evidence,
            ),
            _edge(
                "rnap_binding",
                "negatively regulates",
                "RO:0002212",
                "inhibited",
                (*rnap_binding_evidence, *surplus_evidence),
            ),
            _edge(
                "surplus",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                surplus_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a DnaA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or exact DnaA YAML")
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
