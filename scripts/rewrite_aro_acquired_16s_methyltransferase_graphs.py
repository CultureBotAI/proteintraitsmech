#!/usr/bin/env python3
"""Ground acquired 16S rRNA methyltransferase leaf graphs.

The acquired Arm/Rmt/Npm/Kam/Sgm ARO leaves have already inherited the
antibiotic target alteration, ribosomal alteration, and aminoglycoside
drug-class routes. Their local side path is still a generic, partly ungrounded
``methyltransferase -> methylated -> decoding_site`` model.

This updater rewrites exactly those fourteen leaves to a compact graph that
keeps the ARO mechanism and drug-class edges, then replaces the local
decoding-site state chain with the exact Rhea reaction for the leaf's parent
subfamily: G1405 N7-methylation or A1408 N1-methylation of 16S rRNA.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
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
HISTORY_ACTION = "Grounded acquired 16S rRNA methyltransferase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
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

SUBFAMILY_EVIDENCE = {
    "ARO:3004271": {
        "reference": "ARO:3004271",
        "snippet": (
            "Methyltransferases that methylate the G1405 position of 16S rRNA, "
            "which is part of an aminoglycoside binding site."
        ),
        "notes": "CARD definition for the 16S rRNA methyltransferase G1405 subfamily.",
    },
    "ARO:3004272": {
        "reference": "ARO:3004272",
        "snippet": (
            "Methyltransferases that methylate the A1408 position of 16S rRNA, "
            "which is part of an aminoglycoside binding site."
        ),
        "notes": "CARD definition for the 16S rRNA methyltransferase A1408 subfamily.",
    },
}

G1405_METHYLATION_EVIDENCE = {
    "reference": "RHEA:42772",
    "snippet": (
        "guanosine(1405) in 16S rRNA + S-adenosyl-L-methionine = "
        "N(7)-methylguanosine(1405) in 16S rRNA + "
        "S-adenosyl-L-homocysteine"
    ),
    "notes": "Rhea reaction for 16S rRNA G1405 N7-methylation.",
}

A1408_METHYLATION_EVIDENCE = {
    "reference": "RHEA:42776",
    "snippet": (
        "adenosine(1408) in 16S rRNA + S-adenosyl-L-methionine = "
        "N(1)-methyladenosine(1408) in 16S rRNA + "
        "S-adenosyl-L-homocysteine + H(+)"
    ),
    "notes": "Rhea reaction for 16S rRNA A1408 N1-methylation.",
}

MECHANISM_NODES = [
    (
        "mech0",
        TARGET_ALTERATION_EVIDENCE,
        {
            "node_id": "mech0",
            "label": "antibiotic target alteration",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001001",
        },
    ),
    (
        "mech1",
        RIBOSOMAL_ALTERATION_EVIDENCE,
        {
            "node_id": "mech1",
            "label": "ribosomal alteration conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000211",
        },
    ),
]

DRUG_NODE = {
    "node_id": "drug0",
    "label": "aminoglycoside antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000016",
}

METHYLATION_NODES = {
    "ARO:3004271": {
        "node_id": "g1405_methylation",
        "label": "16S rRNA G1405 N7-methylation",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "RHEA:42772",
    },
    "ARO:3004272": {
        "node_id": "a1408_methylation",
        "label": "16S rRNA A1408 N1-methylation",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "RHEA:42776",
    },
}

METHYLATION_EVIDENCE = {
    "ARO:3004271": G1405_METHYLATION_EVIDENCE,
    "ARO:3004272": A1408_METHYLATION_EVIDENCE,
}

SUBFAMILY_RELATION_LABELS = {
    "ARO:3004271": "16S rRNA methyltransferase (G1405)",
    "ARO:3004272": "16S rRNA methyltransferase (A1408)",
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

DRUG_RELATION_OBJECT = "ARO:0000016"
DRUG_RELATION_LABEL = "aminoglycoside antibiotic"

REQUIRED_CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

LEGACY_METHYLATION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "methyltransferase"),
    ("methyltransferase", "RO:0002411", "methylated"),
    ("methylated", "RO:0002212", "decoding_site"),
    ("drug0", "RO:0002436", "decoding_site"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    subfamily_identifier: str

    @property
    def methylation_node_id(self) -> str:
        return str(METHYLATION_NODES[self.subfamily_identifier]["node_id"])


TARGETS = {
    "ARO:3000858": Target(
        identifier="ARO:3000858",
        filename="arma-aro3000858.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3000859": Target(
        identifier="ARO:3000859",
        filename="rmta-aro3000859.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3000860": Target(
        identifier="ARO:3000860",
        filename="rmtb-aro3000860.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3000861": Target(
        identifier="ARO:3000861",
        filename="rmtc-aro3000861.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3000862": Target(
        identifier="ARO:3000862",
        filename="sgm-aro3000862.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3002665": Target(
        identifier="ARO:3002665",
        filename="npma-aro3002665.yaml",
        subfamily_identifier="ARO:3004272",
    ),
    "ARO:3002666": Target(
        identifier="ARO:3002666",
        filename="rmtf-aro3002666.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3002667": Target(
        identifier="ARO:3002667",
        filename="rmtd-aro3002667.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3002668": Target(
        identifier="ARO:3002668",
        filename="rmtg-aro3002668.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3003198": Target(
        identifier="ARO:3003198",
        filename="rmth-aro3003198.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3004102": Target(
        identifier="ARO:3004102",
        filename="kamb-aro3004102.yaml",
        subfamily_identifier="ARO:3004272",
    ),
    "ARO:3004677": Target(
        identifier="ARO:3004677",
        filename="rmtd2-aro3004677.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3004678": Target(
        identifier="ARO:3004678",
        filename="rmte-aro3004678.yaml",
        subfamily_identifier="ARO:3004271",
    ),
    "ARO:3004679": Target(
        identifier="ARO:3004679",
        filename="rmte2-aro3004679.yaml",
        subfamily_identifier="ARO:3004271",
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _subfamily_evidence(target: Target) -> dict[str, str]:
    return copy.deepcopy(SUBFAMILY_EVIDENCE[target.subfamily_identifier])


def _drug_evidence(target: Target) -> dict[str, str]:
    subfamily_label = SUBFAMILY_RELATION_LABELS[target.subfamily_identifier]
    return {
        "reference": target.subfamily_identifier,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            f"ARO drug-class relationship on {target.subfamily_identifier} "
            f"({subfamily_label}); modeled here as a "
            "determinant-to-aminoglycoside-antibiotic edge and inherited by "
            "the acquired 16S rRNA methyltransferase leaf."
        ),
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item["snippet"],
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


def _methylation_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    return {
        ("determinant", "RO:0002327", target.methylation_node_id),
        (target.methylation_node_id, "RO:0002411", "resistance"),
    }


def _canonical_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    return REQUIRED_CORE_EDGE_KEYS | _methylation_edge_keys(target)


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    return _canonical_edge_keys(target) | LEGACY_METHYLATION_EDGE_KEYS


def _validate_methylation_edges(
    found: set[tuple[str, str, str]],
    target: Target,
) -> None:
    has_exact = _methylation_edge_keys(target) <= found
    has_legacy = LEGACY_METHYLATION_EDGE_KEYS <= found
    if not has_exact and not has_legacy:
        raise ValueError(
            f"{target.identifier}: missing both exact and legacy methylation edges"
        )


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "mech1", "drug0", "resistance"}
    if target.methylation_node_id in nodes:
        required_nodes.add(target.methylation_node_id)
    else:
        required_nodes.update({"methyltransferase", "methylated", "decoding_site"})

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges(target):
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(REQUIRED_CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")
    _validate_methylation_edges(found, target)


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        *(copy.deepcopy(node) for _, _, node in MECHANISM_NODES),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(METHYLATION_NODES[target.subfamily_identifier]),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    subfamily_evidence = _subfamily_evidence(target)
    methylation_evidence = METHYLATION_EVIDENCE[target.subfamily_identifier]
    drug_evidence = (target_evidence, subfamily_evidence, _drug_evidence(target))
    edges: list[dict[str, Any]] = []

    for node_id, mechanism_evidence, node in MECHANISM_NODES:
        edge_evidence = (target_evidence, subfamily_evidence, mechanism_evidence)
        edges.extend(
            [
                _edge(
                    "determinant",
                    "participates in (resistance mechanism)",
                    "RO:0000056",
                    node_id,
                    f"The ARO hierarchy classifies this methyltransferase under {node['label']}.",
                    edge_evidence,
                ),
                _edge(
                    node_id,
                    "causally upstream of",
                    "RO:0002411",
                    "resistance",
                    f"The inherited {node['label']} mechanism links 16S rRNA methylation to resistance.",
                    edge_evidence,
                ),
            ]
        )

    methylation_node = METHYLATION_NODES[target.subfamily_identifier]
    methylation_node_id = str(methylation_node["node_id"])
    edges.extend(
        [
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    "ARO links this determinant to aminoglycoside resistance by "
                    "16S rRNA target-site methylation."
                ),
                drug_evidence + (methylation_evidence, RIBOSOMAL_ALTERATION_EVIDENCE),
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "The ARO hierarchy links this determinant to aminoglycoside antibiotics.",
                drug_evidence + (RIBOSOMAL_ALTERATION_EVIDENCE,),
            ),
            _edge(
                "determinant",
                f"enables ({methylation_node['label']})",
                "RO:0002327",
                methylation_node_id,
                f"ARO assigns this enzyme to the {methylation_node['label']} subfamily.",
                (target_evidence, subfamily_evidence, methylation_evidence),
            ),
            _edge(
                methylation_node_id,
                "causally upstream of (blocks aminoglycoside binding)",
                "RO:0002411",
                "resistance",
                (
                    f"{methylation_node['label']} modifies the 16S rRNA "
                    "aminoglycoside binding site and supports resistance."
                ),
                (
                    target_evidence,
                    subfamily_evidence,
                    methylation_evidence,
                    RIBOSOMAL_ALTERATION_EVIDENCE,
                ),
            ),
        ]
    )
    return edges


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next(
        (item for item in graphs if item.get("graph_id") in {"resistance", "resistance-draft"}),
        None,
    )
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["graph_id"] = "resistance"
    graph["title"] = f"{record['label']} → 16S rRNA methylation → aminoglycoside resistance"
    graph["description"] = (
        "Conservative graph for an acquired 16S rRNA methyltransferase. The "
        "graph keeps the inherited ARO target-alteration, ribosomal-alteration, "
        "and aminoglycoside drug-class routes and replaces the former generic "
        "decoding-site methylation chain with the exact Rhea reaction matching "
        f"the {SUBFAMILY_RELATION_LABELS[target.subfamily_identifier]} parent."
    )
    graph["nodes"] = _canonical_nodes(graph, target)
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def _promote_to_reviewed(text: str) -> str:
    return re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED", text, count=1, flags=re.M)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an acquired 16S rRNA methyltransferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases and record.get("mapping_status") == "REVIEWED":
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _promote_to_reviewed(out)
    if HISTORY_ACTION not in out:
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
        help="ARO directory or one of the fourteen target YAML files",
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
