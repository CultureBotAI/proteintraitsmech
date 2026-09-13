#!/usr/bin/env python3
"""Rewrite the 23S rRNA macrolide-resistance mutation ARO graph.

The macrolide-specific 23S rRNA mutation record had a literature-rich graph but
kept an ungrounded peptidyl-transferase-loop node.  This updater follows the
generic 23S rRNA mutation pattern: it grounds the local antibiotic-binding site
to the broad Sequence Ontology rRNA term, represents the reduced-binding
conformation as a local state, preserves the macrolide drug edge, and keeps the
site-level Douthwaite/Aagaard evidence.

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

TARGET_IDENTIFIER = "ARO:3004125"
TARGET_FILENAME = (
    "23s-rrna-with-mutation-conferring-resistance-to-macrolide-antibiotics-"
    "aro3004125.yaml"
)

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Completed 23S rRNA macrolide-resistance mutation graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

RRNA_PARENT_EVIDENCE = {
    "reference": "ARO:3000336",
    "snippet": (
        "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity "
        "at specific sites, conferring resistance."
    ),
    "notes": "CARD definition for the 23S rRNA mutation parent term.",
}

RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both "
        "structural scaffolding and catalytic activity."
    ),
    "notes": "Sequence Ontology definition for the broad rRNA superclass.",
}

MACROLIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3004125",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000000 ! macrolide antibiotic",
    "notes": "Macrolide drug-class relation asserted directly on ARO:3004125.",
}

DOUTHWAITE_EVIDENCE = {
    "reference": "PMID:7689111",
    "snippet": (
        "Erythromycin still protects against chemical modification in the "
        "mutant peptidyl transferase loops, but the affinity of the drug "
        "interaction is reduced 20-fold in the 2057A mutant, 10(3)-fold in "
        "the 2058U mutant and 10(4)-fold in the 2058G mutant."
    ),
    "notes": (
        "Direct 23S peptidyl-transferase-loop evidence for reduced "
        "erythromycin interaction."
    ),
}

LOOP_BINDING_EVIDENCE = {
    "reference": "PMID:7689111",
    "snippet": (
        "The antibiotic erythromycin inhibits protein synthesis by binding to "
        "the 50 S ribosomal subunit, where the drug interacts with the "
        "unpaired bases 2058A and 2059A in the peptidyl transferase loop of "
        "23 S rRNA."
    ),
    "notes": "Direct evidence for erythromycin interaction with the 23S rRNA loop.",
}

REVIEW_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.45.1.1-12.2001",
    "notes": "PMID:11120937 (aro citation)",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

MACROLIDE_NODE = {
    "node_id": "drug0",
    "label": "macrolide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000000",
}

BINDING_SITE_NODE = {
    "node_id": "binding_site",
    "label": "23S rRNA macrolide-binding site",
    "node_type": "NUCLEIC_ACID",
    "grounding": "SO:0000252",
    "description": (
        "Grounded to the broad Sequence Ontology rRNA term because no stable "
        "narrow term is available for the local 23S peptidyl-transferase-loop "
        "macrolide-binding site modeled here."
    ),
}

ALTERED_SITE_NODE = {
    "node_id": "altered_site",
    "label": "reduced macrolide binding affinity at the mutated 23S site",
    "node_type": "STATE",
    "description": (
        "Local state for 23S rRNA peptidyl-transferase-loop mutations that "
        "reduce erythromycin binding affinity."
    ),
}

SUBUNIT_NODE = {
    "node_id": "subunit",
    "label": "large ribosomal subunit (50S)",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0015934",
    "description": "The 50S subunit that contains bacterial 23S rRNA.",
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
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (
            item["reference"],
            item.get("snippet", ""),
        )
        if key in seen:
            continue
        seen.add(key)
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    mutation_evidence = (
        record_evidence,
        RRNA_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        DOUTHWAITE_EVIDENCE,
        REVIEW_EVIDENCE,
    )
    site_evidence = (
        record_evidence,
        RRNA_PARENT_EVIDENCE,
        RRNA_EVIDENCE,
        DOUTHWAITE_EVIDENCE,
        LOOP_BINDING_EVIDENCE,
    )
    drug_evidence = (
        record_evidence,
        MACROLIDE_RELATION_EVIDENCE,
        DOUTHWAITE_EVIDENCE,
        LOOP_BINDING_EVIDENCE,
        REVIEW_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced 23S macrolide binding",
        "description": (
            "Curated resistance-causation graph for 23S rRNA point mutations "
            "that reduce macrolide binding at the peptidyl-transferase loop "
            "and thereby confer macrolide resistance."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "NUCLEIC_ACID",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(MACROLIDE_NODE),
            copy.deepcopy(BINDING_SITE_NODE),
            copy.deepcopy(ALTERED_SITE_NODE),
            copy.deepcopy(SUBUNIT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies this 23S rRNA term under mutation conferring "
                "antibiotic resistance.",
                *mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism captures 23S rRNA sequence "
                "changes that reduce macrolide binding.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Mutated 23S rRNA peptidyl-transferase-loop determinants "
                "reduce macrolide affinity and confer resistance.",
                *mutation_evidence,
                LOOP_BINDING_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a macrolide-antibiotic drug-class relation on "
                "this 23S rRNA mutation term.",
                *drug_evidence,
            ),
            _edge(
                "binding_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The macrolide-binding peptidyl-transferase loop is modeled "
                "inside the mutated 23S rRNA.",
                *site_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "subunit",
                "The mutated 23S rRNA is part of the bacterial 50S ribosomal "
                "subunit.",
                record_evidence,
                RRNA_PARENT_EVIDENCE,
                RRNA_EVIDENCE,
            ),
            _edge(
                "drug0",
                "molecularly interacts with (binds the 23S rRNA site)",
                "RO:0002436",
                "binding_site",
                "Macrolides bind at the peptidyl-transferase loop of 23S rRNA.",
                *drug_evidence,
                RRNA_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (alters macrolide binding)",
                "RO:0002411",
                "altered_site",
                "Point mutations in the 23S rRNA peptidyl-transferase loop "
                "produce a local state with reduced erythromycin binding.",
                *site_evidence,
            ),
            _edge(
                "altered_site",
                "negatively regulates (reduces macrolide binding)",
                "RO:0002212",
                "binding_site",
                "The altered 23S rRNA loop reduces macrolide binding affinity "
                "at the site.",
                *site_evidence,
            ),
            _edge(
                "altered_site",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Reduced binding at the mutated 23S rRNA site is the terminal "
                "modeled cause of macrolide resistance.",
                *site_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"expected {TARGET_IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{TARGET_IDENTIFIER}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "drug0", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{TARGET_IDENTIFIER}: missing node(s): {missing_ids}")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"{path}: not a 23S rRNA macrolide mutation target")
    if path.name != TARGET_FILENAME:
        raise ValueError(f"{path}: target must be in {TARGET_FILENAME}")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
        help="ARO directory or the exact 23S rRNA macrolide YAML file",
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
