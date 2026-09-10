#!/usr/bin/env python3
"""Rewrite Qnr pentapeptide-repeat target-protection graphs.

These exact score-77 Qnr records have the right inherited target-protection
shape, but every edge is still single-evidenced and the mechanistic edges lack
descriptions. The rewrite keeps the inherited fluoroquinolone drug edge and
uses the shared Qnr parent plus pentapeptide-repeat domain/fold evidence.

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

HISTORY_ACTION = "Completed Qnr pentapeptide-repeat target-protection graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, which "
        "process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for the antibiotic target protection mechanism.",
}

TARGET_PROTECTION_PARENT_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection proteins.",
}

QNR_PARENT_EVIDENCE = {
    "reference": "ARO:3000419",
    "snippet": (
        "Qnr proteins are pentapeptide repeat proteins that mimic DNA and "
        "protect the cell from the activity of fluoroquinolone antibiotics."
    ),
    "notes": "CARD definition for quinolone resistance protein (qnr).",
}

QNR_MECHANISM_EVIDENCE = {
    "reference": "PMID:21227918",
    "snippet": (
        "Plasmid genes qnrA, qnrB, qnrC, qnrD, qnrS, and qnrVC code for "
        "proteins of the pentapeptide repeat family that protects DNA gyrase "
        "and topoisomerase IV from quinolone inhibition."
    ),
    "notes": "Evidence for Qnr pentapeptide-repeat fluoroquinolone target protection.",
}

PENTAPEPTIDE_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF00805",
    "snippet": "Pentapeptide repeats (8 copies)",
    "notes": "Pfam family for the Qnr pentapeptide-repeat domain.",
}

PENTAPEPTIDE_FOLD_EVIDENCE = {
    "reference": "ECOD:T.207.9.1",
    "snippet": "Pentapeptide repeats",
    "notes": "ECOD fold for Qnr/MfpA right-handed beta-helix pentapeptide repeats.",
}

FLUOROQUINOLONE_EVIDENCE = {
    "reference": "ARO:0000001",
    "snippet": "fluoroquinolone antibiotic",
    "notes": "ARO drug-class term inherited by Qnr records.",
}

QNR_FLUOROQUINOLONE_RELATION_EVIDENCE = {
    "reference": "ARO:3000419",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000001 ! fluoroquinolone antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the quinolone resistance "
        "protein (qnr) parent and inherited by Qnr variants."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target protection",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001003",
}

FLUOROQUINOLONE_NODE = {
    "node_id": "drug0",
    "label": "fluoroquinolone antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000001",
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "pentapeptide-repeat domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00805",
    "description": "Pentapeptide-repeat domain shared by Qnr target-protection proteins.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "pentapeptide-repeat right-handed beta-helix fold",
    "node_type": "DOMAIN",
    "grounding": "ECOD:T.207.9.1",
    "description": "Right-handed beta-helix fold formed by pentapeptide-repeat proteins.",
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

REQUIRED_NODES = {"determinant", "mech0", "drug0", "domain", "fold", "resistance"}
REQUIRED_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech0"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3002707 qnra1-aro3002707.yaml
ARO:3002708 qnra2-aro3002708.yaml
ARO:3002709 qnra3-aro3002709.yaml
ARO:3002710 qnra4-aro3002710.yaml
ARO:3002711 qnra5-aro3002711.yaml
ARO:3002712 qnra6-aro3002712.yaml
ARO:3002713 qnra7-aro3002713.yaml
ARO:3004668 qnras-aro3004668.yaml
ARO:3002714 qnrb1-aro3002714.yaml
ARO:3002724 qnrb10-aro3002724.yaml
ARO:3002725 qnrb11-aro3002725.yaml
ARO:3002726 qnrb12-aro3002726.yaml
ARO:3002727 qnrb13-aro3002727.yaml
ARO:3002728 qnrb14-aro3002728.yaml
ARO:3002730 qnrb15-aro3002730.yaml
ARO:3002731 qnrb16-aro3002731.yaml
ARO:3002732 qnrb17-aro3002732.yaml
ARO:3002733 qnrb18-aro3002733.yaml
ARO:3002734 qnrb19-aro3002734.yaml
ARO:3002715 qnrb2-aro3002715.yaml
ARO:3002735 qnrb20-aro3002735.yaml
ARO:3002736 qnrb21-aro3002736.yaml
ARO:3002737 qnrb22-aro3002737.yaml
ARO:3002738 qnrb23-aro3002738.yaml
ARO:3002739 qnrb24-aro3002739.yaml
ARO:3002740 qnrb25-aro3002740.yaml
ARO:3002741 qnrb26-aro3002741.yaml
ARO:3002742 qnrb27-aro3002742.yaml
ARO:3002743 qnrb28-aro3002743.yaml
ARO:3002744 qnrb29-aro3002744.yaml
ARO:3002716 qnrb3-aro3002716.yaml
ARO:3002745 qnrb30-aro3002745.yaml
ARO:3002746 qnrb31-aro3002746.yaml
ARO:3002747 qnrb32-aro3002747.yaml
ARO:3002748 qnrb33-aro3002748.yaml
ARO:3002749 qnrb34-aro3002749.yaml
ARO:3002750 qnrb35-aro3002750.yaml
ARO:3002751 qnrb36-aro3002751.yaml
ARO:3002752 qnrb37-aro3002752.yaml
ARO:3002753 qnrb38-aro3002753.yaml
ARO:3002754 qnrb39-aro3002754.yaml
ARO:3002718 qnrb4-aro3002718.yaml
ARO:3002755 qnrb40-aro3002755.yaml
ARO:3002756 qnrb41-aro3002756.yaml
ARO:3002757 qnrb42-aro3002757.yaml
ARO:3002758 qnrb43-aro3002758.yaml
ARO:3002759 qnrb44-aro3002759.yaml
ARO:3002760 qnrb45-aro3002760.yaml
ARO:3002761 qnrb46-aro3002761.yaml
ARO:3002762 qnrb47-aro3002762.yaml
ARO:3002763 qnrb48-aro3002763.yaml
ARO:3002764 qnrb49-aro3002764.yaml
ARO:3002719 qnrb5-aro3002719.yaml
ARO:3002765 qnrb50-aro3002765.yaml
ARO:3002767 qnrb54-aro3002767.yaml
ARO:3002768 qnrb55-aro3002768.yaml
ARO:3002769 qnrb56-aro3002769.yaml
ARO:3002770 qnrb57-aro3002770.yaml
ARO:3002771 qnrb58-aro3002771.yaml
ARO:3002772 qnrb59-aro3002772.yaml
ARO:3002720 qnrb6-aro3002720.yaml
ARO:3002773 qnrb60-aro3002773.yaml
ARO:3002774 qnrb61-aro3002774.yaml
ARO:3002775 qnrb62-aro3002775.yaml
ARO:3002776 qnrb64-aro3002776.yaml
ARO:3002777 qnrb65-aro3002777.yaml
ARO:3002778 qnrb66-aro3002778.yaml
ARO:3002779 qnrb67-aro3002779.yaml
ARO:3002780 qnrb68-aro3002780.yaml
ARO:3002781 qnrb69-aro3002781.yaml
ARO:3002721 qnrb7-aro3002721.yaml
ARO:3002782 qnrb70-aro3002782.yaml
ARO:3002783 qnrb71-aro3002783.yaml
ARO:3002784 qnrb72-aro3002784.yaml
ARO:3002785 qnrb73-aro3002785.yaml
ARO:3002786 qnrb74-aro3002786.yaml
ARO:3003187 qnrb75-aro3003187.yaml
ARO:3003188 qnrb76-aro3003188.yaml
ARO:3003189 qnrb77-aro3003189.yaml
ARO:3003190 qnrb78-aro3003190.yaml
ARO:3002722 qnrb8-aro3002722.yaml
ARO:3003192 qnrb80-aro3003192.yaml
ARO:3002723 qnrb9-aro3002723.yaml
ARO:3002787 qnrc-aro3002787.yaml
ARO:3002788 qnrd1-aro3002788.yaml
ARO:3002789 qnrd2-aro3002789.yaml
ARO:3004636 qnre1-aro3004636.yaml
ARO:3004637 qnre2-aro3004637.yaml
ARO:3002790 qnrs1-aro3002790.yaml
ARO:3004622 qnrs10-aro3004622.yaml
ARO:3004624 qnrs11-aro3004624.yaml
ARO:3004625 qnrs12-aro3004625.yaml
ARO:3004627 qnrs15-aro3004627.yaml
ARO:3002791 qnrs2-aro3002791.yaml
ARO:3002792 qnrs3-aro3002792.yaml
ARO:3002793 qnrs4-aro3002793.yaml
ARO:3002794 qnrs5-aro3002794.yaml
ARO:3002795 qnrs6-aro3002795.yaml
ARO:3002796 qnrs7-aro3002796.yaml
ARO:3002797 qnrs8-aro3002797.yaml
ARO:3002798 qnrs9-aro3002798.yaml
ARO:3002799 qnrvc1-aro3002799.yaml
ARO:3005007 qnrvc2-aro3005007.yaml
ARO:3002800 qnrvc3-aro3002800.yaml
ARO:3002801 qnrvc4-aro3002801.yaml
ARO:3002802 qnrvc5-aro3002802.yaml
ARO:3002803 qnrvc6-aro3002803.yaml
ARO:3003193 qnrvc7-aro3003193.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item["reference"], item.get("snippet", ""))
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


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


def _validate_graph(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    nodes = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = sorted(REQUIRED_NODES - nodes)
    if missing_nodes:
        raise ValueError(f"{target.identifier}: missing node(s): {', '.join(missing_nodes)}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graphs[0].get("edges")):
        key = _edge_key(edge)
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(REQUIRED_EDGES - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _qnr_graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    protection_evidence = (
        record_evidence,
        QNR_PARENT_EVIDENCE,
        TARGET_PROTECTION_PARENT_EVIDENCE,
        TARGET_PROTECTION_EVIDENCE,
        QNR_MECHANISM_EVIDENCE,
    )
    pentapeptide_evidence = (
        record_evidence,
        QNR_PARENT_EVIDENCE,
        PENTAPEPTIDE_DOMAIN_EVIDENCE,
        PENTAPEPTIDE_FOLD_EVIDENCE,
        QNR_MECHANISM_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → Qnr target protection → fluoroquinolone resistance",
        "description": (
            "Curated resistance-causation graph for a Qnr pentapeptide-repeat "
            "protein. Qnr determinants protect DNA gyrase and topoisomerase IV "
            "from fluoroquinolone inhibition through the shared "
            "pentapeptide-repeat fold."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(FLUOROQUINOLONE_NODE),
            copy.deepcopy(DOMAIN_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (Qnr target-protection mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies Qnr proteins under antibiotic target protection.",
                *protection_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Qnr-mediated target protection prevents fluoroquinolones from "
                "inhibiting DNA gyrase and topoisomerase IV.",
                *protection_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Qnr proteins confer fluoroquinolone resistance through "
                "pentapeptide-repeat target protection.",
                *protection_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                "Qnr variants inherit the Qnr parent confers-resistance-to "
                "relationship to fluoroquinolone antibiotics.",
                record_evidence,
                QNR_FLUOROQUINOLONE_RELATION_EVIDENCE,
                FLUOROQUINOLONE_EVIDENCE,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The pentapeptide-repeat domain is part of the Qnr determinant.",
                record_evidence,
                QNR_PARENT_EVIDENCE,
                PENTAPEPTIDE_DOMAIN_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "Qnr determinants adopt the pentapeptide-repeat right-handed "
                "beta-helix fold.",
                *pentapeptide_evidence,
            ),
            _edge(
                "domain",
                "enables (Qnr target protection)",
                "RO:0002327",
                "mech0",
                "The pentapeptide-repeat domain enables Qnr target protection "
                "through DNA mimicry.",
                *pentapeptide_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_graph(record, target)
    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    out["causal_graphs"] = [_qnr_graph(record)]
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Qnr target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = _dicts(record.get("curation_history"))
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
        help="ARO directory or one Qnr YAML file",
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
