from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fuse_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fuse_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


F = _load()


LABELS = {
    F.PARENT_IDENTIFIER: "antibiotic resistant fusE",
    F.CHILD_IDENTIFIER: "Staphylococcus aureus fusE with mutation conferring resistance to fusidic acid",
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
        "definition": (
            F.PARENT_EVIDENCE["snippet"]
            if identifier == F.PARENT_IDENTIFIER
            else (
                "The mutations to the rplF gene encoding riboprotein L6 have "
                "been shown to cause fusidic acid resistance, demonstrating a "
                "potential secondary site of action of the antibiotic that is "
                "blocked through these mutations."
            )
        ),
        "mapping_status": "SEEDED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
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
                        "label": "fusidane antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007153",
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


def test_target_set_matches_fuse_records() -> None:
    assert {target.identifier for target in F.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in F.TARGETS.values()} == {
        "antibiotic-resistant-fuse-aro3003736.yaml",
        "staphylococcus-aureus-fuse-with-mutation-conferring-resistance-to-fusidic-acid-"
        "aro3003737.yaml",
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_fuse_records_add_local_fusidic_acid_action_site(identifier: str) -> None:
    target = F.TARGETS[identifier]
    out, changed = F.enrich_record(_record(identifier), target)

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "blocked_action",
        "resistance",
    ]
    assert _edge_keys(out) == F.EXPECTED_EDGE_KEYS


def test_all_output_edges_are_multi_evidenced_and_described() -> None:
    for target in F.TARGETS.values():
        out, changed = F.enrich_record(_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            assert edge.get("description")
            assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_enrich_record_is_idempotent() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    once, changed = F.enrich_record(_record(target.identifier), target)
    twice, changed_again = F.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003736, found ARO:3003737"):
        F.enrich_record(_record(F.CHILD_IDENTIFIER), F.TARGETS[F.PARENT_IDENTIFIER])


def test_unexpected_edges_are_refused() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("blocked_action", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge blocked_action -> resistance"):
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
        if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing initial edge"):
        F.enrich_record(record, target)


def test_partial_canonical_edges_are_refused() -> None:
    target = F.TARGETS[F.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "drug0",
            "blocked_action",
            "causally upstream of (acts through rplF/L6 secondary site)",
            "RO:0002411",
        )
    )

    with pytest.raises(ValueError, match="partial canonical edge"):
        F.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = F.TARGETS[F.CHILD_IDENTIFIER]
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
