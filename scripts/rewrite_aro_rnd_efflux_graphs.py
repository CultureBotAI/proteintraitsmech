#!/usr/bin/env python3
"""Rewrite RND efflux complex and subunit ARO graphs.

The RND complex records already carry the RND domain/fold/efflux skeleton but
their edges lack descriptions and second references. The RND subunit records
carry a more specific tripartite-pump skeleton with one unconnected binding
pocket node; this updater drops that orphan and keeps the supported path:

    subunit → local tripartite RND pump complex → antibiotic export

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

HISTORY_ACTION = "Completed RND efflux complex and subunit causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

EFFLUX_SUBUNIT_EVIDENCE = {
    "reference": "ARO:3000748",
    "snippet": "Subunits of efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump subunits.",
}

RND_EVIDENCE = {
    "reference": "ARO:0010004",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Resistance-nodulation-division (RND) proteins are found in both "
        "prokaryotic and eukaryotic cells and have diverse substrate "
        "specificities and physiological roles."
    ),
    "notes": "CARD definition for RND antibiotic efflux pumps.",
}

RND_TRANSPORT_EVIDENCE = {
    "reference": "PMID:16915237",
    "snippet": (
        "The structures indicate that drugs are exported by a three-step "
        "functionally rotating mechanism in which substrates undergo ordered "
        "binding change."
    ),
    "notes": "Evidence for RND pump-mediated drug export.",
}

RND_COMPLEX_EVIDENCE = {
    "reference": "PMID:16915237",
    "snippet": (
        "AcrB is a principal multidrug efflux transporter in Escherichia coli "
        "that cooperates with an outer-membrane channel, TolC, and a "
        "membrane-fusion protein, AcrA."
    ),
    "notes": "Evidence for a tripartite RND pump architecture.",
}

RND_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF00873",
    "snippet": "AcrB/AcrD/AcrF family",
    "notes": "Pfam family for RND transporter domains.",
}

RND_FOLD_EVIDENCE = {
    "reference": "CATH:3.30.70.1430",
    "snippet": "Multidrug efflux transporter AcrB pore domain",
    "notes": "CATH fold for the AcrB pore domain.",
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

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

RND_DOMAIN_NODE = {
    "node_id": "domain",
    "label": "RND transporter domain (AcrB/AcrD/AcrF family)",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00873",
    "description": "Transporter domain used by RND antibiotic efflux pumps.",
}

RND_FOLD_NODE = {
    "node_id": "fold",
    "label": "AcrB pore-domain fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.30.70.1430",
    "description": "Pore-domain fold used by RND antibiotic efflux pumps.",
}

PUMP_COMPLEX_NODE = {
    "node_id": "pump_complex",
    "label": "tripartite RND efflux complex",
    "node_type": "STATE",
    "description": (
        "Local state for a complete RND efflux pump containing an inner-membrane "
        "RND transporter, a membrane-fusion protein or periplasmic adaptor, and "
        "an outer-membrane channel."
    ),
}

EXPORT_NODE = {
    "node_id": "export",
    "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1990961",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    is_subunit: bool


COMPLEX_TARGETS: tuple[Target, ...] = (
    Target(
        identifier="ARO:0010004",
        filename="resistance-nodulation-cell-division-rnd-antibiotic-efflux-pump-aro0010004.yaml",
        is_subunit=False,
    ),
    Target(
        identifier="ARO:3000770",
        filename="adeabc-aro3000770.yaml",
        is_subunit=False,
    ),
)

SUBUNIT_TARGETS: tuple[Target, ...] = (
    Target("ARO:3000207", "acra-aro3000207.yaml", True),
    Target("ARO:3000216", "acrb-aro3000216.yaml", True),
    Target("ARO:3000499", "acre-aro3000499.yaml", True),
    Target("ARO:3000502", "acrf-aro3000502.yaml", True),
    Target("ARO:3000774", "adea-aro3000774.yaml", True),
    Target("ARO:3000775", "adeb-aro3000775.yaml", True),
    Target("ARO:3003811", "adec-aro3003811.yaml", True),
    Target("ARO:3000777", "adef-aro3000777.yaml", True),
    Target("ARO:3000778", "adeg-aro3000778.yaml", True),
    Target("ARO:3000779", "adeh-aro3000779.yaml", True),
    Target("ARO:3000780", "adei-aro3000780.yaml", True),
    Target("ARO:3000781", "adej-aro3000781.yaml", True),
    Target("ARO:3000782", "adek-aro3000782.yaml", True),
    Target("ARO:3002982", "amra-aro3002982.yaml", True),
    Target("ARO:3002983", "amrb-aro3002983.yaml", True),
    Target("ARO:3004143", "axyx-aro3004143.yaml", True),
    Target("ARO:3004144", "axyy-aro3004144.yaml", True),
    Target("ARO:3003009", "ceoa-aro3003009.yaml", True),
)

TARGETS: tuple[Target, ...] = (
    SUBUNIT_TARGETS[0],
    SUBUNIT_TARGETS[1],
    SUBUNIT_TARGETS[2],
    SUBUNIT_TARGETS[3],
    COMPLEX_TARGETS[1],
    *SUBUNIT_TARGETS[4:],
    COMPLEX_TARGETS[0],
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
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
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


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _common_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return (
        _record_evidence(record),
        RND_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        RND_TRANSPORT_EVIDENCE,
    )


def _subunit_graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = _common_evidence(record)
    subunit_evidence = (
        _record_evidence(record),
        EFFLUX_SUBUNIT_EVIDENCE,
        RND_COMPLEX_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → tripartite RND efflux complex → resistance",
        "description": (
            "Curated resistance-causation graph for RND efflux-pump subunits. "
            "The determinant is modeled as part of a local tripartite RND pump "
            "complex that exports antibiotics from the cell."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PUMP_COMPLEX_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this RND efflux-pump subunit under the "
                "antibiotic efflux resistance mechanism.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting antibiotics "
                "out of the cell.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The subunit contributes to an RND efflux complex that pumps "
                "antibiotic out of the cell.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "pump_complex",
                "The determinant is a subunit of the modeled tripartite RND "
                "efflux pump.",
                *subunit_evidence,
            ),
            _edge(
                "pump_complex",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The complete tripartite RND pump exports antibiotics from the "
                "cell.",
                *common_evidence,
            ),
            _edge(
                "export",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic export lowers intracellular drug exposure and causes "
                "the modeled resistance phenotype.",
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                RND_TRANSPORT_EVIDENCE,
            ),
        ],
    }


def _complex_graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = _common_evidence(record)
    domain_evidence = (
        _record_evidence(record),
        RND_EVIDENCE,
        RND_DOMAIN_EVIDENCE,
        RND_TRANSPORT_EVIDENCE,
    )
    fold_evidence = (
        _record_evidence(record),
        RND_EVIDENCE,
        RND_FOLD_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → RND antibiotic efflux → resistance",
        "description": (
            "Curated resistance-causation graph for complete RND antibiotic "
            "efflux pumps. The graph links the RND transporter domain and AcrB "
            "pore-domain fold to the antibiotic efflux mechanism."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(RND_DOMAIN_NODE),
            copy.deepcopy(RND_FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this RND pump under the antibiotic efflux "
                "resistance mechanism.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting antibiotics "
                "out of the cell.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The RND pump confers resistance by exporting antibiotics from "
                "the cell.",
                *common_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The RND transporter domain is part of the modeled RND pump.",
                *domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The RND determinant includes a transporter that adopts the AcrB "
                "pore-domain fold.",
                *fold_evidence,
            ),
            _edge(
                "domain",
                "enables (proton-motive-force-driven drug efflux)",
                "RO:0002327",
                "mech0",
                "The RND transporter domain enables proton-motive-force-driven "
                "antibiotic efflux.",
                *domain_evidence,
            ),
        ],
    }


REQUIRED_NODES = {
    True: {"determinant", "mech0", "pump_complex", "export", "resistance"},
    False: {"determinant", "mech0", "domain", "fold", "resistance"},
}


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = sorted(REQUIRED_NODES[target.is_subunit] - node_ids)
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    graph = _subunit_graph(record) if target.is_subunit else _complex_graph(record)
    out = copy.deepcopy(record)
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an RND efflux target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one of the RND target YAML files",
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
