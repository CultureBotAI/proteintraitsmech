from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cstr_teta_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_cstr_teta_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
                "reference": "PMID:38974671",
                "snippet": "MFS antiport seed evidence",
            }
        ],
    }


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "Corynebacterium striatum tetA",
        "definition": R.CSTR_TETA_DEFINITION,
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
                        "label": "Corynebacterium striatum tetA",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic efflux",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "domain",
                        "label": "major facilitator superfamily (MFS) transporter domain",
                        "node_type": "DOMAIN",
                        "grounding": "Pfam:PF07690",
                    },
                    {
                        "node_id": "fold",
                        "label": "MFS general substrate transporter fold",
                        "node_type": "DOMAIN",
                        "grounding": "CATH:1.20.1250.20",
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
                        "domain",
                        "determinant",
                        "part of (domain of the protein)",
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
                        "mech0",
                        "enables (drug efflux)",
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


def _nodes_by_id(record: dict) -> dict[str, dict]:
    return {node["node_id"]: node for node in record["causal_graphs"][0]["nodes"]}


def test_target_set_matches_exact_hidden_no_ignore_cstr_teta_search() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {R.TARGET_IDENTIFIER}
    assert {target.filename for target in R.TARGETS.values()} == {R.TARGET_FILENAME}


def test_cstr_teta_record_drops_unsupported_mfs_domain_and_fold() -> None:
    target = R.TARGETS[R.TARGET_IDENTIFIER]
    out, changed = R.enrich_record(_record(), target)
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == ["determinant", "mech0", "resistance"]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert "domain" not in nodes
    assert "fold" not in nodes


def test_all_edges_are_described_and_replace_mfs_seed_evidence() -> None:
    target = R.TARGETS[R.TARGET_IDENTIFIER]
    out, changed = R.enrich_record(_record(), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        references = {item["reference"] for item in edge["evidence"]}
        assert len(references) > 1
        assert R.TARGET_IDENTIFIER in references
        assert "ARO:0010001" in references
        assert "PMID:38974671" not in references


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.TARGET_IDENTIFIER]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_removes_legacy_uncommitted_history() -> None:
    record = _record()
    record["curation_history"] = [
        {
            "timestamp": "2026-09-06T00:00:00Z",
            "curator": "codex-causal-graph-quality",
            "action": next(iter(R.LEGACY_HISTORY_ACTIONS)),
            "llm_assisted": True,
        }
    ]
    once, _ = R.enrich_record(record, R.TARGETS[R.TARGET_IDENTIFIER])
    record["causal_graphs"] = once["causal_graphs"]

    out, changed = R.enrich_text(
        yaml.safe_dump(record, sort_keys=False),
        R.ARO_DIR / R.TARGET_FILENAME,
    )

    assert changed
    assert next(iter(R.LEGACY_HISTORY_ACTIONS)) not in out
    assert R.HISTORY_ACTION in out


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004639, found ARO:0010001"):
        R.enrich_record(_record("ARO:0010001"), R.TARGETS[R.TARGET_IDENTIFIER])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("domain", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge domain -> unmodeled"):
        R.enrich_record(record, R.TARGETS[R.TARGET_IDENTIFIER])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, R.TARGETS[R.TARGET_IDENTIFIER])
