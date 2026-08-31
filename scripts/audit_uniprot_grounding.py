#!/usr/bin/env python3
"""Audit UniProt grounding without modifying trait records.

This is the read-only front door of the candidate -> resolve -> validate ->
promote workflow described in ``research/uniprot-organism-protein-grounding-plan.md``.
It deliberately distinguishes two things which the legacy corpus previously
conflated:

* ``inline_state`` describes how complete the fields already embedded in a
  record look.  It is a shape check, not biological validation.
* ``grounding_state`` is fail-closed.  An existing example is
  ``LEGACY_UNVERIFIED`` unless both it and an exact matching trait occurrence
  explicitly say ``QUALIFIED``; marker-only claims are reported as
  ``DECLARED_QUALIFIED_UNVERIFIED`` until the semantic validator dereferences
  their protein and source-evidence registries.  Qualified UniProt
  ``SOURCE_MEMBERSHIP`` occurrences additionally replay the exact provider
  fact in the content-addressed UniProt membership registry.

Only files with a top-level ``canonical_examples`` block are YAML-parsed.  The
remaining (currently roughly 70%) are scanned for three top-level scalar fields,
which keeps a full-corpus audit practical.  Candidate discovery is also
read-only: it joins exact trait identifiers in the InterPro frame to protein
metadata in profiles.jsonl and sequences in the UniProt residue frame.

The four outputs are deterministic and atomically replaced:

* summary.tsv       counts by state, axis, category, and identifier namespace
* records.tsv       one row per trait record
* candidates.jsonl exact, locally supported candidate proteins (never sequence copies)
* blocked.tsv       explicit reasons why records/candidates cannot advance locally
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data" / "grounding" / "protein_registry.jsonl"
DEFAULT_EVIDENCE_REGISTRY = REPO_ROOT / "data" / "grounding" / "occurrence_evidence.jsonl"
DEFAULT_MEMBERSHIP_REGISTRY = REPO_ROOT / "data" / "grounding" / "uniprot_memberships.jsonl"

UNIPROT_ID = re.compile(
    r"^UniProtKB:(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[0-9]+)?$"
)
TAXON_ID = re.compile(r"^NCBITaxon:[0-9]+$")
SEQUENCE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TOP_SCALAR = re.compile(r"(?m)^(identifier|trait_axis|trait_category):[ \t]*(.*?)[ \t]*$")
HAS_EXAMPLES = re.compile(r"(?m)^canonical_examples:[ \t]*(?:#.*)?$")

INLINE_STATES = (
    "NO_VALID_PROTEIN",
    "PROTEIN_ORGANISM_INCOMPLETE",
    "PROTEIN_ORGANISM_NO_SEQUENCE",
    "SEQUENCE_NO_CATEGORY_COORDINATE",
    "STRICT_INLINE_SHAPE",
)
INLINE_RANK = {state: rank for rank, state in enumerate(INLINE_STATES)}

WHOLE_PROTEIN_CATEGORIES = {
    "SEQ_FAMILY",
    "SEQ_HOMOLOGOUS_SUPERFAMILY",
}

RECORD_COLUMNS = (
    "trait_id",
    "record_path",
    "trait_axis",
    "trait_category",
    "source_namespace",
    "grounding_state",
    "inline_state",
    "example_count",
    "valid_protein_count",
    "qualified_example_count",
    "candidate_state",
    "candidate_count",
    "available_candidate_count",
    "blocked_count",
)
BLOCKED_COLUMNS = ("trait_id", "record_path", "protein_id", "reason", "detail")
SUMMARY_COLUMNS = (
    "group_by",
    "group_value",
    "grounding_state",
    "inline_state",
    "candidate_state",
    "count",
)


class AuditInputError(ValueError):
    """An input cannot support a trustworthy audit."""


@dataclass(slots=True)
class RecordAudit:
    trait_id: str
    path: Path
    record_path: str
    trait_axis: str
    trait_category: str
    source_namespace: str
    grounding_state: str
    inline_state: str
    example_count: int = 0
    valid_protein_ids: tuple[str, ...] = ()
    qualified_example_count: int = 0
    invalid_protein_ids: tuple[str, ...] = ()
    candidate_state: str = "NO_LOCAL_CANDIDATE"
    candidate_count: int = 0
    available_candidate_count: int = 0
    blocked_count: int = 0


@dataclass(slots=True)
class Blocked:
    trait_id: str
    record_path: str
    protein_id: str
    reason: str
    detail: str = ""


@dataclass(slots=True)
class Profile:
    protein_id: str
    protein_label: str
    taxon_id: str
    taxon_label: str
    sequence_length: int
    reviewed: bool


@dataclass(slots=True)
class CandidateEvidence:
    accession: str
    intervals: tuple[tuple[int, int], ...]
    profile: Profile | None = None
    sequence: str | None = None
    failures: list[str] = field(default_factory=list)


def _clean_scalar(value: str) -> str:
    """Decode the simple top-level scalar spellings used for routing fields."""
    value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def cheap_metadata(text: str) -> tuple[str, str, str]:
    """Return identifier/axis/category without constructing a YAML object."""
    found = {key: _clean_scalar(value) for key, value in TOP_SCALAR.findall(text)}
    return (
        found.get("identifier", ""),
        found.get("trait_axis", ""),
        found.get("trait_category", ""),
    )


def _display_path(path: Path, traits: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().relative_to(traits.resolve()).as_posix()


def _valid_sequence(example: dict) -> str | None:
    sequence = example.get("sequence")
    if not isinstance(sequence, str):
        return None
    sequence = sequence.strip().upper()
    if not sequence or not SEQUENCE.fullmatch(sequence):
        return None
    length = example.get("sequence_length")
    if length is not None and (not isinstance(length, int) or length != len(sequence)):
        return None
    return sequence


def _has_in_bounds_category_coordinate(example: dict, category: str, sequence: str) -> bool:
    for feature in example.get("features") or []:
        if not isinstance(feature, dict) or feature.get("trait_category") != category:
            continue
        start, end = feature.get("start"), feature.get("end")
        if (
            isinstance(start, int)
            and not isinstance(start, bool)
            and isinstance(end, int)
            and not isinstance(end, bool)
            and 1 <= start <= end <= len(sequence)
        ):
            return True
    return False


def _has_explicit_qualified_occurrence(example: dict, trait_id: str) -> bool:
    """Apply the migration rule; semantic validity belongs to the validator.

    Checking both status flags prevents a newly added example-level marker from
    accidentally blessing an unrelated or absent occurrence.  This audit does
    not pretend it can replace registry dereferencing and residue validation.
    """
    if example.get("qualification_status") != "QUALIFIED":
        return False
    protein_id = example.get("protein_id")
    for occurrence in example.get("trait_occurrences") or []:
        if not isinstance(occurrence, dict):
            continue
        if occurrence.get("qualification_status") != "QUALIFIED":
            continue
        if occurrence.get("trait_id") != trait_id:
            continue
        if occurrence.get("protein_id") != protein_id:
            continue
        return True
    return False


def _has_any_qualified_declaration(examples: object) -> bool:
    """Return whether canonical-example data contains any QUALIFIED marker."""
    if not isinstance(examples, list):
        return False
    for example in examples:
        if not isinstance(example, dict):
            continue
        if example.get("qualification_status") == "QUALIFIED":
            return True
        occurrences = example.get("trait_occurrences")
        if isinstance(occurrences, list) and any(
            isinstance(occurrence, dict) and occurrence.get("qualification_status") == "QUALIFIED"
            for occurrence in occurrences
        ):
            return True
    return False


def _semantic_validator_api() -> tuple[Any, Any, Any, Any, Any, Any, Any]:
    """Import the adjacent semantic validator in CLI and importlib test contexts."""
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from validate_uniprot_grounding import (  # noqa: PLC0415
        build_hierarchy_index,
        _qualified_membership_uses,
        load_evidence_registry,
        load_membership_registry,
        load_registry,
        validate_membership_replay,
        validate_record,
    )

    return (
        load_registry,
        load_evidence_registry,
        load_membership_registry,
        build_hierarchy_index,
        _qualified_membership_uses,
        validate_membership_replay,
        validate_record,
    )


def _semantic_reason(code: object) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", str(code)).strip("_").upper()
    return f"SEMANTIC_{normalized or 'VALIDATION_ERROR'}"


def _semantic_blocks(findings: Iterable[object], record: "RecordAudit") -> list[Blocked]:
    """Translate semantic findings into deterministic, record-local blockers."""
    blocks: list[Blocked] = []
    for finding in findings:
        code = getattr(finding, "code", "validation_error")
        message = str(getattr(finding, "message", "semantic validation failed"))
        source = str(getattr(finding, "file", ""))
        detail = f"{source}: {message}" if source and source != record.record_path else message
        protein_id = str(getattr(finding, "protein_id", "") or "")
        blocks.append(
            Blocked(
                record.trait_id,
                record.record_path,
                protein_id,
                _semantic_reason(code),
                detail,
            )
        )
    return blocks


def classify_examples(
    examples: object, trait_id: str, category: str
) -> tuple[str, str, tuple[str, ...], int, tuple[str, ...], int]:
    """Classify legacy inline shape and explicit qualification.

    Returns grounding state, inline state, valid IDs, qualified count, invalid
    IDs, and raw example count.  The best inline state is reached by one single
    example; fields are never assembled across different proteins.
    """
    if not isinstance(examples, list):
        examples = []
    best = "NO_VALID_PROTEIN"
    valid_ids: set[str] = set()
    invalid_ids: set[str] = set()
    qualified = 0

    for example in examples:
        if not isinstance(example, dict):
            continue
        protein_id = example.get("protein_id")
        if not isinstance(protein_id, str) or not UNIPROT_ID.fullmatch(protein_id):
            if protein_id is not None:
                invalid_ids.add(str(protein_id))
            continue
        valid_ids.add(protein_id)
        state = "PROTEIN_ORGANISM_INCOMPLETE"

        taxon_id, taxon_label = example.get("taxon_id"), example.get("taxon_label")
        if not (
            isinstance(taxon_id, str)
            and TAXON_ID.fullmatch(taxon_id)
            and isinstance(taxon_label, str)
            and bool(taxon_label.strip())
        ):
            if INLINE_RANK[state] > INLINE_RANK[best]:
                best = state
            if _has_explicit_qualified_occurrence(example, trait_id):
                qualified += 1
            continue

        state = "PROTEIN_ORGANISM_NO_SEQUENCE"
        sequence = _valid_sequence(example)
        if sequence is not None:
            state = "SEQUENCE_NO_CATEGORY_COORDINATE"
            if _has_in_bounds_category_coordinate(example, category, sequence):
                state = "STRICT_INLINE_SHAPE"
        if INLINE_RANK[state] > INLINE_RANK[best]:
            best = state
        if _has_explicit_qualified_occurrence(example, trait_id):
            qualified += 1

    if qualified:
        # Status strings are declarations, not proof.  Calling this QUALIFIED would let a
        # fabricated provider/release/coordinate tuple make the completion audit green.
        grounding = "DECLARED_QUALIFIED_UNVERIFIED"
    elif valid_ids:
        grounding = "LEGACY_UNVERIFIED"
    else:
        grounding = "NO_PROTEIN"
    return (
        grounding,
        best,
        tuple(sorted(valid_ids)),
        qualified,
        tuple(sorted(invalid_ids)),
        len(examples),
    )


def scan_records(
    traits: Path,
    *,
    protein_registry_path: Path = DEFAULT_PROTEIN_REGISTRY,
    evidence_registry_path: Path = DEFAULT_EVIDENCE_REGISTRY,
    membership_registry_path: Path = DEFAULT_MEMBERSHIP_REGISTRY,
    hierarchy_traits: Sequence[Path] | None = None,
) -> tuple[list[RecordAudit], list[Blocked]]:
    """Scan records and prove every declared qualification against registries.

    The durable registries are loaded lazily: an all-legacy corpus remains
    auditable while migration artifacts are absent.  The first explicit
    ``QUALIFIED`` declaration makes both core registries mandatory.  The
    UniProt membership registry is loaded only for an explicitly qualified
    ``SOURCE_MEMBERSHIP`` occurrence attributed to UniProtKB.  An authoritative
    hierarchy is loaded only when a declaration carries an inheritance path.
    """
    if not traits.is_dir():
        raise AuditInputError(f"traits directory does not exist: {traits}")
    paths = sorted(traits.rglob("*.yaml"), key=lambda p: p.relative_to(traits).as_posix())
    records: list[RecordAudit] = []
    blocked: list[Blocked] = []
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    semantic_loaded = False
    protein_registry: Mapping[str, Mapping[str, Any]] = {}
    evidence_registry: Mapping[str, Mapping[str, Any]] | None = None
    semantic_input_findings: list[object] = []
    membership_loaded = False
    memberships: Sequence[Mapping[str, Any]] = []
    membership_input_findings: list[object] = []
    hierarchy_loaded = False
    hierarchy_index: Mapping[str, Iterable[str]] | None = None
    hierarchy_findings: list[object] = []
    semantic_api: tuple[Any, Any, Any, Any, Any, Any, Any] | None = None

    for path in paths:
        record_path = _display_path(path, traits)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            blocked.append(Blocked("", record_path, "", "RECORD_READ_ERROR", str(exc)))
            continue
        trait_id, axis, category = cheap_metadata(text)
        namespace = trait_id.split(":", 1)[0] if ":" in trait_id else ""
        grounding = "NO_PROTEIN"
        inline = "NO_VALID_PROTEIN"
        valid_ids: tuple[str, ...] = ()
        invalid_ids: tuple[str, ...] = ()
        qualified = 0
        example_count = 0

        if HAS_EXAMPLES.search(text):
            try:
                blob = yaml.load(text, Loader=loader)
                if not isinstance(blob, dict):
                    raise AuditInputError("record root is not a mapping")
                examples = blob.get("canonical_examples")
                (
                    grounding,
                    inline,
                    valid_ids,
                    qualified,
                    invalid_ids,
                    example_count,
                ) = classify_examples(examples, trait_id, category)

                if _has_any_qualified_declaration(examples):
                    if semantic_api is None:
                        semantic_api = _semantic_validator_api()
                    (
                        load_registry,
                        load_evidence_registry,
                        load_membership_registry,
                        build_hierarchy_index,
                        qualified_membership_uses,
                        validate_membership_replay,
                        validate_record,
                    ) = semantic_api
                    if not semantic_loaded:
                        protein_registry, protein_findings = load_registry(protein_registry_path)
                        evidence_registry, evidence_findings = load_evidence_registry(
                            evidence_registry_path
                        )
                        semantic_input_findings = [
                            *protein_findings,
                            *evidence_findings,
                        ]
                        semantic_loaded = True
                    membership_uses = qualified_membership_uses(blob, file=record_path)
                    evidence_lookup = evidence_registry or {}
                    uniprot_membership_uses = [
                        use
                        for use in membership_uses
                        if (
                            use.evidence_source == "UniProtKB"
                            or evidence_lookup.get(use.evidence_id, {}).get("provider_kind")
                            == "UNIPROT"
                            or evidence_lookup.get(use.evidence_id, {}).get("evidence_source")
                            == "UniProtKB"
                        )
                    ]
                    if uniprot_membership_uses and not membership_loaded:
                        memberships, membership_input_findings = load_membership_registry(
                            membership_registry_path
                        )
                        membership_loaded = True
                    needs_hierarchy = "inheritance_path" in text
                    if needs_hierarchy and not hierarchy_loaded:
                        roots = list(hierarchy_traits) if hierarchy_traits else [traits]
                        hierarchy_index, hierarchy_findings = build_hierarchy_index(roots)
                        hierarchy_loaded = True

                    record_for_findings = RecordAudit(
                        trait_id=trait_id,
                        path=path,
                        record_path=record_path,
                        trait_axis=axis,
                        trait_category=category,
                        source_namespace=namespace,
                        grounding_state=grounding,
                        inline_state=inline,
                    )
                    semantic_findings = [
                        *semantic_input_findings,
                        *(hierarchy_findings if needs_hierarchy else []),
                        *validate_record(
                            blob,
                            protein_registry,
                            evidence_registry=evidence_registry,
                            hierarchy_index=hierarchy_index,
                            file=record_path,
                        ),
                    ]
                    if uniprot_membership_uses:
                        semantic_findings.extend(membership_input_findings)
                        if not membership_input_findings:
                            semantic_findings.extend(
                                validate_membership_replay(
                                    uniprot_membership_uses,
                                    evidence_lookup,
                                    memberships,
                                    membership_path=membership_registry_path,
                                )
                            )
                    if semantic_findings:
                        # Marker presence is useful migration telemetry, but the
                        # completion state and count remain fail-closed.
                        grounding = "DECLARED_QUALIFIED_UNVERIFIED"
                        qualified = 0
                        blocked.extend(_semantic_blocks(semantic_findings, record_for_findings))
                    else:
                        grounding = "QUALIFIED"
            except (yaml.YAMLError, AuditInputError) as exc:
                blocked.append(Blocked(trait_id, record_path, "", "RECORD_YAML_ERROR", str(exc)))

        record = RecordAudit(
            trait_id=trait_id,
            path=path,
            record_path=record_path,
            trait_axis=axis,
            trait_category=category,
            source_namespace=namespace,
            grounding_state=grounding,
            inline_state=inline,
            example_count=example_count,
            valid_protein_ids=valid_ids,
            qualified_example_count=qualified,
            invalid_protein_ids=invalid_ids,
        )
        records.append(record)

        if not trait_id:
            blocked.append(Blocked("", record_path, "", "MISSING_TRAIT_ID"))
        if not axis:
            blocked.append(Blocked(trait_id, record_path, "", "MISSING_TRAIT_AXIS"))
        if not category:
            blocked.append(Blocked(trait_id, record_path, "", "MISSING_TRAIT_CATEGORY"))
        for protein_id in invalid_ids:
            blocked.append(Blocked(trait_id, record_path, protein_id, "INVALID_UNIPROT_IDENTIFIER"))

    return records, blocked


def _load_sidecar(path: Path, payload_key: str) -> tuple[dict, dict]:
    if not path.is_file():
        raise AuditInputError(f"sidecar does not exist: {path}")
    try:
        with path.open(encoding="utf-8") as handle:
            blob = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditInputError(f"cannot read {path}: {exc}") from exc
    if not isinstance(blob, dict):
        raise AuditInputError(f"sidecar root is not an object: {path}")
    if "_meta" in blob:
        payload, meta = blob.get(payload_key), blob.get("_meta")
        if not isinstance(payload, dict) or not isinstance(meta, dict):
            raise AuditInputError(f"malformed wrapped sidecar: {path}")
        return payload, meta
    # Legacy input stays auditable but cannot produce release-qualified candidates.
    return blob, {"release": None, "source": None, "legacy": True}


def _load_profiles(path: Path, wanted: set[str]) -> tuple[dict[str, Profile], set[str]]:
    if not path.is_file():
        raise AuditInputError(f"profiles JSONL does not exist: {path}")
    profiles: dict[str, Profile] = {}
    duplicates: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AuditInputError(
                    f"malformed profiles JSONL at {path}:{line_number}: {exc}"
                ) from exc
            protein_id = row.get("accession") if isinstance(row, dict) else None
            if not isinstance(protein_id, str):
                continue
            if not protein_id.startswith("UniProtKB:"):
                protein_id = f"UniProtKB:{protein_id}"
            accession = protein_id.split(":", 1)[1]
            if accession not in wanted:
                continue
            if accession in profiles:
                duplicates.add(accession)
                continue
            length = row.get("length")
            reviewed = row.get("reviewed")
            profiles[accession] = Profile(
                protein_id=protein_id,
                protein_label=row.get("name") if isinstance(row.get("name"), str) else "",
                taxon_id=row.get("taxon") if isinstance(row.get("taxon"), str) else "",
                taxon_label=(
                    row.get("taxon_label") if isinstance(row.get("taxon_label"), str) else ""
                ),
                sequence_length=(
                    length if isinstance(length, int) and not isinstance(length, bool) else 0
                ),
                reviewed=reviewed if isinstance(reviewed, bool) else False,
            )
    return profiles, duplicates


def _normal_intervals(value: object) -> tuple[tuple[int, int], ...] | None:
    if not isinstance(value, list) or not value:
        return None
    out: set[tuple[int, int]] = set()
    for interval in value:
        if not isinstance(interval, (list, tuple)) or len(interval) != 2:
            return None
        start, end = interval
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
        ):
            return None
        out.add((start, end))
    return tuple(sorted(out))


def _candidate_id(row: dict) -> str:
    identity = {
        "trait_id": row["trait_id"],
        "protein_id": row["protein_id"],
        "source_trait_id": row["source_trait_id"],
        "mapping_method": row["mapping_method"],
        "evidence_source": row["evidence_source"],
        "source_release": row["source_release"],
        "sequence_release": row["sequence_release"],
        "sequence_sha256": row["sequence_sha256"],
        "scope": row["scope"],
        "coordinate_frame": row.get("coordinate_frame"),
        "intervals": row.get("intervals", []),
        "residue_positions": row.get("residue_positions", []),
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return "ug-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _scope(record: RecordAudit) -> str:
    if record.trait_axis in {"FUNCTION", "EVOLUTION"}:
        return "WHOLE_PROTEIN"
    if record.trait_category in WHOLE_PROTEIN_CATEGORIES:
        return "WHOLE_PROTEIN"
    return "LOCALIZED"


def _profile_failures(profile: Profile | None, sequence: str | None) -> list[str]:
    failures: list[str] = []
    if profile is None:
        return ["MISSING_PROFILE_METADATA"]
    if not profile.protein_label.strip():
        failures.append("MISSING_PROTEIN_LABEL")
    if not TAXON_ID.fullmatch(profile.taxon_id):
        failures.append("MISSING_OR_INVALID_TAXON_ID")
    if not profile.taxon_label.strip():
        failures.append("MISSING_TAXON_LABEL")
    if not sequence or not SEQUENCE.fullmatch(sequence):
        failures.append("MISSING_OR_INVALID_SEQUENCE")
    elif profile.sequence_length != len(sequence):
        failures.append("PROFILE_SEQUENCE_LENGTH_MISMATCH")
    return failures


def discover_candidates(
    records: list[RecordAudit],
    residue_frame_path: Path,
    interpro_frame_path: Path,
    profiles_path: Path,
    max_candidates_per_record: int,
) -> tuple[list[dict], list[Blocked]]:
    """Join exact local source matches and return candidate/blocked ledgers."""
    target_records: dict[str, list[RecordAudit]] = collections.defaultdict(list)
    for record in records:
        if record.grounding_state != "QUALIFIED" and record.trait_id:
            target_records[record.trait_id].append(record)

    interpro, interpro_meta = _load_sidecar(interpro_frame_path, "proteins")
    interpro_release = interpro_meta.get("release")
    exact: dict[str, list[CandidateEvidence]] = collections.defaultdict(list)
    wanted_accessions: set[str] = set()
    malformed_matches: list[tuple[str, str]] = []
    for accession, matches in interpro.items():
        if not isinstance(accession, str) or not isinstance(matches, dict):
            continue
        for trait_id, raw_intervals in matches.items():
            if trait_id not in target_records:
                continue
            intervals = _normal_intervals(raw_intervals)
            if intervals is None:
                malformed_matches.append((trait_id, accession))
                continue
            exact[trait_id].append(CandidateEvidence(accession, intervals))
            wanted_accessions.add(accession)

    profiles, duplicate_profiles = _load_profiles(profiles_path, wanted_accessions)
    residue, residue_meta = _load_sidecar(residue_frame_path, "proteins")
    uniprot_release = residue_meta.get("release")
    absent = set(residue_meta.get("absent") or [])
    blocked: list[Blocked] = []
    candidates: list[dict] = []

    for trait_id, accession in malformed_matches:
        for record in target_records[trait_id]:
            blocked.append(
                Blocked(
                    trait_id,
                    record.record_path,
                    f"UniProtKB:{accession}",
                    "MALFORMED_INTERPRO_INTERVAL",
                )
            )

    for record in records:
        if record.grounding_state == "QUALIFIED":
            continue
        for protein_id in record.valid_protein_ids:
            accession = protein_id.split(":", 1)[1]
            if accession in absent:
                blocked.append(
                    Blocked(
                        record.trait_id,
                        record.record_path,
                        protein_id,
                        "ACCESSION_ABSENT_FROM_RESIDUE_FRAME",
                        f"UniProt release {uniprot_release or 'unstamped'}",
                    )
                )
            elif accession not in residue:
                reason = (
                    "ISOFORM_SEQUENCE_NOT_IN_LOCAL_FRAME"
                    if "-" in accession
                    else "ACCESSION_MISSING_FROM_RESIDUE_FRAME"
                )
                blocked.append(Blocked(record.trait_id, record.record_path, protein_id, reason))

        evidence = exact.get(record.trait_id, [])
        if not evidence:
            blocked.append(
                Blocked(
                    record.trait_id,
                    record.record_path,
                    "",
                    "NO_LOCAL_EXACT_TRAIT_MATCH",
                    "No exact identifier in the supplied InterPro frame",
                )
            )
            continue

        valid: list[CandidateEvidence] = []
        review_only: list[CandidateEvidence] = []
        for item in evidence:
            item.profile = profiles.get(item.accession)
            residue_entry = residue.get(item.accession)
            if isinstance(residue_entry, dict) and isinstance(residue_entry.get("seq"), str):
                item.sequence = residue_entry["seq"].strip().upper()
            item.failures = _profile_failures(item.profile, item.sequence)
            if item.accession in duplicate_profiles:
                item.failures.append("DUPLICATE_PROFILE_ACCESSION")
            if not interpro_release:
                item.failures.append("UNPINNED_INTERPRO_RELEASE")
            if not uniprot_release:
                item.failures.append("UNPINNED_UNIPROT_RELEASE")
            if item.sequence and any(
                not (1 <= start <= end <= len(item.sequence)) for start, end in item.intervals
            ):
                item.failures.append("INTERPRO_INTERVAL_OUT_OF_BOUNDS")
            if _scope(record) == "LOCALIZED" and len(item.intervals) > 1:
                # The compact InterPro sidecar flattens location fragments and repeated
                # hits into one list.  Without original hit/location grouping, several
                # ranges cannot safely be asserted as one discontinuous occurrence.
                item.failures.append("UNGROUPED_INTERPRO_LOCATIONS")

            if item.failures:
                for reason in sorted(set(item.failures)):
                    blocked.append(
                        Blocked(
                            record.trait_id,
                            record.record_path,
                            f"UniProtKB:{item.accession}",
                            reason,
                        )
                    )
                if set(item.failures) == {"UNGROUPED_INTERPRO_LOCATIONS"}:
                    review_only.append(item)
            else:
                valid.append(item)

        existing = set(record.valid_protein_ids)
        valid.sort(
            key=lambda item: (
                f"UniProtKB:{item.accession}" not in existing,
                not bool(item.profile and item.profile.reviewed),
                item.accession,
            )
        )
        review_only.sort(
            key=lambda item: (
                f"UniProtKB:{item.accession}" not in existing,
                not bool(item.profile and item.profile.reviewed),
                item.accession,
            )
        )
        record.available_candidate_count = len(valid)
        if len(valid) + len(review_only) > 1:
            record.candidate_state = "AMBIGUOUS_LOCAL_EXACT_CANDIDATES"
            blocked.append(
                Blocked(
                    record.trait_id,
                    record.record_path,
                    "",
                    "MULTIPLE_EXACT_MATCHES",
                    f"{len(valid)} qualification-ready and {len(review_only)} review-only "
                    "local candidates; resolver selection required",
                )
            )
        elif valid:
            record.candidate_state = "LOCAL_EXACT_CANDIDATE"

        ranked = valid + review_only
        selected = ranked[:max_candidates_per_record] if max_candidates_per_record else ranked
        for rank, item in enumerate(selected, 1):
            profile = item.profile
            sequence = item.sequence
            assert profile is not None and sequence is not None
            scope = _scope(record)
            intervals = [{"start": start, "end": end} for start, end in item.intervals]
            row = {
                "schema_version": 1,
                "batch": (
                    "needs-grouped-interpro"
                    if item in review_only
                    else (
                        "ready-local"
                        if record.grounding_state == "NO_PROTEIN"
                        else "repair-existing-local"
                    )
                ),
                "candidate_status": (
                    "LOCATION_SOURCED"
                    if item in review_only
                    else "LOCATION_VERIFIED"
                    if scope == "LOCALIZED"
                    else "WHOLE_PROTEIN_EVIDENCE_VERIFIED"
                ),
                "qualification_status": "CANDIDATE_PROTEIN",
                "trait_id": record.trait_id,
                "record_path": record.record_path,
                "trait_axis": record.trait_axis,
                "trait_category": record.trait_category,
                "source_namespace": record.source_namespace,
                "protein_id": profile.protein_id,
                "protein_label": profile.protein_label,
                "taxon_id": profile.taxon_id,
                "taxon_label": profile.taxon_label,
                "sequence_length": len(sequence),
                "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
                "reviewed": profile.reviewed,
                "scope": scope,
                "intervals": intervals,
                "residue_positions": [],
                "source_trait_id": record.trait_id,
                "mapping_method": "INTERPRO_MATCH",
                "evidence_source": "InterPro",
                "source_release": str(interpro_release),
                "sequence_source": "UniProt",
                "sequence_release": str(uniprot_release),
                "evidence_tier": "A",
                # Reasons are promotion blockers, not general limitations.  All
                # blocking local checks have passed for rows emitted here.
                "reasons": sorted(set(item.failures)),
            }
            if scope == "LOCALIZED":
                row["coordinate_frame"] = "UNIPROT_CANONICAL"
            row["candidate_id"] = _candidate_id(row)
            row["_rank"] = rank
            candidates.append(row)
        record.candidate_count = len(selected)

        if not valid and not review_only:
            record.candidate_state = "NO_COMPLETE_LOCAL_CANDIDATE"

    candidates.sort(key=lambda row: (row["trait_id"], row["_rank"], row["protein_id"]))
    for row in candidates:
        del row["_rank"]
    return candidates, blocked


def _tsv_text(columns: Iterable[str], rows: Iterable[dict]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(columns), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _record_rows(records: list[RecordAudit]) -> Iterator[dict]:
    for record in records:
        yield {
            "trait_id": record.trait_id,
            "record_path": record.record_path,
            "trait_axis": record.trait_axis,
            "trait_category": record.trait_category,
            "source_namespace": record.source_namespace,
            "grounding_state": record.grounding_state,
            "inline_state": record.inline_state,
            "example_count": record.example_count,
            "valid_protein_count": len(record.valid_protein_ids),
            "qualified_example_count": record.qualified_example_count,
            "candidate_state": record.candidate_state,
            "candidate_count": record.candidate_count,
            "available_candidate_count": record.available_candidate_count,
            "blocked_count": record.blocked_count,
        }


def _summary_rows(records: list[RecordAudit]) -> Iterator[dict]:
    counts: collections.Counter[tuple[str, str, str, str, str]] = collections.Counter()
    for record in records:
        state = (record.grounding_state, record.inline_state, record.candidate_state)
        for group_by, value in (
            ("ALL", "ALL"),
            ("AXIS", record.trait_axis or "(missing)"),
            ("CATEGORY", record.trait_category or "(missing)"),
            ("SOURCE", record.source_namespace or "(missing)"),
        ):
            counts[(group_by, value, *state)] += 1
    order = {"ALL": 0, "AXIS": 1, "CATEGORY": 2, "SOURCE": 3}
    for key in sorted(counts, key=lambda k: (order[k[0]], k[1:])):
        group_by, value, grounding, inline, candidate = key
        yield {
            "group_by": group_by,
            "group_value": value,
            "grounding_state": grounding,
            "inline_state": inline,
            "candidate_state": candidate,
            "count": counts[key],
        }


def write_outputs(
    out: Path,
    records: list[RecordAudit],
    candidates: list[dict],
    blocked: list[Blocked],
) -> None:
    block_counts = collections.Counter((b.trait_id, b.record_path) for b in blocked)
    for record in records:
        record.blocked_count = block_counts[(record.trait_id, record.record_path)]
    blocked.sort(
        key=lambda row: (
            row.trait_id,
            row.record_path,
            row.protein_id,
            row.reason,
            row.detail,
        )
    )
    blocked_rows = [
        {
            "trait_id": row.trait_id,
            "record_path": row.record_path,
            "protein_id": row.protein_id,
            "reason": row.reason,
            "detail": row.detail,
        }
        for row in blocked
    ]
    candidate_text = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in candidates
    )
    _atomic_write(out / "summary.tsv", _tsv_text(SUMMARY_COLUMNS, _summary_rows(records)))
    _atomic_write(out / "records.tsv", _tsv_text(RECORD_COLUMNS, _record_rows(records)))
    _atomic_write(out / "candidates.jsonl", candidate_text)
    _atomic_write(out / "blocked.tsv", _tsv_text(BLOCKED_COLUMNS, blocked_rows))


def run_audit(
    traits: Path,
    residue_frame: Path,
    interpro_frame: Path,
    profiles: Path,
    out: Path,
    max_candidates_per_record: int = 3,
    *,
    protein_registry_path: Path = DEFAULT_PROTEIN_REGISTRY,
    evidence_registry_path: Path = DEFAULT_EVIDENCE_REGISTRY,
    membership_registry_path: Path = DEFAULT_MEMBERSHIP_REGISTRY,
    hierarchy_traits: Sequence[Path] | None = None,
) -> tuple[list[RecordAudit], list[dict], list[Blocked]]:
    if max_candidates_per_record < 0:
        raise AuditInputError("--max-candidates-per-record must be >= 0")
    records, blocked = scan_records(
        traits,
        protein_registry_path=protein_registry_path,
        evidence_registry_path=evidence_registry_path,
        membership_registry_path=membership_registry_path,
        hierarchy_traits=hierarchy_traits,
    )
    candidates, candidate_blocks = discover_candidates(
        records,
        residue_frame,
        interpro_frame,
        profiles,
        max_candidates_per_record,
    )
    blocked.extend(candidate_blocks)
    write_outputs(out, records, candidates, blocked)
    return records, candidates, blocked


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--traits", type=Path, required=True)
    ap.add_argument("--residue-frame", type=Path, required=True)
    ap.add_argument("--interpro-frame", type=Path, required=True)
    ap.add_argument("--profiles", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument(
        "--protein-registry",
        "--registry",
        dest="protein_registry",
        type=Path,
        default=DEFAULT_PROTEIN_REGISTRY,
        help=f"authoritative ProteinReference JSONL (default: {DEFAULT_PROTEIN_REGISTRY})",
    )
    ap.add_argument(
        "--evidence-registry",
        type=Path,
        default=DEFAULT_EVIDENCE_REGISTRY,
        help=f"authoritative GroundingEvidence JSONL (default: {DEFAULT_EVIDENCE_REGISTRY})",
    )
    ap.add_argument(
        "--membership-registry",
        type=Path,
        default=DEFAULT_MEMBERSHIP_REGISTRY,
        help=(
            f"content-addressed UniProt membership JSONL (default: {DEFAULT_MEMBERSHIP_REGISTRY})"
        ),
    )
    ap.add_argument(
        "--hierarchy-traits",
        nargs="+",
        type=Path,
        help="authoritative trait YAML roots for inheritance edges (default: --traits)",
    )
    ap.add_argument(
        "--max-candidates-per-record",
        type=int,
        default=3,
        help="retain this many ranked exact matches per record; 0 retains all (default: 3)",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        records, candidates, blocked = run_audit(
            args.traits,
            args.residue_frame,
            args.interpro_frame,
            args.profiles,
            args.out,
            args.max_candidates_per_record,
            protein_registry_path=args.protein_registry,
            evidence_registry_path=args.evidence_registry,
            membership_registry_path=args.membership_registry,
            hierarchy_traits=args.hierarchy_traits,
        )
    except AuditInputError as exc:
        print(f"audit input error: {exc}", file=sys.stderr)
        return 2
    states = collections.Counter(record.inline_state for record in records)
    print(f"records: {len(records):,}; candidates: {len(candidates):,}; blocked: {len(blocked):,}")
    for state in INLINE_STATES:
        print(f"  {state}: {states[state]:,}")
    print(f"wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
