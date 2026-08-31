#!/usr/bin/env python3
"""Plan the PRINTS 42.0 source-model migration without writing trait records.

The legacy PRINTS records were seeded from member names and integrating InterPro
abstracts.  A fingerprint is instead defined by its source-native ``gd`` text
and ordered final motif sets.  This command verifies the allowlisted four-file
snapshot, exact-matches every current record against the known legacy state, and
emits a content-addressed migration plan as canonical JSONL on stdout.

There is deliberately no apply path.  Routing conflicts and any record outside
the exact legacy/source-native envelopes are review-only; both PRINTS grounding
and promotion gates remain independent and closed.

The repository trait tree must be quiescent while this read-only planner runs.
The command binds one trait-root descriptor, uses descriptor-relative no-follow
opens, and performs candidate-set/content drift checks, but it cannot create an
atomic filesystem snapshot against an uncooperative concurrent writer.
"""

from __future__ import annotations

import argparse
import copy
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
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

import ripgrep_prefilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seed_interpro_members as seeder  # noqa: E402
from prints_kdat import (  # noqa: E402
    PrintsFingerprint,
    PrintsRelease,
    build_fingerprint_representation,
)
from prints_snapshot import (  # noqa: E402
    EXPECTED_PRINTS_SNAPSHOT_ID,
    HIERARCHY_NAME,
    MANIFEST_NAME,
    PrintsSnapshotError,
    load_verified_prints_snapshot,
    parse_hierarchy_source,
)

SCHEMA_VERSION = 3
PLAN_KIND = "PRINTS_SOURCE_MODEL_MIGRATION_PLAN"
ROW_KIND = "PRINTS_SOURCE_MODEL_MIGRATION_ROW"
SUMMARY_KIND = "PRINTS_SOURCE_MODEL_MIGRATION_SUMMARY"
PLAN_ID_PREFIX = "prints-migration-plan:"
REPO_ROOT = Path(__file__).resolve().parents[1]
MEMBERS_DIR = REPO_ROOT / "data" / "raw" / "interpro_members"
DEFAULT_API = MEMBERS_DIR / "prints.jsonl"
DEFAULT_KDAT = MEMBERS_DIR / "prints42_0.kdat"
DEFAULT_HIERARCHY = MEMBERS_DIR / HIERARCHY_NAME
DEFAULT_HIERARCHY_SOURCE = MEMBERS_DIR / "FingerPRINTShierarchy21Feb2012"
DEFAULT_MANIFEST = MEMBERS_DIR / MANIFEST_NAME
DEFAULT_INTERPRO = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
DEFAULT_TRAITS = REPO_ROOT / "data" / "traits"
LEGACY_DEFINITION_CAP = 1800
LEGACY_HIERARCHY_SOURCE_SHA256 = "8e852b14bc579bf22c7278e5cadd69d27389bef0371e33444793359822116881"
_READ_CHUNK_BYTES = 1024 * 1024
_SOURCE_CAPTURE_LIMITS = {
    "manifest": 1024 * 1024,
    "api": 4 * 1024 * 1024,
    "kdat": 128 * 1024 * 1024,
    "hierarchy": 8 * 1024 * 1024,
    "interpro": 256 * 1024 * 1024,
    "legacy_hierarchy_source": 8 * 1024 * 1024,
}

_IDENTIFIER = re.compile(r"^PRINTS:PR[0-9]{5}$")
_INTERPRO_OPEN = re.compile(r'<interpro id="(IPR[0-9]{6})"[^>]*\btype="([^"]+)"')
_NORMALIZED_HIERARCHY_FIELDS = frozenset(
    {
        "accession",
        "code",
        "domain_flag",
        "evalue_cutoff",
        "hierarchical_relations",
        "minimum_motif_count",
    }
)
_MANAGED_FIELDS = frozenset(
    {
        "label",
        "definition",
        "definition_source",
        "parent_traits",
        "synonyms",
        "mapped_xrefs",
        "definitions",
        "sequence_fingerprint_representations",
        "license",
    }
)


class PrintsMigrationError(ValueError):
    """The migration cannot be planned exactly from the supplied state."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses silent duplicate-key collapse."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
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
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
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
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require_json_shape(
    value: Any,
    *,
    path: Path,
    location: str = "$",
    ancestors: frozenset[int] = frozenset(),
) -> None:
    """Reject SafeLoader-native values that have no canonical JSON meaning."""

    if value is None or type(value) in {bool, int, str}:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise PrintsMigrationError(
                f"trait record is not JSON-shaped at {location} in {path}: non-finite number"
            )
        return
    if type(value) not in {list, dict}:
        raise PrintsMigrationError(
            f"trait record is not JSON-shaped at {location} in {path}: "
            f"unsupported {type(value).__name__}"
        )
    identity = id(value)
    if identity in ancestors:
        raise PrintsMigrationError(f"trait record has a YAML alias cycle at {location} in {path}")
    nested_ancestors = ancestors | {identity}
    if type(value) is list:
        for index, item in enumerate(value):
            _require_json_shape(
                item,
                path=path,
                location=f"{location}[{index}]",
                ancestors=nested_ancestors,
            )
        return
    for key, item in value.items():
        if type(key) is not str:
            raise PrintsMigrationError(
                f"trait record is not JSON-shaped at {location} in {path}: "
                f"mapping key {key!r} is not a string"
            )
        _require_json_shape(
            item,
            path=path,
            location=f"{location}.{key}",
            ancestors=nested_ancestors,
        )


def _normalise_type(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _legacy_kdat_text(value: str) -> str:
    """Reproduce the legacy parser's UTF-8-with-replacement source decoding."""

    return value.encode("latin-1", errors="strict").decode("utf-8", errors="replace")


