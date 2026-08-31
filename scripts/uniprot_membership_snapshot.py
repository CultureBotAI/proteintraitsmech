#!/usr/bin/env python3
"""Strict helpers for release-pinned UniProt database membership snapshots.

The UniProt search query that discovers a candidate is not occurrence evidence.  A
membership becomes replayable only after an exact-accession response independently
returns the same database cross-reference together with the protein sequence and the
``x-uniprot-release`` header.  This module normalizes each such positive fact into one
content-addressed JSONL row.

The rows are deliberately independent of candidate IDs and rankings.  A resolver must
look up the exact ``(protein_id, source_trait_id, uniprot_release, sequence_sha256)``
tuple and must never infer membership from absence, a query string, or a generic hit.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
MEMBERSHIP_ID_PREFIX = "ug-membership:"
UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"

# REST return field, JSON ``database`` value, corpus CURIE prefix.  Gene3D is
# UniProt's CATH-backed cross-reference; SUPFAM is UniProt's SUPERFAMILY name.
XREF_SPECS: tuple[tuple[str, str, str], ...] = (
    ("xref_cdd", "CDD", "CDD"),
    ("xref_gene3d", "Gene3D", "CATH"),
    ("xref_hamap", "HAMAP", "HAMAP"),
    ("xref_interpro", "InterPro", "InterPro"),
    ("xref_ncbifam", "NCBIfam", "NCBIfam"),
    ("xref_panther", "PANTHER", "PANTHER"),
    ("xref_pfam", "Pfam", "Pfam"),
    ("xref_prints", "PRINTS", "PRINTS"),
    ("xref_prosite", "PROSITE", "PROSITE"),
    ("xref_sfld", "SFLD", "SFLD"),
    ("xref_smart", "SMART", "SMART"),
    ("xref_supfam", "SUPFAM", "SUPERFAMILY"),
)
XREF_FIELDS = tuple(spec[0] for spec in XREF_SPECS)
DATABASE_TO_NAMESPACE = {database: namespace for _, database, namespace in XREF_SPECS}

_UNIPROT = re.compile(
    r"^UniProtKB:([OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-([0-9]+))?$"
)
_RELEASE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_PAYLOAD_FIELDS = (
    "schema_version",
    "protein_id",
    "source_trait_id",
    "database",
    "database_id",
    "uniprot_release",
    "sequence_sha256",
    "api_endpoint",
    "database_cross_reference",
)
_ALLOWED_FIELDS = {"membership_id", *_PAYLOAD_FIELDS}


class MembershipSnapshotError(ValueError):
    """A membership snapshot is malformed, ambiguous, or not content-addressed."""


def _trait_local_id(database: str, database_id: str) -> str:
    """Map an exact provider ID to the corpus local ID without losing the raw ID.

    UniProt returns CATH-Gene3D superfamilies as ``G3DSA:<CATH-code>`` while
    ProteinTraitsMech keys the same identifiers as ``CATH:<CATH-code>``.  The
    original provider object and ``database_id`` remain unchanged in the row.
    """

    if database == "Gene3D" and database_id.startswith("G3DSA:"):
        local_id = database_id.removeprefix("G3DSA:")
        if not local_id:
            raise MembershipSnapshotError("Gene3D cross-reference has an empty G3DSA ID")
        return local_id
    return database_id


def canonical_json(value: Any) -> str:
    """Return deterministic JSON used by every membership digest."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _canonical_value(value: Any) -> Any:
    """Copy a JSON value into a deterministic, lossless Python shape."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MembershipSnapshotError("database cross-reference contains non-finite JSON")
        return value
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise MembershipSnapshotError("database cross-reference has a non-string key")
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    raise MembershipSnapshotError(
        f"database cross-reference contains non-JSON value {type(value).__name__}"
    )


def _normalise_cross_reference(value: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve the exact returned object while stabilizing property ordering."""

    normalized = _canonical_value(dict(value))
    properties = normalized.get("properties")
    if properties is not None:
        if not isinstance(properties, list) or any(
            not isinstance(item, dict) for item in properties
        ):
            raise MembershipSnapshotError(
                "database cross-reference properties must be a list of objects"
            )
        normalized["properties"] = sorted(properties, key=canonical_json)
    return normalized


