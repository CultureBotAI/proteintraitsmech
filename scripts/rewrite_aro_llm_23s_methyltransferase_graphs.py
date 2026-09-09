#!/usr/bin/env python3
"""Rewrite Llm-family 23S rRNA methyltransferase graphs.

The auto-drafted Llm graphs borrowed Cfr-specific radical-SAM/A2503 details.
LlmA is instead RlmK-like and was identified as a Paenibacillus sp. LC231
clindamycin-resistance determinant. This updater keeps only the supported
23S-rRNA target-alteration mechanism and the ARO lincosamide drug-class edge.

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

HISTORY_ACTION = "Replaced Llm 23S rRNA methyltransferase graph"
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
    title_prefix: str


TARGETS = (
    Target(
        "ARO:3004273",
        "llm-23s-ribosomal-rna-methyltransferase-aro3004273.yaml",
        "Llm 23S ribosomal RNA methyltransferase",
    ),
    Target(
        "ARO:3003982",
        "llma-23s-ribosomal-rna-methyltransferase-aro3003982.yaml",
        "LlmA 23S ribosomal RNA methyltransferase",
    ),
)
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS}
TARGET_BY_IDENTIFIER = {target.identifier: target for target in TARGETS}

LLM_FAMILY_EVIDENCE = {
    "reference": "ARO:3004273",
    "snippet": (
        "A family of lincosamide resistant 23S rRNA methyltransferases. The only member of "
        "the family discovered so far was isolated from Paenibacillus sp. LC231, a strain "
        "found in Lechuguilla Cave, NM, USA."
    ),
    "notes": "CARD definition for the Llm 23S ribosomal RNA methyltransferase family.",
}

METHYLTRANSFERASE_PARENT_EVIDENCE = {
    "reference": "ARO:3004274",
    "snippet": (
        "Methyltransferases that modify the 23S rRNA of the 50S subunit of bacterial "
        "ribosomes, conferring resistance to drugs that target 23S rRNA."
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
        "Mutational alteration or enzymatic modification of antibiotic target which results "
        "in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target alteration.",
}

RIBOSOMAL_ALTERATION_EVIDENCE = {
    "reference": "ARO:3000211",
    "snippet": (
        "Chemical alteration of the ribosome results in modification of an antibiotic's "
        "target leading to resistance."
    ),
    "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
}

GO_RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of the transfer of a methyl group from S-adenosyl-L-methionine to a "
        "nucleoside residue in an rRNA molecule."
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
        "Sequence Ontology definition for the broad rRNA superclass used as a conservative "
        "grounding for local 16S/23S rRNA antibiotic-binding sites."
    ),
}

DRUG_RELATION_EVIDENCE = {
    "reference": "ARO:3004273",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000017 ! lincosamide antibiotic",
    "notes": "ARO drug-class relationship asserted on the Llm family term.",
}

LINCOSAMIDE_EVIDENCE = {
    "reference": "ARO:0000017",
    "snippet": "lincosamide antibiotic",
    "notes": "ARO drug-class term targeted by the Llm family.",
}

PUBLISHED_LLM_EVIDENCE = {
    "reference": "DOI:10.1038/ncomms13803",
    "notes": "PMID:27929110; Pawlowski et al. 2016 identified LlmA in Paenibacillus sp. LC231.",
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
        "label": "23S rRNA methyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008649",
        "description": (
            "Grounded to the broad GO rRNA methyltransferase activity term because the "
            "ARO evidence scopes this local activity to 23S rRNA."
        ),
    },
    {
        "node_id": "target_site",
        "label": "23S rRNA lincosamide-binding site",
        "node_type": "NUCLEIC_ACID",
        "grounding": "SO:0000252",
        "description": (
            "Conservative local site for the 23S rRNA region altered by Llm-family "
            "methyltransferases; grounded to broad rRNA because the exact nucleotide "
            "target is not asserted in ARO."
        ),
    },
    {
        "node_id": "methylated",
        "label": "methylated 23S rRNA lincosamide-binding site",
        "node_type": "STATE",
        "grounding": "SO:0000252",
        "description": (
            "Local state representing methylation of a 23S rRNA lincosamide-binding site. "
            "Grounded to broad rRNA because no stable narrow term is available for the "
            "putative Llm-family methylation site."
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
        "label": "lincosamide antibiotic",
        "node_type": "CHEMICAL",
        "grounding": "ARO:0000017",
    },
    {
        "node_id": "resistance",
        "label": "antibiotic resistance phenotype",
        "node_type": "PHENOTYPE",
        "grounding": "GO:0046677",
        "description": (
            "Resistance phenotype conferred by this determinant. Grounded to the nearest "
            "available superclass: ARO models determinants and mechanisms but has no term "
            "for the resistance phenotype itself."
        ),
    },
)

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies Llm-family 23S rRNA methyltransferases under antibiotic target "
        "alteration because they enzymatically modify the rRNA target."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Target alteration is the broad resistance mechanism represented by Llm-family "
        "23S rRNA methylation."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "CARD also classifies Llm-family 23S rRNA methyltransferases under the "
        "ribosome-specific target-alteration mechanism."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Chemical alteration of the ribosome is the ribosome-specific route represented "
        "by Llm-family 23S rRNA methylation."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Llm-family determinants confer lincosamide resistance through 23S rRNA "
        "methyltransferase activity."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the Llm family to lincosamide antibiotic resistance."
    ),
    ("determinant", "RO:0002327", "methyltransferase"): (
        "The determinant enables methyl transfer onto nucleoside residues in 23S rRNA."
    ),
    ("methyltransferase", "RO:0002411", "methylated"): (
        "23S rRNA methyltransferase activity yields a methylated 23S rRNA "
        "lincosamide-binding site."
    ),
    ("methylated", "RO:0002212", "target_site"): (
        "Methylation changes the 23S rRNA lincosamide-binding site and prevents normal "
        "drug binding."
    ),
    ("methylated", "RO:0002411", "resistance"): (
        "The methylated 23S rRNA lincosamide-binding site is the terminal modeled cause "
        "of the resistance phenotype."
    ),
    ("target_site", "BFO:0000050", "subunit"): (
        "The altered lincosamide target is a site in 23S rRNA in the 50S ribosomal "
        "subunit."
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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
    )


def _definition_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record["definition"]).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def _family_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == "ARO:3004273":
        return ()
    return (LLM_FAMILY_EVIDENCE,)


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


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    return {key: value for key, value in ordered.items() if value is not None}


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
            "evidence": _unique_evidence(evidence),
        }
    )


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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }
    expected_nodes = {
        "determinant",
        "mech0",
        "mech1",
        "methyltransferase",
        "target_site",
        "methylated",
        "subunit",
        "drug0",
        "resistance",
    }
    missing_nodes = sorted(expected_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"generated graph missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
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


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target_evidence = _definition_evidence(record)
    family_evidence = _family_evidence(record)
    source_evidence = _source_evidence(record) or (PUBLISHED_LLM_EVIDENCE,)
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
        LINCOSAMIDE_EVIDENCE,
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
            "negatively regulates (blocks antibiotic binding)",
            "RO:0002212",
            "target_site",
            target_site_evidence,
        ),
        _edge(
            "methylated",
            "causally upstream of (blocks antibiotic binding)",
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


def _target_for_record(record: dict[str, Any]) -> Target:
    identifier = str(record.get("identifier") or "")
    try:
        return TARGET_BY_IDENTIFIER[identifier]
    except KeyError as exc:
        raise ValueError(f"not an Llm-family 23S rRNA methyltransferase target: {identifier}") from exc


def enrich_record(record: dict[str, Any], target: Target | None = None) -> tuple[dict[str, Any], bool]:
    target = target or _target_for_record(record)
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graph["title"] = f"{target.title_prefix} → 23S rRNA methylation → lincosamide resistance"
    graph["description"] = (
        "Conservative Llm-family resistance graph for RlmK-like 23S rRNA methyltransferases. "
        "The graph models lincosamide resistance via methylation of a 23S rRNA antibiotic-target "
        "site without assuming the Cfr radical-SAM domain, the Cfr partial TIM-barrel fold, or a "
        "specific modified nucleotide."
    )
    graph["nodes"] = _nodes(out)
    graph["edges"] = _canonical_edges(out)
    _validate_graph(graph)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = _target_for_record(record)
    if path.name != target.filename:
        raise ValueError(f"{path}: target {target.identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = text
    if changed:
        out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, out != text


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
        help="ARO directory or one Llm-family YAML file",
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
