from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_oxa_class_d_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_oxa_class_d_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


def _evidence(reference: str = "ARO:test") -> list[dict[str, str]]:
    return [
        {
            "reference": reference,
            "snippet": f"Snippet for {reference}.",
            "notes": f"Notes for {reference}.",
        }
    ]


def _edge(
    subject: str,
    predicate_id: str,
    object_: str,
    predicate: str = "related to",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": _evidence(),
    }


def _record(identifier: str = "ARO:3008427") -> dict:
    return {
        "identifier": identifier,
        "label": "test OXA beta-lactamase",
        "definition": "A test OXA beta-lactamase.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000187"),
                    _node("active_site", "MOTIF", "PROSITE:PRU10103"),
                    _node("fold", "DOMAIN", "CATH:3.40.710.10"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "RO:0000056",
                        "mech0",
                        "participates in (resistance mechanism)",
                    ),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "RO:0000056",
                        "mech1",
                        "participates in (resistance mechanism)",
                    ),
                    _edge("mech1", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "RO:0002411",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "active_site",
                        "BFO:0000050",
                        "determinant",
                        "part of (active site of the protein)",
                    ),
                    _edge(
                        "determinant",
                        "RO:0002350",
                        "fold",
                        "member of (adopts fold)",
                    ),
                    _edge(
                        "active_site",
                        "RO:0002327",
                        "mech1",
                        "enables (catalysis)",
                    ),
                ],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_targets_are_exact_current_oxa_batch() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3008427",
        "ARO:3008432",
        "ARO:3001706",
        "ARO:3008457",
        "ARO:3008458",
        "ARO:3008460",
        "ARO:3008462",
        "ARO:3001708",
        "ARO:3008507",
        "ARO:3008508",
        "ARO:3008509",
        "ARO:3008526",
        "ARO:3008560",
        "ARO:3008561",
        "ARO:3008571",
        "ARO:3008572",
        "ARO:3008573",
        "ARO:3008574",
        "ARO:3008576",
        "ARO:3008577",
        "ARO:3001441",
        "ARO:3008578",
        "ARO:3008579",
        "ARO:3008581",
        "ARO:3008618",
        "ARO:3008648",
        "ARO:3008649",
        "ARO:3008661",
        "ARO:3008668",
        "ARO:3008669",
        "ARO:3008670",
        "ARO:3008671",
        "ARO:3001452",
        "ARO:3001411",
        "ARO:3001413",
        "ARO:3001697",
        "ARO:3001698",
        "ARO:3001699",
        "ARO:3001700",
        "ARO:3001701",
        "ARO:3001415",
        "ARO:3001809",
        "ARO:3001490",
        "ARO:3001491",
        "ARO:3001492",
        "ARO:3001494",
        "ARO:3001497",
        "ARO:3001610",
        "ARO:3001503",
        "ARO:3001734",
        "ARO:3001744",
        "ARO:3001424",
        "ARO:3001745",
        "ARO:3001751",
        "ARO:3001754",
        "ARO:3001763",
        "ARO:3001505",
        "ARO:3001506",
        "ARO:3001507",
        "ARO:3001508",
        "ARO:3001509",
        "ARO:3001427",
        "ARO:3001428",
        "ARO:3001777",
    }


def test_enrich_record_preserves_class_d_active_site_and_fold() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3008427"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "active_site",
        "fold",
        "resistance",
    ]
    assert ("active_site", "determinant") in _edge_pairs(out)
    assert ("determinant", "fold") in _edge_pairs(out)


def test_expected_edges_are_written() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3008427"])

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "mech1"),
        ("mech1", "resistance"),
        ("determinant", "resistance"),
        ("active_site", "determinant"),
        ("determinant", "fold"),
        ("active_site", "mech1"),
    }


def test_all_nodes_are_grounded_and_all_edges_are_complete() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3008427"])
    graph = out["causal_graphs"][0]

    assert changed
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3008427"])
    twice, changed_again = R.enrich_record(once, R.TARGET_BY_ID["ARO:3008427"])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3008427, found ARO:3008432"):
        R.enrich_record(_record("ARO:3008432"), R.TARGET_BY_ID["ARO:3008427"])


def test_missing_fold_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "fold"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): fold"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3008427"])


def test_unexpected_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("mech0", "RO:0002233", "amide"),
    )

    with pytest.raises(ValueError, match="unexpected edge mech0 -> amide"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3008427"])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGET_BY_ID["ARO:3008427"].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once
