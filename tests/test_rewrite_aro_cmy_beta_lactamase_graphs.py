from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cmy_beta_lactamase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cmy_beta_lactamase_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(
    subject: str,
    object_: str,
    predicate: str = "causally upstream of",
    predicate_id: str = "RO:0002411",
) -> dict:
    if predicate_id == "ARO:2000001":
        evidence = [
            {
                "reference": "ARO:test",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:test ! test drug"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:test",
                "snippet": "Test beta-lactamase definition.",
            }
        ]

    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": evidence,
    }


def _node(node_id: str, node_type: str, grounding: str) -> dict:
    return {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
        "grounding": grounding,
    }


def _record(identifier: str = "ARO:3002012") -> dict:
    target = R.beta.Target(identifier, "cmy-1-aro3002012.yaml", R.beta.GraphKind.CLASS_C)
    parts = R._parts(target)

    return {
        "identifier": identifier,
        "label": "test CMY beta-lactamase",
        "definition": "Test CMY beta-lactamase definition.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", parts.mech1_node["grounding"]),
                    _node("drug0", "CHEMICAL", "ARO:3009106"),
                    _node(
                        parts.catalytic_node_id,
                        parts.catalytic_node["node_type"],
                        parts.catalytic_node["grounding"],
                    ),
                    _node("fold", "DOMAIN", parts.fold_node["grounding"]),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge(
                        "determinant",
                        "mech1",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to",
                        "ARO:2000001",
                    ),
                    _edge(
                        parts.catalytic_node_id,
                        "determinant",
                        "part of",
                        "BFO:0000050",
                    ),
                    _edge(
                        "determinant",
                        "fold",
                        "member of",
                        "RO:0002350",
                    ),
                    _edge(
                        parts.catalytic_node_id,
                        "mech1",
                        "enables (catalysis)",
                        "RO:0002327",
                    ),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _nodes_by_id(record: dict) -> dict[str, dict]:
    return {
        node["node_id"]: node
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_iter_target_paths_is_the_low_score_cmy_slice() -> None:
    target_paths = R.iter_target_paths(R.ARO_DIR)
    names = {path.name for path in target_paths}

    assert len(target_paths) == 199
    assert len(names) == len(target_paths)
    assert all(R.is_target_path(path) for path in target_paths)
    assert "cmy-beta-lactamase-aro3000069.yaml" in names
    assert "cmy-1-aro3002012.yaml" in names
    assert "cmy-8b-aro3006464.yaml" in names
    assert "cmy-199-aro3008133.yaml" in names
    assert "cmy-lat-beta-lactamase-aro3000086.yaml" not in names
    assert "cmy-lat-mox-beta-lactamase-aro3000085.yaml" not in names
    assert "cmy-mox-beta-lactamase-aro3000087.yaml" not in names


def test_non_cmy_grouping_and_efflux_files_are_not_targets() -> None:
    assert not R.is_target_path(pathlib.Path("cmy-lat-beta-lactamase-aro3000086.yaml"))
    assert not R.is_target_path(pathlib.Path("cmy-lat-mox-beta-lactamase-aro3000085.yaml"))
    assert not R.is_target_path(pathlib.Path("cmy-mox-beta-lactamase-aro3000087.yaml"))
    assert not R.is_target_path(pathlib.Path("cmeabc-aro3000773.yaml"))
    assert not R.is_target_path(pathlib.Path("cmla4-aro3002694.yaml"))
    assert not R.is_target_path(pathlib.Path("cdea-aro3003835.yaml"))


def test_target_for_record_uses_class_c() -> None:
    path = pathlib.Path("cmy-1-aro3002012.yaml")

    target = R.target_for_record(_record(), path)

    assert target == R.beta.Target("ARO:3002012", path.name, R.beta.GraphKind.CLASS_C)


def test_target_for_record_rejects_parent_grouping() -> None:
    with pytest.raises(ValueError, match="not a low-score CMY beta-lactamase target"):
        R.target_for_record(
            _record("ARO:3000086"),
            pathlib.Path("cmy-lat-beta-lactamase-aro3000086.yaml"),
        )


def test_record_gains_canonical_class_c_graph() -> None:
    target = R.beta.Target("ARO:3002012", "cmy-1-aro3002012.yaml", R.beta.GraphKind.CLASS_C)

    out, changed = R.enrich_record(_record(), target)

    assert changed

    parts = R._parts(target)
    nodes = _nodes_by_id(out)
    assert nodes[parts.catalytic_node_id] == parts.catalytic_node
    assert nodes["fold"] == parts.fold_node
    assert _edge_keys(out) == {
        *R.beta._core_edge_keys(parts.catalytic_node_id),
        ("determinant", "ARO:2000001", "drug0"),
    }


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    target = R.beta.Target("ARO:3002012", "cmy-1-aro3002012.yaml", R.beta.GraphKind.CLASS_C)

    out, changed = R.enrich_record(_record(), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.beta.Target("ARO:3002012", "cmy-1-aro3002012.yaml", R.beta.GraphKind.CLASS_C)

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    path = pathlib.Path("cmy-1-aro3002012.yaml")
    target = R.beta.Target("ARO:3002012", path.name, R.beta.GraphKind.CLASS_C)
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]

    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed_text = R.enrich_text(text, path)
    out_again, changed_again = R.enrich_text(out, path)

    assert changed_text
    assert "&id" not in out
    assert "*id" not in out
    assert out_again == out
    assert not changed_again
    assert out.count(R.HISTORY_ACTION) == 1
