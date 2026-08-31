"""Fail-closed tests for joining partitioned UniProt review decisions."""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
finalizer = importlib.import_module("finalize_uniprot_review_batch")

TSV_FIELDS = (
    "candidate_id",
    "resolution_digest",
    "decision",
    "trait_id",
    "record_path",
    "source_namespace",
    "mapping_method",
    "evidence_source",
    "source_release",
    "uniprot_release",
    "protein_id",
    "reviewer",
    "reviewed_at",
    "review_notes",
)


def _jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _candidate(
    candidate_id: str,
    trait_id: str,
    record_path: str,
    *,
    source: str,
    protein_id: str,
) -> dict:
    row = {
        "candidate_id": candidate_id,
        "trait_id": trait_id,
        "record_path": record_path,
        "source_namespace": source,
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "uniprot_release": "2026_02",
        "protein_id": protein_id,
        "qualification_status": "QUALIFIED",
        "reasons": [],
    }
    row["resolution_digest"] = hashlib.sha256(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return row


def _decision(candidate: dict, decision: str, primary: str | None) -> dict:
    return {
        "candidate_id": candidate["candidate_id"],
        "resolution_digest": candidate["resolution_digest"],
        "decision": decision,
        "primary_review_candidate_id": primary,
        "record_key": {
            "trait_id": candidate["trait_id"],
            "record_path": candidate["record_path"],
        },
        "reviewer": "Test Curator",
        "reviewed_at": "2026-08-24",
        "review_notes": f"Explicit {decision.lower()} fixture decision.",
    }


def _write_review(path: pathlib.Path, candidates: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(
                {
                    **{field: candidate.get(field, "") for field in TSV_FIELDS},
                    "decision": "",
                    "reviewer": "",
                    "reviewed_at": "",
                    "review_notes": "",
                }
            )


def _case(tmp_path: pathlib.Path) -> dict:
    a1 = _candidate(
        "candidate-a-1",
        "Pfam:PF00001",
        "data/traits/sequence/family/pfam/a.yaml",
        source="Pfam",
        protein_id="UniProtKB:P00001",
    )
    a2 = _candidate(
        "candidate-a-2",
        "Pfam:PF00001",
        "data/traits/sequence/family/pfam/a.yaml",
        source="Pfam",
        protein_id="UniProtKB:P00002",
    )
    b1 = _candidate(
        "candidate-b-1",
        "HAMAP:MF_00001",
        "data/traits/sequence/family/hamap/b.yaml",
        source="HAMAP",
        protein_id="UniProtKB:P00003",
    )
    candidates = [b1, a2, a1]
    candidate_path = tmp_path / "resolved.jsonl"
    review_path = tmp_path / "review.tsv"
    part_one = tmp_path / "review-part-one.jsonl"
    part_two = tmp_path / "review-part-two.jsonl"
    decisions_out = tmp_path / "review-decisions.jsonl"
    approved_out = tmp_path / "approved.tsv"
    _jsonl(candidate_path, candidates)
    _write_review(review_path, candidates)
    _jsonl(
        part_one,
        [
            _decision(a1, "REJECTED", a2["candidate_id"]),
            _decision(b1, "REJECTED", None),
        ],
    )
    _jsonl(part_two, [_decision(a2, "APPROVED", a2["candidate_id"])])
    return {
        "candidates": candidates,
        "a1": a1,
        "a2": a2,
        "b1": b1,
        "candidate_path": candidate_path,
        "review_path": review_path,
        "parts": [part_one, part_two],
        "decisions_out": decisions_out,
        "approved_out": approved_out,
    }


def _args(case: dict, *, apply: bool = False) -> list[str]:
    args = [
        "--candidates",
        str(case["candidate_path"]),
        "--review-tsv",
        str(case["review_path"]),
    ]
    for path in case["parts"]:
        args.extend(["--decisions", str(path)])
    args.extend(
        [
            "--decisions-out",
            str(case["decisions_out"]),
            "--approved-out",
            str(case["approved_out"]),
        ]
    )
    if apply:
        args.append("--apply")
    return args


def test_dry_run_then_apply_writes_canonical_ledger_and_completed_tsv(tmp_path, capsys):
    case = _case(tmp_path)
    assert finalizer.main(_args(case)) == 0
    assert "would finalize 3 decisions" in capsys.readouterr().out
    assert not case["decisions_out"].exists()
    assert not case["approved_out"].exists()

    assert finalizer.main(_args(case, apply=True)) == 0
    decision_rows = _rows(case["decisions_out"])
    assert [row["candidate_id"] for row in decision_rows] == [
        "candidate-a-1",
        "candidate-a-2",
        "candidate-b-1",
    ]
    assert [row["decision"] for row in decision_rows] == [
        "REJECTED",
        "APPROVED",
        "REJECTED",
    ]
    assert decision_rows[-1]["primary_review_candidate_id"] is None
    assert [row["resolution_digest"] for row in decision_rows] == [
        case["a1"]["resolution_digest"],
        case["a2"]["resolution_digest"],
        case["b1"]["resolution_digest"],
    ]

    with case["approved_out"].open(encoding="utf-8", newline="") as handle:
        approved = list(csv.DictReader(handle, delimiter="\t"))
    # The completed TSV remains a row-for-row copy of the resolver review order.
    assert [row["candidate_id"] for row in approved] == [
        "candidate-b-1",
        "candidate-a-2",
        "candidate-a-1",
    ]
    assert [row["decision"] for row in approved] == [
        "REJECTED",
        "APPROVED",
        "REJECTED",
    ]
    assert all(row["reviewer"] == "Test Curator" for row in approved)
    assert approved[0]["protein_id"] == "UniProtKB:P00003"

    first = (case["decisions_out"].read_bytes(), case["approved_out"].read_bytes())
    assert finalizer.main(_args(case, apply=True)) == 0
    assert first == (case["decisions_out"].read_bytes(), case["approved_out"].read_bytes())


def test_partial_decision_coverage_is_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    case["parts"] = case["parts"][:1]
    assert finalizer.main(_args(case)) == 2
    assert "do not cover 1 candidate" in capsys.readouterr().err


def test_duplicate_decision_across_partitions_is_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    _jsonl(
        case["parts"][1],
        [
            _decision(case["a2"], "APPROVED", case["a2"]["candidate_id"]),
            _decision(case["a1"], "REJECTED", case["a2"]["candidate_id"]),
        ],
    )
    assert finalizer.main(_args(case)) == 2
    assert "duplicates candidate_id" in capsys.readouterr().err


def test_extra_unknown_decision_is_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    unknown = _candidate(
        "candidate-extra",
        "Pfam:PF99999",
        "data/traits/sequence/family/pfam/extra.yaml",
        source="Pfam",
        protein_id="UniProtKB:P99999",
    )
    _jsonl(
        case["parts"][1],
        [
            _decision(case["a2"], "APPROVED", case["a2"]["candidate_id"]),
            _decision(unknown, "REJECTED", None),
        ],
    )
    assert finalizer.main(_args(case)) == 2
    assert "unknown candidate_id 'candidate-extra'" in capsys.readouterr().err


def test_stale_decision_record_key_is_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    rows[0]["record_key"]["record_path"] = "data/traits/sequence/family/pfam/stale.yaml"
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 2
    assert "stale record_key" in capsys.readouterr().err


@pytest.mark.parametrize("digest", [None, "0" * 64])
def test_decision_must_bind_exact_resolved_digest(tmp_path, capsys, digest):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    if digest is None:
        del rows[0]["resolution_digest"]
    else:
        rows[0]["resolution_digest"] = digest
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 2
    assert "resolution_digest" in capsys.readouterr().err


def test_recomputed_altered_resolved_row_rejects_old_decision_digest(tmp_path, capsys):
    case = _case(tmp_path)
    candidates = list(case["candidates"])
    changed = {**candidates[0], "protein_id": "UniProtKB:CHANGED"}
    changed["resolution_digest"] = hashlib.sha256(
        json.dumps(
            {key: value for key, value in changed.items() if key != "resolution_digest"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    candidates[0] = changed
    _jsonl(case["candidate_path"], candidates)

    assert finalizer.main(_args(case)) == 2
    assert "stale resolution_digest" in capsys.readouterr().err


def test_multiple_approvals_for_one_record_are_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    rows[0] = _decision(case["a1"], "APPROVED", case["a1"]["candidate_id"])
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 2
    assert "multiple approved candidates" in capsys.readouterr().err


def test_bad_primary_candidate_binding_is_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    rows[0]["primary_review_candidate_id"] = case["a1"]["candidate_id"]
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 2
    assert "primary_review_candidate_id must be 'candidate-a-2'" in capsys.readouterr().err


def test_all_rejected_group_may_use_one_consistent_in_group_primary(tmp_path):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    rows[1]["primary_review_candidate_id"] = case["b1"]["candidate_id"]
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 0


@pytest.mark.parametrize("primary", ["candidate-extra", "candidate-b-1"])
def test_all_rejected_group_rejects_out_of_group_or_mixed_primary(tmp_path, capsys, primary):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    # In the first variant the sole primary is outside the record group.  In the
    # second, add a second candidate to the all-rejected group and mix null/non-null.
    if primary == "candidate-b-1":
        b2 = _candidate(
            "candidate-b-2",
            case["b1"]["trait_id"],
            case["b1"]["record_path"],
            source="HAMAP",
            protein_id="UniProtKB:P00004",
        )
        candidates = [*case["candidates"], b2]
        _jsonl(case["candidate_path"], candidates)
        _write_review(case["review_path"], candidates)
        rows.append(_decision(b2, "REJECTED", primary))
    else:
        rows[1]["primary_review_candidate_id"] = primary
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 2
    error = capsys.readouterr().err
    assert "all-rejected record" in error


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("resolution_digest", "0" * 64, "stale resolution_digest"),
        ("source_namespace", "InterPro", "stale source_namespace"),
        ("decision", "APPROVED", "must have blank decision"),
    ],
)
def test_bad_or_prefilled_review_tsv_is_rejected(
    tmp_path, capsys, field: str, value: str, message: str
):
    case = _case(tmp_path)
    with case["review_path"].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    rows[0][field] = value
    with case["review_path"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    case["decisions_out"].write_text("keep decisions\n", encoding="utf-8")
    case["approved_out"].write_text("keep approval\n", encoding="utf-8")
    assert finalizer.main(_args(case, apply=True)) == 2
    assert message in capsys.readouterr().err
    assert case["decisions_out"].read_text(encoding="utf-8") == "keep decisions\n"
    assert case["approved_out"].read_text(encoding="utf-8") == "keep approval\n"


@pytest.mark.parametrize("alias_kind", ["input", "other_output"])
def test_output_aliases_are_rejected(tmp_path, capsys, alias_kind):
    case = _case(tmp_path)
    if alias_kind == "input":
        case["decisions_out"] = case["candidate_path"]
    else:
        case["approved_out"] = case["decisions_out"]
    assert finalizer.main(_args(case, apply=True)) == 2
    error = capsys.readouterr().err
    assert "must not alias" in error or "must be distinct" in error


@pytest.mark.parametrize(
    ("field", "value"),
    [("reviewer", ""), ("reviewed_at", "2026-02-30"), ("review_notes", "   ")],
)
def test_review_metadata_is_required(tmp_path, capsys, field, value):
    case = _case(tmp_path)
    rows = _rows(case["parts"][0])
    rows[0][field] = value
    _jsonl(case["parts"][0], rows)
    assert finalizer.main(_args(case)) == 2
    assert field in capsys.readouterr().err


def test_duplicate_candidate_and_stale_candidate_digest_are_rejected(tmp_path, capsys):
    case = _case(tmp_path)
    rows = list(case["candidates"])
    rows.append(dict(rows[0]))
    _jsonl(case["candidate_path"], rows)
    assert finalizer.main(_args(case)) == 2
    assert "duplicate candidate_id" in capsys.readouterr().err

    rows = list(case["candidates"])
    rows[0] = {**rows[0], "protein_id": "UniProtKB:STALE"}
    _jsonl(case["candidate_path"], rows)
    assert finalizer.main(_args(case)) == 2
    assert "stale resolution_digest" in capsys.readouterr().err
