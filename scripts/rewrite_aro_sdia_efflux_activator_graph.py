#!/usr/bin/env python3
"""Ground and complete the conditional sdiA efflux-activator ARO graph.

CARD records sdiA as a positive regulator of AcrAB only when expressed from a
plasmid, with no effect observed for chromosomal sdiA.  This updater grounds the
named AcrAB-TolC pump, grounds broad transcriptional activation to GO, adds the
missing pump-to-efflux edge, and replaces stale AdeR archetype evidence with
exact sdiA and AcrAB-TolC evidence.

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

IDENTIFIER = "ARO:3000826"
FILENAME = "sdia-aro3000826.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Replaced stale archetype evidence on the sdiA efflux-activator graph, "
        "grounded its conditional AcrAB-TolC pump and transcriptional-activation "
        "nodes, and linked plasmid-expressed sdiA activation to antibiotic efflux"
    ),
    "llm_assisted": True,
}

SDIA_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "SdiA is a cell division regulator that is also a positive regulator of "
        "AcrAB only when it's expressed from a plasmid. When the sdiA gene is on "
        "the chromosome, it has no effect on expression of acrAB."
    ),
    "notes": "CARD definition for the conditional sdiA efflux-pump activator.",
}

ACRAB_TOLC_EVIDENCE = {
    "reference": "ARO:3000384",
    "snippet": (
        "AcrAB-TolC is a tripartite RND efflux system that confers resistance to "
        "tetracycline, chloramphenicol, ampicillin, nalidixic acid, and rifampin "
        "in Gram-negative bacteria. The system spans the cell membrane (AcrB) and "
        "the outer-membrane (TolC), and is linked together in the periplasm by "
        "AcrA."
    ),
    "notes": "CARD definition for the AcrAB-TolC efflux pump activated by plasmid sdiA.",
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional activation process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "AcrAB-TolC",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000384",
    "description": (
        "Grounded to CARD's AcrAB-TolC, the tripartite pump encoded by the acrAB "
        "locus activated by plasmid-expressed sdiA."
    ),
}

ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of acrAB transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation process "
        "for the plasmid-expressed sdiA condition that promotes acrAB expression."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms but "
        "has no term for the resistance phenotype itself."
    ),
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
            "CARD classifies sdiA under antibiotic efflux because plasmid-expressed "
            "SdiA positively regulates AcrAB expression."
        ),
        evidence=(SDIA_EVIDENCE, ACRAB_TOLC_EVIDENCE),
    ),
    ("mech0", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "The broad efflux mechanism represents elevated activity of the "
            "SdiA-regulated AcrAB-TolC tripartite RND efflux system."
        ),
        evidence=(SDIA_EVIDENCE, ACRAB_TOLC_EVIDENCE),
    ),
    ("determinant", "resistance"): EdgeUpdate(
        predicate="causally upstream of (confers resistance)",
        predicate_id="RO:0002411",
        description=(
            "When sdiA is expressed from a plasmid, SdiA activates AcrAB-TolC "
            "expression and increases antibiotic efflux."
        ),
        evidence=(SDIA_EVIDENCE, ACRAB_TOLC_EVIDENCE),
    ),
    ("determinant", "activation"): EdgeUpdate(
        predicate="enables (activates pump transcription)",
        predicate_id="RO:0002327",
        description=(
            "Plasmid-expressed sdiA participates in positive regulation of acrAB "
            "transcription."
        ),
        evidence=(SDIA_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE),
    ),
    ("activation", "pump"): EdgeUpdate(
        predicate="positively regulates (raises pump expression)",
        predicate_id="RO:0002213",
        description=(
            "Transcriptional activation raises acrAB transcription and increases "
            "expression of AcrAB-TolC."
        ),
        evidence=(SDIA_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE, ACRAB_TOLC_EVIDENCE),
    ),
    ("pump", "mech0"): EdgeUpdate(
        predicate="enables (drug efflux)",
        predicate_id="RO:0002327",
        description=(
            "AcrAB-TolC is the tripartite multidrug efflux system whose "
            "SdiA-activated expression supplies antibiotic efflux."
        ),
        evidence=(SDIA_EVIDENCE, ACRAB_TOLC_EVIDENCE),
    ),
}

ENRICHED_FULL_EDGES = {
    (subject, update.predicate_id, object_)
    for (subject, object_), update in EDGE_UPDATES.items()
}
LEGACY_FULL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "activation"),
    ("activation", "RO:0002213", "pump"),
}
EXPECTED_CURRENT_FULL_EDGES = ENRICHED_FULL_EDGES | LEGACY_FULL_EDGES
EDGE_ORDER = (
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "activation"),
    ("activation", "pump"),
    ("pump", "mech0"),
)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _full_edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return edge.get("subject", ""), edge.get("predicate_id", ""), edge.get("object", "")


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


def _validate_current_edges(graph: dict[str, Any]) -> None:
    current: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _full_edge_key(edge)
        if full_key in current:
            msg = f"{IDENTIFIER}: duplicate edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)
        if full_key not in EXPECTED_CURRENT_FULL_EDGES:
            msg = f"{IDENTIFIER}: unexpected edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)
        current.add(full_key)

    if current != LEGACY_FULL_EDGES and current != ENRICHED_FULL_EDGES:
        for expected in (LEGACY_FULL_EDGES, ENRICHED_FULL_EDGES):
            if current <= expected:
                missing_edges = sorted(expected - current)
                missing = ", ".join(
                    f"{subject} -> {object_}" for subject, _, object_ in missing_edges
                )
                msg = f"{IDENTIFIER}: missing edge(s): {missing}"
                raise ValueError(msg)
        msg = f"{IDENTIFIER}: edge set is neither legacy nor enriched"
        raise ValueError(msg)


def _enrich_nodes(graph: dict[str, Any]) -> None:
    nodes = graph.get("nodes") or []
    by_id = {node.get("node_id"): node for node in nodes if isinstance(node, dict)}
    if "determinant" not in by_id:
        msg = f"{IDENTIFIER}: missing node(s): determinant"
        raise ValueError(msg)

    graph["nodes"] = [
        copy.deepcopy(by_id["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(PUMP_NODE),
        copy.deepcopy(ACTIVATION_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for subject, object_ in EDGE_ORDER:
        update = EDGE_UPDATES[(subject, object_)]
        edges.append(
            _ordered_edge(
                {
                    "subject": subject,
                    "predicate": update.predicate,
                    "predicate_id": update.predicate_id,
                    "object": object_,
                    "description": update.description,
                    "evidence": [copy.deepcopy(item) for item in update.evidence],
                }
            )
        )
    return edges


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

    _validate_current_edges(graph)
    graph["description"] = (
        "Curated resistance-causation graph for conditional sdiA efflux-pump "
        "activation. The graph replaces stale archetype evidence, grounds the "
        "AcrAB-TolC pump and transcriptional activation node, and preserves the "
        "plasmid-expression condition."
    )
    _enrich_nodes(graph)
    graph["edges"] = _canonical_edges()
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not sdiA: {record.get('identifier')}")
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or sdiA YAML file")
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
