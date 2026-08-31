"""Release, accession, and sequence gates for the UniProt registry builder."""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import os
import pathlib
import subprocess
import sys
import urllib.parse
from typing import Any

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
registry = importlib.import_module("fetch_uniprot_registry")


def _jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _candidate(
    protein_id: str,
    sequence: str,
    *,
    number: int = 1,
    batch: str = "ready-local",
    release: str = "2026_02",
) -> dict:
    return {
        "batch": batch,
        "batch_id": batch,
        "candidate_id": f"candidate-{number}",
        "trait_id": f"Pfam:PF{number:05d}",
        "record_path": f"fixtures/pfam/PF{number:05d}.yaml",
        "record_candidate_count": 1,
        "source_batch": "ready-local",
        "protein_id": protein_id,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_release": release,
    }


def _entry(
    accession: str,
    sequence: str,
    *,
    label: str = "Fixture protein",
    taxon: int = 9606,
    taxon_label: str = "Homo sapiens",
    reviewed: bool = True,
    sequence_version: int | None = 3,
) -> dict:
    entry = {
        "primaryAccession": accession,
        "uniProtkbId": f"{accession.replace('-', '_')}_HUMAN",
        "entryType": (
            "UniProtKB reviewed (Swiss-Prot)" if reviewed else "UniProtKB unreviewed (TrEMBL)"
        ),
        "proteinDescription": {"recommendedName": {"fullName": {"value": label}}},
        "organism": {"taxonId": taxon, "scientificName": taxon_label},
        "sequence": {"value": sequence, "length": len(sequence)},
        "entryAudit": {},
    }
    if sequence_version is not None:
        entry["entryAudit"]["sequenceVersion"] = sequence_version
    return entry


def _responses(path: pathlib.Path, responses: list[dict], release: str | None = None) -> None:
    payload: dict = {"responses": responses}
    if release is not None:
        payload["release"] = release
    path.write_text(json.dumps(payload), encoding="utf-8")


