#!/usr/bin/env python3
"""Rewrite the BLMT Tn5 bleomycin-sequestration ARO causal graph.

BLMT was seeded under CARD's broad antibiotic-inactivation mechanism because the
BLMT ARO definition only says the Tn5 ble gene encodes a bleomycin-resistance
protein.  Crystal structures of the Tn5 determinant bound to bleomycin support
the specific sequestration mechanism: the determinant binds the drug into a
determinant-antibiotic complex.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"
TARGET_ID = "ARO:3005036"
TARGET_FILENAME = "blmt-aro3005036.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Curated BLMT bleomycin-sequestration graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

BLMT_EVIDENCE = {
    "reference": "ARO:3005036",
    "snippet": (
        "BLMT is a bleomycin resistance protein encoded by the ble gene on "
        "transposon Tn5."
    ),
    "notes": "CARD definition for the Tn5 BLMT determinant.",
}

BLEOMYCIN_BINDING_EVIDENCE = {
    "reference": "PMID:11134052",
    "snippet": (
        "Crystal structures of the Tn5-carried bleomycin resistance determinant "
        "were solved uncomplexed and complexed with bleomycin."
    ),
    "notes": (
        "Maruyama et al. structurally characterized the Tn5 BLMT determinant in "
        "a bleomycin-bound complex."
    ),
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Direct inactivation of the antibiotic by the resistance gene product.",
    "notes": "CARD definition for broad antibiotic inactivation.",
}

SEQUESTRATION_EVIDENCE = {
    "reference": "ARO:3001206",
    "snippet": "Inactivation of an antibiotic through direct binding by a resistance protein.",
    "notes": "CARD definition for antibiotic inactivation by sequestration.",
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000081",
    "snippet": "glycopeptide antibiotic",
    "notes": "ARO drug-class term inherited by BLMT.",
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(copy.deepcopy(item))
    return evidence


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
        "evidence": _unique_evidence(*evidence),
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    sequestration_evidence = (
        BLMT_EVIDENCE,
        BLEOMYCIN_BINDING_EVIDENCE,
        SEQUESTRATION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": "BLMT → bleomycin sequestration → resistance",
        "description": (
            "Curated resistance-causation graph for BLMT. The graph keeps "
            "CARD's broad antibiotic-inactivation classification, then grounds "
            "BLMT's more specific mechanism as antibiotic sequestration by "
            "direct bleomycin binding."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            {
                "node_id": "mech1",
                "label": "antibiotic inactivation by sequestration",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3001206",
            },
            {
                "node_id": "drug0",
                "label": "bleomycin-family glycopeptide antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000081",
                "description": (
                    "Grounded to CARD's broad glycopeptide-antibiotic drug class "
                    "because the BLMT relation inherits that ARO term for bleomycin."
                ),
            },
            {
                "node_id": "complex",
                "label": "BLMT-bleomycin sequestration complex",
                "node_type": "STATE",
                "description": (
                    "Local state for bleomycin bound by the Tn5 BLMT determinant. "
                    "No stable term is available for this exact determinant-drug "
                    "complex."
                ),
            },
            {
                "node_id": "tn5",
                "label": "ble gene on transposon Tn5",
                "node_type": "NUCLEIC_ACID",
                "grounding": "SO:0000704",
                "description": (
                    "Local node for the Tn5 ble gene that encodes BLMT. "
                    "Grounded to the broad Sequence Ontology gene term because no "
                    "stable narrow term is available for the transposon Tn5 ble gene."
                ),
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies BLMT under the broad antibiotic-inactivation "
                "resistance mechanism.",
                BLMT_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "BLMT inactivates bleomycin-family drugs by binding and "
                "sequestering them.",
                BLMT_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
                BLEOMYCIN_BINDING_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "BLMT belongs to the sequestration subtype of antibiotic "
                "inactivation because it binds the drug.",
                *sequestration_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Sequestration prevents bleomycin-family antibiotics from "
                "reaching their cellular targets.",
                *sequestration_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "BLMT confers resistance by binding and sequestering bleomycin.",
                *sequestration_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts glycopeptide resistance for BLMT.",
                BLMT_EVIDENCE,
                GLYCOPEPTIDE_EVIDENCE,
            ),
            _edge(
                "determinant",
                "molecularly interacts with",
                "RO:0002436",
                "drug0",
                "Crystal structures captured the Tn5 BLMT determinant bound to "
                "bleomycin.",
                BLMT_EVIDENCE,
                BLEOMYCIN_BINDING_EVIDENCE,
            ),
            _edge(
                "complex",
                "has part",
                "BFO:0000051",
                "determinant",
                "The sequestration complex contains the BLMT determinant.",
                BLMT_EVIDENCE,
                BLEOMYCIN_BINDING_EVIDENCE,
            ),
            _edge(
                "complex",
                "has part",
                "BFO:0000051",
                "drug0",
                "The sequestration complex contains the bound bleomycin-family "
                "drug.",
                BLEOMYCIN_BINDING_EVIDENCE,
                GLYCOPEPTIDE_EVIDENCE,
            ),
            _edge(
                "complex",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Formation of the BLMT-drug complex sequesters the drug and "
                "prevents toxicity.",
                *sequestration_evidence,
            ),
            _edge(
                "tn5",
                "causally upstream of (encodes BLMT)",
                "RO:0002411",
                "determinant",
                "The Tn5 ble gene encodes the BLMT protein.",
                BLMT_EVIDENCE,
                BLEOMYCIN_BINDING_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any]) -> None:
    if record.get("identifier") != TARGET_ID:
        raise ValueError(f"{TARGET_FILENAME}: expected {TARGET_ID}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{TARGET_ID}: missing label")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{TARGET_ID}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = {"determinant", "mech0", "drug0", "resistance"} - node_ids
    if missing_nodes:
        missing = ", ".join(sorted(missing_nodes))
        raise ValueError(f"{TARGET_ID}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    _validate_record(record)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if path.name != TARGET_FILENAME:
        raise ValueError(f"{path}: target {TARGET_ID} must be in {TARGET_FILENAME}")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
    return [path / TARGET_FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or BLMT YAML file",
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
