#!/usr/bin/env python3
"""Curate Eis overexpression aminoglycoside-acetylation ARO graphs.

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

HISTORY_ACTION = "Curated Eis kanamycin acetylation graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
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

EIS_PARENT_EVIDENCE = {
    "reference": "ARO:3004961",
    "snippet": "Mutations in the eis gene that can contribute to antibiotic resistance.",
    "notes": "CARD definition for antibiotic resistant eis.",
}

KANAMYCIN_EIS_EVIDENCE = {
    "reference": "ARO:3004962",
    "snippet": (
        "Eis is involved in acetylation and kanamycin-resistant eis is CARD-linked "
        "to aminoglycoside resistance."
    ),
    "notes": "CARD definition and drug-class relation for kanamycin resistant eis.",
}

MTUB_EIS_EVIDENCE = {
    "reference": "ARO:3004963",
    "snippet": "Mutations in eis that contribute to or confer resistance to kanamycin.",
    "notes": "CARD definition for M. tuberculosis eis kanamycin resistance.",
}

ZAUNBRECHER_PROMOTER_EVIDENCE = {
    "reference": "PMID:19906990",
    "snippet": (
        "Zaunbrecher et al. identified M. tuberculosis eis promoter mutations "
        "that increased eis leaderless mRNA 20- to 180-fold, increased Eis protein "
        "expression, and conferred low-level kanamycin resistance."
    ),
    "notes": "Experimental evidence for eis promoter mutations that overexpress Eis.",
}

ZAUNBRECHER_ACTIVITY_EVIDENCE = {
    "reference": "PMID:19906990",
    "snippet": (
        "Zaunbrecher et al. measured increased acetyltransferase activity in eis "
        "promoter-mutant M. tuberculosis strains and showed that Eis acetylates "
        "kanamycin."
    ),
    "notes": "Experimental evidence that Eis overexpression raises kanamycin acetylation.",
}

ACYLATION_EVIDENCE = {
    "reference": "ARO:3000106",
    "snippet": "Addition of an acyl group to an antibiotic, often via acetylation by acetylCoA.",
    "notes": "CARD definition for acylation of antibiotic conferring resistance.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

GO_ACETYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016407",
    "snippet": "Catalysis of the transfer of an acetyl group to an acceptor molecule.",
    "notes": "GO grounding for the broad acetyltransferase activity node.",
}

ACETYL_COA_EVIDENCE = {
    "reference": "CHEBI:15351",
    "snippet": "Acetyl-CoA is an acyl-CoA having acetyl as its S-acetyl component.",
    "notes": "ChEBI grounding for the acetyl-CoA input.",
}

AMINOGLYCOSIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3004962",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000016 ! aminoglycoside antibiotic",
    "notes": (
        "CARD asserts this aminoglycoside drug-class relation on the kanamycin-resistant "
        "eis parent."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

OVEREXPRESSION_NODE = {
    "node_id": "overexpression",
    "label": "increased Eis expression",
    "node_type": "STATE",
    "description": (
        "Local state for eis promoter mutations that increase Eis transcript and "
        "protein abundance."
    ),
}

TRANSFER_NODE = {
    "node_id": "acetylation",
    "label": "Eis aminoglycoside acetyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016407",
    "description": (
        "Grounded to broad GO acetyltransferase activity and scoped here to "
        "Eis-catalyzed kanamycin acetylation."
    ),
}

ACETYL_COA_NODE = {
    "node_id": "acetyl_coa",
    "label": "acetyl-CoA",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15351",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "aminoglycoside antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000016",
}

ACETYLATED_NODE = {
    "node_id": "acetylated",
    "label": "acetylated inactive aminoglycoside",
    "node_type": "STATE",
    "description": "Local state for kanamycin after Eis-mediated acetyl transfer from acetyl-CoA.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "kanamycin resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": "Kanamycin resistance phenotype conferred by Eis-mediated drug acetylation.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    source_evidence: tuple[dict[str, str], ...]
    include_direct_drug_edge: bool


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004961",
        "antibiotic-resistant-eis-aro3004961.yaml",
        (EIS_PARENT_EVIDENCE,),
        False,
    ),
    Target(
        "ARO:3004962",
        "kanamycin-resistant-eis-aro3004962.yaml",
        (KANAMYCIN_EIS_EVIDENCE, EIS_PARENT_EVIDENCE),
        True,
    ),
    Target(
        "ARO:3004963",
        "mycobacterium-tuberculosis-eis-mutations-confer-resistance-to-kanamycin-aro3004963.yaml",
        (MTUB_EIS_EVIDENCE, KANAMYCIN_EIS_EVIDENCE, EIS_PARENT_EVIDENCE),
        True,
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
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    source_evidence = (record_evidence, *target.source_evidence)
    promoter_evidence = (
        record_evidence,
        *target.source_evidence,
        MUTATION_EVIDENCE,
        ZAUNBRECHER_PROMOTER_EVIDENCE,
    )
    acetylation_evidence = (
        *target.source_evidence,
        ZAUNBRECHER_ACTIVITY_EVIDENCE,
        GO_ACETYLTRANSFERASE_EVIDENCE,
        ACETYL_COA_EVIDENCE,
    )

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies Eis-mediated kanamycin resistance under mutation conferring antibiotic resistance.",
            *promoter_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of",
            "RO:0002411",
            "overexpression",
            "Resistance mutations in the eis promoter increase Eis transcript and protein abundance.",
            *promoter_evidence,
        ),
        _edge(
            "overexpression",
            "causally upstream of",
            "RO:0002411",
            "acetylation",
            "Increased Eis protein expression raises aminoglycoside acetyltransferase activity.",
            *promoter_evidence,
            ZAUNBRECHER_ACTIVITY_EVIDENCE,
            GO_ACETYLTRANSFERASE_EVIDENCE,
        ),
        _edge(
            "acetylation",
            "has input (the acetyl donor)",
            "RO:0002233",
            "acetyl_coa",
            "Eis uses acetyl-CoA as the donor for kanamycin acetylation.",
            *acetylation_evidence,
        ),
        _edge(
            "acetylation",
            "has input (the drug)",
            "RO:0002233",
            "drug0",
            "Eis acetyltransferase activity acts on kanamycin in the CARD-linked aminoglycoside class.",
            *acetylation_evidence,
            AMINOGLYCOSIDE_RELATION_EVIDENCE,
        ),
        _edge(
            "acetylation",
            "causally upstream of (inactivates the drug)",
            "RO:0002411",
            "acetylated",
            "Eis acetylates kanamycin to produce an inactive acetylated aminoglycoside state.",
            *acetylation_evidence,
            ACYLATION_EVIDENCE,
            ANTIBIOTIC_INACTIVATION_EVIDENCE,
        ),
        _edge(
            "acetylated",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Eis-mediated drug acetylation inactivates kanamycin and confers resistance.",
            *source_evidence,
            ZAUNBRECHER_ACTIVITY_EVIDENCE,
            ACYLATION_EVIDENCE,
            ANTIBIOTIC_INACTIVATION_EVIDENCE,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "eis promoter mutations confer the modeled kanamycin-resistance phenotype.",
            *promoter_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "Eis determinants connect resistance-conferring mutation to increased kanamycin acetylation.",
            *promoter_evidence,
            ZAUNBRECHER_ACTIVITY_EVIDENCE,
        ),
    ]
    if target.include_direct_drug_edge:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that kanamycin-resistant Eis confers resistance to aminoglycoside antibiotics.",
                AMINOGLYCOSIDE_RELATION_EVIDENCE,
                *source_evidence,
            )
        )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → Eis-mediated kanamycin acetylation",
        "description": (
            "Curated resistance-causation graph for Eis promoter mutations that "
            "increase Eis expression and aminoglycoside acetyltransferase activity."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(OVEREXPRESSION_NODE),
            copy.deepcopy(TRANSFER_NODE),
            copy.deepcopy(ACETYL_COA_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(ACETYLATED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": edges,
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(out, target)]
    return out, out["causal_graphs"] != before or out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an Eis target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


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
        help="ARO directory or one of the three Eis YAML files",
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
