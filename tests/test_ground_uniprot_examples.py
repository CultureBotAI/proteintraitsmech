"""Fail-closed tests for candidate resolution and explicit UniProt promotion."""

from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import importlib
import json
import os
import pathlib
import signal
import sys
import threading
from types import MappingProxyType, SimpleNamespace

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
ground = importlib.import_module("ground_uniprot_examples")
grounding_validator = importlib.import_module("validate_uniprot_grounding")
layout = importlib.import_module("grounding_registry_layout")
membership_snapshot = importlib.import_module("uniprot_membership_snapshot")
ecod_sifts = importlib.import_module("build_ecod_sifts_candidates")
biolip_mapper = importlib.import_module("stage_biolip_sifts_mappings")
biolip_sifts = importlib.import_module("fetch_biolip_sifts_uniprot_references")
fetch_registry = importlib.import_module("fetch_uniprot_registry")


def _jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _jsonl_rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _shard_durable_outputs(fixture: dict) -> None:
    """Point the fixture's durable evidence and bindings at sharded ``.jsonl.d`` paths."""

    for key in ("durable_evidence", "durable_bindings"):
        fixture[key] = fixture[key].with_name(fixture[key].name + ".d")


def _durable_exists(path: pathlib.Path) -> bool:
    return path.is_dir() if layout.is_sharded(path) else path.is_file()


def _durable_bytes(path: pathlib.Path) -> bytes:
    """A durable registry's logical bytes: the flat file, or its verified shards joined."""

    if not layout.is_sharded(path):
        return path.read_bytes()
    assert layout.read_registry(path).issues == ()
    return b"".join(shard.read_bytes() for shard in sorted(path.glob("[0-9a-f][0-9a-f].jsonl")))


def _artifact_image(path: pathlib.Path) -> bytes | dict[str, bytes]:
    """Exact on-disk bytes of a file, or of every entry of a sharded registry."""

    if path.is_dir():
        return {entry.name: entry.read_bytes() for entry in sorted(path.iterdir())}
    return path.read_bytes()


def _tree(root: pathlib.Path) -> dict[str, bytes | None]:
    """Every file (with its bytes) and directory (``None``) under ``root``."""

    return {
        entry.relative_to(root).as_posix(): None if entry.is_dir() else entry.read_bytes()
        for entry in sorted(root.rglob("*"))
    }


def _sidecar(path: pathlib.Path, source: str, release: str, proteins: dict) -> None:
    path.write_text(
        json.dumps(
            {
                "_meta": {
                    "schema": 1,
                    "built": "2026-08-23",
                    "source": source,
                    "release": release,
                    "count": len(proteins),
                },
                "proteins": proteins,
            }
        ),
        encoding="utf-8",
    )


def _record(identifier: str = "Pfam:PF00001", axis: str = "SEQUENCE") -> str:
    category = {
        "SEQUENCE": "SEQ_DOMAIN",
        "FUNCTION": "FUNC_PROTEIN_FAMILY",
        "STRUCTURE": "STRUCT_FOLD",
    }[axis]
    return (
        f"identifier: {identifier}\n"
        f"label: Fixture {identifier}\n"
        "definition: >-\n"
        "  A fixture trait.\n"
        "definition_source: Fixture\n"
        f"trait_axis: {axis}\n"
        f"trait_category: {category}\n"
        "mapping_status: SEEDED\n"
        "license: CC0-1.0\n"
    )


@pytest.fixture
def local_sources(tmp_path):
    traits = tmp_path / "traits"
    traits.mkdir()
    record_path = traits / "pfam.yaml"
    record_path.write_text(_record(), encoding="utf-8")
    sequence = "ACDEFGHIK"
    residue = tmp_path / "residue.json"
    interpro = tmp_path / "interpro.json"
    interpro_grouped = tmp_path / "interpro-grouped.json"
    profiles = tmp_path / "profiles.jsonl"
    source_registry = tmp_path / "source_registry.jsonl"
    panther = tmp_path / "PANTHER19.0_HMM_classifications"
    panther.write_text(
        "PTHR10036\tFixture family\n"
        "PTHR10098\tRAPSYN-RELATED\n"
        "PTHR10459\tDNA LIGASE\n"
        "PTHR10459:SF1\tPOLY [ADP-RIBOSE] POLYMERASE 1\n"
        "PTHR10459:SF2\tPROTEIN ADP-RIBOSYLTRANSFERASE PARP3\n",
        encoding="utf-8",
    )
    _sidecar(residue, "UniProt", "2026_02", {"P12345": {"seq": sequence, "ft": []}})
    _sidecar(interpro, "InterPro", "109.0", {"P12345": {"Pfam:PF00001": [[2, 5]]}})
    _sidecar(
        interpro_grouped,
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[[2, 5]]]}},
    )
    _jsonl(
        profiles,
        [
            {
                "accession": "UniProtKB:P12345",
                "name": "Fixture protein",
                "taxon": "NCBITaxon:9606",
                "taxon_label": "Homo sapiens",
                "length": len(sequence),
                "reviewed": True,
            }
        ],
    )
    _jsonl(
        source_registry,
        [
            {
                "protein_id": "UniProtKB:P12345",
                "protein_label": "Fixture protein",
                "taxon_id": "NCBITaxon:9606",
                "taxon_label": "Homo sapiens",
                "sequence": sequence,
                "sequence_length": len(sequence),
                "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
                "reviewed": True,
                "uniprot_release": "2026_02",
            }
        ],
    )
    candidate = {
        "schema_version": 1,
        "batch": "ready-local",
        "candidate_status": "CANDIDATE_PROTEIN",
        "trait_id": "Pfam:PF00001",
        "record_path": str(record_path),
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DOMAIN",
        "protein_id": "UniProtKB:P12345",
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "intervals": [{"start": 2, "end": 5}],
        "residue_positions": [],
        "source_trait_id": "Pfam:PF00001",
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "sequence_release": "2026_02",
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "evidence_tier": "A",
        "qualification_status": "CANDIDATE",
    }
    queue = tmp_path / "candidates.jsonl"
    _jsonl(queue, [candidate])
    return {
        "traits": traits,
        "record": record_path,
        "original": record_path.read_text(encoding="utf-8"),
        "residue": residue,
        "interpro": interpro,
        "interpro_grouped": interpro_grouped,
        "profiles": profiles,
        "source_registry": source_registry,
        "panther": panther,
        "candidate": candidate,
        "queue": queue,
        "resolved": tmp_path / "resolved.jsonl",
        "review": tmp_path / "review.tsv",
        "registry": tmp_path / "protein_registry.jsonl",
        "evidence": tmp_path / "occurrence_evidence.jsonl",
        "membership": tmp_path / "uniprot_memberships.jsonl",
        "sifts": tmp_path / "sifts_mappings.jsonl",
        "durable_registry": tmp_path / "durable" / "protein_registry.jsonl",
        "durable_evidence": tmp_path / "durable" / "occurrence_evidence.jsonl",
        "durable_membership": tmp_path / "durable" / "uniprot_memberships.jsonl",
        "durable_bindings": tmp_path / "durable" / "qualified_record_bindings.jsonl",
    }


def _update_sidecar(path: pathlib.Path, accession: str, entry: dict) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["proteins"][accession] = entry
    payload["_meta"]["count"] = len(payload["proteins"])
    path.write_text(json.dumps(payload), encoding="utf-8")


