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
                {"database": "EMBL", "id": "X00001"},
            ]
        },
        protein_id="UniProtKB:P12345",
        sequence_sha256=sequence_sha,
        uniprot_release="2026_03",
    )

    # An unsupported database (EMBL) is never captured.
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


def test_registry_malformed_membership_blocks_only_its_accession(tmp_path, capsys):
    """#978: a malformed fact is an accession failure for the blocked TSV, not a crash.

    (This used to abort the whole fetch and preserve the previous outputs; abort paths that
    remain keep their own no-partial-write tests.)
    """

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
    args = _registry_apply_args(
        queue=queue,
        responses=responses,
        protein_out=protein_out,
        membership_out=membership_out,
        blocked=blocked,
        receipt=receipt,
    )

    assert registry.main(args) == 0
    assert protein_out.read_text() == ""
    assert membership_out.read_text() == ""
    rows = blocked.read_text().splitlines()
    assert len(rows) == 2 and "FACT_SNAPSHOT_FAILED" in rows[1] and "UniProtKB:P12345" in rows[1]
    assert receipt.is_file()


GO_XREF = {
    "database": "GO",
    "id": "GO:0009390",
    "properties": [
        {"key": "GoTerm", "value": "C:dimethyl sulfoxide reductase complex"},
        {"key": "GoEvidenceType", "value": "IDA:EcoCyc"},
    ],
    "evidences": [{"evidenceCode": "ECO:0000314", "source": "PubMed", "id": "3280546"}],
}
CATALYTIC = {
    "commentType": "CATALYTIC ACTIVITY",
    "reaction": {
        "name": "2-heptyl-4(1H)-quinolone + NADH + O2 + H(+) = ...",
        "reactionCrossReferences": [
            {"database": "Rhea", "id": "RHEA:37871"},
            {"database": "ChEBI", "id": "CHEBI:15377"},
            # Seen in UniProt 2026_03 (O34351): a polymer participant, not a reaction.
            {"database": "Rhea", "id": "RHEA-COMP:9613"},
        ],
        "ecNumber": "1.14.13.182",
    },
    "physiologicalReactions": [
        {
            "directionType": "left-to-right",
            "reactionCrossReference": {"database": "Rhea", "id": "RHEA:37872"},
        }
    ],
}


def _functional_rows(entry: dict) -> list[dict]:
    return membership.extract_entry_memberships(
        entry,
        protein_id="UniProtKB:P18776",
        sequence_sha256=hashlib.sha256(b"ACDE").hexdigest(),
        uniprot_release="2026_03",
    )


def test_functional_facts_are_captured_with_exact_trait_ids_and_evidence_codes():
    rows = _functional_rows(
        {
            "uniProtKBCrossReferences": [
                GO_XREF,
                {"database": "ComplexPortal", "id": "CPX-320", "properties": []},
                # A Rhea cross-reference outside a catalytic-activity reaction is ignored.
                {"database": "Rhea", "id": "RHEA:99999"},
            ],
            "comments": [CATALYTIC, {"commentType": "FUNCTION", "texts": []}],
        }
    )
    by_trait = {row["source_trait_id"]: row for row in rows}
    assert sorted(by_trait) == ["ComplexPortal:CPX-320", "GO:0009390", "RHEA:37871"]
    go = by_trait["GO:0009390"]
    assert go["database"] == "GO" and go["database_id"] == "GO:0009390"
    assert {"key": "GoEvidenceType", "value": "IDA:EcoCyc"} in (
        go["database_cross_reference"]["properties"]
    )
    rhea = by_trait["RHEA:37871"]
    # The reaction's own evidence list travels with the fact (#974); none in this fixture.
    assert rhea["database_cross_reference"] == {
        "database": "Rhea",
        "evidences": [],
        "id": "RHEA:37871",
    }
    # The directional physiological reaction is never a fact here.
    assert "RHEA:37872" not in by_trait
    assert membership.load_memberships  # rows are valid snapshot rows
    assert membership.merge_memberships(rows) == sorted(
        rows,
        key=lambda row: (
            row["protein_id"],
            row["source_trait_id"],
            row["uniprot_release"],
            row["sequence_sha256"],
            row["membership_id"],
        ),
    )


def test_go_no_data_annotations_are_not_facts():
    nd = {
        "database": "GO",
        "id": "GO:0005575",
        "properties": [
            {"key": "GoTerm", "value": "C:cellular_component"},
            {"key": "GoEvidenceType", "value": "ND:UniProtKB"},
        ],
    }
    assert _functional_rows({"uniProtKBCrossReferences": [nd]}) == []


