#!/usr/bin/env python3
"""Ground and complete the generic rRNA methyltransferase ARO graph.

ARO:3000164 is the parent of both 16S and 23S rRNA methyltransferases, so its
graph must not hard-code the 16S decoding center.  This updater grounds the
broad rRNA methyltransferase activity, grounds the target-site node to the
broad rRNA Sequence Ontology term, adds the missing methylated-site-to-
resistance edge, and describes every causal edge.

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

IDENTIFIER = "ARO:3000164"
FILENAME = "rrna-methyltransferase-conferring-antibiotic-resistance-aro3000164.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Generalized the rRNA methyltransferase parent graph from a 16S decoding "
        "site to an rRNA antibiotic-binding site, grounded the activity and rRNA "
        "nodes, described every edge, and linked methylated rRNA to resistance"
    ),
    "llm_assisted": True,
}

TARGET_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": "Catalyzes methylation of rRNA.",
    "notes": "CARD definition for the rRNA methyltransferase parent term.",
}

TARGET_ALTERATION_EVIDENCE = {
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

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of the transfer of a methyl group from S-adenosyl-L-methionine "
        "to a nucleoside residue in an rRNA molecule. The methyl group can be "
        "transfered to the nucleobase or to the ribose group of the nucleoside."
    ),
    "notes": "GO definition for broad rRNA methyltransferase activity.",
}

RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both structural "
        "scaffolding and catalytic activity."
    ),
    "notes": (
        "Sequence Ontology definition for the broad rRNA superclass; the graph "
        "uses it as a conservative grounding for a generic rRNA antibiotic-binding "
        "site."
    ),
}

SHARED_NODE_UPDATES = {
    "methyltransferase": {
        "node_id": "methyltransferase",
        "label": "rRNA methyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008649",
        "description": (
            "Grounded to the broad GO rRNA methyltransferase activity term because "
            "this parent covers both 16S and 23S rRNA methyltransferases."
        ),
    },
    "decoding_site": {
        "node_id": "decoding_site",
        "label": "rRNA antibiotic-binding site",
        "node_type": "NUCLEIC_ACID",
        "grounding": "SO:0000252",
        "description": (
            "Grounded to the broad Sequence Ontology rRNA term because no stable "
            "narrow term is available for the generic rRNA antibiotic-binding site "
            "covered by this parent."
        ),
    },
    "methylated": {
        "node_id": "methylated",
        "label": "methylated rRNA antibiotic-binding site",
        "node_type": "STATE",
        "grounding": "SO:0000252",
        "description": (
            "Local state representing methylation of an antibiotic-binding site in "
            "16S or 23S rRNA. Grounded to broad rRNA because no stable narrow "
            "term is available for a generic methylated rRNA antibiotic-binding "
            "site."
        ),
    },
}

EXPECTED_EDGES = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "mech1"),
    ("mech1", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "methyltransferase"),
    ("methyltransferase", "methylated"),
    ("methylated", "decoding_site"),
    ("methylated", "resistance"),
}
EDGE_ORDER = (
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "mech1"),
    ("mech1", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "methyltransferase"),
    ("methyltransferase", "methylated"),
    ("methylated", "decoding_site"),
    ("methylated", "resistance"),
)

METHYLATED_RESISTANCE_EDGE = {
    "subject": "methylated",
    "predicate": "causally upstream of (blocks antibiotic binding)",
    "predicate_id": "RO:0002411",
    "object": "resistance",
}


@dataclass(frozen=True)
class EdgeUpdate:
    predicate: str
    predicate_id: str
    description: str
    evidence: tuple[dict[str, str], ...]


EDGE_UPDATES = {
    ("determinant", "mech0"): EdgeUpdate(
        predicate="participates in (resistance mechanism)",
        predicate_id="RO:0000056",
        description=(
            "CARD classifies rRNA methyltransferases under antibiotic target "
            "alteration because they enzymatically methylate rRNA target sites."
        ),
        evidence=(TARGET_EVIDENCE, TARGET_ALTERATION_EVIDENCE),
    ),
    ("mech0", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "Antibiotic target alteration is the broad resistance mechanism "
            "represented by rRNA methylation."
        ),
        evidence=(TARGET_EVIDENCE, TARGET_ALTERATION_EVIDENCE),
    ),
    ("determinant", "mech1"): EdgeUpdate(
        predicate="participates in (resistance mechanism)",
        predicate_id="RO:0000056",
        description=(
            "CARD also classifies rRNA methyltransferases under the "
            "ribosome-specific target-alteration branch."
        ),
        evidence=(TARGET_EVIDENCE, RIBOSOMAL_ALTERATION_EVIDENCE),
    ),
    ("mech1", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "Chemical alteration of ribosomal rRNA is the modeled "
            "ribosome-specific cause of resistance."
        ),
        evidence=(TARGET_EVIDENCE, RIBOSOMAL_ALTERATION_EVIDENCE),
    ),
    ("determinant", "resistance"): EdgeUpdate(
        predicate="causally upstream of (confers resistance)",
        predicate_id="RO:0002411",
        description=(
            "rRNA methyltransferases methylate rRNA target sites, chemically "
            "altering antibiotic binding sites in the ribosome."
        ),
        evidence=(
            TARGET_EVIDENCE,
            TARGET_ALTERATION_EVIDENCE,
            RIBOSOMAL_ALTERATION_EVIDENCE,
        ),
    ),
    ("determinant", "methyltransferase"): EdgeUpdate(
        predicate="enables",
        predicate_id="RO:0002327",
        description=(
            "The determinant enables methyl transfer onto nucleoside residues in "
            "rRNA."
        ),
        evidence=(TARGET_EVIDENCE, RRNA_METHYLTRANSFERASE_EVIDENCE),
    ),
    ("methyltransferase", "methylated"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "rRNA methyltransferase activity yields a methylated rRNA "
            "antibiotic-binding site."
        ),
        evidence=(TARGET_EVIDENCE, RRNA_METHYLTRANSFERASE_EVIDENCE),
    ),
    ("methylated", "decoding_site"): EdgeUpdate(
        predicate="negatively regulates (blocks antibiotic binding)",
        predicate_id="RO:0002212",
        description=(
            "Methylation changes the rRNA antibiotic-binding site and prevents "
            "normal drug binding."
        ),
        evidence=(TARGET_EVIDENCE, RRNA_METHYLTRANSFERASE_EVIDENCE, RRNA_EVIDENCE),
    ),
    ("methylated", "resistance"): EdgeUpdate(
        predicate="causally upstream of (blocks antibiotic binding)",
        predicate_id="RO:0002411",
        description=(
            "The methylated rRNA antibiotic-binding site is the terminal modeled "
            "cause of the resistance phenotype."
        ),
        evidence=(TARGET_EVIDENCE, RIBOSOMAL_ALTERATION_EVIDENCE),
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


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


def _enrich_nodes(graph: dict[str, Any]) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id not in SHARED_NODE_UPDATES:
            continue
        nodes[index] = copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        found.add(node_id)

    missing = sorted(set(SHARED_NODE_UPDATES) - found)
    if missing:
        missing_ids = ", ".join(missing)
        msg = f"{IDENTIFIER}: missing node(s): {missing_ids}"
        raise ValueError(msg)


def _canonical_edges() -> list[dict[str, Any]]:
    return [
        _ordered_edge(
            {
                "subject": subject,
                "predicate": EDGE_UPDATES[(subject, object_)].predicate,
                "predicate_id": EDGE_UPDATES[(subject, object_)].predicate_id,
                "object": object_,
                "description": EDGE_UPDATES[(subject, object_)].description,
                "evidence": [
                    copy.deepcopy(item)
                    for item in EDGE_UPDATES[(subject, object_)].evidence
                ],
            }
        )
        for subject, object_ in EDGE_ORDER
    ]


def _validate_and_complete_edges(graph: dict[str, Any]) -> None:
    edges = graph.setdefault("edges", [])
    if not any(_edge_key(edge) == ("methylated", "resistance") for edge in edges):
        edges.append(copy.deepcopy(METHYLATED_RESISTANCE_EDGE))

    seen: set[tuple[str, str]] = set()
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_EDGES:
            msg = f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    if seen != EXPECTED_EDGES:
        missing_edges = sorted(EXPECTED_EDGES - seen)
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{IDENTIFIER}: missing edge(s): {missing}"
        raise ValueError(msg)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        msg = f"expected {IDENTIFIER}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{IDENTIFIER}: missing resistance causal graph"
        raise ValueError(msg)

    _enrich_nodes(graph)
    _validate_and_complete_edges(graph)
    graph["description"] = (
        "Curated resistance-causation graph for generic rRNA methyltransferases. "
        "The graph covers methylation of 16S or 23S rRNA antibiotic-binding sites "
        "by using broad rRNA methyltransferase and rRNA groundings."
    )
    graph["edges"] = _canonical_edges()
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not generic rRNA methyltransferase: {record.get('identifier')}")
    if path.name != FILENAME:
        raise ValueError(f"{path}: {IDENTIFIER} must be in {FILENAME}")

    enriched, changed = enrich_record(record)
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
    return [path / FILENAME]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the generic rRNA methyltransferase YAML file",
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
