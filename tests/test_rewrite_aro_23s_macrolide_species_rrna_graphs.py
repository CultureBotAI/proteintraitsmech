from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_23s_macrolide_species_rrna_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_23s_macrolide_species_rrna_graphs",
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


def _record(identifier: str = "ARO:3004133") -> dict:
    return {
        "identifier": identifier,
        "label": "species-specific 23S rRNA mutation",
        "definition": "Point mutation in a 23S rRNA that confers macrolide resistance.",
        "evidence": [
            {
                "reference": "DOI:10.1128/AAC.test",
                "notes": "PMID:1 (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "NUCLEIC_ACID", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:0000000"),
                    _node("pt_loop", "NUCLEIC_ACID"),
                    _node("conformation", "STATE"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_set_is_the_exact_low_score_species_slice() -> None:
    assert [target.identifier for target in R.TARGETS] == [
        "ARO:3004133",
        "ARO:3004546",
        "ARO:3004174",
        "ARO:3004132",
        "ARO:3004654",
        "ARO:3004160",
        "ARO:3004131",
    ]
    assert R.iter_target_paths(ARO_DIR) == [
        ARO_DIR / target.filename for target in R.TARGETS
    ]


def test_rewrite_mirrors_parent_23s_macrolide_graph_shape() -> None:
    target = R.TARGET_BY_ID["ARO:3004133"]

    out, changed = R.enrich_record(_record(target.identifier), target)
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("binding_site", "determinant"),
        ("determinant", "subunit"),
        ("drug0", "binding_site"),
        ("determinant", "altered_site"),
        ("altered_site", "binding_site"),
        ("altered_site", "resistance"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["binding_site"] == R.BINDING_SITE_NODE
    assert by_node["altered_site"] == R.ALTERED_SITE_NODE
    assert by_node["subunit"] == R.SUBUNIT_NODE
    assert "pt_loop" not in by_node
    assert "conformation" not in by_node


def test_record_specific_aro_citation_is_preserved() -> None:
    target = R.TARGET_BY_ID["ARO:3004546"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert {
            "reference": "DOI:10.1128/AAC.test",
            "notes": "PMID:1 (aro citation)",
        } in edge["evidence"]


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete(
    target: R.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
        else:
            assert node.get("description")
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert any(item.get("snippet") for item in edge["evidence"])
        assert len({item["reference"] for item in edge["evidence"]}) > 1


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004133, found ARO:3004546"):
        R.enrich_record(_record("ARO:3004546"), R.TARGET_BY_ID["ARO:3004133"])


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node for node in record["causal_graphs"][0]["nodes"] if node["node_id"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): mech0"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3004133"])


def test_enrich_text_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3004133"]
    text = yaml.safe_dump(_record(target.identifier), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
