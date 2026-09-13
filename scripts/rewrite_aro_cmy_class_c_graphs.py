#!/usr/bin/env python3
"""Enrich CMY/LAT/MOX class C beta-lactamase group graphs.

These class C beta-lactamase grouping records already have a grounded Ser64
active-site motif, DD-peptidase/beta-lactamase fold, and serine beta-lactamase
hydrolysis mechanism. This updater replaces their single-reference skeletons
with described, multi-evidence class C serine-hydrolysis graphs.

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

HISTORY_ACTION = "Completed CMY/LAT/MOX class C beta-lactamase causal graphs"
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

BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000001",
    "snippet": (
        "The lactamase enzyme breaks that ring open, deactivating the "
        "molecule's antibacterial properties."
    ),
    "notes": "CARD definition for beta-lactamases.",
}

CLASS_C_EVIDENCE = {
    "reference": "ARO:3000076",
    "snippet": (
        "AmpC beta-lactamases, in contrast to ESBLs, hydrolyse broad and "
        "extended-spectrum cephalosporins (cephamycins as well as to "
        "oxyimino-beta-lactams) but are not inhibited by beta-lactamase "
        "inhibitors such as clavulanic acid."
    ),
    "notes": "CARD definition for the class C beta-lactamase parent.",
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

AMPC_REACTION_EVIDENCE = {
    "reference": "PMID:19136439",
    "snippet": (
        "AmpC β-lactamases are clinically important cephalosporinases encoded "
        "on the chromosomes of many of the Enterobacteriaceae and a few other "
        "organisms."
    ),
    "notes": "Evidence for AmpC/class C beta-lactamases.",
}

PROSITE_CLASS_C_EVIDENCE = {
    "reference": "PROSITE:PRU10102",
    "snippet": "Beta-lactamase class-C active site",
    "notes": "PROSITE active-site signature for class C beta-lactamases.",
}

CATH_SERINE_BETA_LACTAMASE_EVIDENCE = {
    "reference": "CATH:3.40.710.10",
    "snippet": "DD-peptidase/beta-lactamase superfamily",
    "notes": "CATH fold for serine beta-lactamases.",
}

BROAD_INACTIVATION_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

SERINE_HYDROLYSIS_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000187",
}

CLASS_C_ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "class C beta-lactamase active-site signature (Ser64 S-x-x-K)",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PRU10102",
    "description": "Class C beta-lactamase catalytic serine active-site signature.",
}

SERINE_BETA_LACTAMASE_FOLD_NODE = {
    "node_id": "fold",
    "label": "DD-peptidase/beta-lactamase superfamily fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.710.10",
    "description": "DD-peptidase/beta-lactamase superfamily fold.",
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


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000085", "cmy-lat-mox-beta-lactamase-aro3000085.yaml"),
    Target("ARO:3000086", "cmy-lat-beta-lactamase-aro3000086.yaml"),
    Target("ARO:3000087", "cmy-mox-beta-lactamase-aro3000087.yaml"),
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
        "active_site",
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


def _canonical_graph(record: dict[str, Any]) -> dict[str, Any]:
    target_evidence = _record_evidence(record)
    broad_evidence = (
        target_evidence,
        CLASS_C_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        AMPC_REACTION_EVIDENCE,
    )
    serine_evidence = (
        target_evidence,
        CLASS_C_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        SERINE_BETA_LACTAMASE_EVIDENCE,
        AMPC_REACTION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → class C serine beta-lactam hydrolysis → resistance",
        "description": (
            "Curated class C beta-lactamase resistance graph. The determinant "
            "participates in broad antibiotic inactivation and the narrower "
            "class C serine beta-lactamase hydrolysis mechanism through the "
            "Ser64 active-site motif and DD-peptidase/beta-lactamase fold."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(BROAD_INACTIVATION_NODE),
            copy.deepcopy(SERINE_HYDROLYSIS_NODE),
            copy.deepcopy(CLASS_C_ACTIVE_SITE_NODE),
            copy.deepcopy(SERINE_BETA_LACTAMASE_FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies this class C beta-lactamase family under antibiotic inactivation.",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Class C beta-lactamases hydrolyze beta-lactams and thereby inactivate antibiotic.",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "ARO classifies this class C beta-lactamase family under serine beta-lactamase hydrolysis.",
                *serine_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Class C serine beta-lactam hydrolysis renders beta-lactam antibiotics inactive.",
                *serine_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The class C beta-lactamase family hydrolyzes beta-lactam antibiotics to confer resistance.",
                *broad_evidence,
            ),
            _edge(
                "active_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The grounded class C active-site signature is part of the beta-lactamase determinant.",
                target_evidence,
                CLASS_C_EVIDENCE,
                SERINE_BETA_LACTAMASE_EVIDENCE,
                PROSITE_CLASS_C_EVIDENCE,
                AMPC_REACTION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the grounded DD-peptidase/beta-lactamase fold.",
                target_evidence,
                CLASS_C_EVIDENCE,
                CATH_SERINE_BETA_LACTAMASE_EVIDENCE,
                AMPC_REACTION_EVIDENCE,
            ),
            _edge(
                "active_site",
                "enables (serine beta-lactam hydrolysis)",
                "RO:0002327",
                "mech1",
                "The class C active-site signature enables serine beta-lactam hydrolysis.",
                target_evidence,
                CLASS_C_EVIDENCE,
                SERINE_BETA_LACTAMASE_EVIDENCE,
                PROSITE_CLASS_C_EVIDENCE,
                AMPC_REACTION_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a CMY/LAT/MOX target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = _dicts(enriched.get("curation_history"))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
        help="ARO directory or one of the CMY/LAT/MOX YAML files",
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
