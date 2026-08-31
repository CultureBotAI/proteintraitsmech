#!/usr/bin/env python3
"""Plan SFLD 4 source-model migration without writing trait records.

The current SFLD corpus flattens every source level into a whole-protein
functional-family record.  The pinned SFLD 4 release instead supplies 299
executable domain profiles with GA thresholds, correlated site tuples, and a
hierarchy; four current InterPro signatures have no executable release model.

This command binds immutable captures of the pinned source files, authenticates
the installed source-model manifest, indexes every possible SFLD trait safely,
and emits one canonical review row per current record plus a content-addressed
summary.  It deliberately makes no routing or definition decision.  There is
no output-file, serializer, apply, grounding, or promotion path.

The trait tree must be quiescent while the planner runs.  Descriptor-relative
no-follow reads and repeated candidate/content checks detect ordinary drift,
but a filesystem directory tree is not an atomic snapshot against a hostile
concurrent writer.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import os
import re
import stat
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

import ripgrep_prefilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfld_release import (  # noqa: E402
    SFLD_4_HIERARCHY_SHA256,
    SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
    SFLD_4_HMM_SHA256,
    SFLD_4_HMM_SOURCE_ARTIFACT,
    SFLD_4_MANIFEST_SOURCE_ARTIFACT,
    SFLD_4_SITES_SHA256,
    SFLD_4_SITES_SOURCE_ARTIFACT,
    SfldRelease,
    SfldReleaseError,
    build_sfld_profile_representation,
    build_sfld_release_manifest,
    load_sfld_release,
)

SCHEMA_VERSION = 1
PLAN_KIND = "SFLD_SOURCE_MODEL_MIGRATION_PLAN"
ROW_KIND = "SFLD_SOURCE_MODEL_MIGRATION_ROW"
SUMMARY_KIND = "SFLD_SOURCE_MODEL_MIGRATION_SUMMARY"
PLAN_ID_PREFIX = "sfld-source-model-migration-plan:"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HMM = REPO_ROOT / SFLD_4_HMM_SOURCE_ARTIFACT
DEFAULT_HIERARCHY = REPO_ROOT / SFLD_4_HIERARCHY_SOURCE_ARTIFACT
DEFAULT_SITES = REPO_ROOT / SFLD_4_SITES_SOURCE_ARTIFACT
DEFAULT_MANIFEST = REPO_ROOT / SFLD_4_MANIFEST_SOURCE_ARTIFACT
DEFAULT_INTERPRO = REPO_ROOT / "data/raw/interpro/interpro.xml.gz"
DEFAULT_TRAITS = REPO_ROOT / "data/traits"

# This is the same local InterPro XML snapshot already bound by the PRINTS
# migration plan.  It is used here only to classify the integrating entry as a
# Family or Domain for review; it is not treated as an SFLD executable model.
INTERPRO_XML_SHA256 = "c77fe193c1a0de8df903deff9325f734bfca3c9fbf59fd4ce697489c33ef0d87"

# Exact current InterPro signatures absent from the archived release's HMM/site
# accession set.  Accepting an arbitrary fifth record would turn a known
# four-row exception into an open-ended namespace allowlist.
SFLD_4_MODELLESS_CURRENT_ACCESSIONS = frozenset(
    {"SFLDF00030", "SFLDF00034", "SFLDF00109", "SFLDG01106"}
)

CURRENT_LEGACY_ROUTE = {
    "trait_axis": "FUNCTION",
    "trait_category": "FUNC_PROTEIN_FAMILY",
    "directory": "data/traits/function/protein_family/sfld",
}
GROUNDING_GATE = (
    "CLOSED_PENDING_SFLD_SOURCE_MODEL_MIGRATION_REVIEW_AND_CONTENT_ADDRESSED_HMMSEARCH_RECEIPT"
)
QUIESCENCE_CONTRACT = (
    "TRAIT_TREE_MUST_BE_QUIESCENT; descriptor-relative no-follow reads and repeated "
    "candidate/content checks are not an atomic filesystem snapshot"
)

_IDENTIFIER_RE = re.compile(r"^SFLD:SFLD[SGF][0-9]{5}$")
_INTERPRO_OPEN_RE = re.compile(r'<interpro id="(IPR[0-9]{6})"[^>]*\btype="([^"]+)"')
_READ_CHUNK_BYTES = 1024 * 1024
_MAX_SOURCE_BYTES = {
    "hmm": 64 * 1024 * 1024,
    "hierarchy": 1024 * 1024,
    "sites": 2 * 1024 * 1024,
    "manifest": 1024 * 1024,
    "interpro": 128 * 1024 * 1024,
}
_MAX_TRAIT_BYTES = 8 * 1024 * 1024


class SfldMigrationPlanError(ValueError):
    """The review-only migration plan cannot be reproduced exactly."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects silent duplicate-key collapse."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "unhashable YAML mapping key",
                key_node.start_mark,
            ) from error
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate YAML key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(canonical_json(row) + "\n" for row in rows).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _require_json_shape(
    value: Any,
    *,
    path: Path,
    location: str = "$",
    ancestors: frozenset[int] = frozenset(),
) -> None:
    if value is None or type(value) in {bool, int, str}:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise SfldMigrationPlanError(
                f"trait record is not JSON-shaped at {location} in {path}: non-finite number"
            )
        return
    if type(value) not in {list, dict}:
        raise SfldMigrationPlanError(
            f"trait record is not JSON-shaped at {location} in {path}: "
            f"unsupported {type(value).__name__}"
        )
    identity = id(value)
    if identity in ancestors:
        raise SfldMigrationPlanError(f"trait record has a YAML alias cycle at {location} in {path}")
    nested = ancestors | {identity}
    if type(value) is list:
        for index, item in enumerate(value):
            _require_json_shape(
                item,
                path=path,
                location=f"{location}[{index}]",
                ancestors=nested,
            )
        return
    for key, item in value.items():
        if type(key) is not str:
            raise SfldMigrationPlanError(
                f"trait record is not JSON-shaped at {location} in {path}: "
                f"mapping key {key!r} is not a string"
            )
        _require_json_shape(
            item,
            path=path,
            location=f"{location}.{key}",
            ancestors=nested,
        )


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
        or os.stat not in supports_follow_symlinks
    ):
        raise SfldMigrationPlanError(
            "platform lacks required O_NOFOLLOW/O_DIRECTORY/dir_fd filesystem safety"
        )
    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    return (
        os.O_RDONLY | directory_only | no_follow | close_on_exec,
        os.O_RDONLY | no_follow | close_on_exec | getattr(os, "O_NONBLOCK", 0),
    )


