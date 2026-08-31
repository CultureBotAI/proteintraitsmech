#!/usr/bin/env python3
"""Replay every serialized PRINTS representation from the pinned KDAT source.

This is a read-only promotion gate.  It requires the exact allowlisted PRINTS
snapshot receipt and canonical KDAT bytes, discovers every possible PRINTS YAML
record without trusting filenames, and compares each serialized representation
to :func:`prints_kdat.build_fingerprint_representation` with type-strict,
key-exact semantics.  It has no apply or materialization path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

import ripgrep_prefilter

from prints_kdat import (
    PRINTS_42_0_SHA256,
    PRINTS_42_0_SOURCE_ARTIFACT,
    PrintsKdatError,
    PrintsRelease,
    build_fingerprint_representation,
    parse_prints_kdat,
)
from prints_snapshot import (
    EXPECTED_PRINTS_SNAPSHOT_ID,
    KDAT_ARTIFACT,
    KDAT_SOURCE,
    MANIFEST_ID_PREFIX,
    MANIFEST_KIND,
    SCHEMA_VERSION as SNAPSHOT_SCHEMA_VERSION,
    dump_manifest,
    require_expected_manifest_id,
    value_sha256,
)

AUDIT_SCHEMA_VERSION = 1
AUDIT_KIND = "PRINTS_REPRESENTATION_SOURCE_REPLAY_AUDIT"
AUDIT_ID_PREFIX = "prints-representation-audit:"
_IDENTIFIER_RE = re.compile(r"^PRINTS:PR[0-9]{5}$")


class PrintsRepresentationAuditError(ValueError):
    """A source receipt, trait record, or serialized representation is unsafe."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses duplicate keys, including merged keys."""


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


@dataclass(frozen=True, slots=True)
class _Capture:
    """One immutable file capture used for both parsing and its receipt."""

    path: Path
    raw: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class _TraitRecord:
    """One parsed record bound to the exact YAML bytes that produced it."""

    path: Path
    yaml_sha256: str
    value: Mapping[str, Any]