def _manifest(
    path: pathlib.Path,
    queue: pathlib.Path,
    *,
    batch: str = "ready-local",
    count: int | None = None,
    queue_sha256: str | None = None,
) -> None:
    rows = queue.read_text(encoding="utf-8").splitlines()
    parsed_rows = [json.loads(row) for row in rows]
    record_count = len({(row["trait_id"], row["record_path"]) for row in parsed_rows})
    path.write_text(
        json.dumps(
            {
                "schema_version": 6,
                "batch_id": batch,
                "source_batch": "ready-local",
                "candidate_jsonl_sha256": queue_sha256
                or hashlib.sha256(queue.read_bytes()).hexdigest(),
                "shard_selected_candidate_rows": len(rows) if count is None else count,
                "shard_selected_trait_records": record_count,
                "invariants": {key: True for key in sorted(registry.SELECTOR_V6_INVARIANTS)},
                "downstream_requirements": {
                    key: True for key in sorted(registry.SELECTOR_DOWNSTREAM_REQUIREMENTS)
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _dry_args(
    queue: pathlib.Path,
    manifest: pathlib.Path,
    out: pathlib.Path,
    blocked: pathlib.Path,
    *,
    membership: pathlib.Path,
    receipt: pathlib.Path,
    extra: tuple[str, ...] = (),
) -> list[str]:
    return [
        "--queue",
        str(queue),
        "--selector-manifest",
        str(manifest),
        "--batch",
        "ready-local",
        "--expect-release",
        "2026_02",
        "--out",
        str(out),
        "--membership-out",
        str(membership),
        "--blocked",
        str(blocked),
        "--receipt",
        str(receipt),
        *extra,
    ]


def _prepare_apply(
    queue: pathlib.Path,
    responses: pathlib.Path,
    out: pathlib.Path,
    blocked: pathlib.Path,
    *extra: str,
) -> dict[str, Any]:
    manifest = queue.with_name("selector-manifest.json")
    membership = out.with_name("memberships.jsonl")
    receipt = out.with_name("fetch-receipt.json")
    plan_path = out.with_name("fetch-plan.json")
    _manifest(manifest, queue)
    dry_args = _dry_args(
        queue,
        manifest,
        out,
        blocked,
        membership=membership,
        receipt=receipt,
        extra=(*extra, "--offline-responses", str(responses)),
    )
    namespace = registry._parser().parse_args(dry_args)
    prepared = registry._derive_request_plan(namespace)
    plan_path.write_text(registry.render_request_plan(prepared.plan), encoding="utf-8")
    return {
        "args": [
            *dry_args,
            "--request-plan",
            str(plan_path),
            "--apply",
        ],
        "manifest": manifest,
        "membership": membership,
        "receipt": receipt,
        "plan": plan_path,
        "plan_value": prepared.plan,
    }


def _args(
    queue: pathlib.Path,
    responses: pathlib.Path,
    out: pathlib.Path,
    blocked: pathlib.Path,
    *extra: str,
) -> list[str]:
    return _prepare_apply(queue, responses, out, blocked, *extra)["args"]


def _registry_rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _blocked_rows(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_request_uses_exact_accessions_required_fields_and_isoforms():
    url = registry.request_url(["P21802-2", "P12345", "P12345"])
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "rest.uniprot.org"
    assert query["query"] == ["(accession:P12345 OR accession:P21802-2)"]
    assert query["includeIsoform"] == ["true"]
    assert tuple(query["fields"][0].split(",")) == registry.RETURN_FIELDS
    assert set(registry.XREF_FIELDS).issubset(registry.RETURN_FIELDS)
    assert query["format"] == ["json"]


def test_offline_build_is_exact_deduplicated_isoform_aware_and_deterministic(tmp_path, monkeypatch):
    queue = tmp_path / "candidates.jsonl"
    response_file = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    canonical_sequence = "ACDEFGHIK"
    isoform_sequence = "MNPQRSTVWY"
    rows = [
        _candidate("UniProtKB:P21802-2", isoform_sequence, number=2),
        _candidate("UniProtKB:P12345", canonical_sequence, number=1),
        _candidate("UniProtKB:P12345", canonical_sequence, number=3),
    ]
    _jsonl(queue, rows)
    queue_before = queue.read_bytes()
    _responses(
        response_file,
        [
            {
                "requested": ["P12345", "P21802-2"],
                "results": [
                    _entry("P21802-2", isoform_sequence, label="Isoform protein"),
                    _entry("P12345", canonical_sequence, reviewed=False),
                ],
            }
        ],
        release="2026_02",
    )
    monkeypatch.setattr(
        registry.urllib.request,
        "urlopen",
        lambda *args, **kwargs: pytest.fail("offline mode attempted network access"),
    )
    prepared = _prepare_apply(queue, response_file, out, blocked)
    args = prepared["args"]
    assert registry.main(args) == 0
    first_out, first_blocked = out.read_bytes(), blocked.read_bytes()
    first_membership = prepared["membership"].read_bytes()
    first_receipt = prepared["receipt"].read_bytes()
    assert queue.read_bytes() == queue_before
    references = _registry_rows(out)
    assert [row["protein_id"] for row in references] == [
        "UniProtKB:P12345",
        "UniProtKB:P21802-2",
    ]
    canonical, isoform = references
    assert canonical == {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Fixture protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": canonical_sequence,
        "sequence_length": len(canonical_sequence),
        "sequence_sha256": hashlib.sha256(canonical_sequence.encode()).hexdigest(),
        "reviewed": False,
        "uniprot_release": "2026_02",
        "sequence_version": 3,
    }
    assert isoform["isoform"] == 2
    assert isoform["sequence"] == isoform_sequence
    assert isoform["protein_label"] == "Isoform protein"
    assert _blocked_rows(blocked) == []
    receipt = json.loads(first_receipt)
    assert receipt["kind"] == registry.RECEIPT_KIND
    assert receipt["generation_boundary"] is True
    assert receipt["request_plan_id"] == prepared["plan_value"]["request_plan_id"]
    assert receipt["observed_uniprot_release"] == "2026_02"
    assert receipt["acquisition_mode"] == "OFFLINE_FIXTURE"
    assert receipt["network_action_performed"] is False
    assert receipt["offline_fixture_artifact"] == prepared["plan_value"]["offline_fixture_artifact"]
    assert receipt["response_rows"][0]["response_body_sha256"]
    assert receipt["response_rows"][0]["response_url"] is None
    assert receipt["response_rows"][0]["acquisition_mode"] == "OFFLINE_FIXTURE"
    assert receipt["response_rows"][0]["response_header_projection"] == {
        "x-uniprot-release": "2026_02"
    }
    for role, path in {
        "protein_registry": out,
        "membership_registry": prepared["membership"],
        "blocked_registry": blocked,
    }.items():
        projection = receipt["outputs"][role]
        assert projection["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert projection["size_bytes"] == len(path.read_bytes())
    verified = registry.verify_fetch_receipt(
        receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
    )
    assert verified.receipt_sha256 == hashlib.sha256(first_receipt).hexdigest()
    assert verified.request_plan == prepared["plan_value"]
    assert verified.candidate_jsonl_bytes == queue_before
    assert verified.protein_registry_jsonl_bytes == first_out
    assert verified.membership_registry_jsonl_bytes == first_membership
    assert registry.main(args) == 0
    assert out.read_bytes() == first_out
    assert blocked.read_bytes() == first_blocked
    assert prepared["membership"].read_bytes() == first_membership
    assert prepared["receipt"].read_bytes() == first_receipt


def test_dry_run_emits_canonical_offline_plan_without_network_or_output_writes(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    out = tmp_path / "registry.jsonl"
    memberships = tmp_path / "memberships.jsonl"
    blocked = tmp_path / "blocked.tsv"
    receipt = tmp_path / "receipt.json"
    response_fixture = tmp_path / "responses.json"
    _responses(response_fixture, [{"requested": ["P12345"], "results": []}], "2026_02")
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                out,
                blocked,
                membership=memberships,
                receipt=receipt,
                extra=(
                    "--offline-responses",
                    str(response_fixture),
                ),
            )
        )
        == 0
    )
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.endswith("\n") and captured.out.count("\n") == 1
    plan = json.loads(captured.out)
    assert captured.out == registry.render_request_plan(plan)
    assert plan["kind"] == registry.PLAN_KIND
    assert plan["acquisition_mode"] == "OFFLINE_FIXTURE"
    assert plan["offline_fixture_artifact"] == {
        "path": str(response_fixture.resolve()),
        "sha256": hashlib.sha256(response_fixture.read_bytes()).hexdigest(),
        "size_bytes": len(response_fixture.read_bytes()),
    }
    assert plan["candidate_artifact"]["sha256"] == hashlib.sha256(queue.read_bytes()).hexdigest()
    assert (
        plan["selector_manifest_artifact"]["sha256"]
        == hashlib.sha256(manifest.read_bytes()).hexdigest()
    )
    assert plan["target_count"] == 1
    assert plan["requests"][0]["accessions"] == ["P12345"]
    assert plan["request_policy"]["return_fields"] == list(registry.RETURN_FIELDS)
    assert plan["output_paths"]["fetch_receipt"] == str(receipt.resolve())
    assert not out.exists()
    assert not memberships.exists()
    assert not blocked.exists()
    assert not receipt.exists()


@pytest.mark.parametrize("mismatch", ["length", "checksum"])
def test_candidate_sequence_facts_are_compared_and_mismatches_block(tmp_path, mismatch):
    queue = tmp_path / "candidates.jsonl"
    response_file = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    row = _candidate("UniProtKB:P12345", "ACDE")
    if mismatch == "length":
        row["sequence_length"] = 99
    elif mismatch == "checksum":
        row["sequence_sha256"] = "0" * 64
    _jsonl(queue, [row])
    _responses(
        response_file,
        [{"requested": ["P12345"], "release": "2026_02", "results": [_entry("P12345", "ACDE")]}],
    )
    assert registry.main(_args(queue, response_file, out, blocked)) == 0
    assert _registry_rows(out) == []
    rows = _blocked_rows(blocked)
    assert len(rows) == 1
    assert rows[0]["reason"] == "REFERENCE_VALIDATION_FAILED"
    assert mismatch.replace("checksum", "sha256") in rows[0]["detail"]


def test_later_api_release_is_accepted_only_when_sequence_checksum_matches(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    response_file = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(
        queue,
        [_candidate("UniProtKB:P12345", "ACDE", release="2026_02")],
    )
    _responses(
        response_file,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        release="2026_03",
    )
    assert (
        registry.main(
            _args(
                queue,
                response_file,
                out,
                blocked,
                "--expect-release",
                "2026_03",
            )
        )
        == 0
    )
    assert _registry_rows(out)[0]["uniprot_release"] == "2026_03"
    assert _blocked_rows(blocked) == []


@pytest.mark.parametrize(
    "releases,error_fragment",
    [
        ([None], "missing a valid x-uniprot-release"),
        (["2026_02", "2026_03"], "mixed UniProt releases"),
    ],
)
def test_missing_or_mixed_response_release_preserves_previous_good_outputs(
    tmp_path, capsys, releases, error_fragment
):
    queue = tmp_path / "candidates.jsonl"
    response_file = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    accessions = ["P12345", "P21802"][: len(releases)]
    sequences = {"P12345": "ACDE", "P21802": "MNPQ"}
    _jsonl(
        queue,
        [
            _candidate(f"UniProtKB:{accession}", sequences[accession], number=index)
            for index, accession in enumerate(accessions, 1)
        ],
    )
    responses = []
    for accession, release in zip(accessions, releases):
        response = {
            "requested": [accession],
            "results": [_entry(accession, sequences[accession])],
        }
        if release is not None:
            response["release"] = release
        responses.append(response)
    _responses(response_file, responses)
    prepared = _prepare_apply(queue, response_file, out, blocked, "--batch-size", "1")
    out.write_text("previous-registry\n", encoding="utf-8")
    blocked.write_text("previous-blocked\n", encoding="utf-8")
    prepared["membership"].write_text("previous-membership\n", encoding="utf-8")
    prepared["receipt"].write_text("previous-receipt\n", encoding="utf-8")
    assert registry.main(prepared["args"]) == 2
    assert error_fragment in capsys.readouterr().err
    assert out.read_text() == "previous-registry\n"
    assert blocked.read_text() == "previous-blocked\n"
    assert prepared["membership"].read_text() == "previous-membership\n"
    assert prepared["receipt"].read_text() == "previous-receipt\n"


def test_expected_release_mismatch_is_a_run_wide_failure(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "release": "2026_02", "results": [_entry("P12345", "ACDE")]}],
    )
    assert registry.main(_args(queue, responses, out, blocked, "--expect-release", "2026_01")) == 2
    assert not out.exists()
    assert not blocked.exists()


def test_nonexact_isoform_response_is_blocked_not_substituted(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P21802-2", "ACDE")])
    _responses(
        responses,
        [
            {
                "requested": ["P21802-2"],
                "release": "2026_02",
                "results": [_entry("P21802", "ACDE")],
            }
        ],
    )
    assert registry.main(_args(queue, responses, out, blocked)) == 0
    assert _registry_rows(out) == []
    assert _blocked_rows(blocked)[0]["reason"] == "ACCESSION_NOT_RETURNED"


def test_missing_sequence_version_is_blocked(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [
            {
                "requested": ["P12345"],
                "release": "2026_02",
                "results": [_entry("P12345", "ACDE", sequence_version=None)],
            }
        ],
    )
    assert registry.main(_args(queue, responses, out, blocked)) == 0
    assert _registry_rows(out) == []
    assert "sequenceVersion" in _blocked_rows(blocked)[0]["detail"]


def test_conflicting_candidate_expectations_fail_before_fetch(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    first = _candidate("UniProtKB:P12345", "ACDE", number=1)
    second = _candidate("UniProtKB:P12345", "MNPQ", number=2)
    good = _candidate("UniProtKB:P21802", "AAAA", number=3)
    _jsonl(queue, [first, second, good])
    manifest = tmp_path / "manifest.json"
    membership = tmp_path / "memberships.jsonl"
    receipt = tmp_path / "receipt.json"
    _manifest(manifest, queue)
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                out,
                blocked,
                membership=membership,
                receipt=receipt,
            )
        )
        == 2
    )
    assert "conflicting candidate" in capsys.readouterr().err
    assert not out.exists() and not membership.exists() and not blocked.exists()
    assert not receipt.exists() and not responses.exists()


def test_exact_batch_and_batch_id_are_both_required(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    row = _candidate("UniProtKB:P12345", "ACDE")
    row.pop("batch")
    _jsonl(queue, [row])
    manifest = tmp_path / "manifest.json"
    membership = tmp_path / "memberships.jsonl"
    receipt = tmp_path / "receipt.json"
    _manifest(manifest, queue)
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                out,
                blocked,
                membership=membership,
                receipt=receipt,
            )
        )
        == 2
    )
    assert "batch and batch_id" in capsys.readouterr().err
    assert not out.exists()
    assert not blocked.exists()
    assert not membership.exists() and not receipt.exists() and not responses.exists()


