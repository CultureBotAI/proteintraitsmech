#!/usr/bin/env python3
"""Rewrite the emtA evernimicin-resistance ARO causal graph.

CARD currently places emtA under the non-erm 23S rRNA methyltransferase family,
so its seeded graph inherited the Cfr-like A2503 radical-SAM path from another
23S methyltransferase branch and macrolide/lincosamide drug edges from the G748
family parent. EmtA was characterized as a high-level evernimicin-resistance
rRNA methyltransferase instead, and the paper maps its 23S rRNA modification to
G2470 in the evernimicin-binding region.

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
TARGET_ID = "ARO:3004669"
TARGET_FILENAME = "emta-aro3004669.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Curated emtA 23S rRNA G2470 methyltransferase graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE = {
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

EMTA_EVIDENCE = {
    "reference": "ARO:3004669",
    "snippet": "A rRNA methyltransferase conferring high-level evernimicin resistance.",
    "notes": "CARD definition for emtA.",
}

EMTA_PUBMED_EVIDENCE = {
    "reference": "PMID:11580839",
    "snippet": "EmtA is a rRNA methyltransferase conferring high-level evernimicin resistance.",
    "notes": (
        "Mann et al. characterized EmtA in Enterococcus faecium and mapped its "
        "23S rRNA methylation to G2470 by reverse transcription."
    ),
}

G2470_BINDING_EVIDENCE = {
    "reference": "PMID:11580839",
    "snippet": "G2470 is located within the evernimicin-binding site on the ribosome.",
    "notes": (
        "The same study used RNA footprinting to link the methylated G2470 "
        "residue to the evernimicin-binding site."
    ),
}

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of methyl-group transfer from S-adenosyl-L-methionine to an rRNA "
        "nucleoside residue."
    ),
    "notes": (
        "GO definition for the broad rRNA methyltransferase activity superclass; "
        "the CARD/PubMed evidence constrains the substrate to 23S rRNA G2470."
    ),
}

SO_RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide structural "
        "scaffolding and catalytic activity."
    ),
    "notes": (
        "Sequence Ontology definition for the broad rRNA superclass used as a "
        "conservative grounding for the local 23S rRNA G2470 site."
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

MECHANISM_NODES = [
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
        "node_id": "methyltransferase",
        "label": "23S rRNA G2470 methyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008649",
        "description": (
            "Grounded to the broad GO rRNA methyltransferase activity term "
            "because no stable narrow GO term is available for EmtA methylation "
            "of 23S rRNA G2470."
        ),
    },
]

G2470_TARGET_SITE_NODE = {
    "node_id": "target_site",
    "label": "23S rRNA G2470 evernimicin-binding site",
    "node_type": "NUCLEIC_ACID",
    "grounding": "SO:0000252",
    "description": (
        "Local node for guanosine 2470 of 23S rRNA. Grounded to broad rRNA "
        "because no stable narrow term is available for this local "
        "evernimicin-binding site."
    ),
}

METHYLATED_SITE_NODE = {
    "node_id": "methylated",
    "label": "methylated 23S rRNA G2470 site",
    "node_type": "STATE",
    "grounding": "SO:0000252",
    "description": (
        "Local state representing EmtA methylation of 23S rRNA G2470. Grounded "
        "to broad rRNA because no stable narrow term is available for this "
        "methylated local state."
    ),
}

SUBUNIT_NODE = {
    "node_id": "subunit",
    "label": "large ribosomal subunit (50S)",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0015934",
    "description": "The 50S subunit that contains bacterial 23S rRNA.",
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
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    activity_evidence = (
        EMTA_EVIDENCE,
        EMTA_PUBMED_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
    )
    g2470_evidence = (
        EMTA_EVIDENCE,
        EMTA_PUBMED_EVIDENCE,
        G2470_BINDING_EVIDENCE,
        SO_RRNA_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": "emtA → 23S rRNA G2470 methylation → evernimicin resistance",
        "description": (
            "Curated resistance-causation graph for EmtA. The graph models EmtA "
            "methylation of a local 23S rRNA G2470 site as the target alteration "
            "that blocks evernimicin binding at the large ribosomal subunit."
        ),
        "nodes": [
            _determinant_node(record),
            *(copy.deepcopy(node) for node in MECHANISM_NODES),
            copy.deepcopy(G2470_TARGET_SITE_NODE),
            copy.deepcopy(METHYLATED_SITE_NODE),
            copy.deepcopy(SUBUNIT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "EmtA is an rRNA methyltransferase that enzymatically modifies a "
                "23S rRNA target site.",
                EMTA_EVIDENCE,
                EMTA_PUBMED_EVIDENCE,
                ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Target alteration is the broad resistance mechanism represented "
                "by EmtA methylation of the 23S rRNA G2470 site.",
                EMTA_EVIDENCE,
                EMTA_PUBMED_EVIDENCE,
                ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "EmtA modifies bacterial 23S rRNA, so its target alteration is "
                "modeled as a ribosomal alteration.",
                EMTA_EVIDENCE,
                EMTA_PUBMED_EVIDENCE,
                RIBOSOMAL_ALTERATION_EVIDENCE,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Methylation of 23S rRNA G2470 is a ribosomal alteration that "
                "supports evernimicin resistance.",
                EMTA_EVIDENCE,
                EMTA_PUBMED_EVIDENCE,
                RIBOSOMAL_ALTERATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "EmtA methylates 23S rRNA G2470, producing a modified "
                "evernimicin-binding region.",
                EMTA_EVIDENCE,
                EMTA_PUBMED_EVIDENCE,
                G2470_BINDING_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "methyltransferase",
                "The EmtA determinant enables methylation of 23S rRNA G2470.",
                *activity_evidence,
            ),
            _edge(
                "methyltransferase",
                "causally upstream of",
                "RO:0002411",
                "methylated",
                "EmtA methyltransferase activity yields a methylated 23S rRNA "
                "G2470 state.",
                *activity_evidence,
            ),
            _edge(
                "methylated",
                "negatively regulates (blocks evernimicin binding)",
                "RO:0002212",
                "target_site",
                "Methylation of G2470 changes the evernimicin-binding site in "
                "23S rRNA and reduces drug binding.",
                *g2470_evidence,
            ),
            _edge(
                "methylated",
                "causally upstream of (blocks evernimicin binding)",
                "RO:0002411",
                "resistance",
                "The methylated 23S rRNA G2470 state is the terminal modeled "
                "target alteration supporting resistance.",
                *g2470_evidence,
            ),
            _edge(
                "target_site",
                "part of",
                "BFO:0000050",
                "subunit",
                "The G2470 target site is in 23S rRNA in the 50S ribosomal subunit.",
                *g2470_evidence,
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
    missing_nodes = {"determinant", "mech0", "mech1", "resistance"} - node_ids
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
        help="ARO directory or emtA YAML file",
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
