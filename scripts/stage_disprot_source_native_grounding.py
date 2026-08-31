#!/usr/bin/env python3
"""Stage pinned DisProt IDPO regions against local UniProt sequence material.

This is a read-only, candidate-only boundary.  It replays every IDPO region in
the pinned local DisProt JSON array, verifies the current 32 IDPO trait
projections and their historical top-30 example selection, compares the source
sequence with the pinned UniProt residue frame and exact local
ProteinReferences, and emits canonical JSONL only to stdout.

The DisProt bytes were fetched through a mutable ``release=current`` endpoint
and have no bound provider acquisition receipt or global release identifier.
Per-entry and per-region ``released`` values are preserved as source metadata;
they are never promoted to ``source_release``.  Source coordinates are treated
as one-based closed because that convention reproduces the source sequence and
the existing seeder, but the export does not declare it.  Sparse ``term_def``
fields are also preserved but never used to repair trait definitions.

One staging row is retained for every source IDPO ``region_id``.  Duplicate
coordinates therefore remain distinct through their citations, ECO assertions,
experimental context, and region identities.  Exact local matches are emitted
only as ``CANDIDATE_ONLY`` objects.  This command has no network, output-file,
fetch, apply, promotion, or GroundingEvidence writer mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_uniprot_grounding as grounding  # noqa: E402
from yaml_emit import slugify as _slugify  # noqa: E402

SCHEMA_VERSION = 1
OCCURRENCE_KIND = "DISPROT_SOURCE_NATIVE_OCCURRENCE"
REQUEST_KIND = "DISPROT_PROTEIN_REFERENCE_REQUEST"
SUMMARY_KIND = "DISPROT_SOURCE_NATIVE_STAGE_SUMMARY"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "data/raw/disprot.entries.json"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data/traits"
DEFAULT_RESIDUE_FRAME = REPO_ROOT / "data/raw/align_cache/residue_frame.json"
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data/grounding/protein_registry.jsonl"

EXPECTED_SOURCE_SHA256 = "aeb8773ae59b2f569203c13a6515d3c2b1374168bd921f63daf4c2a0543e8844"
EXPECTED_FRAME_SHA256 = "35f053876b234b92267c0f18e94bc8f085316f39343aa98668b714c610ba7848"
EXPECTED_UNIPROT_RELEASE = "2026_02"

SOURCE_URL_DECLARED_BY_REPOSITORY = "https://disprot.org/api/search?release=current&format=json"
TRAIT_DEFINITION_SOURCE = "DisProt (Tosatto lab, U. Padova; IDPO-classed, proteins as examples)"
TRAIT_LICENSE = "CC-BY-4.0"
EXAMPLES_CAP = 30

NAMESPACE_GROUPS: dict[str, tuple[str, str, str, str]] = {
    "Structural state": (
        "proteintraitsmech:IDPO_STRUCTURAL_STATE",
        "disorder structural state",
        "A structural state of an intrinsically disordered region "
        "(disorder, order, molten globule, pre-molten globule).",
        "disorder-structural-state.yaml",
    ),
    "Structural transition": (
        "proteintraitsmech:IDPO_STRUCTURAL_TRANSITION",
        "disorder structural transition",
        "A conformational transition of a disordered region (e.g. disorder-to-order upon binding).",
        "disorder-structural-transition.yaml",
    ),
    "Disorder function": (
        "proteintraitsmech:IDPO_DISORDER_FUNCTION",
        "disorder-based function",
        "A function performed by an intrinsically disordered region "
        "(flexible linker/tail, PTM display site, self-regulation, "
        "molecular recognition, assembly).",
        "disorder-based-function.yaml",
    ),
}

MISSING_PROVIDER_RECEIPT = "MISSING_DISPROT_PROVIDER_ACQUISITION_RECEIPT"
MISSING_REGISTRY_RECEIPT = "MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT"
MUTABLE_PROVIDER_RELEASE = "DISPROT_SOURCE_USES_MUTABLE_RELEASE_CURRENT"
NO_GLOBAL_PROVIDER_RELEASE = "DISPROT_EXPORT_HAS_NO_GLOBAL_PROVIDER_RELEASE"
EXPORT_COMPLETENESS_UNKNOWN = "DISPROT_EXPORT_COMPLETENESS_NOT_ESTABLISHED"
INFERRED_COORDINATES = "ONE_BASED_CLOSED_COORDINATES_INFERRED_NOT_PROVIDER_DECLARED"
MISSING_IDPO_SNAPSHOT = "AUTHORITATIVE_IDPO_ONTOLOGY_SNAPSHOT_NOT_AVAILABLE"
MISSING_PROTEIN_REFERENCE = "MISSING_EXPECTED_RELEASE_LOCAL_PROTEIN_REFERENCE"
NOT_IN_FRAME = "SOURCE_PROTEIN_NOT_IN_LOCAL_RESIDUE_FRAME"
FRAME_SEQUENCE_MISMATCH = "SOURCE_RESIDUE_FRAME_SEQUENCE_MISMATCH"
REGISTRY_SEQUENCE_MISMATCH = "SOURCE_PROTEIN_REFERENCE_SEQUENCE_MISMATCH"
REGISTRY_TAXON_MISMATCH = "SOURCE_PROTEIN_REFERENCE_TAXON_MISMATCH"
STRUCTURED_CONTEXT_REVIEW = "STRUCTURED_EXPERIMENTAL_CONTEXT_REQUIRES_REVIEW"
CONSTRUCT_CONTEXT_REVIEW = "CONSTRUCT_OR_CONSTRUCT_SEQUENCE_REQUIRES_REVIEW"
UNIPROT_CHANGED_REVIEW = "DISPROT_UNIPROT_CHANGED_FLAG_REQUIRES_REVIEW"
TERM_NOT_ANNOTATE_REVIEW = "DISPROT_TERM_NOT_ANNOTATE_FLAG_REQUIRES_REVIEW"

GLOBAL_PROMOTION_BLOCKERS = (
    MISSING_PROVIDER_RECEIPT,
    MISSING_REGISTRY_RECEIPT,
    MUTABLE_PROVIDER_RELEASE,
    NO_GLOBAL_PROVIDER_RELEASE,
    EXPORT_COMPLETENESS_UNKNOWN,
    INFERRED_COORDINATES,
    MISSING_IDPO_SNAPSHOT,
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DISPROT_ID_RE = re.compile(r"^DP[0-9]{5}$")
_REGION_ID_RE = re.compile(r"^DP[0-9]{5}r[0-9]{3}$")
_IDPO_RE = re.compile(r"^IDPO:[0-9]{7}$")
_GO_RE = re.compile(r"^GO:[0-9]{7}$")
_ECO_RE = re.compile(r"^ECO:[0-9]{7}$")
_UNIPROT_RE = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[1-9][0-9]*)?$"
)
_UNIPROT_RELEASE_RE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
_SEQUENCE_RE = re.compile(r"^[A-Z]+$")


class DisProtStageError(ValueError):
    """A source, trait, sequence-frame, registry, or filesystem check failed."""


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
class DisProtTerm:
    term_id: str
    name: str
    namespace: str


@dataclass(frozen=True)
class DisProtEntry:
    source_index: int
    accession: str
    protein_id: str
    disprot_id: str
    name: str
    taxon_id: int
    organism: str
    sequence: str
    sequence_sha256: str
    released: Any
    regions_counter: int
    raw_sha256: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class DisProtRegion:
    entry: DisProtEntry
    source_region_index: int
    region_id: str
    start: int
    end: int
    term: DisProtTerm
    raw_sha256: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class ParsedSource:
    entries: tuple[DisProtEntry, ...]
    idpo_regions: tuple[DisProtRegion, ...]
    terms: Mapping[str, DisProtTerm]
    stats: Mapping[str, Any]


@dataclass(frozen=True)
class ResidueFrame:
    release: str
    proteins: Mapping[str, Mapping[str, Any]]
    absent: frozenset[str]
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class TraitBinding:
    trait_id: str
    parent_trait_id: str
    relative_path: str
    sha256: str
    label: str
    namespace: str


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
        raise DisProtStageError(
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
        raise DisProtStageError(
            f"{description} escapes bound root {lexical_root}: {lexical_path}"
        ) from error
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise DisProtStageError(f"invalid relative {description} path: {relative}")
    return relative


def _bind_absolute_directory(path: Path, *, description: str) -> BoundDirectory:
    directory_flags, _ = _descriptor_safety_flags()
    lexical_path = _lexical_absolute(path)
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
        raise DisProtStageError(
            f"cannot bind {description} without following symlinks {lexical_path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise DisProtStageError(f"{description} must be a directory: {lexical_path}")
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
        raise DisProtStageError(
            f"cannot bind {description} without following symlinks {path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise DisProtStageError(f"{description} must be a directory: {path}")
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
            raise DisProtStageError(f"{description} binding changed while staging: {binding.path}")
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
        raise DisProtStageError(f"invalid relative {description} path: {relative_path}")
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
            raise DisProtStageError(f"{description} must be a regular file: {display_path}")
        chunks: list[bytes] = []
        while chunk := os.read(file_descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise DisProtStageError(f"{description} changed while reading: {display_path}")
        return b"".join(chunks)
    except DisProtStageError:
        raise
    except OSError as error:
        raise DisProtStageError(
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
        raise DisProtStageError(f"invalid pinned sha256 for {description}: {expected_sha256!r}")
    relative = _relative_under(path, bound_root.path, description=description)
    raw = _read_relative_bytes(
        bound_root,
        relative,
        display_path=_lexical_absolute(path),
        description=description,
    )
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise DisProtStageError(
            f"{description} SHA-256 mismatch for {path}: expected {expected_sha256}, "
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
        raise DisProtStageError(
            f"{description} drifted while staging: {artifact.path}; "
            f"expected {artifact.sha256}, observed {observed}"
        )


def _strict_json_value(raw: bytes | str, *, source: str) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise DisProtStageError(f"{source}: duplicate key {key!r} in JSON object")
            result[key] = value
        return result

    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(
            text,
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                DisProtStageError(f"{source}: non-finite JSON number {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, DisProtStageError) as error:
        raise DisProtStageError(f"{source}: invalid JSON: {error}") from error


def _require_mapping(value: Any, *, source: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DisProtStageError(f"{source}: expected an object")
    return value


def _require_string(value: Any, *, source: str) -> str:
    if not isinstance(value, str) or not value:
        raise DisProtStageError(f"{source}: expected a non-empty string")
    return value


def _require_int(value: Any, *, source: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise DisProtStageError(f"{source}: expected an integer >= {minimum}")
    return value


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _has_structured_context(raw: Mapping[str, Any]) -> bool:
    return any(
        _nonempty_list(raw.get(field))
        for field in (
            "annotation_extensions",
            "conditions",
            "construct_alterations",
            "interaction_partner",
            "sample",
            "states_connection",
        )
    ) or bool(raw.get("sequence_construct"))


def _has_construct_context(raw: Mapping[str, Any]) -> bool:
    return _nonempty_list(raw.get("construct_alterations")) or bool(raw.get("sequence_construct"))


def parse_disprot_source(artifact: CapturedArtifact) -> ParsedSource:
    value = _strict_json_value(artifact.raw, source=artifact.relative_path)
    if not isinstance(value, list):
        raise DisProtStageError(
            f"{artifact.relative_path}: DisProt export must be a top-level array"
        )
    entries: list[DisProtEntry] = []
    idpo_regions: list[DisProtRegion] = []
    terms: dict[str, DisProtTerm] = {}
    entry_ids: set[str] = set()
    accessions: set[str] = set()
    region_ids: set[str] = set()
    eco_names: dict[str, str] = {}
    total_regions = 0
    ontology_counts: Counter[str] = Counter()
    citation_counts: Counter[str] = Counter()
    counter_excess_entry_count = 0
    counter_excess_total = 0

    for entry_index, raw_entry_value in enumerate(value):
        source = f"{artifact.relative_path}:entry[{entry_index}]"
        raw_entry = _require_mapping(raw_entry_value, source=source)
        accession = _require_string(raw_entry.get("acc"), source=f"{source}.acc")
        if _UNIPROT_RE.fullmatch(accession) is None or accession in accessions:
            raise DisProtStageError(f"{source}: invalid or duplicate UniProt accession")
        disprot_id = _require_string(raw_entry.get("disprot_id"), source=f"{source}.disprot_id")
        if _DISPROT_ID_RE.fullmatch(disprot_id) is None or disprot_id in entry_ids:
            raise DisProtStageError(f"{source}: invalid or duplicate DisProt identity")
        sequence = _require_string(raw_entry.get("sequence"), source=f"{source}.sequence")
        if _SEQUENCE_RE.fullmatch(sequence) is None:
            raise DisProtStageError(f"{source}: invalid source protein sequence")
        length = _require_int(raw_entry.get("length"), source=f"{source}.length", minimum=1)
        if len(sequence) != length:
            raise DisProtStageError(f"{source}: source sequence length disagrees with length")
        name = _require_string(raw_entry.get("name"), source=f"{source}.name")
        taxon_id = _require_int(
            raw_entry.get("ncbi_taxon_id"), source=f"{source}.ncbi_taxon_id", minimum=1
        )
        organism = _require_string(raw_entry.get("organism"), source=f"{source}.organism")
        raw_regions = raw_entry.get("regions")
        if not isinstance(raw_regions, list):
            raise DisProtStageError(f"{source}.regions: expected an array")
        regions_counter = _require_int(
            raw_entry.get("regions_counter"),
            source=f"{source}.regions_counter",
            minimum=0,
        )
        if regions_counter < len(raw_regions):
            raise DisProtStageError(
                f"{source}: regions_counter is smaller than the physical region array"
            )
        if regions_counter > len(raw_regions):
            counter_excess_entry_count += 1
            counter_excess_total += regions_counter - len(raw_regions)

        entry = DisProtEntry(
            source_index=entry_index,
            accession=accession,
            protein_id=f"UniProtKB:{accession}",
            disprot_id=disprot_id,
            name=name,
            taxon_id=taxon_id,
            organism=organism,
            sequence=sequence,
            sequence_sha256=hashlib.sha256(sequence.encode("ascii")).hexdigest(),
            released=raw_entry.get("released"),
            regions_counter=regions_counter,
            raw_sha256=value_sha256(raw_entry),
            raw=raw_entry,
        )
        entries.append(entry)
        accessions.add(accession)
        entry_ids.add(disprot_id)

        for region_index, raw_region_value in enumerate(raw_regions):
            region_source = f"{source}.regions[{region_index}]"
            raw_region = _require_mapping(raw_region_value, source=region_source)
            region_id = _require_string(
                raw_region.get("region_id"), source=f"{region_source}.region_id"
            )
            if (
                _REGION_ID_RE.fullmatch(region_id) is None
                or not region_id.startswith(f"{disprot_id}r")
                or region_id in region_ids
            ):
                raise DisProtStageError(f"{region_source}: invalid or duplicate region identity")
            region_ids.add(region_id)
            total_regions += 1
            start = _require_int(
                raw_region.get("start"), source=f"{region_source}.start", minimum=1
            )
            end = _require_int(raw_region.get("end"), source=f"{region_source}.end", minimum=1)
            if end < start or end > len(sequence):
                raise DisProtStageError(
                    f"{region_source}: source coordinate is outside protein bounds"
                )
            ontology = _require_string(
                raw_region.get("term_ontology"),
                source=f"{region_source}.term_ontology",
            )
            if ontology not in {"IDPO", "GO"}:
                raise DisProtStageError(f"{region_source}: unknown term ontology")
            ontology_counts[ontology] += 1
            term_id = _require_string(raw_region.get("term_id"), source=f"{region_source}.term_id")
            expected_term_re = _IDPO_RE if ontology == "IDPO" else _GO_RE
            if expected_term_re.fullmatch(term_id) is None:
                raise DisProtStageError(f"{region_source}: malformed {ontology} term identity")
            if ontology != "IDPO":
                continue

            term_name = _require_string(
                raw_region.get("term_name"), source=f"{region_source}.term_name"
            )
            namespace = _require_string(
                raw_region.get("term_namespace"),
                source=f"{region_source}.term_namespace",
            )
            if (
                namespace not in NAMESPACE_GROUPS
                or raw_region.get("disprot_namespace") != namespace
            ):
                raise DisProtStageError(f"{region_source}: invalid or conflicting IDPO namespace")
            observed_term = DisProtTerm(term_id, term_name, namespace)
            previous = terms.get(term_id)
            if previous is not None and previous != observed_term:
                raise DisProtStageError(f"{region_source}: IDPO term identity/name/namespace drift")
            terms[term_id] = observed_term

            reference_source = _require_string(
                raw_region.get("reference_source"),
                source=f"{region_source}.reference_source",
            )
            if reference_source not in {"pmid", "mobidb", "doi"}:
                raise DisProtStageError(f"{region_source}: unknown reference source")
            _require_string(
                raw_region.get("reference_id"),
                source=f"{region_source}.reference_id",
            )
            citation_counts[reference_source] += 1
            eco_id = _require_string(raw_region.get("ec_id"), source=f"{region_source}.ec_id")
            eco_name = _require_string(raw_region.get("ec_name"), source=f"{region_source}.ec_name")
            if _ECO_RE.fullmatch(eco_id) is None or raw_region.get("ec_ontology") != "ECO":
                raise DisProtStageError(f"{region_source}: invalid ECO assertion")
            prior_eco_name = eco_names.get(eco_id)
            if prior_eco_name is not None and prior_eco_name != eco_name:
                raise DisProtStageError(f"{region_source}: ECO ID/name drift")
            eco_names[eco_id] = eco_name
            for field in (
                "annotation_extensions",
                "conditions",
                "construct_alterations",
                "cross_refs",
                "interaction_partner",
                "sample",
                "statement",
                "states_connection",
            ):
                field_value = raw_region.get(field)
                if field_value is not None and not isinstance(field_value, list):
                    raise DisProtStageError(f"{region_source}.{field}: expected an array or null")
            if raw_region.get("sequence_construct") is not None and not isinstance(
                raw_region.get("sequence_construct"), str
            ):
                raise DisProtStageError(f"{region_source}.sequence_construct: expected opaque text")
            idpo_regions.append(
                DisProtRegion(
                    entry=entry,
                    source_region_index=region_index,
                    region_id=region_id,
                    start=start,
                    end=end,
                    term=observed_term,
                    raw_sha256=value_sha256(raw_region),
                    raw=raw_region,
                )
            )

    trait_protein_pairs = {
        (region.term.term_id, region.entry.protein_id) for region in idpo_regions
    }
    coordinate_groups: Counter[tuple[str, str, int, int]] = Counter(
        (
            region.entry.protein_id,
            region.term.term_id,
            region.start,
            region.end,
        )
        for region in idpo_regions
    )
    duplicate_groups = [count for count in coordinate_groups.values() if count > 1]
    stats = {
        "entry_count": len(entries),
        "total_region_count": total_regions,
        "idpo_region_count": len(idpo_regions),
        "go_region_count": ontology_counts["GO"],
        "idpo_protein_count": len({region.entry.protein_id for region in idpo_regions}),
        "protein_count": len({region.entry.protein_id for region in idpo_regions}),
        "trait_count": len(terms),
        "namespace_count": len({term.namespace for term in terms.values()}),
        "trait_protein_pair_count": len(trait_protein_pairs),
        "regions_counter_excess_entry_count": counter_excess_entry_count,
        "regions_counter_excess_total": counter_excess_total,
        "duplicate_coordinate_group_count": len(duplicate_groups),
        "duplicate_coordinate_extra_region_count": sum(count - 1 for count in duplicate_groups),
        "structured_context_region_count": sum(
            _has_structured_context(region.raw) for region in idpo_regions
        ),
        "construct_context_region_count": sum(
            _has_construct_context(region.raw) for region in idpo_regions
        ),
        "uniprot_changed_region_count": sum(
            region.raw.get("uniprot_changed") is True for region in idpo_regions
        ),
        "term_not_annotate_region_count": sum(
            region.raw.get("term_not_annotate") is True for region in idpo_regions
        ),
        "citation_source_counts": dict(sorted(citation_counts.items())),
        "eco_identity_count": len(eco_names),
    }
    return ParsedSource(tuple(entries), tuple(idpo_regions), terms, stats)


def parse_residue_frame(artifact: CapturedArtifact, *, expected_release: str) -> ResidueFrame:
    value = _strict_json_value(artifact.raw, source=artifact.relative_path)
    root = _require_mapping(value, source=artifact.relative_path)
    if set(root) != {"_meta", "proteins"}:
        raise DisProtStageError(f"{artifact.relative_path}: unexpected residue-frame root keys")
    metadata = _require_mapping(root.get("_meta"), source=f"{artifact.relative_path}._meta")
    proteins = _require_mapping(root.get("proteins"), source=f"{artifact.relative_path}.proteins")
    if metadata.get("schema") != 1 or metadata.get("source") != "UniProt":
        raise DisProtStageError(f"{artifact.relative_path}: invalid residue-frame metadata")
    if metadata.get("release") != expected_release:
        raise DisProtStageError(
            f"{artifact.relative_path}: residue-frame release does not equal {expected_release}"
        )
    if metadata.get("count") != len(proteins):
        raise DisProtStageError(f"{artifact.relative_path}: residue-frame count mismatch")
    absent_value = metadata.get("absent")
    if not isinstance(absent_value, list) or any(
        not isinstance(item, str) or _UNIPROT_RE.fullmatch(item) is None for item in absent_value
    ):
        raise DisProtStageError(f"{artifact.relative_path}: invalid absent accession list")
    if absent_value != sorted(set(absent_value)):
        raise DisProtStageError(
            f"{artifact.relative_path}: absent accession list is not unique/sorted"
        )
    absent = frozenset(absent_value)
    normalized: dict[str, Mapping[str, Any]] = {}
    for accession, row_value in proteins.items():
        if (
            not isinstance(accession, str)
            or _UNIPROT_RE.fullmatch(accession) is None
            or accession in absent
        ):
            raise DisProtStageError(
                f"{artifact.relative_path}: invalid/contradictory frame accession {accession!r}"
            )
        row = _require_mapping(row_value, source=f"{artifact.relative_path}.proteins[{accession}]")
        sequence = row.get("seq")
        if not isinstance(sequence, str) or _SEQUENCE_RE.fullmatch(sequence) is None:
            raise DisProtStageError(
                f"{artifact.relative_path}: invalid frame sequence for {accession}"
            )
        if not isinstance(row.get("ft"), list):
            raise DisProtStageError(
                f"{artifact.relative_path}: invalid frame feature list for {accession}"
            )
        normalized[accession] = row
    return ResidueFrame(expected_release, normalized, absent, metadata)


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
            raise DisProtStageError("trait YAML has an unhashable mapping key") from error
        if duplicate:
            raise DisProtStageError(f"trait YAML has duplicate key {key!r}")
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
            raise DisProtStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for key, item in value.items():
            if not isinstance(key, str):
                raise DisProtStageError(f"{source}: YAML mapping key is not a string")
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise DisProtStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for item in value:
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if value is None or type(value) in {str, int, bool}:
        return
    if type(value) is float and math.isfinite(value):
        return
    raise DisProtStageError(f"{source}: YAML value is outside the JSON data model")


def _load_yaml_mapping(raw: bytes, *, path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError, DisProtStageError) as error:
        raise DisProtStageError(f"cannot parse trait record {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise DisProtStageError(f"trait record is not a mapping: {path}")
    _require_json_shape(value, source=str(path))
    return value


def _reject_trait_tree_symlinks(traits_root: Path) -> None:
    def fail(error: OSError) -> None:
        raise DisProtStageError(f"cannot scan trait tree {traits_root}: {error}")

    for directory, names, files in os.walk(
        traits_root, topdown=True, onerror=fail, followlinks=False
    ):
        for name in [*names, *files]:
            path = Path(directory) / name
            try:
                metadata = os.stat(path, follow_symlinks=False)
            except OSError as error:
                raise DisProtStageError(
                    f"cannot inspect trait-tree entry {path}: {error}"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                raise DisProtStageError(f"symlink below trait directory is forbidden: {path}")


def _term_trait_path(traits_root: Path, term: DisProtTerm) -> Path:
    slug = _slugify(term.name, 70, "idpo")
    return (
        traits_root
        / "sequence"
        / "disorder"
        / f"{slug}-{term.term_id.replace(':', '-').lower()}.yaml"
    )


def _group_trait_path(traits_root: Path, namespace: str) -> Path:
    return traits_root / "sequence" / "disorder" / NAMESPACE_GROUPS[namespace][3]


def _candidate_trait_paths(traits_root: Path, source: ParsedSource) -> tuple[Path, ...]:
    command = [
        "rg",
        "--null",
        "-l",
        "--text",
        "--hidden",
        "--no-ignore",
        "-i",
        "--glob",
        "*.[yY][aA][mM][lL]",
        "--glob",
        "*.[yY][mM][lL]",
        "-e",
        "idpo",
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
        raise DisProtStageError(f"cannot run ripgrep IDPO trait prefilter: {error}") from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise DisProtStageError(f"ripgrep IDPO trait prefilter failed: {detail}")
    try:
        paths = {Path(raw.decode("utf-8")) for raw in scan.stdout.split(b"\0") if raw}
    except UnicodeDecodeError as error:
        raise DisProtStageError(f"ripgrep returned a non-UTF-8 path: {error}") from error
    paths.update(_term_trait_path(traits_root, term) for term in source.terms.values())
    paths.update(_group_trait_path(traits_root, namespace) for namespace in NAMESPACE_GROUPS)
    return tuple(sorted(_lexical_absolute(path) for path in paths))


def _normalized_whitespace(value: Any) -> str | None:
    return " ".join(value.split()) if isinstance(value, str) else None


def _expected_group_record(namespace: str) -> dict[str, Any]:
    identifier, label, definition, _ = NAMESPACE_GROUPS[namespace]
    return {
        "identifier": identifier,
        "label": label,
        "definition": definition,
        "definition_source": TRAIT_DEFINITION_SOURCE,
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DISORDER",
        "term_kind": "CLASS",
        "mapping_status": "SEEDED",
        "license": TRAIT_LICENSE,
    }


def _legacy_projection(
    source: ParsedSource,
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    dict[str, int],
]:
    hits: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    region_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    for region in source.idpo_regions:
        entry = region.entry
        example = hits[region.term.term_id].setdefault(
            entry.accession,
            {
                "protein_id": entry.protein_id,
                "protein_label": entry.name,
                "taxon_id": f"NCBITaxon:{entry.taxon_id}",
                "taxon_label": entry.organism,
                "sequence_length": len(entry.sequence),
                "note": f"DisProt entry {entry.disprot_id}",
                "source": "CURATOR",
                "sequence": entry.sequence,
                "features": [],
            },
        )
        example["features"].append(
            {
                "start": region.start,
                "end": region.end,
                "feature_type": "DISORDER",
                "trait_axis": "SEQUENCE",
                "trait_category": "SEQ_DISORDER",
            }
        )
        region_ids[(region.term.term_id, entry.accession)].append(region.region_id)

    selected: dict[str, list[dict[str, Any]]] = {}
    current_binding: dict[str, dict[str, Any]] = {}
    protein_counts: dict[str, int] = {}
    for term_id, proteins in hits.items():
        protein_counts[term_id] = len(proteins)
        ordered = sorted(proteins.items(), key=lambda item: (-len(item[1]["features"]), item[0]))
        selected[term_id] = [example for _, example in ordered[:EXAMPLES_CAP]]
        for example_index, (accession, example) in enumerate(ordered[:EXAMPLES_CAP]):
            ids = region_ids[(term_id, accession)]
            if len(ids) != len(example["features"]):
                raise DisProtStageError("internal legacy region/feature replay mismatch")
            for feature_index, region_id in enumerate(ids):
                current_binding[region_id] = {
                    "selected_by_legacy_top_30_cap": True,
                    "current_example_index": example_index,
                    "current_feature_index": feature_index,
                    "current_example_trait_id": term_id,
                    "current_example_has_inline_sequence": True,
                }
    return selected, current_binding, protein_counts


def _expected_term_record(
    term: DisProtTerm,
    examples: Sequence[Mapping[str, Any]],
    *,
    protein_count: int,
) -> dict[str, Any]:
    parent = NAMESPACE_GROUPS[term.namespace][0]
    definition = (
        f"{term.name} — an IDPO disorder class ({term.namespace}, {term.term_id}); "
        "a protein region with this intrinsic-disorder property. "
        f"{protein_count} DisProt protein(s) annotated (examples below capped)."
    )
    return {
        "identifier": term.term_id,
        "label": term.name,
        "definition": definition,
        "definition_source": TRAIT_DEFINITION_SOURCE,
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DISORDER",
        "term_kind": "CLASS",
        "mapping_status": "SEEDED",
        "parent_traits": [parent],
        "canonical_examples": list(examples),
        "license": TRAIT_LICENSE,
    }


def index_disprot_traits(
    traits_root: Path,
    source: ParsedSource,
    *,
    repo_root: Path,
    repo_binding: BoundDirectory,
) -> tuple[
    Mapping[str, TraitBinding],
    Mapping[str, Mapping[str, Any]],
    tuple[ArtifactDigest, ...],
    Mapping[str, Any],
]:
    traits_binding = _bind_subdirectory(repo_binding, traits_root, description="trait root")
    try:
        _reject_trait_tree_symlinks(traits_binding.path)
        initial_paths = _candidate_trait_paths(traits_binding.path, source)
        selected, current_bindings, protein_counts = _legacy_projection(source)
        expected_term_ids = set(source.terms)
        expected_group_ids = {values[0] for values in NAMESPACE_GROUPS.values()}
        bindings: dict[str, TraitBinding] = {}
        artifacts: list[ArtifactDigest] = []
        observed_relevant_paths: set[Path] = set()
        for path in initial_paths:
            artifact = _capture(
                path,
                description="IDPO trait candidate",
                repo_root=repo_root,
                expected_sha256=None,
                bound_root=repo_binding,
            )
            # Every conservative prefilter candidate participates in the semantic
            # shadow proof, including files whose parsed identifier is not IDPO.
            # Retain its digest so an initially irrelevant file cannot turn into
            # a shadow between parsing and the final membership check.
            artifacts.append(ArtifactDigest(artifact.path, artifact.relative_path, artifact.sha256))
            record = _load_yaml_mapping(artifact.raw, path=path)
            identifier = record.get("identifier")
            relevant = isinstance(identifier, str) and (
                identifier.startswith("IDPO:") or identifier.startswith("proteintraitsmech:IDPO_")
            )
            if not relevant:
                continue
            observed_relevant_paths.add(path)
            if identifier in expected_term_ids:
                term = source.terms[str(identifier)]
                expected_path = _lexical_absolute(_term_trait_path(traits_binding.path, term))
                expected_record = _expected_term_record(
                    term,
                    selected[term.term_id],
                    protein_count=protein_counts[term.term_id],
                )
                parent = NAMESPACE_GROUPS[term.namespace][0]
                namespace = term.namespace
                label = term.name
            elif identifier in expected_group_ids:
                namespace = next(
                    key for key, values in NAMESPACE_GROUPS.items() if values[0] == identifier
                )
                expected_path = _lexical_absolute(_group_trait_path(traits_binding.path, namespace))
                expected_record = _expected_group_record(namespace)
                parent = ""
                label = NAMESPACE_GROUPS[namespace][1]
            else:
                raise DisProtStageError(
                    f"{path}: IDPO semantic shadow/identity absent from source snapshot"
                )
            if path != expected_path:
                raise DisProtStageError(
                    f"{path}: IDPO trait is outside exact source-derived path {expected_path}"
                )
            examples = record.get("canonical_examples")
            if isinstance(examples, list):
                forbidden_grounding_fields = {
                    "qualification_status",
                    "source_evidence_id",
                    "trait_occurrences",
                    "sequence_sha256",
                    "sequence_version",
                    "uniprot_release",
                    "reviewed",
                }
                for example_index, example in enumerate(examples):
                    if not isinstance(example, Mapping):
                        continue
                    forbidden = sorted(forbidden_grounding_fields.intersection(example))
                    if forbidden:
                        raise DisProtStageError(
                            f"{path}: canonical example {example_index} carries forbidden "
                            f"grounding/qualification fields: {forbidden}"
                        )
            if set(record) != set(expected_record):
                raise DisProtStageError(
                    f"{path}: IDPO trait contract fields differ from historical projection"
                )
            for field, expected in expected_record.items():
                observed = record.get(field)
                if field == "definition":
                    if _normalized_whitespace(observed) != _normalized_whitespace(expected):
                        raise DisProtStageError(
                            f"{path}: definition differs from source-derived trait contract"
                        )
                elif observed != expected:
                    raise DisProtStageError(f"{path}: trait contract mismatch for {field}")
            if str(identifier) in bindings:
                raise DisProtStageError(f"duplicate IDPO trait identity {identifier}")
            bindings[str(identifier)] = TraitBinding(
                trait_id=str(identifier),
                parent_trait_id=parent,
                relative_path=artifact.relative_path,
                sha256=artifact.sha256,
                label=label,
                namespace=namespace,
            )
        if set(bindings) != expected_term_ids | expected_group_ids:
            missing = sorted((expected_term_ids | expected_group_ids) - set(bindings))
            raise DisProtStageError(f"IDPO trait identity set is incomplete: {missing[:10]}")
        _reject_trait_tree_symlinks(traits_binding.path)
        final_paths = _candidate_trait_paths(traits_binding.path, source)
        if final_paths != initial_paths:
            raise DisProtStageError("IDPO trait candidate membership drifted while indexing")
        if observed_relevant_paths != {
            _lexical_absolute(_term_trait_path(traits_binding.path, term))
            for term in source.terms.values()
        } | {
            _lexical_absolute(_group_trait_path(traits_binding.path, namespace))
            for namespace in NAMESPACE_GROUPS
        }:
            raise DisProtStageError("IDPO semantic trait path set contains a shadow")
        _assert_directory_binding(traits_binding, description="trait root")
        legacy_stats = {
            "legacy_selected_example_count": sum(len(rows) for rows in selected.values()),
            "legacy_selected_unique_protein_count": len(
                {example["protein_id"] for rows in selected.values() for example in rows}
            ),
            "legacy_selected_feature_count": sum(
                len(example["features"]) for rows in selected.values() for example in rows
            ),
            "legacy_cap_omitted_trait_protein_pair_count": (
                source.stats["trait_protein_pair_count"]
                - sum(len(rows) for rows in selected.values())
            ),
        }
        return bindings, current_bindings, tuple(artifacts), legacy_stats
    finally:
        os.close(traits_binding.descriptor)


def parse_protein_registry(
    artifact: CapturedArtifact, *, expected_release: str
) -> dict[str, dict[str, Any]]:
    if _UNIPROT_RELEASE_RE.fullmatch(expected_release) is None:
        raise DisProtStageError(f"invalid expected UniProt release: {expected_release!r}")
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DisProtStageError(f"{artifact.relative_path}: registry is not UTF-8") from error
    if artifact.raw and (not artifact.raw.endswith(b"\n") or b"\r" in artifact.raw):
        raise DisProtStageError(f"{artifact.relative_path}: registry must be canonical LF JSONL")
    registry: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise DisProtStageError(f"{artifact.relative_path}:{line_number}: blank registry line")
        value = _strict_json_value(line, source=f"{artifact.relative_path}:{line_number}")
        if not isinstance(value, dict):
            raise DisProtStageError(
                f"{artifact.relative_path}:{line_number}: registry line is not an object"
            )
        findings = grounding.validate_protein_reference(value, path=artifact.path, line=line_number)
        if findings:
            detail = "; ".join(f"{item.code}: {item.message}" for item in findings)
            raise DisProtStageError(
                f"{artifact.relative_path}:{line_number}: invalid ProteinReference: {detail}"
            )
        if canonical_json(value) != line:
            raise DisProtStageError(
                f"{artifact.relative_path}:{line_number}: ProteinReference is not canonical JSON"
            )
        if value.get("uniprot_release") != expected_release:
            raise DisProtStageError(
                f"{artifact.relative_path}:{line_number}: ProteinReference release does not "
                f"equal {expected_release}"
            )
        protein_id = str(value["protein_id"])
        if protein_id in registry:
            raise DisProtStageError(
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


def _source_snapshot(artifact: CapturedArtifact) -> dict[str, Any]:
    snapshot = {
        "kind": "DISPROT_LOCAL_SOURCE_SNAPSHOT",
        "schema_version": SCHEMA_VERSION,
        "source_artifact": _artifact_projection(
            artifact, role="DISPROT_MUTABLE_CURRENT_JSON_ARRAY"
        ),
        "repository_declared_source_url": SOURCE_URL_DECLARED_BY_REPOSITORY,
        "endpoint_release_selector": "current",
        "provider_global_release": None,
        "provider_acquisition_receipt": None,
        "provider_license_declared_by_source_bytes": None,
        "repository_source_registration_license": TRAIT_LICENSE,
        "acquisition_status": "LOCAL_PINNED_BYTES_WITHOUT_PROVIDER_FETCH_RECEIPT",
    }
    snapshot["source_snapshot_id"] = "disprot-source-snapshot:" + value_sha256(snapshot)
    return snapshot


def _trait_projection(binding: TraitBinding) -> dict[str, Any]:
    return {
        "trait_id": binding.trait_id,
        "parent_trait_id": binding.parent_trait_id,
        "trait_record_path": binding.relative_path,
        "trait_record_sha256": binding.sha256,
        "label": binding.label,
        "namespace": binding.namespace,
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DISORDER",
    }


def _frame_status(entry: DisProtEntry, frame: ResidueFrame) -> tuple[str, str | None]:
    frame_row = frame.proteins.get(entry.accession)
    if frame_row is None:
        return (
            "EXPLICITLY_ABSENT_FROM_LOCAL_RESIDUE_FRAME"
            if entry.accession in frame.absent
            else "UNLISTED_IN_LOCAL_RESIDUE_FRAME",
            None,
        )
    sequence = str(frame_row["seq"])
    return (
        "EXACT_SOURCE_SEQUENCE_MATCH" if sequence == entry.sequence else "SOURCE_SEQUENCE_MISMATCH",
        sequence,
    )


def _source_projection(region: DisProtRegion) -> dict[str, Any]:
    entry = region.entry
    projection = dict(region.raw)
    derived = {
        "source_entry_index": entry.source_index,
        "source_region_index": region.source_region_index,
        "disprot_id": entry.disprot_id,
        "protein_id": entry.protein_id,
        "primary_accession_is_authoritative": True,
        "source_trait_id": region.term.term_id,
        "source_interval": {"start": region.start, "end": region.end},
        "coordinate_convention": "ONE_BASED_CLOSED_INFERRED_NOT_PROVIDER_DECLARED",
        "source_protein_sequence_length": len(entry.sequence),
        "source_protein_sequence_sha256": entry.sequence_sha256,
        "source_interval_sequence": entry.sequence[region.start - 1 : region.end],
        "source_interval_sequence_sha256": hashlib.sha256(
            entry.sequence[region.start - 1 : region.end].encode("ascii")
        ).hexdigest(),
        "source_entry_canonical_object_sha256": entry.raw_sha256,
        "source_region_canonical_object_sha256": region.raw_sha256,
        "source_object_digest_basis": "RFC8785_LIKE_SORTED_COMPACT_JSON_VALUE_NOT_RAW_LINE",
        "entry_released_metadata_not_global_source_release": entry.released,
    }
    collisions = sorted(set(projection).intersection(derived))
    allowed_repeated = {
        "disprot_id",
        "source_trait_id",
    }
    if set(collisions) - allowed_repeated:
        raise DisProtStageError(
            f"source projection derived-field collision for {region.region_id}: {collisions}"
        )
    projection.update(derived)
    return projection


def _frame_projection(
    entry: DisProtEntry,
    frame: ResidueFrame,
    frame_artifact: CapturedArtifact,
) -> dict[str, Any]:
    status, sequence = _frame_status(entry, frame)
    return {
        "status": status,
        "residue_frame_path": frame_artifact.relative_path,
        "residue_frame_sha256": frame_artifact.sha256,
        "uniprot_release": frame.release,
        "declared_absent": entry.accession in frame.absent,
        "sequence_length": len(sequence) if sequence is not None else None,
        "sequence_sha256": (
            hashlib.sha256(sequence.encode("ascii")).hexdigest() if sequence is not None else None
        ),
    }


def _reference_projection(
    reference: Mapping[str, Any] | None, *, registry_sha256: str
) -> dict[str, Any]:
    if reference is None:
        return {
            "status": "MISSING_EXACT_PROTEIN_REFERENCE",
            "protein_registry_sha256": registry_sha256,
            "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
        }
    return {
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


def _candidate_projection(
    region: DisProtRegion,
    reference: Mapping[str, Any],
    *,
    source_snapshot_id: str,
    blockers: Sequence[str],
) -> dict[str, Any]:
    interval = region.entry.sequence[region.start - 1 : region.end]
    return {
        "candidate_kind": "DISPROT_LOCAL_REGISTRY_SEQUENCE_MATCH",
        "trait_id": region.term.term_id,
        "protein_id": region.entry.protein_id,
        "source_trait_id": region.term.term_id,
        "mapping_method": "SOURCE_NATIVE_COORDINATES",
        "scope": "LOCALIZED",
        "coordinate_frame": (
            "UNIPROT_ISOFORM" if "-" in region.entry.accession else "UNIPROT_CANONICAL"
        ),
        "source_interval": {"start": region.start, "end": region.end},
        "resolved_interval_sequence": interval,
        "resolved_interval_sequence_sha256": hashlib.sha256(interval.encode("ascii")).hexdigest(),
        "resolved_interval_sequence_origin": (
            "DISPROT_EXPORT_MATCHED_TO_PINNED_RESIDUE_FRAME_AND_LOCAL_PROTEIN_REFERENCE"
        ),
        "evidence_source": "DisProt",
        "disprot_source_snapshot_id": source_snapshot_id,
        "disprot_region_id": region.region_id,
        "resolved_protein_sequence_sha256": reference["sequence_sha256"],
        "resolved_protein_uniprot_release": reference["uniprot_release"],
        "qualification_status": "CANDIDATE_ONLY",
        "qualification_blockers": sorted(set(blockers)),
        "source_evidence_id": None,
    }


def _build_occurrence(
    region: DisProtRegion,
    *,
    trait: TraitBinding,
    current_binding: Mapping[str, Any] | None,
    frame: ResidueFrame,
    frame_artifact: CapturedArtifact,
    reference: Mapping[str, Any] | None,
    registry_sha256: str,
    source_snapshot_id: str,
) -> dict[str, Any]:
    blockers = list(GLOBAL_PROMOTION_BLOCKERS)
    if _has_structured_context(region.raw):
        blockers.append(STRUCTURED_CONTEXT_REVIEW)
    if _has_construct_context(region.raw):
        blockers.append(CONSTRUCT_CONTEXT_REVIEW)
    if region.raw.get("uniprot_changed") is True:
        blockers.append(UNIPROT_CHANGED_REVIEW)
    if region.raw.get("term_not_annotate") is True:
        blockers.append(TERM_NOT_ANNOTATE_REVIEW)

    frame_status, _ = _frame_status(region.entry, frame)
    candidate: dict[str, Any] | None = None
    if frame_status in {
        "EXPLICITLY_ABSENT_FROM_LOCAL_RESIDUE_FRAME",
        "UNLISTED_IN_LOCAL_RESIDUE_FRAME",
    }:
        status = "NOT_IN_RESIDUE_FRAME"
        blockers.append(NOT_IN_FRAME)
    elif frame_status == "SOURCE_SEQUENCE_MISMATCH":
        status = "SOURCE_RESIDUE_FRAME_SEQUENCE_MISMATCH"
        blockers.append(FRAME_SEQUENCE_MISMATCH)
    elif reference is None:
        status = "MISSING_LOCAL_PROTEIN_REFERENCE"
        blockers.append(MISSING_PROTEIN_REFERENCE)
    elif reference["sequence"] != region.entry.sequence:
        status = "LOCAL_PROTEIN_REFERENCE_SOURCE_SEQUENCE_MISMATCH"
        blockers.append(REGISTRY_SEQUENCE_MISMATCH)
    elif (
        reference["taxon_id"] != f"NCBITaxon:{region.entry.taxon_id}"
        or reference["taxon_label"] != region.entry.organism
    ):
        status = "LOCAL_PROTEIN_REFERENCE_SOURCE_TAXON_MISMATCH"
        blockers.append(REGISTRY_TAXON_MISMATCH)
    else:
        status = "SEQUENCE_MATCHED_STAGING_ONLY_MISSING_RECEIPTS"
        candidate = _candidate_projection(
            region,
            reference,
            source_snapshot_id=source_snapshot_id,
            blockers=blockers,
        )

    row = {
        "kind": OCCURRENCE_KIND,
        "schema_version": SCHEMA_VERSION,
        "trait_id": region.term.term_id,
        "protein_id": region.entry.protein_id,
        "trait_binding": _trait_projection(trait),
        "source_binding": _source_projection(region),
        "current_example_binding": (
            dict(current_binding)
            if current_binding is not None
            else {
                "selected_by_legacy_top_30_cap": False,
                "current_example_index": None,
                "current_feature_index": None,
                "current_example_trait_id": None,
                "current_example_has_inline_sequence": False,
            }
        ),
        "residue_frame_binding": _frame_projection(region.entry, frame, frame_artifact),
        "protein_reference_binding": _reference_projection(
            reference, registry_sha256=registry_sha256
        ),
        "grounding_status": status,
        "promotion_blockers": sorted(set(blockers)),
        "local_registry_sequence_match_candidate": candidate,
        "grounding_evidence_emitted": False,
        "source_snapshot_id": source_snapshot_id,
        "network_action_performed": False,
        "write_action_performed": False,
    }
    return _content_address(
        row,
        id_field="occurrence_stage_id",
        prefix="disprot-source-occurrence:",
        row_hash_field="occurrence_row_sha256",
    )


def _build_requests(
    source: ParsedSource,
    registry: Mapping[str, Mapping[str, Any]],
    frame: ResidueFrame,
    *,
    source_snapshot_id: str,
    expected_uniprot_release: str,
) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, list[DisProtRegion]] = defaultdict(list)
    for region in source.idpo_regions:
        if region.entry.protein_id not in registry:
            grouped[region.entry.protein_id].append(region)
    requests: list[dict[str, Any]] = []
    for protein_id, regions in sorted(grouped.items()):
        entry = regions[0].entry
        frame_status, _ = _frame_status(entry, frame)
        request = {
            "kind": REQUEST_KIND,
            "schema_version": SCHEMA_VERSION,
            "protein_id": protein_id,
            "primary_accession_is_authoritative": True,
            "coordinate_frame": (
                "UNIPROT_ISOFORM" if "-" in entry.accession else "UNIPROT_CANONICAL"
            ),
            "source_snapshot_id": source_snapshot_id,
            "expected_uniprot_release": expected_uniprot_release,
            "disprot_ids": sorted({region.entry.disprot_id for region in regions}),
            "source_region_ids": [region.region_id for region in regions],
            "source_region_count": len(regions),
            "trait_ids": sorted({region.term.term_id for region in regions}),
            "trait_count": len({region.term.term_id for region in regions}),
            "source_taxon_id": f"NCBITaxon:{entry.taxon_id}",
            "source_taxon_label": entry.organism,
            "source_sequence_length": len(entry.sequence),
            "source_sequence_sha256": entry.sequence_sha256,
            "maximum_source_coordinate": max(region.end for region in regions),
            "residue_frame_status": frame_status,
            "request_reason": MISSING_PROTEIN_REFERENCE,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        requests.append(
            _content_address(
                request,
                id_field="request_id",
                prefix="disprot-protein-request:",
                row_hash_field="request_row_sha256",
            )
        )
    return tuple(requests)


def build_stage(
    *,
    source_path: Path = DEFAULT_SOURCE,
    traits_root: Path = DEFAULT_TRAITS_ROOT,
    residue_frame_path: Path = DEFAULT_RESIDUE_FRAME,
    protein_registry_path: Path = DEFAULT_PROTEIN_REGISTRY,
    repo_root: Path = REPO_ROOT,
    expected_source_sha256: str = EXPECTED_SOURCE_SHA256,
    expected_frame_sha256: str = EXPECTED_FRAME_SHA256,
    expected_uniprot_release: str = EXPECTED_UNIPROT_RELEASE,
) -> StageResult:
    repo_binding = _bind_absolute_directory(repo_root, description="repository root")
    try:
        source_artifact = _capture(
            source_path,
            description="DisProt source export",
            repo_root=repo_root,
            expected_sha256=expected_source_sha256,
            bound_root=repo_binding,
        )
        frame_artifact = _capture(
            residue_frame_path,
            description="UniProt residue frame",
            repo_root=repo_root,
            expected_sha256=expected_frame_sha256,
            bound_root=repo_binding,
        )
        registry_artifact = _capture(
            protein_registry_path,
            description="ProteinReference registry",
            repo_root=repo_root,
            expected_sha256=None,
            bound_root=repo_binding,
        )
        source = parse_disprot_source(source_artifact)
        frame = parse_residue_frame(frame_artifact, expected_release=expected_uniprot_release)
        registry = parse_protein_registry(
            registry_artifact, expected_release=expected_uniprot_release
        )
        traits, current_bindings, trait_artifacts, legacy_stats = index_disprot_traits(
            traits_root,
            source,
            repo_root=repo_root,
            repo_binding=repo_binding,
        )
        source_snapshot = _source_snapshot(source_artifact)
        source_snapshot_id = str(source_snapshot["source_snapshot_id"])
        occurrences = tuple(
            _build_occurrence(
                region,
                trait=traits[region.term.term_id],
                current_binding=current_bindings.get(region.region_id),
                frame=frame,
                frame_artifact=frame_artifact,
                reference=registry.get(region.entry.protein_id),
                registry_sha256=registry_artifact.sha256,
                source_snapshot_id=source_snapshot_id,
            )
            for region in source.idpo_regions
        )
        requests = _build_requests(
            source,
            registry,
            frame,
            source_snapshot_id=source_snapshot_id,
            expected_uniprot_release=expected_uniprot_release,
        )
        status_counts = Counter(row["grounding_status"] for row in occurrences)
        frame_status_counts = Counter(row["residue_frame_binding"]["status"] for row in occurrences)
        trait_rows = [_trait_projection(traits[trait_id]) for trait_id in sorted(traits)]
        group_trait_rows = [
            _trait_projection(traits[values[0]])
            for _namespace, values in sorted(NAMESPACE_GROUPS.items())
        ]
        summary: dict[str, Any] = {
            "kind": SUMMARY_KIND,
            "schema_version": SCHEMA_VERSION,
            "source_snapshot": source_snapshot,
            "source_artifact": source_snapshot["source_artifact"],
            "residue_frame_artifact": _artifact_projection(
                frame_artifact, role="PINNED_UNIPROT_RESIDUE_FRAME"
            ),
            "protein_registry_artifact": _artifact_projection(
                registry_artifact,
                role="LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING",
            ),
            "expected_uniprot_release": expected_uniprot_release,
            "protein_registry_fetch_receipt_verification_status": ("NOT_VERIFIED_BY_THIS_STAGE"),
            "protein_registry_row_count": len(registry),
            **source.stats,
            **legacy_stats,
            "trait_binding_count": len(trait_rows),
            "namespace_group_trait_binding_count": len(group_trait_rows),
            "namespace_group_trait_bindings": group_trait_rows,
            "residue_frame_protein_count": len(frame.proteins),
            "residue_frame_absent_accession_count": len(frame.absent),
            "residue_frame_status_counts": dict(sorted(frame_status_counts.items())),
            "grounding_status_counts": dict(sorted(status_counts.items())),
            "local_registry_sequence_match_candidate_count": sum(
                row["local_registry_sequence_match_candidate"] is not None for row in occurrences
            ),
            "exact_frame_missing_registry_count": status_counts["MISSING_LOCAL_PROTEIN_REFERENCE"],
            "not_in_residue_frame_count": status_counts["NOT_IN_RESIDUE_FRAME"],
            "residue_frame_sequence_mismatch_count": status_counts[
                "SOURCE_RESIDUE_FRAME_SEQUENCE_MISMATCH"
            ],
            "missing_protein_reference_request_count": len(requests),
            "grounding_evidence_emitted_count": 0,
            "trait_binding_rows_sha256": hashlib.sha256(_rows_bytes(trait_rows)).hexdigest(),
            "occurrence_rows_sha256": hashlib.sha256(_rows_bytes(occurrences)).hexdigest(),
            "protein_request_rows_sha256": hashlib.sha256(_rows_bytes(requests)).hexdigest(),
            "combined_non_summary_rows_sha256": hashlib.sha256(
                _rows_bytes([*occurrences, *requests])
            ).hexdigest(),
            "promotion_blockers": [
                *GLOBAL_PROMOTION_BLOCKERS,
                "DISPROT_SOURCE_BYTES_DO_NOT_DECLARE_A_LICENSE",
                "REGIONS_COUNTER_IS_NOT_A_PHYSICAL_EXPORT_COMPLETENESS_ASSERTION",
                "SPARSE_SOURCE_TERM_DEFINITIONS_ARE_NOT_AUTHORITATIVE_IDPO",
                "VALIDATED_AND_UNPUBLISHED_SOURCE_FIELDS_ARE_NOT_ACCEPTANCE_SEMANTICS",
                "STRUCTURED_EXPERIMENTAL_CONTEXT_IS_PRESERVED_BUT_NOT_MODELLED_AS_EVIDENCE",
                "REVIEW_REQUIRED_BEFORE_TRAIT_OR_GROUNDING_WRITE",
            ],
            "coordinate_convention_status": (
                "ONE_BASED_CLOSED_INFERRED_FROM_SOURCE_AND_EXISTING_SEEDER_NOT_DECLARED"
            ),
            "source_export_completeness_claimed": False,
            "provider_release_claimed": False,
            "qualification_claimed": False,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        _content_address(
            summary,
            id_field="stage_id",
            prefix="disprot-source-native-stage:",
            row_hash_field="summary_row_sha256",
        )
        for artifact, description in (
            (source_artifact, "DisProt source export"),
            (frame_artifact, "UniProt residue frame"),
            (registry_artifact, "ProteinReference registry"),
        ):
            _assert_unchanged(artifact, description=description, bound_root=repo_binding)
        for artifact in trait_artifacts:
            _assert_unchanged(artifact, description="IDPO trait record", bound_root=repo_binding)
        _assert_directory_binding(repo_binding, description="repository root")
        return StageResult(occurrences, requests, summary)
    finally:
        os.close(repo_binding.descriptor)


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows = (
        [result.summary]
        if summary_only
        else [*result.occurrences, *result.protein_requests, result.summary]
    )
    return "".join(canonical_json(row) + "\n" for row in rows)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--traits", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument("--residue-frame", type=Path, default=DEFAULT_RESIDUE_FRAME)
    parser.add_argument("--protein-registry", type=Path, default=DEFAULT_PROTEIN_REGISTRY)
    parser.add_argument("--expect-uniprot-release", default=EXPECTED_UNIPROT_RELEASE)
    parser.add_argument("--summary-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_stage(
            source_path=args.source,
            traits_root=args.traits,
            residue_frame_path=args.residue_frame,
            protein_registry_path=args.protein_registry,
            repo_root=REPO_ROOT,
            expected_uniprot_release=args.expect_uniprot_release,
        )
    except DisProtStageError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
