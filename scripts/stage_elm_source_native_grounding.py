#!/usr/bin/env python3
"""Stage ELM source-native occurrences against a local protein registry.

The two ELM TSV exports contain class regular expressions and instance
accession/coordinate assertions, but no source sequence, taxon identifier, or
provider acquisition receipt.  This command binds the exact local exports,
replays every source row, verifies the current 353 ELM trait projections and
the seeder's historical first-15 example slice, and compares true-positive
coordinates with exact ProteinReferences when available.  Registry rows must
all name the expected UniProt release, but the registry bytes are not treated
as provider-verified because this stage has no bound UniProt fetch receipt.

Every source instance is retained.  Non-true-positive logic is excluded;
missing references, coordinate drift, interval/pattern discrepancies, and
terminal-anchor mistakes are partitioned explicitly.  When the exact
canonical/isoform ProteinReference is present, the source
coordinates are in bounds, the ELM regex consumes the exact interval in the
complete protein, and the ELM organism label agrees with the registry taxon
label, those facts are emitted only as local-registry match candidates.  They
are never GroundingEvidence: the current plain-HTTP ELM fetch has no immutable
provider acquisition receipt, the local protein registry is not bound here to
its UniProt fetch receipt, and the central validator rejects ELM qualification
until both provenance chains can be represented and verified.

There is no writer, output-file, network, fetch, apply, or promotion mode.
Canonical JSONL is written only to stdout.  The trait tree must remain
quiescent while the command runs: descriptor-relative no-follow reads and
repeated membership/content checks detect sampled drift but are not an atomic
filesystem snapshot against an uncooperative writer.
"""

from __future__ import annotations

import argparse
import csv
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
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

import ripgrep_prefilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_uniprot_grounding as grounding  # noqa: E402
from yaml_emit import slugify as _slugify  # noqa: E402

SCHEMA_VERSION = 1
OCCURRENCE_KIND = "ELM_SOURCE_NATIVE_OCCURRENCE"
REQUEST_KIND = "ELM_PROTEIN_REFERENCE_REQUEST"
SUMMARY_KIND = "ELM_SOURCE_NATIVE_STAGE_SUMMARY"

EXPECTED_CLASSES_SHA256 = "70b52085abf7c11ccac30feb7a81eb88c405cd029e99d6f8be95c2f613edf9d8"
EXPECTED_INSTANCES_SHA256 = "272e2de87817cabdb236984419c5be7e82dc6fd3b85ecab34b655db48022c7c3"
SOURCE_PINS = {
    "classes": EXPECTED_CLASSES_SHA256,
    "instances": EXPECTED_INSTANCES_SHA256,
}

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLASSES = REPO_ROOT / "data/raw/elm/elm_classes.tsv"
DEFAULT_INSTANCES = REPO_ROOT / "data/raw/elm/elm_instances.tsv"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data/traits"
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data/grounding/protein_registry.jsonl"
EXPECTED_UNIPROT_RELEASE = "2026_02"

CLASS_COLUMNS = (
    "Accession",
    "ELMIdentifier",
    "FunctionalSiteName",
    "Description",
    "Regex",
    "Probability",
    "#Instances",
    "#Instances_in_PDB",
)
INSTANCE_COLUMNS = (
    "Accession",
    "ELMType",
    "ELMIdentifier",
    "ProteinName",
    "Primary_Acc",
    "Accessions",
    "Start",
    "End",
    "References",
    "Methods",
    "InstanceLogic",
    "PDB",
    "Organism",
)
CLASS_METADATA_KEYS = (
    "ELM_Classes_Download_Version",
    "ELM_Classes_Download_Date",
    "Origin",
    "Type",
    "Num_Classes",
)
INSTANCE_METADATA_KEYS = (
    "ELM_Instance_Download_Version",
    "ELM_Instance_Download_Date",
    "Origin",
    "Type",
    "NumInstances",
)

ROUTE = {
    "CLV": ("SEQ_CLEAVAGE_SITE", "cleavage_site"),
    "TRG": ("SEQ_TARGETING_SIGNAL", "targeting_signal"),
    "MOD": ("SEQ_PTM_SITE", "ptm_site"),
    "LIG": ("SEQ_MOTIF", "motif"),
    "DOC": ("SEQ_MOTIF", "motif"),
    "DEG": ("SEQ_MOTIF", "motif"),
}
INSTANCE_LOGIC = frozenset({"true positive", "false positive", "true negative", "unknown"})
TRUE_POSITIVE = "true positive"
TRAIT_LICENSE = "ELM Software License (non-commercial)"

MISSING_ACQUISITION_RECEIPT = "MISSING_ELM_PROVIDER_ACQUISITION_RECEIPT"
MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT = "MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT"
MISSING_PROTEIN_REFERENCE = "MISSING_EXPECTED_RELEASE_LOCAL_PROTEIN_REFERENCE"
NON_TRUE_POSITIVE = "SOURCE_INSTANCE_LOGIC_IS_NOT_TRUE_POSITIVE"
COORDINATE_DRIFT = "SOURCE_COORDINATE_OUT_OF_BOUNDS"
PATTERN_WIDTH_REVIEW = "SOURCE_INTERVAL_CONTAINS_ONLY_PATTERN_SUBSPAN"
PATTERN_SEQUENCE_REVIEW = "SOURCE_INTERVAL_PATTERN_SEQUENCE_MISMATCH"
TAXON_LABEL_REVIEW = "SOURCE_ORGANISM_REGISTRY_TAXON_LABEL_MISMATCH"
INLINE_REFERENCE_CONFLICT = "CURRENT_INLINE_SEQUENCE_DIFFERS_FROM_PROTEIN_REFERENCE"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_CLASS_ACCESSION_RE = re.compile(r"^ELME[0-9]{6}$")
_INSTANCE_ACCESSION_RE = re.compile(r"^ELMI[0-9]{6}$")
_UNIPROT_ACCESSION_RE = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[1-9][0-9]*)?$"
)
_PDB_RE = re.compile(r"^[0-9][A-Za-z0-9]{3}$")
_SEQUENCE_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")
_UNIPROT_RELEASE_RE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
_FORBIDDEN_LEGACY_GROUNDING_FIELDS = frozenset(
    {
        "qualification_status",
        "trait_occurrences",
        "sequence_sha256",
        "sequence_length",
        "sequence_version",
        "uniprot_release",
        "taxon_id",
        "reviewed",
    }
)


class ElmStageError(ValueError):
    """A source, trait, registry, or filesystem invariant failed closed."""


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
class ElmClass:
    accession: str
    identifier: str
    prefix: str
    site_name: str
    description: str
    regex: str
    probability_text: str
    instance_count: int
    pdb_instance_count: int
    source_line_number: int
    source_raw_line_sha256: str

    @property
    def trait_id(self) -> str:
        return f"ELM:{self.accession}"