def load_legacy_generated_parents(path: Path) -> dict[str, str]:
    """Replay the historical parent-generation bug only as provenance evidence.

    The checksum-pinned raw table preserves the line order used by the old
    seeder's tie-breaking.  This function deliberately reproduces that old
    algorithm so a current parent can be proven to be generated state; its
    output must never be interpreted as an ontology hierarchy.
    """

    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as error:
        raise PrintsMigrationError(
            f"cannot read legacy hierarchy source {path}: {error}"
        ) from error
    if hashlib.sha256(raw).hexdigest() != LEGACY_HIERARCHY_SOURCE_SHA256:
        raise PrintsMigrationError(f"legacy PRINTS hierarchy source checksum mismatch: {path}")
    # Apply the corrected parser first so malformed source cannot enter the
    # historical replay merely because the old parser was permissive.
    parse_hierarchy_source(raw)
    code_to_accession: dict[str, str] = {}
    relation_sets: dict[str, set[str]] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        code, accession, _evalue, _minimum_motifs, relation_text = (
            part.strip() for part in line.split("|")
        )
        code_to_accession[code] = accession
        if relation_text and relation_text != "*":
            relation_sets[code] = {
                relation.strip() for relation in relation_text.split(",") if relation.strip()
            }
    generated: dict[str, str] = {}
    for child_code, child_accession in code_to_accession.items():
        holders = [
            code
            for code, relations in relation_sets.items()
            if child_code in relations and code != child_code
        ]
        if holders:
            historical_parent_code = min(holders, key=lambda code: len(relation_sets[code]))
            generated[child_accession] = code_to_accession[historical_parent_code]
    return generated


def load_interpro_entry_types(
    path: Path | None = None,
    *,
    captured_gzip: bytes | None = None,
) -> dict[str, str]:
    """Load entry types from a path or an already snapshot-bound gzip capture."""

    if path is not None and captured_gzip is not None:
        raise PrintsMigrationError(
            "pass an InterPro XML path or captured bytes to the type loader, not both"
        )
    if path is None and captured_gzip is None:
        raise PrintsMigrationError("missing InterPro XML input for the type loader")
    source_label = str(path) if path is not None else "<manifest-bound InterPro XML capture>"

    out: dict[str, str] = {}
    try:
        if captured_gzip is None:
            assert path is not None
            source_handle = gzip.open(path, "rt", encoding="utf-8", errors="strict")
        else:
            compressed = gzip.GzipFile(fileobj=io.BytesIO(captured_gzip), mode="rb")
            source_handle = io.TextIOWrapper(compressed, encoding="utf-8", errors="strict")
        with source_handle as handle:
            for line_number, line in enumerate(handle, 1):
                match = _INTERPRO_OPEN.search(line)
                if match is None:
                    continue
                accession, raw_type = match.groups()
                entry_type = _normalise_type(raw_type)
                if accession in out:
                    raise PrintsMigrationError(
                        f"{source_label}:{line_number}: duplicate InterPro entry {accession}"
                    )
                out[accession] = entry_type
    except (OSError, EOFError, UnicodeDecodeError) as error:
        raise PrintsMigrationError(
            f"cannot parse InterPro entry types from {source_label}: {error}"
        ) from error
    if not out:
        raise PrintsMigrationError(f"no InterPro entry types found in {source_label}")
    return out


def _route(entry_type: str) -> dict[str, str]:
    route = seeder.TYPE_MAP.get(entry_type)
    if route is None:
        raise PrintsMigrationError(f"unroutable PRINTS/InterPro type {entry_type!r}")
    axis, category, directory = route
    return {"trait_axis": axis, "trait_category": category, "directory": directory}


