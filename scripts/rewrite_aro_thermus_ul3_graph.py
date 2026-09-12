#!/usr/bin/env python3
"""Complete the Thermus thermophilus uL3 pleuromutilin-resistance graph.

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
    / "thermus-thermophilus-ul3-mutations-conferring-resistance-to-pleuromutilin-antibi-"
    "aro3005081.yaml"
)

HISTORY_ACTION = "Completed Thermus thermophilus uL3 pleuromutilin-resistance graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

UL3_EVIDENCE = {
    "reference": "ARO:3005081",
    "snippet": (
        "Thermus thermophilus ribosomal protein uL3 containing various "
        "mutations conferring resistance to tiamulin. Mutations in the "
        "ribosomal protein of uL3 acts by interfering with local rRNA "
        "conformation thus conferring resistance."
    ),
    "notes": (
        "CARD definition for Thermus thermophilus uL3 mutations conferring "
        "resistance to pleuromutilin antibiotics."
    ),
}

PARENT_EVIDENCE = {
    "reference": "ARO:3005082",
    "snippet": (
        "Ribosomal protein mutations that interfere with the rRNA conformation "
        "at the active site thus conferring antibiotic resistance."
    ),
    "notes": (
        "CARD definition for ribosomal protein mutations conferring resistance "
        "to pleuromutilin antibiotics."
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

PLEUROMUTILIN_RELATION_EVIDENCE = {
    "reference": "ARO:3005082",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000670 ! pleuromutilin antibiotic",
    "notes": (
        "Asserted on ARO:3005082 (Ribosomal protein mutation conferring "
        "resistance to pleuromutilin antibiotics), an is_a ancestor of this "
        "record's ARO:3005081; inherited by this variant. CARD/ARO release in "
        "data/raw/aro/aro.obo."
    ),
}

SO_RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both "
        "structural scaffolding and catalytic activity."
    ),
    "notes": "Sequence Ontology definition for the broad rRNA superclass.",
}

PFAM_L3_EVIDENCE = {
    "reference": "Pfam:PF00297",
    "snippet": (
        "Ribosomal protein L3 (also known as uL3) is one of the proteins from "
        "the large ribosomal subunit. In Escherichia coli, L3 is known to bind "
        "to the 23S rRNA and may participate in the formation of the "
        "peptidyltransferase centre of the ribosome."
    ),
    "notes": "Pfam family for ribosomal protein L3/uL3.",
}

GO_LARGE_SUBUNIT_EVIDENCE = {
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

BOSLING_L3_EVIDENCE = {
    "reference": "PMID:12936991",
    "snippet": (
        "Selection in a strain with all seven chromosomal rRNA operons yielded "
        "a mutant with an A445G mutation in the gene coding for ribosomal "
        "protein L3, resulting in an Asn149Asp alteration."
    ),
    "notes": "Bosling 2003 identified the ribosomal protein L3 substitution.",
}

BOSLING_RRNA_EVIDENCE = {
    "reference": "PMID:12936991",
    "snippet": (
        "No mutations in the rRNA were selected as resistance determinants "
        "using a strain expressing only a plasmid-encoded rRNA operon."
    ),
    "notes": "Bosling 2003 support for modeling the uL3 mutation as an in-trans determinant.",
}

BOSLING_REDUCED_BINDING_EVIDENCE = {
    "reference": "PMID:12936991",
    "snippet": "Chemical footprinting experiments show a reduced binding of tiamulin to mutant ribosomes.",
    "notes": "Bosling 2003 measured reduced tiamulin binding to mutant ribosomes.",
}

BOSLING_SITE_EVIDENCE = {
    "reference": "PMID:12936991",
    "snippet": (
        "It is inferred that the L3 mutation, which points into the peptidyl "
        "transferase cleft, causes tiamulin resistance by alteration of the "
        "drug-binding site."
    ),
    "notes": "Bosling 2003 inferred a resistance mechanism through altered tiamulin binding.",
}

BOSLING_PTC_EVIDENCE = {
    "reference": "PMID:12936991",
    "snippet": (
        "The antibiotic tiamulin targets the 50S subunit of the bacterial "
        "ribosome and interacts at the peptidyl transferase center."
    ),
    "notes": "Bosling 2003 identified the tiamulin interaction site.",
}

SCHLUENZEN_PTC_EVIDENCE = {
    "reference": "PMID:15554968",
    "snippet": (
        "Our results show that tiamulin is located within the peptidyl "
        "transferase center (PTC) of the 50S ribosomal subunit with its "
        "tricyclic mutilin core positioned in a tight pocket at the A-tRNA "
        "binding site."
    ),
    "notes": "Schlunzen 2004 located tiamulin in the 50S-subunit peptidyl transferase center.",
}

SCHLUENZEN_INHIBITION_EVIDENCE = {
    "reference": "PMID:15554968",
    "snippet": "Thereby, tiamulin directly inhibits peptide bond formation.",
    "notes": "Schlunzen 2004 linked tiamulin binding to inhibition of peptide bond formation.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies Thermus uL3 substitutions under mutation-conferring resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "The inherited mutation mechanism captures altered gene products that cause resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Thermus uL3 substitutions confer tiamulin resistance by reducing drug binding at the PTC.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts inherited pleuromutilin-antibiotic resistance on the ribosomal-protein parent.",
    (
        "family",
        "part of (the L3 family assignment of this determinant)",
        "determinant",
    ): "The determinant is a Thermus ribosomal protein uL3 variant.",
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
    ): "The modeled reduced binding state includes the pleuromutilin-class drug tiamulin.",
    (
        "drug_binding",
        "has part (the site it binds)",
        "ptc",
    ): "The modeled reduced binding state includes the PTC drug-binding site.",
    (
        "determinant",
        "causally upstream of (the substitution alters the conformation)",
        "altered_conformation",
    ): "The uL3 substitution acts in trans by altering local 23S rRNA conformation.",
    (
        "altered_conformation",
        "characteristic of (a conformation of the 23S rRNA)",
        "rrna23s",
    ): "The altered conformation is a local conformation of 23S rRNA.",
    (
        "altered_conformation",
        "negatively regulates (the altered site binds the drug less well)",
        "drug_binding",
    ): "The altered 23S-rRNA conformation reduces tiamulin binding at the drug-binding site.",
    (
        "determinant",
        "negatively regulates (mutation reduces drug binding)",
        "drug_binding",
    ): "Chemical footprinting showed reduced tiamulin binding to ribosomes bearing the uL3 mutation.",
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
        marker = (item["reference"], item["snippet"])
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
            extra = [UL3_EVIDENCE, PARENT_EVIDENCE, MUTATION_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [UL3_EVIDENCE, PARENT_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                UL3_EVIDENCE,
                PARENT_EVIDENCE,
                MUTATION_EVIDENCE,
                BOSLING_REDUCED_BINDING_EVIDENCE,
                BOSLING_SITE_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [PLEUROMUTILIN_RELATION_EVIDENCE, UL3_EVIDENCE, PARENT_EVIDENCE]
        case ("family", "part of (the L3 family assignment of this determinant)", "determinant"):
            extra = [PFAM_L3_EVIDENCE, UL3_EVIDENCE, BOSLING_L3_EVIDENCE]
        case ("ptc", "part of (the PTC of the 50S subunit)", "subunit50s"):
            extra = [SCHLUENZEN_PTC_EVIDENCE, BOSLING_PTC_EVIDENCE, GO_LARGE_SUBUNIT_EVIDENCE]
        case (
            "drug0",
            "molecularly interacts with (binds the peptidyl transferase centre)",
            "ptc",
        ):
            extra = [SCHLUENZEN_PTC_EVIDENCE, BOSLING_PTC_EVIDENCE]
        case ("drug_binding", "has part (the antibiotic)", "drug0"):
            extra = [BOSLING_REDUCED_BINDING_EVIDENCE, SCHLUENZEN_PTC_EVIDENCE]
        case ("drug_binding", "has part (the site it binds)", "ptc"):
            extra = [SCHLUENZEN_PTC_EVIDENCE, BOSLING_PTC_EVIDENCE]
        case (
            "determinant",
            "causally upstream of (the substitution alters the conformation)",
            "altered_conformation",
        ):
            extra = [UL3_EVIDENCE, PARENT_EVIDENCE, BOSLING_RRNA_EVIDENCE]
        case (
            "altered_conformation",
            "characteristic of (a conformation of the 23S rRNA)",
            "rrna23s",
        ):
            extra = [UL3_EVIDENCE, PARENT_EVIDENCE, SO_RRNA_EVIDENCE]
        case (
            "altered_conformation",
            "negatively regulates (the altered site binds the drug less well)",
            "drug_binding",
        ):
            extra = [BOSLING_SITE_EVIDENCE, BOSLING_REDUCED_BINDING_EVIDENCE, UL3_EVIDENCE]
        case ("determinant", "negatively regulates (mutation reduces drug binding)", "drug_binding"):
            extra = [
                BOSLING_REDUCED_BINDING_EVIDENCE,
                BOSLING_SITE_EVIDENCE,
                UL3_EVIDENCE,
                SCHLUENZEN_PTC_EVIDENCE,
            ]
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
    if record.get("identifier") != "ARO:3005081":
        raise ValueError(f"expected ARO:3005081, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = (
        "Thermus thermophilus uL3 mutation → 23S rRNA conformational change → "
        "pleuromutilin resistance"
    )
    graph["description"] = (
        "Curated resistance-causation graph for Thermus thermophilus uL3 "
        "substitutions that alter local 23S rRNA conformation in trans, reduce "
        "tiamulin binding at the peptidyl transferase center, and confer "
        "pleuromutilin resistance."
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