def canonical_membership_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return the complete projection addressed by ``membership_id``."""

    return {field: value.get(field) for field in _PAYLOAD_FIELDS}


def membership_entry_sha256(value: Mapping[str, Any]) -> str:
    """Digest of the exact provider fact used as GroundingEvidence entry hash."""

    encoded = canonical_json(canonical_membership_payload(value)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_membership_id(value: Mapping[str, Any]) -> str:
    """Return the content address for one normalized membership fact."""

    return MEMBERSHIP_ID_PREFIX + membership_entry_sha256(value)


def _validate_membership(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["membership row is not an object"]
    errors: list[str] = []
    missing = sorted(_ALLOWED_FIELDS - set(value))
    unknown = sorted(set(value) - _ALLOWED_FIELDS)
    if missing:
        errors.append(f"missing fields {missing}")
    if unknown:
        errors.append(f"unknown fields {unknown}")
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    protein_id = value.get("protein_id")
    if not isinstance(protein_id, str) or _UNIPROT.fullmatch(protein_id) is None:
        errors.append("protein_id is not an exact UniProtKB accession")
    release = value.get("uniprot_release")
    if not isinstance(release, str) or _RELEASE.fullmatch(release) is None:
        errors.append("uniprot_release must have form YYYY_NN")
    sequence_sha = value.get("sequence_sha256")
    if not isinstance(sequence_sha, str) or _SHA256.fullmatch(sequence_sha) is None:
        errors.append("sequence_sha256 must be 64 lower-case hex digits")
    if value.get("api_endpoint") != UNIPROT_SEARCH:
        errors.append("api_endpoint is not the official UniProtKB search endpoint")

    database = value.get("database")
    database_id = value.get("database_id")
    namespace = DATABASE_TO_NAMESPACE.get(database) if isinstance(database, str) else None
    if namespace is None:
        errors.append(f"unsupported database {database!r}")
    if (
        not isinstance(database_id, str)
        or not database_id.strip()
        or database_id != database_id.strip()
    ):
        errors.append("database_id must be a non-empty, trimmed string")
    expected_trait: str | None = None
    if namespace and isinstance(database, str) and isinstance(database_id, str):
        try:
            expected_trait = f"{namespace}:{_trait_local_id(database, database_id)}"
        except MembershipSnapshotError as exc:
            errors.append(str(exc))
    if value.get("source_trait_id") != expected_trait:
        errors.append(
            f"source_trait_id must be the exact mapped database identifier {expected_trait!r}"
        )

    raw = value.get("database_cross_reference")
    if not isinstance(raw, dict):
        errors.append("database_cross_reference must be an object")
    else:
        try:
            normalized = _normalise_cross_reference(raw)
        except MembershipSnapshotError as exc:
            errors.append(str(exc))
        else:
            if normalized != raw:
                errors.append("database_cross_reference is not in canonical form")
            if raw.get("database") != database or raw.get("id") != database_id:
                errors.append("database/id do not match the preserved cross-reference")

    membership_id = value.get("membership_id")
    if not isinstance(membership_id, str) or not re.fullmatch(
        rf"{re.escape(MEMBERSHIP_ID_PREFIX)}[0-9a-f]{{64}}", membership_id
    ):
        errors.append("membership_id must be ug-membership: plus 64 lower-case hex digits")
    else:
        try:
            expected_id = compute_membership_id(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"membership payload cannot be canonicalized: {exc}")
        else:
            if membership_id != expected_id:
                errors.append(f"membership_id digest mismatch; expected {expected_id}")
    return errors


def extract_entry_memberships(
    entry: Mapping[str, Any],
    *,
    protein_id: str,
    sequence_sha256: str,
    uniprot_release: str,
) -> list[dict[str, Any]]:
    """Extract supported positive xref facts from one exact UniProt response entry."""

    if _UNIPROT.fullmatch(protein_id) is None:
        raise MembershipSnapshotError(f"invalid protein_id {protein_id!r}")
    if _SHA256.fullmatch(sequence_sha256) is None:
        raise MembershipSnapshotError("invalid sequence_sha256")
    if _RELEASE.fullmatch(uniprot_release) is None:
        raise MembershipSnapshotError("invalid uniprot_release")
    raw_cross_references = entry.get("uniProtKBCrossReferences", [])
    if raw_cross_references is None:
        raw_cross_references = []
    if not isinstance(raw_cross_references, list):
        raise MembershipSnapshotError("uniProtKBCrossReferences is not a list")

    by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for index, raw in enumerate(raw_cross_references):
        if not isinstance(raw, dict):
            raise MembershipSnapshotError(f"uniProtKBCrossReferences[{index}] is not an object")
        database = raw.get("database")
        namespace = DATABASE_TO_NAMESPACE.get(database) if isinstance(database, str) else None
        if namespace is None:
            continue
        database_id = raw.get("id")
        if not isinstance(database_id, str) or not database_id.strip():
            raise MembershipSnapshotError(
                f"{database} cross-reference at index {index} has no exact id"
            )
        if database_id != database_id.strip():
            raise MembershipSnapshotError(
                f"{database} cross-reference at index {index} has an untrimmed id"
            )
        normalized_xref = _normalise_cross_reference(raw)
        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "protein_id": protein_id,
            "source_trait_id": f"{namespace}:{_trait_local_id(database, database_id)}",
            "database": database,
            "database_id": database_id,
            "uniprot_release": uniprot_release,
            "sequence_sha256": sequence_sha256,
            "api_endpoint": UNIPROT_SEARCH,
            "database_cross_reference": normalized_xref,
        }
        row["membership_id"] = compute_membership_id(row)
        errors = _validate_membership(row)
        if errors:
            raise MembershipSnapshotError("; ".join(errors))
        key = (protein_id, row["source_trait_id"], uniprot_release, sequence_sha256)
        previous = by_key.get(key)
        if previous is not None and previous != row:
            raise MembershipSnapshotError(
                "ambiguous UniProt membership: multiple distinct cross-references for "
                f"{protein_id} / {row['source_trait_id']}"
            )
        by_key[key] = row
    return sorted(by_key.values(), key=lambda row: (row["source_trait_id"], row["membership_id"]))


def merge_memberships(*collections: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Validate, deduplicate, and deterministically sort membership rows."""

    by_id: dict[str, dict[str, Any]] = {}
    by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for collection in collections:
        for raw in collection:
            row = dict(raw)
            errors = _validate_membership(row)
            if errors:
                raise MembershipSnapshotError("; ".join(errors))
            membership_id = row["membership_id"]
            if membership_id in by_id and by_id[membership_id] != row:
                raise MembershipSnapshotError(f"membership ID collision for {membership_id}")
            key = (
                row["protein_id"],
                row["source_trait_id"],
                row["uniprot_release"],
                row["sequence_sha256"],
            )
            if key in by_key and by_key[key] != row:
                raise MembershipSnapshotError(
                    "ambiguous membership snapshot for "
                    f"{row['protein_id']} / {row['source_trait_id']}"
                )
            by_id[membership_id] = row
            by_key[key] = row
    return sorted(
        by_id.values(),
        key=lambda row: (
            row["protein_id"],
            row["source_trait_id"],
            row["uniprot_release"],
            row["sequence_sha256"],
            row["membership_id"],
        ),
    )


