#!/usr/bin/env python3
"""Rewrite the 50S macrolide-resistance rRNA mutation ARO graph.

The ARO:3005001 record is a 50S rRNA macrolide-specific parent.  It should keep
the conservative broad ribosome model used by its 50S ancestor and avoid
inventing a narrower binding-site node that is only supported by the 16S/23S
child definitions.

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
FILENAME = "50s-rrna-with-mutation-conferring-resistance-to-macrolide-antibiotics-aro3005001.yaml"
IDENTIFIER = "ARO:3005001"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed 50S macrolide rRNA mutation causal graph",
    "llm_assisted": True,
}

R_RNA_EVIDENCE = {
    "reference": "ARO:3000328",
    "snippet": (
        "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic "
        "resistance to drugs that target the bacterial ribosome."
    ),
    "notes": "CARD definition for the rRNA mutation parent term.",
}

FIFTY_S_EVIDENCE = {
    "reference": "ARO:3005003",
    "snippet": (
        "Mutations in the prokaryotic 50S ribosomal RNA subunit disrupt "
        "binding sites and thereby reduce antibiotic efficacy."
    ),
    "notes": "CARD definition for the 50S rRNA mutation parent term.",
}

MUTATION_MECHANISM_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

RIBOSOME_EVIDENCE = {
    "reference": "GO:0005840",
    "snippet": "It consists of two subunits, one large and one small, each containing only protein and RNA.",
    "notes": "GO definition supporting rRNA as a component of the broad ribosome node.",
}

MACROLIDE_RELATION_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000000 ! macrolide antibiotic",
    "notes": "Asserted directly on ARO:3005001 in the CARD/ARO release.",
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

RIBOSOME_NODE = {
    "node_id": "ribosome",
    "label": "bacterial ribosome",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0005840",
    "description": (
        "Grounded to the broad GO ribosome class because the ARO evidence "
        "scopes this local node to the bacterial ribosome."
    ),
}

MACROLIDE_NODE = {
    "node_id": "drug0",
    "label": "macrolide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000000",
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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "NUCLEIC_ACID",
        "grounding": IDENTIFIER,
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        R_RNA_EVIDENCE,
        FIFTY_S_EVIDENCE,
        MUTATION_MECHANISM_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → bacterial ribosome → macrolide resistance",
        "description": (
            "Curated resistance-causation graph for macrolide resistance "
            "caused by mutations in 50S rRNA. The graph uses the broad "
            "ribosome target node supported by this parent record and avoids "
            "naming a narrower 23S binding-site node from descendant "
            "records."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            copy.deepcopy(MACROLIDE_NODE),
            copy.deepcopy(RIBOSOME_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies macrolide-resistance 50S rRNA mutations "
                "under mutation conferring antibiotic resistance.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism represents rRNA sequence "
                "changes that reduce efficacy of ribosome-targeting antibiotics.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Nucleotide point mutations in 50S rRNA confer resistance to "
                "macrolides that target the bacterial ribosome.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that this 50S rRNA mutation class confers "
                "resistance to macrolide antibiotics.",
                record_evidence,
                MACROLIDE_RELATION_EVIDENCE,
                R_RNA_EVIDENCE,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "ribosome",
                "The mutated 50S rRNA is modeled as part of the bacterial "
                "ribosome to identify the cellular target of these "
                "resistance-conferring changes.",
                record_evidence,
                FIFTY_S_EVIDENCE,
                RIBOSOME_EVIDENCE,
            ),
            _edge(
                "drug0",
                "molecularly interacts with (targets the ribosome)",
                "RO:0002436",
                "ribosome",
                "This parent record supports a broad macrolide-ribosome target "
                "edge but does not identify a narrower 23S binding site.",
                record_evidence,
                R_RNA_EVIDENCE,
                RIBOSOME_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any]) -> None:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{FILENAME}: expected {IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "drug0", "ribosome", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing_ids}")


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    _validate_record(record)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != FILENAME:
        raise ValueError(f"{path}: expected filename {FILENAME}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR / FILENAME,
        help="50S macrolide rRNA YAML file",
    )
    args = parser.parse_args(argv)

    try:
        before = args.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, args.path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PROBLEM: {exc}", file=sys.stderr)
        return 1

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {args.path.name}")
        if args.apply:
            args.path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