@dataclass(frozen=True)
class ElmInstance:
    accession: str
    elm_type: str
    elm_identifier: str
    protein_name: str
    primary_accession: str
    aliases: tuple[str, ...]
    start: int
    end: int
    pubmed_ids: tuple[str, ...]
    methods: tuple[str, ...]
    logic: str
    pdb_ids: tuple[str, ...]
    organism_label: str
    source_line_number: int
    source_raw_line_sha256: str

    @property
    def protein_id(self) -> str:
        return f"UniProtKB:{self.primary_accession}"


@dataclass(frozen=True)
class TraitBinding:
    trait_id: str
    path: Path
    relative_path: str
    sha256: str
    record: Mapping[str, Any]
    selected_instance_ids: tuple[str, ...]


@dataclass(frozen=True)
class InlineSequence:
    protein_id: str
    sequence: str
    sequence_sha256: str
    selected_example_count: int


@dataclass(frozen=True)
class StageResult:
    occurrences: tuple[dict[str, Any], ...]
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


def _content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> dict[str, Any]:
    row[id_field] = prefix + value_sha256(row)
    row[row_hash_field] = value_sha256(row)
    return row


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
        raise ElmStageError(
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
        raise ElmStageError(
            f"{description} escapes bound root {lexical_root}: {lexical_path}"
        ) from error
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise ElmStageError(f"invalid relative {description} path: {relative}")
    return relative


def _bind_absolute_directory(path: Path, *, description: str) -> BoundDirectory:
    directory_flags, _ = _descriptor_safety_flags()
    lexical_path = _lexical_absolute(path)
    if lexical_path.anchor != os.sep:
        raise ElmStageError(f"{description} must have an absolute POSIX path: {path}")
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
        raise ElmStageError(
            f"cannot bind {description} without following symlinks {lexical_path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ElmStageError(f"{description} must be a directory: {lexical_path}")
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
        raise ElmStageError(
            f"cannot bind {description} without following symlinks {path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ElmStageError(f"{description} must be a directory: {path}")
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
            raise ElmStageError(f"{description} binding changed while staging: {binding.path}")
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
        raise ElmStageError(f"invalid relative {description} path: {relative_path}")
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
            raise ElmStageError(f"{description} must be a regular file: {display_path}")
        chunks: list[bytes] = []
        while chunk := os.read(file_descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise ElmStageError(f"{description} changed while reading: {display_path}")
        return b"".join(chunks)
    except ElmStageError:
        raise
    except OSError as error:
        raise ElmStageError(
            f"cannot open {description} without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


def _repo_relative(path: Path, repo_root: Path) -> str:
    return _relative_under(path, repo_root, description="path").as_posix()


def _capture(
    path: Path,
    *,
    description: str,
    repo_root: Path,
    expected_sha256: str | None,
    bound_root: BoundDirectory,
) -> CapturedArtifact:
    if expected_sha256 is not None and _SHA256_RE.fullmatch(expected_sha256) is None:
        raise ElmStageError(f"invalid pinned sha256 for {description}: {expected_sha256!r}")
    relative = _relative_under(path, bound_root.path, description=description)
    raw = _read_relative_bytes(
        bound_root,
        relative,
        display_path=_lexical_absolute(path),
        description=description,
    )
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ElmStageError(
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
        raise ElmStageError(
            f"{description} drifted while staging: {artifact.path}; "
            f"expected {artifact.sha256}, observed {observed}"
        )


def _parse_export(
    artifact: CapturedArtifact,
    *,
    metadata_keys: Sequence[str],
    columns: Sequence[str],
) -> tuple[dict[str, str], list[tuple[int, tuple[str, ...], str]]]:
    raw = artifact.raw
    if not raw or not raw.endswith(b"\n") or b"\x00" in raw:
        raise ElmStageError(f"{artifact.relative_path}: expected newline-terminated UTF-8 text")
    try:
        physical = raw.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ElmStageError(f"{artifact.relative_path}: invalid UTF-8: {error}") from error
    if len(physical) < len(metadata_keys) + 2:
        raise ElmStageError(f"{artifact.relative_path}: truncated ELM export")

    def line_content(line: str, line_number: int) -> str:
        if line.endswith("\r\n"):
            content = line[:-2]
        elif line.endswith("\n"):
            content = line[:-1]
        else:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: unterminated physical line"
            )
        if "\r" in content:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: bare carriage return in field data"
            )
        return content

    metadata: dict[str, str] = {}
    for index, expected_key in enumerate(metadata_keys):
        line = line_content(physical[index], index + 1)
        match = re.fullmatch(r"#([^:]+): (.+)", line)
        if match is None or match.group(1) != expected_key:
            raise ElmStageError(
                f"{artifact.relative_path}:{index + 1}: expected metadata key {expected_key}"
            )
        metadata[expected_key] = match.group(2)
    if metadata.get("Origin") != "asimov" or metadata.get("Type") != "tsv":
        raise ElmStageError(f"{artifact.relative_path}: unexpected ELM origin/type metadata")
    header_index = len(metadata_keys)
    try:
        header = tuple(
            next(
                csv.reader(
                    [line_content(physical[header_index], header_index + 1)],
                    delimiter="\t",
                    strict=True,
                )
            )
        )
    except (csv.Error, StopIteration) as error:
        raise ElmStageError(f"{artifact.relative_path}: invalid TSV header: {error}") from error
    if header != tuple(columns):
        raise ElmStageError(
            f"{artifact.relative_path}: header mismatch; expected {tuple(columns)!r}, "
            f"observed {header!r}"
        )
    rows: list[tuple[int, tuple[str, ...], str]] = []
    for line_number, physical_line in enumerate(physical[header_index + 1 :], header_index + 2):
        text = line_content(physical_line, line_number)
        if text.startswith("#"):
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: comment after header")
        try:
            fields = tuple(next(csv.reader([text], delimiter="\t", strict=True)))
        except (csv.Error, StopIteration) as error:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid TSV row: {error}"
            ) from error
        if len(fields) != len(columns):
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: expected {len(columns)} fields, "
                f"observed {len(fields)}"
            )
        rows.append(
            (
                line_number,
                fields,
                hashlib.sha256(physical_line.encode("utf-8")).hexdigest(),
            )
        )
    return metadata, rows


def parse_classes(
    artifact: CapturedArtifact,
) -> tuple[dict[str, str], tuple[ElmClass, ...]]:
    metadata, raw_rows = _parse_export(
        artifact, metadata_keys=CLASS_METADATA_KEYS, columns=CLASS_COLUMNS
    )
    classes: list[ElmClass] = []
    accessions: set[str] = set()
    identifiers: set[str] = set()
    regexes: set[str] = set()
    for line_number, fields, line_sha in raw_rows:
        row = dict(zip(CLASS_COLUMNS, fields, strict=True))
        if any(not value for value in fields):
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: empty class field")
        accession, identifier, expression = (
            row["Accession"],
            row["ELMIdentifier"],
            row["Regex"],
        )
        prefix = identifier.split("_", 1)[0]
        if _CLASS_ACCESSION_RE.fullmatch(accession) is None or prefix not in ROUTE:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid ELM class key")
        if accession in accessions or identifier in identifiers or expression in regexes:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: duplicate class identity")
        try:
            probability = Decimal(row["Probability"])
        except InvalidOperation as error:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid probability"
            ) from error
        if not probability.is_finite() or probability < 0 or probability > 1:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid probability")
        try:
            instance_count = int(row["#Instances"])
            pdb_count = int(row["#Instances_in_PDB"])
        except ValueError as error:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid instance count"
            ) from error
        if instance_count < 0 or pdb_count < 0 or pdb_count > instance_count:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid instance count")
        try:
            re.compile(expression)
        except re.error as error:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid ELM regex: {error}"
            ) from error
        accessions.add(accession)
        identifiers.add(identifier)
        regexes.add(expression)
        classes.append(
            ElmClass(
                accession=accession,
                identifier=identifier,
                prefix=prefix,
                site_name=row["FunctionalSiteName"],
                description=row["Description"],
                regex=expression,
                probability_text=row["Probability"],
                instance_count=instance_count,
                pdb_instance_count=pdb_count,
                source_line_number=line_number,
                source_raw_line_sha256=line_sha,
            )
        )
    if metadata["Num_Classes"] != str(len(classes)):
        raise ElmStageError(f"{artifact.relative_path}: Num_Classes does not match rows")
    return metadata, tuple(classes)


