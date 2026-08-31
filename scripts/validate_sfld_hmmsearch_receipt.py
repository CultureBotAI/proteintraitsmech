#!/usr/bin/env python3
"""Validate one content-addressed SFLD ``hmmsearch --cut_ga`` run receipt.

This is a read-only execution-boundary verifier.  It never runs HMMER, creates
FASTA files, writes grounding, or changes trait records.  A separate controlled
runner must capture a completed invocation and install its receipt last.

The receipt binds the exact executable and version capture; literal argv; the
pinned SFLD HMM, hierarchy, and correlated-site bytes; a canonical
ProteinReference registry and its exact derived FASTA; complete HMMER stdout,
stderr, Stockholm, and domain-table outputs; one selected domain-table row;
the selected model/domain scores; and the selected alignment back to the exact
registry sequence.  The existing :mod:`sfld_match` evaluator is then replayed
on a single-target projection extracted from the full ``-A`` output.

Passing this verifier proves content and semantic consistency of a supplied
execution attestation.  It does not re-execute the process, authenticate the
receipt producer, approve the SFLD source-model migration, satisfy the separate
provider-acquisition receipt, or authorize grounding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping

from sfld_match import SfldMatchError, evaluate_sfld_alignment, parse_hmmer_stockholm
from sfld_release import (
    SFLD_4_HIERARCHY_SHA256,
    SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
    SFLD_4_HMM_SHA256,
    SFLD_4_HMM_SOURCE_ARTIFACT,
    SFLD_4_SITES_SHA256,
    SFLD_4_SITES_SOURCE_ARTIFACT,
    SfldRelease,
    SfldReleaseError,
    build_sfld_release_manifest,
    load_sfld_release,
)
from validate_uniprot_grounding import validate_protein_reference

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "data/grounding/protein_registry.jsonl"
DEFAULT_HMM = REPO_ROOT / SFLD_4_HMM_SOURCE_ARTIFACT
DEFAULT_HIERARCHY = REPO_ROOT / SFLD_4_HIERARCHY_SOURCE_ARTIFACT
DEFAULT_SITES = REPO_ROOT / SFLD_4_SITES_SOURCE_ARTIFACT

SCHEMA_VERSION = 1
RECEIPT_KIND = "SFLD_HMMSEARCH_CUT_GA_EXECUTION_RECEIPT"
RECEIPT_ID_PREFIX = "sfld-hmmsearch-execution-receipt:"
VERIFICATION_KIND = "SFLD_HMMSEARCH_EXECUTION_RECEIPT_VERIFICATION"
SUPPORTED_HMMER_VERSION = "3.4"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
PROVENANCE_LIMIT = (
    "CONTENT_AND_SEMANTIC_BINDINGS_VERIFIED;PROCESS_EXECUTION_ATTESTED_"
    "BY_PRODUCER_NOT_REEXECUTED_OR_AUTHENTICATED"
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_SECOND_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_HMMER_VERSION_RE = re.compile(
    r"^# HMMER (?P<version>[^\s]+) \([^\r\n]+\); https?://hmmer\.org/?$", re.MULTILINE
)
_HMMSEARCH_PROGRAM_RE = re.compile(
    r"^# hmmsearch :: search profile\(s\) against a sequence database\s*$", re.MULTILINE
)
_DOMTBL_PROGRAM_RE = re.compile(r"^# Program:\s+hmmsearch\s*$", re.MULTILINE)
_DOMTBL_VERSION_RE = re.compile(r"^# Version:\s+(?P<version>[^\s]+).*$", re.MULTILINE)
_DOMAIN_TARGET_RE = re.compile(r"^(?P<parent>[^/\s]+)/(?P<start>[1-9][0-9]*)-(?P<end>[1-9][0-9]*)$")
_READ_CHUNK_BYTES = 1024 * 1024

_MAX_BYTES = {
    "receipt": 64 * 1024 * 1024,
    "executable": 512 * 1024 * 1024,
    "version_stdout": 4 * 1024 * 1024,
    "version_stderr": 4 * 1024 * 1024,
    "hmm": 256 * 1024 * 1024,
    "hierarchy": 64 * 1024 * 1024,
    "sites": 64 * 1024 * 1024,
    "registry": 128 * 1024 * 1024,
    "fasta": 256 * 1024 * 1024,
    "main_output": 512 * 1024 * 1024,
    "stderr_output": 64 * 1024 * 1024,
    "alignment_output": 512 * 1024 * 1024,
    "domtblout": 512 * 1024 * 1024,
}

_ARTIFACT_ROLES = (
    "executable",
    "version_stdout",
    "version_stderr",
    "hmm",
    "hierarchy",
    "sites",
    "registry",
    "fasta",
    "main_output",
    "stderr_output",
    "alignment_output",
    "domtblout",
)
_NONEMPTY_ROLES = frozenset(_ARTIFACT_ROLES) - {"version_stderr", "stderr_output"}


class SfldHmmsearchReceiptError(ValueError):
    """A supplied run bundle cannot support the claimed receipt."""


@dataclass(frozen=True, slots=True)
class ArtifactCapture:
    """One immutable, bounded regular-file capture."""

    path: Path
    raw: bytes
    sha256: str
    size_bytes: int
    device: int
    inode: int
    mode_type: int
    mode_bits: int
    mtime_ns: int
    ctime_ns: int

    @property
    def stable_identity(self) -> tuple[int, int, int, int, int, int, str]:
        return (
            self.device,
            self.inode,
            self.mode_type,
            self.size_bytes,
            self.mtime_ns,
            self.ctime_ns,
            self.sha256,
        )


@dataclass(frozen=True, slots=True)
class DomtblRow:
    """The 22 fixed HMMER per-domain columns plus target description."""

    line_number: int
    raw_line: str
    target_name: str
    target_accession: str
    target_length: int
    query_name: str
    query_accession: str
    query_length: int
    full_evalue: str
    full_score: str
    full_bias: str
    domain_number: int
    domain_count: int
    conditional_evalue: str
    independent_evalue: str
    domain_score: str
    domain_bias: str
    hmm_from: int
    hmm_to: int
    alignment_from: int
    alignment_to: int
    envelope_from: int
    envelope_to: int
    accuracy: str
    description: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "alignment_from": self.alignment_from,
            "alignment_to": self.alignment_to,
            "conditional_evalue": self.conditional_evalue,
            "description": self.description,
            "domain_bias": self.domain_bias,
            "domain_count": self.domain_count,
            "domain_number": self.domain_number,
            "domain_score_bits": self.domain_score,
            "envelope_from": self.envelope_from,
            "envelope_to": self.envelope_to,
            "full_bias": self.full_bias,
            "full_evalue": self.full_evalue,
            "full_sequence_score_bits": self.full_score,
            "hmm_from": self.hmm_from,
            "hmm_to": self.hmm_to,
            "independent_evalue": self.independent_evalue,
            "query_accession": self.query_accession,
            "query_length": self.query_length,
            "query_name": self.query_name,
            "target_accession": self.target_accession,
            "target_length": self.target_length,
            "target_name": self.target_name,
        }


@dataclass(frozen=True, slots=True)
class ReceiptPaths:
    """Every independently supplied path needed for strict verification."""

    receipt: Path
    executable: Path
    version_stdout: Path
    version_stderr: Path
    hmm: Path
    hierarchy: Path
    sites: Path
    registry: Path
    fasta: Path
    main_output: Path
    stderr_output: Path
    alignment_output: Path
    domtblout: Path

    def artifact_paths(self) -> dict[str, Path]:
        return {role: getattr(self, role) for role in _ARTIFACT_ROLES}


def canonical_json(value: Any) -> str:
    """Canonical, finite JSON used for every content address."""

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
    raw = "".join(canonical_json(row) + "\n" for row in rows).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise SfldHmmsearchReceiptError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise SfldHmmsearchReceiptError(f"non-finite JSON constant {value!r}")


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _entry_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _capture_regular_file(
    path: Path,
    *,
    label: str,
    max_bytes: int,
    allow_empty: bool = False,
) -> ArtifactCapture:
    """Capture through component-relative ``O_NOFOLLOW`` descriptors."""

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
        raise SfldHmmsearchReceiptError(
            f"{label}: platform lacks descriptor-relative no-follow support"
        )
    if type(max_bytes) is not int or max_bytes < 1:
        raise SfldHmmsearchReceiptError(f"{label}: invalid maximum byte count")

    lexical = _absolute_lexical(path)
    components = lexical.parts[1:]
    if not components or any(component in {"", ".", ".."} for component in components):
        raise SfldHmmsearchReceiptError(f"{label}: path has unsafe components: {path}")

    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    directory_flags = os.O_RDONLY | directory_only | no_follow | close_on_exec
    file_flags = os.O_RDONLY | no_follow | close_on_exec | getattr(os, "O_NONBLOCK", 0)
    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        try:
            current = os.open(lexical.anchor, directory_flags)
        except OSError as error:
            raise SfldHmmsearchReceiptError(
                f"{label}: cannot safely open path root for {path}: {error}"
            ) from error
        descriptors.append(current)
        for component in components[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                metadata = os.fstat(child)
            except OSError as error:
                raise SfldHmmsearchReceiptError(
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
            raise SfldHmmsearchReceiptError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        descriptors.append(descriptor)
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise SfldHmmsearchReceiptError(f"{label}: input is not a regular file: {path}")
        minimum = 0 if allow_empty else 1
        if before.st_size < minimum or before.st_size > max_bytes:
            raise SfldHmmsearchReceiptError(
                f"{label}: input size {before.st_size} is outside {minimum}..{max_bytes}"
            )

        chunks: list[bytes] = []
        captured = 0
        while True:
            try:
                chunk = os.read(descriptor, min(_READ_CHUNK_BYTES, max_bytes - captured + 1))
            except OSError as error:
                raise SfldHmmsearchReceiptError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured += len(chunk)
            if captured > max_bytes:
                raise SfldHmmsearchReceiptError(f"{label}: input exceeds {max_bytes} bytes")
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        before_identity = (
            before.st_dev,
            before.st_ino,
            stat.S_IFMT(before.st_mode),
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            stat.S_IFMT(after.st_mode),
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if len(raw) != before.st_size or before_identity != after_identity:
            raise SfldHmmsearchReceiptError(f"{label}: input changed during capture")
        for parent, component, expected in bindings:
            try:
                live = os.stat(component, dir_fd=parent, follow_symlinks=False)
            except OSError as error:
                raise SfldHmmsearchReceiptError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected:
                raise SfldHmmsearchReceiptError(
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
            mtime_ns=before.st_mtime_ns,
            ctime_ns=before.st_ctime_ns,
        )
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _artifact_projection(
    capture: ArtifactCapture,
    *,
    include_mode: bool = False,
) -> dict[str, Any]:
    projection = {
        "path": str(capture.path),
        "sha256": capture.sha256,
        "size_bytes": capture.size_bytes,
    }
    if include_mode:
        projection["mode_bits"] = capture.mode_bits
    return projection


def _ascii(raw: bytes, *, label: str, allow_empty: bool = False) -> str:
    if not raw and not allow_empty:
        raise SfldHmmsearchReceiptError(f"{label}: empty input")
    try:
        return raw.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise SfldHmmsearchReceiptError(f"{label}: non-ASCII bytes") from error


def _exact_lf_text(raw: bytes, *, label: str, allow_empty: bool = False) -> str:
    text = _ascii(raw, label=label, allow_empty=allow_empty)
    if not text and allow_empty:
        return text
    for character, name in {
        "\r": "CR/CRLF",
        "\u0085": "U+0085",
        "\u2028": "U+2028",
        "\u2029": "U+2029",
    }.items():
        if character in text:
            raise SfldHmmsearchReceiptError(f"{label}: forbidden {name} line separator")
    if not text.endswith("\n"):
        raise SfldHmmsearchReceiptError(f"{label}: must end with LF")
    return text


def _load_receipt(capture: ArtifactCapture) -> dict[str, Any]:
    text = _exact_lf_text(capture.raw, label="receipt")
    if text.count("\n") != 1:
        raise SfldHmmsearchReceiptError("receipt must be one canonical LF-terminated JSON row")
    try:
        value = json.loads(
            text[:-1],
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (ValueError, RecursionError, SfldHmmsearchReceiptError) as error:
        raise SfldHmmsearchReceiptError(f"receipt is invalid JSON: {error}") from error
    if type(value) is not dict or canonical_json(value) + "\n" != text:
        raise SfldHmmsearchReceiptError("receipt is not one exact canonical JSON object")
    return value


def _load_registry(capture: ArtifactCapture) -> list[dict[str, Any]]:
    text = _exact_lf_text(capture.raw, label="ProteinReference registry")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text[:-1].split("\n"), 1):
        if not line:
            raise SfldHmmsearchReceiptError(
                f"ProteinReference registry line {line_number}: blank row"
            )
        try:
            value = json.loads(
                line,
                object_pairs_hook=_unique_json_object,
                parse_constant=_reject_json_constant,
            )
        except (ValueError, RecursionError, SfldHmmsearchReceiptError) as error:
            raise SfldHmmsearchReceiptError(
                f"ProteinReference registry line {line_number}: invalid JSON: {error}"
            ) from error
        if type(value) is not dict or canonical_json(value) != line:
            raise SfldHmmsearchReceiptError(
                f"ProteinReference registry line {line_number}: not canonical JSON"
            )
        findings = validate_protein_reference(
            value,
            path=capture.path,
            line=line_number,
        )
        if findings:
            first = findings[0]
            raise SfldHmmsearchReceiptError(
                f"ProteinReference registry line {line_number}: {first.code}: {first.message}"
            )
        protein_id = value["protein_id"]
        if protein_id in seen:
            raise SfldHmmsearchReceiptError(
                f"ProteinReference registry line {line_number}: duplicate {protein_id}"
            )
        seen.add(protein_id)
        rows.append(value)
    if not rows:
        raise SfldHmmsearchReceiptError("ProteinReference registry has no rows")
    identifiers = [row["protein_id"] for row in rows]
    if identifiers != sorted(identifiers):
        raise SfldHmmsearchReceiptError(
            "ProteinReference registry must be strictly ordered by protein_id"
        )
    releases = {row["uniprot_release"] for row in rows}
    if len(releases) != 1:
        raise SfldHmmsearchReceiptError(
            "ProteinReference registry must bind exactly one UniProt release"
        )
    return rows


def canonical_registry_fasta(rows: Iterable[Mapping[str, Any]]) -> bytes:
    """Derive the exact full-registry FASTA used by the execution contract."""

    parts: list[str] = []
    previous: str | None = None
    for row in rows:
        protein_id = row.get("protein_id")
        sequence = row.get("sequence")
        if not isinstance(protein_id, str) or not isinstance(sequence, str):
            raise SfldHmmsearchReceiptError("cannot derive FASTA from malformed registry row")
        if previous is not None and protein_id <= previous:
            raise SfldHmmsearchReceiptError("registry rows are not in strict protein_id order")
        previous = protein_id
        parts.extend((">", protein_id, "\n", sequence, "\n"))
    try:
        return "".join(parts).encode("ascii", errors="strict")
    except UnicodeEncodeError as error:
        raise SfldHmmsearchReceiptError("registry cannot be represented as ASCII FASTA") from error


def _sequence_projection(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "protein_id": row["protein_id"],
            "sequence_length": row["sequence_length"],
            "sequence_sha256": row["sequence_sha256"],
            "sequence_version": row.get("sequence_version"),
            "uniprot_release": row["uniprot_release"],
        }
        for row in rows
    ]


def _decimal_token(token: str, *, label: str, nonnegative: bool = False) -> Decimal:
    try:
        value = Decimal(token)
    except InvalidOperation as error:
        raise SfldHmmsearchReceiptError(f"{label}: invalid decimal token {token!r}") from error
    if not value.is_finite() or (nonnegative and value < 0):
        raise SfldHmmsearchReceiptError(f"{label}: invalid finite range {token!r}")
    return value


def _positive_int(token: str, *, label: str) -> int:
    if re.fullmatch(r"[1-9][0-9]*", token) is None:
        raise SfldHmmsearchReceiptError(f"{label}: expected positive canonical integer")
    return int(token)


def parse_domtblout(text: str) -> dict[int, DomtblRow]:
    """Parse exact physical HMMER domain-table rows, keyed by line number."""

    if not isinstance(text, str):
        raise SfldHmmsearchReceiptError("domtblout input must be text")
    rows: dict[int, DomtblRow] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        fields = line.split(maxsplit=22)
        if len(fields) != 23:
            raise SfldHmmsearchReceiptError(
                f"domtblout line {line_number}: expected 22 fixed fields and a description"
            )
        for index in (6, 8, 11, 12, 14, 21):
            _decimal_token(
                fields[index],
                label=f"domtblout line {line_number} field {index + 1}",
                nonnegative=index in {6, 11, 12, 21},
            )
        _decimal_token(fields[7], label=f"domtblout line {line_number} full score")
        _decimal_token(fields[13], label=f"domtblout line {line_number} domain score")
        integers = {
            index: _positive_int(
                fields[index], label=f"domtblout line {line_number} field {index + 1}"
            )
            for index in (2, 5, 9, 10, 15, 16, 17, 18, 19, 20)
        }
        row = DomtblRow(
            line_number=line_number,
            raw_line=line,
            target_name=fields[0],
            target_accession=fields[1],
            target_length=integers[2],
            query_name=fields[3],
            query_accession=fields[4],
            query_length=integers[5],
            full_evalue=fields[6],
            full_score=fields[7],
            full_bias=fields[8],
            domain_number=integers[9],
            domain_count=integers[10],
            conditional_evalue=fields[11],
            independent_evalue=fields[12],
            domain_score=fields[13],
            domain_bias=fields[14],
            hmm_from=integers[15],
            hmm_to=integers[16],
            alignment_from=integers[17],
            alignment_to=integers[18],
            envelope_from=integers[19],
            envelope_to=integers[20],
            accuracy=fields[21],
            description=fields[22],
        )
        if row.domain_number > row.domain_count:
            raise SfldHmmsearchReceiptError(
                f"domtblout line {line_number}: domain number exceeds domain count"
            )
        if not (1 <= row.hmm_from <= row.hmm_to <= row.query_length):
            raise SfldHmmsearchReceiptError(
                f"domtblout line {line_number}: HMM coordinates are out of bounds"
            )
        if not (
            1
            <= row.envelope_from
            <= row.alignment_from
            <= row.alignment_to
            <= row.envelope_to
            <= row.target_length
        ):
            raise SfldHmmsearchReceiptError(
                f"domtblout line {line_number}: target coordinates are out of bounds"
            )
        rows[line_number] = row
    if not rows:
        raise SfldHmmsearchReceiptError("domtblout contains no domain rows")
    return rows


def _hmmer_version(text: str, *, label: str) -> str:
    matches = list(_HMMER_VERSION_RE.finditer(text))
    if len(matches) != 1:
        raise SfldHmmsearchReceiptError(
            f"{label}: expected exactly one canonical HMMER version banner"
        )
    if _HMMSEARCH_PROGRAM_RE.search(text) is None:
        raise SfldHmmsearchReceiptError(f"{label}: missing canonical hmmsearch program banner")
    return matches[0].group("version")


def _require_main_execution_header(
    text: str,
    *,
    hmm_path: str,
    fasta_path: str,
    alignment_path: str,
    domtblout_path: str,
) -> None:
    """Replay the command/path declarations HMMER writes into main output."""

    required = {
        "query HMM": rf"^# query HMM file:\s+{re.escape(hmm_path)}\s*$",
        "target sequence database": (
            rf"^# target sequence database:\s+{re.escape(fasta_path)}\s*$"
        ),
        "alignment output": (
            rf"^# MSA of all hits saved to file:\s+{re.escape(alignment_path)}\s*$"
        ),
        "domain-table output": (
            rf"^# per-dom hits tabular output:\s+{re.escape(domtblout_path)}\s*$"
        ),
        "GA cutoff": r"^# model-specific thresholding:\s+GA cutoffs\s*$",
        "fixed random seed": r"^# random number seed set to:\s+42\s*$",
        "target FASTA format": r"^# targ <seqfile> format asserted:\s+fasta\s*$",
        "serial worker count": r"^# number of worker threads:\s+0\s*$",
    }
    for label, pattern in required.items():
        if re.search(pattern, text, re.MULTILINE) is None:
            raise SfldHmmsearchReceiptError(
                f"hmmsearch main output does not bind the exact {label} contract"
            )


def _split_stockholm_records(text: str) -> list[list[str]]:
    lines = text.splitlines()
    records: list[list[str]] = []
    current: list[str] | None = None
    for line_number, line in enumerate(lines, 1):
        if current is None:
            if not line:
                continue
            if line != "# STOCKHOLM 1.0":
                raise SfldHmmsearchReceiptError(
                    f"alignment output line {line_number}: content outside a Stockholm record"
                )
            current = [line]
            continue
        current.append(line)
        if line == "//":
            records.append(current)
            current = None
    if current is not None:
        raise SfldHmmsearchReceiptError("alignment output has an unterminated Stockholm record")
    if not records:
        raise SfldHmmsearchReceiptError("alignment output has no Stockholm records")
    return records


def extract_selected_stockholm(
    text: str,
    *,
    model_accession: str,
    target_identifier: str,
) -> str:
    """Extract one target while retaining the query's complete RF mapping."""

    matching: list[list[str]] = []
    for record in _split_stockholm_records(text):
        accessions = [line.split(maxsplit=2)[2] for line in record if line.startswith("#=GF AC ")]
        if accessions == [model_accession]:
            matching.append(record)
    if len(matching) != 1:
        raise SfldHmmsearchReceiptError(
            f"alignment output has {len(matching)} records for model {model_accession}; expected 1"
        )

    target_fragments: list[str] = []
    rf_fragments: list[str] = []
    for line in matching[0][1:-1]:
        if line.startswith("#=GC RF "):
            parts = line.split(maxsplit=2)
            if len(parts) != 3:
                raise SfldHmmsearchReceiptError("alignment output has malformed #=GC RF row")
            rf_fragments.append(parts[2])
            continue
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise SfldHmmsearchReceiptError("alignment output has malformed sequence row")
        if parts[0] == target_identifier:
            target_fragments.append(parts[1])
    if not target_fragments:
        raise SfldHmmsearchReceiptError(
            f"alignment output has no sequence named {target_identifier!r}"
        )
    if len(target_fragments) != len(rf_fragments):
        raise SfldHmmsearchReceiptError("selected alignment target/RF fragment counts do not match")
    for index, (target, rf) in enumerate(zip(target_fragments, rf_fragments, strict=True), 1):
        if len(target) != len(rf):
            raise SfldHmmsearchReceiptError(
                f"selected alignment block {index} target/RF widths do not match"
            )
    lines = ["# STOCKHOLM 1.0", f"#=GF AC {model_accession}"]
    for index, (target, rf) in enumerate(zip(target_fragments, rf_fragments, strict=True)):
        if index:
            lines.append("")
        lines.extend((f"{target_identifier} {target}", f"#=GC RF {rf}"))
    lines.append("//")
    return "\n".join(lines) + "\n"


