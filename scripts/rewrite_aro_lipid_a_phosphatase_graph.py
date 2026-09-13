#!/usr/bin/env python3
"""Curate the generic lipid A phosphatase charge-alteration graph.

CARD describes lipid A phosphatases generically rather than naming a single
1- or 4'-phosphatase reaction. This updater keeps the graph conservative: it
grounds the shared CARD charge-alteration mechanism and the lipid A substrate,
then records the phosphatase-mediated covalent modification of lipid A as the
charge-reducing state described by ARO.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

IDENTIFIER = "ARO:3004287"
FILENAME = "lipid-a-phosphatase-aro3004287.yaml"
HISTORY_ACTION = "Curated generic lipid A phosphatase charge-alteration graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

LIPID_A_PHOSPHATASE_DEFINITION = (
    "The antimicrobial activity of certain antibiotics, such as peptide "
    "antibiotics, is proposed to be initiated through binding to the lipid A "
    "moiety of lipopolysaccharides. Thus, covalent modification of "
    "Gram-negative bacterial lipid A by phosphatases is a mechanism to reduce "
    "the susceptibility of the bacteria to antibiotics."
)

TARGET_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": LIPID_A_PHOSPHATASE_DEFINITION,
    "notes": (
        "CARD definition for lipid A phosphatase; this generic record frames "
        "peptide-antibiotic binding to lipid A as proposed."
    ),
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall "
        "of gram negative bacteria is a mechanism of resistance for cationic "
        "antimicrobials that depend on the negative charge for binding to the "
        "surface."
    ),
    "notes": "CARD definition for the shared charge-alteration resistance mechanism.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": "ARO drug-class relationship asserted directly on lipid A phosphatase.",
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug class asserted on the lipid A phosphatase parent.",
}

CHEBI_LIPID_A_EVIDENCE = {
    "reference": "CHEBI:47040",
    "snippet": "The glycolipid moiety of bacterial lipopolysaccharide.",
    "notes": "ChEBI definition for lipid A.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "charge alteration conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003588",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

LIPID_A_NODE = {
    "node_id": "lipid_a",
    "label": "lipid A",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:47040",
    "description": (
        "Grounded to the ChEBI class for the glycolipid moiety of bacterial "
        "lipopolysaccharide that CARD says is covalently modified by lipid A "
        "phosphatases."
    ),
}

CHARGE_NODE = {
    "node_id": "charge",
    "label": "reduced net negative surface charge",
    "node_type": "STATE",
    "description": (
        "Local state representing the reduced negative surface charge modeled "
        "for Gram-negative lipid A modified by phosphatases."
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
    ("determinant", "RO:0002411", "lipid_a"),
    ("lipid_a", "RO:0002411", "charge"),
    ("charge", "RO:0002212", "drug0"),
    ("charge", "RO:0002411", "resistance"),
}

_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*\S+[ \t]*$", re.M)


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


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
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
        out.append(copy.deepcopy(item))
    return out


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found_edges: set[tuple[str, str, str]] = set()
    allowed_edges = INITIAL_EDGE_KEYS | EXPECTED_EDGE_KEYS
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in allowed_edges:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if found_edges == EXPECTED_EDGE_KEYS:
        return

    missing_initial = INITIAL_EDGE_KEYS - found_edges
    unexpected_canonical = found_edges - INITIAL_EDGE_KEYS
    if missing_initial:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_initial)
        )
        raise ValueError(f"{IDENTIFIER}: missing initial edge(s): {missing}")
    if unexpected_canonical:
        extra = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(unexpected_canonical)
        )
        raise ValueError(f"{IDENTIFIER}: partial canonical edge(s): {extra}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(LIPID_A_NODE),
        copy.deepcopy(CHARGE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges() -> list[dict[str, Any]]:
    lipid_a_evidence = (TARGET_EVIDENCE, CHEBI_LIPID_A_EVIDENCE)
    charge_evidence = (
        TARGET_EVIDENCE,
        CHEBI_LIPID_A_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
    )
    resistance_evidence = (
        TARGET_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
    )
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies lipid A phosphatase under charge alteration.",
            resistance_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "Charge alteration is the broad mechanism by which covalent "
                "lipid-A modification reduces peptide-antibiotic susceptibility."
            ),
            charge_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Phosphatase-mediated lipid-A modification is modeled as "
                "reducing the susceptibility of Gram-negative bacteria to "
                "peptide antibiotics."
            ),
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "ARO maps lipid A phosphatase to peptide antibiotics.",
            (TARGET_EVIDENCE, DRUG_RELATION_EVIDENCE, PEPTIDE_ANTIBIOTIC_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (modifies lipid A)",
            "RO:0002411",
            "lipid_a",
            (
                "Lipid A phosphatases covalently modify the lipid A moiety of "
                "Gram-negative lipopolysaccharides."
            ),
            lipid_a_evidence,
        ),
        _edge(
            "lipid_a",
            "causally upstream of (reduces surface negative charge)",
            "RO:0002411",
            "charge",
            (
                "The lipid-A modification is modeled as reducing the net "
                "negative surface charge used by cationic antimicrobial binding."
            ),
            charge_evidence,
        ),
        _edge(
            "charge",
            "negatively regulates (impedes drug binding)",
            "RO:0002212",
            "drug0",
            (
                "Reduced net negative surface charge impedes binding by "
                "cationic peptide antibiotics."
            ),
            (CHARGE_ALTERATION_EVIDENCE, TARGET_EVIDENCE, PEPTIDE_ANTIBIOTIC_EVIDENCE),
        ),
        _edge(
            "charge",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "The same charge-reduced envelope state is the terminal "
                "modeled state causally upstream of peptide-antibiotic "
                "resistance."
            ),
            resistance_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = _dicts(out.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{IDENTIFIER}: expected exactly one causal graph")
    graph = graphs[0]
    _validate_graph(graph)

    graph["graph_id"] = "resistance"
    graph["title"] = "lipid A phosphatase → lipid A charge alteration → peptide-antibiotic resistance"
    graph["description"] = (
        "Conservative graph for the generic CARD lipid A phosphatase parent. "
        "It records phosphatase-mediated covalent modification of lipid A and "
        "the proposed downstream peptide-antibiotic binding route without "
        "inventing a specific 1- or 4′-phosphatase reaction for the whole parent."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges()
    out["causal_graphs"] = [graph]
    out["mapping_status"] = "REVIEWED"
    if not any(
        isinstance(item, dict) and item.get("action") == HISTORY_ACTION
        for item in out.get("curation_history") or []
    ):
        out.setdefault("curation_history", []).append(copy.deepcopy(HISTORY_EVENT))
    return out, out.get("causal_graphs") != before or record.get("mapping_status") != "REVIEWED"


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: not a YAML mapping")
    out, changed = enrich_record(record)
    graph_block = _dump({"causal_graphs": out["causal_graphs"]})
    result = replace_block(text, "causal_graphs", graph_block)
    result = _MAPPING_STATUS.sub("mapping_status: REVIEWED", result, count=1)
    if HISTORY_ACTION not in result:
        history_block = _dump({"curation_history": [HISTORY_EVENT]})
        result = append_to_section(result, "curation_history", history_block)
    return result, changed or result != text


def iter_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return [path / FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=ARO_DIR)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = 0
    already = 0
    for path in iter_paths(args.path):
        text = path.read_text(encoding="utf-8")
        out, did_change = enrich_text(text, path)
        if did_change:
            if args.apply:
                path.write_text(out, encoding="utf-8")
                print(f"  wrote {path.name}")
            else:
                print(f"  would write {path.name}")
            changed += 1
        else:
            already += 1

    verb = "changed" if args.apply else "would change"
    print(f"{verb}: {changed}")
    print(f"already enriched: {already}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
