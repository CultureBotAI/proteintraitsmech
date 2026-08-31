#!/usr/bin/env python3
"""Stage CATH annotation discoveries and native-evidence blockers as JSONL.

This command deliberately emits two semantically disjoint streams:

* exact CATH-Gene3D observations captured in the pinned InterPro frame are
  annotation-derived *discovery* rows only, bound to one exact protected
  ProteinReference registry; and
* every no-example CATH trait receives a native representative blocker row
  because the repository does not contain pinned CATH domain boundaries plus
  residue-level SIFTS evidence.

Missing exact ProteinReferences become one deterministic request per full
UniProt identity. The pinned source/frame/registry digests are local content
bindings, not provider acquisition or frame-generation receipts. Every output
row remains receipt-closed and explicitly records zero evidence, network, and
write actions.

Neither stream claims that a protein is qualified, and neither stream is an
apply input.  The command has no writer or output-file mode: canonical JSONL
is written to stdout, followed by one content-addressed summary row.

The repository must remain quiescent while staging. Descriptor-relative
no-follow reads and repeated membership/content checks prevent path escapes and
detect sampled drift, but they do not create an atomic filesystem snapshot
against an uncooperative concurrent writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

import ripgrep_prefilter

SCHEMA_VERSION = 2
ANNOTATION_KIND = "CATH_GENE3D_ANNOTATION_DISCOVERY"
NATIVE_BLOCKER_KIND = "CATH_NATIVE_REPRESENTATIVE_BLOCKER"
REQUEST_KIND = "CATH_PROTEIN_REFERENCE_REQUEST"
SUMMARY_KIND = "CATH_GROUNDING_DISCOVERY_STAGE_SUMMARY"

SINGLE_LOCATION_STATUS = "EXACT_SINGLE_LOCATION_ANNOTATION_DISCOVERY"
UNGROUPED_MULTI_STATUS = "EXACT_UNGROUPED_MULTI_LOCATION_ANNOTATION_DISCOVERY"
NATIVE_BLOCKED_STATUS = "BLOCKED_MISSING_NATIVE_CATH_RESIDUE_EVIDENCE"
READY_LOCAL_REFERENCE = "READY_LOCAL_REFERENCE"
MISSING_LOCAL_PROTEIN_REFERENCE = "MISSING_LOCAL_PROTEIN_REFERENCE"

DISCOVERY_ONLY_REASON = "INTERPRO_GENE3D_FRAME_IS_DISCOVERY_ONLY_PENDING_RAW_PROVIDER_REPLAY"
UNGROUPED_REASON = "INTERPRO_LOCATIONS_ARE_FLATTENED_WITHOUT_FRAGMENT_GROUPING"
MISSING_BOUNDARIES_REASON = "MISSING_RELEASE_PINNED_CATH_DOMAIN_BOUNDARIES"
MISSING_RESIDUE_SIFTS_REASON = "MISSING_RELEASE_PINNED_RESIDUE_LEVEL_SIFTS"
MISSING_REPRESENTATIVE_REASON = "CATH_NAMES_REPRESENTATIVE_IS_PLACEHOLDER"

MISSING_CATH_PROVIDER_RECEIPT = "MISSING_CATH_PROVIDER_ACQUISITION_RECEIPT"
MISSING_INTERPRO_PROVIDER_RECEIPT = "MISSING_INTERPRO_PROVIDER_ACQUISITION_RECEIPT"
MISSING_INTERPRO_FRAME_RECEIPT = "MISSING_INTERPRO_FRAME_GENERATION_RECEIPT"
MISSING_RESIDUE_FRAME_RECEIPT = "MISSING_UNIPROT_RESIDUE_FRAME_GENERATION_RECEIPT"
MISSING_REGISTRY_RECEIPT = "MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT"
MISSING_PROTEIN_REFERENCE = "MISSING_EXPECTED_RELEASE_LOCAL_PROTEIN_REFERENCE"

ANNOTATION_MISSING_RECEIPTS = (
    MISSING_CATH_PROVIDER_RECEIPT,
    MISSING_INTERPRO_PROVIDER_RECEIPT,
    MISSING_INTERPRO_FRAME_RECEIPT,
    MISSING_RESIDUE_FRAME_RECEIPT,
    MISSING_REGISTRY_RECEIPT,
)
NATIVE_MISSING_RECEIPTS = (MISSING_CATH_PROVIDER_RECEIPT,)
ANNOTATION_PROMOTION_BLOCKERS = (*ANNOTATION_MISSING_RECEIPTS, DISCOVERY_ONLY_REASON)
NATIVE_PROMOTION_BLOCKERS = (
    MISSING_CATH_PROVIDER_RECEIPT,
    MISSING_BOUNDARIES_REASON,
    MISSING_RESIDUE_SIFTS_REASON,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATH_NAMES = REPO_ROOT / "data/raw/cath/cath-names.txt"
DEFAULT_INTERPRO_FRAME = REPO_ROOT / "data/raw/align_cache/interpro_frame.json"
DEFAULT_RESIDUE_FRAME = REPO_ROOT / "data/raw/align_cache/residue_frame.json"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data/traits"
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data/grounding/protein_registry.jsonl"

EXPECTED_CATH_NAMES_SHA256 = "9a7b68548a4b755ceda673cfcaba3f19733e1d571f6fafca34e54f62675cdd3a"
EXPECTED_INTERPRO_FRAME_SHA256 = "8d350d73ed5e0525f15885bcff847913d7de208bf58e0155955b47426a382cc0"
EXPECTED_RESIDUE_FRAME_SHA256 = "35f053876b234b92267c0f18e94bc8f085316f39343aa98668b714c610ba7848"
EXPECTED_PROTEIN_REGISTRY_SHA256 = (
    "d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c"
)
EXPECTED_INTERPRO_RELEASE = "109.0"
EXPECTED_UNIPROT_RELEASE = "2026_02"

SOURCE_PINS = {
    "cath_names": EXPECTED_CATH_NAMES_SHA256,
    "interpro_frame": EXPECTED_INTERPRO_FRAME_SHA256,
    "residue_frame": EXPECTED_RESIDUE_FRAME_SHA256,
}

PRODUCTION_COUNTS = {
    "cath_name_count": 8151,
    "all_cath_trait_count": 8151,
    "no_example_trait_count": 4192,
    "native_exact_representative_count": 4191,
    "native_placeholder_count": 1,
    "annotation_discovery_count": 953,
    "annotation_single_location_count": 813,
    "annotation_ungrouped_multi_location_count": 140,
    "annotation_unique_trait_count": 379,
    "annotation_unique_protein_count": 415,
    "protein_registry_row_count": 126,
    "annotation_exact_local_reference_count": 0,
    "annotation_missing_local_reference_count": 953,
    "annotation_exact_local_reference_unique_protein_count": 0,
    "annotation_missing_local_reference_unique_protein_count": 415,
    "protein_reference_request_count": 415,
    "protein_reference_request_unique_protein_count": 415,
    "protein_reference_request_multi_observation_count": 175,
    "protein_reference_request_max_observation_count": 15,
}

CATH_RELEASE = "v4.4.0"
CATH_RELEASE_DATE = "16.12.2024"
CATH_FORMAT = "Cath Names File (CNF) Format 2.0"

ROUTE_BY_DEPTH = {
    1: Path("structure/class/cath"),
    2: Path("structure/architecture/cath"),
    3: Path("structure/topology/cath"),
    4: Path("structure/homologous_superfamily/cath"),
}
CATEGORY_BY_DEPTH = {
    1: "STRUCT_CLASS",
    2: "STRUCT_ARCHITECTURE",
    3: "STRUCT_TOPOLOGY",
    4: "STRUCT_HOMOLOGOUS_SUPERFAMILY",
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_CATH_CODE_RE = re.compile(r"^[1-9][0-9]*(?:\.[1-9][0-9]*){0,3}$")
_CATH_DATA_LINE_RE = re.compile(
    r"^(?P<code>[1-9][0-9]*(?:\.[1-9][0-9]*){0,3})"
    r"[ \t]+(?P<representative>[^ \t]+)[ \t]+:(?P<name>.*)$"
)
_REPRESENTATIVE_RE = re.compile(r"^[0-9a-z]{4}[A-Za-z0-9][0-9]{2}$")
_ACCESSION_RE = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})$"
)
_SEQUENCE_RE = re.compile(r"^[A-Z*]+$")
_TAXON_RE = re.compile(r"^NCBITaxon:[1-9][0-9]*$")

REGISTRY_SCHEMA = frozenset(
    {
        "protein_id",
        "protein_label",
        "reviewed",
        "sequence",
        "sequence_length",
        "sequence_sha256",
        "sequence_version",
        "taxon_id",
        "taxon_label",
        "uniprot_release",
    }
)


class CathStageError(ValueError):
    """A source, frame, trait, or filesystem invariant failed closed."""


@dataclass(frozen=True)
class BoundDirectory:
    path: Path
    descriptor: int
    metadata: os.stat_result


@dataclass(frozen=True)
class CapturedArtifact:
    path: Path
    relative_path: str
    sha256: str
    raw: bytes


@dataclass(frozen=True)
class ArtifactDigest:
    path: Path
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class CathName:
    code: str
    representative: str
    name: str
    source_line_number: int
    source_line_sha256: str

    @property
    def trait_id(self) -> str:
        return f"CATH:{self.code}"

    @property
    def depth(self) -> int:
        return len(self.code.split("."))


@dataclass(frozen=True)
class TraitBinding:
    trait_id: str
    category: str
    path: Path
    relative_path: str
    sha256: str
    has_canonical_examples: bool


@dataclass(frozen=True)
class ProteinReference:
    row: Mapping[str, Any]
    source_line_number: int
    source_row_sha256: str


@dataclass(frozen=True)
class StageResult:
    annotation_discoveries: tuple[dict[str, Any], ...]
    native_blockers: tuple[dict[str, Any], ...]
    protein_requests: tuple[dict[str, Any], ...]
    summary: dict[str, Any]


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


def _rows_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join((canonical_json(row) + "\n").encode("utf-8") for row in rows)


def _descriptor_safety_flags() -> tuple[int, int]:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory_only = getattr(os, "O_DIRECTORY", None)
    supports_dir_fd = getattr(os, "supports_dir_fd", set())
    if (
        not isinstance(no_follow, int)
        or no_follow == 0
        or not isinstance(directory_only, int)
        or directory_only == 0
        or os.open not in supports_dir_fd
    ):
        raise CathStageError(
            "platform lacks required O_NOFOLLOW/O_DIRECTORY/dir_fd filesystem safety"
        )
    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    return (
        os.O_RDONLY | directory_only | no_follow | close_on_exec,
        os.O_RDONLY | no_follow | close_on_exec,
    )


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _relative_under(path: Path, root: Path, *, description: str) -> Path:
    lexical_path = _lexical_absolute(path)
    lexical_root = _lexical_absolute(root)
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise CathStageError(
            f"{description} escapes bound root {lexical_root}: {lexical_path}"
        ) from error
    if not relative.parts:
        raise CathStageError(f"{description} names the bound directory itself: {path}")
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise CathStageError(f"invalid relative {description} path: {relative}")
    return relative


def _bind_absolute_directory(path: Path, *, description: str) -> BoundDirectory:
    directory_flags, _ = _descriptor_safety_flags()
    lexical_path = _lexical_absolute(path)
    if lexical_path.anchor != os.sep:
        raise CathStageError(f"{description} must have an absolute POSIX path: {path}")
    descriptor: int | None = None
    try:
        descriptor = os.open(os.sep, directory_flags)
        for part in lexical_path.parts[1:]:
            next_descriptor = os.open(part, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        metadata = os.fstat(descriptor)
    except OSError as error:
        if descriptor is not None:
            os.close(descriptor)
        raise CathStageError(
            f"cannot bind {description} without following symlinks {lexical_path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise CathStageError(f"{description} must be a directory: {lexical_path}")
    return BoundDirectory(lexical_path, descriptor, metadata)


def _bind_subdirectory(parent: BoundDirectory, path: Path, *, description: str) -> BoundDirectory:
    relative = _relative_under(path, parent.path, description=description)
    directory_flags, _ = _descriptor_safety_flags()
    descriptor = os.dup(parent.descriptor)
    try:
        for part in relative.parts:
            next_descriptor = os.open(part, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        metadata = os.fstat(descriptor)
    except OSError as error:
        os.close(descriptor)
        raise CathStageError(
            f"cannot bind {description} without following symlinks {path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise CathStageError(f"{description} must be a directory: {path}")
    return BoundDirectory(_lexical_absolute(path), descriptor, metadata)


def _directory_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _assert_directory_binding(binding: BoundDirectory, *, description: str) -> None:
    current = _bind_absolute_directory(binding.path, description=description)
    try:
        if _directory_identity(current.metadata) != _directory_identity(
            binding.metadata
        ) or _directory_identity(os.fstat(binding.descriptor)) != _directory_identity(
            binding.metadata
        ):
            raise CathStageError(f"{description} binding changed while staging: {binding.path}")
    finally:
        os.close(current.descriptor)


def _read_relative_bytes(
    root: BoundDirectory,
    relative_path: Path,
    *,
    display_path: Path,
    description: str,
) -> bytes:
    if (
        relative_path.is_absolute()
        or not relative_path.parts
        or any(part in {"", ".", ".."} for part in relative_path.parts)
    ):
        raise CathStageError(f"invalid relative {description} path: {relative_path}")
    directory_flags, file_flags = _descriptor_safety_flags()
    directory_descriptor = os.dup(root.descriptor)
    file_descriptor: int | None = None
    try:
        for part in relative_path.parts[:-1]:
            next_descriptor = os.open(part, directory_flags, dir_fd=directory_descriptor)
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor
        file_descriptor = os.open(relative_path.parts[-1], file_flags, dir_fd=directory_descriptor)
        before = os.fstat(file_descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise CathStageError(f"{description} must be a regular file: {display_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
            raise CathStageError(f"{description} changed while reading: {display_path}")
        return b"".join(chunks)
    except CathStageError:
        raise
    except OSError as error:
        raise CathStageError(
            f"cannot open {description} without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return _relative_under(path, repo_root, description="path").as_posix()
    except CathStageError as error:
        raise CathStageError(
            f"path escapes repository root {_lexical_absolute(repo_root)}: "
            f"{_lexical_absolute(path)}"
        ) from error


def _capture(
    path: Path,
    *,
    description: str,
    repo_root: Path,
    expected_sha256: str,
    bound_root: BoundDirectory,
) -> CapturedArtifact:
    if _SHA256_RE.fullmatch(expected_sha256) is None:
        raise CathStageError(f"invalid pinned sha256 for {description}: {expected_sha256!r}")
    relative = _relative_under(path, bound_root.path, description=description)
    raw = _read_relative_bytes(
        bound_root,
        relative,
        display_path=_lexical_absolute(path),
        description=description,
    )
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise CathStageError(
            f"{description} sha256 mismatch for {path}: expected {expected_sha256}, "
            f"observed {digest}"
        )
    return CapturedArtifact(
        path=_lexical_absolute(path),
        relative_path=_repo_relative(path, repo_root),
        sha256=digest,
        raw=raw,
    )


def _assert_unchanged(
    artifact: CapturedArtifact | ArtifactDigest,
    *,
    description: str,
    bound_root: BoundDirectory,
) -> None:
    relative = _relative_under(artifact.path, bound_root.path, description=description)
    raw = _read_relative_bytes(
        bound_root,
        relative,
        display_path=artifact.path,
        description=description,
    )
    observed = hashlib.sha256(raw).hexdigest()
    if observed != artifact.sha256:
        raise CathStageError(
            f"{description} drifted while staging: {artifact.path}; "
            f"expected {artifact.sha256}, observed {observed}"
        )


def parse_cath_names(artifact: CapturedArtifact) -> dict[str, CathName]:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CathStageError(f"CATH names file is not strict UTF-8: {error}") from error
    if "\r" in text or not text.endswith("\n"):
        raise CathStageError("CATH names file must use LF terminators and end with LF")
    required_headers = {
        f"# FILE NAME:    CathNames.{CATH_RELEASE}",
        f"# FILE DATE:    {CATH_RELEASE_DATE}",
        f"# CATH VERSION: {CATH_RELEASE}",
        f"# VERSION DATE: {CATH_RELEASE_DATE}",
        f"# FILE FORMAT:  {CATH_FORMAT}",
    }
    physical_lines = artifact.raw.splitlines(keepends=True)
    header_lines: set[str] = set()
    rows: dict[str, CathName] = {}
    saw_data = False
    for line_number, raw_line in enumerate(physical_lines, start=1):
        try:
            line = raw_line.decode("utf-8").removesuffix("\n")
        except UnicodeDecodeError as error:
            raise CathStageError(
                f"CATH names line {line_number} is not strict UTF-8: {error}"
            ) from error
        if line.startswith("#"):
            if saw_data:
                raise CathStageError(
                    f"CATH header/comment appears after data at line {line_number}"
                )
            header_lines.add(line)
            continue
        if not line:
            if saw_data:
                raise CathStageError(f"blank line appears after CATH data at line {line_number}")
            continue
        saw_data = True
        match = _CATH_DATA_LINE_RE.fullmatch(line)
        if match is None:
            raise CathStageError(f"malformed CATH names row at line {line_number}")
        code = match.group("code")
        representative = match.group("representative")
        name = match.group("name").rstrip(" \t")
        if code in rows:
            raise CathStageError(f"duplicate CATH names key {code} at line {line_number}")
        if _REPRESENTATIVE_RE.fullmatch(representative) is None and representative != "???????":
            raise CathStageError(
                f"invalid CATH representative {representative!r} at line {line_number}"
            )
        rows[code] = CathName(
            code=code,
            representative=representative,
            name=name,
            source_line_number=line_number,
            source_line_sha256=hashlib.sha256(raw_line).hexdigest(),
        )
    missing_headers = sorted(required_headers - header_lines)
    if missing_headers:
        raise CathStageError(f"CATH names header mismatch; missing={missing_headers}")
    if not rows:
        raise CathStageError("CATH names file contains no data rows")
    for code in rows:
        parts = code.split(".")
        if len(parts) > 1 and ".".join(parts[:-1]) not in rows:
            raise CathStageError(f"CATH names hierarchy parent is missing for {code}")
    return rows


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: yaml.SafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise CathStageError("trait YAML has an unhashable mapping key") from error
        if duplicate:
            raise CathStageError(f"trait YAML has duplicate key {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _require_json_shape(value: Any, *, source: str, active: set[int] | None = None) -> None:
    active = active if active is not None else set()
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in active:
            raise CathStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for key, item in value.items():
            if not isinstance(key, str):
                raise CathStageError(f"{source}: YAML mapping key is not a string")
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise CathStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for item in value:
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if value is None or type(value) in {str, int, bool}:
        return
    if type(value) is float and math.isfinite(value):
        return
    raise CathStageError(f"{source}: YAML value is outside the JSON data model")


def _load_yaml_mapping(raw: bytes, *, path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError, CathStageError) as error:
        raise CathStageError(f"cannot parse trait record {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise CathStageError(f"trait record is not a mapping: {path}")
    _require_json_shape(value, source=str(path))
    return value


def _reject_trait_tree_symlinks(traits_root: Path) -> None:
    def fail(error: OSError) -> None:
        raise CathStageError(f"cannot scan trait tree {traits_root}: {error}")

    for directory, names, files in os.walk(
        traits_root, topdown=True, onerror=fail, followlinks=False
    ):
        for name in [*names, *files]:
            path = Path(directory) / name
            try:
                metadata = os.stat(path, follow_symlinks=False)
            except OSError as error:
                raise CathStageError(f"cannot inspect trait-tree entry {path}: {error}") from error
            if stat.S_ISLNK(metadata.st_mode):
                raise CathStageError(f"symlink below trait directory is forbidden: {path}")


def _route_trait_paths(traits_root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for route in ROUTE_BY_DEPTH.values():
        directory = traits_root / route
        try:
            with os.scandir(directory) as scanner:
                entries = sorted(scanner, key=lambda entry: entry.name)
        except OSError as error:
            raise CathStageError(f"cannot enumerate required CATH trait route {directory}: {error}")
        for entry in entries:
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as error:
                raise CathStageError(
                    f"cannot inspect CATH route entry {entry.path}: {error}"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                raise CathStageError(f"symlink in CATH trait route is forbidden: {entry.path}")
            if not stat.S_ISREG(metadata.st_mode) or not entry.name.endswith(".yaml"):
                raise CathStageError(
                    f"CATH trait routes may contain only direct .yaml records: {entry.path}"
                )
            paths.append(Path(entry.path))
    return tuple(sorted(paths))


def _candidate_cath_trait_paths(traits_root: Path) -> tuple[Path, ...]:
    """Return every expected record plus every semantic-shadow candidate.

    Every case-insensitive ``CATH:`` candidate, every YAML escape-bearing
    file, and every NUL-encoded file is parsed before namespace filtering.
    This catches quoted, flow, block/plain-continuation, escaped, explicitly
    keyed, and aliased CATH identities without parsing the hundreds of
    thousands of unrelated trait records.
    """

    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits_root), "CATH trait")
        return tuple(sorted(found))
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
        "(?i)CATH:",
        "-e",
        r"\\",
        "-e",
        r"\x00",
        "--",
        str(traits_root),
    ]
    try:
        scan = subprocess.run(command, check=False, capture_output=True)
    except OSError as error:
        raise CathStageError(f"cannot run ripgrep CATH trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise CathStageError(f"ripgrep CATH trait prefilter failed: {detail}")
    try:
        candidates = {
            Path(raw_path.decode("utf-8")) for raw_path in scan.stdout.split(b"\0") if raw_path
        }
    except UnicodeDecodeError as error:
        raise CathStageError(f"ripgrep returned a non-UTF-8 trait path: {error}") from error
    candidates.update(_route_trait_paths(traits_root))
    return tuple(sorted(candidates))


def _expected_label(row: CathName) -> str:
    if row.name:
        return row.name
    return f"CATH homologous superfamily {row.code}"


def _cath_sort_key(code_or_trait: str) -> tuple[int, ...]:
    code = code_or_trait.removeprefix("CATH:")
    if _CATH_CODE_RE.fullmatch(code) is None:
        raise CathStageError(f"invalid CATH code used for sorting: {code_or_trait!r}")
    return tuple(int(part) for part in code.split("."))


def index_cath_traits(
    traits_root: Path,
    names: Mapping[str, CathName],
    *,
    repo_root: Path,
    repo_binding: BoundDirectory,
) -> tuple[
    dict[str, TraitBinding],
    tuple[TraitBinding, ...],
    tuple[ArtifactDigest, ...],
    tuple[str, ...],
]:
    traits_binding = _bind_subdirectory(repo_binding, traits_root, description="trait root")
    try:
        _reject_trait_tree_symlinks(traits_binding.path)
        for route in ROUTE_BY_DEPTH.values():
            route_binding = _bind_subdirectory(
                traits_binding,
                traits_binding.path / route,
                description=f"required CATH trait route {route}",
            )
            os.close(route_binding.descriptor)
        paths = _candidate_cath_trait_paths(traits_binding.path)
        bindings: dict[str, TraitBinding] = {}
        captured: list[ArtifactDigest] = []
        captured_relative: list[Path] = []
        for reported_path in paths:
            relative = _relative_under(
                reported_path,
                traits_binding.path,
                description="trait prefilter candidate",
            )
            path = traits_binding.path / relative
            raw = _read_relative_bytes(
                traits_binding,
                relative,
                display_path=path,
                description="trait record",
            )
            digest = hashlib.sha256(raw).hexdigest()
            repo_relative = _repo_relative(path, repo_root)
            captured.append(ArtifactDigest(path, repo_relative, digest))
            captured_relative.append(relative)
            record = _load_yaml_mapping(raw, path=path)
            identifier = record.get("identifier")
            if not isinstance(identifier, str):
                continue
            namespace, separator, _ = identifier.partition(":")
            if separator != ":" or namespace.casefold() != "cath":
                continue
            if namespace != "CATH":
                raise CathStageError(
                    f"{path}: noncanonical CATH trait namespace spelling {namespace!r}"
                )
            if path.suffix != ".yaml":
                raise CathStageError(
                    f"{path}: CATH trait files require the exact lowercase .yaml suffix"
                )
            code = identifier.removeprefix("CATH:")
            source = names.get(code)
            if source is None:
                raise CathStageError(
                    f"{path}: CATH trait identity is absent from cath-names: {identifier}"
                )
            expected_parent = traits_binding.path / ROUTE_BY_DEPTH[source.depth]
            if _lexical_absolute(path).parent != _lexical_absolute(expected_parent):
                raise CathStageError(
                    f"{path}: CATH trait {identifier} is outside its exact depth-{source.depth} route"
                )
            contract = {
                "identifier": identifier,
                "label": _expected_label(source),
                "definition_source": "CATH",
                "trait_axis": "STRUCTURE",
                "trait_category": CATEGORY_BY_DEPTH[source.depth],
                "term_kind": "CLASS",
                "mapping_status": "SEEDED",
                "license": "CC-BY 4.0",
            }
            for field, expected in contract.items():
                if record.get(field) != expected:
                    raise CathStageError(
                        f"{path}: trait contract mismatch for {field}: expected "
                        f"{expected!r}, observed {record.get(field)!r}"
                    )
            expected_parents = (
                [] if source.depth == 1 else [f"CATH:{'.'.join(code.split('.')[:-1])}"]
            )
            if record.get("parent_traits", []) != expected_parents:
                raise CathStageError(f"{path}: exact parent_traits mismatch for {identifier}")
            if source.representative == "???????":
                if (
                    record.get("xrefs", []) != []
                    or record.get("structural_geometry_representations", []) != []
                ):
                    raise CathStageError(
                        f"{path}: placeholder representative must not be projected as PDB evidence"
                    )
            else:
                expected_xrefs = [f"CATH:{source.representative}"]
                if record.get("xrefs") != expected_xrefs:
                    raise CathStageError(f"{path}: representative xref mismatch for {identifier}")
                expected_geometry = [
                    {
                        "structure_ref": f"PDB:{source.representative[:4]}",
                        "structure_source": "CATH",
                        "evidence_source": (
                            f"CATH representative domain {source.representative} "
                            f"(chain {source.representative[4]})"
                        ),
                    }
                ]
                if record.get("structural_geometry_representations") != expected_geometry:
                    raise CathStageError(
                        f"{path}: representative geometry mismatch for {identifier}"
                    )
            if "canonical_examples" in record:
                examples = record["canonical_examples"]
                if not isinstance(examples, list) or not examples:
                    raise CathStageError(
                        f"{path}: canonical_examples must be absent or a non-empty list"
                    )
                has_examples = True
            else:
                has_examples = False
            if identifier in bindings:
                raise CathStageError(
                    f"duplicate CATH trait identity {identifier}: "
                    f"{bindings[identifier].relative_path} and {repo_relative}"
                )
            bindings[identifier] = TraitBinding(
                trait_id=identifier,
                category=CATEGORY_BY_DEPTH[source.depth],
                path=path,
                relative_path=repo_relative,
                sha256=digest,
                has_canonical_examples=has_examples,
            )
        expected_ids = {f"CATH:{code}" for code in names}
        if set(bindings) != expected_ids:
            missing = sorted(expected_ids - set(bindings), key=_cath_sort_key)[:10]
            extra = sorted(set(bindings) - expected_ids, key=_cath_sort_key)[:10]
            raise CathStageError(
                f"CATH trait identity set mismatch; missing={missing}, extra={extra}"
            )
        scope = tuple(
            sorted(
                (binding for binding in bindings.values() if not binding.has_canonical_examples),
                key=lambda item: _cath_sort_key(item.trait_id),
            )
        )
        _reject_trait_tree_symlinks(traits_binding.path)
        _assert_directory_binding(traits_binding, description="trait root")
        final_paths = tuple(
            _relative_under(path, traits_binding.path, description="trait prefilter candidate")
            for path in _candidate_cath_trait_paths(traits_binding.path)
        )
        if final_paths != tuple(captured_relative):
            raise CathStageError("CATH trait candidate membership drifted while indexing")
        return bindings, scope, tuple(captured), tuple(item.relative_path for item in captured)
    finally:
        os.close(traits_binding.descriptor)


def _json_object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise CathStageError(f"JSON has duplicate key {key!r}")
        value[key] = item
    return value


def _reject_json_constant(token: str) -> None:
    raise CathStageError(f"frame JSON contains forbidden non-finite constant {token}")


def _load_json(artifact: CapturedArtifact, *, description: str) -> Mapping[str, Any]:
    try:
        value = json.loads(
            artifact.raw,
            object_pairs_hook=_json_object_no_duplicates,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, CathStageError) as error:
        raise CathStageError(f"cannot parse {description}: {error}") from error
    if not isinstance(value, Mapping):
        raise CathStageError(f"{description} root is not an object")
    return value


def _validate_registry_row(row: Mapping[str, Any], *, source: str) -> None:
    if set(row) != REGISTRY_SCHEMA:
        raise CathStageError(
            f"{source}: exact ProteinReference schema mismatch; expected "
            f"{sorted(REGISTRY_SCHEMA)!r}, observed {sorted(row)!r}"
        )
    protein_id = row["protein_id"]
    if not isinstance(protein_id, str) or not protein_id.startswith("UniProtKB:"):
        raise CathStageError(f"{source}: invalid protein_id")
    accession = protein_id.removeprefix("UniProtKB:")
    if _ACCESSION_RE.fullmatch(accession) is None:
        raise CathStageError(f"{source}: ProteinReference must use a canonical UniProt accession")
    if row["uniprot_release"] != EXPECTED_UNIPROT_RELEASE:
        raise CathStageError(
            f"{source}: ProteinReference release must be exactly {EXPECTED_UNIPROT_RELEASE}"
        )
    for field in ("protein_label", "taxon_label"):
        if not isinstance(row[field], str) or not row[field]:
            raise CathStageError(f"{source}: {field} must be a non-empty string")
    if not isinstance(row["reviewed"], bool):
        raise CathStageError(f"{source}: reviewed must be boolean")
    if not isinstance(row["taxon_id"], str) or _TAXON_RE.fullmatch(row["taxon_id"]) is None:
        raise CathStageError(f"{source}: taxon_id must be an NCBITaxon CURIE")
    sequence = row["sequence"]
    if not isinstance(sequence, str) or _SEQUENCE_RE.fullmatch(sequence) is None:
        raise CathStageError(f"{source}: sequence must be an uppercase amino-acid string")
    length = row["sequence_length"]
    if type(length) is not int or length < 1 or length != len(sequence):
        raise CathStageError(f"{source}: sequence_length does not match sequence")
    checksum = row["sequence_sha256"]
    if not isinstance(checksum, str) or _SHA256_RE.fullmatch(checksum) is None:
        raise CathStageError(f"{source}: invalid sequence_sha256")
    if checksum != hashlib.sha256(sequence.encode("ascii")).hexdigest():
        raise CathStageError(f"{source}: sequence_sha256 does not match sequence")
    version = row["sequence_version"]
    if type(version) is not int or version < 1:
        raise CathStageError(f"{source}: sequence_version must be a positive integer")


def load_protein_registry(artifact: CapturedArtifact) -> dict[str, ProteinReference]:
    if not artifact.raw.endswith(b"\n") or b"\r" in artifact.raw:
        raise CathStageError(
            f"{artifact.relative_path}: ProteinReference registry must use canonical LF JSONL"
        )
    references: dict[str, ProteinReference] = {}
    for line_number, raw_line in enumerate(artifact.raw.splitlines(), 1):
        if not raw_line:
            raise CathStageError(
                f"{artifact.relative_path}:{line_number}: blank ProteinReference row"
            )
        source = f"{artifact.relative_path}:{line_number}"
        try:
            row = json.loads(
                raw_line.decode("utf-8"),
                object_pairs_hook=_json_object_no_duplicates,
                parse_constant=_reject_json_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, CathStageError) as error:
            raise CathStageError(f"{source}: invalid ProteinReference JSON: {error}") from error
        if not isinstance(row, Mapping):
            raise CathStageError(f"{source}: ProteinReference row is not an object")
        _validate_registry_row(row, source=source)
        if raw_line.decode("utf-8") != canonical_json(row):
            raise CathStageError(f"{source}: ProteinReference row is not exact canonical JSON")
        protein_id = str(row["protein_id"])
        if protein_id in references:
            raise CathStageError(f"{source}: duplicate ProteinReference {protein_id}")
        references[protein_id] = ProteinReference(
            row=dict(row),
            source_line_number=line_number,
            source_row_sha256=hashlib.sha256(raw_line).hexdigest(),
        )
    if not references:
        raise CathStageError(f"{artifact.relative_path}: ProteinReference registry is empty")
    return references


def _load_frame(
    artifact: CapturedArtifact,
    *,
    description: str,
    expected_source: str,
    residue: bool,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    value = _load_json(artifact, description=description)
    if set(value) != {"_meta", "proteins"}:
        raise CathStageError(f"{description} must contain exactly _meta and proteins")
    meta = value["_meta"]
    proteins = value["proteins"]
    if not isinstance(meta, Mapping) or not isinstance(proteins, Mapping):
        raise CathStageError(f"{description} metadata/proteins contract is invalid")
    expected_meta_keys = {"schema", "built", "source", "release", "count"}
    if residue:
        expected_meta_keys.add("absent")
    if set(meta) != expected_meta_keys:
        raise CathStageError(f"{description} metadata keys mismatch: observed={sorted(meta)}")
    if meta.get("schema") != 1 or meta.get("source") != expected_source:
        raise CathStageError(f"{description} schema/source metadata mismatch")
    if not isinstance(meta.get("built"), str) or not isinstance(meta.get("release"), str):
        raise CathStageError(f"{description} built/release metadata must be strings")
    if type(meta.get("count")) is not int or meta["count"] != len(proteins):
        raise CathStageError(f"{description} metadata count does not match proteins")
    if any(not isinstance(key, str) for key in proteins):
        raise CathStageError(f"{description} protein keys must be strings")
    if residue:
        absent = meta["absent"]
        if (
            not isinstance(absent, list)
            or any(not isinstance(item, str) for item in absent)
            or absent != sorted(set(absent))
            or set(absent) & set(proteins)
        ):
            raise CathStageError(
                f"{description} absent list must be sorted, unique, and disjoint from proteins"
            )
    return meta, proteins


def _content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> dict[str, Any]:
    row[id_field] = prefix + value_sha256(row)
    row[row_hash_field] = value_sha256(row)
    return row


def _artifact_projection(artifact: CapturedArtifact, *, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": artifact.relative_path,
        "sha256": artifact.sha256,
        "size_bytes": len(artifact.raw),
    }


def _source_snapshot(
    artifacts: Mapping[str, CapturedArtifact],
    *,
    interpro_release: str,
    residue_release: str,
) -> dict[str, Any]:
    if set(artifacts) != set(SOURCE_PINS):
        raise CathStageError(
            "CATH source snapshot must contain cath_names, interpro_frame, and residue_frame"
        )
    snapshot: dict[str, Any] = {
        "kind": "CATH_LOCAL_SOURCE_AND_DERIVED_FRAME_SNAPSHOT",
        "schema_version": SCHEMA_VERSION,
        "cath_release_declared_by_source_bytes": CATH_RELEASE,
        "cath_release_date_declared_by_source_bytes": CATH_RELEASE_DATE,
        "interpro_release_declared_by_frame": interpro_release,
        "uniprot_release_declared_by_residue_frame": residue_release,
        "source_artifacts": [
            _artifact_projection(artifacts["cath_names"], role="CATH_NAMES_LOCAL_PINNED_BYTES"),
            _artifact_projection(
                artifacts["interpro_frame"], role="DERIVED_INTERPRO_ANNOTATION_FRAME"
            ),
            _artifact_projection(artifacts["residue_frame"], role="DERIVED_UNIPROT_RESIDUE_FRAME"),
        ],
        "provider_acquisition_receipts": {
            "CATH": None,
            "InterPro": None,
        },
        "frame_generation_receipts": {
            "InterPro": None,
            "UniProt": None,
        },
        "snapshot_status": "LOCAL_PINNED_BYTES_WITHOUT_PROVIDER_OR_GENERATOR_RECEIPTS",
        "network_action_performed": False,
    }
    snapshot["source_snapshot_id"] = "cath-local-source-snapshot:" + value_sha256(snapshot)
    return snapshot


def _reference_projection(reference: ProteinReference) -> dict[str, Any]:
    row = reference.row
    return {
        "protein_id": row["protein_id"],
        "protein_label": row["protein_label"],
        "taxon_id": row["taxon_id"],
        "taxon_label": row["taxon_label"],
        "reviewed": row["reviewed"],
        "sequence_length": row["sequence_length"],
        "sequence_sha256": row["sequence_sha256"],
        "sequence_version": row["sequence_version"],
        "uniprot_release": row["uniprot_release"],
        "protein_reference_source_line_number": reference.source_line_number,
        "protein_reference_source_row_sha256": reference.source_row_sha256,
    }


def _reference_binding(
    reference: ProteinReference | None,
    *,
    registry_artifact: CapturedArtifact,
    expected_uniprot_release: str,
) -> dict[str, Any]:
    binding: dict[str, Any] = {
        "status": (
            "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT"
            if reference is not None
            else "MISSING_EXACT_PROTEIN_REFERENCE"
        ),
        "protein_registry_artifact": _artifact_projection(
            registry_artifact,
            role="LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING",
        ),
        "expected_uniprot_release": expected_uniprot_release,
        "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
    }
    if reference is not None:
        binding.update(_reference_projection(reference))
    return binding


def _stage_safety_projection(
    *,
    missing_receipts: Sequence[str],
    promotion_blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "missing_receipts": list(missing_receipts),
        "promotion_blockers": sorted(set(promotion_blockers)),
        "grounding_evidence_emitted": False,
        "network_action_performed": False,
        "write_action_performed": False,
    }


def _trait_projection(binding: TraitBinding) -> dict[str, Any]:
    return {
        "trait_record_path": binding.relative_path,
        "trait_record_sha256": binding.sha256,
        "trait_record_has_canonical_examples": binding.has_canonical_examples,
    }


def _source_name_projection(source: CathName) -> dict[str, Any]:
    return {
        "cath_code": source.code,
        "cath_name": source.name or None,
        "cath_names_line_number": source.source_line_number,
        "cath_names_line_sha256": source.source_line_sha256,
        "cath_names_line_sha256_basis": "RAW_UTF8_PHYSICAL_LINE_INCLUDING_TERMINATOR",
    }


def _annotation_row(
    *,
    source: CathName,
    binding: TraitBinding,
    accession: str,
    intervals: Sequence[Sequence[int]],
    interpro_record: Mapping[str, Any],
    residue_record: Mapping[str, Any],
    cath_artifact: CapturedArtifact,
    interpro_artifact: CapturedArtifact,
    residue_artifact: CapturedArtifact,
    registry_artifact: CapturedArtifact,
    interpro_release: str,
    residue_release: str,
    expected_uniprot_release: str,
    source_snapshot_id: str,
    reference: ProteinReference | None,
) -> dict[str, Any]:
    projected_intervals = [{"start": interval[0], "end": interval[1]} for interval in intervals]
    single = len(projected_intervals) == 1
    sequence = residue_record["seq"]
    reasons = [DISCOVERY_ONLY_REASON, *ANNOTATION_MISSING_RECEIPTS]
    if not single:
        reasons.append(UNGROUPED_REASON)
    if reference is None:
        reasons.append(MISSING_PROTEIN_REFERENCE)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": ANNOTATION_KIND,
        "stage_status": SINGLE_LOCATION_STATUS if single else UNGROUPED_MULTI_STATUS,
        "candidate_status": (
            READY_LOCAL_REFERENCE if reference is not None else MISSING_LOCAL_PROTEIN_REFERENCE
        ),
        "candidate_status_basis": (
            "LOCAL_PROTEIN_REGISTRY_AVAILABILITY_ONLY_NOT_MAPPING_REVIEW_READINESS"
        ),
        "qualification_status": "CANDIDATE_PROTEIN",
        "qualification_claimed": False,
        "native_cath_pdb_evidence_claimed": False,
        "evidence_class": "INTERPRO_GENE3D_ANNOTATION_NOT_NATIVE_CATH_PDB_EVIDENCE",
        "selection_policy": "ALL_EXACT_PROTEIN_TRAIT_OBSERVATIONS_RETAINED_WITHOUT_RANKING",
        "blocking_reasons": reasons,
        "trait_id": binding.trait_id,
        "trait_category": binding.category,
        "protein_id": f"UniProtKB:{accession}",
        "intervals": projected_intervals,
        "scope": "LOCALIZED",
        "discovery_coordinate_frame": "UNIPROT_CANONICAL",
        "interval_grouping_status": (
            "SINGLE_LOCATION"
            if single
            else "FLATTENED_LOCATIONS_UNGROUPED_FRAGMENT_RELATIONSHIP_UNKNOWN"
        ),
        "discovery_mapping_method": "INTERPRO_CATH_GENE3D_ANNOTATION_DISCOVERY",
        "interpro_release": interpro_release,
        "residue_frame_uniprot_release": residue_release,
        "residue_frame_sequence_length": len(sequence),
        "residue_frame_sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "interpro_protein_record_sha256": value_sha256(
            {"protein_accession": accession, "matches": interpro_record}
        ),
        "interpro_observation_sha256": value_sha256(
            {
                "protein_accession": accession,
                "trait_id": binding.trait_id,
                "intervals": intervals,
            }
        ),
        "residue_record_sha256": value_sha256(
            {"protein_accession": accession, "residue_record": residue_record}
        ),
        "source_snapshot_id": source_snapshot_id,
        "source_name_binding": _source_name_projection(source),
        "trait_binding": _trait_projection(binding),
        "protein_reference_binding": _reference_binding(
            reference,
            registry_artifact=registry_artifact,
            expected_uniprot_release=expected_uniprot_release,
        ),
        "artifact_bindings": [
            _artifact_projection(cath_artifact, role="CATH_NAMES"),
            _artifact_projection(interpro_artifact, role="INTERPRO_ANNOTATION_FRAME"),
            _artifact_projection(residue_artifact, role="UNIPROT_RESIDUE_FRAME"),
        ],
        **_stage_safety_projection(
            missing_receipts=ANNOTATION_MISSING_RECEIPTS,
            promotion_blockers=reasons,
        ),
    }
    return _content_address(
        row,
        id_field="annotation_discovery_id",
        prefix="cath-gene3d-annotation-discovery:",
        row_hash_field="annotation_discovery_row_sha256",
    )


def _native_blocker_row(
    *,
    source: CathName,
    binding: TraitBinding,
    cath_artifact: CapturedArtifact,
    source_snapshot_id: str,
) -> dict[str, Any]:
    placeholder = source.representative == "???????"
    reasons = [
        MISSING_BOUNDARIES_REASON,
        MISSING_RESIDUE_SIFTS_REASON,
        MISSING_CATH_PROVIDER_RECEIPT,
    ]
    if placeholder:
        reasons.append(MISSING_REPRESENTATIVE_REASON)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": NATIVE_BLOCKER_KIND,
        "stage_status": NATIVE_BLOCKED_STATUS,
        "qualification_claimed": False,
        "native_cath_pdb_evidence_claimed": False,
        "evidence_class": "NATIVE_CATH_PDB_REPRESENTATIVE_UNMAPPED",
        "blocking_reasons": reasons,
        "required_native_sources": [
            "CATH_V4_4_0_DOMAIN_BOUNDARIES_WITH_CHAIN_AND_RESIDUE_COORDINATES",
            "MATCHING_RELEASE_MANIFEST_BOUND_RESIDUE_LEVEL_SIFTS_XML",
        ],
        "admitted_native_sources": [],
        "trait_id": binding.trait_id,
        "trait_category": binding.category,
        "representative_status": (
            "SOURCE_PLACEHOLDER_NO_REPRESENTATIVE"
            if placeholder
            else "EXACT_CATH_NAMES_REPRESENTATIVE"
        ),
        "representative_domain": None if placeholder else source.representative,
        "structure_id": None if placeholder else f"PDB:{source.representative[:4]}",
        "chain_id": None if placeholder else source.representative[4],
        "domain_ordinal": None if placeholder else int(source.representative[5:]),
        "source_snapshot_id": source_snapshot_id,
        "source_name_binding": _source_name_projection(source),
        "trait_binding": _trait_projection(binding),
        "artifact_bindings": [_artifact_projection(cath_artifact, role="CATH_NAMES")],
        **_stage_safety_projection(
            missing_receipts=NATIVE_MISSING_RECEIPTS,
            promotion_blockers=[*NATIVE_PROMOTION_BLOCKERS, *reasons],
        ),
    }
    return _content_address(
        row,
        id_field="native_blocker_id",
        prefix="cath-native-representative-blocker:",
        row_hash_field="native_blocker_row_sha256",
    )


def _request_observation_binding(observation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "annotation_discovery_id": observation["annotation_discovery_id"],
        "candidate_status": observation["candidate_status"],
        "trait_id": observation["trait_id"],
        "intervals": [dict(interval) for interval in observation["intervals"]],
        "interpro_observation_sha256": observation["interpro_observation_sha256"],
        "trait_binding": dict(observation["trait_binding"]),
        "source_name_binding": dict(observation["source_name_binding"]),
    }


def _build_requests(
    observations: Sequence[Mapping[str, Any]],
    *,
    source_snapshot_id: str,
    source_artifacts: Mapping[str, CapturedArtifact],
    registry_artifact: CapturedArtifact,
    expected_uniprot_release: str,
) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for observation in observations:
        binding = observation["protein_reference_binding"]
        if binding["status"] == "MISSING_EXACT_PROTEIN_REFERENCE":
            grouped[str(observation["protein_id"])].append(observation)

    requests: list[dict[str, Any]] = []
    for protein_id, source_rows in sorted(grouped.items()):
        source_rows = sorted(
            source_rows,
            key=lambda row: (
                _cath_sort_key(str(row["trait_id"])),
                str(row["annotation_discovery_id"]),
            ),
        )
        expected_binding = _reference_binding(
            None,
            registry_artifact=registry_artifact,
            expected_uniprot_release=expected_uniprot_release,
        )
        if any(row["protein_reference_binding"] != expected_binding for row in source_rows):
            raise CathStageError(
                f"{protein_id}: missing observations do not share one exact registry binding"
            )
        intervals = [interval for row in source_rows for interval in row["intervals"]]
        trait_ids = sorted({str(row["trait_id"]) for row in source_rows}, key=_cath_sort_key)
        observation_bindings = sorted(
            (_request_observation_binding(source_row) for source_row in source_rows),
            key=canonical_json,
        )
        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "kind": REQUEST_KIND,
            "protein_id": protein_id,
            "primary_accession_is_authoritative": True,
            "coordinate_frame": "UNIPROT_CANONICAL",
            "expected_uniprot_release": expected_uniprot_release,
            "request_reason": MISSING_PROTEIN_REFERENCE,
            "protein_reference_binding": expected_binding,
            "source_snapshot_id": source_snapshot_id,
            "source_artifacts": [
                _artifact_projection(source_artifacts["cath_names"], role="CATH_NAMES"),
                _artifact_projection(
                    source_artifacts["interpro_frame"], role="INTERPRO_ANNOTATION_FRAME"
                ),
                _artifact_projection(
                    source_artifacts["residue_frame"], role="UNIPROT_RESIDUE_FRAME"
                ),
            ],
            "cath_trait_ids": trait_ids,
            "trait_count": len(trait_ids),
            "source_annotation_discovery_ids": sorted(
                str(source_row["annotation_discovery_id"]) for source_row in source_rows
            ),
            "source_observation_count": len(source_rows),
            "source_observation_bindings": observation_bindings,
            "source_interval_count": len(intervals),
            "maximum_source_coordinate": max(int(interval["end"]) for interval in intervals),
            **_stage_safety_projection(
                missing_receipts=ANNOTATION_MISSING_RECEIPTS,
                promotion_blockers=[*ANNOTATION_PROMOTION_BLOCKERS, MISSING_PROTEIN_REFERENCE],
            ),
        }
        requests.append(
            _content_address(
                row,
                id_field="request_id",
                prefix="cath-protein-request:",
                row_hash_field="request_row_sha256",
            )
        )
    return tuple(requests)


def _validate_intervals(value: Any, *, protein: str, trait_id: str) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, list) or not value:
        raise CathStageError(f"{protein} {trait_id}: intervals must be a non-empty list")
    intervals: list[tuple[int, int]] = []
    for interval in value:
        if (
            not isinstance(interval, list)
            or len(interval) != 2
            or type(interval[0]) is not int
            or type(interval[1]) is not int
            or interval[0] < 1
            or interval[1] < interval[0]
        ):
            raise CathStageError(f"{protein} {trait_id}: invalid interval {interval!r}")
        intervals.append((interval[0], interval[1]))
    if intervals != sorted(set(intervals)):
        raise CathStageError(f"{protein} {trait_id}: intervals must be sorted and unique")
    return tuple(intervals)


def _check_expected_counts(summary: Mapping[str, Any], expected: Mapping[str, int]) -> None:
    if set(expected) != set(PRODUCTION_COUNTS):
        raise CathStageError(
            "expected_counts must contain exactly the production count contract keys"
        )
    for field, wanted in expected.items():
        if type(wanted) is not int or wanted < 0:
            raise CathStageError(f"invalid expected count for {field}: {wanted!r}")
        observed = summary.get(field)
        if observed != wanted:
            raise CathStageError(
                f"production count contract failed for {field}: expected {wanted}, observed {observed}"
            )


def build_stage(
    *,
    cath_names_path: Path,
    interpro_frame_path: Path,
    residue_frame_path: Path,
    traits_root: Path,
    protein_registry_path: Path,
    repo_root: Path = REPO_ROOT,
    expected_source_sha256: Mapping[str, str] = SOURCE_PINS,
    expected_protein_registry_sha256: str = EXPECTED_PROTEIN_REGISTRY_SHA256,
    expected_uniprot_release: str = EXPECTED_UNIPROT_RELEASE,
    expected_counts: Mapping[str, int] = PRODUCTION_COUNTS,
) -> StageResult:
    if set(expected_source_sha256) != set(SOURCE_PINS):
        raise CathStageError(
            "expected_source_sha256 must contain exactly cath_names, interpro_frame, residue_frame"
        )
    if _SHA256_RE.fullmatch(expected_protein_registry_sha256) is None:
        raise CathStageError("invalid pinned sha256 for the ProteinReference registry")
    if expected_uniprot_release != EXPECTED_UNIPROT_RELEASE:
        raise CathStageError(f"expected UniProt release must be exactly {EXPECTED_UNIPROT_RELEASE}")
    repo_binding = _bind_absolute_directory(repo_root, description="repository root")
    try:
        artifacts = {
            "cath_names": _capture(
                cath_names_path,
                description="CATH names artifact",
                repo_root=repo_binding.path,
                expected_sha256=expected_source_sha256["cath_names"],
                bound_root=repo_binding,
            ),
            "interpro_frame": _capture(
                interpro_frame_path,
                description="InterPro annotation frame",
                repo_root=repo_binding.path,
                expected_sha256=expected_source_sha256["interpro_frame"],
                bound_root=repo_binding,
            ),
            "residue_frame": _capture(
                residue_frame_path,
                description="UniProt residue frame",
                repo_root=repo_binding.path,
                expected_sha256=expected_source_sha256["residue_frame"],
                bound_root=repo_binding,
            ),
        }
        registry_artifact = _capture(
            protein_registry_path,
            description="ProteinReference registry",
            repo_root=repo_binding.path,
            expected_sha256=expected_protein_registry_sha256,
            bound_root=repo_binding,
        )
        names = parse_cath_names(artifacts["cath_names"])
        all_traits, scope, trait_artifacts, trait_path_snapshot = index_cath_traits(
            traits_root,
            names,
            repo_root=repo_binding.path,
            repo_binding=repo_binding,
        )
        interpro_meta, interpro_proteins = _load_frame(
            artifacts["interpro_frame"],
            description="InterPro annotation frame",
            expected_source="InterPro",
            residue=False,
        )
        residue_meta, residue_proteins = _load_frame(
            artifacts["residue_frame"],
            description="UniProt residue frame",
            expected_source="UniProt",
            residue=True,
        )
        if interpro_meta["release"] != EXPECTED_INTERPRO_RELEASE:
            raise CathStageError(
                f"InterPro annotation frame release must be exactly {EXPECTED_INTERPRO_RELEASE}"
            )
        if residue_meta["release"] != expected_uniprot_release:
            raise CathStageError(
                f"UniProt residue frame release must be exactly {expected_uniprot_release}"
            )
        references = load_protein_registry(registry_artifact)
        source_snapshot = _source_snapshot(
            artifacts,
            interpro_release=str(interpro_meta["release"]),
            residue_release=str(residue_meta["release"]),
        )
        source_snapshot_id = str(source_snapshot["source_snapshot_id"])
        scope_by_id = {binding.trait_id: binding for binding in scope}
        observations: list[dict[str, Any]] = []
        for accession in sorted(interpro_proteins):
            matches = interpro_proteins[accession]
            if not isinstance(matches, Mapping):
                raise CathStageError(f"InterPro protein record {accession} is not an object")
            for trait_id in sorted(set(matches) & set(scope_by_id), key=_cath_sort_key):
                if _ACCESSION_RE.fullmatch(accession) is None:
                    raise CathStageError(
                        f"exact no-example CATH observation uses non-canonical accession {accession}"
                    )
                binding = scope_by_id[trait_id]
                if binding.category != "STRUCT_HOMOLOGOUS_SUPERFAMILY":
                    raise CathStageError(
                        f"InterPro CATH-Gene3D observation is not a homologous superfamily: {trait_id}"
                    )
                intervals = _validate_intervals(
                    matches[trait_id], protein=accession, trait_id=trait_id
                )
                residue_record = residue_proteins.get(accession)
                if not isinstance(residue_record, Mapping) or set(residue_record) != {"seq", "ft"}:
                    raise CathStageError(
                        f"{accession}: exact discovery lacks an exact residue-frame record"
                    )
                sequence = residue_record["seq"]
                if (
                    not isinstance(sequence, str)
                    or _SEQUENCE_RE.fullmatch(sequence) is None
                    or not isinstance(residue_record["ft"], list)
                ):
                    raise CathStageError(f"{accession}: invalid residue-frame record")
                if any(end > len(sequence) for _, end in intervals):
                    raise CathStageError(
                        f"{accession} {trait_id}: InterPro interval exceeds residue frame"
                    )
                reference = references.get(f"UniProtKB:{accession}")
                if reference is not None and (
                    reference.row["sequence_length"] != len(sequence)
                    or reference.row["sequence_sha256"]
                    != hashlib.sha256(sequence.encode("ascii")).hexdigest()
                ):
                    raise CathStageError(
                        f"{accession}: same-release ProteinReference and residue frame disagree"
                    )
                observations.append(
                    _annotation_row(
                        source=names[trait_id.removeprefix("CATH:")],
                        binding=binding,
                        accession=accession,
                        intervals=intervals,
                        interpro_record=matches,
                        residue_record=residue_record,
                        cath_artifact=artifacts["cath_names"],
                        interpro_artifact=artifacts["interpro_frame"],
                        residue_artifact=artifacts["residue_frame"],
                        registry_artifact=registry_artifact,
                        interpro_release=interpro_meta["release"],
                        residue_release=residue_meta["release"],
                        expected_uniprot_release=expected_uniprot_release,
                        source_snapshot_id=source_snapshot_id,
                        reference=reference,
                    )
                )
        observations.sort(key=lambda row: (_cath_sort_key(row["trait_id"]), row["protein_id"]))
        blockers = [
            _native_blocker_row(
                source=names[binding.trait_id.removeprefix("CATH:")],
                binding=binding,
                cath_artifact=artifacts["cath_names"],
                source_snapshot_id=source_snapshot_id,
            )
            for binding in scope
        ]
        blockers.sort(key=lambda row: _cath_sort_key(row["trait_id"]))
        protein_requests = _build_requests(
            observations,
            source_snapshot_id=source_snapshot_id,
            source_artifacts=artifacts,
            registry_artifact=registry_artifact,
            expected_uniprot_release=expected_uniprot_release,
        )

        # Recheck sampled content and membership under the quiescent-tree
        # execution contract before reporting.
        for artifact in artifacts.values():
            _assert_unchanged(
                artifact, description="pinned source/frame artifact", bound_root=repo_binding
            )
        _assert_unchanged(
            registry_artifact,
            description="ProteinReference registry",
            bound_root=repo_binding,
        )
        for artifact in trait_artifacts:
            _assert_unchanged(artifact, description="trait record", bound_root=repo_binding)
        _reject_trait_tree_symlinks(_lexical_absolute(traits_root))
        final_paths = tuple(
            _repo_relative(path, repo_binding.path)
            for path in _candidate_cath_trait_paths(_lexical_absolute(traits_root))
        )
        if final_paths != trait_path_snapshot:
            raise CathStageError("CATH trait candidate membership drifted while staging")
        _assert_directory_binding(repo_binding, description="repository root")

        all_binding_rows = [
            {
                "trait_id": binding.trait_id,
                "trait_record_path": binding.relative_path,
                "trait_record_sha256": binding.sha256,
                "has_canonical_examples": binding.has_canonical_examples,
            }
            for binding in sorted(
                all_traits.values(), key=lambda item: _cath_sort_key(item.trait_id)
            )
        ]
        scope_binding_rows = [row for row in all_binding_rows if not row["has_canonical_examples"]]
        cath_name_rows = [
            {
                **_source_name_projection(names[code]),
                "representative": names[code].representative,
            }
            for code in sorted(names, key=_cath_sort_key)
        ]
        annotation_bytes = _rows_bytes(observations)
        blocker_bytes = _rows_bytes(blockers)
        request_bytes = _rows_bytes(protein_requests)
        single = [row for row in observations if row["stage_status"] == SINGLE_LOCATION_STATUS]
        multi = [row for row in observations if row["stage_status"] == UNGROUPED_MULTI_STATUS]
        exact_references = [
            row
            for row in observations
            if row["protein_reference_binding"]["status"] == "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT"
        ]
        missing_references = [
            row
            for row in observations
            if row["protein_reference_binding"]["status"] == "MISSING_EXACT_PROTEIN_REFERENCE"
        ]
        multi_observation_requests = [
            row for row in protein_requests if row["source_observation_count"] > 1
        ]
        exact_representatives = [
            row
            for row in blockers
            if row["representative_status"] == "EXACT_CATH_NAMES_REPRESENTATIVE"
        ]
        placeholders = [
            row
            for row in blockers
            if row["representative_status"] == "SOURCE_PLACEHOLDER_NO_REPRESENTATIVE"
        ]
        summary: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "kind": SUMMARY_KIND,
            "stage_status": "DISCOVERY_AND_NATIVE_BLOCKER_STAGE_ONLY",
            "qualification_claimed": False,
            "trait_tree_must_be_quiescent": True,
            "trait_tree_verification_semantics": (
                "DESCRIPTOR_RELATIVE_NOFOLLOW_READS_WITH_REPEATED_MEMBERSHIP_AND_"
                "CONTENT_CHECKS_NOT_AN_ATOMIC_FILESYSTEM_SNAPSHOT"
            ),
            "annotation_discovery_semantics": (
                "INTERPRO_GENE3D_ANNOTATIONS_ONLY_NOT_NATIVE_CATH_PDB_EVIDENCE"
            ),
            "native_blocker_semantics": (
                "REPRESENTATIVES_REMAIN_BLOCKED_WITHOUT_CATH_BOUNDARIES_AND_RESIDUE_SIFTS"
            ),
            "alternative_retention_policy": (
                "ALL_EXACT_PROTEIN_TRAIT_OBSERVATIONS_RETAINED_WITHOUT_RANKING"
            ),
            "source_snapshot": source_snapshot,
            "source_snapshot_id": source_snapshot_id,
            "source_artifacts": [
                _artifact_projection(artifacts["cath_names"], role="CATH_NAMES"),
                _artifact_projection(artifacts["interpro_frame"], role="INTERPRO_ANNOTATION_FRAME"),
                _artifact_projection(artifacts["residue_frame"], role="UNIPROT_RESIDUE_FRAME"),
            ],
            "protein_registry_artifact": _artifact_projection(
                registry_artifact,
                role="LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING",
            ),
            "protein_registry_expected_sha256": expected_protein_registry_sha256,
            "protein_registry_sha256_matches_stage_pin": True,
            "protein_registry_fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
            "expected_uniprot_release": expected_uniprot_release,
            "missing_receipts": sorted(
                set([*ANNOTATION_MISSING_RECEIPTS, *NATIVE_MISSING_RECEIPTS])
            ),
            "promotion_blockers": sorted(
                set(
                    [
                        *ANNOTATION_PROMOTION_BLOCKERS,
                        *NATIVE_PROMOTION_BLOCKERS,
                        UNGROUPED_REASON,
                        MISSING_PROTEIN_REFERENCE,
                        "REVIEW_REQUIRED_BEFORE_TRAIT_OR_GROUNDING_WRITE",
                    ]
                )
            ),
            "cath_release": CATH_RELEASE,
            "cath_release_date": CATH_RELEASE_DATE,
            "interpro_release": interpro_meta["release"],
            "interpro_frame_built": interpro_meta["built"],
            "interpro_frame_record_count": interpro_meta["count"],
            "residue_frame_uniprot_release": residue_meta["release"],
            "residue_frame_built": residue_meta["built"],
            "residue_frame_record_count": residue_meta["count"],
            "protein_registry_row_count": len(references),
            "cath_name_count": len(names),
            "cath_name_rows_sha256": hashlib.sha256(_rows_bytes(cath_name_rows)).hexdigest(),
            "all_cath_trait_count": len(all_traits),
            "all_cath_trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(all_binding_rows)
            ).hexdigest(),
            "no_example_trait_count": len(scope),
            "no_example_trait_category_counts": dict(
                sorted(Counter(binding.category for binding in scope).items())
            ),
            "no_example_trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(scope_binding_rows)
            ).hexdigest(),
            "native_blocker_count": len(blockers),
            "native_exact_representative_count": len(exact_representatives),
            "native_placeholder_count": len(placeholders),
            "native_blocking_reason_counts": dict(
                sorted(
                    Counter(
                        reason for row in blockers for reason in row["blocking_reasons"]
                    ).items()
                )
            ),
            "native_blocker_rows_sha256": hashlib.sha256(blocker_bytes).hexdigest(),
            "annotation_discovery_count": len(observations),
            "annotation_single_location_count": len(single),
            "annotation_ungrouped_multi_location_count": len(multi),
            "annotation_unique_trait_count": len({row["trait_id"] for row in observations}),
            "annotation_unique_protein_count": len({row["protein_id"] for row in observations}),
            "annotation_exact_local_reference_count": len(exact_references),
            "annotation_missing_local_reference_count": len(missing_references),
            "annotation_exact_local_reference_unique_protein_count": len(
                {row["protein_id"] for row in exact_references}
            ),
            "annotation_missing_local_reference_unique_protein_count": len(
                {row["protein_id"] for row in missing_references}
            ),
            "annotation_protein_reference_status_counts": dict(
                sorted(
                    Counter(
                        row["protein_reference_binding"]["status"] for row in observations
                    ).items()
                )
            ),
            "annotation_candidate_status_counts": dict(
                sorted(Counter(row["candidate_status"] for row in observations).items())
            ),
            "protein_reference_request_count": len(protein_requests),
            "protein_reference_request_unique_protein_count": len(
                {row["protein_id"] for row in protein_requests}
            ),
            "protein_reference_request_multi_observation_count": len(multi_observation_requests),
            "protein_reference_request_max_observation_count": max(
                (int(row["source_observation_count"]) for row in protein_requests), default=0
            ),
            "annotation_discovery_status_counts": dict(
                sorted(Counter(row["stage_status"] for row in observations).items())
            ),
            "annotation_discovery_rows_sha256": hashlib.sha256(annotation_bytes).hexdigest(),
            "protein_request_rows_sha256": hashlib.sha256(request_bytes).hexdigest(),
            "combined_non_summary_rows_sha256": hashlib.sha256(
                annotation_bytes + blocker_bytes + request_bytes
            ).hexdigest(),
            "grounding_evidence_emitted_count": 0,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        _check_expected_counts(summary, expected_counts)
        _content_address(
            summary,
            id_field="stage_id",
            prefix="cath-grounding-discovery-stage:",
            row_hash_field="summary_row_sha256",
        )
        return StageResult(tuple(observations), tuple(blockers), protein_requests, summary)
    finally:
        os.close(repo_binding.descriptor)


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows: list[str] = []
    if not summary_only:
        rows.extend(canonical_json(row) for row in result.annotation_discoveries)
        rows.extend(canonical_json(row) for row in result.native_blockers)
        rows.extend(canonical_json(row) for row in result.protein_requests)
    rows.append(canonical_json(result.summary))
    return "\n".join(rows) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cath-names", type=Path, default=DEFAULT_CATH_NAMES)
    parser.add_argument("--interpro-frame", type=Path, default=DEFAULT_INTERPRO_FRAME)
    parser.add_argument("--residue-frame", type=Path, default=DEFAULT_RESIDUE_FRAME)
    parser.add_argument("--traits-root", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument(
        "--protein-registry",
        type=Path,
        default=DEFAULT_PROTEIN_REGISTRY,
        help=f"exact local ProteinReference JSONL registry (default: {DEFAULT_PROTEIN_REGISTRY})",
    )
    parser.add_argument("--expected-cath-names-sha256", default=EXPECTED_CATH_NAMES_SHA256)
    parser.add_argument("--expected-interpro-frame-sha256", default=EXPECTED_INTERPRO_FRAME_SHA256)
    parser.add_argument("--expected-residue-frame-sha256", default=EXPECTED_RESIDUE_FRAME_SHA256)
    parser.add_argument(
        "--expected-protein-registry-sha256",
        default=EXPECTED_PROTEIN_REGISTRY_SHA256,
    )
    parser.add_argument("--expect-uniprot-release", default=EXPECTED_UNIPROT_RELEASE)
    parser.add_argument("--summary-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_stage(
            cath_names_path=args.cath_names,
            interpro_frame_path=args.interpro_frame,
            residue_frame_path=args.residue_frame,
            traits_root=args.traits_root,
            protein_registry_path=args.protein_registry,
            expected_protein_registry_sha256=args.expected_protein_registry_sha256,
            expected_uniprot_release=args.expect_uniprot_release,
            expected_source_sha256={
                "cath_names": args.expected_cath_names_sha256,
                "interpro_frame": args.expected_interpro_frame_sha256,
                "residue_frame": args.expected_residue_frame_sha256,
            },
        )
    except (OSError, CathStageError, ValueError) as error:
        print(f"refusing to stage CATH grounding discovery: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
