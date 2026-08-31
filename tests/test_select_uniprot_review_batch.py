"""Determinism and review-protocol tests for UniProt batch selection."""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import pathlib
import sys
from collections import Counter

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
selector = importlib.import_module("select_uniprot_review_batch")


def _candidate(
    source: str,
    number: int,
    *,
    batch: str | None = "ready-local",
    suffix: str = "",
    **updates,
) -> dict:
    trait_id = f"{source}:{number:05d}"
    row = {
        "schema_version": 1,
        "candidate_id": f"candidate-{source}-{number:05d}{suffix}",
        "trait_id": trait_id,
        "record_path": f"fixtures/{source}/{number:05d}.yaml",
        "source_namespace": source,
        "protein_id": f"UniProtKB:P{number:05d}",
        "reviewed": True,
        "scope": "LOCALIZED",
        "intervals": [{"start": 2, "end": 5}],
        "residue_positions": [],
        "source_trait_id": trait_id,
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "reasons": [],
    }
    if batch is not None:
        row["batch"] = batch
    row.update(updates)
    return row


def _jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _decision(candidate: dict, decision: str = "REJECTED", **updates) -> dict:
    row = {
        "candidate_id": candidate["candidate_id"],
        "decision": decision,
        "record_key": {
            "trait_id": candidate["trait_id"],
            "record_path": candidate["record_path"],
        },
    }
    row.update(updates)
    return row


