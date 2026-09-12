from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_afta_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_afta_graphs", SCRIPT)
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
                "reference": "ARO:3003422",
                "snippet": R.AFTA_PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = "ARO:3003422", *, drug: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "antibiotic resistant aftA",
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
                "label": "rifamycin antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000157",
            }
        )
    nodes.extend(
        [
            {
                "node_id": "arabinofuranosyl_transfer",
                "label": "arabinofuranosyltransferase activity",
                "node_type": "MOLECULAR_FUNCTION",
            },
            {
                "node_id": "magp",
                "label": "arabinogalactan region of the mAGP complex",
                "node_type": "CHEMICAL",
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
        edges.append(
            _edge(
                "determinant",
                "drug0",
                "confers resistance to (drug class)",
                "ARO:2000001",
            )
        )
    edges.extend(
        [
            _edge(
                "determinant",
                "arabinofuranosyl_transfer",
                "participates in (arabinogalactan biosynthesis)",
                "RO:0000056",
            ),
            _edge(
                "arabinofuranosyl_transfer",
                "magp",
                "has output (the arabinogalactan region)",
                "RO:0002234",
            ),
        ]
    )

    return {
        "identifier": identifier,
        "label": "antibiotic resistant aftA",
        "definition": R.AFTA_PARENT_EVIDENCE["snippet"],
        "causal_graphs": [{"graph_id": "resistance", "nodes": nodes, "edges": edges}],
    }


def _by_node(record: dict) -> dict[str, dict]:
    return {
        node["node_id"]: node
        for node in record["causal_graphs"][0]["nodes"]
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filenames_are_exactly_the_expected_afta_records():
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-afta-aro3003422.yaml",
        "ethambutol-resistant-afta-aro3002876.yaml",
        "rifamycin-resistant-arabinosyltransferase-aro3003464.yaml",
        "mycobacterium-tuberculosis-afta-mutations-confer-resistance-to-ethambutol-aro3004951.yaml",
        "mycobacterium-tuberculosis-embb-with-mutation-conferring-resistance-to-rifampici-aro3003465.yaml",
    }


def test_exact_afta_record_uses_ec_2_4_2_46_and_grounded_cell_wall_process():
    target = R.TARGETS["ARO:3003422"]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _by_node(out) == {
        "determinant": {
            "node_id": "determinant",
            "label": "antibiotic resistant aftA",
            "node_type": "PROTEIN",
            "grounding": "ARO:3003422",
        },
        "mech0": {
            "node_id": "mech0",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
        "afta_activity": R.AFTA_ACTIVITY_NODE,
        "cell_wall_biogenesis": R.ACTINOBACTERIAL_CELL_WALL_NODE,
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
        ("determinant", "RO:0002327", "afta_activity"),
        ("afta_activity", "BFO:0000050", "cell_wall_biogenesis"),
    }
    assert out["causal_graphs"][0]["description"] == target.graph_description


def test_embb_branch_uses_broad_pentosyltransferase_not_afta_specific_ec():
    target = R.TARGETS["ARO:3003465"]
    out, changed = R.enrich_record(_record(target.identifier, drug=True), target)

    assert changed
    nodes = _by_node(out)
    assert "magp" not in nodes
    assert "afta_activity" not in nodes
    assert nodes["pentosyltransferase_activity"] == R.BROAD_PENTOSYLTRANSFERASE_NODE
    role_edge = next(
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if edge["object"] == "pentosyltransferase_activity"
    )
    role_references = {item["reference"] for item in role_edge["evidence"]}
    assert role_references == {"ARO:3003464", "EC:2.4.2.-"}
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "RO:0002327", "pentosyltransferase_activity"),
        ("pentosyltransferase_activity", "BFO:0000050", "cell_wall_biogenesis"),
    }


def test_all_edges_get_grounded_descriptions_multi_reference_evidence_and_no_obsolete_go():
    for identifier in ("ARO:3002876", "ARO:3004951"):
        target = R.TARGETS[identifier]
        out, changed = R.enrich_record(_record(target.identifier, drug=True), target)

        assert changed
        text = yaml.safe_dump(out, sort_keys=False)
        assert "magp" not in text
        assert "GO:0052636" not in text
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3002876"]

    once, changed = R.enrich_record(_record(target.identifier, drug=True), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3003422, found ARO:3002876"):
        R.enrich_record(_record("ARO:3002876"), R.TARGETS["ARO:3003422"])


def test_unexpected_edges_are_refused():
    record = _record("ARO:3003422")
    record["causal_graphs"][0]["edges"].append(_edge("magp", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge magp -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3003422"])


def test_duplicate_edges_are_refused():
    record = _record("ARO:3003422")
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "arabinofuranosyl_transfer",
            "magp",
            "has output (the arabinogalactan region)",
            "RO:0002234",
        )
    )

    with pytest.raises(
        ValueError,
        match="duplicate edge arabinofuranosyl_transfer -> magp",
    ):
        R.enrich_record(record, R.TARGETS["ARO:3003422"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once():
    target = R.TARGETS["ARO:3003422"]
    enriched, changed = R.enrich_record(_record(), target)
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
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(target):
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record), target)
    assert changed or out == record