def parse_instances(
    artifact: CapturedArtifact,
    classes: Sequence[ElmClass],
) -> tuple[dict[str, str], tuple[ElmInstance, ...]]:
    metadata, raw_rows = _parse_export(
        artifact, metadata_keys=INSTANCE_METADATA_KEYS, columns=INSTANCE_COLUMNS
    )
    by_identifier = {item.identifier: item for item in classes}
    instances: list[ElmInstance] = []
    accessions: set[str] = set()
    source_keys: set[tuple[str, str, int, int]] = set()
    counts: Counter[str] = Counter()
    pdb_counts: Counter[str] = Counter()
    for line_number, fields, line_sha in raw_rows:
        row = dict(zip(INSTANCE_COLUMNS, fields, strict=True))
        required = (
            "Accession",
            "ELMType",
            "ELMIdentifier",
            "ProteinName",
            "Primary_Acc",
            "Accessions",
            "Start",
            "End",
            "InstanceLogic",
            "Organism",
        )
        if any(not row[field] for field in required):
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: empty required field")
        accession = row["Accession"]
        if _INSTANCE_ACCESSION_RE.fullmatch(accession) is None or accession in accessions:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid/duplicate instance accession"
            )
        elm_class = by_identifier.get(row["ELMIdentifier"])
        if elm_class is None or row["ELMType"] != elm_class.prefix:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: missing/mismatched class binding"
            )
        primary = row["Primary_Acc"]
        if _UNIPROT_ACCESSION_RE.fullmatch(primary) is None:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid Primary_Acc {primary!r}"
            )
        try:
            start, end = int(row["Start"]), int(row["End"])
        except ValueError as error:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: non-integral coordinates"
            ) from error
        if start < 1 or end < start:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid coordinates")
        source_key = (row["ELMIdentifier"], primary, start, end)
        if source_key in source_keys:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: duplicate source occurrence tuple"
            )
        logic = row["InstanceLogic"]
        if logic not in INSTANCE_LOGIC:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: unknown instance logic")
        pubmed_ids = tuple(row["References"].split())
        if any(not token.isdigit() for token in pubmed_ids):
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid PMID token")
        methods = tuple(item.strip() for item in row["Methods"].split(";") if item.strip())
        if row["Methods"] and not methods:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid Methods field")
        pdb_ids = tuple(row["PDB"].split())
        if any(_PDB_RE.fullmatch(item) is None for item in pdb_ids):
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid PDB token")
        aliases = tuple(row["Accessions"].split())
        if not aliases or any(re.fullmatch(r"[A-Za-z0-9_-]+", item) is None for item in aliases):
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: invalid alias field")
        accessions.add(accession)
        source_keys.add(source_key)
        counts[elm_class.identifier] += 1
        if pdb_ids:
            pdb_counts[elm_class.identifier] += 1
        instances.append(
            ElmInstance(
                accession=accession,
                elm_type=row["ELMType"],
                elm_identifier=row["ELMIdentifier"],
                protein_name=row["ProteinName"],
                primary_accession=primary,
                aliases=aliases,
                start=start,
                end=end,
                pubmed_ids=pubmed_ids,
                methods=methods,
                logic=logic,
                pdb_ids=pdb_ids,
                organism_label=row["Organism"],
                source_line_number=line_number,
                source_raw_line_sha256=line_sha,
            )
        )
    if metadata["NumInstances"] != str(len(instances)):
        raise ElmStageError(f"{artifact.relative_path}: NumInstances does not match rows")
    for elm_class in classes:
        if counts[elm_class.identifier] != elm_class.instance_count:
            raise ElmStageError(
                f"class {elm_class.identifier} #Instances disagrees with instance export"
            )
        if pdb_counts[elm_class.identifier] != elm_class.pdb_instance_count:
            raise ElmStageError(
                f"class {elm_class.identifier} #Instances_in_PDB disagrees with export"
            )
    return metadata, tuple(instances)


_BaseSafeLoader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


class _UniqueKeyLoader(_BaseSafeLoader):  # type: ignore[misc,valid-type]
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
            raise ElmStageError("trait YAML has an unhashable mapping key") from error
        if duplicate:
            raise ElmStageError(f"trait YAML has duplicate key {key!r}")
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
            raise ElmStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for key, item in value.items():
            if not isinstance(key, str):
                raise ElmStageError(f"{source}: YAML mapping key is not a string")
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise ElmStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for item in value:
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if value is None or type(value) in {str, int, bool}:
        return
    if type(value) is float and math.isfinite(value):
        return
    raise ElmStageError(f"{source}: YAML value is outside the JSON data model")


