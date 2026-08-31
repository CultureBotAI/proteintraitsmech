#!/usr/bin/env python3
"""Strict, binary-safe parser for PRINTS 42.0 final motif sets.

PRINTS fingerprints are ordered sets of aligned motifs, not symbolic regular
expressions.  The release stores each final motif as ``fc/fl/ft/fd`` tagged
lines.  Operational position-frequency matrices and thresholds are derived
from those aligned ``fd`` peptides by PRINTS tooling.

The parser reads structural fields as ASCII, decodes descriptive source text
with the release's lossless single-byte encoding, and hashes the original bytes.
It deliberately fails closed: a missing or checksum-mismatched artefact, an
incomplete record, a malformed repeat marker, or any count/order/length mismatch
raises :class:`PrintsKdatError`.
"""

from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

PRINTS_42_0_RELEASE = "42.0"
PRINTS_42_0_SHA256 = "47b4f0c32002bce2f9b85f335c942cc52deae8bed54c2b4b2eec5e36c5810771"
PRINTS_42_0_SOURCE_ARTIFACT = "data/raw/interpro_members/prints42_0.kdat"
PRINTS_CANONICAL_STATUS = "CANONICAL_PRINTS_42_0_ARTIFACT"
PRINTS_NONCANONICAL_STATUS = "CHECKSUM_VERIFIED_NONCANONICAL_KDAT"
PRINTS_UNSEALED_STATUS = "UNSEALED_PUBLIC_CONSTRUCTION"

# Production identity is intentionally independent of the public compatibility
# constants above. A caller may monkeypatch those constants in a fixture, but
# cannot thereby turn arbitrary bytes into the reviewed production artefact.
_CANONICAL_RELEASE_FINGERPRINTS: Mapping[str, str] = MappingProxyType(
    {PRINTS_42_0_RELEASE: PRINTS_42_0_SHA256}
)
_PARSER_PROVENANCE_SEAL = object()

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ACCESSION_RE = re.compile(r"^PR[0-9]{5}$")
_MOTIF_CODE_RE = re.compile(r"^[A-Za-z0-9._ -]+$")
_COMPOUND_RE = re.compile(rb"^COMPOUND\s*\(\s*([0-9]+)\s*\)$")
_FD_RE = re.compile(
    rb"^fd;\s+([A-Z]+)\s+(\S+)\s+(-?[0-9]+)\s+(-?[0-9]+)"
    rb"(?:\s+\*\*/R([0-9]+)\*\*)?\s*$"
)
_KD_RE = re.compile(
    rb"^KD; INTER_MOTIF_DISTANCE REGION=([0-9]+)-([0-9]+); "
    rb"MIN=(-?[0-9]+); MAX=(-?[0-9]+)(\s+/R)?$"
)


class PrintsKdatError(ValueError):
    """The pinned PRINTS source is absent, corrupt, or semantically inconsistent."""


class PrintsChecksumError(PrintsKdatError):
    """The source bytes do not match the caller's pinned SHA-256."""


@dataclass(frozen=True, slots=True)
class PrintsMotifInstance:
    """One aligned ``fd`` training row from a final motif set."""

    sequence: str
    protein_code: str
    position: int
    distance_from_previous: int
    repeat_number: int | None = None


@dataclass(frozen=True, slots=True)
class PrintsInterMotifDistanceConstraint:
    """One source-declared ``KD`` inter-motif distance constraint.

    ``repeat_qualified`` preserves the literal source ``/R`` qualifier.  It is
    metadata from PRINTS, not a claim that this parser enforces the constraint
    while matching sequences.
    """

    region_start_ordinal: int
    region_end_ordinal: int
    minimum: int
    maximum: int
    repeat_qualified: bool


