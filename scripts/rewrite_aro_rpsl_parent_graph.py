#!/usr/bin/env python3
"""Complete the broad antibiotic-resistant rpsL parent graph.

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
    / "antibiotic-resistant-rpsl-aro3003419.yaml"
)

HISTORY_ACTION = "Completed antibiotic-resistant rpsL parent graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RPSL_GENERIC_EVIDENCE = {
    "reference": "ARO:3003419",
    "snippet": (
        "Ribosomal protein S12 stabilizes the highly conserved pseudoknot "
        "structure formed by 16S rRNA. Amino acid substitutions in RpsL affect "
        "the higher-order structure of 16S rRNA and confer antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic-resistant rpsL.",
}

RPSL_STREPTOMYCIN_EVIDENCE = {
    "reference": "ARO:3003395",
    "snippet": (
        "Ribosomal protein S12 stabilizes the highly conserved pseudoknot "
        "structure formed by 16S rRNA. Amino acid substitutions in RpsL affect "
        "the higher-order structure of 16S rRNA and confer streptomycin "
        "resistance by disrupting interactions between 16S rRNA and "
        "streptomycin."
    ),
    "notes": (
        "CARD definition for the streptomycin-specific rpsL child; its first "
        "two sentences repeat the generic rpsL structural mechanism."
    ),
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

FINKEN_MUTATION_EVIDENCE = {
    "reference": "PMID:7934937",
    "snippet": (
        "The mutations found either lead to amino acid changes in ribosomal "
        "protein S12 or alter the primary structure of the 16S rRNA."
    ),
    "notes": "Finken 1993 reports rpsL amino-acid changes among ribosomal mutations.",
}

FINKEN_SOURCE_ASSOCIATION_SNIPPET = (
    "We demonstrate that streptomycin resistance is associated with mutations "
    "implicated in ribosomal resistance."
)

MUSSER_ASSOCIATION_EVIDENCE = {
    "reference": "PMID:8665467",
    "snippet": (
        "Streptomycin resistance in about one-half of M. tuberculosis isolates "
        "is associated with missense mutations in the rpsL gene coding for "
        "ribosomal protein S12 or nucleotide substitutions in the 16S rRNA "
        "gene (rrs)."
    ),
    "notes": (
        "Musser 1995 explicitly ties rpsL missense mutations to "
        "streptomycin, the aminoglycoside instance that CARD's rpsL parent "
        "generalizes."
    ),
}

FINKEN_PSEUDOKNOT_EVIDENCE = {
    "reference": "PMID:7934937",
    "snippet": (
        "The 16S rRNA region mutated perturbs a pseudoknot structure in a "
        "region which has been linked to ribosomal S12 protein."
    ),
    "notes": "'a pseudoknot structure in a region' of the 16S rRNA.",
}

PFAM_EVIDENCE = {
    "reference": "Pfam:PF00164",
    "snippet": (
        "Ribosomal protein uS12 is one of the proteins from the small "
        "ribosomal subunit. In Escherichia coli, uS12 is known to be involved "
        "in the translation initiation step."
    ),
    "notes": "KB trait: the S12 domain, as on ARO:3003395.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies rpsL sequence variants under mutation-conferring antibiotic resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "The inherited mutation mechanism captures rpsL substitutions that alter ribosomal S12.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): (
        "CARD asserts that RpsL substitutions affect 16S rRNA higher-order "
        "structure and confer resistance."
    ),
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD directly assigns aminoglycoside resistance to the rpsL parent.",
    (
        "domain",
        "part of (the S12 domain of this determinant)",
        "determinant",
    ): "RpsL encodes ribosomal protein S12, whose Pfam S12/S23 domain is modeled here.",
    (
        "pseudoknot",
        "part of (a structure of the 16S rRNA)",
        "rrna16s",
    ): "The pseudoknot region is modeled as a local structure in the 16S rRNA.",
    (
        "altered_structure",
        "characteristic of (a structure of the 16S rRNA)",
        "rrna16s",
    ): (
        "A conformation inheres in a molecule rather than being a "
        "mereological part of one; CARD states that substitutions affect the "
        "higher-order structure OF 16S rRNA."
    ),
    (
        "determinant",
        "correlated with (linked to the pseudoknot region)",
        "pseudoknot",
    ): (
        "Finken reports linkage between S12 and the pseudoknot region; the "
        "edge stays below CARD's stronger stabilizes wording."
    ),
    (
        "determinant",
        "causally upstream of (substitution alters the higher-order structure)",
        "altered_structure",
    ): (
        "The parent asserts altered 16S rRNA structure, and deliberately stops "
        "before the child term's streptomycin-specific drug-interaction arm."
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
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _evidence_for_edge(
    key: tuple[str, str, str], existing: list[dict[str, str]]
) -> list[dict[str, str]]:
    existing = [
        item
        for item in existing
        if (
            item.get("reference"),
            item.get("snippet"),
        )
        != ("PMID:7934937", FINKEN_SOURCE_ASSOCIATION_SNIPPET)
    ]

    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [RPSL_GENERIC_EVIDENCE, MUTATION_EVIDENCE, FINKEN_MUTATION_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [RPSL_GENERIC_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                RPSL_GENERIC_EVIDENCE,
                RPSL_STREPTOMYCIN_EVIDENCE,
                FINKEN_MUTATION_EVIDENCE,
                MUSSER_ASSOCIATION_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [RPSL_STREPTOMYCIN_EVIDENCE, MUSSER_ASSOCIATION_EVIDENCE]
        case ("domain", "part of (the S12 domain of this determinant)", "determinant"):
            extra = [PFAM_EVIDENCE, RPSL_GENERIC_EVIDENCE, FINKEN_MUTATION_EVIDENCE]
        case ("pseudoknot", "part of (a structure of the 16S rRNA)", "rrna16s"):
            extra = [FINKEN_PSEUDOKNOT_EVIDENCE, RPSL_GENERIC_EVIDENCE]
        case (
            "altered_structure",
            "characteristic of (a structure of the 16S rRNA)",
            "rrna16s",
        ):
            extra = [RPSL_GENERIC_EVIDENCE, RPSL_STREPTOMYCIN_EVIDENCE]
        case ("determinant", "correlated with (linked to the pseudoknot region)", "pseudoknot"):
            extra = [FINKEN_PSEUDOKNOT_EVIDENCE, RPSL_GENERIC_EVIDENCE]
        case (
            "determinant",
            "causally upstream of (substitution alters the higher-order structure)",
            "altered_structure",
        ):
            extra = [RPSL_GENERIC_EVIDENCE, RPSL_STREPTOMYCIN_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3003419":
        raise ValueError(f"expected ARO:3003419, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "antibiotic-resistant rpsL → 16S rRNA structural alteration → resistance"

    for node in _dicts(graph.get("nodes")):
        if node.get("node_id") == "rrna16s":
            node["grounding"] = "SO:0000252"
            node["description"] = (
                "Grounded to the broad Sequence Ontology rRNA term because no "
                "stable narrower bacterial 16S rRNA CURIE is available in the "
                "local curation evidence."
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
