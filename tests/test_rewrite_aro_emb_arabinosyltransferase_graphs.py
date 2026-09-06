from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_emb_arabinosyltransferase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_emb_arabinosyltransferase_graphs", SCRIPT
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
        "description": "old description",
        "evidence": [
            {
                "reference": "ARO:3005005",
                "snippet": R.EMB_FAMILY_EVIDENCE["snippet"],
            }
        ],
    }


def _record(
    identifier: str = "ARO:3005005",
    *,
    drug: bool = False,
) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "antibiotic-resistant emb arabinosyltransferase",
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
    ]
    if drug:
        nodes.append(
            {
                "node_id": "drug0",
                "label": "polyamine antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000527",
            }
        )
    nodes.extend(
        [
            {
                "node_id": "arabinosyl_transfer",
                "label": "arabinosyl transferase activity",
                "node_type": "MOLECULAR_FUNCTION",
            },
            {
                "node_id": "arabinogalactan",
                "label": "arabinogalactan synthesis pathway",
                "node_type": "PATHWAY",
            },
            {
                "node_id": "inhibition",
                "label": "ethambutol inhibition of the transferase",
                "node_type": "STATE",
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
            },
        ]
    )

    edges = [
        _edge("determinant", "mech0", "participates in", "RO:0000056"),
        _edge("mech0", "resistance"),
        _edge("determinant", "resistance"),
    ]
    if drug:
        edges.extend(
            [
                _edge(
                    "determinant",
                    "drug0",
                    "confers resistance to (drug class)",
                    "ARO:2000001",
                ),
                _edge(
                    "drug0",
                    "inhibition",
                    "causally upstream of (inhibits the transferase)",
                    "RO:0002411",
                ),
            ]
        )
    edges.extend(
        [
            _edge(
                "determinant",
                "arabinosyl_transfer",
                "enables (arabinosyl transfer)",
                "RO:0002327",
            ),
            _edge(
                "arabinosyl_transfer",
                "arabinogalactan",
                "part of (arabinogalactan synthesis)",
                "BFO:0000050",
            ),
            _edge(
                "determinant",
                "inhibition",
                "negatively regulates (the mutant is no longer inhibited)",
                "RO:0002212",
            ),
        ]
    )

    return {
        "identifier": identifier,
        "label": "antibiotic-resistant emb arabinosyltransferase",
        "definition": R.EMB_FAMILY_EVIDENCE["snippet"],
        "causal_graphs": [{"graph_id": "resistance", "nodes": nodes, "edges": edges}],
    }


def _by_node(record: dict) -> dict[str, dict]:
    return {node["node_id"]: node for node in record["causal_graphs"][0]["nodes"]}


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filenames_are_exactly_the_expected_emb_records() -> None:
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-emb-arabinosyltransferase-aro3005005.yaml",
        "ethambutol-resistant-emba-aro3003452.yaml",
        "ethambutol-resistant-embb-aro3000235.yaml",
        "ethambutol-resistant-embc-aro3002706.yaml",
        "ethambutol-resistant-embr-aro3003454.yaml",
        "mycobacterium-tuberculosis-emba-mutant-conferring-resistance-to-ethambutol-aro3003453.yaml",
        "mycobacterium-tuberculosis-embb-mutant-conferring-resistance-to-ethambutol-aro3003326.yaml",
        "mycobacterium-tuberculosis-embc-mutant-conferring-resistance-to-ethambutol-aro3003327.yaml",
        "mycobacterium-tuberculosis-embr-mutant-conferring-resistance-to-ethambutol-aro3003455.yaml",
        "mycobacterium-tuberculosis-variant-bovis-embb-with-mutation-conferring-resistanc-aro3003325.yaml",
    }


