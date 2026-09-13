#!/usr/bin/env python3
"""Ground and complete Acinetobacter Ade efflux-regulator ARO graphs.

The four records handled here are regulatory routes into Acinetobacter RND
efflux pumps: adeL mutations overexpress AdeFGH, adeN inactivation derepresses
AdeIJK, and the AdeRS pair activates AdeABC expression. This updater replaces
the inherited AcrR/AdeR archetype evidence with each record's own CARD
definition, grounds the named Ade pumps and broad transcriptional-regulation
processes, removes obsolete wild-type role edges from loss-of-repression
graphs, and links each pump node to antibiotic efflux.

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
        "Replaced archetype Ade regulator evidence with exact ARO evidence, grounded "
        "Ade pump/transcription nodes, and linked pump expression to antibiotic efflux"
    ),
    "llm_assisted": True,
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for broad transcriptional repression.",
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for broad transcriptional activation.",
}

ADEFGH_EVIDENCE = {
    "reference": "ARO:3000771",
    "snippet": (
        "AdeFGH is a RND multidrug efflux pump expressed in Acinetobacter baumannii. "
        "It confers resistance to fluoroquinolone, tetracycline, tigecycline, "
        "chloramphenicol, clindamycin, trimethoprim, and sulfamethoxazole."
    ),
    "notes": "CARD definition for the AdeFGH efflux pump controlled by AdeL.",
}

ADEIJK_EVIDENCE = {
    "reference": "ARO:3000772",
    "snippet": (
        "AdeIJK is a RND multidrug efflux pump expressed in Acinetobacter baumannii. "
        "It contributes to resistance for beta-lactams, chloramphenicol, tetracycline, "
        "erythromycin, lincosamides, fluoroquinolone, fusidic acid, novobiocin, "
        "rifampicin, trimethoprim, acridine, pyronine, and safranin."
    ),
    "notes": "CARD definition for the AdeIJK efflux pump repressed by AdeN.",
}

ADEABC_EVIDENCE = {
    "reference": "ARO:3000770",
    "snippet": (
        "AdeABC is an RND multidrug efflux system in Acinetobacter species, notably "
        "A. baunmannii. AdeA is a membrane fusion protein, AdeB is the inner membrane "
        "transporter, and AdeC is the outer membrane factor. It confers resistance to "
        "tigecycline."
    ),
    "notes": "CARD definition for the AdeABC efflux pump controlled by AdeRS.",
}

TARGET_EVIDENCE = {
    "ARO:3000620": {
        "reference": "ARO:3000620",
        "snippet": (
            "AdeL is a regulator of AdeFGH in Acinetobacter baumannii. AdeL mutations "
            "are associated with AdeFGH overexpression and multidrug resistance."
        ),
        "notes": "CARD definition for the adeL regulatory resistance determinant.",
    },
    "ARO:3000559": {
        "reference": "ARO:3000559",
        "snippet": (
            "AdeN is a repressor of AdeIJK, a RND-type efflux pump in Acinetobacter "
            "baumannii. Its inactivation increases expression of AdeJ."
        ),
        "notes": "CARD definition for the adeN repressor resistance determinant.",
    },
    "ARO:3000553": {
        "reference": "ARO:3000553",
        "snippet": "AdeR is a positive regulator of AdeABC efflux system.",
        "notes": "CARD definition for the adeR response-regulator determinant.",
    },
    "ARO:3000549": {
        "reference": "ARO:3000549",
        "snippet": (
            "AdeS is a sensor kinase in the AdeRS regulatory system of AdeABC. It is "
            "essential for AdeABC expression."
        ),
        "notes": "CARD definition for the adeS sensor-kinase determinant.",
    },
}

ADEFGH_NODE = {
    "node_id": "pump",
    "label": "AdeFGH RND multidrug efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000771",
    "description": "Grounded to CARD's AdeFGH RND multidrug efflux pump class.",
}

ADEIJK_NODE = {
    "node_id": "pump",
    "label": "AdeIJK RND multidrug efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000772",
    "description": "Grounded to CARD's AdeIJK RND multidrug efflux pump class.",
}

ADEABC_NODE = {
    "node_id": "pump",
    "label": "AdeABC RND multidrug efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000770",
    "description": "Grounded to CARD's AdeABC RND multidrug efflux pump class.",
}

ADEFGH_OVEREXPRESSION_NODE = {
    "node_id": "overexpression",
    "label": "AdeFGH overexpression",
    "node_type": "STATE",
    "description": (
        "Local state representing AdeFGH overexpression associated with adeL "
        "mutations."
    ),
}

ADEIJK_REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of AdeIJK transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional repression process "
        "because AdeN represses AdeIJK expression."
    ),
}

ADEABC_ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of AdeABC transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation process "
        "because AdeRS is essential for AdeABC expression."
    ),
}

PUMP_EFFLUX_EDGE = {
    "subject": "pump",
    "predicate": "enables (drug efflux)",
    "predicate_id": "RO:0002327",
    "object": "mech0",
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
    old_regulatory_node_id: str
    regulatory_node: dict[str, str]
    pump_node: dict[str, str]
    pump_evidence: dict[str, str]
    transcription_evidence: dict[str, str] | None
    obsolete_edges: set[tuple[str, str, str]]
    edge_updates: dict[tuple[str, str], EdgeUpdate]

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


ADEL_EDGE_UPDATES = {
    ("determinant", "mech0"): EdgeUpdate(
        predicate="participates in (resistance mechanism)",
        predicate_id="RO:0000056",
        description=(
            "CARD classifies adeL under antibiotic efflux because adeL mutations are "
            "associated with overexpression of the AdeFGH efflux pump."
        ),
    ),
    ("mech0", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "The broad efflux mechanism represents overexpressed AdeFGH exporting "
            "antibiotics."
        ),
    ),
    ("determinant", "resistance"): EdgeUpdate(
        predicate="causally upstream of (confers resistance)",
        predicate_id="RO:0002411",
        description=(
            "The adeL mutation class is associated with AdeFGH overexpression and "
            "multidrug resistance."
        ),
    ),
    ("determinant", "overexpression"): EdgeUpdate(
        predicate="causally upstream of (raises AdeFGH expression)",
        predicate_id="RO:0002411",
        description=(
            "The local overexpression state is the regulatory change linked to adeL "
            "mutations."
        ),
    ),
    ("overexpression", "pump"): EdgeUpdate(
        predicate="positively regulates (raises pump expression)",
        predicate_id="RO:0002213",
        description="AdeFGH overexpression increases abundance of the AdeFGH pump.",
    ),
    ("pump", "mech0"): EdgeUpdate(
        predicate="enables (drug efflux)",
        predicate_id="RO:0002327",
        description="AdeFGH is the RND pump whose overexpression supplies antibiotic efflux.",
    ),
}

ADEN_EDGE_UPDATES = {
    ("determinant", "mech0"): EdgeUpdate(
        predicate="participates in (resistance mechanism)",
        predicate_id="RO:0000056",
        description=(
            "CARD classifies adeN under antibiotic efflux because AdeN inactivation "
            "increases AdeIJK expression."
        ),
    ),
    ("mech0", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "The broad efflux mechanism represents derepressed AdeIJK exporting "
            "antibiotics."
        ),
    ),
    ("determinant", "resistance"): EdgeUpdate(
        predicate="causally upstream of (confers resistance)",
        predicate_id="RO:0002411",
        description=(
            "AdeN inactivation derepresses AdeIJK, increasing efflux-pump expression "
            "and causing resistance."
        ),
    ),
    ("repression", "pump"): EdgeUpdate(
        predicate="negatively regulates (holds pump expression down)",
        predicate_id="RO:0002212",
        description="Normal AdeN-dependent transcriptional repression keeps AdeIJK expression low.",
    ),
    ("determinant", "repression"): EdgeUpdate(
        predicate="negatively regulates (mutation lifts the repression)",
        predicate_id="RO:0002212",
        description=(
            "Resistance-conferring adeN inactivation is represented as loss of normal "
            "AdeIJK repression."
        ),
    ),
    ("pump", "mech0"): EdgeUpdate(
        predicate="enables (drug efflux)",
        predicate_id="RO:0002327",
        description="AdeIJK is the RND pump whose derepressed expression supplies antibiotic efflux.",
    ),
}

ADE_RS_EDGE_UPDATES = {
    ("determinant", "mech0"): EdgeUpdate(
        predicate="participates in (resistance mechanism)",
        predicate_id="RO:0000056",
        description=(
            "CARD classifies this AdeRS component under antibiotic efflux because the "
            "system activates AdeABC expression."
        ),
    ),
    ("mech0", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "The broad efflux mechanism represents AdeABC expression driving drug "
            "export."
        ),
    ),
    ("determinant", "resistance"): EdgeUpdate(
        predicate="causally upstream of (confers resistance)",
        predicate_id="RO:0002411",
        description=(
            "The AdeRS regulatory component supports AdeABC expression, which drives "
            "efflux-mediated resistance."
        ),
    ),
    ("determinant", "activation"): EdgeUpdate(
        predicate="enables (activates the pump operon)",
        predicate_id="RO:0002327",
        description=(
            "This AdeRS determinant participates in positive regulation of AdeABC "
            "expression."
        ),
    ),
    ("activation", "pump"): EdgeUpdate(
        predicate="positively regulates (raises pump expression)",
        predicate_id="RO:0002213",
        description="AdeRS-dependent activation increases AdeABC expression.",
    ),
    ("pump", "mech0"): EdgeUpdate(
        predicate="enables (drug efflux)",
        predicate_id="RO:0002327",
        description="AdeABC is the RND pump whose expression supplies antibiotic efflux.",
    ),
}

TARGETS = {
    "ARO:3000620": Target(
        identifier="ARO:3000620",
        filename="adel-aro3000620.yaml",
        old_regulatory_node_id="repression",
        regulatory_node=ADEFGH_OVEREXPRESSION_NODE,
        pump_node=ADEFGH_NODE,
        pump_evidence=ADEFGH_EVIDENCE,
        transcription_evidence=None,
        obsolete_edges={
            ("determinant", "RO:0002327", "overexpression"),
        },
        edge_updates=ADEL_EDGE_UPDATES,
    ),
    "ARO:3000559": Target(
        identifier="ARO:3000559",
        filename="aden-aro3000559.yaml",
        old_regulatory_node_id="repression",
        regulatory_node=ADEIJK_REPRESSION_NODE,
        pump_node=ADEIJK_NODE,
        pump_evidence=ADEIJK_EVIDENCE,
        transcription_evidence=GO_NEGATIVE_TRANSCRIPTION_EVIDENCE,
        obsolete_edges={
            ("determinant", "RO:0002327", "repression"),
        },
        edge_updates=ADEN_EDGE_UPDATES,
    ),
    "ARO:3000553": Target(
        identifier="ARO:3000553",
        filename="ader-aro3000553.yaml",
        old_regulatory_node_id="activation",
        regulatory_node=ADEABC_ACTIVATION_NODE,
        pump_node=ADEABC_NODE,
        pump_evidence=ADEABC_EVIDENCE,
        transcription_evidence=GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
        obsolete_edges=set(),
        edge_updates=ADE_RS_EDGE_UPDATES,
    ),
    "ARO:3000549": Target(
        identifier="ARO:3000549",
        filename="ades-aro3000549.yaml",
        old_regulatory_node_id="activation",
        regulatory_node=ADEABC_ACTIVATION_NODE,
        pump_node=ADEABC_NODE,
        pump_evidence=ADEABC_EVIDENCE,
        transcription_evidence=GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
        obsolete_edges=set(),
        edge_updates=ADE_RS_EDGE_UPDATES,
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


def _edge_evidence(target: Target, key: tuple[str, str]) -> list[dict[str, str]]:
    evidence = [copy.deepcopy(TARGET_EVIDENCE[target.identifier])]
    if key in {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "overexpression"),
        ("repression", "pump"),
        ("overexpression", "pump"),
        ("activation", "pump"),
        ("pump", "mech0"),
    }:
        evidence.append(copy.deepcopy(target.pump_evidence))
    if key in {
        ("determinant", "repression"),
        ("repression", "pump"),
        ("determinant", "activation"),
        ("activation", "pump"),
    } and target.transcription_evidence is not None:
        evidence.append(copy.deepcopy(target.transcription_evidence))
    return evidence


def _rewrite_regulatory_node_references(
    edge: dict[str, Any], target: Target
) -> dict[str, Any]:
    out = copy.deepcopy(edge)
    regulatory_node_id = target.regulatory_node["node_id"]
    if out.get("subject") == target.old_regulatory_node_id:
        out["subject"] = regulatory_node_id
    if out.get("object") == target.old_regulatory_node_id:
        out["object"] = regulatory_node_id
    return out


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id == "pump":
            nodes[index] = copy.deepcopy(target.pump_node)
            found.add("pump")
        elif node_id in {
            target.old_regulatory_node_id,
            target.regulatory_node["node_id"],
        }:
            nodes[index] = copy.deepcopy(target.regulatory_node)
            found.add(target.old_regulatory_node_id)

    missing = sorted({"pump", target.old_regulatory_node_id} - found)
    if missing:
        missing_ids = ", ".join(missing)
        msg = f"{target.identifier}: missing node(s): {missing_ids}"
        raise ValueError(msg)


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

    _enrich_nodes(graph, target)

    edges = [
        _rewrite_regulatory_node_references(edge, target)
        for edge in graph.get("edges", [])
    ]
    if not any(_edge_key(edge) == ("pump", "mech0") for edge in edges):
        edges.append(copy.deepcopy(PUMP_EFFLUX_EDGE))

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in edges:
        if _full_edge_key(edge) in target.obsolete_edges:
            continue

        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        edge_update = target.edge_updates.get(key)
        if edge_update is None:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)

        edge["predicate"] = edge_update.predicate
        edge["predicate_id"] = edge_update.predicate_id
        edge["description"] = edge_update.description
        edge["evidence"] = _edge_evidence(target, key)
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(target.expected_edges - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    graph["edges"] = enriched_edges
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an Ade efflux-regulator target: {identifier}")
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
        help="ARO directory or one of the four Ade efflux-regulator target YAML files",
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