@dataclass(frozen=True, slots=True)
class PrintsMotif:
    """One validated final motif block in source order."""

    ordinal: int
    code: str
    length: int
    description: str
    instances: tuple[PrintsMotifInstance, ...]
    source_motif_sha256: str
    training_distance_from_previous_min: int
    training_distance_from_previous_max: int
    inter_motif_distance_constraint: PrintsInterMotifDistanceConstraint | None = None


@dataclass(frozen=True, slots=True)
class PrintsFingerprint:
    """One validated PRINTS record and its ordered final motif sets."""

    accession: str
    alternate_accessions: tuple[str, ...]
    code: str
    title: str
    description: str
    declared_motif_count: int
    motifs: tuple[PrintsMotif, ...]
    source_record_sha256: str


@dataclass(frozen=True, slots=True)
class _ParsedReleaseProvenance:
    """Private binding between parser output and one immutable byte capture."""

    seal: object
    release: str
    source_path: Path
    source_artifact_sha256: str
    source_artifact_size: int
    canonical_status: str
    fingerprints: Mapping[str, PrintsFingerprint]


@dataclass(frozen=True, slots=True)
class PrintsRelease:
    """A checksum-verified PRINTS KDAT artefact.

    Public construction remains available for type-level fixtures, but only
    :func:`parse_prints_kdat` creates the private provenance binding required by
    production projections. The mapping is made read-only in every instance;
    its values are frozen dataclasses containing tuples.
    """

    release: str
    source_path: Path
    source_artifact_sha256: str
    fingerprints: Mapping[str, PrintsFingerprint]
    source_artifact_size: int | None = None
    canonical_status: str = PRINTS_UNSEALED_STATUS
    _parsed_provenance: _ParsedReleaseProvenance | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.fingerprints, MappingProxyType):
            object.__setattr__(
                self,
                "fingerprints",
                MappingProxyType(dict(self.fingerprints)),
            )


def _require_bound_release(release: PrintsRelease, *, canonical: bool) -> None:
    provenance = release._parsed_provenance
    if provenance is None or provenance.seal is not _PARSER_PROVENANCE_SEAL:
        raise PrintsKdatError("PRINTS release was not created by the checksum-verifying parser")
    if (
        release.release != provenance.release
        or release.source_path != provenance.source_path
        or release.source_artifact_sha256 != provenance.source_artifact_sha256
        or release.source_artifact_size != provenance.source_artifact_size
        or release.canonical_status != provenance.canonical_status
        or release.fingerprints is not provenance.fingerprints
    ):
        raise PrintsKdatError("PRINTS release fields were reparented from their parser provenance")
    if canonical and release.canonical_status != PRINTS_CANONICAL_STATUS:
        raise PrintsKdatError(
            "PRINTS representation requires the canonical checksum-pinned 42.0 artefact; "
            f"got {release.canonical_status}"
        )


