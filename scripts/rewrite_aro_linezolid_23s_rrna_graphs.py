#!/usr/bin/env python3
"""Complete 23S rRNA linezolid mutation graphs.

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

HISTORY_ACTION = "Completed 23S rRNA linezolid mutation graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
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

PARENT_CONFERRAL_EVIDENCE = {
    "reference": "ARO:3000336",
    "snippet": (
        "Point mutations in bacterial 23S rRNA from the large ribosomal "
        "subunit that confer resistance to antibiotics."
    ),
    "notes": "CARD definition for the broad 23S rRNA mutation parent term.",
}

PARENT_BINDING_EVIDENCE = {
    "reference": "ARO:3000336",
    "snippet": (
        "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity "
        "at specific sites, conferring resistance."
    ),
    "notes": "CARD support for the reduced-binding 23S rRNA mutation mechanism.",
}

LINEZOLID_PARENT_EVIDENCE = {
    "reference": "ARO:3004057",
    "snippet": (
        "Point mutations in the 23S rRNA subunit may confer resistance to "
        "linezolid and other oxazolidinone antibiotics."
    ),
    "notes": "CARD definition for the linezolid/oxazolidinone 23S rRNA mutation parent.",
}

RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both "
        "structural scaffolding and catalytic activity."
    ),
    "notes": "Sequence Ontology definition for the broad rRNA superclass.",
}

GO_50S_EVIDENCE = {
    "reference": "GO:0015934",
    "snippet": "large ribosomal subunit",
    "notes": "GO grounding for the large ribosomal subunit.",
}

GO_PEPTIDYL_TRANSFERASE_EVIDENCE = {
    "reference": "GO:0000048",
    "snippet": (
        "The synthesis of a peptide bond, as in the addition of an amino acid "
        "residue to a peptide chain."
    ),
    "notes": "GO definition for peptidyl transferase activity.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    extra_record_evidence: dict[str, str] | None = None


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004057",
        "23s-rrna-with-mutation-conferring-resistance-to-linezolid-antibiotics-"
        "aro3004057.yaml",
    ),
    Target(
        "ARO:3004058",
        "staphylococcus-aureus-23s-rrna-with-mutation-conferring-resistance-to-linezolid-"
        "aro3004058.yaml",
        {
            "reference": "ARO:3004058",
            "snippet": (
                "Point mutations in the 23S rRNA subunit of the large "
                "ribosomal bacterial subunit in Staphylococcus aureus, which "
                "confer resistance to linezolid by disrupting antibiotic "
                "target binding."
            ),
            "notes": (
                "CARD definition for Staphylococcus aureus 23S rRNA mutations "
                "conferring linezolid resistance."
            ),
        },
    ),
)

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies linezolid 23S rRNA mutations under mutation-conferring resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "The inherited mutation mechanism captures 23S rRNA binding-site changes.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "23S rRNA mutations reduce antibiotic binding affinity and confer resistance.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD directly asserts the inherited macrolide-antibiotic resistance relation.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug1",
    ): "CARD directly asserts the inherited lincosamide-antibiotic resistance relation.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug2",
    ): "CARD directly asserts the inherited streptogramin-antibiotic resistance relation.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug3",
    ): "CARD directly asserts the inherited oxazolidinone-antibiotic resistance relation.",
    (
        "binding_site",
        "part of (the 23S rRNA)",
        "determinant",
    ): "The modeled antibiotic-binding site is a local site in the mutated 23S rRNA.",
    (
        "determinant",
        "part of (the 50S subunit)",
        "subunit",
    ): "Bacterial 23S rRNA is part of the large ribosomal subunit.",
    (
        "determinant",
        "has quality (reduced antibiotic binding affinity)",
        "low_affinity",
    ): "The resistance-associated 23S rRNA mutations lower antibiotic binding affinity.",
    (
        "low_affinity",
        "negatively regulates (drug occupancy of the site)",
        "binding_site",
    ): "Reduced affinity at the 23S rRNA site decreases antibiotic occupancy there.",
    (
        "drug3",
        "negatively regulates (linezolid blocks peptide synthesis)",
        "pt_activity",
    ): "Linezolid is an oxazolidinone that blocks peptidyl transferase activity when bound.",
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
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _evidence_for_edge(
    key: tuple[str, str, str],
    existing: list[dict[str, str]],
    record_evidence: dict[str, str],
    target: Target,
) -> list[dict[str, str]]:
    target_evidence = (
        (target.extra_record_evidence,) if target.extra_record_evidence is not None else ()
    )
    linezolid_evidence = (record_evidence, LINEZOLID_PARENT_EVIDENCE, *target_evidence)
    mutation_evidence = (
        *linezolid_evidence,
        PARENT_CONFERRAL_EVIDENCE,
        PARENT_BINDING_EVIDENCE,
        MUTATION_EVIDENCE,
    )
    site_evidence = (*linezolid_evidence, PARENT_BINDING_EVIDENCE, RRNA_EVIDENCE)
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = mutation_evidence
        case ("mech0", "causally upstream of", "resistance"):
            extra = mutation_evidence
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = mutation_evidence
        case ("determinant", "confers resistance to (drug class)", _):
            extra = (*linezolid_evidence, PARENT_BINDING_EVIDENCE)
        case ("binding_site", "part of (the 23S rRNA)", "determinant"):
            extra = site_evidence
        case ("determinant", "part of (the 50S subunit)", "subunit"):
            extra = (
                *linezolid_evidence,
                PARENT_CONFERRAL_EVIDENCE,
                GO_50S_EVIDENCE,
                RRNA_EVIDENCE,
            )
        case ("determinant", "has quality (reduced antibiotic binding affinity)", "low_affinity"):
            extra = (*linezolid_evidence, PARENT_BINDING_EVIDENCE)
        case ("low_affinity", "negatively regulates (drug occupancy of the site)", "binding_site"):
            extra = site_evidence
        case ("drug3", "negatively regulates (linezolid blocks peptide synthesis)", "pt_activity"):
            extra = (
                *linezolid_evidence,
                PARENT_BINDING_EVIDENCE,
                GO_PEPTIDYL_TRANSFERASE_EVIDENCE,
            )
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"{target.filename}: expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = f"{record['label']} → reduced 23S rRNA antibiotic binding"
    graph["description"] = (
        "Curated resistance-causation graph for linezolid-linked 23S rRNA "
        "mutations that reduce antibiotic binding at 23S rRNA sites. "
        "The graph preserves CARD's inherited drug-class assertions and "
        "places the linezolid peptide-synthesis block on the oxazolidinone node."
    )

    for node in _dicts(graph.get("nodes")):
        if node.get("node_id") == "binding_site":
            node["grounding"] = "SO:0000252"
            node["description"] = (
                "Grounded to the broad Sequence Ontology rRNA term because no "
                "stable narrow term is available for a generic 23S rRNA "
                "antibiotic-binding site."
            )

    record_evidence = _record_evidence(record)
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "drug0"
            and edge.get("object") == "pt_activity"
            and edge.get("predicate_id") == "RO:0002212"
        ):
            edge["subject"] = "drug3"
            edge["predicate"] = "negatively regulates (linezolid blocks peptide synthesis)"

        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(
            key, _dicts(edge.get("evidence")), record_evidence, target
        )
        seen.add(key)

    missing = sorted(set(EDGE_DESCRIPTIONS) - seen)
    if missing:
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, target: Target) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{target.filename}: expected a YAML mapping")

    enriched, changed = enrich_record(record, target)
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

    changed = 0
    unchanged = 0
    for target in TARGETS:
        path = ARO_DIR / target.filename
        before = path.read_text(encoding="utf-8")
        after, did_change = enrich_text(before, target)
        if did_change:
            changed += 1
            print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
            if args.apply:
                path.write_text(after, encoding="utf-8")
        else:
            unchanged += 1

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
