from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_her_to_imi_beta_lactamase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_her_to_imi_beta_lactamase_graphs",
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
            "snippet": "Test beta-lactamase evidence.",
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


def _record(identifier: str, kind: R.beta.GraphKind) -> dict:
    if kind == R.beta.GraphKind.METALLO:
        catalytic_node_id = "domain"
        catalytic_node = _node("domain", "DOMAIN", "Pfam:PF00753")
        fold_node = _node("fold", "DOMAIN", "CATH:3.60.15.30")
        mech1_grounding = "ARO:3000203"
    else:
        catalytic_node_id = "active_site"
        catalytic_node = _node("active_site", "MOTIF", "PROSITE:PS00146")
        fold_node = _node("fold", "DOMAIN", "CATH:3.40.710.10")
        mech1_grounding = "ARO:3000187"

    return {
        "identifier": identifier,
        "label": "test beta-lactamase",
        "definition": "Test beta-lactamase definition.",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", mech1_grounding),
                    _node("drug0", "CHEMICAL", "ARO:test"),
                    catalytic_node,
                    fold_node,
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


def test_target_regex_is_exact_to_selected_families() -> None:
    assert R.is_target_path(ARO_DIR / "her-beta-lactamase-aro3007870.yaml")
    assert R.is_target_path(ARO_DIR / "hmb-2-aro3008207.yaml")
    assert R.is_target_path(ARO_DIR / "imi-27-aro3008214.yaml")
    assert not R.is_target_path(ARO_DIR / "imis-aro3003095.yaml")
    assert not R.is_target_path(ARO_DIR / "imih-aro3003094.yaml")
    assert not R.is_target_path(ARO_DIR / "ind-1-aro3002256.yaml")


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_her_to_imi_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)
    names = {path.name for path in paths}

    assert len(paths) == 38
    assert len(names) == len(paths)
    assert all(R.is_target_path(path) for path in paths)
    assert "her-beta-lactamase-aro3007870.yaml" in names
    assert "hmb-beta-lactamase-aro3004209.yaml" in names
    assert "imi-beta-lactamase-aro3000018.yaml" in names
    assert "imi-27-aro3008214.yaml" in names
    assert "imis-aro3003095.yaml" not in names
    assert "ind-beta-lactamase-aro3000060.yaml" not in names


@pytest.mark.parametrize(
    ("filename", "kind"),
    [
        ("her-1-aro3008200.yaml", R.beta.GraphKind.CLASS_A),
        ("hmb-beta-lactamase-aro3004209.yaml", R.beta.GraphKind.METALLO),
        ("imi-27-aro3008214.yaml", R.beta.GraphKind.CLASS_A),
    ],
)
def test_target_for_record_selects_expected_graph_kind(
    filename: str,
    kind: R.beta.GraphKind,
) -> None:
    target = R.target_for_record(_record("ARO:test", kind), ARO_DIR / filename)

    assert target == R.beta.Target("ARO:test", filename, kind)
    assert R._parts(target) == R.beta._parts(target)


@pytest.mark.parametrize(
    ("filename", "kind", "catalytic_node_id"),
    [
        ("her-beta-lactamase-aro3007870.yaml", R.beta.GraphKind.CLASS_A, "active_site"),
        ("hmb-beta-lactamase-aro3004209.yaml", R.beta.GraphKind.METALLO, "domain"),
        ("imi-beta-lactamase-aro3000018.yaml", R.beta.GraphKind.CLASS_A, "active_site"),
    ],
)
def test_enrich_record_delegates_to_selected_rewrite(
    filename: str,
    kind: R.beta.GraphKind,
    catalytic_node_id: str,
) -> None:
    record = _record("ARO:test", kind)
    target = R.target_for_record(record, ARO_DIR / filename)

    out, changed = R.enrich_record(record, target)
    expected_edges = R.beta._core_edge_keys(catalytic_node_id) | {
        ("determinant", "ARO:2000001", "drug0"),
    }

    assert changed
    assert _edge_keys(out) == expected_edges
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])


def test_wrong_path_is_refused() -> None:
    with pytest.raises(ValueError, match="not a low-score HER/HMB/IMI beta-lactamase target"):
        R.target_for_record(
            _record("ARO:3003095", R.beta.GraphKind.METALLO),
            ARO_DIR / "imis-aro3003095.yaml",
        )


def test_missing_identifier_is_refused() -> None:
    record = _record("ARO:test", R.beta.GraphKind.CLASS_A)
    del record["identifier"]

    with pytest.raises(ValueError, match="missing identifier"):
        R.target_for_record(record, ARO_DIR / "imi-beta-lactamase-aro3000018.yaml")


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / "imi-beta-lactamase-aro3000018.yaml"
    text = yaml.safe_dump(_record("ARO:3000018", R.beta.GraphKind.CLASS_A), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