def _candidate_prints_paths(traits: Path) -> list[Path]:
    """Return every byte-level PRINTS/escape/UTF-16 candidate via ripgrep."""

    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits), "PRINTS migration")
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
        "(?i)PRINTS",
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
        raise PrintsMigrationError(f"cannot run ripgrep trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise PrintsMigrationError(f"ripgrep trait prefilter failed: {detail}")
    return sorted(
        Path(raw_path.decode("utf-8", errors="strict"))
        for raw_path in scan.stdout.split(b"\0")
        if raw_path
    )


def _reject_trait_tree_symlinks(traits: Path) -> None:
    """Fail closed if any directory entry below the trait root is a symlink."""

    lexical_root = Path(os.path.abspath(traits))
    if lexical_root.is_symlink():
        raise PrintsMigrationError(f"trait directory is a symlink: {traits}")

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
                    raise PrintsMigrationError(
                        f"symlink below trait directory is not allowed: {candidate}"
                    )
        if walk_error is not None:
            raise walk_error
    except OSError as error:
        raise PrintsMigrationError(f"cannot inspect trait directory {traits}: {error}") from error


def _validated_candidate_path(path: Path, traits: Path) -> tuple[Path, Path]:
    """Return an in-root lexical path and its relative descriptor path."""

    lexical_root = Path(os.path.abspath(traits))
    lexical_path = Path(os.path.abspath(path))
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise PrintsMigrationError(
            f"trait candidate escapes trait directory before read: {path}"
        ) from error

    current = lexical_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise PrintsMigrationError(
                f"trait candidate traverses a symlink before read: {current}"
            )

    try:
        resolved_root = lexical_root.resolve(strict=True)
        resolved_path = lexical_path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise PrintsMigrationError(
            f"trait candidate escapes trait directory before read: {path}"
        ) from error
    except (OSError, RuntimeError) as error:
        raise PrintsMigrationError(
            f"cannot resolve trait candidate before read {path}: {error}"
        ) from error
    if not relative.parts:
        raise PrintsMigrationError(f"trait candidate is the trait directory itself: {path}")
    return lexical_path, relative


def _descriptor_safety_flags() -> tuple[int, int]:
    """Require the no-follow descriptor operations used by the planner contract."""

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
        raise PrintsMigrationError(
            "platform lacks required O_NOFOLLOW/O_DIRECTORY/dir_fd filesystem safety"
        )
    return os.O_RDONLY | directory_only | no_follow, os.O_RDONLY | no_follow


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


def _capture_regular_source(path: Path, *, label: str, max_bytes: int) -> bytes:
    """Capture one bounded source through a stable component-no-follow chain."""

    if max_bytes < 1:
        raise PrintsMigrationError(f"{label}: invalid capture byte limit")
    directory_flags, file_flags = _descriptor_safety_flags()
    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    directory_flags |= close_on_exec
    file_flags |= close_on_exec | getattr(os, "O_NONBLOCK", 0)

    lexical = Path(os.path.abspath(path)) if path.is_absolute() else path
    parts = lexical.parts
    if lexical.is_absolute():
        component_names = parts[1:]
        start = lexical.anchor
    else:
        component_names = parts
        start = "."
    if not component_names or any(component in {"", ".", ".."} for component in component_names):
        raise PrintsMigrationError(f"{label}: path must have ordinary components: {path}")

    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        try:
            current = os.open(start, directory_flags)
        except OSError as error:
            raise PrintsMigrationError(
                f"{label}: cannot safely open path root for {path}: {error}"
            ) from error
        descriptors.append(current)
        for component in component_names[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                child_metadata = os.fstat(child)
            except OSError as error:
                if isinstance(error, FileNotFoundError):
                    raise PrintsMigrationError(f"missing {label}: {path}") from error
                raise PrintsMigrationError(
                    f"{label}: cannot safely open directory component {component!r}: {error}"
                ) from error
            bindings.append((current, component, _entry_identity(child_metadata)))
            descriptors.append(child)
            current = child

        final_name = component_names[-1]
        try:
            file_descriptor = os.open(final_name, file_flags, dir_fd=current)
            before = os.fstat(file_descriptor)
        except OSError as error:
            if isinstance(error, FileNotFoundError):
                raise PrintsMigrationError(f"missing {label}: {path}") from error
            raise PrintsMigrationError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        descriptors.append(file_descriptor)
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise PrintsMigrationError(f"{label}: input is not a regular file: {path}")
        if before.st_size < 1 or before.st_size > max_bytes:
            raise PrintsMigrationError(
                f"{label}: input size {before.st_size} is outside 1..{max_bytes} bytes"
            )

        chunks: list[bytes] = []
        captured_bytes = 0
        while True:
            try:
                chunk = os.read(
                    file_descriptor,
                    min(_READ_CHUNK_BYTES, max_bytes - captured_bytes + 1),
                )
            except OSError as error:
                raise PrintsMigrationError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured_bytes += len(chunk)
            if captured_bytes > max_bytes:
                raise PrintsMigrationError(f"{label}: input exceeds the {max_bytes}-byte limit")
        raw = b"".join(chunks)
        after = os.fstat(file_descriptor)
        if len(raw) != before.st_size or _content_identity(after) != _content_identity(before):
            raise PrintsMigrationError(f"{label}: input changed during capture")

        for parent_descriptor, component, expected_identity in bindings:
            try:
                live = os.stat(component, dir_fd=parent_descriptor, follow_symlinks=False)
            except OSError as error:
                raise PrintsMigrationError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected_identity:
                raise PrintsMigrationError(
                    f"{label}: path component changed during capture: {component!r}"
                )
        return raw
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _open_trait_root(traits: Path) -> tuple[Path, int, os.stat_result]:
    """Bind one non-symlink trait-root directory for descriptor-relative reads."""

    lexical_root = Path(os.path.abspath(traits))
    flags, _ = _descriptor_safety_flags()
    descriptor: int | None = None
    try:
        descriptor = os.open(lexical_root, flags)
        metadata = os.fstat(descriptor)
    except OSError as error:
        if descriptor is not None:
            os.close(descriptor)
        raise PrintsMigrationError(f"cannot bind trait directory {traits}: {error}") from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise PrintsMigrationError(f"trait root is not a directory: {traits}")
    return lexical_root, descriptor, metadata


def _assert_trait_root_binding(
    lexical_root: Path, descriptor: int, expected: os.stat_result
) -> None:
    """Reject replacement of the path naming the bound trait-root directory."""

    try:
        current_path = os.stat(lexical_root, follow_symlinks=False)
        current_descriptor = os.fstat(descriptor)
    except OSError as error:
        raise PrintsMigrationError(
            f"cannot recheck bound trait directory {lexical_root}: {error}"
        ) from error

    def identity(value: os.stat_result) -> tuple[int, int, int]:
        return value.st_dev, value.st_ino, stat.S_IFMT(value.st_mode)

    if identity(current_path) != identity(expected) or identity(current_descriptor) != identity(
        expected
    ):
        raise PrintsMigrationError(
            f"trait directory binding changed during indexing: {lexical_root}"
        )


def _read_candidate_from_root(
    *,
    root_descriptor: int,
    relative_path: Path,
    display_path: Path,
) -> bytes:
    """Read one regular candidate without following any path-component symlink."""

    directory_flags, file_flags = _descriptor_safety_flags()
    directory_descriptor = os.dup(root_descriptor)
    file_descriptor: int | None = None
    try:
        for part in relative_path.parts[:-1]:
            next_descriptor = os.open(part, directory_flags, dir_fd=directory_descriptor)
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor
        file_descriptor = os.open(relative_path.parts[-1], file_flags, dir_fd=directory_descriptor)
        before = os.fstat(file_descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise PrintsMigrationError(f"trait candidate is not a regular file: {display_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable_fields = (
            "st_dev",
            "st_ino",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
            raise PrintsMigrationError(f"trait candidate changed while reading: {display_path}")
        return b"".join(chunks)
    except PrintsMigrationError:
        raise
    except OSError as error:
        raise PrintsMigrationError(
            f"cannot open trait candidate without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


def index_prints_records(traits: Path) -> dict[str, tuple[Path, dict[str, Any], str]]:
    """Find every possible PRINTS-bearing YAML, parse it, then filter by namespace.

    Namespace filtering based on a literal first line can hide a duplicate whose
    YAML starts with ``---``, a comment, quoted/escaped keys, or a flow mapping.
    Rather than constructing all 429,000+ records, the repository-wide byte
    prefilter admits every YAML containing literal ``PRINTS``, any backslash, or
    NUL bytes from a possible UTF-16/32 encoding.
    A semantic PRINTS string either contains those literal ASCII characters or
    uses a YAML escape/continued quoted scalar, which necessarily contains a
    backslash. Every admitted file is parsed with duplicate-key rejection before
    namespace filtering.
    """

    if not traits.is_dir():
        raise PrintsMigrationError(f"missing trait directory: {traits}")
    _reject_trait_tree_symlinks(traits)
    lexical_root, root_descriptor, root_metadata = _open_trait_root(traits)
    try:
        candidate_paths = _candidate_prints_paths(traits)
        candidate_hashes: dict[Path, tuple[Path, str]] = {}
        out: dict[str, tuple[Path, dict[str, Any], str]] = {}
        for reported_path in candidate_paths:
            path, relative_path = _validated_candidate_path(reported_path, lexical_root)
            try:
                raw = _read_candidate_from_root(
                    root_descriptor=root_descriptor,
                    relative_path=relative_path,
                    display_path=path,
                )
                text = raw.decode("utf-8", errors="strict")
                record = yaml.load(text, Loader=_UniqueKeyLoader)
            except (UnicodeDecodeError, yaml.YAMLError) as error:
                raise PrintsMigrationError(f"cannot load trait record {path}: {error}") from error
            if not isinstance(record, dict):
                raise PrintsMigrationError(f"trait record is not a mapping: {path}")
            _require_json_shape(record, path=path)
            raw_sha256 = hashlib.sha256(raw).hexdigest()
            candidate_hashes[path] = (relative_path, raw_sha256)
            identifier = record.get("identifier")
            if not isinstance(identifier, str):
                continue
            namespace, separator, _ = identifier.partition(":")
            if separator != ":" or namespace.casefold() != "prints":
                continue
            if namespace != "PRINTS":
                raise PrintsMigrationError(
                    f"noncanonical PRINTS namespace spelling {namespace!r} in {path}"
                )
            if path.suffix != ".yaml":
                raise PrintsMigrationError(
                    f"PRINTS trait files require the exact lowercase .yaml suffix: {path}"
                )
            if _IDENTIFIER.fullmatch(identifier) is None:
                raise PrintsMigrationError(f"invalid PRINTS identifier {identifier!r} in {path}")
            if identifier in out:
                raise PrintsMigrationError(
                    f"duplicate PRINTS identifier {identifier}: {out[identifier][0]} and {path}"
                )
            out[identifier] = (path, record, raw_sha256)
        _reject_trait_tree_symlinks(traits)
        _assert_trait_root_binding(lexical_root, root_descriptor, root_metadata)
        if _candidate_prints_paths(traits) != candidate_paths:
            raise PrintsMigrationError("trait candidate set changed during PRINTS indexing")
        for path, (relative_path, expected_sha256) in candidate_hashes.items():
            current_sha256 = hashlib.sha256(
                _read_candidate_from_root(
                    root_descriptor=root_descriptor,
                    relative_path=relative_path,
                    display_path=path,
                )
            ).hexdigest()
            if current_sha256 != expected_sha256:
                raise PrintsMigrationError(
                    f"trait candidate changed during PRINTS indexing: {path}"
                )
        _reject_trait_tree_symlinks(traits)
        _assert_trait_root_binding(lexical_root, root_descriptor, root_metadata)
        return out
    finally:
        os.close(root_descriptor)


def _definition_rows(
    definition: str,
    source: str,
    method: str,
    signature: Mapping[str, Any],
    entry: Mapping[str, Any] | None,
    *,
    source_native: bool,
) -> list[dict[str, str]]:
    rows = [{"kind": "GENERAL", "text": definition, "source": source, "method": method}]
    accession = signature["accession"]
    interpro = signature.get("integrated")
    if source_native and seeder.is_curated_abstract(dict(entry) if entry else None):
        abstract = str(entry["abstract"])
        if abstract.strip() != definition.strip():
            rows.append(
                {
                    "kind": "GENERAL",
                    "text": abstract,
                    "source": (
                        f"InterPro:{interpro} abstract (PRINTS {accession} is a member signature)"
                    ),
                    "method": "SOURCED",
                }
            )
    elif entry and entry.get("abstract") and not seeder.is_curated_abstract(dict(entry)):
        rows.append(
            {
                "kind": "GENERAL",
                "text": str(entry["abstract"])[:LEGACY_DEFINITION_CAP].rstrip(),
                "source": (f"InterPro:{interpro} abstract (LLM-generated, not curator-reviewed)"),
                "method": "GENERATED",
            }
        )
    return rows


def legacy_record(
    signature: Mapping[str, Any],
    entry: Mapping[str, Any] | None,
    fingerprint: PrintsFingerprint,
) -> dict[str, Any]:
    """Reconstruct the exact pre-source-model seeder envelope."""

    accession = fingerprint.accession
    legacy_title = _legacy_kdat_text(fingerprint.title)
    identifier = f"PRINTS:{accession}"
    route = _route(str(signature["type"]))
    if seeder.is_curated_abstract(dict(entry) if entry else None):
        definition = str(entry["abstract"])[:LEGACY_DEFINITION_CAP].rstrip()
        source = f"InterPro:{signature.get('integrated')} abstract (PRINTS {accession} is a member signature)"
        method = "SOURCED"
    else:
        definition = seeder.compose_definition(
            "PRINTS",
            accession,
            legacy_title,
            str(signature["type"]).replace("_", " "),
            fingerprint.declared_motif_count,
        )
        source = "PRINTS signature name (composed; no curated InterPro abstract)"
        method = "GENERATED"
    record: dict[str, Any] = {
        "identifier": identifier,
        "label": legacy_title,
        "definition": definition,
        "definition_source": source,
        "trait_axis": route["trait_axis"],
        "trait_category": route["trait_category"],
        "term_kind": "CLASS",
        "mapping_status": "SEEDED",
    }
    if (
        entry
        and isinstance(entry.get("name"), str)
        and str(entry["name"]).strip().lower() != legacy_title.strip().lower()
    ):
        record["synonyms"] = [
            {
                "synonym_text": entry["name"],
                "synonym_type": "RELATED_SYNONYM",
                "source": f"InterPro:{signature.get('integrated')}",
            }
        ]
    if signature.get("integrated"):
        record["mapped_xrefs"] = [
            {
                "object": f"InterPro:{signature['integrated']}",
                "mapping_source": "interpro-member-list",
            }
        ]
    record["definitions"] = _definition_rows(
        definition, source, method, signature, entry, source_native=False
    )
    record["license"] = seeder.LICENSES["prints"]
    return record


def source_native_replacements(
    signature: Mapping[str, Any],
    entry: Mapping[str, Any] | None,
    release: PrintsRelease,
    fingerprint: PrintsFingerprint,
    *,
    remove_invalid_legacy_parent: bool,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    accession = fingerprint.accession
    source = f"PRINTS:{accession} gd description (release {release.release})"
    replacements: dict[str, Any] = {
        "label": fingerprint.title,
        "definition": fingerprint.description,
        "definition_source": source,
        "definitions": _definition_rows(
            fingerprint.description,
            source,
            "SOURCED",
            signature,
            entry,
            source_native=True,
        ),
        "sequence_fingerprint_representations": [
            build_fingerprint_representation(release, fingerprint)
        ],
        "license": seeder.LICENSES["prints"],
    }
    removals: list[str] = []
    if remove_invalid_legacy_parent:
        removals.append("parent_traits")
    if (
        entry
        and isinstance(entry.get("name"), str)
        and str(entry["name"]).strip().lower() != fingerprint.title.strip().lower()
    ):
        replacements["synonyms"] = [
            {
                "synonym_text": entry["name"],
                "synonym_type": "RELATED_SYNONYM",
                "source": f"InterPro:{signature.get('integrated')}",
            }
        ]
    else:
        removals.append("synonyms")
    if signature.get("integrated"):
        replacements["mapped_xrefs"] = [
            {
                "object": f"InterPro:{signature['integrated']}",
                "mapping_source": "interpro-member-list",
            }
        ]
    else:
        removals.append("mapped_xrefs")
    return replacements, tuple(sorted(removals))


def apply_replacements(
    record: Mapping[str, Any],
    replacements: Mapping[str, Any],
    removals: Iterable[str],
) -> dict[str, Any]:
    """Return a deep-copied proposal while preserving every unmanaged field."""

    proposed = copy.deepcopy(dict(record))
    for field_name in removals:
        proposed.pop(field_name, None)
    for field_name, value in replacements.items():
        proposed[field_name] = copy.deepcopy(value)
    return proposed


def _differing_fields(left: Mapping[str, Any], right: Mapping[str, Any]) -> list[str]:
    return sorted(
        key
        for key in set(left) | set(right)
        if key not in left
        or key not in right
        or canonical_json(left[key]) != canonical_json(right[key])
    )


def _semantically_equal(left: Any, right: Any) -> bool:
    """Compare JSON-shaped values without Python's bool/int coercion."""

    return canonical_json(left) == canonical_json(right)


def _presence_value(record: Mapping[str, Any], field_name: str) -> dict[str, Any]:
    """Project missing and explicit-null fields without conflating them."""

    present = field_name in record
    return {
        "present": present,
        "value": copy.deepcopy(record[field_name]) if present else None,
    }


def _record_review_value_projections(
    mismatch_fields: Iterable[str],
    *,
    current: Mapping[str, Any],
    legacy_expected: Mapping[str, Any],
    proposed: Mapping[str, Any],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Expose every exact value needed to review a legacy-state mismatch."""

    return {
        field_name: {
            "current": _presence_value(current, field_name),
            "legacy_expected": _presence_value(legacy_expected, field_name),
            "proposed": _presence_value(proposed, field_name),
        }
        for field_name in mismatch_fields
    }


def _normalized_hierarchy_binding(
    row: Mapping[str, Any], *, fingerprint: PrintsFingerprint
) -> dict[str, Any]:
    """Validate and copy one normalized hierarchy row into planner state."""

    if set(row) != _NORMALIZED_HIERARCHY_FIELDS:
        raise PrintsMigrationError(f"{fingerprint.accession}: normalized hierarchy fields differ")
    if row.get("accession") != fingerprint.accession or row.get("code") != fingerprint.code:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: normalized hierarchy identity disagrees with KDAT"
        )
    if type(row.get("domain_flag")) is not bool:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: normalized hierarchy domain_flag is not boolean"
        )
    if not isinstance(row.get("evalue_cutoff"), str):
        raise PrintsMigrationError(
            f"{fingerprint.accession}: normalized hierarchy evalue_cutoff is not a string"
        )
    relations = row.get("hierarchical_relations")
    if not isinstance(relations, list) or any(not isinstance(value, str) for value in relations):
        raise PrintsMigrationError(
            f"{fingerprint.accession}: normalized hierarchy relations are invalid"
        )
    minimum_motif_count = row.get("minimum_motif_count")
    if type(minimum_motif_count) is not int or minimum_motif_count < 0:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: normalized hierarchy minimum motif count is invalid"
        )
    return copy.deepcopy(dict(row))


def _legacy_comparison_projection(record: Mapping[str, Any]) -> dict[str, Any]:
    """Ignore only trailing whitespace introduced by the historical YAML emitter."""

    projected = copy.deepcopy(dict(record))
    if isinstance(projected.get("definition"), str):
        projected["definition"] = projected["definition"].rstrip()
    definitions = projected.get("definitions")
    if isinstance(definitions, list):
        for definition in definitions:
            if isinstance(definition, dict) and isinstance(definition.get("text"), str):
                definition["text"] = definition["text"].rstrip()
    return projected


def _hierarchy_projection(
    record: Mapping[str, Any], legacy_generated_parent: str | None
) -> tuple[str, dict[str, Any]]:
    """Classify current parents without deriving any from the relation table.

    The historical PRINTS seeder treated column five of the upstream
    post-processing table as subclass descendants.  A single PRINTS parent is
    therefore a recognizable legacy defect and may be removed from the exact
    state comparison.  Any other parent shape is preserved for manual review.
    """

    projected = copy.deepcopy(dict(record))
    if "parent_traits" not in projected:
        return "NONE", projected
    parents = projected.get("parent_traits")
    if (
        isinstance(parents, list)
        and len(parents) == 1
        and isinstance(parents[0], str)
        and _IDENTIFIER.fullmatch(parents[0]) is not None
    ):
        if parents[0] == f"PRINTS:{legacy_generated_parent}":
            projected.pop("parent_traits")
            return "CONFIRMED_LEGACY_GENERATED_PARENT", projected
        return "UNSUPPORTED_PRINTS_PARENT_REVIEW", projected
    return "UNRECOGNIZED_PARENT_REVIEW", projected


def _review_classification(requirements: list[str]) -> str:
    """Render stable detail while keeping each blocking dimension explicit."""

    if requirements == ["RECORD_REVIEW"]:
        return "RECORD_REVIEW_ONLY"
    if len(requirements) == 1:
        return f"{requirements[0]}_REQUIRED"
    labels = [
        requirement.removesuffix("_REVIEW") if requirement == "ROUTING_REVIEW" else requirement
        for requirement in requirements
    ]
    return "_AND_".join(labels) + "_REQUIRED"


def plan_record(
    *,
    path: Path,
    current_record_yaml_sha256: str,
    record: Mapping[str, Any],
    signature: Mapping[str, Any],
    entry: Mapping[str, Any] | None,
    interpro_type: str | None,
    release: PrintsRelease,
    fingerprint: PrintsFingerprint,
    normalized_hierarchy_row: Mapping[str, Any],
    legacy_generated_parent: str | None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    normalized_hierarchy = _normalized_hierarchy_binding(
        normalized_hierarchy_row,
        fingerprint=fingerprint,
    )
    legacy = legacy_record(signature, entry, fingerprint)
    hierarchy_status, hierarchy_projection = _hierarchy_projection(record, legacy_generated_parent)
    replacements, removals = source_native_replacements(
        signature,
        entry,
        release,
        fingerprint,
        remove_invalid_legacy_parent=(hierarchy_status == "CONFIRMED_LEGACY_GENERATED_PARENT"),
    )
    expected_native = apply_replacements(legacy, replacements, removals)
    proposed = apply_replacements(record, replacements, removals)
    legacy_record_projection = _legacy_comparison_projection(hierarchy_projection)
    legacy_expected_projection = _legacy_comparison_projection(legacy)
    if _semantically_equal(legacy_record_projection, legacy_expected_projection):
        record_state = "EXACT_LEGACY"
    elif _semantically_equal(hierarchy_projection, expected_native):
        record_state = "EXACT_SOURCE_NATIVE"
    else:
        record_state = "REVIEW_ONLY"

    member_type = str(signature["type"])
    member_type_is_domain = member_type == "domain"
    normalized_hierarchy_domain_flag = normalized_hierarchy["domain_flag"]
    member_hierarchy_domain_alignment = (
        "AGREES" if member_type_is_domain == normalized_hierarchy_domain_flag else "DISAGREES"
    )
    if signature.get("integrated") is None:
        route_status = "UNINTEGRATED"
    elif interpro_type is None:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: integrating InterPro entry has no parsed type"
        )
    elif interpro_type != member_type:
        route_status = "ROUTING_REVIEW"
    else:
        route_status = "AGREES"

    member_route = _route(member_type)
    lexical_path = Path(os.path.abspath(path))
    # os.path.realpath, not Path.resolve: non-strict resolve() disagrees across
    # supported interpreters on a symlink loop -- 3.13 returns the path unchanged
    # while 3.12 raises RuntimeError("Symlink loop from ...") -- so the same
    # record produced a review row locally and aborted the whole plan in CI
    # (#611). realpath resolves as far as it can and never raises for a loop, on
    # every version this project supports (requires-python >= 3.10), which leaves
    # an unresolvable route to be classified below rather than to end the run.
    try:
        resolved_root = Path(os.path.realpath(repo_root))
        resolved_path = Path(os.path.realpath(lexical_path))
    except OSError as error:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: cannot resolve repository/record path: {path}: {error}"
        ) from error
    try:
        relative_path_object = lexical_path.relative_to(resolved_root)
    except ValueError as error:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: record path escapes repository root: {path}"
        ) from error
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise PrintsMigrationError(
            f"{fingerprint.accession}: record path resolves outside repository root: {path}"
        ) from error
    relative_path = relative_path_object.as_posix()
    expected_directory = resolved_root / "data" / "traits" / member_route["directory"] / "prints"
    cursor = resolved_root
    has_symlink_component = False
    for component in relative_path_object.parts:
        cursor /= component
        if cursor.is_symlink():
            has_symlink_component = True
            break
    path_status = (
        "EXPECTED_MEMBER_ROUTE"
        if lexical_path.parent == expected_directory
        and resolved_path.parent == expected_directory
        and not has_symlink_component
        else "WRONG_MEMBER_ROUTE"
    )

    review_requirements: list[str] = []
    if record_state == "REVIEW_ONLY":
        review_requirements.append("RECORD_REVIEW")
    if route_status == "ROUTING_REVIEW":
        review_requirements.append("ROUTING_REVIEW")
    if hierarchy_status == "CONFIRMED_LEGACY_GENERATED_PARENT":
        review_requirements.append("HIERARCHY_REPAIR")
    elif hierarchy_status in {
        "UNSUPPORTED_PRINTS_PARENT_REVIEW",
        "UNRECOGNIZED_PARENT_REVIEW",
    }:
        review_requirements.append("HIERARCHY_REVIEW")
    if path_status == "WRONG_MEMBER_ROUTE":
        review_requirements.append("PATH_REVIEW")

    if review_requirements:
        classification = _review_classification(review_requirements)
    elif record_state == "EXACT_SOURCE_NATIVE":
        classification = "ALREADY_SOURCE_NATIVE"
    else:
        classification = "CONTENT_MIGRATION_READY"

    changes = _differing_fields(record, proposed)
    legacy_mismatch_fields = (
        []
        if record_state != "REVIEW_ONLY"
        else _differing_fields(legacy_record_projection, legacy_expected_projection)
    )
    review_value_projections = _record_review_value_projections(
        legacy_mismatch_fields,
        current=record,
        legacy_expected=legacy,
        proposed=proposed,
    )
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": ROW_KIND,
        "identifier": f"PRINTS:{fingerprint.accession}",
        "record_path": relative_path,
        "current_record_yaml_sha256": current_record_yaml_sha256,
        "current_record_hash_domain": "EXACT_YAML_BYTES",
        "record_state": record_state,
        "classification": classification,
        "review_requirements": review_requirements,
        "member_type": member_type,
        "member_type_is_domain": member_type_is_domain,
        "member_route": member_route,
        "normalized_hierarchy_row": normalized_hierarchy,
        "normalized_hierarchy_row_sha256": value_sha256(normalized_hierarchy),
        "normalized_hierarchy_domain_flag": normalized_hierarchy_domain_flag,
        "member_hierarchy_domain_alignment": member_hierarchy_domain_alignment,
        "integrating_interpro": signature.get("integrated"),
        "integrating_interpro_type": interpro_type,
        "integrating_interpro_route": (
            _route(interpro_type) if interpro_type in seeder.TYPE_MAP else None
        ),
        "route_status": route_status,
        "hierarchy_status": hierarchy_status,
        "hierarchy_source_semantics": "PRINTS_POSTPROCESSING_RELATIONS_NOT_SUBCLASS_EDGES",
        "confirmed_legacy_generated_parent": (
            f"PRINTS:{legacy_generated_parent}"
            if hierarchy_status == "CONFIRMED_LEGACY_GENERATED_PARENT"
            else None
        ),
        "path_status": path_status,
        "expected_record_directory": expected_directory.relative_to(resolved_root).as_posix(),
        "current_route": {
            "trait_axis": record.get("trait_axis"),
            "trait_category": record.get("trait_category"),
        },
        "source_record_sha256": fingerprint.source_record_sha256,
        "motif_count": fingerprint.declared_motif_count,
        "changed_fields": changes,
        "replacement_fields": replacements,
        "remove_fields": list(removals),
        "content_proposal_semantic_sha256": value_sha256(proposed),
        "content_proposal_hash_domain": "CANONICAL_JSON_SEMANTIC_OBJECT",
        "proposed_record_sha256": None,
        "proposed_record_hash_status": "NOT_MATERIALIZED_PLAN_ONLY",
        "legacy_mismatch_fields": legacy_mismatch_fields,
        "record_review_value_projections": review_value_projections,
        "record_review_value_projections_sha256": value_sha256(review_value_projections),
        "unmanaged_fields_preserved": sorted(set(record) - _MANAGED_FIELDS),
    }
    row["row_sha256"] = value_sha256(row)
    return row


def build_plan(
    *,
    records: Mapping[str, tuple[Path, Mapping[str, Any], str]],
    signatures: Iterable[Mapping[str, Any]],
    entries: Mapping[str, Mapping[str, Any]],
    interpro_types: Mapping[str, str],
    release: PrintsRelease,
    normalized_hierarchy_rows: Iterable[Mapping[str, Any]],
    legacy_generated_parents: Mapping[str, str],
    manifest_id: str,
    repo_root: Path = REPO_ROOT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    signatures_by_id: dict[str, Mapping[str, Any]] = {}
    for signature in signatures:
        accession = signature.get("accession")
        identifier = f"PRINTS:{accession}"
        if not isinstance(accession, str) or _IDENTIFIER.fullmatch(identifier) is None:
            raise PrintsMigrationError(f"invalid source signature accession {accession!r}")
        if identifier in signatures_by_id:
            raise PrintsMigrationError(f"duplicate source signature {identifier}")
        signatures_by_id[identifier] = signature
    hierarchy_by_id: dict[str, Mapping[str, Any]] = {}
    for hierarchy_row in normalized_hierarchy_rows:
        accession = hierarchy_row.get("accession")
        identifier = f"PRINTS:{accession}"
        if not isinstance(accession, str) or _IDENTIFIER.fullmatch(identifier) is None:
            raise PrintsMigrationError(f"invalid normalized hierarchy accession {accession!r}")
        if identifier in hierarchy_by_id:
            raise PrintsMigrationError(f"duplicate normalized hierarchy row {identifier}")
        hierarchy_by_id[identifier] = hierarchy_row
    source_ids = {f"PRINTS:{accession}" for accession in release.fingerprints}
    if source_ids != set(signatures_by_id):
        raise PrintsMigrationError("PRINTS API and KDAT identifier sets differ")
    record_ids = set(records)
    if record_ids != source_ids:
        missing = sorted(source_ids - record_ids)
        extra = sorted(record_ids - source_ids)
        raise PrintsMigrationError(
            "PRINTS source and trait identifier sets differ: "
            f"missing={missing[:5]!r}, extra={extra[:5]!r}"
        )
    if set(hierarchy_by_id) != source_ids:
        missing = sorted(source_ids - set(hierarchy_by_id))
        extra = sorted(set(hierarchy_by_id) - source_ids)
        raise PrintsMigrationError(
            "PRINTS source and normalized hierarchy identifier sets differ: "
            f"missing={missing[:5]!r}, extra={extra[:5]!r}"
        )

    rows: list[dict[str, Any]] = []
    for identifier in sorted(source_ids):
        path, record, record_sha = records[identifier]
        signature = signatures_by_id[identifier]
        interpro = signature.get("integrated")
        rows.append(
            plan_record(
                path=path,
                current_record_yaml_sha256=record_sha,
                record=record,
                signature=signature,
                entry=entries.get(str(interpro)) if interpro else None,
                interpro_type=interpro_types.get(str(interpro)) if interpro else None,
                release=release,
                fingerprint=release.fingerprints[identifier.split(":", 1)[1]],
                normalized_hierarchy_row=hierarchy_by_id[identifier],
                legacy_generated_parent=legacy_generated_parents.get(identifier.split(":", 1)[1]),
                repo_root=repo_root,
            )
        )
    rows_bytes = "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")
    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": SUMMARY_KIND,
        "plan_kind": PLAN_KIND,
        "snapshot_manifest_id": manifest_id,
        "source_release": release.release,
        "source_artifact_sha256": release.source_artifact_sha256,
        "legacy_parent_replay_source_sha256": LEGACY_HIERARCHY_SOURCE_SHA256,
        "record_count": len(rows),
        "motif_count": sum(row["motif_count"] for row in rows),
        "classification_counts": dict(
            sorted(Counter(row["classification"] for row in rows).items())
        ),
        "record_state_counts": dict(sorted(Counter(row["record_state"] for row in rows).items())),
        "route_status_counts": dict(sorted(Counter(row["route_status"] for row in rows).items())),
        "hierarchy_status_counts": dict(
            sorted(Counter(row["hierarchy_status"] for row in rows).items())
        ),
        "normalized_hierarchy_row_count": len(hierarchy_by_id),
        "normalized_hierarchy_projection_sha256": value_sha256(
            [hierarchy_by_id[identifier] for identifier in sorted(hierarchy_by_id)]
        ),
        "normalized_hierarchy_domain_count": sum(
            row["normalized_hierarchy_domain_flag"] for row in rows
        ),
        "member_hierarchy_domain_alignment_counts": dict(
            sorted(Counter(row["member_hierarchy_domain_alignment"] for row in rows).items())
        ),
        "routing_review_member_hierarchy_domain_alignment_counts": dict(
            sorted(
                Counter(
                    row["member_hierarchy_domain_alignment"]
                    for row in rows
                    if row["route_status"] == "ROUTING_REVIEW"
                ).items()
            )
        ),
        "path_status_counts": dict(sorted(Counter(row["path_status"] for row in rows).items())),
        "changed_record_count": sum(bool(row["changed_fields"]) for row in rows),
        "review_required_count": sum(bool(row["review_requirements"]) for row in rows),
        "record_review_count": sum("RECORD_REVIEW" in row["review_requirements"] for row in rows),
        "review_only_mismatch_field_counts": dict(
            sorted(
                Counter(
                    field_name
                    for row in rows
                    if row["record_state"] == "REVIEW_ONLY"
                    for field_name in row["legacy_mismatch_fields"]
                ).items()
            )
        ),
        "review_only_identifiers": [
            row["identifier"] for row in rows if row["record_state"] == "REVIEW_ONLY"
        ],
        "rows_sha256": hashlib.sha256(rows_bytes).hexdigest(),
    }
    summary["plan_id"] = PLAN_ID_PREFIX + value_sha256(summary)
    return rows, summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", type=Path, default=DEFAULT_API)
    parser.add_argument("--kdat", type=Path, default=DEFAULT_KDAT)
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY)
    parser.add_argument("--legacy-hierarchy-source", type=Path, default=DEFAULT_HIERARCHY_SOURCE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--interpro", type=Path, default=DEFAULT_INTERPRO)
    parser.add_argument("--traits", type=Path, default=DEFAULT_TRAITS)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="unsupported safety canary; always refuses before reading sources",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.apply:
        print(
            "refusing --apply: PRINTS migration is plan-only until routing review, "
            "transactional full-corpus preflight, and explicit authorization",
            file=sys.stderr,
        )
        return 2
    try:
        # Capture each live source through one read/open before verification.
        # Every subsequent parser consumes only these private immutable copies,
        # so a path/symlink replacement cannot mix allowlisted bytes with later
        # parsed bytes.
        with tempfile.TemporaryDirectory(prefix="prints-migration-capture-") as temp_dir:
            capture_dir = Path(temp_dir)
            captures: dict[str, Path] = {}
            for name, (source_path, label) in {
                "manifest": (args.manifest, "PRINTS snapshot manifest"),
                "api": (args.api, "PRINTS API source"),
                "kdat": (args.kdat, "PRINTS KDAT source"),
                "hierarchy": (args.hierarchy, "normalized PRINTS hierarchy source"),
                "interpro": (args.interpro, "InterPro XML source"),
                "legacy_hierarchy_source": (
                    args.legacy_hierarchy_source,
                    "legacy PRINTS hierarchy source",
                ),
            }.items():
                captured_path = capture_dir / name
                raw = _capture_regular_source(
                    source_path,
                    label=label,
                    max_bytes=_SOURCE_CAPTURE_LIMITS[name],
                )
                captured_path.write_bytes(raw)
                captures[name] = captured_path

            snapshot = load_verified_prints_snapshot(
                captures["manifest"],
                expected_manifest_id=EXPECTED_PRINTS_SNAPSHOT_ID,
                api_path=captures["api"],
                kdat_path=captures["kdat"],
                hierarchy_path=captures["hierarchy"],
                interpro_xml_path=captures["interpro"],
            )
            release = snapshot.kdat_release
            signatures = snapshot.load_api_rows()
            normalized_hierarchy_rows = snapshot.load_hierarchy_rows()
            interpro_xml_bytes = snapshot.interpro_xml_bytes
            entries = seeder.interpro_entries(captured_gzip=interpro_xml_bytes)
            interpro_types = load_interpro_entry_types(captured_gzip=interpro_xml_bytes)
            legacy_generated_parents = load_legacy_generated_parents(
                captures["legacy_hierarchy_source"]
            )
            records = index_prints_records(args.traits)
            rows, summary = build_plan(
                records=records,
                signatures=signatures,
                entries=entries,
                interpro_types=interpro_types,
                release=release,
                normalized_hierarchy_rows=normalized_hierarchy_rows,
                legacy_generated_parents=legacy_generated_parents,
                manifest_id=snapshot.manifest_id,
            )
    except (PrintsMigrationError, PrintsSnapshotError, ValueError, OSError) as error:
        print(f"refusing to plan PRINTS migration: {error}", file=sys.stderr)
        return 2
    if not args.summary_only:
        for row in rows:
            print(canonical_json(row))
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
