from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_imih_imis_ind_beta_lactamase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_imih_imis_ind_beta_lactamase_graphs",
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
    evidence = [
        {
            "reference": "ARO:test",
            "snippet": "Test metallo-beta-lactamase evidence.",
        }
    ]
    if predicate_id == "ARO:2000001":
        evidence[0]["snippet"] = "relationship: confers_resistance_to_drug_class ARO:test ! test"

    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": evidence,
    }


def _record(identifier: str = "ARO:3000060") -> dict:
    return {
        "identifier": identifier,
        "label": "test metallo-beta-lactamase",
        "definition": "Test metallo-beta-lactamase definition.",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000203"),
                    _node("drug0", "CHEMICAL", "ARO:0000020"),
                    _node("domain", "DOMAIN", "Pfam:PF00753"),
                    _node("fold", "DOMAIN", "CATH:3.60.15.30"),
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
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge("domain", "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge("domain", "mech1", "enables", "RO:0002327"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_regex_is_exact_to_imih_imis_ind() -> None:
    assert R.is_target_path(ARO_DIR / "imih-aro3003094.yaml")
    assert R.is_target_path(ARO_DIR / "imis-aro3003095.yaml")
    assert R.is_target_path(ARO_DIR / "ind-2a-aro3002258.yaml")
    assert R.is_target_path(ARO_DIR / "ind-beta-lactamase-aro3000060.yaml")
    assert not R.is_target_path(ARO_DIR / "imi-1-aro3001858.yaml")
    assert not R.is_target_path(ARO_DIR / "isoniazid-resistant-nudc-aro3004911.yaml")


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_imih_imis_ind_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)
    names = {path.name for path in paths}

    assert len(paths) == 22
    assert len(names) == len(paths)
    assert all(R.is_target_path(path) for path in paths)
    assert "imih-aro3003094.yaml" in names
    assert "imis-aro3003095.yaml" in names
    assert "ind-beta-lactamase-aro3000060.yaml" in names
    assert "ind-19-aro3008227.yaml" in names
    assert "ind-2a-aro3002258.yaml" in names
    assert "isoniazid-resistant-nudc-aro3004911.yaml" not in names


def test_target_for_record_uses_metallo_beta_lactamase_graph_parts() -> None:
    target = R.target_for_record(_record(), ARO_DIR / "ind-beta-lactamase-aro3000060.yaml")

    assert target == R.beta.Target("ARO:3000060", "ind-beta-lactamase-aro3000060.yaml", R.beta.GraphKind.METALLO)
    assert R._parts(target) == R.beta._parts(target)


def test_enrich_record_delegates_to_metallo_rewrite() -> None:
    target = R.target_for_record(_record(), ARO_DIR / "ind-beta-lactamase-aro3000060.yaml")

    out, changed = R.enrich_record(_record(), target)
    expected_edges = R.beta._core_edge_keys("domain") | {
        ("determinant", "ARO:2000001", "drug0"),
    }

    assert changed
    assert _edge_keys(out) == expected_edges
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])


def test_wrong_path_is_refused() -> None:
    with pytest.raises(ValueError, match="not a low-score imiH/imiS/IND beta-lactamase target"):
        R.target_for_record(_record(), ARO_DIR / "imi-1-aro3001858.yaml")


def test_missing_identifier_is_refused() -> None:
    record = _record()
    del record["identifier"]

    with pytest.raises(ValueError, match="missing identifier"):
        R.target_for_record(record, ARO_DIR / "imih-aro3003094.yaml")


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / "ind-beta-lactamase-aro3000060.yaml"
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
