#!/usr/bin/env python3
"""Complete MexCD-OprJ graphs for type-A/type-B NfxB mutation records.

These two CARD records are scoped to the MexCD-OprJ pump in an NfxB-mutant
phenotype, not to the NfxB repressor itself.  Rewrite their stale drug-class
expanded RND skeletons to the supported complete-pump graph used by MexCD-OprJ.

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

HISTORY_ACTION = "Completed MexCD-OprJ NfxB-variant efflux graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
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

MEXCD_OPRJ_EVIDENCE = {
    "reference": "ARO:3000797",
    "snippet": (
        "MexCD-OprJ is a multidrug efflux protein expressed in the Gram-negative "
        "Pseudomonas aeruginosa. MexC is the membrane fusion protein; MexD is "
        "the inner membrane transporter; and OprJ is the outer membrane "
        "channel. MexAB-OprM is associated with resistance to fluoroquinolones, "
        "chloramphenicol, and macrolides. MexCD-OprJ is typically quiescent in "
        "wild-type cells, with expression following mutation of the nfxB gene "
        "that is divergently transcribed from the mexCD-oprJ operon and "
        "encodes a repressor of mexCD-oprJ expression. Expression of "
        "mexCD–oprJ is controlled by a single known regulator, the NfxB "
        "repressor encoded by the nfxB gene, which is transcribed divergently "
        "from the efflux genes."
    ),
    "notes": "CARD definition for the MexCD-OprJ efflux pump.",
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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3004061", "mexcd-oprj-with-type-a-nfxb-mutation-aro3004061.yaml"),
    Target("ARO:3004062", "mexcd-oprj-with-type-b-nfxb-mutation-aro3004062.yaml"),
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
        MEXCD_OPRJ_EVIDENCE,
        RND_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        RND_TRANSPORT_EVIDENCE,
    )


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = _common_evidence(record)
    domain_evidence = (
        _record_evidence(record),
        MEXCD_OPRJ_EVIDENCE,
        RND_EVIDENCE,
        RND_DOMAIN_EVIDENCE,
        RND_TRANSPORT_EVIDENCE,
    )
    fold_evidence = (
        _record_evidence(record),
        MEXCD_OPRJ_EVIDENCE,
        RND_EVIDENCE,
        RND_FOLD_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → MexCD-OprJ antibiotic efflux → resistance",
        "description": (
            "Curated resistance-causation graph for NfxB-mutant MexCD-OprJ "
            "efflux-pump records. The graph models the determinant as the "
            "MexCD-OprJ RND efflux pump in a resistance-conferring NfxB-mutant "
            "phenotype."
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
                "CARD classifies this NfxB-mutant MexCD-OprJ pump under the "
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
                "NfxB-mutant MexCD-OprJ confers resistance through RND-mediated "
                "antibiotic efflux.",
                *common_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The RND transporter domain is part of the modeled MexCD-OprJ pump.",
                *domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The modeled MexCD-OprJ pump includes a transporter that adopts "
                "the AcrB pore-domain fold.",
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


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a MexCD-OprJ NfxB-variant target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or a MexCD-OprJ NfxB-variant target YAML file",
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
