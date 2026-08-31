#!/usr/bin/env python3
"""Stage exact ComplexPortal expanded-component claims as canonical JSONL.

Only the explicitly pinned 28-file curated local ComplexTAB snapshot is
admitted. ``9606_predicted.tsv`` is categorically excluded. Protein membership
is read exclusively from column 19, ``Expanded participant list``; column 5 is
parsed and retained only as direct-versus-expanded provenance.

The local files came from ComplexPortal's moving ``/current/`` endpoint and do
not carry a provider release receipt. Candidates therefore remain
``CANDIDATE_PROTEIN`` and carry a separate staging reason. Unsupported
expanded tokens and rows whose ECO field is not an exact admitted value are
emitted as content-addressed blocked-token rows, never silently dropped or
coerced. Every accepted UniProt identity is partitioned against the exact local
release-2026_02 ProteinReference registry, but that registry has no verified
fetch receipt at this boundary. Missing references become deduplicated request
rows. This command has no network, output-file, apply, promotion, or
GroundingEvidence writer mode.

The whole-tree semantic-shadow scan and final membership recheck require a
quiescent trait tree. Descriptor-relative no-follow reads bind every consumed
file and reject practical path substitution, but a userspace scan is not an
atomic filesystem snapshot against an uncooperative concurrent writer.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seed_complexportal as complexportal_seeder  # noqa: E402
import validate_uniprot_grounding as grounding  # noqa: E402

SCHEMA_VERSION = 3
CANDIDATE_KIND = "COMPLEXPORTAL_GROUNDING_CANDIDATE"
BLOCKED_TOKEN_KIND = "COMPLEXPORTAL_GROUNDING_BLOCKED_TOKEN"
REQUEST_KIND = "COMPLEXPORTAL_PROTEIN_REFERENCE_REQUEST"
SUMMARY_KIND = "COMPLEXPORTAL_GROUNDING_STAGE_SUMMARY"
STAGING_REASON = "STAGING_ONLY_MISSING_PROVIDER_RELEASE"
QUALIFICATION_STATUS = "CANDIDATE_PROTEIN"
MAPPING_METHOD = "SOURCE_MEMBERSHIP"
MEMBERSHIP_BASIS = "EXPANDED_PARTICIPANT_LIST"
SCOPE = "WHOLE_PROTEIN"
PROVIDER_KIND = "SOURCE_DATABASE"
PROVIDER_NAME = "ComplexPortal"
EXCLUDED_PREDICTED_NAME = "9606_predicted.tsv"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = REPO_ROOT / "data" / "raw" / "complexportal"
DEFAULT_TRAITS_ROOT = REPO_ROOT / "data" / "traits"
DEFAULT_TRAITS_DIR = (
    REPO_ROOT / "data" / "traits" / "function" / "interaction_partner" / "complexportal"
)
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data" / "grounding" / "protein_registry.jsonl"
EXPECTED_UNIPROT_RELEASE = "2026_02"

MISSING_PROVIDER_RECEIPT = "MISSING_COMPLEXPORTAL_PROVIDER_ACQUISITION_RECEIPT"
MISSING_PROVIDER_FILE_LIST_RECEIPT = "MISSING_COMPLEXPORTAL_RELEASE_PINNED_FILE_LIST_RECEIPT"
MISSING_REGISTRY_RECEIPT = "MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT"
MISSING_PROTEIN_REFERENCE = "MISSING_EXPECTED_RELEASE_LOCAL_PROTEIN_REFERENCE"
GLOBAL_PROMOTION_BLOCKERS = (
    MISSING_PROVIDER_RECEIPT,
    MISSING_PROVIDER_FILE_LIST_RECEIPT,
    MISSING_REGISTRY_RECEIPT,
)

# These checksums pin the exact local bytes currently present in the repository
# workspace. They are deliberately not represented as a provider release or an
# acquisition receipt: all files came from ComplexPortal's mutable /current/
# endpoint through a fetch recipe that did not record response metadata.
EXPECTED_SOURCE_SHA256: Mapping[str, str] = {
    "10090.tsv": "ba66aed64325da4508f7c0c976831550c6aff015ab76eddb1ec9c96375027684",
    "10116.tsv": "a5f921480dbf016286fe1520d6824d5c3a044b9cfb0b777eb4f4b7bbbb5fb584",
    "1235996.tsv": "b73f73829a29c39344d29870903c9745ca2ec4d5d078876d054d280917a26a27",
    "1263720.tsv": "4d4816cbf80532b7bf40f4117a91d6a92289d39d94675b806805fc8f7945df4b",
    "208964.tsv": "389c8a7f9b0ff4473f10ef7e8370a7584e9f082895dea3fea9c5453d0b8be8d4",
    "243277.tsv": "4d0ee5410595748ff4c4d2d8b5626203c99f50af6b32e8aa377b2e1913d8faba",
    "2697049.tsv": "a24599a541a74e44d1f1755fea80f132af2d58db9eaa1cb5606e56689ff36bc2",
    "284812.tsv": "d19c49cd8b8cf4d5955bf11f71bb7869945847d5d8e779a7b04c50f8bbb61f15",
    "3702.tsv": "dec8674643367376b2b59998f2026db493be03532f40b1b73980b9065f3a31f2",
    "559292.tsv": "73a7bb2552dd2fe503bb0a43b7d86e80eab68ef833329c7b462569902527b922",
    "562.tsv": "084bf9cc673766bba9eff589aa27e78b80acf0a9dc11220f8f9c8ec2b8e316a8",
    "6239.tsv": "5f8c4b4c613f703e95e38c653561cb83868eda4570ed2f248fe26d5fed7341ee",
    "6523.tsv": "17d1cab6c5f6c7cf623b9523ab83514e61c532fe3d25b28d1a1897e56c0f43d3",
    "694009.tsv": "7666b2f39d6ace8d3363baa206c1e445648ff3c263479052d4ff46811e7cc8fe",
    "7227.tsv": "0095c4c98ce81571a8ded76229850c62009f2c7198b3a5a39d3db0b05a630f9b",
    "7787.tsv": "178cf790a992b167b151922f651a06a1b844690e1fb0f2245f3d2bbc9fe33f98",
    "7788.tsv": "d991c08a3dd04ec5bb2c3b9970c9a0308f3c203eb5500cd258bab5e1e07a9725",
    "7955.tsv": "cdd3e6296c408c8e9ff949e9ac5a76496da9dbc0d169eceb3e3443661baf9535",
    "83333.tsv": "46dd5690d8016ebb98d77a695de4f1842a6113ef401d6956791e128bdfffc8b1",
    "8355.tsv": "30cf45a156ea251d4f1c0c0b734f84708efcfde8fb662dfd34a52d7a20a05f7c",
    "8732.tsv": "2a4796711e61f9d9d8c64bac33954d59387b284fcb5710b25688120a4ee651db",
    "9031.tsv": "5d36081b2a2c038c9da76a74a3724ac299be6abee15b561869cdea89987840f7",
    "9606.tsv": "29d3aeec7ede35e8686de3cf73620b5871c3e68d7ca069385153a9b28e80012a",
    "9615.tsv": "437dff7e8af7f9a1a021ac62098a0d2c7a2fcbf9495022bfbe4bbbd5afb67463",
    "9823.tsv": "8fb04983d31be8aeca8db3efada75efa4954d0a770400254815d5f4adeef0771",
    "9913.tsv": "e39325d93b24d858398b4c0e03acfb408c0c9ce2b3f6eac8f0fe98941e6e19cd",
    "9940.tsv": "6868165c1c883f028e2988acd99192f9bece9cb29a257ace02fece263e076e15",
    "9986.tsv": "704545c4955a4a84a3b8ef0171d6db7bb5fc7014953472cd07655d73f5b2c413",
}
EXPECTED_CURATED_SOURCE_FILES = tuple(sorted(EXPECTED_SOURCE_SHA256))

# Exact ComplexTAB 19-column contract in the locally fetched artifacts.
COMPLEXTAB_HEADERS = (
    "#Complex ac",
    "Recommended name",
    "Aliases for complex",
    "Taxonomy identifier",
    "Identifiers (and stoichiometry) of molecules in complex",
    "Evidence Code",
    "Experimental evidence",
    "Go Annotations",
    "Cross references",
    "Description",
    "Complex properties",
    "Complex assembly",
    "Ligand",
    "Disease",
    "Agonist",
    "Antagonist",
    "Comment",
    "Source",
    "Expanded participant list",
)
PROJECTION_FIELDS = (
    "complex_accession",
    "recommended_name",
    "aliases_for_complex",
    "taxonomy_identifier",
    "molecule_identifiers_and_stoichiometry",
    "evidence_code",
    "experimental_evidence",
    "go_annotations",
    "cross_references",
    "description",
    "complex_properties",
    "complex_assembly",
    "ligand",
    "disease",
    "agonist",
    "antagonist",
    "comment",
    "source",
    "expanded_participant_list",
)
EXPECTED_HEADER = "\t".join(COMPLEXTAB_HEADERS)

TRAIT_CONTRACT = {
    "definition_source": "Complex Portal",
    "trait_axis": "FUNCTION",
    "trait_category": "FUNC_INTERACTION_PARTNER",
    "term_kind": "CLASS",
    "mapping_status": "SEEDED",
    "license": "CC0 (EBI Complex Portal)",
}

# Exact code-plus-label values in the curated ComplexPortal format. A known
# code paired with a different label is blocked rather than reduced to a CURIE.
EXACT_ECO_FIELDS = {
    "ECO:0000353": ("ECO:0000353(physical interaction evidence used in manual assertion)"),
    "ECO:0005543": (
        "ECO:0005543(biological system reconstruction evidence by experimental "
        "evidence from mixed species used in manual assertion)"
    ),
    "ECO:0005544": (
        "ECO:0005544(biological system reconstruction evidence based on orthology "
        "evidence used in manual assertion)"
    ),
    "ECO:0005546": (
        "ECO:0005546(biological system reconstruction evidence based on paralogy "
        "evidence used in manual assertion)"
    ),
    "ECO:0005547": (
        "ECO:0005547(biological system reconstruction evidence based on inference "
        "from background scientific knowledge used in manual assertion)"
    ),
    "ECO:0005610": (
        "ECO:0005610(biological system reconstruction evidence based on homology "
        "evidence used in manual assertion)"
    ),
}

_CURATED_FILENAME_RE = re.compile(r"^[1-9][0-9]*\.tsv$")
_TAXON_RE = re.compile(r"^[1-9][0-9]*$")
_COMPLEX_ACCESSION_RE = re.compile(r"^CPX-[1-9][0-9]*$")
_ECO_FIELD_RE = re.compile(r"^(ECO:[0-9]{7})\([^\r\n]*\)$")
_MEMBER_TOKEN_RE = re.compile(r"^(.+)\(([0-9]+)\)$")
_PROCESSED_CHAIN_MARKER_RE = re.compile(r"-PRO_[0-9]+$")
_CHEBI_RE = re.compile(r"^CHEBI:[1-9][0-9]*$")
_RNACENTRAL_RE = re.compile(r"^URS[0-9A-F]+_[1-9][0-9]*$")
_EBI_RE = re.compile(r"^EBI-[1-9][0-9]*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_UNIPROT_RELEASE_RE = re.compile(r"^[0-9]{4}_[0-9]{2}$")


class ComplexPortalStageError(ValueError):
    """The local sources cannot be staged without ambiguity or coercion."""


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
    path: Path
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class ParsedMember:
    exact_token: str
    accession: str
    stoichiometry: int | None
    stoichiometry_known: bool

    def projection(self) -> dict[str, Any]:
        return {
            "source_member_token": self.exact_token,
            "source_member_accession": self.accession,
            "source_member_stoichiometry": self.stoichiometry,
            "source_member_stoichiometry_known": self.stoichiometry_known,
        }


@dataclass(frozen=True)
class SourceArtifact:
    path: Path
    relative_path: str
    sha256: str
    size_bytes: int
    rows: tuple[tuple[int, tuple[str, ...], str], ...]


@dataclass(frozen=True)
class StageResult:
    candidates: tuple[dict[str, Any], ...]
    blocked_tokens: tuple[dict[str, Any], ...]
    protein_requests: tuple[dict[str, Any], ...]
    summary: dict[str, Any]


def canonical_json(value: Any) -> str:
    """Return the repository's stable, newline-free JSON representation."""

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
        raise ComplexPortalStageError(
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
        raise ComplexPortalStageError(
            f"{description} escapes bound root {lexical_root}: {lexical_path}"
        ) from error
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise ComplexPortalStageError(f"invalid relative {description} path: {relative}")
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
        raise ComplexPortalStageError(
            f"cannot bind {description} without following symlinks {lexical_path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ComplexPortalStageError(f"{description} must be a directory: {lexical_path}")
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
        raise ComplexPortalStageError(
            f"cannot bind {description} without following symlinks {path}: {error}"
        ) from error
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise ComplexPortalStageError(f"{description} must be a directory: {path}")
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
            raise ComplexPortalStageError(
                f"{description} binding changed while staging: {binding.path}"
            )
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
        raise ComplexPortalStageError(f"invalid relative {description} path: {relative_path}")
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
            raise ComplexPortalStageError(f"{description} must be a regular file: {display_path}")
        chunks: list[bytes] = []
        while chunk := os.read(file_descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise ComplexPortalStageError(f"{description} changed while reading: {display_path}")
        return b"".join(chunks)
    except ComplexPortalStageError:
        raise
    except OSError as error:
        raise ComplexPortalStageError(
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
        raise ComplexPortalStageError(
            f"invalid pinned sha256 for {description}: {expected_sha256!r}"
        )
    relative = _relative_under(path, bound_root.path, description=description)
    raw = _read_relative_bytes(
        bound_root,
        relative,
        display_path=_lexical_absolute(path),
        description=description,
    )
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ComplexPortalStageError(
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
        raise ComplexPortalStageError(
            f"{description} drifted while staging: {artifact.path}; "
            f"expected {artifact.sha256}, observed {observed}"
        )


def canonical_source_projection(columns: Sequence[str]) -> dict[str, str]:
    """Project one exact 19-column row into stable, named source fields."""

    if len(columns) != len(PROJECTION_FIELDS):
        raise ComplexPortalStageError(
            f"ComplexTAB row has {len(columns)} columns; expected {len(PROJECTION_FIELDS)}"
        )
    return dict(zip(PROJECTION_FIELDS, columns, strict=True))


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
            raise ComplexPortalStageError("trait YAML has an unhashable mapping key") from error
        if duplicate:
            raise ComplexPortalStageError(f"trait YAML has duplicate key {key!r}")
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
            raise ComplexPortalStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for key, item in value.items():
            if not isinstance(key, str):
                raise ComplexPortalStageError(f"{source}: YAML mapping key is not a string")
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise ComplexPortalStageError(f"{source}: YAML aliases form a cycle")
        active.add(identity)
        for item in value:
            _require_json_shape(item, source=source, active=active)
        active.remove(identity)
        return
    if value is None or type(value) in {str, int, bool}:
        return
    if type(value) is float and math.isfinite(value):
        return
    raise ComplexPortalStageError(f"{source}: YAML value is outside the JSON data model")


def _load_yaml_mapping(raw: bytes, *, path: Path) -> Mapping[str, Any]:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError, ComplexPortalStageError) as error:
        raise ComplexPortalStageError(f"cannot parse trait record {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise ComplexPortalStageError(f"trait record is not a mapping: {path}")
    _require_json_shape(value, source=str(path))
    return value


def _reject_tree_symlinks(root: Path, *, description: str) -> None:
    def fail(error: OSError) -> None:
        raise ComplexPortalStageError(f"cannot scan {description} {root}: {error}")

    for directory, names, files in os.walk(root, topdown=True, onerror=fail, followlinks=False):
        for name in [*names, *files]:
            path = Path(directory) / name
            try:
                metadata = os.stat(path, follow_symlinks=False)
            except OSError as error:
                raise ComplexPortalStageError(
                    f"cannot inspect {description} entry {path}: {error}"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                raise ComplexPortalStageError(f"symlink below {description} is forbidden: {path}")


def _exact_route_paths(route_binding: BoundDirectory) -> tuple[Path, ...]:
    try:
        names = os.listdir(route_binding.descriptor)
    except OSError as error:
        raise ComplexPortalStageError(
            f"cannot inventory ComplexPortal trait route: {error}"
        ) from error
    paths: list[Path] = []
    for name in sorted(names):
        try:
            metadata = os.stat(name, dir_fd=route_binding.descriptor, follow_symlinks=False)
        except OSError as error:
            raise ComplexPortalStageError(
                f"cannot inspect ComplexPortal trait route entry {name}: {error}"
            ) from error
        if stat.S_ISLNK(metadata.st_mode):
            raise ComplexPortalStageError(
                f"symlink in ComplexPortal trait route is forbidden: {name}"
            )
        if not stat.S_ISREG(metadata.st_mode) or Path(name).suffix != ".yaml":
            raise ComplexPortalStageError(
                "ComplexPortal trait route must contain only flat regular lowercase .yaml "
                f"records; observed {name!r}"
            )
        paths.append(route_binding.path / name)
    if not paths:
        raise ComplexPortalStageError("ComplexPortal trait route is empty")
    return tuple(paths)


def _candidate_trait_paths(traits_root: Path, route_paths: Sequence[Path]) -> tuple[Path, ...]:
    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits_root), "ComplexPortal trait")
        return tuple(sorted(found))
    command = [
        executable,
        "--no-config",
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
        "complexportal",
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
        raise ComplexPortalStageError(
            f"cannot run ripgrep ComplexPortal trait prefilter: {error}"
        ) from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise ComplexPortalStageError(f"ripgrep ComplexPortal trait prefilter failed: {detail}")
    try:
        paths = {Path(raw.decode("utf-8")) for raw in scan.stdout.split(b"\0") if raw}
    except UnicodeDecodeError as error:
        raise ComplexPortalStageError(f"ripgrep returned a non-UTF-8 path: {error}") from error
    paths.update(route_paths)
    return tuple(sorted(_lexical_absolute(path) for path in paths))


def index_complexportal_traits(
    traits_binding: BoundDirectory,
    route_binding: BoundDirectory,
    *,
    repo_root: Path,
    repo_binding: BoundDirectory,
) -> tuple[dict[str, TraitBinding], tuple[ArtifactDigest, ...], tuple[Path, ...]]:
    """Exhaustively bind exact ComplexPortal records and reject semantic shadows."""

    _assert_directory_binding(traits_binding, description="trait root")
    _assert_directory_binding(route_binding, description="ComplexPortal trait route")
    _reject_tree_symlinks(traits_binding.path, description="trait tree")
    route_paths = _exact_route_paths(route_binding)
    initial_paths = _candidate_trait_paths(traits_binding.path, route_paths)
    try:
        bindings: dict[str, TraitBinding] = {}
        artifacts: list[ArtifactDigest] = []
        exact_route = route_binding.path
        for path in initial_paths:
            artifact = _capture(
                path,
                description="ComplexPortal trait candidate",
                repo_root=repo_root,
                expected_sha256=None,
                bound_root=repo_binding,
            )
            artifacts.append(ArtifactDigest(artifact.path, artifact.relative_path, artifact.sha256))
            record = _load_yaml_mapping(artifact.raw, path=path)
            identifier = record.get("identifier")
            try:
                route_relative = path.relative_to(exact_route)
                in_route = bool(route_relative.parts)
            except ValueError:
                in_route = False
            relevant = isinstance(identifier, str) and identifier.lower().startswith(
                "complexportal:"
            )
            if in_route and not relevant:
                raise ComplexPortalStageError(
                    f"{path}: expected an exact ComplexPortal trait identifier in source route"
                )
            if not relevant:
                continue
            if path.parent != exact_route or path.suffix != ".yaml":
                raise ComplexPortalStageError(
                    f"{path}: ComplexPortal semantic shadow outside exact lowercase .yaml route"
                )
            accession = str(identifier).removeprefix("ComplexPortal:")
            if (
                not str(identifier).startswith("ComplexPortal:")
                or _COMPLEX_ACCESSION_RE.fullmatch(accession) is None
            ):
                raise ComplexPortalStageError(
                    f"{path}: invalid exact ComplexPortal identifier {identifier!r}"
                )
            for field, expected in TRAIT_CONTRACT.items():
                if record.get(field) != expected:
                    raise ComplexPortalStageError(
                        f"{path}: trait contract mismatch for {field}: "
                        f"expected {expected!r}, observed {record.get(field)!r}"
                    )
            if accession in bindings:
                raise ComplexPortalStageError(
                    f"duplicate ComplexPortal trait identifier {accession}: "
                    f"{bindings[accession].path} and {path}"
                )
            bindings[accession] = TraitBinding(
                path=artifact.path,
                relative_path=artifact.relative_path,
                sha256=artifact.sha256,
            )
        if not bindings:
            raise ComplexPortalStageError(
                f"no ComplexPortal trait records found beneath {route_binding.path}"
            )
        _assert_directory_binding(traits_binding, description="trait root")
        _assert_directory_binding(route_binding, description="ComplexPortal trait route")
        _reject_tree_symlinks(traits_binding.path, description="trait tree")
        final_route_paths = _exact_route_paths(route_binding)
        if final_route_paths != route_paths:
            raise ComplexPortalStageError(
                "ComplexPortal exact trait route inventory drifted while indexing"
            )
        final_paths = _candidate_trait_paths(traits_binding.path, final_route_paths)
        if final_paths != initial_paths:
            raise ComplexPortalStageError(
                "ComplexPortal trait candidate membership drifted while indexing"
            )
        _assert_directory_binding(route_binding, description="ComplexPortal trait route")
        _assert_directory_binding(traits_binding, description="trait root")
        return bindings, tuple(artifacts), initial_paths
    except Exception:
        raise


def discover_curated_sources(
    raw_binding: BoundDirectory,
    *,
    expected_source_files: Sequence[str],
) -> tuple[list[Path], list[str]]:
    """Bind one exact directory inventory and categorically exclude predicted data."""

    expected = tuple(sorted(expected_source_files))
    if (
        not expected
        or len(set(expected)) != len(expected)
        or any(_CURATED_FILENAME_RE.fullmatch(name) is None for name in expected)
    ):
        raise ComplexPortalStageError("expected curated source inventory is invalid")
    observed: list[str] = []
    try:
        names = os.listdir(raw_binding.descriptor)
    except OSError as error:
        raise ComplexPortalStageError(f"cannot inventory ComplexPortal raw directory: {error}")
    for name in sorted(names):
        try:
            metadata = os.stat(name, dir_fd=raw_binding.descriptor, follow_symlinks=False)
        except OSError as error:
            raise ComplexPortalStageError(
                f"cannot inspect raw source entry {name}: {error}"
            ) from error
        if stat.S_ISLNK(metadata.st_mode):
            raise ComplexPortalStageError(
                f"symlink in ComplexPortal raw directory is forbidden: {name}"
            )
        if not stat.S_ISREG(metadata.st_mode):
            raise ComplexPortalStageError(
                f"ComplexPortal raw directory contains a non-regular entry: {name}"
            )
        observed.append(name)
    required_inventory = sorted([*expected, EXCLUDED_PREDICTED_NAME])
    if observed != required_inventory:
        missing = sorted(set(required_inventory) - set(observed))
        unexpected = sorted(set(observed) - set(required_inventory))
        raise ComplexPortalStageError(
            f"ComplexPortal raw inventory differs from exact local snapshot; "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    return [raw_binding.path / name for name in expected], [EXCLUDED_PREDICTED_NAME]


def _read_source_artifact(artifact: CapturedArtifact) -> SourceArtifact:
    """Parse the same immutable byte capture that was pinned and hashed."""

    raw = artifact.raw
    if not raw or not raw.endswith(b"\n") or b"\r" in raw:
        raise ComplexPortalStageError(
            f"{artifact.path}: ComplexTAB source must be non-empty canonical LF text "
            "with one terminal newline"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ComplexPortalStageError(
            f"cannot decode UTF-8 ComplexTAB source {artifact.path}: {error}"
        ) from error
    lines = text[:-1].split("\n")
    if not lines or lines[0] != EXPECTED_HEADER:
        raise ComplexPortalStageError(
            f"{artifact.path}: exact 19-column ComplexTAB header mismatch"
        )
    rows: list[tuple[int, tuple[str, ...], str]] = []
    for line_number, line in enumerate(lines[1:], 2):
        if not line:
            raise ComplexPortalStageError(
                f"{artifact.path}:{line_number}: blank ComplexTAB row is forbidden"
            )
        columns = tuple(line.split("\t"))
        if len(columns) != len(PROJECTION_FIELDS):
            raise ComplexPortalStageError(
                f"{artifact.path}:{line_number}: expected 19 tab-separated columns, "
                f"got {len(columns)}"
            )
        rows.append((line_number, columns, hashlib.sha256(line.encode("utf-8")).hexdigest()))
    return SourceArtifact(
        path=artifact.path,
        relative_path=artifact.relative_path,
        sha256=artifact.sha256,
        size_bytes=len(raw),
        rows=tuple(rows),
    )


def _strict_json_value(raw: bytes | str, *, source: str) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ComplexPortalStageError(f"{source}: duplicate key {key!r} in JSON object")
            result[key] = value
        return result

    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return json.loads(
            text,
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ComplexPortalStageError(f"{source}: non-finite JSON number {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ComplexPortalStageError) as error:
        raise ComplexPortalStageError(f"{source}: invalid JSON: {error}") from error


def parse_protein_registry(
    artifact: CapturedArtifact, *, expected_release: str
) -> dict[str, dict[str, Any]]:
    if _UNIPROT_RELEASE_RE.fullmatch(expected_release) is None:
        raise ComplexPortalStageError(f"invalid expected UniProt release: {expected_release!r}")
    try:
        text = artifact.raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ComplexPortalStageError(f"{artifact.relative_path}: registry is not UTF-8") from error
    if artifact.raw and (not artifact.raw.endswith(b"\n") or b"\r" in artifact.raw):
        raise ComplexPortalStageError(
            f"{artifact.relative_path}: registry must be canonical LF JSONL"
        )
    registry: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            raise ComplexPortalStageError(
                f"{artifact.relative_path}:{line_number}: blank registry line"
            )
        value = _strict_json_value(line, source=f"{artifact.relative_path}:{line_number}")
        if not isinstance(value, dict):
            raise ComplexPortalStageError(
                f"{artifact.relative_path}:{line_number}: registry line is not an object"
            )
        findings = grounding.validate_protein_reference(value, path=artifact.path, line=line_number)
        if findings:
            detail = "; ".join(f"{item.code}: {item.message}" for item in findings)
            raise ComplexPortalStageError(
                f"{artifact.relative_path}:{line_number}: invalid ProteinReference: {detail}"
            )
        if canonical_json(value) != line:
            raise ComplexPortalStageError(
                f"{artifact.relative_path}:{line_number}: ProteinReference is not canonical JSON"
            )
        if value.get("uniprot_release") != expected_release:
            raise ComplexPortalStageError(
                f"{artifact.relative_path}:{line_number}: ProteinReference release does not "
                f"equal {expected_release}"
            )
        protein_id = str(value["protein_id"])
        if protein_id in registry:
            raise ComplexPortalStageError(
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


def _source_snapshot(artifacts: Sequence[SourceArtifact]) -> dict[str, Any]:
    source_artifacts = [
        {
            "role": "COMPLEXPORTAL_CURATED_COMPLEXTAB_FROM_MUTABLE_CURRENT_ENDPOINT",
            "path": artifact.relative_path,
            "sha256": artifact.sha256,
            "size_bytes": artifact.size_bytes,
        }
        for artifact in artifacts
    ]
    snapshot: dict[str, Any] = {
        "kind": "COMPLEXPORTAL_LOCAL_SOURCE_SNAPSHOT",
        "schema_version": SCHEMA_VERSION,
        "source_artifacts": source_artifacts,
        "source_artifact_count": len(source_artifacts),
        "excluded_predicted_source_file": EXCLUDED_PREDICTED_NAME,
        "repository_declared_source_url_base": (
            "https://ftp.ebi.ac.uk/pub/databases/intact/complex/current/complextab"
        ),
        "endpoint_release_selector": "current",
        "provider_global_release": None,
        "provider_acquisition_receipt": None,
        "provider_file_list_receipt": None,
        "acquisition_status": "LOCAL_PINNED_BYTES_WITHOUT_PROVIDER_FETCH_RECEIPT",
    }
    snapshot["source_snapshot_id"] = "complexportal-source-snapshot:" + value_sha256(snapshot)
    return snapshot


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


def _parse_member_list(
    value: str,
    *,
    source: Path,
    line_number: int,
    field_name: str,
) -> tuple[ParsedMember, ...]:
    if not value:
        raise ComplexPortalStageError(
            f"{source}:{line_number}: ComplexPortal {field_name} has no participants"
        )
    parsed: list[ParsedMember] = []
    seen_accessions: set[str] = set()
    for exact_token in value.split("|"):
        token_match = _MEMBER_TOKEN_RE.fullmatch(exact_token)
        if token_match is None:
            raise ComplexPortalStageError(
                f"{source}:{line_number}: malformed {field_name} token {exact_token!r}"
            )
        accession, stoichiometry_text = token_match.groups()
        if accession in seen_accessions:
            raise ComplexPortalStageError(
                f"{source}:{line_number}: duplicate {field_name} accession {accession!r}"
            )
        seen_accessions.add(accession)
        source_stoichiometry = int(stoichiometry_text)
        known = source_stoichiometry != 0
        parsed.append(
            ParsedMember(
                exact_token=exact_token,
                accession=accession,
                stoichiometry=source_stoichiometry if known else None,
                stoichiometry_known=known,
            )
        )
    return tuple(parsed)


def _member_class(accession: str) -> str:
    """Classify an expanded source token without rewriting its identifier."""

    if _PROCESSED_CHAIN_MARKER_RE.search(accession):
        return "BLOCKED_PROCESSED_CHAIN"
    if (
        accession.startswith("[")
        or accession.endswith("]")
        or any(marker in accession for marker in (",", ";", "/"))
    ):
        return "BLOCKED_COMPOSITE_TOKEN"
    if grounding.UNIPROT_RE.fullmatch(f"UniProtKB:{accession}") is not None:
        return "ACCEPTED_UNIPROT"
    if _COMPLEX_ACCESSION_RE.fullmatch(accession):
        return "BLOCKED_UNEXPANDED_SUBCOMPLEX"
    if _CHEBI_RE.fullmatch(accession):
        return "BLOCKED_CHEMICAL"
    if _RNACENTRAL_RE.fullmatch(accession):
        return "BLOCKED_RNA"
    if _EBI_RE.fullmatch(accession):
        return "BLOCKED_INTERNAL_INTERACTOR"
    return "BLOCKED_INVALID_OR_UNSUPPORTED_ACCESSION"


def _eco_validation(value: str) -> tuple[str | None, str | None]:
    match = _ECO_FIELD_RE.fullmatch(value)
    if match is None:
        return None, "INVALID_EXACT_ECO_FIELD_SYNTAX"
    code = match.group(1)
    expected = EXACT_ECO_FIELDS.get(code)
    if expected is None:
        return code, "UNADMITTED_EXACT_ECO_CODE"
    if value != expected:
        return code, "EXACT_ECO_CODE_LABEL_MISMATCH"
    return code, None


def _expected_trait_artifact(
    projection: Mapping[str, str], *, traits_dir: Path
) -> tuple[Path, bytes]:
    """Replay the historical seeder's exact path and bytes for one curated row."""

    accession = projection["complex_accession"].strip()
    name = projection["recommended_name"].strip()
    taxonomy = projection["taxonomy_identifier"].strip()
    taxon_match = re.search(r"\(([^)]+)\)", taxonomy)
    taxon_name = taxon_match.group(1) if taxon_match is not None else ""
    members: list[str] = []
    subparts: list[str] = []
    for token in projection["molecule_identifiers_and_stoichiometry"].split("|"):
        member_accession = token.split("(")[0].strip()
        curie = complexportal_seeder.member_curie(member_accession)
        if curie is None:
            continue
        (subparts if curie.startswith("ComplexPortal:") else members).append(curie)
    go_terms = complexportal_seeder.parse_go(projection["go_annotations"])
    expected_text = complexportal_seeder.build_yaml(
        accession,
        name,
        taxon_name,
        members,
        subparts,
        go_terms,
        projection["description"],
    )
    expected_path = traits_dir / (
        f"{complexportal_seeder.slug(name or accession)}-{accession.lower()}.yaml"
    )
    return _lexical_absolute(expected_path), expected_text.encode("utf-8")


def _source_binding(
    *,
    complex_accession: str,
    projection: Mapping[str, str],
    source_row_sha256: str,
    source_raw_line_sha256: str,
    artifact: SourceArtifact,
    source_line_number: int,
    trait: TraitBinding,
    source_snapshot_id: str,
) -> dict[str, Any]:
    return {
        "trait_id": f"ComplexPortal:{complex_accession}",
        "source_trait_id": f"ComplexPortal:{complex_accession}",
        "record_path": trait.relative_path,
        "record_sha256": trait.sha256,
        "evidence_source": PROVIDER_NAME,
        "provider_kind": PROVIDER_KIND,
        "provider_name": PROVIDER_NAME,
        "source_snapshot_id": source_snapshot_id,
        # provider_source names the exact replayable artifact, not a database label.
        "provider_source": artifact.relative_path,
        "provider_entry_sha256": source_raw_line_sha256,
        "source_artifact_path": artifact.relative_path,
        "source_artifact_sha256": artifact.sha256,
        "source_line_number": source_line_number,
        "source_row_projection": dict(projection),
        "source_row_sha256": source_row_sha256,
        "source_raw_line_sha256": source_raw_line_sha256,
        "source_raw_line_sha256_basis": (
            "RAW_UTF8_PHYSICAL_LINE_EXCLUDING_CANONICAL_LF_TERMINATOR"
        ),
    }


def _member_provenance(
    member: ParsedMember, direct_members: Sequence[ParsedMember]
) -> dict[str, Any]:
    direct_matches = [
        item.projection() for item in direct_members if item.accession == member.accession
    ]
    return {
        "membership_basis": MEMBERSHIP_BASIS,
        "expanded_member": member.projection(),
        "present_in_direct_participant_list": bool(direct_matches),
        "matching_direct_participants": direct_matches,
    }


def _content_address(
    row: dict[str, Any], *, id_field: str, id_prefix: str, row_hash_field: str
) -> dict[str, Any]:
    row[id_field] = id_prefix + value_sha256(row)
    row[row_hash_field] = value_sha256(row)
    return row


def _candidate(
    *,
    member: ParsedMember,
    direct_members: Sequence[ParsedMember],
    eco_code: str,
    source_binding: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
    registry_sha256: str,
) -> dict[str, Any]:
    blockers = list(GLOBAL_PROMOTION_BLOCKERS)
    if reference is None:
        blockers.append(MISSING_PROTEIN_REFERENCE)
    source_taxon_id = f"NCBITaxon:{source_binding['source_row_projection']['taxonomy_identifier']}"
    taxon_comparison = {
        "source_complex_taxon_id": source_taxon_id,
        "protein_reference_taxon_id": (reference["taxon_id"] if reference is not None else None),
        "status": (
            "NO_LOCAL_PROTEIN_REFERENCE"
            if reference is None
            else (
                "IDENTICAL"
                if reference["taxon_id"] == source_taxon_id
                else "DIFFERENT_HOST_OR_COMPONENT_TAXON"
            )
        ),
        "acceptance_semantics": (
            "INFORMATIONAL_ONLY_COMPLEX_TAXON_IS_NOT_A_COMPONENT_PROTEIN_TAXON_ASSERTION"
        ),
    }
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": CANDIDATE_KIND,
        "candidate_status": QUALIFICATION_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "staging_reason": STAGING_REASON,
        "missing_receipts": list(GLOBAL_PROMOTION_BLOCKERS),
        "promotion_blockers": sorted(set(blockers)),
        **source_binding,
        "protein_id": f"UniProtKB:{member.accession}",
        "protein_reference_binding": _reference_projection(
            reference, registry_sha256=registry_sha256
        ),
        "source_complex_to_protein_taxon_comparison": taxon_comparison,
        "grounding_status": (
            "LOCAL_PROTEIN_REFERENCE_PRESENT_STAGING_ONLY_MISSING_RECEIPTS"
            if reference is not None
            else "MISSING_LOCAL_PROTEIN_REFERENCE_STAGING_ONLY"
        ),
        "scope": SCOPE,
        "mapping_method": MAPPING_METHOD,
        "eco_code": eco_code,
        "source_member_provenance": _member_provenance(member, direct_members),
        "grounding_evidence_emitted": False,
        "network_action_performed": False,
        "write_action_performed": False,
        **member.projection(),
    }
    return _content_address(
        row,
        id_field="candidate_id",
        id_prefix="complexportal-grounding-candidate:",
        row_hash_field="candidate_row_sha256",
    )


def _blocked_token(
    *,
    member: ParsedMember,
    direct_members: Sequence[ParsedMember],
    blocking_reasons: Sequence[str],
    eco_code: str | None,
    source_binding: Mapping[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": BLOCKED_TOKEN_KIND,
        "candidate_status": "BLOCKED",
        "qualification_status": "BLOCKED",
        "staging_reason": STAGING_REASON,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "missing_receipts": list(GLOBAL_PROMOTION_BLOCKERS),
        "promotion_blockers": sorted(set([*GLOBAL_PROMOTION_BLOCKERS, *blocking_reasons])),
        **source_binding,
        "scope": SCOPE,
        "mapping_method": MAPPING_METHOD,
        "eco_code": eco_code,
        "source_member_class": _member_class(member.accession),
        "source_member_provenance": _member_provenance(member, direct_members),
        "grounding_evidence_emitted": False,
        "network_action_performed": False,
        "write_action_performed": False,
        **member.projection(),
    }
    return _content_address(
        row,
        id_field="blocked_token_id",
        id_prefix="complexportal-grounding-blocked-token:",
        row_hash_field="blocked_token_row_sha256",
    )


def _build_requests(
    candidates: Sequence[Mapping[str, Any]],
    *,
    source_snapshot_id: str,
    expected_uniprot_release: str,
) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if candidate["protein_reference_binding"]["status"] == "MISSING_EXACT_PROTEIN_REFERENCE":
            grouped[str(candidate["protein_id"])].append(candidate)
    requests: list[dict[str, Any]] = []
    for protein_id, memberships in sorted(grouped.items()):
        accession = protein_id.split(":", 1)[1]
        row: dict[str, Any] = {
            "kind": REQUEST_KIND,
            "schema_version": SCHEMA_VERSION,
            "protein_id": protein_id,
            "primary_accession_is_authoritative": True,
            "coordinate_frame": ("UNIPROT_ISOFORM" if "-" in accession else "UNIPROT_CANONICAL"),
            "source_snapshot_id": source_snapshot_id,
            "expected_uniprot_release": expected_uniprot_release,
            "complexportal_trait_ids": sorted({str(item["trait_id"]) for item in memberships}),
            "trait_count": len({str(item["trait_id"]) for item in memberships}),
            "source_membership_count": len(memberships),
            "source_candidate_ids": sorted(str(item["candidate_id"]) for item in memberships),
            "source_taxon_ids": sorted(
                {
                    f"NCBITaxon:{item['source_row_projection']['taxonomy_identifier']}"
                    for item in memberships
                }
            ),
            "source_artifact_paths": sorted(
                {str(item["source_artifact_path"]) for item in memberships}
            ),
            "request_reason": MISSING_PROTEIN_REFERENCE,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        requests.append(
            _content_address(
                row,
                id_field="request_id",
                id_prefix="complexportal-protein-request:",
                row_hash_field="request_row_sha256",
            )
        )
    return tuple(requests)


def build_stage(
    *,
    raw_dir: Path = DEFAULT_RAW_DIR,
    traits_root: Path = DEFAULT_TRAITS_ROOT,
    traits_dir: Path = DEFAULT_TRAITS_DIR,
    protein_registry_path: Path = DEFAULT_PROTEIN_REGISTRY,
    repo_root: Path = REPO_ROOT,
    expected_source_files: Sequence[str] = EXPECTED_CURATED_SOURCE_FILES,
    expected_source_sha256: Mapping[str, str] | None = EXPECTED_SOURCE_SHA256,
    expected_uniprot_release: str = EXPECTED_UNIPROT_RELEASE,
) -> StageResult:
    """Build one deterministic, candidate-only image from all bound local inputs."""

    repo_binding = _bind_absolute_directory(repo_root, description="repository root")
    raw_binding: BoundDirectory | None = None
    traits_binding: BoundDirectory | None = None
    route_binding: BoundDirectory | None = None
    try:
        raw_binding = _bind_subdirectory(
            repo_binding, raw_dir, description="ComplexPortal raw source directory"
        )
        source_paths, excluded = discover_curated_sources(
            raw_binding, expected_source_files=expected_source_files
        )
        if expected_source_sha256 is not None and set(expected_source_sha256) != set(
            expected_source_files
        ):
            raise ComplexPortalStageError(
                "pinned ComplexPortal source checksum keys differ from exact file inventory"
            )
        captured_sources = tuple(
            _capture(
                path,
                description="ComplexTAB source artifact",
                repo_root=repo_root,
                expected_sha256=(
                    expected_source_sha256[path.name]
                    if expected_source_sha256 is not None
                    else None
                ),
                bound_root=repo_binding,
            )
            for path in source_paths
        )
        artifacts = tuple(_read_source_artifact(item) for item in captured_sources)
        source_snapshot = _source_snapshot(artifacts)
        source_snapshot_id = str(source_snapshot["source_snapshot_id"])

        registry_artifact = _capture(
            protein_registry_path,
            description="ProteinReference registry",
            repo_root=repo_root,
            expected_sha256=None,
            bound_root=repo_binding,
        )
        registry = parse_protein_registry(
            registry_artifact, expected_release=expected_uniprot_release
        )
        traits_binding = _bind_subdirectory(repo_binding, traits_root, description="trait root")
        route_binding = _bind_subdirectory(
            traits_binding, traits_dir, description="ComplexPortal trait route"
        )
        traits, trait_artifacts, trait_candidate_paths = index_complexportal_traits(
            traits_binding,
            route_binding,
            repo_root=repo_root,
            repo_binding=repo_binding,
        )

        candidates: list[dict[str, Any]] = []
        blocked_tokens: list[dict[str, Any]] = []
        expanded_member_classes: Counter[str] = Counter()
        direct_member_classes: Counter[str] = Counter()
        source_complexes: set[str] = set()
        candidate_complexes: set[str] = set()
        blocked_complexes: set[str] = set()
        accepted_pairs: set[tuple[str, str]] = set()
        direct_member_count = 0
        expanded_member_count = 0

        for artifact in artifacts:
            expected_taxon = artifact.path.stem
            for line_number, columns, raw_line_sha256 in artifact.rows:
                projection = canonical_source_projection(columns)
                complex_accession = projection["complex_accession"]
                if _COMPLEX_ACCESSION_RE.fullmatch(complex_accession) is None:
                    raise ComplexPortalStageError(
                        f"{artifact.path}:{line_number}: invalid ComplexPortal accession "
                        f"{complex_accession!r}"
                    )
                taxonomy = projection["taxonomy_identifier"]
                if _TAXON_RE.fullmatch(taxonomy) is None or taxonomy != expected_taxon:
                    raise ComplexPortalStageError(
                        f"{artifact.path}:{line_number}: taxonomy {taxonomy!r} does not exactly "
                        f"match curated filename taxon {expected_taxon!r}"
                    )
                if complex_accession in source_complexes:
                    raise ComplexPortalStageError(
                        f"duplicate curated ComplexPortal row for {complex_accession}"
                    )
                source_complexes.add(complex_accession)
                trait = traits.get(complex_accession)
                if trait is None:
                    raise ComplexPortalStageError(
                        f"{artifact.path}:{line_number}: no exact trait record for "
                        f"{complex_accession}"
                    )
                expected_trait_path, expected_trait_bytes = _expected_trait_artifact(
                    projection, traits_dir=route_binding.path
                )
                expected_trait_sha256 = hashlib.sha256(expected_trait_bytes).hexdigest()
                if trait.path != expected_trait_path:
                    raise ComplexPortalStageError(
                        f"{artifact.path}:{line_number}: trait route mismatch for "
                        f"{complex_accession}; expected {expected_trait_path}, observed "
                        f"{trait.path}"
                    )
                if trait.sha256 != expected_trait_sha256:
                    raise ComplexPortalStageError(
                        f"{trait.path}: full trait bytes differ from exact historical seeder "
                        f"projection for {complex_accession}"
                    )

                direct_members = _parse_member_list(
                    projection["molecule_identifiers_and_stoichiometry"],
                    source=artifact.path,
                    line_number=line_number,
                    field_name="direct participant list",
                )
                expanded_members = _parse_member_list(
                    projection["expanded_participant_list"],
                    source=artifact.path,
                    line_number=line_number,
                    field_name="expanded participant list",
                )
                direct_member_count += len(direct_members)
                expanded_member_count += len(expanded_members)
                direct_member_classes.update(
                    _member_class(item.accession) for item in direct_members
                )

                eco_code, eco_error = _eco_validation(projection["evidence_code"])
                source_row_sha = value_sha256(projection)
                binding = _source_binding(
                    complex_accession=complex_accession,
                    projection=projection,
                    source_row_sha256=source_row_sha,
                    source_raw_line_sha256=raw_line_sha256,
                    artifact=artifact,
                    source_line_number=line_number,
                    trait=trait,
                    source_snapshot_id=source_snapshot_id,
                )
                for member in expanded_members:
                    member_class = _member_class(member.accession)
                    expanded_member_classes[member_class] += 1
                    blocking_reasons: list[str] = []
                    if member_class != "ACCEPTED_UNIPROT":
                        blocking_reasons.append(member_class)
                    if eco_error is not None:
                        blocking_reasons.append(eco_error)
                    if blocking_reasons:
                        blocked_complexes.add(complex_accession)
                        blocked_tokens.append(
                            _blocked_token(
                                member=member,
                                direct_members=direct_members,
                                blocking_reasons=blocking_reasons,
                                eco_code=eco_code,
                                source_binding=binding,
                            )
                        )
                        continue

                    pair = (complex_accession, member.accession)
                    if pair in accepted_pairs:
                        raise ComplexPortalStageError(
                            f"duplicate ComplexPortal/UniProt expanded membership {pair!r}"
                        )
                    accepted_pairs.add(pair)
                    candidate_complexes.add(complex_accession)
                    protein_id = f"UniProtKB:{member.accession}"
                    candidates.append(
                        _candidate(
                            member=member,
                            direct_members=direct_members,
                            eco_code=str(eco_code),
                            source_binding=binding,
                            reference=registry.get(protein_id),
                            registry_sha256=registry_artifact.sha256,
                        )
                    )

        candidates.sort(
            key=lambda row: (
                row["trait_id"],
                row["protein_id"],
                row["provider_source"],
                row["source_member_token"],
            )
        )
        blocked_tokens.sort(
            key=lambda row: (
                row["trait_id"],
                row["provider_source"],
                row["source_member_token"],
                row["blocked_token_id"],
            )
        )
        requests = _build_requests(
            candidates,
            source_snapshot_id=source_snapshot_id,
            expected_uniprot_release=expected_uniprot_release,
        )
        uncovered_complexes = sorted(source_complexes - candidate_complexes)
        grounding_status_counts = Counter(row["grounding_status"] for row in candidates)
        registered_candidates = [
            row
            for row in candidates
            if row["protein_reference_binding"]["status"] == "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT"
        ]
        trait_binding_rows = [
            {
                "trait_id": f"ComplexPortal:{accession}",
                "trait_record_path": binding.relative_path,
                "trait_record_sha256": binding.sha256,
            }
            for accession, binding in sorted(traits.items())
        ]
        source_bound_trait_rows = [
            row
            for row in trait_binding_rows
            if row["trait_id"].split(":", 1)[1] in source_complexes
        ]
        taxon_comparison_counts = Counter(
            row["source_complex_to_protein_taxon_comparison"]["status"] for row in candidates
        )
        summary: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "kind": SUMMARY_KIND,
            "stage_status": STAGING_REASON,
            "qualification_claimed": False,
            "candidate_qualification_status": QUALIFICATION_STATUS,
            "missing_receipts": list(GLOBAL_PROMOTION_BLOCKERS),
            "promotion_blockers": [
                *GLOBAL_PROMOTION_BLOCKERS,
                "COMPLEXPORTAL_SOURCE_USES_MUTABLE_CURRENT_ENDPOINT",
                "COMPLEXPORTAL_PROVIDER_RELEASE_AND_EXPORT_COMPLETENESS_NOT_ESTABLISHED",
                "REVIEW_REQUIRED_BEFORE_TRAIT_OR_GROUNDING_WRITE",
            ],
            "provider_name": PROVIDER_NAME,
            "source_policy": "CURATED_COMPLEXTAB_EXPANDED_PARTICIPANTS_ONLY",
            "membership_basis": MEMBERSHIP_BASIS,
            "source_snapshot": source_snapshot,
            "source_snapshot_id": source_snapshot_id,
            "source_artifacts": source_snapshot["source_artifacts"],
            "excluded_source_files": excluded,
            "source_file_count": len(artifacts),
            "protein_registry_artifact": _artifact_projection(
                registry_artifact,
                role="LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING",
            ),
            "expected_uniprot_release": expected_uniprot_release,
            "protein_registry_fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
            "protein_registry_row_count": len(registry),
            "source_complex_count": len(source_complexes),
            "covered_source_complex_count": len(candidate_complexes),
            "uncovered_source_complex_count": len(uncovered_complexes),
            "uncovered_source_complex_ids": uncovered_complexes,
            "complexes_with_blocked_tokens_count": len(blocked_complexes),
            "direct_member_token_count": direct_member_count,
            "expanded_member_token_count": expanded_member_count,
            "source_member_token_count": expanded_member_count,
            "candidate_count": len(candidates),
            "blocked_token_count": len(blocked_tokens),
            "unique_protein_count": len({row["protein_id"] for row in candidates}),
            "local_protein_reference_candidate_count": len(registered_candidates),
            "local_protein_reference_unique_protein_count": len(
                {row["protein_id"] for row in registered_candidates}
            ),
            "missing_protein_reference_candidate_count": grounding_status_counts[
                "MISSING_LOCAL_PROTEIN_REFERENCE_STAGING_ONLY"
            ],
            "missing_protein_reference_request_count": len(requests),
            "grounding_status_counts": dict(sorted(grounding_status_counts.items())),
            "source_complex_to_protein_taxon_comparison_counts": dict(
                sorted(taxon_comparison_counts.items())
            ),
            "source_complex_taxon_is_component_taxon_acceptance_invariant": False,
            "isoform_candidate_count": sum(
                "-" in row["protein_id"].split(":", 1)[1] for row in candidates
            ),
            "unique_isoform_protein_count": len(
                {
                    row["protein_id"]
                    for row in candidates
                    if "-" in row["protein_id"].split(":", 1)[1]
                }
            ),
            "unknown_stoichiometry_candidate_count": sum(
                not row["source_member_stoichiometry_known"] for row in candidates
            ),
            "expanded_member_class_counts": dict(sorted(expanded_member_classes.items())),
            "direct_member_class_counts": dict(sorted(direct_member_classes.items())),
            "blocked_reason_counts": dict(
                sorted(
                    Counter(
                        reason for row in blocked_tokens for reason in row["blocking_reasons"]
                    ).items()
                )
            ),
            "trait_record_count": len(traits),
            "trait_candidate_artifact_count": len(trait_artifacts),
            "trait_records_outside_curated_snapshot": len(set(traits) - source_complexes),
            "source_derived_exact_trait_binding_count": len(source_bound_trait_rows),
            "trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(trait_binding_rows)
            ).hexdigest(),
            "source_derived_trait_binding_rows_sha256": hashlib.sha256(
                _rows_bytes(source_bound_trait_rows)
            ).hexdigest(),
            "candidate_rows_sha256": hashlib.sha256(_rows_bytes(candidates)).hexdigest(),
            "blocked_token_rows_sha256": hashlib.sha256(_rows_bytes(blocked_tokens)).hexdigest(),
            "protein_request_rows_sha256": hashlib.sha256(_rows_bytes(requests)).hexdigest(),
            "combined_non_summary_rows_sha256": hashlib.sha256(
                _rows_bytes([*candidates, *blocked_tokens, *requests])
            ).hexdigest(),
            "grounding_evidence_emitted_count": 0,
            "network_action_performed": False,
            "write_action_performed": False,
        }
        _content_address(
            summary,
            id_field="stage_id",
            id_prefix="complexportal-grounding-stage:",
            row_hash_field="summary_row_sha256",
        )

        # Full end-of-stage quiescence check. All content-bearing candidates,
        # even semantically irrelevant prefilter hits, are re-read through the
        # bound repository descriptor before the result is returned.
        _assert_directory_binding(traits_binding, description="trait root")
        _assert_directory_binding(route_binding, description="ComplexPortal trait route")
        _reject_tree_symlinks(traits_binding.path, description="trait tree")
        final_route_paths = _exact_route_paths(route_binding)
        if _candidate_trait_paths(traits_binding.path, final_route_paths) != trait_candidate_paths:
            raise ComplexPortalStageError(
                "ComplexPortal trait candidate membership drifted during final quiescence check"
            )
        final_sources, final_excluded = discover_curated_sources(
            raw_binding, expected_source_files=expected_source_files
        )
        if final_sources != source_paths or final_excluded != excluded:
            raise ComplexPortalStageError(
                "ComplexPortal raw source membership drifted while staging"
            )
        for artifact in captured_sources:
            _assert_unchanged(
                artifact,
                description="ComplexTAB source artifact",
                bound_root=repo_binding,
            )
        _assert_unchanged(
            registry_artifact,
            description="ProteinReference registry",
            bound_root=repo_binding,
        )
        for artifact in trait_artifacts:
            _assert_unchanged(
                artifact,
                description="ComplexPortal trait candidate",
                bound_root=repo_binding,
            )
        _assert_directory_binding(route_binding, description="ComplexPortal trait route")
        _assert_directory_binding(traits_binding, description="trait root")
        _assert_directory_binding(raw_binding, description="ComplexPortal raw source directory")
        _assert_directory_binding(repo_binding, description="repository root")
        return StageResult(
            candidates=tuple(candidates),
            blocked_tokens=tuple(blocked_tokens),
            protein_requests=requests,
            summary=summary,
        )
    finally:
        if route_binding is not None:
            os.close(route_binding.descriptor)
        if traits_binding is not None:
            os.close(traits_binding.descriptor)
        if raw_binding is not None:
            os.close(raw_binding.descriptor)
        os.close(repo_binding.descriptor)


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows = [] if summary_only else [canonical_json(row) for row in result.candidates]
    if not summary_only:
        rows.extend(canonical_json(row) for row in result.blocked_tokens)
        rows.extend(canonical_json(row) for row in result.protein_requests)
    rows.append(canonical_json(result.summary))
    return "\n".join(rows) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--traits-root", type=Path, default=DEFAULT_TRAITS_ROOT)
    parser.add_argument("--traits-dir", type=Path, default=DEFAULT_TRAITS_DIR)
    parser.add_argument("--protein-registry", type=Path, default=DEFAULT_PROTEIN_REGISTRY)
    parser.add_argument("--expect-uniprot-release", default=EXPECTED_UNIPROT_RELEASE)
    parser.add_argument("--summary-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_stage(
            raw_dir=args.raw_dir,
            traits_root=args.traits_root,
            traits_dir=args.traits_dir,
            protein_registry_path=args.protein_registry,
            expected_uniprot_release=args.expect_uniprot_release,
        )
    except (ComplexPortalStageError, OSError, ValueError) as error:
        print(f"refusing to stage ComplexPortal grounding candidates: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
