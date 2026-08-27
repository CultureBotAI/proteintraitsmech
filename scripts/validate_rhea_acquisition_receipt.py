#!/usr/bin/env python3
"""Verify one content-addressed Rhea provider-acquisition receipt, read-only.

The receipt binds the exact six-artifact release-141 acquisition plan, official
request/final URLs, successful status codes, bounded response-header
projections, acquisition timestamps, raw response body bytes, and the complete
Rhea direction/reaction/mapping semantics.  Verification performs no network
request and no write.

Passing proves internal content and semantic consistency of a producer's HTTPS
attestation.  It does not authenticate the producer, reconstruct TLS, prove
that the server returned the supplied bytes, bind a receipt into
GroundingEvidence, approve review, or authorize qualification.  The central
Rhea validator therefore remains unconditionally receipt-locked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import stage_rhea_uniprot_grounding as rhea_stage


SCHEMA_VERSION = 1
RECEIPT_KIND = "RHEA_PROVIDER_ACQUISITION_RECEIPT"
RECEIPT_ID_PREFIX = "rhea-provider-acquisition-receipt:"
VERIFICATION_KIND = "RHEA_PROVIDER_ACQUISITION_RECEIPT_VERIFICATION"
EXPECTED_MASTER_COUNT = 18_558
PROVENANCE_LIMIT = (
    "CONTENT_AND_SEMANTIC_BINDINGS_VERIFIED;HTTPS_ACQUISITION_ATTESTED_BY_"
    "PRODUCER_NOT_REEXECUTED_OR_AUTHENTICATED"
)
CENTRAL_BINDING_STATUS = "NOT_REPRESENTED_IN_GROUNDING_EVIDENCE_OR_CENTRAL_VALIDATOR"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = REPO_ROOT / "data/raw/rhea/rhea-provider-acquisition-receipt.json"

SOURCE_ROLES = (
    "mapping",
    "release_properties",
    "tsv_readme",
    "license",
    "directions",
    "reactions",
)
DEFAULT_SOURCE_PATHS: Mapping[str, Path] = {
    "mapping": rhea_stage.DEFAULT_MAPPING,
    "release_properties": rhea_stage.DEFAULT_RELEASE_PROPERTIES,
    "tsv_readme": rhea_stage.DEFAULT_TSV_README,
    "license": rhea_stage.DEFAULT_LICENSE,
    "directions": rhea_stage.DEFAULT_DIRECTIONS,
    "reactions": rhea_stage.DEFAULT_REACTIONS,
}

ACQUISITION_PLAN = rhea_stage.acquisition_plan()
ACQUISITION_PLAN_ID = str(ACQUISITION_PLAN["plan_id"])
ACQUISITION_PLAN_ROW_SHA256 = str(ACQUISITION_PLAN["plan_row_sha256"])
PLAN_ARTIFACTS = {str(row["role"]): dict(row) for row in ACQUISITION_PLAN["artifacts"]}
if tuple(PLAN_ARTIFACTS) != SOURCE_ROLES:  # pragma: no cover - import-time source drift
    raise RuntimeError("Rhea acquisition plan role order drifted")

DEFAULT_RECEIPT_RELATIVE = "data/raw/rhea/rhea-provider-acquisition-receipt.json"
_MAX_BYTES = {
    "receipt": 16 * 1024 * 1024,
    "mapping": 64 * 1024 * 1024,
    "release_properties": 16 * 1024,
    "tsv_readme": 4 * 1024 * 1024,
    "license": 4 * 1024 * 1024,
    "directions": 16 * 1024 * 1024,
    "reactions": 64 * 1024 * 1024,
}
_READ_CHUNK_BYTES = 1024 * 1024
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_SECOND_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_HEADER_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class RheaAcquisitionReceiptError(ValueError):
    """A receipt or bound source bundle fails the exact acquisition contract."""


@dataclass(frozen=True, slots=True)
class ArtifactCapture:
    """One bounded regular file captured through no-follow descriptors."""

    path: Path
    raw: bytes
    sha256: str
    size_bytes: int
    device: int
    inode: int
    mode_type: int
    mode_bits: int
    link_count: int
    mtime_ns: int
    ctime_ns: int

    @property
    def stable_identity(self) -> tuple[int, int, int, int, int, int, int, int, str]:
        return (
            self.device,
            self.inode,
            self.mode_type,
            self.mode_bits,
            self.link_count,
            self.size_bytes,
            self.mtime_ns,
            self.ctime_ns,
            self.sha256,
        )


@dataclass(frozen=True, slots=True)
class ReceiptPaths:
    """Canonical repository root, receipt, and six response-body paths."""

    repo_root: Path
    receipt: Path
    mapping: Path
    release_properties: Path
    tsv_readme: Path
    license: Path
    directions: Path
    reactions: Path

    def source_paths(self) -> dict[str, Path]:
        return {role: getattr(self, role) for role in SOURCE_ROLES}


def default_paths() -> ReceiptPaths:
    return ReceiptPaths(
        repo_root=REPO_ROOT,
        receipt=DEFAULT_RECEIPT,
        **DEFAULT_SOURCE_PATHS,
    )


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    raw = "".join(canonical_json(row) + "\n" for row in rows).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RheaAcquisitionReceiptError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise RheaAcquisitionReceiptError(f"non-finite JSON constant {value!r}")


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _relative_under(path: Path, root: Path, *, label: str) -> str:
    absolute = _lexical_absolute(path)
    root_absolute = _lexical_absolute(root)
    try:
        relative = absolute.relative_to(root_absolute)
    except ValueError as error:
        raise RheaAcquisitionReceiptError(
            f"{label}: path is outside canonical repository root: {absolute}"
        ) from error
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise RheaAcquisitionReceiptError(f"{label}: unsafe repository-relative path")
    return relative.as_posix()


def _entry_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _capture_regular_file(
    path: Path,
    *,
    label: str,
    max_bytes: int,
) -> ArtifactCapture:
    """Capture a nonempty single-link file via component-relative no-follow opens."""

    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory_only = getattr(os, "O_DIRECTORY", None)
    if (
        not isinstance(no_follow, int)
        or no_follow == 0
        or not isinstance(directory_only, int)
        or directory_only == 0
        or os.open not in getattr(os, "supports_dir_fd", set())
        or os.stat not in getattr(os, "supports_follow_symlinks", set())
    ):
        raise RheaAcquisitionReceiptError(
            f"{label}: platform lacks descriptor-relative no-follow support"
        )
    if type(max_bytes) is not int or max_bytes < 1:
        raise RheaAcquisitionReceiptError(f"{label}: invalid byte bound")

    lexical = _lexical_absolute(path)
    components = lexical.parts[1:]
    if not components or any(component in {"", ".", ".."} for component in components):
        raise RheaAcquisitionReceiptError(f"{label}: unsafe path components")

    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    directory_flags = os.O_RDONLY | directory_only | no_follow | close_on_exec
    file_flags = os.O_RDONLY | no_follow | close_on_exec | getattr(os, "O_NONBLOCK", 0)
    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        try:
            current = os.open(lexical.anchor, directory_flags)
        except OSError as error:
            raise RheaAcquisitionReceiptError(
                f"{label}: cannot safely open filesystem root: {error}"
            ) from error
        descriptors.append(current)
        for component in components[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                metadata = os.fstat(child)
            except OSError as error:
                raise RheaAcquisitionReceiptError(
                    f"{label}: cannot safely open directory component {component!r}: {error}"
                ) from error
            bindings.append((current, component, _entry_identity(metadata)))
            descriptors.append(child)
            current = child

        final_name = components[-1]
        try:
            descriptor = os.open(final_name, file_flags, dir_fd=current)
            before = os.fstat(descriptor)
        except OSError as error:
            raise RheaAcquisitionReceiptError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        descriptors.append(descriptor)
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise RheaAcquisitionReceiptError(f"{label}: input is not a regular file")
        if before.st_nlink != 1:
            raise RheaAcquisitionReceiptError(f"{label}: input must have exactly one hard link")
        if before.st_size < 1 or before.st_size > max_bytes:
            raise RheaAcquisitionReceiptError(
                f"{label}: input size {before.st_size} is outside 1..{max_bytes}"
            )

        chunks: list[bytes] = []
        captured = 0
        while True:
            try:
                chunk = os.read(descriptor, min(_READ_CHUNK_BYTES, max_bytes - captured + 1))
            except OSError as error:
                raise RheaAcquisitionReceiptError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured += len(chunk)
            if captured > max_bytes:
                raise RheaAcquisitionReceiptError(f"{label}: input exceeds {max_bytes} bytes")
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        before_identity = (
            before.st_dev,
            before.st_ino,
            stat.S_IFMT(before.st_mode),
            stat.S_IMODE(before.st_mode),
            before.st_nlink,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            stat.S_IFMT(after.st_mode),
            stat.S_IMODE(after.st_mode),
            after.st_nlink,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if len(raw) != before.st_size or before_identity != after_identity:
            raise RheaAcquisitionReceiptError(f"{label}: input changed during capture")
        for parent, component, expected in bindings:
            try:
                live = os.stat(component, dir_fd=parent, follow_symlinks=False)
            except OSError as error:
                raise RheaAcquisitionReceiptError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected:
                raise RheaAcquisitionReceiptError(
                    f"{label}: path component changed during capture: {component!r}"
                )
        return ArtifactCapture(
            path=lexical,
            raw=raw,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
            device=before.st_dev,
            inode=before.st_ino,
            mode_type=stat.S_IFMT(before.st_mode),
            mode_bits=stat.S_IMODE(before.st_mode),
            link_count=before.st_nlink,
            mtime_ns=before.st_mtime_ns,
            ctime_ns=before.st_ctime_ns,
        )
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _capture_sources(paths: ReceiptPaths) -> dict[str, ArtifactCapture]:
    captures = {
        role: _capture_regular_file(
            path,
            label=f"Rhea {role.replace('_', ' ')} response body",
            max_bytes=_MAX_BYTES[role],
        )
        for role, path in paths.source_paths().items()
    }
    identities = {(capture.device, capture.inode) for capture in captures.values()}
    if len(identities) != len(captures):
        raise RheaAcquisitionReceiptError("Rhea response-body paths alias one another")
    for role, capture in captures.items():
        observed = _relative_under(capture.path, paths.repo_root, label=f"Rhea {role}")
        expected = PLAN_ARTIFACTS[role]["target_path"]
        if observed != expected:
            raise RheaAcquisitionReceiptError(
                f"Rhea {role} path mismatch: expected {expected}, observed {observed}"
            )
    receipt_relative = _relative_under(paths.receipt, paths.repo_root, label="Rhea receipt")
    if receipt_relative != DEFAULT_RECEIPT_RELATIVE:
        raise RheaAcquisitionReceiptError(
            f"Rhea receipt path mismatch: expected {DEFAULT_RECEIPT_RELATIVE}, "
            f"observed {receipt_relative}"
        )
    return captures


def _recheck_capture(capture: ArtifactCapture, *, label: str, max_bytes: int) -> None:
    replay = _capture_regular_file(capture.path, label=label, max_bytes=max_bytes)
    if replay.stable_identity != capture.stable_identity or replay.raw != capture.raw:
        raise RheaAcquisitionReceiptError(f"{label}: input changed during verification")


def _load_receipt(capture: ArtifactCapture) -> dict[str, Any]:
    try:
        text = capture.raw.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise RheaAcquisitionReceiptError("receipt contains non-ASCII bytes") from error
    if not text.endswith("\n") or text.count("\n") != 1 or "\r" in text:
        raise RheaAcquisitionReceiptError("receipt must be one canonical LF-terminated JSON row")
    try:
        value = json.loads(
            text[:-1],
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (ValueError, RecursionError, RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionReceiptError(f"receipt is invalid JSON: {error}") from error
    if type(value) is not dict or canonical_json(value) + "\n" != text:
        raise RheaAcquisitionReceiptError("receipt is not one exact canonical JSON object")
    return value


def _utc_second(value: Any, *, label: str) -> datetime:
    if not isinstance(value, str) or _UTC_SECOND_RE.fullmatch(value) is None:
        raise RheaAcquisitionReceiptError(f"{label} must be an exact UTC-second timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise RheaAcquisitionReceiptError(f"{label} is not a real UTC timestamp") from error
    return parsed


def _producer(value: Any) -> dict[str, str]:
    if type(value) is not dict or set(value) != {"implementation", "implementation_sha256"}:
        raise RheaAcquisitionReceiptError("producer must have the exact v1 field set")
    implementation = value.get("implementation")
    digest = value.get("implementation_sha256")
    if (
        not isinstance(implementation, str)
        or not implementation.strip()
        or len(implementation) > 512
        or not isinstance(digest, str)
        or _SHA256_RE.fullmatch(digest) is None
    ):
        raise RheaAcquisitionReceiptError("producer implementation binding is invalid")
    return {"implementation": implementation, "implementation_sha256": digest}


def _header_projection(
    value: Any,
    *,
    role: str,
    body_size: int,
    started: datetime,
    completed: datetime,
) -> dict[str, str]:
    if type(value) is not dict or not value:
        raise RheaAcquisitionReceiptError(f"{role} response headers must be a nonempty object")
    headers: dict[str, str] = {}
    for key, item in value.items():
        if (
            not isinstance(key, str)
            or _HEADER_NAME_RE.fullmatch(key) is None
            or key != key.lower()
            or not isinstance(item, str)
            or not item
            or item != item.strip()
            or len(item) > 8192
            or any(ord(character) < 32 and character != "\t" for character in item)
        ):
            raise RheaAcquisitionReceiptError(f"{role} response header projection is invalid")
        headers[key] = item
    if "date" not in headers:
        raise RheaAcquisitionReceiptError(f"{role} response headers lack HTTP Date")
    try:
        http_date = parsedate_to_datetime(headers["date"])
    except (TypeError, ValueError) as error:
        raise RheaAcquisitionReceiptError(f"{role} HTTP Date is invalid") from error
    if http_date.tzinfo is None:
        raise RheaAcquisitionReceiptError(f"{role} HTTP Date lacks a timezone")
    http_date = http_date.astimezone(timezone.utc)
    tolerance = timedelta(minutes=5)
    if http_date < started - tolerance or http_date > completed + tolerance:
        raise RheaAcquisitionReceiptError(
            f"{role} HTTP Date falls outside the acquisition interval tolerance"
        )
    if "content-length" in headers:
        if not headers["content-length"].isdigit() or int(headers["content-length"]) != body_size:
            raise RheaAcquisitionReceiptError(
                f"{role} Content-Length does not equal captured response bytes"
            )
    return dict(sorted(headers.items()))


def _mapping_projection(row: rhea_stage.MappingRow) -> dict[str, Any]:
    return {
        "direction": row.direction,
        "master_id": row.master_id,
        "rhea_id": row.rhea_id,
        "source_line_number": row.line_number,
        "source_raw_line_sha256": row.raw_line_sha256,
        "uniprot_accession": row.accession,
    }


def _source_semantics(
    captures: Mapping[str, ArtifactCapture], *, enforce_release_contract: bool
) -> dict[str, Any]:
    release, release_date = rhea_stage.parse_release_properties(captures["release_properties"])
    if (
        release != rhea_stage.EXPECTED_RHEA_RELEASE
        or release_date != rhea_stage.EXPECTED_RHEA_RELEASE_DATE
    ):
        raise RheaAcquisitionReceiptError(
            f"Rhea release mismatch: observed {release}/{release_date}"
        )
    rhea_stage.validate_tsv_readme(captures["tsv_readme"])
    rhea_stage.validate_license(captures["license"])
    directions = rhea_stage.parse_directions(captures["directions"])
    reactions = rhea_stage.parse_reactions(captures["reactions"])
    if set(directions) != set(reactions):
        raise RheaAcquisitionReceiptError("Rhea direction and reaction master sets disagree")
    mapping = rhea_stage.parse_mapping(
        captures["mapping"], directions=directions, reactions=reactions
    )
    if enforce_release_contract:
        if len(directions) != EXPECTED_MASTER_COUNT:
            raise RheaAcquisitionReceiptError(
                f"release-141 master count {len(directions)} != {EXPECTED_MASTER_COUNT}"
            )
        for role in ("directions", "reactions"):
            expected = rhea_stage.CURRENT_SOURCE_SHA256[role]
            if expected is None or captures[role].sha256 != expected:
                raise RheaAcquisitionReceiptError(
                    f"release-141 {role} digest does not match the pinned source bytes"
                )

    mapping_rows = [_mapping_projection(row) for row in mapping]
    master_ids = sorted(directions, key=int)
    mapped_master_ids = sorted({row.master_id for row in mapping}, key=int)
    direction_counts = Counter(row.direction for row in mapping)
    return {
        "direction_master_count": len(directions),
        "direction_master_ids_sha256": value_sha256(master_ids),
        "direction_reaction_master_sets_equal": True,
        "license_contract": "CC BY 4.0",
        "mapping_direction_counts": dict(sorted(direction_counts.items())),
        "mapping_master_count": len(mapped_master_ids),
        "mapping_master_ids_sha256": value_sha256(mapped_master_ids),
        "mapping_physical_row_count": len(mapping),
        "mapping_rows_sha256": rows_sha256(mapping_rows),
        "mapping_unique_trait_protein_pair_count": len(
            {(row.master_id, row.accession) for row in mapping}
        ),
        "mapping_unique_uniprot_accession_count": len({row.accession for row in mapping}),
        "provider_release": release,
        "provider_release_date": release_date,
        "reaction_master_count": len(reactions),
        "reaction_master_ids_sha256": value_sha256(master_ids),
        "release_141_pinned_catalogue_contract_enforced": enforce_release_contract,
        "tsv_cross_reference_contract_verified": True,
    }


def _response_rows(
    *,
    captures: Mapping[str, ArtifactCapture],
    attestations: Sequence[Mapping[str, Any]],
    started: datetime,
    completed: datetime,
    enforce_release_contract: bool,
) -> list[dict[str, Any]]:
    if type(attestations) not in {list, tuple} or len(attestations) != len(SOURCE_ROLES):
        raise RheaAcquisitionReceiptError("response attestations must cover all six roles")
    rows: list[dict[str, Any]] = []
    prior_received = started
    for role, attestation in zip(SOURCE_ROLES, attestations, strict=True):
        if type(attestation) is not dict or set(attestation) != {
            "role",
            "response_url",
            "response_status",
            "response_received_at_utc",
            "response_header_projection",
        }:
            raise RheaAcquisitionReceiptError(
                f"{role} response attestation does not have the exact v1 field set"
            )
        if attestation.get("role") != role:
            raise RheaAcquisitionReceiptError(f"response role order mismatch at {role}")
        expected_url = PLAN_ARTIFACTS[role]["url"]
        if attestation.get("response_url") != expected_url:
            raise RheaAcquisitionReceiptError(f"{role} final response URL is not canonical")
        if (
            type(attestation.get("response_status")) is not int
            or attestation.get("response_status") != 200
        ):
            raise RheaAcquisitionReceiptError(f"{role} response status is not integer 200")
        received = _utc_second(
            attestation.get("response_received_at_utc"),
            label=f"{role} response_received_at_utc",
        )
        if received < prior_received or received > completed:
            raise RheaAcquisitionReceiptError(
                f"{role} response timestamp is outside ordered acquisition interval"
            )
        prior_received = received
        capture = captures[role]
        headers = _header_projection(
            attestation.get("response_header_projection"),
            role=role,
            body_size=capture.size_bytes,
            started=started,
            completed=completed,
        )
        expected_digest = PLAN_ARTIFACTS[role]["expected_sha256"]
        if (
            enforce_release_contract
            and expected_digest is not None
            and capture.sha256 != expected_digest
        ):
            raise RheaAcquisitionReceiptError(
                f"{role} response bytes disagree with acquisition-plan digest"
            )
        rows.append(
            {
                "artifact_target_path": PLAN_ARTIFACTS[role]["target_path"],
                "request_url": expected_url,
                "response_body_sha256": capture.sha256,
                "response_body_sha256_basis": "HTTP_RESPONSE_BODY_BYTES",
                "response_body_size_bytes": capture.size_bytes,
                "response_header_projection": headers,
                "response_header_projection_sha256": value_sha256(headers),
                "response_received_at_utc": attestation["response_received_at_utc"],
                "response_status": 200,
                "response_url": expected_url,
                "role": role,
            }
        )
    return rows


def _build_expected_receipt(
    *,
    captures: Mapping[str, ArtifactCapture],
    acquisition_started_at_utc: Any,
    acquisition_completed_at_utc: Any,
    response_attestations: Sequence[Mapping[str, Any]],
    producer: Any,
    enforce_release_contract: bool,
) -> dict[str, Any]:
    started = _utc_second(acquisition_started_at_utc, label="acquisition_started_at_utc")
    completed = _utc_second(acquisition_completed_at_utc, label="acquisition_completed_at_utc")
    if completed < started:
        raise RheaAcquisitionReceiptError("acquisition completed before it started")
    producer_value = _producer(producer)
    response_rows = _response_rows(
        captures=captures,
        attestations=response_attestations,
        started=started,
        completed=completed,
        enforce_release_contract=enforce_release_contract,
    )
    semantics = _source_semantics(captures, enforce_release_contract=enforce_release_contract)
    receipt: dict[str, Any] = {
        "acquisition_completed_at_utc": acquisition_completed_at_utc,
        "acquisition_mode": "HTTPS",
        "acquisition_plan_id": ACQUISITION_PLAN_ID,
        "acquisition_plan_row_sha256": ACQUISITION_PLAN_ROW_SHA256,
        "acquisition_started_at_utc": acquisition_started_at_utc,
        "completion_status": "SUCCESSFUL_HTTPS_RESPONSES_ATTESTED_BY_PRODUCER",
        "grounding_boundary": {
            "central_receipt_binding_status": CENTRAL_BINDING_STATUS,
            "grounding_eligible": False,
            "promotion_authorized": False,
            "provider_authenticity_proven": False,
        },
        "network_action_performed": True,
        "producer": producer_value,
        "provenance_limit": PROVENANCE_LIMIT,
        "provider": "Rhea",
        "provider_release": rhea_stage.EXPECTED_RHEA_RELEASE,
        "provider_release_date": rhea_stage.EXPECTED_RHEA_RELEASE_DATE,
        "receipt_kind": RECEIPT_KIND,
        "response_count": len(response_rows),
        "response_rows": response_rows,
        "response_rows_sha256": value_sha256(response_rows),
        "schema_version": SCHEMA_VERSION,
        "source_semantics": semantics,
        "source_semantics_sha256": value_sha256(semantics),
    }
    receipt["receipt_id"] = RECEIPT_ID_PREFIX + value_sha256(receipt)
    return receipt


def build_receipt_value(
    *,
    paths: ReceiptPaths,
    acquisition_started_at_utc: str,
    acquisition_completed_at_utc: str,
    response_attestations: Sequence[Mapping[str, Any]],
    producer: Mapping[str, Any],
    enforce_release_contract: bool = True,
) -> dict[str, Any]:
    """Build, but never write, the exact value a future controlled runner must install."""

    captures = _capture_sources(paths)
    expected = _build_expected_receipt(
        captures=captures,
        acquisition_started_at_utc=acquisition_started_at_utc,
        acquisition_completed_at_utc=acquisition_completed_at_utc,
        response_attestations=response_attestations,
        producer=producer,
        enforce_release_contract=enforce_release_contract,
    )
    for role, capture in captures.items():
        _recheck_capture(
            capture,
            label=f"Rhea {role} receipt-build final recheck",
            max_bytes=_MAX_BYTES[role],
        )
    return expected


def _receipt_attestations(value: Any) -> list[dict[str, Any]]:
    if type(value) is not list:
        raise RheaAcquisitionReceiptError("receipt response_rows is not a list")
    attestations: list[dict[str, Any]] = []
    for row in value:
        if type(row) is not dict:
            raise RheaAcquisitionReceiptError("receipt response row is not an object")
        attestations.append(
            {
                "response_header_projection": row.get("response_header_projection"),
                "response_received_at_utc": row.get("response_received_at_utc"),
                "response_status": row.get("response_status"),
                "response_url": row.get("response_url"),
                "role": row.get("role"),
            }
        )
    return attestations


def verify_receipt(
    *,
    paths: ReceiptPaths,
    enforce_release_contract: bool = True,
) -> dict[str, Any]:
    """Strictly replay one installed receipt without network access or writes."""

    receipt_capture = _capture_regular_file(
        paths.receipt, label="Rhea acquisition receipt", max_bytes=_MAX_BYTES["receipt"]
    )
    captures = _capture_sources(paths)
    if (receipt_capture.device, receipt_capture.inode) in {
        (capture.device, capture.inode) for capture in captures.values()
    }:
        raise RheaAcquisitionReceiptError("receipt aliases a response-body artifact")
    supplied = _load_receipt(receipt_capture)
    expected_fields = {
        "acquisition_completed_at_utc",
        "acquisition_mode",
        "acquisition_plan_id",
        "acquisition_plan_row_sha256",
        "acquisition_started_at_utc",
        "completion_status",
        "grounding_boundary",
        "network_action_performed",
        "producer",
        "provenance_limit",
        "provider",
        "provider_release",
        "provider_release_date",
        "receipt_id",
        "receipt_kind",
        "response_count",
        "response_rows",
        "response_rows_sha256",
        "schema_version",
        "source_semantics",
        "source_semantics_sha256",
    }
    if set(supplied) != expected_fields:
        raise RheaAcquisitionReceiptError("receipt does not have the exact v1 field set")
    expected = _build_expected_receipt(
        captures=captures,
        acquisition_started_at_utc=supplied.get("acquisition_started_at_utc"),
        acquisition_completed_at_utc=supplied.get("acquisition_completed_at_utc"),
        response_attestations=_receipt_attestations(supplied.get("response_rows")),
        producer=supplied.get("producer"),
        enforce_release_contract=enforce_release_contract,
    )
    if canonical_json(supplied) != canonical_json(expected):
        raise RheaAcquisitionReceiptError(
            "receipt does not reproduce the independently derived acquisition binding"
        )

    _recheck_capture(
        receipt_capture,
        label="Rhea acquisition receipt final recheck",
        max_bytes=_MAX_BYTES["receipt"],
    )
    for role, capture in captures.items():
        _recheck_capture(
            capture,
            label=f"Rhea {role} final recheck",
            max_bytes=_MAX_BYTES[role],
        )

    semantics = expected["source_semantics"]
    return {
        "artifact_and_semantic_bindings_verified": True,
        "artifact_kind": VERIFICATION_KIND,
        "central_grounding_eligible": False,
        "central_receipt_binding_status": CENTRAL_BINDING_STATUS,
        "network_action_performed_by_verifier": False,
        "producer_authenticated": False,
        "provenance_limit": PROVENANCE_LIMIT,
        "provider": "Rhea",
        "provider_release": rhea_stage.EXPECTED_RHEA_RELEASE,
        "receipt_id": supplied["receipt_id"],
        "response_count": len(expected["response_rows"]),
        "schema_version": SCHEMA_VERSION,
        "source_mapping_physical_row_count": semantics["mapping_physical_row_count"],
        "source_reaction_master_count": semantics["reaction_master_count"],
        "status": "PASS_RECEIPT_CONTENT_AND_SEMANTIC_BINDINGS_ONLY",
        "writes_performed": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--mapping", type=Path, default=rhea_stage.DEFAULT_MAPPING)
    parser.add_argument(
        "--release-properties", type=Path, default=rhea_stage.DEFAULT_RELEASE_PROPERTIES
    )
    parser.add_argument("--tsv-readme", type=Path, default=rhea_stage.DEFAULT_TSV_README)
    parser.add_argument("--license", type=Path, default=rhea_stage.DEFAULT_LICENSE)
    parser.add_argument("--directions", type=Path, default=rhea_stage.DEFAULT_DIRECTIONS)
    parser.add_argument("--reactions", type=Path, default=rhea_stage.DEFAULT_REACTIONS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    paths = ReceiptPaths(
        repo_root=args.repo_root,
        receipt=args.receipt,
        mapping=args.mapping,
        release_properties=args.release_properties,
        tsv_readme=args.tsv_readme,
        license=args.license,
        directions=args.directions,
        reactions=args.reactions,
    )
    try:
        verification = verify_receipt(paths=paths)
    except (OSError, RheaAcquisitionReceiptError, rhea_stage.RheaStageError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(canonical_json(verification) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
