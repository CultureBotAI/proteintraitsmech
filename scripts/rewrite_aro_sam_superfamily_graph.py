#!/usr/bin/env python3
"""Rewrite the radical-SAM 23S rRNA methyltransferase parent graph.

The S-adenosylmethionine (SAM) superfamily ARO record already has a compact
target-alteration graph with the right broad mechanism, 23S rRNA alteration
mechanism, radical-SAM domain, and radical-SAM fold. This updater replaces the
old single-reference edge evidence and placeholder domain/fold descriptions.

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
FILENAME = "s-adenosylmethionine-sam-superfamily-aro3004575.yaml"
IDENTIFIER = "ARO:3004575"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed radical-SAM 23S rRNA methyltransferase causal graph",
    "llm_assisted": True,
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

SAM_SUPERFAMILY_EVIDENCE = {
    "reference": "ARO:3004575",
    "snippet": (
        "Members of the radical SAM superfamily are involved in a wide variety "
        "of reactions, including unusual methylations, isomerization, sulfur "
        "insertion, ring formation, anaerobic oxidation, and protein radical "
        "formation."
    ),
    "notes": "CARD definition for the S-adenosylmethionine (SAM) superfamily.",
}

CFR_23S_EVIDENCE = {
    "reference": "PMID:20007606",
    "snippet": (
        "The Cfr methyltransferase confers combined resistance to five classes "
        "of antibiotics that bind to the peptidyl tranferase center of "
        "bacterial ribosomes by catalyzing methylation of the C-8 position of "
        "23S rRNA nucleotide A2503."
    ),
    "notes": "Evidence for Cfr-type 23S rRNA A2503 methylation.",
}

PFAM_RADICAL_SAM_EVIDENCE = {
    "reference": "Pfam:PF04055",
    "snippet": "Radical SAM superfamily",
    "notes": "Pfam family for radical-SAM domains.",
}

CATH_RADICAL_SAM_EVIDENCE = {
    "reference": "CATH:3.20.20",
    "snippet": "TIM Barrel",
    "notes": "CATH fold for radical-SAM partial TIM-barrel domains.",
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


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": IDENTIFIER,
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    broad_evidence = (
        SAM_SUPERFAMILY_EVIDENCE,
        TARGET_ALTERATION_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        CFR_23S_EVIDENCE,
    )
    domain_evidence = (
        SAM_SUPERFAMILY_EVIDENCE,
        PFAM_RADICAL_SAM_EVIDENCE,
        CFR_23S_EVIDENCE,
    )
    fold_evidence = (
        SAM_SUPERFAMILY_EVIDENCE,
        CATH_RADICAL_SAM_EVIDENCE,
        CFR_23S_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → 23S rRNA methylation → resistance",
        "description": (
            "Curated resistance-causation graph for the radical-SAM "
            "methyltransferase family. The graph models target alteration by "
            "Cfr-type methylation of 23S rRNA in the ribosomal peptidyl "
            "transferase center."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic target alteration",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001001",
            },
            {
                "node_id": "mech1",
                "label": "ribosomal alteration conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000211",
            },
            {
                "node_id": "domain",
                "label": "radical-SAM methyltransferase domain",
                "node_type": "DOMAIN",
                "grounding": "Pfam:PF04055",
                "description": (
                    "Radical-SAM domain that supports Cfr-type 23S rRNA "
                    "methyltransferase activity."
                ),
            },
            {
                "node_id": "fold",
                "label": "radical-SAM partial TIM-barrel fold",
                "node_type": "DOMAIN",
                "grounding": "CATH:3.20.20",
                "description": "Partial TIM-barrel fold adopted by radical-SAM enzymes.",
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this radical-SAM methyltransferase family "
                "under antibiotic target alteration.",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic target alteration changes the ribosomal target so "
                "that the drug binds less effectively.",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies this family under ribosomal alteration.",
                *broad_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Cfr-type methylation chemically alters 23S rRNA in the "
                "ribosome and causes resistance to antibiotics that target it.",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The radical-SAM methyltransferase determinant methylates the "
                "ribosomal peptidyl transferase center, altering the antibiotic "
                "target.",
                *broad_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The radical-SAM methyltransferase domain is part of the "
                "resistance determinant.",
                *domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the radical-SAM partial TIM-barrel fold.",
                *fold_evidence,
            ),
            _edge(
                "domain",
                "enables (23S rRNA A2503 methylation)",
                "RO:0002327",
                "mech1",
                "The radical-SAM methyltransferase domain enables Cfr-type "
                "A2503 methylation of 23S rRNA.",
                *domain_evidence,
            ),
        ],
    }


def _validate_record(record: dict[str, Any]) -> None:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{FILENAME}: expected {IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{IDENTIFIER}: missing label")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "mech1", "domain", "fold", "resistance"} - node_ids
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
        help="S-adenosylmethionine SAM superfamily YAML file",
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
