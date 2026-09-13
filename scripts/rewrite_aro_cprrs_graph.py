#!/usr/bin/env python3
"""Complete the cprRS charge-alteration regulator graph.

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
TARGET = ROOT / "data" / "traits" / "function" / "resistance" / "aro" / "cprrs-aro3005065.yaml"

HISTORY_ACTION = "Completed cprRS cationic-peptide response graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CPRRS_EVIDENCE = {
    "reference": "ARO:3005065",
    "snippet": (
        "cprRS is a two-component regulatory system. In the presence of "
        "cationic peptides, it induces the Arn operon to confer resistance."
    ),
    "notes": "CARD definition for cprRS.",
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "Modification of the cell wall to be less susceptible to antibiotic "
        "binding will confer resistance."
    ),
    "notes": "CARD definition for charge alteration conferring antibiotic resistance.",
}

CPRRS_PAPER_EVIDENCE = {
    "reference": "PMID:23006746",
    "snippet": (
        "The two-component system CprRS senses cationic peptides and triggers "
        "adaptive resistance in Pseudomonas aeruginosa"
    ),
    "notes": (
        "Fernández et al. 2012; the title states the direct CprRS sensing and "
        "adaptive-resistance result."
    ),
}

PEPTIDE_EVIDENCE = {
    "reference": "ARO:3004269",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": (
        "Asserted on ARO:3004269 (pmr phosphoethanolamine transferase), an "
        "is_a ancestor of cprRS, in the CARD/ARO release used for this record."
    ),
}

ARN_OPERON_EVIDENCE = {
    "reference": "ARO:3003578",
    "snippet": "pmrF is a glycosyl transferase found in the Arn operon.",
    "notes": "CARD definition for PmrF, the KB proxy used here for the Arn operon.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies cprRS under cell-wall charge alteration.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "Cell-wall charge alteration lowers cationic-peptide binding and causes resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "CprRS confers resistance indirectly by inducing the Arn operon.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts peptide-antibiotic resistance through the inherited pmr/Arn lineage.",
    (
        "sensing",
        "causally upstream of (activates the two-component system)",
        "determinant",
    ): "Cationic peptides are the inducing signal sensed by CprRS.",
    (
        "determinant",
        "positively regulates (induces the Arn operon)",
        "arn_operon",
    ): "CprRS induces the Arn operon rather than directly modifying lipid A.",
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
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _evidence_for_edge(
    key: tuple[str, str, str], existing: list[dict[str, str]]
) -> list[dict[str, str]]:
    common = [CPRRS_EVIDENCE, CHARGE_ALTERATION_EVIDENCE, CPRRS_PAPER_EVIDENCE]
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = common
        case ("mech0", "causally upstream of", "resistance"):
            extra = common
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = common
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [PEPTIDE_EVIDENCE, CPRRS_EVIDENCE, CPRRS_PAPER_EVIDENCE]
        case ("sensing", "causally upstream of (activates the two-component system)", "determinant"):
            extra = [CPRRS_EVIDENCE, CPRRS_PAPER_EVIDENCE]
        case ("determinant", "positively regulates (induces the Arn operon)", "arn_operon"):
            extra = [CPRRS_EVIDENCE, ARN_OPERON_EVIDENCE, CPRRS_PAPER_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3005065":
        raise ValueError(f"expected ARO:3005065, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "cprRS → cationic-peptide-induced Arn regulation → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for the CprRS two-component system. "
        "CprRS senses cationic peptides and induces the Arn operon, whose lipid "
        "A modification route reduces peptide-antibiotic susceptibility."
    )

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(key, _dicts(edge.get("evidence")))
        seen.add(key)

    missing = sorted(set(EDGE_DESCRIPTIONS) - seen)
    if missing:
        raise ValueError(f"missing edge(s): {missing}")
    out["causal_graphs"] = [graph]
    return out, out != record


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    before = TARGET.read_text(encoding="utf-8")
    after, changed = enrich_text(before)

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {TARGET.name}")
        if args.apply:
            TARGET.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