def _rounded_score_consistent(displayed: str, threshold: float) -> bool:
    """Allow exactly half one displayed decimal unit for HMMER score rounding."""

    value = _decimal_token(displayed, label="displayed bit score")
    threshold_decimal = Decimal(str(threshold))
    mantissa = displayed.lower().split("e", 1)[0]
    decimal_places = len(mantissa.rsplit(".", 1)[1]) if "." in mantissa else 0
    half_unit = Decimal(5).scaleb(-(decimal_places + 1))
    return value + half_unit >= threshold_decimal


def _load_release_from_captures(
    captures: Mapping[str, ArtifactCapture],
    *,
    expected_hmm_sha256: str,
    expected_hierarchy_sha256: str,
    expected_sites_sha256: str,
    enforce_release_contract: bool,
) -> SfldRelease:
    """Parse temporary copies so verified source paths are never reopened."""

    with tempfile.TemporaryDirectory(prefix="proteintraitsmech-sfld-hmmsearch-") as temporary:
        root = Path(temporary)
        hmm = root / "sfld.hmm"
        hierarchy = root / "sfld_hierarchy_flat.txt"
        sites = root / "sfld_sites.annot"
        hmm.write_bytes(captures["hmm"].raw)
        hierarchy.write_bytes(captures["hierarchy"].raw)
        sites.write_bytes(captures["sites"].raw)
        return load_sfld_release(
            hmm,
            hierarchy,
            sites,
            expected_hmm_sha256=expected_hmm_sha256,
            expected_hierarchy_sha256=expected_hierarchy_sha256,
            expected_sites_sha256=expected_sites_sha256,
            enforce_release_contract=enforce_release_contract,
        )


