#!/usr/bin/env python3
"""Ground and describe ATP synthase bedaquiline-resistance graphs.

The ARO ATP synthase branch models bedaquiline resistance caused by altered
ATP synthase subunit C, but leaves the ATP-synthesis process ungrounded and
does not connect bedaquiline binding/blocking back to ATP synthesis. This
updater grounds that process to GO:0015986, describes the local blocking
state, describes every edge, and keeps the exact three-record branch
idempotent.

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
HISTORY_ACTION = "Grounded ATP synthase bedaquiline-resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of "
        "repressors that result in increased expression of genes that inactivate "
        "or pump out antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

ATP_SYNTHASE_EVIDENCE = {
    "reference": "ARO:3007477",
    "snippet": (
        "ATP synthase enzymes, specifically subunit C, resistant to "
        "diarylquinolone antibiotics including Bedaquiline. Mutations in ATP "
        "synthase confer antibiotic resistance by disrupting binding and "
        "blocking of ATP synthase reactions by Bedaquiline."
    ),
    "notes": "CARD definition for antibiotic resistant ATP synthase.",
}

ATP_SYNTHASE_SOURCE_EVIDENCE = {
    "reference": "PMID:36988496",
    "notes": (
        "CARD cites PMID:36988496 for the parent and Mycobacterium abscessus "
        "atpE bedaquiline-resistance records."
    ),
}

GO_ATP_SYNTHESIS_EVIDENCE = {
    "reference": "GO:0015986",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of ATP "
        "driven by transport of protons across a membrane to generate an "
        "electrochemical gradient (proton-motive force)."
    ),
    "notes": "GO definition for proton motive force-driven ATP synthesis.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "diarylquinoline antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3004491",
}

ATP_SYNTHESIS_NODE = {
    "node_id": "atp_synthesis",
    "label": "proton motive force-driven ATP synthesis",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0015986",
    "description": (
        "ATP synthesis coupled to proton transport by the membrane ATP synthase."
    ),
}

BLOCKING_NODE = {
    "node_id": "blocking",
    "label": "bedaquiline-bound blocked ATP synthase",
    "node_type": "STATE",
    "description": (
        "Local state representing bedaquiline binding and blocking ATP synthase; "
        "subunit-C mutations reduce this drug-bound blocked state."
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("drug0", "RO:0002411", "blocking"),
    ("determinant", "RO:0002212", "blocking"),
}

LEGACY_ATP_SYNTHESIS_EDGE_KEY = (
    "determinant",
    "BFO:0000050",
    "atp_synthesis",
)

CANONICAL_ATP_SYNTHESIS_EDGE_KEY = (
    "determinant",
    "RO:0000056",
    "atp_synthesis",
)

BLOCKING_ATP_SYNTHESIS_EDGE_KEY = (
    "blocking",
    "RO:0002212",
    "atp_synthesis",
)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    has_primary_source: bool = False


TARGETS = {
    "ARO:3007477": Target(
        identifier="ARO:3007477",
        filename="antibiotic-resistant-atp-synthase-aro3007477.yaml",
        has_primary_source=True,
    ),
    "ARO:3007476": Target(
        identifier="ARO:3007476",
        filename=(
            "mycobacterium-abscessus-atpe-with-mutation-conferring-resistance-to-"
            "bedaquiline-aro3007476.yaml"
        ),
        has_primary_source=True,
    ),
    "ARO:3007854": Target(
        identifier="ARO:3007854",
        filename=(
            "mycobacterium-tuberculosis-atpe-with-mutation-conferring-resistance-"
            "to-bedaquili-aro3007854.yaml"
        ),
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return CORE_EDGE_KEYS | {
        CANONICAL_ATP_SYNTHESIS_EDGE_KEY,
        BLOCKING_ATP_SYNTHESIS_EDGE_KEY,
    }


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | {LEGACY_ATP_SYNTHESIS_EDGE_KEY}


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_evidence(target: Target) -> dict[str, str]:
    return {
        "reference": "ARO:3007477",
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3004491 ! "
            "diarylquinoline antibiotic"
        ),
        "notes": (
            "ARO drug-class relationship on ARO:3007477; modeled here as a "
            "determinant-to-diarylquinoline-antibiotic edge and inherited by "
            "the atpE leaf records."
        ),
    }


def _extra_source_evidence(target: Target) -> tuple[dict[str, str], ...]:
    return (ATP_SYNTHASE_SOURCE_EVIDENCE,) if target.has_primary_source else ()


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


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


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": description,
            "evidence": _unique_evidence(evidence),
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {
        "determinant",
        "mech0",
        "drug0",
        "atp_synthesis",
        "blocking",
        "resistance",
    }
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    has_legacy_atp_edge = LEGACY_ATP_SYNTHESIS_EDGE_KEY in found_edges
    has_canonical_atp_edge = CANONICAL_ATP_SYNTHESIS_EDGE_KEY in found_edges
    if not has_legacy_atp_edge and not has_canonical_atp_edge:
        raise ValueError(
            f"{target.identifier}: missing ATP synthase participation edge"
        )


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(ATP_SYNTHESIS_NODE),
        copy.deepcopy(BLOCKING_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    source_evidence = _extra_source_evidence(target)
    mutation_evidence = (
        target_evidence,
        ATP_SYNTHASE_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    atp_evidence = (
        target_evidence,
        ATP_SYNTHASE_EVIDENCE,
        GO_ATP_SYNTHESIS_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        _drug_evidence(target),
        *source_evidence,
    )
    blocking_evidence = (
        target_evidence,
        ATP_SYNTHASE_EVIDENCE,
        GO_ATP_SYNTHESIS_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "ARO classifies these ATP synthase variants under mutation "
                "conferring antibiotic resistance."
            ),
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "The altered ATP synthase target blocks bedaquiline action and "
                "therefore confers resistance."
            ),
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Subunit-C ATP synthase mutations confer bedaquiline resistance "
                "by disrupting target binding and blocking."
            ),
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            (
                "The parent ARO term links antibiotic-resistant ATP synthase to "
                "diarylquinoline antibiotics."
            ),
            drug_evidence,
        ),
        _edge(
            "determinant",
            "participates in (proton motive force-driven ATP synthesis)",
            "RO:0000056",
            "atp_synthesis",
            (
                "ATP synthase subunit C is a component of the membrane ATP "
                "synthase that performs proton motive force-driven ATP synthesis."
            ),
            atp_evidence,
        ),
        _edge(
            "drug0",
            "causally upstream of (binds and blocks ATP synthase)",
            "RO:0002411",
            "blocking",
            (
                "Bedaquiline is modeled as producing the local state in which "
                "ATP synthase is bound and blocked."
            ),
            blocking_evidence,
        ),
        _edge(
            "blocking",
            "negatively regulates",
            "RO:0002212",
            "atp_synthesis",
            (
                "Bedaquiline binding and blocking of ATP synthase inhibits the "
                "grounded ATP-synthesis process."
            ),
            blocking_evidence,
        ),
        _edge(
            "determinant",
            "negatively regulates (mutations disrupt drug binding)",
            "RO:0002212",
            "blocking",
            (
                "ATP synthase subunit-C mutations reduce the bedaquiline-bound "
                "blocked state."
            ),
            mutation_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["title"] = f"{record['label']} → blocked ATP synthesis → resistance"
    graph["description"] = (
        "Conservative graph for bedaquiline resistance caused by ATP synthase "
        "subunit-C variants. The graph grounds proton motive force-driven ATP "
        "synthesis to GO:0015986, models bedaquiline binding and blocking of "
        "ATP synthase as a local state, and links subunit-C variants to reduced "
        "blocking of the ATP-synthesis process."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an atpE target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
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
        help="ARO directory or one of the three target YAML files",
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
