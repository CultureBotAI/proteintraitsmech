#!/usr/bin/env python3
"""Curate VanX D,D-dipeptidase glycopeptide-resistance graphs.

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
ARO = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Curated VanX D,D-dipeptidase glycopeptide graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANX_DEFINITION_EVIDENCE = {
    "reference": "ARO:3000011",
    "snippet": (
        "VanX is a D,D-dipeptidase that cleaves D-Ala-D-Ala but not "
        "D-Ala-D-Lac, ensuring that the latter dipeptide that has reduced "
        "binding affinity with vancomycin is used to synthesize "
        "peptidoglycan substrate."
    ),
    "notes": "CARD definition for vanX.",
}

VANX_MECHANISM_EVIDENCE = {
    "reference": "PMID:7854121",
    "snippet": (
        "These results establish that VanX is required for production of a "
        "D,D-dipeptidase that hydrolyses D-Ala-D-Ala, thereby preventing "
        "pentapeptide synthesis and subsequent binding of glycopeptides to "
        "D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface."
    ),
    "notes": "Reynolds et al. 1994 directly established the VanX causal mechanism.",
}

VANX_LOSS_EVIDENCE = {
    "reference": "PMID:7854121",
    "snippet": (
        "Insertional inactivation of vanX led to increased synthesis of "
        "pentapeptide with a resulting change in the ratio of "
        "pentadepsipeptide: pentapeptide to less than 1:1."
    ),
    "notes": (
        "Reynolds et al. 1994 showed that vanX loss restores the "
        "D-Ala-D-Ala-ending precursor that glycopeptides bind."
    ),
}

VANX_EXPRESSION_EVIDENCE = {
    "reference": "PMID:7854121",
    "snippet": (
        "Expression of vanX in E. faecalis and Escherichia coli resulted in "
        "production of a D,D-dipeptidase that hydrolysed D-Ala-D-Ala."
    ),
    "notes": "Reynolds et al. 1994 expressed vanX heterologously in two hosts.",
}

VANX_SPECIFICITY_EVIDENCE = {
    "reference": "PMID:7854121",
    "snippet": "Pentadepsipeptide, pentapeptide and D-Ala-D-Lac were not substrates for the enzyme.",
    "notes": (
        "Reynolds et al. 1994 showed that VanX destroys the free D-Ala-D-Ala "
        "dipeptide but spares D-Ala-D-Lac and assembled precursors."
    ),
}

GLYCOPEPTIDE_BINDING_EVIDENCE = {
    "reference": "PMID:7854121",
    "snippet": (
        "subsequent binding of glycopeptides to D-Ala-D-Ala-containing "
        "peptidoglycan precursors at the cell surface"
    ),
    "notes": (
        "Reynolds et al. 1994 described the glycopeptide-binding target that "
        "VanX-dependent D-Ala-D-Ala depletion removes."
    ),
}

PFAM_VANX_EVIDENCE = {
    "reference": "Pfam:PF01427",
    "snippet": (
        "This group of metallopeptidases belong to MEROPS peptidase family "
        "M15 (clan MD), subfamily M15D (vanX D-Ala-D-Ala dipeptidase)."
    ),
    "notes": (
        "KB trait record Pfam:PF01427; the InterPro-derived definition names "
        "the VanX M15D D-Ala-D-Ala dipeptidase subfamily."
    ),
}

MOLECULAR_BYPASS_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Mechanism of antibiotic resistance mediated by circumventing or "
        "bypassing the antibiotic target."
    ),
    "notes": "CARD definition for restructuring of bacterial cell wall.",
}

GLYCOPEPTIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3000011",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": "CARD/ARO asserts this glycopeptide-antibiotic drug class on vanX.",
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str


RECORDS = (
    RecordSpec(
        path=ARO / "vanx-aro3000011.yaml",
        identifier="ARO:3000011",
        label="vanX",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vana-cluster-aro3002949.yaml",
        identifier="ARO:3002949",
        label="vanX gene in vanA cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vanb-cluster-aro3002950.yaml",
        identifier="ARO:3002950",
        label="vanX gene in vanB cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vand-cluster-aro3003070.yaml",
        identifier="ARO:3003070",
        label="vanX gene in vanD cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vanf-cluster-aro3002952.yaml",
        identifier="ARO:3002952",
        label="vanX gene in vanF cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vani-cluster-aro3003725.yaml",
        identifier="ARO:3003725",
        label="vanX gene in vanI cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vanm-cluster-aro3002953.yaml",
        identifier="ARO:3002953",
        label="vanX gene in vanM cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vano-cluster-aro3002954.yaml",
        identifier="ARO:3002954",
        label="vanX gene in vanO cluster",
    ),
    RecordSpec(
        path=ARO / "vanx-gene-in-vanp-cluster-aro3007190.yaml",
        identifier="ARO:3007190",
        label="vanX gene in vanP cluster",
    ),
)

EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places VanX in the molecular-bypass cell-wall restructuring mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Cell-wall precursor remodeling replaces the glycopeptide-bound "
        "D-Ala-D-Ala terminus and confers glycopeptide resistance."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "VanX is required for the D,D-dipeptidase activity that depletes "
        "D-Ala-D-Ala and allows resistant D-Ala-D-Lac-ended precursors to dominate."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "CARD asserts that VanX confers resistance to glycopeptide antibiotics."
    ),
    ("domain", "part of (the dipeptidase domain of this determinant)", "determinant"): (
        "The determinant carries a VanX-family M15D metallopeptidase domain."
    ),
    ("domain", "enables (D,D-dipeptidase activity)", "dipeptidase"): (
        "The VanX-family M15D domain provides the D,D-dipeptidase activity."
    ),
    ("dipeptidase", "has input (hydrolyses)", "dala_dala"): (
        "VanX hydrolyzes D-Ala-D-Ala, the free dipeptide used to build "
        "glycopeptide-susceptible peptidoglycan precursors."
    ),
    ("dipeptidase", "negatively regulates (depletes)", "dala_dala"): (
        "Hydrolysis depletes D-Ala-D-Ala while sparing D-Ala-D-Lac, driving "
        "peptidoglycan precursor synthesis toward the low-affinity terminus."
    ),
    ("drug0", "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "dala_dala"): (
        "Glycopeptides bind D-Ala-D-Ala termini in peptidoglycan precursors; "
        "VanX removes the free dipeptide needed to build those termini."
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
        marker = (item["reference"], item.get("snippet", ""))
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge_evidence(key: tuple[str, str, str]) -> list[dict[str, str]]:
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [
                VANX_DEFINITION_EVIDENCE,
                VANX_MECHANISM_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                VANX_DEFINITION_EVIDENCE,
                VANX_MECHANISM_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [VANX_DEFINITION_EVIDENCE, VANX_MECHANISM_EVIDENCE, VANX_LOSS_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                GLYCOPEPTIDE_RELATION_EVIDENCE,
                VANX_DEFINITION_EVIDENCE,
                VANX_MECHANISM_EVIDENCE,
            ]
        case ("domain", "part of (the dipeptidase domain of this determinant)", "determinant"):
            extra = [PFAM_VANX_EVIDENCE, VANX_DEFINITION_EVIDENCE]
        case ("domain", "enables (D,D-dipeptidase activity)", "dipeptidase"):
            extra = [PFAM_VANX_EVIDENCE, VANX_EXPRESSION_EVIDENCE, VANX_DEFINITION_EVIDENCE]
        case ("dipeptidase", "has input (hydrolyses)", "dala_dala"):
            extra = [
                VANX_EXPRESSION_EVIDENCE,
                VANX_SPECIFICITY_EVIDENCE,
                VANX_DEFINITION_EVIDENCE,
            ]
        case ("dipeptidase", "negatively regulates (depletes)", "dala_dala"):
            extra = [
                VANX_MECHANISM_EVIDENCE,
                VANX_SPECIFICITY_EVIDENCE,
                VANX_DEFINITION_EVIDENCE,
            ]
        case ("drug0", "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "dala_dala"):
            extra = [
                GLYCOPEPTIDE_BINDING_EVIDENCE,
                VANX_MECHANISM_EVIDENCE,
                VANX_DEFINITION_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*extra)


def _graph(spec: RecordSpec) -> dict[str, Any]:
    nodes = [
        {
            "node_id": "determinant",
            "label": spec.label,
            "node_type": "PROTEIN",
            "grounding": spec.identifier,
        },
        {
            "node_id": "mech0",
            "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000213",
        },
        {
            "node_id": "drug0",
            "label": "glycopeptide antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000081",
        },
        {
            "node_id": "domain",
            "label": "D-Ala-D-Ala dipeptidase domain",
            "node_type": "DOMAIN",
            "grounding": "Pfam:PF01427",
            "description": "MEROPS M15D metallopeptidase domain carried by VanX.",
        },
        {
            "node_id": "dipeptidase",
            "label": "D,D-dipeptidase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0016805",
        },
        {
            "node_id": "dala_dala",
            "label": "D-alanyl-D-alanine",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:16576",
            "description": (
                "VanX hydrolyzes free D-Ala-D-Ala before ligation into "
                "peptidoglycan precursors; glycopeptides bind the same "
                "D-Ala-D-Ala chemical group when it is present as a stem-peptide "
                "terminus."
            ),
        },
        {
            "node_id": "resistance",
            "label": "glycopeptide antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": "Resistance phenotype conferred by VanX-dependent D-Ala-D-Ala depletion.",
        },
    ]

    edges = [
        {
            "subject": "determinant",
            "predicate": "participates in (resistance mechanism)",
            "predicate_id": "RO:0000056",
            "object": "mech0",
        },
        {
            "subject": "mech0",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
        },
        {
            "subject": "determinant",
            "predicate": "causally upstream of (confers resistance)",
            "predicate_id": "RO:0002411",
            "object": "resistance",
        },
        {
            "subject": "determinant",
            "predicate": "confers resistance to (drug class)",
            "predicate_id": "ARO:2000001",
            "object": "drug0",
        },
        {
            "subject": "domain",
            "predicate": "part of (the dipeptidase domain of this determinant)",
            "predicate_id": "BFO:0000050",
            "object": "determinant",
        },
        {
            "subject": "domain",
            "predicate": "enables (D,D-dipeptidase activity)",
            "predicate_id": "RO:0002327",
            "object": "dipeptidase",
        },
        {
            "subject": "dipeptidase",
            "predicate": "has input (hydrolyses)",
            "predicate_id": "RO:0002233",
            "object": "dala_dala",
        },
        {
            "subject": "dipeptidase",
            "predicate": "negatively regulates (depletes)",
            "predicate_id": "RO:0002212",
            "object": "dala_dala",
        },
        {
            "subject": "drug0",
            "predicate": "molecularly interacts with (binds the D-Ala-D-Ala terminus)",
            "predicate_id": "RO:0002436",
            "object": "dala_dala",
        },
    ]

    for edge in edges:
        key = (
            str(edge["subject"]),
            str(edge["predicate"]),
            str(edge["object"]),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _edge_evidence(key)

    return {
        "graph_id": "resistance",
        "title": f"{spec.label} → VanX D-Ala-D-Ala hydrolysis → glycopeptide resistance",
        "description": (
            "Curated resistance-causation graph for VanX-mediated "
            "glycopeptide resistance. VanX hydrolyzes free D-Ala-D-Ala but "
            "spares D-Ala-D-Lac, forcing peptidoglycan precursor synthesis "
            "away from the glycopeptide-bound terminus."
        ),
        "nodes": nodes,
        "edges": edges,
    }


def enrich_record(record: dict[str, Any], spec: RecordSpec) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != spec.identifier:
        raise ValueError(f"expected {spec.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(spec)]
    return out, out != record


def enrich_text(text: str, spec: RecordSpec) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record, spec)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def run(apply: bool) -> tuple[int, int]:
    changed_count = 0
    for spec in RECORDS:
        before = spec.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, spec)
        if changed:
            changed_count += 1
            print(f"  {'wrote' if apply else 'would write'} {spec.path.name}")
            if apply:
                spec.path.write_text(after, encoding="utf-8")
    return changed_count, len(RECORDS) - changed_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed_count, already = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {changed_count}")
    print(f"already enriched: {already}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
