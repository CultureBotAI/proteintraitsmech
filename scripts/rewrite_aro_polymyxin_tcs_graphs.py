#!/usr/bin/env python3
"""Enrich polymyxin two-component-system ARO causal graphs.

The six records handled here were promoted from the same Lipid A modification
config. They have predicate/evidence skeletons, but every edge is undescribed
and singly cited. This updater makes the claims explicit and adds primary
PubMed support while preserving the ARO snippet as the first evidence item.

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
    "timestamp": "2026-09-05T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Added PubMed evidence, edge descriptions, and the surface-charge-to-resistance "
        "edge to the polymyxin two-component-system causal graph"
    ),
    "llm_assisted": True,
}

CHARGE_ARO_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall of gram "
        "negative bacteria is a mechanism of resistance for cationic antimicrobials "
        "that depend on the negative charge for binding to the surface."
    ),
    "notes": (
        "CARD's charge-alteration mechanism term; aminoarabinose-modified Lipid A lowers "
        "the negative envelope charge available for polymyxin binding."
    ),
}

CHARGE_LITERATURE_EVIDENCE = {
    "reference": "PMID:9570402",
    "snippet": (
        "lipid A aminoarabinose modification promotes resistance to cationic antimicrobial "
        "peptides"
    ),
    "notes": (
        "Gunn et al. connect PmrAB-regulated aminoarabinose Lipid A modification to "
        "polymyxin resistance."
    ),
}

LIPID_A_MOD_NODE = {
    "node_id": "lipid_a_mod",
    "label": "beta-L-Ara4N-lipid A biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1901760",
    "description": (
        "GO term for the aminoarabinose Lipid A modification branch controlled by "
        "pmrHFIJKLM/arn genes."
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this determinant under the broad ARO:0010000 resistance "
        "mechanism; the record-specific causal path is Lipid A remodeling rather than "
        "direct drug efflux."
    ),
    ("mech0", "resistance"): (
        "The broad inherited CARD mechanism category is associated with resistance, while "
        "the concrete route is captured by the Lipid A-modification branch below."
    ),
    ("determinant", "mech1"): (
        "CARD classifies the exact PhoP allele as a resistance-conferring mutation."
    ),
    ("mech1", "resistance"): (
        "The PhoP mutation is the determinant-level event that increases colistin "
        "resistance."
    ),
    ("determinant", "mech2"): (
        "CARD classifies the exact PhoP allele under charge alteration because it "
        "activates pmrHFIJKLM-dependent aminoarabinose synthesis."
    ),
    ("mech2", "resistance"): (
        "Charge alteration is the modeled resistance route: aminoarabinose-modified "
        "Lipid A reduces the negative envelope charge required for polymyxin binding."
    ),
    ("determinant", "resistance"): (
        "The mutant two-component-system member is the determinant associated with the "
        "polymyxin or colistin resistance phenotype."
    ),
    ("determinant", "lipid_a_mod"): (
        "The altered two-component-system member induces the Ara4N Lipid A modification "
        "pathway."
    ),
    ("lipid_a_mod", "surface_charge"): (
        "The induced Lipid A-modification enzymes add aminoarabinose to Lipid A, lowering "
        "the net negative cell-envelope charge."
    ),
    ("surface_charge", "resistance"): (
        "The lower negative charge reduces binding by cationic polymyxins, yielding the "
        "resistance phenotype."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    literature: dict[str, str]


TARGETS = {
    "ARO:3003582": Target(
        identifier="ARO:3003582",
        filename="basr-aro3003582.yaml",
        literature={
            "reference": "PMID:24412662",
            "snippet": (
                "Activated expression of pmrA and/or phoP was identified in 13 isolates "
                "of CNPA isolates"
            ),
            "notes": (
                "Lee and Ko link PmrAB/PhoPQ activation in Pseudomonas isolates to "
                "colistin nonsusceptibility."
            ),
        },
    ),
    "ARO:3003583": Target(
        identifier="ARO:3003583",
        filename="bass-aro3003583.yaml",
        literature={
            "reference": "PMID:14507375",
            "snippet": (
                "Interposon mutants in pmrB, pmrA, or in an intergenic region upstream of "
                "pmrA-pmrB exhibited two to 16-fold increased susceptibility to "
                "polymyxin B"
            ),
            "notes": (
                "McPhee et al. link the PmrA-PmrB two-component system to polymyxin B "
                "resistance."
            ),
        },
    ),
    "ARO:3003585": Target(
        identifier="ARO:3003585",
        filename="klebsiella-mutant-phop-conferring-antibiotic-resistance-to-colistin-"
        "aro3003585.yaml",
        literature={
            "reference": "PMID:25733503",
            "snippet": (
                "Complementation assays with a wild-type phoP gene restored full "
                "susceptibility to colistin"
            ),
            "notes": (
                "Jayol et al. validate the Klebsiella PhoP Asp191Tyr substitution as the "
                "cause of colistin resistance."
            ),
        },
    ),
    "ARO:3003895": Target(
        identifier="ARO:3003895",
        filename="pseudomonas-mutant-phop-conferring-resistance-to-colistin-aro3003895.yaml",
        literature={
            "reference": "PMID:24412662",
            "snippet": (
                "Activated expression of pmrA and/or phoP was identified in 13 isolates "
                "of CNPA isolates"
            ),
            "notes": (
                "Lee and Ko connect activated phoP/PmrAB expression with colistin "
                "nonsusceptibility in Pseudomonas aeruginosa."
            ),
        },
    ),
    "ARO:3003896": Target(
        identifier="ARO:3003896",
        filename="pseudomonas-mutant-phoq-conferring-resistance-to-colistin-aro3003896.yaml",
        literature={
            "reference": "PMID:21968359",
            "snippet": (
                "Probable loss-of-function phoQ alleles found in these cystic fibrosis "
                "strains conferred resistance to polymyxin"
            ),
            "notes": (
                "Miller et al. show that Pseudomonas phoQ loss-of-function alleles "
                "promote Lipid A modification and polymyxin resistance."
            ),
        },
    ),
    "ARO:3007203": Target(
        identifier="ARO:3007203",
        filename="klebsiella-pneumoniae-mutant-phoq-conferring-resistance-to-colistin-"
        "aro3007203.yaml",
        literature={
            "reference": "PMID:35920875",
            "snippet": (
                "the mutation V24G on phoQ was identified. Complementation assay with "
                "proper wild type genes restored colistin susceptibility"
            ),
            "notes": (
                "Sisti et al. validate Klebsiella pneumoniae PhoQ V24G as a colistin "
                "resistance mutation."
            ),
        },
    ),
}

SURFACE_CHARGE_EDGE = {
    "subject": "surface_charge",
    "predicate": "causally upstream of (reduces polymyxin binding)",
    "predicate_id": "RO:0002411",
    "object": "resistance",
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _definition_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    return {
        "reference": target.identifier,
        "snippet": record["definition"],
        "notes": "Exact ARO definition of this determinant.",
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


def _evidence_for_edge(
    edge: dict[str, Any],
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, str]]:
    if _edge_key(edge) in {
        ("lipid_a_mod", "surface_charge"),
        ("surface_charge", "resistance"),
    }:
        return [
            copy.deepcopy(CHARGE_ARO_EVIDENCE),
            copy.deepcopy(CHARGE_LITERATURE_EVIDENCE),
        ]
    return [
        _definition_evidence(record, target),
        copy.deepcopy(target.literature),
    ]


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    for index, node in enumerate(nodes):
        if node.get("node_id") != "lipid_a_mod":
            continue
        nodes[index] = copy.deepcopy(LIPID_A_MOD_NODE)
        return
    msg = f"{target.identifier}: missing lipid_a_mod node"
    raise ValueError(msg)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{target.identifier}: missing resistance causal graph"
        raise ValueError(msg)

    _enrich_nodes(graph, target)

    edges = graph.setdefault("edges", [])
    if not any(_edge_key(edge) == ("surface_charge", "resistance") for edge in edges):
        edges.append(copy.deepcopy(SURFACE_CHARGE_EDGE))

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EDGE_DESCRIPTIONS:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(edge, out, target)
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    graph["edges"] = enriched_edges
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a polymyxin two-component-system target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
    return out, True


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the six target YAML files",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            out, did_change = enrich_text(text, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
