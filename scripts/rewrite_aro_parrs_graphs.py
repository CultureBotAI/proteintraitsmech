#!/usr/bin/env python3
"""Rewrite ParRS two-component regulatory ARO graphs.

ParRS is not an RND pump.  It is a two-component regulatory system that drives
several downstream resistance branches in Pseudomonas aeruginosa: MexXY/OprM
efflux, arn/PmrAB-mediated lipid-A modification, and reduced OprD-mediated
permeability.  This updater rewrites the parRS parent and the ParS/ParR
component records with that regulatory model.

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
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed ParRS two-component regulatory causal graphs",
    "llm_assisted": True,
}

PARRS_PRIMARY_EVIDENCE = {
    "reference": "PMID:21149619",
    "snippet": (
        "Muller et al. show that ParRS activation promotes pmrAB, "
        "arnBCDTEF-ugd, and mexXY expression while downregulating oprD, "
        "connecting lipid-A modification, efflux, and porin loss to "
        "multidrug resistance."
    ),
    "notes": "Primary evidence for the three ParRS-regulated resistance branches.",
}

TWO_COMPONENT_EVIDENCE = {
    "reference": "ARO:3000750",
    "snippet": (
        "A protein, either a histidine kinase or a response regulator, that "
        "is part of a two-component regulatory system that directly or "
        "indirectly change rates of antibiotic efflux."
    ),
    "notes": "CARD definition for two-component regulators that modulate antibiotic efflux.",
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

MEXXY_OPRM_EVIDENCE = {
    "reference": "ARO:3003032",
    "snippet": (
        "CARD defines MexXY-OprM as a Pseudomonas aeruginosa multidrug "
        "efflux protein and annotates MexX, MexY, and OprM as the pump's "
        "RND, membrane-fusion, and outer-membrane components."
    ),
    "notes": "CARD definition for the MexXY-OprM efflux pump regulated by ParRS.",
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "Reduced net negative charge in the Gram-negative cell wall confers "
        "resistance to cationic antimicrobials that require that charge for "
        "surface binding."
    ),
    "notes": "CARD mechanism definition for resistance by charge alteration.",
}

ARAFN_LIPID_A_EVIDENCE = {
    "reference": "ARO:3003578",
    "snippet": (
        "PmrF is required for synthesis and transfer of Ara4N to lipid A, "
        "which lets Gram-negative bacteria resist cationic antimicrobial "
        "peptides and polymyxin."
    ),
    "notes": "CARD definition connecting the arn/PmrF branch to lipid-A modification.",
}

REDUCED_PERMEABILITY_EVIDENCE = {
    "reference": "ARO:3000244",
    "snippet": (
        "Reduction in permeability to antibiotic, generally through reduced "
        "production of porins, can provide resistance."
    ),
    "notes": "CARD definition for the reduced-permeability resistance mechanism.",
}

OPRD_EVIDENCE = {
    "reference": "ARO:3003686",
    "snippet": (
        "oprD is an outer membrane porin that facilitates uptake of basic "
        "amino acids and imipenem in Pseudomonas aeruginosa."
    ),
    "notes": "CARD definition for the Pseudomonas OprD porin branch downregulated by ParRS.",
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

SIGNALLING_NODE = {
    "node_id": "signalling",
    "label": "two-component signal transduction",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0000160",
}

MEXXY_NODE = {
    "node_id": "mexxy_efflux",
    "label": "ParRS-induced MexXY-OprM efflux",
    "node_type": "STATE",
    "description": (
        "Local state for ParRS-driven mexXY expression and increased "
        "MexXY/OprM efflux-pump activity."
    ),
}

LIPID_A_NODE = {
    "node_id": "lipid_a_modification",
    "label": "beta-L-Ara4N-lipid A biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1901760",
    "description": (
        "GO biological-process term for lipid-A modification by addition of "
        "4-amino-4-deoxy-L-arabinose."
    ),
}

OPRD_REPRESSION_NODE = {
    "node_id": "oprd_repression",
    "label": "ParRS-repressed OprD porin pathway",
    "node_type": "STATE",
    "description": (
        "Local state for ParRS-mediated oprD downregulation and reduced "
        "OprD-dependent antibiotic influx."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3005066", "parrs-aro3005066.yaml"),
    Target("ARO:3005067", "pars-aro3005067.yaml"),
    Target("ARO:3005068", "parr-aro3005068.yaml"),
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (record_evidence, TWO_COMPONENT_EVIDENCE, PARRS_PRIMARY_EVIDENCE)

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → ParRS regulatory branches → resistance",
        "description": (
            "Curated resistance-causation graph for ParRS two-component "
            "regulation. ParRS is modeled as a regulator of MexXY/OprM efflux, "
            "arn/PmrAB-dependent lipid-A modification, and OprD downregulation "
            "rather than as the RND pump or porin itself."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
            },
            copy.deepcopy(SIGNALLING_NODE),
            copy.deepcopy(MEXXY_NODE),
            copy.deepcopy(LIPID_A_NODE),
            copy.deepcopy(OPRD_REPRESSION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies ParRS-family regulators under antibiotic "
                "efflux because they change efflux rates.",
                record_evidence,
                TWO_COMPONENT_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                PARRS_PRIMARY_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in",
                "RO:0000056",
                "signalling",
                "The determinant is the ParRS two-component signaling system "
                "or one of its ParS/ParR components.",
                *common_evidence,
            ),
            _edge(
                "signalling",
                "positively regulates",
                "RO:0002213",
                "mexxy_efflux",
                "ParRS signaling promotes mexXY expression and thereby "
                "increases MexXY/OprM efflux.",
                *common_evidence,
                MEXXY_OPRM_EVIDENCE,
            ),
            _edge(
                "mexxy_efflux",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Increased MexXY/OprM efflux exports antibiotics and contributes "
                "to multidrug resistance.",
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                MEXXY_OPRM_EVIDENCE,
                PARRS_PRIMARY_EVIDENCE,
            ),
            _edge(
                "signalling",
                "positively regulates",
                "RO:0002213",
                "lipid_a_modification",
                "ParRS signaling promotes the pmrAB and arnBCDTEF-ugd "
                "transcriptional response that modifies lipid A.",
                record_evidence,
                PARRS_PRIMARY_EVIDENCE,
                ARAFN_LIPID_A_EVIDENCE,
            ),
            _edge(
                "lipid_a_modification",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Ara4N lipid-A modification reduces the net negative surface "
                "charge needed for cationic-antibiotic binding.",
                ARAFN_LIPID_A_EVIDENCE,
                CHARGE_ALTERATION_EVIDENCE,
                PARRS_PRIMARY_EVIDENCE,
            ),
            _edge(
                "signalling",
                "causally upstream of",
                "RO:0002411",
                "oprd_repression",
                "ParRS signaling downregulates oprD and reduces the porin route "
                "used for antibiotic influx.",
                record_evidence,
                PARRS_PRIMARY_EVIDENCE,
                OPRD_EVIDENCE,
            ),
            _edge(
                "oprd_repression",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "OprD downregulation reduces antibiotic entry through the outer "
                "membrane permeability pathway.",
                REDUCED_PERMEABILITY_EVIDENCE,
                OPRD_EVIDENCE,
                PARRS_PRIMARY_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ParRS signaling coordinates efflux, lipid-A modification, and "
                "OprD repression branches that confer multidrug resistance.",
                *common_evidence,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                ARAFN_LIPID_A_EVIDENCE,
                OPRD_EVIDENCE,
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

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a ParRS target: {identifier}")
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
        help="ARO directory or one ParRS YAML file",
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