def _load_yaml_mapping(raw: bytes, *, path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError, ElmStageError) as error:
        raise ElmStageError(f"cannot parse trait record {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise ElmStageError(f"trait record is not a mapping: {path}")
    _require_json_shape(value, source=str(path))
    return value


def _reject_trait_tree_symlinks(traits_root: Path) -> None:
    def fail(error: OSError) -> None:
        raise ElmStageError(f"cannot scan trait tree {traits_root}: {error}")

    for directory, names, files in os.walk(
        traits_root, topdown=True, onerror=fail, followlinks=False
    ):
        for name in [*names, *files]:
            path = Path(directory) / name
            try:
                metadata = os.stat(path, follow_symlinks=False)
            except OSError as error:
                raise ElmStageError(f"cannot inspect trait-tree entry {path}: {error}") from error
            if stat.S_ISLNK(metadata.st_mode):
                raise ElmStageError(f"symlink below trait directory is forbidden: {path}")


def _trait_filename(elm_class: ElmClass) -> str:
    slug = _slugify(elm_class.identifier, 70, "elm")
    return f"{slug}-{elm_class.accession.lower()}.yaml"


def _expected_trait_path(traits_root: Path, elm_class: ElmClass) -> Path:
    _, subdir = ROUTE[elm_class.prefix]
    return traits_root / "sequence" / subdir / "elm" / _trait_filename(elm_class)


def _route_trait_paths(
    traits_binding: BoundDirectory, classes: Sequence[ElmClass]
) -> tuple[Path, ...]:
    paths: set[Path] = set()
    for subdir in sorted({route[1] for route in ROUTE.values()}):
        route = traits_binding.path / "sequence" / subdir / "elm"
        binding = _bind_subdirectory(
            traits_binding, route, description=f"required ELM {subdir} trait route"
        )
        try:
            for name in sorted(os.listdir(binding.descriptor)):
                metadata = os.stat(name, dir_fd=binding.descriptor, follow_symlinks=False)
                path = binding.path / name
                if stat.S_ISLNK(metadata.st_mode):
                    raise ElmStageError(f"symlink in ELM trait route is forbidden: {path}")
                if not stat.S_ISREG(metadata.st_mode) or Path(name).suffix not in {".yaml", ".yml"}:
                    raise ElmStageError(f"ELM trait route may contain only YAML records: {path}")
                paths.add(path)
        finally:
            os.close(binding.descriptor)
    expected = {
        _lexical_absolute(_expected_trait_path(traits_binding.path, item)) for item in classes
    }
    if not expected <= {_lexical_absolute(path) for path in paths}:
        missing = sorted(str(path) for path in expected - {_lexical_absolute(p) for p in paths})[
            :10
        ]
        raise ElmStageError(f"required ELM trait paths are missing: {missing}")
    return tuple(sorted(paths))


def _candidate_trait_paths(
    traits_binding: BoundDirectory, classes: Sequence[ElmClass]
) -> tuple[Path, ...]:
    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits_binding.path), "ELM trait")
        return tuple(sorted(found))
    command = [
        executable,
        "--no-config",
        "--null",
        "-l",
        "--text",
        "--hidden",
        "--no-ignore",
        "--glob",
        "*.yaml",
        "--glob",
        "*.yml",
        "-e",
        "ELM:",
        "-e",
        r"\\",
        "-e",
        r"\x00",
        "--",
        str(traits_binding.path),
    ]
    try:
        scan = subprocess.run(command, check=False, capture_output=True)
    except OSError as error:
        raise ElmStageError(f"cannot run ripgrep ELM trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise ElmStageError(f"ripgrep ELM trait prefilter failed: {detail}")
    try:
        paths = {Path(raw.decode("utf-8")) for raw in scan.stdout.split(b"\0") if raw}
    except UnicodeDecodeError as error:
        raise ElmStageError(f"ripgrep returned a non-UTF-8 trait path: {error}") from error
    paths.update(_route_trait_paths(traits_binding, classes))
    return tuple(sorted(paths))


def _selected_by_class(instances: Sequence[ElmInstance]) -> dict[str, tuple[ElmInstance, ...]]:
    grouped: dict[str, list[ElmInstance]] = defaultdict(list)
    for item in instances:
        if item.logic == TRUE_POSITIVE:
            grouped[item.elm_identifier].append(item)
    return {key: tuple(values[:15]) for key, values in grouped.items()}


def _validate_current_example(
    example: Any,
    source: ElmInstance,
    elm_class: ElmClass,
    *,
    path: Path,
    index: int,
) -> str | None:
    if not isinstance(example, Mapping):
        raise ElmStageError(f"{path}: canonical example {index} is not a mapping")
    forbidden = sorted(_FORBIDDEN_LEGACY_GROUNDING_FIELDS.intersection(example))
    if forbidden:
        raise ElmStageError(
            f"{path}: canonical example {index} carries forbidden grounding fields: {forbidden}"
        )
    allowed = {
        "protein_id",
        "protein_label",
        "taxon_label",
        "note",
        "source",
        "features",
        "sequence",
    }
    unexpected = sorted(set(example) - allowed)
    if unexpected:
        raise ElmStageError(
            f"{path}: canonical example {index} carries unexpected legacy fields: {unexpected}"
        )
    expected = {
        "protein_id": source.protein_id,
        "protein_label": source.protein_name,
        "taxon_label": source.organism_label,
        "note": "ELM true-positive instance",
        "source": "CURATOR",
    }
    for field, value in expected.items():
        if example.get(field) != value:
            raise ElmStageError(
                f"{path}: canonical example {index} source binding mismatch for {field}"
            )
    features = example.get("features")
    expected_feature = {
        "start": source.start,
        "end": source.end,
        "feature_type": "MOTIF",
        "trait_axis": "SEQUENCE",
        "trait_category": ROUTE[elm_class.prefix][0],
    }
    if features != [expected_feature]:
        raise ElmStageError(f"{path}: canonical example {index} feature binding drifted")
    sequence = example.get("sequence")
    if sequence is None:
        return None
    if not isinstance(sequence, str) or _SEQUENCE_RE.fullmatch(sequence) is None:
        raise ElmStageError(f"{path}: canonical example {index} has invalid inline sequence")
    return sequence


def _normalized_whitespace(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return re.sub(r"\s+", " ", value).strip()


def _expected_trait_definition(elm_class: ElmClass) -> str:
    subject = elm_class.site_name or elm_class.identifier
    return f"{subject} — {elm_class.description}" if elm_class.description else subject


def index_traits(
    traits_root: Path,
    classes: Sequence[ElmClass],
    instances: Sequence[ElmInstance],
    *,
    repo_root: Path,
    repo_binding: BoundDirectory,
) -> tuple[
    dict[str, TraitBinding],
    dict[str, dict[str, Any]],
    dict[str, InlineSequence],
    tuple[ArtifactDigest, ...],
    tuple[Path, ...],
]:
    traits_binding = _bind_subdirectory(repo_binding, traits_root, description="trait root")
    try:
        _reject_trait_tree_symlinks(traits_binding.path)
        candidates = _candidate_trait_paths(traits_binding, classes)
        by_trait = {item.trait_id: item for item in classes}
        selected = _selected_by_class(instances)
        selected_example_binding: dict[str, dict[str, Any]] = {}
        sequence_values: dict[str, set[str]] = defaultdict(set)
        sequence_counts: Counter[str] = Counter()
        bindings: dict[str, TraitBinding] = {}
        captured: list[ArtifactDigest] = []
        captured_relative: list[Path] = []
        exact_routes = {
            _lexical_absolute(traits_binding.path / "sequence" / route[1] / "elm")
            for route in ROUTE.values()
        }
        for reported in candidates:
            relative = _relative_under(reported, traits_binding.path, description="trait candidate")
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
            inside_exact_route = _lexical_absolute(path).parent in exact_routes
            if not isinstance(identifier, str) or not identifier.startswith("ELM:"):
                if inside_exact_route:
                    raise ElmStageError(f"{path}: non-ELM identity in an exact ELM route")
                continue
            elm_class = by_trait.get(identifier)
            if elm_class is None:
                raise ElmStageError(f"{path}: ELM identity is absent from the class snapshot")
            expected_path = _lexical_absolute(_expected_trait_path(traits_binding.path, elm_class))
            if _lexical_absolute(path) != expected_path:
                raise ElmStageError(
                    f"{path}: ELM trait is outside its exact source-derived path {expected_path}"
                )
            category, _ = ROUTE[elm_class.prefix]
            contract = {
                "identifier": identifier,
                "label": elm_class.identifier,
                "definition_source": "ELM (Eukaryotic Linear Motif resource)",
                "trait_axis": "SEQUENCE",
                "trait_category": category,
                "term_kind": "CLASS",
                "sequence_pattern": elm_class.regex,
                "license": TRAIT_LICENSE,
            }
            for field, expected in contract.items():
                if record.get(field) != expected:
                    raise ElmStageError(
                        f"{path}: trait contract mismatch for {field}: expected {expected!r}, "
                        f"observed {record.get(field)!r}"
                    )
            expected_definition = _normalized_whitespace(_expected_trait_definition(elm_class))
            observed_definition = _normalized_whitespace(record.get("definition"))
            if observed_definition != expected_definition:
                raise ElmStageError(
                    f"{path}: trait contract mismatch for definition: expected "
                    f"{expected_definition!r}, observed {observed_definition!r}"
                )
            if record.get("mapping_status") not in {"SEEDED", "REVIEWED"}:
                raise ElmStageError(f"{path}: invalid ELM mapping_status")
            source_examples = selected.get(elm_class.identifier, ())
            current_examples = record.get("canonical_examples", [])
            if not isinstance(current_examples, list) or len(current_examples) != len(
                source_examples
            ):
                raise ElmStageError(
                    f"{path}: canonical_examples do not equal the source-order first-15 slice"
                )
            for index, (example, source) in enumerate(
                zip(current_examples, source_examples, strict=True)
            ):
                sequence = _validate_current_example(
                    example, source, elm_class, path=path, index=index
                )
                selected_example_binding[source.accession] = {
                    "selected_by_legacy_first_15_cap": True,
                    "current_example_index": index,
                    "current_example_trait_id": identifier,
                    "current_example_has_inline_sequence": sequence is not None,
                }
                if sequence is not None:
                    sequence_values[source.protein_id].add(sequence)
                    sequence_counts[source.protein_id] += 1
            if identifier in bindings:
                raise ElmStageError(f"duplicate ELM trait identity {identifier}")
            bindings[identifier] = TraitBinding(
                trait_id=identifier,
                path=path,
                relative_path=repo_relative,
                sha256=digest,
                record=record,
                selected_instance_ids=tuple(item.accession for item in source_examples),
            )
        if set(bindings) != set(by_trait):
            raise ElmStageError("ELM trait identity set does not equal the class snapshot")
        inline: dict[str, InlineSequence] = {}
        for protein_id, values in sequence_values.items():
            if len(values) != 1:
                raise ElmStageError(f"conflicting current ELM inline sequences for {protein_id}")
            sequence = next(iter(values))
            inline[protein_id] = InlineSequence(
                protein_id=protein_id,
                sequence=sequence,
                sequence_sha256=hashlib.sha256(sequence.encode("ascii")).hexdigest(),
                selected_example_count=sequence_counts[protein_id],
            )
        _reject_trait_tree_symlinks(traits_binding.path)
        _assert_directory_binding(traits_binding, description="trait root")
        final = tuple(
            _relative_under(path, traits_binding.path, description="trait candidate")
            for path in _candidate_trait_paths(traits_binding, classes)
        )
        if final != tuple(captured_relative):
            raise ElmStageError("ELM trait candidate membership drifted while indexing")
        return bindings, selected_example_binding, inline, tuple(captured), final
    finally:
        os.close(traits_binding.descriptor)


def _strict_json_object(raw: str, *, source: str) -> dict[str, Any]:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ElmStageError(f"{source}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw,
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ElmStageError(f"{source}: non-finite JSON number {token}")
            ),
        )
    except (json.JSONDecodeError, ElmStageError) as error:
        raise ElmStageError(f"{source}: invalid registry JSON: {error}") from error
    if not isinstance(value, dict):
        raise ElmStageError(f"{source}: registry line is not an object")
    return value


def parse_protein_registry(
    artifact: CapturedArtifact,
    *,
    expected_release: str,
) -> dict[str, dict[str, Any]]:
    if _UNIPROT_RELEASE_RE.fullmatch(expected_release) is None:
        raise ElmStageError(f"invalid expected UniProt release: {expected_release!r}")
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ElmStageError(f"{artifact.relative_path}: registry is not UTF-8") from error
    if artifact.raw and (not artifact.raw.endswith(b"\n") or b"\r" in artifact.raw):
        raise ElmStageError(f"{artifact.relative_path}: registry must be canonical LF JSONL")
    registry: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise ElmStageError(f"{artifact.relative_path}:{line_number}: blank registry line")
        value = _strict_json_object(line, source=f"{artifact.relative_path}:{line_number}")
        findings = grounding.validate_protein_reference(value, path=artifact.path, line=line_number)
        if findings:
            detail = "; ".join(f"{item.code}: {item.message}" for item in findings)
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: invalid ProteinReference: {detail}"
            )
        if canonical_json(value) != line:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: ProteinReference is not canonical JSON"
            )
        if value.get("uniprot_release") != expected_release:
            raise ElmStageError(
                f"{artifact.relative_path}:{line_number}: ProteinReference release "
                f"{value.get('uniprot_release')!r} does not equal expected UniProt release "
                f"{expected_release!r}"
            )
        protein_id = value["protein_id"]
        if protein_id in registry:
            raise ElmStageError(
                f"{artifact.relative_path}: duplicate ProteinReference {protein_id}"
            )
        registry[protein_id] = value
    return registry