def test_offline_fixture_must_match_generated_batch_and_is_not_partially_installed(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["Q9H9K5"], "release": "2026_02", "results": []}],
    )
    out.write_text("keep\n", encoding="utf-8")
    assert registry.main(_args(queue, responses, out, blocked)) == 2
    assert out.read_text() == "keep\n"
    assert not blocked.exists()


@pytest.mark.parametrize("defect", ["queue_sha", "row_count", "batch", "duplicate_key"])
def test_selector_manifest_exactly_binds_queue_count_and_batch(tmp_path, capsys, defect):
    queue = tmp_path / "candidates.jsonl"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    value = json.loads(manifest.read_text())
    if defect == "queue_sha":
        value["candidate_jsonl_sha256"] = "0" * 64
        manifest.write_text(json.dumps(value) + "\n", encoding="utf-8")
    elif defect == "row_count":
        value["shard_selected_candidate_rows"] = 2
        manifest.write_text(json.dumps(value) + "\n", encoding="utf-8")
    elif defect == "batch":
        value["batch_id"] = "another-batch"
        manifest.write_text(json.dumps(value) + "\n", encoding="utf-8")
    else:
        manifest.write_text(
            "{"
            '"batch_id":"ready-local","batch_id":"ready-local",'
            f'"candidate_jsonl_sha256":"{hashlib.sha256(queue.read_bytes()).hexdigest()}",'
            '"shard_selected_candidate_rows":1}\n',
            encoding="utf-8",
        )
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    membership = tmp_path / "memberships.jsonl"
    receipt = tmp_path / "receipt.json"
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                out,
                blocked,
                membership=membership,
                receipt=receipt,
            )
        )
        == 2
    )
    assert capsys.readouterr().err.startswith("ERROR:")
    assert not any(path.exists() for path in (out, blocked, membership, receipt))


