from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cpa_acetyltransferase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cpa_acetyltransferase_graphs",
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
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "PMID:26818562",
                "snippet": R.aac.GNAT_REVIEW_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = "ARO:3004257") -> dict:
    return {
        "identifier": identifier,
        "label": "cpa acetyltransferase",
        "definition": "Test cpa aminoglycoside acetyltransferase definition.",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "cpa acetyltransferase",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic inactivation",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001004",
                    },
                    {
                        "node_id": "mech1",
                        "label": "acylation of antibiotic conferring resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000106",
                    },
                    {
                        "node_id": "drug0",
                        "label": "aminoglycoside antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:0000016",
                    },
                    {
                        "node_id": "domain",
                        "label": "GNAT acetyltransferase domain",
                        "node_type": "DOMAIN",
                        "grounding": "InterPro:IPR000182",
                    },
                    {
                        "node_id": "fold",
                        "label": "acyl-CoA N-acyltransferase (GNAT) fold",
                        "node_type": "DOMAIN",
                        "grounding": "CATH:3.40.630",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
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
                    _edge(
                        "domain",
                        "determinant",
                        "part of (catalytic domain of the protein)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "determinant",
                        "fold",
                        "member of (adopts fold)",
                        "RO:0002350",
                    ),
                    _edge(
                        "domain",
                        "mech1",
                        "enables (antibiotic acetylation)",
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


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_is_the_exact_cpa_acetyltransferase_slice() -> None:
    assert R.TARGETS == (
        R.aac.Target("ARO:3004257", "cpa-acetyltransferase-aro3004257.yaml"),
        R.aac.Target("ARO:3003994", "cpaa-aro3003994.yaml"),
    )


@pytest.mark.parametrize("target", R.TARGETS)
def test_records_gain_acetyl_coa_dependent_acetylation_path(
    target: R.aac.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "transfer",
        "acetyl_coa",
        "acetylated",
        "domain",
        "fold",
        "resistance",
    ]
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech1"),
        ("mech1", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", "transfer"),
        ("transfer", "RO:0002233", "acetyl_coa"),
        ("transfer", "RO:0002233", "drug0"),
        ("transfer", "RO:0002411", "acetylated"),
        ("acetylated", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("domain", "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        ("domain", "RO:0002327", "transfer"),
    }


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.aac.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.aac.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004257, found ARO:3003994"):
        R.enrich_record(_record("ARO:3003994"), R.TARGET_BY_ID["ARO:3004257"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3004257"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, R.ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, R.ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert again == out
