#!/usr/bin/env python3
"""Ground and complete the evgA efflux-activator ARO graph.

The evgA CARD definition names two concrete pump complexes, EmrKY-TolC and
MdtEF-TolC.  This updater replaces the generic pump placeholder with both
grounded pumps, grounds broad transcriptional activation to GO, adds pump-to-
efflux edges, and replaces stale AdeR archetype evidence with exact evgA and
pump evidence.

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

IDENTIFIER = "ARO:3000832"
FILENAME = "evga-aro3000832.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Replaced stale archetype evidence on the evgA efflux-activator graph, "
        "grounded its EmrKY-TolC and MdtEF-TolC pump nodes and transcriptional-"
        "activation node, and linked both pump complexes to antibiotic efflux"
    ),
    "llm_assisted": True,
}

EVGA_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "EvgA, when phosphorylated, is a positive regulator for efflux protein "
        "complexes emrKY and mdtEF. While usually phosphorylated in a EvgS "
        "dependent manner, it can be phosphorylated in the absence of EvgS when "
        "overexpressed."
    ),
    "notes": "CARD definition for the evgA efflux-pump activator.",
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

ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of emrKY and mdtEF transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation "
        "process because EvgA promotes emrKY and mdtEF pump-complex expression."
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


@dataclass(frozen=True)
class Pump:
    node_id: str
    label: str
    grounding: str
    activated_process: str
    snippet: str
    notes: str

    @property
    def evidence(self) -> dict[str, str]:
        return {
            "reference": self.grounding,
            "snippet": self.snippet,
            "notes": self.notes,
        }

    @property
    def node(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "node_type": "PROTEIN",
            "grounding": self.grounding,
            "description": f"Grounded to CARD's {self.label}, a pump activated by EvgA.",
        }


EMRKY_TOLC = Pump(
    node_id="emrky_tolc",
    label="EmrKY-TolC",
    grounding="ARO:3000373",
    activated_process="emrKY transcription",
    snippet=(
        "EmrKY is a homolog of EmrAB found in E. coli. Together with TolC, it is "
        "a tripartite multidrug transporter."
    ),
    notes="CARD definition for the EmrKY-TolC pump activated by EvgA.",
)

MDTEF_TOLC = Pump(
    node_id="mdtef_tolc",
    label="MdtEF-TolC",
    grounding="ARO:3000788",
    activated_process="mdtEF transcription",
    snippet=(
        "MdtEF-TolC is a multidrug efflux complex in Gram-negative bacteria, "
        "including E. coli. MdtE is the membrane fusion protein, MdtF is the "
        "inner membrane transporter, while TolC is the outer membrane channel."
    ),
    notes="CARD definition for the MdtEF-TolC pump activated by EvgA.",
)

PUMPS = (EMRKY_TOLC, MDTEF_TOLC)

PUMP_EFFLUX_EDGE_UPDATES = {
    pump.node_id: EdgeUpdate(
        predicate="enables (drug efflux)",
        predicate_id="RO:0002327",
        description=(
            f"{pump.label} is a multidrug pump whose EvgA-activated expression "
            "supplies antibiotic efflux."
        ),
        evidence=(EVGA_EVIDENCE, pump.evidence),
    )
    for pump in PUMPS
}

ACTIVATION_PUMP_EDGE_UPDATES = {
    pump.node_id: EdgeUpdate(
        predicate="positively regulates (raises pump expression)",
        predicate_id="RO:0002213",
        description=(
            f"Transcriptional activation raises {pump.activated_process} and "
            f"increases expression of {pump.label}."
        ),
        evidence=(EVGA_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE, pump.evidence),
    )
    for pump in PUMPS
}

EDGE_UPDATES = {
    ("determinant", "mech0"): EdgeUpdate(
        predicate="participates in (resistance mechanism)",
        predicate_id="RO:0000056",
        description=(
            "CARD classifies evgA under antibiotic efflux because phosphorylated "
            "EvgA positively regulates the emrKY and mdtEF efflux complexes."
        ),
        evidence=(EVGA_EVIDENCE, EMRKY_TOLC.evidence, MDTEF_TOLC.evidence),
    ),
    ("mech0", "resistance"): EdgeUpdate(
        predicate="causally upstream of",
        predicate_id="RO:0002411",
        description=(
            "The broad efflux mechanism represents elevated activity of the "
            "EvgA-regulated EmrKY-TolC and MdtEF-TolC multidrug pumps."
        ),
        evidence=(EVGA_EVIDENCE, EMRKY_TOLC.evidence, MDTEF_TOLC.evidence),
    ),
    ("determinant", "resistance"): EdgeUpdate(
        predicate="causally upstream of (confers resistance)",
        predicate_id="RO:0002411",
        description=(
            "Phosphorylated or overexpressed EvgA activates EmrKY-TolC and "
            "MdtEF-TolC expression, increasing antibiotic efflux."
        ),
        evidence=(EVGA_EVIDENCE, EMRKY_TOLC.evidence, MDTEF_TOLC.evidence),
    ),
    ("determinant", "activation"): EdgeUpdate(
        predicate="enables (activates pump transcription)",
        predicate_id="RO:0002327",
        description=(
            "EvgA participates in positive regulation of emrKY and mdtEF "
            "transcription."
        ),
        evidence=(EVGA_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE),
    ),
    **{
        ("activation", pump.node_id): update
        for pump, update in zip(PUMPS, ACTIVATION_PUMP_EDGE_UPDATES.values(), strict=True)
    },
    **{
        (pump.node_id, "mech0"): update
        for pump, update in zip(PUMPS, PUMP_EFFLUX_EDGE_UPDATES.values(), strict=True)
    },
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
    ("activation", EMRKY_TOLC.node_id),
    ("activation", MDTEF_TOLC.node_id),
    (EMRKY_TOLC.node_id, "mech0"),
    (MDTEF_TOLC.node_id, "mech0"),
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
        copy.deepcopy(EMRKY_TOLC.node),
        copy.deepcopy(MDTEF_TOLC.node),
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
        "Curated resistance-causation graph for evgA efflux-pump activation. The "
        "graph replaces stale archetype evidence, grounds the EmrKY-TolC and "
        "MdtEF-TolC efflux pumps, and links both pump complexes to antibiotic "
        "efflux."
    )
    _enrich_nodes(graph)
    graph["edges"] = _canonical_edges()
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not evgA: {record.get('identifier')}")
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or evgA YAML file")
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