def build_fingerprint_representation(
    release: PrintsRelease,
    fingerprint: PrintsFingerprint,
) -> dict[str, Any]:
    """Project one parsed fingerprint into the canonical KDAT summary.

    The fingerprint must be the object owned by ``release``.  Refusing an
    independently constructed or cross-release object keeps record-level and
    artifact-level digests bound to the same checksum-verified source.  The
    result intentionally does not claim to replay a versioned matcher or the
    separate InterProScan PRINTS post-processing policy.
    """

    _require_bound_release(release, canonical=True)
    authoritative = release.fingerprints.get(fingerprint.accession)
    if authoritative is not fingerprint:
        raise PrintsKdatError(
            f"{fingerprint.accession}: fingerprint is not owned by the supplied "
            "checksum-verified PRINTS release"
        )
    return {
        "source_accession": f"PRINTS:{fingerprint.accession}",
        "source_release": release.release,
        "representation_type": "PRINTS_FINAL_ORDERED_MOTIF_SETS",
        "source_artifact": PRINTS_42_0_SOURCE_ARTIFACT,
        "source_artifact_sha256": release.source_artifact_sha256,
        "source_record_sha256": fingerprint.source_record_sha256,
        "compatible_derivation_tool_hint": "EMBOSS_PRINTSEXTRACT",
        "motif_count": fingerprint.declared_motif_count,
        "motifs": [
            {
                "ordinal": motif.ordinal,
                "motif_code": motif.code,
                "length": motif.length,
                "description": motif.description,
                "training_instance_count": len(motif.instances),
                "source_motif_sha256": motif.source_motif_sha256,
                "training_distance_from_previous_min": (motif.training_distance_from_previous_min),
                "training_distance_from_previous_max": (motif.training_distance_from_previous_max),
                **(
                    {
                        "inter_motif_distance_constraint": {
                            "region_start_ordinal": (
                                motif.inter_motif_distance_constraint.region_start_ordinal
                            ),
                            "region_end_ordinal": (
                                motif.inter_motif_distance_constraint.region_end_ordinal
                            ),
                            "minimum": motif.inter_motif_distance_constraint.minimum,
                            "maximum": motif.inter_motif_distance_constraint.maximum,
                            "repeat_qualified": (
                                motif.inter_motif_distance_constraint.repeat_qualified
                            ),
                        }
                    }
                    if motif.inter_motif_distance_constraint is not None
                    else {}
                ),
            }
            for motif in fingerprint.motifs
        ],
    }


@dataclass(slots=True)
class _MotifBuilder:
    code: str
    line_number: int
    raw_hash: Any = field(default_factory=hashlib.sha256)
    length: int | None = None
    description: str | None = None
    instances: list[PrintsMotifInstance] = field(default_factory=list)
    inter_motif_distance_constraint: PrintsInterMotifDistanceConstraint | None = None


@dataclass(slots=True)
class _RecordBuilder:
    code: str
    line_number: int
    raw_hash: Any = field(default_factory=hashlib.sha256)
    accessions: tuple[str, ...] | None = None
    declared_motif_count: int | None = None
    title: str | None = None
    description_lines: list[str] = field(default_factory=list)
    in_final_motifs: bool = False
    motifs: list[PrintsMotif] = field(default_factory=list)
    current_motif: _MotifBuilder | None = None


def _source_text(raw: bytes) -> str:
    """Decode descriptive text without replacement or byte loss.

    PRINTS 42.0 is a single-byte flat file (it contains, for example, a literal
    ``0xC5`` Angstrom sign), not UTF-8.  Latin-1 gives a reversible mapping for
    every byte; exact provenance remains bound to the raw-byte digests.
    """

    return raw.decode("latin-1")


def _value(raw_line: bytes) -> bytes:
    return raw_line[3:].strip()


def _fail(path: Path, line_number: int, message: str) -> PrintsKdatError:
    return PrintsKdatError(f"{path}:{line_number}: {message}")


def _ascii(path: Path, line_number: int, value: bytes, field_name: str) -> str:
    try:
        return value.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise _fail(path, line_number, f"non-ASCII bytes in {field_name}") from error


def _read_source_bytes(path: Path) -> bytes:
    """Capture a source exactly once so checksum and parser see identical bytes."""

    try:
        with path.open("rb") as handle:
            return handle.read()
    except FileNotFoundError as error:
        raise PrintsKdatError(f"missing pinned PRINTS source: {path}") from error
    except OSError as error:
        raise PrintsKdatError(f"cannot read pinned PRINTS source {path}: {error}") from error


def _finish_motif(path: Path, record: _RecordBuilder) -> None:
    motif = record.current_motif
    if motif is None:
        return
    if motif.length is None:
        raise _fail(path, motif.line_number, f"motif {motif.code} has no fl length")
    if motif.description is None or not motif.description.strip():
        raise _fail(path, motif.line_number, f"motif {motif.code} has no ft description")
    if not motif.instances:
        raise _fail(path, motif.line_number, f"motif {motif.code} has no fd instances")
    distances = [instance.distance_from_previous for instance in motif.instances]
    record.motifs.append(
        PrintsMotif(
            ordinal=len(record.motifs) + 1,
            code=motif.code,
            length=motif.length,
            description=motif.description,
            instances=tuple(motif.instances),
            source_motif_sha256=motif.raw_hash.hexdigest(),
            training_distance_from_previous_min=min(distances),
            training_distance_from_previous_max=max(distances),
            inter_motif_distance_constraint=motif.inter_motif_distance_constraint,
        )
    )
    record.current_motif = None


