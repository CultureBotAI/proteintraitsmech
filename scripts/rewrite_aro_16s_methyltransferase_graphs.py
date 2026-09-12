#!/usr/bin/env python3
"""Ground and complete 16S rRNA methyltransferase ARO causal graphs.

The three records handled here model aminoglycoside resistance by methylation
of the 16S rRNA decoding center. This updater grounds the rRNA
methyltransferase activity to a conservative local GO superclass, describes
every edge, and adds the missing methylated-site-to-resistance edge.

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
HISTORY_ACTION = (
    "Grounded 16S rRNA decoding-site nodes and supplemented methyltransferase evidence"
)
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of the transfer of a methyl group from S-adenosyl-L-methionine to a "
        "nucleoside residue in an rRNA molecule. The methyl group can be transfered to "
        "the nucleobase or to the ribose group of the nucleoside."
    ),
    "notes": (
        "GO definition for the broad rRNA methyltransferase activity superclass; the "
        "ARO/PubMed evidence constrains the substrate to 16S rRNA."
    ),
}

PARENT_EVIDENCE = {
    "reference": "ARO:3000857",
    "snippet": (
        "Methyltransferases that modify the 16S rRNA of the 30S subunit of "
        "bacterial ribosomes, conferring resistance to drugs that target 16S rRNA."
    ),
    "notes": "CARD definition for 16S ribosomal RNA methyltransferase.",
}

TARGET_ALTERATION_EVIDENCE = {
    "reference": "ARO:0001001",
    "snippet": (
        "Mutational alteration or enzymatic modification of antibiotic target "
        "which results in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target alteration.",
}

RIBOSOMAL_ALTERATION_EVIDENCE = {
    "reference": "ARO:3000211",
    "snippet": (
        "Chemical alteration of the ribosome results in modification of an "
        "antibiotic's target leading to resistance."
    ),
    "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
}

AMINOGLYCOSIDE_EVIDENCE = {
    "reference": "ARO:0000016",
    "snippet": "aminoglycoside antibiotic",
    "notes": "ARO drug-class term targeted by A1408 and G1405 methyltransferases.",
}

SO_RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both "
        "structural scaffolding and catalytic activity."
    ),
    "notes": (
        "Sequence Ontology definition for the broad rRNA superclass used as a "
        "conservative grounding for the local 16S rRNA decoding-site nodes."
    ),
}

SHARED_NODE_UPDATES = {
    "methyltransferase": {
        "node_id": "methyltransferase",
        "label": "16S rRNA methyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008649",
        "description": (
            "Grounded to the broad GO rRNA methyltransferase activity superclass because "
            "the ARO/PubMed evidence narrows this node to methylation of 16S rRNA."
        ),
    },
    "decoding_site": {
        "node_id": "decoding_site",
        "label": "16S rRNA decoding site (aminoglycoside binding site)",
        "node_type": "NUCLEIC_ACID",
        "grounding": "SO:0000252",
        "description": (
            "Local rRNA target-site node for the aminoglycoside binding site in the "
            "16S decoding center. Grounded to broad rRNA because no stable narrow "
            "term is available for this local methylated target site."
        ),
    },
    "methylated": {
        "node_id": "methylated",
        "label": "methylated 16S rRNA decoding site",
        "node_type": "STATE",
        "grounding": "SO:0000252",
        "description": (
            "Local state representing methylation of the aminoglycoside-binding 16S "
            "rRNA decoding site. Grounded to broad rRNA because no stable narrow "
            "term is available for this methylated local state."
        ),
    },
}

METHYLATED_RESISTANCE_EDGE = {
    "subject": "methylated",
    "predicate": "causally upstream of (blocks aminoglycoside binding)",
    "predicate_id": "RO:0002411",
    "object": "resistance",
}

ALL_EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this determinant under antibiotic target alteration because "
        "the methyltransferase modifies the 16S rRNA aminoglycoside target site."
    ),
    ("mech0", "resistance"): (
        "Target alteration is the broad resistance mechanism represented by 16S "
        "decoding-site methylation."
    ),
    ("determinant", "mech1"): (
        "CARD also classifies this determinant under ribosomal alteration conferring "
        "antibiotic resistance, the ribosome-specific branch."
    ),
    ("mech1", "resistance"): (
        "Methylation of the 16S decoding center is the ribosomal alteration that "
        "supports aminoglycoside resistance."
    ),
    ("determinant", "resistance"): (
        "The determinant enables 16S rRNA methylation, producing a modified decoding "
        "site that no longer binds aminoglycosides effectively."
    ),
    ("determinant", "drug0"): (
        "CARD asserts aminoglycoside resistance for this 16S rRNA methyltransferase "
        "subfamily."
    ),
    ("determinant", "methyltransferase"): (
        "The determinant enables methyl transfer onto 16S rRNA nucleotides in the "
        "decoding center."
    ),
    ("methyltransferase", "methylated"): (
        "rRNA methyltransferase activity yields a methylated 16S decoding-site state."
    ),
    ("methylated", "decoding_site"): (
        "Methylation changes the 16S rRNA aminoglycoside binding site and prevents "
        "normal drug binding."
    ),
    ("drug0", "decoding_site"): (
        "Aminoglycosides normally target the 16S rRNA decoding site modified by these "
        "methyltransferases."
    ),
    ("methylated", "resistance"): (
        "The methylated 16S decoding-site state is the terminal modeled cause of the "
        "aminoglycoside-resistance phenotype."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    expected_edges: set[tuple[str, str]]


PARENT_EDGES = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "mech1"),
    ("mech1", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "methyltransferase"),
    ("methyltransferase", "methylated"),
    ("methylated", "decoding_site"),
    ("methylated", "resistance"),
}

CHILD_EDGES = PARENT_EDGES | {
    ("determinant", "drug0"),
    ("drug0", "decoding_site"),
}

TARGETS = {
    "ARO:3000857": Target(
        identifier="ARO:3000857",
        filename="16s-ribosomal-rna-methyltransferase-aro3000857.yaml",
        expected_edges=PARENT_EDGES,
    ),
    "ARO:3004272": Target(
        identifier="ARO:3004272",
        filename="16s-rrna-methyltransferase-a1408-aro3004272.yaml",
        expected_edges=CHILD_EDGES,
    ),
    "ARO:3004271": Target(
        identifier="ARO:3004271",
        filename="16s-rrna-methyltransferase-g1405-aro3004271.yaml",
        expected_edges=CHILD_EDGES,
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _definition_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record["definition"]).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _relation_evidence(edge: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        item
        for item in _dicts(edge.get("evidence"))
        if str(item.get("snippet", "")).startswith("relationship:")
    )


def _base_evidence(record: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    evidence: tuple[dict[str, Any], ...] = (_definition_evidence(record),)
    if record["identifier"] != "ARO:3000857":
        evidence = (*evidence, PARENT_EVIDENCE)
    return (*evidence, *_source_evidence(record))


def _supplemental_evidence(
    record: dict[str, Any],
    edge: dict[str, Any],
) -> list[dict[str, Any]]:
    key = _edge_key(edge)
    base = _base_evidence(record)
    by_edge: tuple[dict[str, Any], ...] = ()

    if key in {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
    }:
        by_edge = (TARGET_ALTERATION_EVIDENCE,)
    elif key in {
        ("determinant", "mech1"),
        ("mech1", "resistance"),
    }:
        by_edge = (RIBOSOMAL_ALTERATION_EVIDENCE,)
    elif key in {
        ("determinant", "methyltransferase"),
        ("methyltransferase", "methylated"),
    }:
        by_edge = (RRNA_METHYLTRANSFERASE_EVIDENCE, SO_RRNA_EVIDENCE)
    elif key in {
        ("methylated", "decoding_site"),
        ("methylated", "resistance"),
    }:
        by_edge = (
            RRNA_METHYLTRANSFERASE_EVIDENCE,
            RIBOSOMAL_ALTERATION_EVIDENCE,
            SO_RRNA_EVIDENCE,
        )
    elif key == ("determinant", "drug0"):
        by_edge = (*_relation_evidence(edge), AMINOGLYCOSIDE_EVIDENCE)
    elif key == ("drug0", "decoding_site"):
        by_edge = (*_relation_evidence(edge), AMINOGLYCOSIDE_EVIDENCE, SO_RRNA_EVIDENCE)

    return _unique_evidence(*_dicts(edge.get("evidence")), *base, *by_edge)


def _methylated_resistance_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    det_resistance = next(
        edge
        for edge in graph.get("edges", [])
        if _edge_key(edge) == ("determinant", "resistance")
    )
    return copy.deepcopy(det_resistance["evidence"])


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id not in SHARED_NODE_UPDATES:
            continue
        nodes[index] = copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        found.add(node_id)

    missing = sorted(set(SHARED_NODE_UPDATES) - found)
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

    edges = graph.setdefault("edges", [])
    if not any(_edge_key(edge) == ("methylated", "resistance") for edge in edges):
        new_edge = copy.deepcopy(METHYLATED_RESISTANCE_EDGE)
        new_edge["evidence"] = _methylated_resistance_evidence(graph)
        edges.append(new_edge)

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in target.expected_edges:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        edge["description"] = ALL_EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _supplemental_evidence(record, edge)
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(target.expected_edges - seen)
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
        raise ValueError(f"{path}: not a 16S rRNA methyltransferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