def _artifact_projection(artifact: CapturedArtifact, *, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": artifact.relative_path,
        "sha256": artifact.sha256,
        "size_bytes": len(artifact.raw),
    }


def _source_snapshot(
    classes_artifact: CapturedArtifact,
    instances_artifact: CapturedArtifact,
    classes_metadata: Mapping[str, str],
    instances_metadata: Mapping[str, str],
) -> dict[str, Any]:
    snapshot = {
        "kind": "ELM_SOURCE_PAIR_SNAPSHOT",
        "schema_version": SCHEMA_VERSION,
        "classes": _artifact_projection(classes_artifact, role="ELM_CLASSES_EXPORT"),
        "instances": _artifact_projection(instances_artifact, role="ELM_INSTANCES_EXPORT"),
        "classes_metadata": dict(classes_metadata),
        "instances_metadata": dict(instances_metadata),
        "acquisition_status": "LOCAL_BYTES_WITHOUT_PROVIDER_FETCH_RECEIPT",
        "provider_urls_declared_by_stage": [
            "http://elm.eu.org/elms/elms_index.tsv",
            "http://elm.eu.org/instances.tsv?q=*",
        ],
    }
    snapshot["source_snapshot_id"] = "elm-source-snapshot:" + value_sha256(snapshot)
    return snapshot


