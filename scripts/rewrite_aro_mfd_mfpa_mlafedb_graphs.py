#!/usr/bin/env python3
"""Rewrite low-score mfd, mfpA, and mlaFEDB ARO graphs.

These three records sat next to each other in the score-77 queue but need
different curation:

* mfd was auto-curated through the inherited Qnr target-protection parent.  The
  cited Campylobacter work supports transcription-repair-coupling-driven
  mutagenesis that promotes emergence of fluoroquinolone resistance instead.
* mfpA is a genuine pentapeptide-repeat target-protection protein and should
  keep the MfpA/DNA-gyrase/DNA-mimicry path.
* mlaFEDB is a phospholipid-transport ABC complex; the evidence supports
  MlaFEDB retrograde phospholipid trafficking and MlaF insertion-associated
  linezolid resistance, not direct antibiotic efflux by this pump.

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

HISTORY_ACTION = "Replaced stale mfd, mfpA, and mlaFEDB scaffolds"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_kind: str


TARGETS = (
    Target(
        "ARO:3003844",
        "mfd-aro3003844.yaml",
        "mfd",
    ),
    Target(
        "ARO:3003035",
        "mfpa-aro3003035.yaml",
        "mfpa",
    ),
    Target(
        "ARO:3005058",
        "mlafedb-aro3005058.yaml",
        "mlafedb",
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


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

FLUOROQUINOLONE_NODE = {
    "node_id": "drug0",
    "label": "fluoroquinolone antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000001",
}

OXAZOLIDINONE_NODE = {
    "node_id": "drug0",
    "label": "oxazolidinone antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000079",
}


MFD_TRANSCRIPTION_REPAIR_EVIDENCE = {
    "reference": "PMID:18535657",
    "snippet": (
        "Most importantly, ciprofloxacin induced the expression of mfd, which "
        "encodes a transcription-repair coupling factor involved in "
        "strand-specific DNA repair."
    ),
    "notes": (
        "Han et al. identify mfd as the fluoroquinolone-inducible "
        "transcription-repair coupling factor in C. jejuni."
    ),
}

MFD_MUTATION_EVIDENCE = {
    "reference": "PMID:18535657",
    "snippet": (
        "Mutation of the mfd gene resulted in an approximately 100-fold "
        "reduction in the rate of spontaneous mutation to ciprofloxacin "
        "resistance, while overexpression of mfd elevated the mutation "
        "frequency."
    ),
    "notes": (
        "Mfd activity increased the mutation frequency leading to "
        "ciprofloxacin resistance."
    ),
}

MFD_RESISTANCE_EVIDENCE = {
    "reference": "PMID:18535657",
    "snippet": (
        "In addition, loss of mfd in C. jejuni significantly reduced the "
        "development of fluoroquinolone-resistant Campylobacter in culture "
        "media or chickens treated with fluoroquinolones."
    ),
    "notes": (
        "Loss of mfd reduced fluoroquinolone-resistance development both in "
        "culture and in fluoroquinolone-treated chickens."
    ),
}


MFPA_RESISTANCE_EVIDENCE = {
    "reference": "PMID:15933203",
    "snippet": (
        "The expression of MfpA, a member of the pentapeptide repeat family of "
        "proteins from Mycobacterium tuberculosis, causes resistance to "
        "ciprofloxacin and sparfloxacin."
    ),
    "notes": "Hegde et al. show MfpA expression causes fluoroquinolone resistance.",
}

MFPA_GYRASE_EVIDENCE = {
    "reference": "PMID:15933203",
    "snippet": "This protein binds to DNA gyrase and inhibits its activity.",
    "notes": "MfpA binds and inhibits the fluoroquinolone target DNA gyrase.",
}

MFPA_MIMICRY_EVIDENCE = {
    "reference": "PMID:15933203",
    "snippet": (
        "Its three-dimensional structure reveals a fold, which we have named "
        "the right-handed quadrilateral beta helix, that exhibits size, "
        "shape, and electrostatic similarity to B-form DNA."
    ),
    "notes": (
        "The right-handed beta-helical pentapeptide-repeat fold explains the "
        "DNA mimicry used for target protection."
    ),
}

PENTAPEPTIDE_REPEAT_EVIDENCE = {
    "reference": "InterPro:IPR001646",
    "snippet": (
        "The structure of MfpA represents a form of DNA mimicry as it exhibits "
        "size, shape, and electrostatic similarity to B-form DNA and thus "
        "acting as a DNA gyrase inhibitor."
    ),
    "notes": "InterPro pentapeptide-repeat entry citing DOI:10.1126/science.1110699.",
}


MLAF_INSERTION_EVIDENCE = {
    "reference": "ARO:3005041",
    "snippet": (
        "mlaF from the mla system is a gene proposed to play a part in the "
        "transport of phospholipids to the outer membrane. Insertions in mlaF "
        "are shown to confer resistance to linezolid."
    ),
    "notes": (
        "CARD definition for the MlaF subunit; linezolid is an "
        "oxazolidinone-class antibiotic."
    ),
}

MLAFEDB_COMPLEX_EVIDENCE = {
    "reference": "PMID:27529189",
    "snippet": (
        "We establish that the transporter comprises canonical components, "
        "MlaF and MlaE, and auxiliary proteins, MlaD and MlaB, of previously "
        "unknown functions."
    ),
    "notes": "Thong et al. define the MlaFEDB inner-membrane ABC transporter complex.",
}

MLAFEDB_ACTIVITY_EVIDENCE = {
    "reference": "PMID:27529189",
    "snippet": (
        "MlaB plays critical roles in both the assembly and activity of the "
        "transporter."
    ),
    "notes": "MlaB is required for MlaFEDB assembly and activity.",
}

MLAFEDB_TRANSPORT_EVIDENCE = {
    "reference": "PMID:27529189",
    "snippet": (
        "Our work provides mechanistic insights into how the MlaFEDB complex "
        "participates in ensuring active retrograde PL transport to maintain "
        "OM lipid asymmetry."
    ),
    "notes": (
        "MlaFEDB drives retrograde phospholipid transport that maintains "
        "outer-membrane lipid asymmetry."
    ),
}

MLA_PATHWAY_EVIDENCE = {
    "reference": "PMID:19383799",
    "snippet": (
        "We have identified an ABC transport system in Escherichia coli with "
        "predicted import function that serves to prevent PL accumulation in "
        "the outer leaflet of the OM."
    ),
    "notes": (
        "Malinverni and Silhavy identify the Mla ABC system that maintains "
        "outer-membrane lipid asymmetry."
    ),
}

MLA_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF02470",
    "snippet": (
        "MlaFEDB complex is composed of two ATP-binding proteins (MlaF), two "
        "transmembrane proteins (MlaE), two cytoplasmic solute-binding "
        "proteins (MlaB) and a probable periplamic solute-binding protein "
        "(MlaD)."
    ),
    "notes": "Pfam MlaD entry quoting the InterPro IPR003399 MlaD abstract.",
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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(
    record: dict[str, Any],
    drug: str,
    label: str,
) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": f"relationship: confers_resistance_to_drug_class {drug} ! {label}",
        "notes": (
            f"Asserted directly on {record['identifier']} ({record['label']}) "
            "in the CARD/ARO release represented by this YAML record."
        ),
    }


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
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
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


MFD_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech0"),
}

MFD_OUTPUT_EDGE_KEYS = {
    ("determinant", "RO:0002327", "damaged_dna_binding"),
    ("determinant", "RO:0002327", "atp_binding"),
    ("determinant", "RO:0000056", "dna_repair"),
    ("damaged_dna_binding", "RO:0002411", "dna_repair"),
    ("atp_binding", "RO:0002411", "dna_repair"),
    ("dna_repair", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

MFPA_OUTPUT_EDGE_KEYS = {
    ("repeat", "BFO:0000050", "determinant"),
    ("determinant", "RO:0000056", "mech0"),
    ("repeat", "RO:0002327", "mech0"),
    ("determinant", "RO:0002436", "target"),
    ("determinant", "RO:0002212", "target"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

MLAFEDB_OUTPUT_EDGE_KEYS = {
    ("mlaf", "BFO:0000050", "determinant"),
    ("mlae", "BFO:0000050", "determinant"),
    ("mlab", "BFO:0000050", "determinant"),
    ("mlad", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "abc_complex"),
    ("mlaf", "RO:0002327", "atp_binding"),
    ("atp_binding", "RO:0002411", "phospholipid_transport"),
    ("determinant", "RO:0000056", "phospholipid_transport"),
    ("phospholipid_transport", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

MFD_ALLOWED_EDGE_KEYS = MFD_INPUT_EDGE_KEYS | MFD_OUTPUT_EDGE_KEYS
MFPA_ALLOWED_EDGE_KEYS = MFD_INPUT_EDGE_KEYS | MFPA_OUTPUT_EDGE_KEYS
MLAFEDB_ALLOWED_EDGE_KEYS = MFD_INPUT_EDGE_KEYS | MLAFEDB_OUTPUT_EDGE_KEYS


def _validate_input_graph(
    record: dict[str, Any],
    target: Target,
    allowed_edges: set[tuple[str, str, str]],
) -> None:
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graphs[0].get("edges")):
        key = _edge_key(edge)
        if key not in allowed_edges:
            raise ValueError(
                f"{target.identifier}: unexpected input edge "
                f"{key[0]} {key[1]} {key[2]}"
            )
        if key in seen:
            raise ValueError(
                f"{target.identifier}: duplicate input edge "
                f"{key[0]} {key[1]} {key[2]}"
            )
        seen.add(key)


def _validate_record(
    record: dict[str, Any],
    target: Target,
    allowed_edges: set[tuple[str, str, str]],
) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")
    _validate_input_graph(record, target, allowed_edges)


def _mfd_graph(record: dict[str, Any]) -> dict[str, Any]:
    record_ev = _record_evidence(record)
    repair_evidence = (record_ev, MFD_TRANSCRIPTION_REPAIR_EVIDENCE)
    resistance_evidence = (record_ev, MFD_MUTATION_EVIDENCE, MFD_RESISTANCE_EVIDENCE)

    return {
        "graph_id": "resistance",
        "title": "mfd → transcription-coupled DNA repair → fluoroquinolone resistance emergence",
        "description": (
            "Curated Mfd graph that replaces the stale inherited Qnr "
            "pentapeptide-repeat target-protection scaffold. Mfd is a "
            "transcription-repair coupling factor whose ATP-dependent "
            "handling of stalled transcription complexes promotes the "
            "mutation supply from which fluoroquinolone-resistant "
            "Campylobacter emerges."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "damaged_dna_binding",
                "label": "damaged DNA binding",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0003684",
            },
            {
                "node_id": "atp_binding",
                "label": "ATP binding",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0005524",
            },
            {
                "node_id": "dna_repair",
                "label": "transcription-coupled DNA repair",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0006283",
            },
            copy.deepcopy(FLUOROQUINOLONE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "damaged_dna_binding",
                "Mfd is the damaged-DNA-recognizing transcription-repair coupling factor.",
                *repair_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "atp_binding",
                "Mfd uses ATP to displace RNA polymerase from DNA lesions.",
                *repair_evidence,
            ),
            _edge(
                "determinant",
                "participates in",
                "RO:0000056",
                "dna_repair",
                "Mfd participates in transcription-coupled, strand-specific DNA repair.",
                *repair_evidence,
            ),
            _edge(
                "damaged_dna_binding",
                "causally upstream of",
                "RO:0002411",
                "dna_repair",
                "Damage recognition is part of Mfd-mediated transcription-coupled repair.",
                *repair_evidence,
            ),
            _edge(
                "atp_binding",
                "causally upstream of",
                "RO:0002411",
                "dna_repair",
                "ATP-dependent RNA-polymerase displacement supports Mfd-mediated repair.",
                *repair_evidence,
            ),
            _edge(
                "dna_repair",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                (
                    "Mfd-coupled repair promotes the mutation frequency that "
                    "allows fluoroquinolone resistance to develop."
                ),
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (promotes emergence of resistance)",
                "RO:0002411",
                "resistance",
                "Mfd is required for efficient fluoroquinolone-resistance emergence.",
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                (
                    "Mfd promotes emergence of fluoroquinolone resistance; "
                    "the graph uses the drug class from the ARO record but not "
                    "the inherited Qnr target-protection mechanism."
                ),
                record_ev,
                MFD_RESISTANCE_EVIDENCE,
            ),
        ],
    }


def _mfpa_graph(record: dict[str, Any]) -> dict[str, Any]:
    record_ev = _record_evidence(record)
    target_protection_evidence = (
        record_ev,
        MFPA_RESISTANCE_EVIDENCE,
        MFPA_GYRASE_EVIDENCE,
    )
    mimicry_evidence = (
        record_ev,
        MFPA_MIMICRY_EVIDENCE,
        PENTAPEPTIDE_REPEAT_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": "mfpA → DNA-gyrase target protection → fluoroquinolone resistance",
        "description": (
            "Curated MfpA target-protection graph. MfpA is a "
            "pentapeptide-repeat DNA mimic that binds and inhibits DNA gyrase, "
            "protecting the fluoroquinolone target and causing resistance to "
            "ciprofloxacin and sparfloxacin."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "repeat",
                "label": "pentapeptide repeat",
                "node_type": "DOMAIN",
                "grounding": "InterPro:IPR001646",
            },
            {
                "node_id": "target",
                "label": "DNA gyrase activity",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0003918",
            },
            {
                "node_id": "mech0",
                "label": "antibiotic target protection",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001003",
            },
            copy.deepcopy(FLUOROQUINOLONE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "repeat",
                "part of",
                "BFO:0000050",
                "determinant",
                "MfpA is a member of the pentapeptide-repeat protein family.",
                record_ev,
                MFPA_RESISTANCE_EVIDENCE,
                PENTAPEPTIDE_REPEAT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "MfpA protects the fluoroquinolone target DNA gyrase.",
                *target_protection_evidence,
            ),
            _edge(
                "repeat",
                "enables target protection by DNA mimicry",
                "RO:0002327",
                "mech0",
                "The pentapeptide-repeat fold mimics B-form DNA and enables target protection.",
                *mimicry_evidence,
            ),
            _edge(
                "determinant",
                "molecularly interacts with",
                "RO:0002436",
                "target",
                "MfpA binds the DNA-gyrase antibiotic target.",
                *target_protection_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates (inhibits DNA gyrase)",
                "RO:0002212",
                "target",
                "MfpA binding inhibits DNA-gyrase activity.",
                *target_protection_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "MfpA target protection blocks the fluoroquinolone target and causes resistance.",
                *target_protection_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "MfpA expression causes fluoroquinolone resistance.",
                *target_protection_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "MfpA causes resistance to ciprofloxacin and sparfloxacin.",
                record_ev,
                MFPA_RESISTANCE_EVIDENCE,
            ),
        ],
    }


def _mlafedb_graph(record: dict[str, Any]) -> dict[str, Any]:
    record_ev = _record_evidence(record)
    complex_evidence = (
        record_ev,
        MLAFEDB_COMPLEX_EVIDENCE,
        MLA_DOMAIN_EVIDENCE,
    )
    transport_evidence = (
        record_ev,
        MLAFEDB_TRANSPORT_EVIDENCE,
        MLA_PATHWAY_EVIDENCE,
    )
    resistance_evidence = (
        record_ev,
        MLAFEDB_TRANSPORT_EVIDENCE,
        MLAF_INSERTION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": "mlaFEDB → phospholipid transport → oxazolidinone resistance",
        "description": (
            "Curated MlaFEDB graph that treats the determinant as an "
            "inner-membrane ABC complex for Mla-pathway retrograde "
            "phospholipid transport. The graph keeps CARD's oxazolidinone "
            "resistance assertion while replacing the stale direct "
            "antibiotic-efflux scaffold with MlaFEDB phospholipid "
            "trafficking and MlaF insertion evidence."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mlaf",
                "label": "MlaF ATP-binding subunit",
                "node_type": "PROTEIN",
                "grounding": "NCBIfam:NF008809",
            },
            {
                "node_id": "mlae",
                "label": "MlaE permease subunit",
                "node_type": "PROTEIN",
                "grounding": "NCBIfam:NF033619",
            },
            {
                "node_id": "mlab",
                "label": "MlaB auxiliary subunit",
                "node_type": "PROTEIN",
                "grounding": "NCBIfam:NF033618",
            },
            {
                "node_id": "mlad",
                "label": "MlaD substrate-binding subunit",
                "node_type": "PROTEIN",
                "grounding": "NCBIfam:TIGR04430",
            },
            {
                "node_id": "abc_complex",
                "label": "ATP-binding cassette (ABC) transporter complex",
                "node_type": "CELLULAR_LOCALIZATION",
                "grounding": "GO:0043190",
            },
            {
                "node_id": "atp_binding",
                "label": "ATP binding",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0005524",
            },
            {
                "node_id": "phospholipid_transport",
                "label": "phospholipid transport",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0015914",
            },
            copy.deepcopy(OXAZOLIDINONE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "mlaf",
                "part of",
                "BFO:0000050",
                "determinant",
                "MlaFEDB contains two MlaF ATP-binding subunits.",
                *complex_evidence,
            ),
            _edge(
                "mlae",
                "part of",
                "BFO:0000050",
                "determinant",
                "MlaFEDB contains two MlaE transmembrane subunits.",
                *complex_evidence,
            ),
            _edge(
                "mlab",
                "part of",
                "BFO:0000050",
                "determinant",
                "MlaFEDB contains MlaB auxiliary subunits.",
                *complex_evidence,
                MLAFEDB_ACTIVITY_EVIDENCE,
            ),
            _edge(
                "mlad",
                "part of",
                "BFO:0000050",
                "determinant",
                "MlaFEDB contains an MlaD phospholipid-binding subunit.",
                *complex_evidence,
                MLAFEDB_TRANSPORT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "abc_complex",
                "MlaFEDB is an ATP-binding cassette transporter complex.",
                *complex_evidence,
            ),
            _edge(
                "mlaf",
                "enables",
                "RO:0002327",
                "atp_binding",
                "MlaF is the ATP-binding subunit of the MlaFEDB ABC transporter.",
                *complex_evidence,
            ),
            _edge(
                "atp_binding",
                "causally upstream of",
                "RO:0002411",
                "phospholipid_transport",
                (
                    "ATP binding by MlaF powers the active MlaFEDB "
                    "phospholipid transporter."
                ),
                record_ev,
                MLAFEDB_COMPLEX_EVIDENCE,
                MLAFEDB_TRANSPORT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in",
                "RO:0000056",
                "phospholipid_transport",
                "MlaFEDB participates in active retrograde phospholipid transport.",
                *transport_evidence,
            ),
            _edge(
                "phospholipid_transport",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                (
                    "Disruption of the Mla phospholipid-transport complex is "
                    "the Mla-system route to oxazolidinone resistance."
                ),
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    "The MlaFEDB determinant is associated with "
                    "oxazolidinone resistance through Mla-system "
                    "phospholipid-transport perturbation."
                ),
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that mlaFEDB confers resistance to the oxazolidinone class.",
                _drug_relation_evidence(record, "ARO:3000079", "oxazolidinone antibiotic"),
                MLAF_INSERTION_EVIDENCE,
            ),
        ],
    }


GRAPH_BUILDERS = {
    "mfd": (_mfd_graph, MFD_ALLOWED_EDGE_KEYS),
    "mfpa": (_mfpa_graph, MFPA_ALLOWED_EDGE_KEYS),
    "mlafedb": (_mlafedb_graph, MLAFEDB_ALLOWED_EDGE_KEYS),
}


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    builder, allowed_edges = GRAPH_BUILDERS[target.graph_kind]
    _validate_record(record, target, allowed_edges)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [builder(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an mfd/mfpA/mlaFEDB target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or a target YAML file",
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