def canonical_json(value: Any) -> str:
    """Canonical, type-preserving JSON for comparisons and audit receipts."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _capture(path: Path, label: str) -> _Capture:
    try:
        with path.open("rb") as handle:
            raw = handle.read()
    except FileNotFoundError as error:
        raise PrintsRepresentationAuditError(f"missing {label}: {path}") from error
    except OSError as error:
        raise PrintsRepresentationAuditError(f"cannot read {label} {path}: {error}") from error
    return _Capture(path=path, raw=raw, sha256=hashlib.sha256(raw).hexdigest())


def _load_manifest(capture: _Capture) -> dict[str, Any]:
    try:
        manifest = json.loads(capture.raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PrintsRepresentationAuditError(
            f"cannot parse PRINTS snapshot manifest {capture.path}: {error}"
        ) from error
    if not isinstance(manifest, dict):
        raise PrintsRepresentationAuditError("PRINTS snapshot manifest is not an object")
    if capture.raw != dump_manifest(manifest):
        raise PrintsRepresentationAuditError("PRINTS snapshot manifest is not canonical JSON")
    expected_top = {
        "schema_version",
        "kind",
        "manifest_id",
        "artifacts",
        "release_evidence",
        "replay_evidence",
    }
    if set(manifest) != expected_top:
        raise PrintsRepresentationAuditError(
            "PRINTS snapshot manifest fields differ from the strict contract"
        )
    if (
        manifest.get("schema_version") != SNAPSHOT_SCHEMA_VERSION
        or manifest.get("kind") != MANIFEST_KIND
    ):
        raise PrintsRepresentationAuditError("PRINTS snapshot manifest version/kind mismatch")
    manifest_id = manifest.get("manifest_id")
    if (
        not isinstance(manifest_id, str)
        or re.fullmatch(rf"{re.escape(MANIFEST_ID_PREFIX)}[0-9a-f]{{64}}", manifest_id) is None
    ):
        raise PrintsRepresentationAuditError("PRINTS snapshot manifest_id is malformed")
    payload = {key: value for key, value in manifest.items() if key != "manifest_id"}
    expected_id = MANIFEST_ID_PREFIX + value_sha256(payload)
    if manifest_id != expected_id:
        raise PrintsRepresentationAuditError(
            f"PRINTS snapshot manifest content-address mismatch; expected {expected_id}"
        )
    try:
        require_expected_manifest_id(manifest_id, EXPECTED_PRINTS_SNAPSHOT_ID)
    except ValueError as error:
        raise PrintsRepresentationAuditError(str(error)) from error
    return manifest


def _verify_manifest_kdat(manifest: Mapping[str, Any], release: PrintsRelease) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise PrintsRepresentationAuditError("PRINTS snapshot artifacts is not an object")
    receipt = artifacts.get("prints_kdat")
    if not isinstance(receipt, dict):
        raise PrintsRepresentationAuditError("PRINTS snapshot has no prints_kdat receipt")
    expected_receipt = {
        "path": KDAT_ARTIFACT,
        "source": KDAT_SOURCE,
        "sha256": release.source_artifact_sha256,
        "bytes": release.source_artifact_size,
        "record_count": len(release.fingerprints),
        "alternate_accession_count": sum(
            len(fingerprint.alternate_accessions) for fingerprint in release.fingerprints.values()
        ),
        "motif_count": sum(
            len(fingerprint.motifs) for fingerprint in release.fingerprints.values()
        ),
        "final_instance_count": sum(
            len(motif.instances)
            for fingerprint in release.fingerprints.values()
            for motif in fingerprint.motifs
        ),
    }
    if canonical_json(receipt) != canonical_json(expected_receipt):
        difference = _first_difference(expected_receipt, receipt)
        raise PrintsRepresentationAuditError(
            f"PRINTS snapshot KDAT receipt does not replay exactly: {difference}"
        )
    release_evidence = manifest.get("release_evidence")
    if not isinstance(release_evidence, dict):
        raise PrintsRepresentationAuditError("PRINTS snapshot release_evidence is not an object")
    if release_evidence.get("prints_release") != release.release:
        raise PrintsRepresentationAuditError(
            "PRINTS snapshot release does not equal the parsed KDAT release"
        )
    if release_evidence.get("prints_release_status") != ("DECLARED_BY_LOCAL_INTERPRO_XML_DBINFO"):
        raise PrintsRepresentationAuditError(
            "PRINTS snapshot release status is not the reviewed XML declaration"
        )


def _require_json_shape(
    value: Any,
    *,
    path: Path,
    location: str = "$",
    ancestors: frozenset[int] = frozenset(),
) -> None:
    """Reject YAML-native values and alias cycles without canonical JSON meaning."""

    if value is None or type(value) in {bool, int, str}:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise PrintsRepresentationAuditError(
                f"trait record is not JSON-shaped at {location} in {path}: non-finite number"
            )
        return
    if type(value) not in {list, dict}:
        raise PrintsRepresentationAuditError(
            f"trait record is not JSON-shaped at {location} in {path}: "
            f"unsupported {type(value).__name__}"
        )
    identity = id(value)
    if identity in ancestors:
        raise PrintsRepresentationAuditError(
            f"trait record has a YAML alias cycle at {location} in {path}"
        )
    nested_ancestors = ancestors | {identity}
    if type(value) is list:
        for index, item in enumerate(value):
            _require_json_shape(
                item,
                path=path,
                location=f"{location}[{index}]",
                ancestors=nested_ancestors,
            )
        return
    for key, item in value.items():
        if type(key) is not str:
            raise PrintsRepresentationAuditError(
                f"trait record is not JSON-shaped at {location} in {path}: "
                f"mapping key {key!r} is not a string"
            )
        _require_json_shape(
            item,
            path=path,
            location=f"{location}.{key}",
            ancestors=nested_ancestors,
        )


def _candidate_prints_paths(traits: Path) -> list[Path]:
    """Find every YAML that can semantically contain an escaped PRINTS value."""

    # ripgrep is not a declared dependency and CI does not install it (#571), and
    # os.walk reports an unreadable tree as an empty one, so the fallback fails
    # closed rather than silently scanning nothing (#573). The shared helper holds
    # both; the command below keeps this scan's own flags.
    executable = shutil.which("rg")
    if executable is None:
        found = ripgrep_prefilter.walked_paths(Path(traits), "PRINTS trait")
        return sorted(found)
    command = [
        executable,
        "--no-config",
        "--null",
        "-l",
        "--text",
        "--hidden",
        "--no-ignore",
        "--follow",
        "--glob",
        "*.yaml",
        "--glob",
        "*.yml",
        "-e",
        "PRINTS",
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
        raise PrintsRepresentationAuditError(
            f"cannot run ripgrep trait prefilter: {error}"
        ) from error
    if scan.returncode not in {0, 1}:
        detail = scan.stderr.decode("utf-8", errors="replace").strip()
        raise PrintsRepresentationAuditError(f"ripgrep trait prefilter failed: {detail}")
    try:
        return sorted(
            Path(raw_path.decode("utf-8", errors="strict"))
            for raw_path in scan.stdout.split(b"\0")
            if raw_path
        )
    except UnicodeDecodeError as error:
        raise PrintsRepresentationAuditError(
            "ripgrep returned a non-UTF-8 trait pathname"
        ) from error


def _reject_unsafe_candidate_path(path: Path, traits: Path) -> None:
    lexical_root = Path(os.path.abspath(traits))
    lexical_path = Path(os.path.abspath(path))
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise PrintsRepresentationAuditError(
            f"trait candidate escapes the requested trait root: {path}"
        ) from error
    cursor = lexical_root
    for component in relative.parts:
        cursor /= component
        if cursor.is_symlink():
            raise PrintsRepresentationAuditError(
                f"trait candidate has a symlink path component: {path}"
            )
    try:
        lexical_path.resolve(strict=True).relative_to(lexical_root.resolve(strict=True))
    except (OSError, ValueError) as error:
        raise PrintsRepresentationAuditError(
            f"trait candidate does not resolve inside the requested trait root: {path}"
        ) from error


def _contains_prints_marker(value: Any, ancestors: frozenset[int] = frozenset()) -> bool:
    if isinstance(value, str):
        return "PRINTS" in value
    if type(value) not in {list, dict}:
        return False
    identity = id(value)
    if identity in ancestors:
        return True
    nested = ancestors | {identity}
    if type(value) is list:
        return any(_contains_prints_marker(item, nested) for item in value)
    return any(
        _contains_prints_marker(key, nested) or _contains_prints_marker(item, nested)
        for key, item in value.items()
    )


def _index_trait_records(
    traits: Path,
) -> tuple[dict[str, _TraitRecord], list[Path], dict[Path, str]]:
    if not traits.is_dir():
        raise PrintsRepresentationAuditError(f"missing trait directory: {traits}")
    if traits.is_symlink():
        raise PrintsRepresentationAuditError(f"trait directory may not be a symlink: {traits}")
    candidate_paths = _candidate_prints_paths(traits)
    candidate_hashes: dict[Path, str] = {}
    prints_records: dict[str, _TraitRecord] = {}
    for path in candidate_paths:
        _reject_unsafe_candidate_path(path, traits)
        capture = _capture(path, "trait candidate")
        candidate_hashes[path] = capture.sha256
        try:
            text = capture.raw.decode("utf-8", errors="strict")
            record = yaml.load(text, Loader=_UniqueKeyLoader)
        except (UnicodeDecodeError, yaml.YAMLError) as error:
            raise PrintsRepresentationAuditError(
                f"cannot load trait candidate {path}: {error}"
            ) from error
        if not isinstance(record, dict):
            raise PrintsRepresentationAuditError(f"trait candidate is not a mapping: {path}")
        _require_json_shape(record, path=path)
        identifier = record.get("identifier")
        representations = record.get("sequence_fingerprint_representations")
        if isinstance(identifier, str) and identifier.startswith("PRINTS:"):
            if _IDENTIFIER_RE.fullmatch(identifier) is None:
                raise PrintsRepresentationAuditError(
                    f"invalid PRINTS identifier {identifier!r} in {path}"
                )
            if identifier in prints_records:
                raise PrintsRepresentationAuditError(
                    f"duplicate PRINTS identifier {identifier}: "
                    f"{prints_records[identifier].path} and {path}"
                )
            prints_records[identifier] = _TraitRecord(
                path=path,
                yaml_sha256=capture.sha256,
                value=record,
            )
        elif _contains_prints_marker(representations):
            raise PrintsRepresentationAuditError(
                f"extra PRINTS representation on non-PRINTS trait {identifier!r} in {path}"
            )
    return prints_records, candidate_paths, candidate_hashes


def _first_difference(expected: Any, actual: Any, location: str = "$") -> str:
    if type(expected) is not type(actual):
        return f"{location}: expected type {type(expected).__name__}, found {type(actual).__name__}"
    if type(expected) is dict:
        expected_keys = set(expected)
        actual_keys = set(actual)
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        if missing:
            return f"{location}: missing key {missing[0]!r}"
        if extra:
            return f"{location}: extra key {extra[0]!r}"
        for key in sorted(expected_keys):
            difference = _first_difference(expected[key], actual[key], f"{location}.{key}")
            if difference:
                return difference
        return ""
    if type(expected) is list:
        if len(expected) != len(actual):
            return f"{location}: expected {len(expected)} rows, found {len(actual)}"
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            difference = _first_difference(
                expected_item,
                actual_item,
                f"{location}[{index}]",
            )
            if difference:
                return difference
        return ""
    if expected != actual:
        return f"{location}: expected {expected!r}, found {actual!r}"
    return ""


def _verify_records(records: Mapping[str, _TraitRecord], release: PrintsRelease) -> tuple[str, str]:
    expected_identifiers = {f"PRINTS:{accession}" for accession in release.fingerprints}
    actual_identifiers = set(records)
    extra = sorted(actual_identifiers - expected_identifiers)
    missing = sorted(expected_identifiers - actual_identifiers)
    if extra:
        raise PrintsRepresentationAuditError(
            f"PRINTS trait identifier has no canonical KDAT primary record: {extra[0]}"
        )
    if missing:
        raise PrintsRepresentationAuditError(
            f"missing PRINTS trait/representation for canonical KDAT record: {missing[0]} "
            f"({len(missing)} missing)"
        )

    representation_projection: list[dict[str, str]] = []
    trait_projection: list[dict[str, str]] = []
    for accession in sorted(release.fingerprints):
        identifier = f"PRINTS:{accession}"
        trait = records[identifier]
        representations = trait.value.get("sequence_fingerprint_representations")
        if not isinstance(representations, list):
            raise PrintsRepresentationAuditError(
                f"{identifier}: missing sequence_fingerprint_representations list in {trait.path}"
            )
        if len(representations) != 1:
            raise PrintsRepresentationAuditError(
                f"{identifier}: expected exactly one serialized PRINTS representation, "
                f"found {len(representations)} in {trait.path}"
            )
        actual = representations[0]
        expected = build_fingerprint_representation(
            release,
            release.fingerprints[accession],
        )
        difference = _first_difference(expected, actual)
        if difference:
            raise PrintsRepresentationAuditError(
                f"{identifier}: serialized representation differs from pinned KDAT: "
                f"{difference} in {trait.path}"
            )
        representation_projection.append(
            {"identifier": identifier, "representation_sha256": value_sha256(expected)}
        )
        trait_projection.append({"identifier": identifier, "yaml_sha256": trait.yaml_sha256})
    return value_sha256(representation_projection), value_sha256(trait_projection)


def _assert_capture_unchanged(path: Path, expected_sha256: str, label: str) -> None:
    current = _capture(path, label)
    if current.sha256 != expected_sha256:
        raise PrintsRepresentationAuditError(f"{label} changed during the audit: {path}")


def audit_prints_representations(
    *, traits_path: Path, kdat_path: Path, manifest_path: Path
) -> dict[str, Any]:
    """Return a deterministic PASS receipt or raise without modifying any input."""

    manifest_capture = _capture(manifest_path, "PRINTS snapshot manifest")
    manifest = _load_manifest(manifest_capture)
    try:
        release = parse_prints_kdat(kdat_path, PRINTS_42_0_SHA256)
    except (PrintsKdatError, OSError, ValueError) as error:
        raise PrintsRepresentationAuditError(str(error)) from error
    _verify_manifest_kdat(manifest, release)

    records, candidate_paths, candidate_hashes = _index_trait_records(traits_path)
    representation_sha256, trait_sha256 = _verify_records(records, release)

    # Re-scan the namespace and re-hash every parsed input before reporting
    # success.  Parsing always used an immutable capture; these checks ensure
    # the live promotion inputs did not drift after those captures.
    if _candidate_prints_paths(traits_path) != candidate_paths:
        raise PrintsRepresentationAuditError(
            "trait candidate set changed during the PRINTS representation audit"
        )
    for path in candidate_paths:
        _assert_capture_unchanged(path, candidate_hashes[path], "trait candidate")
    _assert_capture_unchanged(kdat_path, release.source_artifact_sha256, "PRINTS KDAT source")
    _assert_capture_unchanged(
        manifest_path,
        manifest_capture.sha256,
        "PRINTS snapshot manifest",
    )

    motif_count = sum(len(fingerprint.motifs) for fingerprint in release.fingerprints.values())
    summary: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "kind": AUDIT_KIND,
        "status": "PASS",
        "snapshot_manifest_id": manifest["manifest_id"],
        "snapshot_manifest_sha256": manifest_capture.sha256,
        "source_release": release.release,
        "source_artifact": PRINTS_42_0_SOURCE_ARTIFACT,
        "source_artifact_sha256": release.source_artifact_sha256,
        "source_artifact_bytes": release.source_artifact_size,
        "record_count": len(release.fingerprints),
        "representation_count": len(records),
        "motif_count": motif_count,
        "representation_projection_sha256": representation_sha256,
        "trait_yaml_projection_sha256": trait_sha256,
    }
    summary["audit_id"] = AUDIT_ID_PREFIX + value_sha256(summary)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traits", type=Path, required=True)
    parser.add_argument("--kdat", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = audit_prints_representations(
            traits_path=args.traits,
            kdat_path=args.kdat,
            manifest_path=args.manifest,
        )
    except (PrintsRepresentationAuditError, OSError, ValueError) as error:
        failure = {
            "schema_version": AUDIT_SCHEMA_VERSION,
            "kind": AUDIT_KIND,
            "status": "FAIL",
            "error": str(error),
        }
        print(canonical_json(failure))
        return 2
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
