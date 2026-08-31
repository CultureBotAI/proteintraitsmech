#!/usr/bin/env python3
"""Stage SCOPe 2.08 ``! SQ`` UniProt interval comments as canonical JSONL.

SCOPe documents ``dir.com`` as an exclamation-delimited comment file and uses
``! SQ`` for curated mappings from Species nodes to UniProt sequences.  The
SCOP literature further describes these mappings as carrying domain
boundaries.  The edge-case mini-grammar in the historical 2.08 file is not a
formal provider API, however, so every accepted mapping remains
``CANDIDATE_PROTEIN`` with reason
``DIRECT_SCOP_COMMENT_MAPPING_REVIEW_REQUIRED``.

This is a staging-only command.  It has no apply, fetch, or output-file mode:
canonical JSONL is written to stdout, followed by one content-addressed summary
row.  Missing exact ProteinReferences become one deduplicated request per full
UniProt identity.  Malformed/ambiguous SQ clauses and locally provable
out-of-bounds intervals are emitted as content-addressed blocked rows rather
than silently discarded.  ``READY_LOCAL_REFERENCE`` means only that an exact
local protein-registry row is available; it is not a statement that the mapping
is ready for acceptance.

The pinned SCOPe release headers and local file digests are content bindings,
not acquisition receipts.  Every row remains blocked on authentic SCOPe and
verified UniProt-registry receipts, exact px/PDB-chain selection, and a
release-manifested residue-level SIFTS replay.  No GroundingEvidence is emitted.

The repository must remain quiescent while staging. Descriptor-relative
no-follow reads and repeated membership/content checks prevent path escapes and
detect sampled drift, but they do not create an atomic filesystem snapshot
against an uncooperative concurrent writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

import ripgrep_prefilter

SCHEMA_VERSION = 3
CANDIDATE_KIND = "SCOPE_SQ_GROUNDING_CANDIDATE"
BLOCKED_CLAUSE_KIND = "SCOPE_SQ_GROUNDING_BLOCKED_CLAUSE"
BLOCKED_OOB_KIND = "SCOPE_SQ_GROUNDING_BLOCKED_OUT_OF_BOUNDS"
BLOCKED_TAXON_CONFLICT_KIND = "SCOPE_SQ_GROUNDING_BLOCKED_TAXON_CONFLICT"
UNMARKED_SQ_DIAGNOSTIC_KIND = "SCOPE_UNMARKED_SQ_TEXT_DIAGNOSTIC"
REQUEST_KIND = "SCOPE_SQ_PROTEIN_REFERENCE_REQUEST"
TRAIT_BINDING_KIND = "SCOPE_TRAIT_BINDING"
SUMMARY_KIND = "SCOPE_SQ_GROUNDING_STAGE_SUMMARY"

QUALIFICATION_STATUS = "CANDIDATE_PROTEIN"
STAGING_REASON = "DIRECT_SCOP_COMMENT_MAPPING_REVIEW_REQUIRED"
READY_LOCAL_REFERENCE = "READY_LOCAL_REFERENCE"
MISSING_LOCAL_PROTEIN_REFERENCE = "MISSING_LOCAL_PROTEIN_REFERENCE"
BLOCKED_OUT_OF_BOUNDS = "BLOCKED_OUT_OF_BOUNDS"
BLOCKED_SOURCE_REGISTRY_TAXON_CONFLICT = "BLOCKED_SOURCE_REGISTRY_TAXON_CONFLICT"

PROVIDER_NAME = "SCOPe"
PROVIDER_RELEASE = "2.08"
PROVIDER_RELEASE_DATE = "2021-07-29"
PROVIDER_KIND = "SOURCE_DATABASE"
MAPPING_METHOD = "SOURCE_NATIVE_COORDINATES"
SCOPE = "LOCALIZED"
COORDINATE_FRAME = "UNIPROT_CANONICAL"

MISSING_PROVIDER_RECEIPT = "MISSING_SCOPE_PROVIDER_ACQUISITION_RECEIPT"
MISSING_REGISTRY_RECEIPT = "MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT"
MISSING_PX_CHAIN_BINDING = "MISSING_EXACT_SCOP_PX_PDB_CHAIN_BINDING"
MISSING_SIFTS_REPLAY = "MISSING_RELEASE_MANIFESTED_RESIDUE_LEVEL_SIFTS_REPLAY"
MISSING_PROTEIN_REFERENCE = "MISSING_EXPECTED_RELEASE_LOCAL_PROTEIN_REFERENCE"
GLOBAL_PROMOTION_BLOCKERS = (
    MISSING_PROVIDER_RECEIPT,
    MISSING_REGISTRY_RECEIPT,
    MISSING_PX_CHAIN_BINDING,
    MISSING_SIFTS_REPLAY,
    STAGING_REASON,
)
MISSING_RECEIPTS = (MISSING_PROVIDER_RECEIPT, MISSING_REGISTRY_RECEIPT)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMMENTS = REPO_ROOT / "data/raw/scope/dir.com.scope.2.08-stable.txt"
DEFAULT_DESCRIPTIONS = REPO_ROOT / "data/raw/scope/dir.des.scope.2.08-stable.txt"
DEFAULT_HIERARCHY = REPO_ROOT / "data/raw/scope/dir.hie.scope.2.08-stable.txt"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data/traits"
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data/grounding/protein_registry.jsonl"
EXPECTED_UNIPROT_RELEASE = "2026_02"
EXPECTED_PROTEIN_REGISTRY_SHA256 = (
    "d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c"
)

EXPECTED_COMMENTS_SHA256 = "4d68d96829e9c0cdba7b941185eb6debb91dadb3c98e01f9d4d4ca45244382f1"
EXPECTED_DESCRIPTIONS_SHA256 = "41aad433fda2d30eb05fb5a4d03692345e0cce39134a8f7cddb2ec140b5c8af8"
EXPECTED_HIERARCHY_SHA256 = "adf535bde5d8284c84d08cca70dfa45c59ea007a27174c66c48a0484d8ea56de"

SOURCE_PINS = {
    "comments": EXPECTED_COMMENTS_SHA256,
    "descriptions": EXPECTED_DESCRIPTIONS_SHA256,
    "hierarchy": EXPECTED_HIERARCHY_SHA256,
}

# This exact source assertion is an observed provider/registry conflict, not a
# species/strain refinement: SCOPe assigns the interval to Bos taurus while
# UniProt P00734 is the human prothrombin sequence.  Keep it pinned and blocked
# explicitly; do not let it disappear into the broader unresolved taxon-mismatch
# review partition.
OBSERVED_TAXON_CONFLICT = {
    "source_node_sunid": "50533",
    "accession": "P00734",
    "start": 333,
    "end": 622,
    "source_taxon_id": "NCBITaxon:9913",
    "registry_taxon_id": "NCBITaxon:9606",
}

EXPECTED_HEADER_FIRST_LINES = {
    "comments": "# dir.com.scope.txt",
    "descriptions": "# dir.des.scope.txt",
    "hierarchy": "# dir.hie.scope.txt",
}
EXPECTED_FORMAT_VERSIONS = {
    "comments": "1.01",
    "descriptions": "1.02",
    "hierarchy": "1.01",
}
_RELEASE_HEADER_RE = re.compile(
    r"^# SCOPe release (?P<release>[0-9]+\.[0-9]+) "
    r"\((?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})\)  "
    r"\[File format version (?P<format>[0-9]+\.[0-9]+)\]$"
)
_COPYRIGHT_RE = re.compile(
    r"^# Copyright \(c\) 1994-[0-9]{4} the SCOP and SCOPe authors; "
    r"see http://scop\.berkeley\.edu/about$"
)

LEVELS = ("cl", "cf", "sf", "fa", "dm", "sp", "px")
PARENT_LEVEL = {
    "cl": "root",
    "cf": "cl",
    "sf": "cf",
    "fa": "sf",
    "dm": "fa",
    "sp": "dm",
    "px": "sp",
}
SQ_PATH_LEVELS = ("sp", "dm", "fa", "sf", "cf", "cl")
MODELED_LEVELS = frozenset({"cl", "cf", "sf", "fa", "dm"})
LEVEL_TO_ROUTE = {
    "cl": Path("structure/class/scope"),
    "cf": Path("structure/fold/scope"),
    "sf": Path("structure/homologous_superfamily"),
    "fa": Path("structure/fold/scope"),
    "dm": Path("structure/domain/scope"),
}
LEVEL_TO_CATEGORY = {
    "cl": "STRUCT_CLASS",
    "cf": "STRUCT_FOLD",
    "sf": "STRUCT_HOMOLOGOUS_SUPERFAMILY",
    "fa": "STRUCT_FOLD",
    "dm": "STRUCT_DOMAIN",
}

_SUNID_RE = re.compile(r"^(?:0|[1-9][0-9]*)$")
_CANONICAL_ACCESSION_TEXT = (
    r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})"
)
_CANONICAL_ACCESSION_RE = re.compile(rf"^{_CANONICAL_ACCESSION_TEXT}$")
_RANGE_TEXT = r"[1-9][0-9]*-[1-9][0-9]*"
_EXACT_CORE_RE = re.compile(
    rf"^(?P<accession>{_CANONICAL_ACCESSION_TEXT})[ \t]+"
    rf"(?P<start>[1-9][0-9]*)-(?P<end>[1-9][0-9]*)$"
)
_ACCESSION_TOKEN_RE = re.compile(rf"(?<![A-Z0-9]){_CANONICAL_ACCESSION_TEXT}(?![A-Z0-9])")
_RANGE_TOKEN_RE = re.compile(rf"(?<![0-9]){_RANGE_TEXT}(?![0-9])")
_WORD_SQ_RE = re.compile(r"(?<![A-Za-z0-9])SQ(?![A-Za-z0-9])")
_DIRECT_SEMICOLON_CLAIM_RE = re.compile(
    rf"^(?:(?:SQ[ \t]+)?{_CANONICAL_ACCESSION_TEXT}[ \t]+)?{_RANGE_TEXT}(?:[ \t]|$)"
)
_SEQUENCE_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TAXON_RE = re.compile(r"^NCBITaxon:[1-9][0-9]*$")
_SOURCE_TAXON_RE = re.compile(r"\[TaxId:\s*([1-9][0-9]*)\]", re.IGNORECASE)

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


class ScopeSqStageError(ValueError):
    """A source, hierarchy, trait, or registry invariant failed closed."""


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
class BoundDirectory:
    """One descriptor-bound directory used for no-follow relative reads."""

    path: Path
    descriptor: int
    metadata: os.stat_result


@dataclass(frozen=True)
class SourceHeader:
    release: str
    date: str
    format_version: str


@dataclass(frozen=True)
class ScopeNode:
    sunid: str
    level: str
    sccs: str
    sid: str
    description: str
    taxon_id: str | None
    source_line_number: int


@dataclass(frozen=True)
class TraitBinding:
    trait_id: str
    level: str
    category: str
    path: Path
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class RegistryOrigin:
    artifact_path: str
    artifact_sha256: str
    source_line_number: int
    source_row_sha256: str

    def projection(self) -> dict[str, Any]:
        return {
            "artifact_path": self.artifact_path,
            "artifact_sha256": self.artifact_sha256,
            "source_line_number": self.source_line_number,
            "source_row_sha256": self.source_row_sha256,
        }


@dataclass(frozen=True)
class ProteinReference:
    row: Mapping[str, Any]
    origins: tuple[RegistryOrigin, ...]


@dataclass(frozen=True)
class SqAssertion:
    source_node_sunid: str
    line_number: int
    field_index: int
    segment_index: int
    line_sha256: str
    segment_text: str
    segment_sha256: str
    segment_sha256_basis: str
    marker_kind: str
    accession: str | None
    start: int | None
    end: int | None
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class StageResult:
    candidates: tuple[dict[str, Any], ...]
    blocked_clauses: tuple[dict[str, Any], ...]
    blocked_out_of_bounds: tuple[dict[str, Any], ...]
    blocked_taxon_conflicts: tuple[dict[str, Any], ...]
    unmarked_sq_diagnostics: tuple[dict[str, Any], ...]
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
        raise ScopeSqStageError(
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
        raise ScopeSqStageError(
            f"{description} escapes bound root {lexical_root}: {lexical_path}"
        ) from error
    if not relative.parts:
        raise ScopeSqStageError(f"{description} names the bound directory itself: {path}")
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise ScopeSqStageError(f"invalid relative {description} path: {relative}")
    return relative


def _bind_absolute_directory(path: Path, *, description: str) -> BoundDirectory:
    """Bind an absolute directory without following any path-component symlink."""

    directory_flags, _ = _descriptor_safety_flags()
    lexical_path = _lexical_absolute(path)
    if lexical_path.anchor != os.sep:
        raise ScopeSqStageError(f"{description} must have an absolute POSIX path: {path}")
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
        raise ScopeSqStageError(
            f"cannot bind {description} without following symlinks {lexical_path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ScopeSqStageError(f"{description} must be a directory: {lexical_path}")
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
        raise ScopeSqStageError(
            f"cannot bind {description} without following symlinks {path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ScopeSqStageError(f"{description} must be a directory: {path}")
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
            raise ScopeSqStageError(f"{description} binding changed while staging: {binding.path}")
    finally:
        os.close(current.descriptor)


def _read_relative_bytes(
    root: BoundDirectory,
    relative_path: Path,
    *,
    display_path: Path,
    description: str,
) -> bytes:
    """Read one stable regular file without following any path component."""

    if (
        relative_path.is_absolute()
        or not relative_path.parts
        or any(part in {"", ".", ".."} for part in relative_path.parts)
    ):
        raise ScopeSqStageError(f"invalid relative {description} path: {relative_path}")
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
            raise ScopeSqStageError(f"{description} must be a regular file: {display_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
            raise ScopeSqStageError(f"{description} changed while reading: {display_path}")
        return b"".join(chunks)
    except ScopeSqStageError:
        raise
    except OSError as error:
        raise ScopeSqStageError(
            f"cannot open {description} without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


def _read_bytes(
    path: Path,
    *,
    description: str,
    bound_root: BoundDirectory,
) -> bytes:
    relative = _relative_under(path, bound_root.path, description=description)
    return _read_relative_bytes(
        bound_root,
        relative,
        display_path=_lexical_absolute(path),
        description=description,
    )


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return _relative_under(path, repo_root, description="path").as_posix()
    except ScopeSqStageError as error:
        raise ScopeSqStageError(
            f"path escapes repository root {_lexical_absolute(repo_root)}: "
            f"{_lexical_absolute(path)}"
        ) from error


def _capture(
    path: Path,
    *,
    description: str,
    repo_root: Path,
    expected_sha256: str | None = None,
    bound_root: BoundDirectory | None = None,
) -> CapturedArtifact:
    owns_binding = bound_root is None
    binding = bound_root or _bind_absolute_directory(repo_root, description="repository root")
    try:
        relative_path = _repo_relative(path, binding.path)
        raw = _read_bytes(path, description=description, bound_root=binding)
    finally:
        if owns_binding:
            os.close(binding.descriptor)
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ScopeSqStageError(
            f"{description} sha256 mismatch for {path}: expected {expected_sha256}, "
            f"observed {digest}"
        )
    return CapturedArtifact(
        path=_lexical_absolute(path),
        relative_path=relative_path,
        sha256=digest,
        raw=raw,
    )


def _assert_unchanged(
    artifact: CapturedArtifact | ArtifactDigest,
    *,
    description: str,
    bound_root: BoundDirectory,
) -> None:
    observed = hashlib.sha256(
        _read_bytes(artifact.path, description=description, bound_root=bound_root)
    ).hexdigest()
    if observed != artifact.sha256:
        raise ScopeSqStageError(
            f"{description} drifted while staging: {artifact.path}; "
            f"expected {artifact.sha256}, observed {observed}"
        )


def _decode_source(artifact: CapturedArtifact, *, description: str) -> str:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ScopeSqStageError(f"{description} is not strict UTF-8: {error}") from error
    if "\r" in text:
        raise ScopeSqStageError(f"{description} must use LF line endings")
    return text


def _parse_header(artifact: CapturedArtifact, *, kind: str) -> tuple[SourceHeader, list[str]]:
    text = _decode_source(artifact, description=f"SCOPe {kind} artifact")
    lines = text.splitlines()
    if len(lines) < 5:
        raise ScopeSqStageError(f"SCOPe {kind} artifact is shorter than its required header")
    if lines[0] != EXPECTED_HEADER_FIRST_LINES[kind]:
        raise ScopeSqStageError(f"SCOPe {kind} exact first header line mismatch")
    release_match = _RELEASE_HEADER_RE.fullmatch(lines[1])
    if release_match is None:
        raise ScopeSqStageError(f"SCOPe {kind} release header mismatch: {lines[1]!r}")
    if lines[2] != "# http://scop.berkeley.edu/":
        raise ScopeSqStageError(f"SCOPe {kind} provider URL header mismatch")
    if _COPYRIGHT_RE.fullmatch(lines[3]) is None:
        raise ScopeSqStageError(f"SCOPe {kind} copyright header mismatch")
    header = SourceHeader(
        release=release_match.group("release"),
        date=release_match.group("date"),
        format_version=release_match.group("format"),
    )
    if header.release != PROVIDER_RELEASE or header.date != PROVIDER_RELEASE_DATE:
        raise ScopeSqStageError(
            f"SCOPe {kind} must be release {PROVIDER_RELEASE} dated "
            f"{PROVIDER_RELEASE_DATE}; observed {header.release} dated {header.date}"
        )
    if header.format_version != EXPECTED_FORMAT_VERSIONS[kind]:
        raise ScopeSqStageError(
            f"SCOPe {kind} format must be {EXPECTED_FORMAT_VERSIONS[kind]}; "
            f"observed {header.format_version}"
        )
    return header, lines


def parse_descriptions(
    artifact: CapturedArtifact,
) -> tuple[dict[str, ScopeNode], SourceHeader]:
    header, lines = _parse_header(artifact, kind="descriptions")
    nodes: dict[str, ScopeNode] = {}
    for line_number, line in enumerate(lines[4:], 5):
        if not line:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: blank description row"
            )
        if line.startswith("#"):
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: unexpected header/comment row"
            )
        fields = line.split("\t")
        if len(fields) != 5:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: expected 5 description columns, "
                f"got {len(fields)}"
            )
        sunid, level, sccs, sid, description = fields
        if _SUNID_RE.fullmatch(sunid) is None or sunid == "0":
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid positive sunid {sunid!r}"
            )
        if level not in LEVELS:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid SCOPe level {level!r}"
            )
        if not sccs or not sid or not description:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: empty required description field"
            )
        if sunid in nodes:
            raise ScopeSqStageError(f"duplicate SCOPe description node {sunid}")
        source_taxa = _SOURCE_TAXON_RE.findall(description) if level == "sp" else []
        if len(source_taxa) > 1:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: multiple source TaxIds on species node"
            )
        taxon_id = f"NCBITaxon:{source_taxa[0]}" if source_taxa else None
        nodes[sunid] = ScopeNode(sunid, level, sccs, sid, description, taxon_id, line_number)
    if not nodes:
        raise ScopeSqStageError("SCOPe description artifact has no nodes")
    return nodes, header


def parse_hierarchy(
    artifact: CapturedArtifact, nodes: Mapping[str, ScopeNode]
) -> tuple[dict[str, str], SourceHeader]:
    header, lines = _parse_header(artifact, kind="hierarchy")
    parents: dict[str, str] = {}
    declared_children: dict[str, tuple[str, ...]] = {}
    for line_number, line in enumerate(lines[4:], 5):
        fields = line.split("\t")
        if len(fields) != 3:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: expected 3 hierarchy columns, "
                f"got {len(fields)}"
            )
        child, parent, children_text = fields
        if _SUNID_RE.fullmatch(child) is None:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid hierarchy sunid {child!r}"
            )
        if child in parents:
            raise ScopeSqStageError(f"duplicate SCOPe hierarchy node {child}")
        if child == "0":
            if parent != "-":
                raise ScopeSqStageError("SCOPe hierarchy root must have parent '-'")
        elif _SUNID_RE.fullmatch(parent) is None:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid parent sunid {parent!r}"
            )
        children = () if children_text == "-" else tuple(children_text.split(","))
        if any(_SUNID_RE.fullmatch(item) is None or item == "0" for item in children):
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid child-list sunid"
            )
        if len(children) != len(set(children)):
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: duplicate child-list sunid"
            )
        parents[child] = parent
        declared_children[child] = children

    expected_nodes = {"0", *nodes}
    if set(parents) != expected_nodes:
        missing = sorted(expected_nodes - set(parents), key=int)[:10]
        extra = sorted(set(parents) - expected_nodes, key=int)[:10]
        raise ScopeSqStageError(
            f"SCOPe hierarchy/description node-set mismatch; missing={missing}, extra={extra}"
        )
    inverse: dict[str, list[str]] = defaultdict(list)
    for child, parent in parents.items():
        if child == "0":
            continue
        if parent not in parents:
            raise ScopeSqStageError(f"SCOPe hierarchy node {child} has unknown parent {parent}")
        inverse[parent].append(child)
        observed_parent_level = "root" if parent == "0" else nodes[parent].level
        expected_parent_level = PARENT_LEVEL[nodes[child].level]
        if observed_parent_level != expected_parent_level:
            raise ScopeSqStageError(
                f"SCOPe hierarchy level transition for {child}: "
                f"{nodes[child].level}->{observed_parent_level}, expected "
                f"{nodes[child].level}->{expected_parent_level}"
            )
    for parent in parents:
        declared = declared_children[parent]
        actual = tuple(inverse.get(parent, ()))
        if len(declared) != len(actual) or set(declared) != set(actual):
            raise ScopeSqStageError(
                f"SCOPe hierarchy inverse child list mismatch at parent {parent}"
            )

    for start in nodes:
        seen: set[str] = set()
        current = start
        while current != "0":
            if current in seen:
                raise ScopeSqStageError(f"SCOPe hierarchy cycle from node {start} at {current}")
            seen.add(current)
            current = parents[current]
        if len(seen) > len(LEVELS):
            raise ScopeSqStageError(
                f"SCOPe hierarchy path from {start} exceeds the seven-level contract"
            )
    return parents, header


def _hierarchy_path(
    sunid: str, nodes: Mapping[str, ScopeNode], parents: Mapping[str, str]
) -> list[dict[str, Any]]:
    path: list[dict[str, Any]] = []
    current = sunid
    while current != "0":
        node = nodes[current]
        path.append(
            {
                "sunid": node.sunid,
                "trait_id": f"SCOP:{node.sunid}" if node.level in MODELED_LEVELS else None,
                "level": node.level,
                "sccs": node.sccs,
                "taxon_id": node.taxon_id,
            }
        )
        current = parents[current]
    return path


def _split_core_and_annotation(text: str) -> tuple[str, str]:
    delimiter_positions: list[int] = []
    for index, char in enumerate(text):
        if char == ";":
            delimiter_positions.append(index)
            break
        if char == "#" and (index == 0 or text[index - 1].isspace()):
            delimiter_positions.append(index)
            break
    if not delimiter_positions:
        return text.strip(), ""
    index = min(delimiter_positions)
    return text[:index].strip(), text[index:].strip()


def parse_sq_segment(
    segment_text: str,
) -> tuple[str | None, int | None, int | None, tuple[str, ...]]:
    """Parse one trimmed ``!``-delimited SCOPe ``SQ`` comment field.

    SCOPe's ``#`` and ``;`` suffixes are opaque curator annotations.
    They are not searched for incidental accessions or numeric spans.  A suffix
    that *starts* with a second bare range/accession claim is blocked as an
    ambiguous mapping. Literal ``!`` bytes delimit fields before this parser is
    called; surrounding field whitespace is presentation, not grammar.
    """

    exact_field = re.match(r"^SQ(?=[ \t]|$)", segment_text)
    if exact_field is None:
        return None, None, None, ("INVALID_SQ_FIELD",)
    payload = segment_text[exact_field.end() :].strip()
    core, annotation = _split_core_and_annotation(payload)
    match = _EXACT_CORE_RE.fullmatch(core)
    reasons: set[str] = set()
    accession: str | None = None
    start: int | None = None
    end: int | None = None
    if match is not None:
        accession = match.group("accession")
        start = int(match.group("start"))
        end = int(match.group("end"))
        if start > end:
            reasons.add("INVALID_REVERSED_RANGE")
    else:
        accessions = _ACCESSION_TOKEN_RE.findall(core)
        ranges = _RANGE_TOKEN_RE.findall(core)
        if not accessions:
            reasons.add("NO_EXACT_UNIPROT_ACCESSION")
        elif len(accessions) > 1:
            reasons.add("MULTIPLE_UNIPROT_ACCESSIONS")
        else:
            accession = accessions[0]
        if not ranges:
            reasons.add("NO_EXACT_SINGLE_RANGE")
        elif len(ranges) > 1:
            reasons.add("MULTIPLE_RANGES")
        else:
            range_start, range_end = ranges[0].split("-", 1)
            start, end = int(range_start), int(range_end)
            if start > end:
                reasons.add("INVALID_REVERSED_RANGE")
        reasons.add("INVALID_SQ_CLAUSE_SYNTAX")

    if annotation.startswith(";") and _DIRECT_SEMICOLON_CLAIM_RE.match(annotation[1:].lstrip()):
        reasons.add("MULTIPLE_RANGES")
        if _ACCESSION_TOKEN_RE.search(annotation[1:]) is not None:
            reasons.add("MULTIPLE_UNIPROT_ACCESSIONS")

    if reasons:
        return accession, start, end, tuple(sorted(reasons))
    return accession, start, end, ()


def parse_comments(
    artifact: CapturedArtifact,
    nodes: Mapping[str, ScopeNode],
) -> tuple[tuple[SqAssertion, ...], SourceHeader, int]:
    header, _ = _parse_header(artifact, kind="comments")
    assertions: list[SqAssertion] = []
    seen_comment_nodes: set[str] = set()
    total_comment_rows = 0
    raw_lines = artifact.raw.splitlines(keepends=True)
    for line_number, raw_line in enumerate(raw_lines[4:], 5):
        line_bytes = raw_line[:-1] if raw_line.endswith(b"\n") else raw_line
        try:
            line = line_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid UTF-8: {error}"
            ) from error
        if not line:
            raise ScopeSqStageError(f"{artifact.relative_path}:{line_number}: blank comment row")
        fields = line.split("!")
        if len(fields) < 2:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid dir.com row prefix"
            )
        sunid = fields[0].strip(" \t")
        if re.fullmatch(r"[1-9][0-9]*", sunid) is None:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: invalid dir.com sunid column"
            )
        if sunid not in nodes:
            raise ScopeSqStageError(
                f"{artifact.relative_path}:{line_number}: comment has unknown sunid {sunid}"
            )
        if sunid in seen_comment_nodes:
            raise ScopeSqStageError(f"duplicate SCOPe comment node {sunid}")
        seen_comment_nodes.add(sunid)
        total_comment_rows += 1
        line_sha256 = hashlib.sha256(raw_line).hexdigest()
        sq_token_index = 0
        for field_index, raw_field in enumerate(fields[1:], 1):
            field_text = raw_field.strip(" \t")
            if not field_text:
                raise ScopeSqStageError(
                    f"{artifact.relative_path}:{line_number}: empty dir.com comment field"
                )
            word_markers = list(_WORD_SQ_RE.finditer(field_text))
            exact_provider_field = re.match(r"^SQ(?=[ \t]|$)", field_text) is not None
            for word_index, word_marker in enumerate(word_markers):
                sq_token_index += 1
                marker_kind = (
                    "EXACT_PROVIDER_FIELD"
                    if exact_provider_field and word_index == 0 and word_marker.start() == 0
                    else "UNMARKED_SQ_TEXT"
                )
                parsing_view = (
                    field_text
                    if marker_kind == "EXACT_PROVIDER_FIELD"
                    else field_text[word_marker.start() :]
                )
                accession, start, end, reasons = parse_sq_segment(parsing_view)
                if marker_kind == "UNMARKED_SQ_TEXT":
                    reasons = tuple(sorted({*reasons, "UNMARKED_SQ_TEXT_NOT_PROVIDER_FIELD"}))
                node = nodes[sunid]
                if node.level != "sp":
                    reasons = tuple(sorted({*reasons, "SOURCE_NODE_LEVEL_NOT_SP"}))
                assertions.append(
                    SqAssertion(
                        source_node_sunid=sunid,
                        line_number=line_number,
                        field_index=field_index,
                        segment_index=sq_token_index,
                        line_sha256=line_sha256,
                        segment_text=field_text,
                        segment_sha256=hashlib.sha256(field_text.encode("utf-8")).hexdigest(),
                        segment_sha256_basis=(
                            "EXACT_UTF8_BANG_DELIMITED_COMMENT_FIELD_AFTER_ASCII_SPACE_TAB_TRIM"
                        ),
                        marker_kind=marker_kind,
                        accession=accession,
                        start=start,
                        end=end,
                        blocking_reasons=reasons,
                    )
                )
    assertions.sort(
        key=lambda item: (
            item.line_number,
            item.field_index,
            item.segment_index,
            item.marker_kind,
        )
    )
    return tuple(assertions), header, total_comment_rows


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
            raise ScopeSqStageError("trait YAML has an unhashable mapping key") from error
        if duplicate:
            raise ScopeSqStageError(f"trait YAML has duplicate key {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _load_yaml_mapping(raw: bytes, *, path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError, ScopeSqStageError) as error:
        raise ScopeSqStageError(f"cannot parse trait record {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise ScopeSqStageError(f"trait record is not a mapping: {path}")
    return value


_SCOPE_PREFILTER_PATTERNS = ("(?i)SCOPe?:", r"\\", r"\x00")
_SCOPE_PREFILTER_LABEL = "SCOP trait"


def _candidate_scope_trait_paths(traits_root: Path) -> tuple[Path, ...]:
    """Exhaustively prefilter semantic SCOP identity candidates.

    A YAML scalar equal to ``SCOP:*`` either contains the literal ASCII text,
    uses an escape/continued quoted scalar (and therefore a backslash), or is a
    UTF-16/32 byte stream containing NUL.  Every admitted file is parsed before
    namespace filtering, so quoted, flow, escaped, and encoding-shadowed
    duplicate identities cannot hide outside the expected routes.

    Routed through the one guarded prefilter: ripgrep is not a declared
    dependency and CI does not install it (#571), and a fallback that treats an
    unreadable tree as an empty one would silently empty this scan (#573).
    """
    try:
        return ripgrep_prefilter.candidate_paths(
            traits_root, _SCOPE_PREFILTER_PATTERNS, label=_SCOPE_PREFILTER_LABEL
        )
    except ripgrep_prefilter.PrefilterError as error:
        raise ScopeSqStageError(str(error)) from error


def _reject_trait_tree_symlinks(traits_root: Path) -> None:
    """Reject every static symlink in the trait tree before or after indexing."""

    def fail(error: OSError) -> None:
        raise ScopeSqStageError(f"cannot scan trait tree {traits_root}: {error}")

    for directory, names, files in os.walk(
        traits_root, topdown=True, onerror=fail, followlinks=False
    ):
        for name in [*names, *files]:
            path = Path(directory) / name
            try:
                metadata = os.stat(path, follow_symlinks=False)
            except OSError as error:
                raise ScopeSqStageError(
                    f"cannot inspect trait-tree entry {path}: {error}"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                raise ScopeSqStageError(f"symlink below trait directory is forbidden: {path}")


def index_scope_traits(
    traits_root: Path,
    nodes: Mapping[str, ScopeNode],
    parents: Mapping[str, str],
    *,
    repo_root: Path,
    repo_binding: BoundDirectory,
) -> tuple[dict[str, TraitBinding], tuple[ArtifactDigest, ...], tuple[str, ...]]:
    expected = {sunid for sunid, node in nodes.items() if node.level in MODELED_LEVELS}
    traits_binding = _bind_subdirectory(repo_binding, traits_root, description="trait root")
    try:
        _reject_trait_tree_symlinks(traits_binding.path)
        for route in sorted(set(LEVEL_TO_ROUTE.values())):
            route_binding = _bind_subdirectory(
                traits_binding,
                traits_binding.path / route,
                description=f"required SCOPe trait route {route}",
            )
            os.close(route_binding.descriptor)
        paths = _candidate_scope_trait_paths(traits_binding.path)
        if not paths:
            raise ScopeSqStageError("no trait YAML files found in SCOPe routes")
        bindings: dict[str, TraitBinding] = {}
        captured: list[ArtifactDigest] = []
        trait_relative_paths: list[Path] = []
        for reported_path in paths:
            trait_relative = _relative_under(
                reported_path,
                traits_binding.path,
                description="trait prefilter candidate",
            )
            path = traits_binding.path / trait_relative
            raw = _read_relative_bytes(
                traits_binding,
                trait_relative,
                display_path=path,
                description="trait record",
            )
            digest = hashlib.sha256(raw).hexdigest()
            relative = _repo_relative(path, repo_root)
            captured.append(ArtifactDigest(path, relative, digest))
            trait_relative_paths.append(trait_relative)
            record = _load_yaml_mapping(raw, path=path)
            identifier = record.get("identifier")
            if not isinstance(identifier, str):
                continue
            namespace, separator, _ = identifier.partition(":")
            if separator != ":" or namespace.casefold() not in {"scop", "scope"}:
                continue
            if namespace != "SCOP":
                raise ScopeSqStageError(
                    f"{path}: noncanonical SCOP trait namespace spelling {namespace!r}"
                )
            if path.suffix != ".yaml":
                raise ScopeSqStageError(
                    f"{path}: SCOP trait files require the exact lowercase .yaml suffix"
                )
            sunid = identifier.removeprefix("SCOP:")
            node = nodes.get(sunid)
            if node is None or node.level not in MODELED_LEVELS:
                raise ScopeSqStageError(f"{path}: unexpected SCOP trait identity {identifier}")
            expected_directory = _lexical_absolute(traits_binding.path / LEVEL_TO_ROUTE[node.level])
            if _lexical_absolute(path).parent != expected_directory:
                raise ScopeSqStageError(
                    f"{path}: SCOP trait {identifier} is outside its exact {node.level} route"
                )
            contract = {
                "identifier": identifier,
                "definition_source": "SCOPe 2.08-stable",
                "trait_axis": "STRUCTURE",
                "trait_category": LEVEL_TO_CATEGORY[node.level],
                "term_kind": "CLASS",
                "mapping_status": "SEEDED",
                "license": "CC-BY 4.0",
            }
            for field, expected_value in contract.items():
                if record.get(field) != expected_value:
                    raise ScopeSqStageError(
                        f"{path}: trait contract mismatch for {field}: expected "
                        f"{expected_value!r}, observed {record.get(field)!r}"
                    )
            expected_parents = [] if node.level == "cl" else [f"SCOP:{parents[sunid]}"]
            observed_parents = record.get("parent_traits", [])
            if observed_parents != expected_parents:
                raise ScopeSqStageError(
                    f"{path}: exact parent_traits mismatch for {identifier}: expected "
                    f"{expected_parents!r}, observed {observed_parents!r}"
                )
            xrefs = record.get("xrefs")
            expected_xref = f"SCOP:{node.sccs}"
            if not isinstance(xrefs, list) or expected_xref not in xrefs:
                raise ScopeSqStageError(f"{path}: missing exact SCOPe sccs xref {expected_xref}")
            if sunid in bindings:
                raise ScopeSqStageError(
                    f"duplicate SCOP trait identity {identifier}: "
                    f"{bindings[sunid].relative_path} and {relative}"
                )
            bindings[sunid] = TraitBinding(
                trait_id=identifier,
                level=node.level,
                category=LEVEL_TO_CATEGORY[node.level],
                path=path,
                relative_path=relative,
                sha256=digest,
            )
        if set(bindings) != expected:
            missing = sorted(expected - set(bindings), key=int)[:10]
            extra = sorted(set(bindings) - expected, key=int)[:10]
            raise ScopeSqStageError(
                f"SCOPe trait identity set mismatch; missing={missing}, extra={extra}"
            )
        _reject_trait_tree_symlinks(traits_binding.path)
        _assert_directory_binding(traits_binding, description="trait root")
        final_paths = tuple(
            _relative_under(path, traits_binding.path, description="trait prefilter candidate")
            for path in _candidate_scope_trait_paths(traits_binding.path)
        )
        if final_paths != tuple(trait_relative_paths):
            raise ScopeSqStageError("SCOPe trait candidate membership drifted while indexing")
        return bindings, tuple(captured), tuple(item.relative_path for item in captured)
    finally:
        os.close(traits_binding.descriptor)


def _json_object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ScopeSqStageError(f"registry JSON has duplicate key {key!r}")
        value[key] = item
    return value


def _validate_registry_row(row: Mapping[str, Any], *, source: str) -> None:
    if set(row) != REGISTRY_SCHEMA:
        raise ScopeSqStageError(
            f"{source}: exact protein registry schema mismatch; expected "
            f"{sorted(REGISTRY_SCHEMA)!r}, observed {sorted(row)!r}"
        )
    protein_id = row["protein_id"]
    if not isinstance(protein_id, str) or not protein_id.startswith("UniProtKB:"):
        raise ScopeSqStageError(f"{source}: invalid protein_id")
    accession = protein_id.removeprefix("UniProtKB:")
    if _CANONICAL_ACCESSION_RE.fullmatch(accession) is None:
        # Explicit local registries may contain isoforms, but this staging source
        # is canonical-only.  Validate the common registry form without using
        # such a row as a canonical collision.
        isoform = accession.rsplit("-", 1)
        if (
            len(isoform) != 2
            or _CANONICAL_ACCESSION_RE.fullmatch(isoform[0]) is None
            or re.fullmatch(r"[1-9][0-9]*", isoform[1]) is None
        ):
            raise ScopeSqStageError(f"{source}: invalid UniProtKB accession")
    if row["uniprot_release"] != EXPECTED_UNIPROT_RELEASE:
        raise ScopeSqStageError(
            f"{source}: registry row must be exact UniProt release {EXPECTED_UNIPROT_RELEASE}"
        )
    if not isinstance(row["protein_label"], str) or not row["protein_label"]:
        raise ScopeSqStageError(f"{source}: protein_label must be non-empty")
    if not isinstance(row["taxon_label"], str) or not row["taxon_label"]:
        raise ScopeSqStageError(f"{source}: taxon_label must be non-empty")
    if not isinstance(row["reviewed"], bool):
        raise ScopeSqStageError(f"{source}: reviewed must be boolean")
    if not isinstance(row["taxon_id"], str) or _TAXON_RE.fullmatch(row["taxon_id"]) is None:
        raise ScopeSqStageError(f"{source}: taxon_id must be an NCBITaxon CURIE")
    sequence = row["sequence"]
    if not isinstance(sequence, str) or _SEQUENCE_RE.fullmatch(sequence) is None:
        raise ScopeSqStageError(f"{source}: sequence must be an uppercase amino-acid string")
    length = row["sequence_length"]
    if not isinstance(length, int) or isinstance(length, bool) or length < 1:
        raise ScopeSqStageError(f"{source}: sequence_length must be a positive integer")
    if length != len(sequence):
        raise ScopeSqStageError(f"{source}: sequence_length does not match sequence")
    checksum = row["sequence_sha256"]
    if not isinstance(checksum, str) or _SHA256_RE.fullmatch(checksum) is None:
        raise ScopeSqStageError(f"{source}: invalid sequence_sha256")
    if checksum != hashlib.sha256(sequence.encode("ascii")).hexdigest():
        raise ScopeSqStageError(f"{source}: sequence_sha256 does not match sequence")
    version = row["sequence_version"]
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ScopeSqStageError(f"{source}: sequence_version must be a positive integer")


def load_protein_registries(
    paths: Sequence[Path],
    *,
    repo_root: Path,
    repo_binding: BoundDirectory | None = None,
) -> tuple[dict[str, ProteinReference], tuple[CapturedArtifact, ...]]:
    if not paths:
        raise ScopeSqStageError("at least one explicit protein registry is required")
    normalized = [_lexical_absolute(path) for path in paths]
    if len(set(normalized)) != len(paths):
        raise ScopeSqStageError("duplicate explicit protein registry path")
    ordered_paths = [
        path for _, path in sorted((_repo_relative(path, repo_root), path) for path in normalized)
    ]
    owns_binding = repo_binding is None
    binding = repo_binding or _bind_absolute_directory(repo_root, description="repository root")
    artifacts: list[CapturedArtifact] = []
    rows_by_id: dict[str, Mapping[str, Any]] = {}
    origins: dict[str, list[RegistryOrigin]] = defaultdict(list)
    try:
        for path in ordered_paths:
            artifact = _capture(
                path,
                description="protein registry",
                repo_root=binding.path,
                bound_root=binding,
            )
            artifacts.append(artifact)
            if not artifact.raw.endswith(b"\n") or b"\r" in artifact.raw:
                raise ScopeSqStageError(
                    f"{artifact.relative_path}: registry must use LF lines and end with LF"
                )
            seen_in_artifact: set[str] = set()
            for line_number, raw_line in enumerate(artifact.raw.splitlines(), 1):
                if not raw_line:
                    raise ScopeSqStageError(
                        f"{artifact.relative_path}:{line_number}: blank registry row"
                    )
                try:
                    row = json.loads(
                        raw_line.decode("utf-8"), object_pairs_hook=_json_object_no_duplicates
                    )
                except (UnicodeDecodeError, json.JSONDecodeError, ScopeSqStageError) as error:
                    raise ScopeSqStageError(
                        f"{artifact.relative_path}:{line_number}: invalid registry JSON: {error}"
                    ) from error
                if not isinstance(row, Mapping):
                    raise ScopeSqStageError(
                        f"{artifact.relative_path}:{line_number}: registry row is not an object"
                    )
                source = f"{artifact.relative_path}:{line_number}"
                _validate_registry_row(row, source=source)
                if raw_line.decode("utf-8") != canonical_json(row):
                    raise ScopeSqStageError(f"{source}: registry row is not exact canonical JSON")
                protein_id = str(row["protein_id"])
                if protein_id in seen_in_artifact:
                    raise ScopeSqStageError(f"{source}: duplicate protein_id within registry")
                seen_in_artifact.add(protein_id)
                old = rows_by_id.get(protein_id)
                if old is not None and old != row:
                    raise ScopeSqStageError(
                        f"conflicting protein registry collision for {protein_id} across inputs"
                    )
                rows_by_id[protein_id] = dict(row)
                origins[protein_id].append(
                    RegistryOrigin(
                        artifact_path=artifact.relative_path,
                        artifact_sha256=artifact.sha256,
                        source_line_number=line_number,
                        source_row_sha256=hashlib.sha256(raw_line).hexdigest(),
                    )
                )
    finally:
        if owns_binding:
            os.close(binding.descriptor)
    references = {
        protein_id: ProteinReference(
            row=rows_by_id[protein_id],
            origins=tuple(
                sorted(
                    origins[protein_id],
                    key=lambda item: (item.artifact_path, item.source_line_number),
                )
            ),
        )
        for protein_id in sorted(rows_by_id)
    }
    return references, tuple(artifacts)


def _content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> dict[str, Any]:
    row[id_field] = prefix + value_sha256(row)
    row[row_hash_field] = value_sha256(row)
    return row


def _source_assertion_projection(
    assertion: SqAssertion,
    *,
    nodes: Mapping[str, ScopeNode],
    parents: Mapping[str, str],
) -> dict[str, Any]:
    source_node = nodes[assertion.source_node_sunid]
    return {
        "source_node_id": f"SCOP:{assertion.source_node_sunid}",
        "source_node_level": source_node.level,
        "source_node_description": source_node.description,
        "source_species_taxon_id": source_node.taxon_id,
        "source_line_number": assertion.line_number,
        "source_field_index": assertion.field_index,
        "source_segment_index": assertion.segment_index,
        "source_marker_kind": assertion.marker_kind,
        "source_line_sha256": assertion.line_sha256,
        "source_line_sha256_basis": "RAW_UTF8_PHYSICAL_LINE_INCLUDING_TERMINATOR",
        "source_segment": assertion.segment_text,
        "source_segment_sha256": assertion.segment_sha256,
        "source_segment_sha256_basis": assertion.segment_sha256_basis,
        "hierarchy_path": _hierarchy_path(assertion.source_node_sunid, nodes, parents),
    }


def _trait_projection(binding: TraitBinding) -> dict[str, Any]:
    return {
        "trait_id": binding.trait_id,
        "trait_level": binding.level,
        "trait_category": binding.category,
        "record_path": binding.relative_path,
        "record_sha256": binding.sha256,
    }


def _reference_projection(reference: ProteinReference) -> dict[str, Any]:
    row = reference.row
    return {
        "protein_label": row["protein_label"],
        "taxon_id": row["taxon_id"],
        "taxon_label": row["taxon_label"],
        "reviewed": row["reviewed"],
        "sequence_length": row["sequence_length"],
        "sequence_sha256": row["sequence_sha256"],
        "sequence_version": row["sequence_version"],
        "sequence_release": row["uniprot_release"],
        "protein_reference_origins": [item.projection() for item in reference.origins],
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
        "protein_registry_artifact": {
            "path": registry_artifact.relative_path,
            "sha256": registry_artifact.sha256,
            "size_bytes": len(registry_artifact.raw),
        },
        "expected_uniprot_release": expected_uniprot_release,
        "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
    }
    if reference is not None:
        binding.update(
            {
                "protein_id": reference.row["protein_id"],
                **_reference_projection(reference),
            }
        )
    return binding


def _derivation_source_artifacts(
    artifacts: Mapping[str, CapturedArtifact],
) -> list[dict[str, str]]:
    """Bind every source artifact used to parse and project an emitted row."""

    if set(artifacts) != set(SOURCE_PINS):
        raise ScopeSqStageError(
            "row derivation artifacts must contain comments, descriptions, and hierarchy"
        )
    return [
        {
            "kind": kind,
            "path": artifacts[kind].relative_path,
            "sha256": artifacts[kind].sha256,
        }
        for kind in sorted(artifacts)
    ]


def _source_snapshot(artifacts: Mapping[str, CapturedArtifact]) -> dict[str, Any]:
    """Content-address the exact local SCOPe bytes without calling them a receipt."""

    snapshot: dict[str, Any] = {
        "kind": "SCOPE_LOCAL_SOURCE_SNAPSHOT",
        "schema_version": SCHEMA_VERSION,
        "provider_name": PROVIDER_NAME,
        "provider_release_declared_by_source_bytes": PROVIDER_RELEASE,
        "provider_release_date_declared_by_source_bytes": PROVIDER_RELEASE_DATE,
        "source_artifacts": _derivation_source_artifacts(artifacts),
        "repository_declared_download_base": "https://scop.berkeley.edu/downloads/parse/",
        "provider_acquisition_receipt": None,
        "acquisition_status": "LOCAL_PINNED_BYTES_WITHOUT_PROVIDER_ACQUISITION_RECEIPT",
        "network_action_performed": False,
    }
    snapshot["source_snapshot_id"] = "scope-source-snapshot:" + value_sha256(snapshot)
    return snapshot


def _stage_safety_projection(
    source_snapshot_id: str,
    *additional_blockers: str,
) -> dict[str, Any]:
    return {
        "source_snapshot_id": source_snapshot_id,
        "missing_receipts": list(MISSING_RECEIPTS),
        "promotion_blockers": sorted(set([*GLOBAL_PROMOTION_BLOCKERS, *additional_blockers])),
        "grounding_evidence_emitted": False,
        "network_action_performed": False,
        "write_action_performed": False,
    }


def _trait_binding_rows(traits: Mapping[str, TraitBinding]) -> list[dict[str, Any]]:
    return [
        {
            "kind": TRAIT_BINDING_KIND,
            "schema_version": SCHEMA_VERSION,
            **_trait_projection(binding),
        }
        for _, binding in sorted(traits.items(), key=lambda item: int(item[0]))
    ]


def _taxon_comparison_projection(
    source_assertions: Sequence[Mapping[str, Any]],
    reference: ProteinReference | None,
) -> dict[str, Any]:
    source_pairs = sorted(
        {
            (str(item["source_node_id"]), item.get("source_species_taxon_id"))
            for item in source_assertions
        },
        key=lambda item: (item[0], str(item[1] or "")),
    )
    source_taxon_ids = sorted(
        {str(taxon_id) for _, taxon_id in source_pairs if taxon_id is not None}
    )
    projection: dict[str, Any] = {"source_species_taxon_ids": source_taxon_ids}
    if reference is None:
        projection["source_registry_taxon_comparisons"] = []
        projection["source_registry_taxon_review_status"] = "NOT_COMPARED_MISSING_LOCAL_REFERENCE"
        return projection
    registry_taxon = str(reference.row["taxon_id"])
    comparisons = []
    for source_node_id, source_taxon in source_pairs:
        if source_taxon is None:
            status = "SOURCE_TAXON_UNAVAILABLE"
        elif source_taxon == registry_taxon:
            status = "EXACT_TAXON_MATCH"
        else:
            # No NCBI Taxonomy closure is captured by this staging command.
            # A mismatch may be a species/strain refinement or a true anomaly;
            # never infer lineage compatibility from labels.
            status = "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW"
        comparisons.append(
            {
                "source_node_id": source_node_id,
                "source_taxon_id": source_taxon,
                "registry_taxon_id": registry_taxon,
                "comparison_status": status,
            }
        )
    projection["source_registry_taxon_comparisons"] = comparisons
    statuses = {item["comparison_status"] for item in comparisons}
    if "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW" in statuses:
        review_status = "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW"
    elif "SOURCE_TAXON_UNAVAILABLE" in statuses:
        review_status = "SOURCE_TAXON_UNAVAILABLE"
    else:
        review_status = "EXACT_TAXON_MATCH"
    projection["source_registry_taxon_review_status"] = review_status
    return projection


def _blocked_clause_row(
    assertion: SqAssertion,
    *,
    source_snapshot_id: str,
    source_artifact: CapturedArtifact,
    source_artifacts: Mapping[str, CapturedArtifact],
    nodes: Mapping[str, ScopeNode],
    parents: Mapping[str, str],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": BLOCKED_CLAUSE_KIND,
        "candidate_status": "BLOCKED_INVALID_OR_AMBIGUOUS_SQ_CLAUSE",
        "qualification_status": "BLOCKED",
        "staging_reason": STAGING_REASON,
        "blocking_reasons": list(assertion.blocking_reasons),
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "provider_release": PROVIDER_RELEASE,
        "provider_release_date": PROVIDER_RELEASE_DATE,
        "provider_source": source_artifact.relative_path,
        "source_artifact_sha256": source_artifact.sha256,
        "derivation_source_artifacts": _derivation_source_artifacts(source_artifacts),
        "parsed_accession": assertion.accession,
        "parsed_start": assertion.start,
        "parsed_end": assertion.end,
        **_stage_safety_projection(source_snapshot_id, *assertion.blocking_reasons),
        **_source_assertion_projection(assertion, nodes=nodes, parents=parents),
    }
    return _content_address(
        row,
        id_field="blocked_clause_id",
        prefix="scope-sq-blocked-clause:",
        row_hash_field="blocked_clause_row_sha256",
    )


def _unmarked_sq_diagnostic_row(
    assertion: SqAssertion,
    *,
    source_snapshot_id: str,
    source_artifact: CapturedArtifact,
    source_artifacts: Mapping[str, CapturedArtifact],
    nodes: Mapping[str, ScopeNode],
    parents: Mapping[str, str],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": UNMARKED_SQ_DIAGNOSTIC_KIND,
        "diagnostic_status": "NOT_A_PROVIDER_SQ_FIELD",
        "qualification_status": "BLOCKED",
        "staging_reason": STAGING_REASON,
        "diagnostic_reasons": list(assertion.blocking_reasons),
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "provider_release": PROVIDER_RELEASE,
        "provider_release_date": PROVIDER_RELEASE_DATE,
        "provider_source": source_artifact.relative_path,
        "source_artifact_sha256": source_artifact.sha256,
        "derivation_source_artifacts": _derivation_source_artifacts(source_artifacts),
        "parsed_accession": assertion.accession,
        "parsed_start": assertion.start,
        "parsed_end": assertion.end,
        **_stage_safety_projection(source_snapshot_id, *assertion.blocking_reasons),
        **_source_assertion_projection(assertion, nodes=nodes, parents=parents),
    }
    return _content_address(
        row,
        id_field="diagnostic_id",
        prefix="scope-unmarked-sq-diagnostic:",
        row_hash_field="diagnostic_row_sha256",
    )


def _blocked_oob_row(
    assertion: SqAssertion,
    *,
    source_snapshot_id: str,
    source_artifact: CapturedArtifact,
    source_artifacts: Mapping[str, CapturedArtifact],
    nodes: Mapping[str, ScopeNode],
    parents: Mapping[str, str],
    traits: Mapping[str, TraitBinding],
    reference: ProteinReference,
) -> dict[str, Any]:
    hierarchy = _hierarchy_path(assertion.source_node_sunid, nodes, parents)
    affected = [_trait_projection(traits[item["sunid"]]) for item in hierarchy[1:]]
    source_projection = _source_assertion_projection(assertion, nodes=nodes, parents=parents)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": BLOCKED_OOB_KIND,
        "candidate_status": BLOCKED_OUT_OF_BOUNDS,
        "qualification_status": QUALIFICATION_STATUS,
        "staging_reason": STAGING_REASON,
        "blocking_reasons": ["INTERVAL_END_EXCEEDS_LOCAL_SEQUENCE_LENGTH"],
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "provider_release": PROVIDER_RELEASE,
        "provider_release_date": PROVIDER_RELEASE_DATE,
        "provider_source": source_artifact.relative_path,
        "source_artifact_sha256": source_artifact.sha256,
        "derivation_source_artifacts": _derivation_source_artifacts(source_artifacts),
        "protein_id": f"UniProtKB:{assertion.accession}",
        "scope": SCOPE,
        "coordinate_frame": COORDINATE_FRAME,
        "intervals": [{"start": assertion.start, "end": assertion.end}],
        "mapping_method": MAPPING_METHOD,
        "qualification_mapping_method_required": "SIFTS_RESIDUE_MAPPING",
        "affected_trait_projections": affected,
        **_stage_safety_projection(
            source_snapshot_id, "INTERVAL_END_EXCEEDS_LOCAL_SEQUENCE_LENGTH"
        ),
        **_reference_projection(reference),
        **_taxon_comparison_projection([source_projection], reference),
        **source_projection,
    }
    return _content_address(
        row,
        id_field="blocked_out_of_bounds_id",
        prefix="scope-sq-blocked-out-of-bounds:",
        row_hash_field="blocked_out_of_bounds_row_sha256",
    )


def _is_observed_taxon_conflict(
    assertion: SqAssertion,
    *,
    nodes: Mapping[str, ScopeNode],
    reference: ProteinReference | None,
) -> bool:
    if reference is None:
        return False
    observed = {
        "source_node_sunid": assertion.source_node_sunid,
        "accession": assertion.accession,
        "start": assertion.start,
        "end": assertion.end,
        "source_taxon_id": nodes[assertion.source_node_sunid].taxon_id,
        "registry_taxon_id": reference.row["taxon_id"],
    }
    return observed == OBSERVED_TAXON_CONFLICT


def _blocked_taxon_conflict_row(
    assertion: SqAssertion,
    *,
    source_snapshot_id: str,
    source_artifact: CapturedArtifact,
    source_artifacts: Mapping[str, CapturedArtifact],
    nodes: Mapping[str, ScopeNode],
    parents: Mapping[str, str],
    traits: Mapping[str, TraitBinding],
    reference: ProteinReference,
) -> dict[str, Any]:
    hierarchy = _hierarchy_path(assertion.source_node_sunid, nodes, parents)
    affected = [_trait_projection(traits[item["sunid"]]) for item in hierarchy[1:]]
    source_projection = _source_assertion_projection(assertion, nodes=nodes, parents=parents)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": BLOCKED_TAXON_CONFLICT_KIND,
        "candidate_status": BLOCKED_SOURCE_REGISTRY_TAXON_CONFLICT,
        "qualification_status": QUALIFICATION_STATUS,
        "staging_reason": STAGING_REASON,
        "blocking_reasons": ["OBSERVED_SOURCE_REGISTRY_TAXON_CONFLICT"],
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "provider_release": PROVIDER_RELEASE,
        "provider_release_date": PROVIDER_RELEASE_DATE,
        "provider_source": source_artifact.relative_path,
        "source_artifact_sha256": source_artifact.sha256,
        "derivation_source_artifacts": _derivation_source_artifacts(source_artifacts),
        "protein_id": f"UniProtKB:{assertion.accession}",
        "scope": SCOPE,
        "coordinate_frame": COORDINATE_FRAME,
        "intervals": [{"start": assertion.start, "end": assertion.end}],
        "mapping_method": MAPPING_METHOD,
        "qualification_mapping_method_required": "SIFTS_RESIDUE_MAPPING",
        "affected_trait_projections": affected,
        **_stage_safety_projection(source_snapshot_id, "OBSERVED_SOURCE_REGISTRY_TAXON_CONFLICT"),
        **_reference_projection(reference),
        **_taxon_comparison_projection([source_projection], reference),
        **source_projection,
    }
    return _content_address(
        row,
        id_field="blocked_taxon_conflict_id",
        prefix="scope-sq-blocked-taxon-conflict:",
        row_hash_field="blocked_taxon_conflict_row_sha256",
    )


def _candidate_row(
    *,
    source_snapshot_id: str,
    registry_artifact: CapturedArtifact,
    expected_uniprot_release: str,
    trait: TraitBinding,
    accession: str,
    start: int,
    end: int,
    source_assertions: Sequence[dict[str, Any]],
    source_artifact: CapturedArtifact,
    source_artifacts: Mapping[str, CapturedArtifact],
    reference: ProteinReference | None,
) -> dict[str, Any]:
    status = READY_LOCAL_REFERENCE if reference is not None else MISSING_LOCAL_PROTEIN_REFERENCE
    direct_source_traits = sorted(
        {
            item["hierarchy_path"][1]["trait_id"]
            for item in source_assertions
            if len(item["hierarchy_path"]) > 1
        }
    )
    taxon_projection = _taxon_comparison_projection(source_assertions, reference)
    candidate_blockers: list[str] = []
    if reference is None:
        candidate_blockers.append(MISSING_PROTEIN_REFERENCE)
    taxon_review_status = taxon_projection["source_registry_taxon_review_status"]
    if taxon_review_status in {
        "SOURCE_TAXON_UNAVAILABLE",
        "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW",
    }:
        candidate_blockers.append(str(taxon_review_status))
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": CANDIDATE_KIND,
        "candidate_status": status,
        "candidate_status_basis": (
            "LOCAL_PROTEIN_REGISTRY_AVAILABILITY_ONLY_NOT_MAPPING_REVIEW_READINESS"
        ),
        "qualification_status": QUALIFICATION_STATUS,
        "staging_reason": STAGING_REASON,
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "provider_release": PROVIDER_RELEASE,
        "provider_release_date": PROVIDER_RELEASE_DATE,
        "provider_source": source_artifact.relative_path,
        "source_artifact_sha256": source_artifact.sha256,
        "derivation_source_artifacts": _derivation_source_artifacts(source_artifacts),
        **_trait_projection(trait),
        "source_trait_ids": direct_source_traits,
        "protein_id": f"UniProtKB:{accession}",
        "scope": SCOPE,
        "coordinate_frame": COORDINATE_FRAME,
        "intervals": [{"start": start, "end": end}],
        "mapping_method": MAPPING_METHOD,
        "qualification_mapping_method_required": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": PROVIDER_NAME,
        "source_release": PROVIDER_RELEASE,
        "source_assertions": list(source_assertions),
        "protein_reference_binding": _reference_binding(
            reference,
            registry_artifact=registry_artifact,
            expected_uniprot_release=expected_uniprot_release,
        ),
        **_stage_safety_projection(source_snapshot_id, *candidate_blockers),
        **taxon_projection,
    }
    if reference is not None:
        row.update(_reference_projection(reference))
    return _content_address(
        row,
        id_field="candidate_id",
        prefix="scope-sq-grounding-candidate:",
        row_hash_field="candidate_row_sha256",
    )


def _rows_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")


def _request_assertion_binding(
    candidate: Mapping[str, Any], assertion: Mapping[str, Any]
) -> dict[str, Any]:
    interval = candidate["intervals"][0]
    return {
        "source_node_id": assertion["source_node_id"],
        "source_line_number": assertion["source_line_number"],
        "source_field_index": assertion["source_field_index"],
        "source_segment_index": assertion["source_segment_index"],
        "source_line_sha256": assertion["source_line_sha256"],
        "source_segment_sha256": assertion["source_segment_sha256"],
        "start": interval["start"],
        "end": interval["end"],
    }


def _build_requests(
    candidates: Sequence[Mapping[str, Any]],
    *,
    source_snapshot_id: str,
    source_artifacts: Mapping[str, CapturedArtifact],
    registry_artifact: CapturedArtifact,
    expected_uniprot_release: str,
) -> tuple[dict[str, Any], ...]:
    """Emit one deterministic ProteinReference request per missing full identity."""

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if candidate["candidate_status"] == MISSING_LOCAL_PROTEIN_REFERENCE:
            grouped[str(candidate["protein_id"])].append(candidate)

    requests: list[dict[str, Any]] = []
    for protein_id, projections in sorted(grouped.items()):
        assertion_bindings_by_json: dict[str, dict[str, Any]] = {}
        for candidate in projections:
            for assertion in candidate["source_assertions"]:
                binding = _request_assertion_binding(candidate, assertion)
                assertion_bindings_by_json[canonical_json(binding)] = binding
        assertion_bindings = [
            assertion_bindings_by_json[key] for key in sorted(assertion_bindings_by_json)
        ]
        trait_ids = sorted({str(item["trait_id"]) for item in projections})
        direct_source_trait_ids = sorted(
            {
                str(source_trait_id)
                for item in projections
                for source_trait_id in item["source_trait_ids"]
            }
        )
        source_taxon_ids = sorted(
            {
                str(source_taxon_id)
                for item in projections
                for source_taxon_id in item["source_species_taxon_ids"]
            }
        )
        row: dict[str, Any] = {
            "kind": REQUEST_KIND,
            "schema_version": SCHEMA_VERSION,
            "protein_id": protein_id,
            "primary_accession_is_authoritative": True,
            "coordinate_frame": COORDINATE_FRAME,
            "expected_uniprot_release": expected_uniprot_release,
            "request_reason": MISSING_PROTEIN_REFERENCE,
            "protein_reference_binding": _reference_binding(
                None,
                registry_artifact=registry_artifact,
                expected_uniprot_release=expected_uniprot_release,
            ),
            "source_artifacts": _derivation_source_artifacts(source_artifacts),
            "source_candidate_ids": sorted(str(item["candidate_id"]) for item in projections),
            "source_candidate_count": len(projections),
            "scope_trait_ids": trait_ids,
            "trait_count": len(trait_ids),
            "direct_source_trait_ids": direct_source_trait_ids,
            "direct_source_trait_count": len(direct_source_trait_ids),
            "source_node_ids": sorted({str(item["source_node_id"]) for item in assertion_bindings}),
            "source_taxon_ids": source_taxon_ids,
            "source_assertion_bindings": assertion_bindings,
            "source_assertion_count": len(assertion_bindings),
            "maximum_source_coordinate": max(
                int(item["intervals"][0]["end"]) for item in projections
            ),
            **_stage_safety_projection(source_snapshot_id, MISSING_PROTEIN_REFERENCE),
        }
        requests.append(
            _content_address(
                row,
                id_field="request_id",
                prefix="scope-sq-protein-request:",
                row_hash_field="request_row_sha256",
            )
        )
    return tuple(requests)


def build_stage(
    *,
    comments_path: Path,
    descriptions_path: Path,
    hierarchy_path: Path,
    traits_root: Path,
    protein_registry_path: Path,
    repo_root: Path = REPO_ROOT,
    expected_source_sha256: Mapping[str, str] = SOURCE_PINS,
    expected_protein_registry_sha256: str = EXPECTED_PROTEIN_REGISTRY_SHA256,
    expected_uniprot_release: str = EXPECTED_UNIPROT_RELEASE,
) -> StageResult:
    repo_binding = _bind_absolute_directory(repo_root, description="repository root")
    try:
        return _build_stage_bound(
            comments_path=comments_path,
            descriptions_path=descriptions_path,
            hierarchy_path=hierarchy_path,
            traits_root=traits_root,
            protein_registry_path=protein_registry_path,
            repo_root=repo_binding.path,
            repo_binding=repo_binding,
            expected_source_sha256=expected_source_sha256,
            expected_protein_registry_sha256=expected_protein_registry_sha256,
            expected_uniprot_release=expected_uniprot_release,
        )
    finally:
        os.close(repo_binding.descriptor)


def _build_stage_bound(
    *,
    comments_path: Path,
    descriptions_path: Path,
    hierarchy_path: Path,
    traits_root: Path,
    protein_registry_path: Path,
    repo_root: Path,
    repo_binding: BoundDirectory,
    expected_source_sha256: Mapping[str, str],
    expected_protein_registry_sha256: str,
    expected_uniprot_release: str,
) -> StageResult:
    if set(expected_source_sha256) != set(SOURCE_PINS):
        raise ScopeSqStageError(
            "expected_source_sha256 must contain exactly comments, descriptions, and hierarchy"
        )
    for source_kind, digest in expected_source_sha256.items():
        if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
            raise ScopeSqStageError(f"invalid pinned sha256 for SCOPe {source_kind}")
    if _SHA256_RE.fullmatch(expected_protein_registry_sha256) is None:
        raise ScopeSqStageError("invalid pinned sha256 for the ProteinReference registry")
    if expected_uniprot_release != EXPECTED_UNIPROT_RELEASE:
        raise ScopeSqStageError(
            f"expected UniProt release must be exactly {EXPECTED_UNIPROT_RELEASE}"
        )
    source_artifacts = {
        "comments": _capture(
            comments_path,
            description="SCOPe comments",
            repo_root=repo_root,
            expected_sha256=expected_source_sha256.get("comments"),
            bound_root=repo_binding,
        ),
        "descriptions": _capture(
            descriptions_path,
            description="SCOPe descriptions",
            repo_root=repo_root,
            expected_sha256=expected_source_sha256.get("descriptions"),
            bound_root=repo_binding,
        ),
        "hierarchy": _capture(
            hierarchy_path,
            description="SCOPe hierarchy",
            repo_root=repo_root,
            expected_sha256=expected_source_sha256.get("hierarchy"),
            bound_root=repo_binding,
        ),
    }
    source_snapshot = _source_snapshot(source_artifacts)
    nodes, des_header = parse_descriptions(source_artifacts["descriptions"])
    parents, hie_header = parse_hierarchy(source_artifacts["hierarchy"], nodes)
    assertions, com_header, comment_row_count = parse_comments(source_artifacts["comments"], nodes)
    if len({(item.release, item.date) for item in (des_header, hie_header, com_header)}) != 1:
        raise ScopeSqStageError("SCOPe source release/date headers disagree")

    traits, trait_artifacts, trait_path_snapshot = index_scope_traits(
        traits_root,
        nodes,
        parents,
        repo_root=repo_root,
        repo_binding=repo_binding,
    )
    references, registry_artifacts = load_protein_registries(
        [protein_registry_path], repo_root=repo_root, repo_binding=repo_binding
    )
    if len(registry_artifacts) != 1:
        raise ScopeSqStageError("SCOPe v3 requires exactly one ProteinReference registry")
    registry_artifact = registry_artifacts[0]
    if registry_artifact.sha256 != expected_protein_registry_sha256:
        raise ScopeSqStageError(
            f"{registry_artifact.relative_path}: sha256 mismatch; expected "
            f"{expected_protein_registry_sha256}, observed {registry_artifact.sha256}"
        )

    blocked_clauses: list[dict[str, Any]] = []
    blocked_oob: list[dict[str, Any]] = []
    blocked_taxon_conflicts: list[dict[str, Any]] = []
    unmarked_sq_diagnostics: list[dict[str, Any]] = []
    admitted: list[SqAssertion] = []
    for assertion in assertions:
        if assertion.marker_kind == "UNMARKED_SQ_TEXT":
            unmarked_sq_diagnostics.append(
                _unmarked_sq_diagnostic_row(
                    assertion,
                    source_snapshot_id=source_snapshot["source_snapshot_id"],
                    source_artifact=source_artifacts["comments"],
                    source_artifacts=source_artifacts,
                    nodes=nodes,
                    parents=parents,
                )
            )
            continue
        if assertion.blocking_reasons:
            blocked_clauses.append(
                _blocked_clause_row(
                    assertion,
                    source_snapshot_id=source_snapshot["source_snapshot_id"],
                    source_artifact=source_artifacts["comments"],
                    source_artifacts=source_artifacts,
                    nodes=nodes,
                    parents=parents,
                )
            )
            continue
        path = _hierarchy_path(assertion.source_node_sunid, nodes, parents)
        if tuple(item["level"] for item in path) != SQ_PATH_LEVELS:
            raise ScopeSqStageError(
                f"admitted SQ node {assertion.source_node_sunid} does not have exact "
                "sp->dm->fa->sf->cf->cl hierarchy"
            )
        admitted.append(assertion)

    prospective: dict[tuple[str, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    admitted_non_oob: list[SqAssertion] = []
    for assertion in admitted:
        assert assertion.accession is not None
        assert assertion.start is not None
        assert assertion.end is not None
        protein_id = f"UniProtKB:{assertion.accession}"
        reference = references.get(protein_id)
        path = _hierarchy_path(assertion.source_node_sunid, nodes, parents)
        source_projection = _source_assertion_projection(assertion, nodes=nodes, parents=parents)
        for item in path[1:]:
            prospective[
                (item["sunid"], assertion.accession, assertion.start, assertion.end)
            ].append(source_projection)
        if _is_observed_taxon_conflict(assertion, nodes=nodes, reference=reference):
            assert reference is not None
            blocked_taxon_conflicts.append(
                _blocked_taxon_conflict_row(
                    assertion,
                    source_snapshot_id=source_snapshot["source_snapshot_id"],
                    source_artifact=source_artifacts["comments"],
                    source_artifacts=source_artifacts,
                    nodes=nodes,
                    parents=parents,
                    traits=traits,
                    reference=reference,
                )
            )
        elif reference is not None and assertion.end > int(reference.row["sequence_length"]):
            blocked_oob.append(
                _blocked_oob_row(
                    assertion,
                    source_snapshot_id=source_snapshot["source_snapshot_id"],
                    source_artifact=source_artifacts["comments"],
                    source_artifacts=source_artifacts,
                    nodes=nodes,
                    parents=parents,
                    traits=traits,
                    reference=reference,
                )
            )
        else:
            admitted_non_oob.append(assertion)

    grouped: dict[tuple[str, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for assertion in admitted_non_oob:
        assert assertion.accession is not None
        assert assertion.start is not None
        assert assertion.end is not None
        path = _hierarchy_path(assertion.source_node_sunid, nodes, parents)
        source_projection = _source_assertion_projection(assertion, nodes=nodes, parents=parents)
        for item in path[1:]:
            grouped[(item["sunid"], assertion.accession, assertion.start, assertion.end)].append(
                source_projection
            )

    candidates: list[dict[str, Any]] = []
    for (sunid, accession, start, end), provenance in sorted(
        grouped.items(), key=lambda item: (int(item[0][0]), item[0][1], item[0][2], item[0][3])
    ):
        provenance.sort(
            key=lambda item: (
                item["source_line_number"],
                item["source_field_index"],
                item["source_segment_index"],
                item["source_segment_sha256"],
            )
        )
        candidates.append(
            _candidate_row(
                source_snapshot_id=source_snapshot["source_snapshot_id"],
                registry_artifact=registry_artifact,
                expected_uniprot_release=expected_uniprot_release,
                trait=traits[sunid],
                accession=accession,
                start=start,
                end=end,
                source_assertions=provenance,
                source_artifact=source_artifacts["comments"],
                source_artifacts=source_artifacts,
                reference=references.get(f"UniProtKB:{accession}"),
            )
        )

    candidates.sort(
        key=lambda row: (
            row["trait_id"],
            row["protein_id"],
            row["intervals"][0]["start"],
            row["intervals"][0]["end"],
        )
    )
    blocked_clauses.sort(
        key=lambda row: (
            row["source_line_number"],
            row["source_field_index"],
            row["source_segment_index"],
            row["blocked_clause_id"],
        )
    )
    blocked_oob.sort(
        key=lambda row: (
            row["source_line_number"],
            row["source_field_index"],
            row["source_segment_index"],
            row["blocked_out_of_bounds_id"],
        )
    )
    blocked_taxon_conflicts.sort(
        key=lambda row: (
            row["source_line_number"],
            row["source_field_index"],
            row["source_segment_index"],
            row["blocked_taxon_conflict_id"],
        )
    )
    unmarked_sq_diagnostics.sort(
        key=lambda row: (
            row["source_line_number"],
            row["source_field_index"],
            row["source_segment_index"],
            row["diagnostic_id"],
        )
    )
    protein_requests = _build_requests(
        candidates,
        source_snapshot_id=source_snapshot["source_snapshot_id"],
        source_artifacts=source_artifacts,
        registry_artifact=registry_artifact,
        expected_uniprot_release=expected_uniprot_release,
    )

    # Final content and directory-membership checks close capture/parse drift.
    for artifact in source_artifacts.values():
        _assert_unchanged(artifact, description="SCOPe source artifact", bound_root=repo_binding)
    for artifact in registry_artifacts:
        _assert_unchanged(
            artifact, description="protein registry artifact", bound_root=repo_binding
        )
    for artifact in trait_artifacts:
        _assert_unchanged(artifact, description="trait record", bound_root=repo_binding)
    _reject_trait_tree_symlinks(_lexical_absolute(traits_root))
    final_trait_paths = tuple(
        _repo_relative(path, repo_root)
        for path in _candidate_scope_trait_paths(_lexical_absolute(traits_root))
    )
    if final_trait_paths != trait_path_snapshot:
        raise ScopeSqStageError("SCOPe trait route membership drifted while staging")
    _assert_directory_binding(repo_binding, description="repository root")

    candidate_bytes = _rows_bytes(candidates)
    blocked_clause_bytes = _rows_bytes(blocked_clauses)
    blocked_oob_bytes = _rows_bytes(blocked_oob)
    blocked_taxon_conflict_bytes = _rows_bytes(blocked_taxon_conflicts)
    unmarked_sq_diagnostic_bytes = _rows_bytes(unmarked_sq_diagnostics)
    protein_request_bytes = _rows_bytes(protein_requests)
    trait_binding_rows = _trait_binding_rows(traits)
    admitted_occurrences = {
        (
            item.source_node_sunid,
            item.accession,
            item.start,
            item.end,
        )
        for item in admitted
    }
    ready = [row for row in candidates if row["candidate_status"] == READY_LOCAL_REFERENCE]
    missing = [
        row for row in candidates if row["candidate_status"] == MISSING_LOCAL_PROTEIN_REFERENCE
    ]
    ready_trait_ids = {row["trait_id"] for row in ready}
    ready_proteins = {row["protein_id"] for row in ready}
    oob_trait_ids = {
        item["trait_id"] for row in blocked_oob for item in row["affected_trait_projections"]
    }
    oob_proteins = {row["protein_id"] for row in blocked_oob}
    conflict_trait_ids = {
        item["trait_id"]
        for row in blocked_taxon_conflicts
        for item in row["affected_trait_projections"]
    }
    conflict_proteins = {row["protein_id"] for row in blocked_taxon_conflicts}
    local_registry_projection_keys = {
        key for key in prospective if f"UniProtKB:{key[1]}" in references
    }
    taxon_mismatch_pair_candidate_ids: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in ready:
        for comparison in row["source_registry_taxon_comparisons"]:
            if (
                comparison["comparison_status"]
                != "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW"
            ):
                continue
            pair = (
                str(comparison["source_taxon_id"]),
                str(comparison["registry_taxon_id"]),
            )
            taxon_mismatch_pair_candidate_ids[pair].add(str(row["candidate_id"]))
    source_rows = [
        {
            "kind": kind,
            "path": artifact.relative_path,
            "sha256": artifact.sha256,
            "format_version": {
                "comments": com_header,
                "descriptions": des_header,
                "hierarchy": hie_header,
            }[kind].format_version,
        }
        for kind, artifact in sorted(source_artifacts.items())
    ]
    registry_row = {
        "path": registry_artifact.relative_path,
        "sha256": registry_artifact.sha256,
        "size_bytes": len(registry_artifact.raw),
    }
    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": SUMMARY_KIND,
        "stage_status": STAGING_REASON,
        "qualification_claimed": False,
        "candidate_qualification_status": QUALIFICATION_STATUS,
        "ready_local_reference_semantics": (
            "LOCAL_PROTEIN_REGISTRY_AVAILABILITY_ONLY_NOT_MAPPING_REVIEW_READINESS"
        ),
        "provider_name": PROVIDER_NAME,
        "provider_release": PROVIDER_RELEASE,
        "provider_release_date": PROVIDER_RELEASE_DATE,
        "provider_kind": PROVIDER_KIND,
        "source_snapshot": source_snapshot,
        "source_snapshot_id": source_snapshot["source_snapshot_id"],
        "source_artifacts": source_rows,
        "protein_registry_artifact": registry_row,
        "protein_registry_expected_sha256": expected_protein_registry_sha256,
        "protein_registry_sha256_matches_stage_pin": True,
        "protein_registry_fetch_receipt_verification_status": ("NOT_VERIFIED_BY_THIS_STAGE"),
        "provider_acquisition_receipt_verification_status": ("MISSING_NOT_VERIFIED_BY_THIS_STAGE"),
        "missing_receipts": list(MISSING_RECEIPTS),
        "promotion_blockers": sorted(GLOBAL_PROMOTION_BLOCKERS),
        "protein_registry_artifact_count": 1,
        "protein_registry_unique_row_count": len(references),
        "scope_node_count": len(nodes),
        "scope_comment_row_count": comment_row_count,
        "scope_trait_record_count": len(traits),
        "trait_binding_count": len(trait_binding_rows),
        "trait_binding_rows_sha256": hashlib.sha256(_rows_bytes(trait_binding_rows)).hexdigest(),
        "scope_trait_level_counts": dict(
            sorted(Counter(binding.level for binding in traits.values()).items())
        ),
        "exact_sq_clause_count": sum(
            item.marker_kind == "EXACT_PROVIDER_FIELD" for item in assertions
        ),
        "total_sq_clause_count": sum(
            item.marker_kind == "EXACT_PROVIDER_FIELD" for item in assertions
        ),
        "unmarked_sq_text_count": len(unmarked_sq_diagnostics),
        "total_sq_like_token_count": len(assertions),
        "admitted_sq_clause_count": len(admitted),
        "unique_admitted_occurrence_count": len(admitted_occurrences),
        "blocked_sq_clause_count": len(blocked_clauses),
        "blocked_sq_reason_counts": dict(
            sorted(
                Counter(
                    reason for row in blocked_clauses for reason in row["blocking_reasons"]
                ).items()
            )
        ),
        "prospective_candidate_projection_count": len(admitted) * 5,
        "unique_prospective_candidate_projection_count": len(prospective),
        "candidate_count": len(candidates),
        "candidate_status_counts": dict(
            sorted(Counter(row["candidate_status"] for row in candidates).items())
        ),
        "candidate_unique_trait_count": len({row["trait_id"] for row in candidates}),
        "candidate_unique_protein_count": len({row["protein_id"] for row in candidates}),
        "ready_local_reference_candidate_count": len(ready),
        "ready_local_reference_trait_count": len(ready_trait_ids),
        "ready_local_reference_protein_count": len(ready_proteins),
        "ready_local_reference_taxon_review_status_counts": dict(
            sorted(Counter(row["source_registry_taxon_review_status"] for row in ready).items())
        ),
        "ready_local_reference_unresolved_taxon_mismatch_candidate_count": sum(
            row["source_registry_taxon_review_status"]
            == "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW"
            for row in ready
        ),
        "ready_local_reference_taxon_mismatch_pair_counts": [
            {
                "source_taxon_id": source_taxon,
                "registry_taxon_id": registry_taxon,
                "candidate_count": len(candidate_ids),
            }
            for (source_taxon, registry_taxon), candidate_ids in sorted(
                taxon_mismatch_pair_candidate_ids.items(),
                key=lambda item: (item[0][0], item[0][1]),
            )
        ],
        "missing_local_protein_reference_candidate_count": len(missing),
        "missing_local_protein_reference_trait_count": len({row["trait_id"] for row in missing}),
        "missing_local_protein_reference_protein_count": len(
            {row["protein_id"] for row in missing}
        ),
        "protein_reference_request_count": len(protein_requests),
        "protein_reference_request_unique_protein_count": len(
            {row["protein_id"] for row in protein_requests}
        ),
        "blocked_out_of_bounds_source_assertion_count": len(blocked_oob),
        "blocked_out_of_bounds_affected_projection_count": sum(
            len(row["affected_trait_projections"]) for row in blocked_oob
        ),
        "blocked_taxon_conflict_source_assertion_count": len(blocked_taxon_conflicts),
        "blocked_taxon_conflict_affected_projection_count": sum(
            len(row["affected_trait_projections"]) for row in blocked_taxon_conflicts
        ),
        "local_registry_available_projection_semantics": (
            "UNIQUE_PROSPECTIVE_TRAIT_PROTEIN_INTERVAL_KEYS_WITH_LOCAL_REFERENCE_"
            "INCLUDING_BLOCKED_OOB_AND_TAXON_CONFLICT"
        ),
        "local_registry_available_projection_count": len(local_registry_projection_keys),
        "local_heterogeneous_output_row_count": len(ready)
        + len(blocked_oob)
        + len(blocked_taxon_conflicts),
        "local_union_trait_count": len(ready_trait_ids | oob_trait_ids | conflict_trait_ids),
        "local_union_protein_count": len(ready_proteins | oob_proteins | conflict_proteins),
        "candidate_rows_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
        "blocked_clause_rows_sha256": hashlib.sha256(blocked_clause_bytes).hexdigest(),
        "blocked_out_of_bounds_rows_sha256": hashlib.sha256(blocked_oob_bytes).hexdigest(),
        "blocked_taxon_conflict_rows_sha256": hashlib.sha256(
            blocked_taxon_conflict_bytes
        ).hexdigest(),
        "unmarked_sq_diagnostic_rows_sha256": hashlib.sha256(
            unmarked_sq_diagnostic_bytes
        ).hexdigest(),
        "protein_request_rows_sha256": hashlib.sha256(protein_request_bytes).hexdigest(),
        "combined_non_summary_rows_sha256": hashlib.sha256(
            b"".join(
                (
                    candidate_bytes,
                    blocked_clause_bytes,
                    blocked_oob_bytes,
                    blocked_taxon_conflict_bytes,
                    unmarked_sq_diagnostic_bytes,
                    protein_request_bytes,
                )
            )
        ).hexdigest(),
        "grounding_evidence_emitted_count": 0,
        "network_action_performed": False,
        "write_action_performed": False,
    }
    _content_address(
        summary,
        id_field="stage_id",
        prefix="scope-sq-grounding-stage:",
        row_hash_field="summary_row_sha256",
    )
    return StageResult(
        candidates=tuple(candidates),
        blocked_clauses=tuple(blocked_clauses),
        blocked_out_of_bounds=tuple(blocked_oob),
        blocked_taxon_conflicts=tuple(blocked_taxon_conflicts),
        unmarked_sq_diagnostics=tuple(unmarked_sq_diagnostics),
        protein_requests=protein_requests,
        summary=summary,
    )


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows: list[str] = []
    if not summary_only:
        rows.extend(canonical_json(row) for row in result.candidates)
        rows.extend(canonical_json(row) for row in result.blocked_clauses)
        rows.extend(canonical_json(row) for row in result.blocked_out_of_bounds)
        rows.extend(canonical_json(row) for row in result.blocked_taxon_conflicts)
        rows.extend(canonical_json(row) for row in result.unmarked_sq_diagnostics)
        rows.extend(canonical_json(row) for row in result.protein_requests)
    rows.append(canonical_json(result.summary))
    return "\n".join(rows) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments", type=Path, default=DEFAULT_COMMENTS)
    parser.add_argument("--descriptions", type=Path, default=DEFAULT_DESCRIPTIONS)
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY)
    parser.add_argument("--traits-root", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument(
        "--protein-registry",
        type=Path,
        default=DEFAULT_PROTEIN_REGISTRY,
        help=f"exact local protein registry JSONL (default: {DEFAULT_PROTEIN_REGISTRY})",
    )
    parser.add_argument(
        "--expected-protein-registry-sha256",
        default=EXPECTED_PROTEIN_REGISTRY_SHA256,
    )
    parser.add_argument("--expect-uniprot-release", default=EXPECTED_UNIPROT_RELEASE)
    parser.add_argument("--expected-comments-sha256", default=EXPECTED_COMMENTS_SHA256)
    parser.add_argument("--expected-descriptions-sha256", default=EXPECTED_DESCRIPTIONS_SHA256)
    parser.add_argument("--expected-hierarchy-sha256", default=EXPECTED_HIERARCHY_SHA256)
    parser.add_argument("--summary-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_stage(
            comments_path=args.comments,
            descriptions_path=args.descriptions,
            hierarchy_path=args.hierarchy,
            traits_root=args.traits_root,
            protein_registry_path=args.protein_registry,
            expected_protein_registry_sha256=args.expected_protein_registry_sha256,
            expected_uniprot_release=args.expect_uniprot_release,
            expected_source_sha256={
                "comments": args.expected_comments_sha256,
                "descriptions": args.expected_descriptions_sha256,
                "hierarchy": args.expected_hierarchy_sha256,
            },
        )
    except (OSError, ScopeSqStageError, ValueError) as error:
        print(f"refusing to stage SCOPe SQ grounding candidates: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
