#!/usr/bin/env python3
"""Rewrite Borreliella 16S rRNA mutation causal graphs.

These records are 16S rRNA target-site mutations selected in Borreliella
burgdorferi.  The gentamicin and kanamycin records affect the 3' minor domain;
the spectinomycin record affects the 3' major domain.  This updater replaces
the old generic A1408 decoding-site graph with the corrected, grounded
antibiotic-binding-site shape used by the curated 16S rRNA mutation parent.

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
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed Borreliella 16S rRNA aminoglycoside target-site graphs",
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

PARENT_EVIDENCE = {
    "reference": "ARO:3003666",
    "snippet": "Point mutations in the 16S rRNA of bacteria can confer resistance to aminoglycosides.",
    "notes": "CARD definition for the 16S rRNA aminoglycoside mutation parent.",
}

RRNA_MUTATION_EVIDENCE = {
    "reference": "ARO:3003211",
    "snippet": (
        "Point mutations in the bacterial 16S ribosomal RNA in the small 30S "
        "subunit can confer resistance to antibiotics."
    ),
    "notes": "CARD definition for the 16S rRNA mutation term.",
}

RRNA_BINDING_SITE_EVIDENCE = {
    "reference": "ARO:3003211",
    "snippet": (
        "The antibiotic-binding sites are located within functionally important "
        "structures in the ribosomal RNA. Antibiotic resistance is often conferred "
        "by base substitutions or methylations at these sites in the rRNA."
    ),
    "notes": "CARD support for 16S rRNA binding-site alteration.",
}

RRNA_PARENT_EVIDENCE = {
    "reference": "ARO:3000328",
    "snippet": (
        "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic "
        "resistance to drugs that target the bacterial ribosome."
    ),
    "notes": "CARD definition for the rRNA mutation parent term.",
}

SO_RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both structural "
        "scaffolding and catalytic activity."
    ),
    "notes": "Sequence Ontology definition for the broad rRNA superclass.",
}

SMALL_SUBUNIT_EVIDENCE = {
    "reference": "GO:0015935",
    "snippet": "small ribosomal subunit",
    "notes": "GO grounding for the small ribosomal subunit.",
}

BORRELIA_PAPER_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.50.2.445-452.2006",
    "notes": (
        "Criswell et al. selected B. burgdorferi mutants resistant to "
        "spectinomycin, kanamycin, and gentamicin and mapped the resistance "
        "mutations to 16S rRNA."
    ),
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

SUBUNIT_NODE = {
    "node_id": "subunit",
    "label": "small ribosomal subunit (30S)",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0015935",
    "description": "The 30S subunit that contains bacterial 16S rRNA.",
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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    binding_site_label: str
    binding_site_description: str


TARGETS: tuple[Target, ...] = (
    Target(
        identifier="ARO:3003504",
        filename="borreliella-burgdorferi-16s-rrna-mutation-conferring-resistance-to-gentamicin-aro3003504.yaml",
        binding_site_label="Borreliella 16S rRNA 3' minor-domain aminoglycoside-binding site",
        binding_site_description=(
            "Grounded to the broad Sequence Ontology rRNA term because no stable "
            "narrow term is available for the 3' minor-domain 16S rRNA site "
            "linked to gentamicin resistance in B. burgdorferi."
        ),
    ),
    Target(
        identifier="ARO:3003503",
        filename="borreliella-burgdorferi-16s-rrna-mutation-conferring-resistance-to-kanamycin-aro3003503.yaml",
        binding_site_label="Borreliella 16S rRNA 3' minor-domain aminoglycoside-binding site",
        binding_site_description=(
            "Grounded to the broad Sequence Ontology rRNA term because no stable "
            "narrow term is available for the 3' minor-domain 16S rRNA site "
            "linked to kanamycin resistance in B. burgdorferi."
        ),
    ),
    Target(
        identifier="ARO:3003502",
        filename="borreliella-burgdorferi-16s-rrna-mutation-conferring-resistance-to-spectinomycin-aro3003502.yaml",
        binding_site_label="Borreliella 16S rRNA 3' major-domain spectinomycin-binding site",
        binding_site_description=(
            "Grounded to the broad Sequence Ontology rRNA term because no stable "
            "narrow term is available for the 3' major-domain 16S rRNA site "
            "linked to spectinomycin resistance in B. burgdorferi."
        ),
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["reference"]), str(item.get("snippet", "")))
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
    *evidence: dict[str, Any],
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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _relation_evidence(old_graph: dict[str, Any]) -> list[dict[str, Any]]:
    for edge in _dicts(old_graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
            and edge.get("object") == "drug0"
        ):
            evidence = [
                item
                for item in _dicts(edge.get("evidence"))
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class "
                )
            ]
            if evidence:
                return evidence
    raise ValueError("missing inherited aminoglycoside drug-class edge evidence")


def _drug_node(old_graph: dict[str, Any]) -> dict[str, Any]:
    for node in _dicts(old_graph.get("nodes")):
        if node.get("node_id") == "drug0":
            return copy.deepcopy(node)
    raise ValueError("missing drug0 node")


def _graph(record: dict[str, Any], target: Target, old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    source_evidence = _source_evidence(record)
    relation_evidence = _relation_evidence(old_graph)
    target_evidence = (
        record_evidence,
        PARENT_EVIDENCE,
        RRNA_BINDING_SITE_EVIDENCE,
        RRNA_PARENT_EVIDENCE,
        SO_RRNA_EVIDENCE,
        BORRELIA_PAPER_EVIDENCE,
        *source_evidence,
    )
    broad_evidence = (
        record_evidence,
        PARENT_EVIDENCE,
        RRNA_MUTATION_EVIDENCE,
        RRNA_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        BORRELIA_PAPER_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → 16S rRNA aminoglycoside target-site alteration",
        "description": (
            "Curated resistance-causation graph for Borreliella burgdorferi 16S "
            "rRNA point mutations that alter local antibiotic-binding sites in "
            "the small ribosomal subunit."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "NUCLEIC_ACID",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECH0_NODE),
            _drug_node(old_graph),
            {
                "node_id": "binding_site",
                "label": target.binding_site_label,
                "node_type": "NUCLEIC_ACID",
                "grounding": "SO:0000252",
                "description": target.binding_site_description,
            },
            copy.deepcopy(SUBUNIT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this 16S rRNA variant under mutation conferring antibiotic resistance.",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism captures rRNA sequence changes that alter ribosomal antibiotic-binding sites.",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The mutated Borreliella 16S rRNA alters an antibiotic-binding site and thereby confers resistance.",
                *broad_evidence,
                *relation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that this 16S rRNA mutation record confers resistance to aminoglycoside antibiotic.",
                *relation_evidence,
                *target_evidence,
            ),
            _edge(
                "binding_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The local antibiotic-binding site is modeled inside the mutated 16S rRNA.",
                *target_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "subunit",
                "The mutated 16S rRNA is part of the small bacterial ribosomal subunit.",
                record_evidence,
                RRNA_MUTATION_EVIDENCE,
                SMALL_SUBUNIT_EVIDENCE,
                SO_RRNA_EVIDENCE,
                BORRELIA_PAPER_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (alters antibiotic-binding site)",
                "RO:0002411",
                "binding_site",
                "Point mutations in the Borreliella 16S rRNA alter the local antibiotic-binding site linked to resistance.",
                *target_evidence,
                *relation_evidence,
            ),
            _edge(
                "drug0",
                "molecularly interacts with",
                "RO:0002436",
                "binding_site",
                "CARD links this drug class to resistance-conferring 16S rRNA binding-site mutations.",
                *relation_evidence,
                *target_evidence,
            ),
            _edge(
                "binding_site",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Alteration of the 16S rRNA antibiotic-binding site lowers effective drug binding and causes resistance.",
                *target_evidence,
                *relation_evidence,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    if _drug_node(graphs[0]).get("grounding") != "ARO:0000016":
        raise ValueError(f"{target.identifier}: expected aminoglycoside drug0 node")
    _relation_evidence(graphs[0])


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)
    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, target, record["causal_graphs"][0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Borreliella 16S rRNA mutation target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the Borreliella 16S rRNA YAML files",
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
