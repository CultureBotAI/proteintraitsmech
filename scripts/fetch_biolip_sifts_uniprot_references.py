#!/usr/bin/env python3
"""Fetch release-pinned UniProt references for mapped BioLiP/SIFTS accessions.

Dry-run replays ``stage_biolip_sifts_mappings.py`` from its BioLiP source stage and
completed residue-level SIFTS snapshot, derives the exact UniProt accessions that need
``ProteinReference`` rows, and emits one canonical request plan to stdout.  It does not
touch the network or write outputs.

``--apply`` requires an exact saved ``--request-plan``.  The current BioLiP stage,
SIFTS manifest, mapping summary, request chunks, offline fixture when supplied, and
output paths must still match that saved plan before the first REST request and again
before any ignored staging output is replaced.  Successful exact responses also emit a
content-addressed BioLiP/SIFTS mapping registry row for every fetched candidate whose
mapped residue identities replay against the fetched UniProt sequence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import stage_biolip_sifts_mappings as mapper
from build_ecod_sifts_candidates import EcodSiftsError
from fetch_uniprot_registry import (
    REQUEST_HEADERS,
    RETURN_FIELDS,
    UNIPROT_SEARCH,
    NetworkClient,
    OfflineClient,
    RegistryBuildError,
    Target,
    _ACCESSION,
    _RELEASE,
    _artifact_projection,
    _capture,
    _clean,
    _canonical_json,
    _entry_reference,
    _load_json_unique,
    _output_path,
    _request_projection,
    _response_receipt_row,
    _validate_staging_output_paths,
    _value_sha256,
)
from uniprot_membership_snapshot import (
    MembershipSnapshotError,
    dump_memberships,
    extract_entry_memberships,
    merge_memberships,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "uniprot-grounding"
DEFAULT_REGISTRY = DEFAULT_OUT_DIR / "biolip-sifts-uniprot_registry.jsonl"
DEFAULT_MEMBERSHIPS = DEFAULT_OUT_DIR / "biolip-sifts-uniprot_memberships.jsonl"
DEFAULT_MAPPINGS = DEFAULT_OUT_DIR / "biolip-sifts-mappings.jsonl"
DEFAULT_BLOCKED = DEFAULT_OUT_DIR / "biolip-sifts-registry_blocked.tsv"
DEFAULT_RECEIPT = DEFAULT_OUT_DIR / "biolip-sifts-uniprot_fetch_receipt.json"

PLAN_SCHEMA_VERSION = 1
PLAN_KIND = "BIOLIP_SIFTS_UNIPROT_FETCH_REQUEST_PLAN"
PLAN_ID_PREFIX = "biolip-sifts-uniprot-fetch-plan:"
MAPPING_REGISTRY_KIND = "BIOLIP_SIFTS_MAPPING_REGISTRY_ROW"
MAPPING_REGISTRY_ID_PREFIX = "biolip-sifts:"
RECEIPT_SCHEMA_VERSION = 1
RECEIPT_KIND = "BIOLIP_SIFTS_UNIPROT_FETCH_RECEIPT"
RECEIPT_ID_PREFIX = "biolip-sifts-uniprot-fetch-receipt:"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_ACCESSION = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[1-9][0-9]*)?$"
)
_POLYMER_LIGAND_XREFS = {
    "dna": "CHEBI:16991",
    "rna": "CHEBI:33697",
    "peptide": "CHEBI:16670",
}

MAPPING_REGISTRY_FIELDS = frozenset(
    {
        "chain_id",
        "coordinate_frame",
        "expected_residues",
        "fetch_request_plan_id",
        "kind",
        "mapped_residue_count",
        "mapped_residues",
        "mapping_candidate_id",
        "mapping_candidate_row_sha256",
        "mapping_completeness",
        "mapping_id",
        "mapping_method",
        "mapping_row_sha256",
        "mapping_stage",
        "protein_id",
        "qualification_claimed",
        "record_path",
        "record_sha256",
        "residue_positions",
        "schema_version",
        "scope",
        "sequence_sha256",
        "sifts_entry_date",
        "sifts_snapshot",
        "sifts_source_url",
        "sifts_uniprot_release",
        "sifts_uniprot_version",
        "sifts_xml_sha256",
        "source_projection",
        "source_residue_count",
        "source_stage_artifact",
        "stage_status",
        "structure_id",
        "trait_id",
        "uniprot_release",
    }
)

SOURCE_PROJECTION_FIELDS = frozenset(
    {
        "binding_residue_pairs",
        "source_binding",
        "source_occurrence_id",
        "source_occurrence_row_sha256",
        "trait_binding",
    }
)

SOURCE_BINDING_FIELDS = frozenset(
    {
        "binding_residues_pdb_author_text",
        "binding_residues_receptor_sequence_text",
        "binding_site_code",
        "ligand_chain_id",
        "ligand_id",
        "ligand_serial_number_text",
        "receptor_chain_id",
        "receptor_sequence_length",
        "receptor_sequence_sha256",
        "resolution_text",
        "source_field_projection_sha256",
        "source_line_numbers",
        "source_occurrence_key",
        "source_physical_line_count",
        "source_raw_line_sha256",
        "source_raw_line_sha256_basis",
        "source_uniprot_accession_claims",
        "source_uniprot_claim_status",
        "source_uniprot_field_text",
        "structure_id",
    }
)

SOURCE_OCCURRENCE_KEY_FIELDS = frozenset(
    {
        "binding_site_code",
        "ligand_chain",
        "ligand_id",
        "ligand_serial_number",
        "pdb_id",
        "receptor_chain",
    }
)

BINDING_RESIDUE_PAIR_FIELDS = frozenset(
    {
        "author_insertion_code",
        "author_residue_number",
        "author_residue_token",
        "biolip_receptor_sequence_position",
        "ordinal",
        "receptor_sequence_residue_token",
        "source_amino_acid",
    }
)

TRAIT_BINDING_FIELDS = frozenset(
    {
        "ligand_id",
        "trait_id",
        "trait_record_has_canonical_examples",
        "trait_record_path",
        "trait_record_sha256",
        "trait_source_xref_status",
        "trait_source_xrefs",
    }
)

_BLOCKED_COLUMNS = (
    "protein_id",
    "accession",
    "candidate_count",
    "candidate_ids",
    "trait_ids",
    "reason",
    "detail",
)


@dataclass(frozen=True)
class PreparedPlan:
    plan: dict[str, Any]
    targets: tuple[Target, ...]
    mappings_by_candidate_id: Mapping[str, Mapping[str, Any]]
    offline_fixture: Any | None


def _resolved_output_paths(args: argparse.Namespace) -> dict[str, Path]:
    outputs = {
        "protein_registry": args.out,
        "membership_registry": args.membership_out or DEFAULT_MEMBERSHIPS,
        "sifts_mapping_registry": args.mapping_out or DEFAULT_MAPPINGS,
        "blocked_registry": args.blocked,
        "fetch_receipt": args.receipt or DEFAULT_RECEIPT,
    }
    _validate_staging_output_paths(outputs)
    return outputs


def _reject_input_output_collisions(
    args: argparse.Namespace, outputs: Mapping[str, Path]
) -> None:
    inputs = {
        "BioLiP source stage": args.stage,
        "SIFTS manifest": args.sifts_snapshot / "manifest.json",
    }
    if args.offline_responses is not None:
        inputs["offline response fixture"] = args.offline_responses
    input_paths = {_output_path(path): role for role, path in inputs.items()}
    for output_role, path in outputs.items():
        input_role = input_paths.get(_output_path(path))
        if input_role is not None:
            raise RegistryBuildError(
                f"{output_role} output collides with {input_role}: {path}"
            )


def _normalise_mapping_request(row: Mapping[str, Any]) -> dict[str, Any]:
    protein_id = row.get("protein_id")
    accession = row.get("accession")
    candidate_ids = row.get("mapping_candidate_ids")
    trait_ids = row.get("trait_ids")
    record_paths = row.get("record_paths")
    if row.get("kind") != mapper.REQUEST_KIND:
        raise RegistryBuildError("BioLiP/SIFTS request row has the wrong kind")
    if not isinstance(protein_id, str) or not protein_id.startswith("UniProtKB:"):
        raise RegistryBuildError("BioLiP/SIFTS request row lacks an exact protein_id")
    if (
        not isinstance(accession, str)
        or protein_id != f"UniProtKB:{accession}"
        or _ACCESSION.fullmatch(accession) is None
    ):
        raise RegistryBuildError(f"BioLiP/SIFTS request has invalid accession {accession!r}")
    if (
        not isinstance(candidate_ids, list)
        or not candidate_ids
        or any(not isinstance(value, str) or not value for value in candidate_ids)
        or candidate_ids != sorted(candidate_ids)
        or len(set(candidate_ids)) != len(candidate_ids)
    ):
        raise RegistryBuildError(f"{protein_id} lacks sorted mapping_candidate_ids")
    if row.get("mapping_candidate_count") != len(candidate_ids):
        raise RegistryBuildError(f"{protein_id} mapping_candidate_count mismatch")
    if row.get("mapping_candidate_ids_sha256") != mapper.value_sha256(candidate_ids):
        raise RegistryBuildError(f"{protein_id} mapping_candidate_ids digest mismatch")
    if (
        not isinstance(trait_ids, list)
        or not trait_ids
        or any(not isinstance(value, str) or not value for value in trait_ids)
    ):
        raise RegistryBuildError(f"{protein_id} lacks trait_ids")
    if (
        not isinstance(record_paths, list)
        or not record_paths
        or any(not isinstance(value, str) or not value for value in record_paths)
    ):
        raise RegistryBuildError(f"{protein_id} lacks record_paths")
    return dict(row)


def _targets_from_stage(
    requests: Sequence[Mapping[str, Any]], *, expected_release: str
) -> tuple[Target, ...]:
    targets: list[Target] = []
    seen_ids: set[str] = set()
    for request in sorted(requests, key=lambda row: str(row.get("protein_id", ""))):
        row = _normalise_mapping_request(request)
        request_id = row.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise RegistryBuildError("BioLiP/SIFTS request row lacks request_id")
        if request_id in seen_ids:
            raise RegistryBuildError(f"duplicate BioLiP/SIFTS request_id {request_id}")
        seen_ids.add(request_id)
        if row.get("sifts_uniprot_release") != expected_release:
            raise RegistryBuildError(
                f"{row['protein_id']} SIFTS release {row.get('sifts_uniprot_release')!r} "
                f"does not match expected UniProt release {expected_release}"
            )
        targets.append(
            Target(
                protein_id=row["protein_id"],
                accession=row["accession"],
                candidates=(row,),
                expected_length=None,  # type: ignore[arg-type]
                expected_sha256=None,  # type: ignore[arg-type]
                expected_release=expected_release,
            )
        )
    if not targets:
        raise RegistryBuildError("BioLiP/SIFTS mapping stage has no protein requests")
    return tuple(targets)


def _target_projection(target: Target) -> dict[str, Any]:
    request = target.candidates[0]
    return {
        "protein_id": target.protein_id,
        "accession": target.accession,
        "mapping_request_id": request["request_id"],
        "mapping_candidate_count": request["mapping_candidate_count"],
        "mapping_candidate_ids": request["mapping_candidate_ids"],
        "mapping_candidate_ids_sha256": request["mapping_candidate_ids_sha256"],
        "trait_ids": request["trait_ids"],
        "record_paths": request["record_paths"],
        "sifts_uniprot_release": request["sifts_uniprot_release"],
    }


def _mappings_by_candidate_id(
    mappings: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    by_id: dict[str, Mapping[str, Any]] = {}
    for mapping in mappings:
        candidate_id = mapping.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise RegistryBuildError("BioLiP/SIFTS mapping lacks candidate_id")
        previous = by_id.get(candidate_id)
        if previous is not None:
            raise RegistryBuildError(f"duplicate BioLiP/SIFTS mapping candidate {candidate_id}")
        by_id[candidate_id] = mapping
    return by_id


def mapping_entry_sha256(value: Mapping[str, Any]) -> str:
    """Digest a BioLiP/SIFTS mapping row, excluding its row-hash field."""

    return mapper.value_sha256(
        {key: value[key] for key in value if key != "mapping_row_sha256"}
    )


def _mapping_id_sha256(value: Mapping[str, Any]) -> str:
    return mapper.value_sha256(
        {
            key: value[key]
            for key in value
            if key not in {"mapping_id", "mapping_row_sha256"}
        }
    )


def _require_registry_text(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise RegistryBuildError(f"BioLiP/SIFTS mapping lacks required {field}")
    return value


def _require_sha256(row: Mapping[str, Any], field: str) -> str:
    value = _require_registry_text(row, field)
    if _SHA256.fullmatch(value) is None:
        raise RegistryBuildError(f"BioLiP/SIFTS mapping {field} is not a SHA-256 digest")
    return value


def _require_release(row: Mapping[str, Any], field: str) -> str:
    value = _require_registry_text(row, field)
    if _RELEASE.fullmatch(value) is None:
        raise RegistryBuildError(f"BioLiP/SIFTS mapping {field} is not a UniProt release")
    return value


def _require_int(
    row: Mapping[str, Any], field: str, *, positive: bool = False, context: str
) -> int:
    value = row.get(field)
    if type(value) is not int:
        raise RegistryBuildError(f"BioLiP/SIFTS {context} has invalid {field}")
    if positive and value < 1:
        raise RegistryBuildError(f"BioLiP/SIFTS {context} has invalid {field}")
    return value


def _require_mapping(
    value: Any, fields: frozenset[str], *, context: str
) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise RegistryBuildError(f"BioLiP/SIFTS {context} projection is invalid")
    return value


def _validate_binding_residue_pair(
    pair: Mapping[str, Any],
    mapped_residue: Mapping[str, Any],
    index: int,
) -> None:
    if set(pair) != BINDING_RESIDUE_PAIR_FIELDS:
        raise RegistryBuildError(f"BioLiP/SIFTS binding residue pair {index} is invalid")
    if pair.get("ordinal") != index:
        raise RegistryBuildError(f"BioLiP/SIFTS binding residue pair {index} ordinal mismatch")
    if not isinstance(pair.get("author_insertion_code"), str):
        raise RegistryBuildError(
            f"BioLiP/SIFTS binding residue pair {index} insertion code is invalid"
        )
    _require_int(pair, "author_residue_number", context=f"binding residue pair {index}")
    _require_int(
        pair,
        "biolip_receptor_sequence_position",
        positive=True,
        context=f"binding residue pair {index}",
    )
    for field in (
        "author_residue_token",
        "receptor_sequence_residue_token",
        "source_amino_acid",
    ):
        _require_registry_text(pair, field)
    if len(str(pair["source_amino_acid"])) != 1:
        raise RegistryBuildError(
            f"BioLiP/SIFTS binding residue pair {index} amino acid is invalid"
        )
    copied_fields = (
        "author_insertion_code",
        "author_residue_number",
        "source_amino_acid",
    )
    for field in copied_fields:
        if pair[field] != mapped_residue[field]:
            raise RegistryBuildError(
                f"BioLiP/SIFTS binding residue pair {index} {field} mismatch"
            )


def _parse_source_uniprot_accessions(value: str) -> tuple[str, tuple[str, ...]]:
    semantic = value.strip(" \t")
    if semantic in {"", "-"}:
        return "MISSING", ()
    accessions = tuple(item.strip(" \t") for item in semantic.split(","))
    if any(not item or _SOURCE_ACCESSION.fullmatch(item) is None for item in accessions):
        return "MALFORMED", accessions
    return ("SINGLE" if len(accessions) == 1 else "MULTIPLE"), accessions


def _validate_source_uniprot_projection(source_binding: Mapping[str, Any]) -> None:
    source_text = source_binding.get("source_uniprot_field_text")
    if not isinstance(source_text, str):
        raise RegistryBuildError("BioLiP/SIFTS source UniProt field is invalid")
    status, accessions = _parse_source_uniprot_accessions(source_text)
    if source_binding.get("source_uniprot_claim_status") != status:
        raise RegistryBuildError("BioLiP/SIFTS source UniProt claim status mismatch")
    if source_binding.get("source_uniprot_accession_claims") != list(accessions):
        raise RegistryBuildError("BioLiP/SIFTS source UniProt accession claims mismatch")


def _expected_exact_source_xrefs(ligand_id: str) -> list[str]:
    xref = _POLYMER_LIGAND_XREFS.get(ligand_id)
    return [xref if xref is not None else f"pdb.ligand:{ligand_id}"]


def _validate_mapping_residue(row: Mapping[str, Any], chain_id: str, index: int) -> int:
    if set(row) != {
        "author_insertion_code",
        "author_residue_number",
        "chain_id",
        "ordinal",
        "pdb_amino_acid",
        "pdbe_sequence_position",
        "source_amino_acid",
        "uniprot_amino_acid",
        "uniprot_position",
    }:
        raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} has invalid fields")
    if row.get("chain_id") != chain_id:
        raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} chain mismatch")
    if row.get("ordinal") != index:
        raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} ordinal mismatch")
    if not isinstance(row.get("author_insertion_code"), str):
        raise RegistryBuildError(
            f"BioLiP/SIFTS mapped residue {index} author insertion code is invalid"
        )
    _require_int(row, "author_residue_number", context=f"mapped residue {index}")
    _require_int(row, "pdbe_sequence_position", positive=True, context=f"mapped residue {index}")
    _require_int(row, "uniprot_position", positive=True, context=f"mapped residue {index}")
    for field in ("source_amino_acid", "pdb_amino_acid", "uniprot_amino_acid"):
        value = row.get(field)
        if not isinstance(value, str) or len(value) != 1:
            raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} has invalid {field}")
    if row["source_amino_acid"] != row["pdb_amino_acid"]:
        raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} PDB mismatch")
    if row["source_amino_acid"] != row["uniprot_amino_acid"]:
        raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} UniProt mismatch")
    return int(row["uniprot_position"])


def _validate_source_projection(
    row: Mapping[str, Any],
    mapped_residues: Sequence[Mapping[str, Any]],
) -> None:
    source_projection = _require_mapping(
        row.get("source_projection"),
        SOURCE_PROJECTION_FIELDS,
        context="source",
    )
    occurrence_id = _require_registry_text(source_projection, "source_occurrence_id")
    if not occurrence_id.startswith("biolip-missing-protein-source-occurrence:"):
        raise RegistryBuildError("BioLiP/SIFTS source occurrence id is invalid")
    _require_sha256(source_projection, "source_occurrence_row_sha256")

    trait_binding = _require_mapping(
        source_projection.get("trait_binding"),
        TRAIT_BINDING_FIELDS,
        context="trait binding",
    )
    if trait_binding.get("trait_id") != row["trait_id"]:
        raise RegistryBuildError("BioLiP/SIFTS trait projection mismatch")
    if trait_binding.get("trait_record_path") != row["record_path"]:
        raise RegistryBuildError("BioLiP/SIFTS record projection mismatch")
    if trait_binding.get("trait_record_sha256") != row["record_sha256"]:
        raise RegistryBuildError("BioLiP/SIFTS record digest projection mismatch")
    if trait_binding.get("trait_record_has_canonical_examples") is not False:
        raise RegistryBuildError("BioLiP/SIFTS trait binding must not have examples")

    source_binding = _require_mapping(
        source_projection.get("source_binding"),
        SOURCE_BINDING_FIELDS,
        context="source binding",
    )
    if source_binding.get("structure_id") != row["structure_id"]:
        raise RegistryBuildError("BioLiP/SIFTS structure projection mismatch")
    if source_binding.get("receptor_chain_id") != row["chain_id"]:
        raise RegistryBuildError("BioLiP/SIFTS receptor chain projection mismatch")
    _require_int(
        source_binding,
        "receptor_sequence_length",
        positive=True,
        context="source binding",
    )
    _require_int(
        source_binding,
        "source_physical_line_count",
        positive=True,
        context="source binding",
    )
    for field in (
        "binding_residues_pdb_author_text",
        "binding_residues_receptor_sequence_text",
        "binding_site_code",
        "ligand_chain_id",
        "ligand_id",
        "ligand_serial_number_text",
        "resolution_text",
        "source_raw_line_sha256_basis",
    ):
        _require_registry_text(source_binding, field)
    for field in (
        "receptor_sequence_sha256",
        "source_field_projection_sha256",
        "source_raw_line_sha256",
    ):
        _require_sha256(source_binding, field)
    if source_binding["source_raw_line_sha256_basis"] != "RAW_UTF8_PHYSICAL_LINE_INCLUDING_LF":
        raise RegistryBuildError("BioLiP/SIFTS source raw-line hash basis mismatch")
    _validate_source_uniprot_projection(source_binding)
    source_line_numbers = source_binding.get("source_line_numbers")
    if (
        not isinstance(source_line_numbers, list)
        or not source_line_numbers
        or any(type(value) is not int or value < 1 for value in source_line_numbers)
    ):
        raise RegistryBuildError("BioLiP/SIFTS source line numbers are invalid")

    key = _require_mapping(
        source_binding.get("source_occurrence_key"),
        SOURCE_OCCURRENCE_KEY_FIELDS,
        context="source occurrence key",
    )
    for field in SOURCE_OCCURRENCE_KEY_FIELDS:
        _require_registry_text(key, field)
    pdb_id = str(row["structure_id"])[4:]
    if key["pdb_id"] != pdb_id:
        raise RegistryBuildError("BioLiP/SIFTS source occurrence PDB mismatch")
    if key["receptor_chain"] != row["chain_id"]:
        raise RegistryBuildError("BioLiP/SIFTS chain projection mismatch")
    key_binding_fields = {
        "binding_site_code": "binding_site_code",
        "ligand_chain": "ligand_chain_id",
        "ligand_id": "ligand_id",
        "ligand_serial_number": "ligand_serial_number_text",
    }
    for key_field, binding_field in key_binding_fields.items():
        if key[key_field] != source_binding[binding_field]:
            raise RegistryBuildError(
                f"BioLiP/SIFTS source occurrence {key_field} mismatch"
            )
    if trait_binding.get("ligand_id") != key["ligand_id"]:
        raise RegistryBuildError("BioLiP/SIFTS ligand projection mismatch")
    expected_xrefs_by_status = {
        "EXACT_SEEDER_SOURCE_XREFS": _expected_exact_source_xrefs(key["ligand_id"])
    }
    if key["ligand_id"] == "dna":
        expected_xrefs_by_status["EXPLICIT_CURRENT_POLYMER_DNA_COLLISION_XREF_EXCEPTION"] = [
            "CHEBI:16991",
            "pdb.ligand:DNA",
        ]
    expected_xrefs = expected_xrefs_by_status.get(
        str(trait_binding.get("trait_source_xref_status"))
    )
    if expected_xrefs is None:
        raise RegistryBuildError("BioLiP/SIFTS trait source xref status mismatch")
    if trait_binding.get("trait_source_xrefs") != expected_xrefs:
        raise RegistryBuildError("BioLiP/SIFTS trait source xrefs mismatch")

    binding_residue_pairs = source_projection.get("binding_residue_pairs")
    if not isinstance(binding_residue_pairs, list) or len(binding_residue_pairs) != len(
        mapped_residues
    ):
        raise RegistryBuildError("BioLiP/SIFTS binding residue pair count mismatch")
    for index, (pair, residue) in enumerate(
        zip(binding_residue_pairs, mapped_residues, strict=True), 1
    ):
        if not isinstance(pair, dict):
            raise RegistryBuildError(f"BioLiP/SIFTS binding residue pair {index} is invalid")
        _validate_binding_residue_pair(pair, residue, index)


def _validate_mapping_registry_row(row: Mapping[str, Any]) -> None:
    if set(row) != MAPPING_REGISTRY_FIELDS:
        missing = sorted(MAPPING_REGISTRY_FIELDS - set(row))
        extra = sorted(set(row) - MAPPING_REGISTRY_FIELDS)
        raise RegistryBuildError(
            f"BioLiP/SIFTS mapping fields mismatch; missing={missing}, extra={extra}"
        )
    if row.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise RegistryBuildError("BioLiP/SIFTS mapping schema_version is unsupported")
    if row.get("kind") != MAPPING_REGISTRY_KIND:
        raise RegistryBuildError("BioLiP/SIFTS mapping has unexpected kind")
    if row.get("stage_status") != "RELEASE_PINNED_PROTEIN_REFERENCE_BOUND":
        raise RegistryBuildError("BioLiP/SIFTS mapping stage_status is not bound")
    if row.get("qualification_claimed") is not False:
        raise RegistryBuildError("BioLiP/SIFTS mapping must not claim qualification")

    mapping_id = _require_registry_text(row, "mapping_id")
    expected_mapping_id = MAPPING_REGISTRY_ID_PREFIX + _mapping_id_sha256(row)
    if mapping_id != expected_mapping_id:
        raise RegistryBuildError("BioLiP/SIFTS mapping_id digest mismatch")
    if _require_sha256(row, "mapping_row_sha256") != mapping_entry_sha256(row):
        raise RegistryBuildError("BioLiP/SIFTS mapping_row_sha256 mismatch")
    if not _require_registry_text(row, "mapping_candidate_id").startswith(
        "biolip-sifts-mapping-candidate:"
    ):
        raise RegistryBuildError("BioLiP/SIFTS mapping_candidate_id has invalid prefix")
    _require_sha256(row, "mapping_candidate_row_sha256")

    protein_id = _require_registry_text(row, "protein_id")
    if not protein_id.startswith("UniProtKB:") or _ACCESSION.fullmatch(protein_id[10:]) is None:
        raise RegistryBuildError("BioLiP/SIFTS mapping protein_id is not an accession")
    for field in (
        "chain_id",
        "coordinate_frame",
        "expected_residues",
        "fetch_request_plan_id",
        "mapping_method",
        "mapping_completeness",
        "record_path",
        "scope",
        "sifts_entry_date",
        "sifts_source_url",
        "sifts_uniprot_version",
        "stage_status",
        "structure_id",
        "trait_id",
    ):
        _require_registry_text(row, field)
    for field in ("record_sha256", "sequence_sha256", "sifts_xml_sha256"):
        _require_sha256(row, field)
    if row["mapping_method"] != mapper.MAPPING_METHOD:
        raise RegistryBuildError("BioLiP/SIFTS mapping_method mismatch")
    if row["scope"] != mapper.SCOPE:
        raise RegistryBuildError("BioLiP/SIFTS scope mismatch")
    if row["coordinate_frame"] != mapper.COORDINATE_FRAME:
        raise RegistryBuildError("BioLiP/SIFTS coordinate_frame mismatch")
    if row["mapping_completeness"] != "COMPLETE":
        raise RegistryBuildError("BioLiP/SIFTS mapping is not complete")
    if not str(row["structure_id"]).startswith("PDB:"):
        raise RegistryBuildError("BioLiP/SIFTS structure_id is not a PDB CURIE")
    uniprot_release = _require_release(row, "uniprot_release")
    if _require_release(row, "sifts_uniprot_release") != uniprot_release:
        raise RegistryBuildError("BioLiP/SIFTS UniProt releases disagree")
    if row["sifts_uniprot_version"] != uniprot_release.replace("_", "."):
        raise RegistryBuildError("BioLiP/SIFTS release/version mismatch")

    snapshot = row.get("sifts_snapshot")
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "sifts_manifest_entry",
        "sifts_manifest_entry_sha256",
        "sifts_manifest_path",
        "sifts_manifest_sha256",
        "sifts_snapshot_id",
    }:
        raise RegistryBuildError("BioLiP/SIFTS snapshot projection is invalid")
    manifest_entry = snapshot["sifts_manifest_entry"]
    if not isinstance(manifest_entry, dict) or set(manifest_entry) != {
        "path",
        "pdb_id",
        "sha256",
        "sifts_entry_date",
        "sifts_uniprot_release",
        "sifts_uniprot_version",
        "size_bytes",
        "url",
    }:
        raise RegistryBuildError("BioLiP/SIFTS manifest entry projection is invalid")
    pdb_id = _require_registry_text(manifest_entry, "pdb_id")
    if not re.fullmatch(r"[0-9][a-z0-9]{3}", pdb_id):
        raise RegistryBuildError("BioLiP/SIFTS manifest entry pdb_id is invalid")
    if manifest_entry.get("path") != f"{pdb_id}.xml.gz":
        raise RegistryBuildError("BioLiP/SIFTS manifest entry path mismatch")
    if row["structure_id"] != f"PDB:{pdb_id}":
        raise RegistryBuildError("BioLiP/SIFTS structure/PDB mismatch")
    _require_int(manifest_entry, "size_bytes", positive=True, context="manifest entry")
    duplicated_entry_fields = {
        "sha256": "sifts_xml_sha256",
        "sifts_entry_date": "sifts_entry_date",
        "sifts_uniprot_release": "sifts_uniprot_release",
        "sifts_uniprot_version": "sifts_uniprot_version",
        "url": "sifts_source_url",
    }
    for field, row_field in duplicated_entry_fields.items():
        if row.get(row_field) != manifest_entry.get(field):
            raise RegistryBuildError(f"BioLiP/SIFTS manifest entry {field} mismatch")
    if snapshot["sifts_manifest_entry_sha256"] != mapper.value_sha256(manifest_entry):
        raise RegistryBuildError("BioLiP/SIFTS manifest entry digest mismatch")
    for field in ("sifts_manifest_path", "sifts_snapshot_id"):
        _require_registry_text(snapshot, field)
    for field in ("sifts_manifest_sha256",):
        _require_sha256(snapshot, field)

    mapped_residues = row.get("mapped_residues")
    residue_positions = row.get("residue_positions")
    if (
        not isinstance(mapped_residues, list)
        or not mapped_residues
        or not isinstance(residue_positions, list)
    ):
        raise RegistryBuildError("BioLiP/SIFTS residue projection is invalid")
    source_residue_count = _require_int(
        row, "source_residue_count", positive=True, context="mapping"
    )
    mapped_residue_count = _require_int(
        row, "mapped_residue_count", positive=True, context="mapping"
    )
    if source_residue_count != len(mapped_residues) or mapped_residue_count != len(
        mapped_residues
    ):
        raise RegistryBuildError("BioLiP/SIFTS mapped residue count mismatch")
    positions: list[int] = []
    residues: list[str] = []
    validated_mapped_residues: list[Mapping[str, Any]] = []
    for index, residue in enumerate(mapped_residues, 1):
        if not isinstance(residue, dict):
            raise RegistryBuildError(f"BioLiP/SIFTS mapped residue {index} is invalid")
        positions.append(_validate_mapping_residue(residue, str(row["chain_id"]), index))
        residues.append(str(residue["source_amino_acid"]))
        validated_mapped_residues.append(residue)
    if residue_positions != positions:
        raise RegistryBuildError("BioLiP/SIFTS residue_positions mismatch")
    if row["expected_residues"] != "".join(residues):
        raise RegistryBuildError("BioLiP/SIFTS expected_residues mismatch")

    _validate_source_projection(row, validated_mapped_residues)


def load_mapping_registry(path: Path) -> dict[str, dict[str, Any]]:
    """Load BioLiP/SIFTS registry rows and verify their content addresses."""

    if not path.is_file():
        raise RegistryBuildError(f"BioLiP/SIFTS mapping registry does not exist: {path}")
    registry: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                raise RegistryBuildError(
                    f"{path}:{line_number}: blank BioLiP/SIFTS mapping row"
                )
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RegistryBuildError(
                    f"{path}:{line_number}: invalid BioLiP/SIFTS mapping JSON: {exc}"
                ) from exc
            if not isinstance(row, dict):
                raise RegistryBuildError(
                    f"{path}:{line_number}: BioLiP/SIFTS mapping row is not an object"
                )
            if raw != _canonical_json(row) + "\n":
                raise RegistryBuildError(
                    f"{path}:{line_number}: BioLiP/SIFTS mapping row is not canonical"
                )
            try:
                _validate_mapping_registry_row(row)
            except RegistryBuildError as exc:
                raise RegistryBuildError(f"{path}:{line_number}: {exc}") from exc
            mapping_id = str(row["mapping_id"])
            if mapping_id in registry:
                raise RegistryBuildError(
                    f"{path}:{line_number}: duplicate BioLiP/SIFTS mapping {mapping_id}"
                )
            registry[mapping_id] = row
    return registry


def _chunks(values: Sequence[Target], size: int) -> Iterable[Sequence[Target]]:
    for offset in range(0, len(values), size):
        yield values[offset : offset + size]


def _derive_request_plan(args: argparse.Namespace) -> PreparedPlan:
    if not 1 <= args.batch_size <= 200:
        raise RegistryBuildError("--batch-size must be between 1 and 200")
    if not args.expect_release or _RELEASE.fullmatch(args.expect_release) is None:
        raise RegistryBuildError("--expect-release is required and must have form YYYY_NN")

    outputs = _resolved_output_paths(args)
    _reject_input_output_collisions(args, outputs)
    source_stage_artifact = _capture(args.stage, description="BioLiP source stage")
    sifts_manifest = _capture(args.sifts_snapshot / "manifest.json", description="SIFTS manifest")
    offline_fixture = (
        _capture(args.offline_responses, description="offline response fixture")
        if args.offline_responses is not None
        else None
    )

    result = mapper.build_stage(source_stage=args.stage, sifts_snapshot=args.sifts_snapshot)
    summary = result.summary
    if summary.get("source_stage_sha256") != source_stage_artifact.sha256:
        raise RegistryBuildError("BioLiP source stage changed during plan derivation")
    if summary.get("sifts_manifest_sha256") != sifts_manifest.sha256:
        raise RegistryBuildError("SIFTS manifest changed during plan derivation")

    targets = _targets_from_stage(result.protein_requests, expected_release=args.expect_release)
    mappings_by_candidate_id = _mappings_by_candidate_id(result.mappings)
    expected_candidate_ids = {
        candidate_id
        for target in targets
        for candidate_id in target.candidates[0]["mapping_candidate_ids"]
    }
    missing_candidate_ids = sorted(set(expected_candidate_ids) - set(mappings_by_candidate_id))
    if missing_candidate_ids:
        raise RegistryBuildError(
            "BioLiP/SIFTS protein requests reference missing mapping candidates: "
            + ", ".join(missing_candidate_ids[:5])
        )
    target_rows = [_target_projection(target) for target in targets]
    requests = [
        _request_projection(index, chunk)
        for index, chunk in enumerate(_chunks(targets, args.batch_size), 1)
    ]
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "kind": PLAN_KIND,
        "qualification_claimed": False,
        "network_action_performed": False,
        "fresh_fetch_scope": "ALL_EXACT_TARGETS_IN_BIOLIP_SIFTS_MAPPING_STAGE",
        "source_stage_artifact": _artifact_projection(source_stage_artifact),
        "sifts_manifest_artifact": _artifact_projection(sifts_manifest),
        "mapping_stage": {
            "stage_id": summary["stage_id"],
            "source_stage_id": summary["source_stage_id"],
            "source_stage_sha256": summary["source_stage_sha256"],
            "sifts_manifest_sha256": summary["sifts_manifest_sha256"],
            "ready_source_occurrence_count": summary["ready_source_occurrence_count"],
            "mapping_candidate_count": summary["mapping_candidate_count"],
            "mapping_blocker_count": summary["mapping_blocker_count"],
            "mapped_unique_trait_count": summary["mapped_unique_trait_count"],
            "mapped_unique_protein_count": summary["mapped_unique_protein_count"],
            "protein_reference_request_count": summary["protein_reference_request_count"],
            "mapping_candidate_rows_sha256": summary["mapping_candidate_rows_sha256"],
            "mapping_blocker_rows_sha256": summary["mapping_blocker_rows_sha256"],
            "protein_reference_request_rows_sha256": summary[
                "protein_reference_request_rows_sha256"
            ],
            "summary_sha256": mapper.value_sha256(summary),
        },
        "acquisition_mode": "OFFLINE_FIXTURE" if offline_fixture is not None else "UNIPROT_REST",
        "offline_fixture_artifact": (
            _artifact_projection(offline_fixture) if offline_fixture is not None else None
        ),
        "expected_uniprot_release": args.expect_release,
        "target_count": len(targets),
        "target_rows": target_rows,
        "target_rows_sha256": _value_sha256(target_rows),
        "request_policy": {
            "method": "GET",
            "endpoint": UNIPROT_SEARCH,
            "headers": REQUEST_HEADERS,
            "format": "json",
            "page_size": 500,
            "include_isoform": True,
            "return_fields": list(RETURN_FIELDS),
            "batch_size": args.batch_size,
            "response_release_header": "x-uniprot-release",
        },
        "request_count": len(requests),
        "requests": requests,
        "requests_sha256": _value_sha256(requests),
        "output_paths": {role: _output_path(path) for role, path in outputs.items()},
        "receipt_install_policy": "INSTALL_RECEIPT_LAST_AFTER_IGNORED_STAGING_OUTPUTS",
    }
    plan["request_plan_id"] = PLAN_ID_PREFIX + _value_sha256(plan)
    return PreparedPlan(
        plan=plan,
        targets=targets,
        mappings_by_candidate_id=mappings_by_candidate_id,
        offline_fixture=offline_fixture,
    )


def render_request_plan(plan: Mapping[str, Any]) -> str:
    return _canonical_json(plan) + "\n"


def _load_request_plan(path: Path) -> dict[str, Any]:
    artifact = _capture(path, description="request plan")
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"request plan is not strict UTF-8: {exc}") from exc
    if "\r" in text or not text.endswith("\n") or text.count("\n") != 1:
        raise RegistryBuildError("request plan must be one LF-terminated canonical JSON row")
    value = _load_json_unique(text[:-1], source=str(artifact.path))
    if not isinstance(value, dict) or text != render_request_plan(value):
        raise RegistryBuildError("request plan is not exact canonical JSON")
    if value.get("schema_version") != PLAN_SCHEMA_VERSION or value.get("kind") != PLAN_KIND:
        raise RegistryBuildError("request plan schema/kind mismatch")
    without_id = dict(value)
    observed_id = without_id.pop("request_plan_id", None)
    if observed_id != PLAN_ID_PREFIX + _value_sha256(without_id):
        raise RegistryBuildError("request plan content address is invalid")
    return value


def _require_exact_plan(supplied: Mapping[str, Any], derived: Mapping[str, Any]) -> None:
    if _canonical_json(supplied) != _canonical_json(derived):
        raise RegistryBuildError("supplied request plan does not match rederived exact plan")


def _blocked_row(target: Target, reason: str, detail: str) -> dict[str, str | int]:
    request = target.candidates[0]
    candidate_ids = request["mapping_candidate_ids"]
    return {
        "protein_id": target.protein_id,
        "accession": target.accession,
        "candidate_count": len(candidate_ids),
        "candidate_ids": ";".join(candidate_ids),
        "trait_ids": ";".join(request["trait_ids"]),
        "reason": reason,
        "detail": " ".join(detail.split()),
    }


def _blocked_text(rows: Sequence[Mapping[str, str | int]]) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=_BLOCKED_COLUMNS, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda row: (str(row["protein_id"]), str(row["reason"]))))
    return buffer.getvalue()


def _mapping_registry_row(
    mapping: Mapping[str, Any],
    *,
    reference: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    sifts_snapshot = mapping["sifts_snapshot"]
    sifts_entry = sifts_snapshot["sifts_manifest_entry"]
    row: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "kind": MAPPING_REGISTRY_KIND,
        "stage_status": "RELEASE_PINNED_PROTEIN_REFERENCE_BOUND",
        "qualification_claimed": False,
        "mapping_candidate_id": mapping["candidate_id"],
        "mapping_candidate_row_sha256": mapping["candidate_row_sha256"],
        "trait_id": mapping["trait_id"],
        "record_path": mapping["record_path"],
        "record_sha256": mapping["record_sha256"],
        "structure_id": mapping["structure_id"],
        "chain_id": mapping["chain_id"],
        "protein_id": mapping["protein_id"],
        "sequence_sha256": reference["sequence_sha256"],
        "uniprot_release": reference["uniprot_release"],
        "mapping_method": mapping["mapping_method"],
        "scope": mapping["scope"],
        "coordinate_frame": mapping["coordinate_frame"],
        "residue_positions": mapping["residue_positions"],
        "expected_residues": mapping["expected_residues"],
        "source_residue_count": mapping["source_residue_count"],
        "mapped_residue_count": mapping["mapped_residue_count"],
        "mapping_completeness": mapping["mapping_completeness"],
        "mapped_residues": mapping["mapped_residues"],
        "source_projection": mapping["source_projection"],
        "sifts_snapshot": sifts_snapshot,
        "sifts_entry_date": sifts_entry["sifts_entry_date"],
        "sifts_uniprot_release": sifts_entry["sifts_uniprot_release"],
        "sifts_uniprot_version": sifts_entry["sifts_uniprot_version"],
        "sifts_xml_sha256": sifts_entry["sha256"],
        "sifts_source_url": sifts_entry["url"],
        "source_stage_artifact": plan["source_stage_artifact"],
        "mapping_stage": plan["mapping_stage"],
        "fetch_request_plan_id": plan["request_plan_id"],
    }
    return mapper._content_address(  # noqa: SLF001 - reuse the BioLiP stage address rule
        row,
        id_field="mapping_id",
        prefix=MAPPING_REGISTRY_ID_PREFIX,
        row_hash_field="mapping_row_sha256",
    )


def _validate_mapped_residues(
    reference: Mapping[str, Any],
    target: Target,
    mappings_by_candidate_id: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    sequence = str(reference["sequence"])
    failures: list[str] = []
    request = target.candidates[0]
    for candidate_id in request["mapping_candidate_ids"]:
        mapping = mappings_by_candidate_id.get(candidate_id)
        if mapping is None:
            failures.append(f"{candidate_id}: mapping row is missing from replayed stage")
            continue
        positions = mapping.get("residue_positions")
        expected = mapping.get("expected_residues")
        if (
            not isinstance(positions, list)
            or not positions
            or not isinstance(expected, str)
            or len(positions) != len(expected)
        ):
            failures.append(f"{candidate_id}: malformed mapped residue projection")
            continue
        for position, amino_acid in zip(positions, expected, strict=True):
            if not isinstance(position, int) or position < 1:
                failures.append(f"{candidate_id}: invalid UniProt position {position!r}")
                continue
            if position > len(sequence):
                failures.append(
                    f"{candidate_id}: mapped position {position} exceeds fetched sequence "
                    f"length {len(sequence)}"
                )
                continue
            observed = sequence[position - 1]
            if observed != amino_acid:
                failures.append(
                    f"{candidate_id}: mapped position {position} expected {amino_acid} "
                    f"but fetched sequence has {observed}"
                )
    return failures


def _output_projection(path: str, text: str, *, row_count: int) -> dict[str, Any]:
    raw = text.encode("utf-8")
    return {
        "path": path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "row_count": row_count,
    }


def _receipt(
    *,
    plan: Mapping[str, Any],
    response_rows: Sequence[Mapping[str, Any]],
    release: str,
    registry_text: str,
    membership_text: str,
    mapping_text: str,
    blocked_text: str,
    reference_count: int,
    membership_count: int,
    mapping_count: int,
    blocked_count: int,
) -> dict[str, Any]:
    output_paths = plan["output_paths"]
    row: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "kind": RECEIPT_KIND,
        "generation_boundary": True,
        "receipt_install_policy": plan["receipt_install_policy"],
        "request_plan_id": plan["request_plan_id"],
        "expected_uniprot_release": plan["expected_uniprot_release"],
        "observed_uniprot_release": release,
        "acquisition_mode": plan["acquisition_mode"],
        "network_action_performed": plan["acquisition_mode"] == "UNIPROT_REST",
        "offline_fixture_artifact": plan["offline_fixture_artifact"],
        "mapping_stage": plan["mapping_stage"],
        "target_count": plan["target_count"],
        "request_count": len(response_rows),
        "response_rows": list(response_rows),
        "response_rows_sha256": _value_sha256(list(response_rows)),
        "outputs": {
            "protein_registry": _output_projection(
                output_paths["protein_registry"], registry_text, row_count=reference_count
            ),
            "membership_registry": _output_projection(
                output_paths["membership_registry"], membership_text, row_count=membership_count
            ),
            "sifts_mapping_registry": _output_projection(
                output_paths["sifts_mapping_registry"], mapping_text, row_count=mapping_count
            ),
            "blocked_registry": _output_projection(
                output_paths["blocked_registry"], blocked_text, row_count=blocked_count
            ),
        },
        "all_targets_accounted_for": True,
        "qualification_claimed": False,
    }
    row["receipt_id"] = RECEIPT_ID_PREFIX + _value_sha256(row)
    return row


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _fetch_outputs(
    *, args: argparse.Namespace, prepared: PreparedPlan, supplied_plan: Mapping[str, Any]
) -> tuple[str, str, str, str, str, int, int, int, int]:
    client = (
        OfflineClient(prepared.offline_fixture)
        if prepared.offline_fixture is not None
        else NetworkClient(
            timeout=args.timeout,
            retries=args.retries,
            interval=args.request_interval,
        )
    )
    references: list[dict[str, Any]] = []
    memberships: list[dict[str, Any]] = []
    mapping_registry: list[dict[str, Any]] = []
    blocked: list[dict[str, str | int]] = []
    response_receipts: list[dict[str, Any]] = []
    pinned_release: str | None = None

    chunks = list(_chunks(prepared.targets, args.batch_size))
    if len(chunks) != len(supplied_plan["requests"]):
        raise RegistryBuildError("request plan chunk count changed before fetch")
    for target_batch, planned_request in zip(chunks, supplied_plan["requests"], strict=True):
        requested = tuple(target.accession for target in target_batch)
        response = client.fetch(requested)
        if response.acquisition_mode != supplied_plan["acquisition_mode"]:
            raise RegistryBuildError("fetch response acquisition mode does not match request plan")
        if response.requested != requested:
            raise RegistryBuildError("fetch client response does not bind the requested set")
        if response.request_url != planned_request["request_url"]:
            raise RegistryBuildError("fetch client response does not bind the planned URL")
        if response.status != 200:
            raise RegistryBuildError(f"UniProt response status {response.status} is not 200")
        release = _clean(response.release)
        if not release or _RELEASE.fullmatch(release) is None:
            raise RegistryBuildError("UniProt response is missing a valid x-uniprot-release")
        if pinned_release is None:
            pinned_release = release
        elif release != pinned_release:
            raise RegistryBuildError(
                f"mixed UniProt releases in one BioLiP/SIFTS run: {pinned_release} and {release}"
            )
        if release != args.expect_release:
            raise RegistryBuildError(
                f"UniProt response release {release} != expected {args.expect_release}"
            )

        by_accession: dict[str, list[dict[str, Any]]] = {}
        requested_set = set(requested)
        unexpected: set[str] = set()
        for entry in response.results:
            accession = _clean(entry.get("primaryAccession"))
            if accession not in requested_set:
                if accession:
                    unexpected.add(accession)
                continue
            by_accession.setdefault(accession, []).append(entry)
        exact_returned = sorted(
            accession for accession, entries in by_accession.items() for _entry in entries
        )
        unexpected_sorted = sorted(unexpected)
        response_receipts.append(
            _response_receipt_row(
                request=planned_request,
                response=response,
                exact_accessions=exact_returned,
                unexpected_accessions=unexpected_sorted,
            )
        )
        for target in target_batch:
            matches = by_accession.get(target.accession, [])
            if not matches:
                blocked.append(
                    _blocked_row(
                        target,
                        "ACCESSION_NOT_RETURNED",
                        "official exact-accession query returned no exact entry",
                    )
                )
                continue
            if len(matches) != 1:
                blocked.append(
                    _blocked_row(
                        target,
                        "DUPLICATE_API_RESULT",
                        f"official response contained {len(matches)} exact entries",
                    )
                )
                continue
            reference, failures = _entry_reference(matches[0], target, release)
            if failures:
                blocked.append(
                    _blocked_row(target, "REFERENCE_VALIDATION_FAILED", "; ".join(failures))
                )
                continue
            if reference is None:
                raise RegistryBuildError("internal error: valid UniProt entry made no reference")
            residue_failures = _validate_mapped_residues(
                reference,
                target,
                prepared.mappings_by_candidate_id,
            )
            if residue_failures:
                blocked.append(
                    _blocked_row(
                        target,
                        "MAPPED_RESIDUE_VALIDATION_FAILED",
                        "; ".join(residue_failures),
                    )
                )
                continue
            try:
                facts = extract_entry_memberships(
                    matches[0],
                    protein_id=reference["protein_id"],
                    sequence_sha256=reference["sequence_sha256"],
                    uniprot_release=reference["uniprot_release"],
                )
            except MembershipSnapshotError as exc:
                # One malformed fact blocks that accession, never the batch (#978).
                blocked.append(_blocked_row(target, "FACT_SNAPSHOT_FAILED", str(exc)))
                continue
            references.append(reference)
            for candidate_id in target.candidates[0]["mapping_candidate_ids"]:
                mapping_registry.append(
                    _mapping_registry_row(
                        prepared.mappings_by_candidate_id[candidate_id],
                        reference=reference,
                        plan=supplied_plan,
                    )
                )
            memberships.extend(facts)
    client.finish()

    if pinned_release is None:
        raise RegistryBuildError("fetch produced no release-stamped responses")
    references.sort(key=lambda row: row["protein_id"])
    mapping_registry.sort(key=lambda row: row["mapping_id"])
    if len({row["protein_id"] for row in references}) != len(references):
        raise RegistryBuildError("internal error: duplicate ProteinReference output key")
    if len({row["mapping_id"] for row in mapping_registry}) != len(mapping_registry):
        raise RegistryBuildError("internal error: duplicate BioLiP/SIFTS mapping output key")
    reference_ids = {str(row["protein_id"]) for row in references}
    expected_mapping_candidate_ids = {
        candidate_id
        for target in prepared.targets
        if target.protein_id in reference_ids
        for candidate_id in target.candidates[0]["mapping_candidate_ids"]
    }
    observed_mapping_candidate_ids = {
        str(row["mapping_candidate_id"]) for row in mapping_registry
    }
    if expected_mapping_candidate_ids != observed_mapping_candidate_ids:
        raise RegistryBuildError(
            "internal error: BioLiP/SIFTS mapping outputs do not account for every "
            "successful mapped candidate"
        )
    try:
        memberships = merge_memberships(memberships)
        membership_text = dump_memberships(memberships)
    except MembershipSnapshotError as exc:
        raise RegistryBuildError(f"invalid UniProt membership snapshot: {exc}") from exc

    registry_text = "".join(_canonical_json(reference) + "\n" for reference in references)
    mapping_text = "".join(_canonical_json(row) + "\n" for row in mapping_registry)
    blocked_text = _blocked_text(blocked)
    target_ids = {target.protein_id for target in prepared.targets}
    blocked_ids = {str(row["protein_id"]) for row in blocked}
    if reference_ids & blocked_ids or reference_ids | blocked_ids != target_ids:
        raise RegistryBuildError("internal error: fetched outputs do not account for every target")

    final = _derive_request_plan(args)
    _require_exact_plan(supplied_plan, final.plan)

    receipt = _receipt(
        plan=supplied_plan,
        response_rows=response_receipts,
        release=pinned_release,
        registry_text=registry_text,
        membership_text=membership_text,
        mapping_text=mapping_text,
        blocked_text=blocked_text,
        reference_count=len(references),
        membership_count=len(memberships),
        mapping_count=len(mapping_registry),
        blocked_count=len(blocked),
    )
    return (
        registry_text,
        membership_text,
        mapping_text,
        blocked_text,
        _canonical_json(receipt) + "\n",
        len(references),
        len(memberships),
        len(mapping_registry),
        len(blocked),
    )


def build(args: argparse.Namespace) -> int:
    prepared = _derive_request_plan(args)
    if not args.apply:
        if args.request_plan is not None:
            raise RegistryBuildError("--request-plan is supplied only with --apply")
        sys.stdout.write(render_request_plan(prepared.plan))
        return 0
    if args.request_plan is None:
        raise RegistryBuildError("--apply requires an exact saved --request-plan")
    output_paths = _resolved_output_paths(args)
    plan_path = Path(args.request_plan)
    plan_output_collisions = {
        _output_path(path): role for role, path in output_paths.items()
    }
    if _output_path(plan_path) in plan_output_collisions:
        raise RegistryBuildError("request plan path collides with a staging output")
    supplied_plan = _load_request_plan(plan_path)
    _require_exact_plan(supplied_plan, prepared.plan)

    (
        registry_text,
        membership_text,
        mapping_text,
        blocked_text,
        receipt_text,
        reference_count,
        membership_count,
        mapping_count,
        blocked_count,
    ) = _fetch_outputs(args=args, prepared=prepared, supplied_plan=supplied_plan)

    _atomic_write(output_paths["protein_registry"], registry_text)
    _atomic_write(output_paths["membership_registry"], membership_text)
    _atomic_write(output_paths["sifts_mapping_registry"], mapping_text)
    _atomic_write(output_paths["blocked_registry"], blocked_text)
    _atomic_write(output_paths["fetch_receipt"], receipt_text)
    print(f"WROTE {output_paths['protein_registry']} ({reference_count:,} ProteinReference rows)")
    print(f"WROTE {output_paths['membership_registry']} ({membership_count:,} membership rows)")
    print(f"WROTE {output_paths['sifts_mapping_registry']} ({mapping_count:,} SIFTS mapping rows)")
    print(f"WROTE {output_paths['blocked_registry']} ({blocked_count:,} blocked accessions)")
    print(f"WROTE {output_paths['fetch_receipt']} (generation boundary)")
    return 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, default=mapper.DEFAULT_STAGE)
    ap.add_argument("--sifts-snapshot", type=Path, default=mapper.DEFAULT_SIFTS_SNAPSHOT)
    ap.add_argument("--batch-size", type=int, default=100)
    ap.add_argument("--expect-release", required=True)
    ap.add_argument("--out", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--membership-out", type=Path)
    ap.add_argument("--mapping-out", type=Path)
    ap.add_argument("--blocked", type=Path, default=DEFAULT_BLOCKED)
    ap.add_argument("--receipt", type=Path)
    ap.add_argument("--request-plan", type=Path)
    ap.add_argument("--offline-responses", type=Path)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--request-interval", type=float, default=0.15)
    ap.add_argument("--apply", action="store_true")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.timeout <= 0 or args.retries < 0 or args.request_interval < 0:
        print(
            "ERROR: timeout must be positive; retries/interval cannot be negative",
            file=sys.stderr,
        )
        return 2
    try:
        return build(args)
    except (
        EcodSiftsError,
        KeyError,
        OSError,
        RegistryBuildError,
        mapper.BioLipSiftsMappingError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
