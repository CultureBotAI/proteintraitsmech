#!/usr/bin/env python3
"""Validate release-pinned UniProt grounding of canonical examples.

LinkML validates object shape.  This command enforces the cross-object and
sequence-dependent invariants that JSON Schema cannot express: exact registry
resolution, content-addressed source-evidence dereferencing, version/checksum
agreement, UniProt coordinate frames and bounds, record-specific trait identity,
authoritative inheritance paths, sequence/pattern agreement, complete SIFTS
mapping, and the categories allowed to make WHOLE_PROTEIN assertions.

Existing canonical examples are migration data: absence of
``qualification_status`` means ``LEGACY_UNVERIFIED`` and is allowed by default.
Use ``--require-qualified`` for a completion gate; it rejects every legacy or
intermediate canonical example and every record without a declared QUALIFIED
example.  A QUALIFIED claim is always validated strictly, with or without that
flag.

The protein, occurrence-evidence, and UniProt-membership registries are JSONL
with one normalized object per line.  A qualified UniProt ``SOURCE_MEMBERSHIP``
claim is replayed against the exact content-addressed database cross-reference::

    python scripts/validate_uniprot_grounding.py data/traits/sequence/domain \
      --registry reports/uniprot-grounding/protein_registry.jsonl \
      --evidence-registry reports/uniprot-grounding/occurrence_evidence.jsonl \
      --membership-registry reports/uniprot-grounding/uniprot_memberships.jsonl \
      --out reports/uniprot-grounding/validation.tsv

No network access is performed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAITS = ROOT / "data" / "traits"
DEFAULT_REPORT = ROOT / "reports" / "uniprot-grounding" / "validation.tsv"
DEFAULT_REGISTRY = ROOT / "data" / "grounding" / "protein_registry.jsonl"
DEFAULT_EVIDENCE_REGISTRY = ROOT / "data" / "grounding" / "occurrence_evidence.jsonl"
DEFAULT_MEMBERSHIP_REGISTRY = ROOT / "data" / "grounding" / "uniprot_memberships.jsonl"

QUALIFIED = "QUALIFIED"
LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"

UNIPROT_RE = re.compile(
    r"^UniProtKB:([OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-([0-9]+))?$"
)
TAXON_RE = re.compile(r"^NCBITaxon:[0-9]+$")
CURIE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RELEASE_RE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
SEQUENCE_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")
ELM_TRAIT_RE = re.compile(r"^ELM:ELME[0-9]{6}$")
IDPO_TRAIT_RE = re.compile(r"^IDPO:[0-9]{7}$")
COMPLEXPORTAL_TRAIT_RE = re.compile(r"^ComplexPortal:CPX-[1-9][0-9]*$")
RHEA_TRAIT_RE = re.compile(r"^RHEA:[1-9][0-9]*$")
SCOP_TRAIT_RE = re.compile(r"^SCOP:[1-9][0-9]*$")
CATH_TRAIT_RE = re.compile(r"^CATH:[1-9][0-9]*(?:\.[1-9][0-9]*){0,3}$")
CATH_HOMOLOGOUS_SUPERFAMILY_TRAIT_RE = re.compile(r"^CATH:[1-9][0-9]*(?:\.[1-9][0-9]*){3}$")
THREEDID_TRAIT_RE = re.compile(r"^proteintraitsmech:INTERFACE_PF[0-9]+_PF[0-9]+$")
BIOLIP_TRAIT_RE = re.compile(r"^proteintraitsmech:BIOLIP_[A-Z0-9_]+$")
METALPDB_TRAIT_RE = re.compile(r"^proteintraitsmech:METALPDB_[A-Z0-9_]+$")
RHEA_RELEASE = "141"
RHEA_PROVIDER_SOURCE = "data/raw/rhea/rhea2uniprot_sprot.tsv"
REGISTRY_REQUIRED_FIELDS = (
    "protein_id",
    "protein_label",
    "taxon_id",
    "taxon_label",
    "sequence",
    "sequence_length",
    "sequence_sha256",
    "reviewed",
    "uniprot_release",
)
REGISTRY_ALLOWED_FIELDS = set(REGISTRY_REQUIRED_FIELDS) | {"isoform", "sequence_version"}

EVIDENCE_PREFIX = "ug-evidence:"
EVIDENCE_REQUIRED_FIELDS = (
    "evidence_id",
    "trait_id",
    "protein_id",
    "source_trait_id",
    "mapping_method",
    "scope",
    "evidence_source",
    "source_release",
    "sequence_sha256",
    "provider_kind",
    "provider_source",
    "provider_release",
    "provider_entry_sha256",
)
OCCURRENCE_EVIDENCE_FIELDS = (
    "trait_id",
    "protein_id",
    "source_trait_id",
    "inheritance_path",
    "mapping_method",
    "scope",
    "coordinate_frame",
    "intervals",
    "residue_positions",
    "expected_residues",
    "evidence_source",
    "source_release",
    "sequence_sha256",
    "structure_id",
    "chain_id",
    "mapping_completeness",
    "source_residue_count",
    "mapped_residue_count",
)
EVIDENCE_PROVIDER_FIELDS = (
    "provider_kind",
    "provider_source",
    "provider_release",
    "provider_entry_sha256",
)
EVIDENCE_PAYLOAD_FIELDS = OCCURRENCE_EVIDENCE_FIELDS + EVIDENCE_PROVIDER_FIELDS
EVIDENCE_ALLOWED_FIELDS = {"evidence_id", *EVIDENCE_PAYLOAD_FIELDS}
EVIDENCE_PROVIDER_KINDS = {"UNIPROT", "INTERPRO", "SIFTS", "SOURCE_DATABASE"}

INTERPRO_NAMESPACES = {
    "CATH",
    "CDD",
    "Gene3D",
    "HAMAP",
    "InterPro",
    "NCBIfam",
    "PANTHER",
    "Pfam",
    "PRINTS",
    "PROSITE",
    "SFLD",
    "SMART",
    "SUPERFAMILY",
}
STRUCTURE_DERIVED_NAMESPACES = {
    "3did",
    "BioLiP",
    "ECOD",
    "M-CSA",  # Legacy alias retained for already-staged evidence.
    "MCSA",
    "MetalPDB",
    "PDB",
    "RepeatsDB",
    "SCOP",
    "SCOPe",
    "ThreeDID",
}

WHOLE_PROTEIN_SEQUENCE_CATEGORIES = {"SEQ_FAMILY", "SEQ_HOMOLOGOUS_SUPERFAMILY"}
WHOLE_PROTEIN_METHODS = {"SOURCE_MEMBERSHIP", "SOURCE_ANNOTATION", "INTERPRO_MATCH"}
LOCALIZED_METHODS = {
    "UNIPROT_FEATURE",
    "INTERPRO_MATCH",
    "SOURCE_NATIVE_COORDINATES",
    "SIFTS_RESIDUE_MAPPING",
    "PATTERN_MATCH",
}


@dataclass(frozen=True)
class PendingProviderLock:
    """One exact source identity whose qualification receipt is not yet verifiable."""

    key: str
    code: str
    message: str
    evidence_sources: frozenset[str]
    namespaces: frozenset[str]
    identifier_patterns: tuple[re.Pattern[str], ...] = ()


PENDING_PROVIDER_LOCKS = (
    PendingProviderLock(
        key="prints",
        code="prints_provider_receipt_required",
        message=(
            "PRINTS evidence cannot qualify until a versioned ordered-fingerprint "
            "matcher and post-processing execution receipt is represented and verified "
            "by the grounding boundary"
        ),
        evidence_sources=frozenset({"PRINTS"}),
        namespaces=frozenset({"PRINTS"}),
    ),
    PendingProviderLock(
        key="sfld",
        code="sfld_provider_receipt_required",
        message=(
            "SFLD evidence cannot qualify until the source-model repair and exact "
            "profile/site execution receipt are represented and verified by the "
            "grounding boundary"
        ),
        evidence_sources=frozenset({"SFLD"}),
        namespaces=frozenset({"SFLD"}),
    ),
    PendingProviderLock(
        key="ecod",
        code="ecod_provider_receipt_required",
        message=(
            "ECOD evidence cannot qualify until complete source, ProteinReference, and "
            "residue-level SIFTS acquisition receipts are represented and verified by "
            "the grounding boundary"
        ),
        evidence_sources=frozenset({"ECOD", "ECOD via PDBe SIFTS"}),
        namespaces=frozenset({"ECOD"}),
    ),
    PendingProviderLock(
        key="threedid",
        code="threedid_provider_receipt_required",
        message=(
            "3did evidence cannot qualify until the corrected source model and complete "
            "residue-level SIFTS replay of both interface participants and their contact "
            "residues are represented and verified by the grounding boundary"
        ),
        evidence_sources=frozenset({"3did", "ThreeDID"}),
        namespaces=frozenset({"3did", "ThreeDID"}),
        identifier_patterns=(THREEDID_TRAIT_RE,),
    ),
    PendingProviderLock(
        key="biolip",
        code="biolip_provider_receipt_required",
        message=(
            "BioLiP evidence cannot qualify until provider-release, ProteinReference, "
            "and complete residue-level SIFTS receipts are represented and verified by "
            "the grounding boundary"
        ),
        evidence_sources=frozenset({"BioLiP"}),
        namespaces=frozenset({"BioLiP"}),
        identifier_patterns=(BIOLIP_TRAIT_RE,),
    ),
    PendingProviderLock(
        key="mcsa",
        code="mcsa_provider_receipt_required",
        message=(
            "M-CSA evidence cannot qualify until an exact source occurrence and the "
            "exemplar protein's complete catalytic-residue SIFTS receipt are represented "
            "and verified by the grounding boundary"
        ),
        evidence_sources=frozenset({"M-CSA", "MCSA"}),
        namespaces=frozenset({"M-CSA", "MCSA"}),
    ),
    PendingProviderLock(
        key="metalpdb",
        code="metalpdb_provider_receipt_required",
        message=(
            "MetalPDB evidence cannot qualify until exact source-site and complete "
            "residue-level SIFTS receipts are represented and verified by the grounding "
            "boundary"
        ),
        evidence_sources=frozenset({"MetalPDB"}),
        namespaces=frozenset({"MetalPDB"}),
        identifier_patterns=(METALPDB_TRAIT_RE,),
    ),
    PendingProviderLock(
        key="repeatsdb",
        code="repeatsdb_provider_receipt_required",
        message=(
            "RepeatsDB evidence cannot qualify until exact source-occurrence boundaries "
            "and complete residue-level SIFTS receipts are represented and verified by "
            "the grounding boundary"
        ),
        evidence_sources=frozenset({"RepeatsDB"}),
        namespaces=frozenset({"RepeatsDB"}),
    ),
)


@dataclass(frozen=True)
class Finding:
    """One deterministic semantic-validation finding."""

    file: str
    trait_id: str
    protein_id: str
    example_index: str
    occurrence_index: str
    code: str
    message: str


@dataclass(frozen=True)
class MembershipUse:
    """One qualified record occurrence that claims UniProt source membership."""

    file: str
    trait_id: str
    protein_id: str
    example_index: int
    occurrence_index: int
    evidence_id: str
    evidence_source: str


def _finding(
    code: str,
    message: str,
    *,
    file: str,
    trait_id: object = "",
    protein_id: object = "",
    example_index: object = "",
    occurrence_index: object = "",
) -> Finding:
    return Finding(
        file=file,
        trait_id=str(trait_id or ""),
        protein_id=str(protein_id or ""),
        example_index=str(example_index),
        occurrence_index=str(occurrence_index),
        code=code,
        message=message,
    )


def _is_positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def effective_qualification_status(example: Mapping[str, Any]) -> str:
    """Return the migration-aware status; an absent marker is legacy, never qualified."""

    value = example.get("qualification_status")
    return str(value) if value is not None else LEGACY_UNVERIFIED


def _registry_finding(code: str, message: str, path: Path, line: int, pid: object = "") -> Finding:
    return _finding(
        code,
        message,
        file=f"{path}:{line}",
        protein_id=pid,
        example_index="",
        occurrence_index="",
    )


def validate_protein_reference(reference: object, *, path: Path, line: int) -> list[Finding]:
    """Validate one registry object independently of whether a record uses it."""

    if not isinstance(reference, dict):
        return [
            _registry_finding(
                "registry_not_object", "registry line must be a JSON object", path, line
            )
        ]

    findings: list[Finding] = []
    pid = reference.get("protein_id", "")
    for field in REGISTRY_REQUIRED_FIELDS:
        if field not in reference:
            findings.append(
                _registry_finding(
                    "registry_missing_field", f"missing required field {field!r}", path, line, pid
                )
            )
    for field in sorted(set(reference) - REGISTRY_ALLOWED_FIELDS):
        findings.append(
            _registry_finding(
                "registry_unknown_field",
                f"unknown ProteinReference field {field!r}",
                path,
                line,
                pid,
            )
        )

    accession_match = UNIPROT_RE.fullmatch(pid) if isinstance(pid, str) else None
    if accession_match is None:
        findings.append(
            _registry_finding(
                "invalid_accession",
                "protein_id is not an exact UniProtKB accession",
                path,
                line,
                pid,
            )
        )
    for field in ("protein_label", "taxon_label"):
        if field in reference and not _nonempty_string(reference[field]):
            findings.append(
                _registry_finding(
                    "registry_invalid_field", f"{field} must be a non-empty string", path, line, pid
                )
            )
    taxon_id = reference.get("taxon_id")
    if "taxon_id" in reference and (
        not isinstance(taxon_id, str) or TAXON_RE.fullmatch(taxon_id) is None
    ):
        findings.append(
            _registry_finding(
                "invalid_taxon_id", "taxon_id must be an NCBITaxon CURIE", path, line, pid
            )
        )

    sequence = reference.get("sequence")
    sequence_ok = isinstance(sequence, str) and SEQUENCE_RE.fullmatch(sequence) is not None
    if "sequence" in reference and not sequence_ok:
        findings.append(
            _registry_finding(
                "registry_invalid_sequence",
                "sequence must be an uppercase, separator-free amino-acid string",
                path,
                line,
                pid,
            )
        )
    length = reference.get("sequence_length")
    if "sequence_length" in reference and not _is_positive_int(length):
        findings.append(
            _registry_finding(
                "registry_invalid_length",
                "sequence_length must be a positive integer",
                path,
                line,
                pid,
            )
        )
    elif sequence_ok and length != len(sequence):
        findings.append(
            _registry_finding(
                "registry_length_mismatch",
                f"sequence_length={length!r}, but len(sequence)={len(sequence)}",
                path,
                line,
                pid,
            )
        )

    checksum = reference.get("sequence_sha256")
    if "sequence_sha256" in reference and (
        not isinstance(checksum, str) or SHA256_RE.fullmatch(checksum) is None
    ):
        findings.append(
            _registry_finding(
                "registry_invalid_checksum",
                "sequence_sha256 must be 64 lower-case hex digits",
                path,
                line,
                pid,
            )
        )
    elif sequence_ok:
        observed = hashlib.sha256(sequence.encode("ascii")).hexdigest()
        if checksum != observed:
            findings.append(
                _registry_finding(
                    "registry_checksum_mismatch",
                    f"sequence_sha256 does not match sequence (expected {observed})",
                    path,
                    line,
                    pid,
                )
            )

    if "reviewed" in reference and not isinstance(reference["reviewed"], bool):
        findings.append(
            _registry_finding(
                "registry_invalid_reviewed", "reviewed must be true or false", path, line, pid
            )
        )
    release = reference.get("uniprot_release")
    if "uniprot_release" in reference and (
        not isinstance(release, str) or RELEASE_RE.fullmatch(release) is None
    ):
        findings.append(
            _registry_finding(
                "registry_invalid_release",
                "uniprot_release must have form YYYY_NN",
                path,
                line,
                pid,
            )
        )
    if "sequence_version" in reference and not _is_positive_int(reference["sequence_version"]):
        findings.append(
            _registry_finding(
                "registry_invalid_sequence_version",
                "sequence_version must be a positive integer when present",
                path,
                line,
                pid,
            )
        )

    isoform = reference.get("isoform")
    suffix = int(accession_match.group(2)) if accession_match and accession_match.group(2) else None
    if suffix is None and "isoform" in reference:
        findings.append(
            _registry_finding(
                "canonical_has_isoform",
                "canonical protein_id must omit the isoform field",
                path,
                line,
                pid,
            )
        )
    elif suffix is not None and isoform != suffix:
        findings.append(
            _registry_finding(
                "isoform_mismatch",
                f"protein_id suffix -{suffix} requires isoform={suffix}",
                path,
                line,
                pid,
            )
        )
    return findings


def load_registry(path: Path) -> tuple[dict[str, dict[str, Any]], list[Finding]]:
    """Load and strictly validate a ProteinReference JSONL registry."""

    registry: dict[str, dict[str, Any]] = {}
    findings: list[Finding] = []
    if not path.is_file():
        return registry, [
            _registry_finding("registry_not_found", "protein registry does not exist", path, 0)
        ]
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                findings.append(
                    _registry_finding(
                        "registry_json_error", f"invalid JSON: {error.msg}", path, line_number
                    )
                )
                continue
            findings.extend(validate_protein_reference(value, path=path, line=line_number))
            if not isinstance(value, dict) or not isinstance(value.get("protein_id"), str):
                continue
            pid = value["protein_id"]
            if pid in registry:
                findings.append(
                    _registry_finding(
                        "duplicate_registry_key",
                        f"duplicate protein_id; first occurrence retained: {pid}",
                        path,
                        line_number,
                        pid,
                    )
                )
                continue
            registry[pid] = value
    return registry, findings


def canonical_evidence_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return the stable, complete payload used to address GroundingEvidence.

    Optional fields are represented as JSON null, so omission and an explicit
    null cannot create two identifiers for the same assertion. Lists retain
    their biologically significant order. JSON object key order is normalized
    by :func:`compute_evidence_id`.
    """

    return {field: value.get(field) for field in EVIDENCE_PAYLOAD_FIELDS}