def _finish_record(
    path: Path,
    record: _RecordBuilder | None,
    fingerprints: dict[str, PrintsFingerprint],
    line_number: int,
) -> None:
    if record is None:
        return
    _finish_motif(path, record)
    if record.accessions is None:
        raise _fail(path, record.line_number, f"record {record.code} has no gx accession")
    accession = record.accessions[0]
    if record.title is None or not record.title.strip():
        raise _fail(path, record.line_number, f"record {accession} has no gt title")
    if record.declared_motif_count is None:
        raise _fail(path, record.line_number, f"record {accession} has no gn count")
    if record.declared_motif_count < 2:
        raise _fail(
            path,
            record.line_number,
            f"record {accession} declares fewer than two fingerprint motifs",
        )
    if not record.in_final_motifs:
        raise _fail(path, record.line_number, f"record {accession} has no final motif set")
    if len(record.motifs) != record.declared_motif_count:
        raise _fail(
            path,
            record.line_number,
            f"record {accession} declares {record.declared_motif_count} motifs "
            f"but contains {len(record.motifs)} final fc blocks",
        )
    prior_accessions = {
        source_accession
        for fingerprint in fingerprints.values()
        for source_accession in (fingerprint.accession, *fingerprint.alternate_accessions)
    }
    duplicated = prior_accessions.intersection(record.accessions)
    if duplicated:
        raise _fail(path, record.line_number, f"duplicate gx accession {sorted(duplicated)[0]}")

    description = " ".join(" ".join(record.description_lines).split())
    if not description:
        raise _fail(path, record.line_number, f"record {accession} has no gd description")
    fingerprints[accession] = PrintsFingerprint(
        accession=accession,
        alternate_accessions=record.accessions[1:],
        code=record.code,
        title=record.title,
        description=description,
        declared_motif_count=record.declared_motif_count,
        motifs=tuple(record.motifs),
        source_record_sha256=record.raw_hash.hexdigest(),
    )


