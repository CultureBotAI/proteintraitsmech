from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rnd_efflux_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rnd_efflux_graphs", SCRIPT)
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


def _record(identifier: str = "ARO:3000207", is_subunit: bool = True) -> dict:
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
        _node("resistance", "PHENOTYPE", "GO:0046677"),
    ]
    if is_subunit:
        nodes.extend(
            [
                _node("pump_complex", "STATE"),
                _node("binding_pocket", "STATE"),
                _node("export", "BIOLOGICAL_PROCESS", "GO:1990961"),
            ]
        )
    else:
        nodes.extend(
            [
                _node("domain", "DOMAIN", "Pfam:PF00873"),
                _node("fold", "DOMAIN", "CATH:3.30.70.1430"),
            ]
        )

    return {
        "identifier": identifier,
        "label": "test label",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": [],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> set[str]:
    return {
        node["node_id"]
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_targets_are_exact_current_rnd_records() -> None:
    assert len(R.TARGETS) == 62
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:0010004",
        "ARO:3000207",
        "ARO:3000216",
        "ARO:3000499",
        "ARO:3000502",
        "ARO:3000770",
        "ARO:3000774",
        "ARO:3000775",
        "ARO:3000777",
        "ARO:3000778",
        "ARO:3000779",
        "ARO:3000780",
        "ARO:3000781",
        "ARO:3000782",
        "ARO:3000787",
        "ARO:3000788",
        "ARO:3000789",
        "ARO:3000790",
        "ARO:3000791",
        "ARO:3000792",
        "ARO:3000793",
        "ARO:3000794",
        "ARO:3000795",
        "ARO:3000796",
        "ARO:3000783",
        "ARO:3000784",
        "ARO:3000785",
        "ARO:3002982",
        "ARO:3002983",
        "ARO:3003030",
        "ARO:3003031",
        "ARO:3003033",
        "ARO:3003034",
        "ARO:3003691",
        "ARO:3003692",
        "ARO:3003693",
        "ARO:3003694",
        "ARO:3003697",
        "ARO:3003698",
        "ARO:3003699",
        "ARO:3003703",
        "ARO:3003704",
        "ARO:3003705",
        "ARO:3003009",
        "ARO:3003010",
        "ARO:3003811",
        "ARO:3004143",
        "ARO:3004144",
        "ARO:3004041",
        "ARO:3004042",
        "ARO:3004043",
        "ARO:3004099",
        "ARO:3004100",
        "ARO:3000799",
        "ARO:3000800",
        "ARO:3000801",
        "ARO:3000803",
        "ARO:3000804",
        "ARO:3000807",
        "ARO:3000808",
        "ARO:3009148",
        "ARO:3009153",
    }


def test_subunit_graph_drops_orphan_binding_pocket_and_links_export() -> None:
    out, changed = R.enrich_record(_record("ARO:3000207"), R.SUBUNIT_TARGETS[0])
    nodes = _node_ids(out)

    assert changed
    assert "binding_pocket" not in nodes
    assert "pump_complex" in nodes
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "pump_complex"),
        ("pump_complex", "export"),
        ("export", "resistance"),
    }


def test_complex_graph_keeps_rnd_domain_and_fold() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3000770", is_subunit=False),
        R.COMPLEX_TARGETS[1],
    )
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert by_node["domain"]["grounding"] == "Pfam:PF00873"
    assert by_node["fold"]["grounding"] == "CATH:3.30.70.1430"
    assert ("domain", "mech0") in _edge_pairs(out)


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(
            _record(target.identifier, is_subunit=target.is_subunit),
            target,
        )
        graph = out["causal_graphs"][0]

        assert changed
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
        for edge in graph["edges"]:
            references = {item["reference"] for item in edge["evidence"]}
            assert edge["description"]
            assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record("ARO:3000207"), R.SUBUNIT_TARGETS[0])
    twice, changed_again = R.enrich_record(once, R.SUBUNIT_TARGETS[0])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000207, found ARO:3000216"):
        R.enrich_record(_record("ARO:3000216"), R.SUBUNIT_TARGETS[0])


def test_missing_required_node_is_refused() -> None:
    record = _record("ARO:3000207")
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "pump_complex"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): pump_complex"):
        R.enrich_record(record, R.SUBUNIT_TARGETS[0])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record("ARO:3000207"), sort_keys=False)
    path = ARO_DIR / R.SUBUNIT_TARGETS[0].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
