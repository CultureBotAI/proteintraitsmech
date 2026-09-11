#!/usr/bin/env python3
"""Complete the generic pleuromutilin-resistance ribosomal-protein graph.

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
from rewrite_aro_thermus_ul3_graph import (  # noqa: E402
    BOSLING_PTC_EVIDENCE,
    GO_LARGE_SUBUNIT_EVIDENCE,
    GO_PEPTIDYL_TRANSFERASE_EVIDENCE,
    MUTATION_EVIDENCE,
    PARENT_EVIDENCE,
    SCHLUENZEN_INHIBITION_EVIDENCE,
    SCHLUENZEN_PTC_EVIDENCE,
    SO_RRNA_EVIDENCE,
)

ROOT = Path(__file__).resolve().parent.parent
TARGET = (
    ROOT
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "ribosomal-protein-mutation-conferring-resistance-to-pleuromutilin-antibiotics-aro3005082.yaml"
)

HISTORY_ACTION = "Completed generic ribosomal-protein pleuromutilin-resistance graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PLEUROMUTILIN_RELATION_EVIDENCE = {
    "reference": "ARO:3005082",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000670 ! pleuromutilin antibiotic",
    "notes": (
        "Asserted directly on ARO:3005082 (Ribosomal protein mutation conferring "
        "resistance to pleuromutilin antibiotics) in the CARD/ARO release in "
        "data/raw/aro/aro.obo."
    ),
}

KILLEAVY_TIAMULIN_EVIDENCE = {
    "reference": "PMID:32526926",
    "snippet": "Tiamulin is a semisynthetic pleuromutilin antibiotic",
    "notes": (
        "Killeavy 2020 isolated tiamulin-resistant Thermus thermophilus mutants; "
        "tiamulin is the tested pleuromutilin-class member."
    ),
}

KILLEAVY_UL3_CONFORMATION_EVIDENCE = {
    "reference": "PMID:32526926",
    "snippet": (
        "amino acid substitutions in uL3 are predicted to act indirectly by destabilizing "
        "rRNA conformation in the active site"
    ),
    "notes": (
        "Killeavy 2020 interprets the uL3 substitutions as an example of a "
        "ribosomal-protein mutation acting in trans on the rRNA conformation."
    ),
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies this ribosomal-protein determinant under mutation-conferring resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "The inherited mutation mechanism captures altered gene products that cause resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Ribosomal protein mutations can confer resistance by altering local rRNA conformation at the active site.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts that this ribosomal-protein mutation class confers resistance to pleuromutilin antibiotics.",
    (
        "ptc",
        "part of (the PTC of the 50S subunit)",
        "subunit50s",
    ): "Tiamulin binds in the peptidyl transferase center of the 50S ribosomal subunit.",
    (
        "drug0",
        "molecularly interacts with (binds the peptidyl transferase centre)",
        "ptc",
    ): "Tiamulin represents the pleuromutilin drug class and binds the PTC.",
    (
        "drug_binding",
        "has part (the antibiotic)",
        "drug0",
    ): "The modeled drug-binding state includes the pleuromutilin-class drug tiamulin.",
    (
        "drug_binding",
        "has part (the site it binds)",
        "ptc",
    ): "The modeled drug-binding state includes the PTC drug-binding site.",
    (
        "determinant",
        "causally upstream of (the substitution alters the conformation)",
        "altered_conformation",
    ): "The ribosomal-protein substitution acts in trans by altering local 23S rRNA conformation.",
    (
        "altered_conformation",
        "characteristic of (a conformation of the 23S rRNA)",
        "rrna23s",
    ): "The altered conformation is a local conformation of 23S rRNA.",
    (
        "drug_binding",
        "negatively regulates (bound drug blocks peptide bond formation)",
        "peptide_bond",
    ): "Tiamulin binding at the PTC directly blocks the peptidyl transferase reaction.",
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


def _evidence_for_edge(
    key: tuple[str, str, str], existing: list[dict[str, str]]
) -> list[dict[str, str]]:
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [PARENT_EVIDENCE, MUTATION_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [PARENT_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [PARENT_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [PLEUROMUTILIN_RELATION_EVIDENCE, PARENT_EVIDENCE, KILLEAVY_TIAMULIN_EVIDENCE]
        case ("ptc", "part of (the PTC of the 50S subunit)", "subunit50s"):
            extra = [SCHLUENZEN_PTC_EVIDENCE, BOSLING_PTC_EVIDENCE, GO_LARGE_SUBUNIT_EVIDENCE]
        case (
            "drug0",
            "molecularly interacts with (binds the peptidyl transferase centre)",
            "ptc",
        ):
            extra = [SCHLUENZEN_PTC_EVIDENCE, BOSLING_PTC_EVIDENCE]
        case ("drug_binding", "has part (the antibiotic)", "drug0"):
            extra = [BOSLING_PTC_EVIDENCE, SCHLUENZEN_PTC_EVIDENCE]
        case ("drug_binding", "has part (the site it binds)", "ptc"):
            extra = [SCHLUENZEN_PTC_EVIDENCE, BOSLING_PTC_EVIDENCE]
        case (
            "determinant",
            "causally upstream of (the substitution alters the conformation)",
            "altered_conformation",
        ):
            extra = [PARENT_EVIDENCE, KILLEAVY_UL3_CONFORMATION_EVIDENCE]
        case (
            "altered_conformation",
            "characteristic of (a conformation of the 23S rRNA)",
            "rrna23s",
        ):
            extra = [PARENT_EVIDENCE, SO_RRNA_EVIDENCE]
        case (
            "drug_binding",
            "negatively regulates (bound drug blocks peptide bond formation)",
            "peptide_bond",
        ):
            extra = [
                SCHLUENZEN_INHIBITION_EVIDENCE,
                SCHLUENZEN_PTC_EVIDENCE,
                GO_PEPTIDYL_TRANSFERASE_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3005082":
        raise ValueError(f"expected ARO:3005082, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = (
        "Ribosomal protein mutation → 23S rRNA conformational change → "
        "pleuromutilin resistance"
    )
    graph["description"] = (
        "Curated resistance-causation graph for generic ribosomal-protein "
        "substitutions that alter local 23S rRNA conformation in trans and "
        "confer pleuromutilin resistance without naming one protein family."
    )

    for node in _dicts(graph.get("nodes")):
        if node.get("node_id") == "rrna23s":
            node["grounding"] = "SO:0000252"
            node["description"] = (
                "Grounded to the broad Sequence Ontology rRNA term because no "
                "stable narrower bacterial 23S rRNA CURIE is available in the "
                "local curation evidence."
            )
        elif node.get("node_id") == "peptide_bond":
            node["label"] = "peptidyl transferase activity"
            node["node_type"] = "MOLECULAR_FUNCTION"
            node["grounding"] = "GO:0000048"
            node["description"] = (
                "The ribosomal activity that synthesizes peptide bonds and is "
                "blocked when tiamulin binds at the PTC."
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args()

    before = TARGET.read_text(encoding="utf-8")
    after, did_change = enrich_text(before)
    if did_change:
        print(f"{'wrote' if args.apply else 'would write'} {TARGET}")
        if args.apply:
            TARGET.write_text(after, encoding="utf-8")
    else:
        print(f"already enriched {TARGET}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