def dump_memberships(rows: Iterable[Mapping[str, Any]]) -> str:
    """Serialize a strict, deterministic one-fact-per-line snapshot."""

    normalized = merge_memberships(rows)
    return "".join(canonical_json(row) + "\n" for row in normalized)


def load_memberships(path: Path) -> list[dict[str, Any]]:
    """Load a snapshot fail-closed, including content and ambiguity checks."""

    if not path.is_file():
        raise MembershipSnapshotError(f"membership snapshot does not exist: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise MembershipSnapshotError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
            if not isinstance(value, dict):
                raise MembershipSnapshotError(f"{path}:{line_number}: row is not an object")
            errors = _validate_membership(value)
            if errors:
                raise MembershipSnapshotError(f"{path}:{line_number}: " + "; ".join(errors))
            rows.append(value)
    return merge_memberships(rows)


def find_exact_membership(
    rows: Iterable[Mapping[str, Any]],
    *,
    protein_id: str,
    source_trait_id: str,
    uniprot_release: str,
    sequence_sha256: str,
) -> dict[str, Any] | None:
    """Return one exact positive fact; missing or ambiguous evidence never qualifies."""

    matches = [
        dict(row)
        for row in rows
        if row.get("protein_id") == protein_id
        and row.get("source_trait_id") == source_trait_id
        and row.get("uniprot_release") == uniprot_release
        and row.get("sequence_sha256") == sequence_sha256
    ]
    if not matches:
        return None
    normalized = merge_memberships(matches)
    if len(normalized) != 1:
        raise MembershipSnapshotError(
            f"ambiguous exact membership for {protein_id} / {source_trait_id}"
        )
    return normalized[0]
