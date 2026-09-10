#!/usr/bin/env python3
"""Ground and re-evidence the ampR beta-lactamase-overexpression graph.

The ampR ARO record states that AmpR is a LysR-type transcriptional regulator
for beta-lactamase-encoding gene expression and that mutations in ampR can
confer resistance because of beta-lactamase overexpression.  This updater keeps
that broad shape rather than choosing a single beta-lactamase target for the
family-level record.

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
IDENTIFIER = "ARO:3007797"
FILENAME = "ampr-transcriptional-regulator-with-mutation-conferring-resistance-to-monobactam-aro3007797.yaml"

HISTORY_ACTION = "Completed ampR beta-lactamase-overexpression causal graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CARD_DEFINITION_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding "
        "gene expression. Mutations in ampR of certain organisms have been shown to "
        "confer resistance to antibiotics due to beta-lactamase overexpression."
    ),
    "notes": "CARD definition for ampR.",
}

MONOBACTAM_RELATION_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000004 ! monobactam",
    "notes": (
        "CARD/ARO drug-class relationship asserted on the ampR record in "
        "data/raw/aro/aro.obo."
    ),
}

DING_AMPR_MUTATION_EVIDENCE = {
    "reference": "DOI:10.1128/spectrum.03080-22",
    "snippet": (
        "Mutation in ampR leads to its loss of control over bla_{PDC-16}, allowing "
        "overexpression of bla_{PDC-16} and further resistance to aztreonam."
    ),
    "notes": "Clinical Pseudomonas aeruginosa case linking ampR mutation to blaPDC-16 overexpression.",
}

DING_OVEREXPRESSION_EVIDENCE = {
    "reference": "DOI:10.1128/spectrum.03080-22",
    "snippet": (
        "overexpression of bla_{PDC-16} is the primary resistance mechanism to "
        "aztreonam"
    ),
    "notes": "Paper conclusion from RT-PCR and inhibitor rescue assays in P. aeruginosa HS110.",
}

GENE_EXPRESSION_EVIDENCE = {
    "reference": "GO:0010467",
    "snippet": (
        "Gene expression is the process in which a gene's coding sequence is "
        "converted into a mature gene product or products."
    ),
    "notes": "GO definition for the broad gene-expression process used to ground beta-lactamase expression.",
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
        key = (item["reference"], item.get("snippet", ""))
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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    source_evidence = _source_evidence(record)
    card_and_literature = (
        CARD_DEFINITION_EVIDENCE,
        DING_AMPR_MUTATION_EVIDENCE,
        *source_evidence,
    )
    overexpression_evidence = (
        CARD_DEFINITION_EVIDENCE,
        DING_OVEREXPRESSION_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": "ampR mutation → beta-lactamase overexpression → monobactam resistance",
        "description": (
            "Curated resistance-causation graph for the broad ampR route in which "
            "regulator mutation causes beta-lactamase overexpression and monobactam "
            "resistance. The graph stops at the overexpression step because the "
            "family-level CARD record does not identify one beta-lactamase target."
        ),
        "nodes": [
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
                "label": "monobactam",
                "node_type": "CHEMICAL",
                "grounding": "ARO:0000004",
            },
            {
                "node_id": "bla_expression",
                "label": "beta-lactamase gene expression",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0010467",
                "description": (
                    "Grounded to broad GO gene expression because CARD names the "
                    "regulated product class, not one specific beta-lactamase gene."
                ),
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
                "description": (
                    "Resistance phenotype conferred by this determinant. Grounded "
                    "to the nearest available superclass: ARO models determinants "
                    "and mechanisms but has no term for the resistance phenotype "
                    "itself."
                ),
            },
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies resistant ampR variants under mutation conferring antibiotic resistance.",
                *card_and_literature,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "bla_expression",
                "The ampR mutation mechanism causes beta-lactamase overexpression.",
                *card_and_literature,
            ),
            _edge(
                "bla_expression",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "CARD and the cited clinical study identify beta-lactamase overexpression as the causal route to resistance.",
                *overexpression_evidence,
                GENE_EXPRESSION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Mutant ampR confers resistance through beta-lactamase overexpression.",
                *overexpression_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "ARO directly maps this ampR class to monobactam resistance, and the cited case demonstrates aztreonam resistance.",
                MONOBACTAM_RELATION_EVIDENCE,
                DING_OVEREXPRESSION_EVIDENCE,
                *source_evidence,
            ),
            _edge(
                "determinant",
                "regulates (beta-lactamase gene expression)",
                "RO:0002211",
                "bla_expression",
                "AmpR is a beta-lactamase transcriptional regulator; the edge stays direction-neutral for the wild-type role.",
                *card_and_literature,
                GENE_EXPRESSION_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not ampR: {record.get('identifier')}")
    if path.name != FILENAME:
        raise ValueError(f"{path}: {IDENTIFIER} must be in {FILENAME}")

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
    return [path / FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the ampR YAML file",
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