def _append_jsonl(path: pathlib.Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def _add_second_interpro_candidate(fixture: dict) -> None:
    accession = "Q67890"
    protein_id = f"UniProtKB:{accession}"
    sequence = "ACDEFGHIK"
    sequence_sha256 = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    _update_sidecar(
        fixture["residue"],
        accession,
        {"seq": sequence, "ft": []},
    )
    _update_sidecar(
        fixture["interpro"],
        accession,
        {"Pfam:PF00001": [[2, 5]]},
    )
    _update_sidecar(
        fixture["interpro_grouped"],
        accession,
        {"Pfam:PF00001": [[[2, 5]]]},
    )
    _append_jsonl(
        fixture["profiles"],
        {
            "accession": protein_id,
            "name": "Second fixture protein",
            "taxon": "NCBITaxon:83333",
            "taxon_label": "Escherichia coli",
            "length": len(sequence),
            "reviewed": True,
        },
    )
    _append_jsonl(
        fixture["source_registry"],
        {
            "protein_id": protein_id,
            "protein_label": "Second fixture protein",
            "taxon_id": "NCBITaxon:83333",
            "taxon_label": "Escherichia coli",
            "sequence": sequence,
            "sequence_length": len(sequence),
            "sequence_sha256": sequence_sha256,
            "reviewed": True,
            "uniprot_release": "2026_02",
        },
    )
    _jsonl(
        fixture["queue"],
        [fixture["candidate"], {**fixture["candidate"], "protein_id": protein_id}],
    )


def _resolve_args(fixture: dict) -> list[str]:
    return [
        "resolve",
        "--allow-unreceipted-inputs",
        "--queue",
        str(fixture["queue"]),
        "--traits",
        str(fixture["traits"]),
        "--residue-frame",
        str(fixture["residue"]),
        "--interpro-frame",
        str(fixture["interpro"]),
        "--interpro-grouped-frame",
        str(fixture["interpro_grouped"]),
        "--profiles",
        str(fixture["profiles"]),
        "--protein-registry",
        str(fixture["source_registry"]),
        "--out",
        str(fixture["resolved"]),
        "--review",
        str(fixture["review"]),
        "--registry-out",
        str(fixture["registry"]),
        "--evidence-out",
        str(fixture["evidence"]),
        "--durable-membership-registry",
        str(fixture["durable_membership"]),
        "--panther-classifications",
        str(fixture["panther"]),
        "--panther-classifications-sha256",
        hashlib.sha256(fixture["panther"].read_bytes()).hexdigest(),
        "--batch",
        "ready-local",
    ]


def _prepare_receipt_bound_resolve(fixture: dict) -> list[str]:
    """Install one genuine offline fetch generation and return bounded resolver args."""

    candidate = {
        **fixture["candidate"],
        "batch": "ready-local",
        "batch_id": "ready-local",
        "source_batch": "fixture-source-batch",
        "record_candidate_count": 1,
        "sequence_length": 9,
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    fixture["candidate"] = candidate
    _jsonl(fixture["queue"], [candidate])

    selector = fixture["queue"].with_name("ready-local.manifest.json")
    selector.write_text(
        json.dumps(
            {
                "schema_version": fetch_registry.SELECTOR_MANIFEST_SCHEMA_VERSION,
                "batch_id": "ready-local",
                "source_batch": "fixture-source-batch",
                "candidate_jsonl_sha256": hashlib.sha256(fixture["queue"].read_bytes()).hexdigest(),
                "shard_selected_candidate_rows": 1,
                "shard_selected_trait_records": 1,
                "invariants": {key: True for key in sorted(fetch_registry.SELECTOR_V6_INVARIANTS)},
                "downstream_requirements": {
                    key: True for key in sorted(fetch_registry.SELECTOR_DOWNSTREAM_REQUIREMENTS)
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    responses = fixture["queue"].with_name("ready-local.offline-responses.json")
    responses.write_text(
        json.dumps(
            {
                "release": "2026_02",
                "responses": [
                    {
                        "requested": ["P12345"],
                        "results": [
                            {
                                "primaryAccession": "P12345",
                                "uniProtkbId": "P12345_HUMAN",
                                "entryType": "UniProtKB reviewed (Swiss-Prot)",
                                "proteinDescription": {
                                    "recommendedName": {"fullName": {"value": "Fixture protein"}}
                                },
                                "organism": {
                                    "taxonId": 9606,
                                    "scientificName": "Homo sapiens",
                                },
                                "sequence": {"value": "ACDEFGHIK", "length": 9},
                                "entryAudit": {"sequenceVersion": 1},
                            }
                        ],
                    }
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    blocked = fixture["queue"].with_name("ready-local.registry-blocked.tsv")
    receipt = fixture["queue"].with_name("ready-local.fetch-receipt.json")
    request_plan = fixture["queue"].with_name("ready-local.fetch-plan.json")
    fetch_args = [
        "--queue",
        str(fixture["queue"]),
        "--selector-manifest",
        str(selector),
        "--batch",
        "ready-local",
        "--expect-release",
        "2026_02",
        "--out",
        str(fixture["source_registry"]),
        "--membership-out",
        str(fixture["membership"]),
        "--blocked",
        str(blocked),
        "--receipt",
        str(receipt),
        "--offline-responses",
        str(responses),
    ]
    prepared = fetch_registry._derive_request_plan(fetch_registry._parser().parse_args(fetch_args))
    request_plan.write_text(fetch_registry.render_request_plan(prepared.plan), encoding="utf-8")
    assert fetch_registry.main([*fetch_args, "--request-plan", str(request_plan), "--apply"]) == 0
    fixture.update(
        {
            "selector": selector,
            "fetch_responses": responses,
            "fetch_blocked": blocked,
            "fetch_receipt": receipt,
            "fetch_plan": request_plan,
        }
    )

    args = _resolve_args(fixture)
    args.remove("--allow-unreceipted-inputs")
    args[1:1] = ["--providers", "protein-registry,interpro,uniprot-membership"]
    args.extend(
        [
            "--selector-manifest",
            str(selector),
            "--fetch-request-plan",
            str(request_plan),
            "--fetch-receipt",
            str(receipt),
            "--membership-registry",
            str(fixture["membership"]),
            "--registry-blocked",
            str(blocked),
            "--expect-uniprot-release",
            "2026_02",
            "--allow-offline-uniprot-fixture",
            "--replace-staging-outputs",
        ]
    )
    return args


def _assert_no_resolver_outputs(fixture: dict) -> None:
    assert not any(fixture[key].exists() for key in ("resolved", "review", "registry", "evidence"))


def _forbid_resolver_io(monkeypatch) -> None:
    def unexpected(*_args, **_kwargs):
        pytest.fail("resolver read or write ran before receipt-bound preflight failed")

    monkeypatch.setattr(ground, "_read_jsonl", unexpected)
    monkeypatch.setattr(ground, "_write_jsonl", unexpected)
    monkeypatch.setattr(ground, "_atomic_text", unexpected)


def _resolved(fixture: dict) -> dict:
    return json.loads(fixture["resolved"].read_text(encoding="utf-8"))


def _approve(review: pathlib.Path, approved: pathlib.Path) -> None:
    with review.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
        fieldnames = list(rows[0])
    for row in rows:
        row["decision"] = "APPROVED"
        row["reviewer"] = "Test Curator"
        row["reviewed_at"] = "2026-08-23"
        row["review_notes"] = "Verified fixture evidence."
    with approved.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_decisions(approved: pathlib.Path, decisions: list[tuple[dict, str]]) -> None:
    fieldnames = (
        "candidate_id",
        "resolution_digest",
        "decision",
        "reviewer",
        "reviewed_at",
        "review_notes",
    )
    with approved.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row, decision in decisions:
            reviewed = decision in {"APPROVED", "REJECTED"}
            writer.writerow(
                {
                    "candidate_id": row["candidate_id"],
                    "resolution_digest": row["resolution_digest"],
                    "decision": decision,
                    "reviewer": "Test Curator" if reviewed else "",
                    "reviewed_at": "2026-08-23" if reviewed else "",
                    "review_notes": "Verified fixture evidence." if reviewed else "",
                }
            )


def _alternative(
    row: dict, candidate_id: str, *, trait_id: str | None = None, record_path: str | None = None
) -> dict:
    alternative = {
        **row,
        "candidate_id": candidate_id,
        "trait_id": trait_id or row["trait_id"],
        "record_path": record_path or row["record_path"],
    }
    alternative["resolution_digest"] = ground._resolution_digest(alternative)
    return alternative


def _promote_args(fixture: dict, approved: pathlib.Path, apply: bool = False) -> list[str]:
    args = [
        "promote",
        "--resolved",
        str(fixture["resolved"]),
        "--approved",
        str(approved),
        "--traits",
        str(fixture["traits"]),
        "--protein-registry",
        str(fixture["registry"]),
        "--evidence-registry",
        str(fixture["evidence"]),
        "--membership-registry",
        str(fixture["membership"]),
        "--sifts-registry",
        str(fixture["sifts"]),
        "--durable-protein-registry",
        str(fixture["durable_registry"]),
        "--durable-evidence-registry",
        str(fixture["durable_evidence"]),
        "--durable-membership-registry",
        str(fixture["durable_membership"]),
        "--durable-qualified-record-bindings",
        str(fixture["durable_bindings"]),
        "--panther-classifications",
        str(fixture["panther"]),
        "--panther-classifications-sha256",
        hashlib.sha256(fixture["panther"].read_bytes()).hexdigest(),
        "--min-source-reviews",
        "1",
    ]
    if apply:
        args.append("--apply")
    return args


def _unrelated_registry_rows(fixture: dict, protein_id: str) -> tuple[dict, dict]:
    reference = json.loads(fixture["registry"].read_text(encoding="utf-8"))
    reference["protein_id"] = protein_id
    reference["protein_label"] = f"Existing {protein_id}"
    evidence = json.loads(fixture["evidence"].read_text(encoding="utf-8"))
    evidence["protein_id"] = protein_id
    evidence["evidence_id"] = grounding_validator.compute_evidence_id(evidence)
    return reference, evidence


def _membership_row(
    fixture: dict,
    *,
    trait_id: str = "PANTHER:PTHR12345",
    release: str = "2026_02",
    property_value: str = "fixture",
    sequence_sha256: str | None = None,
) -> dict:
    database_id = trait_id.split(":", 1)[1]
    rows = membership_snapshot.extract_entry_memberships(
        {
            "uniProtKBCrossReferences": [
                {
                    "database": "PANTHER",
                    "id": database_id,
                    "properties": [{"key": "source", "value": property_value}],
                }
            ]
        },
        protein_id="UniProtKB:P12345",
        sequence_sha256=sequence_sha256 or fixture["candidate"]["sequence_sha256"],
        uniprot_release=release,
    )
    return rows[0]


def _write_memberships(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(membership_snapshot.dump_memberships(rows), encoding="utf-8")


def _membership_resolve_args(fixture: dict) -> list[str]:
    args = _resolve_args(fixture)
    args[1:1] = ["--providers", "protein-registry,uniprot-membership"]
    args.extend(["--membership-registry", str(fixture["membership"])])
    args[args.index("--batch") + 1] = "ready-uniprot-membership"
    return args


def _prepare_membership_candidate(fixture: dict) -> tuple[dict, dict]:
    trait_id = "PANTHER:PTHR12345"
    fixture["record"].write_text(_record(trait_id, axis="FUNCTION"), encoding="utf-8")
    candidate = {
        **fixture["candidate"],
        "batch": "ready-uniprot-membership",
        "candidate_status": "PROTEIN_RESOLVED",
        "trait_id": trait_id,
        "record_path": str(fixture["record"]),
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "source_namespace": "PANTHER",
        "scope": "WHOLE_PROTEIN",
        "source_trait_id": trait_id,
        "mapping_method": "SOURCE_MEMBERSHIP",
        "evidence_source": "UniProtKB",
        "source_release": "2026_02",
        "query": "xref:untrusted-query-is-never-evidence",
        "family_classifications": ["PANTHER:UNTRUSTED"],
        "reasons": sorted(ground._MEMBERSHIP_RESOLUTION_REASONS),
    }
    for key in (
        "coordinate_frame",
        "intervals",
        "residue_positions",
        "sequence_release",
        "sequence_sha256",
    ):
        candidate.pop(key, None)
    membership = _membership_row(fixture)
    _write_memberships(fixture["membership"], [membership])
    _jsonl(fixture["queue"], [candidate])
    return candidate, membership


def _prepare_sfld_candidate(fixture: dict) -> dict:
    trait_id = "SFLD:SFLDG00001"
    fixture["record"].write_text(_record(trait_id, axis="FUNCTION"), encoding="utf-8")
    candidate = {
        **fixture["candidate"],
        "trait_id": trait_id,
        "source_trait_id": trait_id,
        "source_namespace": "SFLD",
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": [{"start": 1, "end": 9}],
    }
    _sidecar(
        fixture["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {trait_id: [[1, 9]]}},
    )
    _jsonl(fixture["queue"], [candidate])
    return candidate


def _prepare_prints_candidate(fixture: dict) -> dict:
    trait_id = "PRINTS:PR00001"
    fixture["record"].write_text(_record(trait_id), encoding="utf-8")
    candidate = {
        **fixture["candidate"],
        "trait_id": trait_id,
        "source_trait_id": trait_id,
        "source_namespace": "PRINTS",
    }
    _sidecar(
        fixture["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {trait_id: [[2, 5]]}},
    )
    _jsonl(fixture["queue"], [candidate])
    return candidate


_PRINTS_KDAT_FIXTURE = (
    b"gc; TESTPRINT\n"
    b"gx; PR00001\n"
    b"gn; COMPOUND(2)\n"
    b"gt; Test fingerprint\n"
    b"gd; Source-native description.\n"
    b"fm; FINAL MOTIF-SETS\n"
    b"fm; ----------------\n"
    b"fc; TEST1\n"
    b"fl; 3\n"
    b"ft; Test motif I\n"
    b"fd; ACD PROTEIN 1 1\n"
    b"KD; INTER_MOTIF_DISTANCE REGION=0-1; MIN=1; MAX=1\n"
    b"fc; TEST2\n"
    b"fl; 3\n"
    b"ft; Test motif II\n"
    b"fd; EFG PROTEIN 5 1\n"
    b"KD; INTER_MOTIF_DISTANCE REGION=1-2; MIN=1; MAX=1 /R\n"
)


def _prints_release_fixture(tmp_path, monkeypatch):
    """Parse compact KDAT through a test-scoped canonical digest allowlist."""
    prints_kdat = importlib.import_module("prints_kdat")
    path = tmp_path / "prints42_0.kdat"
    path.write_bytes(_PRINTS_KDAT_FIXTURE)
    digest = hashlib.sha256(_PRINTS_KDAT_FIXTURE).hexdigest()
    monkeypatch.setattr(
        prints_kdat,
        "_CANONICAL_RELEASE_FINGERPRINTS",
        MappingProxyType({prints_kdat.PRINTS_42_0_RELEASE: digest}),
    )
    return ground.parse_prints_kdat(path, digest)


def _sifts_resolve_args(fixture: dict) -> list[str]:
    args = _resolve_args(fixture)
    args[1:1] = ["--providers", "protein-registry,sifts-mapping"]
    args.extend(
        [
            "--sifts-registry",
            str(fixture["sifts"]),
            "--allow-offline-sifts-fixtures",
        ]
    )
    args[args.index("--batch") + 1] = "ready-sifts"
    return args


def _prepare_sifts_candidate(fixture: dict) -> tuple[dict, dict, dict, dict]:
    trait_id = "ECOD:F.1.2.3.4"
    fixture["record"].write_text(_record(trait_id, axis="STRUCTURE"), encoding="utf-8")
    reference = json.loads(fixture["source_registry"].read_text(encoding="utf-8"))
    ecod_line = "1\te1abcA1\tTrue\t1.2.3.4\t1abc\tA\tA:10A-10B\tA:1-2"
    ecod_source = fixture["sifts"].with_name("ecod-fixture.txt")
    ecod_source.write_text(
        "# ECOD Domain List\n"
        "# Version: vTEST\n"
        "uid\tecod_domain_id\tmanual_rep\tf_id\tpdb\tchain\tpdb_range\tseqid_range\n"
        f"{ecod_line}\n",
        encoding="utf-8",
    )
    xml_bytes = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<entry xmlns="http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd" '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'dbSource="PDBe" dbVersion="2.0" dbCoordSys="PDBe" '
        'dbAccessionId="1abc" date="2026-08-17">'
        '<rdf:RDF><rdf:Description rdf:about="self">'
        f'<dc:rights rdf:resource="{ecod_sifts.SIFTS_RIGHTS_URL}">'
        "fixture SIFTS rights</dc:rights>"
        "</rdf:Description></rdf:RDF>"
        '<listDB><db dbSource="PDB" dbVersion="33.26"/>'
        '<db dbSource="UniProt" dbVersion="2026.02"/></listDB>'
        '<entity type="protein" entityId="A"><segment segId="fixture">'
        "<listResidue>"
        '<residue dbSource="PDBe" dbCoordSys="PDBe" dbResNum="1" dbResName="CYS">'
        '<crossRefDb dbSource="PDB" dbCoordSys="PDBresnum" '
        'dbAccessionId="1abc" dbResNum="10A" dbResName="CYS" dbChainId="A"/>'
        '<crossRefDb dbSource="UniProt" dbCoordSys="UniProt" '
        'dbAccessionId="P12345" dbResNum="2" dbResName="C"/>'
        "</residue>"
        '<residue dbSource="PDBe" dbCoordSys="PDBe" dbResNum="2" dbResName="ASP">'
        '<crossRefDb dbSource="PDB" dbCoordSys="PDBresnum" '
        'dbAccessionId="1abc" dbResNum="null" dbResName="ASP" dbChainId="A"/>'
        '<crossRefDb dbSource="UniProt" dbCoordSys="UniProt" '
        'dbAccessionId="P12345" dbResNum="3" dbResName="D"/>'
        "</residue>"
        "</listResidue></segment></entity></entry>"
    ).encode("utf-8")
    xml_sha = hashlib.sha256(xml_bytes).hexdigest()
    manifest_entry = {
        "pdb_id": "1abc",
        "path": "1abc.xml",
        "sha256": xml_sha,
        "sifts_entry_date": "2026-08-17",
        "sifts_uniprot_release": reference["uniprot_release"],
        "sifts_uniprot_version": "2026.02",
        "url": f"{ecod_sifts.SIFTS_XML_ROOT}/1abc.xml.gz",
    }
    snapshot_id = "fixture-2026-08-24"
    manifest_path = fixture["sifts"].with_name("offline-fixture-manifest.json")
    (manifest_path.parent / manifest_entry["path"]).write_bytes(xml_bytes)
    mapping_payload = {
        "schema_version": 1,
        "trait_id": trait_id,
        "ecod_domain_id": "e1abcA1",
        "ecod_uid": "1",
        "ecod_release": "ECOD vTEST",
        "ecod_license": ecod_sifts.ECOD_LICENSE,
        "ecod_source_path": ground._display_path(ecod_source),
        "ecod_source_sha256": hashlib.sha256(ecod_source.read_bytes()).hexdigest(),
        "ecod_line_number": 4,
        "ecod_raw_line_sha256": hashlib.sha256(ecod_line.encode("utf-8")).hexdigest(),
        "structure_id": "PDB:1abc",
        "chain_id": "A",
        "ecod_chain": "A",
        "ecod_pdb_range": "A:10A-10B",
        "ecod_seqid_range": "A:1-2",
        "native_ranges": [
            {
                "chain_id": "A",
                "start": {
                    "author_residue_number": 10,
                    "author_insertion_code": "A",
                },
                "end": {
                    "author_residue_number": 10,
                    "author_insertion_code": "B",
                },
            }
        ],
        "protein_id": reference["protein_id"],
        "sequence_sha256": reference["sequence_sha256"],
        "uniprot_release": reference["uniprot_release"],
        "sifts_snapshot_mode": ecod_sifts.OFFLINE_FIXTURE,
        "sifts_snapshot_id": snapshot_id,
        "sifts_manifest_path": ground._display_path(manifest_path),
        "sifts_manifest_sha256": ecod_sifts._fixture_manifest_sha(snapshot_id, manifest_entry),
        "sifts_manifest_entry": manifest_entry,
        "sifts_manifest_entry_sha256": ecod_sifts.value_sha256(manifest_entry),
        "sifts_entry_date": "2026-08-17",
        "sifts_uniprot_release": reference["uniprot_release"],
        "sifts_uniprot_version": "2026.02",
        "sifts_xml_sha256": xml_sha,
        "sifts_source_url": f"{ecod_sifts.SIFTS_XML_ROOT}/1abc.xml.gz",
        "sifts_rights": "fixture SIFTS rights",
        "sifts_rights_url": ecod_sifts.SIFTS_RIGHTS_URL,
        "mapped_residues": [
            {
                "chain_id": "A",
                "pdbe_sequence_position": 1,
                "author_residue_number": 10,
                "author_insertion_code": "A",
                "pdb_amino_acid": "C",
                "uniprot_position": 2,
                "uniprot_amino_acid": "C",
            },
            {
                "chain_id": "A",
                "pdbe_sequence_position": 2,
                "author_residue_number": None,
                "author_insertion_code": None,
                "pdb_amino_acid": "D",
                "uniprot_position": 3,
                "uniprot_amino_acid": "D",
            },
        ],
    }
    mapping_sha = ecod_sifts.mapping_entry_sha256(mapping_payload)
    mapping = {"mapping_id": f"ecod-sifts:{mapping_sha}", **mapping_payload}
    provider_release = "SIFTS 2026-08-17; UniProt 2026_02"
    occurrence = {
        "trait_id": trait_id,
        "protein_id": reference["protein_id"],
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "residue_positions": [2, 3],
        "expected_residues": "CD",
        "source_trait_id": trait_id,
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "ECOD via PDBe SIFTS",
        "source_release": "ECOD vTEST",
        "sequence_sha256": reference["sequence_sha256"],
        "structure_id": "PDB:1abc",
        "chain_id": "A",
        "mapping_completeness": "COMPLETE",
        "source_residue_count": 2,
        "mapped_residue_count": 2,
        "qualification_status": "LOCATION_VERIFIED",
    }
    evidence = grounding_validator.build_grounding_evidence(
        occurrence,
        provider_kind="SIFTS",
        provider_source=ground._display_path(fixture["sifts"]),
        provider_release=provider_release,
        provider_entry_sha256=mapping_sha,
    )
    occurrence["source_evidence_id"] = evidence["evidence_id"]
    candidate = {
        "batch": "ready-sifts",
        "candidate_status": "LOCATION_VERIFIED",
        "qualification_status": "CANDIDATE_PROTEIN",
        "trait_id": trait_id,
        "record_path": str(fixture["record"]),
        "source_namespace": "ECOD",
        "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_FOLD",
        "protein_id": reference["protein_id"],
        "protein_label": reference["protein_label"],
        "taxon_id": reference["taxon_id"],
        "taxon_label": reference["taxon_label"],
        "sequence_length": reference["sequence_length"],
        "sequence_sha256": reference["sequence_sha256"],
        "sequence_release": reference["uniprot_release"],
        "reviewed": reference["reviewed"],
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "intervals": [{"start": 2, "end": 3}],
        "residue_positions": [2, 3],
        "expected_residues": "CD",
        "source_trait_id": trait_id,
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "ECOD via PDBe SIFTS",
        "source_release": "ECOD vTEST",
        "evidence_tier": "B",
        "mapping_completeness": "COMPLETE",
        "source_residue_count": 2,
        "mapped_residue_count": 2,
        "structure_id": "PDB:1abc",
        "chain_id": "A",
        "ecod_domain_id": "e1abcA1",
        "ecod_pdb_range": "A:10A-10B",
        "ecod_native_ranges": mapping["native_ranges"],
        "sifts_mapping_id": mapping["mapping_id"],
        "sifts_release": provider_release,
        "reasons": [],
        "provider_evidence": [
            {
                "kind": "sifts_mapping",
                "path": ground._display_path(fixture["sifts"]),
                "key": mapping["mapping_id"],
                "source": "PDBe SIFTS",
                "release": provider_release,
                "entry_sha256": mapping_sha,
                "trait_id": trait_id,
            }
        ],
        "trait_occurrence": occurrence,
        "grounding_evidence": evidence,
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    _jsonl(fixture["sifts"], [mapping])
    _jsonl(fixture["queue"], [candidate])
    return candidate, mapping, occurrence, evidence


def _prepare_biolip_sifts_candidate(fixture: dict, tmp_path: pathlib.Path) -> tuple[dict, dict]:
    trait_id = "proteintraitsmech:BIOLIP_ATP"
    fixture["record"].write_text(_record(trait_id, axis="STRUCTURE"), encoding="utf-8")

    stage = tmp_path / "biolip-stage.jsonl"
    snapshot = tmp_path / "biolip-sifts-snapshot"
    snapshot.mkdir()
    occurrence = {
        "schema_version": 1,
        "kind": biolip_mapper.INPUT_OCCURRENCE_KIND,
        "stage_status": "READY_FOR_RESIDUE_LEVEL_SIFTS",
        "qualification_claimed": False,
        "protein_identity_claimed": False,
        "uniprot_coordinates_claimed": False,
        "source_residue_count": 1,
        "binding_residue_pairs": [
            {
                "author_insertion_code": "",
                "author_residue_number": 1,
                "author_residue_token": "A1",
                "biolip_receptor_sequence_position": 1,
                "ordinal": 1,
                "receptor_sequence_residue_token": "A1",
                "source_amino_acid": "A",
            }
        ],
        "source_binding": {
            "binding_residues_pdb_author_text": "A1",
            "binding_residues_receptor_sequence_text": "A1",
            "binding_site_code": "BS01",
            "ligand_chain_id": "X",
            "ligand_id": "ATP",
            "ligand_serial_number_text": "1",
            "receptor_chain_id": "A",
            "receptor_sequence_length": 1,
            "receptor_sequence_sha256": "3" * 64,
            "resolution_text": "1.0",
            "source_field_projection_sha256": "4" * 64,
            "source_line_numbers": [1],
            "source_occurrence_key": {
                "binding_site_code": "BS01",
                "ligand_chain": "X",
                "ligand_id": "ATP",
                "ligand_serial_number": "1",
                "pdb_id": "1abc",
                "receptor_chain": "A",
            },
            "source_physical_line_count": 1,
            "source_raw_line_sha256": "0" * 64,
            "source_raw_line_sha256_basis": "RAW_UTF8_PHYSICAL_LINE_INCLUDING_LF",
            "source_uniprot_accession_claims": [],
            "source_uniprot_claim_status": "MISSING",
            "source_uniprot_field_text": "",
            "structure_id": "PDB:1abc",
        },
        "trait_binding": {
            "ligand_id": "ATP",
            "trait_id": trait_id,
            "trait_record_has_canonical_examples": False,
            "trait_record_path": str(fixture["record"]),
            "trait_record_sha256": "1" * 64,
            "trait_source_xref_status": "EXACT_SEEDER_SOURCE_XREFS",
            "trait_source_xrefs": ["pdb.ligand:ATP"],
        },
        "source_occurrence_id": "biolip-missing-protein-source-occurrence:ok",
        "source_occurrence_row_sha256": "2" * 64,
    }
    stage_summary = {
        "schema_version": 1,
        "kind": biolip_mapper.INPUT_SUMMARY_KIND,
        "stage_id": "biolip-missing-protein-stage:fixture",
        "combined_non_summary_rows_sha256": "fixture",
        "ready_for_residue_level_sifts_count": 1,
    }
    stage.write_text(
        "".join(
            biolip_mapper.canonical_json(row) + "\n"
            for row in (occurrence, stage_summary)
        ),
        encoding="utf-8",
    )

    xml = gzip.compress(
        b"""<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd"
       xmlns:dc="http://purl.org/dc/elements/1.1/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       dbSource="PDBe"
       dbCoordSys="PDBe"
       dbAccessionId="1abc"
       date="2026-09-27">
  <listDB><db dbSource="UniProt" dbVersion="2026.03"/></listDB>
  <entity>
    <segment>
      <listResidue>
        <residue dbSource="PDBe" dbCoordSys="PDBe" dbResNum="1">
          <crossRefDb dbSource="PDB" dbCoordSys="PDBresnum"
                      dbAccessionId="1abc" dbChainId="A"
                      dbResNum="1" dbResName="ALA"/>
          <crossRefDb dbSource="UniProt" dbCoordSys="UniProt"
                      dbAccessionId="P12345" dbResNum="10" dbResName="A"/>
        </residue>
      </listResidue>
    </segment>
  </entity>
  <dc:rights rdf:resource="http://pdbe.org/sifts">PDBe SIFTS terms</dc:rights>
</entry>
"""
    )
    sifts_xml = snapshot / "1abc.xml.gz"
    sifts_xml.write_bytes(xml)
    manifest_entry = {
        "path": sifts_xml.name,
        "pdb_id": "1abc",
        "sha256": hashlib.sha256(xml).hexdigest(),
        "sifts_entry_date": "2026-09-27",
        "sifts_uniprot_release": "2026_03",
        "sifts_uniprot_version": "2026.03",
        "size_bytes": len(xml),
        "url": f"{biolip_mapper.SIFTS_XML_ROOT}/{sifts_xml.name}",
    }
    manifest = {
        "schema_version": 1,
        "kind": biolip_mapper.SNAPSHOT_KIND,
        "complete": True,
        "entries": [manifest_entry],
        "failures": [],
        "fetch_request_count": 1,
        "requested_pdb_count": 1,
        "snapshot_id": "fixture",
        "source": "PDBe SIFTS residue-level XML",
        "source_root": biolip_mapper.SIFTS_XML_ROOT,
        "stage_combined_non_summary_rows_sha256": "fixture",
        "stage_id": "biolip-missing-protein-stage:fixture",
        "stage_path": "biolip-stage.jsonl",
        "stage_sha256": hashlib.sha256(stage.read_bytes()).hexdigest(),
    }
    (snapshot / "manifest.json").write_text(
        biolip_mapper.canonical_json(manifest) + "\n",
        encoding="utf-8",
    )

    responses = tmp_path / "biolip-uniprot-responses.json"
    responses.write_text(
        json.dumps(
            {
                "release": "2026_03",
                "responses": [
                    {
                        "requested": ["P12345"],
                        "results": [
                            {
                                "primaryAccession": "P12345",
                                "uniProtkbId": "P12345_FIXTURE",
                                "entryType": "UniProtKB reviewed (Swiss-Prot)",
                                "proteinDescription": {
                                    "recommendedName": {
                                        "fullName": {"value": "Fixture protein"}
                                    }
                                },
                                "organism": {
                                    "taxonId": 562,
                                    "scientificName": "Escherichia coli",
                                },
                                "sequence": {"value": "CCCCCCCCCA", "length": 10},
                                "entryAudit": {"sequenceVersion": 3},
                                "uniProtKBCrossReferences": [
                                    {"database": "Pfam", "id": "PF00001", "properties": []}
                                ],
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    registry = tmp_path / "biolip-registry.jsonl"
    memberships = tmp_path / "biolip-memberships.jsonl"
    mappings = tmp_path / "biolip-mappings.jsonl"
    blocked = tmp_path / "biolip-blocked.tsv"
    receipt = tmp_path / "biolip-receipt.json"
    plan = tmp_path / "biolip-plan.json"
    args = [
        "--stage",
        str(stage),
        "--sifts-snapshot",
        str(snapshot),
        "--expect-release",
        "2026_03",
        "--out",
        str(registry),
        "--membership-out",
        str(memberships),
        "--mapping-out",
        str(mappings),
        "--blocked",
        str(blocked),
        "--receipt",
        str(receipt),
        "--offline-responses",
        str(responses),
    ]
    namespace = biolip_sifts.parser().parse_args(args)
    prepared = biolip_sifts._derive_request_plan(namespace)
    plan.write_text(biolip_sifts.render_request_plan(prepared.plan), encoding="utf-8")
    assert biolip_sifts.main([*args, "--request-plan", str(plan), "--apply"]) == 0

    [reference] = _jsonl_rows(registry)
    [mapping] = _jsonl_rows(mappings)
    fixture["source_registry"].write_bytes(registry.read_bytes())
    _sidecar(
        fixture["residue"],
        "UniProt",
        reference["uniprot_release"],
        {"P12345": {"seq": reference["sequence"], "ft": []}},
    )
    _jsonl(fixture["profiles"], [])
    fixture["sifts"] = mappings

    provider_release = ground._sifts_provider_release(mapping)
    mapping_sha = biolip_sifts.mapping_entry_sha256(mapping)
    candidate = {
        "batch": "ready-sifts",
        "candidate_status": "LOCATION_VERIFIED",
        "qualification_status": "CANDIDATE_PROTEIN",
        "trait_id": trait_id,
        "record_path": str(fixture["record"]),
        "source_namespace": "BioLiP",
        "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_FOLD",
        "protein_id": reference["protein_id"],
        "protein_label": reference["protein_label"],
        "taxon_id": reference["taxon_id"],
        "taxon_label": reference["taxon_label"],
        "sequence_length": reference["sequence_length"],
        "sequence_sha256": reference["sequence_sha256"],
        "sequence_release": reference["uniprot_release"],
        "reviewed": reference["reviewed"],
        "scope": mapping["scope"],
        "coordinate_frame": mapping["coordinate_frame"],
        "intervals": [{"start": 10, "end": 10}],
        "residue_positions": mapping["residue_positions"],
        "expected_residues": mapping["expected_residues"],
        "source_trait_id": trait_id,
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "BioLiP via PDBe SIFTS",
        "source_release": None,
        "evidence_tier": "B",
        "mapping_completeness": mapping["mapping_completeness"],
        "source_residue_count": mapping["source_residue_count"],
        "mapped_residue_count": mapping["mapped_residue_count"],
        "structure_id": mapping["structure_id"],
        "chain_id": mapping["chain_id"],
        "sifts_mapping_id": mapping["mapping_id"],
        "sifts_release": provider_release,
        "reasons": [],
        "provider_evidence": [
            {
                "kind": "sifts_mapping",
                "path": ground._display_path(mappings),
                "key": mapping["mapping_id"],
                "source": "PDBe SIFTS",
                "release": provider_release,
                "entry_sha256": mapping_sha,
                "trait_id": trait_id,
            }
        ],
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    _jsonl(fixture["queue"], [candidate])
    return candidate, mapping


def test_candidate_id_covers_sequence_release_coordinates_and_positions(local_sources):
    row = local_sources["candidate"]
    candidate_id = ground.derive_candidate_id(row)
    assert candidate_id.startswith("ug-") and len(candidate_id) == 67
    assert ground.derive_candidate_id({**row, "sequence_release": "2026_03"}) != candidate_id
    assert ground.derive_candidate_id({**row, "intervals": [[3, 5]]}) != candidate_id
    assert ground.derive_candidate_id({**row, "residue_positions": [4]}) != candidate_id
    assert (
        ground.derive_candidate_id(
            {**row, "interpro_location_id": "interpro-location:a"}
        )
        != ground.derive_candidate_id(
            {**row, "interpro_location_id": "interpro-location:b"}
        )
    )
    assert ground.derive_interpro_location_id(
        "UniProtKB:P12345",
        "Pfam:PF00001",
        [{"start": 7, "end": 8}, {"start": 2, "end": 3}],
    ) == ground.derive_interpro_location_id(
        "UniProtKB:P12345",
        "Pfam:PF00001",
        [{"start": 2, "end": 3}, {"start": 7, "end": 8}],
    )
    # Schema-facing resolved rows use uniprot_release, but retain the same identity.
    resolved_shape = {**row, "uniprot_release": row["sequence_release"]}
    resolved_shape.pop("sequence_release")
    assert ground.derive_candidate_id(resolved_shape) == candidate_id


def test_receipt_bound_resolve_accepts_one_exact_offline_test_generation(local_sources):
    args = _prepare_receipt_bound_resolve(local_sources)

    assert ground.main(args) == 0
    assert _resolved(local_sources)["qualification_status"] == "QUALIFIED"
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]


@pytest.mark.parametrize(
    ("fixture_key", "forged_bytes"),
    [
        ("queue", b'{"batch":"ready-local"}\n'),
        ("source_registry", b'{"protein_id":"UniProtKB:P12345"}\n'),
        ("membership", b'{"protein_id":"UniProtKB:P12345"}\n'),
    ],
)
def test_bounded_resolve_uses_verified_bytes_across_swap_and_restore(
    local_sources, monkeypatch, capsys, fixture_key, forged_bytes
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    swapped_path = local_sources[fixture_key]
    original_bytes = swapped_path.read_bytes()
    original_verify = ground.verify_fetch_receipt
    calls = 0

    def swap_between_verifications(*, receipt_path, request_plan_path):
        nonlocal calls
        calls += 1
        if calls == 1:
            verified = original_verify(
                receipt_path=receipt_path,
                request_plan_path=request_plan_path,
            )
            swapped_path.write_bytes(forged_bytes)
            return verified
        assert calls == 2
        swapped_path.write_bytes(original_bytes)
        return original_verify(
            receipt_path=receipt_path,
            request_plan_path=request_plan_path,
        )

    monkeypatch.setattr(ground, "verify_fetch_receipt", swap_between_verifications)

    assert ground.main(args) == 0
    assert calls == 2
    assert swapped_path.read_bytes() == original_bytes
    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["trait_id"] == "Pfam:PF00001"
    assert row["protein_label"] == "Fixture protein"


def test_bounded_registry_evidence_path_ignores_swapped_symlink_target(
    local_sources, monkeypatch, capsys
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    registry_path = local_sources["source_registry"]
    original_bytes = registry_path.read_bytes()
    backup = registry_path.with_name("verified-registry-backup.jsonl")
    forged_target = registry_path.with_name("forged-registry-target.jsonl")
    forged_target.write_bytes(b'{"protein_id":"UniProtKB:P12345"}\n')
    original_verify = ground.verify_fetch_receipt
    calls = 0

    def swap_symlink_between_verifications(*, receipt_path, request_plan_path):
        nonlocal calls
        calls += 1
        if calls == 1:
            verified = original_verify(
                receipt_path=receipt_path,
                request_plan_path=request_plan_path,
            )
            registry_path.rename(backup)
            registry_path.symlink_to(forged_target)
            return verified
        assert calls == 2
        registry_path.unlink()
        backup.rename(registry_path)
        return original_verify(
            receipt_path=receipt_path,
            request_plan_path=request_plan_path,
        )

    monkeypatch.setattr(ground, "verify_fetch_receipt", swap_symlink_between_verifications)

    assert ground.main(args) == 0
    assert calls == 2
    assert registry_path.read_bytes() == original_bytes
    source_evidence = next(
        evidence
        for evidence in _resolved(local_sources)["provider_evidence"]
        if evidence["kind"] == "source_protein_registry"
    )
    assert source_evidence["path"] == ground._lexical_display_path(registry_path)
    assert source_evidence["path"] != str(forged_target)


def test_generic_resolve_requires_explicit_unreceipted_mode_before_any_io(
    local_sources, monkeypatch, capsys
):
    args = _resolve_args(local_sources)
    args.remove("--allow-unreceipted-inputs")
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "use --allow-unreceipted-inputs only for the generic historical path" in (
        capsys.readouterr().err
    )
    _assert_no_resolver_outputs(local_sources)


@pytest.mark.parametrize("missing_option", ["--fetch-receipt", "--fetch-request-plan"])
def test_bounded_resolve_requires_receipt_and_plan_together_before_any_io(
    local_sources, monkeypatch, capsys, missing_option
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    index = args.index(missing_option)
    del args[index : index + 2]
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert missing_option in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


def test_bounded_resolve_rejects_tampered_receipt_before_any_io(local_sources, monkeypatch, capsys):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    local_sources["fetch_receipt"].write_text(
        local_sources["fetch_receipt"].read_text(encoding="utf-8") + " ",
        encoding="utf-8",
    )
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "invalid UniProt fetch receipt boundary" in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


@pytest.mark.parametrize(
    "fixture_key",
    ["selector", "source_registry", "membership", "fetch_blocked"],
)
def test_bounded_resolve_rejects_tampered_bound_artifact_before_any_io(
    local_sources, monkeypatch, capsys, fixture_key
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    path = local_sources[fixture_key]
    path.write_bytes(path.read_bytes() + b"tampered")
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "invalid UniProt fetch receipt boundary" in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


def test_bounded_resolve_rejects_stale_queue_before_any_io(local_sources, monkeypatch, capsys):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    stale = _jsonl_rows(local_sources["queue"])[0]
    stale["source_release"] = "110.0"
    _jsonl(local_sources["queue"], [stale])
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "invalid UniProt fetch receipt boundary" in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


@pytest.mark.parametrize(
    ("option", "fixture_key"),
    [
        ("--queue", "queue"),
        ("--selector-manifest", "selector"),
        ("--protein-registry", "source_registry"),
        ("--membership-registry", "membership"),
        ("--registry-blocked", "fetch_blocked"),
    ],
)
def test_bounded_resolve_rejects_same_byte_path_substitution_before_any_io(
    local_sources, monkeypatch, capsys, option, fixture_key
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    source = local_sources[fixture_key]
    substitute = source.with_name(f"substitute-{source.name}")
    substitute.write_bytes(source.read_bytes())
    args[args.index(option) + 1] = str(substitute)
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "resolver inputs do not match the verified fetch generation" in (capsys.readouterr().err)
    _assert_no_resolver_outputs(local_sources)


@pytest.mark.parametrize(
    ("option", "value"),
    [("--batch", "stale-batch"), ("--expect-uniprot-release", "2026_03")],
)
def test_bounded_resolve_rejects_batch_or_release_drift_before_any_io(
    local_sources, monkeypatch, capsys, option, value
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    args[args.index(option) + 1] = value
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "does not match verified fetch generation" in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


def test_bounded_resolve_rejects_offline_receipt_without_test_only_flag(
    local_sources, monkeypatch, capsys
):
    args = _prepare_receipt_bound_resolve(local_sources)
    capsys.readouterr()
    args.remove("--allow-offline-uniprot-fixture")
    _forbid_resolver_io(monkeypatch)

    assert ground.main(args) == 2
    assert "OFFLINE_FIXTURE UniProt acquisition is test-only" in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


def test_resolve_is_read_only_deterministic_and_emits_registry(local_sources):
    assert ground.main(_resolve_args(local_sources)) == 0
    first = {
        path: local_sources[path].read_bytes()
        for path in ("resolved", "review", "registry", "evidence")
    }
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]
    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["protein_label"] == "Fixture protein"
    assert row["taxon_id"] == "NCBITaxon:9606"
    assert row["uniprot_release"] == "2026_02"
    assert row["trait_occurrence"] == {
        "coordinate_frame": "UNIPROT_CANONICAL",
        "evidence_source": "InterPro",
        "intervals": [{"end": 5, "start": 2}],
        "mapping_method": "INTERPRO_MATCH",
        "protein_id": "UniProtKB:P12345",
        "qualification_status": "QUALIFIED",
        "scope": "LOCALIZED",
        "sequence_sha256": local_sources["candidate"]["sequence_sha256"],
        "source_evidence_id": row["grounding_evidence"]["evidence_id"],
        "source_release": "109.0",
        "source_trait_id": "Pfam:PF00001",
        "trait_id": "Pfam:PF00001",
    }
    registry = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    assert registry["sequence"] == "ACDEFGHIK"
    assert registry["sequence_sha256"] == local_sources["candidate"]["sequence_sha256"]
    evidence = json.loads(local_sources["evidence"].read_text(encoding="utf-8"))
    assert evidence == row["grounding_evidence"]
    assert evidence["provider_kind"] == "INTERPRO"
    assert evidence["provider_source"] == "InterPro"
    assert {item["kind"] for item in row["provider_evidence"]} == {
        "interpro_frame",
        "profiles",
        "protein_registry",
        "residue_frame",
        "source_protein_registry",
    }
    with local_sources["review"].open(encoding="utf-8", newline="") as handle:
        review = next(csv.DictReader(handle, delimiter="\t"))
    assert review["decision"] == ""
    assert review["resolution_digest"] == row["resolution_digest"]
    # A one-row JSONL file is also a valid standalone JSON object.  The loader must
    # recognize it as a registry row, not mistake its fields for an accession map.
    assert ground.main(_resolve_args(local_sources)) == 0
    assert all(local_sources[path].read_bytes() == first[path] for path in first)


def test_cath_interpro_candidate_is_rejected_by_central_receipt_lock(local_sources):
    trait_id = "CATH:1.10.10.10"
    local_sources["record"].write_text(_record(trait_id, axis="STRUCTURE"), encoding="utf-8")
    candidate = {
        **local_sources["candidate"],
        "trait_id": trait_id,
        "source_trait_id": trait_id,
        "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_FOLD",
    }
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {trait_id: [[2, 5]]}},
    )
    _jsonl(local_sources["queue"], [candidate])

    assert ground.main(_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["invalid:grounding_evidence:cath_provider_receipt_required"]
    assert "trait_occurrence" not in row
    assert "grounding_evidence" not in row
    assert local_sources["registry"].read_text(encoding="utf-8") == ""
    assert local_sources["evidence"].read_text(encoding="utf-8") == ""


@pytest.mark.parametrize("option", ["--out", "--review", "--registry-out", "--evidence-out"])
@pytest.mark.parametrize("via_symlink", [False, True])
def test_resolve_rejects_every_staging_output_under_protected_grounding(
    local_sources, monkeypatch, capsys, option, via_symlink
):
    protected_root = local_sources["traits"].parent / "protected-grounding"
    protected_root.mkdir()
    target = protected_root / f"{option.removeprefix('--')}.sentinel"
    target.write_bytes(b"protected grounding bytes\n")
    output = target
    if via_symlink:
        output = local_sources["traits"].parent / f"{target.name}.alias"
        output.symlink_to(target)
    monkeypatch.setattr(ground, "PROTECTED_GROUNDING_ROOT", protected_root)
    args = _resolve_args(local_sources)
    args[args.index(option) + 1] = str(output)

    assert ground.main(args) == 2
    assert "outside protected trait/grounding data" in capsys.readouterr().err
    assert target.read_bytes() == b"protected grounding bytes\n"
    assert all(
        not local_sources[key].exists()
        for key in ("resolved", "review", "registry", "evidence")
        if local_sources[key] != target
    )


@pytest.mark.parametrize("option", ["--out", "--review", "--registry-out", "--evidence-out"])
@pytest.mark.parametrize(
    "protected_root_name",
    ["canonical-traits", "canonical-grounding", "selected-traits"],
)
@pytest.mark.parametrize("through_symlink", [False, True], ids=["direct", "symlink-alias"])
def test_resolve_rejects_all_outputs_across_exact_protected_roots_before_write(
    local_sources,
    monkeypatch,
    option,
    protected_root_name,
    through_symlink,
):
    protected_roots = {
        "canonical-traits": ground.DEFAULT_TRAITS,
        "canonical-grounding": ground.PROTECTED_GROUNDING_ROOT,
        "selected-traits": local_sources["traits"],
    }
    protected_root = protected_roots[protected_root_name]
    probe_name = f"_grounding_resolve_no_write_probe_{option.removeprefix('--')}"
    canonical_probe = protected_root / probe_name
    assert not canonical_probe.exists()
    output_parent = protected_root
    if through_symlink:
        output_parent = local_sources["traits"].parent / f"{protected_root_name}-alias"
        output_parent.symlink_to(protected_root, target_is_directory=True)

    args = _resolve_args(local_sources)
    args[args.index(option) + 1] = str(output_parent / probe_name)
    attempted_writes = []

    def reject_write(*write_args, **_write_kwargs):
        attempted_writes.append(write_args[0])
        raise AssertionError(f"path validation reached a write: {write_args[0]}")

    monkeypatch.setattr(ground, "_write_jsonl", reject_write)
    monkeypatch.setattr(ground, "_atomic_text", reject_write)
    assert ground.main(args) == 2
    assert attempted_writes == []
    assert not canonical_probe.exists()


@pytest.mark.parametrize("option", ["--out", "--review", "--registry-out", "--evidence-out"])
@pytest.mark.parametrize(
    "protected_root_name",
    ["canonical-traits", "canonical-grounding", "selected-traits"],
)
def test_resolve_rejects_case_varied_physical_aliases_before_write(
    local_sources,
    monkeypatch,
    option,
    protected_root_name,
):
    roots = {
        "canonical-traits": (
            ground.DEFAULT_TRAITS,
            ground.REPO_ROOT / "DATA" / "TRAITS",
        ),
        "canonical-grounding": (
            ground.PROTECTED_GROUNDING_ROOT,
            ground.REPO_ROOT / "DATA" / "GROUNDING",
        ),
        "selected-traits": (
            local_sources["traits"],
            local_sources["traits"].with_name(local_sources["traits"].name.swapcase()),
        ),
    }
    protected_root, case_alias = roots[protected_root_name]
    try:
        physically_aliased = case_alias.samefile(protected_root)
    except OSError:
        physically_aliased = False
    if not physically_aliased:
        pytest.skip("filesystem is case-sensitive for this protected root")

    probe_name = f"_grounding_resolve_case_alias_probe_{option.removeprefix('--')}"
    canonical_probe = protected_root / probe_name
    assert not canonical_probe.exists()
    args = _resolve_args(local_sources)
    args[args.index(option) + 1] = str(case_alias / probe_name)
    attempted_writes = []

    def reject_write(*write_args, **_write_kwargs):
        attempted_writes.append(write_args[0])
        raise AssertionError(f"path validation reached a write: {write_args[0]}")

    monkeypatch.setattr(ground, "_write_jsonl", reject_write)
    monkeypatch.setattr(ground, "_atomic_text", reject_write)
    assert ground.main(args) == 2
    assert attempted_writes == []
    assert not canonical_probe.exists()


@pytest.mark.parametrize("via_symlink", [False, True])
def test_resolve_rejects_staging_output_under_selected_trait_root(
    local_sources, capsys, via_symlink
):
    target = local_sources["record"]
    original = target.read_bytes()
    output = target
    if via_symlink:
        output = local_sources["traits"].parent / "trait-output.alias"
        output.symlink_to(target)
    args = _resolve_args(local_sources)
    args[args.index("--out") + 1] = str(output)

    assert ground.main(args) == 2
    assert "outside protected trait/grounding data" in capsys.readouterr().err
    assert target.read_bytes() == original
    _assert_no_resolver_outputs(local_sources)


def test_resolve_rejects_output_aliasing_input_or_another_output(local_sources, capsys):
    input_alias_args = _resolve_args(local_sources)
    input_alias_args[input_alias_args.index("--out") + 1] = str(local_sources["queue"])
    assert ground.main(input_alias_args) == 2
    assert "aliases a resolver input" in capsys.readouterr().err
    assert len(_jsonl_rows(local_sources["queue"])) == 1
    _assert_no_resolver_outputs(local_sources)

    duplicate_args = _resolve_args(local_sources)
    duplicate_args[duplicate_args.index("--out") + 1] = str(local_sources["evidence"])
    assert ground.main(duplicate_args) == 2
    assert "must be four distinct paths" in capsys.readouterr().err
    _assert_no_resolver_outputs(local_sources)


def test_resolve_rejects_case_varied_existing_input_alias(local_sources, capsys):
    queue = local_sources["queue"]
    case_alias = queue.with_name(queue.name.swapcase())
    try:
        physically_aliased = case_alias.samefile(queue)
    except OSError:
        physically_aliased = False
    if not physically_aliased:
        pytest.skip("filesystem is case-sensitive for the queue path")
    original = queue.read_bytes()
    args = _resolve_args(local_sources)
    args[args.index("--out") + 1] = str(case_alias)

    assert ground.main(args) == 2
    assert "aliases a resolver input" in capsys.readouterr().err
    assert queue.read_bytes() == original
    _assert_no_resolver_outputs(local_sources)


def test_resolve_rejects_case_only_collision_between_new_output_names(local_sources, capsys):
    first = local_sources["traits"].parent / "FutureLedger.jsonl"
    second = local_sources["traits"].parent / "futureledger.JSONL"
    assert not first.exists() and not second.exists()
    args = _resolve_args(local_sources)
    args[args.index("--out") + 1] = str(first)
    args[args.index("--evidence-out") + 1] = str(second)

    assert ground.main(args) == 2
    assert "must be four distinct paths" in capsys.readouterr().err
    assert not first.exists() and not second.exists()
    _assert_no_resolver_outputs(local_sources)


def test_resolve_rejects_unicode_normalized_collision_between_new_output_names(
    local_sources, capsys
):
    composed = local_sources["traits"].parent / "caf\N{LATIN SMALL LETTER E WITH ACUTE}.jsonl"
    decomposed = local_sources["traits"].parent / "cafe\N{COMBINING ACUTE ACCENT}.jsonl"
    assert not composed.exists() and not decomposed.exists()
    args = _resolve_args(local_sources)
    args[args.index("--out") + 1] = str(composed)
    args[args.index("--evidence-out") + 1] = str(decomposed)

    assert ground.main(args) == 2
    assert "must be four distinct paths" in capsys.readouterr().err
    assert not composed.exists() and not decomposed.exists()
    _assert_no_resolver_outputs(local_sources)


def test_resolve_default_retains_cumulative_staging_rows(local_sources):
    assert ground.main(_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    selected_evidence = json.loads(local_sources["evidence"].read_text(encoding="utf-8"))
    unrelated_reference, unrelated_evidence = _unrelated_registry_rows(
        local_sources, "UniProtKB:Q54321"
    )
    _jsonl(local_sources["registry"], [unrelated_reference, selected_reference])
    _jsonl(local_sources["evidence"], [unrelated_evidence, selected_evidence])

    assert ground.main(_resolve_args(local_sources)) == 0

    assert {row["protein_id"] for row in _jsonl_rows(local_sources["registry"])} == {
        "UniProtKB:P12345",
        "UniProtKB:Q54321",
    }
    assert {row["evidence_id"] for row in _jsonl_rows(local_sources["evidence"])} == {
        selected_evidence["evidence_id"],
        unrelated_evidence["evidence_id"],
    }


def test_resolve_replace_staging_prunes_stale_rows_and_is_byte_idempotent(local_sources):
    assert ground.main(_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    selected_evidence = json.loads(local_sources["evidence"].read_text(encoding="utf-8"))
    unrelated_reference, unrelated_evidence = _unrelated_registry_rows(
        local_sources, "UniProtKB:Q54321"
    )
    _jsonl(local_sources["registry"], [unrelated_reference, selected_reference])
    _jsonl(local_sources["evidence"], [unrelated_evidence, selected_evidence])
    args = [*_resolve_args(local_sources), "--replace-staging-outputs"]

    assert ground.main(args) == 0
    assert _jsonl_rows(local_sources["registry"]) == [selected_reference]
    assert _jsonl_rows(local_sources["evidence"]) == [selected_evidence]
    first = {
        key: local_sources[key].read_bytes()
        for key in ("resolved", "review", "registry", "evidence")
    }

    assert ground.main(args) == 0
    assert all(local_sources[key].read_bytes() == content for key, content in first.items())


def test_resolve_replace_staging_prunes_candidate_that_becomes_rejected(local_sources):
    assert ground.main(_resolve_args(local_sources)) == 0
    assert len(_jsonl_rows(local_sources["registry"])) == 1
    assert len(_jsonl_rows(local_sources["evidence"])) == 1
    record = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))
    record["label"] = "DNA-binding protein <locus_tag>"
    local_sources["record"].write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")

    assert ground.main([*_resolve_args(local_sources), "--replace-staging-outputs"]) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["unqualifiable:record_content:unresolved_source_placeholder"]
    assert local_sources["registry"].read_text(encoding="utf-8") == ""
    assert local_sources["evidence"].read_text(encoding="utf-8") == ""


def test_resolve_replace_staging_rejects_debug_limit(local_sources, capsys):
    args = [
        *_resolve_args(local_sources),
        "--replace-staging-outputs",
        "--limit",
        "1",
    ]

    assert ground.main(args) == 2
    assert "cannot be combined with --limit" in capsys.readouterr().err
    assert all(
        not local_sources[key].exists() for key in ("resolved", "review", "registry", "evidence")
    )


def test_sfld_resolve_is_unqualifiable_until_source_model_repair(local_sources):
    _prepare_sfld_candidate(local_sources)
    record_before = local_sources["record"].read_bytes()

    assert ground.main(_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert row["candidate_status"] == "REJECTED"
    assert row["reasons"] == [
        "invalid:grounding_evidence:sfld_provider_receipt_required",
        ground._SFLD_SOURCE_MODEL_REPAIR_REASON,
    ]
    assert "trait_occurrence" not in row
    assert "grounding_evidence" not in row
    assert local_sources["registry"].read_text(encoding="utf-8") == ""
    assert local_sources["evidence"].read_text(encoding="utf-8") == ""
    assert local_sources["record"].read_bytes() == record_before


def test_prints_resolve_is_unqualifiable_until_fingerprint_model_replay(local_sources):
    _prepare_prints_candidate(local_sources)
    record_before = local_sources["record"].read_bytes()

    assert ground.main(_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert row["candidate_status"] == "REJECTED"
    assert row["reasons"] == [
        "invalid:grounding_evidence:prints_provider_receipt_required",
        ground._PRINTS_FINGERPRINT_MODEL_REPLAY_REASON,
    ]
    assert "trait_occurrence" not in row
    assert "grounding_evidence" not in row
    assert local_sources["registry"].read_text(encoding="utf-8") == ""
    assert local_sources["evidence"].read_text(encoding="utf-8") == ""
    assert local_sources["record"].read_bytes() == record_before


def test_prints_snapshot_provider_emits_shape_compatible_nonqualifying_diagnostic(
    local_sources, monkeypatch
):
    candidate = _prepare_prints_candidate(local_sources)
    candidate["intervals"] = [{"start": 1, "end": 3}, {"start": 5, "end": 7}]
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {"PRINTS:PR00001": [[1, 3], [5, 7]]}},
    )
    _jsonl(local_sources["queue"], [candidate])
    release = _prints_release_fixture(local_sources["traits"].parent, monkeypatch)
    manifest_id = "prints-snapshot:" + "a" * 64
    monkeypatch.setattr(
        ground,
        "verify_prints_manifest",
        lambda *args, **kwargs: {"manifest_id": manifest_id},
    )
    monkeypatch.setattr(ground, "parse_prints_kdat", lambda *args, **kwargs: release)
    args = _resolve_args(local_sources)
    args[1:1] = ["--providers", "protein-registry,interpro,prints-snapshot"]

    assert ground.main(args) == 0

    row = _resolved(local_sources)
    replay = row["prints_interval_shape_diagnostic"]
    assert replay["status"] == "ANONYMOUS_INTERVAL_SHAPE_COMPATIBLE"
    assert replay["diagnostic_semantics"] == (
        "ANONYMOUS_INTERVAL_SHAPE_COMPATIBILITY_NOT_MOTIF_OCCURRENCE_REPLAY"
    )
    assert replay["record_model_status"] == "MISSING_RECORD_REPRESENTATION"
    assert replay["count_matches_model"] and replay["length_vector_matches_model"]
    assert not replay["motif_identity_verified"]
    assert not replay["occurrence_grouping_verified"]
    assert not replay["grounding_eligible"]
    assert replay["snapshot_manifest_id"] == manifest_id
    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == sorted(
        {
            "ambiguous:ungrouped_interpro_locations",
            ground._PRINTS_FINGERPRINT_MODEL_REPLAY_REASON,
            "missing:prints_record_fingerprint_representation",
        }
    )
    model_evidence = [
        item for item in row["provider_evidence"] if item["kind"] == "prints_fingerprint_model"
    ]
    assert len(model_evidence) == 1
    assert model_evidence[0]["snapshot_manifest_id"] == manifest_id
    assert local_sources["registry"].read_text(encoding="utf-8") == ""


def test_prints_snapshot_provider_labels_partial_fingerprint(local_sources, monkeypatch):
    _prepare_prints_candidate(local_sources)
    release = _prints_release_fixture(local_sources["traits"].parent, monkeypatch)
    monkeypatch.setattr(
        ground,
        "verify_prints_manifest",
        lambda *args, **kwargs: {"manifest_id": "prints-snapshot:" + "b" * 64},
    )
    monkeypatch.setattr(ground, "parse_prints_kdat", lambda *args, **kwargs: release)
    args = _resolve_args(local_sources)
    args[1:1] = ["--providers", "protein-registry,interpro,prints-snapshot"]

    assert ground.main(args) == 0

    row = _resolved(local_sources)
    assert row["prints_interval_shape_diagnostic"]["status"] == ("ANONYMOUS_INTERVAL_COUNT_SHORT")
    assert "mismatch:prints_anonymous_interval_count_vs_motif_count" in row["reasons"]
    assert ground._PRINTS_FINGERPRINT_MODEL_REPLAY_REASON in row["reasons"]


def test_prints_record_representation_projection_replays_exactly(tmp_path, monkeypatch):
    release = _prints_release_fixture(tmp_path, monkeypatch)
    fingerprint = release.fingerprints["PR00001"]
    representation = {
        "source_accession": "PRINTS:PR00001",
        "source_release": release.release,
        "representation_type": "PRINTS_FINAL_ORDERED_MOTIF_SETS",
        "source_artifact": ground.PRINTS_42_0_SOURCE_ARTIFACT,
        "source_artifact_sha256": release.source_artifact_sha256,
        "source_record_sha256": fingerprint.source_record_sha256,
        "compatible_derivation_tool_hint": "EMBOSS_PRINTSEXTRACT",
        "motif_count": 2,
        "motifs": [
            {
                "ordinal": motif.ordinal,
                "length": motif.length,
                "source_motif_sha256": motif.source_motif_sha256,
                "motif_code": motif.code,
                "description": motif.description,
                "training_instance_count": len(motif.instances),
                "training_distance_from_previous_min": (motif.training_distance_from_previous_min),
                "training_distance_from_previous_max": (motif.training_distance_from_previous_max),
                **(
                    {
                        "inter_motif_distance_constraint": {
                            "region_start_ordinal": (
                                motif.inter_motif_distance_constraint.region_start_ordinal
                            ),
                            "region_end_ordinal": (
                                motif.inter_motif_distance_constraint.region_end_ordinal
                            ),
                            "minimum": motif.inter_motif_distance_constraint.minimum,
                            "maximum": motif.inter_motif_distance_constraint.maximum,
                            "repeat_qualified": (
                                motif.inter_motif_distance_constraint.repeat_qualified
                            ),
                        }
                    }
                    if motif.inter_motif_distance_constraint is not None
                    else {}
                ),
            }
            for motif in fingerprint.motifs
        ],
    }
    context = ground.ProviderContext(
        providers={"prints-snapshot"},
        residue_path=tmp_path / "unused.json",
        prints_manifest_path=tmp_path / "manifest.json",
        prints_manifest={"manifest_id": "prints-snapshot:" + "c" * 64},
        prints_release=release,
    )

    diagnostic, evidence, reasons = ground._prints_interval_shape_diagnostic(
        {"trait_id": "PRINTS:PR00001", "source_trait_id": "PRINTS:PR00001"},
        {
            "identifier": "PRINTS:PR00001",
            "sequence_fingerprint_representations": [representation],
        },
        [{"start": 1, "end": 3}, {"start": 5, "end": 7}],
        context,
    )

    assert diagnostic is not None
    assert diagnostic["record_model_status"] == "EXACT_RECORD_REPRESENTATION"
    assert diagnostic["status"] == "ANONYMOUS_INTERVAL_SHAPE_COMPATIBLE"
    assert diagnostic["motif_identity_verified"] is False
    assert diagnostic["occurrence_grouping_verified"] is False
    assert diagnostic["grounding_eligible"] is False
    assert reasons == []
    assert len(evidence) == 1


def test_prints_identity_gate_uses_namespace_or_curie():
    assert ground._is_prints_grounding({"source_namespace": "prints"})
    assert ground._is_prints_grounding({"identifier": "PRINTS:PR00001"})
    assert ground._is_prints_grounding({"trait_id": "PRINTS:PR00001"})
    assert ground._is_prints_grounding({"source_trait_id": "PRINTS:PR00001"})
    assert not ground._is_prints_grounding({"source_namespace": "Pfam"})


def test_sifts_mapping_stays_candidate_only_without_provider_receipt(local_sources):
    candidate, mapping, _occurrence, _evidence = _prepare_sifts_candidate(local_sources)
    assert candidate["candidate_id"] == ecod_sifts._candidate_id(candidate)
    assert (
        ground.derive_candidate_id({**candidate, "structure_id": "PDB:2xyz"})
        != candidate["candidate_id"]
    )
    assert ground.derive_candidate_id({**candidate, "chain_id": "B"}) != candidate["candidate_id"]
    assert (
        ground.derive_candidate_id({**candidate, "ecod_domain_id": "e1abcA2"})
        != candidate["candidate_id"]
    )
    assert (
        ground.derive_candidate_id({**candidate, "sifts_mapping_id": "ecod-sifts:" + "0" * 64})
        != candidate["candidate_id"]
    )

    assert ground.main(_sifts_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["invalid:sifts_grounding_evidence:ecod_provider_receipt_required"]
    assert row["intervals"] == candidate["intervals"]
    assert row["residue_positions"] == candidate["residue_positions"]
    assert "trait_occurrence" not in row
    assert "grounding_evidence" not in row
    sifts_provider = next(
        item for item in row["provider_evidence"] if item["kind"] == "sifts_mapping"
    )
    assert sifts_provider["key"] == mapping["mapping_id"]
    assert sifts_provider["entry_sha256"] == ecod_sifts.mapping_entry_sha256(mapping)
    assert local_sources["registry"].read_text(encoding="utf-8") == ""
    assert local_sources["evidence"].read_text(encoding="utf-8") == ""


def test_biolip_sifts_mapping_loads_and_resolves_fail_closed_without_source_release(
    local_sources, tmp_path
):
    candidate, mapping = _prepare_biolip_sifts_candidate(local_sources, tmp_path)

    loaded = ground._load_sifts_mapping_registry(local_sources["sifts"])

    assert loaded == {mapping["mapping_id"]: mapping}
    assert ground._sifts_mapping_entry_sha256(mapping) == biolip_sifts.mapping_entry_sha256(
        mapping
    )
    assert ground._sifts_expected_mapping_id(
        mapping,
        biolip_sifts.mapping_entry_sha256(mapping),
    ) == mapping["mapping_id"]
    assert ground._sifts_expected_chain(mapping) == "A"
    assert ground._sifts_evidence_source(mapping) == "BioLiP via PDBe SIFTS"
    assert ground._sifts_authoritative_source_release(mapping) is None

    assert ground.main(_sifts_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["missing:sifts_source_release", "missing:source_release"]
    assert row["intervals"] == candidate["intervals"]
    assert row["residue_positions"] == candidate["residue_positions"]
    assert "trait_occurrence" not in row
    assert "grounding_evidence" not in row
    sifts_provider = next(
        item for item in row["provider_evidence"] if item["kind"] == "sifts_mapping"
    )
    assert sifts_provider["key"] == mapping["mapping_id"]
    assert sifts_provider["entry_sha256"] == biolip_sifts.mapping_entry_sha256(mapping)
    assert local_sources["registry"].read_text(encoding="utf-8") == ""
    assert local_sources["evidence"].read_text(encoding="utf-8") == ""


def test_biolip_sifts_mapping_loader_rejects_tampered_content_address(
    local_sources, tmp_path, capsys
):
    _candidate, mapping = _prepare_biolip_sifts_candidate(local_sources, tmp_path)
    mapping["mapping_row_sha256"] = "0" * 64
    _jsonl(local_sources["sifts"], [mapping])

    assert ground.main(_sifts_resolve_args(local_sources)) == 2
    assert "BioLiP/SIFTS mapping_row_sha256 mismatch" in capsys.readouterr().err
    assert not local_sources["resolved"].exists()


def test_sifts_provider_requires_explicit_registry(local_sources, capsys):
    _prepare_sifts_candidate(local_sources)
    args = _sifts_resolve_args(local_sources)
    index = args.index("--sifts-registry")
    del args[index : index + 2]

    assert ground.main(args) == 2
    assert "provider sifts-mapping requires --sifts-registry" in capsys.readouterr().err
    assert not local_sources["resolved"].exists()


def test_sifts_offline_fixture_registry_requires_explicit_test_mode(local_sources, capsys):
    _prepare_sifts_candidate(local_sources)
    args = _sifts_resolve_args(local_sources)
    args.remove("--allow-offline-sifts-fixtures")

    assert ground.main(args) == 2
    assert "OFFLINE_FIXTURE mapping rejected" in capsys.readouterr().err
    assert not local_sources["resolved"].exists()


def test_sifts_resolver_replays_bound_ecod_source_before_resolution(local_sources, capsys):
    _, mapping, _, _ = _prepare_sifts_candidate(local_sources)
    ecod_source = pathlib.Path(mapping["ecod_source_path"])
    ecod_source.write_text(
        ecod_source.read_text(encoding="utf-8").replace("e1abcA1", "e1abcA9"),
        encoding="utf-8",
    )

    assert ground.main(_sifts_resolve_args(local_sources)) == 2
    assert "ECOD source file digest mismatch" in capsys.readouterr().err
    assert not local_sources["resolved"].exists()


@pytest.mark.parametrize(
    "tamper,reason",
    [
        ("top-level-coordinates", "mismatch:sifts_candidate_intervals"),
        ("embedded-occurrence", "mismatch:sifts_trait_occurrence_projection"),
        ("reference-binding", "mismatch:sifts_mapping_sequence_sha256"),
    ],
)
def test_sifts_resolution_rejects_mutated_coordinates_projection_or_mapping(
    local_sources, tamper, reason
):
    candidate, mapping, _, _ = _prepare_sifts_candidate(local_sources)
    if tamper == "top-level-coordinates":
        candidate["intervals"] = [{"start": 2, "end": 2}]
    elif tamper == "embedded-occurrence":
        candidate["trait_occurrence"]["residue_positions"] = [2]
    else:
        mapping = dict(mapping)
        mapping.pop("mapping_id")
        mapping["sequence_sha256"] = "0" * 64
        mapping_sha = ecod_sifts.mapping_entry_sha256(mapping)
        mapping = {"mapping_id": f"ecod-sifts:{mapping_sha}", **mapping}
        candidate["sifts_mapping_id"] = mapping["mapping_id"]
        candidate["provider_evidence"][0]["key"] = mapping["mapping_id"]
        candidate["provider_evidence"][0]["entry_sha256"] = mapping_sha
        evidence = grounding_validator.build_grounding_evidence(
            candidate["trait_occurrence"],
            provider_kind="SIFTS",
            provider_source=ground._display_path(local_sources["sifts"]),
            provider_release=candidate["sifts_release"],
            provider_entry_sha256=mapping_sha,
        )
        candidate["trait_occurrence"]["source_evidence_id"] = evidence["evidence_id"]
        candidate["grounding_evidence"] = evidence
        _jsonl(local_sources["sifts"], [mapping])
    _jsonl(local_sources["queue"], [candidate])

    assert ground.main(_sifts_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert reason in row["reasons"]
    assert "trait_occurrence" not in row


def test_sifts_promotion_is_blocked_until_durable_authenticity_replay_exists(
    local_sources, monkeypatch, capsys
):
    _prepare_sifts_candidate(local_sources)
    assert ground.main(_sifts_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("sifts-blocked-promotion.tsv")
    _approve(local_sources["review"], approved)
    # The authenticity-contract blocker must fire before even attempting to reopen
    # a provider, and certainly before any durable or trait write.
    local_sources["sifts"].unlink()
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    error = capsys.readouterr().err
    assert "SIFTS promotion is disabled" in error
    assert "pinned ECOD raw line" in error
    assert "immutable SIFTS XML manifest" in error
    assert writes == []
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_ready_local_batch_filter_does_not_include_unlabelled_ledger_rows(local_sources):
    unlabelled = {**local_sources["candidate"], "candidate_id": "unlabelled-row"}
    unlabelled.pop("batch")
    _jsonl(local_sources["queue"], [unlabelled, local_sources["candidate"]])
    assert ground.main(_resolve_args(local_sources)) == 0
    rows = [json.loads(line) for line in local_sources["resolved"].read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["batch"] == "ready-local"


def test_whole_protein_keeps_real_match_footprint_out_of_occurrence(local_sources):
    local_sources["record"].write_text(
        _record("PANTHER:PTHR12345", axis="FUNCTION"), encoding="utf-8"
    )
    candidate = {
        **local_sources["candidate"],
        "trait_id": "PANTHER:PTHR12345",
        "source_trait_id": "PANTHER:PTHR12345",
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": [{"start": 1, "end": 9}],
    }
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {"PANTHER:PTHR12345": [[1, 9]]}},
    )
    _jsonl(local_sources["queue"], [candidate])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["intervals"] == [{"end": 9, "start": 1}]
    assert row["trait_occurrence"]["scope"] == "WHOLE_PROTEIN"
    assert "intervals" not in row["trait_occurrence"]
    assert "coordinate_frame" not in row["trait_occurrence"]


def _prepare_panther_content_gate_fixture(
    local_sources, *, template_only: bool, redundant_class: bool = False
) -> None:
    identifier = "PANTHER:PTHR10036"
    record = yaml.safe_load(_record(identifier, axis="FUNCTION"))
    if template_only:
        definition = (
            "Fixture PANTHER:PTHR10036 — a full-length protein family modelled by "
            "the PANTHER 19.0 profile HMM PTHR10036."
        )
        if redundant_class:
            definition += " PANTHER protein class: Fixture."
        record["definition"] = definition
        record["definition_source"] = "PANTHER 19.0 profile HMM PTHR10036"
        record["definitions"] = [
            {
                "text": definition,
                "method": "GENERATED",
                "generated_by": "seed_panther.py",
            }
        ]
    local_sources["record"].write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    candidate = {
        **local_sources["candidate"],
        "trait_id": identifier,
        "source_trait_id": identifier,
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": [{"start": 1, "end": 9}],
    }
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {identifier: [[1, 9]]}},
    )
    _jsonl(local_sources["queue"], [candidate])


def _prepare_low_coverage_panther_fixture(local_sources) -> None:
    identifier = "PANTHER:PTHR10098"
    definition = (
        "RAPSYN-RELATED — a full-length protein family modelled by the PANTHER 19.0 "
        "profile HMM PTHR10098. PANTHER protein class: scaffold/adaptor protein."
    )
    record = yaml.safe_load(_record(identifier, axis="SEQUENCE"))
    record.update(
        {
            "label": "RAPSYN-RELATED",
            "definition": definition,
            "definition_source": "PANTHER 19.0 composed seeder output",
            "definitions": [
                {
                    "kind": "GENERAL",
                    "text": definition,
                    "source": "PANTHER 19.0 composed seeder output",
                    "method": "GENERATED",
                }
            ],
            "trait_category": "SEQ_FAMILY",
        }
    )
    local_sources["record"].write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    candidate = {
        **local_sources["candidate"],
        "trait_id": identifier,
        "source_trait_id": identifier,
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_FAMILY",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": [{"start": 2, "end": 2}],
    }
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {identifier: [[2, 2]]}},
    )
    _jsonl(local_sources["queue"], [candidate])


def _require_pinned_record_content_sources() -> None:
    """Skip when the record-content replay's pinned downloads are absent (#610).

    The replay verifies each source against a pinned SHA-256, so a synthetic
    fixture cannot stand in without also overriding four hashes. These tests
    assumed the downloads were present rather than gating on them, which made
    them green only on a machine that had already fetched them -- the #569 shape.

    Skipping is this repo's existing pattern for artifact-conditional tests, and
    it carries the same cost: the assertions below never run in CI. A synthetic
    source set with overridden pins would be strictly better, noted on #610.
    """
    gate = importlib.import_module("uniprot_record_content_gate")
    missing = [
        path.name
        for path in (
            gate.DEFAULT_INTERPRO_XML,
            gate.DEFAULT_PFAM_CLANS,
            gate.DEFAULT_PFAM_TYPES,
            gate.DEFAULT_PANTHER_CLASSIFICATIONS,
        )
        if not path.is_file()
    ]
    if missing:
        pytest.skip(f"pinned record-content sources are unavailable: {', '.join(missing)}")


def _prepare_panther_identity_fixture(local_sources, *, conflicting: bool) -> None:
    identifier = "PANTHER:PTHR10459"
    label = "DNA LIGASE" if conflicting else "ADP-ribosyltransferase PARP"
    definition = (
        f"{label} — a full-length protein family modelled by the PANTHER 19.0 "
        "profile HMM PTHR10459. PANTHER protein class: DNA metabolism protein."
    )
    record = yaml.safe_load(_record(identifier, axis="SEQUENCE"))
    record.update(
        {
            "label": label,
            "definition": definition,
            "definition_source": "PANTHER 19.0 composed seeder output",
            "definitions": [
                {
                    "kind": "GENERAL",
                    "text": definition,
                    "source": "PANTHER 19.0 composed seeder output",
                    "method": "GENERATED",
                }
            ],
            "mapped_xrefs": [
                {
                    "object": "InterPro:IPR050800",
                    "mapping_source": "interpro-member-list",
                }
            ],
            "trait_category": "SEQ_FAMILY",
        }
    )
    local_sources["record"].write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    candidate = {
        **local_sources["candidate"],
        "trait_id": identifier,
        "source_trait_id": identifier,
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_FAMILY",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": [{"start": 1, "end": 9}],
    }
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {identifier: [[1, 9]]}},
    )
    _jsonl(local_sources["queue"], [candidate])


def test_resolver_attaches_hard_record_content_finding(local_sources):
    _prepare_panther_content_gate_fixture(local_sources, template_only=True)

    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)

    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["unqualifiable:record_content:definition_template_only"]
    assert [finding["code"] for finding in row["record_content_findings"]] == [
        "DEFINITION_TEMPLATE_ONLY"
    ]
    assert row["record_content_findings"][0]["severity"] == "HARD"
    # Record-level hard reasons must be installed before occurrence resolution.
    # This preserves the historical rejected-row shape and its digest semantics.
    assert "trait_occurrence" not in row
    assert "grounding_evidence" not in row


def test_resolver_attaches_low_panther_coverage_as_review_only(local_sources):
    _prepare_low_coverage_panther_fixture(local_sources)

    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)

    assert row["qualification_status"] == "QUALIFIED"
    assert row["reasons"] == []
    assert [finding["code"] for finding in row["record_content_findings"]] == [
        "LOW_WHOLE_PROTEIN_FAMILY_COVERAGE"
    ]
    assert row["record_content_findings"][0]["severity"] == "REVIEW"
    with local_sources["review"].open(encoding="utf-8", newline="") as handle:
        review = next(csv.DictReader(handle, delimiter="\t"))
    assert "RECORD_CONTENT:LOW_WHOLE_PROTEIN_FAMILY_COVERAGE" in review["review_flags"]


def test_resolver_hard_rejects_panther_family_identity_conflict(local_sources):
    _require_pinned_record_content_sources()
    _prepare_panther_identity_fixture(local_sources, conflicting=True)

    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)

    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["unqualifiable:record_content:source_family_identity_conflict"]
    finding = row["record_content_findings"][0]
    assert finding["code"] == "SOURCE_FAMILY_IDENTITY_CONFLICT"
    assert [binding["kind"] for binding in finding["source_bindings"]] == [
        "PANTHER_HMM_CLASSIFICATIONS",
        "INTERPRO_XML",
    ]


def test_promoter_recomputes_but_does_not_hard_block_low_panther_coverage(
    local_sources,
):
    _prepare_low_coverage_panther_fixture(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("low-coverage-approved.tsv")
    _approve(local_sources["review"], approved)

    assert ground.main(_promote_args(local_sources, approved, apply=False)) == 0


def test_promoter_independently_recomputes_panther_identity_conflict(local_sources, capsys):
    _require_pinned_record_content_sources()
    _prepare_panther_identity_fixture(local_sources, conflicting=False)
    assert ground.main(_resolve_args(local_sources)) == 0
    assert _resolved(local_sources)["qualification_status"] == "QUALIFIED"
    approved = local_sources["review"].with_name("panther-identity-approved.tsv")
    _approve(local_sources["review"], approved)

    _prepare_panther_identity_fixture(local_sources, conflicting=True)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2

    error = capsys.readouterr().err
    assert "promotion record-content preflight rejected current record" in error
    assert "SOURCE_FAMILY_IDENTITY_CONFLICT" in error
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_resolver_rejects_literal_placeholder_in_primary_label(local_sources):
    record = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))
    record["label"] = "DNA-binding protein <locus_tag>"
    local_sources["record"].write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")

    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)

    assert row["qualification_status"] == "REJECTED"
    assert row["reasons"] == ["unqualifiable:record_content:unresolved_source_placeholder"]
    assert [finding["code"] for finding in row["record_content_findings"]] == [
        "UNRESOLVED_SOURCE_PLACEHOLDER"
    ]


def test_promoter_recomputes_current_record_content_findings(local_sources, capsys):
    _prepare_panther_content_gate_fixture(local_sources, template_only=False)
    assert ground.main(_resolve_args(local_sources)) == 0
    assert _resolved(local_sources)["record_content_findings"] == []
    approved = local_sources["review"].with_name("content-gate-approved.tsv")
    _approve(local_sources["review"], approved)

    # Simulate a stale resolved artifact whose structured findings predate the current
    # record.  Promotion must inspect current YAML before any registry/trait write.
    _prepare_panther_content_gate_fixture(local_sources, template_only=True, redundant_class=True)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2

    error = capsys.readouterr().err
    assert "promotion record-content preflight rejected current record" in error
    assert "DEFINITION_TEMPLATE_ONLY" in error
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_flattened_multi_location_interpro_match_is_not_qualified(local_sources):
    candidate = {
        **local_sources["candidate"],
        "intervals": [{"start": 2, "end": 3}, {"start": 6, "end": 7}],
    }
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[2, 3], [6, 7]]}},
    )
    _jsonl(local_sources["queue"], [candidate])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert "ambiguous:ungrouped_interpro_locations" in row["reasons"]
    with local_sources["review"].open(encoding="utf-8", newline="") as handle:
        review = next(csv.DictReader(handle, delimiter="\t"))
    assert "MULTI_INTERVAL_OR_HIT" in review["review_flags"]


@pytest.mark.parametrize(
    "mutation,reason",
    [
        ({"protein_id": None}, "missing_or_invalid:protein_id"),
        ({"intervals": [{"start": 3, "end": 5}]}, "mismatch:interpro_intervals"),
        ({"evidence_tier": "D"}, "unqualifiable:evidence_tier:D"),
        ({"sequence_sha256": "0" * 64}, "mismatch:sequence_sha256"),
        ({"record_path": "../outside.yaml"}, "invalid:record_path_outside_traits"),
    ],
)
def test_incomplete_or_mismatched_candidates_are_explicitly_rejected(
    local_sources, mutation, reason
):
    _jsonl(local_sources["queue"], [{**local_sources["candidate"], **mutation}])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert any(item.startswith(reason) for item in row["reasons"])
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]


def test_resolve_fills_missing_candidate_metadata_from_local_providers(local_sources):
    minimal = {
        key: local_sources["candidate"][key]
        for key in (
            "batch",
            "trait_id",
            "record_path",
            "protein_id",
            "source_trait_id",
            "mapping_method",
            "evidence_source",
            "source_release",
        )
    }
    _jsonl(local_sources["queue"], [minimal])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["sequence_sha256"] == local_sources["candidate"]["sequence_sha256"]
    assert row["intervals"] == [{"end": 5, "start": 2}]


def test_unstamped_profile_metadata_cannot_borrow_the_sequence_sidecars_release(local_sources):
    args = _resolve_args(local_sources)
    index = args.index("--protein-registry")
    del args[index : index + 2]
    assert ground.main(args) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert "missing:versioned_metadata_provider" in row["reasons"]
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]


def test_producer_blocker_is_preserved_and_prevents_qualification(local_sources):
    candidate = {
        **local_sources["candidate"],
        "reasons": ["UNGROUPED_INTERPRO_LOCATIONS"],
    }
    _jsonl(local_sources["queue"], [candidate])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert "producer:UNGROUPED_INTERPRO_LOCATIONS" in row["reasons"]


def test_resolve_qualifies_grouped_multi_fragment_interpro_location(local_sources):
    intervals = [{"start": 2, "end": 3}, {"start": 7, "end": 8}]
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[2, 3], [7, 8]]}},
    )
    _sidecar(
        local_sources["interpro_grouped"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[[2, 3], [7, 8]]]}},
    )
    candidate = {
        **local_sources["candidate"],
        "intervals": intervals,
        "interpro_location_id": ground.derive_interpro_location_id(
            "UniProtKB:P12345",
            "Pfam:PF00001",
            intervals,
        ),
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    _jsonl(local_sources["queue"], [candidate])

    assert ground.main(_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["reasons"] == []
    assert row["intervals"] == intervals
    assert "interpro_location_id" not in row["trait_occurrence"]
    assert row["grounding_evidence"]["interpro_location_id"] == candidate["interpro_location_id"]
    assert row["grounding_evidence"]["provider_entry_sha256"] == next(
        evidence["entry_sha256"]
        for evidence in row["provider_evidence"]
        if evidence["kind"] == "interpro_grouped_location"
    )
    assert {evidence["kind"] for evidence in row["provider_evidence"]} >= {
        "interpro_frame",
        "interpro_grouped_location",
    }


def test_promotion_replays_grouped_interpro_provider_evidence(local_sources):
    intervals = [{"start": 2, "end": 3}, {"start": 7, "end": 8}]
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[2, 3], [7, 8]]}},
    )
    _sidecar(
        local_sources["interpro_grouped"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[[2, 3], [7, 8]]]}},
    )
    candidate = {
        **local_sources["candidate"],
        "intervals": list(reversed(intervals)),
        "interpro_location_id": ground.derive_interpro_location_id(
            "UniProtKB:P12345",
            "Pfam:PF00001",
            intervals,
        ),
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    _jsonl(local_sources["queue"], [candidate])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    replay_args = SimpleNamespace(
        residue_frame=local_sources["residue"],
        interpro_frame=local_sources["interpro"],
        interpro_grouped_frame=local_sources["interpro_grouped"],
        profiles=local_sources["profiles"],
        protein_registry=local_sources["registry"],
        membership_registry=local_sources["membership"],
        sifts_registry=local_sources["sifts"],
    )

    cache = ground._provider_cache([row], replay_args)
    assert ground._verify_provider_evidence(row, replay_args, cache) == []

    _sidecar(
        local_sources["interpro_grouped"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[[2, 3]]]}},
    )
    stale_cache = ground._provider_cache([row], replay_args)
    assert "stale:provider_entry_missing:interpro_grouped_location" in (
        ground._verify_provider_evidence(row, replay_args, stale_cache)
    )

    _sidecar(
        local_sources["interpro_grouped"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[[2, 3], [7, 8]]]}},
    )
    approved = local_sources["review"].with_name("grouped-interpro-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert _jsonl_rows(local_sources["durable_bindings"])[0]["candidate_id"] == candidate[
        "candidate_id"
    ]