@pytest.mark.parametrize(
    "defect",
    [
        "schema",
        "source_batch",
        "row_source_batch",
        "record_count",
        "record_alternative_count",
        "missing_invariant",
        "false_invariant",
        "missing_exhaustive",
        "false_one_approved",
    ],
)
def test_selector_v6_shape_and_review_contract_are_fail_closed(tmp_path, capsys, defect):
    queue = tmp_path / "candidates.jsonl"
    row = _candidate("UniProtKB:P12345", "ACDE")
    if defect == "row_source_batch":
        row["source_batch"] = "wrong-source"
    elif defect == "record_alternative_count":
        row["record_candidate_count"] = 2
    _jsonl(queue, [row])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    value = json.loads(manifest.read_text())
    if defect == "schema":
        value["schema_version"] = 5
    elif defect == "source_batch":
        value["source_batch"] = "wrong-source"
    elif defect == "record_count":
        value["shard_selected_trait_records"] = 2
    elif defect == "missing_invariant":
        value["invariants"].pop("within_record_cap")
    elif defect == "false_invariant":
        value["invariants"]["within_record_cap"] = False
    elif defect == "missing_exhaustive":
        value["downstream_requirements"].pop(
            "all_alternatives_must_receive_an_explicit_review_decision"
        )
    elif defect == "false_one_approved":
        value["downstream_requirements"]["at_most_one_approved_candidate_per_record"] = False
    manifest.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    paths = [tmp_path / name for name in ("registry", "blocked", "membership", "receipt")]
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                paths[0],
                paths[1],
                membership=paths[2],
                receipt=paths[3],
            )
        )
        == 2
    )
    assert capsys.readouterr().err.startswith("ERROR:")
    assert not any(path.exists() for path in paths)


@pytest.mark.parametrize("defect", ["noncanonical", "duplicate_key", "duplicate_id"])
def test_candidate_jsonl_is_canonical_unique_keyed_and_candidate_ids_are_unique(
    tmp_path, capsys, defect
):
    queue = tmp_path / "candidates.jsonl"
    first = _candidate("UniProtKB:P12345", "ACDE", number=1)
    if defect == "noncanonical":
        queue.write_text(json.dumps(first) + "\n", encoding="utf-8")
    elif defect == "duplicate_key":
        canonical = registry._canonical_json(first)
        queue.write_text(
            canonical.replace(
                '{"batch":',
                '{"batch":"ready-local","batch":',
                1,
            )
            + "\n",
            encoding="utf-8",
        )
    else:
        second = _candidate("UniProtKB:P21802", "MNPQ", number=1)
        _jsonl(queue, [first, second])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    membership = tmp_path / "memberships.jsonl"
    receipt = tmp_path / "receipt.json"
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                out,
                blocked,
                membership=membership,
                receipt=receipt,
            )
        )
        == 2
    )
    assert capsys.readouterr().err.startswith("ERROR:")
    assert not any(path.exists() for path in (out, blocked, membership, receipt))


@pytest.mark.parametrize("field", ["batch", "batch_id"])
def test_candidate_batch_fields_cannot_be_missing_or_disagree(tmp_path, capsys, field):
    queue = tmp_path / "candidates.jsonl"
    row = _candidate("UniProtKB:P12345", "ACDE")
    if field == "batch":
        row.pop("batch")
    else:
        row["batch_id"] = "different-batch"
    _jsonl(queue, [row])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    paths = [tmp_path / name for name in ("registry", "blocked", "memberships", "receipt")]
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                paths[0],
                paths[1],
                membership=paths[2],
                receipt=paths[3],
            )
        )
        == 2
    )
    assert "batch and batch_id" in capsys.readouterr().err
    assert not any(path.exists() for path in paths)


@pytest.mark.parametrize("field", ["sequence_length", "sequence_sha256", "sequence_release"])
def test_every_target_requires_a_complete_sequence_fact_triple(tmp_path, capsys, field):
    queue = tmp_path / "candidates.jsonl"
    row = _candidate("UniProtKB:P12345", "ACDE")
    row.pop(field)
    _jsonl(queue, [row])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    membership = tmp_path / "memberships.jsonl"
    receipt = tmp_path / "receipt.json"
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                out,
                blocked,
                membership=membership,
                receipt=receipt,
            )
        )
        == 2
    )
    assert f"missing candidate {field}" in capsys.readouterr().err
    assert not any(path.exists() for path in (out, blocked, membership, receipt))