def test_family_parent_uses_broad_ec_and_drops_embb_specific_nodes() -> None:
    target = R.TARGETS["ARO:3005005"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    nodes = _by_node(out)
    assert set(nodes) == {
        "determinant",
        "mech0",
        "pentosyltransferase_activity",
        "resistance",
    }
    assert nodes["pentosyltransferase_activity"] == R.PENTOSYLTRANSFERASE_NODE
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", "pentosyltransferase_activity"),
    }
    assert out["causal_graphs"][0]["description"] == target.graph_description


def test_embb_records_keep_cell_wall_context_but_drop_inhibition_state() -> None:
    target = R.TARGETS["ARO:3000235"]

    out, changed = R.enrich_record(_record(target.identifier, drug=True), target)

    assert changed
    nodes = _by_node(out)
    assert "inhibition" not in nodes
    assert "arabinogalactan" not in nodes
    assert nodes["cell_wall_biogenesis"] == R.ACTINOBACTERIAL_CELL_WALL_NODE
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "RO:0002327", "pentosyltransferase_activity"),
        ("pentosyltransferase_activity", "BFO:0000050", "cell_wall_biogenesis"),
    }


def test_emba_and_embc_records_do_not_borrow_embb_cell_wall_context() -> None:
    for identifier in ("ARO:3003452", "ARO:3002706"):
        out, changed = R.enrich_record(_record(identifier, drug=True), R.TARGETS[identifier])

        assert changed
        assert "cell_wall_biogenesis" not in _by_node(out)
        assert _edge_keys(out) == {
            ("determinant", "RO:0000056", "mech0"),
            ("mech0", "RO:0002411", "resistance"),
            ("determinant", "RO:0002411", "resistance"),
            ("determinant", "ARO:2000001", "drug0"),
            ("determinant", "RO:0002327", "pentosyltransferase_activity"),
        }


def test_embr_records_drop_arabinosyltransferase_edges() -> None:
    target = R.TARGETS["ARO:3003454"]

    out, changed = R.enrich_record(_record(target.identifier, drug=True), target)

    assert changed
    assert _by_node(out) == {
        "determinant": {
            "node_id": "determinant",
            "label": "antibiotic-resistant emb arabinosyltransferase",
            "node_type": "PROTEIN",
            "grounding": "ARO:3003454",
        },
        "mech0": {
            "node_id": "mech0",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
        "drug0": {
            "node_id": "drug0",
            "label": "polyamine antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000527",
        },
        "resistance": {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    }
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_all_edges_get_grounded_descriptions_multi_reference_evidence(target) -> None:
    out, changed = R.enrich_record(_record(target.identifier, drug=target.drug_relation_reference), target)

    assert changed
    text = yaml.safe_dump(out, sort_keys=False)
    assert "arabinogalactan synthesis pathway" not in text
    assert "ethambutol inhibition" not in text
    assert "rounds 56-79" not in text
    graph = out["causal_graphs"][0]
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3000235"]

    once, changed = R.enrich_record(_record(target.identifier, drug=True), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3005005, found ARO:3000235"):
        R.enrich_record(_record("ARO:3000235"), R.TARGETS["ARO:3005005"])


def test_unexpected_edges_are_refused() -> None:
    record = _record("ARO:3005005")
    record["causal_graphs"][0]["edges"].append(_edge("inhibition", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge inhibition -> resistance"):
        R.enrich_record(record, R.TARGETS["ARO:3005005"])


def test_duplicate_edges_are_refused() -> None:
    record = _record("ARO:3005005")
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "arabinosyl_transfer",
            "arabinogalactan",
            "part of (arabinogalactan synthesis)",
            "BFO:0000050",
        )
    )

    with pytest.raises(
        ValueError,
        match="duplicate edge arabinosyl_transfer -> arabinogalactan",
    ):
        R.enrich_record(record, R.TARGETS["ARO:3005005"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3000235"]
    enriched, changed = R.enrich_record(_record(target.identifier, drug=True), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-06T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(target) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record), target)
    assert changed or out == record
