#!/usr/bin/env python3
"""Describe catalytic antibiotic-inactivation ARO parent graphs.

The ADC/class beta-lactamase and AAC/ANT/APH aminoglycoside-modifying records
already have the right catalytic-feature/fold skeleton. This updater replaces
placeholder KB node descriptions, adds edge descriptions, and attaches exact
ARO mechanism evidence to every edge.

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

HISTORY_ACTION = "Completed catalytic antibiotic-inactivation causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

AMINOGLYCOSIDE_MODIFICATION_EVIDENCE = {
    "reference": "ARO:3007380",
    "snippet": (
        "Resistance-conferring genetic elements encoding proteins involved in "
        "the enzymatic inactivation of aminoglycoside antibiotics through "
        "chemical modification."
    ),
    "notes": "CARD definition for aminoglycoside-modifying enzymes.",
}

BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000001",
    "snippet": (
        "The lactamase enzyme breaks that ring open, deactivating the "
        "molecule's antibacterial properties."
    ),
    "notes": "CARD definition for beta-lactamases.",
}

ACETYLATION_EVIDENCE = {
    "reference": "ARO:3000106",
    "snippet": "Addition of an acyl group to an antibiotic, often via acetylation by acetylCoA.",
    "notes": "CARD definition for acylation of antibiotic conferring resistance.",
}

NUCLEOTIDYLATION_EVIDENCE = {
    "reference": "ARO:3000107",
    "snippet": "Modification by NMP, usually AMP.",
    "notes": "CARD definition for nucleotidylation of antibiotic conferring resistance.",
}

PHOSPHORYLATION_EVIDENCE = {
    "reference": "ARO:3000105",
    "snippet": "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
    "notes": "CARD definition for phosphorylation of antibiotic conferring resistance.",
}

SERINE_BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000187",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class A, C and D "
        "beta-lactamases. A serine residue located in the active site is used "
        "to form an acyl-enzyme intermediate and subsequent hydrolysis renders "
        "the beta-lactam inactive."
    ),
    "notes": "CARD definition for serine beta-lactamase hydrolysis.",
}

METALLO_BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000203",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class B "
        "beta-lactamases. One or two zinc atoms are used to orient a hydroxide "
        "nucleophile for attack of the beta-lactam ring."
    ),
    "notes": "CARD definition for metallo-beta-lactamase hydrolysis.",
}

AAC_REACTION_EVIDENCE = {
    "reference": "PMID:26818562",
    "snippet": (
        "N-Acetyltransferases transfer an acetyl group from acetyl-CoA to a "
        "large array of substrates, from small molecules such as aminoglycoside "
        "antibiotics to macromolecules."
    ),
    "notes": "Evidence for GNAT-mediated acetyl transfer to aminoglycosides.",
}

ANT_REACTION_EVIDENCE = {
    "reference": "PMID:25564464",
    "snippet": (
        "ANT(2″)-Ia confers resistance by magnesium-dependent transfer of a "
        "nucleoside monophosphate (AMP) to the 2″-hydroxyl of aminoglycoside "
        "substrates containing a 2-deoxystreptamine core."
    ),
    "notes": "Evidence for aminoglycoside nucleotidyltransferase activity.",
}

APH_REACTION_EVIDENCE = {
    "reference": "PMID:9200607",
    "snippet": (
        "Structure of an enzyme required for aminoglycoside antibiotic "
        "resistance reveals homology to eukaryotic protein kinases."
    ),
    "notes": "Evidence for the protein-kinase-like APH fold.",
}

SERINE_BETA_LACTAMASE_REACTION_EVIDENCE = {
    "reference": "PMID:32576842",
    "snippet": (
        "In the first acylation step, the β-lactam antibiotic forms an "
        "acyl-enzyme intermediate (ES*) with the catalytic serine residue."
    ),
    "notes": "Evidence for the serine beta-lactamase acyl-enzyme mechanism.",
}

AMPC_REACTION_EVIDENCE = {
    "reference": "PMID:19136439",
    "snippet": (
        "AmpC β-lactamases are clinically important cephalosporinases encoded "
        "on the chromosomes of many of the Enterobacteriaceae and a few other "
        "organisms."
    ),
    "notes": "Evidence for AmpC/class C beta-lactamases.",
}

MBL_REACTION_EVIDENCE = {
    "reference": "PMID:33199283",
    "snippet": (
        "MBLs are one class of β-lactamases (Ambler class B), requiring "
        "divalent zinc ions for their β-lactamase activity."
    ),
    "notes": "Evidence for zinc-dependent metallo-beta-lactamase activity.",
}

INTERPRO_GNAT_EVIDENCE = {
    "reference": "InterPro:IPR000182",
    "snippet": "GNAT domain",
    "notes": "InterPro domain carried by GNAT acetyltransferases.",
}

CATH_GNAT_EVIDENCE = {
    "reference": "CATH:3.40.630",
    "snippet": "Aminopeptidase",
    "notes": "CATH fold used by GNAT acetyltransferases.",
}

PFAM_NUCLEOTIDYLTRANSFERASE_EVIDENCE = {
    "reference": "Pfam:PF01909",
    "snippet": "Nucleotidyltransferase domain",
    "notes": "Pfam family for aminoglycoside nucleotidyltransferases.",
}

CATH_NUCLEOTIDYLTRANSFERASE_EVIDENCE = {
    "reference": "CATH:3.30.460",
    "snippet": "Beta Polymerase; domain 2",
    "notes": "CATH fold for nucleotidyltransferases.",
}

PFAM_PHOSPHOTRANSFERASE_EVIDENCE = {
    "reference": "Pfam:PF01636",
    "snippet": "Phosphotransferase enzyme family",
    "notes": "Pfam family for aminoglycoside phosphotransferases.",
}

CATH_PHOSPHOTRANSFERASE_EVIDENCE = {
    "reference": "CATH:3.90.1200",
    "snippet": "Aminoglycoside 3'-phosphotransferase; Chain: A, domain 2",
    "notes": "CATH fold for aminoglycoside phosphotransferases.",
}

PROSITE_CLASS_A_EVIDENCE = {
    "reference": "PROSITE:PS00146",
    "snippet": "Beta-lactamase class-A active site",
    "notes": "PROSITE active-site signature for class A beta-lactamases.",
}

PROSITE_CLASS_C_EVIDENCE = {
    "reference": "PROSITE:PRU10102",
    "snippet": "Beta-lactamase class-C active site",
    "notes": "PROSITE active-site signature for class C beta-lactamases.",
}

PFAM_MBL_EVIDENCE = {
    "reference": "Pfam:PF00753",
    "snippet": "Metallo-beta-lactamase superfamily",
    "notes": "Pfam family for metallo-beta-lactamases.",
}

CATH_SERINE_BETA_LACTAMASE_EVIDENCE = {
    "reference": "CATH:3.40.710.10",
    "snippet": "DD-peptidase/beta-lactamase superfamily",
    "notes": "CATH fold for serine beta-lactamases.",
}

CATH_MBL_EVIDENCE = {
    "reference": "CATH:3.60.15.30",
    "snippet": "Metallo-beta-lactamase domain",
    "notes": "CATH fold for metallo-beta-lactamases.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    mechanism_id: str
    mechanism_label: str
    mechanism_evidence: dict[str, str]
    family_evidence: dict[str, str]
    reaction_evidence: dict[str, str]
    catalytic_node_id: str
    catalytic_node: dict[str, str]
    catalytic_evidence: dict[str, str]
    fold_node: dict[str, str]
    fold_evidence: dict[str, str]
    catalytic_predicate: str


TARGETS: tuple[Target, ...] = (
    Target(
        identifier="ARO:3005459",
        filename="adc-beta-lactamase-aro3005459.yaml",
        mechanism_id="ARO:3000187",
        mechanism_label="hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
        mechanism_evidence=SERINE_BETA_LACTAMASE_EVIDENCE,
        family_evidence=BETA_LACTAMASE_EVIDENCE,
        reaction_evidence=AMPC_REACTION_EVIDENCE,
        catalytic_node_id="active_site",
        catalytic_node={
            "node_id": "active_site",
            "label": "class C beta-lactamase active-site signature (Ser64 S-x-x-K)",
            "node_type": "MOTIF",
            "grounding": "PROSITE:PRU10102",
            "description": "Class C beta-lactamase catalytic serine active-site signature.",
        },
        catalytic_evidence=PROSITE_CLASS_C_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "DD-peptidase/beta-lactamase superfamily fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.40.710.10",
            "description": "DD-peptidase/beta-lactamase superfamily fold.",
        },
        fold_evidence=CATH_SERINE_BETA_LACTAMASE_EVIDENCE,
        catalytic_predicate="enables (serine beta-lactam hydrolysis)",
    ),
    Target(
        identifier="ARO:3000121",
        filename="aminoglycoside-acetyltransferase-aac-aro3000121.yaml",
        mechanism_id="ARO:3000106",
        mechanism_label="acylation of antibiotic conferring resistance",
        mechanism_evidence=ACETYLATION_EVIDENCE,
        family_evidence=AMINOGLYCOSIDE_MODIFICATION_EVIDENCE,
        reaction_evidence=AAC_REACTION_EVIDENCE,
        catalytic_node_id="domain",
        catalytic_node={
            "node_id": "domain",
            "label": "GNAT acetyltransferase domain",
            "node_type": "DOMAIN",
            "grounding": "InterPro:IPR000182",
            "description": "GNAT acetyltransferase domain that modifies aminoglycosides.",
        },
        catalytic_evidence=INTERPRO_GNAT_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "acyl-CoA N-acyltransferase (GNAT) fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.40.630",
            "description": "GNAT acyltransferase structural fold.",
        },
        fold_evidence=CATH_GNAT_EVIDENCE,
        catalytic_predicate="enables (antibiotic acetylation)",
    ),
    Target(
        identifier="ARO:3000218",
        filename="aminoglycoside-nucleotidyltransferase-ant-aro3000218.yaml",
        mechanism_id="ARO:3000107",
        mechanism_label="nucleotidylation of antibiotic conferring resistance",
        mechanism_evidence=NUCLEOTIDYLATION_EVIDENCE,
        family_evidence=AMINOGLYCOSIDE_MODIFICATION_EVIDENCE,
        reaction_evidence=ANT_REACTION_EVIDENCE,
        catalytic_node_id="domain",
        catalytic_node={
            "node_id": "domain",
            "label": "nucleotidyltransferase domain",
            "node_type": "DOMAIN",
            "grounding": "Pfam:PF01909",
            "description": "Nucleotidyltransferase domain that modifies aminoglycosides.",
        },
        catalytic_evidence=PFAM_NUCLEOTIDYLTRANSFERASE_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "DNA-polymerase-β-like nucleotidyltransferase fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.30.460",
            "description": "Beta-polymerase-like nucleotidyltransferase fold.",
        },
        fold_evidence=CATH_NUCLEOTIDYLTRANSFERASE_EVIDENCE,
        catalytic_predicate="enables (antibiotic nucleotidylation)",
    ),
    Target(
        identifier="ARO:3000114",
        filename="aminoglycoside-phosphotransferase-aph-aro3000114.yaml",
        mechanism_id="ARO:3000105",
        mechanism_label="phosphorylation of antibiotic conferring resistance",
        mechanism_evidence=PHOSPHORYLATION_EVIDENCE,
        family_evidence=AMINOGLYCOSIDE_MODIFICATION_EVIDENCE,
        reaction_evidence=APH_REACTION_EVIDENCE,
        catalytic_node_id="domain",
        catalytic_node={
            "node_id": "domain",
            "label": "aminoglycoside phosphotransferase domain",
            "node_type": "DOMAIN",
            "grounding": "Pfam:PF01636",
            "description": "Phosphotransferase domain that modifies aminoglycosides.",
        },
        catalytic_evidence=PFAM_PHOSPHOTRANSFERASE_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "aminoglycoside phosphotransferase (protein-kinase-like) fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.90.1200",
            "description": "Protein-kinase-like aminoglycoside phosphotransferase fold.",
        },
        fold_evidence=CATH_PHOSPHOTRANSFERASE_EVIDENCE,
        catalytic_predicate="enables (antibiotic phosphorylation)",
    ),
    Target(
        identifier="ARO:3000078",
        filename="class-a-beta-lactamase-aro3000078.yaml",
        mechanism_id="ARO:3000187",
        mechanism_label="hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
        mechanism_evidence=SERINE_BETA_LACTAMASE_EVIDENCE,
        family_evidence=BETA_LACTAMASE_EVIDENCE,
        reaction_evidence=SERINE_BETA_LACTAMASE_REACTION_EVIDENCE,
        catalytic_node_id="active_site",
        catalytic_node={
            "node_id": "active_site",
            "label": "class A beta-lactamase active-site signature (S-x-x-K)",
            "node_type": "MOTIF",
            "grounding": "PROSITE:PS00146",
            "description": "Class A beta-lactamase catalytic serine active-site signature.",
        },
        catalytic_evidence=PROSITE_CLASS_A_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "DD-peptidase/beta-lactamase superfamily fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.40.710.10",
            "description": "DD-peptidase/beta-lactamase superfamily fold.",
        },
        fold_evidence=CATH_SERINE_BETA_LACTAMASE_EVIDENCE,
        catalytic_predicate="enables (serine beta-lactam hydrolysis)",
    ),
    Target(
        identifier="ARO:3000004",
        filename="class-b-metallo-beta-lactamase-aro3000004.yaml",
        mechanism_id="ARO:3000203",
        mechanism_label="hydrolysis of beta-lactam antibiotic by metallo-beta-lactamase",
        mechanism_evidence=METALLO_BETA_LACTAMASE_EVIDENCE,
        family_evidence=BETA_LACTAMASE_EVIDENCE,
        reaction_evidence=MBL_REACTION_EVIDENCE,
        catalytic_node_id="domain",
        catalytic_node={
            "node_id": "domain",
            "label": "metallo-beta-lactamase superfamily domain",
            "node_type": "DOMAIN",
            "grounding": "Pfam:PF00753",
            "description": "Metallo-beta-lactamase domain that binds catalytic zinc.",
        },
        catalytic_evidence=PFAM_MBL_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "metallo-beta-lactamase domain fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.60.15.30",
            "description": "Metallo-beta-lactamase structural fold.",
        },
        fold_evidence=CATH_MBL_EVIDENCE,
        catalytic_predicate="enables (zinc-dependent beta-lactam hydrolysis)",
    ),
    Target(
        identifier="ARO:3000076",
        filename="class-c-beta-lactamase-aro3000076.yaml",
        mechanism_id="ARO:3000187",
        mechanism_label="hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
        mechanism_evidence=SERINE_BETA_LACTAMASE_EVIDENCE,
        family_evidence=BETA_LACTAMASE_EVIDENCE,
        reaction_evidence=AMPC_REACTION_EVIDENCE,
        catalytic_node_id="active_site",
        catalytic_node={
            "node_id": "active_site",
            "label": "class C beta-lactamase active-site signature (Ser64 S-x-x-K)",
            "node_type": "MOTIF",
            "grounding": "PROSITE:PRU10102",
            "description": "Class C beta-lactamase catalytic serine active-site signature.",
        },
        catalytic_evidence=PROSITE_CLASS_C_EVIDENCE,
        fold_node={
            "node_id": "fold",
            "label": "DD-peptidase/beta-lactamase superfamily fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.40.710.10",
            "description": "DD-peptidase/beta-lactamase superfamily fold.",
        },
        fold_evidence=CATH_SERINE_BETA_LACTAMASE_EVIDENCE,
        catalytic_predicate="enables (serine beta-lactam hydrolysis)",
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


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    target_evidence = _record_evidence(record)
    broad_evidence = (
        target_evidence,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        target.family_evidence,
        target.reaction_evidence,
    )
    specific_evidence = (
        target_evidence,
        target.family_evidence,
        target.mechanism_evidence,
        target.reaction_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → catalytic antibiotic inactivation → resistance",
        "description": (
            "Curated resistance-causation graph for catalytic antibiotic "
            "inactivation. The determinant participates in broad antibiotic "
            f"inactivation and in the narrower {target.mechanism_label} "
            "mechanism through a grounded catalytic feature and fold."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            {
                "node_id": "mech1",
                "label": target.mechanism_label,
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": target.mechanism_id,
            },
            copy.deepcopy(target.catalytic_node),
            copy.deepcopy(target.fold_node),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this enzyme under antibiotic inactivation.",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Enzymatic antibiotic inactivation removes active antibiotic and "
                "thereby causes resistance.",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies this enzyme under a narrower catalytic "
                "antibiotic-modification mechanism.",
                *specific_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The narrower catalytic mechanism produces an inactive "
                "antibiotic species.",
                *specific_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant modifies and inactivates antibiotic molecules.",
                *broad_evidence,
            ),
            _edge(
                target.catalytic_node_id,
                "part of",
                "BFO:0000050",
                "determinant",
                "The grounded catalytic feature is part of the inactivation "
                "enzyme represented by the determinant.",
                target_evidence,
                target.catalytic_evidence,
                target.reaction_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the grounded fold associated with this "
                "catalytic family.",
                target_evidence,
                target.fold_evidence,
                target.reaction_evidence,
            ),
            _edge(
                target.catalytic_node_id,
                target.catalytic_predicate,
                "RO:0002327",
                "mech1",
                "The catalytic feature enables the narrower antibiotic "
                "modification mechanism.",
                target_evidence,
                target.mechanism_evidence,
                target.catalytic_evidence,
                target.reaction_evidence,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    required_nodes = {
        "determinant",
        "mech0",
        "mech1",
        target.catalytic_node_id,
        "fold",
        "resistance",
    }
    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = sorted(required_nodes - node_ids)
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a catalytic inactivation target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the catalytic target YAML files",
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
