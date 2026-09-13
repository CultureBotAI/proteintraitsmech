#!/usr/bin/env python3
"""Rewrite Cya/cyaA fosfomycin reduced-import ARO graphs.

Cya adenylate-cyclase mutations affect fosfomycin susceptibility through cAMP
control of GlpT-dependent uptake.  The existing graphs leave cAMP and glpT
ungrounded and stop at regulation.  This updater grounds cAMP and terminates
the pathway at reduced GlpT-mediated fosfomycin uptake.

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
    "action": "Completed Cya/cyaA reduced fosfomycin uptake causal graphs",
    "llm_assisted": True,
}

MUTATION_MECHANISM_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

CYA_PARENT_EVIDENCE = {
    "reference": "ARO:3004251",
    "snippet": (
        "Adenylate cyclases encoded by cya genes synthesize cyclic AMP, which "
        "regulates the fosfomycin transporter glpT; cya mutations can confer "
        "resistance to fosfomycin."
    ),
    "notes": "CARD definition for antibiotic-resistant cya adenylate cyclase.",
}

CYAA_CLINICAL_EVIDENCE = {
    "reference": "PMID:20071153",
    "snippet": (
        "Takahata et al. examined E. coli fosfomycin-resistant clinical "
        "isolates for mutations in murA, glpT, uhpT, uhpA, ptsI, and cyaA."
    ),
    "notes": "CARD-cited clinical evidence for the E. coli cyaA fosfomycin-resistance term.",
}

CRP_CAMP_EVIDENCE = {
    "reference": "PMID:28360903",
    "snippet": (
        "Kurabayashi et al. showed that the CRP-cAMP regulator complex "
        "induces glpT and uhpT expression and that cyaA deletion decreases "
        "fosfomycin susceptibility."
    ),
    "notes": "Experimental support for cAMP-dependent GlpT/UhpT fosfomycin uptake.",
}

GLPT_EVIDENCE = {
    "reference": "ARO:3004247",
    "snippet": (
        "GlpT encodes a glycerol-3-phosphate transporter that imports "
        "fosfomycin; mutations in GlpT can confer fosfomycin resistance."
    ),
    "notes": "CARD definition for antibiotic-resistant GlpT.",
}

CAMP_EVIDENCE = {
    "reference": "CHEBI:17489",
    "snippet": "3',5'-cyclic AMP is a 3',5'-cyclic purine nucleotide.",
    "notes": "ChEBI grounding for cyclic AMP.",
}

PHOSPHONIC_RELATION_EVIDENCE = {
    "reference": "ARO:3004251",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007149 ! phosphonic acid antibiotic",
    "notes": "Phosphonic-acid drug-class relation asserted on the cya adenylate-cyclase parent.",
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

PHOSPHONIC_NODE = {
    "node_id": "drug0",
    "label": "phosphonic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007149",
}

CAMP_NODE = {
    "node_id": "camp",
    "label": "3',5'-cyclic AMP",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:17489",
    "description": "The Cya adenylate-cyclase product that regulates glpT expression.",
}

REDUCED_IMPORT_NODE = {
    "node_id": "reduced_import",
    "label": "reduced GlpT-mediated fosfomycin uptake",
    "node_type": "STATE",
    "description": (
        "Local state for reduced fosfomycin uptake after impaired "
        "cAMP-dependent regulation of the GlpT importer."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3004251", "antibiotic-resistant-cya-adenylate-cyclase-aro3004251.yaml"),
    Target(
        "ARO:3003900",
        "escherichia-coli-cyaa-with-mutation-conferring-resistance-to-fosfomycin-aro3003900.yaml",
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        CYA_PARENT_EVIDENCE,
        MUTATION_MECHANISM_EVIDENCE,
        CRP_CAMP_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced GlpT-mediated fosfomycin uptake",
        "description": (
            "Curated resistance-causation graph for cya adenylate-cyclase "
            "mutations that alter cyclic-AMP control of GlpT-dependent "
            "fosfomycin uptake."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            copy.deepcopy(PHOSPHONIC_NODE),
            copy.deepcopy(CAMP_NODE),
            copy.deepcopy(REDUCED_IMPORT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies Cya/cyaA fosfomycin resistance under mutation "
                "conferring antibiotic resistance.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The Cya/cyaA mutation mechanism confers resistance by "
                "reducing fosfomycin uptake.",
                *common_evidence,
                GLPT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "camp",
                "Cya adenylate cyclase mutations alter cyclic AMP synthesis.",
                *common_evidence,
                CAMP_EVIDENCE,
            ),
            _edge(
                "camp",
                "causally upstream of",
                "RO:0002411",
                "reduced_import",
                "Altered cAMP-dependent regulation reduces GlpT-mediated "
                "fosfomycin uptake.",
                record_evidence,
                CYA_PARENT_EVIDENCE,
                CAMP_EVIDENCE,
                GLPT_EVIDENCE,
                CRP_CAMP_EVIDENCE,
            ),
            _edge(
                "reduced_import",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Reduced import lowers intracellular fosfomycin exposure and "
                "causes the modeled resistance phenotype.",
                record_evidence,
                CYA_PARENT_EVIDENCE,
                GLPT_EVIDENCE,
                CRP_CAMP_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Resistance-conferring Cya/cyaA mutations act through "
                "cyclic-AMP regulation of fosfomycin import.",
                *common_evidence,
                GLPT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a phosphonic-acid antibiotic drug-class relation "
                "for the cya adenylate-cyclase lineage.",
                record_evidence,
                PHOSPHONIC_RELATION_EVIDENCE,
                CRP_CAMP_EVIDENCE,
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
    missing = {"determinant", "mech0", "drug0", "camp", "resistance"} - node_ids
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
        raise ValueError(f"{path}: not a Cya/cyaA fosfomycin target: {identifier}")
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
        help="ARO directory or one Cya/cyaA fosfomycin YAML file",
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
