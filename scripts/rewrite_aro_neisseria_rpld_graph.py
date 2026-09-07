#!/usr/bin/env python3
"""Rewrite the Neisseria gonorrhoeae rplD macrolide-resistance graph.

The rplD record is a macrolide-resistance gene variant for the 50S L4
ribosomal protein.  Its promoted graph left the broad ribosome target node
ungrounded and modeled the rplD determinant itself as part of the ribosome.
This updater keeps the supported mutation and drug-target assertions, grounds
the broad ribosome target to GO:0005840, and leaves out unsupported 50S
binding-site partonomy.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

TARGET_IDENTIFIER = "ARO:3004956"
TARGET_FILENAME = "neisseria-gonorrhoeae-rpld-aro3004956.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Completed Neisseria gonorrhoeae rplD macrolide-resistance graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

MACROLIDE_PARENT_EVIDENCE = {
    "reference": "ARO:3005001",
    "snippet": (
        "Nucleotide point mutations in the 50S rRNA subunit may confer "
        "resistance to macrolide antibiotics."
    ),
    "notes": "ARO parent carrying the inherited macrolide drug-class relation.",
}

MACROLIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3005001",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000000 ! macrolide antibiotic",
    "notes": "Macrolide drug-class relation inherited from ARO:3005001.",
}

RIBOSOME_EVIDENCE = {
    "reference": "GO:0005840",
    "snippet": (
        "A ribonucleoprotein complex which is the site of protein synthesis "
        "during translation."
    ),
    "notes": "GO definition for the broad ribosome node.",
}

JCM_EVIDENCE = {
    "reference": "DOI:10.1128/JCM.03195-15",
    "notes": "PMID:26935729 (aro citation)",
}

JID_EVIDENCE = {
    "reference": "DOI:10.1093/infdis/jiw420",
    "notes": "PMID:27638945 (aro citation)",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

MACROLIDE_NODE = {
    "node_id": "drug0",
    "label": "macrolide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000000",
}

RIBOSOME_NODE = {
    "node_id": "ribosome",
    "label": "bacterial ribosome",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0005840",
    "description": (
        "Grounded to the broad GO ribosome class because the record supports "
        "a broad macrolide-ribosome target node, not a narrower binding site."
    ),
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
        key = (
            item["reference"],
            item.get("snippet", ""),
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        MUTATION_EVIDENCE,
        JCM_EVIDENCE,
        JID_EVIDENCE,
    )
    drug_evidence = (
        record_evidence,
        MACROLIDE_PARENT_EVIDENCE,
        MACROLIDE_RELATION_EVIDENCE,
        JCM_EVIDENCE,
        JID_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → L4 mutation → macrolide resistance",
        "description": (
            "Curated resistance-causation graph for Neisseria gonorrhoeae "
            "rplD macrolide resistance. The graph preserves the broad "
            "macrolide-ribosome target context without asserting a specific "
            "altered binding site."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "NUCLEIC_ACID",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(MACROLIDE_NODE),
            copy.deepcopy(RIBOSOME_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies Neisseria gonorrhoeae rplD under mutation "
                "conferring antibiotic resistance.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "rplD mutations cause an altered gene product associated with "
                "macrolide resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Neisseria gonorrhoeae rplD variants confer macrolide "
                "resistance through the antibiotic-resistance mutation "
                "mechanism.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts an inherited macrolide-antibiotic drug-class "
                "relation for Neisseria gonorrhoeae rplD.",
                *drug_evidence,
            ),
            _edge(
                "drug0",
                "molecularly interacts with (targets the ribosome)",
                "RO:0002436",
                "ribosome",
                "Macrolides target the bacterial ribosome; this rplD record "
                "does not support a narrower binding-site assertion.",
                *drug_evidence,
                RIBOSOME_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"expected {TARGET_IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{TARGET_IDENTIFIER}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "drug0", "ribosome", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{TARGET_IDENTIFIER}: missing node(s): {missing_ids}")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"{path}: not a Neisseria gonorrhoeae rplD target")
    if path.name != TARGET_FILENAME:
        raise ValueError(f"{path}: target must be in {TARGET_FILENAME}")

    enriched, changed = enrich_record(record)
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
    return [path / TARGET_FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the exact Neisseria gonorrhoeae rplD YAML file",
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
