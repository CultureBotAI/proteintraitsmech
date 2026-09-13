#!/usr/bin/env python3
"""Rewrite non-erm G748 23S rRNA methyltransferase ARO causal graphs.

These records are 23S rRNA methyltransferases that modify guanosine 748 rather
than the Cfr A2503 radical-SAM target.  This updater removes that stale Cfr-like
domain/fold path and replaces it with a local G748 N1-methylation path:

    G748 methyltransferase -> N1-methyl-G748 23S rRNA -> blocked drug binding

emtA is intentionally excluded: CARD places it under the same family, but its
evernimicin-resistance mechanism is at a different 23S rRNA nucleotide and needs
a separate model.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Curated non-erm 23S rRNA G748 methyltransferase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE = {
    "reference": "ARO:0001001",
    "snippet": (
        "Mutational alteration or enzymatic modification of antibiotic target "
        "which results in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target alteration.",
}

RIBOSOMAL_ALTERATION_EVIDENCE = {
    "reference": "ARO:3000211",
    "snippet": (
        "Chemical alteration of the ribosome results in modification of an "
        "antibiotic's target leading to resistance."
    ),
    "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
}

PARENT_EVIDENCE = {
    "reference": "ARO:3001298",
    "snippet": (
        "Non-erm 23S ribosomal RNA methyltransferases modify guanosine 748 to confer "
        "resistance to some macrolides and lincosamides."
    ),
    "notes": "CARD definition for the G748 non-erm 23S rRNA methyltransferase family.",
}

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of methyl-group transfer from S-adenosyl-L-methionine to an rRNA "
        "nucleoside residue."
    ),
    "notes": (
        "GO definition for the broad rRNA methyltransferase activity superclass; "
        "the ARO/PubMed evidence constrains the substrate to 23S rRNA G748."
    ),
}

G748_TARGET_EVIDENCE = {
    "reference": "PMID:15046978",
    "snippet": "RlmA(II) (TlrB) modifies the N-1 position of 23S rRNA nucleotide G748.",
    "notes": (
        "Douthwaite et al. identified the TlrB methylation site as N1 of G748 "
        "by mass spectrometry."
    ),
}

TLRB_G748_EVIDENCE = {
    "reference": "DOI:10.1046/j.1365-2958.2000.02046.x",
    "snippet": "TlrB of Streptomyces fradiae targets G748 in 23S rRNA.",
    "notes": "Primary characterization of TlrB as a G748-directed methyltransferase.",
}

G748_A2058_SYNERGY_EVIDENCE = {
    "reference": "PMID:12417742",
    "snippet": "TlrB and TlrD methylate 23S rRNA nucleotides G748 and A2058.",
    "notes": (
        "The Streptomyces fradiae tylosin producer uses G748 and A2058 "
        "methylations together for high tylosin resistance."
    ),
}

SO_RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide structural "
        "scaffolding and catalytic activity."
    ),
    "notes": (
        "Sequence Ontology definition for the broad rRNA superclass used as a "
        "conservative grounding for the local 23S rRNA G748 site."
    ),
}

DRUG_CLASS_EVIDENCE = {
    "drug0": {
        "reference": "ARO:0000000",
        "snippet": "macrolide antibiotic",
        "notes": "ARO drug-class term inherited by the G748 methyltransferase records.",
    },
    "drug1": {
        "reference": "ARO:0000017",
        "snippet": "lincosamide antibiotic",
        "notes": "ARO drug-class term inherited by the G748 methyltransferase records.",
    },
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the nearest "
        "available superclass: ARO models determinants and mechanisms but has no "
        "term for the resistance phenotype itself."
    ),
}

MECHANISM_NODES = [
    {
        "node_id": "mech0",
        "label": "antibiotic target alteration",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "ARO:0001001",
    },
    {
        "node_id": "mech1",
        "label": "ribosomal alteration conferring antibiotic resistance",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "ARO:3000211",
    },
    {
        "node_id": "methyltransferase",
        "label": "23S rRNA G748 N1-methyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008649",
        "description": (
            "Grounded to the broad GO rRNA methyltransferase activity term "
            "because no stable narrow GO term is available for N1 methylation "
            "of 23S rRNA G748."
        ),
    },
]

G748_TARGET_SITE_NODE = {
    "node_id": "target_site",
    "label": "23S rRNA G748 macrolide-binding site",
    "node_type": "NUCLEIC_ACID",
    "grounding": "SO:0000252",
    "description": (
        "Local node for guanosine 748 in hairpin 35 of 23S rRNA. Grounded to "
        "broad rRNA because no stable narrow term is available for this local "
        "23S rRNA nucleotide target."
    ),
}

METHYLATED_SITE_NODE = {
    "node_id": "methylated",
    "label": "N1-methyl-G748 23S rRNA site",
    "node_type": "STATE",
    "grounding": "SO:0000252",
    "description": (
        "Local state representing N1 methylation of guanosine 748 in 23S rRNA. "
        "Grounded to broad rRNA because no stable narrow term is available for "
        "this methylated local state."
    ),
}

SUBUNIT_NODE = {
    "node_id": "subunit",
    "label": "large ribosomal subunit (50S)",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0015934",
    "description": "The 50S subunit that contains bacterial 23S rRNA.",
}

DRUG_NODES = [
    {
        "node_id": "drug0",
        "label": "macrolide antibiotic",
        "node_type": "CHEMICAL",
        "grounding": "ARO:0000000",
    },
    {
        "node_id": "drug1",
        "label": "lincosamide antibiotic",
        "node_type": "CHEMICAL",
        "grounding": "ARO:0000017",
    },
]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3001298",
        "non-erm-23s-ribosomal-rna-methyltransferase-g748-aro3001298.yaml",
        PARENT_EVIDENCE,
    ),
    Target(
        "ARO:3001299",
        "tlrb-conferring-tylosin-resistance-aro3001299.yaml",
        {
            "reference": "ARO:3001299",
            "snippet": "TlrB adds a methyl group to guanosine 748 of 23S rRNA.",
            "notes": "CARD definition for tlrB conferring tylosin resistance.",
        },
    ),
    Target(
        "ARO:3001300",
        "myra-aro3001300.yaml",
        {
            "reference": "ARO:3001300",
            "snippet": "MyrA adds a methyl group to guanosine 748 of 23S rRNA.",
            "notes": "CARD definition for the mycinamicin-resistance MyrA methyltransferase.",
        },
    ),
    Target(
        "ARO:3001301",
        "rlma-ii-aro3001301.yaml",
        {
            "reference": "ARO:3001301",
            "snippet": "RlmA(II) adds a methyl group to guanosine 748 of 23S rRNA.",
            "notes": "CARD definition for the RlmA(II) methyltransferase.",
        },
    ),
    Target(
        "ARO:3001302",
        "chrb-aro3001302.yaml",
        {
            "reference": "ARO:3001302",
            "snippet": "ChrB adds a methyl group to guanosine 748.",
            "notes": "CARD definition for the chalcomycin-resistance ChrB methyltransferase.",
        },
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


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    determinant_evidence = (target.determinant_evidence, PARENT_EVIDENCE)
    target_alteration_evidence = (
        target.determinant_evidence,
        PARENT_EVIDENCE,
        ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE,
    )
    ribosomal_evidence = (
        target.determinant_evidence,
        PARENT_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
    )
    methyltransferase_evidence = (
        target.determinant_evidence,
        PARENT_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        TLRB_G748_EVIDENCE,
        G748_TARGET_EVIDENCE,
    )
    local_g748_evidence = (
        PARENT_EVIDENCE,
        TLRB_G748_EVIDENCE,
        G748_TARGET_EVIDENCE,
        G748_A2058_SYNERGY_EVIDENCE,
        SO_RRNA_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → 23S rRNA G748 methylation → resistance",
        "description": (
            "Curated resistance-causation graph for non-erm 23S rRNA "
            "methyltransferases that methylate guanosine 748. The graph models "
            "N1 methylation of a local 23S rRNA G748 site as the target alteration "
            "that blocks binding of G748-proximal ribosome-targeting antibiotics."
        ),
        "nodes": [
            _determinant_node(record),
            *(copy.deepcopy(node) for node in MECHANISM_NODES),
            copy.deepcopy(G748_TARGET_SITE_NODE),
            copy.deepcopy(METHYLATED_SITE_NODE),
            copy.deepcopy(SUBUNIT_NODE),
            *(copy.deepcopy(node) for node in DRUG_NODES),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies G748 23S rRNA methyltransferases under "
                "antibiotic target alteration.",
                *target_alteration_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Target alteration is the broad resistance mechanism represented "
                "by methylation of the 23S rRNA G748 site.",
                *target_alteration_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD also classifies G748 23S rRNA methyltransferases under "
                "the ribosome-specific target-alteration mechanism.",
                *ribosomal_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Methylation of 23S rRNA G748 is a ribosomal alteration that "
                "supports macrolide and lincosamide resistance.",
                *ribosomal_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant methylates 23S rRNA G748, producing a modified "
                "target site that changes drug binding.",
                *determinant_evidence,
                TLRB_G748_EVIDENCE,
                G748_TARGET_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts macrolide resistance for the non-erm G748 23S "
                "rRNA methyltransferase family.",
                *determinant_evidence,
                DRUG_CLASS_EVIDENCE["drug0"],
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug1",
                "CARD asserts lincosamide resistance for the non-erm G748 23S "
                "rRNA methyltransferase family.",
                *determinant_evidence,
                DRUG_CLASS_EVIDENCE["drug1"],
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "methyltransferase",
                "The determinant enables methyl transfer to the N1 position of "
                "23S rRNA guanosine 748.",
                *methyltransferase_evidence,
            ),
            _edge(
                "methyltransferase",
                "causally upstream of",
                "RO:0002411",
                "methylated",
                "G748-directed 23S rRNA methyltransferase activity yields an "
                "N1-methyl-G748 state.",
                *methyltransferase_evidence,
            ),
            _edge(
                "methylated",
                "negatively regulates (blocks antibiotic binding)",
                "RO:0002212",
                "target_site",
                "N1 methylation of G748 changes the 23S rRNA site contacted by "
                "tylosin and other macrolides at the large ribosomal subunit.",
                *local_g748_evidence,
            ),
            _edge(
                "methylated",
                "causally upstream of (blocks antibiotic binding)",
                "RO:0002411",
                "resistance",
                "The N1-methyl-G748 23S rRNA state is the terminal modeled "
                "target alteration supporting resistance.",
                *local_g748_evidence,
            ),
            _edge(
                "target_site",
                "part of",
                "BFO:0000050",
                "subunit",
                "The G748 target site is in 23S rRNA in the 50S ribosomal subunit.",
                *local_g748_evidence,
            ),
            _edge(
                "drug0",
                "molecularly interacts with",
                "RO:0002436",
                "target_site",
                "Macrolides act at a 23S rRNA target that includes the G748 site "
                "modified by TlrB-family methyltransferases.",
                *local_g748_evidence,
                DRUG_CLASS_EVIDENCE["drug0"],
            ),
            _edge(
                "drug1",
                "molecularly interacts with",
                "RO:0002436",
                "target_site",
                "Lincosamide resistance is inherited from the G748 "
                "methyltransferase parent; the graph keeps the same 23S rRNA "
                "target-site branch.",
                *determinant_evidence,
                DRUG_CLASS_EVIDENCE["drug1"],
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

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = {"determinant", "mech0", "mech1", "resistance"} - node_ids
    if missing_nodes:
        missing = ", ".join(sorted(missing_nodes))
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a G748 23S rRNA methyltransferase target: {identifier}")
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
        help="ARO directory or one of the G748 methyltransferase YAML files",
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
