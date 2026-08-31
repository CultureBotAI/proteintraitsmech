"""Fail-closed tests for exact UniProt database membership snapshots."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import fetch_uniprot_registry as registry  # noqa: E402
import uniprot_membership_snapshot as membership  # noqa: E402


def _entry(accession: str, sequence: str, xrefs: list[dict]) -> dict:
    return {
        "primaryAccession": accession,
        "uniProtkbId": f"{accession}_HUMAN",
        "entryType": "UniProtKB reviewed (Swiss-Prot)",
        "proteinDescription": {"recommendedName": {"fullName": {"value": "Fixture protein"}}},
        "organism": {"taxonId": 9606, "scientificName": "Homo sapiens"},
        "sequence": {"value": sequence, "length": len(sequence)},
        "entryAudit": {"sequenceVersion": 4},
        "uniProtKBCrossReferences": xrefs,
    }


def _candidate(source_trait_id: str, sequence: str) -> dict:
    batch = "ready-uniprot-membership"
    return {
        "schema_version": 1,
        "batch": batch,
        "batch_id": batch,
        "source_batch": batch,
        "candidate_id": "candidate-membership",
        "trait_id": source_trait_id,
        "record_path": f"fixtures/{source_trait_id.replace(':', '_')}.yaml",
        "record_candidate_count": 1,
        "protein_id": "UniProtKB:P12345",
        "scope": "WHOLE_PROTEIN",
        "source_trait_id": source_trait_id,
        "mapping_method": "SOURCE_MEMBERSHIP",
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_release": "2026_02",
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_selector_manifest(path: Path, queue: Path) -> None:
    rows = [json.loads(line) for line in queue.read_text(encoding="utf-8").splitlines()]
    path.write_text(
        json.dumps(
            {
                "schema_version": registry.SELECTOR_MANIFEST_SCHEMA_VERSION,
                "batch_id": "ready-uniprot-membership",
                "source_batch": "ready-uniprot-membership",
                "candidate_jsonl_sha256": hashlib.sha256(queue.read_bytes()).hexdigest(),
                "shard_selected_candidate_rows": len(rows),
                "shard_selected_trait_records": len(
                    {(row["trait_id"], row["record_path"]) for row in rows}
                ),
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


def _registry_apply_args(
    *,
    queue: Path,
    responses: Path,
    protein_out: Path,
    membership_out: Path,
    blocked: Path,
    receipt: Path,
) -> list[str]:
    selector = queue.with_name("selector-manifest.json")
    request_plan = queue.with_name("fetch-plan.json")
    _write_selector_manifest(selector, queue)
    dry_args = [
        "--queue",
        str(queue),
        "--selector-manifest",
        str(selector),
        "--batch",
        "ready-uniprot-membership",
        "--expect-release",
        "2026_03",
        "--offline-responses",
        str(responses),
        "--out",
        str(protein_out),
        "--membership-out",
        str(membership_out),
        "--blocked",
        str(blocked),
        "--receipt",
        str(receipt),
    ]
    prepared = registry._derive_request_plan(registry._parser().parse_args(dry_args))
    request_plan.write_text(registry.render_request_plan(prepared.plan), encoding="utf-8")
    return [*dry_args, "--request-plan", str(request_plan), "--apply"]


def test_extract_preserves_exact_xrefs_and_namespace_mappings():
    sequence_sha = hashlib.sha256(b"ACDE").hexdigest()
    rows = membership.extract_entry_memberships(
        {
            "uniProtKBCrossReferences": [
                {
                    "database": "PANTHER",
                    "id": "PTHR12345",
                    "properties": [
                        {"key": "B", "value": "2"},
                        {"key": "A", "value": "1"},
                    ],
                },
                {"database": "Gene3D", "id": "G3DSA:1.10.10.10"},
                {"database": "SUPFAM", "id": "SSF12345"},
                {"database": "GO", "id": "GO:0000001"},
            ]
        },
        protein_id="UniProtKB:P12345",
        sequence_sha256=sequence_sha,
        uniprot_release="2026_03",
    )

    assert [row["source_trait_id"] for row in rows] == [
        "CATH:1.10.10.10",
        "PANTHER:PTHR12345",
        "SUPERFAMILY:SSF12345",
    ]
    panther = rows[1]
    assert panther["database_cross_reference"] == {
        "database": "PANTHER",
        "id": "PTHR12345",
        "properties": [
            {"key": "A", "value": "1"},
            {"key": "B", "value": "2"},
        ],
    }
    assert panther["membership_id"] == (
        membership.MEMBERSHIP_ID_PREFIX + membership.membership_entry_sha256(panther)
    )
    assert rows[0]["database_id"] == "G3DSA:1.10.10.10"
    assert rows[0]["database_cross_reference"]["id"] == "G3DSA:1.10.10.10"
    assert (
        membership.find_exact_membership(
            rows,
            protein_id="UniProtKB:P12345",
            source_trait_id="PANTHER:PTHR12345",
            uniprot_release="2026_03",
            sequence_sha256=sequence_sha,
        )
        == panther
    )
    assert (
        membership.find_exact_membership(
            rows,
            protein_id="UniProtKB:P12345",
            source_trait_id="PANTHER:PTHR99999",
            uniprot_release="2026_03",
            sequence_sha256=sequence_sha,
        )
        is None
    )


def test_snapshot_round_trip_is_deterministic_and_tamper_evident(tmp_path):
    sequence_sha = hashlib.sha256(b"ACDE").hexdigest()
    rows = membership.extract_entry_memberships(
        {"uniProtKBCrossReferences": [{"database": "NCBIfam", "id": "NF012345"}]},
        protein_id="UniProtKB:P12345",
        sequence_sha256=sequence_sha,
        uniprot_release="2026_03",
    )
    path = tmp_path / "memberships.jsonl"
    first = membership.dump_memberships(rows)
    second = membership.dump_memberships(reversed(rows))
    assert first == second
    path.write_text(first, encoding="utf-8")
    assert membership.load_memberships(path) == rows

    tampered = json.loads(first)
    tampered["database_id"] = "NF999999"
    tampered["source_trait_id"] = "NCBIfam:NF999999"
    tampered["database_cross_reference"]["id"] = "NF999999"
    path.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
    with pytest.raises(membership.MembershipSnapshotError, match="digest mismatch"):
        membership.load_memberships(path)


def test_conflicting_same_membership_fact_is_rejected():
    with pytest.raises(membership.MembershipSnapshotError, match="ambiguous UniProt membership"):
        membership.extract_entry_memberships(
            {
                "uniProtKBCrossReferences": [
                    {
                        "database": "PANTHER",
                        "id": "PTHR12345",
                        "properties": [{"key": "family", "value": "one"}],
                    },
                    {
                        "database": "PANTHER",
                        "id": "PTHR12345",
                        "properties": [{"key": "family", "value": "two"}],
                    },
                ]
            },
            protein_id="UniProtKB:P12345",
            sequence_sha256=hashlib.sha256(b"ACDE").hexdigest(),
            uniprot_release="2026_03",
        )


def test_registry_offline_response_writes_same_release_membership_not_query_claim(
    tmp_path,
):
    sequence = "ACDE"
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    protein_out = tmp_path / "uniprot_registry.jsonl"
    membership_out = tmp_path / "uniprot_memberships.jsonl"
    blocked = tmp_path / "blocked.tsv"
    receipt = tmp_path / "fetch-receipt.json"
    # Discovery claims a different family. The saved provider artifact must contain
    # only what the exact-accession response independently returns.
    _write_jsonl(queue, [_candidate("PANTHER:PTHR99999", sequence)])
    responses.write_text(
        json.dumps(
            {
                "release": "2026_03",
                "responses": [
                    {
                        "requested": ["P12345"],
                        "results": [
                            _entry(
                                "P12345",
                                sequence,
                                [{"database": "PANTHER", "id": "PTHR12345"}],
                            )
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    args = _registry_apply_args(
        queue=queue,
        responses=responses,
        protein_out=protein_out,
        membership_out=membership_out,
        blocked=blocked,
        receipt=receipt,
    )

    assert registry.main(args) == 0
    references = [json.loads(line) for line in protein_out.read_text().splitlines()]
    rows = membership.load_memberships(membership_out)
    assert references[0]["uniprot_release"] == "2026_03"
    assert rows[0]["uniprot_release"] == references[0]["uniprot_release"]
    assert rows[0]["sequence_sha256"] == references[0]["sequence_sha256"]
    assert rows[0]["source_trait_id"] == "PANTHER:PTHR12345"
    assert (
        membership.find_exact_membership(
            rows,
            protein_id="UniProtKB:P12345",
            source_trait_id="PANTHER:PTHR99999",
            uniprot_release="2026_03",
            sequence_sha256=references[0]["sequence_sha256"],
        )
        is None
    )


def test_registry_malformed_membership_preserves_all_previous_outputs(tmp_path, capsys):
    sequence = "ACDE"
    queue = tmp_path / "candidates.jsonl"
    responses = tmp_path / "responses.json"
    protein_out = tmp_path / "uniprot_registry.jsonl"
    membership_out = tmp_path / "uniprot_memberships.jsonl"
    blocked = tmp_path / "blocked.tsv"
    receipt = tmp_path / "fetch-receipt.json"
    _write_jsonl(queue, [_candidate("PANTHER:PTHR12345", sequence)])
    responses.write_text(
        json.dumps(
            {
                "release": "2026_03",
                "responses": [
                    {
                        "requested": ["P12345"],
                        "results": [
                            _entry(
                                "P12345",
                                sequence,
                                [{"database": "PANTHER", "id": ""}],
                            )
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    for path, value in (
        (protein_out, "old proteins\n"),
        (membership_out, "old memberships\n"),
        (blocked, "old blocks\n"),
        (receipt, "old receipt\n"),
    ):
        path.write_text(value, encoding="utf-8")

    args = _registry_apply_args(
        queue=queue,
        responses=responses,
        protein_out=protein_out,
        membership_out=membership_out,
        blocked=blocked,
        receipt=receipt,
    )

    assert registry.main(args) == 2
    assert "cannot snapshot UniProt memberships" in capsys.readouterr().err
    assert protein_out.read_text() == "old proteins\n"
    assert membership_out.read_text() == "old memberships\n"
    assert blocked.read_text() == "old blocks\n"
    assert receipt.read_text() == "old receipt\n"
