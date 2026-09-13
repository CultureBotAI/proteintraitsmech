#!/usr/bin/env python3
"""Complete tetracycline ribosomal-protection protein ARO graphs.

The Tet(M) graph carries Tet(M)-specific GTPase-domain nodes.  These records
share the same tetracycline target-protection mechanism, but keep the older
7-edge generic RPP topology.

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

HISTORY_ACTION = "Completed tetracycline RPP ribosome-displacement graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RPP_EVIDENCE = {
    "reference": "ARO:0000002",
    "snippet": (
        "A family of proteins known to bind to the 30S ribosomal subunit. "
        "This interaction prevents tetracycline and tetracycline derivatives "
        "from inhibiting ribosomal function."
    ),
    "notes": "CARD definition for tetracycline-resistant ribosomal protection proteins.",
}

TARGET_PROTEIN_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection proteins.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, "
        "which process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target protection.",
}

DONHOFER_BINDING_EVIDENCE = {
    "reference": "PMID:23027944",
    "snippet": (
        "Ribosome protection proteins (RPPs) confer tetracycline resistance by "
        "binding to the ribosome and chasing the drug from its binding site."
    ),
    "notes": "Dönhöfer et al. summarized tetracycline RPP target protection.",
}

DONHOFER_CONTACT_EVIDENCE = {
    "reference": "PMID:23027944",
    "snippet": (
        "Moreover, we observe direct interaction between domain IV of TetM and "
        "the tetracycline binding site and identify residues critical for "
        "conferring tetracycline resistance."
    ),
    "notes": "TetM cryo-EM support for direct contact with the tetracycline binding site.",
}

DONHOFER_RELEASE_EVIDENCE = {
    "reference": "PMID:23027944",
    "snippet": (
        "The current model for the mechanism of action of RPPs proposes that "
        "drug release is indirect and achieved via conformational changes "
        "within the drug-binding site induced upon binding of the RPP to the "
        "ribosome."
    ),
    "notes": (
        "Dönhöfer et al. record the earlier indirect-release model while their "
        "structure supports direct TetM domain-IV displacement."
    ),
}

TETRACYCLINE_RELATION_EVIDENCE = {
    "reference": "ARO:0000002",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000050 ! tetracycline antibiotic",
    "notes": (
        "Drug-class relation asserted on ARO:0000002 "
        "(tetracycline-resistant ribosomal protection protein) in the CARD/ARO "
        "release in data/raw/aro/aro.obo."
    ),
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies this determinant under antibiotic target protection.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "Tetracycline target protection dislodges the drug from the ribosome and restores growth.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Tetracycline RPP determinants confer resistance by protecting the ribosomal target.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts tetracycline-antibiotic resistance on the Tet RPP parent.",
    (
        "determinant",
        "enables (binds the ribosome)",
        "ribosome_binding",
    ): "RPP binding to the ribosome is the first step in tetracycline target protection.",
    (
        "drug0",
        "molecularly interacts with (occupies its binding site)",
        "tet_site",
    ): "Tetracycline occupies a ribosomal drug-binding site that RPPs clear.",
    (
        "ribosome_binding",
        "negatively regulates (chases the drug from the site)",
        "tet_site",
    ): "RPP binding displaces tetracycline from its ribosomal binding site.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:0000002", "tetracycline-resistant-ribosomal-protection-protein-aro0000002.yaml"),
    Target("ARO:3000190", "tet-o-aro3000190.yaml"),
    Target("ARO:3000191", "tet-q-aro3000191.yaml"),
    Target("ARO:3000192", "tet-s-aro3000192.yaml"),
    Target("ARO:3000193", "tet-t-aro3000193.yaml"),
    Target("ARO:3000194", "tet-w-aro3000194.yaml"),
    Target("ARO:3000195", "tetb-p-aro3000195.yaml"),
    Target("ARO:3000196", "tet-32-aro3000196.yaml"),
    Target("ARO:3000197", "tet-36-aro3000197.yaml"),
    Target("ARO:3000556", "tet-44-aro3000556.yaml"),
    Target("ARO:3002891", "streptomyces-rimosus-otr-a-aro3002891.yaml"),
    Target("ARO:3004442", "tet-w-n-w-aro3004442.yaml"),
    Target("ARO:3004576", "tet-61-aro3004576.yaml"),
    Target("ARO:3007119", "tet-o-32-o-aro3007119.yaml"),
    Target("ARO:3007120", "tet-o-m-o-aro3007120.yaml"),
    Target("ARO:3007121", "tet-o-w-aro3007121.yaml"),
    Target("ARO:3007122", "tet-o-w-32-o-aro3007122.yaml"),
    Target("ARO:3007123", "tet-o-w-o-aro3007123.yaml"),
    Target("ARO:3007124", "tet-w-32-o-aro3007124.yaml"),
    Target("ARO:3007127", "streptomyces-lividans-otr-a-aro3007127.yaml"),
)


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
    seen: set[tuple[str, str]] = set()
    for item in items:
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _own_evidence(record: dict[str, Any]) -> dict[str, str]:
    identifier = str(record["identifier"])
    label = str(record["label"])
    definition = str(record["definition"])
    return {
        "reference": identifier,
        "snippet": definition,
        "notes": f"CARD definition for {label}.",
    }


def _relation_evidence(record: dict[str, Any]) -> dict[str, str]:
    if record["identifier"] == "ARO:0000002":
        return {
            **TETRACYCLINE_RELATION_EVIDENCE,
            "notes": (
                "Asserted directly on ARO:0000002 "
                "(tetracycline-resistant ribosomal protection protein) in the "
                "CARD/ARO release in data/raw/aro/aro.obo."
            ),
        }

    return {
        **TETRACYCLINE_RELATION_EVIDENCE,
        "notes": (
            "Asserted on ARO:0000002 (tetracycline-resistant ribosomal "
            "protection protein), an is_a ancestor of this record's "
            f"{record['identifier']}; inherited by this variant. CARD/ARO "
            "release in data/raw/aro/aro.obo."
        ),
    }


def _parent_evidence(record: dict[str, Any]) -> list[dict[str, str]]:
    if record["identifier"] == "ARO:0000002":
        return []
    return [RPP_EVIDENCE]


def _existing_evidence(
    record: dict[str, Any], existing: list[dict[str, str]]
) -> list[dict[str, str]]:
    if record["identifier"] != "ARO:0000002":
        return existing
    return [
        item
        for item in existing
        if not (
            item.get("reference") == RPP_EVIDENCE["reference"]
            and item.get("snippet") == RPP_EVIDENCE["snippet"]
        )
    ]


def _evidence_for_edge(
    key: tuple[str, str, str],
    existing: list[dict[str, str]],
    record: dict[str, Any],
) -> list[dict[str, str]]:
    own = _own_evidence(record)
    parent = _parent_evidence(record)
    relation = _relation_evidence(record)

    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [
                own,
                *parent,
                TARGET_PROTEIN_EVIDENCE,
                TARGET_PROTECTION_EVIDENCE,
                DONHOFER_BINDING_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                own,
                *parent,
                TARGET_PROTEIN_EVIDENCE,
                TARGET_PROTECTION_EVIDENCE,
                DONHOFER_BINDING_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                own,
                *parent,
                TARGET_PROTEIN_EVIDENCE,
                TARGET_PROTECTION_EVIDENCE,
                DONHOFER_BINDING_EVIDENCE,
                DONHOFER_CONTACT_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [relation, own, *parent, DONHOFER_BINDING_EVIDENCE]
        case ("determinant", "enables (binds the ribosome)", "ribosome_binding"):
            extra = [own, *parent, DONHOFER_BINDING_EVIDENCE]
        case (
            "drug0",
            "molecularly interacts with (occupies its binding site)",
            "tet_site",
        ):
            extra = [own, *parent, DONHOFER_BINDING_EVIDENCE, DONHOFER_CONTACT_EVIDENCE]
        case (
            "ribosome_binding",
            "negatively regulates (chases the drug from the site)",
            "tet_site",
        ):
            extra = [
                *parent,
                TARGET_PROTEIN_EVIDENCE,
                TARGET_PROTECTION_EVIDENCE,
                DONHOFER_CONTACT_EVIDENCE,
                DONHOFER_RELEASE_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")

    return _unique_evidence(*_existing_evidence(record, existing), *extra)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    identifier = record.get("identifier")
    if identifier != target.identifier:
        raise ValueError(f"{target.filename}: expected {target.identifier}, found {identifier}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = f"{record['label']} → ribosomal target protection → tetracycline resistance"
    graph["description"] = (
        "Curated resistance-causation graph for tetracycline ribosomal "
        "protection proteins, which bind the ribosome and displace "
        "tetracycline from its ribosomal binding site."
    )

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(key, _dicts(edge.get("evidence")), record)
        seen.add(key)

    missing = sorted(set(EDGE_DESCRIPTIONS) - seen)
    if missing:
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, target: Target) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def run(apply: bool) -> tuple[int, int]:
    changed = 0
    enriched = 0
    for target in TARGETS:
        path = ARO_DIR / target.filename
        before = path.read_text(encoding="utf-8")
        after, did_change = enrich_text(before, target)
        if did_change:
            print(f"  {'wrote' if apply else 'would write'} {path}")
            changed += 1
            if apply:
                path.write_text(after, encoding="utf-8")
        else:
            enriched += 1
    return changed, enriched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args()

    changed, enriched = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {enriched}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