def compute_evidence_id(value: Mapping[str, Any]) -> str:
    """Compute ``ug-evidence:<sha256>`` over canonical UTF-8 JSON."""

    encoded = json.dumps(
        canonical_evidence_payload(value),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return EVIDENCE_PREFIX + hashlib.sha256(encoded).hexdigest()


def build_grounding_evidence(
    occurrence: Mapping[str, Any],
    *,
    provider_kind: str,
    provider_source: str,
    provider_release: str,
    provider_entry_sha256: str,
) -> dict[str, Any]:
    """Build a content-addressed evidence object from an occurrence.

    This is the resolver-facing API. It intentionally ignores
    ``qualification_status`` and ``source_evidence_id``; all scientific facts
    copied to a TraitOccurrence are projected from the fixed field list above.
    """

    evidence = {
        field: occurrence[field]
        for field in OCCURRENCE_EVIDENCE_FIELDS
        if field in occurrence and occurrence[field] is not None
    }
    evidence.update(
        {
            "provider_kind": provider_kind,
            "provider_source": provider_source,
            "provider_release": provider_release,
            "provider_entry_sha256": provider_entry_sha256,
        }
    )
    evidence["evidence_id"] = compute_evidence_id(evidence)
    return evidence


def _evidence_finding(
    code: str, message: str, path: Path, line: int, value: object = None
) -> Finding:
    evidence = value if isinstance(value, dict) else {}
    return _finding(
        code,
        message,
        file=f"{path}:{line}",
        trait_id=evidence.get("trait_id", ""),
        protein_id=evidence.get("protein_id", ""),
        example_index="",
        occurrence_index="",
    )


def _namespace(value: object) -> str:
    return value.split(":", 1)[0] if isinstance(value, str) and ":" in value else ""


def _matching_pending_provider_locks(
    evidence: Mapping[str, Any],
) -> tuple[PendingProviderLock, ...]:
    """Return each pending source lock once from exact source or identifier claims."""

    source = evidence.get("evidence_source")
    identifiers = (evidence.get("trait_id"), evidence.get("source_trait_id"))
    namespaces = {_namespace(identifier) for identifier in identifiers}
    matched: list[PendingProviderLock] = []
    for lock in PENDING_PROVIDER_LOCKS:
        if (
            isinstance(source, str)
            and source in lock.evidence_sources
            or namespaces & lock.namespaces
        ):
            matched.append(lock)
            continue
        if any(
            isinstance(identifier, str)
            and any(
                pattern.fullmatch(identifier) is not None for pattern in lock.identifier_patterns
            )
            for identifier in identifiers
        ):
            matched.append(lock)
    return tuple(matched)


def _provider_contract_errors(evidence: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Return method/provider/source contracts independent of a trait record."""

    method = evidence.get("mapping_method")
    kind = evidence.get("provider_kind")
    source = evidence.get("evidence_source")
    source_namespace = _namespace(evidence.get("source_trait_id"))
    namespaces = {source_namespace, _namespace(evidence.get("trait_id"))}
    pending_locks = _matching_pending_provider_locks(evidence)
    errors: list[tuple[str, str]] = []

    allowed_kinds = {
        "UNIPROT_FEATURE": {"UNIPROT"},
        "INTERPRO_MATCH": {"INTERPRO"},
        "SOURCE_NATIVE_COORDINATES": {"SOURCE_DATABASE"},
        "SIFTS_RESIDUE_MAPPING": {"SIFTS"},
        "PATTERN_MATCH": {"SOURCE_DATABASE"},
        "SOURCE_MEMBERSHIP": {"SOURCE_DATABASE", "UNIPROT"},
        "SOURCE_ANNOTATION": {"SOURCE_DATABASE", "UNIPROT"},
    }.get(method)
    if allowed_kinds is not None and kind not in allowed_kinds:
        errors.append(
            (
                "evidence_provider_method_mismatch",
                f"{method} requires provider_kind in {sorted(allowed_kinds)}, observed {kind!r}",
            )
        )

    if method == "INTERPRO_MATCH":
        if source != "InterPro":
            errors.append(
                (
                    "interpro_source_mismatch",
                    "INTERPRO_MATCH requires evidence_source exactly 'InterPro'",
                )
            )
        if source_namespace not in INTERPRO_NAMESPACES:
            errors.append(
                (
                    "interpro_namespace_mismatch",
                    f"{source_namespace!r} is not an exact InterPro/member signature namespace",
                )
            )
        if evidence.get("provider_release") != evidence.get("source_release"):
            errors.append(
                (
                    "interpro_release_mismatch",
                    "INTERPRO_MATCH provider_release must equal source_release",
                )
            )
    if method == "UNIPROT_FEATURE":
        if source != "UniProtKB":
            errors.append(
                (
                    "uniprot_source_mismatch",
                    "UNIPROT_FEATURE requires evidence_source exactly 'UniProtKB'",
                )
            )
        if evidence.get("provider_release") != evidence.get("source_release"):
            errors.append(
                (
                    "uniprot_release_mismatch",
                    "UNIPROT_FEATURE provider_release must equal source_release",
                )
            )
    if source == "ELM" or "ELM" in namespaces:
        if method != "SOURCE_NATIVE_COORDINATES":
            errors.append(
                (
                    "elm_source_method_mismatch",
                    "ELM occurrence evidence requires SOURCE_NATIVE_COORDINATES",
                )
            )
        if source != "ELM":
            errors.append(
                (
                    "elm_source_mismatch",
                    "ELM occurrence evidence requires evidence_source exactly 'ELM'",
                )
            )
        if (
            not isinstance(evidence.get("source_trait_id"), str)
            or ELM_TRAIT_RE.fullmatch(evidence["source_trait_id"]) is None
        ):
            errors.append(
                (
                    "elm_source_trait_namespace_mismatch",
                    "ELM occurrence evidence requires source_trait_id matching ELM:ELME######",
                )
            )
        if kind != "SOURCE_DATABASE":
            errors.append(
                (
                    "elm_provider_mismatch",
                    "ELM occurrence evidence requires provider_kind='SOURCE_DATABASE'",
                )
            )
        if evidence.get("provider_release") != evidence.get("source_release"):
            errors.append(
                (
                    "elm_release_mismatch",
                    "ELM provider_release must equal source_release",
                )
            )
        errors.append(
            (
                "elm_provider_receipt_required",
                "ELM evidence cannot qualify until a provider acquisition receipt is "
                "represented and verified by the grounding boundary",
            )
        )
    if source == "DisProt" or "IDPO" in namespaces:
        trait_id = evidence.get("trait_id")
        source_trait_id = evidence.get("source_trait_id")
        if method != "SOURCE_NATIVE_COORDINATES":
            errors.append(
                (
                    "disprot_source_method_mismatch",
                    "DisProt/IDPO occurrence evidence requires SOURCE_NATIVE_COORDINATES",
                )
            )
        if source != "DisProt":
            errors.append(
                (
                    "disprot_source_mismatch",
                    "DisProt/IDPO occurrence evidence requires evidence_source exactly 'DisProt'",
                )
            )
        if (
            not isinstance(trait_id, str)
            or IDPO_TRAIT_RE.fullmatch(trait_id) is None
            or not isinstance(source_trait_id, str)
            or IDPO_TRAIT_RE.fullmatch(source_trait_id) is None
            or source_trait_id != trait_id
        ):
            errors.append(
                (
                    "disprot_source_trait_mismatch",
                    "DisProt source-native evidence requires exact "
                    "trait_id == source_trait_id == IDPO:#######",
                )
            )
        if kind != "SOURCE_DATABASE":
            errors.append(
                (
                    "disprot_provider_mismatch",
                    "DisProt/IDPO occurrence evidence requires provider_kind='SOURCE_DATABASE'",
                )
            )
        if evidence.get("scope") != "LOCALIZED":
            errors.append(
                (
                    "disprot_scope_mismatch",
                    "DisProt source-native evidence requires LOCALIZED scope",
                )
            )
        if evidence.get("provider_release") != evidence.get("source_release"):
            errors.append(
                (
                    "disprot_release_mismatch",
                    "DisProt provider_release must equal source_release",
                )
            )
        errors.append(
            (
                "disprot_provider_receipt_required",
                "DisProt evidence cannot qualify until a provider acquisition receipt is "
                "represented and verified by the grounding boundary",
            )
        )
    if source == "ComplexPortal" or "ComplexPortal" in namespaces:
        trait_id = evidence.get("trait_id")
        source_trait_id = evidence.get("source_trait_id")
        if method != "SOURCE_MEMBERSHIP":
            errors.append(
                (
                    "complexportal_source_method_mismatch",
                    "ComplexPortal evidence requires SOURCE_MEMBERSHIP",
                )
            )
        if source != "ComplexPortal":
            errors.append(
                (
                    "complexportal_source_mismatch",
                    "ComplexPortal evidence requires evidence_source exactly 'ComplexPortal'",
                )
            )
        if (
            not isinstance(trait_id, str)
            or COMPLEXPORTAL_TRAIT_RE.fullmatch(trait_id) is None
            or not isinstance(source_trait_id, str)
            or COMPLEXPORTAL_TRAIT_RE.fullmatch(source_trait_id) is None
            or source_trait_id != trait_id
        ):
            errors.append(
                (
                    "complexportal_source_trait_mismatch",
                    "ComplexPortal evidence requires exact trait_id == source_trait_id "
                    "matching ComplexPortal:CPX-<positive decimal integer>",
                )
            )
        if kind != "SOURCE_DATABASE":
            errors.append(
                (
                    "complexportal_provider_mismatch",
                    "ComplexPortal evidence requires provider_kind='SOURCE_DATABASE'",
                )
            )
        if evidence.get("scope") != "WHOLE_PROTEIN":
            errors.append(
                (
                    "complexportal_scope_mismatch",
                    "ComplexPortal evidence requires WHOLE_PROTEIN scope",
                )
            )
        if evidence.get("provider_release") != evidence.get("source_release"):
            errors.append(
                (
                    "complexportal_release_mismatch",
                    "ComplexPortal provider_release must equal source_release",
                )
            )
        errors.append(
            (
                "complexportal_provider_receipt_required",
                "ComplexPortal evidence cannot qualify until a provider acquisition receipt "
                "is represented and verified by the grounding boundary",
            )
        )
    if source == "Rhea" or "RHEA" in namespaces:
        trait_id = evidence.get("trait_id")
        source_trait_id = evidence.get("source_trait_id")
        if method != "SOURCE_MEMBERSHIP":
            errors.append(
                (
                    "rhea_source_method_mismatch",
                    "Rhea evidence requires direct SOURCE_MEMBERSHIP",
                )
            )
        if source != "Rhea":
            errors.append(
                (
                    "rhea_source_mismatch",
                    "Rhea evidence requires evidence_source exactly 'Rhea'",
                )
            )
        if (
            not isinstance(trait_id, str)
            or RHEA_TRAIT_RE.fullmatch(trait_id) is None
            or not isinstance(source_trait_id, str)
            or RHEA_TRAIT_RE.fullmatch(source_trait_id) is None
            or source_trait_id != trait_id
        ):
            errors.append(
                (
                    "rhea_source_trait_mismatch",
                    "Rhea evidence requires exact trait_id == source_trait_id matching "
                    "RHEA:<positive decimal integer>",
                )
            )
        if kind != "SOURCE_DATABASE":
            errors.append(
                (
                    "rhea_provider_mismatch",
                    "Rhea evidence requires provider_kind='SOURCE_DATABASE'",
                )
            )
        if evidence.get("scope") != "WHOLE_PROTEIN":
            errors.append(
                (
                    "rhea_scope_mismatch",
                    "Rhea evidence requires WHOLE_PROTEIN scope",
                )
            )
        if (
            evidence.get("source_release") != RHEA_RELEASE
            or evidence.get("provider_release") != RHEA_RELEASE
        ):
            errors.append(
                (
                    "rhea_release_mismatch",
                    "Rhea evidence requires source_release and provider_release exactly '141'",
                )
            )
        if evidence.get("provider_source") != RHEA_PROVIDER_SOURCE:
            errors.append(
                (
                    "rhea_provider_source_mismatch",
                    "Rhea evidence requires the canonical direct "
                    "data/raw/rhea/rhea2uniprot_sprot.tsv source artifact",
                )
            )
        if evidence.get("inheritance_path") is not None:
            errors.append(
                (
                    "rhea_inheritance_mismatch",
                    "direct Rhea source membership does not permit an inheritance path",
                )
            )
        if any(
            evidence.get(field) is not None
            for field in (
                "structure_id",
                "chain_id",
                "mapping_completeness",
                "source_residue_count",
                "mapped_residue_count",
            )
        ):
            errors.append(
                (
                    "rhea_structural_provenance_mismatch",
                    "whole-protein Rhea source membership must not carry structure or residue-"
                    "mapping provenance",
                )
            )
        errors.append(
            (
                "rhea_provider_receipt_required",
                "Rhea evidence cannot qualify until the authentic release-141 provider "
                "acquisition receipt, exact mapping-row replay, verified ProteinReference "
                "fetch receipt, and receipt verifier are represented and verified by the "
                "grounding boundary",
            )
        )
    if source == "SCOPe" or namespaces & {"SCOP", "SCOPe"}:
        trait_id = evidence.get("trait_id")
        source_trait_id = evidence.get("source_trait_id")
        if method != "SIFTS_RESIDUE_MAPPING":
            errors.append(
                (
                    "scope_source_method_mismatch",
                    "SCOPe occurrence evidence requires SIFTS_RESIDUE_MAPPING",
                )
            )
        if source != "SCOPe":
            errors.append(
                (
                    "scope_source_mismatch",
                    "SCOPe occurrence evidence requires evidence_source exactly 'SCOPe'",
                )
            )
        if (
            not isinstance(trait_id, str)
            or SCOP_TRAIT_RE.fullmatch(trait_id) is None
            or not isinstance(source_trait_id, str)
            or SCOP_TRAIT_RE.fullmatch(source_trait_id) is None
        ):
            errors.append(
                (
                    "scope_trait_id_mismatch",
                    "SCOPe evidence requires trait_id and source_trait_id to independently "
                    "match SCOP:<positive decimal integer>",
                )
            )
        if kind != "SIFTS":
            errors.append(
                (
                    "scope_provider_mismatch",
                    "SCOPe occurrence evidence requires provider_kind='SIFTS'",
                )
            )
        if evidence.get("scope") != "LOCALIZED":
            errors.append(
                (
                    "scope_scope_mismatch",
                    "SCOPe occurrence evidence requires LOCALIZED scope",
                )
            )
        if evidence.get("coordinate_frame") != "UNIPROT_CANONICAL":
            errors.append(
                (
                    "scope_coordinate_frame_mismatch",
                    "SCOPe occurrence evidence requires coordinate_frame='UNIPROT_CANONICAL'",
                )
            )
        if evidence.get("source_release") != "2.08":
            errors.append(
                (
                    "scope_release_mismatch",
                    "SCOPe occurrence evidence requires source_release exactly '2.08'",
                )
            )
        errors.append(
            (
                "scope_provider_receipt_required",
                "SCOPe evidence cannot qualify until an authentic provider acquisition receipt "
                "is represented and verified by the grounding boundary",
            )
        )
    if source == "CATH" or "CATH" in namespaces:
        trait_id = evidence.get("trait_id")
        source_trait_id = evidence.get("source_trait_id")
        if (
            not isinstance(trait_id, str)
            or CATH_TRAIT_RE.fullmatch(trait_id) is None
            or not isinstance(source_trait_id, str)
            or CATH_TRAIT_RE.fullmatch(source_trait_id) is None
        ):
            errors.append(
                (
                    "cath_trait_id_mismatch",
                    "CATH evidence requires trait_id and source_trait_id to independently "
                    "match a one- to four-level CATH CURIE",
                )
            )
        if evidence.get("scope") != "LOCALIZED":
            errors.append(
                (
                    "cath_scope_mismatch",
                    "CATH occurrence evidence requires LOCALIZED scope",
                )
            )
        if evidence.get("coordinate_frame") != "UNIPROT_CANONICAL":
            errors.append(
                (
                    "cath_coordinate_frame_mismatch",
                    "CATH occurrence evidence requires coordinate_frame='UNIPROT_CANONICAL'",
                )
            )

        if method == "INTERPRO_MATCH":
            if (
                not isinstance(source_trait_id, str)
                or CATH_HOMOLOGOUS_SUPERFAMILY_TRAIT_RE.fullmatch(source_trait_id) is None
            ):
                errors.append(
                    (
                        "cath_interpro_source_trait_mismatch",
                        "CATH INTERPRO_MATCH evidence requires source_trait_id to be an exact "
                        "four-level CATH homologous-superfamily CURIE; ancestor traits require "
                        "explicit inheritance from that descendant",
                    )
                )
            if source != "InterPro":
                errors.append(
                    (
                        "cath_source_mismatch",
                        "CATH INTERPRO_MATCH evidence requires evidence_source exactly 'InterPro'",
                    )
                )
            if kind != "INTERPRO":
                errors.append(
                    (
                        "cath_provider_mismatch",
                        "CATH INTERPRO_MATCH evidence requires provider_kind='INTERPRO'",
                    )
                )
            if (
                evidence.get("source_release") != "109.0"
                or evidence.get("provider_release") != "109.0"
            ):
                errors.append(
                    (
                        "cath_release_mismatch",
                        "CATH INTERPRO_MATCH evidence requires source_release and "
                        "provider_release exactly '109.0'",
                    )
                )
        elif method == "SIFTS_RESIDUE_MAPPING":
            if source != "CATH":
                errors.append(
                    (
                        "cath_source_mismatch",
                        "native CATH evidence requires evidence_source exactly 'CATH'",
                    )
                )
            if kind != "SIFTS":
                errors.append(
                    (
                        "cath_provider_mismatch",
                        "native CATH evidence requires provider_kind='SIFTS'",
                    )
                )
            if evidence.get("source_release") != "v4.4.0":
                errors.append(
                    (
                        "cath_release_mismatch",
                        "native CATH evidence requires source_release exactly 'v4.4.0'; "
                        "the SIFTS provider release is an independent provenance axis",
                    )
                )
        else:
            errors.append(
                (
                    "cath_source_method_mismatch",
                    "CATH evidence requires INTERPRO_MATCH or SIFTS_RESIDUE_MAPPING",
                )
            )
        errors.append(
            (
                "cath_provider_receipt_required",
                "CATH evidence cannot qualify until authentic source/provider acquisition "
                "receipts are represented and verified by the grounding boundary",
            )
        )

    for lock in pending_locks:
        errors.append((lock.code, lock.message))

    detailed_lock_matched = any(
        (
            source == "ELM" or "ELM" in namespaces,
            source == "DisProt" or "IDPO" in namespaces,
            source == "ComplexPortal" or "ComplexPortal" in namespaces,
            source == "Rhea" or "RHEA" in namespaces,
            source == "SCOPe" or bool(namespaces & {"SCOP", "SCOPe"}),
            source == "CATH" or "CATH" in namespaces,
        )
    )
    if not pending_locks and not detailed_lock_matched:
        if method == "SIFTS_RESIDUE_MAPPING" or kind == "SIFTS":
            errors.append(
                (
                    "sifts_provider_receipt_required",
                    "SIFTS evidence cannot qualify until its complete acquisition manifest "
                    "and provider-entry receipt are represented and verified by the grounding "
                    "boundary",
                )
            )
        elif kind == "SOURCE_DATABASE":
            errors.append(
                (
                    "source_database_contract_required",
                    "SOURCE_DATABASE evidence cannot qualify until an exact source-specific "
                    "contract and acquisition receipt are represented and verified by the "
                    "grounding boundary",
                )
            )
    if method == "SOURCE_MEMBERSHIP" and (kind == "UNIPROT" or source == "UniProtKB"):
        if kind != "UNIPROT":
            errors.append(
                (
                    "uniprot_membership_provider_mismatch",
                    "UniProtKB SOURCE_MEMBERSHIP requires provider_kind='UNIPROT'",
                )
            )
        if source != "UniProtKB":
            errors.append(
                (
                    "uniprot_membership_source_mismatch",
                    "UNIPROT SOURCE_MEMBERSHIP requires evidence_source exactly 'UniProtKB'",
                )
            )
        if evidence.get("provider_release") != evidence.get("source_release"):
            errors.append(
                (
                    "uniprot_membership_release_mismatch",
                    "UNIPROT SOURCE_MEMBERSHIP provider_release must equal source_release",
                )
            )
        if evidence.get("scope") != "WHOLE_PROTEIN":
            errors.append(
                (
                    "uniprot_membership_scope_mismatch",
                    "UNIPROT SOURCE_MEMBERSHIP requires WHOLE_PROTEIN scope",
                )
            )
        if evidence.get("source_trait_id") != evidence.get("trait_id"):
            errors.append(
                (
                    "uniprot_membership_trait_mismatch",
                    "UNIPROT SOURCE_MEMBERSHIP requires exact source_trait_id == trait_id",
                )
            )

    # CATH may be proven by an exact InterPro/Gene3D match under the saved
    # plan. Native CATH coordinates, like every other structural source, still
    # require SIFTS. The other listed namespaces have no signature exception.
    structure_derived = (
        bool(namespaces & STRUCTURE_DERIVED_NAMESPACES)
        or evidence.get("structure_id") is not None
        or ("CATH" in namespaces and method != "INTERPRO_MATCH")
    )
    if structure_derived and method != "SIFTS_RESIDUE_MAPPING":
        errors.append(
            (
                "structure_evidence_requires_sifts",
                "structure-derived trait namespaces require SIFTS_RESIDUE_MAPPING",
            )
        )
    if structure_derived and method == "SOURCE_NATIVE_COORDINATES":
        errors.append(
            (
                "structure_native_coordinates_forbidden",
                "structure-derived source coordinates cannot be treated as UniProt coordinates",
            )
        )
    if method == "SIFTS_RESIDUE_MAPPING" or structure_derived:
        if evidence.get("provider_kind") != "SIFTS":
            errors.append(
                (
                    "sifts_provider_required",
                    "structure-derived evidence requires provider_kind='SIFTS'",
                )
            )
        for field in ("structure_id", "chain_id"):
            if not _nonempty_string(evidence.get(field)):
                errors.append(
                    (
                        "incomplete_sifts_provenance",
                        f"structure-derived evidence requires {field}",
                    )
                )
        if evidence.get("mapping_completeness") != "COMPLETE":
            errors.append(
                (
                    "incomplete_sifts_mapping",
                    "structure-derived evidence requires mapping_completeness='COMPLETE'",
                )
            )
        source_count = evidence.get("source_residue_count")
        mapped_count = evidence.get("mapped_residue_count")
        if not _is_positive_int(source_count) or not _is_positive_int(mapped_count):
            errors.append(
                (
                    "missing_sifts_counts",
                    "structure-derived evidence requires positive source and mapped residue counts",
                )
            )
        elif source_count != mapped_count:
            errors.append(
                (
                    "incomplete_sifts_mapping",
                    f"structure-derived evidence maps {mapped_count} of {source_count} residues",
                )
            )
    return errors


def validate_grounding_evidence(evidence: object, *, path: Path, line: int) -> list[Finding]:
    """Strictly validate one external GroundingEvidence object."""

    if not isinstance(evidence, dict):
        return [
            _evidence_finding(
                "evidence_not_object", "evidence-registry line must be a JSON object", path, line
            )
        ]

    findings: list[Finding] = []
    for field in EVIDENCE_REQUIRED_FIELDS:
        if field not in evidence:
            findings.append(
                _evidence_finding(
                    "evidence_missing_field",
                    f"missing required field {field!r}",
                    path,
                    line,
                    evidence,
                )
            )
    for field in sorted(set(evidence) - EVIDENCE_ALLOWED_FIELDS):
        findings.append(
            _evidence_finding(
                "evidence_unknown_field",
                f"unknown GroundingEvidence field {field!r}",
                path,
                line,
                evidence,
            )
        )

    evidence_id = evidence.get("evidence_id")
    if not isinstance(evidence_id, str) or not re.fullmatch(
        rf"{re.escape(EVIDENCE_PREFIX)}[0-9a-f]{{64}}", evidence_id
    ):
        findings.append(
            _evidence_finding(
                "invalid_evidence_id",
                "evidence_id must be ug-evidence: plus 64 lower-case hex digits",
                path,
                line,
                evidence,
            )
        )
    else:
        try:
            expected_id = compute_evidence_id(evidence)
        except (TypeError, ValueError) as error:
            findings.append(
                _evidence_finding(
                    "noncanonical_evidence_payload",
                    f"evidence payload cannot be canonicalized: {error}",
                    path,
                    line,
                    evidence,
                )
            )
        else:
            if evidence_id != expected_id:
                findings.append(
                    _evidence_finding(
                        "evidence_id_digest_mismatch",
                        f"evidence_id does not match canonical payload; expected {expected_id}",
                        path,
                        line,
                        evidence,
                    )
                )

    for field in ("trait_id", "source_trait_id"):
        value = evidence.get(field)
        if field in evidence and (not isinstance(value, str) or CURIE_RE.fullmatch(value) is None):
            findings.append(
                _evidence_finding(
                    "invalid_evidence_curie", f"{field} must be a CURIE", path, line, evidence
                )
            )
    protein_id = evidence.get("protein_id")
    if "protein_id" in evidence and (
        not isinstance(protein_id, str) or UNIPROT_RE.fullmatch(protein_id) is None
    ):
        findings.append(
            _evidence_finding(
                "invalid_evidence_protein",
                "protein_id must be an exact UniProtKB key",
                path,
                line,
                evidence,
            )
        )
    for field in ("evidence_source", "source_release", "provider_source", "provider_release"):
        if field in evidence and not _nonempty_string(evidence.get(field)):
            findings.append(
                _evidence_finding(
                    "invalid_evidence_field",
                    f"{field} must be a non-empty string",
                    path,
                    line,
                    evidence,
                )
            )
    for field in ("sequence_sha256", "provider_entry_sha256"):
        value = evidence.get(field)
        if field in evidence and (not isinstance(value, str) or SHA256_RE.fullmatch(value) is None):
            code = (
                "invalid_provider_entry_digest"
                if field == "provider_entry_sha256"
                else "invalid_evidence_sequence_digest"
            )
            findings.append(
                _evidence_finding(
                    code, f"{field} must be 64 lower-case hex digits", path, line, evidence
                )
            )
    if "provider_kind" in evidence and evidence.get("provider_kind") not in EVIDENCE_PROVIDER_KINDS:
        findings.append(
            _evidence_finding(
                "invalid_evidence_provider_kind",
                f"provider_kind must be one of {sorted(EVIDENCE_PROVIDER_KINDS)}",
                path,
                line,
                evidence,
            )
        )

    method = evidence.get("mapping_method")
    known_methods = WHOLE_PROTEIN_METHODS | LOCALIZED_METHODS
    if "mapping_method" in evidence and method not in known_methods:
        findings.append(
            _evidence_finding(
                "invalid_evidence_mapping_method",
                f"mapping_method must be one of {sorted(known_methods)}",
                path,
                line,
                evidence,
            )
        )
    scope = evidence.get("scope")
    if "scope" in evidence and scope not in {"LOCALIZED", "WHOLE_PROTEIN"}:
        findings.append(
            _evidence_finding(
                "invalid_evidence_scope",
                "scope must be LOCALIZED or WHOLE_PROTEIN",
                path,
                line,
                evidence,
            )
        )
    frame = evidence.get("coordinate_frame")
    if frame is not None and frame not in {"UNIPROT_CANONICAL", "UNIPROT_ISOFORM"}:
        findings.append(
            _evidence_finding(
                "invalid_evidence_coordinate_frame",
                "coordinate_frame must be UNIPROT_CANONICAL or UNIPROT_ISOFORM",
                path,
                line,
                evidence,
            )
        )
    inheritance = evidence.get("inheritance_path")
    if inheritance is not None:
        if (
            not isinstance(inheritance, list)
            or any(
                not isinstance(item, str) or CURIE_RE.fullmatch(item) is None
                for item in inheritance
            )
            or len(inheritance) != len(set(inheritance))
        ):
            findings.append(
                _evidence_finding(
                    "invalid_evidence_inheritance_path",
                    "inheritance_path must contain unique CURIEs",
                    path,
                    line,
                    evidence,
                )
            )
        elif evidence.get("source_trait_id") != evidence.get("trait_id") and not (
            len(inheritance) >= 2
            and inheritance[0] == evidence.get("source_trait_id")
            and inheritance[-1] == evidence.get("trait_id")
        ):
            findings.append(
                _evidence_finding(
                    "invalid_evidence_inheritance_path",
                    "inheritance_path endpoints must be source_trait_id and trait_id",
                    path,
                    line,
                    evidence,
                )
            )
    elif evidence.get("source_trait_id") != evidence.get("trait_id"):
        findings.append(
            _evidence_finding(
                "evidence_missing_inheritance_path",
                "different source_trait_id and trait_id require inheritance_path",
                path,
                line,
                evidence,
            )
        )

    intervals = evidence.get("intervals")
    if intervals is not None:
        if not isinstance(intervals, list) or not intervals:
            findings.append(
                _evidence_finding(
                    "invalid_evidence_intervals",
                    "intervals must be a non-empty list",
                    path,
                    line,
                    evidence,
                )
            )
        else:
            previous_end = 0
            for index, interval in enumerate(intervals):
                if not isinstance(interval, dict):
                    findings.append(
                        _evidence_finding(
                            "invalid_evidence_interval",
                            f"interval {index} is not an object",
                            path,
                            line,
                            evidence,
                        )
                    )
                    continue
                unknown = set(interval) - {"start", "end", "expected_sequence"}
                if unknown:
                    findings.append(
                        _evidence_finding(
                            "evidence_unknown_interval_field",
                            f"interval {index} has unknown fields {sorted(unknown)}",
                            path,
                            line,
                            evidence,
                        )
                    )
                if not _is_positive_int(interval.get("start")) or not _is_positive_int(
                    interval.get("end")
                ):
                    findings.append(
                        _evidence_finding(
                            "invalid_evidence_interval",
                            f"interval {index} requires positive integer start/end",
                            path,
                            line,
                            evidence,
                        )
                    )
                elif interval["start"] > interval["end"]:
                    findings.append(
                        _evidence_finding(
                            "invalid_evidence_interval",
                            f"interval {index} has start greater than end",
                            path,
                            line,
                            evidence,
                        )
                    )
                elif interval["start"] <= previous_end:
                    findings.append(
                        _evidence_finding(
                            "invalid_evidence_interval_order",
                            "evidence intervals must be ordered and non-overlapping",
                            path,
                            line,
                            evidence,
                        )
                    )
                else:
                    previous_end = interval["end"]
                expected_sequence = interval.get("expected_sequence")
                if expected_sequence is not None and (
                    not isinstance(expected_sequence, str)
                    or SEQUENCE_RE.fullmatch(expected_sequence) is None
                ):
                    findings.append(
                        _evidence_finding(
                            "invalid_evidence_interval_sequence",
                            f"interval {index} expected_sequence is invalid",
                            path,
                            line,
                            evidence,
                        )
                    )
    positions = evidence.get("residue_positions")
    if positions is not None and (
        not isinstance(positions, list)
        or not positions
        or any(not _is_positive_int(position) for position in positions)
        or positions != sorted(set(positions))
    ):
        findings.append(
            _evidence_finding(
                "invalid_evidence_positions",
                "residue_positions must be non-empty, positive, strictly increasing, and unique",
                path,
                line,
                evidence,
            )
        )
    expected_residues = evidence.get("expected_residues")
    if expected_residues is not None and (
        not isinstance(expected_residues, str)
        or SEQUENCE_RE.fullmatch(expected_residues) is None
        or not isinstance(positions, list)
        or len(expected_residues) != len(positions)
    ):
        findings.append(
            _evidence_finding(
                "invalid_evidence_expected_residues",
                "expected_residues must be valid and align one-for-one with residue_positions",
                path,
                line,
                evidence,
            )
        )

    if scope == "WHOLE_PROTEIN":
        if any(
            evidence.get(field) is not None
            for field in ("coordinate_frame", "intervals", "residue_positions", "expected_residues")
        ):
            findings.append(
                _evidence_finding(
                    "whole_protein_evidence_has_coordinates",
                    "WHOLE_PROTEIN evidence must omit coordinate and residue fields",
                    path,
                    line,
                    evidence,
                )
            )
        if method not in WHOLE_PROTEIN_METHODS:
            findings.append(
                _evidence_finding(
                    "invalid_whole_protein_evidence_method",
                    f"{method!r} cannot support WHOLE_PROTEIN evidence",
                    path,
                    line,
                    evidence,
                )
            )
    elif scope == "LOCALIZED":
        if frame is None:
            findings.append(
                _evidence_finding(
                    "localized_evidence_without_frame",
                    "LOCALIZED evidence requires coordinate_frame",
                    path,
                    line,
                    evidence,
                )
            )
        if intervals is None and positions is None:
            findings.append(
                _evidence_finding(
                    "localized_evidence_without_coordinates",
                    "LOCALIZED evidence requires intervals and/or residue_positions",
                    path,
                    line,
                    evidence,
                )
            )
        if method not in LOCALIZED_METHODS:
            findings.append(
                _evidence_finding(
                    "invalid_localized_evidence_method",
                    f"{method!r} cannot support LOCALIZED evidence",
                    path,
                    line,
                    evidence,
                )
            )

    structure_id = evidence.get("structure_id")
    if structure_id is not None and (
        not isinstance(structure_id, str) or CURIE_RE.fullmatch(structure_id) is None
    ):
        findings.append(
            _evidence_finding(
                "invalid_evidence_structure_id",
                "structure_id must be a CURIE",
                path,
                line,
                evidence,
            )
        )
    if evidence.get("chain_id") is not None and not _nonempty_string(evidence.get("chain_id")):
        findings.append(
            _evidence_finding(
                "invalid_evidence_chain_id",
                "chain_id must be a non-empty string",
                path,
                line,
                evidence,
            )
        )
    completeness = evidence.get("mapping_completeness")
    if completeness is not None and completeness not in {"NOT_APPLICABLE", "COMPLETE", "PARTIAL"}:
        findings.append(
            _evidence_finding(
                "invalid_evidence_mapping_completeness",
                "mapping_completeness is not recognized",
                path,
                line,
                evidence,
            )
        )
    for field in ("source_residue_count", "mapped_residue_count"):
        if (
            field in evidence
            and evidence[field] is not None
            and not _is_positive_int(evidence[field])
        ):
            findings.append(
                _evidence_finding(
                    "invalid_evidence_residue_count",
                    f"{field} must be a positive integer",
                    path,
                    line,
                    evidence,
                )
            )

    for code, message in _provider_contract_errors(evidence):
        findings.append(_evidence_finding(code, message, path, line, evidence))
    return findings


def load_evidence_registry(
    path: Path,
) -> tuple[dict[str, dict[str, Any]], list[Finding]]:
    """Load a strict, content-addressed GroundingEvidence JSONL registry.

    Invalid rows are rejected from the returned mapping; callers can never
    dereference an object with unknown/missing fields or a bad digest.
    """

    registry: dict[str, dict[str, Any]] = {}
    findings: list[Finding] = []
    if not path.is_file():
        return registry, [
            _evidence_finding(
                "evidence_registry_not_found", "evidence registry does not exist", path, 0
            )
        ]
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                value = json.loads(
                    raw,
                    parse_constant=lambda token: (_ for _ in ()).throw(
                        ValueError(f"non-finite JSON value {token}")
                    ),
                )
            except (json.JSONDecodeError, ValueError) as error:
                findings.append(
                    _evidence_finding(
                        "evidence_json_error", f"invalid JSON: {error}", path, line_number
                    )
                )
                continue
            row_findings = validate_grounding_evidence(value, path=path, line=line_number)
            findings.extend(row_findings)
            if row_findings or not isinstance(value, dict):
                continue
            evidence_id = value["evidence_id"]
            if evidence_id in registry:
                findings.append(
                    _evidence_finding(
                        "duplicate_evidence_key",
                        f"duplicate evidence_id; first occurrence retained: {evidence_id}",
                        path,
                        line_number,
                        value,
                    )
                )
                continue
            registry[evidence_id] = value
    return registry, findings


def load_membership_registry(
    path: Path,
) -> tuple[list[dict[str, Any]], list[Finding]]:
    """Strictly load the content-addressed UniProt membership provider snapshot."""

    if not path.is_file():
        return [], [
            _finding(
                "membership_registry_not_found",
                "UniProt membership registry does not exist",
                file=str(path),
            )
        ]
    try:
        from uniprot_membership_snapshot import (
            MembershipSnapshotError,
            load_memberships,
        )

        return load_memberships(path), []
    except (MembershipSnapshotError, OSError) as error:
        return [], [
            _finding(
                "membership_registry_invalid",
                f"invalid UniProt membership registry: {error}",
                file=str(path),
            )
        ]


def _qualified_membership_uses(value: object, *, file: str) -> list[MembershipUse]:
    """Collect qualified UniProt membership claims without trusting their evidence."""

    if not isinstance(value, Mapping):
        return []
    trait_id = str(value.get("identifier") or "")
    examples = value.get("canonical_examples")
    if not isinstance(examples, list):
        return []
    uses: list[MembershipUse] = []
    for example_index, example in enumerate(examples):
        if not isinstance(example, Mapping):
            continue
        protein_id = str(example.get("protein_id") or "")
        occurrences = example.get("trait_occurrences")
        if not isinstance(occurrences, list):
            continue
        for occurrence_index, occurrence in enumerate(occurrences):
            if not isinstance(occurrence, Mapping):
                continue
            if occurrence.get("qualification_status") != QUALIFIED:
                continue
            if occurrence.get("mapping_method") != "SOURCE_MEMBERSHIP":
                continue
            uses.append(
                MembershipUse(
                    file=file,
                    trait_id=trait_id,
                    protein_id=protein_id,
                    example_index=example_index,
                    occurrence_index=occurrence_index,
                    evidence_id=str(occurrence.get("source_evidence_id") or ""),
                    evidence_source=str(occurrence.get("evidence_source") or ""),
                )
            )
    return uses


def _provider_source_path(value: object) -> Path | None:
    if not _nonempty_string(value):
        return None
    path = Path(str(value))
    return (path if path.is_absolute() else ROOT / path).resolve()


def validate_membership_replay(
    uses: Sequence[MembershipUse],
    evidence_registry: Mapping[str, Mapping[str, Any]],
    memberships: Sequence[Mapping[str, Any]],
    *,
    membership_path: Path,
) -> list[Finding]:
    """Replay each qualified UniProt membership claim against one exact provider fact."""

    from uniprot_membership_snapshot import (
        MembershipSnapshotError,
        find_exact_membership,
        membership_entry_sha256,
    )

    findings: list[Finding] = []
    expected_provider_path = membership_path.resolve()
    for use in uses:
        context = {
            "file": use.file,
            "trait_id": use.trait_id,
            "protein_id": use.protein_id,
            "example_index": use.example_index,
            "occurrence_index": use.occurrence_index,
        }
        evidence = evidence_registry.get(use.evidence_id)
        if not isinstance(evidence, Mapping):
            # The ordinary evidence dereference reports the missing or malformed row.
            continue
        if evidence.get("mapping_method") != "SOURCE_MEMBERSHIP":
            continue
        is_uniprot = (
            evidence.get("provider_kind") == "UNIPROT"
            or evidence.get("evidence_source") == "UniProtKB"
            or use.evidence_source == "UniProtKB"
        )
        if not is_uniprot:
            continue
        observed_provider_path = _provider_source_path(evidence.get("provider_source"))
        if observed_provider_path != expected_provider_path:
            findings.append(
                _finding(
                    "membership_provider_source_mismatch",
                    "GroundingEvidence provider_source does not name the validated "
                    "UniProt membership registry",
                    **context,
                )
            )
        try:
            membership = find_exact_membership(
                memberships,
                protein_id=str(evidence.get("protein_id") or ""),
                source_trait_id=str(evidence.get("source_trait_id") or ""),
                uniprot_release=str(evidence.get("provider_release") or ""),
                sequence_sha256=str(evidence.get("sequence_sha256") or ""),
            )
        except MembershipSnapshotError as error:
            findings.append(
                _finding(
                    "ambiguous_uniprot_membership",
                    f"exact UniProt membership lookup is ambiguous: {error}",
                    **context,
                )
            )
            continue
        if membership is None:
            findings.append(
                _finding(
                    "exact_uniprot_membership_not_found",
                    "no membership row matches the exact protein, source trait, provider "
                    "release, and sequence checksum",
                    **context,
                )
            )
            continue
        observed_digest = membership_entry_sha256(membership)
        if evidence.get("provider_entry_sha256") != observed_digest:
            findings.append(
                _finding(
                    "membership_provider_entry_mismatch",
                    "GroundingEvidence provider_entry_sha256 does not match the exact "
                    "UniProt membership row",
                    **context,
                )
            )
    return findings


def build_hierarchy_index(
    paths: Iterable[Path],
) -> tuple[dict[str, frozenset[str]], list[Finding]]:
    """Build an authoritative child-to-direct-parent index from trait YAML.

    Every claimed inheritance step must correspond to one explicit
    ``parent_traits`` edge. Duplicate record identifiers make the index
    ambiguous and are reported rather than silently merged.
    """

    hierarchy: dict[str, frozenset[str]] = {}
    findings: list[Finding] = []
    for path in iter_yaml_files(paths):
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            findings.append(
                _finding("hierarchy_yaml_error", str(error).splitlines()[0], file=str(path))
            )
            continue
        if not isinstance(value, dict):
            findings.append(
                _finding(
                    "hierarchy_record_not_object",
                    "trait hierarchy input must parse to an object",
                    file=str(path),
                )
            )
            continue
        trait_id = value.get("identifier")
        if not isinstance(trait_id, str) or CURIE_RE.fullmatch(trait_id) is None:
            findings.append(
                _finding(
                    "hierarchy_invalid_trait_id",
                    "trait hierarchy record lacks a valid identifier",
                    file=str(path),
                )
            )
            continue
        if trait_id in hierarchy:
            findings.append(
                _finding(
                    "hierarchy_duplicate_trait_id",
                    f"duplicate authoritative hierarchy record for {trait_id}",
                    file=str(path),
                    trait_id=trait_id,
                )
            )
            continue
        parents = value.get("parent_traits", [])
        if parents is None:
            parents = []
        if not isinstance(parents, list) or any(
            not isinstance(parent, str) or CURIE_RE.fullmatch(parent) is None for parent in parents
        ):
            findings.append(
                _finding(
                    "hierarchy_invalid_parents",
                    "parent_traits must be a list of CURIEs",
                    file=str(path),
                    trait_id=trait_id,
                )
            )
            continue
        hierarchy[trait_id] = frozenset(parents)
    return hierarchy, findings


def _validate_trait_inheritance(
    source_trait_id: object,
    trait_id: object,
    inheritance: object,
    hierarchy_index: Mapping[str, Iterable[str]] | None,
    context: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    source_valid = (
        isinstance(source_trait_id, str) and CURIE_RE.fullmatch(source_trait_id) is not None
    )
    if not source_valid:
        findings.append(
            _finding("invalid_source_trait_id", "source_trait_id must be a CURIE", **context)
        )
    path_valid = inheritance is None or (
        isinstance(inheritance, list)
        and all(
            isinstance(value, str) and CURIE_RE.fullmatch(value) is not None
            for value in inheritance
        )
    )
    if not path_valid:
        findings.append(
            _finding(
                "invalid_trait_inheritance_path",
                "every inheritance_path value must be a CURIE",
                **context,
            )
        )
        return findings
    if isinstance(inheritance, list) and len(inheritance) != len(set(inheritance)):
        findings.append(
            _finding(
                "cyclic_trait_inheritance", "inheritance_path must not repeat a CURIE", **context
            )
        )
        return findings

    if source_trait_id == trait_id:
        if inheritance not in (None, [], [trait_id]):
            findings.append(
                _finding(
                    "unexpected_trait_inheritance_path",
                    "identical source and record traits may only omit the path or use a singleton",
                    **context,
                )
            )
        return findings

    if not (
        isinstance(inheritance, list)
        and len(inheritance) >= 2
        and inheritance[0] == source_trait_id
        and inheritance[-1] == trait_id
    ):
        findings.append(
            _finding(
                "undocumented_trait_inheritance",
                "source_trait_id differs from record trait_id without an inclusive "
                "source-descendant to record-ancestor inheritance_path",
                **context,
            )
        )
        return findings
    if hierarchy_index is None:
        findings.append(
            _finding(
                "inheritance_hierarchy_unavailable",
                "cannot qualify inheritance without an authoritative trait hierarchy index",
                **context,
            )
        )
        return findings
    for child, parent in zip(inheritance, inheritance[1:]):
        authoritative_parents = set(hierarchy_index.get(child, ()))
        if parent not in authoritative_parents:
            findings.append(
                _finding(
                    "unproven_trait_inheritance_edge",
                    f"authoritative hierarchy has no direct edge {child} -> {parent}",
                    **context,
                )
            )
    return findings


def _prosite_atom(atom: str) -> str | None:
    """Translate one PROSITE-pattern atom to regex, or return None if unsupported."""

    repeat = ""
    match = re.fullmatch(r"(.+?)\(([0-9]+)(?:,([0-9]+))?\)", atom)
    if match:
        atom = match.group(1)
        low, high = match.group(2), match.group(3)
        repeat = "{" + low + ("," + high if high is not None else "") + "}"
    if atom in {"x", "X"}:
        base = "[ACDEFGHIKLMNPQRSTVWYUOBZJX*]"
    elif re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYUOBZJX*]", atom, re.I):
        base = re.escape(atom.upper())
    elif re.fullmatch(r"\[[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+\]", atom, re.I):
        base = atom.upper()
    elif re.fullmatch(r"\{[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+\}", atom, re.I):
        base = "[^" + atom[1:-1].upper() + "]"
    else:
        return None
    return base + repeat


def compile_sequence_pattern(pattern: object) -> tuple[re.Pattern[str] | None, str | None]:
    """Compile a literal, ``regex:`` or common PROSITE pattern for exact matching."""

    if not isinstance(pattern, str) or not pattern.strip():
        return None, "sequence_pattern is not a non-empty string"
    value = pattern.strip()
    if value.lower().startswith("regex:"):
        expression = value.split(":", 1)[1]
        try:
            return re.compile(rf"^(?:{expression})$"), None
        except re.error as error:
            return None, f"invalid regex sequence_pattern: {error}"

    # PROSITE records conventionally end the pattern with a full stop.
    if value.endswith("."):
        value = value[:-1]
    if SEQUENCE_RE.fullmatch(value):
        return re.compile(rf"^{re.escape(value)}$"), None

    start_anchor = value.startswith("<")
    end_anchor = value.endswith(">")
    value = value.removeprefix("<").removesuffix(">")
    translated: list[str] = []
    for atom in value.split("-"):
        part = _prosite_atom(atom)
        if part is None:
            return None, f"unsupported PROSITE atom {atom!r}"
        translated.append(part)
    prefix = r"\A" if start_anchor else "^"
    suffix = r"\Z" if end_anchor else "$"
    try:
        return re.compile(prefix + "".join(translated) + suffix), None
    except re.error as error:  # defensive: atoms above should already be safe
        return None, f"invalid translated sequence_pattern: {error}"


def compile_elm_sequence_pattern(pattern: object) -> tuple[re.Pattern[str] | None, str | None]:
    """Compile ELM's source-native Python-compatible regular-expression syntax.

    ELM class records predate this validator and store the expression without
    the generic ``regex:`` discriminator.  This compiler is selected only for
    an exact ``ELM:`` trait identity.  Callers must evaluate it against the
    complete resolved protein at the source start coordinate so ``^`` and ``$``
    retain their biological N/C-terminal meaning.
    """

    if not isinstance(pattern, str) or not pattern.strip():
        return None, "ELM sequence_pattern is not a non-empty string"
    try:
        return re.compile(pattern), None
    except re.error as error:
        return None, f"invalid ELM regex sequence_pattern: {error}"


def elm_pattern_matches_exact_span(
    compiled: re.Pattern[str], sequence: str, start: object, end: object
) -> bool:
    r"""Match an ELM expression at one exact endpoint in the complete protein.

    A plain ``Pattern.match`` commits to the regex engine's preferred greedy
    endpoint.  The source annotation can nevertheless be a valid shorter
    backtracking solution.  The appended lookahead constrains the endpoint
    against the real full-sequence ``\Z`` without turning a mid-protein source
    interval into an artificial string end for an ELM ``$`` anchor.
    """

    if (
        not _is_positive_int(start)
        or not _is_positive_int(end)
        or start > end
        or end > len(sequence)
    ):
        return False
    remaining = len(sequence) - end
    try:
        endpoint_constrained = re.compile(
            rf"(?:{compiled.pattern})(?=[\s\S]{{{remaining}}}\Z)", compiled.flags
        )
    except re.error:
        return False
    match = endpoint_constrained.match(sequence, start - 1)
    return match is not None and match.start() == start - 1 and match.end() == end


def _elm_pattern_matches_exact_interval(
    compiled: re.Pattern[str], occurrence: Mapping[str, Any], sequence: str
) -> bool:
    """Return whether one ELM expression consumes the exact source interval.

    ``Pattern.fullmatch(sequence[start-1:end])`` is intentionally not used:
    it would make a ``$``-anchored C-terminal motif appear valid in the middle
    of a precursor.  Matching at ``pos`` against the complete protein preserves
    anchors and any future zero-width context while still requiring the exact
    one-based closed ELM span.
    """

    intervals = occurrence.get("intervals")
    if not isinstance(intervals, list) or len(intervals) != 1:
        return False
    interval = intervals[0]
    if not isinstance(interval, Mapping):
        return False
    start, end = interval.get("start"), interval.get("end")
    return elm_pattern_matches_exact_span(compiled, sequence, start, end)


def _whole_protein_allowed(record: Mapping[str, Any]) -> bool:
    axis = record.get("trait_axis")
    category = record.get("trait_category")
    return axis in {"FUNCTION", "EVOLUTION"} or category in WHOLE_PROTEIN_SEQUENCE_CATEGORIES


def _localized_fragments(occurrence: Mapping[str, Any], sequence: str) -> tuple[list[str], int]:
    """Return exact localized strings and coordinate cardinality after bounds checks."""

    fragments: list[str] = []
    intervals = occurrence.get("intervals")
    if isinstance(intervals, list):
        interval_fragments: list[str] = []
        for interval in intervals:
            if not isinstance(interval, dict):
                continue
            start, end = interval.get("start"), interval.get("end")
            if _is_positive_int(start) and _is_positive_int(end) and start <= end <= len(sequence):
                fragment = sequence[start - 1 : end]
                interval_fragments.append(fragment)
                fragments.append(fragment)
        if len(interval_fragments) > 1:
            fragments.append("".join(interval_fragments))
    positions = occurrence.get("residue_positions")
    if (
        isinstance(positions, list)
        and positions
        and all(_is_positive_int(position) and position <= len(sequence) for position in positions)
    ):
        fragments.append("".join(sequence[position - 1] for position in positions))
        return fragments, len(positions)
    cardinality = 0
    if isinstance(intervals, list):
        for interval in intervals:
            if not isinstance(interval, dict):
                continue
            start, end = interval.get("start"), interval.get("end")
            if _is_positive_int(start) and _is_positive_int(end) and start <= end <= len(sequence):
                cardinality += end - start + 1
    return fragments, cardinality


def _validate_intervals(
    occurrence: Mapping[str, Any], sequence: str, context: dict[str, Any]
) -> list[Finding]:
    findings: list[Finding] = []
    intervals = occurrence.get("intervals")
    if intervals is None:
        return findings
    if not isinstance(intervals, list) or not intervals:
        return [
            _finding(
                "invalid_intervals", "intervals must be a non-empty list when present", **context
            )
        ]
    previous_end = 0
    for index, interval in enumerate(intervals):
        if not isinstance(interval, dict):
            findings.append(
                _finding("invalid_interval", f"interval {index} is not an object", **context)
            )
            continue
        start, end = interval.get("start"), interval.get("end")
        if not _is_positive_int(start) or not _is_positive_int(end):
            findings.append(
                _finding(
                    "invalid_interval",
                    f"interval {index} start/end must be positive integers",
                    **context,
                )
            )
            continue
        if start > end:
            findings.append(
                _finding(
                    "reversed_interval",
                    f"interval {index} has start={start} > end={end}",
                    **context,
                )
            )
            continue
        if end > len(sequence):
            findings.append(
                _finding(
                    "coordinate_out_of_bounds",
                    f"interval {index} ends at {end}, beyond sequence length {len(sequence)}",
                    **context,
                )
            )
            continue
        if start <= previous_end:
            findings.append(
                _finding(
                    "overlapping_or_unsorted_intervals",
                    f"interval {index} starts at {start}, not after previous end {previous_end}",
                    **context,
                )
            )
        previous_end = end
        expected = interval.get("expected_sequence")
        if expected is not None and expected != sequence[start - 1 : end]:
            findings.append(
                _finding(
                    "interval_sequence_mismatch",
                    f"interval {index} expected_sequence does not match registry sequence",
                    **context,
                )
            )
    return findings


def _validate_positions(
    occurrence: Mapping[str, Any], sequence: str, context: dict[str, Any]
) -> list[Finding]:
    findings: list[Finding] = []
    positions = occurrence.get("residue_positions")
    expected = occurrence.get("expected_residues")
    if positions is None:
        if expected is not None:
            findings.append(
                _finding(
                    "expected_residues_without_positions",
                    "expected_residues requires residue_positions",
                    **context,
                )
            )
        return findings
    if not isinstance(positions, list) or not positions:
        return [
            _finding(
                "invalid_residue_positions",
                "residue_positions must be a non-empty list when present",
                **context,
            )
        ]
    valid = True
    for position in positions:
        if not _is_positive_int(position):
            valid = False
            findings.append(
                _finding(
                    "invalid_residue_position", f"invalid residue position {position!r}", **context
                )
            )
        elif position > len(sequence):
            valid = False
            findings.append(
                _finding(
                    "coordinate_out_of_bounds",
                    f"residue position {position} exceeds sequence length {len(sequence)}",
                    **context,
                )
            )
    if all(_is_positive_int(position) for position in positions):
        if positions != sorted(set(positions)):
            findings.append(
                _finding(
                    "unsorted_or_duplicate_positions",
                    "residue_positions must be strictly increasing and unique",
                    **context,
                )
            )
    if expected is not None:
        if not isinstance(expected, str) or SEQUENCE_RE.fullmatch(expected) is None:
            findings.append(
                _finding(
                    "invalid_expected_residues",
                    "expected_residues must be an uppercase amino-acid string",
                    **context,
                )
            )
        elif len(expected) != len(positions):
            findings.append(
                _finding(
                    "expected_residue_count_mismatch",
                    "expected_residues length must equal residue_positions length",
                    **context,
                )
            )
        elif valid:
            observed = "".join(sequence[position - 1] for position in positions)
            if expected != observed:
                findings.append(
                    _finding(
                        "expected_residue_mismatch",
                        f"expected_residues={expected!r}, observed={observed!r}",
                        **context,
                    )
                )
    return findings


def _validate_sifts(
    occurrence: Mapping[str, Any], sequence: str, context: dict[str, Any]
) -> list[Finding]:
    findings: list[Finding] = []
    method = occurrence.get("mapping_method")
    structure_id = occurrence.get("structure_id")
    is_pdb = isinstance(structure_id, str) and structure_id.upper().startswith("PDB:")
    if is_pdb and method != "SIFTS_RESIDUE_MAPPING":
        findings.append(
            _finding(
                "pdb_mapping_without_sifts",
                "PDB-derived occurrence must use SIFTS_RESIDUE_MAPPING",
                **context,
            )
        )
    if occurrence.get("mapping_completeness") == "PARTIAL":
        findings.append(
            _finding(
                "partial_mapping_cannot_qualify",
                "a partial residue mapping cannot be QUALIFIED",
                **context,
            )
        )
    if method != "SIFTS_RESIDUE_MAPPING":
        return findings
    for field in ("structure_id", "chain_id"):
        if not _nonempty_string(occurrence.get(field)):
            findings.append(
                _finding(
                    "incomplete_sifts_provenance", f"SIFTS mapping requires {field}", **context
                )
            )
    if occurrence.get("mapping_completeness") != "COMPLETE":
        findings.append(
            _finding(
                "incomplete_sifts_mapping",
                "SIFTS mapping requires mapping_completeness=COMPLETE",
                **context,
            )
        )
    source_count = occurrence.get("source_residue_count")
    mapped_count = occurrence.get("mapped_residue_count")
    if not _is_positive_int(source_count) or not _is_positive_int(mapped_count):
        findings.append(
            _finding(
                "missing_sifts_counts",
                "SIFTS mapping requires positive source_residue_count and mapped_residue_count",
                **context,
            )
        )
    elif source_count != mapped_count:
        findings.append(
            _finding(
                "incomplete_sifts_mapping",
                f"mapped {mapped_count} of {source_count} trait-defining residues",
                **context,
            )
        )
    _, cardinality = _localized_fragments(occurrence, sequence)
    if _is_positive_int(mapped_count) and cardinality and mapped_count != cardinality:
        findings.append(
            _finding(
                "sifts_coordinate_count_mismatch",
                f"mapped_residue_count={mapped_count}, UniProt coordinate cardinality={cardinality}",
                **context,
            )
        )
    return findings


def _validate_occurrence_evidence(
    occurrence: Mapping[str, Any],
    evidence_registry: Mapping[str, Mapping[str, Any]] | None,
    context: dict[str, Any],
) -> list[Finding]:
    """Dereference and exactly compare immutable evidence for a QUALIFIED claim."""

    evidence_id = occurrence.get("source_evidence_id")
    if not isinstance(evidence_id, str) or not re.fullmatch(
        rf"{re.escape(EVIDENCE_PREFIX)}[0-9a-f]{{64}}", evidence_id
    ):
        return [
            _finding(
                "qualified_occurrence_without_evidence",
                "QUALIFIED occurrence requires a valid source_evidence_id",
                **context,
            )
        ]
    if evidence_registry is None:
        return [
            _finding(
                "evidence_registry_unavailable",
                "cannot dereference source_evidence_id without an evidence registry",
                **context,
            )
        ]
    evidence = evidence_registry.get(evidence_id)
    if not isinstance(evidence, Mapping):
        return [
            _finding(
                "unknown_source_evidence",
                f"source_evidence_id {evidence_id!r} is absent from the evidence registry",
                **context,
            )
        ]
    findings: list[Finding] = []
    if evidence.get("evidence_id") != evidence_id:
        findings.append(
            _finding(
                "evidence_registry_key_mismatch",
                "evidence registry key does not equal the object's evidence_id",
                **context,
            )
        )
    # Do not let programmatic callers bypass the JSONL loader's strictness.
    # Revalidate the dereferenced object, then rewrite its location onto the
    # record occurrence so all findings remain actionable in the trait file.
    strict_findings = validate_grounding_evidence(
        dict(evidence), path=Path(str(context["file"])), line=0
    )
    findings.extend(
        _finding(finding.code, finding.message, **context) for finding in strict_findings
    )
    mismatched = [
        field
        for field in OCCURRENCE_EVIDENCE_FIELDS
        if occurrence.get(field) != evidence.get(field)
    ]
    if mismatched:
        findings.append(
            _finding(
                "occurrence_evidence_mismatch",
                "occurrence differs from source evidence in: " + ", ".join(mismatched),
                **context,
            )
        )
    return findings


def _validate_occurrence(
    occurrence: object,
    *,
    record: Mapping[str, Any],
    example: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
    evidence_registry: Mapping[str, Mapping[str, Any]] | None,
    hierarchy_index: Mapping[str, Iterable[str]] | None,
    file: str,
    example_index: int,
    occurrence_index: int,
) -> list[Finding]:
    trait_id = record.get("identifier", "")
    protein_id = example.get("protein_id", "")
    context = {
        "file": file,
        "trait_id": trait_id,
        "protein_id": protein_id,
        "example_index": example_index,
        "occurrence_index": occurrence_index,
    }
    if not isinstance(occurrence, dict):
        return [_finding("occurrence_not_object", "trait occurrence must be an object", **context)]

    findings: list[Finding] = []
    status = occurrence.get("qualification_status")
    if status != QUALIFIED:
        findings.append(
            _finding(
                "unqualified_occurrence_in_canonical_example",
                f"canonical occurrence has status {status!r}; candidates belong in the ledger",
                **context,
            )
        )
    for field in (
        "trait_id",
        "protein_id",
        "scope",
        "source_trait_id",
        "mapping_method",
        "evidence_source",
        "source_release",
        "source_evidence_id",
        "sequence_sha256",
        "qualification_status",
    ):
        if field not in occurrence:
            findings.append(
                _finding("occurrence_missing_field", f"occurrence is missing {field!r}", **context)
            )

    if occurrence.get("trait_id") != trait_id:
        findings.append(
            _finding(
                "trait_id_mismatch",
                f"occurrence trait_id={occurrence.get('trait_id')!r}, record identifier={trait_id!r}",
                **context,
            )
        )
    if occurrence.get("protein_id") != protein_id:
        findings.append(
            _finding(
                "occurrence_protein_mismatch",
                "occurrence protein_id must equal containing example protein_id",
                **context,
            )
        )

    findings.extend(
        _validate_trait_inheritance(
            occurrence.get("source_trait_id"),
            trait_id,
            occurrence.get("inheritance_path"),
            hierarchy_index,
            context,
        )
    )

    for field in ("evidence_source", "source_release"):
        if not _nonempty_string(occurrence.get(field)):
            findings.append(
                _finding(
                    "missing_occurrence_provenance",
                    f"QUALIFIED occurrence requires non-empty {field}",
                    **context,
                )
            )

    if status == QUALIFIED:
        findings.extend(_validate_occurrence_evidence(occurrence, evidence_registry, context))

    if reference is None:
        return findings
    sequence = reference.get("sequence")
    if not isinstance(sequence, str) or SEQUENCE_RE.fullmatch(sequence) is None:
        return findings  # the registry-level error is more useful; avoid follow-on crashes
    if occurrence.get("sequence_sha256") != reference.get("sequence_sha256"):
        findings.append(
            _finding(
                "occurrence_checksum_mismatch",
                "occurrence sequence_sha256 does not match ProteinReference",
                **context,
            )
        )

    scope = occurrence.get("scope")
    coordinate_frame = occurrence.get("coordinate_frame")
    intervals = occurrence.get("intervals")
    positions = occurrence.get("residue_positions")
    method = occurrence.get("mapping_method")
    if scope == "WHOLE_PROTEIN":
        if not _whole_protein_allowed(record):
            findings.append(
                _finding(
                    "whole_protein_not_permitted",
                    f"WHOLE_PROTEIN is not permitted for {record.get('trait_category')!r}",
                    **context,
                )
            )
        if coordinate_frame is not None or intervals is not None or positions is not None:
            findings.append(
                _finding(
                    "whole_protein_has_coordinates",
                    "WHOLE_PROTEIN must not carry a coordinate frame, intervals, or residue positions",
                    **context,
                )
            )
        if occurrence.get("expected_residues") is not None:
            findings.append(
                _finding(
                    "whole_protein_has_residues",
                    "WHOLE_PROTEIN must not carry expected_residues",
                    **context,
                )
            )
        if method not in WHOLE_PROTEIN_METHODS:
            findings.append(
                _finding(
                    "invalid_whole_protein_method",
                    f"{method!r} is not exact whole-protein membership/annotation evidence",
                    **context,
                )
            )
        return findings

    if scope != "LOCALIZED":
        findings.append(
            _finding(
                "invalid_occurrence_scope", "scope must be LOCALIZED or WHOLE_PROTEIN", **context
            )
        )
        return findings
    if record.get("trait_axis") in {"FUNCTION", "EVOLUTION"}:
        findings.append(
            _finding(
                "localized_scope_not_permitted",
                f"{record.get('trait_axis')} records require WHOLE_PROTEIN scope",
                **context,
            )
        )
    if method not in LOCALIZED_METHODS:
        findings.append(
            _finding("invalid_localized_method", f"{method!r} is not localized evidence", **context)
        )
    expected_frame = (
        "UNIPROT_ISOFORM"
        if UNIPROT_RE.fullmatch(str(protein_id)) and UNIPROT_RE.fullmatch(str(protein_id)).group(2)
        else "UNIPROT_CANONICAL"
    )
    if coordinate_frame != expected_frame:
        findings.append(
            _finding(
                "coordinate_frame_mismatch",
                f"{protein_id} requires coordinate_frame={expected_frame}",
                **context,
            )
        )
    if intervals is None and positions is None:
        findings.append(
            _finding(
                "localized_occurrence_without_coordinates",
                "LOCALIZED occurrence needs intervals and/or residue_positions",
                **context,
            )
        )
    findings.extend(_validate_intervals(occurrence, sequence, context))
    findings.extend(_validate_positions(occurrence, sequence, context))
    findings.extend(_validate_sifts(occurrence, sequence, context))

    fragments, _ = _localized_fragments(occurrence, sequence)
    residue_sequence = record.get("residue_sequence")
    if residue_sequence is not None and residue_sequence not in fragments:
        findings.append(
            _finding(
                "record_residue_sequence_mismatch",
                "record residue_sequence does not equal the sequence selected by occurrence coordinates",
                **context,
            )
        )
    sequence_pattern = record.get("sequence_pattern")
    if sequence_pattern is not None:
        elm_trait = _namespace(record.get("identifier")) == "ELM"
        compiled, error = (
            compile_elm_sequence_pattern(sequence_pattern)
            if elm_trait
            else compile_sequence_pattern(sequence_pattern)
        )
        if compiled is None:
            findings.append(
                _finding(
                    "unsupported_sequence_pattern",
                    f"cannot verify record sequence_pattern: {error}",
                    **context,
                )
            )
        elif elm_trait and not _elm_pattern_matches_exact_interval(compiled, occurrence, sequence):
            findings.append(
                _finding(
                    "record_sequence_pattern_mismatch",
                    "ELM sequence_pattern does not consume the exact source interval "
                    "in the complete resolved protein",
                    **context,
                )
            )
        elif not elm_trait and not any(compiled.fullmatch(fragment) for fragment in fragments):
            findings.append(
                _finding(
                    "record_sequence_pattern_mismatch",
                    "record sequence_pattern does not match the sequence selected by coordinates",
                    **context,
                )
            )
    return findings


def _validate_qualified_example(
    example: Mapping[str, Any],
    *,
    record: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
    file: str,
    example_index: int,
) -> list[Finding]:
    trait_id = record.get("identifier", "")
    pid = example.get("protein_id", "")
    context = {
        "file": file,
        "trait_id": trait_id,
        "protein_id": pid,
        "example_index": example_index,
        "occurrence_index": "",
    }
    findings: list[Finding] = []
    if not isinstance(pid, str) or UNIPROT_RE.fullmatch(pid) is None:
        findings.append(
            _finding(
                "invalid_accession", "protein_id is not an exact UniProtKB accession", **context
            )
        )
    if reference is None:
        findings.append(
            _finding(
                "unresolved_protein_reference",
                "QUALIFIED example has no exact protein_id in the supplied registry",
                **context,
            )
        )
        return findings

    required_snapshots = (
        "protein_label",
        "taxon_id",
        "taxon_label",
        "sequence_length",
        "sequence_sha256",
        "uniprot_release",
        "source",
    )
    for field in required_snapshots:
        if field not in example or example[field] in (None, ""):
            findings.append(
                _finding(
                    "qualified_example_missing_field",
                    f"QUALIFIED example requires {field!r}",
                    **context,
                )
            )
    for field in (
        "protein_label",
        "taxon_id",
        "taxon_label",
        "sequence_length",
        "sequence_sha256",
        "uniprot_release",
    ):
        if field in example and example.get(field) != reference.get(field):
            findings.append(
                _finding(
                    f"{field}_mismatch",
                    f"example {field}={example.get(field)!r}, registry has {reference.get(field)!r}",
                    **context,
                )
            )
    for field in ("reviewed", "sequence_version"):
        if field in example and example.get(field) != reference.get(field):
            findings.append(
                _finding(
                    f"{field}_mismatch",
                    f"example {field}={example.get(field)!r}, registry has {reference.get(field)!r}",
                    **context,
                )
            )
    if "sequence" in example and example.get("sequence") != reference.get("sequence"):
        findings.append(
            _finding(
                "inline_sequence_mismatch",
                "inline example sequence does not match ProteinReference sequence",
                **context,
            )
        )
    occurrences = example.get("trait_occurrences")
    if not isinstance(occurrences, list) or not occurrences:
        findings.append(
            _finding(
                "qualified_without_occurrence",
                "QUALIFIED example requires at least one record-specific trait_occurrence",
                **context,
            )
        )
    return findings


def validate_record(
    record: object,
    registry: Mapping[str, Mapping[str, Any]],
    *,
    evidence_registry: Mapping[str, Mapping[str, Any]] | None = None,
    hierarchy_index: Mapping[str, Iterable[str]] | None = None,
    file: str = "<memory>",
    require_qualified: bool = False,
) -> list[Finding]:
    """Validate every canonical example in one parsed ProteinTraitRecord."""

    if not isinstance(record, dict):
        return [_finding("record_not_object", "record YAML must parse to an object", file=file)]
    trait_id = record.get("identifier", "")
    examples = record.get("canonical_examples")
    if examples is None:
        if require_qualified:
            return [
                _finding(
                    "no_qualified_example",
                    "record has no canonical_examples",
                    file=file,
                    trait_id=trait_id,
                )
            ]
        return []
    if not isinstance(examples, list):
        return [
            _finding(
                "canonical_examples_not_list",
                "canonical_examples must be a list",
                file=file,
                trait_id=trait_id,
            )
        ]

    findings: list[Finding] = []
    declared_qualified = False
    for example_index, example in enumerate(examples):
        if not isinstance(example, dict):
            findings.append(
                _finding(
                    "example_not_object",
                    "canonical example must be an object",
                    file=file,
                    trait_id=trait_id,
                    example_index=example_index,
                )
            )
            continue
        pid = example.get("protein_id", "")
        status = effective_qualification_status(example)
        declared_qualified |= status == QUALIFIED
        if status != QUALIFIED:
            if status != LEGACY_UNVERIFIED:
                findings.append(
                    _finding(
                        "unqualified_canonical_example",
                        f"explicit intermediate status {status!r} belongs in the candidate ledger",
                        file=file,
                        trait_id=trait_id,
                        protein_id=pid,
                        example_index=example_index,
                    )
                )
            if require_qualified:
                findings.append(
                    _finding(
                        "legacy_unverified_example",
                        f"canonical example has effective status {status}",
                        file=file,
                        trait_id=trait_id,
                        protein_id=pid,
                        example_index=example_index,
                    )
                )

        reference = registry.get(pid) if isinstance(pid, str) else None
        if status == QUALIFIED:
            findings.extend(
                _validate_qualified_example(
                    example,
                    record=record,
                    reference=reference,
                    file=file,
                    example_index=example_index,
                )
            )
        occurrences = example.get("trait_occurrences")
        if occurrences is not None and not isinstance(occurrences, list):
            findings.append(
                _finding(
                    "trait_occurrences_not_list",
                    "trait_occurrences must be a list",
                    file=file,
                    trait_id=trait_id,
                    protein_id=pid,
                    example_index=example_index,
                )
            )
            continue
        qualified_occurrences = 0
        for occurrence_index, occurrence in enumerate(occurrences or []):
            if isinstance(occurrence, dict) and occurrence.get("qualification_status") == QUALIFIED:
                qualified_occurrences += 1
            findings.extend(
                _validate_occurrence(
                    occurrence,
                    record=record,
                    example=example,
                    reference=reference,
                    evidence_registry=evidence_registry,
                    hierarchy_index=hierarchy_index,
                    file=file,
                    example_index=example_index,
                    occurrence_index=occurrence_index,
                )
            )
        if status == QUALIFIED and qualified_occurrences == 0:
            findings.append(
                _finding(
                    "qualified_without_qualified_occurrence",
                    "example status is QUALIFIED but no occurrence status is QUALIFIED",
                    file=file,
                    trait_id=trait_id,
                    protein_id=pid,
                    example_index=example_index,
                )
            )
        if status != QUALIFIED and qualified_occurrences:
            findings.append(
                _finding(
                    "qualified_occurrence_on_unqualified_example",
                    "a QUALIFIED occurrence requires the containing example to be QUALIFIED",
                    file=file,
                    trait_id=trait_id,
                    protein_id=pid,
                    example_index=example_index,
                )
            )
    if require_qualified and not declared_qualified:
        findings.append(
            _finding(
                "no_qualified_example",
                "record has no canonical example declared QUALIFIED",
                file=file,
                trait_id=trait_id,
            )
        )
    return findings


def iter_yaml_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}:
            files.append(path)
        elif path.is_dir():
            files.extend(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file() and candidate.suffix.lower() in {".yaml", ".yml"}
            )
    return sorted(set(files))


def _qualification_scan_required(text: str, *, require_qualified: bool) -> bool:
    """Conservatively decide whether a trait must be parsed for this validator.

    Every YAML spelling that constructs the exact key ``qualification_status``
    either contains that literal text or uses a double-quoted escape, which
    necessarily contains a backslash. Anchors and merge keys must still define
    the scalar somewhere in the same document. This is only a negative
    optimization for migration-era legacy records; all possible qualification
    claims are parsed structurally before any validation or registry decision.
    """

    return require_qualified or "qualification_status" in text or "\\" in text


def _load_yaml_value(path: Path, text: str | None = None) -> tuple[object, Finding | None]:
    if text is None:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            return None, _finding("yaml_error", str(error).splitlines()[0], file=str(path))
    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError as error:
        return None, _finding("yaml_error", str(error).splitlines()[0], file=str(path))


def _qualified_claim_facts(value: object) -> tuple[bool, bool]:
    """Return (has QUALIFIED claim, has qualified inheritance) from parsed YAML."""

    if not isinstance(value, Mapping):
        return False, False
    examples = value.get("canonical_examples")
    if not isinstance(examples, list):
        return False, False
    qualified = False
    qualified_inheritance = False
    for example in examples:
        if not isinstance(example, Mapping):
            continue
        qualified |= example.get("qualification_status") == QUALIFIED
        occurrences = example.get("trait_occurrences")
        if not isinstance(occurrences, list):
            continue
        for occurrence in occurrences:
            if not isinstance(occurrence, Mapping):
                continue
            occurrence_qualified = occurrence.get("qualification_status") == QUALIFIED
            qualified |= occurrence_qualified
            qualified_inheritance |= occurrence_qualified and "inheritance_path" in occurrence
    return qualified, qualified_inheritance


def validate_yaml_file(
    path: Path,
    registry: Mapping[str, Mapping[str, Any]],
    *,
    evidence_registry: Mapping[str, Mapping[str, Any]] | None = None,
    hierarchy_index: Mapping[str, Iterable[str]] | None = None,
    require_qualified: bool = False,
) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return [_finding("yaml_error", str(error).splitlines()[0], file=str(path))]
    if not _qualification_scan_required(text, require_qualified=require_qualified):
        return []
    record, error = _load_yaml_value(path, text)
    if error is not None:
        return [error]
    return validate_record(
        record,
        registry,
        evidence_registry=evidence_registry,
        hierarchy_index=hierarchy_index,
        file=str(path),
        require_qualified=require_qualified,
    )


def _write_findings(path: Path, findings: Sequence[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "file",
        "trait_id",
        "protein_id",
        "example_index",
        "occurrence_index",
        "code",
        "message",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for finding in findings:
            writer.writerow(asdict(finding))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths", nargs="*", type=Path, help="Trait YAML files/directories; default data/traits"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help=f"ProteinReference JSONL registry (default {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--evidence-registry",
        type=Path,
        default=DEFAULT_EVIDENCE_REGISTRY,
        help=f"GroundingEvidence JSONL registry (default {DEFAULT_EVIDENCE_REGISTRY})",
    )
    parser.add_argument(
        "--membership-registry",
        type=Path,
        default=DEFAULT_MEMBERSHIP_REGISTRY,
        help=(
            "content-addressed UniProt membership JSONL registry "
            f"(default {DEFAULT_MEMBERSHIP_REGISTRY})"
        ),
    )
    parser.add_argument(
        "--hierarchy-traits",
        nargs="+",
        type=Path,
        help="Authoritative trait YAML roots for inheritance edges; default input paths",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_REPORT, help="Finding TSV")
    parser.add_argument(
        "--require-qualified",
        action="store_true",
        help="Completion gate: reject legacy examples and records with no QUALIFIED example",
    )
    parser.add_argument(
        "--fail-on", choices=("error", "never"), default="error", help="Exit policy"
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="exit 0 when every supplied path is missing; for the CI diff "
        "caller, whose file list can be deletion-only (#616, and #540 for the "
        "same flag on validate_strict.py)",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    roots = args.paths or [DEFAULT_TRAITS]
    files = iter_yaml_files(roots)
    if not files:
        # Deletion-only diffs are legitimate; a scan with nothing left to scan is
        # not a fault. Opt in, so a human typing a mistyped path still gets an
        # error rather than a silent "validated" -- the distinction #540 drew for
        # validate_strict.py, kept identical here so the two CI steps agree.
        if args.allow_missing and args.paths:
            print(
                "All supplied paths were missing (e.g. deleted files) — nothing to validate.",
                file=sys.stderr,
            )
            return 0
        print("No trait YAML files found.", file=sys.stderr)
        return 2

    # Durable default registries may be absent during the migration. Do not turn
    # the entire legacy corpus red merely because it contains no new qualified
    # assertion. Every possible qualification-bearing YAML is parsed before the
    # decision; as soon as a semantic QUALIFIED claim exists, both registries
    # become mandatory and their missing-file findings fail CI.
    qualified_input = False
    qualified_inheritance_input = False
    membership_uses: list[MembershipUse] = []
    parsed_records: dict[Path, object] = {}
    input_findings: list[Finding] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            input_findings.append(
                _finding("yaml_error", str(error).splitlines()[0], file=str(path))
            )
            continue
        if not _qualification_scan_required(text, require_qualified=args.require_qualified):
            continue
        value, error = _load_yaml_value(path, text)
        if error is not None:
            input_findings.append(error)
            continue
        parsed_records[path] = value
        has_qualified, has_qualified_inheritance = _qualified_claim_facts(value)
        qualified_input |= has_qualified
        qualified_inheritance_input |= has_qualified_inheritance
        membership_uses.extend(_qualified_membership_uses(value, file=str(path)))

    registry: dict[str, dict[str, Any]] = {}
    evidence_registry: dict[str, dict[str, Any]] | None = None
    memberships: list[dict[str, Any]] = []
    hierarchy_index: dict[str, frozenset[str]] | None = None
    findings: list[Finding] = list(input_findings)
    registry_explicit = args.registry != DEFAULT_REGISTRY
    if qualified_input or registry_explicit or args.registry.is_file():
        registry, registry_findings = load_registry(args.registry)
        findings.extend(registry_findings)
    evidence_explicit = args.evidence_registry != DEFAULT_EVIDENCE_REGISTRY
    if qualified_input or evidence_explicit or args.evidence_registry.is_file():
        evidence_registry, evidence_findings = load_evidence_registry(args.evidence_registry)
        findings.extend(evidence_findings)
    evidence_lookup = evidence_registry or {}
    uniprot_membership_uses = [
        use
        for use in membership_uses
        if (
            use.evidence_source == "UniProtKB"
            or evidence_lookup.get(use.evidence_id, {}).get("provider_kind") == "UNIPROT"
            or evidence_lookup.get(use.evidence_id, {}).get("evidence_source") == "UniProtKB"
        )
    ]
    membership_explicit = args.membership_registry != DEFAULT_MEMBERSHIP_REGISTRY
    membership_findings: list[Finding] = []
    if uniprot_membership_uses or membership_explicit or args.membership_registry.is_file():
        memberships, membership_findings = load_membership_registry(args.membership_registry)
        findings.extend(membership_findings)
    if qualified_inheritance_input or args.hierarchy_traits:
        hierarchy_roots = args.hierarchy_traits or roots
        hierarchy_index, hierarchy_findings = build_hierarchy_index(hierarchy_roots)
        findings.extend(hierarchy_findings)

    for path, record in parsed_records.items():
        findings.extend(
            validate_record(
                record,
                registry,
                evidence_registry=evidence_registry,
                hierarchy_index=hierarchy_index,
                file=str(path),
                require_qualified=args.require_qualified,
            )
        )
    if uniprot_membership_uses and not membership_findings:
        findings.extend(
            validate_membership_replay(
                uniprot_membership_uses,
                evidence_lookup,
                memberships,
                membership_path=args.membership_registry,
            )
        )
    findings.sort(
        key=lambda item: (
            item.file,
            item.trait_id,
            item.protein_id,
            item.example_index,
            item.occurrence_index,
            item.code,
            item.message,
        )
    )
    _write_findings(args.out, findings)

    if not args.quiet:
        by_code: dict[str, int] = {}
        for finding in findings:
            by_code[finding.code] = by_code.get(finding.code, 0) + 1
        print(f"files scanned: {len(files)}", file=sys.stderr)
        print(f"registry proteins: {len(registry)}", file=sys.stderr)
        print(f"source evidence objects: {len(evidence_registry or {})}", file=sys.stderr)
        print(f"UniProt membership objects: {len(memberships)}", file=sys.stderr)
        print(f"hierarchy records: {len(hierarchy_index or {})}", file=sys.stderr)
        print(f"semantic findings: {len(findings)}", file=sys.stderr)
        for code, count in sorted(by_code.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {code}: {count}", file=sys.stderr)
        print(f"TSV: {args.out}", file=sys.stderr)
    if findings and args.fail_on == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
