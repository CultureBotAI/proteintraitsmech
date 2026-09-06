from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fabi_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fabi_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


F = _load()


LABELS = {
    "ARO:3004270": "antibiotic resistant fabI",
    "ARO:3004045": "Escherichia coli fabI mutations conferring resistance to isoniazid and triclosan",
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
                "reference": F.PARENT_IDENTIFIER,
                "snippet": F.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = F.PARENT_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": F.PARENT_EVIDENCE["snippet"],
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
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": LABELS[identifier],
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "drug0",
                        "label": "disinfecting agents and antiseptics",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3005386",
                    },
                    {
                        "node_id": "drug1",
                        "label": "isoniazid-like antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007152",
                    },
                    {
                        "node_id": "enoyl_reduction",
                        "label": "enoyl-acyl carrier reductase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "fa_elongation",
                        "label": "final reduction step of fatty acid elongation",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "inhibition",
                        "label": "Triclosan inhibition of fatty acid biosynthesis",
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
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "drug1",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "enoyl_reduction",
                        "enables (enoyl-ACP reduction)",
                        "RO:0002327",
                    ),
                    _edge(
                        "enoyl_reduction",
                        "fa_elongation",
                        "part of (the final reduction step)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "drug0",
                        "inhibition",
                        "causally upstream of (blocks the reduction step)",
                    ),
                    _edge(
                        "determinant",
                        "inhibition",
                        "negatively regulates (the mutant is no longer inhibited)",
                        "RO:0002212",
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


def test_target_set_matches_fabi_records() -> None:
    assert {target.identifier for target in F.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in F.TARGETS.values()} == {
        "antibiotic-resistant-fabi-aro3004270.yaml",
        (
            "escherichia-coli-fabi-mutations-conferring-resistance-to-"
            "isoniazid-and-triclosan-aro3004045.yaml"
        ),
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_fabi_records_ground_enoyl_reduction_and_remove_fa_elongation(
    identifier: str,
) -> None:
    target = F.TARGETS[identifier]
    out, changed = F.enrich_record(_record(identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "drug1",
        "enoyl_reduction",
        "inhibition",
        "resistance",
    ]
    assert _edge_keys(out) == F.EXPECTED_EDGE_KEYS
    assert "node_id: fa_elongation" not in yaml.safe_dump(out)
    enoyl_reduction = next(
        node
        for node in out["causal_graphs"][0]["nodes"]
        if node["node_id"] == "enoyl_reduction"
    )
    assert enoyl_reduction["grounding"] == "GO:0004318"


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    for target in F.TARGETS.values():
        out, changed = F.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
        assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    for target in F.TARGETS.values():
        out, changed = F.enrich_record(_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_enoyl_reduction_edge_has_go_evidence() -> None:
    for target in F.TARGETS.values():
        out, changed = F.enrich_record(_record(target.identifier), target)

        assert changed
        edge = next(
            edge
            for edge in out["causal_graphs"][0]["edges"]
            if edge["object"] == "enoyl_reduction"
        )
        assert "GO:0004318" in {item["reference"] for item in edge["evidence"]}


def test_isoniazid_has_no_fabi_action_edge() -> None:
    out, changed = F.enrich_record(_record(), F.TARGETS[F.PARENT_IDENTIFIER])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["subject"] != "drug1"
        assert edge["object"] != "drug1" or edge["predicate_id"] == "ARO:2000001"


def test_enrich_record_is_idempotent() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    once, changed = F.enrich_record(_record(target.identifier), target)
    twice, changed_again = F.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004270, found ARO:3004045"):
        F.enrich_record(_record("ARO:3004045"), F.TARGETS["ARO:3004270"])


def test_unexpected_edges_are_refused() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug1", "inhibition"))

    with pytest.raises(ValueError, match="unexpected edge drug1 -> inhibition"):
        F.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        F.enrich_record(record, target)


def test_missing_edges_are_refused() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "drug1"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        F.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = F.TARGETS["ARO:3004045"]
    enriched, changed = F.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = F.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = F.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(F.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", F.TARGETS.values(), ids=lambda target: target.identifier)
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: F.Target,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = F.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == F.EXPECTED_EDGE_KEYS
