"""Safety tests for binding legacy review decisions to resolved-row digests."""

from __future__ import annotations

import hashlib
import importlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
binder = importlib.import_module("bind_uniprot_review_digests")


def _jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _resolved(candidate_id: str, trait_id: str, record_path: str) -> dict:
    row = {
        "candidate_id": candidate_id,
        "trait_id": trait_id,
        "record_path": record_path,
        "source_namespace": trait_id.split(":", 1)[0],
        "protein_id": "UniProtKB:P00001",
        "qualification_status": "QUALIFIED",
        "provider_evidence": [],
    }
    row["resolution_digest"] = hashlib.sha256(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return row


def _decision(candidate: dict, **updates) -> dict:
    row = {
        "candidate_id": candidate["candidate_id"],
        "decision": "REJECTED",
        "record_key": {
            "trait_id": candidate["trait_id"],
            "record_path": candidate["record_path"],
        },
        "reviewer": "Test Curator",
        "reviewed_at": "2026-08-24",
        "review_notes": "Explicit fixture review.",
    }
    row.update(updates)
    return row


def _case(tmp_path: pathlib.Path, monkeypatch) -> dict:
    artifact_root = tmp_path / "reports" / "uniprot-grounding" / "review-batches"
    monkeypatch.setattr(binder, "REVIEW_ARTIFACT_ROOT", artifact_root)
    first = _resolved("candidate-b", "Pfam:PF00002", "fixtures/pfam/b.yaml")
    second = _resolved("candidate-a", "HAMAP:MF_00001", "fixtures/hamap/a.yaml")
    resolved = tmp_path / "inputs" / "batch.resolved.jsonl"
    decisions = tmp_path / "inputs" / "batch.legacy-decisions.jsonl"
    out = artifact_root / "batch.review-decisions.digest-bound.jsonl"
    _jsonl(resolved, [first, second])
    _jsonl(decisions, [_decision(first), _decision(second)])
    return {
        "resolved_rows": [first, second],
        "first": first,
        "second": second,
        "resolved": resolved,
        "decisions": decisions,
        "out": out,
    }


def _args(case: dict, *, apply: bool = False) -> list[str]:
    args = [
        "--resolved",
        str(case["resolved"]),
        "--decisions",
        str(case["decisions"]),
        "--out",
        str(case["out"]),
    ]
    if apply:
        args.append("--apply")
    return args


def test_dry_run_then_apply_binds_and_sorts_legacy_rows(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    assert binder.main(_args(case)) == 0
    assert "would bind 2 decision row(s)" in capsys.readouterr().out
    assert not case["out"].exists()

    assert binder.main(_args(case, apply=True)) == 0
    rows = _rows(case["out"])
    assert [row["candidate_id"] for row in rows] == ["candidate-a", "candidate-b"]
    expected = {row["candidate_id"]: row["resolution_digest"] for row in case["resolved_rows"]}
    assert {row["candidate_id"]: row["resolution_digest"] for row in rows} == expected
    assert all(row["review_notes"] == "Explicit fixture review." for row in rows)


def test_exact_existing_digests_are_idempotently_accepted(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    decisions = _rows(case["decisions"])
    by_id = {row["candidate_id"]: row for row in case["resolved_rows"]}
    for decision in decisions:
        decision["resolution_digest"] = by_id[decision["candidate_id"]]["resolution_digest"]
    _jsonl(case["decisions"], decisions)

    assert binder.main(_args(case, apply=True)) == 0
    assert "0 legacy, 2 already exact" in capsys.readouterr().out
    first = case["out"].read_bytes()
    assert binder.main(_args(case, apply=True)) == 0
    assert case["out"].read_bytes() == first


@pytest.mark.parametrize(
    ("fault", "expected"),
    [
        ("unknown", "absent from the resolved snapshot"),
        ("record_key", "stale record_key"),
        ("duplicate", "duplicates candidate_id"),
        ("existing_digest", "conflicting existing resolution_digest"),
    ],
)
def test_unknown_stale_duplicate_and_conflicting_rows_fail_closed(
    tmp_path, monkeypatch, capsys, fault, expected
):
    case = _case(tmp_path, monkeypatch)
    decisions = _rows(case["decisions"])
    if fault == "unknown":
        decisions[0]["candidate_id"] = "candidate-unknown"
    elif fault == "record_key":
        decisions[0]["record_key"]["trait_id"] = "Pfam:STALE"
    elif fault == "duplicate":
        decisions.append(dict(decisions[0]))
    else:
        decisions[0]["resolution_digest"] = "0" * 64
    _jsonl(case["decisions"], decisions)
    case["out"].parent.mkdir(parents=True, exist_ok=True)
    case["out"].write_text("previous-good\n", encoding="utf-8")

    assert binder.main(_args(case, apply=True)) == 2
    assert expected in capsys.readouterr().err
    assert case["out"].read_text(encoding="utf-8") == "previous-good\n"


def test_tampered_resolved_row_with_old_digest_fails_before_write(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    resolved = _rows(case["resolved"])
    resolved[0]["protein_id"] = "UniProtKB:TAMPERED"
    _jsonl(case["resolved"], resolved)

    assert binder.main(_args(case, apply=True)) == 2
    assert "stale resolution_digest" in capsys.readouterr().err
    assert not case["out"].exists()


@pytest.mark.parametrize("alias", ["resolved", "decisions"])
def test_output_must_not_alias_an_input(tmp_path, monkeypatch, capsys, alias):
    case = _case(tmp_path, monkeypatch)
    case["out"] = case[alias]
    assert binder.main(_args(case, apply=True)) == 2
    assert "must not alias" in capsys.readouterr().err


@pytest.mark.parametrize("fault", ["outside_review_root", "wrong_suffix"])
def test_output_is_restricted_to_explicit_digest_bound_review_artifact(
    tmp_path, monkeypatch, capsys, fault
):
    case = _case(tmp_path, monkeypatch)
    if fault == "outside_review_root":
        case["out"] = tmp_path / "outside.digest-bound.jsonl"
    else:
        case["out"] = binder.REVIEW_ARTIFACT_ROOT / "canonical-review-decisions.jsonl"
    assert binder.main(_args(case, apply=True)) == 2
    error = capsys.readouterr().err
    assert "--out" in error
    assert not case["out"].exists()


@pytest.mark.parametrize("input_name", ["resolved", "decisions"])
def test_inputs_must_not_be_trait_or_data_registry_artifacts(
    tmp_path, monkeypatch, capsys, input_name
):
    case = _case(tmp_path, monkeypatch)
    data_root = tmp_path / "data"
    monkeypatch.setattr(binder, "DATA_ROOT", data_root)
    protected = data_root / "grounding" / case[input_name].name
    protected.parent.mkdir(parents=True, exist_ok=True)
    protected.write_bytes(case[input_name].read_bytes())
    case[input_name] = protected

    assert binder.main(_args(case, apply=True)) == 2
    assert "must not read a trait or data-registry" in capsys.readouterr().err
    assert not case["out"].exists()
