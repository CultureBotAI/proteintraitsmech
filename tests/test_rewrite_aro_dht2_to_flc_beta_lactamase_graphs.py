from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_dht2_to_flc_beta_lactamase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_dht2_to_flc_beta_lactamase_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _node(node_id: str, node_type: str, grounding: str) -> dict:
    return {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
        "grounding": grounding,
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
                "reference": "ARO:test",
                "snippet": "Test beta-lactamase evidence.",
            }
        ],
    }


def _record(identifier: str = "ARO:3006872", *, catalytic_node_id: str = "domain") -> dict:
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
        _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000076"),
        _node("drug0", "CHEMICAL", "ARO:3000007"),
        _node("fold", "DOMAIN", "CATH:test"),
        _node("resistance", "PHENOTYPE", "GO:0046677"),
    ]
    if catalytic_node_id == "domain":
        nodes.insert(4, _node("domain", "DOMAIN", "Pfam:PF00753"))
    else:
        nodes.insert(4, _node("active_site", "MOTIF", "PROSITE:test"))

    return {
        "identifier": identifier,
        "label": "test beta-lactamase",
        "definition": "Test beta-lactamase definition.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge(
                        "determinant",
                        "mech1",
                        "participates in (specific hydrolysis)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(catalytic_node_id, "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge(catalytic_node_id, "mech1", "enables", "RO:0002327"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _expected_edges(catalytic_node_id: str) -> set[tuple[str, str, str]]:
    return R.beta._core_edge_keys(catalytic_node_id) | {
        ("determinant", "ARO:2000001", "drug0"),
    }


def test_target_regex_includes_only_beta_lactamase_names() -> None:
    assert R.is_target_path(ARO_DIR / "dht2-1-aro3006872.yaml")
    assert R.is_target_path(ARO_DIR / "ec-beta-lactamase-aro3005406.yaml")
    assert R.is_target_path(ARO_DIR / "flc-1-aro3005033.yaml")
    assert not R.is_target_path(ARO_DIR / "efma-aro3003954.yaml")
    assert not R.is_target_path(ARO_DIR / "fara-aro3003961.yaml")


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_mixed_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)

    assert len(paths) == 34
    assert all(R.is_target_path(path) for path in paths)


@pytest.mark.parametrize(
    "filename,kind",
    [
        ("dht2-1-aro3006872.yaml", R.beta.GraphKind.METALLO),
        ("ec-13-aro3006874.yaml", R.beta.GraphKind.CLASS_C),
        ("erp-1-aro3004782.yaml", R.beta.GraphKind.CLASS_A),
        ("flc-1-aro3005033.yaml", R.beta.GraphKind.CLASS_A),
    ],
)
def test_kind_for_path(filename: str, kind: R.beta.GraphKind) -> None:
    assert R.kind_for_path(ARO_DIR / filename) == kind


@pytest.mark.parametrize(
    "filename,kind,catalytic_node_id",
    [
        ("dht2-1-aro3006872.yaml", R.beta.GraphKind.METALLO, "domain"),
        ("ec-13-aro3006874.yaml", R.beta.GraphKind.CLASS_C, "active_site"),
        ("erp-1-aro3004782.yaml", R.beta.GraphKind.CLASS_A, "active_site"),
    ],
)
def test_enrich_record_delegates_to_expected_graph_kind(
    filename: str,
    kind: R.beta.GraphKind,
    catalytic_node_id: str,
) -> None:
    target = R.target_for_record(
        _record(catalytic_node_id=catalytic_node_id),
        ARO_DIR / filename,
    )

    out, changed = R.enrich_record(_record(catalytic_node_id=catalytic_node_id), target)

    assert target.kind == kind
    assert changed
    assert _edge_keys(out) == _expected_edges(catalytic_node_id)
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])


def test_wrong_path_is_refused() -> None:
    with pytest.raises(ValueError, match="not a DHT2-to-FLC"):
        R.target_for_record(_record(), ARO_DIR / "fosa-aro3000149.yaml")


def test_missing_identifier_is_refused() -> None:
    record = _record()
    del record["identifier"]

    with pytest.raises(ValueError, match="missing identifier"):
        R.target_for_record(record, ARO_DIR / "dht2-1-aro3006872.yaml")


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / "dht2-1-aro3006872.yaml"
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
