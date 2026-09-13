#!/usr/bin/env python3
"""Rewrite A1067-specific 23S rRNA methyltransferase ARO graphs.

The previous graphs for the non-erm A1067 parent and tsnR inherited Cfr/A2503
radical-SAM details.  These records instead assert 23S rRNA A1067 methylation
and peptide-antibiotic resistance, so this updater keeps the supported 23S rRNA
methyltransferase target-alteration model without claiming a radical-SAM
domain or A2503 chemistry.

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

HISTORY_ACTION = "Replaced A1067 23S rRNA methyltransferase graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3003065",
        "non-erm-23s-ribosomal-rna-methyltransferase-a1067-aro3003065.yaml",
    ),
    Target("ARO:3003060", "tsnr-aro3003060.yaml"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

PARENT_IDENTIFIER = "ARO:3003065"

A1067_PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Non-erm 23S ribosomal RNA methyltransferases modify adenosine 1067 "
        "to confer resistance to peptide antibiotics."
    ),
    "notes": "CARD definition for non-erm 23S ribosomal RNA methyltransferase (A1067).",
}

METHYLTRANSFERASE_PARENT_EVIDENCE = {
    "reference": "ARO:3004274",
    "snippet": (
        "Methyltransferases that modify the 23S rRNA of the 50S subunit of "
        "bacterial ribosomes, conferring resistance to drugs that target 23S rRNA."
    ),
    "notes": "CARD definition for the 23S ribosomal RNA methyltransferase parent term.",
}

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "ARO:3000164",
    "snippet": "Catalyzes methylation of rRNA.",
    "notes": "CARD definition for the rRNA methyltransferase parent term.",
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

GO_RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of the transfer of a methyl group from "
        "S-adenosyl-L-methionine to a nucleoside residue in an rRNA molecule."
    ),
    "notes": "GO definition for broad rRNA methyltransferase activity.",
}

SO_RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both structural "
        "scaffolding and catalytic activity."
    ),
    "notes": (
        "Sequence Ontology definition for the broad rRNA superclass used as a "
        "conservative grounding for the local 23S rRNA A1067 site."
    ),
}

DRUG_RELATION_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": (
        "Peptide-antibiotic drug-class relation asserted on ARO:3003065 and "
        "inherited by its child records."
    ),
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term targeted by A1067-specific 23S rRNA methyltransferases.",
}

MECHANISM_NODES = (
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
        "label": "23S rRNA A1067 methyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008649",
        "description": (
            "Grounded to the broad GO rRNA methyltransferase activity term and "
            "scoped here to 23S rRNA A1067 methylation."
        ),
    },
    {
        "node_id": "target_site",
        "label": "23S rRNA A1067 peptide-antibiotic-binding site",
        "node_type": "NUCLEIC_ACID",
        "grounding": "SO:0000252",
        "description": (
            "Conservative local 23S rRNA site centered on A1067; grounded to "
            "broad rRNA because no stable narrow term is available for this "
            "local peptide-antibiotic target site."
        ),
    },
    {
        "node_id": "methylated",
        "label": "methylated 23S rRNA A1067 peptide-antibiotic-binding site",
        "node_type": "STATE",
        "grounding": "SO:0000252",
        "description": (
            "Local state representing methylation of the 23S rRNA A1067 "
            "peptide-antibiotic target site. Grounded to broad rRNA because no "
            "stable narrow term is available for this methylated local state."
        ),
    },
    {
        "node_id": "subunit",
        "label": "large ribosomal subunit (50S)",
        "node_type": "CELLULAR_LOCALIZATION",
        "grounding": "GO:0015934",
        "description": "The 50S subunit that contains bacterial 23S rRNA.",
    },
    {
        "node_id": "drug0",
        "label": "peptide antibiotic",
        "node_type": "CHEMICAL",
        "grounding": "ARO:3000053",
    },
    {
        "node_id": "resistance",
        "label": "antibiotic resistance phenotype",
        "node_type": "PHENOTYPE",
        "grounding": "GO:0046677",
        "description": (
            "Resistance phenotype conferred by this determinant. Grounded to "
            "the nearest available superclass: ARO models determinants and "
            "mechanisms but has no term for the resistance phenotype itself."
        ),
    },
)

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies A1067-specific 23S rRNA methyltransferases under "
        "antibiotic target alteration because they enzymatically modify 23S rRNA."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic target alteration is the broad resistance mechanism "
        "represented by A1067-specific 23S rRNA methylation."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "CARD also classifies A1067-specific 23S rRNA methyltransferases under "
        "ribosomal alteration."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Chemical alteration of the ribosome is the ribosome-specific route "
        "represented by A1067-specific 23S rRNA methylation."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The determinant confers peptide-antibiotic resistance through "
        "methylation of 23S rRNA A1067."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps A1067-specific 23S rRNA methyltransferases to peptide "
        "antibiotic resistance."
    ),
    ("determinant", "RO:0002327", "methyltransferase"): (
        "The determinant enables methyl transfer onto adenosine 1067 in 23S rRNA."
    ),
    ("methyltransferase", "RO:0002411", "methylated"): (
        "A1067 methyltransferase activity yields a methylated 23S rRNA "
        "peptide-antibiotic target site."
    ),
    ("methylated", "RO:0002212", "target_site"): (
        "Methylation changes the local 23S rRNA A1067 site and prevents normal "
        "peptide-antibiotic binding."
    ),
    ("methylated", "RO:0002411", "resistance"): (
        "The methylated A1067-containing 23S rRNA site is the terminal modeled "
        "cause of peptide-antibiotic resistance."
    ),
    ("target_site", "BFO:0000050", "subunit"): (
        "The A1067 site is part of the 23S rRNA in the 50S ribosomal subunit."
    ),
}
EXPECTED_EDGE_KEYS = set(EDGE_DESCRIPTIONS)


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


def _family_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == PARENT_IDENTIFIER:
        return ()
    return (A1067_PARENT_EVIDENCE,)


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
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
        unique.append(copy.deepcopy(item))
    return unique


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


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


def _nodes(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "node_id": "determinant",
            "label": str(record["label"]),
            "node_type": "PROTEIN",
            "grounding": str(record["identifier"]),
        },
        *(copy.deepcopy(node) for node in MECHANISM_NODES),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target_evidence = _definition_evidence(record)
    family_evidence = _family_evidence(record)
    source_evidence = _source_evidence(record)
    mechanism_evidence = (
        target_evidence,
        *family_evidence,
        METHYLTRANSFERASE_PARENT_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        *source_evidence,
    )
    target_alteration_evidence = (
        *mechanism_evidence,
        TARGET_ALTERATION_EVIDENCE,
    )
    ribosomal_alteration_evidence = (
        *mechanism_evidence,
        RIBOSOMAL_ALTERATION_EVIDENCE,
    )
    resistance_evidence = (
        *mechanism_evidence,
        TARGET_ALTERATION_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
    )
    methylation_evidence = (
        *mechanism_evidence,
        GO_RRNA_METHYLTRANSFERASE_EVIDENCE,
        SO_RRNA_EVIDENCE,
    )
    target_site_evidence = (
        *mechanism_evidence,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        GO_RRNA_METHYLTRANSFERASE_EVIDENCE,
        SO_RRNA_EVIDENCE,
    )
    drug_evidence = (
        target_evidence,
        *family_evidence,
        DRUG_RELATION_EVIDENCE,
        PEPTIDE_ANTIBIOTIC_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            target_alteration_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            target_alteration_evidence,
        ),
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech1",
            ribosomal_alteration_evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            ribosomal_alteration_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            resistance_evidence,
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
            "methyltransferase",
            methylation_evidence,
        ),
        _edge(
            "methyltransferase",
            "causally upstream of",
            "RO:0002411",
            "methylated",
            methylation_evidence,
        ),
        _edge(
            "methylated",
            "negatively regulates (blocks peptide-antibiotic binding)",
            "RO:0002212",
            "target_site",
            target_site_evidence,
        ),
        _edge(
            "methylated",
            "causally upstream of (blocks peptide-antibiotic binding)",
            "RO:0002411",
            "resistance",
            target_site_evidence,
        ),
        _edge(
            "target_site",
            "part of",
            "BFO:0000050",
            "subunit",
            target_site_evidence,
        ),
    ]


def _validate_graph(graph: dict[str, Any]) -> None:
    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"generated graph has unexpected edge {key}")
        if key in seen:
            raise ValueError(f"generated graph has duplicate edge {key}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"generated graph missing edge(s): {missing}")


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    graph = {
        "graph_id": "resistance",
        "title": f"{record['label']} → methylated 23S rRNA A1067",
        "description": (
            "Curated resistance-causation graph for A1067-specific 23S rRNA "
            "methyltransferases. The determinant methylates adenosine 1067 in "
            "23S rRNA, chemically altering a peptide-antibiotic target site in "
            "the 50S ribosomal subunit."
        ),
        "nodes": _nodes(record),
        "edges": _canonical_edges(record),
    }
    _validate_graph(graph)
    return graph


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an A1067 23S rRNA methyltransferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the two A1067 23S rRNA methyltransferase YAML files",
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
