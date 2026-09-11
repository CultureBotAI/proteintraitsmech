from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "audit_causal_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_causal_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


A = _load()
VALID_TYPES = {"LIGAND", "MOLECULAR_FUNCTION", "PROTEIN", "RESIDUE", "STATE"}


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [{"reference": "PMID:1", "snippet": "evidence"}],
    }


def _audit(nodes: list[dict], edges: list[dict]):
    errors: list[str] = []
    warns: list[A.AuditWarning] = []
    stats = {"records": 0, "graphs": 0, "nodes": 0, "edges": 0, "grounded": 0, "snippet_edges": 0}
    A.audit_record(
        {
            "causal_graphs": [
                {
                    "graph_id": "resistance",
                    "nodes": nodes,
                    "edges": edges,
                },
            ],
        },
        "record.yaml",
        VALID_TYPES,
        errors,
        warns,
        stats,
    )
    return errors, warns


def test_described_local_state_nodes_do_not_warn_about_grounding() -> None:
    errors, warns = _audit(
        [
            {
                "node_id": "determinant",
                "label": "determinant",
                "node_type": "PROTEIN",
                "grounding": "ARO:1",
            },
            {
                "node_id": "state",
                "label": "local catalytic state",
                "node_type": "STATE",
                "description": "Local state with no stable external CURIE.",
            },
        ],
        [_edge("determinant", "state")],
    )

    assert errors == []
    assert warns == []


def test_source_local_residue_nodes_do_not_warn_about_grounding() -> None:
    errors, warns = _audit(
        [
            {
                "node_id": "ligand",
                "label": "ligand",
                "node_type": "LIGAND",
                "grounding": "pdb.ligand:ATP",
            },
            {
                "node_id": "pdb_residue",
                "label": (
                    "binding residue E1534 "
                    "(PDB 5ek0 chain A author numbering; no UniProt position asserted)"
                ),
                "node_type": "RESIDUE",
            },
            {
                "node_id": "rhea_reactive_part",
                "label": "L-seryl residue",
                "node_type": "RESIDUE",
                "description": "The reacting group Rhea names inside a generic protein participant.",
            },
        ],
        [
            _edge("pdb_residue", "ligand"),
            _edge("rhea_reactive_part", "ligand"),
        ],
    )

    assert errors == []
    assert warns == []


def test_under_modeled_residue_nodes_still_warn_about_grounding() -> None:
    errors, warns = _audit(
        [
            {
                "node_id": "determinant",
                "label": "determinant",
                "node_type": "PROTEIN",
                "grounding": "ARO:1",
            },
            {
                "node_id": "mutation",
                "label": "mutation locus",
                "node_type": "RESIDUE",
            },
        ],
        [_edge("mutation", "determinant")],
    )

    assert errors == []
    assert len(warns) == 1
    assert "node 'mutation' has no grounding" in str(warns[0])
    assert warns[0].key == "record.yaml|resistance|ungrounded-node|mutation"


def test_warning_keys_pin_warning_identity() -> None:
    edge = _edge("determinant", "activity")
    edge.pop("predicate_id")
    edge["evidence"] = [{"reference": "PMID:1"}]

    errors, warns = _audit(
        [
            {
                "node_id": "determinant",
                "label": "determinant",
                "node_type": "PROTEIN",
                "grounding": "ARO:1",
            },
            {
                "node_id": "activity",
                "label": "local activity",
                "node_type": "MOLECULAR_FUNCTION",
            },
        ],
        [edge],
    )

    assert errors == []
    assert [warning.key for warning in warns] == [
        "record.yaml|resistance|ungrounded-node|activity",
        "record.yaml|resistance|missing-predicate-id|determinant->activity",
        "record.yaml|resistance|missing-snippet|determinant->activity",
    ]


def test_diff_baseline_sees_warning_swaps_at_unchanged_counts() -> None:
    current = {
        "record.yaml|resistance|ungrounded-node|new_node": 1,
    }
    known = {
        "record.yaml|resistance|ungrounded-node|old_node": 1,
    }

    fixed, new = A.diff_baseline(current, known)

    assert fixed == ["record.yaml|resistance|ungrounded-node|old_node"]
    assert new == ["record.yaml|resistance|ungrounded-node|new_node"]


def test_diff_baseline_preserves_duplicate_warning_counts() -> None:
    current = {
        "record.yaml|resistance|missing-snippet|determinant->activity": 2,
    }
    known = {
        "record.yaml|resistance|missing-snippet|determinant->activity": 1,
    }

    fixed, new = A.diff_baseline(current, known)

    assert fixed == []
    assert new == ["record.yaml|resistance|missing-snippet|determinant->activity"]
