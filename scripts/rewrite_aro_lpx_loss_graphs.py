#!/usr/bin/env python3
"""Rewrite Acinetobacter Lpx lipid-A-loss ARO graphs.

Mutant Acinetobacter lpxA/lpxC/lpxD records are mutation-driven, lipid-A-loss
determinants.  Their existing graphs have the right broad mechanism terms, but
leave lipid-A biosynthesis ungrounded and stop at a vague membrane state
instead of the loss of the polymyxin lipid-A target.

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
    "action": "Completed Acinetobacter Lpx lipid-A-loss causal graphs",
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

MOLECULAR_BYPASS_EVIDENCE = {
    "reference": "ARO:3000012",
    "snippet": "Proteins involved in restructuring of the cell wall, causing antibiotic resistance.",
    "notes": "CARD parent term for molecular bypass through cell-wall restructuring.",
}

LIPID_A_PARENT_EVIDENCE = {
    "reference": "ARO:3003581",
    "snippet": (
        "Acinetobacter mutant Lpx genes are involved in lipid-A biosynthesis, "
        "and absence or ISAba11 insertion can cause resistance in "
        "Acinetobacter baumannii."
    ),
    "notes": "CARD definition for the Acinetobacter mutant Lpx parent term.",
}

MOFFATT_EVIDENCE = {
    "reference": "PMID:21402838",
    "snippet": (
        "Moffatt et al. found that colistin-resistant Acinetobacter baumannii "
        "derivatives carried mutations in lpxA, lpxC, or lpxD and lost "
        "lipopolysaccharide production."
    ),
    "notes": "Primary evidence that disrupting one of the first three lipid-A genes eliminates LPS.",
}

BECEIRO_EVIDENCE = {
    "reference": "PMID:24189257",
    "snippet": (
        "Beceiro et al. describe Acinetobacter baumannii colistin resistance "
        "from lpxA, lpxC, and lpxD inactivation, including ISAba11 disruption "
        "and the resulting loss of lipopolysaccharide."
    ),
    "notes": "Evidence for clinical and insertional Lpx loss-of-function routes.",
}

LIPID_A_PROCESS_EVIDENCE = {
    "reference": "GO:0009245",
    "snippet": "The chemical reactions and pathways resulting in the formation of lipid A.",
    "notes": "GO definition for lipid-A biosynthetic process.",
}

PEPTIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3003581",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": "Peptide-antibiotic drug-class relation asserted on the Acinetobacter mutant Lpx parent.",
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

PEPTIDE_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

LIPID_A_SYNTHESIS_NODE = {
    "node_id": "lipid_a_synthesis",
    "label": "lipid A biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009245",
}

LIPID_A_LOSS_NODE = {
    "node_id": "lipid_a_loss",
    "label": "loss of lipid A-containing lipopolysaccharide",
    "node_type": "STATE",
    "description": (
        "Local state for disrupted lipid-A biosynthesis causing loss of the "
        "lipopolysaccharide target used by colistin and related polymyxins."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3003581",
        "acinetobacter-mutant-lpx-gene-conferring-resistance-to-colistin-aro3003581.yaml",
    ),
    Target("ARO:3003573", "lpxa-aro3003573.yaml"),
    Target("ARO:3003574", "lpxc-aro3003574.yaml"),
    Target("ARO:3003575", "lpxd-aro3003575.yaml"),
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
        LIPID_A_PARENT_EVIDENCE,
        MOFFATT_EVIDENCE,
        BECEIRO_EVIDENCE,
    )
    pathway_evidence = (
        record_evidence,
        LIPID_A_PARENT_EVIDENCE,
        LIPID_A_PROCESS_EVIDENCE,
        MOFFATT_EVIDENCE,
        BECEIRO_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → loss of lipid A → colistin resistance",
        "description": (
            "Curated resistance-causation graph for Acinetobacter Lpx "
            "loss-of-function determinants. Mutations or insertional "
            "inactivation disrupt lipid-A biosynthesis and can eliminate the "
            "lipopolysaccharide lipid-A target of peptide antibiotics."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            {
                "node_id": "mech1",
                "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000213",
            },
            copy.deepcopy(PEPTIDE_NODE),
            copy.deepcopy(LIPID_A_SYNTHESIS_NODE),
            copy.deepcopy(LIPID_A_LOSS_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies Acinetobacter mutant Lpx determinants under "
                "mutation conferring antibiotic resistance.",
                *common_evidence,
                MUTATION_MECHANISM_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Lpx loss-of-function mutations cause peptide-antibiotic "
                "resistance through lipid-A loss.",
                *common_evidence,
                MUTATION_MECHANISM_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD also classifies the Lpx lipid-A-loss route under "
                "cell-wall restructuring.",
                *common_evidence,
                MOLECULAR_BYPASS_EVIDENCE,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Disrupted lipid-A biosynthesis restructures the outer "
                "membrane by eliminating LPS and causing peptide-antibiotic "
                "resistance.",
                *common_evidence,
                MOLECULAR_BYPASS_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "lipid_a_loss",
                "Mutation or insertional inactivation of lpxA, lpxC, or lpxD "
                "blocks lipid-A biosynthesis and causes LPS loss.",
                *common_evidence,
                LIPID_A_PROCESS_EVIDENCE,
            ),
            _edge(
                "lipid_a_loss",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Loss of lipid A-containing LPS removes the outer-membrane "
                "target of colistin and related peptide antibiotics.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The mutant Lpx determinant confers resistance by disrupting "
                "lipid-A biosynthesis and eliminating the peptide-antibiotic "
                "target.",
                *common_evidence,
                MOLECULAR_BYPASS_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a peptide-antibiotic drug-class relation for "
                "the Acinetobacter mutant Lpx lineage.",
                record_evidence,
                LIPID_A_PARENT_EVIDENCE,
                PEPTIDE_RELATION_EVIDENCE,
                MOFFATT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in",
                "RO:0000056",
                "lipid_a_synthesis",
                "Wild-type Lpx proteins act in lipid-A biosynthesis, the "
                "pathway disrupted by resistance-causing lpx mutations.",
                *pathway_evidence,
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
    missing = {
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "lipid_a_synthesis",
        "resistance",
    } - node_ids
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
        raise ValueError(f"{path}: not an Acinetobacter Lpx target: {identifier}")
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
        help="ARO directory or one Acinetobacter Lpx YAML file",
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