@pytest.mark.parametrize(
    "entry",
    [
        {"uniProtKBCrossReferences": [{"database": "GO", "id": "GO:123"}]},
        {"uniProtKBCrossReferences": [{"database": "ComplexPortal", "id": "CPX-0"}]},
        {
            "comments": [
                {
                    "commentType": "CATALYTIC ACTIVITY",
                    "reaction": {"reactionCrossReferences": [{"database": "Rhea", "id": "37871"}]},
                }
            ]
        },
        {"comments": [{"commentType": "CATALYTIC ACTIVITY", "reaction": "not an object"}]},
    ],
)
def test_malformed_functional_facts_fail_closed(entry):
    with pytest.raises(membership.MembershipSnapshotError):
        _functional_rows(entry)


def test_expected_mapping_method_separates_annotation_from_membership():
    assert membership.expected_mapping_method("GO:0009390") == "SOURCE_ANNOTATION"
    for trait in ("RHEA:37871", "ComplexPortal:CPX-320", "Pfam:PF00001", "CATH:1.10.10.10"):
        assert membership.expected_mapping_method(trait) == "SOURCE_MEMBERSHIP"
    assert membership.UNIPROT_FACT_METHODS == {"SOURCE_MEMBERSHIP", "SOURCE_ANNOTATION"}
    assert membership.CATALYTIC_ACTIVITY_FIELD in membership.FACT_FIELDS
    assert "go_id" in membership.FACT_FIELDS and "xref_complexportal" in membership.FACT_FIELDS


def test_rhea_facts_keep_their_reaction_evidence_sorted_and_skip_isoform_scope():
    evidences = [
        {"evidenceCode": "ECO:0000269", "source": "PubMed", "id": "20662781"},
        {"evidenceCode": "ECO:0000250", "source": "UniProtKB", "id": "P00001"},
    ]
    scoped = {**CATALYTIC, "molecule": "Isoform 2"}
    rows = _functional_rows(
        {
            "comments": [
                {**CATALYTIC, "reaction": {**CATALYTIC["reaction"], "evidences": evidences}},
                scoped,
            ]
        }
    )
    (rhea,) = rows
    assert rhea["database_cross_reference"]["evidences"] == sorted(
        evidences, key=membership.canonical_json
    )
    only_scoped = _functional_rows({"comments": [scoped]})
    assert only_scoped == []


@pytest.mark.parametrize(
    ("xref_or_reaction", "expected"),
    [
        ({"GoEvidenceType": "IDA:EcoCyc"}, None),
        ({"GoEvidenceType": "TAS:Reactome"}, None),
        ({"GoEvidenceType": "IEA:InterPro"}, "go_evidence_IEA"),
        ({"GoEvidenceType": "IBA:GO_Central"}, "go_evidence_IBA"),
        ({"GoEvidenceType": "NAS:ComplexPortal"}, "go_evidence_NAS"),
        ({}, "go_evidence_missing"),
        (["ECO:0000269"], None),
        (["ECO:0000256", "ECO:0000305"], None),
        (["ECO:0000256"], "rhea_evidence_ECO:0000256"),
        (["ECO:0000250"], "rhea_evidence_ECO:0000250"),
        ([], "rhea_evidence_missing_entry_type_missing"),
    ],
)
def test_fact_evidence_policy_is_default_deny(xref_or_reaction, expected):
    if isinstance(xref_or_reaction, dict):
        row = {
            "database": "GO",
            "database_cross_reference": {
                "database": "GO",
                "id": "GO:0009390",
                "properties": [{"key": k, "value": v} for k, v in xref_or_reaction.items()],
            },
        }
    else:
        row = {
            "database": "Rhea",
            "database_cross_reference": {
                "database": "Rhea",
                "id": "RHEA:37871",
                "evidences": [{"evidenceCode": code} for code in xref_or_reaction],
            },
        }
    assert membership.fact_evidence_failure(row) == expected
    # Signature and ComplexPortal facts are governed by their own contracts.
    assert membership.fact_evidence_failure({"database": "ComplexPortal"}) is None


def _go_row(evidence, entry_type=None):
    row = {
        "database": "GO",
        "database_cross_reference": {
            "database": "GO",
            "id": "GO:0008800",
            "properties": [{"key": "GoEvidenceType", "value": evidence}],
        },
    }
    if entry_type is not None:
        row["uniprot_entry_type"] = entry_type
    return row