def test_descriptor_capture_rejects_final_and_intermediate_symlinks(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source = source_dir / "fixture.json"
    source.write_text('{"ok":true}\n', encoding="utf-8")
    final_alias = source_dir / "final-alias.json"
    final_alias.symlink_to(source)
    with pytest.raises(registry.RegistryBuildError, match="symlink"):
        registry._capture(final_alias, description="fixture")

    directory_alias = tmp_path / "directory-alias"
    directory_alias.symlink_to(source_dir, target_is_directory=True)
    with pytest.raises(registry.RegistryBuildError, match="without following symlinks"):
        registry._capture(directory_alias / source.name, description="fixture")


def test_descriptor_capture_intermediate_swap_never_consumes_external_bytes(tmp_path, monkeypatch):
    live = tmp_path / "bound" / "live"
    live.mkdir(parents=True)
    source = live / "fixture.json"
    source.write_bytes(b"bound bytes")
    external_dir = tmp_path / "external"
    external_dir.mkdir()
    external = external_dir / source.name
    external.write_bytes(b"external bytes must not be read")
    external_stat = external.stat()
    external_reads: list[int] = []
    original_read = registry.os.read

    def audited_read(descriptor, size):
        metadata = registry.os.fstat(descriptor)
        if (metadata.st_dev, metadata.st_ino) == (external_stat.st_dev, external_stat.st_ino):
            external_reads.append(descriptor)
            raise AssertionError("external bytes consumed")
        return original_read(descriptor, size)

    detached = live.with_name("detached")

    def swap(event):
        if event == "PARENT_DIRECTORIES_BOUND":
            live.rename(detached)
            live.symlink_to(external_dir, target_is_directory=True)

    monkeypatch.setattr(registry.os, "read", audited_read)
    with pytest.raises(registry.RegistryBuildError, match="parent path binding changed"):
        registry._capture(source, description="fixture", _test_hook=swap)
    assert external_reads == []


def test_output_parent_symlink_and_existing_inode_aliases_are_rejected(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    real_outputs = tmp_path / "real-outputs"
    real_outputs.mkdir()
    output_alias = tmp_path / "output-alias"
    output_alias.symlink_to(real_outputs, target_is_directory=True)
    args = _dry_args(
        queue,
        manifest,
        output_alias / "registry.jsonl",
        output_alias / "blocked.tsv",
        membership=output_alias / "membership.jsonl",
        receipt=output_alias / "receipt.json",
    )
    assert registry.main(args) == 2
    assert "without following symlinks" in capsys.readouterr().err

    first = real_outputs / "registry.jsonl"
    second = real_outputs / "membership.jsonl"
    first.write_text("old\n", encoding="utf-8")
    os.link(first, second)
    assert (
        registry.main(
            _dry_args(
                queue,
                manifest,
                first,
                real_outputs / "blocked.tsv",
                membership=second,
                receipt=real_outputs / "receipt.json",
            )
        )
        == 2
    )
    assert "alias the same inode" in capsys.readouterr().err


def test_request_plan_contains_exact_deterministic_chunks_and_urls(tmp_path, capsys):
    queue = tmp_path / "candidates.jsonl"
    _jsonl(
        queue,
        [
            _candidate("UniProtKB:Q9H9K5", "AAAA", number=3),
            _candidate("UniProtKB:P21802", "MNPQ", number=2),
            _candidate("UniProtKB:P12345", "ACDE", number=1),
        ],
    )
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, queue)
    paths = [tmp_path / name for name in ("registry", "blocked", "memberships", "receipt")]
    args = _dry_args(
        queue,
        manifest,
        paths[0],
        paths[1],
        membership=paths[2],
        receipt=paths[3],
        extra=("--batch-size", "2"),
    )
    assert registry.main(args) == 0
    first = capsys.readouterr().out
    assert registry.main(args) == 0
    second = capsys.readouterr().out
    assert first == second
    plan = json.loads(first)
    assert [row["accessions"] for row in plan["requests"]] == [
        ["P12345", "P21802"],
        ["Q9H9K5"],
    ]
    for row in plan["requests"]:
        assert row["request_url"] == registry.request_url(row["accessions"])
        assert row["request_url_sha256"] == hashlib.sha256(row["request_url"].encode()).hexdigest()
    assert not any(path.exists() for path in paths)


def test_apply_requires_supplied_exact_plan_before_opening_response_fixture(
    tmp_path, monkeypatch, capsys
):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(responses, [{"requested": ["P12345"], "results": []}], release="2026_02")
    prepared = _prepare_apply(queue, responses, out, blocked)
    monkeypatch.setattr(
        registry,
        "OfflineClient",
        lambda *_args, **_kwargs: pytest.fail("plan failure opened response fixture"),
    )

    without_plan = list(prepared["args"])
    index = without_plan.index("--request-plan")
    del without_plan[index : index + 2]
    assert registry.main(without_plan) == 2
    assert "requires an exact saved --request-plan" in capsys.readouterr().err

    mismatched = [*prepared["args"], "--batch-size", "2"]
    assert registry.main(mismatched) == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert not any(
        path.exists() for path in (out, blocked, prepared["membership"], prepared["receipt"])
    )


def test_queue_and_manifest_recheck_runs_before_first_response(tmp_path, monkeypatch, capsys):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        release="2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    original_derive = registry._derive_request_plan
    calls = 0

    def drift_on_second_derivation(args):
        nonlocal calls
        calls += 1
        if calls == 2:
            rows = [json.loads(line) for line in queue.read_text().splitlines()]
            rows[0]["trait_id"] = "Pfam:PF99999"
            _jsonl(queue, rows)
            _manifest(prepared["manifest"], queue)
        return original_derive(args)

    monkeypatch.setattr(registry, "_derive_request_plan", drift_on_second_derivation)
    monkeypatch.setattr(
        registry.OfflineClient,
        "fetch",
        lambda *_args, **_kwargs: pytest.fail("response fetched before plan recheck"),
    )
    assert registry.main(prepared["args"]) == 2
    assert calls == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert not any(
        path.exists() for path in (out, blocked, prepared["membership"], prepared["receipt"])
    )


def test_output_parent_swap_after_plan_fails_before_response_and_writes(
    tmp_path, monkeypatch, capsys
):
    queue = tmp_path / "candidates.jsonl"
    manifest = tmp_path / "manifest.json"
    responses = tmp_path / "responses.json"
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _manifest(manifest, queue)
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    dry_args = _dry_args(
        queue,
        manifest,
        output_dir / "registry.jsonl",
        output_dir / "blocked.tsv",
        membership=output_dir / "membership.jsonl",
        receipt=output_dir / "receipt.json",
        extra=("--offline-responses", str(responses)),
    )
    prepared = registry._derive_request_plan(registry._parser().parse_args(dry_args))
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(registry.render_request_plan(prepared.plan), encoding="utf-8")
    detached = tmp_path / "detached-outputs"
    output_dir.rename(detached)
    output_dir.mkdir()
    monkeypatch.setattr(
        registry,
        "OfflineClient",
        lambda *_args, **_kwargs: pytest.fail("output-parent drift opened response fixture"),
    )
    assert registry.main([*dry_args, "--request-plan", str(plan_path), "--apply"]) == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert list(output_dir.iterdir()) == []


def test_final_queue_recheck_prevents_install_after_responses(tmp_path, monkeypatch, capsys):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        release="2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    for path, marker in (
        (out, "old-registry\n"),
        (blocked, "old-blocked\n"),
        (prepared["membership"], "old-membership\n"),
        (prepared["receipt"], "old-receipt\n"),
    ):
        path.write_text(marker, encoding="utf-8")
    original_finish = registry.OfflineClient.finish

    def drift_after_responses(client):
        original_finish(client)
        rows = [json.loads(line) for line in queue.read_text().splitlines()]
        rows[0]["trait_id"] = "Pfam:PF99999"
        _jsonl(queue, rows)
        _manifest(prepared["manifest"], queue)

    monkeypatch.setattr(registry.OfflineClient, "finish", drift_after_responses)
    assert registry.main(prepared["args"]) == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert out.read_text() == "old-registry\n"
    assert blocked.read_text() == "old-blocked\n"
    assert prepared["membership"].read_text() == "old-membership\n"
    assert prepared["receipt"].read_text() == "old-receipt\n"


