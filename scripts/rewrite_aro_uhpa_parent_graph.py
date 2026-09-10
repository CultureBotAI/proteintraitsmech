#!/usr/bin/env python3
"""Curate the UhpA fosfomycin-resistance parent graph.

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
TARGET = (
    ROOT
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "uhpa-aro3004249.yaml"
)

HISTORY_ACTION = "Curated UhpA fosfomycin-import regulator graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

UHPA_EVIDENCE = {
    "reference": "ARO:3004249",
    "snippet": (
        "UhpA acts as a positive regulator of UhpT, which is a transporter to "
        "bring fosfomycin drugs into bacterial cells. Mutations in UhpA that "
        "negatively impact the expression of UhpT can confer resistance."
    ),
    "notes": "CARD definition for UhpA.",
}

UHP_MUTANT_EVIDENCE = {
    "reference": "ARO:3003893",
    "snippet": (
        "uhpA is a positive activator of the fosfomycin importer uhpT, thus "
        "mutations to uhpA confer fosfomycin resistance by reducing uhpT "
        "expression."
    ),
    "notes": "CARD definition for Escherichia coli uhpA with mutation.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

UHP_T_EVIDENCE = {
    "reference": "ARO:3004248",
    "snippet": (
        "UhpT encodes a transporter that can import fosfomycin-type drugs "
        "into bacterial cells. Mutations to UhpT confer resistance."
    ),
    "notes": "CARD definition for antibiotic-resistant UhpT.",
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or "
        "extent of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for broad transcriptional activation.",
}


EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies UhpA under mutation conferring antibiotic resistance."
    ),
    ("determinant", "activation"): (
        "Wild-type UhpA positively regulates UhpT expression; "
        "resistance-conferring UhpA mutations reduce that expression."
    ),
    ("activation", "uhpt"): (
        "UhpA-dependent transcriptional activation increases expression of "
        "the UhpT fosfomycin importer."
    ),
    ("uhpt", "resistance"): (
        "UhpT importer expression counteracts the reduced-fosfomycin-uptake "
        "state that confers resistance."
    ),
    ("mech0", "resistance"): (
        "UhpA mutations negatively impact UhpT expression and can confer "
        "fosfomycin resistance."
    ),
    ("determinant", "resistance"): (
        "The UhpA determinant links resistance-conferring mutations to "
        "decreased UhpT expression and reduced fosfomycin import."
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


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, object_)],
        "evidence": copy.deepcopy(evidence),
    }


def _graph() -> dict[str, Any]:
    mutation_evidence = _unique_evidence(UHPA_EVIDENCE, UHP_MUTANT_EVIDENCE, MUTATION_EVIDENCE)
    activation_evidence = _unique_evidence(
        UHPA_EVIDENCE,
        UHP_MUTANT_EVIDENCE,
        GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
        UHP_T_EVIDENCE,
    )
    uhpt_evidence = _unique_evidence(UHPA_EVIDENCE, UHP_MUTANT_EVIDENCE, UHP_T_EVIDENCE)

    return {
        "graph_id": "resistance",
        "title": "UhpA mutation → reduced UhpT expression → reduced fosfomycin uptake",
        "description": (
            "Curated graph for UhpA-mediated fosfomycin resistance. The graph "
            "grounds wild-type UhpA as a positive transcriptional regulator of "
            "the UhpT fosfomycin importer and represents resistance mutations "
            "as variants that reduce UhpT expression."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": "UhpA",
                "node_type": "PROTEIN",
                "grounding": "ARO:3004249",
            },
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            {
                "node_id": "activation",
                "label": "positive regulation of UhpT transcription",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0045893",
                "description": (
                    "Grounded to broad GO DNA-templated transcriptional "
                    "activation because UhpA activates uhpT expression."
                ),
            },
            {
                "node_id": "uhpt",
                "label": "UhpT fosfomycin importer",
                "node_type": "PROTEIN",
                "grounding": "ARO:3004248",
                "description": "Grounded to CARD's antibiotic-resistant UhpT class.",
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
                "description": "Fosfomycin resistance mediated by reduced UhpT expression.",
            },
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "enables (activates UhpT transcription)",
                "RO:0002327",
                "activation",
                activation_evidence,
            ),
            _edge(
                "activation",
                "positively regulates (raises UhpT expression)",
                "RO:0002213",
                "uhpt",
                activation_evidence,
            ),
            _edge(
                "uhpt",
                "negatively regulates (fosfomycin resistance)",
                "RO:0002212",
                "resistance",
                uhpt_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                _unique_evidence(UHPA_EVIDENCE, UHP_MUTANT_EVIDENCE, MUTATION_EVIDENCE, UHP_T_EVIDENCE),
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3004249":
        raise ValueError(f"expected ARO:3004249, found {record.get('identifier')}")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError("ARO:3004249: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["causal_graphs"] = [_graph()]
    return out, out["causal_graphs"] != before


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def run(apply: bool) -> bool:
    before = TARGET.read_text(encoding="utf-8")
    after, changed = enrich_text(before)
    if changed:
        print(f"  {'wrote' if apply else 'would write'} {TARGET.name}")
        if apply:
            TARGET.write_text(after, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
