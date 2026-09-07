from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_pump_and_abcf_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_pump_and_abcf_graphs", SCRIPT)
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


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [
            {
                "reference": "PMID:test",
                "snippet": "test",
            }
        ],
    }


def _record(identifier: str = "ARO:3007669") -> dict:
    return {
        "identifier": identifier,
        "label": "test label",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
                    _node("domain", "DOMAIN", "Pfam:test"),
                    _node("fold", "DOMAIN", "CATH:test"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge("determinant", "mech0"),
                    _edge("mech0", "resistance"),
                ],
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


def test_targets_are_exact_current_efflux_and_abcf_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:0010001",
        "ARO:0010002",
        "ARO:3000344",
        "ARO:3000343",
        "ARO:3000373",
        "ARO:3000391",
        "ARO:3000421",
        "ARO:3000448",
        "ARO:3000545",
        "ARO:3000561",
        "ARO:3000769",
        "ARO:3001214",
        "ARO:3001216",
        "ARO:3001313",
        "ARO:3001329",
        "ARO:3002522",
        "ARO:3002690",
        "ARO:3002691",
        "ARO:3002693",
        "ARO:3002695",
        "ARO:3002696",
        "ARO:3002698",
        "ARO:3002699",
        "ARO:3002701",
        "ARO:3002702",
        "ARO:3002703",
        "ARO:3002704",
        "ARO:3002705",
        "ARO:3002812",
        "ARO:3002813",
        "ARO:3002817",
        "ARO:3002881",
        "ARO:3002892",
        "ARO:3002894",
        "ARO:3002987",
        "ARO:3002988",
        "ARO:3003036",
        "ARO:3003746",
        "ARO:3003748",
        "ARO:3003761",
        "ARO:3003801",
        "ARO:3003942",
        "ARO:3003947",
        "ARO:3003950",
        "ARO:3003955",
        "ARO:3003960",
        "ARO:3003963",
        "ARO:3003964",
        "ARO:3004101",
        "ARO:3004103",
        "ARO:3004469",
        "ARO:3004470",
        "ARO:3004572",
        "ARO:3004573",
        "ARO:3004577",
        "ARO:3004665",
        "ARO:3004666",
        "ARO:3004667",
        "ARO:3005043",
        "ARO:3007010",
        "ARO:3007011",
        "ARO:3007019",
        "ARO:3007061",
        "ARO:3007068",
        "ARO:3007553",
        "ARO:3007554",
        "ARO:3007566",
        "ARO:3007637",
        "ARO:3007644",
        "ARO:3007645",
        "ARO:3007646",
        "ARO:3007662",
        "ARO:3007669",
    }


def test_mfs_targets_keep_mfs_domain_and_fold() -> None:
    out, changed = R.enrich_record(_record("ARO:3007669"), R.EFFLUX_TARGETS[0])
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert by_node["domain"]["grounding"] == "Pfam:PF07690"
    assert by_node["fold"]["grounding"] == "CATH:1.20.1250.20"
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("domain", "determinant"),
        ("determinant", "fold"),
        ("domain", "mech0"),
    }


def test_abc_efflux_targets_keep_abc_domain_and_fold() -> None:
    target = next(target for target in R.EFFLUX_TARGETS if target.identifier == "ARO:3003942")

    out, changed = R.enrich_record(_record("ARO:3003942"), target)
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert by_node["domain"]["grounding"] == "Pfam:PF00005"
    assert by_node["fold"]["grounding"] == "CATH:3.40.50.300"


def test_abcf_is_ribosomal_protection_not_efflux() -> None:
    out, changed = R.enrich_record(_record("ARO:3004469"), R.ABC_F_TARGET)
    nodes = _node_ids(out)
    pairs = _edge_pairs(out)
    graph = out["causal_graphs"][0]

    assert changed
    assert "ribosome" in nodes
    assert "displaced_antibiotic" in nodes
    assert ("determinant", "ribosome") in pairs
    assert ("displaced_antibiotic", "resistance") in pairs
    assert graph["nodes"][1]["grounding"] == "ARO:0001003"
    assert "efflux transporter" in graph["description"]


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(_record(target.identifier), target)
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
    once, changed = R.enrich_record(_record("ARO:3004469"), R.ABC_F_TARGET)
    twice, changed_again = R.enrich_record(once, R.ABC_F_TARGET)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004469, found ARO:3007669"):
        R.enrich_record(_record("ARO:3007669"), R.ABC_F_TARGET)


def test_missing_required_node_is_refused() -> None:
    record = _record("ARO:3007669")
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "domain"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): domain"):
        R.enrich_record(record, R.EFFLUX_TARGETS[0])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record("ARO:3004469"), sort_keys=False)
    path = ARO_DIR / R.ABC_F_TARGET.filename

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
