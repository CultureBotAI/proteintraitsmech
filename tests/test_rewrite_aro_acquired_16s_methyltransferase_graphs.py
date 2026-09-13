from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_acquired_16s_methyltransferase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_acquired_16s_methyltransferase_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3000858": "armA",
    "ARO:3000859": "rmtA",
    "ARO:3000860": "rmtB",
    "ARO:3000861": "rmtC",
    "ARO:3000862": "sgm",
    "ARO:3002665": "npmA",
    "ARO:3002666": "rmtF",
    "ARO:3002667": "rmtD",
    "ARO:3002668": "rmtG",
    "ARO:3003198": "rmtH",
    "ARO:3004102": "kamB",
    "ARO:3004677": "rmtD2",
    "ARO:3004678": "rmtE",
    "ARO:3004679": "rmtE2",
}

SUBFAMILIES = {
    "ARO:3000858": "ARO:3004271",
    "ARO:3000859": "ARO:3004271",
    "ARO:3000860": "ARO:3004271",
    "ARO:3000861": "ARO:3004271",
    "ARO:3000862": "ARO:3004271",
    "ARO:3002665": "ARO:3004272",
    "ARO:3002666": "ARO:3004271",
    "ARO:3002667": "ARO:3004271",
    "ARO:3002668": "ARO:3004271",
    "ARO:3003198": "ARO:3004271",
    "ARO:3004102": "ARO:3004272",
    "ARO:3004677": "ARO:3004271",
    "ARO:3004678": "ARO:3004271",
    "ARO:3004679": "ARO:3004271",
}

FILES = {
    target.filename
    for target in R.TARGETS.values()
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
                "reference": "PMID:40643688",
                "snippet": "16S rRNA methyltransferase evidence",
            }
        ],
    }


def _record(identifier: str = "ARO:3000858") -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": f"{LABELS[identifier]} is a 16S rRNA methyltransferase.",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": LABELS[identifier],
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic target alteration",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001001",
                    },
                    {
                        "node_id": "mech1",
                        "label": "ribosomal alteration conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000211",
                    },
                    {
                        "node_id": "drug0",
                        "label": "aminoglycoside antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:0000016",
                    },
                    {
                        "node_id": "methyltransferase",
                        "label": "16S rRNA methyltransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "decoding_site",
                        "label": "16S rRNA decoding site",
                        "node_type": "NUCLEIC_ACID",
                    },
                    {
                        "node_id": "methylated",
                        "label": "methylated decoding site",
                        "node_type": "STATE",
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
                        "determinant",
                        "methyltransferase",
                        "enables (16S rRNA methylation)",
                        "RO:0002327",
                    ),
                    _edge("methyltransferase", "methylated"),
                    _edge(
                        "methylated",
                        "decoding_site",
                        "negatively regulates",
                        "RO:0002212",
                    ),
                    _edge(
                        "drug0",
                        "decoding_site",
                        "molecularly interacts with",
                        "RO:0002436",
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


def test_target_set_matches_exact_hidden_no_ignore_acquired_16s_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == FILES
    assert len(R.TARGETS) == 14


def test_subfamily_assignments_match_parent_traits() -> None:
    assert {
        identifier: target.subfamily_identifier
        for identifier, target in R.TARGETS.items()
    } == SUBFAMILIES


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_records_gain_exact_rhea_methylation(identifier: str) -> None:
    target = R.TARGETS[identifier]

    out, changed = R.enrich_record(_record(identifier), target)

    assert changed
    methylation_node_id = R.METHYLATION_NODES[target.subfamily_identifier]["node_id"]
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        methylation_node_id,
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_g1405_and_a1408_use_distinct_rhea_reactions() -> None:
    g1405, _ = R.enrich_record(_record("ARO:3000858"), R.TARGETS["ARO:3000858"])
    a1408, _ = R.enrich_record(_record("ARO:3002665"), R.TARGETS["ARO:3002665"])

    assert "grounding: RHEA:42772" in yaml.safe_dump(g1405)
    assert "grounding: RHEA:42776" not in yaml.safe_dump(g1405)
    assert "grounding: RHEA:42776" in yaml.safe_dump(a1408)
    assert "grounding: RHEA:42772" not in yaml.safe_dump(a1408)


def test_legacy_decoding_site_subgraph_is_removed() -> None:
    out, changed = R.enrich_record(_record("ARO:3004102"), R.TARGETS["ARO:3004102"])
    text = yaml.safe_dump(out)

    assert changed
    assert "node_id: methyltransferase" not in text
    assert "object: methyltransferase" not in text
    assert "node_id: decoding_site" not in text
    assert "object: decoding_site" not in text
    assert "node_id: methylated" not in text
    assert "subject: methylated" not in text


def test_all_output_nodes_are_grounded() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        assert all(node.get("grounding") for node in out["causal_graphs"][0]["nodes"])


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert all(item.get("snippet") for item in edge["evidence"])
            assert len(
                {(item["reference"], item["snippet"]) for item in edge["evidence"]}
            ) == len(edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3000858"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000858, found ARO:3002665"):
        R.enrich_record(_record("ARO:3002665"), R.TARGETS["ARO:3000858"])


def test_wrong_methylation_reaction_is_refused() -> None:
    target = R.TARGETS["ARO:3000858"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "determinant",
            "a1408_methylation",
            "enables (16S rRNA A1408 N1-methylation)",
            "RO:0002327",
        )
    )

    with pytest.raises(ValueError, match="unexpected edge determinant -> a1408_methylation"):
        R.enrich_record(record, target)


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3000858"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3000858"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_missing_core_edge_is_refused() -> None:
    target = R.TARGETS["ARO:3000858"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "mech1"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, target)


def test_missing_legacy_and_exact_methylation_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3000858"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] not in {"methyltransferase", "methylated", "decoding_site"}
        and edge["subject"] not in {"methyltransferase", "methylated"}
    ]

    with pytest.raises(ValueError, match="missing both exact and legacy methylation"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3000858"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "mapping_status: REVIEWED" in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out