def test_receipt_is_canonical_content_addressed_and_installed_last(tmp_path, monkeypatch):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [
            {
                "requested": ["P12345"],
                "headers": {
                    "content-type": "application/json",
                    "etag": '"fixture-etag"',
                },
                "results": [_entry("P12345", "ACDE")],
            }
        ],
        release="2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    installed: list[tuple[pathlib.Path, str]] = []
    original_atomic = registry._atomic_replace_bound

    def recording_atomic(output, text, *, phase):
        installed.append((output.path, phase))
        original_atomic(output, text, phase=phase)

    monkeypatch.setattr(registry, "_atomic_replace_bound", recording_atomic)
    assert registry.main(prepared["args"]) == 0
    assert installed == [
        (prepared["receipt"], "generation_pending"),
        (out, "protein_registry"),
        (prepared["membership"], "membership_registry"),
        (blocked, "blocked_registry"),
        (prepared["receipt"], "final_receipt"),
    ]
    receipt_text = prepared["receipt"].read_text()
    receipt = json.loads(receipt_text)
    assert receipt_text == registry._canonical_json(receipt) + "\n"
    without_id = dict(receipt)
    observed_id = without_id.pop("receipt_id")
    assert observed_id == registry.RECEIPT_ID_PREFIX + registry._value_sha256(without_id)
    response = receipt["response_rows"][0]
    assert response["response_header_projection"] == {
        "content-type": "application/json",
        "etag": '"fixture-etag"',
        "x-uniprot-release": "2026_02",
    }
    assert response["response_header_projection_sha256"] == registry._value_sha256(
        response["response_header_projection"]
    )
    expected_body = registry._canonical_json({"results": [_entry("P12345", "ACDE")]}).encode()
    assert response["response_body_sha256"] == hashlib.sha256(expected_body).hexdigest()
    assert response["response_body_size_bytes"] == len(expected_body)
    assert receipt["outputs"]["protein_registry"]["row_count"] == 1
    assert receipt["outputs"]["membership_registry"]["row_count"] == 0
    assert receipt["outputs"]["blocked_registry"]["row_count"] == 0