def _pattern_evaluation(
    elm_class: ElmClass, instance: ElmInstance, sequence: str
) -> dict[str, Any]:
    if instance.end > len(sequence):
        return {
            "status": "SOURCE_COORDINATE_OUT_OF_BOUNDS",
            "bounds_verified": False,
            "sequence_length": len(sequence),
            "annotated_sequence": None,
        }
    expression = re.compile(elm_class.regex)
    annotated = sequence[instance.start - 1 : instance.end]
    if grounding.elm_pattern_matches_exact_span(expression, sequence, instance.start, instance.end):
        status = "EXACT_REGEX_SPAN_IN_COMPLETE_PROTEIN"
        exact_span = [instance.start, instance.end]
    else:
        contained = []
        for position in range(instance.start - 1, instance.end):
            match = expression.match(sequence, position)
            if match is not None and match.end() <= instance.end:
                contained.append([match.start() + 1, match.end()])
                continue
            for candidate_end in range(position + 1, instance.end + 1):
                if grounding.elm_pattern_matches_exact_span(
                    expression, sequence, position + 1, candidate_end
                ):
                    contained.append([position + 1, candidate_end])
                    break
        if contained:
            status = "REGEX_SUBSPAN_WITHIN_SOURCE_INTERVAL"
            exact_span = contained[0]
        elif expression.search(sequence) is not None:
            status = "REGEX_MATCH_ELSEWHERE_IN_COMPLETE_PROTEIN"
            exact_span = None
        else:
            status = "NO_REGEX_MATCH_IN_COMPLETE_PROTEIN"
            exact_span = None
    return {
        "status": status,
        "bounds_verified": True,
        "sequence_length": len(sequence),
        "annotated_sequence": annotated,
        "annotated_sequence_sha256": hashlib.sha256(annotated.encode("ascii")).hexdigest(),
        "exact_pattern_span": exact_span,
    }


def _trait_projection(binding: TraitBinding, elm_class: ElmClass) -> dict[str, Any]:
    category, subdir = ROUTE[elm_class.prefix]
    return {
        "trait_id": binding.trait_id,
        "trait_record_path": binding.relative_path,
        "trait_record_sha256": binding.sha256,
        "elm_class_accession": elm_class.accession,
        "elm_identifier": elm_class.identifier,
        "elm_type": elm_class.prefix,
        "trait_category": category,
        "trait_route": f"sequence/{subdir}/elm",
        "class_regex": elm_class.regex,
        "class_source_line_number": elm_class.source_line_number,
        "class_source_raw_line_sha256": elm_class.source_raw_line_sha256,
    }


def _source_projection(instance: ElmInstance) -> dict[str, Any]:
    return {
        "elm_instance_accession": instance.accession,
        "elm_identifier": instance.elm_identifier,
        "instance_logic": instance.logic,
        "protein_id": instance.protein_id,
        "primary_accession_is_authoritative": True,
        "primary_accession_present_in_aliases": instance.primary_accession in instance.aliases,
        "alias_accessions": list(instance.aliases),
        "protein_name": instance.protein_name,
        "organism_label": instance.organism_label,
        "coordinate_convention": "ONE_BASED_CLOSED_INFERRED_NOT_DECLARED_BY_EXPORT",
        "start": instance.start,
        "end": instance.end,
        "annotated_length": instance.end - instance.start + 1,
        "pubmed_ids": list(instance.pubmed_ids),
        "methods": list(instance.methods),
        "structure_ids": [f"PDB:{item.lower()}" for item in instance.pdb_ids],
        "instance_source_line_number": instance.source_line_number,
        "instance_source_raw_line_sha256": instance.source_raw_line_sha256,
        "instance_source_raw_line_sha256_basis": (
            "RAW_UTF8_PHYSICAL_LINE_INCLUDING_ORIGINAL_LINE_TERMINATOR"
        ),
    }


def _local_registry_match_projection(
    *,
    elm_class: ElmClass,
    instance: ElmInstance,
    reference: Mapping[str, Any],
    sequence_evaluation: Mapping[str, Any],
    source_snapshot_id: str,
) -> dict[str, Any]:
    return {
        "candidate_kind": "ELM_LOCAL_REGISTRY_SEQUENCE_MATCH",
        "trait_id": elm_class.trait_id,
        "protein_id": instance.protein_id,
        "source_trait_id": elm_class.trait_id,
        "mapping_method": "SOURCE_NATIVE_COORDINATES",
        "scope": "LOCALIZED",
        "coordinate_frame": (
            "UNIPROT_ISOFORM" if "-" in instance.primary_accession else "UNIPROT_CANONICAL"
        ),
        "source_interval": {"start": instance.start, "end": instance.end},
        "resolved_interval_sequence": sequence_evaluation["annotated_sequence"],
        "resolved_interval_sequence_sha256": sequence_evaluation["annotated_sequence_sha256"],
        "resolved_interval_sequence_origin": ("LOCAL_PROTEIN_REFERENCE_NOT_ELM_EXPORT"),
        "evidence_source": "ELM",
        "elm_source_snapshot_id": source_snapshot_id,
        "resolved_protein_sequence_sha256": reference["sequence_sha256"],
        "resolved_protein_uniprot_release": reference["uniprot_release"],
        "qualification_status": "CANDIDATE_ONLY",
        "qualification_blockers": sorted(
            {
                MISSING_ACQUISITION_RECEIPT,
                MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT,
            }
        ),
        "source_evidence_id": None,
    }


