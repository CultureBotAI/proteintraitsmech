#!/usr/bin/env python3
"""Plan the pinned 3did source-model repair without changing the corpus.

The legacy 3did seeder searched each complete ``#=ID`` line for ``PF\\d+`` and
therefore mistook fragments of domain names such as ``UPF1`` and ``6PF2K`` for
Pfam accessions.  This planner captures and verifies the exact March 2025
source artifact, parses the two accession columns rather than the name columns,
and proves the current generated YAML state byte-for-byte before proposing any
repair.

Source capture binds each absolute path component through retained,
descriptor-relative ``O_DIRECTORY|O_NOFOLLOW`` opens, binds the final regular
file with ``O_NOFOLLOW``, and rechecks the complete lexical path after copying.

Output is canonical JSONL on stdout: one exhaustive current-trait byte-index
row, one source-record/proposal row, and a final content-addressed summary.
There is deliberately no writer, apply, delete, fetch, grounding, or promotion
mode.  Grounding remains closed until the repair is reviewed and explicitly
authorized and an exact occurrence is mapped through residue-level SIFTS.

The trait tree must remain quiescent while this read-only planner runs.  The
planner rejects every symlink below the trait root, binds a no-follow root
descriptor, rechecks candidate membership and bytes, and detects root
replacement.  These checks do not constitute an atomic filesystem snapshot
against an uncooperative concurrent writer.
"""

from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import json
import math
import os
import re
import stat
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

import yaml

import ripgrep_prefilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from yaml_emit import folded, yaml_escape  # noqa: E402

SCHEMA_VERSION = 1
PLAN_KIND = "THREEDID_SOURCE_MODEL_REPAIR_PLAN"
SOURCE_ROW_KIND = "THREEDID_SOURCE_MODEL_REPAIR_ROW"
CURRENT_ROW_KIND = "THREEDID_CURRENT_TRAIT_BYTE_INDEX_ROW"
SUMMARY_KIND = "THREEDID_SOURCE_MODEL_REPAIR_SUMMARY"
PLAN_ID_PREFIX = "3did-source-model-repair-plan:"
SOURCE_RECORD_ID_PREFIX = "3did-source-record:"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "data" / "raw" / "3did" / "3did_flat.gz"
DEFAULT_TRAITS = REPO_ROOT / "data" / "traits"
THREEDID_ROUTE = Path("structure/interface/3did")

SOURCE_URL = "https://3did.irbbarcelona.org/download/current/3did_flat.gz"
SOURCE_RELEASE = "3did_flat_Mar_3_2025.dat"
SOURCE_GZIP_SHA256 = "092d404d77a36971053404bf3c45e5c8aeb7ea6ca0b9d54c26a3d24bfb96d433"
SOURCE_DECOMPRESSED_SHA256 = "1eba61d08a11291ea194ad5922e30ca71614c82ac7c397886c067e43cd69a689"
SOURCE_GZIP_SIZE = 71_887_209
SOURCE_DECOMPRESSED_SIZE = 665_819_102
SOURCE_GZIP_MTIME_UTC = 1_741_001_574
SOURCE_LICENSE = "3did (IRB Barcelona) — no explicit open license (FLAGGED)"

GROUNDING_GATE = "CLOSED_PENDING_SOURCE_MODEL_REPAIR_REVIEW_AUTHORIZATION_AND_RESIDUE_LEVEL_SIFTS"
QUIESCENCE_CONTRACT = (
    "DESCRIPTOR_BOUND_NOFOLLOW_CANDIDATE_SET_AND_BYTE_REHASH_NOT_AN_ATOMIC_SNAPSHOT"
)

_PFAM_ACCESSION = re.compile(r"^PF[0-9]{5}$")
_LEGACY_PFAM_SEARCH = re.compile(r"PF[0-9]+")
_PDB_ID = re.compile(rb"^[0-9][A-Za-z0-9]{3}$")
_NATIVE_RANGE = re.compile(rb"^[^:\t\r\n]+:-?[0-9]+[A-Za-z]?--?[0-9]+[A-Za-z]?$")
_FINITE_NUMBER = re.compile(rb"^-?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?$")
_TOPOLOGY = re.compile(rb"^[0-9]+:[0-9]+$")
_CONTACT = re.compile(
    rb"^[A-Z*?XUBZOJ-]\t[A-Z*?XUBZOJ-]\t\s*-?[0-9]+[A-Za-z]?\s*"
    rb"\t\s*-?[0-9]+[A-Za-z]?\s*\t(?:mm|ms|sm|ss)$"
)
_LEGACY_IDENTIFIER = re.compile(r"^proteintraitsmech:INTERFACE_PF[0-9]+_PF[0-9]+$")
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


class ThreeDidRepairError(ValueError):
    """The source-model repair cannot be planned from the supplied state."""


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


def rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(canonical_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


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
            raise ThreeDidRepairError(
                f"trait record is not JSON-shaped at {location} in {path}: non-finite number"
            )
        return
    if type(value) not in {list, dict}:
        raise ThreeDidRepairError(
            f"trait record is not JSON-shaped at {location} in {path}: "
            f"unsupported {type(value).__name__}"
        )
    identity = id(value)
    if identity in ancestors:
        raise ThreeDidRepairError(f"trait record has a YAML alias cycle at {location} in {path}")
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
            raise ThreeDidRepairError(
                f"trait record is not JSON-shaped at {location} in {path}: "
                f"mapping key {key!r} is not a string"
            )
        _require_json_shape(
            item,
            path=path,
            location=f"{location}.{key}",
            ancestors=nested,
        )


def _slug(value: str) -> str:
    return (_SLUG_RE.sub("-", value.lower()).strip("-")[:40]) or "dom"


def _pair_key(accessions: Sequence[str]) -> tuple[str, str]:
    if len(accessions) != 2:
        raise ThreeDidRepairError(f"expected two Pfam accessions, found {accessions!r}")
    left, right = accessions
    if _PFAM_ACCESSION.fullmatch(left) is None or _PFAM_ACCESSION.fullmatch(right) is None:
        raise ThreeDidRepairError(f"invalid source Pfam pair {accessions!r}")
    return tuple(sorted((left, right)))


def _legacy_pair_key(accessions: Sequence[str]) -> tuple[str, str]:
    if len(accessions) != 2:
        raise ThreeDidRepairError(f"legacy parser did not yield two hits: {accessions!r}")
    return tuple(sorted((accessions[0], accessions[1])))


def _identifier(pair: Sequence[str]) -> str:
    return "proteintraitsmech:INTERFACE_" + "_".join(sorted(pair))


def _relative_path(name_left: str, name_right: str, pair: Sequence[str]) -> Path:
    suffix = "_".join(sorted(pair)).lower()
    return THREEDID_ROUTE / f"{_slug(name_left)}-{_slug(name_right)}-{suffix}.yaml"


def _render_yaml(
    name_left: str,
    name_right: str,
    pfam_ordered: Sequence[str],
    pdb_ids: Sequence[str],
) -> bytes:
    if len(pfam_ordered) != 2:
        raise ThreeDidRepairError("renderer requires exactly two ordered Pfam accessions")
    pair = tuple(sorted(pfam_ordered))
    identifier = _identifier(pair)
    label = f"{name_left}–{name_right} domain interface"
    definition = (
        f"The structural interface between the {name_left} and {name_right} domains "
        f"(Pfam {pfam_ordered[0]}–{pfam_ordered[1]}), observed in {len(pdb_ids)} PDB "
        f"structure{'s' if len(pdb_ids) != 1 else ''} — a domain–domain "
        "interaction interface from 3did."
    )
    lines = [f"identifier: {identifier}", f"label: {yaml_escape(label)}"]
    folded_definition = folded(definition)
    lines += [f"definition: {folded_definition[0]}", *folded_definition[1:]]
    lines += [
        "definition_source: 3did",
        "trait_axis: STRUCTURE",
        "trait_category: STRUCT_INTERFACE",
        "term_kind: CLASS",
        "mapping_status: SEEDED",
    ]
    xrefs = list(dict.fromkeys(pfam_ordered))
    lines += ["xrefs:"] + [f"  - Pfam:{accession}" for accession in xrefs]
    if pdb_ids:
        lines.append("structural_geometry_representations:")
        for pdb_id in pdb_ids[:5]:
            lines += [
                f"  - structure_ref: PDB:{pdb_id}",
                "    structure_source: 3did",
            ]
    lines.append(f"license: {yaml_escape(SOURCE_LICENSE)}")
    return ("\n".join(lines) + "\n").encode("utf-8")


@dataclass(frozen=True)
class SourceCapture:
    compressed_path: Path
    decompressed_path: Path
    compressed_sha256: str
    decompressed_sha256: str
    compressed_size: int
    decompressed_size: int
    gzip_original_name: str
    gzip_mtime_utc: int


def _stat_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _assert_source_path_binding(
    *,
    lexical: Path,
    directory_bindings: Sequence[tuple[int, str, int, os.stat_result]],
    source_parent_descriptor: int,
    source_name: str,
    source_descriptor: int,
    expected_source: os.stat_result,
) -> None:
    """Prove the lexical source path still names every descriptor-bound object."""

    try:
        root_descriptor = directory_bindings[0][2]
        root_expected = directory_bindings[0][3]
        root_current = os.stat(lexical.anchor, follow_symlinks=False)
        if _stat_identity(os.fstat(root_descriptor)) != _stat_identity(root_expected):
            raise ThreeDidRepairError("bound 3did source root descriptor changed during capture")
        if _stat_identity(root_current) != _stat_identity(root_expected):
            raise ThreeDidRepairError("3did source path binding changed after capture")

        for parent_descriptor, component, target_descriptor, expected in directory_bindings[1:]:
            current = os.stat(
                component,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            if _stat_identity(os.fstat(target_descriptor)) != _stat_identity(expected):
                raise ThreeDidRepairError(
                    "bound 3did source directory descriptor changed during capture"
                )
            if _stat_identity(current) != _stat_identity(expected):
                raise ThreeDidRepairError("3did source path binding changed after capture")

        current_source = os.stat(
            source_name,
            dir_fd=source_parent_descriptor,
            follow_symlinks=False,
        )
        if _stat_identity(os.fstat(source_descriptor)) != _stat_identity(expected_source):
            raise ThreeDidRepairError("bound 3did source descriptor changed during capture")
        if _stat_identity(current_source) != _stat_identity(expected_source):
            raise ThreeDidRepairError("3did source path binding changed after capture")
    except ThreeDidRepairError:
        raise
    except OSError as error:
        raise ThreeDidRepairError(
            f"cannot recheck descriptor-bound 3did source path {lexical}: {error}"
        ) from error


def _bind_source_path(
    path: Path,
    *,
    test_hook: Callable[[str], None] | None,
) -> tuple[
    Path,
    int,
    os.stat_result,
    list[tuple[int, str, int, os.stat_result]],
]:
    """Open every source path component relative to a retained no-follow fd."""

    lexical = Path(os.path.abspath(path))
    if lexical.anchor != os.path.sep or len(lexical.parts) < 2:
        raise ThreeDidRepairError(f"3did source must be an absolute POSIX file path: {path}")
    directory_flags, file_flags = _descriptor_safety_flags()
    directory_bindings: list[tuple[int, str, int, os.stat_result]] = []
    source_descriptor: int | None = None
    try:
        root_descriptor: int | None = None
        try:
            root_descriptor = os.open(lexical.anchor, directory_flags)
            root_metadata = os.fstat(root_descriptor)
        except OSError as error:
            if root_descriptor is not None:
                os.close(root_descriptor)
            raise ThreeDidRepairError(
                f"cannot bind 3did source path anchor {lexical.anchor!r}: {error}"
            ) from error
        if not stat.S_ISDIR(root_metadata.st_mode):
            os.close(root_descriptor)
            raise ThreeDidRepairError("3did source path anchor is not a directory")
        # The synthetic first entry retains the root descriptor and its identity.
        directory_bindings.append((-1, lexical.anchor, root_descriptor, root_metadata))

        parent_descriptor = root_descriptor
        for component in lexical.parts[1:-1]:
            target_descriptor: int | None = None
            try:
                target_descriptor = os.open(
                    component,
                    directory_flags,
                    dir_fd=parent_descriptor,
                )
                target_metadata = os.fstat(target_descriptor)
            except OSError as error:
                if target_descriptor is not None:
                    os.close(target_descriptor)
                raise ThreeDidRepairError(
                    "cannot bind 3did source directory component without following "
                    f"symlinks ({component!r} in {lexical}): {error}"
                ) from error
            if not stat.S_ISDIR(target_metadata.st_mode):
                os.close(target_descriptor)
                raise ThreeDidRepairError(
                    f"3did source path component is not a directory: {component!r}"
                )
            directory_bindings.append(
                (parent_descriptor, component, target_descriptor, target_metadata)
            )
            parent_descriptor = target_descriptor

        if test_hook is not None:
            test_hook("PARENT_DIRECTORIES_BOUND")
        source_name = lexical.parts[-1]
        try:
            source_descriptor = os.open(
                source_name,
                file_flags,
                dir_fd=parent_descriptor,
            )
        except OSError as error:
            raise ThreeDidRepairError(
                "cannot bind 3did source file without following symlinks "
                f"({source_name!r} in {lexical}): {error}"
            ) from error
        source_metadata = os.fstat(source_descriptor)
        if not stat.S_ISREG(source_metadata.st_mode):
            raise ThreeDidRepairError(f"3did source is not a regular file: {path}")
        if test_hook is not None:
            test_hook("SOURCE_FILE_BOUND")
        return (
            lexical,
            source_descriptor,
            source_metadata,
            directory_bindings,
        )
    except Exception:
        if source_descriptor is not None:
            os.close(source_descriptor)
        for _parent, _component, descriptor, _metadata in reversed(directory_bindings):
            os.close(descriptor)
        raise


def _gzip_header(payload: bytes) -> tuple[str, int]:
    if len(payload) < 10 or payload[:3] != b"\x1f\x8b\x08":
        raise ThreeDidRepairError("3did source is not a gzip stream")
    flags = payload[3]
    if flags & 0xE0:
        raise ThreeDidRepairError("3did gzip header uses reserved flags")
    mtime = int.from_bytes(payload[4:8], "little")
    cursor = 10
    if flags & 0x04:
        if len(payload) < cursor + 2:
            raise ThreeDidRepairError("truncated 3did gzip extra header")
        extra_length = int.from_bytes(payload[cursor : cursor + 2], "little")
        cursor += 2 + extra_length
    original_name = ""
    if flags & 0x08:
        end = payload.find(b"\0", cursor)
        if end < 0:
            raise ThreeDidRepairError("unterminated 3did gzip original filename")
        try:
            original_name = payload[cursor:end].decode("ascii", errors="strict")
        except UnicodeDecodeError as error:
            raise ThreeDidRepairError("3did gzip original filename is not ASCII") from error
        cursor = end + 1
    if flags & 0x10:
        end = payload.find(b"\0", cursor)
        if end < 0:
            raise ThreeDidRepairError("unterminated 3did gzip comment")
        cursor = end + 1
    if flags & 0x02:
        cursor += 2
    if cursor > len(payload):
        raise ThreeDidRepairError("truncated 3did gzip header")
    return original_name, mtime


@contextlib.contextmanager
def capture_source(
    path: Path,
    *,
    expected_compressed_sha256: str,
    expected_decompressed_sha256: str,
    expected_compressed_size: int | None = None,
    expected_decompressed_size: int | None = None,
    expected_original_name: str | None = None,
    expected_mtime_utc: int | None = None,
    _test_hook: Callable[[str], None] | None = None,
) -> Iterator[SourceCapture]:
    """Capture one descriptor-bound stable gzip read and verified decompression."""

    descriptor: int | None = None
    directory_bindings: list[tuple[int, str, int, os.stat_result]] = []
    try:
        lexical, descriptor, before, directory_bindings = _bind_source_path(
            path,
            test_hook=_test_hook,
        )
        source_parent_descriptor = directory_bindings[-1][2]
        source_name = lexical.parts[-1]
        with tempfile.TemporaryDirectory(prefix="3did-source-repair-capture-") as temp_dir:
            capture_dir = Path(temp_dir)
            compressed_path = capture_dir / "source.gz"
            compressed_digest = hashlib.sha256()
            header = bytearray()
            compressed_size = 0
            with compressed_path.open("wb") as output:
                while True:
                    chunk = os.read(descriptor, 1024 * 1024)
                    if not chunk:
                        break
                    if len(header) < 4096:
                        header.extend(chunk[: 4096 - len(header)])
                    output.write(chunk)
                    compressed_digest.update(chunk)
                    compressed_size += len(chunk)
                output.flush()
                os.fsync(output.fileno())
            after = os.fstat(descriptor)
            _assert_source_path_binding(
                lexical=lexical,
                directory_bindings=directory_bindings,
                source_parent_descriptor=source_parent_descriptor,
                source_name=source_name,
                source_descriptor=descriptor,
                expected_source=before,
            )
            stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
            if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
                raise ThreeDidRepairError("3did source changed during immutable capture")
            compressed_sha256 = compressed_digest.hexdigest()
            if compressed_sha256 != expected_compressed_sha256:
                raise ThreeDidRepairError(
                    "3did compressed source checksum mismatch: "
                    f"expected {expected_compressed_sha256}, found {compressed_sha256}"
                )
            if expected_compressed_size is not None and compressed_size != expected_compressed_size:
                raise ThreeDidRepairError(
                    "3did compressed source size mismatch: "
                    f"expected {expected_compressed_size}, found {compressed_size}"
                )
            original_name, mtime = _gzip_header(bytes(header))
            if expected_original_name is not None and original_name != expected_original_name:
                raise ThreeDidRepairError(
                    "3did gzip original filename mismatch: "
                    f"expected {expected_original_name!r}, found {original_name!r}"
                )
            if expected_mtime_utc is not None and mtime != expected_mtime_utc:
                raise ThreeDidRepairError(
                    f"3did gzip mtime mismatch: expected {expected_mtime_utc}, found {mtime}"
                )

            decompressed_path = capture_dir / "source.dat"
            decompressed_digest = hashlib.sha256()
            decompressed_size = 0
            try:
                with (
                    gzip.open(compressed_path, "rb") as source,
                    decompressed_path.open("wb") as output,
                ):
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
                        decompressed_digest.update(chunk)
                        decompressed_size += len(chunk)
                    output.flush()
                    os.fsync(output.fileno())
            except (OSError, EOFError) as error:
                raise ThreeDidRepairError(
                    f"cannot decompress captured 3did source: {error}"
                ) from error
            decompressed_sha256 = decompressed_digest.hexdigest()
            if decompressed_sha256 != expected_decompressed_sha256:
                raise ThreeDidRepairError(
                    "3did decompressed source checksum mismatch: "
                    f"expected {expected_decompressed_sha256}, found {decompressed_sha256}"
                )
            if (
                expected_decompressed_size is not None
                and decompressed_size != expected_decompressed_size
            ):
                raise ThreeDidRepairError(
                    "3did decompressed source size mismatch: "
                    f"expected {expected_decompressed_size}, found {decompressed_size}"
                )
            compressed_path.chmod(0o400)
            decompressed_path.chmod(0o400)
            yield SourceCapture(
                compressed_path=compressed_path,
                decompressed_path=decompressed_path,
                compressed_sha256=compressed_sha256,
                decompressed_sha256=decompressed_sha256,
                compressed_size=compressed_size,
                decompressed_size=decompressed_size,
                gzip_original_name=original_name,
                gzip_mtime_utc=mtime,
            )
    except ThreeDidRepairError:
        raise
    except OSError as error:
        raise ThreeDidRepairError(f"cannot capture 3did source {path}: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for _parent, _component, directory_descriptor, _metadata in reversed(directory_bindings):
            os.close(directory_descriptor)


@dataclass(frozen=True)
class SourceSide:
    side: int
    name: str
    pfam_accession: str
    pfam_version: str

    @property
    def versioned_token(self) -> str:
        return f"{self.pfam_accession}.{self.pfam_version}@Pfam"


@dataclass(frozen=True)
class SourceRecord:
    ordinal: int
    start_line: int
    end_line: int
    id_line_sha256: str
    block_sha256: str
    sides: tuple[SourceSide, SourceSide]
    legacy_hits: tuple[str, ...]
    occurrence_count: int
    contact_count: int
    pdb_ids: tuple[str, ...]

    @property
    def source_record_id(self) -> str:
        return SOURCE_RECORD_ID_PREFIX + self.block_sha256

    @property
    def true_ordered_pair(self) -> tuple[str, str]:
        return self.sides[0].pfam_accession, self.sides[1].pfam_accession

    @property
    def true_pair(self) -> tuple[str, str]:
        return _pair_key(self.true_ordered_pair)

    @property
    def legacy_ordered_pair(self) -> tuple[str, str]:
        return self.legacy_hits[0], self.legacy_hits[1]

    @property
    def legacy_pair(self) -> tuple[str, str]:
        return _legacy_pair_key(self.legacy_ordered_pair)

    @property
    def label(self) -> str:
        return f"{self.sides[0].name}–{self.sides[1].name} domain interface"

    @property
    def corrected_identifier(self) -> str:
        return _identifier(self.true_pair)

    @property
    def legacy_identifier(self) -> str:
        return _identifier(self.legacy_pair)

    @property
    def corrected_path(self) -> Path:
        return _relative_path(self.sides[0].name, self.sides[1].name, self.true_pair)

    @property
    def legacy_path(self) -> Path:
        return _relative_path(self.sides[0].name, self.sides[1].name, self.legacy_pair)

    def corrected_yaml(self) -> bytes:
        return _render_yaml(
            self.sides[0].name,
            self.sides[1].name,
            self.true_ordered_pair,
            self.pdb_ids,
        )

    def legacy_yaml(self) -> bytes:
        return _render_yaml(
            self.sides[0].name,
            self.sides[1].name,
            self.legacy_ordered_pair,
            self.pdb_ids,
        )


def _parse_id_line(
    raw: bytes, *, line_number: int
) -> tuple[SourceSide, SourceSide, tuple[str, ...]]:
    content = raw[:-1] if raw.endswith(b"\n") else raw
    if content.endswith(b"\r"):
        raise ThreeDidRepairError(f"line {line_number}: CRLF is not allowed in 3did source")
    fields = content.split(b"\t")
    if len(fields) != 5 or fields[0] != b"#=ID":
        raise ThreeDidRepairError(f"line {line_number}: #=ID must contain exactly five tab fields")
    try:
        name_left = fields[1].decode("utf-8", errors="strict")
        name_right = fields[2].decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ThreeDidRepairError(f"line {line_number}: domain name is not UTF-8") from error
    if not name_left or not name_right:
        raise ThreeDidRepairError(f"line {line_number}: domain names must be non-empty")
    left = re.fullmatch(rb" \((PF[0-9]{5})\.([0-9]+)@Pfam", fields[3])
    right = re.fullmatch(rb"(PF[0-9]{5})\.([0-9]+)@Pfam\)", fields[4])
    if left is None or right is None:
        raise ThreeDidRepairError(f"line {line_number}: invalid anchored Pfam fields in #=ID")
    side_left = SourceSide(
        side=1,
        name=name_left,
        pfam_accession=left.group(1).decode("ascii"),
        pfam_version=left.group(2).decode("ascii"),
    )
    side_right = SourceSide(
        side=2,
        name=name_right,
        pfam_accession=right.group(1).decode("ascii"),
        pfam_version=right.group(2).decode("ascii"),
    )
    legacy_hits = tuple(match.decode("ascii") for match in re.findall(rb"PF[0-9]+", content))
    if len(legacy_hits) < 2:
        raise ThreeDidRepairError(f"line {line_number}: legacy parser yielded fewer than two hits")
    return side_left, side_right, legacy_hits


def _parse_3d_line(raw: bytes, *, line_number: int) -> str:
    content = raw[:-1] if raw.endswith(b"\n") else raw
    fields = content.split(b"\t")
    if len(fields) not in {6, 7} or fields[0] != b"#=3D":
        raise ThreeDidRepairError(f"line {line_number}: #=3D must contain six or seven tab fields")
    if _PDB_ID.fullmatch(fields[1]) is None:
        raise ThreeDidRepairError(f"line {line_number}: invalid PDB identifier")
    if _NATIVE_RANGE.fullmatch(fields[2]) is None or _NATIVE_RANGE.fullmatch(fields[3]) is None:
        raise ThreeDidRepairError(f"line {line_number}: invalid PDB-native domain range")
    if _FINITE_NUMBER.fullmatch(fields[4]) is None or _FINITE_NUMBER.fullmatch(fields[5]) is None:
        raise ThreeDidRepairError(f"line {line_number}: invalid 3did score or Z-score")
    if len(fields) == 7 and _TOPOLOGY.fullmatch(fields[6]) is None:
        raise ThreeDidRepairError(f"line {line_number}: invalid 3did topology")
    return fields[1].decode("ascii").lower()


def parse_source(capture: SourceCapture) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    current_sides: tuple[SourceSide, SourceSide] | None = None
    current_legacy_hits: tuple[str, ...] = ()
    current_start = 0
    current_id_sha = ""
    current_hash: Any | None = None
    current_occurrences = 0
    current_contacts = 0
    current_occurrence_contacts = 0
    current_pdbs: list[str] = []
    seen_pdbs: set[str] = set()

    try:
        handle = capture.decompressed_path.open("rb")
    except OSError as error:
        raise ThreeDidRepairError(f"cannot open captured 3did source: {error}") from error
    with handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.endswith(b"\n"):
                raise ThreeDidRepairError(f"line {line_number}: unterminated source line")
            if raw.startswith(b"#=ID"):
                if current_sides is not None:
                    raise ThreeDidRepairError(
                        f"line {line_number}: new #=ID before previous block terminator"
                    )
                left, right, legacy_hits = _parse_id_line(raw, line_number=line_number)
                current_sides = (left, right)
                current_legacy_hits = legacy_hits
                current_start = line_number
                current_id_sha = hashlib.sha256(raw).hexdigest()
                current_hash = hashlib.sha256(raw)
                current_occurrences = 0
                current_contacts = 0
                current_occurrence_contacts = 0
                current_pdbs = []
                seen_pdbs = set()
                continue
            if current_sides is None or current_hash is None:
                raise ThreeDidRepairError(f"line {line_number}: content outside a #=ID block")
            current_hash.update(raw)
            if raw.startswith(b"#=3D"):
                if current_occurrences and current_occurrence_contacts < 5:
                    raise ThreeDidRepairError(
                        f"line {line_number}: previous #=3D has fewer than five contacts"
                    )
                pdb_id = _parse_3d_line(raw, line_number=line_number)
                current_occurrences += 1
                current_occurrence_contacts = 0
                if pdb_id not in seen_pdbs:
                    seen_pdbs.add(pdb_id)
                    current_pdbs.append(pdb_id)
                continue
            if raw == b"//\n":
                if current_occurrences == 0:
                    raise ThreeDidRepairError(
                        f"line {line_number}: #=ID block contains no #=3D occurrence"
                    )
                if current_occurrence_contacts < 5:
                    raise ThreeDidRepairError(
                        f"line {line_number}: final #=3D has fewer than five contacts"
                    )
                records.append(
                    SourceRecord(
                        ordinal=len(records) + 1,
                        start_line=current_start,
                        end_line=line_number,
                        id_line_sha256=current_id_sha,
                        block_sha256=current_hash.hexdigest(),
                        sides=current_sides,
                        legacy_hits=current_legacy_hits,
                        occurrence_count=current_occurrences,
                        contact_count=current_contacts,
                        pdb_ids=tuple(current_pdbs),
                    )
                )
                current_sides = None
                current_hash = None
                continue
            content = raw[:-1]
            if _CONTACT.fullmatch(content) is None:
                raise ThreeDidRepairError(f"line {line_number}: invalid 3did contact row")
            if current_occurrences == 0:
                raise ThreeDidRepairError(f"line {line_number}: contact before #=3D occurrence")
            current_contacts += 1
            current_occurrence_contacts += 1
    if current_sides is not None:
        raise ThreeDidRepairError("unterminated final #=ID block")
    if not records:
        raise ThreeDidRepairError("3did source contains no records")

    identifiers: dict[str, SourceRecord] = {}
    paths: dict[Path, SourceRecord] = {}
    labels: dict[str, SourceRecord] = {}
    block_ids: set[str] = set()
    for record in records:
        identifier = record.corrected_identifier
        if identifier in identifiers:
            raise ThreeDidRepairError(f"duplicate corrected source identifier {identifier}")
        identifiers[identifier] = record
        if record.corrected_path in paths:
            raise ThreeDidRepairError(f"duplicate corrected source path {record.corrected_path}")
        paths[record.corrected_path] = record
        if record.label in labels:
            raise ThreeDidRepairError(f"duplicate corrected source label {record.label!r}")
        labels[record.label] = record
        if record.source_record_id in block_ids:
            raise ThreeDidRepairError(f"duplicate source block digest {record.source_record_id}")
        block_ids.add(record.source_record_id)
    return records


@dataclass(frozen=True)
class CurrentTrait:
    identifier: str
    relative_path: Path
    record: Mapping[str, Any]
    raw: bytes
    raw_sha256: str


def _candidate_3did_paths(traits: Path) -> list[Path]:
    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits), "3did repair")
        return sorted(found)
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
        "-e",
        "3did",
        "-e",
        "INTERFACE_",
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
        raise ThreeDidRepairError(f"cannot run ripgrep trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise ThreeDidRepairError(f"ripgrep trait prefilter failed: {detail}")
    try:
        return sorted(
            Path(item.decode("utf-8", errors="strict")) for item in scan.stdout.split(b"\0") if item
        )
    except UnicodeDecodeError as error:
        raise ThreeDidRepairError("ripgrep returned a non-UTF-8 trait path") from error


def _reject_trait_tree_symlinks(traits: Path) -> None:
    lexical_root = Path(os.path.abspath(traits))
    if lexical_root.is_symlink():
        raise ThreeDidRepairError(f"trait directory is a symlink: {traits}")
    walk_error: OSError | None = None

    def remember(error: OSError) -> None:
        nonlocal walk_error
        walk_error = error

    try:
        for directory, directory_names, file_names in os.walk(
            lexical_root,
            topdown=True,
            onerror=remember,
            followlinks=False,
        ):
            if walk_error is not None:
                raise walk_error
            parent = Path(directory)
            for name in (*directory_names, *file_names):
                candidate = parent / name
                if candidate.is_symlink():
                    raise ThreeDidRepairError(
                        f"symlink below trait directory is not allowed: {candidate}"
                    )
        if walk_error is not None:
            raise walk_error
    except OSError as error:
        raise ThreeDidRepairError(f"cannot inspect trait directory {traits}: {error}") from error


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
    ):
        raise ThreeDidRepairError(
            "platform lacks required O_NOFOLLOW/O_DIRECTORY/dir_fd filesystem safety"
        )
    return os.O_RDONLY | directory_only | no_follow, os.O_RDONLY | no_follow


def _open_trait_root(traits: Path) -> tuple[Path, int, os.stat_result]:
    lexical_root = Path(os.path.abspath(traits))
    flags, _ = _descriptor_safety_flags()
    descriptor: int | None = None
    try:
        descriptor = os.open(lexical_root, flags)
        metadata = os.fstat(descriptor)
    except OSError as error:
        if descriptor is not None:
            os.close(descriptor)
        raise ThreeDidRepairError(f"cannot bind trait directory {traits}: {error}") from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ThreeDidRepairError(f"trait root is not a directory: {traits}")
    return lexical_root, descriptor, metadata


def _assert_trait_root_binding(
    lexical_root: Path, descriptor: int, expected: os.stat_result
) -> None:
    try:
        current_path = os.stat(lexical_root, follow_symlinks=False)
        current_descriptor = os.fstat(descriptor)
    except OSError as error:
        raise ThreeDidRepairError(
            f"cannot recheck bound trait directory {lexical_root}: {error}"
        ) from error

    def identity(value: os.stat_result) -> tuple[int, int, int]:
        return value.st_dev, value.st_ino, stat.S_IFMT(value.st_mode)

    if identity(current_path) != identity(expected) or identity(current_descriptor) != identity(
        expected
    ):
        raise ThreeDidRepairError(
            f"trait directory binding changed during indexing: {lexical_root}"
        )


def _validated_candidate_path(path: Path, traits: Path) -> tuple[Path, Path]:
    lexical_root = Path(os.path.abspath(traits))
    lexical_path = Path(os.path.abspath(path))
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise ThreeDidRepairError(
            f"trait candidate escapes trait directory before read: {path}"
        ) from error
    current = lexical_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ThreeDidRepairError(f"trait candidate traverses a symlink before read: {current}")
    try:
        resolved_root = lexical_root.resolve(strict=True)
        resolved_path = lexical_path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise ThreeDidRepairError(
            f"trait candidate escapes trait directory before read: {path}"
        ) from error
    except (OSError, RuntimeError) as error:
        raise ThreeDidRepairError(
            f"cannot resolve trait candidate before read {path}: {error}"
        ) from error
    if not relative.parts:
        raise ThreeDidRepairError(f"trait candidate is the trait directory itself: {path}")
    return lexical_path, relative


def _read_candidate_from_root(
    *, root_descriptor: int, relative_path: Path, display_path: Path
) -> bytes:
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
            raise ThreeDidRepairError(f"trait candidate is not a regular file: {display_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
            raise ThreeDidRepairError(f"trait candidate changed while reading: {display_path}")
        return b"".join(chunks)
    except ThreeDidRepairError:
        raise
    except OSError as error:
        raise ThreeDidRepairError(
            f"cannot open trait candidate without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


def _is_3did_record(relative_path: Path, record: Mapping[str, Any]) -> bool:
    if relative_path.parent == THREEDID_ROUTE:
        return True
    if record.get("definition_source") == "3did":
        return True
    license_value = record.get("license")
    if isinstance(license_value, str) and "3did" in license_value.lower():
        return True
    representations = record.get("structural_geometry_representations")
    if isinstance(representations, list):
        for representation in representations:
            if (
                isinstance(representation, dict)
                and representation.get("structure_source") == "3did"
            ):
                return True
    return False


def index_current_traits(traits: Path) -> dict[str, CurrentTrait]:
    if not traits.is_dir():
        raise ThreeDidRepairError(f"missing trait directory: {traits}")
    _reject_trait_tree_symlinks(traits)
    lexical_root, root_descriptor, root_metadata = _open_trait_root(traits)
    try:
        candidates = _candidate_3did_paths(traits)
        candidate_hashes: dict[Path, tuple[Path, str]] = {}
        out: dict[str, CurrentTrait] = {}
        seen_paths: set[Path] = set()
        for reported_path in candidates:
            path, relative = _validated_candidate_path(reported_path, lexical_root)
            try:
                raw = _read_candidate_from_root(
                    root_descriptor=root_descriptor,
                    relative_path=relative,
                    display_path=path,
                )
                text = raw.decode("utf-8", errors="strict")
                record = yaml.load(text, Loader=_UniqueKeyLoader)
            except (UnicodeDecodeError, yaml.YAMLError) as error:
                raise ThreeDidRepairError(f"cannot load trait record {path}: {error}") from error
            if not isinstance(record, dict):
                raise ThreeDidRepairError(f"trait record is not a mapping: {path}")
            _require_json_shape(record, path=path)
            raw_sha256 = hashlib.sha256(raw).hexdigest()
            candidate_hashes[path] = (relative, raw_sha256)
            if not _is_3did_record(relative, record):
                continue
            identifier = record.get("identifier")
            if not isinstance(identifier, str) or _LEGACY_IDENTIFIER.fullmatch(identifier) is None:
                raise ThreeDidRepairError(f"invalid 3did trait identifier {identifier!r} in {path}")
            if relative.parent != THREEDID_ROUTE:
                raise ThreeDidRepairError(
                    f"3did trait is outside its exact route {THREEDID_ROUTE}: {relative}"
                )
            if identifier in out:
                raise ThreeDidRepairError(
                    f"duplicate 3did trait identifier {identifier}: "
                    f"{out[identifier].relative_path} and {relative}"
                )
            if relative in seen_paths:
                raise ThreeDidRepairError(f"duplicate 3did trait path in index: {relative}")
            seen_paths.add(relative)
            out[identifier] = CurrentTrait(
                identifier=identifier,
                relative_path=relative,
                record=record,
                raw=raw,
                raw_sha256=raw_sha256,
            )
        _reject_trait_tree_symlinks(traits)
        _assert_trait_root_binding(lexical_root, root_descriptor, root_metadata)
        if _candidate_3did_paths(traits) != candidates:
            raise ThreeDidRepairError("trait candidate set changed during 3did indexing")
        for path, (relative, expected_sha256) in candidate_hashes.items():
            found = hashlib.sha256(
                _read_candidate_from_root(
                    root_descriptor=root_descriptor,
                    relative_path=relative,
                    display_path=path,
                )
            ).hexdigest()
            if found != expected_sha256:
                raise ThreeDidRepairError(f"trait candidate changed during 3did indexing: {path}")
        _reject_trait_tree_symlinks(traits)
        _assert_trait_root_binding(lexical_root, root_descriptor, root_metadata)
        return out
    finally:
        os.close(root_descriptor)


def _side_value(side: SourceSide) -> dict[str, Any]:
    return {
        "side": side.side,
        "name": side.name,
        "pfam_accession": side.pfam_accession,
        "pfam_version": side.pfam_version,
        "versioned_token": side.versioned_token,
    }


def _with_row_hash(row: dict[str, Any]) -> dict[str, Any]:
    row["row_sha256"] = value_sha256(row)
    return row


def _pair_set_hash(pairs: Iterable[tuple[str, str]]) -> str:
    rows = [{"pfam_a": left, "pfam_b": right} for left, right in sorted(set(pairs))]
    return rows_sha256(rows)


def build_plan(
    *,
    capture: SourceCapture,
    source_records: Sequence[SourceRecord],
    current_traits: Mapping[str, CurrentTrait],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    legacy_groups: dict[tuple[str, str], list[SourceRecord]] = defaultdict(list)
    for record in source_records:
        legacy_groups[record.legacy_pair].append(record)

    legacy_primary: dict[tuple[str, str], SourceRecord] = {
        pair: records[0] for pair, records in legacy_groups.items()
    }
    expected_current: dict[str, SourceRecord] = {}
    for pair, primary in legacy_primary.items():
        identifier = _identifier(pair)
        if identifier in expected_current:
            raise ThreeDidRepairError(f"duplicate expected legacy identifier {identifier}")
        expected_current[identifier] = primary

    if set(current_traits) != set(expected_current):
        missing = sorted(set(expected_current) - set(current_traits))
        extra = sorted(set(current_traits) - set(expected_current))
        raise ThreeDidRepairError(
            "current 3did trait identity set drifted from exact legacy state: "
            f"missing={missing[:5]!r}, extra={extra[:5]!r}"
        )

    corrected_ids = {record.corrected_identifier for record in source_records}
    source_by_id = {record.corrected_identifier: record for record in source_records}
    if len(source_by_id) != len(source_records):
        raise ThreeDidRepairError("corrected source identifier set is not unique")

    current_rows: list[dict[str, Any]] = []
    spurious_current_ids: set[str] = set()
    exact_current_ids: set[str] = set()
    for identifier in sorted(current_traits):
        current = current_traits[identifier]
        primary = expected_current[identifier]
        expected_path = primary.legacy_path
        expected_bytes = primary.legacy_yaml()
        expected_sha256 = hashlib.sha256(expected_bytes).hexdigest()
        if current.relative_path != expected_path:
            raise ThreeDidRepairError(
                f"legacy path drift for {identifier}: expected {expected_path}, "
                f"found {current.relative_path}"
            )
        if current.raw != expected_bytes:
            expected_record = yaml.load(expected_bytes.decode("utf-8"), Loader=_UniqueKeyLoader)
            if canonical_json(current.record) != canonical_json(expected_record):
                raise ThreeDidRepairError(f"legacy YAML envelope drift for {identifier}")
            raise ThreeDidRepairError(f"legacy YAML byte drift for {identifier}")
        if current.raw_sha256 != expected_sha256:
            raise ThreeDidRepairError(f"legacy YAML digest replay mismatch for {identifier}")
        group = legacy_groups[primary.legacy_pair]
        source_bindings = [record.source_record_id for record in group]
        if identifier in corrected_ids and len(group) == 1:
            corrected = source_by_id[identifier]
            if (
                current.raw != corrected.corrected_yaml()
                or current.relative_path != corrected.corrected_path
            ):
                raise ThreeDidRepairError(f"source-native current replay mismatch for {identifier}")
            classification = "EXACT_SOURCE_NATIVE_CURRENT"
            exact_current_ids.add(identifier)
        else:
            classification = "SPURIOUS_LEGACY_MISPARSE_CURRENT"
            spurious_current_ids.add(identifier)
        current_rows.append(
            _with_row_hash(
                {
                    "schema_version": SCHEMA_VERSION,
                    "kind": CURRENT_ROW_KIND,
                    "identifier": identifier,
                    "record_path": current.relative_path.as_posix(),
                    "current_record_yaml_sha256": current.raw_sha256,
                    "current_record_hash_domain": "EXACT_YAML_BYTES",
                    "classification": classification,
                    "legacy_pair": list(primary.legacy_pair),
                    "legacy_primary_source_record_id": primary.source_record_id,
                    "bound_source_record_ids": source_bindings,
                    "legacy_collision_group_size": len(group),
                    "current_envelope_status": "EXACT_LEGACY_GENERATED_YAML_BYTES",
                    "current_route_status": "EXACT_STRUCTURE_INTERFACE_3DID_ROUTE",
                    "grounding_gate": GROUNDING_GATE,
                }
            )
        )

    source_rows: list[dict[str, Any]] = []
    corrected_missing_ids: set[str] = set()
    affected_source_records: list[SourceRecord] = []
    for record in source_records:
        group = legacy_groups[record.legacy_pair]
        group_ordinal = group.index(record) + 1
        proposal_bytes = record.corrected_yaml()
        proposal_sha256 = hashlib.sha256(proposal_bytes).hexdigest()
        proposal_record = yaml.load(proposal_bytes.decode("utf-8"), Loader=_UniqueKeyLoader)
        current = current_traits.get(record.corrected_identifier)
        if (
            current is not None
            and current.relative_path == record.corrected_path
            and current.raw == proposal_bytes
        ):
            classification = "EXACT_SOURCE_NATIVE"
            source_state = "EXACT_CURRENT_TRAIT"
            current_binding = {
                "identifier": current.identifier,
                "record_path": current.relative_path.as_posix(),
                "current_record_yaml_sha256": current.raw_sha256,
            }
        else:
            corrected_missing_ids.add(record.corrected_identifier)
            affected_source_records.append(record)
            source_state = "CORRECTED_TRAIT_MISSING"
            legacy_current = current_traits[record.legacy_identifier]
            current_binding = {
                "identifier": legacy_current.identifier,
                "record_path": legacy_current.relative_path.as_posix(),
                "current_record_yaml_sha256": legacy_current.raw_sha256,
            }
            if len(group) == 1:
                classification = "DIRECT_REPAIR_PROPOSAL"
            elif group_ordinal == 1:
                classification = "COLLAPSE_PRIMARY_REPAIR_PROPOSAL"
            else:
                classification = "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL"
        row = {
            "schema_version": SCHEMA_VERSION,
            "kind": SOURCE_ROW_KIND,
            "source_record_id": record.source_record_id,
            "source_record_ordinal": record.ordinal,
            "source_block_start_line": record.start_line,
            "source_block_end_line": record.end_line,
            "source_id_line_sha256": record.id_line_sha256,
            "source_block_sha256": record.block_sha256,
            "source_hash_domain": "EXACT_DECOMPRESSED_BYTES_INCLUDING_LF",
            "source_sides": [_side_value(side) for side in record.sides],
            "source_true_pair": list(record.true_pair),
            "source_occurrence_count": record.occurrence_count,
            "source_contact_count": record.contact_count,
            "source_distinct_pdb_count": len(record.pdb_ids),
            "source_first_five_pdb_ids": list(record.pdb_ids[:5]),
            "legacy_unanchored_pfam_hits": list(record.legacy_hits),
            "legacy_first_two_ordered": list(record.legacy_ordered_pair),
            "legacy_pair": list(record.legacy_pair),
            "legacy_identifier": record.legacy_identifier,
            "legacy_expected_path": record.legacy_path.as_posix(),
            "legacy_collision_group_size": len(group),
            "legacy_collision_group_ordinal": group_ordinal,
            "legacy_collision_primary_source_record_id": group[0].source_record_id,
            "classification": classification,
            "source_state": source_state,
            "current_binding": current_binding,
            "corrected_proposal": {
                "identifier": record.corrected_identifier,
                "label": record.label,
                "record_path": record.corrected_path.as_posix(),
                "ordered_xrefs": [f"Pfam:{accession}" for accession in record.true_ordered_pair],
                "proposed_record_yaml_sha256": proposal_sha256,
                "proposed_record_semantic_sha256": value_sha256(proposal_record),
                "hash_domains": {
                    "yaml": "EXACT_PROPOSED_YAML_BYTES_NOT_MATERIALIZED",
                    "semantic": "CANONICAL_JSON_SEMANTIC_OBJECT",
                },
            },
            "writer_available": False,
            "apply_supported": False,
            "grounding_gate": GROUNDING_GATE,
        }
        source_rows.append(_with_row_hash(row))

    true_pairs = {record.true_pair for record in source_records}
    legacy_pairs = set(legacy_groups)
    missing_pairs = true_pairs - legacy_pairs
    spurious_pairs = legacy_pairs - true_pairs
    if len(corrected_missing_ids) != len(missing_pairs):
        raise ThreeDidRepairError("corrected missing identifier/pair counts diverge")
    if len(spurious_current_ids) != len(spurious_pairs):
        raise ThreeDidRepairError("spurious current identifier/pair counts diverge")

    collapse_rows = []
    for pair, group in sorted(legacy_groups.items()):
        if len(group) <= 1:
            continue
        collapse_rows.append(
            {
                "legacy_identifier": _identifier(pair),
                "legacy_pair": list(pair),
                "current_record_path": group[0].legacy_path.as_posix(),
                "primary_source_record_id": group[0].source_record_id,
                "suppressed_source_record_ids": [record.source_record_id for record in group[1:]],
                "corrected_identifiers": [record.corrected_identifier for record in group],
            }
        )

    source_block_index = [
        {
            "source_record_id": record.source_record_id,
            "source_record_ordinal": record.ordinal,
            "source_block_sha256": record.block_sha256,
        }
        for record in source_records
    ]
    all_rows = [*current_rows, *source_rows]
    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": SUMMARY_KIND,
        "plan_kind": PLAN_KIND,
        "source": "3did",
        "source_url": SOURCE_URL,
        "source_release": SOURCE_RELEASE,
        "source_release_semantics": "GZIP_ORIGINAL_FILENAME_ARTIFACT_LABEL_NOT_INTERNAL_RELEASE_HEADER",
        "source_compressed_sha256": capture.compressed_sha256,
        "source_decompressed_sha256": capture.decompressed_sha256,
        "source_compressed_size": capture.compressed_size,
        "source_decompressed_size": capture.decompressed_size,
        "source_gzip_original_name": capture.gzip_original_name,
        "source_gzip_mtime_utc": capture.gzip_mtime_utc,
        "source_license": SOURCE_LICENSE,
        "source_license_status": "NO_EXPLICIT_OPEN_LICENSE_RELEASE_BLOCKER",
        "source_record_count": len(source_records),
        "source_occurrence_count": sum(record.occurrence_count for record in source_records),
        "source_contact_count": sum(record.contact_count for record in source_records),
        "source_distinct_block_pdb_count": sum(len(record.pdb_ids) for record in source_records),
        "current_trait_count": len(current_traits),
        "exact_source_native_count": len(exact_current_ids),
        "corrected_trait_missing_count": len(corrected_missing_ids),
        "spurious_current_trait_count": len(spurious_current_ids),
        "direct_repair_source_count": sum(
            row["classification"] == "DIRECT_REPAIR_PROPOSAL" for row in source_rows
        ),
        "collapse_primary_source_count": sum(
            row["classification"] == "COLLAPSE_PRIMARY_REPAIR_PROPOSAL" for row in source_rows
        ),
        "collapse_suppressed_source_count": sum(
            row["classification"] == "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL" for row in source_rows
        ),
        "legacy_collision_key_count": len(collapse_rows),
        "legacy_collapsed_extra_source_count": sum(
            len(group) - 1 for group in legacy_groups.values() if len(group) > 1
        ),
        "source_classification_counts": dict(
            sorted(Counter(row["classification"] for row in source_rows).items())
        ),
        "current_classification_counts": dict(
            sorted(Counter(row["classification"] for row in current_rows).items())
        ),
        "corrected_pair_set_sha256": _pair_set_hash(true_pairs),
        "legacy_pair_set_sha256": _pair_set_hash(legacy_pairs),
        "missing_corrected_pair_set_sha256": _pair_set_hash(missing_pairs),
        "spurious_legacy_pair_set_sha256": _pair_set_hash(spurious_pairs),
        "source_block_index_sha256": rows_sha256(source_block_index),
        "current_trait_byte_index_sha256": rows_sha256(current_rows),
        "source_repair_rows_sha256": rows_sha256(source_rows),
        "collapse_provenance_sha256": rows_sha256(collapse_rows),
        "rows_sha256": rows_sha256(all_rows),
        "current_trait_path_domain": "RELATIVE_TO_TRAIT_ROOT",
        "source_parser_contract": (
            "EXACT_FIVE_TAB_FIELDS_ANCHORED_VERSIONED_PFAM_COLUMNS_NAMES_NEVER_SCANNED"
        ),
        "trait_tree_must_be_quiescent": True,
        "trait_tree_quiescence_verification": QUIESCENCE_CONTRACT,
        "writes_performed": False,
        "writer_available": False,
        "apply_supported": False,
        "delete_supported": False,
        "fetch_supported": False,
        "grounding_gate": GROUNDING_GATE,
        "grounding_gate_detail": (
            "Generic Pfam or InterPro membership is not source-native 3did interface evidence; "
            "repair authorization and exact contact replay through residue-level SIFTS are required."
        ),
    }
    summary["plan_id"] = PLAN_ID_PREFIX + value_sha256(summary)
    return current_rows, source_rows, summary


def plan_from_paths(
    source: Path,
    traits: Path,
    *,
    expected_compressed_sha256: str = SOURCE_GZIP_SHA256,
    expected_decompressed_sha256: str = SOURCE_DECOMPRESSED_SHA256,
    expected_compressed_size: int | None = SOURCE_GZIP_SIZE,
    expected_decompressed_size: int | None = SOURCE_DECOMPRESSED_SIZE,
    expected_original_name: str | None = SOURCE_RELEASE,
    expected_mtime_utc: int | None = SOURCE_GZIP_MTIME_UTC,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    with capture_source(
        source,
        expected_compressed_sha256=expected_compressed_sha256,
        expected_decompressed_sha256=expected_decompressed_sha256,
        expected_compressed_size=expected_compressed_size,
        expected_decompressed_size=expected_decompressed_size,
        expected_original_name=expected_original_name,
        expected_mtime_utc=expected_mtime_utc,
    ) as capture:
        source_records = parse_source(capture)
        current_traits = index_current_traits(traits)
        return build_plan(
            capture=capture,
            source_records=source_records,
            current_traits=current_traits,
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--traits", type=Path, default=DEFAULT_TRAITS)
    parser.add_argument("--summary-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        current_rows, source_rows, summary = plan_from_paths(args.source, args.traits)
    except (ThreeDidRepairError, OSError, ValueError) as error:
        print(f"refusing to plan 3did source-model repair: {error}", file=sys.stderr)
        return 2
    if not args.summary_only:
        for row in current_rows:
            print(canonical_json(row))
        for row in source_rows:
            print(canonical_json(row))
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