@pytest.mark.parametrize(
    "failure_phase",
    ["protein_registry", "membership_registry", "blocked_registry", "final_receipt"],
)
def test_partial_install_failure_leaves_only_canonical_pending_receipt(
    tmp_path, monkeypatch, capsys, failure_phase
):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    registry.verify_fetch_receipt(
        receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
    )
    original_replace = registry._atomic_replace_bound

    def fail_one_phase(output, text, *, phase):
        if phase == failure_phase:
            raise OSError(f"injected {phase} failure")
        return original_replace(output, text, phase=phase)

    monkeypatch.setattr(registry, "_atomic_replace_bound", fail_one_phase)
    assert registry.main(prepared["args"]) == 2
    assert "partial output install failed" in capsys.readouterr().err
    marker_text = prepared["receipt"].read_text(encoding="utf-8")
    marker = json.loads(marker_text)
    assert marker_text == registry._canonical_json(marker) + "\n"
    assert marker["kind"] == registry.PENDING_KIND
    assert marker["generation_pending"] is True
    without_id = dict(marker)
    pending_id = without_id.pop("pending_id")
    assert pending_id == registry.PENDING_ID_PREFIX + registry._value_sha256(without_id)
    with pytest.raises(registry.RegistryBuildError, match="generation is pending"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


def test_failure_after_final_receipt_replace_is_recovered_to_pending(tmp_path, monkeypatch, capsys):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    original_replace = registry._atomic_replace_bound

    def fail_after_final_replace(output, text, *, phase):
        original_replace(output, text, phase=phase)
        if phase == "final_receipt":
            raise OSError("injected post-replace failure")

    monkeypatch.setattr(registry, "_atomic_replace_bound", fail_after_final_replace)
    assert registry.main(prepared["args"]) == 2
    assert "partial output install failed" in capsys.readouterr().err
    marker = json.loads(prepared["receipt"].read_text())
    assert marker["kind"] == registry.PENDING_KIND
    with pytest.raises(registry.RegistryBuildError, match="generation is pending"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


def test_pending_marker_failure_before_mutation_preserves_prior_valid_generation(
    tmp_path, monkeypatch, capsys
):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    before = {
        path: path.read_bytes()
        for path in (out, prepared["membership"], blocked, prepared["receipt"])
    }
    original_replace = registry._atomic_replace_bound

    def reject_pending(output, text, *, phase):
        if phase == "generation_pending":
            raise OSError("injected pre-mutation failure")
        return original_replace(output, text, phase=phase)

    monkeypatch.setattr(registry, "_atomic_replace_bound", reject_pending)
    assert registry.main(prepared["args"]) == 2
    assert "could not invalidate prior fetch receipt" in capsys.readouterr().err
    assert all(path.read_bytes() == raw for path, raw in before.items())
    registry.verify_fetch_receipt(
        receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
    )


def _rewrite_receipt(path: pathlib.Path, mutate) -> None:
    value = json.loads(path.read_text())
    mutate(value)
    value.pop("receipt_id", None)
    value["receipt_id"] = registry.RECEIPT_ID_PREFIX + registry._value_sha256(value)
    path.write_text(registry._canonical_json(value) + "\n", encoding="utf-8")


def _rebind_receipt_output(
    receipt_path: pathlib.Path, *, role: str, output_path: pathlib.Path, row_count: int
) -> None:
    def mutate(value):
        raw = output_path.read_bytes()
        value["outputs"][role] = {
            "path": str(output_path.resolve()),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
            "row_count": row_count,
        }

    _rewrite_receipt(receipt_path, mutate)


def test_verifier_holds_plan_matched_output_parent_across_all_captures(tmp_path, monkeypatch):
    queue = tmp_path / "candidates.jsonl"
    manifest = tmp_path / "manifest.json"
    responses = tmp_path / "responses.json"
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _manifest(manifest, queue)
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    dry_args = _dry_args(
        queue,
        manifest,
        output_dir / "registry.jsonl",
        output_dir / "blocked.tsv",
        membership=output_dir / "membership.jsonl",
        receipt=output_dir / "receipt.json",
        extra=("--offline-responses", str(responses)),
    )
    plan = registry._derive_request_plan(registry._parser().parse_args(dry_args)).plan
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(registry.render_request_plan(plan), encoding="utf-8")
    assert registry.main([*dry_args, "--request-plan", str(plan_path), "--apply"]) == 0
    forged_bytes = {path.name: path.read_bytes() for path in output_dir.iterdir()}
    original_capture = registry._capture_bound_output
    swapped = False

    def capture_then_swap(output, *, description):
        nonlocal swapped
        captured = original_capture(output, description=description)
        if not swapped and description == "fetch receipt":
            swapped = True
            output_dir.rename(tmp_path / "detached-outputs")
            output_dir.mkdir()
            for name, raw in forged_bytes.items():
                (output_dir / name).write_bytes(raw)
        return captured

    monkeypatch.setattr(registry, "_capture_bound_output", capture_then_swap)
    with pytest.raises(registry.RegistryBuildError, match="parent path binding changed"):
        registry.verify_fetch_receipt(
            receipt_path=output_dir / "receipt.json", request_plan_path=plan_path
        )


def test_verifier_rechecks_bound_output_bytes_before_accepting_receipt(tmp_path, monkeypatch):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    original_capture = registry._capture_bound_output
    modified = False

    def capture_then_modify(output, *, description):
        nonlocal modified
        captured = original_capture(output, description=description)
        if not modified and description == "installed protein_registry":
            modified = True
            descriptor = os.open(
                output.leaf_name,
                os.O_WRONLY | os.O_APPEND,
                dir_fd=output.parent_descriptor,
            )
            try:
                os.write(descriptor, b"\n")
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return captured

    monkeypatch.setattr(registry, "_capture_bound_output", capture_then_modify)
    with pytest.raises(registry.RegistryBuildError, match="changed during strict verification"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


@pytest.mark.parametrize("field", ["accession", "sequence_length", "sequence_sha256", "release"])
def test_verifier_compares_every_reference_to_exact_target_projection(tmp_path, field):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    row = _registry_rows(out)[0]
    if field == "accession":
        row["protein_id"] = "UniProtKB:Q9H9K5"
    elif field == "sequence_length":
        row["sequence"] = "ACDEF"
        row["sequence_length"] = 5
        row["sequence_sha256"] = hashlib.sha256(b"ACDEF").hexdigest()
    elif field == "sequence_sha256":
        row["sequence"] = "AAAA"
        row["sequence_sha256"] = hashlib.sha256(b"AAAA").hexdigest()
    else:
        row["uniprot_release"] = "2026_01"
    _jsonl(out, [row])
    _rebind_receipt_output(
        prepared["receipt"], role="protein_registry", output_path=out, row_count=1
    )
    with pytest.raises(registry.RegistryBuildError, match="target|unplanned"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


@pytest.mark.parametrize("field", ["accession", "candidate_count", "candidate_ids", "trait_ids"])
def test_verifier_compares_blocked_metadata_to_exact_target_projection(tmp_path, field):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(responses, [{"requested": ["P12345"], "results": []}], "2026_02")
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    row = _blocked_rows(blocked)[0]
    row[field] = {
        "accession": "Q9H9K5",
        "candidate_count": "2",
        "candidate_ids": "forged-candidate",
        "trait_ids": "Pfam:PF99999",
    }[field]
    blocked.write_text(registry._blocked_text([row]), encoding="utf-8")
    _rebind_receipt_output(
        prepared["receipt"], role="blocked_registry", output_path=blocked, row_count=1
    )
    with pytest.raises(registry.RegistryBuildError, match="does not match target projection"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


@pytest.mark.parametrize(
    "field", ["schema_version", "target_count", "request_count", "output_row_count"]
)
def test_verifier_rejects_readdressed_bool_for_integer_receipt_fields(tmp_path, field):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0

    def mutate(value):
        if field == "output_row_count":
            value["outputs"]["protein_registry"]["row_count"] = True
        else:
            value[field] = True

    _rewrite_receipt(prepared["receipt"], mutate)
    with pytest.raises(registry.RegistryBuildError, match="schema|count|row_count"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


@pytest.mark.parametrize("field", ["schema_version", "target_count"])
def test_verifier_rejects_readdressed_bool_for_integer_plan_fields(tmp_path, field):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    value = json.loads(prepared["plan"].read_text())
    value[field] = True
    value.pop("request_plan_id")
    value["request_plan_id"] = registry.PLAN_ID_PREFIX + registry._value_sha256(value)
    prepared["plan"].write_text(registry.render_request_plan(value), encoding="utf-8")
    with pytest.raises(registry.RegistryBuildError, match="schema|rederived exact plan"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


def test_verifier_rejects_readdressed_unexpected_or_nonstring_response_headers(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0

    def mutate(value):
        response = value["response_rows"][0]
        response["response_header_projection"]["x-forged-header"] = 7
        response["response_header_projection_sha256"] = registry._value_sha256(
            response["response_header_projection"]
        )
        value["response_rows_sha256"] = registry._value_sha256(value["response_rows"])

    _rewrite_receipt(prepared["receipt"], mutate)
    with pytest.raises(registry.RegistryBuildError, match="header binding"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


@pytest.mark.parametrize(
    ("tamper", "error"),
    [
        ("unexpected_count_bool", "body binding"),
        ("offline_index_bool", "offline response 1"),
        ("impossible_result_partition", "body binding"),
        ("unexpected_overlaps_request", "body binding"),
    ],
)
def test_verifier_rejects_readdressed_impossible_response_accounting(tmp_path, tamper, error):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0

    def mutate(value):
        response = value["response_rows"][0]
        if tamper == "unexpected_count_bool":
            response["unexpected_accessions"] = ["Q9H9K5"]
            response["unexpected_accession_count"] = True
            response["response_result_count"] = 2
        elif tamper == "offline_index_bool":
            response["offline_response_index"] = True
        elif tamper == "impossible_result_partition":
            response["response_result_count"] = 0
        else:
            response["unexpected_accessions"] = ["P12345"]
            response["unexpected_accession_count"] = 1
            response["response_result_count"] = 2
        value["response_rows_sha256"] = registry._value_sha256(value["response_rows"])

    _rewrite_receipt(prepared["receipt"], mutate)
    with pytest.raises(registry.RegistryBuildError, match=error):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


def test_verifier_rejects_readdressed_live_response_url_with_evil_suffix(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0

    plan = json.loads(prepared["plan"].read_text())
    plan["acquisition_mode"] = "UNIPROT_REST"
    plan["offline_fixture_artifact"] = None
    plan.pop("request_plan_id")
    plan["request_plan_id"] = registry.PLAN_ID_PREFIX + registry._value_sha256(plan)
    prepared["plan"].write_text(registry.render_request_plan(plan), encoding="utf-8")
    plan_raw = prepared["plan"].read_bytes()

    def mutate(value):
        value["request_plan_id"] = plan["request_plan_id"]
        value["request_plan_artifact"] = {
            "path": str(prepared["plan"].resolve()),
            "sha256": hashlib.sha256(plan_raw).hexdigest(),
            "size_bytes": len(plan_raw),
        }
        value["acquisition_mode"] = "UNIPROT_REST"
        value["network_action_performed"] = True
        value["offline_fixture_artifact"] = None
        response = value["response_rows"][0]
        response["acquisition_mode"] = "UNIPROT_REST"
        response["offline_response_index"] = None
        response["response_url"] = "https://rest.uniprot.org.evil/uniprotkb/search"
        response["response_body_sha256_basis"] = "HTTP_RESPONSE_BODY_BYTES"
        value["response_rows_sha256"] = registry._value_sha256(value["response_rows"])

    _rewrite_receipt(prepared["receipt"], mutate)
    with pytest.raises(registry.RegistryBuildError, match="live response 1 URL is invalid"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


@pytest.mark.parametrize("tamper", ["output_bytes", "plan_binding", "output_count"])
def test_strict_receipt_verifier_rejects_readdressed_tampering(tmp_path, tamper):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    if tamper == "output_bytes":
        out.write_text(out.read_text() + "\n", encoding="utf-8")
    elif tamper == "plan_binding":
        _rewrite_receipt(
            prepared["receipt"], lambda value: value.__setitem__("request_plan_id", "wrong")
        )
    else:
        _rewrite_receipt(
            prepared["receipt"],
            lambda value: value["outputs"]["protein_registry"].__setitem__("row_count", 2),
        )
    with pytest.raises(registry.RegistryBuildError):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


def test_strict_receipt_verifier_rejects_duplicate_keys_and_output_symlink(tmp_path):
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    out = tmp_path / "registry.jsonl"
    blocked = tmp_path / "blocked.tsv"
    _jsonl(queue, [_candidate("UniProtKB:P12345", "ACDE")])
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "ACDE")]}],
        "2026_02",
    )
    prepared = _prepare_apply(queue, responses, out, blocked)
    assert registry.main(prepared["args"]) == 0
    original_receipt = prepared["receipt"].read_text()
    prepared["receipt"].write_text(
        original_receipt.replace(
            '{"acquisition_mode":',
            '{"acquisition_mode":"OFFLINE_FIXTURE","acquisition_mode":',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(registry.RegistryBuildError, match="duplicate key"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )
    prepared["receipt"].write_text(original_receipt, encoding="utf-8")
    saved = tmp_path / "saved-registry.jsonl"
    saved.write_bytes(out.read_bytes())
    out.unlink()
    out.symlink_to(saved)
    with pytest.raises(registry.RegistryBuildError, match="symlink"):
        registry.verify_fetch_receipt(
            receipt_path=prepared["receipt"], request_plan_path=prepared["plan"]
        )


def test_just_wrappers_supply_selector_manifest_and_batch_receipt_paths():
    source = (REPO / "justfile").read_text(encoding="utf-8")
    generic = source.split("fetch-uniprot-registry queue selector_manifest batch_id *args:\n", 1)[
        1
    ].split("\n\n", 1)[0]
    assert "shift 3" in generic
    assert "--queue {{quote(queue)}}" in generic
    assert "--selector-manifest {{quote(selector_manifest)}}" in generic
    assert "--batch {{quote(batch_id)}}" in generic
    assert "--offline-responses" not in generic
    assert '"$@"' not in generic
    assert "mode_args" not in generic
    assert 'if [[ "$apply" == true ]]; then' in generic
    assert "unsupported fetch option" in generic

    bounded = source.split("fetch-uniprot-review-batch batch_id *args:\n", 1)[1].split("\n\n", 1)[0]
    assert "shift\n" in bounded
    assert "{{quote(batch_id)}}.manifest.json" in bounded
    assert "{{quote(batch_id)}}.uniprot_fetch_receipt.json" in bounded
    assert "--offline-responses" not in bounded
    assert '"$@"' not in bounded
    assert "mode_args" not in bounded
    assert 'if [[ "$apply" == true ]]; then' in bounded
    assert "offline fixtures and option overrides are forbidden" in bounded


def test_bounded_dry_wrapper_executes_under_system_bash_with_nounset(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_uv.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    result = subprocess.run(
        [
            "just",
            "fetch-uniprot-review-batch",
            "ready-local-review-012-s12of14",
        ],
        cwd=REPO,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_registry_builder_has_no_trait_record_write_route():
    source = (REPO / "scripts" / "fetch_uniprot_registry.py").read_text(encoding="utf-8")
    assert "data/traits" not in source
    assert "write_validated_record" not in source
    assert "write_record(" not in source
