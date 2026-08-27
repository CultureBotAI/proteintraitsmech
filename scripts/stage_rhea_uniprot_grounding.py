#!/usr/bin/env python3
"""Stage direct Rhea-to-UniProtKB/Swiss-Prot associations as canonical JSONL.

This is the direct whole-protein lane required by the grounding plan.  It does
not infer Rhea membership through EC numbers.  Instead it consumes Rhea's own
``rhea2uniprot_sprot.tsv`` export, whose ``MASTER_ID`` field binds a UniProtKB
accession to the corresponding undirected Rhea reaction.

The current workspace does not contain that export or a provider acquisition
receipt.  ``--acquisition-plan`` therefore emits a canonical, no-network plan
for the exact release-141 artifacts.  Normal staging is available only after
all named artifacts exist and agree on release, direction quartet, reaction,
trait, and accession semantics.  Even then every row is ``CANDIDATE_ONLY``:
this command has no network, output-file, apply, promotion, trait-writer, or
GroundingEvidence-writer mode.

The trait tree must remain quiescent while staging.  No-follow reads, exact
inode/content rechecks, a whole-tree Rhea identifier scan, and a final
membership replay detect practical substitution and sampled concurrent drift;
they are not an atomic filesystem snapshot against an uncooperative writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml


SCHEMA_VERSION = 1
CANDIDATE_KIND = "RHEA_UNIPROT_SOURCE_MEMBERSHIP_CANDIDATE"
REQUEST_KIND = "RHEA_UNIPROT_PROTEIN_REFERENCE_REQUEST"
SUMMARY_KIND = "RHEA_UNIPROT_SOURCE_NATIVE_STAGE_SUMMARY"
ACQUISITION_PLAN_KIND = "RHEA_UNIPROT_SOURCE_ACQUISITION_PLAN"

PROVIDER_NAME = "Rhea"
PROVIDER_KIND = "SOURCE_DATABASE"
MAPPING_METHOD = "SOURCE_MEMBERSHIP"
MEMBERSHIP_BASIS = "RHEA_TO_UNIPROTKB_SWISS_PROT_CROSS_REFERENCE"
SCOPE = "WHOLE_PROTEIN"

EXPECTED_RHEA_RELEASE = "141"
EXPECTED_RHEA_RELEASE_DATE = "2026-06-10"
EXPECTED_UNIPROT_RELEASE = "2026_02"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = REPO_ROOT / "data" / "raw" / "rhea"
DEFAULT_MAPPING = DEFAULT_RAW_DIR / "rhea2uniprot_sprot.tsv"
DEFAULT_RELEASE_PROPERTIES = DEFAULT_RAW_DIR / "rhea-release.properties"
DEFAULT_TSV_README = DEFAULT_RAW_DIR / "rhea-tsv-README.txt"
DEFAULT_LICENSE = DEFAULT_RAW_DIR / "LICENSE.txt"
DEFAULT_DIRECTIONS = DEFAULT_RAW_DIR / "rhea-directions.tsv"
DEFAULT_REACTIONS = DEFAULT_RAW_DIR / "rhea-reactions.tsv"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data" / "traits"
DEFAULT_TRAITS_DIR = DEFAULT_TRAITS_ROOT / "function" / "enzymatic_activity" / "rhea"
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data" / "grounding" / "protein_registry.jsonl"

CURRENT_SOURCE_SHA256: Mapping[str, str | None] = {
    # These two values pin the release-141-compatible local bytes already in the
    # workspace.  The absent artifacts intentionally have no guessed digest;
    # their future bytes are still content-addressed but remain un-authenticated
    # until a separate acquisition receipt exists.
    "mapping": None,
    "release_properties": None,
    "tsv_readme": None,
    "license": None,
    "directions": "0b62f0cd92991b89e7b6e05707e671e80787527c30192b3d44cf7fc05a5c748f",
    "reactions": "94b8a17bfc84951badf6f9a1f1594356f5a2091e27f6556646810e7a983bc066",
}

MISSING_PROVIDER_RECEIPT = "MISSING_RHEA_PROVIDER_ACQUISITION_RECEIPT"
MISSING_REGISTRY_RECEIPT = "MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT"
MISSING_SOURCE_RECEIPT_VERIFIER = "MISSING_RHEA_ACQUISITION_RECEIPT_VERIFIER_IN_GROUNDING_BOUNDARY"
MISSING_REVIEW = "HUMAN_REVIEW_REQUIRED_BEFORE_PROMOTION"
MISSING_PROMOTION_AUTHORIZATION = "EXPLICIT_PROMOTION_AUTHORIZATION_REQUIRED"
MISSING_PROTEIN_REFERENCE = "MISSING_EXPECTED_RELEASE_LOCAL_PROTEIN_REFERENCE"
GLOBAL_PROMOTION_BLOCKERS = (
    MISSING_PROVIDER_RECEIPT,
    MISSING_REGISTRY_RECEIPT,
    MISSING_SOURCE_RECEIPT_VERIFIER,
    MISSING_REVIEW,
    MISSING_PROMOTION_AUTHORIZATION,
)

MAPPING_HEADER = "RHEA_ID\tDIRECTION\tMASTER_ID\tID"
DIRECTIONS_HEADER = "RHEA_ID_MASTER\tRHEA_ID_LR\tRHEA_ID_RL\tRHEA_ID_BI"
REACTIONS_HEADER = "Reaction identifier\tEquation\tChEBI identifier\tEC number"
TRAIT_CONTRACT = {
    "definition_source": "Rhea",
    "trait_axis": "FUNCTION",
    "trait_category": "FUNC_ENZYMATIC_ACTIVITY",
    "term_kind": "CLASS",
    "license": "CC-BY 4.0",
}

OFFICIAL_URLS = {
    "mapping": "https://ftp.expasy.org/databases/rhea/tsv/rhea2uniprot_sprot.tsv",
    "release_properties": "https://ftp.expasy.org/databases/rhea/rhea-release.properties",
    "tsv_readme": "https://ftp.expasy.org/databases/rhea/tsv/README.txt",
    "license": "https://ftp.expasy.org/databases/rhea/LICENSE.txt",
    "directions": "https://ftp.expasy.org/databases/rhea/tsv/rhea-directions.tsv",
    "reactions": (
        "https://www.rhea-db.org/rhea?query=&columns=rhea-id,equation,chebi-id,ec&format=tsv"
    ),
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_POSITIVE_ID_RE = re.compile(r"^[1-9][0-9]*$")
_RHEA_IDENTIFIER_RE = re.compile(r"^RHEA:([1-9][0-9]*)$")
_RELEASE_RE = re.compile(r"^[1-9][0-9]*$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_UNIPROT_PRIMARY_RE = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})$"
)
_UNIPROT_ID_RE = re.compile(
    r"^UniProtKB:(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[1-9][0-9]*)?$"
)
_SEQUENCE_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")


class RheaStageError(ValueError):
    """A source, trait, registry, or filesystem invariant failed closed."""


@dataclass(frozen=True)
class CapturedArtifact:
    path: Path
    relative_path: str
    sha256: str
    size: int
    identity: tuple[int, int, int, int, int, int, int]
    raw: bytes


@dataclass(frozen=True)
class MappingRow:
    rhea_id: str
    direction: str
    master_id: str
    accession: str
    line_number: int
    raw_line_sha256: str

    @property
    def trait_id(self) -> str:
        return f"RHEA:{self.master_id}"

    @property
    def protein_id(self) -> str:
        return f"UniProtKB:{self.accession}"


@dataclass(frozen=True)
class TraitBinding:
    trait_id: str
    label: str
    path: Path
    relative_path: str
    sha256: str
    has_canonical_examples: bool


@dataclass(frozen=True)
class StageResult:
    candidates: tuple[dict[str, Any], ...]
    protein_requests: tuple[dict[str, Any], ...]
    summary: dict[str, Any]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _rows_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join((canonical_json(row) + "\n").encode("utf-8") for row in rows)


def _content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> dict[str, Any]:
    if id_field in row or row_hash_field in row:
        raise RheaStageError(f"content-address fields already present in {row.get('kind')!r}")
    row[id_field] = prefix + value_sha256(row)
    row[row_hash_field] = value_sha256(row)
    return row


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _relative_under(path: Path, root: Path, *, description: str) -> Path:
    absolute = _lexical_absolute(path)
    root_absolute = _lexical_absolute(root)
    try:
        relative = absolute.relative_to(root_absolute)
    except ValueError as exc:
        raise RheaStageError(f"{description} is outside repository root: {absolute}") from exc
    if not relative.parts:
        raise RheaStageError(f"{description} cannot be the repository root")
    return relative


def _identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
        metadata.st_mode,
        metadata.st_nlink,
    )


def _reject_symlink_components(path: Path, root: Path, *, description: str) -> None:
    relative = _relative_under(path, root, description=description)
    current = _lexical_absolute(root)
    root_stat = os.lstat(current)
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise RheaStageError(f"repository root is not a real directory: {current}")
    for index, component in enumerate(relative.parts):
        current /= component
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise RheaStageError(f"{description} traverses a symlink: {current}")
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise RheaStageError(f"{description} parent is not a directory: {current}")


def _read_open_file(descriptor: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _capture(
    path: Path,
    *,
    repo_root: Path,
    description: str,
    expected_sha256: str | None,
) -> CapturedArtifact:
    absolute = _lexical_absolute(path)
    relative = _relative_under(absolute, repo_root, description=description)
    try:
        _reject_symlink_components(absolute, repo_root, description=description)
    except FileNotFoundError as exc:
        raise RheaStageError(f"missing {description}: {absolute}") from exc
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RheaStageError(f"{description} is not a regular file: {absolute}")
        if before.st_nlink != 1:
            raise RheaStageError(f"{description} must have exactly one hard link: {absolute}")
        raw = _read_open_file(descriptor)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if _identity(before) != _identity(after) or len(raw) != after.st_size:
        raise RheaStageError(f"{description} changed while being captured: {absolute}")
    path_stat = os.lstat(absolute)
    if _identity(path_stat) != _identity(after):
        raise RheaStageError(f"{description} path identity changed during capture: {absolute}")
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None:
        if _SHA256_RE.fullmatch(expected_sha256) is None:
            raise RheaStageError(f"invalid expected SHA-256 for {description}")
        if digest != expected_sha256:
            raise RheaStageError(
                f"{description} SHA-256 mismatch: expected {expected_sha256}, observed {digest}"
            )
    return CapturedArtifact(
        path=absolute,
        relative_path=relative.as_posix(),
        sha256=digest,
        size=len(raw),
        identity=_identity(after),
        raw=raw,
    )


def _assert_unchanged(artifact: CapturedArtifact, *, repo_root: Path, description: str) -> None:
    replay = _capture(
        artifact.path,
        repo_root=repo_root,
        description=description,
        expected_sha256=artifact.sha256,
    )
    if replay.identity != artifact.identity or replay.raw != artifact.raw:
        raise RheaStageError(f"{description} changed after capture: {artifact.path}")


def _strict_lf_text(artifact: CapturedArtifact, *, description: str) -> str:
    if not artifact.raw or not artifact.raw.endswith(b"\n"):
        raise RheaStageError(f"{description} must be nonempty LF-terminated text")
    if b"\r" in artifact.raw or b"\x00" in artifact.raw:
        raise RheaStageError(f"{description} must use canonical LF text without NUL")
    try:
        return artifact.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RheaStageError(f"{description} is not UTF-8") from exc


def parse_release_properties(artifact: CapturedArtifact) -> tuple[str, str]:
    lines = _strict_lf_text(artifact, description="Rhea release properties").splitlines()
    if len(lines) != 2:
        raise RheaStageError("Rhea release properties must contain exactly two declarations")
    values: dict[str, str] = {}
    for line in lines:
        if line.count("=") != 1:
            raise RheaStageError("malformed Rhea release property")
        key, value = line.split("=", 1)
        if key in values:
            raise RheaStageError(f"duplicate Rhea release property {key!r}")
        values[key] = value
    if set(values) != {"rhea.release.number", "rhea.release.date"}:
        raise RheaStageError("unexpected Rhea release property set")
    release = values["rhea.release.number"]
    release_date = values["rhea.release.date"]
    if _RELEASE_RE.fullmatch(release) is None or _DATE_RE.fullmatch(release_date) is None:
        raise RheaStageError("invalid Rhea release number or date")
    return release, release_date


def validate_tsv_readme(artifact: CapturedArtifact) -> None:
    text = _strict_lf_text(artifact, description="Rhea TSV README")
    required = (
        "Files named rhea2<db>.tsv contain cross-references to other databases",
        "RHEA_ID:",
        "DIRECTION:",
        "MASTER_ID:",
        "ID:",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise RheaStageError(f"Rhea TSV README lacks required contract text: {missing}")


def validate_license(artifact: CapturedArtifact) -> None:
    text = _strict_lf_text(artifact, description="Rhea license")
    if "Creative Commons Attribution 4.0 International" not in text:
        raise RheaStageError("Rhea license does not declare CC BY 4.0")
    if "All files in the Rhea FTP directory may be copied and redistributed freely" not in text:
        raise RheaStageError("Rhea license lacks the FTP redistribution declaration")


def parse_directions(artifact: CapturedArtifact) -> dict[str, dict[str, str]]:
    lines = _strict_lf_text(artifact, description="Rhea directions TSV").splitlines()
    if not lines or lines[0] != DIRECTIONS_HEADER:
        raise RheaStageError("Rhea directions TSV header mismatch")
    result: dict[str, dict[str, str]] = {}
    seen_ids: set[str] = set()
    for line_number, line in enumerate(lines[1:], 2):
        fields = line.split("\t")
        if len(fields) != 4 or any(_POSITIVE_ID_RE.fullmatch(value) is None for value in fields):
            raise RheaStageError(f"invalid Rhea directions row at line {line_number}")
        master, lr, rl, bi = fields
        if master in result:
            raise RheaStageError(f"duplicate Rhea master direction row {master}")
        if len(set(fields)) != 4 or seen_ids.intersection(fields):
            raise RheaStageError(
                f"Rhea direction IDs are not globally unique at line {line_number}"
            )
        seen_ids.update(fields)
        result[master] = {"UN": master, "LR": lr, "RL": rl, "BI": bi}
    if not result:
        raise RheaStageError("Rhea directions TSV has no rows")
    return result


def parse_reactions(artifact: CapturedArtifact) -> dict[str, str]:
    lines = _strict_lf_text(artifact, description="Rhea reactions TSV").splitlines()
    if not lines or lines[0] != REACTIONS_HEADER:
        raise RheaStageError("Rhea reactions TSV header mismatch")
    result: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], 2):
        fields = line.split("\t")
        if len(fields) != 4:
            raise RheaStageError(f"Rhea reactions row {line_number} must have four fields")
        match = _RHEA_IDENTIFIER_RE.fullmatch(fields[0])
        if match is None or not fields[1]:
            raise RheaStageError(f"invalid Rhea reaction at line {line_number}")
        master = match.group(1)
        if master in result:
            raise RheaStageError(f"duplicate Rhea reaction {fields[0]}")
        result[master] = fields[1]
    if not result:
        raise RheaStageError("Rhea reactions TSV has no rows")
    return result


def parse_mapping(
    artifact: CapturedArtifact,
    *,
    directions: Mapping[str, Mapping[str, str]],
    reactions: Mapping[str, str],
) -> tuple[MappingRow, ...]:
    lines = _strict_lf_text(
        artifact, description="Rhea to UniProtKB/Swiss-Prot mapping TSV"
    ).splitlines()
    if not lines or lines[0] != MAPPING_HEADER:
        raise RheaStageError("Rhea to UniProtKB mapping TSV header mismatch")
    result: list[MappingRow] = []
    seen_physical: set[tuple[str, str, str, str]] = set()
    for line_number, line in enumerate(lines[1:], 2):
        fields = line.split("\t")
        if len(fields) != 4:
            raise RheaStageError(f"Rhea mapping row {line_number} must have four fields")
        rhea_id, direction, master, accession = fields
        physical = (rhea_id, direction, master, accession)
        if physical in seen_physical:
            raise RheaStageError(f"duplicate Rhea mapping row at line {line_number}")
        seen_physical.add(physical)
        if (
            _POSITIVE_ID_RE.fullmatch(rhea_id) is None
            or _POSITIVE_ID_RE.fullmatch(master) is None
            or direction not in {"UN", "LR", "RL", "BI"}
            or _UNIPROT_PRIMARY_RE.fullmatch(accession) is None
        ):
            raise RheaStageError(f"invalid Rhea mapping fields at line {line_number}")
        quartet = directions.get(master)
        if quartet is None or quartet[direction] != rhea_id:
            raise RheaStageError(f"Rhea mapping direction/master mismatch at line {line_number}")
        if master not in reactions:
            raise RheaStageError(f"Rhea mapping master {master} lacks a reaction row")
        result.append(
            MappingRow(
                rhea_id=rhea_id,
                direction=direction,
                master_id=master,
                accession=accession,
                line_number=line_number,
                raw_line_sha256=hashlib.sha256((line + "\n").encode("utf-8")).hexdigest(),
            )
        )
    if not result:
        raise RheaStageError("Rhea to UniProtKB mapping TSV has no rows")
    return tuple(result)


class _UniqueSafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueSafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise RheaStageError(f"duplicate YAML key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _load_yaml_mapping(artifact: CapturedArtifact) -> Mapping[str, Any]:
    try:
        value = yaml.load(artifact.raw, Loader=_UniqueSafeLoader)
    except (yaml.YAMLError, RheaStageError) as exc:
        raise RheaStageError(f"invalid trait YAML {artifact.relative_path}: {exc}") from exc
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise RheaStageError(f"trait is not a string-keyed mapping: {artifact.relative_path}")
    return value


def _reject_trait_tree_symlinks(traits_root: Path) -> None:
    root = _lexical_absolute(traits_root)
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        for name in [*dirnames, *filenames]:
            path = Path(directory) / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                raise RheaStageError(f"trait tree contains a symlink: {path}")


def _exact_rhea_route_paths(traits_dir: Path) -> tuple[Path, ...]:
    expected_dir = _lexical_absolute(traits_dir)
    try:
        names = os.listdir(expected_dir)
    except OSError as exc:
        raise RheaStageError(f"cannot inventory Rhea trait route: {exc}") from exc
    paths: list[Path] = []
    for name in sorted(names):
        path = expected_dir / name
        try:
            metadata = os.lstat(path)
        except OSError as exc:
            raise RheaStageError(f"cannot inspect Rhea trait route entry {path}: {exc}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise RheaStageError(f"Rhea trait route contains a symlink: {path}")
        if not stat.S_ISREG(metadata.st_mode) or path.suffix != ".yaml":
            raise RheaStageError(
                f"Rhea trait route must contain only flat regular lowercase .yaml records: {path}"
            )
        paths.append(path)
    if not paths:
        raise RheaStageError("Rhea trait route is empty")
    return tuple(paths)


def _candidate_rhea_trait_paths(traits_root: Path, route_paths: Sequence[Path]) -> tuple[Path, ...]:
    """Exhaustively prefilter files that can decode to a Rhea identifier.

    A YAML scalar equal to ``RHEA:*`` contains the literal text, an escape (and
    therefore a backslash), or NUL bytes when encoded as UTF-16/32.  Every
    candidate is parsed below, so quoted, folded, escaped, ignored, hidden, and
    alternate-extension semantic shadows cannot evade namespace inventory.
    """

    paths = _ripgrep_candidate_paths(traits_root)
    if paths is None:
        paths = _walked_candidate_paths(traits_root)
    paths.update(route_paths)
    return tuple(sorted(_lexical_absolute(path) for path in paths))


def _ripgrep_candidate_paths(traits_root: Path) -> set[Path] | None:
    """Ripgrep's candidate set, or ``None`` when ripgrep is not installed.

    Ripgrep is not a declared dependency of this repository and CI does not
    install it (#571), so its absence must be a fallback and not a failure.
    An `rg` that is present but errors is still fatal.
    """

    executable = shutil.which("rg")
    if executable is None:
        return None
    command = [
        executable,
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
        "RHEA:",
        "-e",
        r"\\",
        "-e",
        r"\x00",
        "--",
        os.fspath(traits_root),
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True)
    except OSError as exc:
        raise RheaStageError(f"cannot run ripgrep Rhea trait prefilter: {exc}") from exc
    if completed.returncode not in {0, 1}:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RheaStageError(f"Rhea trait prefilter failed: {detail}")
    try:
        return {
            Path(raw_path.decode("utf-8")) for raw_path in completed.stdout.split(b"\0") if raw_path
        }
    except UnicodeDecodeError as exc:
        raise RheaStageError(f"ripgrep returned a non-UTF-8 trait path: {exc}") from exc


def _walked_candidate_paths(traits_root: Path) -> set[Path]:
    """Every YAML file under the root: a strict superset of the ripgrep prefilter.

    Deliberately not a reimplementation of ripgrep's matching.  Reproducing its
    escape, NUL, and UTF-16 semantics in a second matcher is exactly how two
    paths drift apart (#539), and the drift would be silent.  Over-inclusion
    cannot change the result, because every candidate is parsed below; it only
    costs time.  ``followlinks=False`` matches ripgrep's default traversal.
    """

    paths: set[Path] = set()
    for directory, _subdirectories, filenames in os.walk(traits_root, followlinks=False):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in {".yaml", ".yml"}:
                paths.add(Path(directory) / filename)
    return paths


def _scan_rhea_trait_paths(
    *, traits_root: Path, traits_dir: Path, repo_root: Path
) -> tuple[
    dict[str, Path],
    tuple[dict[str, str], ...],
    tuple[CapturedArtifact, ...],
    tuple[Path, ...],
]:
    root = _lexical_absolute(traits_root)
    expected_dir = _lexical_absolute(traits_dir)
    _relative_under(root, repo_root, description="trait root")
    _relative_under(expected_dir, repo_root, description="Rhea trait directory")
    _reject_trait_tree_symlinks(root)
    route_paths = _exact_rhea_route_paths(expected_dir)
    candidate_paths = _candidate_rhea_trait_paths(root, route_paths)
    result: dict[str, Path] = {}
    rows: list[dict[str, str]] = []
    candidate_artifacts: list[CapturedArtifact] = []
    for path in candidate_paths:
        artifact = _capture(
            path,
            repo_root=repo_root,
            description="Rhea trait identity candidate",
            expected_sha256=None,
        )
        candidate_artifacts.append(artifact)
        record = _load_yaml_mapping(artifact)
        identifier = record.get("identifier")
        match = _RHEA_IDENTIFIER_RE.fullmatch(identifier) if isinstance(identifier, str) else None
        in_exact_route = path.parent == expected_dir and path.suffix == ".yaml"
        if in_exact_route and match is None:
            raise RheaStageError(f"Rhea trait route record lacks an exact RHEA identifier: {path}")
        if match is None:
            continue
        trait_id = identifier
        if not in_exact_route:
            raise RheaStageError(
                f"Rhea semantic shadow exists outside exact source directory: {path}"
            )
        if trait_id in result:
            raise RheaStageError(f"duplicate Rhea trait identifier {trait_id}")
        result[trait_id] = path
        rows.append(
            {
                "trait_id": trait_id,
                "trait_record_path": _relative_under(
                    path, repo_root, description="Rhea trait record"
                ).as_posix(),
            }
        )
    rows.sort(key=lambda row: row["trait_id"])
    return result, tuple(rows), tuple(candidate_artifacts), route_paths


def _validate_trait(artifact: CapturedArtifact, *, trait_id: str, equation: str) -> TraitBinding:
    record = _load_yaml_mapping(artifact)
    expected_definition = (
        f"Enzymatic reaction ({trait_id}): {equation}. A specific curated "
        "biochemical reaction; a protein with this activity catalyses it."
    )
    exact = {
        "identifier": trait_id,
        "label": equation,
        "definition": expected_definition,
        **TRAIT_CONTRACT,
    }
    for field, expected in exact.items():
        if record.get(field) != expected:
            raise RheaStageError(f"{artifact.relative_path}: Rhea trait field {field!r} drifted")
    if record.get("mapping_status") not in {"SEEDED", "REVIEWED"}:
        raise RheaStageError(f"{artifact.relative_path}: invalid Rhea mapping_status")
    examples = record.get("canonical_examples")
    if examples is not None and not isinstance(examples, list):
        raise RheaStageError(f"{artifact.relative_path}: canonical_examples is not a list")
    return TraitBinding(
        trait_id=trait_id,
        label=equation,
        path=artifact.path,
        relative_path=artifact.relative_path,
        sha256=artifact.sha256,
        has_canonical_examples=bool(examples),
    )


def _strict_json_object(line: str, *, source: str) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise RheaStageError(f"{source}: non-finite JSON constant {value}")

    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise RheaStageError(f"{source}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(line, object_pairs_hook=pairs, parse_constant=reject_constant)
    except (json.JSONDecodeError, RheaStageError) as exc:
        raise RheaStageError(f"{source}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise RheaStageError(f"{source}: registry row is not an object")
    return value


def parse_protein_registry(
    artifact: CapturedArtifact, *, expected_release: str
) -> dict[str, dict[str, Any]]:
    text = _strict_lf_text(artifact, description="ProteinReference registry")
    result: dict[str, dict[str, Any]] = {}
    prior_id = ""
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise RheaStageError(f"empty ProteinReference row at line {line_number}")
        row = _strict_json_object(line, source=f"{artifact.relative_path}:{line_number}")
        if canonical_json(row) != line:
            raise RheaStageError(f"noncanonical ProteinReference row at line {line_number}")
        protein_id = row.get("protein_id")
        if not isinstance(protein_id, str) or _UNIPROT_ID_RE.fullmatch(protein_id) is None:
            raise RheaStageError(f"invalid ProteinReference protein_id at line {line_number}")
        if protein_id <= prior_id:
            raise RheaStageError("ProteinReference registry must be strictly sorted and unique")
        prior_id = protein_id
        sequence = row.get("sequence")
        if not isinstance(sequence, str) or _SEQUENCE_RE.fullmatch(sequence) is None:
            raise RheaStageError(f"invalid ProteinReference sequence at line {line_number}")
        if row.get("sequence_length") != len(sequence):
            raise RheaStageError(f"ProteinReference sequence length mismatch at line {line_number}")
        if row.get("sequence_sha256") != hashlib.sha256(sequence.encode("ascii")).hexdigest():
            raise RheaStageError(f"ProteinReference sequence digest mismatch at line {line_number}")
        if row.get("uniprot_release") != expected_release:
            raise RheaStageError(f"ProteinReference release mismatch at line {line_number}")
        for field in ("protein_label", "taxon_id", "taxon_label"):
            if not isinstance(row.get(field), str) or not row[field]:
                raise RheaStageError(
                    f"ProteinReference field {field!r} is invalid at line {line_number}"
                )
        if not isinstance(row.get("reviewed"), bool):
            raise RheaStageError(f"ProteinReference reviewed flag invalid at line {line_number}")
        if not isinstance(row.get("sequence_version"), int) or isinstance(
            row.get("sequence_version"), bool
        ):
            raise RheaStageError(f"ProteinReference sequence_version invalid at line {line_number}")
        result[protein_id] = row
    return result


def _artifact_projection(artifact: CapturedArtifact, *, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": artifact.relative_path,
        "size": artifact.size,
        "sha256": artifact.sha256,
        "provider_acquisition_receipt": None,
    }


def _trait_projection(binding: TraitBinding) -> dict[str, Any]:
    return {
        "trait_id": binding.trait_id,
        "trait_label": binding.label,
        "trait_record_path": binding.relative_path,
        "trait_record_sha256": binding.sha256,
        "trait_record_has_canonical_examples": binding.has_canonical_examples,
    }


def _association_projection(row: MappingRow) -> dict[str, Any]:
    return {
        "rhea_id": f"RHEA:{row.rhea_id}",
        "direction": row.direction,
        "master_trait_id": row.trait_id,
        "uniprot_accession": row.accession,
        "source_line_number": row.line_number,
        "source_raw_line_sha256": row.raw_line_sha256,
    }


def _reference_projection(
    reference: Mapping[str, Any] | None, *, registry_sha256: str, protein_id: str
) -> dict[str, Any]:
    if reference is None:
        return {
            "status": "MISSING_EXACT_PROTEIN_REFERENCE",
            "protein_id": protein_id,
            "registry_sha256": registry_sha256,
            "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
        }
    return {
        "status": "EXACT_LOCAL_REFERENCE_PRESENT_WITHOUT_FETCH_RECEIPT_BINDING",
        "protein_id": protein_id,
        "protein_label": reference["protein_label"],
        "taxon_id": reference["taxon_id"],
        "taxon_label": reference["taxon_label"],
        "reviewed": reference["reviewed"],
        "sequence_length": reference["sequence_length"],
        "sequence_sha256": reference["sequence_sha256"],
        "sequence_version": reference["sequence_version"],
        "uniprot_release": reference["uniprot_release"],
        "protein_reference_row_sha256": value_sha256(reference),
        "registry_sha256": registry_sha256,
        "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
    }


def _candidate_row(
    *,
    trait: TraitBinding,
    protein_id: str,
    associations: Sequence[MappingRow],
    reference: Mapping[str, Any] | None,
    registry_sha256: str,
    source_snapshot_id: str,
    source_release: str,
    mapping_path: str,
) -> dict[str, Any]:
    source_associations = [_association_projection(item) for item in associations]
    blockers = list(GLOBAL_PROMOTION_BLOCKERS)
    if reference is None:
        blockers.append(MISSING_PROTEIN_REFERENCE)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": CANDIDATE_KIND,
        "qualification_status": "CANDIDATE_ONLY",
        "qualification_claimed": False,
        "grounding_evidence_emitted": False,
        "write_action_performed": False,
        "network_action_performed": False,
        "trait_id": trait.trait_id,
        "source_trait_id": trait.trait_id,
        "protein_id": protein_id,
        "scope": SCOPE,
        "mapping_method": MAPPING_METHOD,
        "membership_basis": MEMBERSHIP_BASIS,
        "evidence_source": PROVIDER_NAME,
        "source_release": source_release,
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "provider_source": mapping_path,
        "provider_release": source_release,
        "provider_release_binding_status": (
            "COLOCATED_RELEASE_PROPERTY_CONTENT_BOUND_WITHOUT_ACQUISITION_RECEIPT"
        ),
        "provider_entry_sha256": value_sha256(source_associations),
        "source_snapshot_id": source_snapshot_id,
        "source_association_count": len(source_associations),
        "source_associations": source_associations,
        "trait_binding": _trait_projection(trait),
        "protein_reference_binding": _reference_projection(
            reference, registry_sha256=registry_sha256, protein_id=protein_id
        ),
        "promotion_blockers": blockers,
    }
    return _content_address(
        row,
        id_field="candidate_id",
        prefix="rhea-uniprot-source-membership-candidate:",
        row_hash_field="candidate_row_sha256",
    )


def _request_rows(
    candidates: Sequence[Mapping[str, Any]],
    *,
    registry: Mapping[str, Mapping[str, Any]],
    expected_uniprot_release: str,
    source_snapshot_id: str,
) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if candidate["protein_id"] not in registry:
            grouped[str(candidate["protein_id"])].append(candidate)
    requests: list[dict[str, Any]] = []
    for protein_id, memberships in sorted(grouped.items()):
        candidate_ids = sorted(str(item["candidate_id"]) for item in memberships)
        trait_ids = sorted({str(item["trait_id"]) for item in memberships})
        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "kind": REQUEST_KIND,
            "request_status": "PROTEIN_REFERENCE_FETCH_REQUIRED",
            "qualification_claimed": False,
            "network_action_performed": False,
            "write_action_performed": False,
            "protein_id": protein_id,
            "expected_uniprot_release": expected_uniprot_release,
            "request_reason": MISSING_PROTEIN_REFERENCE,
            "source_snapshot_id": source_snapshot_id,
            "rhea_trait_count": len(trait_ids),
            "rhea_trait_ids": trait_ids,
            "source_candidate_count": len(candidate_ids),
            "source_candidate_ids": candidate_ids,
            "source_candidate_ids_sha256": value_sha256(candidate_ids),
            "verified_fetch_receipt_required": True,
        }
        requests.append(
            _content_address(
                row,
                id_field="request_id",
                prefix="rhea-uniprot-protein-request:",
                row_hash_field="request_row_sha256",
            )
        )
    return tuple(requests)


def build_stage(
    *,
    mapping_path: Path = DEFAULT_MAPPING,
    release_properties_path: Path = DEFAULT_RELEASE_PROPERTIES,
    tsv_readme_path: Path = DEFAULT_TSV_README,
    license_path: Path = DEFAULT_LICENSE,
    directions_path: Path = DEFAULT_DIRECTIONS,
    reactions_path: Path = DEFAULT_REACTIONS,
    traits_root: Path = DEFAULT_TRAITS_ROOT,
    traits_dir: Path = DEFAULT_TRAITS_DIR,
    protein_registry_path: Path = DEFAULT_PROTEIN_REGISTRY,
    repo_root: Path = REPO_ROOT,
    expected_source_sha256: Mapping[str, str | None] = CURRENT_SOURCE_SHA256,
    expected_rhea_release: str = EXPECTED_RHEA_RELEASE,
    expected_rhea_release_date: str = EXPECTED_RHEA_RELEASE_DATE,
    expected_uniprot_release: str = EXPECTED_UNIPROT_RELEASE,
) -> StageResult:
    roles = {
        "mapping": mapping_path,
        "release_properties": release_properties_path,
        "tsv_readme": tsv_readme_path,
        "license": license_path,
        "directions": directions_path,
        "reactions": reactions_path,
    }
    if set(expected_source_sha256) != set(roles):
        raise RheaStageError("expected_source_sha256 must name exactly all six source roles")
    root = _lexical_absolute(repo_root)
    artifacts = {
        role: _capture(
            path,
            repo_root=root,
            description=f"Rhea {role.replace('_', ' ')} artifact",
            expected_sha256=expected_source_sha256[role],
        )
        for role, path in roles.items()
    }
    release, release_date = parse_release_properties(artifacts["release_properties"])
    if release != expected_rhea_release or release_date != expected_rhea_release_date:
        raise RheaStageError(
            "Rhea release mismatch: "
            f"expected {expected_rhea_release}/{expected_rhea_release_date}, "
            f"observed {release}/{release_date}"
        )
    validate_tsv_readme(artifacts["tsv_readme"])
    validate_license(artifacts["license"])
    directions = parse_directions(artifacts["directions"])
    reactions = parse_reactions(artifacts["reactions"])
    if set(directions) != set(reactions):
        raise RheaStageError("Rhea directions and reaction master sets disagree")
    mapping = parse_mapping(artifacts["mapping"], directions=directions, reactions=reactions)
    (
        trait_paths,
        trait_path_rows,
        trait_identity_artifacts,
        rhea_route_paths,
    ) = _scan_rhea_trait_paths(traits_root=traits_root, traits_dir=traits_dir, repo_root=root)
    reaction_trait_ids = {f"RHEA:{master}" for master in reactions}
    if set(trait_paths) != reaction_trait_ids:
        missing = sorted(reaction_trait_ids - set(trait_paths))[:10]
        extra = sorted(set(trait_paths) - reaction_trait_ids)[:10]
        raise RheaStageError(f"Rhea reaction/trait sets disagree; missing={missing}, extra={extra}")
    selected_trait_ids = sorted({item.trait_id for item in mapping})
    trait_artifacts: list[CapturedArtifact] = []
    traits: dict[str, TraitBinding] = {}
    for trait_id in selected_trait_ids:
        master = trait_id.removeprefix("RHEA:")
        artifact = _capture(
            trait_paths[trait_id],
            repo_root=root,
            description=f"Rhea trait {trait_id}",
            expected_sha256=None,
        )
        trait_artifacts.append(artifact)
        traits[trait_id] = _validate_trait(artifact, trait_id=trait_id, equation=reactions[master])
    registry_artifact = _capture(
        protein_registry_path,
        repo_root=root,
        description="ProteinReference registry",
        expected_sha256=None,
    )
    registry = parse_protein_registry(registry_artifact, expected_release=expected_uniprot_release)
    source_artifact_rows = [
        _artifact_projection(artifacts[role], role=f"RHEA_{role.upper()}") for role in roles
    ]
    source_snapshot: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "RHEA_UNIPROT_SOURCE_SNAPSHOT",
        "provider": PROVIDER_NAME,
        "provider_release": release,
        "provider_release_date": release_date,
        "provider_release_binding_status": (
            "COLOCATED_RELEASE_PROPERTY_CONTENT_BOUND_WITHOUT_ACQUISITION_RECEIPT"
        ),
        "provider_license": "CC BY 4.0",
        "provider_acquisition_receipt": None,
        "membership_basis": MEMBERSHIP_BASIS,
        "source_artifacts": source_artifact_rows,
    }
    _content_address(
        source_snapshot,
        id_field="source_snapshot_id",
        prefix="rhea-uniprot-source-snapshot:",
        row_hash_field="source_snapshot_row_sha256",
    )
    source_snapshot_id = str(source_snapshot["source_snapshot_id"])
    grouped: dict[tuple[str, str], list[MappingRow]] = defaultdict(list)
    for item in mapping:
        grouped[(item.trait_id, item.protein_id)].append(item)
    candidates: list[dict[str, Any]] = []
    excluded_existing_examples = 0
    for (trait_id, protein_id), associations in sorted(grouped.items()):
        trait = traits[trait_id]
        if trait.has_canonical_examples:
            excluded_existing_examples += 1
            continue
        candidates.append(
            _candidate_row(
                trait=trait,
                protein_id=protein_id,
                associations=sorted(
                    associations,
                    key=lambda item: (
                        int(item.rhea_id),
                        item.direction,
                        item.line_number,
                    ),
                ),
                reference=registry.get(protein_id),
                registry_sha256=registry_artifact.sha256,
                source_snapshot_id=source_snapshot_id,
                source_release=release,
                mapping_path=artifacts["mapping"].relative_path,
            )
        )
    requests = _request_rows(
        candidates,
        registry=registry,
        expected_uniprot_release=expected_uniprot_release,
        source_snapshot_id=source_snapshot_id,
    )
    status_counts = Counter(row["protein_reference_binding"]["status"] for row in candidates)
    trait_binding_rows = [_trait_projection(traits[trait_id]) for trait_id in selected_trait_ids]
    candidate_bytes = _rows_bytes(candidates)
    request_bytes = _rows_bytes(requests)
    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": SUMMARY_KIND,
        "stage_status": "DIRECT_SOURCE_MEMBERSHIP_CANDIDATES_ONLY",
        "qualification_claimed": False,
        "grounding_evidence_emitted_count": 0,
        "network_action_performed": False,
        "write_action_performed": False,
        "writer_available": False,
        "trait_tree_must_be_quiescent": True,
        "trait_tree_verification_semantics": (
            "NOFOLLOW_CONTENT_READS_WITH_WHOLE_TREE_IDENTIFIER_SCAN_AND_FINAL_REPLAY_"
            "NOT_AN_ATOMIC_FILESYSTEM_SNAPSHOT"
        ),
        "scope_policy": "RHEA_TRAITS_WITHOUT_CANONICAL_EXAMPLES",
        "ec_bridge_policy": "EC_ONLY_ASSOCIATIONS_ARE_CATEGORICALLY_EXCLUDED",
        "source_snapshot": source_snapshot,
        "protein_registry": _artifact_projection(
            registry_artifact,
            role="LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING",
        ),
        "expected_uniprot_release": expected_uniprot_release,
        "protein_registry_fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
        "protein_registry_row_count": len(registry),
        "rhea_reaction_count": len(reactions),
        "rhea_trait_count": len(trait_paths),
        "rhea_trait_path_rows_sha256": hashlib.sha256(_rows_bytes(trait_path_rows)).hexdigest(),
        "mapped_rhea_trait_count": len(selected_trait_ids),
        "mapped_trait_binding_rows_sha256": hashlib.sha256(
            _rows_bytes(trait_binding_rows)
        ).hexdigest(),
        "source_mapping_physical_row_count": len(mapping),
        "source_unique_trait_protein_pair_count": len(grouped),
        "source_unique_uniprot_accession_count": len({item.accession for item in mapping}),
        "excluded_existing_example_pair_count": excluded_existing_examples,
        "candidate_count": len(candidates),
        "candidate_trait_count": len({row["trait_id"] for row in candidates}),
        "candidate_protein_count": len({row["protein_id"] for row in candidates}),
        "protein_reference_binding_status_counts": dict(sorted(status_counts.items())),
        "missing_protein_reference_request_count": len(requests),
        "candidate_rows_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
        "protein_request_rows_sha256": hashlib.sha256(request_bytes).hexdigest(),
        "combined_non_summary_rows_sha256": hashlib.sha256(
            candidate_bytes + request_bytes
        ).hexdigest(),
        "promotion_blockers": list(GLOBAL_PROMOTION_BLOCKERS),
        "provider_source_contract_status": (
            "DIRECT_TSV_STRUCTURAL_CONTRACT_DEFINED_BUT_ACQUISITION_RECEIPT_AND_VERIFIER_ABSENT"
        ),
    }
    _content_address(
        summary,
        id_field="stage_id",
        prefix="rhea-uniprot-source-native-stage:",
        row_hash_field="summary_row_sha256",
    )

    for role, artifact in artifacts.items():
        _assert_unchanged(
            artifact, repo_root=root, description=f"Rhea {role.replace('_', ' ')} artifact"
        )
    _assert_unchanged(registry_artifact, repo_root=root, description="ProteinReference registry")
    for artifact in trait_artifacts:
        _assert_unchanged(artifact, repo_root=root, description="Rhea trait record")
    final_traits_root = _lexical_absolute(traits_root)
    final_traits_dir = _lexical_absolute(traits_dir)
    _reject_trait_tree_symlinks(final_traits_root)
    final_route_paths = _exact_rhea_route_paths(final_traits_dir)
    final_candidate_paths = _candidate_rhea_trait_paths(final_traits_root, final_route_paths)
    initial_candidate_paths = tuple(artifact.path for artifact in trait_identity_artifacts)
    if final_route_paths != rhea_route_paths or final_candidate_paths != initial_candidate_paths:
        raise RheaStageError("Rhea trait identifier membership drifted while staging")
    for artifact in trait_identity_artifacts:
        _assert_unchanged(
            artifact,
            repo_root=root,
            description="Rhea trait identity candidate",
        )
    return StageResult(tuple(candidates), requests, summary)


def acquisition_plan(*, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = _lexical_absolute(repo_root)
    targets = {
        "mapping": DEFAULT_MAPPING,
        "release_properties": DEFAULT_RELEASE_PROPERTIES,
        "tsv_readme": DEFAULT_TSV_README,
        "license": DEFAULT_LICENSE,
        "directions": DEFAULT_DIRECTIONS,
        "reactions": DEFAULT_REACTIONS,
    }
    rows = [
        {
            "role": role,
            "url": OFFICIAL_URLS[role],
            "target_path": _relative_under(
                path, root, description=f"Rhea acquisition target {role}"
            ).as_posix(),
            "expected_sha256": CURRENT_SOURCE_SHA256[role],
        }
        for role, path in targets.items()
    ]
    plan: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": ACQUISITION_PLAN_KIND,
        "plan_status": "NO_NETWORK_NO_WRITE_REQUEST_PLAN_ONLY",
        "provider": PROVIDER_NAME,
        "expected_provider_release": EXPECTED_RHEA_RELEASE,
        "expected_provider_release_date": EXPECTED_RHEA_RELEASE_DATE,
        "expected_provider_license": "CC BY 4.0",
        "network_action_performed": False,
        "write_action_performed": False,
        "apply_authorized": False,
        "current_endpoint_expiry_policy": (
            "FAIL_IF_CURRENT_RHEA_RELEASE_PROPERTIES_NO_LONGER_EQUAL_141_AND_2026-06-10"
        ),
        "acquisition_receipt_required": True,
        "required_receipt_semantics": (
            "RAW_RESPONSE_BYTES_URL_STATUS_HEADERS_SIZE_SHA256_AND_RELEASE_COHERENCE"
        ),
        "artifacts": rows,
        "post_acquisition_stage_command": (
            ".venv/bin/python scripts/stage_rhea_uniprot_grounding.py --summary-only"
        ),
        "forbidden_substitutions": [
            "EXPASY_ENZYME_EC_DR_LINES",
            "RHEA2EC_BRIDGE",
            "UNRECEIPTED_SYNTHETIC_MAPPING",
            "PARTIAL_MAPPING_EXPORT",
        ],
    }
    return _content_address(
        plan,
        id_field="plan_id",
        prefix="rhea-uniprot-source-acquisition-plan:",
        row_hash_field="plan_row_sha256",
    )


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows: Sequence[Mapping[str, Any]] = (
        [result.summary]
        if summary_only
        else [*result.candidates, *result.protein_requests, result.summary]
    )
    return "".join(canonical_json(row) + "\n" for row in rows)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--acquisition-plan",
        action="store_true",
        help="print the canonical no-network release-141 acquisition plan",
    )
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--release-properties", type=Path, default=DEFAULT_RELEASE_PROPERTIES)
    parser.add_argument("--tsv-readme", type=Path, default=DEFAULT_TSV_README)
    parser.add_argument("--license", type=Path, default=DEFAULT_LICENSE)
    parser.add_argument("--directions", type=Path, default=DEFAULT_DIRECTIONS)
    parser.add_argument("--reactions", type=Path, default=DEFAULT_REACTIONS)
    parser.add_argument("--traits-root", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument("--traits-dir", type=Path, default=DEFAULT_TRAITS_DIR)
    parser.add_argument("--protein-registry", type=Path, default=DEFAULT_PROTEIN_REGISTRY)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.acquisition_plan:
            if args.summary_only:
                raise RheaStageError("--summary-only cannot be combined with --acquisition-plan")
            sys.stdout.write(canonical_json(acquisition_plan()) + "\n")
            return 0
        result = build_stage(
            mapping_path=args.mapping,
            release_properties_path=args.release_properties,
            tsv_readme_path=args.tsv_readme,
            license_path=args.license,
            directions_path=args.directions,
            reactions_path=args.reactions,
            traits_root=args.traits_root,
            traits_dir=args.traits_dir,
            protein_registry_path=args.protein_registry,
        )
    except (OSError, RheaStageError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
