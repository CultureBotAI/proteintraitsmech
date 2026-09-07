#!/usr/bin/env python3
"""Ground and correct ndh-mediated isoniazid resistance graphs.

The existing ndh graphs keep CARD's two downstream arms separate, but leave the
NADH-oxidation activity ungrounded and model one local blocked-activation state
as an ungrounded BIOLOGICAL_PROCESS. This updater grounds the activity to the
broad NADH dehydrogenase GO term and keeps all ndh-specific metabolite and
InhA-binding changes as described local STATE nodes.

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
HISTORY_ACTION = "Grounded ndh NADH-dehydrogenase resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3003460"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "ndh is a NADH oxidase. It participates in antibiotic resistance by "
        "diminishing NADH oxidation and consequently causes an increase in NADH "
        "concentration and depletion of NAD+. This alteration of the NADH/NAD+ "
        "ratio prevents the peroxidation reactions required for the activation "
        "of INH, as well as the displacement of the NADH-isonicotinic acyl "
        "complex from InhA enzyme binding site."
    ),
    "notes": "CARD definition for the antibiotic resistant ndh parent.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

NADH_DEHYDROGENASE_EVIDENCE = {
    "reference": "GO:0003954",
    "snippet": "Catalysis of the reaction: NADH + H+ + acceptor = NAD+ + reduced acceptor.",
    "notes": (
        "GO NADH dehydrogenase activity covers NADH oxidation while leaving the "
        "electron acceptor unspecified."
    ),
}

ISONIAZID_LIKE_EVIDENCE = {
    "reference": "ARO:3007152",
    "snippet": "isoniazid-like antibiotic",
    "notes": "ARO drug-class term inherited by ndh records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "isoniazid-like antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007152",
}

NADH_DEHYDROGENASE_NODE = {
    "node_id": "nadh_dehydrogenase",
    "label": "NADH dehydrogenase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0003954",
}

DIMINISHED_ACTIVITY_NODE = {
    "node_id": "diminished_activity",
    "label": "diminished Ndh NADH dehydrogenase activity",
    "node_type": "STATE",
    "description": (
        "Local state for ndh mutations that reduce NdhII-mediated NADH "
        "oxidation."
    ),
}

RATIO_NODE = {
    "node_id": "nadh_ratio",
    "label": "increased intracellular NADH/NAD+ ratio",
    "node_type": "STATE",
    "description": (
        "Local state for the increased NADH concentration and depleted NAD+ "
        "pool caused by reduced Ndh activity."
    ),
}

BLOCKED_ACTIVATION_NODE = {
    "node_id": "blocked_activation",
    "label": "reduced isoniazid activation",
    "node_type": "STATE",
    "description": (
        "Local state for impaired INH activation caused by altered NADH/NAD+ "
        "balance."
    ),
}

INHA_BINDING_NODE = {
    "node_id": "inha_binding",
    "label": "reduced INH-NAD adduct binding to InhA",
    "node_type": "STATE",
    "description": (
        "Local state for high NADH competitively inhibiting INH-NAD adduct "
        "binding to InhA."
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
}

OLD_NDH_EDGE_KEYS = {
    ("determinant", "RO:0002212", "nadh_ox"),
    ("nadh_ox", "RO:0002411", "ratio"),
    ("ratio", "RO:0002212", "peroxidation"),
    ("ratio", "RO:0002212", "displacement"),
}

NEW_NDH_EDGE_KEYS = {
    ("determinant", "RO:0002327", "nadh_dehydrogenase"),
    ("determinant", "RO:0000086", "diminished_activity"),
    ("diminished_activity", "RO:0002212", "nadh_dehydrogenase"),
    ("diminished_activity", "RO:0002411", "nadh_ratio"),
    ("nadh_ratio", "RO:0002411", "blocked_activation"),
    ("nadh_ratio", "RO:0002411", "inha_binding"),
    ("blocked_activation", "RO:0002411", "resistance"),
    ("inha_binding", "RO:0002411", "resistance"),
}

EXPECTED_EDGE_KEYS = CORE_EDGE_KEYS | NEW_NDH_EDGE_KEYS
INPUT_EDGE_KEYS = CORE_EDGE_KEYS | OLD_NDH_EDGE_KEYS | NEW_NDH_EDGE_KEYS

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies ndh records under mutation conferring antibiotic "
        "resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Loss-of-function point mutations in ndh are a mutation-mediated "
        "isoniazid-resistance mechanism."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "ndh mutations confer isoniazid resistance by diminishing NADH "
        "oxidation and altering intracellular NADH/NAD+ balance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the antibiotic resistant ndh family to isoniazid-like "
        "antibiotics."
    ),
    ("determinant", "RO:0002327", "nadh_dehydrogenase"): (
        "Ndh normally enables NADH dehydrogenase activity."
    ),
    ("determinant", "RO:0000086", "diminished_activity"): (
        "Resistance-conferring ndh mutations diminish Ndh-mediated NADH "
        "oxidation."
    ),
    ("diminished_activity", "RO:0002212", "nadh_dehydrogenase"): (
        "The diminished-activity state inhibits Ndh NADH dehydrogenase "
        "activity."
    ),
    ("diminished_activity", "RO:0002411", "nadh_ratio"): (
        "Reduced Ndh-mediated NADH oxidation increases intracellular NADH "
        "concentration and depletes NAD+."
    ),
    ("nadh_ratio", "RO:0002411", "blocked_activation"): (
        "The altered NADH/NAD+ ratio blocks peroxidation reactions required "
        "for INH activation."
    ),
    ("nadh_ratio", "RO:0002411", "inha_binding"): (
        "Increased NADH competitively interferes with INH-NAD adduct binding "
        "to InhA."
    ),
    ("blocked_activation", "RO:0002411", "resistance"): (
        "Decreased INH activation prevents formation of the active inhibitor "
        "and contributes to isoniazid resistance."
    ),
    ("inha_binding", "RO:0002411", "resistance"): (
        "Decreased INH-NAD adduct binding leaves InhA less inhibited and "
        "contributes to isoniazid resistance."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="antibiotic-resistant-ndh-aro3003460.yaml",
    ),
    "ARO:3003461": Target(
        identifier="ARO:3003461",
        filename=(
            "mycobacterium-tuberculosis-ndh-with-mutation-conferring-"
            "resistance-to-isoniazid-aro3003461.yaml"
        ),
    ),
    "ARO:3003778": Target(
        identifier="ARO:3003778",
        filename=(
            "mycolicibacterium-smegmatis-ndh-with-mutation-conferring-"
            "resistance-to-isoniazid-aro3003778.yaml"
        ),
    ),
    "ARO:3003779": Target(
        identifier="ARO:3003779",
        filename=(
            "mycobacterium-tuberculosis-variant-bovis-ndh-with-mutation-"
            "conferring-resistance-aro3003779.yaml"
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = (
            "ARO drug-class relationship asserted directly on the antibiotic "
            "resistant ndh parent."
        )
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3003460 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3007152 ! "
            "isoniazid-like antibiotic"
        ),
        "notes": notes,
    }


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


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    old_edges = found_edges & OLD_NDH_EDGE_KEYS
    new_edges = found_edges & NEW_NDH_EDGE_KEYS
    if old_edges == OLD_NDH_EDGE_KEYS and not new_edges:
        return
    if new_edges == NEW_NDH_EDGE_KEYS and not old_edges:
        return

    missing_old = OLD_NDH_EDGE_KEYS - old_edges
    missing_new = NEW_NDH_EDGE_KEYS - new_edges
    missing = min(missing_old, missing_new, key=len)
    missing_text = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in sorted(missing))
    raise ValueError(f"{target.identifier}: incomplete ndh edge set: {missing_text}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)

    mutation_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    nadh_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        NADH_DEHYDROGENASE_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        _drug_relation_evidence(target),
        ISONIAZID_LIKE_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → altered NADH/NAD+ balance → isoniazid resistance",
        "description": (
            "Conservative graph for ndh-mediated isoniazid resistance. The "
            "graph grounds the diminished NADH-oxidation step to the broad "
            "NADH dehydrogenase GO activity and models both downstream "
            "consequences of the altered NADH/NAD+ ratio as described local "
            "states."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(NADH_DEHYDROGENASE_NODE),
            copy.deepcopy(DIMINISHED_ACTIVITY_NODE),
            copy.deepcopy(RATIO_NODE),
            copy.deepcopy(BLOCKED_ACTIVATION_NODE),
            copy.deepcopy(INHA_BINDING_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "nadh_dehydrogenase",
                nadh_evidence,
            ),
            _edge(
                "determinant",
                "has quality",
                "RO:0000086",
                "diminished_activity",
                nadh_evidence,
            ),
            _edge(
                "diminished_activity",
                "negatively regulates",
                "RO:0002212",
                "nadh_dehydrogenase",
                nadh_evidence,
            ),
            _edge(
                "diminished_activity",
                "causally upstream of",
                "RO:0002411",
                "nadh_ratio",
                nadh_evidence,
            ),
            _edge(
                "nadh_ratio",
                "causally upstream of",
                "RO:0002411",
                "blocked_activation",
                nadh_evidence,
            ),
            _edge(
                "nadh_ratio",
                "causally upstream of",
                "RO:0002411",
                "inha_binding",
                nadh_evidence,
            ),
            _edge(
                "blocked_activation",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                nadh_evidence,
            ),
            _edge(
                "inha_binding",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                nadh_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ndh target: {identifier}")
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or exact ndh YAML")
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