def _review_bundle(
    tmp_path: pathlib.Path,
    name: str,
    candidates: list[dict],
    decisions: list[dict],
    *,
    prior_queue_sha256: str = "a" * 64,
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    candidates_path = tmp_path / f"{name}.candidates.jsonl"
    manifest_path = tmp_path / f"{name}.manifest.json"
    resolved_path = tmp_path / f"{name}.resolved.jsonl"
    decisions_path = tmp_path / f"{name}.review-decisions.jsonl"
    counts = Counter(candidate["record_path"] for candidate in candidates)
    selected = []
    for candidate in candidates:
        row = dict(candidate)
        row["source_batch"] = row.pop("batch", "ready-local")
        row["batch"] = name
        row["batch_id"] = name
        row["record_candidate_count"] = counts[row["record_path"]]
        selected.append(row)
    _jsonl(candidates_path, selected)
    manifest = {
        "schema_version": 4,
        "batch_id": name,
        "source_batch": "ready-local",
        "queue": "reports/uniprot-grounding/candidates.jsonl",
        "queue_sha256": prior_queue_sha256,
        "queue_exact_batch_rows": len(selected),
        "candidate_jsonl_sha256": hashlib.sha256(candidates_path.read_bytes()).hexdigest(),
        "shard_selected_candidate_rows": len(selected),
        "shard_selected_trait_records": len(counts),
        "invariants": {"all_selected_candidate_alternatives_retained": True},
        "downstream_requirements": {
            "all_alternatives_must_receive_an_explicit_review_decision": True
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    resolved = []
    for candidate in selected:
        row = {
            **candidate,
            "qualification_status": "QUALIFIED",
            "provider_evidence": [],
        }
        row["resolution_digest"] = hashlib.sha256(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        resolved.append(row)
    _jsonl(resolved_path, resolved)
    resolution_by_id = {row["candidate_id"]: row["resolution_digest"] for row in resolved}
    bound_decisions = []
    for decision in decisions:
        row = dict(decision)
        row.setdefault("resolution_digest", resolution_by_id.get(row.get("candidate_id"), "0" * 64))
        bound_decisions.append(row)
    _jsonl(decisions_path, bound_decisions)
    return candidates_path, manifest_path, resolved_path, decisions_path


def _exclusion_args(
    *bundles: tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path],
) -> list[str]:
    args: list[str] = []
    for candidates, manifest, resolved, decisions in bundles:
        args.extend(
            [
                "--exclude-reviewed-candidates",
                str(candidates),
                "--exclude-reviewed-manifest",
                str(manifest),
                "--exclude-reviewed-resolved",
                str(resolved),
                "--exclude-decisions",
                str(decisions),
            ]
        )
    return args


def _rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _refresh_resolution_digest(row: dict) -> None:
    row["resolution_digest"] = hashlib.sha256(
        json.dumps(
            {key: value for key, value in row.items() if key != "resolution_digest"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _deferral_case(tmp_path: pathlib.Path, monkeypatch, *, alternatives: int = 1) -> dict:
    monkeypatch.setattr(selector, "REPO_ROOT", tmp_path)
    traits_root = tmp_path / "data" / "traits"
    monkeypatch.setattr(selector, "TRAITS_ROOT", traits_root)
    record_path = "data/traits/sequence/family/alpha/reviewed.yaml"
    record_file = tmp_path / record_path
    record_file.parent.mkdir(parents=True, exist_ok=True)
    record_file.write_text("id: Alpha:00001\nname: reviewed\n", encoding="utf-8")
    record_sha256 = hashlib.sha256(record_file.read_bytes()).hexdigest()
    reviewed = [
        _candidate(
            "Alpha",
            1,
            suffix="" if index == 0 else f"-alternative-{index}",
            protein_id=f"UniProtKB:P{index + 1:05d}",
            record_path=record_path,
            record_sha256=record_sha256,
        )
        for index in range(alternatives)
    ]
    residual = [_candidate("Alpha", number) for number in range(2, 27)]
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path / "output")
    _jsonl(queue, [*reviewed, *residual])
    prior = _review_bundle(
        tmp_path,
        "prior-all-rejected",
        reviewed,
        [_decision(candidate) for candidate in reviewed],
    )
    return {
        "queue": queue,
        "paths": paths,
        "prior": prior,
        "reviewed": reviewed,
        "residual": residual,
        "record_file": record_file,
        "record_sha256": record_sha256,
    }


def _tsv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _paths(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    return (
        tmp_path / "selected.jsonl",
        tmp_path / "manifest.tsv",
        tmp_path / "manifest.json",
    )


def _args(
    queue: pathlib.Path,
    paths: tuple[pathlib.Path, pathlib.Path, pathlib.Path],
    *extra: str,
    apply: bool = True,
) -> list[str]:
    out, tsv, json_path = paths
    args = [
        "--queue",
        str(queue),
        "--batch-id",
        "review-001",
        "--out",
        str(out),
        "--manifest-tsv",
        str(tsv),
        "--manifest-json",
        str(json_path),
        *extra,
    ]
    if apply:
        args.append("--apply")
    return args


def test_source_minima_all_special_classes_and_manifest_binding_are_deterministic(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [_candidate("Alpha", number) for number in range(1, 32)]
    rows.extend(_candidate("Beta", number) for number in range(1, 8))
    rows.extend(
        [
            # A second candidate for one record must be retained while the record
            # group itself is still counted once against the cap.
            _candidate("Alpha", 1, suffix="-unreviewed", reviewed=False),
            _candidate("Alpha", 26, protein_id="UniProtKB:P00026-2"),
            _candidate(
                "Alpha",
                27,
                intervals=[{"start": 2, "end": 3}, {"start": 8, "end": 9}],
            ),
            _candidate("Alpha", 28, residue_positions=[3, 7, 11]),
            _candidate(
                "Alpha",
                29,
                source_trait_id="Alpha:CHILD",
                inheritance_path=["Alpha:CHILD", "Alpha:00029"],
            ),
            _candidate(
                "Alpha",
                30,
                mapping_method="SIFTS_RESIDUE_MAPPING",
                evidence_source="SIFTS",
                mapping_completeness="PARTIAL",
            ),
            _candidate("Alpha", 31, reasons=["ambiguous:fixture"]),
            _candidate("Ignored", 1, batch="later"),
            _candidate("Unlabelled", 1, batch=None),
        ]
    )
    # Replace, rather than duplicate, the six baseline Alpha candidates that were
    # enriched into special fixtures above.
    replacements = {
        row["record_path"]: row
        for row in rows
        if row["source_namespace"] == "Alpha" and 26 <= int(row["trait_id"].split(":")[1]) <= 31
    }
    rows = [
        row
        for row in rows
        if not (
            row["record_path"] in replacements
            and row["candidate_id"].endswith(row["trait_id"].split(":")[1])
        )
    ]
    rows.extend(replacements.values())
    _jsonl(queue, rows)
    queue_sha256 = hashlib.sha256(queue.read_bytes()).hexdigest()

    args = _args(queue, paths, "--max-records", "32")
    assert selector.main(args) == 0
    out, tsv_path, manifest_path = paths
    first_bytes = tuple(path.read_bytes() for path in paths)
    selected = _rows(out)
    assert len(selected) == 33
    assert len({row["record_path"] for row in selected}) == 32
    assert {row["source_namespace"] for row in selected} == {"Alpha", "Beta"}
    assert sum(row["source_namespace"] == "Alpha" for row in selected) == 26
    assert sum(row["source_namespace"] == "Beta" for row in selected) == 7
    assert all(row["batch"] == row["batch_id"] == "review-001" for row in selected)
    assert all(row["source_batch"] == "ready-local" for row in selected)
    assert all(row["review_shard_count"] == 1 for row in selected)
    assert all(row["review_shard_index"] == 0 for row in selected)
    assert all(len(row["record_shard_sha256"]) == 64 for row in selected)
    assert {
        "candidate-Alpha-00001",
        "candidate-Alpha-00001-unreviewed",
    } <= {row["candidate_id"] for row in selected}
    assert all(
        row["record_candidate_count"] == 2 for row in selected if row["trait_id"] == "Alpha:00001"
    )

    by_trait = {row["trait_id"]: row for row in selected}
    assert by_trait["Alpha:00026"]["review_flags"] == ["ISOFORM"]
    assert by_trait["Alpha:00027"]["review_flags"] == ["MULTI_INTERVAL_OR_HIT"]
    assert by_trait["Alpha:00028"]["review_flags"] == ["RESIDUE_SET"]
    assert by_trait["Alpha:00029"]["review_flags"] == ["INHERITANCE"]
    assert by_trait["Alpha:00030"]["review_flags"] == ["PARTIAL_SIFTS", "SIFTS"]
    assert by_trait["Alpha:00031"]["review_flags"] == ["EXPLICIT_AMBIGUITY"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["queue_sha256"] == queue_sha256
    assert manifest["candidate_jsonl_sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    assert manifest["queue_exact_batch_rows"] == 39
    assert manifest["global_source_slice_candidate_rows"] == 39
    assert manifest["global_source_slice_trait_records"] == 38
    assert manifest["shard_available_trait_records"] == 38
    assert manifest["shard_selected_trait_records"] == 32
    assert manifest["shard_selected_candidate_rows"] == 33
    assert manifest["schema_version"] == selector.MANIFEST_SCHEMA_VERSION
    assert manifest["record_shard_algorithm"] == selector.SHARD_ALGORITHM
    assert manifest["shard_count"] == 1
    assert manifest["shard_index"] == 0
    assert manifest["downstream_requirements"] == {
        "all_alternatives_must_receive_an_explicit_review_decision": True,
        "at_most_one_approved_candidate_per_record": True,
    }
    assert all(manifest["invariants"].values())
    assert manifest["shard_available_review_flags"] == manifest["shard_selected_review_flags"]
    manifest_rows = _tsv(tsv_path)
    assert [row["source_namespace"] for row in manifest_rows] == [
        "Alpha",
        "Beta",
        "(TOTAL)",
    ]
    assert all(row["queue_sha256"] == queue_sha256 for row in manifest_rows)
    assert all(row["shard_minimum_satisfied"] == "true" for row in manifest_rows)
    assert all(row["all_shard_special_selected"] == "true" for row in manifest_rows)
    assert manifest_rows[-1]["global_source_slice_trait_records"] == "38"
    assert manifest_rows[-1]["shard_available_trait_records"] == "38"
    assert manifest_rows[-1]["shard_selected_trait_records"] == "32"
    assert manifest_rows[-1]["shard_selected_candidate_rows"] == "33"

    assert selector.main(args) == 0
    assert tuple(path.read_bytes() for path in paths) == first_bytes


def test_planned_ready_local_sources_form_a_stratified_batch_of_exactly_1000(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    large_sources = ("PANTHER", "HAMAP", "PRINTS", "InterPro", "Pfam", "SFLD")
    rows = [_candidate(source, number) for source in large_sources for number in range(1, 181)]
    rows.extend(_candidate("NCBIfam", number) for number in range(1, 25))
    rows.append(_candidate("CDD", 1))
    _jsonl(queue, rows)

    assert selector.main(_args(queue, paths)) == 0
    selected = _rows(paths[0])
    assert len(selected) == 1000
    counts = Counter(row["source_namespace"] for row in selected)
    assert counts["CDD"] == 1
    assert counts["NCBIfam"] == 24
    assert all(counts[source] >= 25 for source in large_sources)


def test_complete_prior_decisions_exclude_whole_groups_and_bind_content_addresses(
    tmp_path,
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [_candidate("Alpha", number) for number in range(2, 31)]
    rows.append(_candidate("Alpha", 31, residue_positions=[7]))
    prior_first = _candidate("Alpha", 1)
    alternative = _candidate("Alpha", 1, suffix="-alternative", protein_id="UniProtKB:Q00001-2")
    _jsonl(queue, rows)
    by_id = {row["candidate_id"]: row for row in rows}
    prior_a = _review_bundle(
        tmp_path,
        "prior-a",
        [prior_first, alternative],
        [
            _decision(prior_first, "APPROVED"),
            _decision(alternative),
        ],
    )
    prior_b = _review_bundle(
        tmp_path,
        "prior-b",
        [by_id["candidate-Alpha-00002"]],
        [_decision(by_id["candidate-Alpha-00002"])],
    )
    prior_c = _review_bundle(
        tmp_path,
        "prior-c",
        [by_id["candidate-Alpha-00003"]],
        [_decision(by_id["candidate-Alpha-00003"], "APPROVED")],
    )

    args = _args(
        queue,
        paths,
        "--max-records",
        "25",
        *_exclusion_args(prior_c, prior_b, prior_a),
    )
    assert selector.main(args) == 0
    first_bytes = tuple(path.read_bytes() for path in paths)
    selected = _rows(paths[0])
    selected_traits = {row["trait_id"] for row in selected}
    assert "Alpha:00001" not in selected_traits
    assert "Alpha:00002" in selected_traits, "all-rejected groups must re-enter review"
    assert "Alpha:00003" not in selected_traits
    assert "Alpha:00031" in selected_traits, "residual special cases remain mandatory"
    assert len({row["record_path"] for row in selected}) == 25

    manifest = json.loads(paths[2].read_text(encoding="utf-8"))
    exclusions = manifest["reviewed_exclusions"]
    assert exclusions["algorithm"] == selector.DECISION_EXCLUSION_ALGORITHM
    assert exclusions["ledger_count"] == 3
    assert exclusions["decision_row_count"] == 4
    assert exclusions["approved_count"] == 2
    assert exclusions["rejected_count"] == 2
    assert len(exclusions["ledger_set_sha256"]) == 64
    assert [item["decisions"]["path"] for item in exclusions["reviewed_batches"]] == [
        prior_a[3].as_posix(),
        prior_b[3].as_posix(),
        prior_c[3].as_posix(),
    ]
    assert {item["decisions"]["sha256"] for item in exclusions["reviewed_batches"]} == {
        hashlib.sha256(prior_a[3].read_bytes()).hexdigest(),
        hashlib.sha256(prior_b[3].read_bytes()).hexdigest(),
        hashlib.sha256(prior_c[3].read_bytes()).hexdigest(),
    }
    for item, prior in zip(
        exclusions["reviewed_batches"], (prior_a, prior_b, prior_c), strict=True
    ):
        assert len(item["reviewed_candidates"]["sha256"]) == 64
        assert len(item["review_manifest"]["sha256"]) == 64
        assert item["reviewed_resolved"] == {
            "path": prior[2].as_posix(),
            "sha256": hashlib.sha256(prior[2].read_bytes()).hexdigest(),
            "candidate_rows": len(_rows(prior[2])),
        }
        assert not item["review_manifest"]["prior_queue_matches_current"]
    assert exclusions["projection"] == {
        "fully_decided_candidate_rows": 4,
        "fully_decided_trait_records": 3,
        "approved_candidate_rows": 3,
        "approved_trait_records": 2,
        "already_absent_candidate_rows": 2,
        "already_absent_trait_records": 1,
        "current_exact_batch_excluded_candidate_rows": 1,
        "current_exact_batch_excluded_trait_records": 1,
        "stale_candidate_rows": 0,
        "stale_trait_records": 0,
    }
    all_rejected = exclusions["all_rejected_not_excluded"]
    assert all_rejected["candidate_rows"] == 1
    assert all_rejected["trait_records"] == 1
    assert all_rejected["current_exact_batch_candidate_rows"] == 1
    assert all_rejected["current_exact_batch_trait_records"] == 1
    assert len(all_rejected["candidate_ids_sha256"]) == 64
    assert len(all_rejected["record_keys_sha256"]) == 64
    assert exclusions["exact_batch"] == {
        "excluded_candidate_rows": 1,
        "excluded_trait_records": 1,
    }
    assert exclusions["source_slice"] == exclusions["exact_batch"]
    assert exclusions["shard"] == exclusions["exact_batch"]
    assert manifest["pre_exclusion_source_slice_candidate_rows"] == 30
    assert manifest["pre_exclusion_source_slice_trait_records"] == 30
    assert manifest["global_source_slice_candidate_rows"] == 29
    assert manifest["global_source_slice_trait_records"] == 29
    assert manifest["shard_available_special_records"] == 1
    assert manifest["shard_selected_special_records"] == 1
    assert all(manifest["invariants"].values())

    total = _tsv(paths[1])[-1]
    assert total["decision_ledger_set_sha256"] == exclusions["ledger_set_sha256"]
    assert total["decision_ledger_count"] == "3"
    assert total["decision_row_count"] == "4"
    assert total["already_absent_reviewed_trait_records"] == "1"
    assert total["all_rejected_not_excluded_trait_records"] == "1"
    assert total["all_rejected_record_keys_sha256"] == all_rejected["record_keys_sha256"]
    assert total["stale_reviewed_trait_records"] == "0"
    assert total["excluded_source_slice_trait_records"] == "1"
    assert total["excluded_shard_candidate_rows"] == "1"

    # Argument order cannot alter the content-addressed ledger set or selection.
    reversed_args = _args(
        queue,
        paths,
        "--max-records",
        "25",
        *_exclusion_args(prior_a, prior_b, prior_c),
    )
    assert selector.main(reversed_args) == 0
    assert tuple(path.read_bytes() for path in paths) == first_bytes


def test_repeated_complete_all_rejected_histories_coalesce_and_are_order_deterministic(
    tmp_path,
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    first = _candidate("Alpha", 1)
    old_alternative = _candidate(
        "Alpha", 1, suffix="-old-alternative", protein_id="UniProtKB:Q00001"
    )
    new_alternative = _candidate(
        "Alpha", 1, suffix="-new-alternative", protein_id="UniProtKB:Q99999"
    )
    _jsonl(queue, [first, new_alternative, *[_candidate("Alpha", n) for n in range(2, 27)]])
    prior_z = _review_bundle(
        tmp_path,
        "prior-z",
        [first, old_alternative],
        [_decision(first), _decision(old_alternative)],
    )
    prior_a = _review_bundle(
        tmp_path,
        "prior-a",
        [first, new_alternative],
        [_decision(first), _decision(new_alternative)],
    )

    args = _args(
        queue,
        paths,
        *_exclusion_args(prior_z, prior_a),
        "--max-records",
        "25",
    )
    assert selector.main(args) == 0
    first_bytes = tuple(path.read_bytes() for path in paths)
    assert {first["candidate_id"], new_alternative["candidate_id"]} <= {
        row["candidate_id"] for row in _rows(paths[0])
    }

    exclusions = json.loads(paths[2].read_text(encoding="utf-8"))["reviewed_exclusions"]
    assert exclusions["decision_row_count"] == 4
    assert exclusions["unique_decided_candidate_rows"] == 3
    assert exclusions["approved_count"] == 0
    assert exclusions["rejected_count"] == 4
    assert exclusions["projection"]["fully_decided_candidate_rows"] == 3
    assert exclusions["projection"]["fully_decided_trait_records"] == 1
    repeated = exclusions["repeated_all_rejected"]
    assert repeated["trait_records"] == 1
    assert repeated["adjudication_count"] == 2
    assert repeated["decision_rows"] == 4
    assert repeated["unique_candidate_rows"] == 3
    assert repeated["duplicate_decision_rows"] == 1
    assert len(repeated["record_keys_sha256"]) == 64
    assert len(repeated["history_sha256"]) == 64
    assert len(repeated["records"]) == 1
    record = repeated["records"][0]
    assert record["trait_id"] == first["trait_id"]
    assert record["record_path"] == first["record_path"]
    assert record["adjudication_count"] == 2
    assert len(record["adjudication_digests"]) == 2
    assert len(set(record["adjudication_digests"])) == 2
    assert len(record["adjudication_set_sha256"]) == 64
    assert exclusions["all_rejected_not_excluded"]["candidate_rows"] == 3
    assert exclusions["all_rejected_not_excluded"]["current_exact_batch_candidate_rows"] == 2

    total = _tsv(paths[1])[-1]
    assert total["decision_row_count"] == "4"
    assert total["unique_decided_candidate_rows"] == "3"
    assert total["repeated_all_rejected_trait_records"] == "1"
    assert total["repeated_all_rejected_adjudications"] == "2"
    assert total["repeated_all_rejected_decision_rows"] == "4"
    assert total["repeated_all_rejected_duplicate_decision_rows"] == "1"
    assert total["repeated_all_rejected_history_sha256"] == repeated["history_sha256"]

    reversed_args = _args(
        queue,
        paths,
        *_exclusion_args(prior_a, prior_z),
        "--max-records",
        "25",
    )
    assert selector.main(reversed_args) == 0
    assert tuple(path.read_bytes() for path in paths) == first_bytes


@pytest.mark.parametrize(
    ("approved_name", "rejected_name"),
    [
        ("prior-a-approved", "prior-z-rejected"),
        ("prior-z-approved", "prior-a-rejected"),
    ],
)
def test_one_approved_adjudication_terminally_resolves_all_rejected_history(
    tmp_path, approved_name, rejected_name
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    first = _candidate("Alpha", 1)
    old_alternative = _candidate(
        "Alpha", 1, suffix="-old-alternative", protein_id="UniProtKB:Q00001"
    )
    new_alternative = _candidate(
        "Alpha", 1, suffix="-new-alternative", protein_id="UniProtKB:Q99999"
    )
    _jsonl(queue, [first, new_alternative, *[_candidate("Alpha", n) for n in range(2, 28)]])
    rejected = _review_bundle(
        tmp_path,
        rejected_name,
        [first, old_alternative],
        [_decision(first), _decision(old_alternative)],
    )
    approved = _review_bundle(
        tmp_path,
        approved_name,
        [first, new_alternative],
        [_decision(first, "APPROVED"), _decision(new_alternative)],
    )

    args = _args(
        queue,
        paths,
        *_exclusion_args(rejected, approved),
        "--defer-unchanged-all-rejected",
        "--max-records",
        "25",
    )
    assert selector.main(args) == 0
    first_bytes = tuple(path.read_bytes() for path in paths)
    assert first["trait_id"] not in {row["trait_id"] for row in _rows(paths[0])}

    exclusions = json.loads(paths[2].read_text(encoding="utf-8"))["reviewed_exclusions"]
    assert exclusions["decision_row_count"] == 4
    assert exclusions["unique_decided_candidate_rows"] == 3
    assert exclusions["approved_count"] == 1
    assert exclusions["rejected_count"] == 3
    assert exclusions["repeated_all_rejected"]["trait_records"] == 0
    assert exclusions["all_rejected_not_excluded"]["trait_records"] == 0
    assert exclusions["all_rejected_deferral"]["evaluated_trait_records"] == 0
    assert exclusions["exact_batch"] == {
        "excluded_candidate_rows": 2,
        "excluded_trait_records": 1,
    }
    resolved = exclusions["resolved_all_rejected_histories"]
    assert resolved["trait_records"] == 1
    assert resolved["superseded_all_rejected_adjudications"] == 1
    assert resolved["superseded_all_rejected_decision_rows"] == 2
    assert resolved["approved_adjudications"] == 1
    assert resolved["approved_decision_rows"] == 2
    assert len(resolved["record_keys_sha256"]) == 64
    assert len(resolved["history_sha256"]) == 64
    record = resolved["records"][0]
    assert record["trait_id"] == first["trait_id"]
    assert record["record_path"] == first["record_path"]
    assert len(record["record_history_sha256"]) == 64
    assert [item["batch_id"] for item in record["superseded_all_rejected_adjudications"]] == [
        rejected_name
    ]
    approved_projection = record["approved_adjudication"]
    assert approved_projection["batch_id"] == approved_name
    assert approved_projection["approved_candidate_id"] == first["candidate_id"]
    assert len(approved_projection["approved_resolution_digest"]) == 64
    assert len(approved_projection["candidate_ids_sha256"]) == 64
    total = _tsv(paths[1])[-1]
    assert total["resolved_all_rejected_trait_records"] == "1"
    assert total["resolved_all_rejected_superseded_adjudications"] == "1"
    assert total["resolved_all_rejected_superseded_decision_rows"] == "2"
    assert total["resolved_all_rejected_approved_adjudications"] == "1"
    assert total["resolved_all_rejected_approved_decision_rows"] == "2"
    assert total["resolved_all_rejected_history_sha256"] == resolved["history_sha256"]

    reversed_args = _args(
        queue,
        paths,
        *_exclusion_args(approved, rejected),
        "--defer-unchanged-all-rejected",
        "--max-records",
        "25",
    )
    assert selector.main(reversed_args) == 0
    assert tuple(path.read_bytes() for path in paths) == first_bytes


@pytest.mark.parametrize(
    ("fault", "expected"),
    [
        ("partial", "partial decisions"),
        ("stale_digest", "stale resolution_digest for candidate_id"),
        ("identity_conflict", "duplicate decision"),
    ],
)
def test_repeated_review_history_rejects_partial_stale_or_identity_conflict(
    tmp_path, capsys, fault, expected
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    first = _candidate("Alpha", 1)
    alternative = _candidate("Alpha", 1, suffix="-alternative", protein_id="UniProtKB:Q00001")
    _jsonl(queue, [_candidate("Alpha", number) for number in range(3, 29)])
    first_decisions = [_decision(first), _decision(alternative)]
    second_candidates = [first, alternative]
    second_decisions = [_decision(first), _decision(alternative)]
    if fault == "partial":
        second_decisions.pop()
    elif fault == "identity_conflict":
        conflict = _candidate("Beta", 2)
        conflict["candidate_id"] = first["candidate_id"]
        second_candidates = [conflict]
        second_decisions = [_decision(conflict)]
    prior_a = _review_bundle(tmp_path, "prior-a", [first, alternative], first_decisions)
    prior_b = _review_bundle(tmp_path, "prior-b", second_candidates, second_decisions)
    if fault == "stale_digest":
        decisions = _rows(prior_b[3])
        decisions[0]["resolution_digest"] = "f" * 64
        _jsonl(prior_b[3], decisions)

    assert (
        selector.main(
            _args(
                queue,
                paths,
                *_exclusion_args(prior_b, prior_a),
                "--max-records",
                "25",
            )
        )
        == 2
    )
    assert expected in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


@pytest.mark.parametrize("same_primary", [True, False])
def test_repeated_review_history_rejects_a_second_approved_adjudication(
    tmp_path, capsys, same_primary
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    first = _candidate("Alpha", 1)
    alternative = _candidate("Alpha", 1, suffix="-alternative", protein_id="UniProtKB:Q00001")
    _jsonl(queue, [first, alternative, *[_candidate("Alpha", number) for number in range(2, 28)]])
    prior_a = _review_bundle(
        tmp_path,
        "prior-a",
        [first, alternative],
        [_decision(first, "APPROVED"), _decision(alternative)],
    )
    prior_b = _review_bundle(
        tmp_path,
        "prior-b",
        [first, alternative],
        [
            _decision(first, "APPROVED" if same_primary else "REJECTED"),
            _decision(alternative, "REJECTED" if same_primary else "APPROVED"),
        ],
    )

    assert (
        selector.main(
            _args(
                queue,
                paths,
                *_exclusion_args(prior_b, prior_a),
                "--max-records",
                "25",
            )
        )
        == 2
    )
    assert "2 independently complete approved adjudications" in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_repeated_all_rejected_deferral_checks_every_bound_record_hash(
    tmp_path, monkeypatch, capsys
):
    case = _deferral_case(tmp_path, monkeypatch, alternatives=2)
    second = _review_bundle(
        tmp_path,
        "prior-second",
        case["reviewed"],
        [_decision(candidate) for candidate in case["reviewed"]],
    )
    args = _args(
        case["queue"],
        case["paths"],
        *_exclusion_args(second, case["prior"]),
        "--defer-unchanged-all-rejected",
        "--max-records",
        "25",
    )
    assert selector.main(args) == 0
    manifest = json.loads(case["paths"][2].read_text(encoding="utf-8"))
    exclusions = manifest["reviewed_exclusions"]
    assert exclusions["repeated_all_rejected"]["trait_records"] == 1
    assert exclusions["all_rejected_deferral"]["deferred_unchanged"]["trait_records"] == 1
    assert exclusions["all_rejected_deferral"]["evaluated_trait_records"] == 1

    resolved = _rows(second[2])
    for row in resolved:
        row["record_sha256"] = "f" * 64
        _refresh_resolution_digest(row)
    _jsonl(second[2], resolved)
    decisions = _rows(second[3])
    digest_by_id = {row["candidate_id"]: row["resolution_digest"] for row in resolved}
    for decision in decisions:
        decision["resolution_digest"] = digest_by_id[decision["candidate_id"]]
    _jsonl(second[3], decisions)
    for path in case["paths"]:
        path.unlink()

    assert selector.main(args) == 2
    assert "across alternatives or repeated adjudications" in capsys.readouterr().err
    assert all(not path.exists() for path in case["paths"])


@pytest.mark.parametrize(
    "fault, expected",
    [
        ("partial", "partial decisions"),
        ("duplicate", "duplicate decision"),
        ("stale_record_key", "stale record_key"),
        ("stale_candidate", "stale candidate alternatives"),
        ("unknown_candidate", "unknown decision candidate_id"),
        ("unknown_decision", "unknown decision"),
        ("multiple_approved", "2 APPROVED candidates"),
    ],
)
def test_decision_ledgers_reject_partial_duplicate_stale_and_unknown_rows(
    tmp_path, capsys, fault, expected
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    first = _candidate("Alpha", 1)
    second = _candidate("Alpha", 1, suffix="-alternative", protein_id="UniProtKB:Q00001")
    _jsonl(queue, [first, second, _candidate("Alpha", 2)])
    decisions = [_decision(first), _decision(second)]
    if fault == "partial":
        decisions.pop()
    elif fault == "duplicate":
        decisions.append(_decision(first))
    elif fault == "stale_record_key":
        decisions[0]["record_key"]["trait_id"] = "Alpha:STALE"
    elif fault == "stale_candidate":
        decisions[0]["decision"] = "APPROVED"
    elif fault == "unknown_candidate":
        decisions[0]["candidate_id"] = "candidate-Unknown-99999"
        decisions[0]["record_key"] = {
            "trait_id": "Unknown:99999",
            "record_path": "fixtures/Unknown/99999.yaml",
        }
    elif fault == "unknown_decision":
        decisions[0]["decision"] = "PENDING"
    elif fault == "multiple_approved":
        decisions[0]["decision"] = "APPROVED"
        decisions[1]["decision"] = "APPROVED"
    prior = _review_bundle(tmp_path, "prior", [first, second], decisions)
    if fault == "stale_candidate":
        changed = dict(second)
        changed["candidate_id"] = "candidate-Alpha-00001-new-alternative"
        _jsonl(queue, [first, changed, _candidate("Alpha", 2)])

    assert selector.main(_args(queue, paths, *_exclusion_args(prior), "--max-records", "1")) == 2
    assert expected in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_all_rejected_group_reenters_even_when_current_alternatives_changed(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    prior_first = _candidate("Alpha", 1)
    prior_second = _candidate("Alpha", 1, suffix="-old-alternative", protein_id="UniProtKB:Q00001")
    changed = _candidate("Alpha", 1, suffix="-new-alternative", protein_id="UniProtKB:Q99999")
    _jsonl(queue, [prior_first, changed])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [prior_first, prior_second],
        [_decision(prior_first), _decision(prior_second)],
    )

    assert selector.main(_args(queue, paths, *_exclusion_args(prior), "--max-records", "1")) == 0
    assert {row["candidate_id"] for row in _rows(paths[0])} == {
        prior_first["candidate_id"],
        changed["candidate_id"],
    }
    exclusions = json.loads(paths[2].read_text(encoding="utf-8"))["reviewed_exclusions"]
    assert exclusions["exact_batch"]["excluded_trait_records"] == 0
    assert exclusions["all_rejected_not_excluded"]["trait_records"] == 1
    assert exclusions["all_rejected_not_excluded"]["current_exact_batch_trait_records"] == 1


def test_opt_in_defers_unchanged_all_rejected_group_and_binds_manifest(tmp_path, monkeypatch):
    case = _deferral_case(tmp_path, monkeypatch)
    args = _args(
        case["queue"],
        case["paths"],
        *_exclusion_args(case["prior"]),
        "--defer-unchanged-all-rejected",
        "--max-records",
        "25",
    )
    assert selector.main(args) == 0
    first_bytes = tuple(path.read_bytes() for path in case["paths"])
    assert case["reviewed"][0]["candidate_id"] not in {
        row["candidate_id"] for row in _rows(case["paths"][0])
    }

    manifest = json.loads(case["paths"][2].read_text(encoding="utf-8"))
    assert manifest["defer_unchanged_all_rejected"] is True
    deferral = manifest["reviewed_exclusions"]["all_rejected_deferral"]
    assert deferral["enabled"] is True
    assert deferral["evaluated_trait_records"] == 1
    assert len(deferral["evaluated_state_sha256"]) == 64
    assert deferral["deferred_unchanged"]["trait_records"] == 1
    assert deferral["deferred_unchanged"]["candidate_rows"] == 1
    assert deferral["deferred_unchanged"]["reviewed_candidate_rows"] == 1
    assert deferral["reopened_changed"]["trait_records"] == 0
    assert manifest["reviewed_exclusions"]["all_rejected_not_excluded"] == {
        "candidate_rows": 0,
        "trait_records": 0,
        "candidate_ids_sha256": selector._identity_set_sha256([]),
        "record_keys_sha256": selector._identity_set_sha256([]),
        "current_exact_batch_candidate_rows": 0,
        "current_exact_batch_trait_records": 0,
    }
    assert all(manifest["invariants"].values())

    total = _tsv(case["paths"][1])[-1]
    assert total["defer_unchanged_all_rejected"] == "true"
    assert total["deferred_unchanged_trait_records"] == "1"
    assert total["deferred_unchanged_candidate_rows"] == "1"
    assert total["reopened_changed_trait_records"] == "0"
    assert len(total["all_rejected_deferral_sha256"]) == 64

    assert selector.main(args) == 0
    assert tuple(path.read_bytes() for path in case["paths"]) == first_bytes


def test_exact_current_record_change_explicitly_reopens_all_rejected_group(tmp_path, monkeypatch):
    case = _deferral_case(tmp_path, monkeypatch)
    case["record_file"].write_text("id: Alpha:00001\nname: reviewed changed\n", encoding="utf-8")
    assert (
        selector.main(
            _args(
                case["queue"],
                case["paths"],
                *_exclusion_args(case["prior"]),
                "--defer-unchanged-all-rejected",
                "--max-records",
                "25",
            )
        )
        == 0
    )
    assert case["reviewed"][0]["candidate_id"] in {
        row["candidate_id"] for row in _rows(case["paths"][0])
    }
    manifest = json.loads(case["paths"][2].read_text(encoding="utf-8"))
    deferral = manifest["reviewed_exclusions"]["all_rejected_deferral"]
    assert deferral["deferred_unchanged"]["trait_records"] == 0
    assert deferral["reopened_changed"]["trait_records"] == 1
    assert deferral["reopened_changed"]["candidate_rows"] == 1
    assert deferral["reopened_changed"]["state_sha256"] != selector._identity_set_sha256([])
    assert manifest["reviewed_exclusions"]["all_rejected_not_excluded"]["trait_records"] == 1
    assert all(manifest["invariants"].values())


def test_default_behavior_reopens_all_rejected_without_reading_trait_file(tmp_path, monkeypatch):
    case = _deferral_case(tmp_path, monkeypatch)
    case["record_file"].unlink()
    assert (
        selector.main(
            _args(
                case["queue"],
                case["paths"],
                *_exclusion_args(case["prior"]),
                "--max-records",
                "25",
            )
        )
        == 0
    )
    assert case["reviewed"][0]["candidate_id"] in {
        row["candidate_id"] for row in _rows(case["paths"][0])
    }
    manifest = json.loads(case["paths"][2].read_text(encoding="utf-8"))
    deferral = manifest["reviewed_exclusions"]["all_rejected_deferral"]
    assert manifest["defer_unchanged_all_rejected"] is False
    assert deferral["enabled"] is False
    assert deferral["evaluated_trait_records"] == 0
    assert deferral["deferred_unchanged"]["trait_records"] == 0
    assert deferral["reopened_changed"]["trait_records"] == 0
    assert manifest["reviewed_exclusions"]["all_rejected_not_excluded"]["trait_records"] == 1
    assert all(manifest["invariants"].values())


def test_deferral_flag_does_not_change_approved_group_exclusion(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    approved = _candidate("Alpha", 1)
    residual = [_candidate("Alpha", number) for number in range(2, 27)]
    _jsonl(queue, [approved, *residual])
    prior = _review_bundle(
        tmp_path,
        "prior-approved",
        [approved],
        [_decision(approved, "APPROVED")],
    )

    assert (
        selector.main(
            _args(
                queue,
                paths,
                *_exclusion_args(prior),
                "--defer-unchanged-all-rejected",
                "--max-records",
                "25",
            )
        )
        == 0
    )
    assert approved["candidate_id"] not in {row["candidate_id"] for row in _rows(paths[0])}
    manifest = json.loads(paths[2].read_text(encoding="utf-8"))
    assert manifest["reviewed_exclusions"]["projection"]["approved_trait_records"] == 1
    assert manifest["reviewed_exclusions"]["all_rejected_deferral"]["evaluated_trait_records"] == 0
    assert all(manifest["invariants"].values())


@pytest.mark.parametrize(
    ("fault", "expected"),
    [
        ("stale_resolved_digest", "stale resolution_digest"),
        ("invalid_record_hash", "lacks a valid resolved record_sha256"),
        ("mixed_record_hash", "inconsistent resolved record_sha256"),
        ("missing_current_file", "missing or unreadable"),
        ("mixed_current_identity", "mixed current identity"),
    ],
)
def test_all_rejected_deferral_fails_closed_on_untrusted_record_state(
    tmp_path, monkeypatch, capsys, fault, expected
):
    case = _deferral_case(
        tmp_path,
        monkeypatch,
        alternatives=2 if fault == "mixed_record_hash" else 1,
    )
    if fault in {"stale_resolved_digest", "invalid_record_hash", "mixed_record_hash"}:
        resolved = _rows(case["prior"][2])
        if fault == "stale_resolved_digest":
            resolved[0]["record_sha256"] = "0" * 64
        elif fault == "invalid_record_hash":
            resolved[0]["record_sha256"] = "not-a-sha256"
            _refresh_resolution_digest(resolved[0])
        else:
            resolved[1]["record_sha256"] = "f" * 64
            _refresh_resolution_digest(resolved[1])
        _jsonl(case["prior"][2], resolved)
        if fault != "stale_resolved_digest":
            decisions = _rows(case["prior"][3])
            digest_by_id = {row["candidate_id"]: row["resolution_digest"] for row in resolved}
            for decision in decisions:
                decision["resolution_digest"] = digest_by_id[decision["candidate_id"]]
            _jsonl(case["prior"][3], decisions)
    elif fault == "missing_current_file":
        case["record_file"].unlink()
    else:
        queue_rows = _rows(case["queue"])
        queue_rows[0]["trait_id"] = "Alpha:MIXED"
        _jsonl(case["queue"], queue_rows)

    assert (
        selector.main(
            _args(
                case["queue"],
                case["paths"],
                *_exclusion_args(case["prior"]),
                "--defer-unchanged-all-rejected",
                "--max-records",
                "25",
            )
        )
        == 2
    )
    assert expected in capsys.readouterr().err
    assert all(not path.exists() for path in case["paths"])


@pytest.mark.parametrize(
    "fault, expected",
    [
        ("candidate_hash", "does not bind the exact candidate snapshot"),
        ("queue_binding", "valid bound queue_sha256"),
    ],
)
def test_review_companion_manifest_must_bind_candidates_and_prior_queue(
    tmp_path, capsys, fault, expected
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    candidate = _candidate("Alpha", 1)
    _jsonl(queue, [candidate])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [candidate],
        [_decision(candidate, "APPROVED")],
    )
    if fault == "candidate_hash":
        prior[0].write_bytes(prior[0].read_bytes() + b"\n")
    else:
        manifest = json.loads(prior[1].read_text(encoding="utf-8"))
        manifest["queue_sha256"] = "not-a-content-address"
        prior[1].write_text(json.dumps(manifest), encoding="utf-8")

    assert selector.main(_args(queue, paths, *_exclusion_args(prior))) == 2
    assert expected in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_altered_resolved_row_with_old_digest_is_rejected(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    reviewed = _candidate("Alpha", 1)
    _jsonl(queue, [reviewed, _candidate("Alpha", 2)])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [reviewed],
        [_decision(reviewed, "APPROVED")],
    )
    resolved = _rows(prior[2])
    resolved[0]["protein_id"] = "UniProtKB:ALTERED"
    _jsonl(prior[2], resolved)

    assert selector.main(_args(queue, paths, *_exclusion_args(prior))) == 2
    assert "stale resolution_digest" in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_recomputed_altered_resolved_row_rejects_old_decision_digest(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    reviewed = _candidate("Alpha", 1)
    _jsonl(queue, [reviewed, _candidate("Alpha", 2)])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [reviewed],
        [_decision(reviewed, "APPROVED")],
    )
    resolved = _rows(prior[2])
    resolved[0]["protein_id"] = "UniProtKB:ALTERED"
    resolved[0]["resolution_digest"] = hashlib.sha256(
        json.dumps(
            {key: value for key, value in resolved[0].items() if key != "resolution_digest"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    _jsonl(prior[2], resolved)

    assert selector.main(_args(queue, paths, *_exclusion_args(prior))) == 2
    assert "stale resolution_digest for candidate_id" in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_mixed_candidate_and_resolved_snapshots_are_rejected(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    reviewed = _candidate("Alpha", 1)
    _jsonl(queue, [reviewed, _candidate("Alpha", 2)])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [reviewed],
        [_decision(reviewed, "APPROVED")],
    )
    resolved = _rows(prior[2])
    resolved[0]["record_path"] = "fixtures/Alpha/mixed.yaml"
    resolved[0]["resolution_digest"] = hashlib.sha256(
        json.dumps(
            {key: value for key, value in resolved[0].items() if key != "resolution_digest"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    _jsonl(prior[2], resolved)

    assert selector.main(_args(queue, paths, *_exclusion_args(prior))) == 2
    assert "mixed record identity" in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


@pytest.mark.parametrize("extra_resolved", [False, True])
def test_reviewed_exclusions_require_matching_artifact_quadruples(tmp_path, capsys, extra_resolved):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    reviewed = _candidate("Alpha", 1)
    _jsonl(queue, [reviewed, _candidate("Alpha", 2)])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [reviewed],
        [_decision(reviewed, "APPROVED")],
    )
    exclusion_args = _exclusion_args(prior)
    resolved_flag = exclusion_args.index("--exclude-reviewed-resolved")
    if extra_resolved:
        exclusion_args.extend(
            ["--exclude-reviewed-resolved", str(tmp_path / "unexpected.resolved.jsonl")]
        )
    else:
        del exclusion_args[resolved_flag : resolved_flag + 2]

    assert selector.main(_args(queue, paths, *exclusion_args)) == 2
    error = capsys.readouterr().err
    assert "resolved + decisions quadruple" in error
    assert "--exclude-reviewed-resolved=" in error
    assert all(not path.exists() for path in paths)


def test_exact_resolved_snapshot_accepts_subset_decisions_by_complete_record_group(
    tmp_path,
):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    first = _candidate("Alpha", 1)
    alternative = _candidate("Alpha", 1, suffix="-alternative", protein_id="UniProtKB:Q00001")
    undecided = _candidate("Alpha", 2)
    _jsonl(queue, [first, alternative, undecided])
    prior = _review_bundle(
        tmp_path,
        "prior",
        [first, alternative, undecided],
        [_decision(first, "APPROVED"), _decision(alternative)],
    )

    assert selector.main(_args(queue, paths, *_exclusion_args(prior), "--max-records", "1")) == 0
    assert {row["candidate_id"] for row in _rows(paths[0])} == {undecided["candidate_id"]}


def test_mandatory_special_cases_over_cap_fail_without_replacing_outputs(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [
        _candidate("Alpha", number, protein_id=f"UniProtKB:P{number:05d}-2")
        for number in range(1, 27)
    ]
    _jsonl(queue, rows)
    for path in paths:
        path.write_text("previous-good\n", encoding="utf-8")

    assert selector.main(_args(queue, paths, "--max-records", "25")) == 2
    assert "exceeding --max-records=25" in capsys.readouterr().err
    assert all(path.read_text(encoding="utf-8") == "previous-good\n" for path in paths)


def test_source_slice_and_input_batch_matching_are_exact(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [_candidate("Alpha", number) for number in range(1, 31)]
    rows.extend(_candidate("Alphabet", number) for number in range(1, 31))
    rows.append(_candidate("Alpha", 31, batch="ready-local-extra"))
    rows.append(_candidate("Alpha", 32, batch=None))
    _jsonl(queue, rows)

    assert selector.main(_args(queue, paths, "--source", "Alpha", "--max-records", "25")) == 0
    selected = _rows(paths[0])
    assert len(selected) == 25
    assert {row["source_namespace"] for row in selected} == {"Alpha"}
    assert all(row["trait_id"] not in {"Alpha:00031", "Alpha:00032"} for row in selected)


def test_dry_run_computes_selection_but_writes_nothing(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    _jsonl(queue, [_candidate("Alpha", number) for number in range(1, 26)])
    assert selector.main(_args(queue, paths, apply=False)) == 0
    assert "dry run: no output files written" in capsys.readouterr().out
    assert all(not path.exists() for path in paths)


@pytest.mark.parametrize("fault", ["duplicate_id", "missing_source"])
def test_malformed_or_unrepresentable_candidate_groups_fail_closed(tmp_path, fault, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [_candidate("Alpha", number) for number in range(1, 26)]
    if fault == "duplicate_id":
        duplicate = _candidate("Alpha", 26)
        duplicate["candidate_id"] = rows[0]["candidate_id"]
        rows.append(duplicate)
    elif fault == "missing_source":
        del rows[0]["source_namespace"]
    _jsonl(queue, rows)

    assert selector.main(_args(queue, paths)) == 2
    error = capsys.readouterr().err
    expected = {
        "duplicate_id": "duplicate candidate_id",
        "missing_source": "source_namespace",
    }
    assert expected[fault] in error
    assert all(not path.exists() for path in paths)


def test_every_alternative_and_split_special_case_is_retained(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [
        _candidate(
            "SFLD",
            9,
            suffix="-alphabetical",
            protein_id="UniProtKB:O34508",
            protein_label="UDP-N-acetylglucosamine 2-epimerase",
        ),
        _candidate(
            "SFLD",
            9,
            suffix="-matching",
            protein_id="UniProtKB:O34514-2",
            protein_label="O-succinylbenzoate synthase",
        ),
        _candidate(
            "SFLD",
            9,
            suffix="-residues",
            protein_id="UniProtKB:P29208",
            protein_label="O-succinylbenzoate synthase",
            residue_positions=[4, 9],
        ),
    ]
    _jsonl(queue, rows)

    assert selector.main(_args(queue, paths, "--max-records", "1")) == 0
    selected = _rows(paths[0])
    assert [row["candidate_id"] for row in selected] == [
        "candidate-SFLD-00009-alphabetical",
        "candidate-SFLD-00009-matching",
        "candidate-SFLD-00009-residues",
    ]
    assert {row["record_path"] for row in selected} == {"fixtures/SFLD/00009.yaml"}
    assert all(row["record_candidate_count"] == 3 for row in selected)
    assert all(row["record_review_flags"] == ["ISOFORM", "RESIDUE_SET"] for row in selected)
    by_id = {row["candidate_id"]: row for row in selected}
    assert by_id["candidate-SFLD-00009-alphabetical"]["review_flags"] == []
    assert by_id["candidate-SFLD-00009-matching"]["review_flags"] == ["ISOFORM"]
    assert by_id["candidate-SFLD-00009-residues"]["review_flags"] == ["RESIDUE_SET"]

    manifest = json.loads(paths[2].read_text(encoding="utf-8"))
    assert manifest["global_source_slice_trait_records"] == 1
    assert manifest["shard_available_trait_records"] == 1
    assert manifest["shard_selected_trait_records"] == 1
    assert manifest["global_source_slice_candidate_rows"] == 3
    assert manifest["shard_selected_candidate_rows"] == 3
    assert manifest["invariants"]["all_selected_candidate_alternatives_retained"]


def test_max_records_caps_groups_not_candidate_rows_and_is_idempotent(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    rows = [
        _candidate("Alpha", 1, suffix="-c", protein_id="UniProtKB:P00003"),
        _candidate("Alpha", 1, suffix="-a", protein_id="UniProtKB:P00001"),
        _candidate("Alpha", 1, suffix="-b", protein_id="UniProtKB:P00002"),
        *[_candidate("Alpha", number) for number in range(2, 27)],
    ]
    _jsonl(queue, rows)
    args = _args(queue, paths, "--max-records", "25")

    assert selector.main(args) == 0
    first = tuple(path.read_bytes() for path in paths)
    selected = _rows(paths[0])
    assert len(selected) == 27
    assert len({row["record_path"] for row in selected}) == 25
    assert "Alpha:00026" not in {row["trait_id"] for row in selected}
    assert [row["protein_id"] for row in selected if row["trait_id"] == "Alpha:00001"] == [
        "UniProtKB:P00001",
        "UniProtKB:P00002",
        "UniProtKB:P00003",
    ]
    manifest = json.loads(paths[2].read_text(encoding="utf-8"))
    assert manifest["shard_selected_trait_records"] == 25
    assert manifest["shard_selected_candidate_rows"] == 27
    assert manifest["invariants"]["within_record_cap"]

    assert selector.main(args) == 0
    assert tuple(path.read_bytes() for path in paths) == first


@pytest.mark.parametrize(
    "extra, expected",
    [
        (("--shard-count", "0"), "--shard-count"),
        (("--shard-count", "-2"), "--shard-count"),
        (("--shard-index", "-1"), "--shard-index"),
        (("--shard-index", "1"), "--shard-index"),
        (("--shard-count", "2", "--shard-index", "2"), "--shard-index"),
    ],
)
def test_invalid_shard_pair_or_range_fails_without_writes(tmp_path, capsys, extra, expected):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    _jsonl(queue, [_candidate("Alpha", 1)])

    assert selector.main(_args(queue, paths, *extra)) == 2
    assert expected in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_empty_shard_fails_closed_without_replacing_outputs(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    row = _candidate("Alpha", 1)
    _jsonl(queue, [row])
    record = selector.TraitRecord(
        record_path=row["record_path"],
        trait_id=row["trait_id"],
        source_namespace=row["source_namespace"],
        candidates=(row,),
        review_flags=(),
    )
    empty_index = 1 - selector._record_shard_index(record, 2)
    for path in paths:
        path.write_text("previous-good\n", encoding="utf-8")

    assert (
        selector.main(
            _args(
                queue,
                paths,
                "--shard-count",
                "2",
                "--shard-index",
                str(empty_index),
            )
        )
        == 2
    )
    assert "contains no trait records" in capsys.readouterr().err
    assert all(path.read_text(encoding="utf-8") == "previous-good\n" for path in paths)


def test_two_shards_partition_1502_special_records_without_loss(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    rows = [
        _candidate(
            "PRINTS",
            number,
            intervals=[{"start": 2, "end": 5}, {"start": 8, "end": 11}],
        )
        for number in range(1, 1503)
    ]
    rows.append(
        _candidate(
            "PRINTS",
            1,
            suffix="-alternative",
            protein_id="UniProtKB:Q00001",
            intervals=[{"start": 2, "end": 5}, {"start": 8, "end": 11}],
        )
    )
    _jsonl(queue, rows)
    expected_paths = {row["record_path"] for row in rows}
    expected_candidates = {row["candidate_id"] for row in rows}
    shard_path_sets: list[set[str]] = []
    observed_candidates: set[str] = set()
    shard_sizes: list[int] = []

    for shard_index in range(2):
        shard_dir = tmp_path / f"shard-{shard_index}"
        paths = _paths(shard_dir)
        args = _args(
            queue,
            paths,
            "--source",
            "PRINTS",
            "--shard-count",
            "2",
            "--shard-index",
            str(shard_index),
        )
        assert selector.main(args) == 0
        first_bytes = tuple(path.read_bytes() for path in paths)
        selected = _rows(paths[0])
        selected_paths = {row["record_path"] for row in selected}
        shard_path_sets.append(selected_paths)
        observed_candidates.update(row["candidate_id"] for row in selected)
        shard_sizes.append(len(selected_paths))
        assert len(selected_paths) <= 1000
        assert all(row["review_shard_count"] == 2 for row in selected)
        assert all(row["review_shard_index"] == shard_index for row in selected)
        assert all(
            row["record_shard_sha256"]
            == hashlib.sha256(
                json.dumps(
                    [row["trait_id"], row["record_path"]],
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            for row in selected
        )
        manifest = json.loads(paths[2].read_text(encoding="utf-8"))
        assert manifest["schema_version"] == selector.MANIFEST_SCHEMA_VERSION
        assert manifest["shard_count"] == 2
        assert manifest["shard_index"] == shard_index
        assert manifest["global_source_slice_trait_records"] == 1502
        assert manifest["global_source_slice_candidate_rows"] == 1503
        assert manifest["global_source_slice_special_records"] == 1502
        assert manifest["shard_available_trait_records"] == len(selected_paths)
        assert manifest["shard_selected_trait_records"] == len(selected_paths)
        assert manifest["shard_available_special_records"] == len(selected_paths)
        assert manifest["shard_selected_special_records"] == len(selected_paths)
        assert manifest["invariants"]["all_shard_special_cases_selected"]
        assert all(manifest["invariants"].values())
        assert selector.main(args) == 0
        assert tuple(path.read_bytes() for path in paths) == first_bytes

    assert shard_path_sets[0].isdisjoint(shard_path_sets[1])
    assert set().union(*shard_path_sets) == expected_paths
    assert observed_candidates == expected_candidates
    assert sum(shard_sizes) == 1502
    assert (
        sum(
            row["candidate_id"].endswith("-alternative")
            for shard_index in range(2)
            for row in _rows(_paths(tmp_path / f"shard-{shard_index}")[0])
        )
        == 1
    )


@pytest.mark.parametrize(
    "record_path",
    [
        "/absolute/record.yaml",
        "fixtures/../escape.yaml",
        "fixtures\\windows\\record.yaml",
        "fixtures//non-normalized.yaml",
        " fixtures/leading-space.yaml",
        "fixtures/not-yaml.txt",
    ],
)
def test_unsafe_record_identity_paths_fail_closed(tmp_path, capsys, record_path):
    queue = tmp_path / "candidates.jsonl"
    paths = _paths(tmp_path)
    _jsonl(queue, [_candidate("Alpha", 1, record_path=record_path)])

    assert selector.main(_args(queue, paths)) == 2
    assert "unsafe record_path" in capsys.readouterr().err
    assert all(not path.exists() for path in paths)


def test_output_paths_cannot_alias_each_other_or_the_queue(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    _jsonl(queue, [_candidate("Alpha", number) for number in range(1, 26)])
    manifest = tmp_path / "manifest"
    args = [
        "--queue",
        str(queue),
        "--batch-id",
        "review-001",
        "--out",
        str(queue),
        "--manifest-tsv",
        str(manifest),
        "--manifest-json",
        str(manifest),
        "--apply",
    ]
    assert selector.main(args) == 2
    assert "output paths must be distinct" in capsys.readouterr().err


def test_selector_source_has_no_trait_writer_route():
    source = (REPO / "scripts" / "select_uniprot_review_batch.py").read_text(encoding="utf-8")
    assert "record_io" not in source
    assert "write_record" not in source
    assert 'target.open("rb")' in source
    assert 'target.open("w")' not in source


def test_named_review_batch_recipes_do_not_forward_batch_id_twice():
    source = (REPO / "justfile").read_text(encoding="utf-8")
    for recipe in (
        "select-uniprot-review-batch",
        "fetch-uniprot-review-batch",
        "resolve-uniprot-review-batch",
        "finalize-uniprot-review-batch",
        "promote-uniprot-review-batch",
    ):
        marker = f"{recipe} batch_id *args:\n"
        assert marker in source
        block = source.split(marker, 1)[1].split("\n\n", 1)[0]
        assert "\n    shift\n" in block