def _entry_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _content_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        stat.S_IFMT(metadata.st_mode),
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _capture_regular_file(path: Path, *, label: str, max_bytes: int) -> bytes:
    """Capture a bounded regular file through a stable no-follow path chain."""

    if max_bytes < 1:
        raise SfldMigrationPlanError(f"{label}: invalid capture byte limit")
    directory_flags, file_flags = _descriptor_safety_flags()
    lexical = Path(os.path.abspath(path)) if path.is_absolute() else path
    components = lexical.parts[1:] if lexical.is_absolute() else lexical.parts
    start = lexical.anchor if lexical.is_absolute() else "."
    if not components or any(component in {"", ".", ".."} for component in components):
        raise SfldMigrationPlanError(f"{label}: path must have ordinary components: {path}")

    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        try:
            current = os.open(start, directory_flags)
        except OSError as error:
            raise SfldMigrationPlanError(
                f"{label}: cannot safely open path root for {path}: {error}"
            ) from error
        descriptors.append(current)
        for component in components[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                child_metadata = os.fstat(child)
            except OSError as error:
                if isinstance(error, FileNotFoundError):
                    raise SfldMigrationPlanError(f"missing {label}: {path}") from error
                raise SfldMigrationPlanError(
                    f"{label}: cannot safely open directory component {component!r}: {error}"
                ) from error
            bindings.append((current, component, _entry_identity(child_metadata)))
            descriptors.append(child)
            current = child

        final_name = components[-1]
        try:
            file_descriptor = os.open(final_name, file_flags, dir_fd=current)
            before = os.fstat(file_descriptor)
        except OSError as error:
            if isinstance(error, FileNotFoundError):
                raise SfldMigrationPlanError(f"missing {label}: {path}") from error
            raise SfldMigrationPlanError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        descriptors.append(file_descriptor)
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise SfldMigrationPlanError(f"{label}: input is not a regular file: {path}")
        if before.st_size < 1 or before.st_size > max_bytes:
            raise SfldMigrationPlanError(
                f"{label}: input size {before.st_size} is outside 1..{max_bytes} bytes"
            )

        chunks: list[bytes] = []
        captured = 0
        while True:
            try:
                chunk = os.read(
                    file_descriptor,
                    min(_READ_CHUNK_BYTES, max_bytes - captured + 1),
                )
            except OSError as error:
                raise SfldMigrationPlanError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured += len(chunk)
            if captured > max_bytes:
                raise SfldMigrationPlanError(f"{label}: input exceeds {max_bytes} bytes")
        raw = b"".join(chunks)
        after = os.fstat(file_descriptor)
        if len(raw) != before.st_size or _content_identity(after) != _content_identity(before):
            raise SfldMigrationPlanError(f"{label}: input changed during capture")

        for parent_descriptor, component, expected_identity in bindings:
            try:
                live = os.stat(component, dir_fd=parent_descriptor, follow_symlinks=False)
            except OSError as error:
                raise SfldMigrationPlanError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected_identity:
                raise SfldMigrationPlanError(
                    f"{label}: path component changed during capture: {component!r}"
                )
        return raw
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _verify_sha256(raw: bytes, expected: str, *, label: str) -> str:
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected:
        raise SfldMigrationPlanError(
            f"{label} checksum mismatch: expected {expected}, found {observed}"
        )
    return observed


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise SfldMigrationPlanError(f"duplicate JSON key {key!r} in SFLD manifest")
        out[key] = value
    return out


def _reject_json_constant(value: str) -> Any:
    raise SfldMigrationPlanError(f"non-finite JSON constant {value!r} in SFLD manifest")


def _load_exact_manifest(raw: bytes, expected: Mapping[str, Any]) -> dict[str, Any]:
    try:
        text = raw.decode("ascii", errors="strict")
        parsed = json.loads(
            text,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SfldMigrationPlanError(f"cannot parse SFLD source-model manifest: {error}") from error
    if type(parsed) is not dict:
        raise SfldMigrationPlanError("SFLD source-model manifest must be one JSON object")
    expected_bytes = (canonical_json(expected) + "\n").encode("ascii")
    if raw != expected_bytes or parsed != expected:
        raise SfldMigrationPlanError(
            "SFLD source-model manifest is not the exact canonical projection of captured sources"
        )
    return parsed


def parse_interpro_entry_types(captured_gzip: bytes) -> dict[str, str]:
    """Parse the pinned InterPro entry accession/type table from captured bytes."""

    out: dict[str, str] = {}
    try:
        compressed = gzip.GzipFile(fileobj=io.BytesIO(captured_gzip), mode="rb")
        with io.TextIOWrapper(compressed, encoding="utf-8", errors="strict") as handle:
            for line_number, line in enumerate(handle, 1):
                match = _INTERPRO_OPEN_RE.search(line)
                if match is None:
                    continue
                accession, raw_type = match.groups()
                entry_type = raw_type.strip().lower().replace(" ", "_").replace("-", "_")
                if accession in out:
                    raise SfldMigrationPlanError(
                        f"InterPro XML line {line_number}: duplicate entry {accession}"
                    )
                out[accession] = entry_type
    except (OSError, EOFError, UnicodeDecodeError) as error:
        raise SfldMigrationPlanError(f"cannot parse captured InterPro XML: {error}") from error
    if not out:
        raise SfldMigrationPlanError("captured InterPro XML contains no entries")
    return out


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    release: SfldRelease
    manifest: Mapping[str, Any]
    interpro_types: Mapping[str, str]
    interpro_xml_sha256: str


def load_verified_source_snapshot(
    *,
    hmm_path: Path,
    hierarchy_path: Path,
    sites_path: Path,
    manifest_path: Path,
    interpro_path: Path,
    expected_hmm_sha256: str = SFLD_4_HMM_SHA256,
    expected_hierarchy_sha256: str = SFLD_4_HIERARCHY_SHA256,
    expected_sites_sha256: str = SFLD_4_SITES_SHA256,
    expected_interpro_sha256: str = INTERPRO_XML_SHA256,
    enforce_release_contract: bool = True,
) -> SourceSnapshot:
    """Load every parser from immutable, checksum-bound source captures."""

    hmm_raw = _capture_regular_file(
        hmm_path,
        label="SFLD HMM",
        max_bytes=_MAX_SOURCE_BYTES["hmm"],
    )
    hierarchy_raw = _capture_regular_file(
        hierarchy_path,
        label="SFLD hierarchy",
        max_bytes=_MAX_SOURCE_BYTES["hierarchy"],
    )
    sites_raw = _capture_regular_file(
        sites_path,
        label="SFLD sites",
        max_bytes=_MAX_SOURCE_BYTES["sites"],
    )
    manifest_raw = _capture_regular_file(
        manifest_path,
        label="SFLD manifest",
        max_bytes=_MAX_SOURCE_BYTES["manifest"],
    )
    interpro_raw = _capture_regular_file(
        interpro_path,
        label="InterPro XML",
        max_bytes=_MAX_SOURCE_BYTES["interpro"],
    )
    _verify_sha256(hmm_raw, expected_hmm_sha256, label="SFLD HMM")
    _verify_sha256(hierarchy_raw, expected_hierarchy_sha256, label="SFLD hierarchy")
    _verify_sha256(sites_raw, expected_sites_sha256, label="SFLD sites")
    interpro_sha256 = _verify_sha256(
        interpro_raw,
        expected_interpro_sha256,
        label="InterPro XML",
    )

    try:
        with tempfile.TemporaryDirectory(prefix="proteintraitsmech-sfld-capture-") as temporary:
            temporary_root = Path(temporary)
            captured_hmm = temporary_root / "sfld.hmm"
            captured_hierarchy = temporary_root / "sfld_hierarchy_flat.txt"
            captured_sites = temporary_root / "sfld_sites.annot"
            captured_hmm.write_bytes(hmm_raw)
            captured_hierarchy.write_bytes(hierarchy_raw)
            captured_sites.write_bytes(sites_raw)
            release = load_sfld_release(
                captured_hmm,
                captured_hierarchy,
                captured_sites,
                expected_hmm_sha256=expected_hmm_sha256,
                expected_hierarchy_sha256=expected_hierarchy_sha256,
                expected_sites_sha256=expected_sites_sha256,
                enforce_release_contract=enforce_release_contract,
            )
    except (OSError, SfldReleaseError) as error:
        raise SfldMigrationPlanError(f"cannot replay captured SFLD release: {error}") from error

    expected_manifest = build_sfld_release_manifest(release)
    manifest = _load_exact_manifest(manifest_raw, expected_manifest)
    interpro_types = parse_interpro_entry_types(interpro_raw)
    return SourceSnapshot(
        release=release,
        manifest=manifest,
        interpro_types=interpro_types,
        interpro_xml_sha256=interpro_sha256,
    )


def _candidate_sfld_paths(traits: Path) -> list[Path]:
    """Find every YAML that could decode to an SFLD namespace identifier."""

    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits), "SFLD migration")
        return sorted(found)
    command = [
        executable,
        "--no-config",
        "--null",
        "-l",
        "--text",
        "--hidden",
        "--no-ignore",
        "--iglob",
        "*.yaml",
        "--iglob",
        "*.yml",
        "-e",
        "(?i)SFLD",
        "-e",
        r"\\",
        "-e",
        r"\x00",
        "--",
        str(traits),
    ]
    try:
        scan = subprocess.run(command, check=False, capture_output=True)
    except OSError as error:
        raise SfldMigrationPlanError(f"cannot run ripgrep trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise SfldMigrationPlanError(f"ripgrep trait prefilter failed: {detail}")
    try:
        return sorted(
            Path(raw_path.decode("utf-8", errors="strict"))
            for raw_path in scan.stdout.split(b"\0")
            if raw_path
        )
    except UnicodeDecodeError as error:
        raise SfldMigrationPlanError("ripgrep returned a non-UTF-8 trait path") from error


def _reject_trait_tree_symlinks(traits: Path) -> None:
    lexical_root = Path(os.path.abspath(traits))
    if lexical_root.is_symlink():
        raise SfldMigrationPlanError(f"trait directory is a symlink: {traits}")
    walk_error: OSError | None = None

    def remember_walk_error(error: OSError) -> None:
        nonlocal walk_error
        walk_error = error

    try:
        for directory, directory_names, file_names in os.walk(
            lexical_root,
            topdown=True,
            onerror=remember_walk_error,
            followlinks=False,
        ):
            if walk_error is not None:
                raise walk_error
            parent = Path(directory)
            for name in (*directory_names, *file_names):
                candidate = parent / name
                if candidate.is_symlink():
                    raise SfldMigrationPlanError(
                        f"symlink below trait directory is not allowed: {candidate}"
                    )
        if walk_error is not None:
            raise walk_error
    except OSError as error:
        raise SfldMigrationPlanError(f"cannot inspect trait directory {traits}: {error}") from error


def _validated_candidate_path(path: Path, traits: Path) -> tuple[Path, Path]:
    lexical_root = Path(os.path.abspath(traits))
    lexical_path = Path(os.path.abspath(path))
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise SfldMigrationPlanError(
            f"trait candidate escapes trait directory before read: {path}"
        ) from error
    if not relative.parts:
        raise SfldMigrationPlanError(f"trait candidate is the trait directory itself: {path}")
    current = lexical_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise SfldMigrationPlanError(
                f"trait candidate traverses a symlink before read: {current}"
            )
    try:
        resolved_root = lexical_root.resolve(strict=True)
        resolved_path = lexical_path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise SfldMigrationPlanError(
            f"trait candidate escapes trait directory before read: {path}"
        ) from error
    except (OSError, RuntimeError) as error:
        raise SfldMigrationPlanError(
            f"cannot resolve trait candidate before read {path}: {error}"
        ) from error
    return lexical_path, relative


def _open_trait_root(traits: Path) -> tuple[Path, int, os.stat_result]:
    lexical_root = Path(os.path.abspath(traits))
    directory_flags, _ = _descriptor_safety_flags()
    descriptor: int | None = None
    try:
        descriptor = os.open(lexical_root, directory_flags)
        metadata = os.fstat(descriptor)
    except OSError as error:
        if descriptor is not None:
            os.close(descriptor)
        raise SfldMigrationPlanError(f"cannot bind trait directory {traits}: {error}") from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise SfldMigrationPlanError(f"trait root is not a directory: {traits}")
    return lexical_root, descriptor, metadata


def _assert_trait_root_binding(
    lexical_root: Path,
    descriptor: int,
    expected: os.stat_result,
) -> None:
    try:
        current_path = os.stat(lexical_root, follow_symlinks=False)
        current_descriptor = os.fstat(descriptor)
    except OSError as error:
        raise SfldMigrationPlanError(
            f"cannot recheck bound trait directory {lexical_root}: {error}"
        ) from error
    if _entry_identity(current_path) != _entry_identity(expected) or _entry_identity(
        current_descriptor
    ) != _entry_identity(expected):
        raise SfldMigrationPlanError(
            f"trait directory binding changed during indexing: {lexical_root}"
        )


def _read_candidate_from_root(
    *,
    root_descriptor: int,
    relative_path: Path,
    display_path: Path,
) -> bytes:
    directory_flags, file_flags = _descriptor_safety_flags()
    directory_descriptor = os.dup(root_descriptor)
    file_descriptor: int | None = None
    try:
        for part in relative_path.parts[:-1]:
            next_descriptor = os.open(part, directory_flags, dir_fd=directory_descriptor)
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor
        file_descriptor = os.open(
            relative_path.parts[-1],
            file_flags,
            dir_fd=directory_descriptor,
        )
        before = os.fstat(file_descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise SfldMigrationPlanError(f"trait candidate is not a regular file: {display_path}")
        if before.st_size < 1 or before.st_size > _MAX_TRAIT_BYTES:
            raise SfldMigrationPlanError(
                f"trait candidate size {before.st_size} is outside 1..{_MAX_TRAIT_BYTES}: "
                f"{display_path}"
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, _READ_CHUNK_BYTES)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        if _content_identity(after) != _content_identity(before):
            raise SfldMigrationPlanError(f"trait candidate changed while reading: {display_path}")
        return b"".join(chunks)
    except SfldMigrationPlanError:
        raise
    except OSError as error:
        raise SfldMigrationPlanError(
            f"cannot open trait candidate without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


@dataclass(frozen=True, slots=True)
class TraitCapture:
    path: Path
    relative_to_traits: Path
    record: Mapping[str, Any]
    yaml_sha256: str


def index_sfld_records(traits: Path) -> dict[str, TraitCapture]:
    """Index all semantic SFLD records without trusting location or first line."""

    if not traits.is_dir():
        raise SfldMigrationPlanError(f"missing trait directory: {traits}")
    _reject_trait_tree_symlinks(traits)
    lexical_root, root_descriptor, root_metadata = _open_trait_root(traits)
    try:
        candidates = _candidate_sfld_paths(traits)
        captured_candidates: dict[Path, tuple[Path, str]] = {}
        records: dict[str, TraitCapture] = {}
        for reported_path in candidates:
            path, relative_path = _validated_candidate_path(reported_path, lexical_root)
            raw = _read_candidate_from_root(
                root_descriptor=root_descriptor,
                relative_path=relative_path,
                display_path=path,
            )
            try:
                text = raw.decode("utf-8", errors="strict")
                record = yaml.load(text, Loader=_UniqueKeyLoader)
            except (UnicodeDecodeError, yaml.YAMLError) as error:
                raise SfldMigrationPlanError(f"cannot load trait record {path}: {error}") from error
            if type(record) is not dict:
                raise SfldMigrationPlanError(f"trait record is not a mapping: {path}")
            _require_json_shape(record, path=path)
            digest = hashlib.sha256(raw).hexdigest()
            captured_candidates[path] = (relative_path, digest)
            identifier = record.get("identifier")
            if not isinstance(identifier, str):
                continue
            namespace, separator, _ = identifier.partition(":")
            if separator != ":" or namespace.casefold() != "sfld":
                continue
            if namespace != "SFLD":
                raise SfldMigrationPlanError(
                    f"noncanonical SFLD namespace spelling {namespace!r} in {path}"
                )
            if path.suffix != ".yaml":
                raise SfldMigrationPlanError(
                    f"SFLD trait files require the exact lowercase .yaml suffix: {path}"
                )
            if _IDENTIFIER_RE.fullmatch(identifier) is None:
                raise SfldMigrationPlanError(f"invalid SFLD identifier {identifier!r} in {path}")
            if identifier in records:
                raise SfldMigrationPlanError(
                    f"duplicate SFLD identifier {identifier}: {records[identifier].path} and {path}"
                )
            records[identifier] = TraitCapture(path, relative_path, record, digest)

        _reject_trait_tree_symlinks(traits)
        _assert_trait_root_binding(lexical_root, root_descriptor, root_metadata)
        if _candidate_sfld_paths(traits) != candidates:
            raise SfldMigrationPlanError("trait candidate set changed during SFLD indexing")
        for path, (relative_path, expected_digest) in captured_candidates.items():
            current = _read_candidate_from_root(
                root_descriptor=root_descriptor,
                relative_path=relative_path,
                display_path=path,
            )
            if hashlib.sha256(current).hexdigest() != expected_digest:
                raise SfldMigrationPlanError(
                    f"trait candidate changed during SFLD indexing: {path}"
                )
        _reject_trait_tree_symlinks(traits)
        _assert_trait_root_binding(lexical_root, root_descriptor, root_metadata)
        return records
    finally:
        os.close(root_descriptor)


def _list_of_strings(value: Any, *, field: str, identifier: str) -> list[str]:
    if value is None:
        return []
    if type(value) is not list or any(type(item) is not str for item in value):
        raise SfldMigrationPlanError(f"{identifier}: {field} must be a list of strings")
    return list(value)


def _interpro_bindings(record: Mapping[str, Any], *, identifier: str) -> list[str]:
    value = record.get("mapped_xrefs")
    if value is None:
        return []
    if type(value) is not list:
        raise SfldMigrationPlanError(f"{identifier}: mapped_xrefs must be a list")
    out: list[str] = []
    for index, row in enumerate(value):
        if type(row) is not dict:
            raise SfldMigrationPlanError(f"{identifier}: mapped_xrefs[{index}] must be a mapping")
        object_id = row.get("object")
        if isinstance(object_id, str) and object_id.startswith("InterPro:"):
            accession = object_id.split(":", 1)[1]
            if re.fullmatch(r"IPR[0-9]{6}", accession) is None:
                raise SfldMigrationPlanError(
                    f"{identifier}: invalid mapped InterPro accession {object_id!r}"
                )
            out.append(accession)
    if len(out) != len(set(out)):
        raise SfldMigrationPlanError(f"{identifier}: duplicate mapped InterPro accession")
    return sorted(out)


def _definition_status(
    record: Mapping[str, Any],
    *,
    identifier: str,
    interpro_bindings: list[str],
    interpro_types: Mapping[str, str],
) -> str:
    source = record.get("definition_source")
    if not isinstance(source, str):
        return "UNRECOGNIZED_DEFINITION_PROVENANCE"
    if source == "SFLD signature name (composed; no curated InterPro abstract)":
        return (
            "GENERATED_SIGNATURE_RESTATEMENT"
            if not interpro_bindings
            else "GENERATED_WITH_INTERPRO_BINDING_REVIEW"
        )
    if len(interpro_bindings) == 1:
        accession = interpro_bindings[0]
        entry_type = interpro_types.get(accession)
        if entry_type is None:
            raise SfldMigrationPlanError(
                f"{identifier}: mapped InterPro entry {accession} is absent from pinned XML"
            )
        if f"InterPro:{accession} abstract" not in source:
            return "INTERPRO_BINDING_DEFINITION_SOURCE_MISMATCH"
        if entry_type == "family":
            return "INTERPRO_FAMILY_ABSTRACT"
        if entry_type == "domain":
            return "INTERPRO_DOMAIN_ABSTRACT_GRANULARITY_REVIEW"
        return "INTERPRO_OTHER_TYPE_ABSTRACT_REVIEW"
    return "UNRECOGNIZED_DEFINITION_PROVENANCE"


def _relative_repo_path(path: Path, repo_root: Path, *, identifier: str) -> str:
    lexical_root = Path(os.path.abspath(repo_root))
    lexical_path = Path(os.path.abspath(path))
    try:
        relative = lexical_path.relative_to(lexical_root)
        resolved_root = lexical_root.resolve(strict=True)
        resolved_path = lexical_path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise SfldMigrationPlanError(
            f"{identifier}: trait path escapes repository root: {path}"
        ) from error
    except (OSError, RuntimeError) as error:
        raise SfldMigrationPlanError(
            f"{identifier}: cannot resolve repository path {path}: {error}"
        ) from error
    return relative.as_posix()


def _current_level(identifier: str) -> str:
    return {"S": "SUPERFAMILY", "G": "SUBGROUP", "F": "FAMILY"}[identifier[9]]


def _review_value_projection(
    record: Mapping[str, Any],
    field_names: Iterable[str],
) -> dict[str, dict[str, Any]]:
    """Preserve missing-versus-null semantics for values a reviewer must inspect."""

    return {
        field_name: {
            "present": field_name in record,
            "value": record.get(field_name),
        }
        for field_name in field_names
    }


def plan_record(
    *,
    capture: TraitCapture,
    release: SfldRelease,
    interpro_types: Mapping[str, str],
    repo_root: Path,
) -> dict[str, Any]:
    record = capture.record
    identifier = record.get("identifier")
    if not isinstance(identifier, str) or _IDENTIFIER_RE.fullmatch(identifier) is None:
        raise SfldMigrationPlanError(f"invalid indexed SFLD identifier {identifier!r}")
    accession = identifier.split(":", 1)[1]
    record_path = _relative_repo_path(capture.path, repo_root, identifier=identifier)
    expected_parent = (
        [f"SFLD:{release.direct_parents[accession]}"] if accession in release.direct_parents else []
    )
    current_parents = _list_of_strings(
        record.get("parent_traits"),
        field="parent_traits",
        identifier=identifier,
    )
    path_status = (
        "EXPECTED_LEGACY_ROUTE"
        if Path(record_path).parent.as_posix() == CURRENT_LEGACY_ROUTE["directory"]
        else "PATH_REVIEW"
    )
    current_route = {
        "trait_axis": record.get("trait_axis"),
        "trait_category": record.get("trait_category"),
    }
    route_status = (
        "LEGACY_WHOLE_PROTEIN_FUNCTION_ROUTE_SEMANTIC_REVIEW"
        if current_route
        == {
            "trait_axis": CURRENT_LEGACY_ROUTE["trait_axis"],
            "trait_category": CURRENT_LEGACY_ROUTE["trait_category"],
        }
        else "CURRENT_ROUTE_DRIFT_REVIEW"
    )
    interpro_bindings = _interpro_bindings(record, identifier=identifier)
    integration_types: list[str] = []
    for interpro_accession in interpro_bindings:
        entry_type = interpro_types.get(interpro_accession)
        if entry_type is None:
            raise SfldMigrationPlanError(
                f"{identifier}: mapped InterPro entry {interpro_accession} absent from pinned XML"
            )
        integration_types.append(entry_type)
    definition_status = _definition_status(
        record,
        identifier=identifier,
        interpro_bindings=interpro_bindings,
        interpro_types=interpro_types,
    )
    definition_review_projection = _review_value_projection(
        record,
        (
            "label",
            "definition",
            "definition_source",
            "definitions",
            "synonyms",
            "mapped_xrefs",
        ),
    )

    review_requirements = ["SEMANTIC_ROUTING_REVIEW", "DEFINITION_REVIEW"]
    model = release.models.get(accession)
    if model is None:
        profile_status = "NO_EXECUTABLE_SOURCE_MODEL"
        parent_status = "NO_EXECUTABLE_SOURCE_MODEL"
        label_status = "NO_EXECUTABLE_SOURCE_MODEL"
        source_profile = None
        source_profile_sha256 = None
        source_model = None
        review_requirements.append("NO_EXECUTABLE_MODEL_DISPOSITION_REVIEW")
        classification = "NO_EXECUTABLE_MODEL_DISPOSITION_REVIEW_REQUIRED"
    else:
        source_profile = build_sfld_profile_representation(release, accession)
        source_profile_sha256 = value_sha256(source_profile)
        current_profiles = record.get("sequence_profile_representations")
        if current_profiles is None:
            profile_status = "SOURCE_PROFILE_AVAILABLE_NOT_SERIALIZED"
        elif current_profiles == [source_profile]:
            profile_status = "EXACT_SOURCE_PROFILE_ALREADY_SERIALIZED"
        else:
            profile_status = "SOURCE_PROFILE_SERIALIZATION_CONFLICT_REVIEW"
            review_requirements.append("PROFILE_SERIALIZATION_CONFLICT_REVIEW")
        review_requirements.append("PROFILE_REPRESENTATION_REVIEW")
        parent_status = (
            "MATCHES_SOURCE_HIERARCHY" if current_parents == expected_parent else "HIERARCHY_REVIEW"
        )
        if parent_status == "HIERARCHY_REVIEW":
            review_requirements.append("HIERARCHY_REVIEW")
        label = record.get("label")
        if not isinstance(label, str):
            label_status = "LABEL_REVIEW"
            review_requirements.append("LABEL_REVIEW")
        elif label == model.description:
            label_status = "EXACT_SOURCE_DESCRIPTION"
        elif " ".join(label.split()) == " ".join(model.description.split()):
            label_status = "SOURCE_DESCRIPTION_WHITESPACE_NORMALIZATION_REVIEW"
            review_requirements.append("LABEL_NORMALIZATION_REVIEW")
        else:
            label_status = "LABEL_REVIEW"
            review_requirements.append("LABEL_REVIEW")
        source_model = {
            "accession": accession,
            "name": model.name,
            "description": model.description,
            "native_classification_level": model.native_classification_level,
            "source_model_record_sha256": model.source_record_sha256,
            "source_site_record_sha256": release.site_rules[accession].source_record_sha256,
            "source_immediate_parent": expected_parent[0] if expected_parent else None,
        }
        classification = "EXECUTABLE_MODEL_SEMANTIC_REVIEW_REQUIRED"

    if definition_status == "INTERPRO_DOMAIN_ABSTRACT_GRANULARITY_REVIEW":
        review_requirements.append("INTERPRO_DOMAIN_GRANULARITY_REVIEW")
    elif definition_status not in {
        "GENERATED_SIGNATURE_RESTATEMENT",
        "INTERPRO_FAMILY_ABSTRACT",
    }:
        review_requirements.append("DEFINITION_PROVENANCE_REVIEW")
    if path_status == "PATH_REVIEW":
        review_requirements.append("PATH_REVIEW")
    if route_status == "CURRENT_ROUTE_DRIFT_REVIEW":
        review_requirements.append("CURRENT_ROUTE_DRIFT_REVIEW")

    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": ROW_KIND,
        "identifier": identifier,
        "accession": accession,
        "current_native_level_from_accession": _current_level(identifier),
        "record_path": record_path,
        "current_record_yaml_sha256": capture.yaml_sha256,
        "current_record_hash_domain": "EXACT_YAML_BYTES",
        "classification": classification,
        "review_requirements": review_requirements,
        "path_status": path_status,
        "current_route": current_route,
        "route_status": route_status,
        "routing_decision": None,
        "routing_decision_status": "NOT_MADE_REVIEW_REQUIRED",
        "current_parent_traits": current_parents,
        "source_parent_traits": expected_parent if model is not None else None,
        "parent_status": parent_status,
        "current_label": record.get("label"),
        "source_label_status": label_status,
        "definition_status": definition_status,
        "definition_review_projection": definition_review_projection,
        "definition_review_projection_sha256": value_sha256(definition_review_projection),
        "definition_decision": None,
        "definition_decision_status": "NOT_MADE_REVIEW_REQUIRED",
        "integrating_interpro_accessions": interpro_bindings,
        "integrating_interpro_types": integration_types,
        "profile_status": profile_status,
        "source_model": source_model,
        "source_profile_projection": source_profile,
        "source_profile_projection_sha256": source_profile_sha256,
        "source_profile_projection_status": (
            "SOURCE_FACT_NOT_A_PROTEIN_MATCH_OR_MIGRATION_AUTHORIZATION"
            if source_profile is not None
            else "UNAVAILABLE_NO_EXECUTABLE_MODEL"
        ),
        "record_serialization_status": "NOT_MATERIALIZED_REVIEW_ONLY",
        "apply_authorized": False,
        "grounding_eligible": False,
        "grounding_gate": GROUNDING_GATE,
    }
    row["row_sha256"] = value_sha256(row)
    return row


def _source_projection(release: SfldRelease) -> list[dict[str, Any]]:
    return [
        {
            "accession": accession,
            "source_model_record_sha256": release.models[accession].source_record_sha256,
            "source_site_record_sha256": release.site_rules[accession].source_record_sha256,
            "source_immediate_parent": release.direct_parents.get(accession),
        }
        for accession in sorted(release.models)
    ]


def build_plan(
    *,
    records: Mapping[str, TraitCapture],
    snapshot: SourceSnapshot,
    repo_root: Path = REPO_ROOT,
    expected_modelless_accessions: frozenset[str] = SFLD_4_MODELLESS_CURRENT_ACCESSIONS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    for identifier, capture in records.items():
        if capture.record.get("identifier") != identifier:
            raise SfldMigrationPlanError(
                f"SFLD record index key {identifier!r} does not match captured identifier "
                f"{capture.record.get('identifier')!r}"
            )
    invalid_modelless = sorted(
        accession
        for accession in expected_modelless_accessions
        if re.fullmatch(r"SFLD[SGF][0-9]{5}", accession) is None
    )
    if invalid_modelless:
        raise SfldMigrationPlanError(
            f"invalid expected model-less SFLD accessions: {invalid_modelless!r}"
        )
    source_ids = {f"SFLD:{accession}" for accession in snapshot.release.models}
    expected_modelless_ids = {f"SFLD:{accession}" for accession in expected_modelless_accessions}
    current_ids = set(records)
    if source_ids - current_ids:
        raise SfldMigrationPlanError(
            f"SFLD source models lack current records: {sorted(source_ids - current_ids)[:5]!r}"
        )
    current_only = current_ids - source_ids
    if current_only != expected_modelless_ids:
        raise SfldMigrationPlanError(
            "SFLD current-only record set differs from the exact reviewed model-less set: "
            f"expected={sorted(expected_modelless_ids)!r}, found={sorted(current_only)!r}"
        )

    rows = [
        plan_record(
            capture=records[identifier],
            release=snapshot.release,
            interpro_types=snapshot.interpro_types,
            repo_root=repo_root,
        )
        for identifier in sorted(current_ids)
    ]
    binding_projection = [
        {
            "identifier": row["identifier"],
            "record_path": row["record_path"],
            "current_record_yaml_sha256": row["current_record_yaml_sha256"],
        }
        for row in rows
    ]
    source_projection = _source_projection(snapshot.release)
    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": SUMMARY_KIND,
        "plan_kind": PLAN_KIND,
        "source_release": snapshot.release.release,
        "source_model_manifest_sha256": snapshot.manifest["manifest_sha256"],
        "source_hmm_sha256": snapshot.release.hmm_sha256,
        "source_hierarchy_sha256": snapshot.release.hierarchy_sha256,
        "source_sites_sha256": snapshot.release.sites_sha256,
        "interpro_xml_sha256": snapshot.interpro_xml_sha256,
        "interpro_xml_role": "INTEGRATING_ENTRY_TYPE_REVIEW_ONLY_NOT_EXECUTABLE_MODEL",
        "legacy_sfld_api_snapshot_status": "ABSENT_NOT_REPLAYED",
        "source_model_count": len(source_ids),
        "current_record_count": len(rows),
        "model_less_current_count": len(expected_modelless_ids),
        "model_less_current_identifiers": sorted(expected_modelless_ids),
        "current_level_counts": dict(
            sorted(Counter(row["current_native_level_from_accession"] for row in rows).items())
        ),
        "classification_counts": dict(
            sorted(Counter(row["classification"] for row in rows).items())
        ),
        "profile_status_counts": dict(
            sorted(Counter(row["profile_status"] for row in rows).items())
        ),
        "parent_status_counts": dict(sorted(Counter(row["parent_status"] for row in rows).items())),
        "source_label_status_counts": dict(
            sorted(Counter(row["source_label_status"] for row in rows).items())
        ),
        "definition_status_counts": dict(
            sorted(Counter(row["definition_status"] for row in rows).items())
        ),
        "integrating_interpro_type_counts": dict(
            sorted(
                Counter(
                    entry_type for row in rows for entry_type in row["integrating_interpro_types"]
                ).items()
            )
        ),
        "path_status_counts": dict(sorted(Counter(row["path_status"] for row in rows).items())),
        "route_status_counts": dict(sorted(Counter(row["route_status"] for row in rows).items())),
        "source_profile_projection_count": sum(
            row["source_profile_projection"] is not None for row in rows
        ),
        "source_site_position_count": sum(
            row["source_profile_projection"]["site_count"]
            for row in rows
            if row["source_profile_projection"] is not None
        ),
        "source_site_feature_pattern_count": sum(
            row["source_profile_projection"]["site_feature_pattern_count"]
            for row in rows
            if row["source_profile_projection"] is not None
        ),
        "review_required_count": len(rows),
        "content_ready_count": 0,
        "current_trait_binding_sha256": value_sha256(binding_projection),
        "source_model_projection_sha256": value_sha256(source_projection),
        "rows_sha256": rows_sha256(rows),
        "routing_policy_status": "NOT_DECIDED_FULL_FILE_REVIEW_REQUIRED",
        "definition_policy_status": "NOT_DECIDED_FULL_FILE_REVIEW_REQUIRED",
        "serialization_status": "NOT_PERFORMED",
        "writer_available": False,
        "apply_authorized": False,
        "grounding_eligible": False,
        "grounding_gate": GROUNDING_GATE,
        "quiescence_contract": QUIESCENCE_CONTRACT,
    }
    summary["plan_id"] = PLAN_ID_PREFIX + value_sha256(summary)
    return rows, summary


def dump_plan(rows: Iterable[Mapping[str, Any]], summary: Mapping[str, Any]) -> str:
    return "".join(canonical_json(row) + "\n" for row in [*rows, summary])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hmm", type=Path, default=DEFAULT_HMM)
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY)
    parser.add_argument("--sites", type=Path, default=DEFAULT_SITES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--interpro", type=Path, default=DEFAULT_INTERPRO)
    parser.add_argument("--traits", type=Path, default=DEFAULT_TRAITS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        snapshot = load_verified_source_snapshot(
            hmm_path=args.hmm,
            hierarchy_path=args.hierarchy,
            sites_path=args.sites,
            manifest_path=args.manifest,
            interpro_path=args.interpro,
        )
        records = index_sfld_records(args.traits)
        rows, summary = build_plan(records=records, snapshot=snapshot)
    except SfldMigrationPlanError as error:
        print(f"SFLD migration planning failed: {error}", file=sys.stderr)
        return 1
    sys.stdout.write(dump_plan(rows, summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