def _build_occurrence(
    *,
    elm_class: ElmClass,
    instance: ElmInstance,
    trait: TraitBinding,
    selected_example: Mapping[str, Any] | None,
    inline: InlineSequence | None,
    reference: Mapping[str, Any] | None,
    registry_sha256: str,
    source_snapshot_id: str,
) -> dict[str, Any]:
    blockers = [
        MISSING_ACQUISITION_RECEIPT,
        MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT,
    ]
    reference_projection: dict[str, Any]
    reference_evaluation: dict[str, Any] | None = None
    candidate_projection: dict[str, Any] | None = None
    if reference is None:
        reference_projection = {
            "status": "MISSING_EXACT_PROTEIN_REFERENCE",
            "protein_registry_sha256": registry_sha256,
            "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
        }
        if instance.logic == TRUE_POSITIVE:
            blockers.append(MISSING_PROTEIN_REFERENCE)
    else:
        reference_projection = {
            "status": "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT",
            "protein_registry_sha256": registry_sha256,
            "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
            "protein_id": reference["protein_id"],
            "protein_label": reference["protein_label"],
            "taxon_id": reference["taxon_id"],
            "taxon_label": reference["taxon_label"],
            "sequence_length": reference["sequence_length"],
            "sequence_sha256": reference["sequence_sha256"],
            "sequence_version": reference.get("sequence_version"),
            "reviewed": reference["reviewed"],
            "uniprot_release": reference["uniprot_release"],
        }
        reference_evaluation = _pattern_evaluation(elm_class, instance, str(reference["sequence"]))
        if instance.logic == TRUE_POSITIVE:
            if reference_evaluation["status"] == "SOURCE_COORDINATE_OUT_OF_BOUNDS":
                blockers.append(COORDINATE_DRIFT)
            elif reference_evaluation["status"] == "REGEX_SUBSPAN_WITHIN_SOURCE_INTERVAL":
                blockers.append(PATTERN_WIDTH_REVIEW)
            elif reference_evaluation["status"] != "EXACT_REGEX_SPAN_IN_COMPLETE_PROTEIN":
                blockers.append(PATTERN_SEQUENCE_REVIEW)
            if instance.organism_label != reference["taxon_label"]:
                blockers.append(TAXON_LABEL_REVIEW)
            if inline is not None and inline.sequence_sha256 != reference["sequence_sha256"]:
                blockers.append(INLINE_REFERENCE_CONFLICT)
            if set(blockers) == {
                MISSING_ACQUISITION_RECEIPT,
                MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT,
            }:
                candidate_projection = _local_registry_match_projection(
                    elm_class=elm_class,
                    instance=instance,
                    reference=reference,
                    sequence_evaluation=reference_evaluation,
                    source_snapshot_id=source_snapshot_id,
                )
    inline_evaluation = (
        _pattern_evaluation(elm_class, instance, inline.sequence) if inline is not None else None
    )
    if instance.logic != TRUE_POSITIVE:
        blockers.append(NON_TRUE_POSITIVE)
        status = "EXCLUDED_NON_TRUE_POSITIVE_SOURCE_LOGIC"
    elif candidate_projection is not None:
        status = "SEQUENCE_MATCHED_STAGING_ONLY_MISSING_RECEIPTS"
    elif reference is None:
        status = "BLOCKED_MISSING_PROTEIN_REFERENCE"
    else:
        status = "BLOCKED_SEQUENCE_OR_TAXON_REVIEW"
    row = {
        "kind": OCCURRENCE_KIND,
        "schema_version": SCHEMA_VERSION,
        "trait_binding": _trait_projection(trait, elm_class),
        "source_binding": _source_projection(instance),
        "current_example_binding": (
            dict(selected_example)
            if selected_example is not None
            else {
                "selected_by_legacy_first_15_cap": False,
                "current_example_index": None,
                "current_example_trait_id": None,
                "current_example_has_inline_sequence": False,
            }
        ),
        "inline_sequence_diagnostic": (
            {
                "status": "AVAILABLE_UNRELEASED_CURRENT_TRAIT_SEQUENCE",
                "sequence_length": len(inline.sequence),
                "sequence_sha256": inline.sequence_sha256,
                "selected_example_count": inline.selected_example_count,
                "pattern_evaluation": inline_evaluation,
                "qualification_eligible": False,
            }
            if inline is not None
            else {
                "status": "NO_CURRENT_ELM_INLINE_SEQUENCE",
                "qualification_eligible": False,
            }
        ),
        "protein_reference_binding": reference_projection,
        "local_registry_sequence_evaluation": reference_evaluation,
        "grounding_status": status,
        "promotion_blockers": sorted(set(blockers)),
        "local_registry_sequence_match_candidate": candidate_projection,
        "grounding_evidence_emitted": False,
        "source_snapshot_id": source_snapshot_id,
        "network_action_performed": False,
        "write_action_performed": False,
    }
    return _content_address(
        row,
        id_field="occurrence_stage_id",
        prefix="elm-source-occurrence:",
        row_hash_field="occurrence_row_sha256",
    )