def _capture_artifacts(paths: ReceiptPaths) -> dict[str, ArtifactCapture]:
    captures = {
        role: _capture_regular_file(
            path,
            label=role,
            max_bytes=_MAX_BYTES[role],
            allow_empty=role not in _NONEMPTY_ROLES,
        )
        for role, path in paths.artifact_paths().items()
    }
    lexical_paths = [str(capture.path) for capture in captures.values()]
    if len(set(lexical_paths)) != len(lexical_paths):
        raise SfldHmmsearchReceiptError("execution artifact paths must be pairwise distinct")
    inode_keys = [(capture.device, capture.inode) for capture in captures.values()]
    if len(set(inode_keys)) != len(inode_keys):
        raise SfldHmmsearchReceiptError("execution artifacts must not be hard-link aliases")
    if captures["executable"].mode_bits & 0o111 == 0:
        raise SfldHmmsearchReceiptError("hmmsearch executable has no execute permission bit")
    return captures


def _capture_bundle(paths: ReceiptPaths) -> tuple[ArtifactCapture, dict[str, ArtifactCapture]]:
    receipt = _capture_regular_file(
        paths.receipt,
        label="receipt",
        max_bytes=_MAX_BYTES["receipt"],
    )
    captures = _capture_artifacts(paths)
    if str(receipt.path) in {str(capture.path) for capture in captures.values()}:
        raise SfldHmmsearchReceiptError("receipt path aliases an execution artifact path")
    if (receipt.device, receipt.inode) in {
        (capture.device, capture.inode) for capture in captures.values()
    }:
        raise SfldHmmsearchReceiptError("receipt file is a hard-link alias of an artifact")
    return receipt, captures


