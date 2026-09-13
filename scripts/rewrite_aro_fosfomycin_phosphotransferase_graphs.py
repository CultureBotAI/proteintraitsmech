#!/usr/bin/env python3
"""Ground and complete fosfomycin phosphotransferase graphs.

The fosfomycin phosphotransferase branch had a redundant ungrounded local
``transfer`` molecular-function node. ARO:3000105 already names the
phosphorylation mechanism, so this updater uses that grounded mechanism as the
activity that modifies fosfomycin, preserves inherited phosphonic-acid
drug-class edges where CARD asserts them, and adds multi-source evidence and
edge descriptions throughout.

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

HISTORY_ACTION = "Grounded fosfomycin phosphotransferase causal graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PHOSPHOTRANSFERASE_PARENT = "ARO:3000359"
FOSC_PARENT = "ARO:3004245"
FOM_PARENT = "ARO:3004246"
DRUG_RELATION_SNIPPET = (
    "relationship: confers_resistance_to_drug_class ARO:3007149 ! "
    "phosphonic acid antibiotic"
)

PHOSPHOTRANSFERASE_DEFINITION = (
    "In the presence of ATP and magnesium (II), fosfomycin gets phosphorylated at the "
    "phosphate group resulting in a diphosphate group which inactivates the antibiotic."
)

FOSC_DEFINITION = (
    "The fosC family of phosphotransferases phosphorylate fosfomycin to confer "
    "resistance and have been found in various bacterial isolates."
)

FOM_DEFINITION = (
    "Two members of the Fom family have been identified, FomA and FomB. FomB "
    "must interact with FomA confer resistance to fosfomycin, however FomA is "
    "capable of conferring resistance alone."
)

PARENT_EVIDENCE = {
    PHOSPHOTRANSFERASE_PARENT: {
        "reference": PHOSPHOTRANSFERASE_PARENT,
        "snippet": PHOSPHOTRANSFERASE_DEFINITION,
        "notes": "CARD definition for fosfomycin phosphotransferases.",
    },
    FOSC_PARENT: {
        "reference": FOSC_PARENT,
        "snippet": FOSC_DEFINITION,
        "notes": "CARD definition for the fosC phosphotransferase family.",
    },
    FOM_PARENT: {
        "reference": FOM_PARENT,
        "snippet": FOM_DEFINITION,
        "notes": "CARD definition for the Fom phosphotransferase family.",
    },
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic-inactivation resistance mechanism.",
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": "CARD definition for antibiotic-inactivation enzymes.",
}

PHOSPHORYLATION_EVIDENCE = {
    "reference": "ARO:3000105",
    "snippet": "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
    "notes": "CARD definition for phosphorylation of antibiotics.",
}

PHOSPHONIC_ACID_EVIDENCE = {
    "reference": "ARO:3007149",
    "snippet": "phosphonic acid antibiotic",
    "notes": "ARO phosphonic-acid antibiotic drug class inherited by FosC and Fom records.",
}

INACTIVATION_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

PHOSPHORYLATION_NODE = {
    "node_id": "mech1",
    "label": "phosphorylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000105",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "phosphonic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007149",
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "phosphorylated inactive fosfomycin",
    "node_type": "STATE",
    "description": (
        "Local product state for fosfomycin after phosphotransferase-mediated "
        "phosphorylation inactivates the antibiotic."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms but "
        "has no term for the resistance phenotype itself."
    ),
}

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("mech1", "RO:0002411", "modified"),
}

DRUG_EDGE_KEYS = {
    ("determinant", "ARO:2000001", "drug0"),
    ("mech1", "RO:0002233", "drug0"),
}

OBSOLETE_EDGE_KEYS = {
    ("determinant", "RO:0002327", "transfer"),
    ("transfer", "RO:0002233", "drug0"),
    ("transfer", "RO:0002411", "modified"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies fosfomycin phosphotransferases under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Fosfomycin inactivation is causally upstream of the resistance phenotype."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "CARD classifies this branch under phosphorylation of antibiotic "
        "conferring resistance."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Phosphorylation of fosfomycin inactivates the antibiotic and confers resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The phosphotransferase determinant phosphorylates fosfomycin upstream of "
        "antibiotic inactivation and resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this phosphotransferase branch to phosphonic acid antibiotics."
    ),
    ("mech1", "RO:0002233", "drug0"): (
        "Fosfomycin is the phosphonic-acid antibiotic input to the phosphorylation "
        "reaction."
    ),
    ("mech1", "RO:0002411", "modified"): (
        "The phosphorylation mechanism produces the inactive phosphorylated "
        "fosfomycin state."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    parent_identifier: str
    drug_relation_source: str | None = None

    @property
    def has_drug(self) -> bool:
        return self.drug_relation_source is not None

    @property
    def parent_evidence(self) -> dict[str, str]:
        return PARENT_EVIDENCE[self.parent_identifier]


TARGETS = {
    PHOSPHOTRANSFERASE_PARENT: Target(
        identifier=PHOSPHOTRANSFERASE_PARENT,
        filename="fosfomycin-phosphotransferase-aro3000359.yaml",
        parent_identifier=PHOSPHOTRANSFERASE_PARENT,
    ),
    FOSC_PARENT: Target(
        identifier=FOSC_PARENT,
        filename="fosc-phosphotransferase-family-aro3004245.yaml",
        parent_identifier=FOSC_PARENT,
        drug_relation_source=FOSC_PARENT,
    ),
    "ARO:3000380": Target(
        identifier="ARO:3000380",
        filename="fosc-aro3000380.yaml",
        parent_identifier=FOSC_PARENT,
        drug_relation_source=FOSC_PARENT,
    ),
    "ARO:3002874": Target(
        identifier="ARO:3002874",
        filename="fosc2-aro3002874.yaml",
        parent_identifier=FOSC_PARENT,
        drug_relation_source=FOSC_PARENT,
    ),
    FOM_PARENT: Target(
        identifier=FOM_PARENT,
        filename="fom-phosphotransferase-family-aro3004246.yaml",
        parent_identifier=FOM_PARENT,
        drug_relation_source=FOM_PARENT,
    ),
    "ARO:3000423": Target(
        identifier="ARO:3000423",
        filename="foma-aro3000423.yaml",
        parent_identifier=FOM_PARENT,
        drug_relation_source=FOM_PARENT,
    ),
    "ARO:3000449": Target(
        identifier="ARO:3000449",
        filename="fomb-aro3000449.yaml",
        parent_identifier=FOM_PARENT,
        drug_relation_source=FOM_PARENT,
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.drug_relation_source is None:
        raise ValueError(f"{target.identifier}: no drug relation source")
    if target.drug_relation_source == target.identifier:
        notes = "ARO drug-class relationship asserted directly on this record."
    else:
        notes = (
            "ARO drug-class relationship asserted on "
            f"{target.drug_relation_source} and inherited by {target.identifier}."
        )
    return {
        "reference": target.drug_relation_source,
        "snippet": DRUG_RELATION_SNIPPET,
        "notes": notes,
    }


def _expected_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    if target.has_drug:
        return CORE_EDGE_KEYS | DRUG_EDGE_KEYS
    return CORE_EDGE_KEYS


def _input_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    return _expected_edge_keys(target) | {
        ("determinant", "RO:0002327", "transfer"),
        ("transfer", "RO:0002411", "modified"),
    } | (OBSOLETE_EDGE_KEYS if target.has_drug else set())


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
    missing_nodes = sorted({"determinant", "mech0", "mech1", "modified", "resistance"} - set(nodes))
    if target.has_drug and "drug0" not in nodes:
        missing_nodes.append("drug0")
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    input_edges = _input_edge_keys(target)
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in input_edges:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    required = _expected_edge_keys(target) - {
        ("mech1", "RO:0002233", "drug0"),
        ("mech1", "RO:0002411", "modified"),
    }
    missing_edges = required - seen
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
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)
    inactivation_evidence = (
        target_evidence,
        target.parent_evidence,
        PARENT_EVIDENCE[PHOSPHOTRANSFERASE_PARENT],
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    phosphorylation_evidence = (
        target_evidence,
        target.parent_evidence,
        PARENT_EVIDENCE[PHOSPHOTRANSFERASE_PARENT],
        PHOSPHORYLATION_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        *source_evidence,
    )

    nodes_out = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(INACTIVATION_NODE),
        copy.deepcopy(PHOSPHORYLATION_NODE),
    ]
    if target.has_drug:
        nodes_out.append(copy.deepcopy(DRUG_NODE))
    nodes_out.extend([copy.deepcopy(MODIFIED_NODE), copy.deepcopy(RESISTANCE_NODE)])

    edges = [
        _edge(
            "determinant",
            "participates in (inactivation mechanism)",
            "RO:0000056",
            "mech0",
            inactivation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            inactivation_evidence,
        ),
        _edge(
            "determinant",
            "participates in (phosphorylation mechanism)",
            "RO:0000056",
            "mech1",
            phosphorylation_evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            phosphorylation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            phosphorylation_evidence,
        ),
    ]

    if target.has_drug:
        drug_evidence = (
            target_evidence,
            target.parent_evidence,
            PARENT_EVIDENCE[PHOSPHOTRANSFERASE_PARENT],
            _drug_relation_evidence(target),
            PHOSPHONIC_ACID_EVIDENCE,
            *source_evidence,
        )
        edges.extend(
            [
                _edge(
                    "determinant",
                    "confers resistance to",
                    "ARO:2000001",
                    "drug0",
                    drug_evidence,
                ),
                _edge(
                    "mech1",
                    "has input (the drug)",
                    "RO:0002233",
                    "drug0",
                    (*phosphorylation_evidence, PHOSPHONIC_ACID_EVIDENCE),
                ),
            ]
        )

    edges.append(
        _edge(
            "mech1",
            "causally upstream of (inactivates the drug)",
            "RO:0002411",
            "modified",
            phosphorylation_evidence,
        )
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → fosfomycin phosphorylation → resistance",
        "description": (
            "Curated resistance graph for fosfomycin phosphotransferases. The "
            "grounded ARO:3000105 phosphorylation mechanism is represented as "
            "the modifying activity, producing a described local state for "
            "inactive phosphorylated fosfomycin."
        ),
        "nodes": nodes_out,
        "edges": edges,
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
        raise ValueError(f"{path}: not a fosfomycin phosphotransferase target: {identifier}")
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
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or exact fosfomycin phosphotransferase YAML",
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