def _build_requests(
    instances: Sequence[ElmInstance],
    classes: Mapping[str, ElmClass],
    registry: Mapping[str, Mapping[str, Any]],
    *,
    source_snapshot_id: str,
    expected_uniprot_release: str,
) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, list[ElmInstance]] = defaultdict(list)
    for item in instances:
        if item.logic == TRUE_POSITIVE and item.protein_id not in registry:
            grouped[item.protein_id].append(item)
    requests: list[dict[str, Any]] = []
    for protein_id, rows in sorted(grouped.items()):
        trait_ids = sorted({classes[item.elm_identifier].trait_id for item in rows})
        request = {
            "kind": REQUEST_KIND,
            "schema_version": SCHEMA_VERSION,
            "protein_id": protein_id,
            "primary_accession_is_authoritative": True,
            "coordinate_frame": (
                "UNIPROT_ISOFORM" if "-" in protein_id.split(":", 1)[1] else "UNIPROT_CANONICAL"
            ),
            "source_snapshot_id": source_snapshot_id,
            "expected_uniprot_release": expected_uniprot_release,
            "source_instance_accessions": [item.accession for item in rows],
            "source_instance_count": len(rows),
            "trait_ids": trait_ids,
            "trait_count": len(trait_ids),
            "source_organism_labels": sorted({item.organism_label for item in rows}),
            "maximum_source_coordinate": max(item.end for item in rows),
            "request_reason": MISSING_PROTEIN_REFERENCE,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        requests.append(
            _content_address(
                request,
                id_field="request_id",
                prefix="elm-protein-request:",
                row_hash_field="request_row_sha256",
            )
        )
    return tuple(requests)


def build_stage(
    *,
    classes_path: Path = DEFAULT_CLASSES,
    instances_path: Path = DEFAULT_INSTANCES,
    traits_root: Path = DEFAULT_TRAITS_ROOT,
    protein_registry_path: Path = DEFAULT_PROTEIN_REGISTRY,
    repo_root: Path = REPO_ROOT,
    expected_source_sha256: Mapping[str, str] = SOURCE_PINS,
    expected_uniprot_release: str = EXPECTED_UNIPROT_RELEASE,
) -> StageResult:
    if set(expected_source_sha256) != {"classes", "instances"}:
        raise ElmStageError("expected source pins must name exactly classes and instances")
    repo_binding = _bind_absolute_directory(repo_root, description="repository root")
    try:
        classes_artifact = _capture(
            classes_path,
            description="ELM classes export",
            repo_root=repo_root,
            expected_sha256=expected_source_sha256["classes"],
            bound_root=repo_binding,
        )
        instances_artifact = _capture(
            instances_path,
            description="ELM instances export",
            repo_root=repo_root,
            expected_sha256=expected_source_sha256["instances"],
            bound_root=repo_binding,
        )
        registry_artifact = _capture(
            protein_registry_path,
            description="ProteinReference registry",
            repo_root=repo_root,
            expected_sha256=None,
            bound_root=repo_binding,
        )
        classes_metadata, classes = parse_classes(classes_artifact)
        instances_metadata, instances = parse_instances(instances_artifact, classes)
        if (
            classes_metadata["ELM_Classes_Download_Version"]
            != instances_metadata["ELM_Instance_Download_Version"]
        ):
            raise ElmStageError("ELM class and instance export format versions disagree")
        timestamp_re = re.compile(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+$"
        )
        for field, value in (
            ("ELM_Classes_Download_Date", classes_metadata["ELM_Classes_Download_Date"]),
            (
                "ELM_Instance_Download_Date",
                instances_metadata["ELM_Instance_Download_Date"],
            ),
        ):
            if timestamp_re.fullmatch(value) is None:
                raise ElmStageError(f"invalid ELM export timestamp in {field}: {value!r}")
        source_snapshot = _source_snapshot(
            classes_artifact,
            instances_artifact,
            classes_metadata,
            instances_metadata,
        )
        source_snapshot_id = source_snapshot["source_snapshot_id"]
        traits, selected_examples, inline, trait_artifacts, _ = index_traits(
            traits_root,
            classes,
            instances,
            repo_root=repo_root,
            repo_binding=repo_binding,
        )
        registry = parse_protein_registry(
            registry_artifact, expected_release=expected_uniprot_release
        )
        class_by_identifier = {item.identifier: item for item in classes}
        occurrence_rows = tuple(
            _build_occurrence(
                elm_class=class_by_identifier[item.elm_identifier],
                instance=item,
                trait=traits[class_by_identifier[item.elm_identifier].trait_id],
                selected_example=selected_examples.get(item.accession),
                inline=inline.get(item.protein_id),
                reference=registry.get(item.protein_id),
                registry_sha256=registry_artifact.sha256,
                source_snapshot_id=source_snapshot_id,
            )
            for item in instances
        )
        requests = _build_requests(
            instances,
            class_by_identifier,
            registry,
            source_snapshot_id=source_snapshot_id,
            expected_uniprot_release=expected_uniprot_release,
        )
        status_counts = Counter(row["grounding_status"] for row in occurrence_rows)
        logic_counts = Counter(item.logic for item in instances)
        inline_status_counts = Counter(
            row["inline_sequence_diagnostic"]["pattern_evaluation"]["status"]
            if row["inline_sequence_diagnostic"].get("pattern_evaluation") is not None
            else "NO_INLINE_SEQUENCE"
            for row in occurrence_rows
            if row["source_binding"]["instance_logic"] == TRUE_POSITIVE
        )
        reference_status_counts = Counter(
            row["local_registry_sequence_evaluation"]["status"]
            if row["local_registry_sequence_evaluation"] is not None
            else "NO_EXACT_PROTEIN_REFERENCE"
            for row in occurrence_rows
            if row["source_binding"]["instance_logic"] == TRUE_POSITIVE
        )
        selected_count = len(selected_examples)
        true_positive_count = logic_counts[TRUE_POSITIVE]
        trait_binding_rows = [_trait_projection(traits[item.trait_id], item) for item in classes]
        summary = {
            "kind": SUMMARY_KIND,
            "schema_version": SCHEMA_VERSION,
            "source_snapshot": source_snapshot,
            "protein_registry": _artifact_projection(
                registry_artifact,
                role="LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING",
            ),
            "expected_uniprot_release": expected_uniprot_release,
            "protein_registry_fetch_receipt_verification_status": ("NOT_VERIFIED_BY_THIS_STAGE"),
            "protein_registry_row_count": len(registry),
            "class_count": len(classes),
            "class_type_counts": dict(sorted(Counter(item.prefix for item in classes).items())),
            "instance_count": len(instances),
            "instance_logic_counts": dict(sorted(logic_counts.items())),
            "true_positive_instance_count": true_positive_count,
            "true_positive_unique_protein_count": len(
                {item.protein_id for item in instances if item.logic == TRUE_POSITIVE}
            ),
            "true_positive_isoform_instance_count": sum(
                item.logic == TRUE_POSITIVE and "-" in item.primary_accession for item in instances
            ),
            "trait_count": len(traits),
            "trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(trait_binding_rows)
            ).hexdigest(),
            "legacy_selected_example_count": selected_count,
            "legacy_selected_inline_sequence_count": sum(
                value["current_example_has_inline_sequence"] for value in selected_examples.values()
            ),
            "legacy_cap_omitted_true_positive_count": true_positive_count - selected_count,
            "inline_sequence_unique_protein_count": len(inline),
            "inline_true_positive_pattern_status_counts": dict(
                sorted(inline_status_counts.items())
            ),
            "local_registry_true_positive_pattern_status_counts": dict(
                sorted(reference_status_counts.items())
            ),
            "grounding_status_counts": dict(sorted(status_counts.items())),
            "local_registry_sequence_match_candidate_count": sum(
                row["local_registry_sequence_match_candidate"] is not None
                for row in occurrence_rows
            ),
            "grounding_evidence_emitted_count": 0,
            "missing_protein_reference_request_count": len(requests),
            "occurrence_rows_sha256": hashlib.sha256(_rows_bytes(occurrence_rows)).hexdigest(),
            "protein_request_rows_sha256": hashlib.sha256(_rows_bytes(requests)).hexdigest(),
            "combined_non_summary_rows_sha256": hashlib.sha256(
                _rows_bytes([*occurrence_rows, *requests])
            ).hexdigest(),
            "promotion_blockers": [
                MISSING_ACQUISITION_RECEIPT,
                MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT,
                "ELM_EXPORT_DOES_NOT_DECLARE_DATABASE_RELEASE_OR_LICENSE",
                "ELM_EXPORT_DOES_NOT_CARRY_SOURCE_SEQUENCE_OR_TAXON_ID",
                "REVIEW_REQUIRED_BEFORE_TRAIT_OR_GROUNDING_WRITE",
            ],
            "coordinate_convention_status": (
                "ONE_BASED_CLOSED_INFERRED_FROM_SOURCE_AND_EXISTING_SEEDER_NOT_DECLARED"
            ),
            "qualification_claimed": False,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        _content_address(
            summary,
            id_field="stage_id",
            prefix="elm-source-native-stage:",
            row_hash_field="summary_row_sha256",
        )
        for artifact, description in (
            (classes_artifact, "ELM classes export"),
            (instances_artifact, "ELM instances export"),
            (registry_artifact, "ProteinReference registry"),
        ):
            _assert_unchanged(artifact, description=description, bound_root=repo_binding)
        for artifact in trait_artifacts:
            _assert_unchanged(artifact, description="ELM trait candidate", bound_root=repo_binding)
        _assert_directory_binding(repo_binding, description="repository root")
        return StageResult(occurrence_rows, requests, summary)
    finally:
        os.close(repo_binding.descriptor)


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows = (
        [result.summary]
        if summary_only
        else [
            *result.occurrences,
            *result.protein_requests,
            result.summary,
        ]
    )
    return "".join(canonical_json(row) + "\n" for row in rows)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--instances", type=Path, default=DEFAULT_INSTANCES)
    parser.add_argument("--traits", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument("--protein-registry", type=Path, default=DEFAULT_PROTEIN_REGISTRY)
    parser.add_argument("--expect-uniprot-release", default=EXPECTED_UNIPROT_RELEASE)
    parser.add_argument("--summary-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_stage(
            classes_path=args.classes,
            instances_path=args.instances,
            traits_root=args.traits,
            protein_registry_path=args.protein_registry,
            repo_root=REPO_ROOT,
            expected_uniprot_release=args.expect_uniprot_release,
        )
    except ElmStageError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