@pytest.mark.parametrize(
    ("evidence", "entry_type", "expected"),
    [
        ("IEA:UniProtKB-EC", membership.SWISSPROT_ENTRY_TYPE, None),
        ("IEA:UniProtKB-EC", membership.TREMBL_ENTRY_TYPE, "go_evidence_IEA:UniProtKB-EC_on_trembl"),
        ("IEA:UniProtKB-EC", None, "go_evidence_IEA:UniProtKB-EC_entry_type_missing"),
        # Every other automatic source stays excluded, even on Swiss-Prot.
        ("IEA:InterPro", membership.SWISSPROT_ENTRY_TYPE, "go_evidence_IEA"),
        ("IEA:UniProtKB-UniRule", membership.SWISSPROT_ENTRY_TYPE, "go_evidence_IEA"),
        ("IEA:UniProtKB-ARBA", membership.SWISSPROT_ENTRY_TYPE, "go_evidence_IEA"),
        ("IEA:UniProtKB-SubCell", membership.SWISSPROT_ENTRY_TYPE, "go_evidence_IEA"),
        ("IBA:GO_Central", membership.SWISSPROT_ENTRY_TYPE, "go_evidence_IBA"),
    ],
)
def test_swissprot_ec_inference_is_the_only_admitted_go_iea(evidence, entry_type, expected):
    assert membership.fact_evidence_failure(_go_row(evidence, entry_type)) == expected


@pytest.mark.parametrize(
    ("codes", "entry_type", "expected"),
    [
        ([], membership.SWISSPROT_ENTRY_TYPE, None),
        ([], membership.TREMBL_ENTRY_TYPE, "rhea_evidence_missing_on_trembl"),
        # A tagged-but-weak reaction is not "untagged": Swiss-Prot does not rescue it.
        (["ECO:0000250"], membership.SWISSPROT_ENTRY_TYPE, "rhea_evidence_ECO:0000250"),
        (["ECO:0000256"], membership.SWISSPROT_ENTRY_TYPE, "rhea_evidence_ECO:0000256"),
        (["ECO:0000303"], membership.SWISSPROT_ENTRY_TYPE, "rhea_evidence_ECO:0000303"),
    ],
)
def test_untagged_swissprot_reactions_qualify(codes, entry_type, expected):
    row = {
        "database": "Rhea",
        "database_cross_reference": {
            "database": "Rhea",
            "id": "RHEA:37871",
            "evidences": [{"evidenceCode": code} for code in codes],
        },
        "uniprot_entry_type": entry_type,
    }
    assert membership.fact_evidence_failure(row) == expected


def test_entry_type_is_recorded_only_where_the_swissprot_rule_decides():
    ec_xref = {
        "database": "GO",
        "id": "GO:0008800",
        "properties": [{"key": "GoEvidenceType", "value": "IEA:UniProtKB-EC"}],
    }
    rows = _functional_rows(
        {
            "entryType": membership.SWISSPROT_ENTRY_TYPE,
            "uniProtKBCrossReferences": [GO_XREF, ec_xref],
            "comments": [CATALYTIC],
        }
    )
    by_trait = {row["source_trait_id"]: row for row in rows}
    # The IDA fact keeps the pre-#1004 payload, and therefore its content address.
    assert "uniprot_entry_type" not in by_trait["GO:0009390"]
    assert by_trait["GO:0008800"]["uniprot_entry_type"] == membership.SWISSPROT_ENTRY_TYPE
    assert by_trait["RHEA:37871"]["uniprot_entry_type"] == membership.SWISSPROT_ENTRY_TYPE
    assert all(membership.fact_evidence_failure(row) is None for row in rows)
    assert membership.merge_memberships(rows)  # stamped rows are valid snapshot rows
    # An entry type on a fact the rule does not decide is rejected, not ignored.
    stray = {**by_trait["GO:0009390"], "uniprot_entry_type": membership.SWISSPROT_ENTRY_TYPE}
    stray["membership_id"] = membership.compute_membership_id(stray)
    with pytest.raises(membership.MembershipSnapshotError, match="only where"):
        membership.merge_memberships([stray])
    # The stamp is part of the content address.
    unstamped = {k: v for k, v in by_trait["GO:0008800"].items() if k != "uniprot_entry_type"}
    assert membership.compute_membership_id(unstamped) != by_trait["GO:0008800"]["membership_id"]
