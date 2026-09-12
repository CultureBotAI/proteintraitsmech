from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_inbr_isoniazid_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_inbr_isoniazid_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, predicate_id: str, object_: str, snippet: str = "") -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [{"reference": "ARO:3004898", "snippet": snippet}],
    }


def _record(identifier: str = "ARO:3004898", *, has_drug_edge: bool = False) -> dict:
    nodes = [
        {"node_id": "determinant"},
        {"node_id": "mech0"},
        {"node_id": "resistance"},
    ]
    edges = [
        _edge("determinant", "RO:0000056", "mech0"),
        _edge("mech0", "RO:0002411", "resistance"),
        _edge(
            "determinant",
            "RO:0002411",
            "resistance",
            "relationship: confers_resistance_to_antibiotic ARO:3000520 ! isoniazid",
        ),
    ]
    if has_drug_edge:
        nodes.insert(2, {"node_id": "drug0"})
        edges.append(
            _edge(
                "determinant",
                "ARO:2000001",
                "drug0",
                "relationship: confers_resistance_to_drug_class "
                "ARO:3007152 ! isoniazid-like antibiotic",
            )
        )

    return {
        "identifier": identifier,
        "label": "Mycobacterium tuberculosis inbR mutations conferring resistance to isoniazid",
        "definition": (
            "Mutations that occur in inbR that result in or contribute to antibiotic "
            "resistance to isoniazid."
        ),
        "mapping_status": "SEEDED",
        "evidence": [{"reference": "DOI:10.1038/srep13969", "notes": "PMID:26353937"}],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
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


def test_targets_are_exact_current_inbr_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004898",
        "ARO:3004899",
        "ARO:3004924",
    }


def test_generic_parent_promotes_core_graph_without_drug_edge() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _edge_keys(out) == set(R.CORE_EDGE_ORDER)
    assert all(node["node_id"] != "drug0" for node in out["causal_graphs"][0]["nodes"])
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_isoniazid_parent_keeps_drug_edge() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3004899", has_drug_edge=True),
        R.TARGETS[1],
    )

    assert changed
    assert _edge_keys(out) == set(R.EDGE_ORDER)


def test_child_keeps_direct_isoniazid_relationship() -> None:
    record = _record("ARO:3004924", has_drug_edge=True)

    out, changed = R.enrich_record(record, R.TARGETS[2])

    assert changed
    assert any(
        "ARO:3000520" in item.get("snippet", "")
        for edge in out["causal_graphs"][0]["edges"]
        for item in edge["evidence"]
    )


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(
        _record("ARO:3004924", has_drug_edge=True),
        R.TARGETS[2],
    )
    twice, changed_again = R.enrich_record(once, R.TARGETS[2])

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGETS[0].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004898, found ARO:3004899"):
        R.enrich_record(_record("ARO:3004899"), R.TARGETS[0])


def test_unexpected_drug_edge_is_refused_on_generic_parent() -> None:
    with pytest.raises(ValueError, match="unexpected edge set"):
        R.enrich_record(
            _record("ARO:3004898", has_drug_edge=True),
            R.TARGETS[0],
        )


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert _edge_keys(out) == set(R._edge_order(target))
