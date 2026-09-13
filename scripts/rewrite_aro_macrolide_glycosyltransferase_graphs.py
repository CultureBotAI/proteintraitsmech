#!/usr/bin/env python3
"""Curate grounded macrolide glycosyltransferase ARO causal graphs.

The eight macrolide glycosyltransferase records share the same resistance
chemistry: a glycosyltransferase glycosylates a macrolide and thereby
inactivates it. Earlier graphs modeled a variable glycosylated product and a
23S rRNA binding site as label-only nodes. This updater rewrites each graph to
the grounded shared mechanism instead.

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

HISTORY_ACTION = "Rewrote macrolide glycosyltransferase graphs to grounded shared chemistry"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

FAMILY_PMID_EVIDENCE = {
    "reference": "PMID:17376874",
    "snippet": (
        "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, "
        "glycosylate and inactivate oleandomycin and diverse macrolides "
        "including erythromycin, respectively."
    ),
    "notes": "OleI and OleD glycosylate and inactivate macrolides.",
}

MACROLIDE_FAMILY_EVIDENCE = {
    "reference": "ARO:3000458",
    "snippet": (
        "Macrolide glycosyltransferases are enzymes encoded by macrolide "
        "glycosyltransferase genes and inactivate macrolides by glycosylating "
        "them at 2'-OH of desosamine sugar moiety."
    ),
    "notes": "CARD definition for the macrolide glycosyltransferase family.",
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

GLYCOSYLATION_EVIDENCE = {
    "reference": "ARO:3000208",
    "snippet": "Addition of glycosyl moiety to antibiotics thereby inactivating them.",
    "notes": "CARD definition for glycosylation of antibiotic conferring resistance.",
}

GO_GLYCOSYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016757",
    "snippet": (
        "Catalysis of the transfer of a glycosyl group from one compound "
        "(donor) to another (acceptor)."
    ),
    "notes": "GO definition for the broad glycosyltransferase activity superclass.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Macrolide resistance phenotype conferred by enzymatic glycosylation "
        "and inactivation of the drug."
    ),
}

MACROLIDE_NODE = {
    "node_id": "drug0",
    "label": "macrolide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000000",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    has_drug_edge: bool


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000458", "macrolide-glycosyltransferase-aro3000458.yaml", False),
    Target("ARO:3000463", "gima-aro3000463.yaml", True),
    Target("ARO:3004236", "gima-family-macrolide-glycosyltransferase-aro3004236.yaml", True),
    Target("ARO:3000462", "mgta-aro3000462.yaml", True),
    Target("ARO:3004237", "mgt-macrolide-glycotransferase-aro3004237.yaml", True),
    Target("ARO:3000465", "ole-glycosyltransferase-aro3000465.yaml", True),
    Target("ARO:3000865", "oled-aro3000865.yaml", True),
    Target("ARO:3000866", "olei-aro3000866.yaml", True),
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


def _old_drug_evidence(record: dict[str, Any]) -> list[dict[str, str]]:
    for graph in _dicts(record.get("causal_graphs")):
        for edge in _dicts(graph.get("edges")):
            if edge.get("subject") == "determinant" and edge.get("object") == "drug0":
                evidence = _dicts(edge.get("evidence"))
                if evidence:
                    return copy.deepcopy(evidence)

    relation = next(
        (
            item
            for item in _dicts(record.get("trait_relations"))
            if item.get("predicate") == "biolink:related_to"
            and item.get("object") == "ARO:0000000"
        ),
        None,
    )
    if relation is None:
        raise ValueError(f"{record['identifier']}: missing macrolide drug-class relation")

    return [
        {
            "reference": str(record["identifier"]),
            "snippet": "relationship: confers_resistance_to_drug_class ARO:0000000 ! macrolide antibiotic",
            "notes": str(relation.get("relation_source", "CARD macrolide drug-class relation.")),
        }
    ]


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = _unique_evidence(
        record_evidence,
        MACROLIDE_FAMILY_EVIDENCE,
        FAMILY_PMID_EVIDENCE,
        GLYCOSYLATION_EVIDENCE,
        INACTIVATION_EVIDENCE,
    )
    glycosyltransferase_evidence = _unique_evidence(
        record_evidence,
        MACROLIDE_FAMILY_EVIDENCE,
        FAMILY_PMID_EVIDENCE,
        GO_GLYCOSYLTRANSFERASE_EVIDENCE,
    )

    nodes = [
        _determinant_node(record),
        {
            "node_id": "mech0",
            "label": "antibiotic inactivation",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001004",
        },
        {
            "node_id": "mech1",
            "label": "glycosylation of antibiotic conferring resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000208",
        },
        {
            "node_id": "glycosyl",
            "label": "macrolide glycosyltransferase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0016757",
            "description": (
                "Grounded to the broad GO glycosyltransferase activity "
                "superclass because no macrolide-specific glycosyltransferase "
                "class is available locally."
            ),
        },
        copy.deepcopy(RESISTANCE_NODE),
    ]
    if target.has_drug_edge:
        nodes.append(copy.deepcopy(MACROLIDE_NODE))

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies this determinant under antibiotic inactivation "
            "because macrolide glycosyltransferases chemically modify and "
            "inactivate macrolides.",
            *common_evidence,
        ),
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech1",
            "CARD also classifies this determinant under glycosylation of "
            "antibiotic conferring resistance, the specific inactivation "
            "chemistry.",
            *common_evidence,
        ),
        _edge(
            "determinant",
            "enables (macrolide glycosylation)",
            "RO:0002327",
            "glycosyl",
            "The determinant enables a macrolide glycosyltransferase activity "
            "that chemically modifies the drug substrate.",
            *glycosyltransferase_evidence,
        ),
        _edge(
            "glycosyl",
            "causally upstream of",
            "RO:0002411",
            "mech1",
            "The enabled glycosyltransferase activity is the enzymatic "
            "activity that realizes the glycosylation resistance mechanism.",
            *glycosyltransferase_evidence,
            GLYCOSYLATION_EVIDENCE,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "mech0",
            "Glycosylation of the macrolide is the specific chemical "
            "modification that enzymatically inactivates the antibiotic.",
            *common_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Antibiotic inactivation prevents the macrolide from acting on "
            "its target and supports the resistance phenotype.",
            *common_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The determinant confers macrolide resistance through "
            "glycosyltransferase-mediated inactivation of the drug.",
            *common_evidence,
            GO_GLYCOSYLTRANSFERASE_EVIDENCE,
        ),
    ]
    if target.has_drug_edge:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts macrolide-antibiotic resistance for this "
                "glycosyltransferase family or an ancestor of the determinant.",
                record_evidence,
                FAMILY_PMID_EVIDENCE,
                *_old_drug_evidence(record),
            )
        )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → macrolide glycosylation → resistance",
        "description": (
            "Curated resistance-causation graph for macrolide "
            "glycosyltransferases that glycosylate and inactivate macrolide "
            "antibiotics."
        ),
        "nodes": nodes,
        "edges": edges,
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
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["causal_graphs"] = [_graph(out, target)]
    return out, out["causal_graphs"] != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a macrolide glycosyltransferase target: {identifier}")
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
        help="ARO directory or one of the eight target YAML files",
    )
    args = parser.parse_args(argv)

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