def test_resolve_rejects_stale_grouped_interpro_location_id(local_sources):
    intervals = [{"start": 2, "end": 3}, {"start": 7, "end": 8}]
    _sidecar(
        local_sources["interpro"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[2, 3], [7, 8]]}},
    )
    _sidecar(
        local_sources["interpro_grouped"],
        "InterPro",
        "109.0",
        {"P12345": {"Pfam:PF00001": [[[2, 3], [7, 8]]]}},
    )
    candidate = {
        **local_sources["candidate"],
        "intervals": intervals,
        "interpro_location_id": ground.derive_interpro_location_id(
            "UniProtKB:P12345",
            "Pfam:PF00001",
            [{"start": 2, "end": 3}],
        ),
    }
    candidate["candidate_id"] = ground.derive_candidate_id(candidate)
    _jsonl(local_sources["queue"], [candidate])

    assert ground.main(_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert "missing:exact_interpro_grouped_location" in row["reasons"]


def test_resolve_preserves_an_incomplete_producers_stable_candidate_key(local_sources):
    producer_id = "producer-search-row-17"
    candidate = {**local_sources["candidate"], "candidate_id": producer_id}
    candidate.pop("sequence_sha256")
    candidate.pop("sequence_release")
    candidate.pop("intervals")
    _jsonl(local_sources["queue"], [candidate])
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["candidate_id"] == producer_id
    assert row["resolution_digest"]


def test_resolve_qualifies_only_an_exact_release_pinned_uniprot_membership(local_sources):
    candidate, membership = _prepare_membership_candidate(local_sources)

    assert ground.main(_membership_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["candidate_id"] == ground.derive_candidate_id(row)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["reasons"] == []
    assert row["mapping_method"] == "SOURCE_MEMBERSHIP"
    assert row["source_release"] == membership["uniprot_release"]
    occurrence = row["trait_occurrence"]
    assert occurrence["scope"] == "WHOLE_PROTEIN"
    assert occurrence["source_trait_id"] == row["trait_id"]
    assert occurrence["mapping_method"] == "SOURCE_MEMBERSHIP"
    assert occurrence["evidence_source"] == "UniProtKB"
    assert occurrence["source_release"] == membership["uniprot_release"]
    assert "coordinate_frame" not in occurrence
    assert "intervals" not in occurrence
    assert "residue_positions" not in occurrence
    evidence = row["grounding_evidence"]
    assert evidence["provider_kind"] == "UNIPROT"
    assert evidence["provider_source"] == str(local_sources["durable_membership"].resolve())
    assert evidence["provider_release"] == membership["uniprot_release"]
    assert evidence["provider_entry_sha256"] == membership_snapshot.membership_entry_sha256(
        membership
    )
    provider_membership = next(
        item for item in row["provider_evidence"] if item["kind"] == "uniprot_membership"
    )
    assert provider_membership["key"] == membership["membership_id"]
    assert provider_membership["entry_sha256"] == membership_snapshot.membership_entry_sha256(
        membership
    )
    # Discovery fields are deliberately hostile: qualification came from the exact
    # snapshot, not from the query or producer classification strings.
    assert row["query"] == candidate["query"]
    assert row["family_classifications"] == candidate["family_classifications"]


def test_exact_membership_release_supersedes_stale_discovery_release(local_sources):
    candidate, _ = _prepare_membership_candidate(local_sources)
    reference = json.loads(local_sources["source_registry"].read_text(encoding="utf-8"))
    reference["uniprot_release"] = "2026_03"
    _jsonl(local_sources["source_registry"], [reference])
    membership = _membership_row(local_sources, release="2026_03")
    _write_memberships(local_sources["membership"], [membership])
    assert candidate["source_release"] == "2026_02"

    assert ground.main(_membership_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "QUALIFIED"
    assert row["uniprot_release"] == "2026_03"
    assert row["source_release"] == "2026_03"
    assert row["trait_occurrence"]["source_release"] == "2026_03"
    assert row["grounding_evidence"]["provider_release"] == "2026_03"


@pytest.mark.parametrize(
    "snapshot_rows,candidate_mutation,reason",
    [
        ([], {}, "missing:exact_uniprot_membership"),
        ("wrong-release", {}, "missing:exact_uniprot_membership"),
        ("wrong-sha", {}, "missing:exact_uniprot_membership"),
        (
            "exact",
            {"intervals": [{"start": 1, "end": 9}]},
            "invalid:membership_coordinates",
        ),
    ],
)
def test_membership_resolution_fails_closed_without_an_exact_coordinate_free_fact(
    local_sources, snapshot_rows, candidate_mutation, reason
):
    candidate, membership = _prepare_membership_candidate(local_sources)
    if snapshot_rows == "wrong-release":
        rows = [_membership_row(local_sources, release="2026_03")]
    elif snapshot_rows == "wrong-sha":
        rows = [_membership_row(local_sources, sequence_sha256="0" * 64)]
    elif snapshot_rows == "exact":
        rows = [membership]
    else:
        rows = snapshot_rows
    _write_memberships(local_sources["membership"], rows)
    _jsonl(local_sources["queue"], [{**candidate, **candidate_mutation}])

    assert ground.main(_membership_resolve_args(local_sources)) == 0

    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"
    assert reason in row["reasons"]
    assert local_sources["record"].read_text(encoding="utf-8") == _record(
        "PANTHER:PTHR12345", axis="FUNCTION"
    )


def test_membership_provider_rejects_a_malformed_snapshot_before_resolution(local_sources):
    _prepare_membership_candidate(local_sources)
    local_sources["membership"].write_text("{not-json}\n", encoding="utf-8")

    assert ground.main(_membership_resolve_args(local_sources)) == 2
    assert not local_sources["resolved"].exists()


def test_promote_review_minimum_is_capped_by_available_unique_trait_records(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("small-source-approved.tsv")
    _approve(local_sources["review"], approved)
    args = _promote_args(local_sources, approved)
    args[args.index("--min-source-reviews") + 1] = "25"

    assert ground.main(args) == 0
    assert "review coverage: Pfam=1/1" in capsys.readouterr().out


def test_promote_installs_multiple_approved_alternatives_for_one_trait_record(
    local_sources, monkeypatch
):
    _add_second_interpro_candidate(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    rows = _jsonl_rows(local_sources["resolved"])
    assert len(rows) == 2
    approved = local_sources["review"].with_name("multiple-approved-alternatives.tsv")
    _write_decisions(approved, [(row, "APPROVED") for row in rows])

    monkeypatch.setattr(ground, "_strict_errors_for_text", lambda text: [])
    monkeypatch.setattr(
        ground,
        "write_validated_record",
        lambda path, text, encoding="utf-8": pathlib.Path(path).write_text(
            text, encoding=encoding
        ),
    )
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0

    record = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))
    examples = record["canonical_examples"]
    assert {example["protein_id"] for example in examples} == {
        "UniProtKB:P12345",
        "UniProtKB:Q67890",
    }
    assert all(example["qualification_status"] == "QUALIFIED" for example in examples)
    assert {example["taxon_id"] for example in examples} == {
        "NCBITaxon:83333",
        "NCBITaxon:9606",
    }
    durable_evidence = [
        json.loads(line) for line in local_sources["durable_evidence"].read_text().splitlines()
    ]
    assert {row["protein_id"] for row in durable_evidence} == {
        "UniProtKB:P12345",
        "UniProtKB:Q67890",
    }


@pytest.mark.parametrize("undecided", [None, "", "SKIP"])
def test_promote_requires_explicit_decisions_for_every_approved_record_alternative(
    local_sources, capsys, undecided
):
    assert ground.main(_resolve_args(local_sources)) == 0
    first = _resolved(local_sources)
    alternative = _alternative(first, "ug-" + "b" * 64)
    _jsonl(local_sources["resolved"], [first, alternative])
    approved = local_sources["review"].with_name(f"undecided-alternative-{undecided}.tsv")
    decisions = [(first, "APPROVED")]
    if undecided is not None:
        decisions.append((alternative, undecided))
    _write_decisions(approved, decisions)

    assert ground.main(_promote_args(local_sources, approved)) == 2
    error = capsys.readouterr().err
    assert "leaves alternatives undecided in an approved trait record" in error
    assert alternative["candidate_id"] in error
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_source_coverage_counts_only_fully_reviewed_unique_trait_records(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    first = _resolved(local_sources)
    first_alternative = _alternative(first, "ug-" + "c" * 64)
    second_path = str(local_sources["traits"] / "second-pfam.yaml")
    second = _alternative(
        first,
        "ug-" + "d" * 64,
        trait_id="Pfam:PF00002",
        record_path=second_path,
    )
    second_alternative = _alternative(
        second,
        "ug-" + "e" * 64,
        trait_id="Pfam:PF00002",
        record_path=second_path,
    )
    _jsonl(
        local_sources["resolved"],
        [first, first_alternative, second, second_alternative],
    )
    approved = local_sources["review"].with_name("unique-record-coverage.tsv")
    _write_decisions(
        approved,
        [
            (first, "APPROVED"),
            (first_alternative, "REJECTED"),
            (second, "REJECTED"),
            (second_alternative, "SKIP"),
        ],
    )
    args = _promote_args(local_sources, approved)
    args[args.index("--min-source-reviews") + 1] = "25"

    assert ground.main(args) == 2
    assert "Pfam=1/2" in capsys.readouterr().err

    _write_decisions(
        approved,
        [
            (first, "APPROVED"),
            (first_alternative, "REJECTED"),
            (second, "REJECTED"),
            (second_alternative, "REJECTED"),
        ],
    )
    assert ground.main(args) == 0
    assert "review coverage: Pfam=2/2" in capsys.readouterr().out


def test_promote_rejects_small_source_when_one_available_record_is_undecided(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("incomplete-small-source.tsv")
    _approve(local_sources["review"], approved)
    first = _resolved(local_sources)
    undecided = {
        **first,
        "candidate_id": "undecided-second-trait-record",
        "record_path": str(local_sources["traits"] / "second-pfam.yaml"),
    }
    _jsonl(local_sources["resolved"], [first, undecided])
    args = _promote_args(local_sources, approved)
    args[args.index("--min-source-reviews") + 1] = "25"

    assert ground.main(args) == 2
    assert "Pfam=1/2" in capsys.readouterr().err
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


@pytest.mark.parametrize("durable_layout", ["flat", "sharded"])
def test_promote_is_dry_run_then_validated_apply_and_idempotent(
    local_sources, monkeypatch, durable_layout
):
    if durable_layout == "sharded":
        _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("approved.tsv")
    _approve(local_sources["review"], approved)
    writes: list[pathlib.Path] = []

    def validated_write(path, text, encoding="utf-8"):
        assert encoding == "utf-8"
        # Durable references and source evidence must exist before trait mutation.
        assert local_sources["durable_registry"].is_file()
        assert _durable_exists(local_sources["durable_evidence"])
        assert _durable_exists(local_sources["durable_bindings"])
        writes.append(pathlib.Path(path))
        pathlib.Path(path).write_text(text, encoding=encoding)

    monkeypatch.setattr(ground, "_strict_errors_for_text", lambda text: [])
    monkeypatch.setattr(ground, "write_validated_record", validated_write)
    assert ground.main(_promote_args(local_sources, approved)) == 0
    assert writes == []
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()
    assert not local_sources["durable_membership"].exists()
    assert not local_sources["durable_bindings"].exists()
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert writes == [local_sources["record"]]
    durable_reference = json.loads(local_sources["durable_registry"].read_text())
    durable_evidence = json.loads(_durable_bytes(local_sources["durable_evidence"]))
    assert durable_reference == json.loads(local_sources["registry"].read_text())
    assert durable_evidence == json.loads(local_sources["evidence"].read_text())
    if durable_layout == "sharded":
        # One evidence row: one shard plus the manifest, whose logical digest is the
        # sha256 the flat file would have had.
        evidence_dir = local_sources["durable_evidence"]
        [shard] = sorted(evidence_dir.glob("[0-9a-f][0-9a-f].jsonl"))
        assert shard.name == layout.shard_name(durable_evidence["evidence_id"])
        assert sorted(entry.name for entry in evidence_dir.iterdir()) == [
            shard.name,
            layout.MANIFEST_NAME,
        ]
        manifest = json.loads((evidence_dir / layout.MANIFEST_NAME).read_text())
        assert manifest["logical_sha256"] == hashlib.sha256(shard.read_bytes()).hexdigest()
        assert ground._artifact_digest(evidence_dir) == manifest["logical_sha256"]
    durable_bytes = (
        local_sources["durable_registry"].read_bytes(),
        _artifact_image(local_sources["durable_evidence"]),
        _artifact_image(local_sources["durable_bindings"]),
    )
    record = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))
    example = record["canonical_examples"][0]
    assert example["source"] == "UNIPROT_GROUNDING"
    assert example["qualification_status"] == "QUALIFIED"
    assert example["trait_occurrences"][0]["qualification_status"] == "QUALIFIED"
    assert "sequence" not in example  # normalized once in protein_registry.jsonl
    # The original record digest is now stale, but an exact installed occurrence is a
    # successful idempotent no-op rather than an attempted overwrite.
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert writes == [local_sources["record"]]
    assert (
        local_sources["durable_registry"].read_bytes(),
        _artifact_image(local_sources["durable_evidence"]),
        _artifact_image(local_sources["durable_bindings"]),
    ) == durable_bytes
    assert not local_sources["durable_membership"].exists()


def test_membership_promotion_installs_only_reviewed_fact_and_is_idempotent(
    local_sources, monkeypatch
):
    _, membership = _prepare_membership_candidate(local_sources)
    assert ground.main(_membership_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("membership-approved.tsv")
    _approve(local_sources["review"], approved)
    writes: list[pathlib.Path] = []

    def validated_write(path, text, encoding="utf-8"):
        assert local_sources["durable_membership"].is_file()
        assert local_sources["durable_registry"].is_file()
        assert local_sources["durable_evidence"].is_file()
        assert local_sources["durable_bindings"].is_file()
        writes.append(pathlib.Path(path))
        pathlib.Path(path).write_text(text, encoding=encoding)

    monkeypatch.setattr(ground, "_strict_errors_for_text", lambda text: [])
    monkeypatch.setattr(ground, "write_validated_record", validated_write)

    assert ground.main(_promote_args(local_sources, approved)) == 0
    assert writes == []
    assert not local_sources["durable_membership"].exists()
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert writes == [local_sources["record"]]
    assert _jsonl_rows(local_sources["durable_membership"]) == [membership]
    durable_bytes = {
        key: local_sources[key].read_bytes()
        for key in (
            "durable_membership",
            "durable_registry",
            "durable_evidence",
            "durable_bindings",
        )
    }

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert writes == [local_sources["record"]]
    assert all(local_sources[key].read_bytes() == value for key, value in durable_bytes.items())


def test_membership_promotion_rejects_durable_fact_conflict_without_any_write(
    local_sources, monkeypatch
):
    _prepare_membership_candidate(local_sources)
    assert ground.main(_membership_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("membership-conflict-approved.tsv")
    _approve(local_sources["review"], approved)
    conflicting = _membership_row(local_sources, property_value="different-provider-fact")
    _write_memberships(local_sources["durable_membership"], [conflicting])
    before_membership = local_sources["durable_membership"].read_bytes()
    before_record = local_sources["record"].read_bytes()
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert writes == []
    assert local_sources["durable_membership"].read_bytes() == before_membership
    assert local_sources["record"].read_bytes() == before_record
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_promote_merges_existing_durable_rows_but_not_unapproved_staging_rows(
    local_sources, monkeypatch
):
    assert ground.main(_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    selected_evidence = json.loads(local_sources["evidence"].read_text(encoding="utf-8"))
    unapproved_reference, unapproved_evidence = _unrelated_registry_rows(
        local_sources, "UniProtKB:O12345"
    )
    approved = local_sources["review"].with_name("merge-approved.tsv")
    _approve(local_sources["review"], approved)
    monkeypatch.setattr(ground, "_strict_errors_for_text", lambda text: [])
    monkeypatch.setattr(
        ground,
        "write_validated_record",
        lambda path, text, encoding="utf-8": pathlib.Path(path).write_text(text, encoding=encoding),
    )

    # Establish a fully receipted durable row through the only supported writer, then
    # contaminate staging with an unrelated unapproved row.  Re-promotion must retain
    # the durable row and must not copy the staging-only row into any durable artifact.
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    _jsonl(local_sources["registry"], [unapproved_reference, selected_reference])
    _jsonl(local_sources["evidence"], [unapproved_evidence, selected_evidence])
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    durable_references = {
        row["protein_id"]: row for row in _jsonl_rows(local_sources["durable_registry"])
    }
    durable_evidence = {
        row["evidence_id"]: row for row in _jsonl_rows(local_sources["durable_evidence"])
    }
    assert set(durable_references) == {"UniProtKB:P12345"}
    assert unapproved_reference["protein_id"] not in durable_references
    assert set(durable_evidence) == {selected_evidence["evidence_id"]}
    assert unapproved_evidence["evidence_id"] not in durable_evidence
    assert list(durable_references) == sorted(durable_references)
    assert list(durable_evidence) == sorted(durable_evidence)


def test_promote_reuses_same_sequence_durable_protein_from_older_uniprot_release(
    local_sources, monkeypatch
):
    selected_source_reference = json.loads(
        local_sources["source_registry"].read_text(encoding="utf-8")
    )
    selected_source_reference["uniprot_release"] = "2026_03"
    _jsonl(local_sources["source_registry"], [selected_source_reference])
    candidate = {**local_sources["candidate"], "sequence_release": "2026_03"}
    _jsonl(local_sources["queue"], [candidate])
    assert ground.main(_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    row = _resolved(local_sources)
    assert row["uniprot_release"] == "2026_03"
    existing_reference = {**selected_reference, "uniprot_release": "2026_02"}
    local_sources["durable_registry"].parent.mkdir()
    _jsonl(local_sources["durable_registry"], [existing_reference])
    approved = local_sources["review"].with_name("same-sequence-older-release.tsv")
    _write_decisions(approved, [(row, "APPROVED")])
    writes: list[pathlib.Path] = []

    def validated_write(path, text, encoding="utf-8"):
        assert encoding == "utf-8"
        writes.append(pathlib.Path(path))
        pathlib.Path(path).write_text(text, encoding=encoding)

    monkeypatch.setattr(ground, "write_validated_record", validated_write)

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0

    assert writes == [local_sources["record"]]
    record = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))
    assert record["canonical_examples"][0]["uniprot_release"] == "2026_02"
    assert _jsonl_rows(local_sources["durable_registry"]) == [existing_reference]
    assert len(_jsonl_rows(local_sources["durable_evidence"])) == 1
    bindings = _jsonl_rows(local_sources["durable_bindings"])
    assert bindings[0]["candidate_id"] == ground.derive_candidate_id(
        {**row, "uniprot_release": "2026_02"}
    )

    assert ground.main(_promote_args(local_sources, approved)) == 0


def test_promote_rejects_membership_with_durable_protein_from_different_uniprot_release(
    local_sources,
):
    _prepare_membership_candidate(local_sources)
    assert ground.main(_membership_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    local_sources["durable_registry"].parent.mkdir()
    _jsonl(
        local_sources["durable_registry"],
        [{**selected_reference, "uniprot_release": "2026_01"}],
    )
    approved = local_sources["review"].with_name("membership-release-conflict.tsv")
    _approve(local_sources["review"], approved)

    assert ground.main(_promote_args(local_sources, approved)) == 2

    assert local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_effective_selected_rows_reject_source_membership_release_remap():
    selected_reference = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Fixture protein",
        "reviewed": True,
        "sequence": "ACDEFGHIK",
        "sequence_length": 9,
        "sequence_sha256": hashlib.sha256(b"ACDEFGHIK").hexdigest(),
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "uniprot_release": "2026_03",
    }
    durable_reference = {**selected_reference, "uniprot_release": "2026_02"}

    with pytest.raises(ground.GroundingError, match="SOURCE_MEMBERSHIP"):
        ground._selected_rows_for_merged_protein_references(
            [
                {
                    "candidate_id": "ug-source-membership",
                    "mapping_method": "SOURCE_MEMBERSHIP",
                    "protein_id": selected_reference["protein_id"],
                    "uniprot_release": selected_reference["uniprot_release"],
                }
            ],
            {selected_reference["protein_id"]: selected_reference},
            {durable_reference["protein_id"]: durable_reference},
        )


@pytest.mark.parametrize("registry_kind", ["protein", "evidence"])
def test_promote_rejects_durable_registry_conflicts_without_changing_any_artifact(
    local_sources, monkeypatch, registry_kind
):
    assert ground.main(_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    selected_evidence = json.loads(local_sources["evidence"].read_text(encoding="utf-8"))
    local_sources["durable_registry"].parent.mkdir()
    _jsonl(local_sources["durable_registry"], [selected_reference])
    _jsonl(local_sources["durable_evidence"], [selected_evidence])
    if registry_kind == "protein":
        conflict = {**selected_reference, "protein_label": "Conflicting reviewed label"}
        _jsonl(local_sources["durable_registry"], [conflict])
    else:
        # A differing row under an existing content address is invalid and cannot be
        # silently replaced, even if the selected staging row itself is valid.
        conflict = {**selected_evidence, "provider_source": "Conflicting source"}
        _jsonl(local_sources["durable_evidence"], [conflict])
    before = {
        path: local_sources[path].read_bytes()
        for path in ("record", "durable_registry", "durable_evidence")
    }
    approved = local_sources["review"].with_name(f"conflict-{registry_kind}.tsv")
    _approve(local_sources["review"], approved)
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert writes == []
    assert all(local_sources[path].read_bytes() == content for path, content in before.items())


def test_promote_rejects_broken_merged_registry_links_in_memory(local_sources, monkeypatch):
    assert ground.main(_resolve_args(local_sources)) == 0
    selected_reference = json.loads(local_sources["registry"].read_text(encoding="utf-8"))
    _, orphan_evidence = _unrelated_registry_rows(local_sources, "UniProtKB:Q54321")
    local_sources["durable_registry"].parent.mkdir()
    _jsonl(local_sources["durable_registry"], [selected_reference])
    _jsonl(local_sources["durable_evidence"], [orphan_evidence])
    before = {
        path: local_sources[path].read_bytes()
        for path in ("record", "durable_registry", "durable_evidence")
    }
    approved = local_sources["review"].with_name("orphan-evidence.tsv")
    _approve(local_sources["review"], approved)
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert writes == []
    assert all(local_sources[path].read_bytes() == content for path, content in before.items())


def test_promoted_fixture_passes_closed_schema_and_semantic_validation(local_sources):
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    text = local_sources["record"].read_text(encoding="utf-8")
    record, changed = ground._install_example(yaml.safe_load(text), row)
    assert changed
    candidate_text = ground._replace_examples_block(text, record)
    assert ground._strict_errors_for_text(candidate_text) == []
    registry = ground._semantic_registry(local_sources["registry"])
    evidence = ground._semantic_evidence_registry(local_sources["evidence"])
    assert (
        ground._semantic_errors_for_record(
            record,
            registry,
            local_sources["record"],
            evidence_registry=evidence,
            hierarchy_index={"Pfam:PF00001": frozenset()},
        )
        == []
    )


@pytest.mark.parametrize("tamper", ["approval", "provider", "qualification"])
def test_promotion_rejects_stale_or_unqualified_rows_before_any_write(
    local_sources, monkeypatch, tamper
):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("approved.tsv")
    _approve(local_sources["review"], approved)
    if tamper == "approval":
        text = approved.read_text(encoding="utf-8")
        approved.write_text(text.replace(_resolved(local_sources)["resolution_digest"], "0" * 64))
    elif tamper == "provider":
        _sidecar(
            local_sources["interpro"],
            "InterPro",
            "110.0",
            {"P12345": {"Pfam:PF00001": [[2, 5]]}},
        )
    else:
        row = _resolved(local_sources)
        row["qualification_status"] = "REJECTED"
        row["reasons"] = ["manual rejection"]
        row["resolution_digest"] = ground._resolution_digest(row)
        _jsonl(local_sources["resolved"], [row])
        _approve(local_sources["review"], approved)
        # Bind approval to the tampered row to show status itself is independently gated.
        with approved.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
            fields = list(rows[0])
        rows[0]["resolution_digest"] = row["resolution_digest"]
        with approved.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    writes = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert writes == []
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_sfld_promotion_rejects_tampered_machine_qualified_row(local_sources, monkeypatch, capsys):
    _prepare_sfld_candidate(local_sources)
    record_before = local_sources["record"].read_bytes()
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"

    # Simulate a legacy or tampered ledger whose mutable machine-decision fields and
    # approval digest have all been made internally consistent.
    row["qualification_status"] = "QUALIFIED"
    row["candidate_status"] = "QUALIFIED"
    row["reasons"] = []
    row["resolution_digest"] = ground._resolution_digest(row)
    _jsonl(local_sources["resolved"], [row])
    approved = local_sources["review"].with_name("sfld-tampered-approved.tsv")
    _write_decisions(approved, [(row, "APPROVED")])
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    error = capsys.readouterr().err
    assert "SFLD promotion is disabled" in error
    assert "source-model repair" in error
    assert writes == []
    assert local_sources["record"].read_bytes() == record_before
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_prints_promotion_rejects_tampered_machine_qualified_row(
    local_sources, monkeypatch, capsys
):
    _prepare_prints_candidate(local_sources)
    record_before = local_sources["record"].read_bytes()
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    assert row["qualification_status"] == "REJECTED"

    # Simulate a legacy or tampered ledger whose mutable machine-decision fields and
    # approval digest have all been made internally consistent.  Remove the redundant
    # namespace claim so the promoter must independently recognize the PRINTS CURIE.
    row.pop("source_namespace", None)
    row["qualification_status"] = "QUALIFIED"
    row["candidate_status"] = "QUALIFIED"
    row["reasons"] = []
    row["resolution_digest"] = ground._resolution_digest(row)
    _jsonl(local_sources["resolved"], [row])
    approved = local_sources["review"].with_name("prints-tampered-approved.tsv")
    _write_decisions(approved, [(row, "APPROVED")])
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    error = capsys.readouterr().err
    assert "PRINTS promotion is disabled" in error
    assert "ordered fingerprint count/length replay" in error
    assert writes == []
    assert local_sources["record"].read_bytes() == record_before
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()


def test_semantic_preflight_rejects_in_bounds_shape_with_out_of_bounds_claim(
    local_sources, monkeypatch
):
    """Positive integers pass LinkML shape, but residue 99 is false for a 9-aa protein."""
    assert ground.main(_resolve_args(local_sources)) == 0
    row = _resolved(local_sources)
    row["trait_occurrence"]["intervals"][0]["end"] = 99
    row["resolution_digest"] = ground._resolution_digest(row)
    _jsonl(local_sources["resolved"], [row])
    approved = local_sources["review"].with_name("semantic-approved.tsv")
    with approved.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "candidate_id",
                "resolution_digest",
                "decision",
                "reviewer",
                "reviewed_at",
                "review_notes",
            ),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "candidate_id": row["candidate_id"],
                "resolution_digest": row["resolution_digest"],
                "decision": "APPROVED",
                "reviewer": "Test Curator",
                "reviewed_at": "2026-08-23",
                "review_notes": "Verified fixture evidence.",
            }
        )
    writes = []
    monkeypatch.setattr(ground, "_strict_errors_for_text", lambda text: [])
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert writes == []
    assert local_sources["record"].read_text(encoding="utf-8") == local_sources["original"]


def test_promotion_requires_explicit_approval_and_caps_batch(local_sources):
    assert ground.main(_resolve_args(local_sources)) == 0
    missing = local_sources["review"].with_name("missing.tsv")
    assert ground.main(_promote_args(local_sources, missing, apply=True)) == 2
    base = _resolved(local_sources)
    rows = []
    approvals = []
    for number in range(ground.MAX_PROMOTION_BATCH + 1):
        row = {**base, "candidate_id": f"ug-{number:064x}"}
        rows.append(row)
        approvals.append(
            {
                "candidate_id": row["candidate_id"],
                "resolution_digest": row["resolution_digest"],
                "decision": "APPROVED",
                "reviewer": "Test Curator",
                "reviewed_at": "2026-08-23",
                "review_notes": "Verified fixture evidence.",
            }
        )
    _jsonl(local_sources["resolved"], rows)
    approved = local_sources["review"].with_name("too-many.tsv")
    with approved.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "candidate_id",
                "resolution_digest",
                "decision",
                "reviewer",
                "reviewed_at",
                "review_notes",
            ),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(approvals)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2


def test_promoter_refuses_unreceipted_durable_evidence_before_any_write(
    local_sources, monkeypatch, capsys
):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("missing-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    local_sources["durable_registry"].parent.mkdir()
    local_sources["durable_registry"].write_bytes(local_sources["registry"].read_bytes())
    local_sources["durable_evidence"].write_bytes(local_sources["evidence"].read_bytes())
    before = {
        key: local_sources[key].read_bytes()
        for key in ("record", "durable_registry", "durable_evidence")
    }
    writes: list[tuple] = []
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert "binding registry is missing" in capsys.readouterr().err
    assert writes == []
    assert not local_sources["durable_bindings"].exists()
    assert all(local_sources[key].read_bytes() == value for key, value in before.items())


def test_promoter_refuses_duplicate_durable_receipts_without_any_write(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("duplicate-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    receipt = _jsonl_rows(local_sources["durable_bindings"])[0]
    _jsonl(local_sources["durable_bindings"], [receipt, receipt])
    before = {
        key: local_sources[key].read_bytes()
        for key in ("record", "durable_registry", "durable_evidence", "durable_bindings")
    }

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert "duplicate qualified-record binding" in capsys.readouterr().err
    assert all(local_sources[key].read_bytes() == value for key, value in before.items())


def test_promoter_refuses_tampered_durable_receipt_digest_without_any_write(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("tampered-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    receipt = _jsonl_rows(local_sources["durable_bindings"])[0]
    receipt["content_gate_projection"]["record_identifier"] = "Pfam:PF99999"
    _jsonl(local_sources["durable_bindings"], [receipt])
    before = {
        key: local_sources[key].read_bytes()
        for key in ("record", "durable_registry", "durable_evidence", "durable_bindings")
    }

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert "tampered qualified-record content-gate digest" in capsys.readouterr().err
    assert all(local_sources[key].read_bytes() == value for key, value in before.items())


def test_promoter_refuses_stale_durable_record_receipt_without_any_write(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("stale-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    local_sources["record"].write_text(
        local_sources["record"].read_text(encoding="utf-8") + "# curator edit\n",
        encoding="utf-8",
    )
    before = {
        key: local_sources[key].read_bytes()
        for key in ("record", "durable_registry", "durable_evidence", "durable_bindings")
    }

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert "stale qualified-record binding record_sha256" in capsys.readouterr().err
    assert all(local_sources[key].read_bytes() == value for key, value in before.items())


def test_promoter_refuses_stale_content_gate_projection_with_valid_receipt_digest(
    local_sources, capsys
):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("stale-gate-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    receipt = _jsonl_rows(local_sources["durable_bindings"])[0]
    receipt["content_gate_projection"]["source_artifact_sha256"]["interpro_xml"] = "0" * 64
    receipt["content_gate_digest"] = ground._value_digest(receipt["content_gate_projection"])
    _jsonl(local_sources["durable_bindings"], [receipt])
    before = {
        key: local_sources[key].read_bytes()
        for key in ("record", "durable_registry", "durable_evidence", "durable_bindings")
    }

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert "content-gate receipt(s) are stale" in capsys.readouterr().err
    assert all(local_sources[key].read_bytes() == value for key, value in before.items())


@pytest.mark.parametrize(
    ("intervals", "expected_error"),
    [
        ([{"start": 1, "end": 8}], "candidate_id does not match"),
        ([{"start": 0, "end": 9}], "intervals exceed"),
    ],
)
def test_receipt_bound_whole_protein_intervals_are_identity_and_bounds_checked(
    local_sources, capsys, intervals, expected_error
):
    _prepare_panther_content_gate_fixture(local_sources, template_only=False)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("interval-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    receipt = _jsonl_rows(local_sources["durable_bindings"])[0]
    receipt["content_gate_projection"]["candidate"]["intervals"] = intervals
    receipt["content_gate_digest"] = ground._value_digest(receipt["content_gate_projection"])
    _jsonl(local_sources["durable_bindings"], [receipt])

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert expected_error in capsys.readouterr().err


def test_current_hard_debt_blocks_even_with_a_digest_valid_durable_receipt(local_sources, capsys):
    # Model the historical Batch-001 PTHR10352 debt: a durable QUALIFIED occurrence
    # whose record has subsequently become an exact PANTHER template-only definition.
    _prepare_panther_content_gate_fixture(local_sources, template_only=False)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("hard-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0

    installed_examples = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))[
        "canonical_examples"
    ]
    _prepare_panther_content_gate_fixture(local_sources, template_only=True)
    hard_record = yaml.safe_load(local_sources["record"].read_text(encoding="utf-8"))
    hard_record["canonical_examples"] = installed_examples
    hard_text = yaml.safe_dump(hard_record, sort_keys=False)
    local_sources["record"].write_text(hard_text, encoding="utf-8")
    receipt = _jsonl_rows(local_sources["durable_bindings"])[0]
    parsed_args = ground._parser().parse_args(_promote_args(local_sources, approved))
    record = yaml.safe_load(hard_text)
    candidate = receipt["content_gate_projection"]["candidate"]
    gate = ground._prepare_content_gate([record], parsed_args)
    projection, findings = ground._content_gate_projection(gate, record, candidate, parsed_args)
    assert any(finding.severity == "HARD" for finding in findings)
    receipt["record_sha256"] = hashlib.sha256(hard_text.encode("utf-8")).hexdigest()
    receipt["content_gate_projection"] = projection
    receipt["content_gate_digest"] = ground._value_digest(projection)
    _jsonl(local_sources["durable_bindings"], [receipt])
    before = {
        key: local_sources[key].read_bytes()
        for key in ("record", "durable_registry", "durable_evidence", "durable_bindings")
    }

    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    error = capsys.readouterr().err
    assert "promotion record-content preflight rejected current record" in error
    assert "DEFINITION_TEMPLATE_ONLY" in error
    assert all(local_sources[key].read_bytes() == value for key, value in before.items())


@pytest.mark.parametrize("durable_layout", ["flat", "sharded"])
def test_all_clean_durable_and_selected_receipts_replay_idempotently(
    local_sources, capsys, durable_layout
):
    if durable_layout == "sharded":
        _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("clean-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    [receipt] = [
        json.loads(line) for line in _durable_bytes(local_sources["durable_bindings"]).splitlines()
    ]
    assert (
        receipt["evidence_id"]
        == json.loads(_durable_bytes(local_sources["durable_evidence"]))["evidence_id"]
    )
    assert receipt["record_path"] == ground._display_path(local_sources["record"])
    assert (
        receipt["record_sha256"] == hashlib.sha256(local_sources["record"].read_bytes()).hexdigest()
    )
    assert receipt["content_gate_digest"] == ground._value_digest(
        receipt["content_gate_projection"]
    )

    before = {
        key: _artifact_image(local_sources[key])
        for key in ("record", "durable_registry", "durable_evidence", "durable_bindings")
    }
    assert ground.main(_promote_args(local_sources, approved)) == 0
    assert "1 qualified-record binding(s)" in capsys.readouterr().out
    assert all(_artifact_image(local_sources[key]) == value for key, value in before.items())
    # The applied replay rewrites nothing either: every artifact's digest is unchanged.
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert "WROTE 0 durable registry artifact(s)" in capsys.readouterr().out
    assert all(_artifact_image(local_sources[key]) == value for key, value in before.items())


@pytest.mark.parametrize("durable_layout", ["flat", "sharded"])
def test_promotion_transaction_rolls_back_every_artifact_after_trait_install_failure(
    local_sources, monkeypatch, capsys, durable_layout
):
    if durable_layout == "sharded":
        _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("rollback-binding-approved.tsv")
    _approve(local_sources["review"], approved)
    original = local_sources["record"].read_bytes()

    def fail_after_replace(path, text, encoding="utf-8"):
        assert local_sources["durable_registry"].is_file()
        assert _durable_exists(local_sources["durable_evidence"])
        assert _durable_exists(local_sources["durable_bindings"])
        pathlib.Path(path).write_text(text, encoding=encoding)
        raise OSError("injected trait install failure")

    monkeypatch.setattr(ground, "_strict_errors_for_text", lambda text: [])
    monkeypatch.setattr(ground, "write_validated_record", fail_after_replace)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert "failed and was rolled back" in capsys.readouterr().err
    assert local_sources["record"].read_bytes() == original
    assert not local_sources["durable_registry"].exists()
    assert not local_sources["durable_evidence"].exists()
    assert not local_sources["durable_bindings"].exists()
    assert not local_sources["durable_membership"].exists()
    # The directories the install created, sharded registries included, are gone too.
    assert not local_sources["durable_registry"].parent.exists()


@pytest.mark.parametrize(
    ("tamper", "expected"),
    [
        ("edit", "registry_manifest_mismatch"),
        ("add", "registry_manifest_mismatch"),
        ("remove", "registry_manifest_mismatch"),
        ("edit-and-reseal", "changed during promotion preflight"),
    ],
)
def test_promoter_refuses_a_shard_changed_between_preflight_and_apply(
    local_sources, monkeypatch, capsys, tamper, expected
):
    _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("stale-shard-approved.tsv")
    _approve(local_sources["review"], approved)
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    capsys.readouterr()
    bindings = local_sources["durable_bindings"]
    untouched = {
        key: _artifact_image(local_sources[key])
        for key in ("record", "durable_registry", "durable_evidence")
    }
    tampered: list[bytes | dict[str, bytes]] = []
    preflight = ground._promotion_qualified_record_preflight

    def tamper_after_preflight(*args, **kwargs):
        result = preflight(*args, **kwargs)
        [shard] = sorted(bindings.glob("[0-9a-f][0-9a-f].jsonl"))
        row = json.loads(shard.read_text(encoding="utf-8"))
        if tamper == "remove":
            shard.unlink()
        elif tamper == "add":
            # A well-formed row in its correct shard; only the manifest can catch it.
            prefix = "ff" if shard.name != "ff.jsonl" else "00"
            added = dict(row, evidence_id=f"ug-evidence:{prefix}{row['evidence_id'][14:]}")
            (bindings / f"{prefix}.jsonl").write_text(
                layout.canonical_line(added), encoding="utf-8"
            )
        else:
            edited = dict(row, candidate_id=row["candidate_id"] + "-edited")
            shard.write_text(layout.canonical_line(edited), encoding="utf-8")
            if tamper == "edit-and-reseal":
                (bindings / layout.MANIFEST_NAME).write_text(
                    layout.build_manifest_text({shard.name: shard.read_bytes()}),
                    encoding="utf-8",
                )
        tampered.append(_artifact_image(bindings))
        return result

    writes: list[tuple] = []
    monkeypatch.setattr(ground, "_promotion_qualified_record_preflight", tamper_after_preflight)
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
    assert expected in capsys.readouterr().err
    assert writes == []
    assert all(_artifact_image(local_sources[key]) == value for key, value in untouched.items())
    assert tampered == [_artifact_image(bindings)]


def _registry_row(prefix: str, value: int) -> dict:
    """A minimal row keyed into shard ``<prefix>.jsonl``; the layout reads only the key."""

    return {"evidence_id": f"ug-evidence:{prefix}{value:062x}", "value": value}


def _sharded_text(rows: list[dict]) -> str:
    ordered = sorted(rows, key=lambda row: row["evidence_id"])
    return "".join(layout.canonical_line(row) for row in ordered)


def _write_sharded(path: pathlib.Path, rows: list[dict]) -> None:
    shards = layout.split_registry_text(_sharded_text(rows))
    path.mkdir(parents=True)
    for name, data in shards.items():
        (path / name).write_bytes(data)
    (path / layout.MANIFEST_NAME).write_text(layout.build_manifest_text(shards), encoding="utf-8")


def _transaction_case(root: pathlib.Path) -> tuple[list, dict]:
    """One install exercising every kind of transaction step.

    An existing sharded registry gets a changed shard, a new shard, an emptied
    (deleted) shard, and a new manifest; a flat registry migrates to its sharded twin
    and is deleted in the same call; a verbatim JSON artifact lands in two directories
    the install creates; and one trait record is rewritten.
    """

    grounding = root / "grounding"
    existing = grounding / "occurrence_evidence.jsonl.d"
    _write_sharded(existing, [_registry_row("00", 1), _registry_row("01", 2)])
    legacy = grounding / "migrated.jsonl"
    legacy.write_text(_sharded_text([_registry_row("0a", 3)]), encoding="utf-8")
    record = root / "traits" / "record.yaml"
    record.parent.mkdir(parents=True)
    record.write_text("identifier: X\n", encoding="utf-8")
    updates = [
        (existing, _sharded_text([_registry_row("00", 9), _registry_row("02", 4)])),
        (legacy.with_name("migrated.jsonl.d"), legacy.read_text(encoding="utf-8")),
        (legacy, None),
        (root / "new" / "deeper" / "receipt.json", '{"b": 1, "a": [2]}\n'),
    ]
    return updates, {record: "identifier: X\nlabel: changed\n"}


def _plain_record_writer(path, text, encoding="utf-8"):
    pathlib.Path(path).write_text(text, encoding=encoding)


# 4 steps for the existing registry, 2 for the migrated one, the flat delete, the
# verbatim receipt, and the trait write.
TRANSACTION_STEPS = 9


def test_transaction_installs_shards_manifests_deletes_and_verbatim_files(
    tmp_path, monkeypatch
):
    updates, traits = _transaction_case(tmp_path)
    planned, verify = ground._plan_artifact_updates(updates)
    assert len(planned) + len(traits) == TRANSACTION_STEPS
    existing, existing_text = updates[0]
    migrated, migrated_text = updates[1]
    assert [path.name for path, _payload in planned][:4] == [
        "00.jsonl",
        "02.jsonl",
        "01.jsonl",
        layout.MANIFEST_NAME,
    ]
    assert [payload for path, payload in planned if path.name == "01.jsonl"] == [None]
    assert [path for path, _digest in verify] == [existing.resolve(), migrated.resolve()]
    monkeypatch.setattr(ground, "write_validated_record", _plain_record_writer)

    ground._install_promotion_transaction(updates, traits)

    assert ground._artifact_digest(existing) == ground._text_digest(existing_text)
    assert sorted(entry.name for entry in existing.iterdir()) == [
        "00.jsonl",
        "02.jsonl",
        layout.MANIFEST_NAME,
    ]
    assert layout.plan_sharded_write(existing, existing_text) == []
    assert ground._artifact_digest(migrated) == ground._text_digest(migrated_text)
    assert not updates[2][0].exists()
    receipt, receipt_text = updates[3]
    assert receipt.read_text(encoding="utf-8") == receipt_text  # verbatim, not canonical
    assert [path.read_text(encoding="utf-8") for path in traits] == list(traits.values())


@pytest.mark.parametrize("failure", [OSError, KeyboardInterrupt], ids=["oserror", "interrupt"])
@pytest.mark.parametrize("when", ["before", "after"])
@pytest.mark.parametrize("step_index", range(TRANSACTION_STEPS))
def test_transaction_restores_every_preimage_after_a_fault_at_any_step(
    tmp_path, monkeypatch, failure, when, step_index
):
    updates, traits = _transaction_case(tmp_path)
    before = _tree(tmp_path)
    calls = 0
    apply_operation = ground._apply_artifact_operation

    def step(action):
        nonlocal calls
        calls += 1
        if calls - 1 == step_index and when == "before":
            raise failure("injected transaction fault")
        action()
        if calls - 1 == step_index and when == "after":
            raise failure("injected transaction fault")

    monkeypatch.setattr(
        ground,
        "_apply_artifact_operation",
        lambda path, payload: step(lambda: apply_operation(path, payload)),
    )
    monkeypatch.setattr(
        ground,
        "write_validated_record",
        lambda path, text, encoding="utf-8": step(
            lambda: _plain_record_writer(path, text, encoding)
        ),
    )

    if failure is KeyboardInterrupt:
        with pytest.raises(KeyboardInterrupt):
            ground._install_promotion_transaction(updates, traits)
    else:
        with pytest.raises(ground.GroundingError, match="failed and was rolled back"):
            ground._install_promotion_transaction(updates, traits)
    assert calls == step_index + 1
    # Byte-identical preimages, no residue, and the created directories removed.
    assert _tree(tmp_path) == before


# Rollback of _transaction_case, in reverse install order: the trait restore is its 1st
# _atomic_bytes call, 01.jsonl (deleted by the install) its 4th.
ROLLBACK_WRITE_PATHS = {
    1: "traits/record.yaml",
    4: "grounding/occurrence_evidence.jsonl.d/01.jsonl",
}


@pytest.mark.parametrize("rollback_write", sorted(ROLLBACK_WRITE_PATHS))
@pytest.mark.parametrize("second_interrupt", ["sigint", "raised"])
def test_a_second_interrupt_during_the_rollback_cannot_leave_a_silent_torn_install(
    tmp_path, monkeypatch, second_interrupt, rollback_write
):
    """A real Ctrl-C is held until the rollback ends; any other exception from a restore
    lets the remaining restores run and is reported as an incomplete rollback (#865)."""

    updates, traits = _transaction_case(tmp_path)
    before = _tree(tmp_path)
    rolling_back = False
    rollback_writes = 0
    atomic_bytes = ground._atomic_bytes

    def interrupted_trait_write(path, text, encoding="utf-8"):
        nonlocal rolling_back
        _plain_record_writer(path, text, encoding)
        rolling_back = True
        raise KeyboardInterrupt  # the first Ctrl-C, after the last install step

    def restore(path, payload):
        nonlocal rollback_writes
        if rolling_back:
            rollback_writes += 1
            if rollback_writes == rollback_write:
                if second_interrupt == "sigint":
                    signal.raise_signal(signal.SIGINT)
                else:
                    raise KeyboardInterrupt
        atomic_bytes(path, payload)

    monkeypatch.setattr(ground, "write_validated_record", interrupted_trait_write)
    monkeypatch.setattr(ground, "_atomic_bytes", restore)
    handler = signal.getsignal(signal.SIGINT)

    if second_interrupt == "sigint":
        with pytest.raises(KeyboardInterrupt, match="the rollback completed"):
            ground._install_promotion_transaction(updates, traits)
        assert _tree(tmp_path) == before
    else:
        with pytest.raises(ground.GroundingError, match="rollback was incomplete") as caught:
            ground._install_promotion_transaction(updates, traits)
        skipped = ROLLBACK_WRITE_PATHS[rollback_write]
        assert f"{skipped}: KeyboardInterrupt" in str(caught.value)
        after = _tree(tmp_path)
        differing = {
            name
            for name in before.keys() | after.keys()
            if before.get(name, b"") != after.get(name, b"")
        }
        assert differing == {skipped}
    assert rollback_writes == 5
    assert signal.getsignal(signal.SIGINT) is handler


def test_a_rollback_off_the_main_thread_still_restores_every_preimage(tmp_path, monkeypatch):
    updates, traits = _transaction_case(tmp_path)
    before = _tree(tmp_path)
    outcome: list[BaseException] = []

    def failing_trait_write(path, text, encoding="utf-8"):
        raise OSError("injected trait failure")

    monkeypatch.setattr(ground, "write_validated_record", failing_trait_write)

    def install():
        try:
            ground._install_promotion_transaction(updates, traits)
        except BaseException as exc:
            outcome.append(exc)

    worker = threading.Thread(target=install)
    worker.start()
    worker.join(timeout=120)
    assert len(outcome) == 1 and isinstance(outcome[0], ground.GroundingError)
    assert "failed and was rolled back" in str(outcome[0])
    assert _tree(tmp_path) == before


@pytest.mark.parametrize("failure", ["mismatch", "interrupt"])
def test_post_install_verify_failure_rolls_back_before_any_trait_write(
    tmp_path, monkeypatch, failure
):
    updates, traits = _transaction_case(tmp_path)
    before = _tree(tmp_path)
    writes: list[tuple] = []

    def disagree(path):
        if failure == "interrupt":
            raise KeyboardInterrupt
        return "0" * 64

    monkeypatch.setattr(ground.layout, "sharded_digest", disagree)
    monkeypatch.setattr(
        ground, "write_validated_record", lambda *args, **kwargs: writes.append(args)
    )
    if failure == "interrupt":
        with pytest.raises(KeyboardInterrupt):
            ground._install_promotion_transaction(updates, traits)
    else:
        with pytest.raises(ground.GroundingError, match="does not verify"):
            ground._install_promotion_transaction(updates, traits)
    assert writes == []
    assert _tree(tmp_path) == before


@pytest.mark.parametrize("case", ["sharded-over-flat", "flat-over-sharded", "both-in-one-call"])
def test_transaction_refuses_to_leave_both_registry_layouts(tmp_path, case):
    flat = tmp_path / "occurrence_evidence.jsonl"
    sharded = tmp_path / "occurrence_evidence.jsonl.d"
    rows = [_registry_row("00", 1)]
    text = _sharded_text(rows)
    if case == "sharded-over-flat":
        flat.write_text(text, encoding="utf-8")
        updates = [(sharded, text)]
    elif case == "flat-over-sharded":
        _write_sharded(sharded, rows)
        updates = [(flat, text)]
    else:
        updates = [(flat, text), (sharded, text)]
    before = _tree(tmp_path)

    with pytest.raises(ground.GroundingError, match="other registry layout"):
        ground._install_promotion_transaction(updates, {})
    assert _tree(tmp_path) == before


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ('{"value": 1, "evidence_id": "ug-evidence:' + "0" * 64 + '"}\n', "not canonical"),
        (
            _sharded_text([_registry_row("01", 1)]) + _sharded_text([_registry_row("00", 1)]),
            "sorts",
        ),
        (_sharded_text([_registry_row("00", 1)]).rstrip("\n"), "final newline"),
        ('{"evidence_id":"not-a-key"}\n', "evidence_id"),
        (None, "cannot be deleted"),
    ],
    ids=["noncanonical", "unsorted", "unterminated", "bad-key", "delete"],
)
def test_transaction_refuses_a_malformed_sharded_image_before_any_write(
    tmp_path, payload, message
):
    registry = tmp_path / "grounding" / "occurrence_evidence.jsonl.d"
    other = tmp_path / "grounding" / "receipt.json"

    with pytest.raises(ground.GroundingError, match=message):
        ground._install_promotion_transaction([(other, "{}\n"), (registry, payload)], {})
    assert _tree(tmp_path) == {}


def test_flat_artifacts_are_still_written_verbatim(tmp_path):
    # Staging-style flat JSONL keeps its lenient pre-#801 handling: no key, order, or
    # canonical-form check, and the bytes land exactly as given.
    flat = tmp_path / "durable" / "occurrence_evidence.jsonl"
    receipt = tmp_path / "durable" / "receipt.json"
    flat_text = '{"z": 1, "a": 2}\n\n{"evidence_id": "free-form"}\n'
    receipt_text = '{\n  "b": 1\n}'

    ground._install_promotion_transaction([(flat, flat_text), (receipt, receipt_text)], {})
    assert flat.read_bytes() == flat_text.encode("utf-8")
    assert receipt.read_bytes() == receipt_text.encode("utf-8")


@pytest.mark.parametrize("case", ["nested-output", "input-inside", "traits-inside"])
def test_promoter_rejects_paths_inside_a_sharded_durable_output(local_sources, case):
    _shard_durable_outputs(local_sources)
    args = ground._parser().parse_args(
        _promote_args(local_sources, local_sources["traits"].parent / "approved.tsv")
    )
    evidence = args.durable_evidence_registry
    if case == "nested-output":
        args.durable_protein_registry = evidence / "protein_registry.jsonl"
        message = "must not nest"
    elif case == "input-inside":
        args.approved = evidence / "approved.tsv"
        message = "--approved must not be inside the sharded durable registry"
    else:
        args.traits = evidence / "traits"
        message = "--traits must not be inside the sharded durable registry"

    with pytest.raises(ground.GroundingError, match=message):
        ground._validate_durable_paths(args, args.traits.resolve())
    assert not evidence.exists()


@pytest.mark.parametrize(
    "attribute", ["durable_evidence_registry", "durable_qualified_record_bindings"]
)
def test_promoter_rejects_flat_evidence_or_bindings_output_under_protected_root(
    local_sources, tmp_path, monkeypatch, attribute
):
    protected = tmp_path / "protected-grounding"
    monkeypatch.setattr(ground, "PROTECTED_GROUNDING_ROOT", protected)
    args = ground._parser().parse_args(
        _promote_args(local_sources, local_sources["traits"].parent / "approved.tsv")
    )
    flat = protected / getattr(args, attribute).name
    setattr(args, attribute, flat)

    with pytest.raises(ground.GroundingError, match=r"must be a sharded \.jsonl\.d registry"):
        ground._validate_durable_paths(args, args.traits.resolve())
    setattr(args, attribute, flat.with_name(flat.name + ".d"))
    ground._validate_durable_paths(args, args.traits.resolve())
    assert not protected.exists()


@pytest.mark.parametrize(
    "attribute", ["durable_evidence_registry", "durable_qualified_record_bindings"]
)
def test_promoter_refuses_a_symlinked_sharded_durable_registry(local_sources, attribute):
    """The promoter must not write through a symlink the validator rejects (#867)."""

    _shard_durable_outputs(local_sources)
    args = ground._parser().parse_args(
        _promote_args(local_sources, local_sources["traits"].parent / "approved.tsv")
    )
    registry = getattr(args, attribute)
    target = registry.with_name("elsewhere-" + registry.name)
    target.mkdir(parents=True)
    (target / layout.MANIFEST_NAME).write_text(layout.build_manifest_text({}), encoding="utf-8")
    registry.symlink_to(target, target_is_directory=True)
    target_before = sorted((path.name, path.read_bytes()) for path in target.iterdir())

    with pytest.raises(ground.GroundingError, match="must not be a symlink"):
        ground._validate_durable_paths(args, args.traits.resolve())
    assert layout.read_registry(registry).issues[0].code == "registry_layout_conflict"
    assert sorted((path.name, path.read_bytes()) for path in target.iterdir()) == target_before


def test_absent_evidence_or_bindings_under_protected_root_is_not_a_fresh_start(
    tmp_path, monkeypatch
):
    protected = tmp_path / "grounding"
    protected.mkdir()
    monkeypatch.setattr(ground, "PROTECTED_GROUNDING_ROOT", protected)

    with pytest.raises(ground.GroundingError, match="evidence registry missing under"):
        ground._load_durable_evidence_registry(protected / "occurrence_evidence.jsonl.d")
    with pytest.raises(
        ground.GroundingError, match="qualified-record binding registry missing under"
    ):
        ground._load_durable_qualified_record_bindings(
            protected / "qualified_record_bindings.jsonl.d", {}
        )
    # Scratch fixture paths keep reading a missing registry as empty.
    scratch = tmp_path / "scratch"
    assert ground._load_durable_evidence_registry(scratch / "occurrence_evidence.jsonl.d") == (
        {},
        None,
    )
    assert ground._load_durable_qualified_record_bindings(
        scratch / "qualified_record_bindings.jsonl.d", {}
    ) == ({}, None)
    assert list(protected.iterdir()) == []
    assert not scratch.exists()


def test_legacy_flat_path_beside_its_sharded_twin_is_refused_by_the_promoter(tmp_path):
    sharded = tmp_path / "qualified_record_bindings.jsonl.d"
    _write_sharded(sharded, [])

    with pytest.raises(ground.GroundingError, match="registry migrated to"):
        ground._artifact_digest(tmp_path / "qualified_record_bindings.jsonl")
    assert ground._artifact_digest(sharded) == hashlib.sha256(b"").hexdigest()


def test_second_promote_apply_under_a_held_lock_exits_2_and_dry_runs_take_no_lock(
    local_sources, capsys
):
    _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("locked-approved.tsv")
    _approve(local_sources["review"], approved)
    durable_root = local_sources["durable_bindings"].parent
    durable_root.mkdir()
    lock_file = durable_root / layout.LOCK_NAME
    original = local_sources["record"].read_bytes()

    assert ground.main(_promote_args(local_sources, approved)) == 0
    assert not lock_file.exists()
    with layout.registry_lock(durable_root) as held:
        assert held == lock_file
        assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
        assert "registry_locked" in capsys.readouterr().err
        assert local_sources["record"].read_bytes() == original
        assert sorted(entry.name for entry in durable_root.iterdir()) == [layout.LOCK_NAME]
        # A dry run never contends for the lock.
        assert ground.main(_promote_args(local_sources, approved)) == 0
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert local_sources["record"].read_bytes() != original


def _lock_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(root.rglob(layout.LOCK_NAME)) if root.exists() else []


@pytest.mark.parametrize(
    "case",
    [
        "bindings-inside-traits",
        "bindings-inside-default-traits",
        "bindings-inside-sharded-registry",
        "bindings-inside-case-alias-of-sharded-registry",
        "protein-inside-another-sharded-registry",
    ],
)
def test_promote_apply_never_locks_inside_a_trait_tree_or_a_sharded_registry(
    local_sources, tmp_path, monkeypatch, capsys, case
):
    """Validation runs before the lock is chosen, so a refused layout leaves no lock file.

    On case-insensitive APFS ``occurrence_evidence.jsonl.D`` *is* the evidence registry,
    so a lock file created there would make every later read of it fail.
    """

    _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("protected-approved.tsv")
    _approve(local_sources["review"], approved)
    evidence = local_sources["durable_evidence"]
    _write_sharded(evidence, [])
    default_traits = tmp_path / "default-traits"
    default_traits.mkdir()
    monkeypatch.setattr(ground, "DEFAULT_TRAITS", default_traits)
    foreign = tmp_path / "other-grounding" / "occurrence_evidence.jsonl.d"
    _write_sharded(foreign, [])
    if case == "bindings-inside-traits":
        local_sources["durable_bindings"] = (
            local_sources["traits"] / "sub" / "qualified_record_bindings.jsonl.d"
        )
        (local_sources["traits"] / "sub").mkdir()
    elif case == "bindings-inside-default-traits":
        local_sources["durable_bindings"] = default_traits / "qualified_record_bindings.jsonl.d"
    elif case == "bindings-inside-sharded-registry":
        local_sources["durable_bindings"] = evidence / "qualified_record_bindings.jsonl.d"
    elif case == "bindings-inside-case-alias-of-sharded-registry":
        alias = evidence.with_name(evidence.name[: -len("d")] + "D")
        local_sources["durable_bindings"] = alias / "qualified_record_bindings.jsonl.d"
    else:
        local_sources["durable_registry"] = foreign / "protein_registry.jsonl"
    protected = [local_sources["traits"], default_traits, evidence, foreign]
    before = {root: _tree(root) for root in protected}

    for apply in (False, True):
        assert ground.main(_promote_args(local_sources, approved, apply=apply)) == 2
        assert "ERROR: durable registry output" in capsys.readouterr().err
    assert {root: _tree(root) for root in protected} == before
    for root in protected:
        assert _lock_files(root) == []


@pytest.mark.parametrize("held", ["bindings-directory", "other-outputs-directory"])
def test_promote_apply_locks_every_directory_it_writes_durable_registries_into(
    local_sources, tmp_path, capsys, held
):
    """Durable outputs split across two directories are both locked, so neither can be
    written while another writer, such as eLife promote on data/grounding, holds it."""

    _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("split-approved.tsv")
    _approve(local_sources["review"], approved)
    durable = local_sources["durable_evidence"].parent
    durable.mkdir()
    scratch = tmp_path / "scratch-bindings"
    scratch.mkdir()
    local_sources["durable_bindings"] = scratch / "qualified_record_bindings.jsonl.d"
    original = local_sources["record"].read_bytes()

    with layout.registry_lock(scratch if held == "bindings-directory" else durable):
        assert ground.main(_promote_args(local_sources, approved, apply=True)) == 2
        assert "registry_locked" in capsys.readouterr().err
        assert local_sources["record"].read_bytes() == original
        assert not local_sources["durable_evidence"].exists()
        assert not local_sources["durable_bindings"].exists()
    assert ground.main(_promote_args(local_sources, approved, apply=True)) == 0
    assert local_sources["record"].read_bytes() != original
    assert _lock_files(durable) == [durable / layout.LOCK_NAME]
    assert _lock_files(scratch) == [scratch / layout.LOCK_NAME]


@pytest.mark.parametrize("lock_file", ["read-only", "symlink"])
def test_promote_apply_handles_a_lock_file_it_cannot_write(
    local_sources, tmp_path, capsys, lock_file
):
    """A lock file left by another user still locks; one that cannot be opened is a clean
    exit 2 with registry_lock_unavailable, never a traceback."""

    if lock_file == "read-only" and hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root bypasses file modes")
    _shard_durable_outputs(local_sources)
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("lock-file-approved.tsv")
    _approve(local_sources["review"], approved)
    durable = local_sources["durable_bindings"].parent
    durable.mkdir()
    lock_path = durable / layout.LOCK_NAME
    original = local_sources["record"].read_bytes()
    if lock_file == "read-only":
        lock_path.write_text("4242\n")
        lock_path.chmod(0o444)
    else:
        target = tmp_path / "elsewhere.txt"
        target.write_text("not a lock\n")
        lock_path.symlink_to(target)
    capsys.readouterr()
    try:
        result = ground.main(_promote_args(local_sources, approved, apply=True))
    finally:
        if lock_file == "read-only":
            lock_path.chmod(0o644)
    if lock_file == "read-only":
        assert result == 0
        assert local_sources["record"].read_bytes() != original
        assert lock_path.read_text() == "4242\n"
    else:
        assert result == 2
        assert "ERROR: registry_lock_unavailable" in capsys.readouterr().err
        assert local_sources["record"].read_bytes() == original
        assert target.read_text() == "not a lock\n"
        assert sorted(entry.name for entry in durable.iterdir()) == [layout.LOCK_NAME]


def test_promoter_cli_has_distinct_staging_inputs_and_durable_output_defaults(tmp_path):
    args = ground._parser().parse_args(
        [
            "promote",
            "--resolved",
            str(tmp_path / "resolved.jsonl"),
            "--approved",
            str(tmp_path / "approved.tsv"),
        ]
    )
    assert args.protein_registry is None
    assert args.evidence_registry is None
    assert args.membership_registry is None
    assert args.sifts_registry is None
    assert args.durable_protein_registry == ground.DEFAULT_DURABLE_PROTEIN_REGISTRY
    assert args.durable_evidence_registry == ground.DEFAULT_DURABLE_EVIDENCE_REGISTRY
    assert args.durable_membership_registry == ground.DEFAULT_DURABLE_MEMBERSHIP_REGISTRY
    assert (
        args.durable_qualified_record_bindings == ground.DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS
    )
    assert args.durable_protein_registry == REPO / "data/grounding/protein_registry.jsonl"
    assert args.durable_evidence_registry == REPO / "data/grounding/occurrence_evidence.jsonl.d"
    assert args.durable_membership_registry == REPO / "data/grounding/uniprot_memberships.jsonl"
    assert (
        args.durable_qualified_record_bindings
        == REPO / "data/grounding/qualified_record_bindings.jsonl.d"
    )


@pytest.mark.parametrize(
    "attribute",
    [
        "durable_protein_registry",
        "durable_evidence_registry",
        "durable_membership_registry",
        "durable_qualified_record_bindings",
    ],
)
@pytest.mark.parametrize("protected_root_name", ["canonical-traits", "selected-traits"])
def test_promoter_rejects_every_durable_output_through_case_varied_trait_roots(
    local_sources,
    attribute,
    protected_root_name,
):
    args = ground._parser().parse_args(
        _promote_args(local_sources, local_sources["traits"].parent / "approved.tsv")
    )
    roots = {
        "canonical-traits": (
            ground.DEFAULT_TRAITS,
            ground.REPO_ROOT / "DATA" / "TRAITS",
        ),
        "selected-traits": (
            local_sources["traits"],
            local_sources["traits"].with_name(local_sources["traits"].name.swapcase()),
        ),
    }
    protected_root, case_alias = roots[protected_root_name]
    try:
        physically_aliased = case_alias.samefile(protected_root)
    except OSError:
        physically_aliased = False
    if not physically_aliased:
        pytest.skip("filesystem is case-sensitive for this trait root")
    probe = protected_root / f"_promotion_case_alias_probe_{attribute}.jsonl"
    assert not probe.exists()
    setattr(args, attribute, case_alias / probe.name)

    with pytest.raises(ground.GroundingError, match="outside trait records"):
        ground._validate_durable_paths(args, args.traits.resolve())
    assert not probe.exists()


@pytest.mark.parametrize(
    "attribute",
    [
        "durable_protein_registry",
        "durable_evidence_registry",
        "durable_membership_registry",
        "durable_qualified_record_bindings",
    ],
)
def test_promoter_rejects_existing_staging_input_case_alias(local_sources, attribute):
    local_sources["resolved"].write_text("{}\n", encoding="utf-8")
    approved = local_sources["traits"].parent / "approved.tsv"
    approved.write_text("candidate_id\n", encoding="utf-8")
    args = ground._parser().parse_args(_promote_args(local_sources, approved))
    case_alias = local_sources["resolved"].with_name(local_sources["resolved"].name.swapcase())
    try:
        physically_aliased = case_alias.samefile(local_sources["resolved"])
    except OSError:
        physically_aliased = False
    if not physically_aliased:
        pytest.skip("filesystem is case-sensitive for the staging input")
    setattr(args, attribute, case_alias)

    with pytest.raises(ground.GroundingError, match="differ from staging/review input"):
        ground._validate_durable_paths(args, args.traits.resolve())
    assert local_sources["resolved"].read_text(encoding="utf-8") == "{}\n"


@pytest.mark.parametrize(
    ("first_name", "second_name"),
    [
        ("Future-Durable.JSONL", "future-durable.jsonl"),
        (
            "caf\N{LATIN SMALL LETTER E WITH ACUTE}.jsonl",
            "cafe\N{COMBINING ACUTE ACCENT}.jsonl",
        ),
    ],
)
def test_promoter_rejects_physically_colliding_prospective_durable_outputs(
    local_sources, first_name, second_name
):
    args = ground._parser().parse_args(
        _promote_args(local_sources, local_sources["traits"].parent / "approved.tsv")
    )
    first = local_sources["traits"].parent / first_name
    second = local_sources["traits"].parent / second_name
    assert not first.exists() and not second.exists()
    args.durable_protein_registry = first
    args.durable_evidence_registry = second

    with pytest.raises(ground.GroundingError, match="paths must differ"):
        ground._validate_durable_paths(args, args.traits.resolve())
    assert not first.exists() and not second.exists()


def test_promoter_apply_rejects_case_alias_before_any_durable_or_trait_write(local_sources, capsys):
    assert ground.main(_resolve_args(local_sources)) == 0
    approved = local_sources["review"].with_name("case-alias-approved.tsv")
    _approve(local_sources["review"], approved)
    case_alias = ground.REPO_ROOT / "DATA" / "TRAITS"
    try:
        physically_aliased = case_alias.samefile(ground.DEFAULT_TRAITS)
    except OSError:
        physically_aliased = False
    if not physically_aliased:
        pytest.skip("filesystem is case-sensitive for canonical trait storage")
    probe = ground.DEFAULT_TRAITS / "_promotion_apply_no_write_probe.jsonl"
    assert not probe.exists()
    original_record = local_sources["record"].read_bytes()
    args = _promote_args(local_sources, approved, apply=True)
    args[args.index("--durable-protein-registry") + 1] = str(case_alias / probe.name)

    assert ground.main(args) == 2
    assert "outside trait records" in capsys.readouterr().err
    assert not probe.exists()
    assert local_sources["record"].read_bytes() == original_record
    assert all(
        not local_sources[key].exists()
        for key in (
            "durable_registry",
            "durable_evidence",
            "durable_membership",
            "durable_bindings",
        )
    )


def test_named_review_batch_resolver_is_receipt_bound_and_rejects_overrides():
    source = (REPO / "justfile").read_text(encoding="utf-8")
    generic_marker = "resolve-uniprot-grounding *args:\n"
    generic = source.split(generic_marker, 1)[1].split("\n\n", 1)[0]
    assert "--allow-unreceipted-inputs" in generic

    marker = "resolve-uniprot-review-batch batch_id *args:\n"
    block = source.split(marker, 1)[1].split("\n\n", 1)[0]

    for fixed_option in (
        "--queue",
        "--selector-manifest",
        "--fetch-request-plan",
        "--fetch-receipt",
        "--providers",
        "--protein-registry",
        "--membership-registry",
        "--sifts-registry",
        "--durable-membership-registry",
        "--registry-blocked",
        "--expect-uniprot-release",
        "--batch",
        "--out",
        "--review",
        "--registry-out",
        "--evidence-out",
        "--replace-staging-outputs",
    ):
        assert fixed_option in block
    assert "bounded review resolver argument is fixed by the recipe" in block
    assert "--allow-unreceipted-inputs" in block
    assert "--allow-offline-uniprot-fixture" in block
    assert "--allow-offline-sifts-fixtures" in block


def test_promoter_source_uses_the_validated_atomic_writer_only():
    source = (REPO / "scripts" / "ground_uniprot_examples.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    writers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name in {"promote", "_install_promotion_transaction"}
    ]
    calls = {
        node.func.id
        for writer in writers
        for node in ast.walk(writer)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "write_validated_record" in calls
    assert "write_record" not in calls
    assert all(".write_text(" not in ast.unparse(writer) for writer in writers)


def test_the_resolution_digest_rule_has_exactly_one_implementation():
    """Three copies of this rule existed and had to agree (#620).

    `finalize_uniprot_review_batch` and `select_uniprot_review_batch` each carried
    their own inline `hashlib.sha256(_canonical_json({... if key !=
    "resolution_digest"}))`. Adding `record_preimage` to the resolver's exclusion
    set changed one and left two behind, and the disagreement only surfaced where a
    path crossed two of them.

    Worse than an ordinary duplication, because the digest is what approvals are
    bound to: two implementations disagreeing does not produce a wrong number in a
    report, it makes reviewed work look stale and sends it back through review.
    """
    reimplementations = [
        path.name
        for path in sorted((REPO / "scripts").glob("*.py"))
        if '!= "resolution_digest"' in path.read_text(encoding="utf-8")
    ]
    assert not reimplementations, (
        "these re-derive the resolution digest instead of calling the resolver's "
        f"_resolution_digest: {reimplementations}"
    )


def test_every_caller_of_the_digest_uses_the_shared_helper():
    """The converse: the consumers must actually reach for it.

    A file could stop re-implementing the rule and simply stop checking, which is
    the quieter failure -- a gate removed rather than a gate disagreeing.
    """
    for name in ("finalize_uniprot_review_batch.py", "select_uniprot_review_batch.py"):
        text = (REPO / "scripts" / name).read_text(encoding="utf-8")
        assert "ground._resolution_digest(row)" in text, f"{name} no longer verifies the digest"
