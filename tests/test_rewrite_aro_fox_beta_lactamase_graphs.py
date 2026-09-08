from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fox_beta_lactamase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fox_beta_lactamase_graphs", SCRIPT)
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
    if predicate_id == "ARO:2000001":
        evidence = [
            {
                "reference": "ARO:3000067",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:0000032 ! cephalosporin"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:test",
                "snippet": "Test FOX beta-lactamase evidence.",
            }
        ]

    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": evidence,
    }


def _record(identifier: str = "ARO:3000067") -> dict:
    return {
        "identifier": identifier,
        "label": "FOX beta-lactamase",
        "definition": "FOX beta-lactamases are class C beta-lactamases.",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000187"),
                    _node("drug0", "CHEMICAL", "ARO:0000032"),
                    _node("active_site", "MOTIF", "PROSITE:PRU10102"),
                    _node("fold", "DOMAIN", "CATH:3.40.710.10"),
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
                        "participates in (beta-lactam hydrolysis)",
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
                    _edge(
                        "active_site",
                        "determinant",
                        "part of (Ser64 beta-lactamase motif)",
                        "BFO:0000050",
                    ),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge("active_site", "mech1", "enables", "RO:0002327"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_regex_is_exact_to_fox_parent_and_variants() -> None:
    assert R.is_target_path(ARO_DIR / "fox-beta-lactamase-aro3000067.yaml")
    assert R.is_target_path(ARO_DIR / "fox-21-aro3008183.yaml")
    assert not R.is_target_path(ARO_DIR / "fph-beta-lactamase-aro3004794.yaml")
    assert not R.is_target_path(ARO_DIR / "gox-1-aro3009999.yaml")


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_fox_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)

    assert len(paths) == 21
    assert {path.name for path in paths} == {
        "fox-1-aro3002155.yaml",
        "fox-2-aro3002156.yaml",
        "fox-3-aro3002157.yaml",
        "fox-4-aro3002158.yaml",
        "fox-5-aro3002159.yaml",
        "fox-7-aro3002160.yaml",
        "fox-8-aro3002161.yaml",
        "fox-9-aro3002163.yaml",
        "fox-10-aro3002162.yaml",
        "fox-11-aro3002164.yaml",
        "fox-12-aro3002165.yaml",
        "fox-13-aro3006471.yaml",
        "fox-14-aro3006472.yaml",
        "fox-15-aro3006473.yaml",
        "fox-16-aro3006474.yaml",
        "fox-17-aro3006475.yaml",
        "fox-18-aro3008180.yaml",
        "fox-19-aro3008181.yaml",
        "fox-20-aro3008182.yaml",
        "fox-21-aro3008183.yaml",
        "fox-beta-lactamase-aro3000067.yaml",
    }
    assert all(R.is_target_path(path) for path in paths)


def test_wrapper_uses_class_c_beta_lactamase_graph_parts() -> None:
    target = R.target_for_record(_record(), ARO_DIR / "fox-beta-lactamase-aro3000067.yaml")

    assert target.kind == R.beta.GraphKind.CLASS_C
    assert R._parts(target) == R.beta._parts(target)


def test_enrich_record_delegates_to_class_c_rewrite() -> None:
    target = R.target_for_record(_record(), ARO_DIR / "fox-beta-lactamase-aro3000067.yaml")

    out, changed = R.enrich_record(_record(), target)
    expected_edges = R.beta._core_edge_keys("active_site") | {
        ("determinant", "ARO:2000001", "drug0"),
    }

    assert changed
    assert _edge_keys(out) == expected_edges
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])


def test_wrong_path_is_refused() -> None:
    with pytest.raises(ValueError, match="not a low-score FOX beta-lactamase target"):
        R.target_for_record(_record(), ARO_DIR / "fph-beta-lactamase-aro3004794.yaml")


def test_missing_identifier_is_refused() -> None:
    record = _record()
    del record["identifier"]

    with pytest.raises(ValueError, match="missing identifier"):
        R.target_for_record(record, ARO_DIR / "fox-beta-lactamase-aro3000067.yaml")


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / "fox-beta-lactamase-aro3000067.yaml"
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
