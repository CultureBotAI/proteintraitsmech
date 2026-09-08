from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_efma_emrd_efflux_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_efma_emrd_efflux_graphs",
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
                "snippet": "relationship: confers_resistance_to_drug_class ARO:test ! test drug",
            }
        ],
    }


def _record(identifier: str = "ARO:3003954") -> dict:
    return {
        "identifier": identifier,
        "label": "efmA",
        "definition": "efmA is an MFS transporter permease in E. faecium.",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
                    _node("drug0", "CHEMICAL", "ARO:0000001"),
                    _node("domain", "DOMAIN", "Pfam:PF07690"),
                    _node("fold", "DOMAIN", "CATH:1.20.1250.20"),
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
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "domain",
                        "determinant",
                        "part of (MFS transporter domain)",
                        "BFO:0000050",
                    ),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge("domain", "mech0", "enables", "RO:0002327"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_set_is_exactly_efma_and_emrd() -> None:
    assert R.TARGETS == (
        R.efflux.Target("ARO:3003954", "efma-aro3003954.yaml", R.efflux.GraphKind.MFS),
        R.efflux.Target("ARO:3000309", "emrd-aro3000309.yaml", R.efflux.GraphKind.MFS),
    )


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_efma_emrd_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)

    assert len(paths) == 2
    assert {path.name for path in paths} == {
        "efma-aro3003954.yaml",
        "emrd-aro3000309.yaml",
    }


def test_wrapper_uses_mfs_efflux_graph_kind() -> None:
    target = R.target_for_record(_record(), ARO_DIR / "efma-aro3003954.yaml")

    assert target.kind == R.efflux.GraphKind.MFS


def test_enrich_record_delegates_to_mfs_rewrite() -> None:
    target = R.target_for_record(_record(), ARO_DIR / "efma-aro3003954.yaml")

    out, changed = R.enrich_record(_record(), target)

    assert changed
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("domain", "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        ("domain", "RO:0002327", "mech0"),
    }
    domain_edges = [
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if edge["subject"] == "domain" and edge["object"] == "mech0"
    ]
    assert domain_edges[0]["predicate"] == "enables (ion-motive-force-driven drug efflux)"
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])


def test_wrong_path_is_refused() -> None:
    with pytest.raises(ValueError, match="not a low-score efmA/emrD MFS efflux target"):
        R.target_for_record(_record(), ARO_DIR / "bmr-aro3003007.yaml")


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003954, found ARO:3000309"):
        R.target_for_record(
            _record("ARO:3000309"),
            ARO_DIR / "efma-aro3003954.yaml",
        )


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / "efma-aro3003954.yaml"
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
