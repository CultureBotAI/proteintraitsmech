#!/usr/bin/env python3
"""Ground and complete Arl/Bae efflux-activator ARO graphs.

The four records handled here are positive efflux regulators that were seeded
from the AdeR archetype. This updater replaces the inherited AdeR evidence with
target-specific CARD evidence, grounds broad transcriptional activation to GO,
grounds the named NorA/MdtABC/AcrD pump nodes, and links those pumps to the
antibiotic-efflux mechanism.

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
        "Replaced AdeR archetype evidence in Arl/Bae efflux activators, "
        "grounded pump/transcription nodes, and linked pump expression to "
        "antibiotic efflux"
    ),
    "llm_assisted": True,
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for broad transcriptional activation.",
}

NORA_EVIDENCE = {
    "reference": "ARO:3000391",
    "snippet": (
        "NorA is a multidrug efflux pump in Staphylococcus aureus that confers "
        "resistance to fluoroquinolones and other structurally unrelated "
        "antibiotics like acriflavine."
    ),
    "notes": "CARD definition for the NorA efflux pump controlled by ArlRS.",
}

MDTABC_TOLC_EVIDENCE = {
    "reference": "ARO:3000787",
    "snippet": (
        "MdtABC-TolC is a multidrug efflux system in Gram-negative bacteria, "
        "including E. coli and Salmonella. MdtA is a membrane fusion protein; "
        "TolC is the outer membrane channel; MdtBC form a drug transporter."
    ),
    "notes": "CARD definition for an efflux system promoted by BaeR.",
}

ACRD_EVIDENCE = {
    "reference": "ARO:3000491",
    "snippet": (
        "AcrD is an aminoglycoside efflux pump expressed in E. coli. Its expression "
        "can be induced by indole, and is regulated by baeRS and cpxAR."
    ),
    "notes": "CARD definition for an efflux pump regulated by BaeSR.",
}

BAER_EVIDENCE = {
    "reference": "ARO:3000828",
    "snippet": (
        "BaeR is a response regulator that promotes the expression of MdtABC and "
        "AcrD efflux complexes."
    ),
    "notes": "CARD definition for the baeR response-regulator determinant.",
}

TARGET_EVIDENCE = {
    "ARO:3000838": (
        {
            "reference": "ARO:3000838",
            "snippet": (
                "ArlR is a response regulator that binds to the norA promoter to "
                "activate expression. ArlR must first be phosphorylated by ArlS."
            ),
            "notes": "CARD definition for the arlR response-regulator determinant.",
        },
    ),
    "ARO:3000547": (
        {
            "reference": "ARO:3000547",
            "snippet": (
                "ArlRS is a two-component regulatory system for NorA. ArlS "
                "phosphorylates ArlR to promote NorA expression."
            ),
            "notes": "CARD definition for the ArlRS two-component determinant.",
        },
    ),
    "ARO:3000828": (BAER_EVIDENCE,),
    "ARO:3000829": (
        {
            "reference": "ARO:3000829",
            "snippet": (
                "BaeS is a sensor kinase in the BaeSR regulatory system. While it "
                "phosphorylates BaeR to increase its activity, BaeS is not necessary "
                "for overexpressed BaeR to confer resistance."
            ),
            "notes": "CARD definition for the baeS sensor-kinase determinant.",
        },
        BAER_EVIDENCE,
    ),
}

NORA_NODE = {
    "node_id": "pump",
    "label": "NorA multidrug efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000391",
    "description": "Grounded to CARD's NorA multidrug efflux pump class.",
}

MDTABC_TOLC_NODE = {
    "node_id": "mdtabc_pump",
    "label": "MdtABC-TolC multidrug efflux system",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000787",
    "description": "Grounded to CARD's MdtABC-TolC multidrug efflux system class.",
}

ACRD_NODE = {
    "node_id": "acrd_pump",
    "label": "AcrD aminoglycoside efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000491",
    "description": "Grounded to CARD's AcrD aminoglycoside efflux pump class.",
}

PUMP_EVIDENCE = {
    "pump": NORA_EVIDENCE,
    "mdtabc_pump": MDTABC_TOLC_EVIDENCE,
    "acrd_pump": ACRD_EVIDENCE,
}


@dataclass(frozen=True)
class EdgeUpdate:
    predicate: str
    predicate_id: str
    description: str


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    activation_node: dict[str, str]
    pump_nodes: tuple[dict[str, str], ...]
    edge_updates: dict[tuple[str, str], EdgeUpdate]
    obsolete_edges: frozenset[tuple[str, str]] = frozenset()

    @property
    def pump_ids(self) -> tuple[str, ...]:
        return tuple(node["node_id"] for node in self.pump_nodes)

    @property
    def pump_id_set(self) -> set[str]:
        return set(self.pump_ids)

    @property
    def target_evidence(self) -> tuple[dict[str, str], ...]:
        return TARGET_EVIDENCE[self.identifier]

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


def _edge_updates(
    *,
    determinant_mechanism: str,
    mechanism_resistance: str,
    determinant_resistance: str,
    determinant_activation: str,
    activation_pump: dict[str, str],
    pump_mechanism: dict[str, str],
) -> dict[tuple[str, str], EdgeUpdate]:
    updates = {
        ("determinant", "mech0"): EdgeUpdate(
            predicate="participates in (resistance mechanism)",
            predicate_id="RO:0000056",
            description=determinant_mechanism,
        ),
        ("mech0", "resistance"): EdgeUpdate(
            predicate="causally upstream of",
            predicate_id="RO:0002411",
            description=mechanism_resistance,
        ),
        ("determinant", "resistance"): EdgeUpdate(
            predicate="causally upstream of (confers resistance)",
            predicate_id="RO:0002411",
            description=determinant_resistance,
        ),
        ("determinant", "activation"): EdgeUpdate(
            predicate="enables (activates efflux pump expression)",
            predicate_id="RO:0002327",
            description=determinant_activation,
        ),
    }
    for pump_id, description in activation_pump.items():
        updates[("activation", pump_id)] = EdgeUpdate(
            predicate="positively regulates (raises pump expression)",
            predicate_id="RO:0002213",
            description=description,
        )
    for pump_id, description in pump_mechanism.items():
        updates[(pump_id, "mech0")] = EdgeUpdate(
            predicate="enables (drug efflux)",
            predicate_id="RO:0002327",
            description=description,
        )
    return updates


NORA_ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of NorA transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation process "
        "because ArlRS promotes NorA expression."
    ),
}

BAE_ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of MdtABC/AcrD transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation process "
        "because BaeR promotes MdtABC and AcrD expression."
    ),
}

NORA_EDGE_UPDATES = _edge_updates(
    determinant_mechanism=(
        "CARD classifies this ArlRS regulator under antibiotic efflux because it "
        "promotes NorA expression."
    ),
    mechanism_resistance="The broad efflux mechanism represents NorA-driven drug export.",
    determinant_resistance=(
        "The ArlRS regulator promotes expression of the NorA pump, which confers "
        "fluoroquinolone resistance."
    ),
    determinant_activation=(
        "The ArlRS regulator participates in positive regulation of NorA expression."
    ),
    activation_pump={
        "pump": "ArlRS-dependent activation increases NorA expression.",
    },
    pump_mechanism={
        "pump": "NorA is the multidrug pump whose expression supplies antibiotic efflux.",
    },
)

BAE_EDGE_UPDATES = _edge_updates(
    determinant_mechanism=(
        "CARD classifies this BaeSR regulator under antibiotic efflux because BaeR "
        "promotes MdtABC and AcrD expression."
    ),
    mechanism_resistance=(
        "The broad efflux mechanism represents BaeSR-regulated MdtABC-TolC and AcrD "
        "drug export."
    ),
    determinant_resistance=(
        "The BaeSR regulatory component increases BaeR activity or efflux-gene "
        "expression, which drives efflux-mediated resistance."
    ),
    determinant_activation=(
        "The BaeSR regulator participates in positive regulation of MdtABC and AcrD "
        "expression."
    ),
    activation_pump={
        "mdtabc_pump": "BaeR-dependent activation increases MdtABC expression.",
        "acrd_pump": "BaeR-dependent activation increases AcrD expression.",
    },
    pump_mechanism={
        "mdtabc_pump": (
            "MdtABC-TolC is one multidrug efflux system promoted by BaeR."
        ),
        "acrd_pump": "AcrD is one efflux pump regulated by BaeSR.",
    },
)

TARGETS = {
    "ARO:3000838": Target(
        identifier="ARO:3000838",
        filename="arlr-aro3000838.yaml",
        activation_node=NORA_ACTIVATION_NODE,
        pump_nodes=(NORA_NODE,),
        edge_updates=NORA_EDGE_UPDATES,
    ),
    "ARO:3000547": Target(
        identifier="ARO:3000547",
        filename="arlrs-aro3000547.yaml",
        activation_node=NORA_ACTIVATION_NODE,
        pump_nodes=(NORA_NODE,),
        edge_updates=NORA_EDGE_UPDATES,
    ),
    "ARO:3000828": Target(
        identifier="ARO:3000828",
        filename="baer-aro3000828.yaml",
        activation_node=BAE_ACTIVATION_NODE,
        pump_nodes=(MDTABC_TOLC_NODE, ACRD_NODE),
        edge_updates=BAE_EDGE_UPDATES,
        obsolete_edges=frozenset({("activation", "pump")}),
    ),
    "ARO:3000829": Target(
        identifier="ARO:3000829",
        filename="baes-aro3000829.yaml",
        activation_node=BAE_ACTIVATION_NODE,
        pump_nodes=(MDTABC_TOLC_NODE, ACRD_NODE),
        edge_updates=BAE_EDGE_UPDATES,
        obsolete_edges=frozenset({("activation", "pump")}),
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


def _edge_evidence(target: Target, subject: str, object_: str) -> list[dict[str, str]]:
    evidence = list(target.target_evidence)
    if object_ == "activation" or subject == "activation":
        evidence.append(GO_POSITIVE_TRANSCRIPTION_EVIDENCE)
    if object_ in target.pump_id_set:
        evidence.append(PUMP_EVIDENCE[object_])
    elif subject in target.pump_id_set:
        evidence.append(PUMP_EVIDENCE[subject])
    elif (subject, object_) in {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
    }:
        evidence.extend(PUMP_EVIDENCE[node_id] for node_id in target.pump_ids)
    return [copy.deepcopy(item) for item in evidence]


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found = {node.get("node_id") for node in nodes if isinstance(node, dict)}
    legal_pump_ids = target.pump_id_set | {"pump"}
    required = {"determinant", "mech0", "activation", "resistance"}
    missing = required - found
    if not found & legal_pump_ids:
        missing.add("pump")
    if missing:
        missing_ids = ", ".join(sorted(missing))
        msg = f"{target.identifier}: missing node(s): {missing_ids}"
        raise ValueError(msg)

    enriched_nodes = []
    inserted_pumps = False
    for node in nodes:
        node_id = node.get("node_id") if isinstance(node, dict) else None
        if node_id in legal_pump_ids:
            if not inserted_pumps:
                enriched_nodes.extend(copy.deepcopy(node) for node in target.pump_nodes)
                inserted_pumps = True
            continue
        if node_id == "activation":
            enriched_nodes.append(copy.deepcopy(target.activation_node))
            continue
        enriched_nodes.append(copy.deepcopy(node))
    graph["nodes"] = enriched_nodes


def _enrich_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.get("edges") or []
    allowed_edges = target.expected_edges | target.obsolete_edges
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in allowed_edges:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    graph["edges"] = [
        _ordered_edge(
            {
                "subject": subject,
                "predicate": update.predicate,
                "predicate_id": update.predicate_id,
                "object": object_,
                "description": update.description,
                "evidence": _edge_evidence(target, subject, object_),
            }
        )
        for (subject, object_), update in target.edge_updates.items()
    ]


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

    graph["description"] = (
        "Curated resistance-causation graph for target-specific activation of "
        "antibiotic efflux. The graph replaces the seeded AdeR archetype evidence "
        "with this record's own CARD evidence, grounds the named efflux pump and "
        "broad positive transcriptional regulation, and models pump expression as "
        "causally upstream of antibiotic efflux."
    )
    _enrich_nodes(graph, target)
    _enrich_edges(graph, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an Arl/Bae efflux activator target: {identifier}")
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
        help="ARO directory or one of the four Arl/Bae efflux-activator target YAML files",
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
