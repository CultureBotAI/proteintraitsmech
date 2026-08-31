#!/usr/bin/env python3
"""Stage missing-protein BioLiP occurrences for residue-level SIFTS acquisition.

The BioLiP trait model aggregates source rows by ligand.  This stage selects
only exact BioLiP trait records which currently have no ``canonical_examples``
and replays every corresponding source row.  Byte-identical physical source
lines are represented once with all line numbers retained.  An internally
consistent row becomes a request for future residue-level SIFTS evidence; an
inconsistent row is retained as a blocker.  A second stream contains one
download request per PDB needed by the admissible rows.

This is deliberately not a protein-grounding resolver.  BioLiP's re-numbered
positions are positions in its receptor sequence, not UniProt coordinates.
The command emits no ``protein_id``, no UniProt coordinate frame, no
TraitOccurrence, and no qualification claim.  The old segment-level PDBe cache
is not an input.  Release-manifested residue-level SIFTS and a release-pinned
ProteinReference remain mandatory future evidence.

There is no writer, output-file, network, or apply mode.  Canonical JSONL is
written to stdout, followed by a content-addressed summary row.  The trait tree
must remain quiescent while the command runs: descriptor-relative no-follow
reads and repeated membership/content checks detect sampled drift, but do not
create an atomic filesystem snapshot against an uncooperative writer.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
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

SCHEMA_VERSION = 1
OCCURRENCE_KIND = "BIOLIP_MISSING_PROTEIN_SOURCE_OCCURRENCE"
FETCH_REQUEST_KIND = "BIOLIP_RESIDUE_LEVEL_SIFTS_FETCH_REQUEST"
SUMMARY_KIND = "BIOLIP_MISSING_PROTEIN_STAGE_SUMMARY"

READY_STATUS = "READY_FOR_RESIDUE_LEVEL_SIFTS"
BLOCKED_STATUS = "BLOCKED_SOURCE_RESIDUE_INCONSISTENCY"

MISSING_SOURCE_ACCESSION = "MISSING_SOURCE_UNIPROT_ACCESSION"
MISSING_PROVIDER_RELEASE = "MISSING_BIOLIP_PROVIDER_RELEASE_RECEIPT"
MISSING_OPEN_LICENSE = "BIOLIP_HAS_NO_EXPLICIT_OPEN_LICENSE"
MISSING_RESIDUE_SIFTS = "MISSING_RELEASE_MANIFESTED_REMEDIATED_RESIDUE_LEVEL_SIFTS"
MISSING_PROTEIN_REFERENCE = "MISSING_RELEASE_PINNED_PROTEIN_REFERENCE"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIOLIP = REPO_ROOT / "data" / "raw" / "biolip" / "BioLiP_nr.txt"
DEFAULT_README = REPO_ROOT / "data" / "raw" / "biolip" / "readme.txt"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data" / "traits"
BIOLIP_TRAIT_ROUTE = Path("structure/binding_site/biolip")

EXPECTED_BIOLIP_SHA256 = "4688b8c3c3acf68a6e3816780cc0ddbba8d2ba6aaa40a41daba741b099d33099"
EXPECTED_README_SHA256 = "120b22b3e26cf0d0ce7edfde122925963cdd81e6e5a8f4165d16f3238406c161"
SOURCE_PINS = {
    "biolip": EXPECTED_BIOLIP_SHA256,
    "readme": EXPECTED_README_SHA256,
}

BIOLIP_COLUMNS = (
    "pdb_id",
    "receptor_chain",
    "resolution",
    "binding_site_code",
    "ligand_id",
    "ligand_chain",
    "ligand_serial_number",
    "binding_residues_pdb_author",
    "binding_residues_receptor_sequence",
    "catalytic_residues_pdb_author",
    "catalytic_residues_receptor_sequence",
    "ec_number",
    "go_terms",
    "binding_affinity_manual",
    "binding_affinity_moad",
    "binding_affinity_pdbbind_cn",
    "binding_affinity_bindingdb",
    "uniprot_id",
    "pubmed_id",
    "ligand_author_sequence_number",
    "receptor_sequence",
)

README_COLUMN_LABELS = (
    "PDB ID",
    "Receptor chain",
    'Resolution. "-1.00" stands for lack of resolution information, e.g. for NMR',
    "Binding site number code",
    "Ligand ID in the Chemical Component Dictionary (CCD) used by the PDB database",
    "Ligand chain",
    "Ligand serial number",
    "Binding site residues (with PDB residue numbering)",
    "Binding site residues (with residue re-numbered starting from 1)",
    "Catalytic site residues (different sites are separated by ';') (with PDB residue numbering)",
    "Catalytic site residues (different sites are separated by ';') (with residue re-numbered starting from 1)",
    "EC number",
    "GO terms",
    "Binding affinity by manual survey of the original literature. The information in '()' is the PubMed ID",
    "Binding affinity provided by the Binding MOAD database. The information in '()' is the ligand information in Binding MOAD",
    "Binding affinity provided by the PDBbind-CN database. The information in '()' is the ligand information in PDBbind-CN",
    "Binding affinity provided by the BindingDB database",
    "UniProt ID",
    "PubMed ID",
    "Residue sequence number of the ligand (field _atom_site.auth_seq_id in PDBx/mmCIF format)",
    "Receptor sequence",
)

TRAIT_LICENSE = "BioLiP2 — free for academic use (Zhang Lab); no explicit open license (FLAGGED)"
POLYMER_LIGANDS = {
    "rna": "CHEBI:33697",
    "dna": "CHEBI:16991",
    "peptide": "CHEBI:16670",
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PDB_RE = re.compile(r"^[0-9A-Za-z]{4}$")
_SITE_RE = re.compile(r"^BS[0-9]+$")
_SERIAL_RE = re.compile(r"^-?[0-9]+$")
_AUTHOR_RESIDUE_RE = re.compile(
    r"^(?P<amino_acid>[A-Z])(?P<number>-?[0-9]+)(?P<insertion_code>[A-Za-z]?)$"
)
_SEQUENCE_RESIDUE_RE = re.compile(r"^(?P<amino_acid>[A-Z])(?P<position>[0-9]+)$")
_ACCESSION_RE = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[1-9][0-9]*)?$"
)
_EXACT_RESIDUES = frozenset("ACDEFGHIKLMNPQRSTVWYUO")
_AMBIGUOUS_RESIDUES = frozenset("BJXZ")
_README_COLUMN_RE = re.compile(r"^(?P<number>[0-9]{2})[ \t]+(?P<label>.*?)[ \t]*$")


class BioLipStageError(ValueError):
    """A source, trait, or filesystem invariant failed closed."""


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
class TraitBinding:
    trait_id: str
    ligand_id: str
    path: Path
    relative_path: str
    sha256: str
    has_canonical_examples: bool
    source_xrefs: tuple[str, ...]
    source_xref_status: str


@dataclass
class SourceRow:
    raw_line: bytes
    raw_line_sha256: str
    fields: tuple[str, ...]
    line_numbers: list[int]
    trait_id: str
    occurrence_key: tuple[str, str, str, str, str, str]
    binding_pairs: tuple[dict[str, Any], ...]
    residue_blocking_reasons: tuple[str, ...]
    source_accession_status: str
    source_accessions: tuple[str, ...]


@dataclass(frozen=True)
class ParsedSource:
    physical_line_count: int
    rows: tuple[SourceRow, ...]
    ligand_ids: frozenset[str]


@dataclass(frozen=True)
class StageResult:
    occurrences: tuple[dict[str, Any], ...]
    fetch_requests: tuple[dict[str, Any], ...]
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
        raise BioLipStageError(
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
        raise BioLipStageError(
            f"{description} escapes bound root {lexical_root}: {lexical_path}"
        ) from error
    if not relative.parts:
        raise BioLipStageError(f"{description} names the bound directory itself: {path}")
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise BioLipStageError(f"invalid relative {description} path: {relative}")
    return relative


def _bind_absolute_directory(path: Path, *, description: str) -> BoundDirectory:
    directory_flags, _ = _descriptor_safety_flags()
    lexical_path = _lexical_absolute(path)
    if lexical_path.anchor != os.sep:
        raise BioLipStageError(f"{description} must have an absolute POSIX path: {path}")
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
        raise BioLipStageError(
            f"cannot bind {description} without following symlinks {lexical_path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise BioLipStageError(f"{description} must be a directory: {lexical_path}")
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
        raise BioLipStageError(
            f"cannot bind {description} without following symlinks {path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise BioLipStageError(f"{description} must be a directory: {path}")
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
            raise BioLipStageError(f"{description} binding changed while staging: {binding.path}")
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
        raise BioLipStageError(f"invalid relative {description} path: {relative_path}")
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
            raise BioLipStageError(f"{description} must be a regular file: {display_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
            raise BioLipStageError(f"{description} changed while reading: {display_path}")
        return b"".join(chunks)
    except BioLipStageError:
        raise
    except OSError as error:
        raise BioLipStageError(
            f"cannot open {description} without following symlinks {display_path}: {error}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(directory_descriptor)


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return _relative_under(path, repo_root, description="path").as_posix()
    except BioLipStageError as error:
        raise BioLipStageError(
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
        raise BioLipStageError(f"invalid pinned sha256 for {description}: {expected_sha256!r}")
    relative = _relative_under(path, bound_root.path, description=description)
    raw = _read_relative_bytes(
        bound_root,
        relative,
        display_path=_lexical_absolute(path),
        description=description,
    )
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise BioLipStageError(
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
        raise BioLipStageError(
            f"{description} drifted while staging: {artifact.path}; "
            f"expected {artifact.sha256}, observed {observed}"
        )


def _artifact_projection(artifact: CapturedArtifact, *, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": artifact.relative_path,
        "sha256": artifact.sha256,
        "size_bytes": len(artifact.raw),
    }


def parse_readme(artifact: CapturedArtifact) -> None:
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise BioLipStageError(f"BioLiP README is not strict UTF-8: {error}") from error
    if "\r" in text or not text.endswith("\n"):
        raise BioLipStageError("BioLiP README must use LF terminators and end with LF")
    observed: dict[int, str] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        match = _README_COLUMN_RE.fullmatch(line)
        if match is None:
            continue
        number = int(match.group("number"))
        if 1 <= number <= len(README_COLUMN_LABELS):
            if number in observed:
                raise BioLipStageError(
                    f"BioLiP README repeats column {number:02d} at line {line_number}"
                )
            observed[number] = match.group("label")
    expected = {index: label for index, label in enumerate(README_COLUMN_LABELS, 1)}
    if observed != expected:
        missing = sorted(set(expected) - set(observed))
        mismatched = {
            number: {"expected": expected[number], "observed": observed[number]}
            for number in sorted(set(expected) & set(observed))
            if observed[number] != expected[number]
        }
        raise BioLipStageError(
            f"BioLiP README 21-column contract mismatch; missing={missing}, mismatched={mismatched}"
        )


def _trait_id_for_ligand(ligand_id: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", ligand_id).strip("_").upper() or "LIGAND"
    if ligand_id not in POLYMER_LIGANDS and ligand_id.lower() in POLYMER_LIGANDS:
        token = f"CCD_{token}"
    return f"proteintraitsmech:BIOLIP_{token}"


def _parse_accessions(value: str) -> tuple[str, tuple[str, ...]]:
    semantic = value.strip(" \t")
    if semantic in {"", "-"}:
        return "MISSING", ()
    accessions = tuple(item.strip(" \t") for item in semantic.split(","))
    if any(not item or _ACCESSION_RE.fullmatch(item) is None for item in accessions):
        return "MALFORMED", accessions
    return ("SINGLE" if len(accessions) == 1 else "MULTIPLE"), accessions


def _parse_binding_pairs(
    author_text: str,
    sequence_text: str,
    receptor_sequence: str,
) -> tuple[tuple[dict[str, Any], ...], tuple[str, ...]]:
    author_tokens = author_text.strip(" \t").split()
    sequence_tokens = sequence_text.strip(" \t").split()
    reasons: set[str] = set()
    if not author_tokens or not sequence_tokens:
        reasons.add("EMPTY_BINDING_RESIDUE_FIELD")
    if len(author_tokens) != len(sequence_tokens):
        reasons.add("BINDING_RESIDUE_TOKEN_COUNT_MISMATCH")
    pairs: list[dict[str, Any]] = []
    for ordinal, (author_token, sequence_token) in enumerate(
        itertools.zip_longest(author_tokens, sequence_tokens), 1
    ):
        pair: dict[str, Any] = {
            "ordinal": ordinal,
            "author_residue_token": author_token,
            "receptor_sequence_residue_token": sequence_token,
        }
        author_match = (
            _AUTHOR_RESIDUE_RE.fullmatch(author_token) if author_token is not None else None
        )
        sequence_match = (
            _SEQUENCE_RESIDUE_RE.fullmatch(sequence_token) if sequence_token is not None else None
        )
        if author_match is None:
            reasons.add("MALFORMED_PDB_AUTHOR_RESIDUE_TOKEN")
        else:
            pair["author_residue_number"] = int(author_match.group("number"))
            pair["author_insertion_code"] = author_match.group("insertion_code")
        if sequence_match is None:
            reasons.add("MALFORMED_RECEPTOR_SEQUENCE_RESIDUE_TOKEN")
        else:
            position = int(sequence_match.group("position"))
            pair["biolip_receptor_sequence_position"] = position
        if author_match is not None and sequence_match is not None:
            author_amino_acid = author_match.group("amino_acid")
            sequence_amino_acid = sequence_match.group("amino_acid")
            pair["source_amino_acid"] = author_amino_acid
            if author_amino_acid != sequence_amino_acid:
                reasons.add("SOURCE_RESIDUE_LETTER_MISMATCH")
            if author_amino_acid in _AMBIGUOUS_RESIDUES:
                reasons.add("AMBIGUOUS_SOURCE_AMINO_ACID")
            elif author_amino_acid not in _EXACT_RESIDUES:
                reasons.add("UNSUPPORTED_SOURCE_AMINO_ACID")
            position = int(sequence_match.group("position"))
            if not 1 <= position <= len(receptor_sequence):
                reasons.add("RECEPTOR_SEQUENCE_POSITION_OUT_OF_RANGE")
            elif receptor_sequence[position - 1] != sequence_amino_acid:
                reasons.add("SOURCE_RESIDUE_RECEPTOR_SEQUENCE_MISMATCH")
        pairs.append(pair)
    return tuple(pairs), tuple(sorted(reasons))


def parse_biolip(artifact: CapturedArtifact) -> ParsedSource:
    if b"\r" in artifact.raw or not artifact.raw.endswith(b"\n"):
        raise BioLipStageError("BioLiP source must use LF terminators and end with LF")
    grouped: dict[str, SourceRow] = {}
    ligand_ids: set[str] = set()
    full_keys: dict[tuple[str, str, str, str, str, str], str] = {}
    physical_lines = artifact.raw.splitlines(keepends=True)
    for line_number, raw_line in enumerate(physical_lines, 1):
        if raw_line == b"\n":
            raise BioLipStageError(f"blank BioLiP row at line {line_number}")
        try:
            text = raw_line.removesuffix(b"\n").decode("utf-8")
        except UnicodeDecodeError as error:
            raise BioLipStageError(
                f"BioLiP line {line_number} is not strict UTF-8: {error}"
            ) from error
        fields = tuple(text.split("\t"))
        if len(fields) != len(BIOLIP_COLUMNS):
            raise BioLipStageError(
                f"BioLiP line {line_number} has {len(fields)} tab fields; expected 21"
            )
        pdb_id, receptor_chain, _, site, ligand_id, ligand_chain, serial = fields[:7]
        if _PDB_RE.fullmatch(pdb_id) is None:
            raise BioLipStageError(f"invalid PDB id {pdb_id!r} at BioLiP line {line_number}")
        if not receptor_chain or any(char.isspace() for char in receptor_chain):
            raise BioLipStageError(
                f"invalid receptor chain {receptor_chain!r} at BioLiP line {line_number}"
            )
        if _SITE_RE.fullmatch(site) is None:
            raise BioLipStageError(
                f"invalid binding-site code {site!r} at BioLiP line {line_number}"
            )
        if not ligand_id or any(char.isspace() for char in ligand_id):
            raise BioLipStageError(f"invalid ligand id {ligand_id!r} at BioLiP line {line_number}")
        if not ligand_chain or any(char.isspace() for char in ligand_chain):
            raise BioLipStageError(
                f"invalid ligand chain {ligand_chain!r} at BioLiP line {line_number}"
            )
        if _SERIAL_RE.fullmatch(serial) is None:
            raise BioLipStageError(f"invalid ligand serial {serial!r} at BioLiP line {line_number}")
        receptor_sequence = fields[20]
        if (
            not receptor_sequence
            or not receptor_sequence.isascii()
            or not receptor_sequence.isalpha()
        ):
            raise BioLipStageError(f"invalid receptor sequence field at BioLiP line {line_number}")
        binding_pairs, residue_reasons = _parse_binding_pairs(
            fields[7], fields[8], receptor_sequence
        )
        accession_status, accessions = _parse_accessions(fields[17])
        digest = hashlib.sha256(raw_line).hexdigest()
        old = grouped.get(digest)
        if old is not None:
            if old.raw_line != raw_line:
                raise BioLipStageError("SHA-256 collision across distinct BioLiP source lines")
            old.line_numbers.append(line_number)
            continue
        occurrence_key = (pdb_id, receptor_chain, site, ligand_id, ligand_chain, serial)
        conflicting_digest = full_keys.get(occurrence_key)
        if conflicting_digest is not None and conflicting_digest != digest:
            raise BioLipStageError(
                "conflicting non-identical BioLiP rows share the exact occurrence key "
                f"{occurrence_key!r}"
            )
        full_keys[occurrence_key] = digest
        ligand_ids.add(ligand_id)
        grouped[digest] = SourceRow(
            raw_line=raw_line,
            raw_line_sha256=digest,
            fields=fields,
            line_numbers=[line_number],
            trait_id=_trait_id_for_ligand(ligand_id),
            occurrence_key=occurrence_key,
            binding_pairs=binding_pairs,
            residue_blocking_reasons=residue_reasons,
            source_accession_status=accession_status,
            source_accessions=accessions,
        )
    if not grouped:
        raise BioLipStageError("BioLiP source contains no rows")
    rows = tuple(
        sorted(
            grouped.values(),
            key=lambda row: (
                row.occurrence_key[0].lower(),
                row.occurrence_key[1],
                row.occurrence_key[2],
                row.occurrence_key[3],
                row.occurrence_key[4],
                int(row.occurrence_key[5]),
                row.raw_line_sha256,
            ),
        )
    )
    return ParsedSource(len(physical_lines), rows, frozenset(ligand_ids))


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
            raise BioLipStageError("trait YAML has an unhashable mapping key") from error
        if duplicate:
            raise BioLipStageError(f"trait YAML has duplicate key {key!r}")
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
            raise BioLipStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for key, item in value.items():
            if not isinstance(key, str):
                raise BioLipStageError(f"{source}: YAML mapping key is not a string")
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise BioLipStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for item in value:
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if value is None or type(value) in {str, int, bool}:
        return
    if type(value) is float and math.isfinite(value):
        return
    raise BioLipStageError(f"{source}: YAML value is outside the JSON data model")


def _load_yaml_mapping(raw: bytes, *, path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError, BioLipStageError) as error:
        raise BioLipStageError(f"cannot parse trait record {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise BioLipStageError(f"trait record is not a mapping: {path}")
    _require_json_shape(value, source=str(path))
    return value


def _reject_trait_tree_symlinks(traits_root: Path) -> None:
    def fail(error: OSError) -> None:
        raise BioLipStageError(f"cannot scan trait tree {traits_root}: {error}")

    for directory, names, files in os.walk(
        traits_root, topdown=True, onerror=fail, followlinks=False
    ):
        for name in [*names, *files]:
            path = Path(directory) / name
            try:
                metadata = os.stat(path, follow_symlinks=False)
            except OSError as error:
                raise BioLipStageError(
                    f"cannot inspect trait-tree entry {path}: {error}"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                raise BioLipStageError(f"symlink below trait directory is forbidden: {path}")


def _route_trait_paths(traits_binding: BoundDirectory) -> tuple[Path, ...]:
    route_binding = _bind_subdirectory(
        traits_binding,
        traits_binding.path / BIOLIP_TRAIT_ROUTE,
        description="required BioLiP trait route",
    )
    try:
        try:
            names = sorted(os.listdir(route_binding.descriptor))
        except OSError as error:
            raise BioLipStageError(
                f"cannot enumerate required BioLiP trait route {route_binding.path}: {error}"
            ) from error
        paths: list[Path] = []
        for name in names:
            try:
                metadata = os.stat(name, dir_fd=route_binding.descriptor, follow_symlinks=False)
            except OSError as error:
                raise BioLipStageError(
                    f"cannot inspect BioLiP route entry {route_binding.path / name}: {error}"
                ) from error
            path = route_binding.path / name
            if stat.S_ISLNK(metadata.st_mode):
                raise BioLipStageError(f"symlink in BioLiP trait route is forbidden: {path}")
            if not stat.S_ISREG(metadata.st_mode) or Path(name).suffix not in {".yaml", ".yml"}:
                raise BioLipStageError(
                    f"BioLiP trait route may contain only direct YAML records: {path}"
                )
            paths.append(path)
        return tuple(paths)
    finally:
        os.close(route_binding.descriptor)


def _candidate_trait_paths(traits_binding: BoundDirectory) -> tuple[Path, ...]:
    """Return required BioLiP records plus every semantic-shadow candidate."""

    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits_binding.path), "BioLiP trait")
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
        "BIOLIP",
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
        raise BioLipStageError(f"cannot run ripgrep BioLiP trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise BioLipStageError(f"ripgrep BioLiP trait prefilter failed: {detail}")
    try:
        candidates = {
            Path(raw_path.decode("utf-8")) for raw_path in scan.stdout.split(b"\0") if raw_path
        }
    except UnicodeDecodeError as error:
        raise BioLipStageError(f"ripgrep returned a non-UTF-8 trait path: {error}") from error
    candidates.update(_route_trait_paths(traits_binding))
    return tuple(sorted(candidates))


def _expected_xrefs(ligand_id: str) -> list[str]:
    polymer = POLYMER_LIGANDS.get(ligand_id)
    return [polymer if polymer is not None else f"pdb.ligand:{ligand_id}"]


def _expected_trait_filename(ligand_id: str) -> str:
    """Replay ``seed_biolip.target_path`` without importing a writer module."""

    slug = re.sub(r"[^A-Za-z0-9]+", "-", f"{ligand_id}-binding-site".lower()).strip("-")
    slug = slug[:70] or "site"
    stem = ligand_id.lower()
    if ligand_id not in POLYMER_LIGANDS and ligand_id.lower() in POLYMER_LIGANDS:
        stem = f"ccd-{stem}"
    return f"{slug}-{stem}.yaml"


def index_traits(
    traits_root: Path,
    ligand_ids: frozenset[str],
    *,
    repo_root: Path,
    repo_binding: BoundDirectory,
) -> tuple[
    dict[str, TraitBinding],
    tuple[ArtifactDigest, ...],
    tuple[str, ...],
]:
    traits_binding = _bind_subdirectory(repo_binding, traits_root, description="trait root")
    try:
        _reject_trait_tree_symlinks(traits_binding.path)
        route_binding = _bind_subdirectory(
            traits_binding,
            traits_binding.path / BIOLIP_TRAIT_ROUTE,
            description="required BioLiP trait route",
        )
        os.close(route_binding.descriptor)
        paths = _candidate_trait_paths(traits_binding)
        ligand_by_trait: dict[str, str] = {}
        for ligand_id in sorted(ligand_ids):
            trait_id = _trait_id_for_ligand(ligand_id)
            old = ligand_by_trait.get(trait_id)
            if old is not None and old != ligand_id:
                raise BioLipStageError(
                    f"BioLiP ligand ids {old!r} and {ligand_id!r} collapse to {trait_id}"
                )
            ligand_by_trait[trait_id] = ligand_id
        bindings: dict[str, TraitBinding] = {}
        captured: list[ArtifactDigest] = []
        captured_relative: list[Path] = []
        expected_parent = _lexical_absolute(traits_binding.path / BIOLIP_TRAIT_ROUTE)
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
            inside_exact_route = _lexical_absolute(path).parent == expected_parent
            if not isinstance(identifier, str) or not identifier.startswith(
                "proteintraitsmech:BIOLIP_"
            ):
                if inside_exact_route:
                    raise BioLipStageError(
                        f"{path}: non-BioLiP trait identity is forbidden in the exact "
                        f"BioLiP route: {identifier!r}"
                    )
                continue
            ligand_id = ligand_by_trait.get(identifier)
            if ligand_id is None:
                raise BioLipStageError(
                    f"{path}: BioLiP semantic identity is absent from the source: {identifier}"
                )
            if not inside_exact_route:
                raise BioLipStageError(
                    f"{path}: BioLiP trait identity {identifier} is outside its exact route"
                )
            expected_filename = _expected_trait_filename(ligand_id)
            if path.name != expected_filename:
                raise BioLipStageError(
                    f"{path}: BioLiP trait {identifier} is not at its exact seeded path; "
                    f"expected filename {expected_filename!r}"
                )
            contract = {
                "identifier": identifier,
                "definition_source": "BioLiP2 (Yang/Zhang group)",
                "trait_axis": "STRUCTURE",
                "trait_category": "STRUCT_BINDING_SITE",
                "term_kind": "CLASS",
                "license": TRAIT_LICENSE,
            }
            for field, expected in contract.items():
                if record.get(field) != expected:
                    raise BioLipStageError(
                        f"{path}: trait contract mismatch for {field}: expected "
                        f"{expected!r}, observed {record.get(field)!r}"
                    )
            xrefs = record.get("xrefs")
            required_xrefs = _expected_xrefs(ligand_id)
            allowed_xref_lists = [required_xrefs]
            if ligand_id == "dna":
                # The current polymer-DNA record retains the CCD-DNA xref from
                # the historical filename/identifier collision.  The distinct
                # CCD record now exists, so this is an explicit, byte-bound
                # current-corpus exception, not a general permission for extra
                # xrefs on source-derived traits.
                allowed_xref_lists.append(["CHEBI:16991", "pdb.ligand:DNA"])
            if xrefs not in allowed_xref_lists:
                raise BioLipStageError(
                    f"{path}: trait xrefs are outside the exact BioLiP source-model "
                    f"contract {allowed_xref_lists!r}: observed {xrefs!r}"
                )
            source_xref_status = (
                "EXACT_SEEDER_SOURCE_XREFS"
                if xrefs == required_xrefs
                else "EXPLICIT_CURRENT_POLYMER_DNA_COLLISION_XREF_EXCEPTION"
            )
            if record.get("mapping_status") not in {"SEEDED", "REVIEWED"}:
                raise BioLipStageError(f"{path}: invalid BioLiP mapping_status")
            if "canonical_examples" in record:
                examples = record["canonical_examples"]
                if not isinstance(examples, list) or not examples:
                    raise BioLipStageError(
                        f"{path}: canonical_examples must be absent or a non-empty list"
                    )
                has_examples = True
            else:
                has_examples = False
            if identifier in bindings:
                raise BioLipStageError(
                    f"duplicate BioLiP trait identity {identifier}: "
                    f"{bindings[identifier].relative_path} and {repo_relative}"
                )
            bindings[identifier] = TraitBinding(
                trait_id=identifier,
                ligand_id=ligand_id,
                path=path,
                relative_path=repo_relative,
                sha256=digest,
                has_canonical_examples=has_examples,
                source_xrefs=tuple(xrefs),
                source_xref_status=source_xref_status,
            )
        if set(bindings) != set(ligand_by_trait):
            missing = sorted(set(ligand_by_trait) - set(bindings))[:10]
            extra = sorted(set(bindings) - set(ligand_by_trait))[:10]
            raise BioLipStageError(
                f"BioLiP trait identity set mismatch; missing={missing}, extra={extra}"
            )
        _reject_trait_tree_symlinks(traits_binding.path)
        _assert_directory_binding(traits_binding, description="trait root")
        final_paths = tuple(
            _relative_under(path, traits_binding.path, description="trait prefilter candidate")
            for path in _candidate_trait_paths(traits_binding)
        )
        if final_paths != tuple(captured_relative):
            raise BioLipStageError("BioLiP trait candidate membership drifted while indexing")
        return bindings, tuple(captured), tuple(item.relative_path for item in captured)
    finally:
        os.close(traits_binding.descriptor)


def _trait_projection(binding: TraitBinding) -> dict[str, Any]:
    return {
        "trait_id": binding.trait_id,
        "ligand_id": binding.ligand_id,
        "trait_record_path": binding.relative_path,
        "trait_record_sha256": binding.sha256,
        "trait_record_has_canonical_examples": binding.has_canonical_examples,
        "trait_source_xrefs": list(binding.source_xrefs),
        "trait_source_xref_status": binding.source_xref_status,
    }


def _source_projection(row: SourceRow) -> dict[str, Any]:
    fields = dict(zip(BIOLIP_COLUMNS, row.fields, strict=True))
    receptor_sequence = fields["receptor_sequence"]
    return {
        "structure_id": f"PDB:{fields['pdb_id'].lower()}",
        "receptor_chain_id": fields["receptor_chain"],
        "resolution_text": fields["resolution"],
        "binding_site_code": fields["binding_site_code"],
        "ligand_id": fields["ligand_id"],
        "ligand_chain_id": fields["ligand_chain"],
        "ligand_serial_number_text": fields["ligand_serial_number"],
        "binding_residues_pdb_author_text": fields["binding_residues_pdb_author"],
        "binding_residues_receptor_sequence_text": fields["binding_residues_receptor_sequence"],
        "source_uniprot_field_text": fields["uniprot_id"],
        "source_uniprot_claim_status": row.source_accession_status,
        "source_uniprot_accession_claims": list(row.source_accessions),
        "receptor_sequence_length": len(receptor_sequence),
        "receptor_sequence_sha256": hashlib.sha256(receptor_sequence.encode("ascii")).hexdigest(),
        "source_field_projection_sha256": value_sha256(
            {"column_names": BIOLIP_COLUMNS, "exact_fields": row.fields}
        ),
        "source_line_numbers": row.line_numbers,
        "source_physical_line_count": len(row.line_numbers),
        "source_raw_line_sha256": row.raw_line_sha256,
        "source_raw_line_sha256_basis": "RAW_UTF8_PHYSICAL_LINE_INCLUDING_LF",
        "source_occurrence_key": {
            "pdb_id": row.occurrence_key[0],
            "receptor_chain": row.occurrence_key[1],
            "binding_site_code": row.occurrence_key[2],
            "ligand_id": row.occurrence_key[3],
            "ligand_chain": row.occurrence_key[4],
            "ligand_serial_number": row.occurrence_key[5],
        },
    }


def _occurrence_row(
    *,
    source: SourceRow,
    binding: TraitBinding,
    biolip_artifact: CapturedArtifact,
    readme_artifact: CapturedArtifact,
) -> dict[str, Any]:
    ready = not source.residue_blocking_reasons
    reasons = list(source.residue_blocking_reasons)
    promotion_blockers = [
        MISSING_PROVIDER_RELEASE,
        MISSING_OPEN_LICENSE,
        MISSING_RESIDUE_SIFTS,
        MISSING_PROTEIN_REFERENCE,
    ]
    if source.source_accession_status == "MISSING":
        promotion_blockers.append(MISSING_SOURCE_ACCESSION)
    elif source.source_accession_status == "MALFORMED":
        promotion_blockers.append("MALFORMED_SOURCE_UNIPROT_ACCESSION")
    elif source.source_accession_status == "MULTIPLE":
        promotion_blockers.append("SOURCE_UNIPROT_ACCESSION_REQUIRES_SIFTS_DISAMBIGUATION")
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": OCCURRENCE_KIND,
        "stage_status": READY_STATUS if ready else BLOCKED_STATUS,
        "qualification_claimed": False,
        "protein_identity_claimed": False,
        "uniprot_coordinates_claimed": False,
        "source_residue_validation_policy": "ALL_BINDING_RESIDUES_OR_WHOLE_ROW_BLOCKED",
        "source_residue_blocking_reasons": reasons,
        "promotion_blocking_reasons": sorted(promotion_blockers),
        "required_future_mapping_method": "SIFTS_RESIDUE_MAPPING",
        "source_coordinate_systems": [
            "PDB_AUTHOR_RESIDUE_NUMBER_WITH_INSERTION_CODE",
            "BIOLIP_RECEPTOR_SEQUENCE_POSITION_1_BASED",
        ],
        "binding_residue_pairs": list(source.binding_pairs),
        "source_residue_count": len(source.binding_pairs),
        "source_binding": _source_projection(source),
        "trait_binding": _trait_projection(binding),
        "artifact_bindings": [
            _artifact_projection(biolip_artifact, role="BIOLIP_NONREDUNDANT_ANNOTATIONS"),
            _artifact_projection(readme_artifact, role="BIOLIP_21_COLUMN_README"),
        ],
    }
    return _content_address(
        row,
        id_field="source_occurrence_id",
        prefix="biolip-missing-protein-source-occurrence:",
        row_hash_field="source_occurrence_row_sha256",
    )


def _fetch_request_row(
    *,
    pdb_id: str,
    occurrences: Sequence[Mapping[str, Any]],
    biolip_artifact: CapturedArtifact,
    readme_artifact: CapturedArtifact,
) -> dict[str, Any]:
    occurrence_ids = sorted(str(row["source_occurrence_id"]) for row in occurrences)
    source_line_bindings = sorted(
        (
            {
                "source_occurrence_id": row["source_occurrence_id"],
                "source_raw_line_sha256": row["source_binding"]["source_raw_line_sha256"],
                "source_line_numbers": row["source_binding"]["source_line_numbers"],
                "trait_id": row["trait_binding"]["trait_id"],
                "trait_record_path": row["trait_binding"]["trait_record_path"],
                "trait_record_sha256": row["trait_binding"]["trait_record_sha256"],
            }
            for row in occurrences
        ),
        key=lambda value: str(value["source_occurrence_id"]),
    )
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": FETCH_REQUEST_KIND,
        "stage_status": "RESIDUE_LEVEL_SIFTS_FETCH_REQUIRED",
        "qualification_claimed": False,
        "network_action_performed": False,
        "structure_id": f"PDB:{pdb_id}",
        "pdb_id": pdb_id,
        "requested_artifact_kind": "PDBe_SIFTS_REMEDIATED_RESIDUE_LEVEL_XML_GZIP",
        "requested_source_root": ("https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml_remediated"),
        "requested_relative_path": f"{pdb_id}.xml.gz",
        "fetch_manifest_required": True,
        "required_fetch_manifest_semantics": (
            "COMPLETE_CANONICAL_CONTENT_ADDRESSED_MANIFEST_BINDING_EVERY_REQUESTED_FILE"
        ),
        "source_occurrence_count": len(occurrence_ids),
        "source_occurrence_ids": occurrence_ids,
        "source_occurrence_ids_sha256": value_sha256(occurrence_ids),
        "source_line_and_trait_bindings": source_line_bindings,
        "source_line_and_trait_bindings_sha256": value_sha256(source_line_bindings),
        "artifact_bindings": [
            _artifact_projection(biolip_artifact, role="BIOLIP_NONREDUNDANT_ANNOTATIONS"),
            _artifact_projection(readme_artifact, role="BIOLIP_21_COLUMN_README"),
        ],
    }
    return _content_address(
        row,
        id_field="fetch_request_id",
        prefix="biolip-residue-sifts-fetch-request:",
        row_hash_field="fetch_request_row_sha256",
    )


def build_stage(
    *,
    biolip_path: Path,
    readme_path: Path,
    traits_root: Path,
    repo_root: Path = REPO_ROOT,
    expected_source_sha256: Mapping[str, str] = SOURCE_PINS,
) -> StageResult:
    if set(expected_source_sha256) != set(SOURCE_PINS):
        raise BioLipStageError("expected_source_sha256 must contain exactly biolip and readme")
    repo_binding = _bind_absolute_directory(repo_root, description="repository root")
    try:
        artifacts = {
            "biolip": _capture(
                biolip_path,
                description="BioLiP non-redundant annotation source",
                repo_root=repo_binding.path,
                expected_sha256=expected_source_sha256["biolip"],
                bound_root=repo_binding,
            ),
            "readme": _capture(
                readme_path,
                description="BioLiP source README",
                repo_root=repo_binding.path,
                expected_sha256=expected_source_sha256["readme"],
                bound_root=repo_binding,
            ),
        }
        parse_readme(artifacts["readme"])
        source = parse_biolip(artifacts["biolip"])
        traits, trait_artifacts, trait_path_snapshot = index_traits(
            traits_root,
            source.ligand_ids,
            repo_root=repo_binding.path,
            repo_binding=repo_binding,
        )
        no_example_ids = {
            trait_id for trait_id, binding in traits.items() if not binding.has_canonical_examples
        }
        selected_source = [row for row in source.rows if row.trait_id in no_example_ids]
        selected_ids = {row.trait_id for row in selected_source}
        if selected_ids != no_example_ids:
            missing = sorted(no_example_ids - selected_ids)[:10]
            raise BioLipStageError(f"no-example BioLiP traits lack source rows: {missing}")
        occurrences = [
            _occurrence_row(
                source=row,
                binding=traits[row.trait_id],
                biolip_artifact=artifacts["biolip"],
                readme_artifact=artifacts["readme"],
            )
            for row in selected_source
        ]
        occurrences.sort(
            key=lambda row: (
                row["trait_binding"]["trait_id"],
                row["source_binding"]["structure_id"],
                row["source_binding"]["receptor_chain_id"],
                row["source_binding"]["binding_site_code"],
                row["source_occurrence_id"],
            )
        )
        ready = [row for row in occurrences if row["stage_status"] == READY_STATUS]
        blocked = [row for row in occurrences if row["stage_status"] == BLOCKED_STATUS]
        ready_by_pdb: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in ready:
            pdb_id = str(row["source_binding"]["structure_id"]).removeprefix("PDB:")
            ready_by_pdb[pdb_id].append(row)
        fetch_requests = [
            _fetch_request_row(
                pdb_id=pdb_id,
                occurrences=ready_by_pdb[pdb_id],
                biolip_artifact=artifacts["biolip"],
                readme_artifact=artifacts["readme"],
            )
            for pdb_id in sorted(ready_by_pdb)
        ]

        # Recheck source bytes, every parsed semantic-shadow candidate, and
        # candidate membership before reporting under the quiescent-tree contract.
        for artifact in artifacts.values():
            _assert_unchanged(
                artifact, description="pinned BioLiP source artifact", bound_root=repo_binding
            )
        for artifact in trait_artifacts:
            _assert_unchanged(artifact, description="trait record", bound_root=repo_binding)
        traits_absolute = _lexical_absolute(traits_root)
        _reject_trait_tree_symlinks(traits_absolute)
        traits_binding = _bind_subdirectory(repo_binding, traits_absolute, description="trait root")
        try:
            final_paths = tuple(
                _repo_relative(path, repo_binding.path)
                for path in _candidate_trait_paths(traits_binding)
            )
        finally:
            os.close(traits_binding.descriptor)
        if final_paths != trait_path_snapshot:
            raise BioLipStageError("BioLiP trait candidate membership drifted while staging")
        _assert_directory_binding(repo_binding, description="repository root")

        all_trait_binding_rows = [
            _trait_projection(binding)
            for binding in sorted(traits.values(), key=lambda item: item.trait_id)
        ]
        no_example_binding_rows = [
            row for row in all_trait_binding_rows if not row["trait_record_has_canonical_examples"]
        ]
        occurrence_bytes = _rows_bytes(occurrences)
        fetch_bytes = _rows_bytes(fetch_requests)
        selected_physical_count = sum(
            int(row["source_binding"]["source_physical_line_count"]) for row in occurrences
        )
        summary: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "kind": SUMMARY_KIND,
            "stage_status": "MISSING_PROTEIN_SOURCE_STAGE_ONLY",
            "qualification_claimed": False,
            "protein_identity_claimed": False,
            "uniprot_coordinates_claimed": False,
            "network_action_performed": False,
            "writer_available": False,
            "trait_tree_must_be_quiescent": True,
            "trait_tree_verification_semantics": (
                "DESCRIPTOR_RELATIVE_NOFOLLOW_READS_WITH_REPEATED_MEMBERSHIP_AND_"
                "CONTENT_CHECKS_NOT_AN_ATOMIC_FILESYSTEM_SNAPSHOT"
            ),
            "scope_policy": "EXACT_BIOLIP_TRAITS_WITHOUT_CANONICAL_EXAMPLES",
            "duplicate_policy": (
                "BYTE_IDENTICAL_SOURCE_LINES_AGGREGATED_WITH_ALL_PHYSICAL_LINE_NUMBERS"
            ),
            "source_residue_validation_policy": (
                "COLUMN_8_AND_COLUMN_9_PAIRWISE_ALL_OR_WHOLE_ROW_BLOCKED"
            ),
            "source_accession_policy": (
                "SOURCE_ACCESSION_IS_PROVENANCE_ONLY_AND_NEVER_SELECTED_WITHOUT_SIFTS"
            ),
            "excluded_inputs": [
                "UNMANIFESTED_SEGMENT_LEVEL_PDBe_MAPPING_CACHE",
                "NETWORK_RESPONSES",
            ],
            "required_future_evidence": [
                "RELEASE_MANIFESTED_REMEDIATED_RESIDUE_LEVEL_SIFTS_XML",
                "RELEASE_PINNED_PROTEIN_REFERENCE",
                "BIOLIP_PROVIDER_RELEASE_RECEIPT",
                "BIOLIP_RIGHTS_REVIEW",
            ],
            "source_artifacts": [
                _artifact_projection(artifacts["biolip"], role="BIOLIP_NONREDUNDANT_ANNOTATIONS"),
                _artifact_projection(artifacts["readme"], role="BIOLIP_21_COLUMN_README"),
            ],
            "source_snapshot_id": f"sha256:{artifacts['biolip'].sha256}",
            "source_release": None,
            "source_release_status": "MISSING_PROVIDER_RELEASE_RECEIPT",
            "source_license_status": "ACADEMIC_USE_NO_EXPLICIT_OPEN_LICENSE",
            "source_physical_line_count": source.physical_line_count,
            "source_unique_exact_line_count": len(source.rows),
            "source_duplicate_physical_line_count": source.physical_line_count - len(source.rows),
            "source_distinct_ligand_count": len(source.ligand_ids),
            "all_trait_count": len(traits),
            "all_trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(all_trait_binding_rows)
            ).hexdigest(),
            "no_example_trait_count": len(no_example_ids),
            "no_example_trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(no_example_binding_rows)
            ).hexdigest(),
            "trait_source_xref_status_counts": dict(
                sorted(Counter(binding.source_xref_status for binding in traits.values()).items())
            ),
            "selected_source_physical_line_count": selected_physical_count,
            "selected_unique_source_line_count": len(occurrences),
            "selected_duplicate_physical_line_count": selected_physical_count - len(occurrences),
            "ready_for_residue_level_sifts_count": len(ready),
            "source_residue_blocker_count": len(blocked),
            "source_residue_blocking_reason_counts": dict(
                sorted(
                    Counter(
                        reason
                        for row in blocked
                        for reason in row["source_residue_blocking_reasons"]
                    ).items()
                )
            ),
            "source_uniprot_claim_status_counts": dict(
                sorted(
                    Counter(
                        row["source_binding"]["source_uniprot_claim_status"] for row in occurrences
                    ).items()
                )
            ),
            "ready_unique_trait_count": len({row["trait_binding"]["trait_id"] for row in ready}),
            "blocked_unique_trait_count": len(
                {row["trait_binding"]["trait_id"] for row in blocked}
            ),
            "residue_level_sifts_fetch_request_count": len(fetch_requests),
            "residue_level_sifts_requested_pdb_ids_sha256": value_sha256(sorted(ready_by_pdb)),
            "occurrence_rows_sha256": hashlib.sha256(occurrence_bytes).hexdigest(),
            "fetch_request_rows_sha256": hashlib.sha256(fetch_bytes).hexdigest(),
            "combined_non_summary_rows_sha256": hashlib.sha256(
                occurrence_bytes + fetch_bytes
            ).hexdigest(),
        }
        summary["stage_id"] = "biolip-missing-protein-stage:" + value_sha256(summary)
        return StageResult(tuple(occurrences), tuple(fetch_requests), summary)
    finally:
        os.close(repo_binding.descriptor)


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows: list[str] = []
    if not summary_only:
        rows.extend(canonical_json(row) for row in result.occurrences)
        rows.extend(canonical_json(row) for row in result.fetch_requests)
    rows.append(canonical_json(result.summary))
    return "\n".join(rows) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--biolip", type=Path, default=DEFAULT_BIOLIP)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--traits-root", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument("--expected-biolip-sha256", default=EXPECTED_BIOLIP_SHA256)
    parser.add_argument("--expected-readme-sha256", default=EXPECTED_README_SHA256)
    parser.add_argument("--summary-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_stage(
            biolip_path=args.biolip,
            readme_path=args.readme,
            traits_root=args.traits_root,
            expected_source_sha256={
                "biolip": args.expected_biolip_sha256,
                "readme": args.expected_readme_sha256,
            },
        )
    except (OSError, BioLipStageError, ValueError) as error:
        print(f"refusing to stage BioLiP missing-protein candidates: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
