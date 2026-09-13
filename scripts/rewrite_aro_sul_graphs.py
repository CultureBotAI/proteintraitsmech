#!/usr/bin/env python3
"""Rewrite sulfonamide-resistant sul target-replacement graphs.

The sul branch encodes sulfonamide-resistant dihydropteroate synthases that
replace the sensitive folate-pathway DHPS target. These exact score-77 records
already carried grounded pterin-binding/TIM-barrel annotations, but their old
graphs lacked grounded dihydropteroate synthase activity.

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

PARENT_IDENTIFIER = "ARO:3004238"
SULFONAMIDE_IDENTIFIER = "ARO:3000282"

HISTORY_ACTION = "Completed sul DHPS target-replacement graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

SUL_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "The sul genes encode forms of dihydropteroate synthase that confer "
        "resistance to sulfonamide."
    ),
    "notes": "CARD definition for sulfonamide resistant sul.",
}

TARGET_REPLACEMENT_EVIDENCE = {
    "reference": "ARO:3000381",
    "snippet": (
        "Alternate proteins that have the same functions as other antibiotic "
        "target proteins, but are structurally different and thus resistant to "
        "antibiotics. These can replace the activity of other "
        "antibiotic-sensitive proteins in the presence of antibiotics."
    ),
    "notes": "CARD definition for antibiotic target replacement proteins.",
}

SUL_STRUCTURE_EVIDENCE = {
    "reference": "PMID:37419898",
    "snippet": (
        "Sul enzyme types (Sul1, Sul2 and Sul3) in multiple ligand-bound states, "
        "revealing a substantial reorganization of their pABA-interaction "
        "region relative to the corresponding region of DHPS."
    ),
    "notes": "Evidence for sulfonamide-resistant Sul DHPS target replacement.",
}

GO_DHPS_EVIDENCE = {
    "reference": "GO:0004156",
    "snippet": (
        "Catalysis of the reaction: "
        "2-amino-4-hydroxy-6-hydroxymethyl-7,8-dihydropteridine diphosphate + "
        "4-aminobenzoate = diphosphate + dihydropteroate."
    ),
    "notes": "GO definition for dihydropteroate synthase activity.",
}

GO_FOLATE_EVIDENCE = {
    "reference": "GO:0009396",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "folic acid and its derivatives."
    ),
    "notes": "GO definition for folic acid-containing compound biosynthetic process.",
}

SULFONAMIDE_EVIDENCE = {
    "reference": SULFONAMIDE_IDENTIFIER,
    "snippet": "sulfonamide antibiotic",
    "notes": "ARO drug-class term for sulfonamide antibiotics.",
}

PFAM_DHPS_EVIDENCE = {
    "reference": "Pfam:PF00809",
    "snippet": "Pterin binding enzyme",
    "notes": "Pfam family for the pterin-binding DHPS domain.",
}

CATH_TIM_BARREL_EVIDENCE = {
    "reference": "CATH:3.20.20",
    "snippet": "TIM Barrel",
    "notes": "CATH fold used by these sulfonamide-resistant DHPS records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target replacement",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001002",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "sulfonamide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": SULFONAMIDE_IDENTIFIER,
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "pterin-binding dihydropteroate synthase domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00809",
    "description": "Pterin-binding DHPS catalytic domain.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "TIM-barrel fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.20.20",
    "description": "TIM-barrel structural fold.",
}

DHPS_NODE = {
    "node_id": "dhps_activity",
    "label": "dihydropteroate synthase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004156",
}

FOLATE_NODE = {
    "node_id": "folate_biosynthesis",
    "label": "folic acid-containing compound biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009396",
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
    is_parent: bool = False


TARGETS = (
    Target(PARENT_IDENTIFIER, "sulfonamide-resistant-sul-aro3004238.yaml", True),
    Target("ARO:3000410", "sul1-aro3000410.yaml"),
    Target("ARO:3000412", "sul2-aro3000412.yaml"),
    Target("ARO:3000413", "sul3-aro3000413.yaml"),
    Target("ARO:3004361", "sul4-aro3004361.yaml"),
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
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (item["reference"], item.get("snippet", ""), item.get("notes", ""))
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    notes = (
        "Asserted directly on ARO:3004238 in the CARD/ARO release in data/raw/aro/aro.obo."
        if target.is_parent
        else (
            f"Asserted on ARO:3004238 and inherited by this record's {target.identifier}. "
            "CARD/ARO release in data/raw/aro/aro.obo."
        )
    )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": "relationship: confers_resistance_to_drug_class ARO:3000282 ! sulfonamide antibiotic",
        "notes": notes,
    }


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


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    target_evidence = _target_evidence(record)
    sul_branch_evidence = (
        target_evidence,
        SUL_EVIDENCE,
        TARGET_REPLACEMENT_EVIDENCE,
        SUL_STRUCTURE_EVIDENCE,
    )
    dhps_evidence = (
        target_evidence,
        SUL_EVIDENCE,
        GO_DHPS_EVIDENCE,
        SUL_STRUCTURE_EVIDENCE,
    )
    drug_evidence = (
        target_evidence,
        _drug_relation_evidence(target),
        SULFONAMIDE_EVIDENCE,
        SUL_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → DHPS target replacement → sulfonamide resistance",
        "description": (
            "Curated resistance-causation graph for a sulfonamide-resistant "
            "Sul dihydropteroate synthase. The graph models resistance as "
            "target replacement by a sulfonamide-insensitive DHPS enzyme that "
            "preserves folate-pathway activity."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(DOMAIN_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(DHPS_NODE),
            copy.deepcopy(FOLATE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies sulfonamide-resistant Sul under antibiotic target replacement.",
                *sul_branch_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Sulfonamide-resistant replacement DHPS maintains folate biosynthesis.",
                *sul_branch_evidence,
                GO_FOLATE_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The sul determinant encodes a DHPS that replaces the sulfonamide-sensitive target.",
                *sul_branch_evidence,
                GO_DHPS_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "ARO maps the sul branch to sulfonamide antibiotics.",
                *drug_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The pterin-binding DHPS domain is part of the Sul protein determinant.",
                target_evidence,
                PFAM_DHPS_EVIDENCE,
                GO_DHPS_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the TIM-barrel fold used by DHPS enzymes.",
                target_evidence,
                CATH_TIM_BARREL_EVIDENCE,
                GO_DHPS_EVIDENCE,
            ),
            _edge(
                "domain",
                "enables",
                "RO:0002327",
                "dhps_activity",
                "The pterin-binding domain enables dihydropteroate synthase activity.",
                PFAM_DHPS_EVIDENCE,
                *dhps_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "dhps_activity",
                "The Sul determinant encodes a dihydropteroate synthase enzyme.",
                *dhps_evidence,
            ),
            _edge(
                "dhps_activity",
                "part of",
                "BFO:0000050",
                "folate_biosynthesis",
                "Dihydropteroate synthase activity is part of folate biosynthesis.",
                GO_DHPS_EVIDENCE,
                GO_FOLATE_EVIDENCE,
                SUL_EVIDENCE,
            ),
        ],
    }


def enrich_record(
    record: dict[str, Any],
    target: Target,
) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

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
        raise ValueError(f"{path}: not a sul DHPS target: {identifier}")
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
        help="ARO directory or one sul DHPS YAML file",
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
