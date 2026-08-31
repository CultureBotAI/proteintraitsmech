#!/usr/bin/env python3
"""Plan and build release-stamped UniProt snapshots from selected candidates.

The candidate ledger is intentionally not a metadata authority.  This command
deduplicates the exact UniProtKB accessions (including isoforms) in one named batch,
retrieves them from the official UniProt REST search endpoint in bounded batches, and
captures ``x-uniprot-release`` from every response.  It writes only references whose
accession, metadata, sequence, checksum, and sequence version validate.  From that
same response it also writes content-addressed UniProt database-cross-reference facts;
these are the replayable provider input for exact ``SOURCE_MEMBERSHIP`` resolution.
Every accession-specific response failure is retained in a deterministic blocked TSV.

Dry-run is a no-write, no-network operation which emits one canonical, content-addressed
request plan to stdout.  The plan binds the selector manifest, canonical candidate
ledger, exact requests, and all staging output paths.  Network access and output writes
require both ``--apply`` and an exact saved ``--request-plan``.  The plan is rederived
before the first response and immediately before output installation.  The receipt is
installed last and is the generation boundary for the three normalized outputs.

Tests and reproducible offline reviews can provide ``--offline-responses`` instead of
using the network.  There is no stale-release override: a missing, malformed, mixed, or
unexpected release aborts the run before any existing output is replaced.  This script
has no trait-record or durable-grounding write route.

Examples::

    uv run python scripts/fetch_uniprot_registry.py \
      --queue B.candidates.jsonl --selector-manifest B.manifest.json \
      --batch B --expect-release 2026_02 > B.fetch-plan.json

    uv run python scripts/fetch_uniprot_registry.py \
      --queue B.candidates.jsonl --selector-manifest B.manifest.json \
      --batch B --expect-release 2026_02 --request-plan B.fetch-plan.json --apply
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import secrets
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from uniprot_membership_snapshot import (
    MembershipSnapshotError,
    XREF_FIELDS,
    canonical_json as canonical_membership_json,
    dump_memberships,
    extract_entry_memberships,
    merge_memberships,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "uniprot-grounding"
DEFAULT_REGISTRY = DEFAULT_OUT_DIR / "uniprot_registry.jsonl"
DEFAULT_BLOCKED = DEFAULT_OUT_DIR / "uniprot_registry_blocked.tsv"
DEFAULT_MEMBERSHIPS = DEFAULT_OUT_DIR / "uniprot_memberships.jsonl"
DEFAULT_RECEIPT = DEFAULT_OUT_DIR / "uniprot_fetch_receipt.json"

PLAN_SCHEMA_VERSION = 1
PLAN_KIND = "UNIPROT_REGISTRY_FETCH_REQUEST_PLAN"
RECEIPT_SCHEMA_VERSION = 1
RECEIPT_KIND = "UNIPROT_REGISTRY_FETCH_RECEIPT"
PENDING_KIND = "UNIPROT_REGISTRY_FETCH_GENERATION_PENDING"
PLAN_ID_PREFIX = "uniprot-registry-fetch-plan:"
RECEIPT_ID_PREFIX = "uniprot-registry-fetch-receipt:"
PENDING_ID_PREFIX = "uniprot-registry-fetch-pending:"

SELECTOR_MANIFEST_SCHEMA_VERSION = 6
SELECTOR_V6_INVARIANTS = frozenset(
    {
        "shard_is_nonempty",
        "unique_selected_record_groups_within_shard",
        "every_available_record_matches_shard",
        "all_selected_records_are_available_in_shard",
        "no_one_approved_reviewed_record_in_residual_queue",
        "every_excluded_source_slice_record_is_approved_or_deferred_unchanged",
        "all_non_deferred_all_rejected_source_slice_records_remain_in_residual_queue",
        "all_deferred_unchanged_source_slice_records_are_absent_from_residual_queue",
        "all_reopened_changed_source_slice_records_remain_in_residual_queue",
        "all_rejected_deferral_states_partition_when_enabled",
        "all_deferred_and_reopened_record_hash_classifications_are_exact",
        "all_repeated_review_histories_are_coalesced_all_rejected",
        "all_resolved_all_rejected_histories_are_terminal_approved_exclusions",
        "all_selected_candidate_alternatives_retained",
        "within_record_cap",
        "shard_source_minima_satisfied",
        "all_shard_special_cases_selected",
    }
)
SELECTOR_DOWNSTREAM_REQUIREMENTS = frozenset(
    {
        "all_alternatives_must_receive_an_explicit_review_decision",
        "at_most_one_approved_candidate_per_record",
    }
)

UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"
RETURN_FIELDS = (
    "accession",
    "id",
    "protein_name",
    "organism_name",
    "organism_id",
    "reviewed",
    "sequence",
    "sequence_version",
    *XREF_FIELDS,
)
USER_AGENT = "ProteinTraitsMech-UniProt-registry/1.0"
REQUEST_HEADERS = {"Accept": "application/json", "User-Agent": USER_AGENT}
RESPONSE_PROVENANCE_HEADERS = (
    "x-uniprot-release",
    "content-type",
    "content-length",
    "etag",
    "last-modified",
    "link",
)

_UNIPROT = re.compile(
    r"^UniProtKB:([OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-([0-9]+))?$"
)
_ACCESSION = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-([0-9]+))?$"
)
_RELEASE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SEQUENCE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")

_BLOCKED_COLUMNS = (
    "protein_id",
    "accession",
    "candidate_count",
    "candidate_ids",
    "trait_ids",
    "reason",
    "detail",
)


class RegistryBuildError(RuntimeError):
    """A run-wide invariant failed; existing outputs must remain untouched."""


@dataclass(frozen=True)
class FetchResponse:
    requested: tuple[str, ...]
    release: str | None
    results: tuple[dict[str, Any], ...]
    request_url: str
    response_url: str | None
    status: int
    body_sha256: str
    body_size_bytes: int
    body_sha256_basis: str
    header_projection: dict[str, str]
    acquisition_mode: str
    offline_response_index: int | None


@dataclass(frozen=True)
class CapturedArtifact:
    path: Path
    sha256: str
    size_bytes: int
    raw: bytes
    device: int
    inode: int


@dataclass(frozen=True)
class PreparedPlan:
    plan: dict[str, Any]
    targets: tuple[Target, ...]
    queue: CapturedArtifact
    selector_manifest: CapturedArtifact
    offline_fixture: CapturedArtifact | None


@dataclass(frozen=True)
class Target:
    protein_id: str
    accession: str
    candidates: tuple[dict[str, Any], ...]
    expected_length: int
    expected_sha256: str
    expected_release: str


@dataclass
class BoundOutput:
    role: str
    path: Path
    leaf_name: str
    parent_descriptor: int
    directory_bindings: list[tuple[int, str, int, os.stat_result]]
    existing_identity: tuple[int, int] | None


@dataclass
class BoundOutputs:
    by_role: dict[str, BoundOutput]

    def close(self) -> None:
        for output in self.by_role.values():
            for _parent, _component, descriptor, _metadata in reversed(output.directory_bindings):
                os.close(descriptor)
            output.directory_bindings.clear()


@dataclass(frozen=True)
class VerifiedFetchReceipt:
    receipt: dict[str, Any]
    request_plan: dict[str, Any]
    receipt_sha256: str
    request_plan_sha256: str
    output_sha256s: dict[str, str]
    candidate_jsonl_bytes: bytes
    protein_registry_jsonl_bytes: bytes
    membership_registry_jsonl_bytes: bytes


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _value_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise RegistryBuildError(f"JSON object contains duplicate key {key!r}")
        value[key] = item
    return value


def _load_json_unique(text: str, *, source: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_unique_object)
    except RegistryBuildError as exc:
        raise RegistryBuildError(f"{source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryBuildError(f"{source}: invalid JSON: {exc}") from exc


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _descriptor_safety_flags() -> tuple[int, int]:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory_only = getattr(os, "O_DIRECTORY", None)
    supports_dir_fd = getattr(os, "supports_dir_fd", set())
    supports_follow_symlinks = getattr(os, "supports_follow_symlinks", set())
    if (
        not isinstance(no_follow, int)
        or no_follow == 0
        or not isinstance(directory_only, int)
        or directory_only == 0
        or os.open not in supports_dir_fd
        or os.stat not in supports_dir_fd
        or os.stat not in supports_follow_symlinks
        or os.unlink not in supports_dir_fd
        or os.rename not in supports_dir_fd
    ):
        raise RegistryBuildError(
            "platform lacks required O_NOFOLLOW/O_DIRECTORY/dir_fd filesystem safety"
        )
    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    return (
        os.O_RDONLY | directory_only | no_follow | close_on_exec,
        os.O_RDONLY | no_follow | close_on_exec,
    )


def _stat_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _bind_parent_components(
    path: Path,
    *,
    description: str,
    test_hook: Callable[[str], None] | None = None,
) -> tuple[Path, list[tuple[int, str, int, os.stat_result]]]:
    lexical = _lexical_absolute(path)
    if lexical.anchor != os.path.sep or len(lexical.parts) < 2:
        raise RegistryBuildError(f"{description} must be an absolute POSIX path: {path}")
    directory_flags, _file_flags = _descriptor_safety_flags()
    bindings: list[tuple[int, str, int, os.stat_result]] = []
    try:
        root_descriptor = os.open(lexical.anchor, directory_flags)
        root_metadata = os.fstat(root_descriptor)
        if not stat.S_ISDIR(root_metadata.st_mode):  # pragma: no cover - POSIX root
            raise RegistryBuildError(f"{description} path anchor is not a directory")
        bindings.append((-1, lexical.anchor, root_descriptor, root_metadata))
        parent_descriptor = root_descriptor
        for component in lexical.parts[1:-1]:
            descriptor = os.open(component, directory_flags, dir_fd=parent_descriptor)
            metadata = os.fstat(descriptor)
            if not stat.S_ISDIR(metadata.st_mode):
                os.close(descriptor)
                raise RegistryBuildError(
                    f"{description} path component is not a directory: {component!r}"
                )
            bindings.append((parent_descriptor, component, descriptor, metadata))
            parent_descriptor = descriptor
        if test_hook is not None:
            test_hook("PARENT_DIRECTORIES_BOUND")
        return lexical, bindings
    except RegistryBuildError:
        for _parent, _component, descriptor, _metadata in reversed(bindings):
            os.close(descriptor)
        raise
    except OSError as exc:
        for _parent, _component, descriptor, _metadata in reversed(bindings):
            os.close(descriptor)
        raise RegistryBuildError(
            f"cannot bind {description} path without following symlinks ({lexical}): {exc}"
        ) from exc


def _assert_parent_path_binding(
    lexical: Path,
    bindings: Sequence[tuple[int, str, int, os.stat_result]],
    *,
    description: str,
) -> None:
    try:
        root = bindings[0]
        if _stat_identity(os.fstat(root[2])) != _stat_identity(root[3]):
            raise RegistryBuildError(f"bound {description} root descriptor changed")
        if _stat_identity(os.stat(lexical.anchor, follow_symlinks=False)) != _stat_identity(
            root[3]
        ):
            raise RegistryBuildError(f"{description} parent path binding changed")
        for parent_descriptor, component, descriptor, expected in bindings[1:]:
            current = os.stat(component, dir_fd=parent_descriptor, follow_symlinks=False)
            if _stat_identity(os.fstat(descriptor)) != _stat_identity(expected):
                raise RegistryBuildError(f"bound {description} directory descriptor changed")
            if _stat_identity(current) != _stat_identity(expected):
                raise RegistryBuildError(f"{description} parent path binding changed")
    except RegistryBuildError:
        raise
    except OSError as exc:
        raise RegistryBuildError(f"cannot recheck bound {description} parent: {exc}") from exc


def _capture(
    path: Path,
    *,
    description: str,
    _test_hook: Callable[[str], None] | None = None,
) -> CapturedArtifact:
    lexical_path, bindings = _bind_parent_components(
        path, description=description, test_hook=_test_hook
    )
    parent_descriptor = bindings[-1][2]
    _directory_flags, file_flags = _descriptor_safety_flags()
    descriptor: int | None = None
    try:
        descriptor = os.open(lexical_path.name, file_flags, dir_fd=parent_descriptor)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RegistryBuildError(
                f"{description} must be a regular non-symlink file: {lexical_path}"
            )
        if _test_hook is not None:
            _test_hook("FILE_BOUND")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        _assert_parent_path_binding(lexical_path, bindings, description=description)
        current = os.stat(
            lexical_path.name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if _stat_identity(current) != _stat_identity(before):
            raise RegistryBuildError(f"{description} path binding changed while being read")
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise RegistryBuildError(f"{description} changed while being read: {lexical_path}")
        raw = b"".join(chunks)
        return CapturedArtifact(
            path=lexical_path,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
            raw=raw,
            device=before.st_dev,
            inode=before.st_ino,
        )
    except RegistryBuildError:
        raise
    except OSError as exc:
        raise RegistryBuildError(
            f"cannot capture {description} without following symlinks {lexical_path}: {exc}"
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for _parent, _component, bound_descriptor, _metadata in reversed(bindings):
            os.close(bound_descriptor)


def _capture_bound_output(output: BoundOutput, *, description: str) -> CapturedArtifact:
    """Read one output leaf relative to its retained, plan-matched parent descriptor."""

    _assert_bound_output_parent(output)
    _directory_flags, file_flags = _descriptor_safety_flags()
    descriptor: int | None = None
    try:
        descriptor = os.open(
            output.leaf_name,
            file_flags,
            dir_fd=output.parent_descriptor,
        )
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RegistryBuildError(f"{description} is not a regular non-symlink file")
        identity = (before.st_dev, before.st_ino)
        if output.existing_identity is None or identity != output.existing_identity:
            raise RegistryBuildError(f"{description} changed after output binding")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        named = os.stat(
            output.leaf_name,
            dir_fd=output.parent_descriptor,
            follow_symlinks=False,
        )
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise RegistryBuildError(f"{description} changed while being read")
        if _stat_identity(named) != _stat_identity(before):
            raise RegistryBuildError(f"{description} leaf binding changed while being read")
        _assert_bound_output_parent(output)
        raw = b"".join(chunks)
        return CapturedArtifact(
            path=output.path,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
            raw=raw,
            device=before.st_dev,
            inode=before.st_ino,
        )
    except RegistryBuildError:
        raise
    except OSError as exc:
        raise RegistryBuildError(f"cannot read descriptor-bound {description}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _artifact_projection(artifact: CapturedArtifact) -> dict[str, Any]:
    return {
        "path": str(artifact.path),
        "sha256": artifact.sha256,
        "size_bytes": artifact.size_bytes,
    }


def _output_path(path: Path) -> str:
    return str(_lexical_absolute(path))


def _is_below(path: Path, parent: Path) -> bool:
    try:
        _lexical_absolute(path).relative_to(_lexical_absolute(parent))
    except ValueError:
        return False
    return True


def _validate_staging_output_paths(paths: Mapping[str, Path]) -> None:
    resolved = {_output_path(path) for path in paths.values()}
    if len(resolved) != len(paths):
        raise RegistryBuildError(
            "registry, membership, blocked, and receipt paths must be distinct"
        )
    protected = (REPO_ROOT / "data" / "traits", REPO_ROOT / "data" / "grounding")
    for role, path in paths.items():
        if any(_is_below(path, root) for root in protected):
            raise RegistryBuildError(f"{role} output may not target protected trait/grounding data")
        if _is_below(path, REPO_ROOT) and not _is_below(path, DEFAULT_OUT_DIR):
            raise RegistryBuildError(
                f"{role} output inside the repository must remain below {DEFAULT_OUT_DIR}"
            )


def _bind_output_paths(
    paths: Mapping[str, Path],
    *,
    forbidden_artifacts: Sequence[CapturedArtifact] = (),
    _test_hook: Callable[[str, str], None] | None = None,
) -> BoundOutputs:
    outputs: dict[str, BoundOutput] = {}
    output_keys: set[tuple[int, int, str]] = set()
    existing_file_identities: set[tuple[int, int]] = set()
    forbidden_identities = {(item.device, item.inode) for item in forbidden_artifacts}
    try:
        for role, path in paths.items():
            lexical, bindings = _bind_parent_components(
                path,
                description=f"{role} output",
                test_hook=(
                    (lambda event, role=role: _test_hook(role, event))
                    if _test_hook is not None
                    else None
                ),
            )
            parent_descriptor = bindings[-1][2]
            parent_metadata = os.fstat(parent_descriptor)
            output = BoundOutput(
                role=role,
                path=lexical,
                leaf_name=lexical.name,
                parent_descriptor=parent_descriptor,
                directory_bindings=bindings,
                existing_identity=None,
            )
            outputs[role] = output
            key = (parent_metadata.st_dev, parent_metadata.st_ino, lexical.name)
            if key in output_keys:
                raise RegistryBuildError("staging output paths alias the same parent/name")
            output_keys.add(key)
            existing_identity: tuple[int, int] | None = None
            try:
                existing = os.stat(
                    lexical.name,
                    dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                pass
            else:
                if not stat.S_ISREG(existing.st_mode):
                    raise RegistryBuildError(
                        f"{role} output exists but is not a regular non-symlink file: {lexical}"
                    )
                existing_identity = (existing.st_dev, existing.st_ino)
                if existing_identity in forbidden_identities:
                    raise RegistryBuildError(f"{role} output aliases a bound input artifact")
                if existing_identity in existing_file_identities:
                    raise RegistryBuildError("existing staging outputs alias the same inode")
                existing_file_identities.add(existing_identity)
            output.existing_identity = existing_identity
        return BoundOutputs(outputs)
    except Exception:
        BoundOutputs(outputs).close()
        raise


def _assert_bound_output_parent(output: BoundOutput) -> None:
    _assert_parent_path_binding(
        output.path,
        output.directory_bindings,
        description=f"{output.role} output",
    )


def _validate_output_bindings(
    paths: Mapping[str, Path], *, forbidden_artifacts: Sequence[CapturedArtifact]
) -> dict[str, dict[str, Any]]:
    bound = _bind_output_paths(paths, forbidden_artifacts=forbidden_artifacts)
    try:
        return {
            role: {
                "parent_path": str(output.path.parent),
                "parent_device": os.fstat(output.parent_descriptor).st_dev,
                "parent_inode": os.fstat(output.parent_descriptor).st_ino,
            }
            for role, output in bound.by_role.items()
        }
    finally:
        bound.close()


def _assert_bound_outputs_match_plan(bound: BoundOutputs, plan: Mapping[str, Any]) -> None:
    if set(bound.by_role) != set(plan["output_paths"]):
        raise RegistryBuildError("bound output roles do not match request plan")
    for role, output in bound.by_role.items():
        _assert_bound_output_parent(output)
        if str(output.path) != plan["output_paths"][role]:
            raise RegistryBuildError(f"bound {role} output path does not match request plan")
        metadata = os.fstat(output.parent_descriptor)
        expected = plan["output_parent_bindings"][role]
        observed = {
            "parent_path": str(output.path.parent),
            "parent_device": metadata.st_dev,
            "parent_inode": metadata.st_ino,
        }
        if observed != expected:
            raise RegistryBuildError(f"bound {role} output parent does not match request plan")


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalise_sha(value: Any) -> str | None:
    text = _clean(value)
    if text and text.lower().startswith("sha256:"):
        text = text.split(":", 1)[1]
    return text.lower() if text else None


def _read_candidates(artifact: CapturedArtifact, batch: str) -> list[dict[str, Any]]:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"candidate ledger is not strict UTF-8: {exc}") from exc
    if "\r" in text or not text.endswith("\n"):
        raise RegistryBuildError("candidate ledger must use LF terminators and end with LF")
    selected: list[dict[str, Any]] = []
    candidate_ids: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise RegistryBuildError(f"candidate ledger has a blank row at line {line_number}")
        row = _load_json_unique(line, source=f"{artifact.path}:{line_number}")
        if not isinstance(row, dict):
            raise RegistryBuildError(f"{artifact.path}:{line_number}: row is not a JSON object")
        if line != _canonical_json(row):
            raise RegistryBuildError(
                f"{artifact.path}:{line_number}: candidate row is not exact canonical JSON"
            )
        row_batch = row.get("batch")
        row_batch_id = row.get("batch_id")
        if not isinstance(row_batch, str) or not isinstance(row_batch_id, str):
            raise RegistryBuildError(
                f"{artifact.path}:{line_number}: batch and batch_id must both be present strings"
            )
        if row_batch != row_batch_id or row_batch != batch:
            raise RegistryBuildError(
                f"{artifact.path}:{line_number}: batch and batch_id must both equal {batch!r}"
            )
        candidate_id = row.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise RegistryBuildError(
                f"{artifact.path}:{line_number}: candidate_id must be a non-empty string"
            )
        if candidate_id in candidate_ids:
            raise RegistryBuildError(
                f"candidate ledger contains duplicate candidate_id {candidate_id}"
            )
        candidate_ids.add(candidate_id)
        selected.append({**row, "_ledger_line": line_number})
    if not selected:
        raise RegistryBuildError("candidate ledger contains no rows")
    return selected


def _read_selector_manifest(
    artifact: CapturedArtifact,
    *,
    batch: str,
    queue_sha256: str,
    candidates: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"selector manifest is not strict UTF-8: {exc}") from exc
    manifest = _load_json_unique(text, source=str(artifact.path))
    if not isinstance(manifest, dict):
        raise RegistryBuildError("selector manifest must be a JSON object")
    schema_version = manifest.get("schema_version")
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version != SELECTOR_MANIFEST_SCHEMA_VERSION
    ):
        raise RegistryBuildError(
            f"selector manifest schema_version must be exact integer "
            f"{SELECTOR_MANIFEST_SCHEMA_VERSION}"
        )
    if manifest.get("batch_id") != batch:
        raise RegistryBuildError(
            f"selector manifest batch_id {manifest.get('batch_id')!r} != requested {batch!r}"
        )
    if manifest.get("candidate_jsonl_sha256") != queue_sha256:
        raise RegistryBuildError("selector manifest candidate_jsonl_sha256 does not bind queue")
    candidate_count = len(candidates)
    declared_count = manifest.get("shard_selected_candidate_rows")
    if (
        not isinstance(declared_count, int)
        or isinstance(declared_count, bool)
        or declared_count != candidate_count
    ):
        raise RegistryBuildError(
            "selector manifest shard_selected_candidate_rows does not bind candidate count"
        )
    source_batch = manifest.get("source_batch")
    if not isinstance(source_batch, str) or not source_batch:
        raise RegistryBuildError("selector manifest source_batch must be a non-empty string")
    record_to_trait: dict[str, str] = {}
    trait_to_record: dict[str, str] = {}
    record_counts: dict[tuple[str, str], int] = {}
    for row in candidates:
        line = row["_ledger_line"]
        if row.get("source_batch") != source_batch:
            raise RegistryBuildError(
                f"candidate ledger line {line} source_batch does not match selector manifest"
            )
        trait_id = row.get("trait_id")
        record_path = row.get("record_path")
        if not isinstance(trait_id, str) or not trait_id:
            raise RegistryBuildError(f"candidate ledger line {line} lacks exact trait_id")
        if not isinstance(record_path, str) or not record_path:
            raise RegistryBuildError(f"candidate ledger line {line} lacks exact record_path")
        if record_path in record_to_trait and record_to_trait[record_path] != trait_id:
            raise RegistryBuildError("candidate record_path maps to more than one trait_id")
        if trait_id in trait_to_record and trait_to_record[trait_id] != record_path:
            raise RegistryBuildError("candidate trait_id maps to more than one record_path")
        record_to_trait[record_path] = trait_id
        trait_to_record[trait_id] = record_path
        key = (trait_id, record_path)
        record_counts[key] = record_counts.get(key, 0) + 1
    declared_records = manifest.get("shard_selected_trait_records")
    if (
        not isinstance(declared_records, int)
        or isinstance(declared_records, bool)
        or declared_records != len(record_counts)
    ):
        raise RegistryBuildError(
            "selector manifest shard_selected_trait_records does not bind exact record count"
        )
    for row in candidates:
        declared_alternatives = row.get("record_candidate_count")
        key = (str(row["trait_id"]), str(row["record_path"]))
        if (
            not isinstance(declared_alternatives, int)
            or isinstance(declared_alternatives, bool)
            or declared_alternatives != record_counts[key]
        ):
            raise RegistryBuildError(
                f"candidate ledger line {row['_ledger_line']} record_candidate_count "
                "does not bind the exact alternative count"
            )
    invariants = manifest.get("invariants")
    if not isinstance(invariants, dict) or set(invariants) != SELECTOR_V6_INVARIANTS:
        raise RegistryBuildError("selector manifest lacks the exact v6 invariant set")
    if any(value is not True for value in invariants.values()):
        raise RegistryBuildError("every selector manifest invariant must be literal true")
    downstream = manifest.get("downstream_requirements")
    if not isinstance(downstream, dict) or set(downstream) != SELECTOR_DOWNSTREAM_REQUIREMENTS:
        raise RegistryBuildError("selector manifest lacks the exact downstream contract")
    if any(value is not True for value in downstream.values()):
        raise RegistryBuildError("every selector downstream requirement must be literal true")
    return manifest


def _candidate_values(rows: Iterable[dict], key: str) -> list[Any]:
    return [row[key] for row in rows if row.get(key) not in (None, "")]


def _blocked_row(
    protein_id: str,
    rows: Iterable[dict],
    reason: str,
    detail: str,
) -> dict[str, str | int]:
    rows = list(rows)
    accession = protein_id.removeprefix("UniProtKB:")
    candidate_ids = sorted(
        {_clean(row.get("candidate_id")) or f"line:{row['_ledger_line']}" for row in rows}
    )
    trait_ids = sorted({_clean(row.get("trait_id")) or "" for row in rows})
    return {
        "protein_id": protein_id,
        "accession": accession,
        "candidate_count": len(rows),
        "candidate_ids": ";".join(candidate_ids),
        "trait_ids": ";".join(value for value in trait_ids if value),
        "reason": reason,
        "detail": " ".join(detail.split()),
    }


def _targets(
    rows: list[dict[str, Any]],
) -> tuple[list[Target], list[dict[str, str | int]]]:
    by_protein: dict[str, list[dict[str, Any]]] = {}
    invalid: list[dict[str, str | int]] = []
    for row in rows:
        protein_id = _clean(row.get("protein_id"))
        if not protein_id or _UNIPROT.fullmatch(protein_id) is None:
            shown = protein_id or f"<missing@line:{row['_ledger_line']}>"
            invalid.append(
                _blocked_row(shown, [row], "INVALID_ACCESSION", "not an exact UniProtKB CURIE")
            )
            continue
        by_protein.setdefault(protein_id, []).append(row)

    targets: list[Target] = []
    for protein_id in sorted(by_protein):
        candidates = by_protein[protein_id]
        accession = protein_id.removeprefix("UniProtKB:")
        lengths: set[int] = set()
        bad_length = False
        raw_lengths = _candidate_values(candidates, "sequence_length")
        for raw in raw_lengths:
            if not isinstance(raw, int) or isinstance(raw, bool) or raw < 1:
                bad_length = True
            else:
                lengths.add(raw)
        raw_hashes = _candidate_values(candidates, "sequence_sha256")
        hashes = {_normalise_sha(value) for value in raw_hashes}
        raw_releases = _candidate_values(candidates, "sequence_release")
        releases = {_clean(value) for value in raw_releases}
        reasons: list[str] = []
        if len(raw_lengths) != len(candidates):
            reasons.append("missing candidate sequence_length")
        if bad_length:
            reasons.append("invalid candidate sequence_length")
        if len(lengths) > 1:
            reasons.append(f"conflicting candidate lengths {sorted(lengths)}")
        if len(raw_hashes) != len(candidates):
            reasons.append("missing candidate sequence_sha256")
        if any(value is None or _SHA256.fullmatch(value) is None for value in hashes):
            reasons.append("invalid candidate sequence_sha256")
        if len(hashes) > 1:
            reasons.append("conflicting candidate sequence_sha256 values")
        if len(raw_releases) != len(candidates):
            reasons.append("missing candidate sequence_release")
        if any(value is None or _RELEASE.fullmatch(value) is None for value in releases):
            reasons.append("invalid candidate sequence_release")
        if len(releases) > 1:
            reasons.append(f"conflicting candidate releases {sorted(releases)}")
        if reasons:
            invalid.append(
                _blocked_row(
                    protein_id, candidates, "CONFLICTING_CANDIDATE_FACTS", "; ".join(reasons)
                )
            )
            continue
        targets.append(
            Target(
                protein_id=protein_id,
                accession=accession,
                candidates=tuple(candidates),
                expected_length=next(iter(lengths)),
                expected_sha256=next(iter(hashes)),  # type: ignore[arg-type]
                expected_release=next(iter(releases)),  # type: ignore[arg-type]
            )
        )
    return targets, invalid


def request_url(accessions: Iterable[str]) -> str:
    """Official REST URL for one exact-accession batch, including isoforms."""
    ordered = tuple(sorted(set(accessions)))
    if not ordered:
        raise RegistryBuildError("cannot construct an empty UniProt request")
    query = "(" + " OR ".join(f"accession:{accession}" for accession in ordered) + ")"
    params = {
        "query": query,
        "format": "json",
        "size": "500",
        "includeIsoform": "true",
        "fields": ",".join(RETURN_FIELDS),
    }
    return f"{UNIPROT_SEARCH}?{urllib.parse.urlencode(params)}"


def _target_projection(target: Target) -> dict[str, Any]:
    return {
        "protein_id": target.protein_id,
        "accession": target.accession,
        "candidate_count": len(target.candidates),
        "candidate_ids": sorted(str(row["candidate_id"]) for row in target.candidates),
        "trait_ids": sorted({str(row.get("trait_id") or "") for row in target.candidates}),
        "expected_sequence_length": target.expected_length,
        "expected_sequence_sha256": target.expected_sha256,
        "expected_sequence_release": target.expected_release,
    }


def _request_projection(index: int, targets: Sequence[Target]) -> dict[str, Any]:
    accessions = [target.accession for target in targets]
    protein_ids = [target.protein_id for target in targets]
    url = request_url(accessions)
    row: dict[str, Any] = {
        "chunk_index": index,
        "accession_count": len(accessions),
        "accessions": accessions,
        "accessions_sha256": _value_sha256(accessions),
        "protein_ids": protein_ids,
        "protein_ids_sha256": _value_sha256(protein_ids),
        "request_url": url,
        "request_url_sha256": hashlib.sha256(url.encode("utf-8")).hexdigest(),
    }
    row["request_id"] = "uniprot-registry-fetch-request:" + _value_sha256(row)
    return row


def _resolved_output_paths(args: argparse.Namespace) -> dict[str, Path]:
    membership = args.membership_out or args.out.with_name(DEFAULT_MEMBERSHIPS.name)
    receipt = args.receipt or args.out.with_name(DEFAULT_RECEIPT.name)
    outputs = {
        "protein_registry": args.out,
        "membership_registry": membership,
        "blocked_registry": args.blocked,
        "fetch_receipt": receipt,
    }
    _validate_staging_output_paths(outputs)
    return outputs


def _derive_request_plan(args: argparse.Namespace) -> PreparedPlan:
    if not 1 <= args.batch_size <= 200:
        raise RegistryBuildError("--batch-size must be between 1 and 200")
    if not args.expect_release or _RELEASE.fullmatch(args.expect_release) is None:
        raise RegistryBuildError("--expect-release is required and must have form YYYY_NN")
    if not isinstance(args.batch, str) or not args.batch:
        raise RegistryBuildError("--batch must be a non-empty exact batch label")
    outputs = _resolved_output_paths(args)
    queue = _capture(args.queue, description="candidate ledger")
    selector = _capture(args.selector_manifest, description="selector manifest")
    offline_fixture = (
        _capture(args.offline_responses, description="offline response fixture")
        if args.offline_responses is not None
        else None
    )
    candidates = _read_candidates(queue, args.batch)
    manifest = _read_selector_manifest(
        selector,
        batch=args.batch,
        queue_sha256=queue.sha256,
        candidates=candidates,
    )
    bound_inputs = [queue, selector]
    if offline_fixture is not None:
        bound_inputs.append(offline_fixture)
    output_parent_bindings = _validate_output_bindings(outputs, forbidden_artifacts=bound_inputs)
    targets, blocked = _targets(candidates)
    if blocked:
        detail = "; ".join(
            f"{row['protein_id']}:{row['reason']}:{row['detail']}" for row in blocked[:5]
        )
        raise RegistryBuildError(
            f"candidate request plan has {len(blocked)} pre-fetch blocker(s): {detail}"
        )
    if not targets:
        raise RegistryBuildError("candidate request plan contains no eligible targets")
    target_rows = [_target_projection(target) for target in targets]
    requests = [
        _request_projection(index, chunk)
        for index, chunk in enumerate(_chunks(targets, args.batch_size), 1)
    ]
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "kind": PLAN_KIND,
        "batch_id": args.batch,
        "source_batch": manifest["source_batch"],
        "qualification_claimed": False,
        "network_action_performed": False,
        "fresh_fetch_scope": "ALL_EXACT_TARGETS_IN_SELECTOR_BOUND_CANDIDATE_LEDGER",
        "candidate_artifact": {
            **_artifact_projection(queue),
            "candidate_row_count": len(candidates),
            "candidate_id_count": len(candidates),
            "candidate_ids_sha256": _value_sha256(
                sorted(str(row["candidate_id"]) for row in candidates)
            ),
        },
        "selector_manifest_artifact": {
            **_artifact_projection(selector),
            "selector_schema_version": manifest.get("schema_version"),
            "source_batch": manifest["source_batch"],
            "declared_candidate_sha256": manifest["candidate_jsonl_sha256"],
            "declared_candidate_row_count": manifest["shard_selected_candidate_rows"],
            "declared_record_count": manifest["shard_selected_trait_records"],
            "invariants_sha256": _value_sha256(manifest["invariants"]),
            "downstream_requirements_sha256": _value_sha256(manifest["downstream_requirements"]),
        },
        "acquisition_mode": ("OFFLINE_FIXTURE" if offline_fixture is not None else "UNIPROT_REST"),
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
            "response_release_header": "x-uniprot-release",
            "batch_size": args.batch_size,
        },
        "request_count": len(requests),
        "requests": requests,
        "requests_sha256": _value_sha256(requests),
        "output_paths": {role: _output_path(path) for role, path in outputs.items()},
        "output_parent_bindings": output_parent_bindings,
        "receipt_install_policy": "INSTALL_RECEIPT_LAST_AS_GENERATION_BOUNDARY",
    }
    plan["request_plan_id"] = PLAN_ID_PREFIX + _value_sha256(plan)
    return PreparedPlan(plan, tuple(targets), queue, selector, offline_fixture)


def render_request_plan(plan: Mapping[str, Any]) -> str:
    return _canonical_json(plan) + "\n"


def _load_request_plan(path: Path) -> tuple[dict[str, Any], CapturedArtifact]:
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
    if (
        type(value.get("schema_version")) is not int
        or value.get("schema_version") != PLAN_SCHEMA_VERSION
        or value.get("kind") != PLAN_KIND
    ):
        raise RegistryBuildError("request plan schema/kind mismatch")
    without_id = dict(value)
    observed_id = without_id.pop("request_plan_id", None)
    expected_id = PLAN_ID_PREFIX + _value_sha256(without_id)
    if observed_id != expected_id:
        raise RegistryBuildError("request plan content address is invalid")
    return value, artifact


def _require_exact_plan(supplied: Mapping[str, Any], derived: Mapping[str, Any]) -> None:
    if _canonical_json(supplied) != _canonical_json(derived):
        raise RegistryBuildError("supplied request plan does not match rederived exact plan")


def _assert_artifact_unchanged(artifact: CapturedArtifact, *, description: str) -> None:
    observed = _capture(artifact.path, description=description)
    if observed.sha256 != artifact.sha256:
        raise RegistryBuildError(
            f"{description} drifted: expected {artifact.sha256}, observed {observed.sha256}"
        )


def _header_projection(headers: Mapping[str, Any], *, release: str | None = None) -> dict[str, str]:
    lowered = {str(key).lower(): str(value) for key, value in headers.items() if value is not None}
    if release is not None:
        lowered["x-uniprot-release"] = release
    return {
        key: lowered[key]
        for key in RESPONSE_PROVENANCE_HEADERS
        if key in lowered and lowered[key] != ""
    }


def _response_payload(
    raw: bytes, *, source: str
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"{source} returned non-UTF-8 JSON: {exc}") from exc
    payload = _load_json_unique(text, source=source)
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list) or any(not isinstance(result, dict) for result in results):
        raise RegistryBuildError(f"{source} has no object-valued results list")
    return payload, tuple(results)


class NetworkClient:
    def __init__(self, *, timeout: float, retries: int, interval: float):
        self.timeout = timeout
        self.retries = retries
        self.interval = interval
        self._last_request = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self._last_request = time.monotonic()

    def fetch(self, accessions: tuple[str, ...]) -> FetchResponse:
        url = request_url(accessions)
        for attempt in range(self.retries + 1):
            self._throttle()
            request = urllib.request.Request(url, headers=REQUEST_HEADERS)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    release = response.headers.get("x-uniprot-release")
                    link = response.headers.get("link") or ""
                    if 'rel="next"' in link or "rel=next" in link:
                        raise RegistryBuildError(
                            "exact-accession batch unexpectedly paginated; reduce --batch-size"
                        )
                    raw = response.read()
                    _, results = _response_payload(raw, source="UniProt response")
                    headers = _header_projection(response.headers, release=release)
                    return FetchResponse(
                        requested=accessions,
                        release=release,
                        results=results,
                        request_url=url,
                        response_url=str(getattr(response, "geturl", lambda: url)()),
                        status=int(getattr(response, "status", 200)),
                        body_sha256=hashlib.sha256(raw).hexdigest(),
                        body_size_bytes=len(raw),
                        body_sha256_basis="HTTP_RESPONSE_BODY_BYTES",
                        header_projection=headers,
                        acquisition_mode="UNIPROT_REST",
                        offline_response_index=None,
                    )
            except urllib.error.HTTPError as exc:
                transient = exc.code in {429, 500, 502, 503, 504}
                if transient and attempt < self.retries:
                    time.sleep(min(30.0, 2**attempt))
                    continue
                raise RegistryBuildError(f"UniProt HTTP {exc.code} for one batch") from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt < self.retries:
                    time.sleep(min(30.0, 2**attempt))
                    continue
                raise RegistryBuildError(f"UniProt network failure: {exc}") from exc
        raise RegistryBuildError("UniProt request exhausted retries")  # pragma: no cover

    def finish(self) -> None:
        return


def _offline_objects(artifact: CapturedArtifact) -> list[dict[str, Any]]:
    path = artifact.path
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"offline response fixture is not strict UTF-8: {exc}") from exc
    try:
        payload = json.loads(text, object_pairs_hook=_unique_object)
    except json.JSONDecodeError:
        payload = None
    inherited_release: str | None = None
    if isinstance(payload, dict) and isinstance(payload.get("responses"), list):
        inherited_release = _clean(payload.get("release"))
        objects = payload["responses"]
    elif isinstance(payload, list):
        objects = payload
    elif isinstance(payload, dict):
        objects = [payload]
    else:
        objects = []
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                objects.append(json.loads(line, object_pairs_hook=_unique_object))
            except json.JSONDecodeError as exc:
                raise RegistryBuildError(
                    f"{path}:{line_number}: invalid offline response JSON"
                ) from exc
    if not objects or any(not isinstance(obj, dict) for obj in objects):
        raise RegistryBuildError("offline fixture must contain one or more response objects")
    if inherited_release:
        objects = [
            obj if obj.get("release") is not None else {**obj, "release": inherited_release}
            for obj in objects
        ]
    return objects


class OfflineClient:
    """Ordered, exact-request response fixture used for tests and offline review."""

    def __init__(self, artifact: CapturedArtifact):
        self.path = artifact.path
        self.responses = _offline_objects(artifact)
        self.index = 0

    def fetch(self, accessions: tuple[str, ...]) -> FetchResponse:
        if self.index >= len(self.responses):
            raise RegistryBuildError("offline fixture has fewer responses than request batches")
        raw = self.responses[self.index]
        self.index += 1
        declared = raw.get("requested")
        if declared is not None and tuple(sorted(declared)) != tuple(sorted(accessions)):
            raise RegistryBuildError(
                f"offline response {self.index} requested set does not match generated batch"
            )
        headers = raw.get("headers") if isinstance(raw.get("headers"), dict) else {}
        release = _clean(raw.get("release") or headers.get("x-uniprot-release"))
        body = raw.get("body") if isinstance(raw.get("body"), dict) else raw
        results = body.get("results") if isinstance(body, dict) else None
        if not isinstance(results, list) or any(not isinstance(result, dict) for result in results):
            raise RegistryBuildError(f"offline response {self.index} has no results list")
        response_body = body if raw.get("body") is not None else {"results": results}
        body_bytes = _canonical_json(response_body).encode("utf-8")
        header_projection = _header_projection(headers, release=release)
        return FetchResponse(
            requested=accessions,
            release=release,
            results=tuple(results),
            request_url=request_url(accessions),
            response_url=None,
            status=int(raw.get("status", 200)),
            body_sha256=hashlib.sha256(body_bytes).hexdigest(),
            body_size_bytes=len(body_bytes),
            body_sha256_basis="CANONICAL_OFFLINE_RESPONSE_BODY_JSON_UTF8",
            header_projection=header_projection,
            acquisition_mode="OFFLINE_FIXTURE",
            offline_response_index=self.index,
        )

    def finish(self) -> None:
        if self.index != len(self.responses):
            raise RegistryBuildError(
                f"offline fixture has {len(self.responses) - self.index} unused response(s)"
            )


def _protein_label(entry: dict[str, Any]) -> str | None:
    description = entry.get("proteinDescription")
    if isinstance(description, dict):
        recommended = description.get("recommendedName")
        if isinstance(recommended, dict):
            full_name = recommended.get("fullName")
            if isinstance(full_name, dict) and _clean(full_name.get("value")):
                return _clean(full_name["value"])
        for key in ("alternativeNames", "submissionNames"):
            names = description.get(key)
            if not isinstance(names, list):
                continue
            for name in names:
                full_name = name.get("fullName") if isinstance(name, dict) else None
                if isinstance(full_name, dict) and _clean(full_name.get("value")):
                    return _clean(full_name["value"])
    return _clean(entry.get("uniProtkbId"))


def _entry_reference(
    entry: dict[str, Any], target: Target, release: str
) -> tuple[dict[str, Any] | None, list[str]]:
    failures: list[str] = []
    accession = _clean(entry.get("primaryAccession"))
    if accession != target.accession:
        failures.append(
            f"response accession {accession!r} does not equal requested {target.accession!r}"
        )
    label = _protein_label(entry)
    if not label:
        failures.append("missing protein name")
    organism = entry.get("organism")
    taxon_number = organism.get("taxonId") if isinstance(organism, dict) else None
    taxon_label = _clean(organism.get("scientificName")) if isinstance(organism, dict) else None
    if not isinstance(taxon_number, int) or isinstance(taxon_number, bool) or taxon_number < 1:
        failures.append("missing or invalid organism taxonId")
    if not taxon_label:
        failures.append("missing organism scientificName")
    entry_type = _clean(entry.get("entryType"))
    if entry_type and entry_type.startswith("UniProtKB reviewed"):
        reviewed: bool | None = True
    elif entry_type and entry_type.startswith("UniProtKB unreviewed"):
        reviewed = False
    else:
        reviewed = None
        failures.append("missing or unrecognized entryType")
    sequence_object = entry.get("sequence")
    sequence = _clean(sequence_object.get("value")) if isinstance(sequence_object, dict) else None
    sequence_length = sequence_object.get("length") if isinstance(sequence_object, dict) else None
    if not sequence or _SEQUENCE.fullmatch(sequence) is None:
        failures.append("missing or invalid full sequence")
    if (
        not isinstance(sequence_length, int)
        or isinstance(sequence_length, bool)
        or sequence_length < 1
    ):
        failures.append("missing or invalid API sequence length")
    elif sequence and sequence_length != len(sequence):
        failures.append(
            f"API sequence length {sequence_length} disagrees with len(sequence) {len(sequence)}"
        )
    audit = entry.get("entryAudit")
    sequence_version = audit.get("sequenceVersion") if isinstance(audit, dict) else None
    if (
        not isinstance(sequence_version, int)
        or isinstance(sequence_version, bool)
        or sequence_version < 1
    ):
        failures.append("missing or invalid entryAudit.sequenceVersion")
    actual_sha = hashlib.sha256(sequence.encode("ascii")).hexdigest() if sequence else None
    if target.expected_length is not None and sequence_length != target.expected_length:
        failures.append(
            f"candidate sequence_length {target.expected_length} != UniProt {sequence_length}"
        )
    if target.expected_sha256 is not None and actual_sha != target.expected_sha256:
        failures.append("candidate sequence_sha256 does not match UniProt sequence")
    if failures:
        return None, failures
    match = _ACCESSION.fullmatch(target.accession)
    reference: dict[str, Any] = {
        "protein_id": target.protein_id,
        "protein_label": label,
        "taxon_id": f"NCBITaxon:{taxon_number}",
        "taxon_label": taxon_label,
        "sequence": sequence,
        "sequence_length": sequence_length,
        "sequence_sha256": actual_sha,
        "reviewed": reviewed,
        "uniprot_release": release,
        "sequence_version": sequence_version,
    }
    if match and match.group(2):
        reference["isoform"] = int(match.group(2))
    from validate_uniprot_grounding import validate_protein_reference

    findings = validate_protein_reference(reference, path=Path("<generated>"), line=1)
    if findings:
        return None, [f"{finding.code}: {finding.message}" for finding in findings]
    return reference, []


def _chunks(values: list[Target], size: int) -> Iterable[list[Target]]:
    for offset in range(0, len(values), size):
        yield values[offset : offset + size]


def _write_all(descriptor: int, raw: bytes) -> None:
    offset = 0
    while offset < len(raw):
        try:
            written = os.write(descriptor, raw[offset:])
        except InterruptedError:
            continue
        if written <= 0:  # pragma: no cover - defensive POSIX invariant
            raise RegistryBuildError("descriptor write made no progress")
        offset += written


def _atomic_replace_bound(output: BoundOutput, text: str, *, phase: str) -> None:
    del phase  # phase is an explicit test/audit hook at the call boundary.
    _assert_bound_output_parent(output)
    _directory_flags, _file_read_flags = _descriptor_safety_flags()
    write_flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW")
        | getattr(os, "O_CLOEXEC", 0)
    )
    temporary_name = f".{output.leaf_name}.pending-{os.getpid()}-{secrets.token_hex(12)}"
    descriptor: int | None = None
    replaced = False
    try:
        descriptor = os.open(
            temporary_name,
            write_flags,
            0o600,
            dir_fd=output.parent_descriptor,
        )
        raw = text.encode("utf-8")
        _write_all(descriptor, raw)
        os.fsync(descriptor)
        staged = os.fstat(descriptor)
        if not stat.S_ISREG(staged.st_mode) or staged.st_size != len(raw):
            raise RegistryBuildError("staged output descriptor has wrong type or size")
        os.rename(
            temporary_name,
            output.leaf_name,
            src_dir_fd=output.parent_descriptor,
            dst_dir_fd=output.parent_descriptor,
        )
        replaced = True
        installed = os.stat(
            output.leaf_name,
            dir_fd=output.parent_descriptor,
            follow_symlinks=False,
        )
        if _stat_identity(installed) != _stat_identity(staged):
            raise RegistryBuildError("installed output does not bind the staged descriptor")
        output.existing_identity = (installed.st_dev, installed.st_ino)
        os.fsync(output.parent_descriptor)
        _assert_bound_output_parent(output)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if not replaced:
            try:
                os.unlink(temporary_name, dir_fd=output.parent_descriptor)
            except FileNotFoundError:
                pass


def _generation_pending_marker(
    *, plan: Mapping[str, Any], intended_receipt_id: str
) -> dict[str, Any]:
    marker: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "kind": PENDING_KIND,
        "generation_pending": True,
        "generation_boundary": False,
        "batch_id": plan["batch_id"],
        "request_plan_id": plan["request_plan_id"],
        "intended_receipt_id": intended_receipt_id,
        "output_paths": plan["output_paths"],
    }
    marker["pending_id"] = PENDING_ID_PREFIX + _value_sha256(marker)
    return marker


def _install_generation(
    *,
    bound: BoundOutputs,
    plan: Mapping[str, Any],
    registry_text: str,
    membership_text: str,
    blocked_text: str,
    receipt_text: str,
    receipt_id: str,
) -> None:
    receipt_value = _load_json_unique(receipt_text.rstrip("\n"), source="generated receipt")
    if not isinstance(receipt_value, dict) or receipt_value.get("receipt_id") != receipt_id:
        raise RegistryBuildError("generated receipt text/id mismatch before install")
    marker = _generation_pending_marker(plan=plan, intended_receipt_id=receipt_id)
    marker_text = _canonical_json(marker) + "\n"
    receipt_output = bound.by_role["fetch_receipt"]
    try:
        _atomic_replace_bound(receipt_output, marker_text, phase="generation_pending")
    except RegistryBuildError:
        raise
    except Exception as exc:
        raise RegistryBuildError(f"could not invalidate prior fetch receipt: {exc}") from exc
    try:
        _atomic_replace_bound(
            bound.by_role["protein_registry"],
            registry_text,
            phase="protein_registry",
        )
        _atomic_replace_bound(
            bound.by_role["membership_registry"],
            membership_text,
            phase="membership_registry",
        )
        _atomic_replace_bound(
            bound.by_role["blocked_registry"],
            blocked_text,
            phase="blocked_registry",
        )
        for role in ("protein_registry", "membership_registry", "blocked_registry"):
            _verify_output_projection(
                role=role,
                projection=receipt_value["outputs"][role],
                expected_path=plan["output_paths"][role],
                bound_output=bound.by_role[role],
            )
        _atomic_replace_bound(receipt_output, receipt_text, phase="final_receipt")
    except Exception as exc:
        try:
            _atomic_replace_bound(
                receipt_output,
                marker_text,
                phase="generation_pending_recovery",
            )
        except Exception as recovery_exc:
            raise RegistryBuildError(
                "partial install failed and generation-pending receipt recovery also failed: "
                f"install={exc}; recovery={recovery_exc}"
            ) from recovery_exc
        if isinstance(exc, RegistryBuildError):
            raise
        raise RegistryBuildError(f"partial output install failed: {exc}") from exc


def _blocked_text(rows: list[dict[str, str | int]]) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=_BLOCKED_COLUMNS, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda row: (str(row["protein_id"]), str(row["reason"]))))
    return buffer.getvalue()


def _response_receipt_row(
    *,
    request: Mapping[str, Any],
    response: FetchResponse,
    exact_accessions: Sequence[str],
    unexpected_accessions: Sequence[str],
) -> dict[str, Any]:
    headers = dict(sorted(response.header_projection.items()))
    return {
        "request_id": request["request_id"],
        "chunk_index": request["chunk_index"],
        "request_url": response.request_url,
        "response_url": response.response_url,
        "acquisition_mode": response.acquisition_mode,
        "offline_response_index": response.offline_response_index,
        "response_status": response.status,
        "requested_accession_count": len(response.requested),
        "requested_accessions_sha256": _value_sha256(list(response.requested)),
        "response_release": response.release,
        "response_body_sha256": response.body_sha256,
        "response_body_size_bytes": response.body_size_bytes,
        "response_body_sha256_basis": response.body_sha256_basis,
        "response_header_projection": headers,
        "response_header_projection_sha256": _value_sha256(headers),
        "response_result_count": len(response.results),
        "returned_exact_accession_count": len(exact_accessions),
        "returned_exact_accessions_sha256": _value_sha256(list(exact_accessions)),
        "unexpected_accession_count": len(unexpected_accessions),
        "unexpected_accessions": list(unexpected_accessions),
    }


def _output_projection(path: str, text: str, *, row_count: int) -> dict[str, Any]:
    raw = text.encode("utf-8")
    return {
        "path": path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "row_count": row_count,
    }


def _build_receipt(
    *,
    plan: Mapping[str, Any],
    plan_artifact: CapturedArtifact,
    response_rows: Sequence[Mapping[str, Any]],
    release: str,
    registry_text: str,
    membership_text: str,
    blocked_text: str,
    reference_count: int,
    membership_count: int,
    blocked_count: int,
) -> dict[str, Any]:
    output_paths = plan["output_paths"]
    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "kind": RECEIPT_KIND,
        "generation_boundary": True,
        "generation_pending": False,
        "receipt_install_policy": "INSTALLED_LAST_AFTER_THREE_BOUND_OUTPUTS",
        "batch_id": plan["batch_id"],
        "request_plan_id": plan["request_plan_id"],
        "request_plan_artifact": _artifact_projection(plan_artifact),
        "expected_uniprot_release": plan["expected_uniprot_release"],
        "observed_uniprot_release": release,
        "acquisition_mode": plan["acquisition_mode"],
        "network_action_performed": plan["acquisition_mode"] == "UNIPROT_REST",
        "offline_fixture_artifact": plan["offline_fixture_artifact"],
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
            "blocked_registry": _output_projection(
                output_paths["blocked_registry"], blocked_text, row_count=blocked_count
            ),
        },
        "all_targets_accounted_for": True,
        "qualification_claimed": False,
    }
    receipt["receipt_id"] = RECEIPT_ID_PREFIX + _value_sha256(receipt)
    return receipt


def _load_canonical_json_artifact(
    artifact: CapturedArtifact, *, description: str
) -> dict[str, Any]:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"{description} is not strict UTF-8: {exc}") from exc
    if "\r" in text or not text.endswith("\n") or text.count("\n") != 1:
        raise RegistryBuildError(f"{description} must be one LF-terminated canonical JSON row")
    value = _load_json_unique(text[:-1], source=str(artifact.path))
    if not isinstance(value, dict) or text != _canonical_json(value) + "\n":
        raise RegistryBuildError(f"{description} is not exact canonical JSON")
    return value


def _canonical_jsonl_rows(
    artifact: CapturedArtifact,
    *,
    description: str,
    canonicalizer: Callable[[Any], str] = _canonical_json,
) -> list[dict[str, Any]]:
    if not artifact.raw:
        return []
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"{description} is not strict UTF-8: {exc}") from exc
    if "\r" in text or not text.endswith("\n"):
        raise RegistryBuildError(f"{description} must use LF and end with LF")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise RegistryBuildError(f"{description} has a blank row at line {line_number}")
        value = _load_json_unique(line, source=f"{artifact.path}:{line_number}")
        if not isinstance(value, dict) or line != canonicalizer(value):
            raise RegistryBuildError(
                f"{description} line {line_number} is not a canonical JSON object"
            )
        rows.append(value)
    return rows


def _strict_blocked_rows(artifact: CapturedArtifact) -> list[dict[str, str]]:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"blocked registry is not strict UTF-8: {exc}") from exc
    if "\r" in text or not text.endswith("\n"):
        raise RegistryBuildError("blocked registry must use LF and end with LF")
    reader = csv.DictReader(StringIO(text), delimiter="\t")
    if tuple(reader.fieldnames or ()) != _BLOCKED_COLUMNS:
        raise RegistryBuildError("blocked registry header does not match exact schema")
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise RegistryBuildError("blocked registry contains a malformed TSV row")
    canonical = _blocked_text(rows)
    if canonical != text:
        raise RegistryBuildError("blocked registry is not in canonical row order/format")
    return rows


def _request_plan_args(plan: Mapping[str, Any]) -> argparse.Namespace:
    try:
        acquisition_mode = plan["acquisition_mode"]
        offline = plan["offline_fixture_artifact"]
        if acquisition_mode == "UNIPROT_REST":
            if offline is not None:
                raise RegistryBuildError("REST request plan carries an offline fixture")
            offline_path: str | None = None
        elif acquisition_mode == "OFFLINE_FIXTURE":
            if not isinstance(offline, dict) or not isinstance(offline.get("path"), str):
                raise RegistryBuildError("offline request plan lacks its fixture artifact")
            offline_path = offline["path"]
        else:
            raise RegistryBuildError("request plan acquisition_mode is invalid")
        values = [
            "--queue",
            str(plan["candidate_artifact"]["path"]),
            "--selector-manifest",
            str(plan["selector_manifest_artifact"]["path"]),
            "--batch",
            str(plan["batch_id"]),
            "--batch-size",
            str(plan["request_policy"]["batch_size"]),
            "--expect-release",
            str(plan["expected_uniprot_release"]),
            "--out",
            str(plan["output_paths"]["protein_registry"]),
            "--membership-out",
            str(plan["output_paths"]["membership_registry"]),
            "--blocked",
            str(plan["output_paths"]["blocked_registry"]),
            "--receipt",
            str(plan["output_paths"]["fetch_receipt"]),
        ]
        if offline_path is not None:
            values.extend(("--offline-responses", offline_path))
    except (KeyError, TypeError) as exc:
        raise RegistryBuildError(f"request plan lacks verifier-required shape: {exc}") from exc
    return _parser().parse_args(values)


def _verify_output_projection(
    *,
    role: str,
    projection: Mapping[str, Any],
    expected_path: str,
    bound_output: BoundOutput | None = None,
) -> tuple[CapturedArtifact, list[dict[str, Any]] | list[dict[str, str]]]:
    if set(projection) != {"path", "sha256", "size_bytes", "row_count"}:
        raise RegistryBuildError(f"receipt {role} output projection has wrong shape")
    if projection.get("path") != expected_path:
        raise RegistryBuildError(f"receipt {role} output path does not match request plan")
    declared_sha = projection.get("sha256")
    declared_size = projection.get("size_bytes")
    row_count = projection.get("row_count")
    if (
        not isinstance(declared_sha, str)
        or _SHA256.fullmatch(declared_sha) is None
        or type(declared_size) is not int
        or declared_size < 0
        or type(row_count) is not int
        or row_count < 0
    ):
        raise RegistryBuildError(f"receipt {role} hash/size/row_count must have exact scalar types")
    artifact = (
        _capture_bound_output(bound_output, description=f"installed {role}")
        if bound_output is not None
        else _capture(Path(expected_path), description=f"installed {role}")
    )
    if declared_sha != artifact.sha256 or declared_size != artifact.size_bytes:
        raise RegistryBuildError(f"installed {role} bytes do not match receipt")
    if role == "blocked_registry":
        rows: list[dict[str, Any]] | list[dict[str, str]] = _strict_blocked_rows(artifact)
    else:
        rows = _canonical_jsonl_rows(
            artifact,
            description=f"installed {role}",
            canonicalizer=(
                canonical_membership_json if role == "membership_registry" else _canonical_json
            ),
        )
    if row_count != len(rows):
        raise RegistryBuildError(f"installed {role} row count does not match receipt")
    return artifact, rows


def verify_fetch_receipt(*, receipt_path: Path, request_plan_path: Path) -> VerifiedFetchReceipt:
    """Strictly verify one complete installed generation without network or writes."""

    request_plan, plan_artifact = _load_request_plan(request_plan_path)
    rederived = _derive_request_plan(_request_plan_args(request_plan))
    _require_exact_plan(request_plan, rederived.plan)
    expected_receipt_path = request_plan["output_paths"]["fetch_receipt"]
    if _output_path(receipt_path) != expected_receipt_path:
        raise RegistryBuildError("supplied receipt path does not match independent request plan")
    output_paths = {role: Path(path) for role, path in request_plan["output_paths"].items()}
    bound = _bind_output_paths(output_paths, forbidden_artifacts=[plan_artifact])
    try:
        _assert_bound_outputs_match_plan(bound, request_plan)
        return _verify_fetch_receipt_bound(
            request_plan=request_plan,
            plan_artifact=plan_artifact,
            bound=bound,
            candidate_jsonl_bytes=rederived.queue.raw,
        )
    finally:
        bound.close()


def _verify_fetch_receipt_bound(
    *,
    request_plan: Mapping[str, Any],
    plan_artifact: CapturedArtifact,
    bound: BoundOutputs,
    candidate_jsonl_bytes: bytes,
) -> VerifiedFetchReceipt:
    receipt_artifact = _capture_bound_output(
        bound.by_role["fetch_receipt"], description="fetch receipt"
    )
    receipt = _load_canonical_json_artifact(receipt_artifact, description="fetch receipt")
    if receipt.get("kind") == PENDING_KIND or receipt.get("generation_pending") is True:
        raise RegistryBuildError("fetch generation is pending and is not a valid receipt")
    expected_receipt_keys = {
        "schema_version",
        "kind",
        "generation_boundary",
        "generation_pending",
        "receipt_install_policy",
        "batch_id",
        "request_plan_id",
        "request_plan_artifact",
        "expected_uniprot_release",
        "observed_uniprot_release",
        "acquisition_mode",
        "network_action_performed",
        "offline_fixture_artifact",
        "target_count",
        "request_count",
        "response_rows",
        "response_rows_sha256",
        "outputs",
        "all_targets_accounted_for",
        "qualification_claimed",
        "receipt_id",
    }
    if set(receipt) != expected_receipt_keys:
        raise RegistryBuildError("fetch receipt does not have the exact v1 field set")
    if (
        type(receipt.get("schema_version")) is not int
        or receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION
        or receipt.get("kind") != RECEIPT_KIND
        or receipt.get("generation_boundary") is not True
        or receipt.get("generation_pending") is not False
        or receipt.get("receipt_install_policy") != "INSTALLED_LAST_AFTER_THREE_BOUND_OUTPUTS"
        or receipt.get("all_targets_accounted_for") is not True
        or receipt.get("qualification_claimed") is not False
    ):
        raise RegistryBuildError("fetch receipt completion/schema contract is invalid")
    without_id = dict(receipt)
    observed_id = without_id.pop("receipt_id")
    if observed_id != RECEIPT_ID_PREFIX + _value_sha256(without_id):
        raise RegistryBuildError("fetch receipt content address is invalid")
    target_count = receipt.get("target_count")
    request_count = receipt.get("request_count")
    if (
        type(target_count) is not int
        or target_count < 0
        or type(request_count) is not int
        or request_count < 0
    ):
        raise RegistryBuildError("fetch receipt target/request counts must be exact integers")
    if (
        receipt.get("batch_id") != request_plan["batch_id"]
        or receipt.get("request_plan_id") != request_plan["request_plan_id"]
        or receipt.get("expected_uniprot_release") != request_plan["expected_uniprot_release"]
        or receipt.get("observed_uniprot_release") != request_plan["expected_uniprot_release"]
        or target_count != request_plan["target_count"]
    ):
        raise RegistryBuildError("fetch receipt does not bind the exact plan/release/targets")
    if receipt.get("request_plan_artifact") != _artifact_projection(plan_artifact):
        raise RegistryBuildError("fetch receipt does not bind supplied request-plan bytes")
    mode = request_plan["acquisition_mode"]
    if (
        receipt.get("acquisition_mode") != mode
        or receipt.get("offline_fixture_artifact") != request_plan["offline_fixture_artifact"]
        or receipt.get("network_action_performed") is not (mode == "UNIPROT_REST")
    ):
        raise RegistryBuildError("fetch receipt acquisition provenance is inconsistent")
    response_rows = receipt.get("response_rows")
    if (
        not isinstance(response_rows, list)
        or request_count != len(response_rows)
        or len(response_rows) != request_plan["request_count"]
        or receipt.get("response_rows_sha256") != _value_sha256(response_rows)
    ):
        raise RegistryBuildError("fetch receipt response rows/count/hash are inconsistent")
    for index, (response, request) in enumerate(
        zip(response_rows, request_plan["requests"], strict=True), 1
    ):
        if not isinstance(response, dict):
            raise RegistryBuildError(f"fetch receipt response {index} is not an object")
        if set(response) != {
            "request_id",
            "chunk_index",
            "request_url",
            "response_url",
            "acquisition_mode",
            "offline_response_index",
            "response_status",
            "requested_accession_count",
            "requested_accessions_sha256",
            "response_release",
            "response_body_sha256",
            "response_body_size_bytes",
            "response_body_sha256_basis",
            "response_header_projection",
            "response_header_projection_sha256",
            "response_result_count",
            "returned_exact_accession_count",
            "returned_exact_accessions_sha256",
            "unexpected_accession_count",
            "unexpected_accessions",
        }:
            raise RegistryBuildError(
                f"fetch receipt response {index} does not have the exact v1 field set"
            )
        headers = response.get("response_header_projection")
        if (
            not isinstance(headers, dict)
            or any(
                key not in RESPONSE_PROVENANCE_HEADERS or not isinstance(value, str) or not value
                for key, value in headers.items()
            )
            or response.get("response_header_projection_sha256") != _value_sha256(headers)
        ):
            raise RegistryBuildError(f"fetch receipt response {index} header binding is invalid")
        if (
            response.get("request_id") != request["request_id"]
            or type(response.get("chunk_index")) is not int
            or response.get("chunk_index") != request["chunk_index"]
            or response.get("request_url") != request["request_url"]
            or type(response.get("requested_accession_count")) is not int
            or response.get("requested_accession_count") != request["accession_count"]
            or response.get("requested_accessions_sha256") != request["accessions_sha256"]
            or type(response.get("response_status")) is not int
            or response.get("response_status") != 200
            or response.get("response_release") != request_plan["expected_uniprot_release"]
            or headers.get("x-uniprot-release") != request_plan["expected_uniprot_release"]
            or response.get("acquisition_mode") != mode
        ):
            raise RegistryBuildError(f"fetch receipt response {index} does not bind request")
        body_sha = response.get("response_body_sha256")
        body_size = response.get("response_body_size_bytes")
        response_result_count = response.get("response_result_count")
        returned_exact_count = response.get("returned_exact_accession_count")
        unexpected_count = response.get("unexpected_accession_count")
        unexpected = response.get("unexpected_accessions")
        # The returned-accession hash remains an audit field bound to the captured
        # response body. A receipt-only verifier cannot independently reconstruct
        # that list without retaining the raw live HTTP response.
        if (
            not isinstance(body_sha, str)
            or _SHA256.fullmatch(body_sha) is None
            or not isinstance(body_size, int)
            or isinstance(body_size, bool)
            or body_size < 1
            or type(response_result_count) is not int
            or response_result_count < 0
            or type(returned_exact_count) is not int
            or returned_exact_count < 0
            or not isinstance(response.get("returned_exact_accessions_sha256"), str)
            or _SHA256.fullmatch(response["returned_exact_accessions_sha256"]) is None
            or type(unexpected_count) is not int
            or not isinstance(unexpected, list)
            or any(not isinstance(value, str) for value in unexpected)
            or unexpected != sorted(set(unexpected))
            or unexpected_count != len(unexpected)
            or returned_exact_count + len(unexpected) > response_result_count
            or not set(unexpected).isdisjoint(request["accessions"])
        ):
            raise RegistryBuildError(f"fetch receipt response {index} body binding is invalid")
        if mode == "OFFLINE_FIXTURE":
            if (
                response.get("response_url") is not None
                or type(response.get("offline_response_index")) is not int
                or response.get("offline_response_index") != index
                or response.get("response_body_sha256_basis")
                != "CANONICAL_OFFLINE_RESPONSE_BODY_JSON_UTF8"
            ):
                raise RegistryBuildError(
                    f"fetch receipt offline response {index} claims HTTP provenance"
                )
        else:
            response_url = response.get("response_url")
            parsed_response_url = (
                urllib.parse.urlparse(response_url) if isinstance(response_url, str) else None
            )
            if (
                parsed_response_url is None
                or parsed_response_url.scheme != "https"
                or parsed_response_url.netloc != "rest.uniprot.org"
                or response.get("offline_response_index") is not None
                or response.get("response_body_sha256_basis") != "HTTP_RESPONSE_BODY_BYTES"
            ):
                raise RegistryBuildError(f"fetch receipt live response {index} URL is invalid")
    outputs = receipt.get("outputs")
    expected_roles = {"protein_registry", "membership_registry", "blocked_registry"}
    if not isinstance(outputs, dict) or set(outputs) != expected_roles:
        raise RegistryBuildError("fetch receipt outputs do not have exact roles")
    captured: dict[str, CapturedArtifact] = {}
    parsed: dict[str, list[dict[str, Any]] | list[dict[str, str]]] = {}
    for role in sorted(expected_roles):
        projection = outputs[role]
        if not isinstance(projection, dict):
            raise RegistryBuildError(f"fetch receipt {role} projection is not an object")
        captured[role], parsed[role] = _verify_output_projection(
            role=role,
            projection=projection,
            expected_path=request_plan["output_paths"][role],
            bound_output=bound.by_role[role],
        )
    registry_rows = parsed["protein_registry"]
    membership_rows = parsed["membership_registry"]
    blocked_rows = parsed["blocked_registry"]
    target_rows = request_plan["target_rows"]
    if not isinstance(target_rows, list) or any(not isinstance(row, dict) for row in target_rows):
        raise RegistryBuildError("request plan target_rows are malformed")
    targets_by_id = {str(row.get("protein_id")): row for row in target_rows}
    if len(targets_by_id) != len(target_rows):
        raise RegistryBuildError("request plan target_rows have duplicate protein_id")
    from validate_uniprot_grounding import validate_protein_reference

    references: dict[str, dict[str, Any]] = {}
    for line_number, row in enumerate(registry_rows, 1):
        findings = validate_protein_reference(
            row, path=Path(request_plan["output_paths"]["protein_registry"]), line=line_number
        )
        if findings:
            raise RegistryBuildError("installed protein registry fails strict validation")
        protein_id = str(row["protein_id"])
        if protein_id in references:
            raise RegistryBuildError("installed protein registry has duplicate protein_id")
        target = targets_by_id.get(protein_id)
        if target is None:
            raise RegistryBuildError("installed protein registry contains an unplanned target")
        if (
            protein_id.removeprefix("UniProtKB:") != target.get("accession")
            or row.get("sequence_length") != target.get("expected_sequence_length")
            or row.get("sequence_sha256") != target.get("expected_sequence_sha256")
            or row.get("uniprot_release") != request_plan.get("expected_uniprot_release")
        ):
            raise RegistryBuildError(
                f"installed ProteinReference {protein_id} does not match target projection"
            )
        references[protein_id] = row
    try:
        normalized_memberships = merge_memberships(membership_rows)
    except MembershipSnapshotError as exc:
        raise RegistryBuildError(f"installed memberships fail strict validation: {exc}") from exc
    if normalized_memberships != membership_rows:
        raise RegistryBuildError("installed memberships are not in canonical semantic order")
    blocked_ids = [str(row["protein_id"]) for row in blocked_rows]
    if len(set(blocked_ids)) != len(blocked_ids):
        raise RegistryBuildError("blocked registry has duplicate protein_id")
    for row in blocked_rows:
        protein_id = str(row["protein_id"])
        target = targets_by_id.get(protein_id)
        if target is None:
            raise RegistryBuildError("blocked registry contains an unplanned target")
        try:
            candidate_count = int(row["candidate_count"])
        except (TypeError, ValueError) as exc:
            raise RegistryBuildError("blocked candidate_count is not an integer") from exc
        if (
            row["candidate_count"] != str(candidate_count)
            or candidate_count != target.get("candidate_count")
            or row.get("accession") != target.get("accession")
            or row.get("candidate_ids") != ";".join(target.get("candidate_ids", []))
            or row.get("trait_ids") != ";".join(target.get("trait_ids", []))
        ):
            raise RegistryBuildError(f"blocked row {protein_id} does not match target projection")
    target_ids = set(targets_by_id)
    if set(references) & set(blocked_ids) or set(references) | set(blocked_ids) != target_ids:
        raise RegistryBuildError("installed registry/blocked partition does not equal targets")
    for row in normalized_memberships:
        reference = references.get(str(row["protein_id"]))
        if (
            reference is None
            or row["uniprot_release"] != reference["uniprot_release"]
            or row["sequence_sha256"] != reference["sequence_sha256"]
        ):
            raise RegistryBuildError("installed membership is orphaned from exact reference")
    for role, initial in captured.items():
        rechecked = _capture_bound_output(
            bound.by_role[role], description=f"installed {role} final recheck"
        )
        if (
            rechecked.sha256 != initial.sha256
            or rechecked.device != initial.device
            or rechecked.inode != initial.inode
        ):
            raise RegistryBuildError(f"installed {role} changed during strict verification")
    _assert_bound_outputs_match_plan(bound, request_plan)
    final_receipt = _capture_bound_output(
        bound.by_role["fetch_receipt"], description="fetch receipt final recheck"
    )
    if (
        final_receipt.sha256 != receipt_artifact.sha256
        or final_receipt.device != receipt_artifact.device
        or final_receipt.inode != receipt_artifact.inode
    ):
        raise RegistryBuildError("fetch receipt changed during strict verification")
    _assert_bound_outputs_match_plan(bound, request_plan)
    return VerifiedFetchReceipt(
        receipt=receipt,
        request_plan=request_plan,
        receipt_sha256=receipt_artifact.sha256,
        request_plan_sha256=plan_artifact.sha256,
        output_sha256s={role: artifact.sha256 for role, artifact in captured.items()},
        candidate_jsonl_bytes=candidate_jsonl_bytes,
        protein_registry_jsonl_bytes=captured["protein_registry"].raw,
        membership_registry_jsonl_bytes=captured["membership_registry"].raw,
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
    supplied_plan, plan_artifact = _load_request_plan(args.request_plan)
    _require_exact_plan(supplied_plan, prepared.plan)
    output_paths = _resolved_output_paths(args)
    forbidden_collisions = {
        prepared.queue.path,
        prepared.selector_manifest.path,
        plan_artifact.path,
    }
    if any(_lexical_absolute(path) in forbidden_collisions for path in output_paths.values()):
        raise RegistryBuildError("staging output path collides with a bound input artifact")

    forbidden_artifacts = [prepared.queue, prepared.selector_manifest, plan_artifact]
    if prepared.offline_fixture is not None:
        forbidden_artifacts.append(prepared.offline_fixture)
    bound = _bind_output_paths(output_paths, forbidden_artifacts=forbidden_artifacts)
    try:
        _assert_bound_outputs_match_plan(bound, supplied_plan)
        return _execute_apply(
            args=args,
            supplied_plan=supplied_plan,
            plan_artifact=plan_artifact,
            output_paths=output_paths,
            bound=bound,
        )
    finally:
        bound.close()


def _execute_apply(
    *,
    args: argparse.Namespace,
    supplied_plan: Mapping[str, Any],
    plan_artifact: CapturedArtifact,
    output_paths: Mapping[str, Path],
    bound: BoundOutputs,
) -> int:

    # This is the last complete plan derivation before the first response is requested.
    checkpoint = _derive_request_plan(args)
    _require_exact_plan(supplied_plan, checkpoint.plan)
    _assert_artifact_unchanged(plan_artifact, description="request plan")
    _assert_bound_outputs_match_plan(bound, supplied_plan)
    targets = list(checkpoint.targets)
    client: NetworkClient | OfflineClient
    if checkpoint.offline_fixture is not None:
        client = OfflineClient(checkpoint.offline_fixture)
    else:
        client = NetworkClient(
            timeout=args.timeout, retries=args.retries, interval=args.request_interval
        )
    references: list[dict[str, Any]] = []
    memberships: list[dict[str, Any]] = []
    blocked: list[dict[str, str | int]] = []
    response_receipts: list[dict[str, Any]] = []
    pinned_release: str | None = None
    chunks = list(_chunks(targets, args.batch_size))
    if len(chunks) != len(supplied_plan["requests"]):
        raise RegistryBuildError("request plan chunk count changed before fetch")
    for target_batch, planned_request in zip(chunks, supplied_plan["requests"], strict=True):
        requested = tuple(target.accession for target in target_batch)
        response = client.fetch(requested)
        if response.acquisition_mode != supplied_plan["acquisition_mode"]:
            raise RegistryBuildError("fetch response acquisition mode does not match request plan")
        if response.requested != requested:
            raise RegistryBuildError("fetch client response does not bind the exact requested set")
        if response.request_url != planned_request["request_url"]:
            raise RegistryBuildError("fetch client response does not bind the planned request URL")
        if response.status != 200:
            raise RegistryBuildError(f"UniProt response status {response.status} is not 200")
        release = _clean(response.release)
        if not release or _RELEASE.fullmatch(release) is None:
            raise RegistryBuildError("UniProt response is missing a valid x-uniprot-release")
        if pinned_release is None:
            pinned_release = release
        elif release != pinned_release:
            raise RegistryBuildError(
                f"mixed UniProt releases in one registry run: {pinned_release} and {release}"
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
        if unexpected:
            print(
                "warning: ignored unrequested UniProt result(s): "
                + ", ".join(sorted(unexpected)[:10]),
                file=sys.stderr,
            )
        for target in target_batch:
            matches = by_accession.get(target.accession, [])
            if not matches:
                blocked.append(
                    _blocked_row(
                        target.protein_id,
                        target.candidates,
                        "ACCESSION_NOT_RETURNED",
                        "official exact-accession query returned no exact entry",
                    )
                )
                continue
            if len(matches) != 1:
                blocked.append(
                    _blocked_row(
                        target.protein_id,
                        target.candidates,
                        "DUPLICATE_API_RESULT",
                        f"official response contained {len(matches)} exact entries",
                    )
                )
                continue
            reference, failures = _entry_reference(matches[0], target, release)
            if failures:
                blocked.append(
                    _blocked_row(
                        target.protein_id,
                        target.candidates,
                        "REFERENCE_VALIDATION_FAILED",
                        "; ".join(failures),
                    )
                )
            elif reference:
                references.append(reference)
                try:
                    memberships.extend(
                        extract_entry_memberships(
                            matches[0],
                            protein_id=reference["protein_id"],
                            sequence_sha256=reference["sequence_sha256"],
                            uniprot_release=reference["uniprot_release"],
                        )
                    )
                except MembershipSnapshotError as exc:
                    raise RegistryBuildError(
                        f"cannot snapshot UniProt memberships for {target.protein_id}: {exc}"
                    ) from exc
    client.finish()
    references.sort(key=lambda row: row["protein_id"])
    if len({row["protein_id"] for row in references}) != len(references):
        raise RegistryBuildError("internal error: duplicate ProteinReference output key")
    try:
        memberships = merge_memberships(memberships)
        membership_text = dump_memberships(memberships)
    except MembershipSnapshotError as exc:
        raise RegistryBuildError(f"invalid UniProt membership snapshot: {exc}") from exc
    registry_text = "".join(_canonical_json(reference) + "\n" for reference in references)
    blocked_output = _blocked_text(blocked)
    target_ids = {target.protein_id for target in targets}
    reference_ids = {str(row["protein_id"]) for row in references}
    blocked_ids = {str(row["protein_id"]) for row in blocked}
    if reference_ids & blocked_ids or reference_ids | blocked_ids != target_ids:
        raise RegistryBuildError("internal error: fetched outputs do not account for every target")

    # Re-derive all queue/manifest/request facts after the final response and
    # immediately before any install. The saved plan itself must also be unchanged.
    final_checkpoint = _derive_request_plan(args)
    _require_exact_plan(supplied_plan, final_checkpoint.plan)
    _assert_artifact_unchanged(plan_artifact, description="request plan")
    _assert_bound_outputs_match_plan(bound, supplied_plan)
    if pinned_release is None:
        raise RegistryBuildError("fetch produced no release-stamped responses")
    receipt = _build_receipt(
        plan=supplied_plan,
        plan_artifact=plan_artifact,
        response_rows=response_receipts,
        release=pinned_release,
        registry_text=registry_text,
        membership_text=membership_text,
        blocked_text=blocked_output,
        reference_count=len(references),
        membership_count=len(memberships),
        blocked_count=len(blocked),
    )
    receipt_text = _canonical_json(receipt) + "\n"

    _install_generation(
        bound=bound,
        plan=supplied_plan,
        registry_text=registry_text,
        membership_text=membership_text,
        blocked_text=blocked_output,
        receipt_text=receipt_text,
        receipt_id=receipt["receipt_id"],
    )
    print(
        f"WROTE {output_paths['protein_registry']} ({len(references):,} ProteinReference rows; "
        f"UniProt release {pinned_release or 'no eligible accessions'})"
    )
    print(
        f"WROTE {output_paths['membership_registry']} "
        f"({len(memberships):,} exact database membership rows)"
    )
    print(f"WROTE {output_paths['blocked_registry']} ({len(blocked):,} blocked accessions)")
    print(f"WROTE {output_paths['fetch_receipt']} (generation boundary {receipt['receipt_id']})")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queue", type=Path, required=True, help="canonical candidate JSONL ledger"
    )
    parser.add_argument(
        "--selector-manifest",
        type=Path,
        required=True,
        help="selector JSON manifest binding queue SHA-256, row count, and batch",
    )
    parser.add_argument("--batch", default="ready-local", help="exact batch label")
    parser.add_argument("--batch-size", type=int, default=100, help="accessions per REST query")
    parser.add_argument(
        "--expect-release", required=True, help="required UniProt response release, YYYY_NN"
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--blocked", type=Path, default=DEFAULT_BLOCKED)
    parser.add_argument(
        "--membership-out",
        type=Path,
        help=(
            "exact UniProt databaseCrossReferences JSONL; default: "
            "uniprot_memberships.jsonl beside --out"
        ),
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        help="fetch generation receipt installed last; default beside --out",
    )
    parser.add_argument(
        "--request-plan",
        type=Path,
        help="exact canonical dry-run plan; required with --apply",
    )
    parser.add_argument(
        "--offline-responses",
        type=Path,
        help="ordered JSON/JSONL response fixture; performs no network access",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--request-interval", type=float, default=0.15)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="fetch and install three outputs followed by their receipt boundary",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout <= 0 or args.retries < 0 or args.request_interval < 0:
        print(
            "ERROR: timeout must be positive; retries/interval cannot be negative", file=sys.stderr
        )
        return 2
    try:
        return build(args)
    except RegistryBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