def parse_prints_kdat(path: str | Path, expected_sha256: str) -> PrintsRelease:
    """Parse a checksum-pinned PRINTS 42.0 KDAT file.

    Raw record digests cover bytes from ``gc;`` through the byte immediately
    before the next ``gc;`` (or EOF). Raw motif digests cover only the source
    ``fc/fl/ft/fd/KD`` lines, including their original line endings; the ``bb;``
    separator is excluded.
    """

    source_path = Path(path)
    if not _SHA256_RE.fullmatch(expected_sha256):
        raise PrintsKdatError(
            f"expected SHA-256 must be 64 lower-case hexadecimal characters: {expected_sha256!r}"
        )
    source_bytes = _read_source_bytes(source_path)
    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise PrintsChecksumError(
            f"PRINTS source checksum mismatch for {source_path}: expected "
            f"{expected_sha256}, got {actual_sha256}"
        )

    fingerprints: dict[str, PrintsFingerprint] = {}
    record: _RecordBuilder | None = None
    line_number = 0
    # BytesIO parses the same immutable capture used for the artifact digest.
    with io.BytesIO(source_bytes) as handle:
        for line_number, raw_line in enumerate(handle, 1):
            tag = raw_line[:3]
            if tag == b"gc;":
                _finish_record(source_path, record, fingerprints, line_number - 1)
                code = _source_text(_value(raw_line))
                if not code:
                    raise _fail(source_path, line_number, "empty gc record code")
                record = _RecordBuilder(code=code, line_number=line_number)
                record.raw_hash.update(raw_line)
                continue

            if record is None:
                if raw_line.strip():
                    raise _fail(source_path, line_number, "content before the first gc record")
                continue
            record.raw_hash.update(raw_line)

            if tag == b"gx;":
                if record.accessions is not None:
                    raise _fail(source_path, line_number, "duplicate gx tag")
                accession_text = _ascii(source_path, line_number, _value(raw_line), "gx accession")
                accessions = tuple(part.strip() for part in accession_text.split(";"))
                if not accessions or any(not _ACCESSION_RE.fullmatch(item) for item in accessions):
                    raise _fail(
                        source_path, line_number, f"invalid PRINTS accessions {accessions!r}"
                    )
                if len(set(accessions)) != len(accessions):
                    raise _fail(
                        source_path, line_number, f"duplicate accession on gx line {accessions!r}"
                    )
                record.accessions = accessions
                continue
            if tag == b"gn;":
                if record.declared_motif_count is not None:
                    raise _fail(source_path, line_number, "duplicate gn tag")
                match = _COMPOUND_RE.fullmatch(_value(raw_line))
                if match is None:
                    raise _fail(source_path, line_number, "malformed gn COMPOUND count")
                record.declared_motif_count = int(match.group(1))
                continue
            if tag == b"gt;":
                if record.title is not None:
                    raise _fail(source_path, line_number, "duplicate gt tag")
                record.title = _source_text(_value(raw_line))
                continue
            if tag == b"gd;":
                record.description_lines.append(_source_text(_value(raw_line)))
                continue
            if tag == b"fm;":
                marker = _value(raw_line)
                if marker == b"FINAL MOTIF-SETS":
                    if record.in_final_motifs:
                        raise _fail(source_path, line_number, "duplicate FINAL MOTIF-SETS marker")
                    record.in_final_motifs = True
                elif record.in_final_motifs and marker.strip(b"-"):
                    raise _fail(source_path, line_number, f"unexpected fm line {marker!r}")
                continue
            if not record.in_final_motifs:
                continue

            if tag == b"bb;":
                continue
            if tag == b"fc;":
                _finish_motif(source_path, record)
                code = _ascii(source_path, line_number, _value(raw_line), "fc motif code")
                if not _MOTIF_CODE_RE.fullmatch(code):
                    raise _fail(source_path, line_number, f"invalid final motif code {code!r}")
                record.current_motif = _MotifBuilder(code=code, line_number=line_number)
                record.current_motif.raw_hash.update(raw_line)
                continue

            motif = record.current_motif
            if motif is None:
                raise _fail(source_path, line_number, f"{tag!r} appears before a final fc block")
            if tag in {b"fl;", b"ft;", b"fd;", b"KD;"}:
                motif.raw_hash.update(raw_line)
            else:
                raise _fail(source_path, line_number, f"unexpected tag {tag!r} in final motif sets")

            if tag == b"fl;":
                if motif.length is not None or motif.description is not None or motif.instances:
                    raise _fail(
                        source_path, line_number, f"out-of-order or duplicate fl for {motif.code}"
                    )
                try:
                    length = int(_value(raw_line))
                except ValueError as error:
                    raise _fail(
                        source_path, line_number, f"non-integer fl for {motif.code}"
                    ) from error
                if length < 1:
                    raise _fail(source_path, line_number, f"non-positive fl for {motif.code}")
                motif.length = length
                continue
            if tag == b"ft;":
                if motif.length is None or motif.description is not None or motif.instances:
                    raise _fail(
                        source_path, line_number, f"out-of-order or duplicate ft for {motif.code}"
                    )
                motif.description = _source_text(_value(raw_line))
                continue
            if tag == b"fd;":
                if (
                    motif.length is None
                    or motif.description is None
                    or motif.inter_motif_distance_constraint is not None
                ):
                    raise _fail(source_path, line_number, f"out-of-order fd for {motif.code}")
                match = _FD_RE.fullmatch(raw_line.rstrip(b"\r\n"))
                if match is None:
                    raise _fail(source_path, line_number, f"malformed fd row for {motif.code}")
                sequence = _ascii(source_path, line_number, match.group(1), "fd peptide")
                protein_code = _ascii(source_path, line_number, match.group(2), "fd protein code")
                position = int(match.group(3))
                distance = int(match.group(4))
                repeat_number = int(match.group(5)) if match.group(5) is not None else None
                if len(sequence) != motif.length:
                    raise _fail(
                        source_path,
                        line_number,
                        f"fd peptide length {len(sequence)} != fl {motif.length} for {motif.code}",
                    )
                if position < 1:
                    raise _fail(
                        source_path, line_number, f"non-positive fd position for {motif.code}"
                    )
                if repeat_number is not None and repeat_number < 1:
                    raise _fail(source_path, line_number, f"invalid repeat marker for {motif.code}")
                motif.instances.append(
                    PrintsMotifInstance(
                        sequence=sequence,
                        protein_code=protein_code,
                        position=position,
                        distance_from_previous=distance,
                        repeat_number=repeat_number,
                    )
                )
                continue
            if tag == b"KD;":
                if not motif.instances or motif.inter_motif_distance_constraint is not None:
                    raise _fail(
                        source_path, line_number, f"out-of-order or duplicate KD for {motif.code}"
                    )
                match = _KD_RE.fullmatch(raw_line.rstrip(b"\r\n"))
                if match is None:
                    raise _fail(source_path, line_number, f"malformed KD row for {motif.code}")
                region_start = int(match.group(1))
                region_end = int(match.group(2))
                minimum = int(match.group(3))
                maximum = int(match.group(4))
                ordinal = len(record.motifs) + 1
                expected_region = (ordinal - 1, ordinal)
                if (region_start, region_end) != expected_region:
                    raise _fail(
                        source_path,
                        line_number,
                        f"KD REGION {region_start}-{region_end} for {motif.code} must be "
                        f"{expected_region[0]}-{expected_region[1]}",
                    )
                if minimum > maximum:
                    raise _fail(
                        source_path,
                        line_number,
                        f"KD MIN {minimum} exceeds MAX {maximum} for {motif.code}",
                    )
                motif.inter_motif_distance_constraint = PrintsInterMotifDistanceConstraint(
                    region_start_ordinal=region_start,
                    region_end_ordinal=region_end,
                    minimum=minimum,
                    maximum=maximum,
                    repeat_qualified=match.group(5) is not None,
                )

    _finish_record(source_path, record, fingerprints, line_number)
    if not fingerprints:
        raise PrintsKdatError(f"{source_path}: no PRINTS records found")
    immutable_fingerprints: Mapping[str, PrintsFingerprint] = MappingProxyType(dict(fingerprints))
    canonical_status = (
        PRINTS_CANONICAL_STATUS
        if actual_sha256 == _CANONICAL_RELEASE_FINGERPRINTS[PRINTS_42_0_RELEASE]
        else PRINTS_NONCANONICAL_STATUS
    )
    provenance = _ParsedReleaseProvenance(
        seal=_PARSER_PROVENANCE_SEAL,
        release=PRINTS_42_0_RELEASE,
        source_path=source_path,
        source_artifact_sha256=actual_sha256,
        source_artifact_size=len(source_bytes),
        canonical_status=canonical_status,
        fingerprints=immutable_fingerprints,
    )
    return PrintsRelease(
        release=provenance.release,
        source_path=provenance.source_path,
        source_artifact_sha256=provenance.source_artifact_sha256,
        fingerprints=immutable_fingerprints,
        source_artifact_size=provenance.source_artifact_size,
        canonical_status=provenance.canonical_status,
        _parsed_provenance=provenance,
    )
