from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_van_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_van_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3004255": "vanJ membrane protein",
    "ARO:3002914": "vanJ",
    "ARO:3002915": "vanK",
    "ARO:3003727": "vanK gene in vanI cluster",
}

DEFINITIONS = {
    "ARO:3004255": "vanJ and vanJ homologue proteins confer resistance to teicoplanin.",
    "ARO:3002914": (
        "vanJ is a novel membrane protein that confers resistance to teicoplanin and its "
        "derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate "
        "during cell wall biosynthesis."
    ),
    "ARO:3002915": R.VANK_PARENT_EVIDENCE["snippet"],
    "ARO:3003727": (
        "Also known as vanKI, is a peptidoglycan bridge formation protein also known as "
        "FemAB that is part of the vanI glycopeptide resistance gene cluster."
    ),
}


def _edge(
    subject: str,
    object_: str,
    predicate: str = "causally upstream of",
    predicate_id: str = "RO:0002411",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:3002914",
                "snippet": DEFINITIONS["ARO:3002914"],
            }
        ],
    }


def _record(identifier: str = "ARO:3002914") -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": LABELS[identifier],
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000213",
        },
        {
            "node_id": "drug0",
            "label": "glycopeptide antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000081",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    edges = [
        _edge("determinant", "mech0", "participates in", "RO:0000056"),
        _edge("mech0", "resistance"),
        _edge("determinant", "resistance"),
        _edge("determinant", "drug0", "confers resistance to", "ARO:2000001"),
    ]

    if target.side_path == "vanj_recycling":
        nodes.insert(
            3,
            {
                "node_id": "upp_recycling",
                "label": "undecaprenol pyrophosphate recycling",
                "node_type": "MOLECULAR_FUNCTION",
                "description": "Ungrounded.",
            },
        )
        nodes.insert(
            4,
            {
                "node_id": "wall",
                "label": "cell wall biosynthesis",
                "node_type": "BIOLOGICAL_PROCESS",
                "description": "Ungrounded.",
            },
        )
        edges.extend(
            [
                _edge("determinant", "upp_recycling", "enables", "RO:0002327"),
                _edge("upp_recycling", "wall", "part of", "BFO:0000050"),
            ]
        )

    if identifier == "ARO:3002915":
        nodes.extend(
            [
                {
                    "node_id": "crossbridge_transfer",
                    "label": "cross-bridge amino acid addition",
                    "node_type": "MOLECULAR_FUNCTION",
                },
                {
                    "node_id": "stem_pentapeptide",
                    "label": "stem pentapeptide of cell wall precursors",
                    "node_type": "CHEMICAL",
                },
            ]
        )
        edges.extend(
            [
                _edge("determinant", "crossbridge_transfer", "enables", "RO:0002327"),
                _edge("crossbridge_transfer", "stem_pentapeptide", "has input", "RO:0002233"),
            ]
        )

    if identifier == "ARO:3004255":
        nodes.append(
            {
                "node_id": "vanj_record",
                "label": "vanJ",
                "node_type": "PROTEIN",
                "grounding": "ARO:3002914",
            }
        )
        edges.append(_edge("determinant", "vanj_record", "shares ancestor with", "RO:0002158"))

    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": DEFINITIONS[identifier],
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "title": "old",
                "description": "old",
                "nodes": nodes,
                "edges": edges,
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_matches_exact_hidden_no_ignore_van_neighborhood() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3002914",
        "ARO:3002915",
        "ARO:3003727",
        "ARO:3004255",
    }


def test_vanj_parent_drops_homology_pointer_side_path() -> None:
    target = R.TARGETS["ARO:3004255"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == ["determinant", "mech0", "drug0", "resistance"]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_vanj_gets_grounded_upp_recycling_path() -> None:
    target = R.TARGETS["ARO:3002914"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "upp_recycling",
        "wall",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_vank_records_get_grounded_peptidoglycan_path() -> None:
    for identifier in {"ARO:3002915", "ARO:3003727"}:
        target = R.TARGETS[identifier]

        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        assert _node_ids(out) == [
            "determinant",
            "mech0",
            "drug0",
            "peptidoglycan_biosynthesis",
            "resistance",
        ]
        assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_legacy_ungrounded_side_paths_are_removed() -> None:
    for identifier in {"ARO:3002914", "ARO:3002915"}:
        target = R.TARGETS[identifier]

        out, changed = R.enrich_record(_record(target.identifier), target)
        text = yaml.safe_dump(out)

        assert changed
        assert "Ungrounded" not in text
        assert "node_id: crossbridge_transfer" not in text
        assert "object: crossbridge_transfer" not in text
        assert "node_id: stem_pentapeptide" not in text
        assert "object: stem_pentapeptide" not in text


def test_all_output_nodes_are_grounded() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        assert all(node.get("grounding") for node in out["causal_graphs"][0]["nodes"])


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert all(item.get("snippet") for item in edge["evidence"])
            assert len(
                {(item["reference"], item["snippet"]) for item in edge["evidence"]}
            ) == len(edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3002914"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002914, found ARO:3002915"):
        R.enrich_record(_record("ARO:3002915"), R.TARGETS["ARO:3002914"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3002914"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3002914"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_vanj_missing_recycling_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3002914"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:4]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_promotes_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3003727"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "mapping_status: REVIEWED" in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out
