from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fungal_p450_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fungal_p450_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


P = _load()


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
                "reference": P.PARENT_IDENTIFIER,
                "snippet": P.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = P.PARENT_IDENTIFIER) -> dict:
    target = P.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": target.identifier,
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
    for drug_class in target.drug_classes:
        nodes.append(
            {
                "node_id": drug_class.node_id,
                "label": drug_class.label,
                "node_type": "CHEMICAL",
                "grounding": drug_class.grounding,
            }
        )
    nodes.extend(
        [
            {
                "node_id": "p450_activity",
                "label": "cytochrome P450 monooxygenase activity",
                "node_type": "MOLECULAR_FUNCTION",
                "description": (
                    "The one functional fact CARD's naming supplies. "
                    "Ungrounded: not looked up rather than guessed."
                ),
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
        _edge(
            "determinant",
            "mech0",
            "participates in (resistance mechanism)",
            "RO:0000056",
        ),
        _edge("mech0", "resistance"),
        _edge(
            "determinant",
            "resistance",
            "causally upstream of (confers resistance)",
        ),
    ]
    for drug_class in target.drug_classes:
        edges.append(
            _edge(
                "determinant",
                drug_class.node_id,
                "confers resistance to (drug class)",
                "ARO:2000001",
            )
        )
    edges.append(
        _edge(
            "determinant",
            "p450_activity",
            "enables (cytochrome P450 activity)",
            "RO:0002327",
        )
    )

    return {
        "identifier": identifier,
        "label": "fungal cytochrome P450 enzyme",
        "definition": P.PARENT_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": nodes,
                "edges": edges,
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


def test_target_set_matches_exact_fungal_p450_branch() -> None:
    assert {target.identifier for target in P.TARGETS.values()} == {
        "ARO:3007522",
        "ARO:3007523",
        "ARO:3007524",
        "ARO:3007565",
        "ARO:3007666",
        "ARO:3007667",
    }
    assert {target.filename for target in P.TARGETS.values()} == {
        "antifungal-resistant-cytochrome-p450-enzyme-aro3007522.yaml",
        "triazole-resistant-fungal-cytochrome-p450-enzyme-aro3007523.yaml",
        "candida-spp-erg11-with-mutations-conferring-resistance-to-azole-antibiotics-aro3007524.yaml",
        "aspergillus-spp-cyp51a-with-mutations-conferring-resistance-to-triazoles-antibio-aro3007565.yaml",
        "candida-spp-cyp51a1-with-mutations-conferring-resistance-to-triazoles-and-imidaz-aro3007666.yaml",
        "imidazole-resistant-fungal-cytochrome-p450-enzyme-aro3007667.yaml",
    }


@pytest.mark.parametrize("target", P.TARGETS.values(), ids=lambda target: target.identifier)
def test_p450_records_ground_activity_without_azole_binding_path(
    target: P.Target,
) -> None:
    out, changed = P.enrich_record(_record(target.identifier), target)

    assert changed
    assert _edge_keys(out) == P._expected_edge_keys(target)
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        *(drug_class.node_id for drug_class in target.drug_classes),
        "p450_activity",
        "resistance",
    ]
    graph = out["causal_graphs"][0]
    p450_activity = next(node for node in graph["nodes"] if node["node_id"] == "p450_activity")
    assert p450_activity["grounding"] == "GO:0004497"
    assert {
        (edge["subject"], edge["object"])
        for edge in graph["edges"]
        if edge["subject"] == "p450_activity" or edge["object"] == "p450_activity"
    } == {("determinant", "p450_activity")}


def test_dual_class_cyp51a1_keeps_two_drug_edges() -> None:
    target = P.TARGETS["ARO:3007666"]
    out, changed = P.enrich_record(_record(target.identifier), target)

    assert changed
    drug_edges = [
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if edge["predicate_id"] == "ARO:2000001"
    ]
    assert [edge["object"] for edge in drug_edges] == ["drug0", "drug1"]
    assert [edge["evidence"][1]["reference"] for edge in drug_edges] == [
        "ARO:3007523",
        "ARO:3007667",
    ]


def test_all_output_nodes_are_grounded_and_edges_described() -> None:
    for target in P.TARGETS.values():
        out, changed = P.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        assert all(edge.get("description") for edge in graph["edges"])


def test_drug_edges_are_multi_evidenced() -> None:
    for target in P.TARGETS.values():
        out, changed = P.enrich_record(_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            if edge["predicate_id"] != "ARO:2000001":
                continue
            assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_mutation_edges_inherit_broad_aro_mutation_evidence() -> None:
    out, changed = P.enrich_record(
        _record(P.PARENT_IDENTIFIER),
        P.TARGETS[P.PARENT_IDENTIFIER],
    )

    assert changed
    for edge in out["causal_graphs"][0]["edges"][:3]:
        assert "ARO:3000212" in {item["reference"] for item in edge["evidence"]}


def test_enrich_record_is_idempotent() -> None:
    target = P.TARGETS[P.PARENT_IDENTIFIER]
    once, changed = P.enrich_record(_record(target.identifier), target)
    twice, changed_again = P.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007522, found ARO:3007523"):
        P.enrich_record(_record("ARO:3007523"), P.TARGETS["ARO:3007522"])


def test_unexpected_edges_are_refused() -> None:
    target = P.TARGETS[P.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("p450_activity", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge p450_activity -> resistance"):
        P.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = P.TARGETS[P.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        P.enrich_record(record, target)


def test_missing_edges_are_refused() -> None:
    target = P.TARGETS[P.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "p450_activity"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        P.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = P.TARGETS["ARO:3007523"]
    enriched, changed = P.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = P.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = P.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(P.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", P.TARGETS.values(), ids=lambda target: target.identifier)
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: P.Target,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = P.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == P._expected_edge_keys(target)
