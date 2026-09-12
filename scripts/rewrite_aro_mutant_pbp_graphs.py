#!/usr/bin/env python3
"""Curate mutant penicillin-binding-protein target-alteration graphs.

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

HISTORY_ACTION = "Curated mutant PBP target-alteration graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PBP_PARENT_EVIDENCE = {
    "reference": "ARO:3003938",
    "snippet": (
        "Mutations in PBP transpeptidases that change the affinity for "
        "penicillin thereby conferring resistance to penicillin antibiotics."
    ),
    "notes": "CARD definition for mutant PBPs conferring beta-lactam resistance.",
}

DECREASED_AFFINITY_EVIDENCE = {
    "reference": "ARO:3004833",
    "snippet": (
        "Point mutation in Neisseria gonorrhoeae PBP1 decreases the affinity "
        "between a beta-lactam antibiotic molecule and PBP1, thereby "
        "conferring beta-lactam resistance."
    ),
    "notes": (
        "CARD gives the direction of the affinity change explicitly for a "
        "ponA/PBP1 point mutation."
    ),
}

LOW_AFFINITY_EVIDENCE = {
    "reference": "PMID:1938899",
    "snippet": (
        "Defined PBP2x region replacements in Streptococcus pneumoniae "
        "generated mutant low-affinity PBP2x proteins."
    ),
    "notes": (
        "Laible and Hakenbeck 1991 showed that PBP mutations can produce the "
        "low-affinity target state."
    ),
}

MUTATION_MECHANISM_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": "mutation conferring antibiotic resistance",
    "notes": "CARD mechanism for antibiotic-resistant gene variants or mutants.",
}

CEPHALOSPORIN_RELATION_EVIDENCE = {
    "reference": "ARO:3003938",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000032 ! cephalosporin",
    "notes": "CARD/ARO asserts this cephalosporin drug class on the mutant-PBP parent.",
}

PENICILLIN_RELATION_EVIDENCE = {
    "reference": "ARO:3003938",
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:3000008 ! "
        "penicillin beta-lactam"
    ),
    "notes": "CARD/ARO asserts this penicillin beta-lactam drug class on the mutant-PBP parent.",
}

PENICILLIN_BINDING_EVIDENCE = {
    "reference": "GO:0008658",
    "snippet": "penicillin binding",
    "notes": "GO molecular-function term used to ground beta-lactam binding by PBPs.",
}

PEPTIDOGLYCAN_SYNTHESIS_EVIDENCE = {
    "reference": "GO:0009252",
    "snippet": "peptidoglycan biosynthetic process",
    "notes": "GO biological-process term for peptidoglycan synthesis by PBPs.",
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str


RECORDS = (
    RecordSpec(
        path=ARO / "escherichia-coli-pbp3-mutants-conferring-resistance-to-beta-lactam-antibiotics-aro3007423.yaml",
        identifier="ARO:3007423",
    ),
    RecordSpec(
        path=ARO / "haemophilus-influenzae-pbp3-conferring-resistance-to-beta-lactam-antibiotics-aro3004446.yaml",
        identifier="ARO:3004446",
    ),
    RecordSpec(
        path=ARO / "helicobacter-pylori-pbp1-mutants-conferring-resistance-to-amoxicillin-aro3007060.yaml",
        identifier="ARO:3007060",
    ),
    RecordSpec(
        path=ARO / "helicobacter-pylori-pbp2-mutants-conferring-resistance-to-amoxicillin-aro3007058.yaml",
        identifier="ARO:3007058",
    ),
    RecordSpec(
        path=ARO / "helicobacter-pylori-pbp3-conferring-resistance-to-amoxicillin-aro3007057.yaml",
        identifier="ARO:3007057",
    ),
    RecordSpec(
        path=ARO / "klebsiella-pneumoniae-pbp3-mutants-conferring-resistance-to-ceftazidime-avibacta-aro3007421.yaml",
        identifier="ARO:3007421",
    ),
    RecordSpec(
        path=ARO / "neisseria-gonorrhoeae-pbp1-conferring-resistance-to-beta-lactam-antibiotics-aro3004833.yaml",
        identifier="ARO:3004833",
    ),
    RecordSpec(
        path=ARO / "neisseria-gonorrhoeae-pbp2-conferring-resistance-to-beta-lactam-antibiotics-aro3004832.yaml",
        identifier="ARO:3004832",
    ),
    RecordSpec(
        path=ARO / "neisseria-meningititis-pbp2-conferring-resistance-to-beta-lactam-aro3003937.yaml",
        identifier="ARO:3003937",
    ),
    RecordSpec(
        path=ARO / "penicillin-binding-protein-mutations-conferring-resistance-to-beta-lactam-antibi-aro3003938.yaml",
        identifier="ARO:3003938",
    ),
    RecordSpec(
        path=ARO / "streptococcus-pneumoniae-pbp1a-conferring-resistance-to-amoxicillin-aro3003041.yaml",
        identifier="ARO:3003041",
    ),
    RecordSpec(
        path=ARO / "streptococcus-pneumoniae-pbp2b-conferring-resistance-to-amoxicillin-aro3003042.yaml",
        identifier="ARO:3003042",
    ),
    RecordSpec(
        path=ARO / "streptococcus-pneumoniae-pbp2x-conferring-resistance-to-amoxicillin-aro3003043.yaml",
        identifier="ARO:3003043",
    ),
    RecordSpec(
        path=ARO / "streptococcus-pyogenes-pbp2x-conferring-resistance-to-beta-lactam-antibiotics-aro3007531.yaml",
        identifier="ARO:3007531",
    ),
    RecordSpec(
        path=ARO / "streptococcus-pyogenes-pbp2x-with-mutation-conferring-resistance-to-beta-lactam--aro3007530.yaml",
        identifier="ARO:3007530",
    ),
)

EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD classifies mutant PBPs under mutation-conferring antibiotic resistance."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "PBP mutations lower beta-lactam affinity and thereby confer beta-lactam resistance."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "The mutant PBP target binds beta-lactams poorly enough to sustain "
        "peptidoglycan synthesis under drug exposure."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "CARD asserts that mutant PBPs confer resistance to cephalosporins."
    ),
    ("determinant", "confers resistance to (drug class)", "drug1"): (
        "CARD asserts that mutant PBPs confer resistance to penicillin beta-lactams."
    ),
    ("determinant", "negatively regulates (decreases beta-lactam binding)", "beta_lactam_binding"): (
        "The resistance mutations decrease beta-lactam binding to the native PBP target."
    ),
    ("beta_lactam_binding", "negatively regulates (inhibits wall synthesis)", "pg_synth"): (
        "Beta-lactam binding to PBPs inhibits peptidoglycan biosynthesis."
    ),
    ("determinant", "participates in", "pg_synth"): (
        "The mutated PBP still participates in peptidoglycan biosynthesis."
    ),
    ("pg_synth", "causally upstream of", "resistance"): (
        "Continued PBP-dependent peptidoglycan biosynthesis under beta-lactam "
        "exposure causes resistance."
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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record.get("definition", "")).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def _edge_evidence(key: tuple[str, str, str], record: dict[str, Any]) -> list[dict[str, str]]:
    record_definition = _record_evidence(record)

    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [
                record_definition,
                PBP_PARENT_EVIDENCE,
                MUTATION_MECHANISM_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                record_definition,
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
                MUTATION_MECHANISM_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                record_definition,
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
                LOW_AFFINITY_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                CEPHALOSPORIN_RELATION_EVIDENCE,
                record_definition,
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug1"):
            extra = [
                PENICILLIN_RELATION_EVIDENCE,
                record_definition,
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
            ]
        case (
            "determinant",
            "negatively regulates (decreases beta-lactam binding)",
            "beta_lactam_binding",
        ):
            extra = [
                record_definition,
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
                LOW_AFFINITY_EVIDENCE,
                PENICILLIN_BINDING_EVIDENCE,
            ]
        case ("beta_lactam_binding", "negatively regulates (inhibits wall synthesis)", "pg_synth"):
            extra = [
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
                LOW_AFFINITY_EVIDENCE,
                PENICILLIN_BINDING_EVIDENCE,
                PEPTIDOGLYCAN_SYNTHESIS_EVIDENCE,
            ]
        case ("determinant", "participates in", "pg_synth"):
            extra = [
                record_definition,
                PBP_PARENT_EVIDENCE,
                PEPTIDOGLYCAN_SYNTHESIS_EVIDENCE,
            ]
        case ("pg_synth", "causally upstream of", "resistance"):
            extra = [
                record_definition,
                PBP_PARENT_EVIDENCE,
                DECREASED_AFFINITY_EVIDENCE,
                LOW_AFFINITY_EVIDENCE,
                PEPTIDOGLYCAN_SYNTHESIS_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*extra)


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    nodes = [
        {
            "node_id": "determinant",
            "label": str(record["label"]),
            "node_type": "PROTEIN",
            "grounding": str(record["identifier"]),
        },
        {
            "node_id": "mech0",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
        {
            "node_id": "drug0",
            "label": "cephalosporin",
            "node_type": "CHEMICAL",
            "grounding": "ARO:0000032",
        },
        {
            "node_id": "drug1",
            "label": "penicillin beta-lactam",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000008",
        },
        {
            "node_id": "beta_lactam_binding",
            "label": "penicillin binding by the mutant PBP",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0008658",
            "description": "GO-grounded beta-lactam binding by a penicillin-binding protein.",
        },
        {
            "node_id": "pg_synth",
            "label": "peptidoglycan biosynthetic process",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0009252",
        },
        {
            "node_id": "resistance",
            "label": "beta-lactam antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by decreased beta-lactam "
                "binding to a mutated penicillin-binding protein."
            ),
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
            "subject": "determinant",
            "predicate": "confers resistance to (drug class)",
            "predicate_id": "ARO:2000001",
            "object": "drug1",
        },
        {
            "subject": "determinant",
            "predicate": "negatively regulates (decreases beta-lactam binding)",
            "predicate_id": "RO:0002212",
            "object": "beta_lactam_binding",
        },
        {
            "subject": "beta_lactam_binding",
            "predicate": "negatively regulates (inhibits wall synthesis)",
            "predicate_id": "RO:0002212",
            "object": "pg_synth",
        },
        {
            "subject": "determinant",
            "predicate": "participates in",
            "predicate_id": "RO:0000056",
            "object": "pg_synth",
        },
        {
            "subject": "pg_synth",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
        },
    ]

    for edge in edges:
        key = (
            str(edge["subject"]),
            str(edge["predicate"]),
            str(edge["object"]),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _edge_evidence(key, record)

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → decreased beta-lactam affinity → resistance",
        "description": (
            "Curated resistance-causation graph for beta-lactam-resistant PBP "
            "target alteration. Native PBP mutations decrease beta-lactam "
            "binding while preserving PBP-dependent "
            "peptidoglycan biosynthesis."
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
    out["causal_graphs"] = [_graph(record)]
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