def _validate_selected_domain(
    *,
    line_number: int,
    captures: Mapping[str, ArtifactCapture],
    registry_rows: list[dict[str, Any]],
    release: SfldRelease,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    domtbl_text = _exact_lf_text(captures["domtblout"].raw, label="domtblout")
    if _DOMTBL_PROGRAM_RE.search(domtbl_text) is None:
        raise SfldHmmsearchReceiptError("domtblout has no hmmsearch program footer")
    version_match = _DOMTBL_VERSION_RE.search(domtbl_text)
    if version_match is None:
        raise SfldHmmsearchReceiptError("domtblout has no HMMER version footer")
    rows = parse_domtblout(domtbl_text)
    row = rows.get(line_number)
    if row is None:
        raise SfldHmmsearchReceiptError(
            f"selected domtblout line {line_number} is not a domain row"
        )

    model = release.models.get(row.query_accession)
    if model is None:
        raise SfldHmmsearchReceiptError(
            f"selected query accession {row.query_accession!r} is absent from pinned SFLD"
        )
    if row.query_name != model.name or row.query_length != model.model_length:
        raise SfldHmmsearchReceiptError(
            "selected domtblout query name/length does not match the pinned model"
        )
    registry_by_id = {item["protein_id"]: item for item in registry_rows}
    target = registry_by_id.get(row.target_name)
    if target is None:
        raise SfldHmmsearchReceiptError(
            f"selected target {row.target_name!r} is absent from the full registry"
        )
    if row.target_accession != "-" or row.description != "-":
        raise SfldHmmsearchReceiptError(
            "selected target accession/description does not match canonical header-only FASTA"
        )
    if row.target_length != target["sequence_length"]:
        raise SfldHmmsearchReceiptError(
            "selected domtblout target length does not match the registry"
        )
    if not _rounded_score_consistent(row.full_score, model.gathering_sequence_score):
        raise SfldHmmsearchReceiptError(
            "selected full-sequence score is visibly below the gathering threshold"
        )
    if not _rounded_score_consistent(row.domain_score, model.gathering_domain_score):
        raise SfldHmmsearchReceiptError(
            "selected domain score is visibly below the gathering threshold"
        )

    target_identifier = f"{row.target_name}/{row.alignment_from}-{row.alignment_to}"
    alignment_text = _exact_lf_text(
        captures["alignment_output"].raw,
        label="alignment output",
    )
    selected_stockholm = extract_selected_stockholm(
        alignment_text,
        model_accession=row.query_accession,
        target_identifier=target_identifier,
    )
    alignment = parse_hmmer_stockholm(selected_stockholm)
    aligned_sequence = "".join(
        symbol.upper() for symbol in alignment.aligned_target if symbol not in ".-"
    )
    expected_subsequence = target["sequence"][row.alignment_from - 1 : row.alignment_to]
    if aligned_sequence != expected_subsequence:
        raise SfldHmmsearchReceiptError(
            "selected Stockholm residues do not equal the registry alignment-coordinate substring"
        )
    site_evaluation = evaluate_sfld_alignment(release, row.query_accession, alignment)

    score_evaluation = {
        "cut_ga_command_selected_row": True,
        "displayed_scores_are_rounding_consistent": True,
        "gathering_domain_score_bits": str(Decimal(str(model.gathering_domain_score))),
        "gathering_sequence_score_bits": str(Decimal(str(model.gathering_sequence_score))),
        "observed_domain_score_bits": row.domain_score,
        "observed_full_sequence_score_bits": row.full_score,
        "qualification_basis": (
            "ROW_EMITTED_BY_ATTESTED_HMMSEARCH_CUT_GA_AND_DISPLAYED_SCORES_"
            "NOT_BELOW_HALF_UNIT_ROUNDING_BOUNDS"
        ),
    }
    selected = {
        "alignment_target_identifier": target_identifier,
        "derived_single_target_stockholm_sha256": hashlib.sha256(
            selected_stockholm.encode("ascii")
        ).hexdigest(),
        "domtblout_line_number": row.line_number,
        "domtblout_raw_line": row.raw_line,
        "domtblout_raw_line_sha256": hashlib.sha256(row.raw_line.encode("ascii")).hexdigest(),
        "model_accession": row.query_accession,
        "parsed_domtblout_row": row.as_dict(),
        "profile_threshold_evaluation": score_evaluation,
        "registry_sequence_sha256": target["sequence_sha256"],
        "site_evaluation": site_evaluation,
        "site_evaluation_sha256": value_sha256(site_evaluation),
        "target_sequence_identifier": row.target_name,
        "target_sequence_registry_binding_verified": True,
    }
    return selected, site_evaluation, version_match.group("version")


def _build_expected_receipt(
    *,
    captures: Mapping[str, ArtifactCapture],
    selected_domtblout_line_number: int,
    captured_at_utc: str,
    producer: Mapping[str, Any],
    expected_hmm_sha256: str,
    expected_hierarchy_sha256: str,
    expected_sites_sha256: str,
    enforce_release_contract: bool,
) -> dict[str, Any]:
    if type(selected_domtblout_line_number) is not int or selected_domtblout_line_number < 1:
        raise SfldHmmsearchReceiptError("selected domtblout line number must be a positive integer")
    if not isinstance(captured_at_utc, str) or _UTC_SECOND_RE.fullmatch(captured_at_utc) is None:
        raise SfldHmmsearchReceiptError("captured_at_utc must be an exact UTC-second timestamp")
    try:
        datetime.strptime(captured_at_utc, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise SfldHmmsearchReceiptError(
            "captured_at_utc is not a real UTC calendar timestamp"
        ) from error
    if type(producer) is not dict or set(producer) != {
        "implementation",
        "implementation_sha256",
    }:
        raise SfldHmmsearchReceiptError("producer must have the exact v1 field set")
    if (
        not isinstance(producer["implementation"], str)
        or not producer["implementation"].strip()
        or not isinstance(producer["implementation_sha256"], str)
        or _SHA256_RE.fullmatch(producer["implementation_sha256"]) is None
    ):
        raise SfldHmmsearchReceiptError("producer implementation binding is invalid")

    version_stdout = _exact_lf_text(
        captures["version_stdout"].raw,
        label="hmmsearch version stdout",
    )
    version = _hmmer_version(version_stdout, label="hmmsearch version stdout")
    if version != SUPPORTED_HMMER_VERSION:
        raise SfldHmmsearchReceiptError(
            f"unsupported HMMER version {version!r}; required {SUPPORTED_HMMER_VERSION}"
        )
    if (
        "Usage:" not in version_stdout
        or "--cut_ga" not in version_stdout
        or "--cpu" not in version_stdout
        or "--seed" not in version_stdout
        or "--tformat" not in version_stdout
    ):
        raise SfldHmmsearchReceiptError(
            "hmmsearch version stdout is not a complete '-h' capability capture"
        )
    version_stderr = _exact_lf_text(
        captures["version_stderr"].raw,
        label="hmmsearch version stderr",
        allow_empty=True,
    )
    main_output = _exact_lf_text(
        captures["main_output"].raw,
        label="hmmsearch main output",
    )
    main_version = _hmmer_version(main_output, label="hmmsearch main output")
    if main_version != version:
        raise SfldHmmsearchReceiptError("main and version outputs declare different HMMER versions")
    _require_main_execution_header(
        main_output,
        hmm_path=str(captures["hmm"].path),
        fasta_path=str(captures["fasta"].path),
        alignment_path=str(captures["alignment_output"].path),
        domtblout_path=str(captures["domtblout"].path),
    )
    stderr_output = _exact_lf_text(
        captures["stderr_output"].raw,
        label="hmmsearch stderr output",
        allow_empty=True,
    )
    if version_stderr or stderr_output:
        raise SfldHmmsearchReceiptError(
            "successful execution/version stderr captures must be empty"
        )

    registry_rows = _load_registry(captures["registry"])
    expected_fasta = canonical_registry_fasta(registry_rows)
    if captures["fasta"].raw != expected_fasta:
        raise SfldHmmsearchReceiptError(
            "FASTA bytes are not the exact canonical projection of the full registry"
        )
    release = _load_release_from_captures(
        captures,
        expected_hmm_sha256=expected_hmm_sha256,
        expected_hierarchy_sha256=expected_hierarchy_sha256,
        expected_sites_sha256=expected_sites_sha256,
        enforce_release_contract=enforce_release_contract,
    )
    manifest = build_sfld_release_manifest(release)
    selected, site_evaluation, domtbl_version = _validate_selected_domain(
        line_number=selected_domtblout_line_number,
        captures=captures,
        registry_rows=registry_rows,
        release=release,
    )
    if domtbl_version != version:
        raise SfldHmmsearchReceiptError(
            "domtblout and executable/main captures declare different HMMER versions"
        )

    artifact_projections = {
        role: _artifact_projection(
            captures[role],
            include_mode=role == "executable",
        )
        for role in _ARTIFACT_ROLES
    }
    executable_path = artifact_projections["executable"]["path"]
    execution = {
        "argv": [
            executable_path,
            "--cut_ga",
            "--cpu",
            "0",
            "--seed",
            "42",
            "--tformat",
            "fasta",
            "-A",
            artifact_projections["alignment_output"]["path"],
            "--domtblout",
            artifact_projections["domtblout"]["path"],
            artifact_projections["hmm"]["path"],
            artifact_projections["fasta"]["path"],
        ],
        "environment": {"LC_ALL": "C"},
        "exit_code": 0,
        "network_action_performed": False,
        "stderr_path": artifact_projections["stderr_output"]["path"],
        "stdin_sha256": EMPTY_SHA256,
        "stdout_path": artifact_projections["main_output"]["path"],
        "version_argv": [executable_path, "-h"],
        "version_exit_code": 0,
        "version_stderr_path": artifact_projections["version_stderr"]["path"],
        "version_stdout_path": artifact_projections["version_stdout"]["path"],
        "working_directory": str(captures["main_output"].path.parent),
    }
    sequence_projection = _sequence_projection(registry_rows)
    receipt: dict[str, Any] = {
        "artifacts": artifact_projections,
        "captured_at_utc": captured_at_utc,
        "completion_status": "COMPLETE_RECEIPT_INSTALLED_AFTER_BOUND_OUTPUTS",
        "execution": execution,
        "grounding_boundary": {
            "apply_authorized": False,
            "grounding_eligible": False,
            "process_execution_replayed_by_verifier": False,
            "profile_execution_binding_available": True,
            "provider_acquisition_receipt_verified": False,
            "qualification_status": "EXECUTION_RECEIPT_ONLY_NOT_GROUNDING_QUALIFIED",
            "remaining_blockers": [
                "HMMER_EXECUTABLE_BUILD_OR_ACQUISITION_RECEIPT_REQUIRED",
                "SFLD_SOURCE_MODEL_MIGRATION_REVIEW_AND_APPLY_REQUIRED",
                "SFLD_PROVIDER_ACQUISITION_RECEIPT_REQUIRED",
                "QUALIFIED_RECORD_BINDING_AND_REVIEW_REQUIRED",
            ],
            "writes_performed_by_verifier": False,
        },
        "hmmer_version": version,
        "producer": dict(producer),
        "provenance_limit": PROVENANCE_LIMIT,
        "receipt_kind": RECEIPT_KIND,
        "schema_version": SCHEMA_VERSION,
        "selected_domain": selected,
        "source_binding": {
            "hierarchy_artifact_sha256": release.hierarchy_sha256,
            "hmm_artifact_sha256": release.hmm_sha256,
            "manifest_sha256": manifest["manifest_sha256"],
            "model_count": len(release.models),
            "sites_artifact_sha256": release.sites_sha256,
            "source_release": release.release,
        },
        "source_native_match_status": (
            "PROFILE_AND_CORRELATED_SITE_MATCH"
            if site_evaluation["direct_model_evaluation"]["correlated_site_tuple_matched"]
            else "PROFILE_MATCH_CORRELATED_SITE_MISMATCH"
        ),
        "target_registry_binding": {
            "canonical_fasta_sha256": captures["fasta"].sha256,
            "protein_count": len(registry_rows),
            "registry_artifact_sha256": captures["registry"].sha256,
            "registry_rows_sha256": rows_sha256(registry_rows),
            "target_sequence_projection_sha256": value_sha256(sequence_projection),
            "uniprot_release": registry_rows[0]["uniprot_release"],
        },
    }
    receipt["receipt_id"] = RECEIPT_ID_PREFIX + value_sha256(receipt)
    return receipt


def build_receipt_value(
    *,
    paths: ReceiptPaths,
    selected_domtblout_line_number: int,
    captured_at_utc: str,
    producer: Mapping[str, Any],
    expected_hmm_sha256: str = SFLD_4_HMM_SHA256,
    expected_hierarchy_sha256: str = SFLD_4_HIERARCHY_SHA256,
    expected_sites_sha256: str = SFLD_4_SITES_SHA256,
    enforce_release_contract: bool = True,
) -> dict[str, Any]:
    """Build the deterministic value a controlled runner must install last.

    This helper does not write the value and does not execute HMMER.  It exists
    so a future controlled runner and this independent verifier share one exact
    receipt contract.
    """

    captures = _capture_artifacts(paths)
    return _build_expected_receipt(
        captures=captures,
        selected_domtblout_line_number=selected_domtblout_line_number,
        captured_at_utc=captured_at_utc,
        producer=producer,
        expected_hmm_sha256=expected_hmm_sha256,
        expected_hierarchy_sha256=expected_hierarchy_sha256,
        expected_sites_sha256=expected_sites_sha256,
        enforce_release_contract=enforce_release_contract,
    )


def verify_receipt(
    *,
    paths: ReceiptPaths,
    expected_hmm_sha256: str = SFLD_4_HMM_SHA256,
    expected_hierarchy_sha256: str = SFLD_4_HIERARCHY_SHA256,
    expected_sites_sha256: str = SFLD_4_SITES_SHA256,
    enforce_release_contract: bool = True,
) -> dict[str, Any]:
    """Strictly replay one installed receipt without executing or writing."""

    receipt_capture, captures = _capture_bundle(paths)
    supplied = _load_receipt(receipt_capture)
    expected_top_level = {
        "artifacts",
        "captured_at_utc",
        "completion_status",
        "execution",
        "grounding_boundary",
        "hmmer_version",
        "producer",
        "provenance_limit",
        "receipt_id",
        "receipt_kind",
        "schema_version",
        "selected_domain",
        "source_binding",
        "source_native_match_status",
        "target_registry_binding",
    }
    if set(supplied) != expected_top_level:
        raise SfldHmmsearchReceiptError("receipt does not have the exact v1 field set")
    if (
        supplied.get("schema_version") != SCHEMA_VERSION
        or supplied.get("receipt_kind") != RECEIPT_KIND
        or supplied.get("provenance_limit") != PROVENANCE_LIMIT
    ):
        raise SfldHmmsearchReceiptError("receipt version/kind/provenance contract is invalid")
    selected = supplied.get("selected_domain")
    if not isinstance(selected, dict):
        raise SfldHmmsearchReceiptError("receipt selected_domain is not an object")
    line_number = selected.get("domtblout_line_number")
    expected = _build_expected_receipt(
        captures=captures,
        selected_domtblout_line_number=line_number,
        captured_at_utc=supplied.get("captured_at_utc"),
        producer=supplied.get("producer"),
        expected_hmm_sha256=expected_hmm_sha256,
        expected_hierarchy_sha256=expected_hierarchy_sha256,
        expected_sites_sha256=expected_sites_sha256,
        enforce_release_contract=enforce_release_contract,
    )
    if canonical_json(supplied) != canonical_json(expected):
        raise SfldHmmsearchReceiptError(
            "receipt does not exactly reproduce the independently derived execution binding"
        )

    # Detect same-path replacement or mutation after parsing every supplied byte.
    final_receipt = _capture_regular_file(
        paths.receipt,
        label="receipt final recheck",
        max_bytes=_MAX_BYTES["receipt"],
    )
    if final_receipt.stable_identity != receipt_capture.stable_identity:
        raise SfldHmmsearchReceiptError("receipt changed during verification")
    for role, path in paths.artifact_paths().items():
        final = _capture_regular_file(
            path,
            label=f"{role} final recheck",
            max_bytes=_MAX_BYTES[role],
            allow_empty=role not in _NONEMPTY_ROLES,
        )
        if final.stable_identity != captures[role].stable_identity:
            raise SfldHmmsearchReceiptError(f"{role} changed during verification")

    return {
        "artifact_kind": VERIFICATION_KIND,
        "artifact_and_semantic_bindings_verified": True,
        "grounding_eligible": False,
        "process_execution_replayed": False,
        "provenance_limit": PROVENANCE_LIMIT,
        "receipt_id": supplied["receipt_id"],
        "schema_version": SCHEMA_VERSION,
        "selected_model_accession": selected["model_accession"],
        "selected_target_sequence_identifier": selected["target_sequence_identifier"],
        "source_native_match_status": supplied["source_native_match_status"],
        "status": "PASS_EXECUTION_RECEIPT_CONTENT_AND_SEMANTIC_BINDINGS_ONLY",
        "writes_performed": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--version-stdout", type=Path, required=True)
    parser.add_argument("--version-stderr", type=Path, required=True)
    parser.add_argument("--hmm", type=Path, default=DEFAULT_HMM)
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY)
    parser.add_argument("--sites", type=Path, default=DEFAULT_SITES)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--fasta", type=Path, required=True)
    parser.add_argument("--main-output", type=Path, required=True)
    parser.add_argument("--stderr-output", type=Path, required=True)
    parser.add_argument("--alignment-output", type=Path, required=True)
    parser.add_argument("--domtblout", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    paths = ReceiptPaths(
        receipt=args.receipt,
        executable=args.executable,
        version_stdout=args.version_stdout,
        version_stderr=args.version_stderr,
        hmm=args.hmm,
        hierarchy=args.hierarchy,
        sites=args.sites,
        registry=args.registry,
        fasta=args.fasta,
        main_output=args.main_output,
        stderr_output=args.stderr_output,
        alignment_output=args.alignment_output,
        domtblout=args.domtblout,
    )
    try:
        verification = verify_receipt(paths=paths)
    except (SfldHmmsearchReceiptError, SfldMatchError, SfldReleaseError) as error:
        print(f"SFLD hmmsearch receipt verification failed: {error}", file=sys.stderr)
        return 1
    print(canonical_json(verification))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
