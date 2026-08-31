#!/usr/bin/env python3
"""Content-addressed snapshot contract for the four PRINTS seeding inputs.

The InterPro API payload does not declare a release.  This module therefore
never assigns one to it.  Instead, it records a narrowly labelled inference:
the exact API accession set agrees with the checksum-pinned PRINTS 42.0 KDAT,
the normalized hierarchy, and the PRINTS ``dbinfo`` count in the exact local
InterPro XML.  Integration assertions are independently replayed from that XML.

For sources already present locally, run from any directory:

    python scripts/prints_snapshot.py --apply

The command performs no network requests and is a dry run without ``--apply``.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import tempfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping

from prints_kdat import (
    PRINTS_42_0_RELEASE,
    PRINTS_42_0_SHA256,
    PrintsRelease,
    parse_prints_kdat,
)

SCHEMA_VERSION = 2
MANIFEST_KIND = "PRINTS_RAW_SNAPSHOT"
MANIFEST_ID_PREFIX = "prints-snapshot:"
# Production is intentionally allowlisted to one reviewed four-artifact capture.
# A content address alone detects mutation relative to a receipt, but would also
# accept a newly generated, internally consistent API/XML snapshot.  Keep this
# identifier in version control so every production consumer rejects that drift.
EXPECTED_PRINTS_SNAPSHOT_ID = (
    "prints-snapshot:05fdb2bd7460d07294708bc6143b2d8ef1fcfdea28cb28d1042fec67715c8b10"
)
MANIFEST_NAME = "prints_snapshot_manifest.json"
HIERARCHY_NAME = "prints_hierarchy.jsonl"
REPO_ROOT = Path(__file__).resolve().parent.parent

API_ARTIFACT = "data/raw/interpro_members/prints.jsonl"
KDAT_ARTIFACT = "data/raw/interpro_members/prints42_0.kdat"
HIERARCHY_ARTIFACT = f"data/raw/interpro_members/{HIERARCHY_NAME}"
INTERPRO_XML_ARTIFACT = "data/raw/interpro/interpro.xml.gz"

API_ENDPOINT = "https://www.ebi.ac.uk/interpro/api/entry/prints/"
KDAT_SOURCE = "https://ftp.ebi.ac.uk/pub/databases/interpro/databases/prints/42.0/prints42_0.kdat"
HIERARCHY_SOURCE = (
    "https://ftp.ebi.ac.uk/pub/databases/interpro/databases/prints/"
    "42.0/FingerPRINTShierarchy21Feb2012"
)

_ACCESSION_RE = re.compile(r"^PR[0-9]{5}$")
_INTERPRO_RE = re.compile(r"^IPR[0-9]{6}$")
_CODE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_EVALUE_RE = re.compile(r"^\+?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
_INTERPRO_OPEN_RE = re.compile(r'<interpro id="(IPR[0-9]{6})"')
_ATTRIBUTE_RE = re.compile(r'([A-Za-z_]+)="([^"]*)"')


class PrintsSnapshotError(ValueError):
    """A PRINTS snapshot is absent, malformed, inconsistent, or not replayable."""


def _valid_evalue_cutoff(value: Any) -> bool:
    """Accept only finite, non-negative decimal/scientific cutoffs."""

    if not isinstance(value, str) or _EVALUE_RE.fullmatch(value) is None:
        return False
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        return False
    return parsed.is_finite() and parsed >= 0


def canonical_json(value: Any) -> str:
    """Deterministic JSON used by JSONL rows and the manifest content address."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class _ArtifactCapture:
    """One immutable read used for every manifest fact about an artifact."""

    path: Path
    raw: bytes
    sha256: str

    @property
    def size(self) -> int:
        return len(self.raw)


def _capture_artifact(path: Path, label: str) -> _ArtifactCapture:
    try:
        with path.open("rb") as handle:
            raw = handle.read()
    except FileNotFoundError as error:
        raise PrintsSnapshotError(f"missing {label} artifact: {path}") from error
    except OSError as error:
        raise PrintsSnapshotError(f"cannot read {label} artifact {path}: {error}") from error
    return _ArtifactCapture(
        path=path,
        raw=raw,
        sha256=hashlib.sha256(raw).hexdigest(),
    )


def file_sha256(path: Path) -> str:
    return _capture_artifact(path, "snapshot").sha256


def _load_jsonl_bytes(raw: bytes, path: Path, label: str) -> list[dict[str, Any]]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise PrintsSnapshotError(f"{path}: {label} artifact is not valid UTF-8") from error
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            raise PrintsSnapshotError(f"{path}:{line_number}: blank JSONL row")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise PrintsSnapshotError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
        if not isinstance(value, dict):
            raise PrintsSnapshotError(f"{path}:{line_number}: row is not an object")
        rows.append(value)
    return rows


def _parse_prints_api_rows(raw: bytes, path: Path) -> list[dict[str, Any]]:
    rows = _load_jsonl_bytes(raw, path, "PRINTS API")
    allowed = {"accession", "name", "type", "integrated", "source_database"}
    seen: set[str] = set()
    for line_number, row in enumerate(rows, 1):
        if set(row) != allowed:
            raise PrintsSnapshotError(
                f"{path}:{line_number}: API fields differ from the strict contract"
            )
        accession = row.get("accession")
        if not isinstance(accession, str) or _ACCESSION_RE.fullmatch(accession) is None:
            raise PrintsSnapshotError(f"{path}:{line_number}: invalid accession {accession!r}")
        if accession in seen:
            raise PrintsSnapshotError(f"{path}:{line_number}: duplicate accession {accession}")
        seen.add(accession)
        if row.get("source_database") != "prints":
            raise PrintsSnapshotError(
                f"{path}:{line_number}: source_database is not exactly 'prints'"
            )
        if not isinstance(row.get("name"), str) or not isinstance(row.get("type"), str):
            raise PrintsSnapshotError(f"{path}:{line_number}: name/type must be strings")
        integrated = row.get("integrated")
        if integrated is not None and (
            not isinstance(integrated, str) or _INTERPRO_RE.fullmatch(integrated) is None
        ):
            raise PrintsSnapshotError(
                f"{path}:{line_number}: malformed integrated accession {integrated!r}"
            )
    return rows


def load_prints_api_rows(path: Path) -> list[dict[str, Any]]:
    """Load API rows from the same immutable capture used for decoding."""

    capture = _capture_artifact(path, "PRINTS API")
    return _parse_prints_api_rows(capture.raw, path)


def parse_hierarchy_source(raw: bytes) -> list[dict[str, Any]]:
    """Normalize the upstream PRINTS post-processing table without inventing a tree.

    InterProScan's official ``FingerPRINTSHierarchyDBParser`` defines columns
    3--5 (zero-based 2--4) as e-value cutoff, minimum motif count, and a sibling /
    hierarchical-relation field.  A literal ``*`` in the final field is a domain
    flag.  These relations are post-processing constraints, not subclass edges.
    """

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise PrintsSnapshotError("PRINTS hierarchy source is not valid UTF-8") from error
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 5:
            raise PrintsSnapshotError(
                f"hierarchy source line {line_number}: expected five pipe fields"
            )
        code, accession, evalue, motif_count_text, relation_text = (part.strip() for part in parts)
        if _CODE_RE.fullmatch(code) is None:
            raise PrintsSnapshotError(f"hierarchy source line {line_number}: invalid code {code!r}")
        if _ACCESSION_RE.fullmatch(accession) is None:
            raise PrintsSnapshotError(
                f"hierarchy source line {line_number}: invalid accession {accession!r}"
            )
        try:
            minimum_motif_count = int(motif_count_text)
        except ValueError as error:
            raise PrintsSnapshotError(
                f"hierarchy source line {line_number}: non-integer minimum motif count"
            ) from error
        if minimum_motif_count < 0 or not _valid_evalue_cutoff(evalue):
            raise PrintsSnapshotError(
                f"hierarchy source line {line_number}: invalid motif count/e-value"
            )
        relations = (
            []
            if relation_text in {"", "*"}
            else [item.strip() for item in relation_text.split(",")]
        )
        if any(_CODE_RE.fullmatch(item) is None for item in relations):
            raise PrintsSnapshotError(
                f"hierarchy source line {line_number}: invalid hierarchical relation code"
            )
        rows.append(
            {
                "accession": accession,
                "code": code,
                "domain_flag": relation_text == "*",
                "evalue_cutoff": evalue,
                "hierarchical_relations": relations,
                "minimum_motif_count": minimum_motif_count,
            }
        )
    return _validate_hierarchy_rows(rows, "hierarchy source")


def _validate_hierarchy_rows(rows: Iterable[Mapping[str, Any]], label: str) -> list[dict[str, Any]]:
    allowed = {
        "accession",
        "code",
        "domain_flag",
        "evalue_cutoff",
        "hierarchical_relations",
        "minimum_motif_count",
    }
    normalized: list[dict[str, Any]] = []
    accessions: set[str] = set()
    codes: set[str] = set()
    for line_number, raw in enumerate(rows, 1):
        row = dict(raw)
        if set(row) != allowed:
            raise PrintsSnapshotError(f"{label}:{line_number}: hierarchy fields differ")
        accession = row.get("accession")
        code = row.get("code")
        relations = row.get("hierarchical_relations")
        if not isinstance(accession, str) or _ACCESSION_RE.fullmatch(accession) is None:
            raise PrintsSnapshotError(f"{label}:{line_number}: invalid hierarchy accession")
        if not isinstance(code, str) or _CODE_RE.fullmatch(code) is None:
            raise PrintsSnapshotError(f"{label}:{line_number}: invalid hierarchy code")
        if accession in accessions or code in codes:
            raise PrintsSnapshotError(f"{label}:{line_number}: duplicate accession/code")
        if not isinstance(relations, list) or any(
            not isinstance(item, str) or _CODE_RE.fullmatch(item) is None for item in relations
        ):
            raise PrintsSnapshotError(f"{label}:{line_number}: invalid hierarchical relations")
        if len(set(relations)) != len(relations):
            raise PrintsSnapshotError(f"{label}:{line_number}: duplicate hierarchical relation")
        if not isinstance(row.get("domain_flag"), bool):
            raise PrintsSnapshotError(f"{label}:{line_number}: invalid domain flag")
        if not _valid_evalue_cutoff(row.get("evalue_cutoff")):
            raise PrintsSnapshotError(f"{label}:{line_number}: invalid e-value cutoff")
        if type(row.get("minimum_motif_count")) is not int or row["minimum_motif_count"] < 0:
            raise PrintsSnapshotError(f"{label}:{line_number}: invalid minimum motif count")
        if row["domain_flag"] and relations:
            raise PrintsSnapshotError(
                f"{label}:{line_number}: domain flag cannot carry hierarchical relations"
            )
        accessions.add(accession)
        codes.add(code)
        normalized.append(row)
    unknown_relations = sorted(
        {
            relation
            for row in normalized
            for relation in row["hierarchical_relations"]
            if relation not in codes
        }
    )
    if unknown_relations:
        raise PrintsSnapshotError(
            f"{label}: unknown hierarchical relation codes {unknown_relations[:5]!r}"
        )
    return sorted(normalized, key=lambda row: row["accession"])


def dump_hierarchy_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    normalized = _validate_hierarchy_rows(rows, "hierarchy rows")
    return "".join(canonical_json(row) + "\n" for row in normalized).encode("utf-8")


def _parse_hierarchy_jsonl(raw: bytes, path: Path) -> list[dict[str, Any]]:
    rows = _load_jsonl_bytes(raw, path, "normalized PRINTS hierarchy")
    normalized = _validate_hierarchy_rows(rows, str(path))
    if rows != normalized:
        raise PrintsSnapshotError(f"{path}: hierarchy rows are not in canonical order")
    expected = dump_hierarchy_jsonl(normalized)
    if raw != expected:
        raise PrintsSnapshotError(f"{path}: hierarchy JSONL is not canonical")
    return normalized


def load_hierarchy_jsonl(path: Path) -> list[dict[str, Any]]:
    capture = _capture_artifact(path, "normalized PRINTS hierarchy")
    return _parse_hierarchy_jsonl(capture.raw, path)


def _parse_interpro_xml_bytes(raw: bytes, path: Path) -> dict[str, Any]:
    """Parse exact XML declarations from one captured compressed byte string."""

    dbinfo: dict[str, dict[str, Any]] = {}
    integrations: dict[str, str] = {}
    current_interpro: str | None = None
    in_member_list = False
    observed_interpro_entries = 0
    try:
        compressed = io.BytesIO(raw)
        with gzip.GzipFile(fileobj=compressed, mode="rb") as binary_handle:
            with io.TextIOWrapper(binary_handle, encoding="utf-8", errors="strict") as handle:
                for line_number, line in enumerate(handle, 1):
                    if "<dbinfo " in line:
                        attributes = dict(_ATTRIBUTE_RE.findall(line))
                        name = attributes.get("dbname")
                        if not name or name in dbinfo:
                            raise PrintsSnapshotError(
                                f"{path}:{line_number}: duplicate/malformed dbinfo"
                            )
                        try:
                            entry_count = int(attributes["entry_count"])
                        except (KeyError, ValueError) as error:
                            raise PrintsSnapshotError(
                                f"{path}:{line_number}: malformed dbinfo entry_count"
                            ) from error
                        dbinfo[name] = {
                            "version": attributes.get("version"),
                            "entry_count": entry_count,
                            "file_date": attributes.get("file_date"),
                        }
                    opened = _INTERPRO_OPEN_RE.search(line)
                    if opened:
                        current_interpro = opened.group(1)
                        observed_interpro_entries += 1
                    if "<member_list>" in line:
                        in_member_list = True
                        continue
                    if "</member_list>" in line:
                        in_member_list = False
                        continue
                    if in_member_list and 'db="PRINTS"' in line:
                        attributes = dict(_ATTRIBUTE_RE.findall(line))
                        accession = attributes.get("dbkey")
                        if (
                            current_interpro is None
                            or not isinstance(accession, str)
                            or _ACCESSION_RE.fullmatch(accession) is None
                        ):
                            raise PrintsSnapshotError(
                                f"{path}:{line_number}: malformed PRINTS member mapping"
                            )
                        previous = integrations.get(accession)
                        if previous is not None and previous != current_interpro:
                            raise PrintsSnapshotError(
                                f"{path}:{line_number}: ambiguous integration for {accession}"
                            )
                        integrations[accession] = current_interpro
    except (OSError, EOFError, UnicodeDecodeError) as error:
        raise PrintsSnapshotError(f"cannot parse local InterPro XML {path}: {error}") from error

    prints_info = dbinfo.get("PRINTS")
    interpro_info = dbinfo.get("INTERPRO")
    if prints_info is None or interpro_info is None:
        raise PrintsSnapshotError(f"{path}: missing PRINTS or INTERPRO dbinfo declaration")
    if interpro_info["entry_count"] != observed_interpro_entries:
        raise PrintsSnapshotError(
            f"{path}: INTERPRO dbinfo count {interpro_info['entry_count']} != "
            f"observed {observed_interpro_entries}"
        )
    return {
        "prints_dbinfo": prints_info,
        "interpro_dbinfo": interpro_info,
        "observed_interpro_entries": observed_interpro_entries,
        "integrations": integrations,
    }


def _parse_interpro_xml(path: Path) -> dict[str, Any]:
    """Read XML from one immutable capture (compatibility wrapper)."""

    capture = _capture_artifact(path, "local InterPro XML")
    return _parse_interpro_xml_bytes(capture.raw, path)


def _projection_sha(mapping: Mapping[str, str]) -> str:
    projection = [
        {"accession": accession, "interpro": mapping[accession]} for accession in sorted(mapping)
    ]
    return value_sha256(projection)


def _with_manifest_id(payload: dict[str, Any]) -> dict[str, Any]:
    value = dict(payload)
    value["manifest_id"] = MANIFEST_ID_PREFIX + value_sha256(payload)
    return value


def require_expected_manifest_id(actual: Any, expected: str) -> None:
    """Reject a valid-but-unapproved snapshot identity before artifact replay."""

    pattern = rf"{re.escape(MANIFEST_ID_PREFIX)}[0-9a-f]{{64}}"
    if not isinstance(expected, str) or re.fullmatch(pattern, expected) is None:
        raise PrintsSnapshotError(
            f"configured expected PRINTS snapshot manifest_id is malformed: {expected!r}"
        )
    if actual != expected:
        raise PrintsSnapshotError(
            "PRINTS snapshot is internally content-addressed but is not the pinned "
            f"production snapshot; expected {expected}, found {actual!r}"
        )


@dataclass(frozen=True, slots=True)
class _CapturedPrintsSources:
    """The only source objects a verified replay or downstream consumer may use."""

    api: _ArtifactCapture
    kdat: PrintsRelease
    hierarchy: _ArtifactCapture
    interpro_xml: _ArtifactCapture


@dataclass(frozen=True, slots=True)
class VerifiedPrintsSnapshot:
    """Manifest-bound PRINTS inputs captured before any live path can be reopened.

    The raw byte captures are private and immutable.  Accessors parse those
    bytes, while the KDAT release is the parser-sealed object created from its
    own single immutable read.  Consequently a caller cannot accidentally
    verify one version of a path and consume a later same-path replacement.
    """

    _manifest_raw: bytes
    _sources: _CapturedPrintsSources

    @property
    def manifest(self) -> dict[str, Any]:
        """Return a fresh copy so callers cannot mutate the verified receipt."""

        value = json.loads(self._manifest_raw)
        assert isinstance(value, dict)
        return value

    @property
    def manifest_id(self) -> str:
        value = self.manifest["manifest_id"]
        assert isinstance(value, str)
        return value

    @property
    def kdat_release(self) -> PrintsRelease:
        return self._sources.kdat

    @property
    def interpro_xml_bytes(self) -> bytes:
        return self._sources.interpro_xml.raw

    def load_api_rows(self) -> list[dict[str, Any]]:
        return _parse_prints_api_rows(self._sources.api.raw, self._sources.api.path)

    def load_hierarchy_rows(self) -> list[dict[str, Any]]:
        return _parse_hierarchy_jsonl(
            self._sources.hierarchy.raw,
            self._sources.hierarchy.path,
        )


def _capture_prints_sources(
    *,
    api_path: Path,
    kdat_path: Path,
    hierarchy_path: Path,
    interpro_xml_path: Path,
) -> _CapturedPrintsSources:
    """Capture each live source path exactly once into immutable parser state."""

    api_capture = _capture_artifact(api_path, "PRINTS API")
    hierarchy_capture = _capture_artifact(hierarchy_path, "normalized PRINTS hierarchy")
    xml_capture = _capture_artifact(interpro_xml_path, "local InterPro XML")
    try:
        # parse_prints_kdat performs one binary read and binds every parsed value,
        # its digest, and its size to a private provenance seal.
        kdat = parse_prints_kdat(kdat_path, PRINTS_42_0_SHA256)
    except ValueError as error:
        raise PrintsSnapshotError(str(error)) from error
    return _CapturedPrintsSources(
        api=api_capture,
        kdat=kdat,
        hierarchy=hierarchy_capture,
        interpro_xml=xml_capture,
    )


def _build_prints_manifest_from_sources(sources: _CapturedPrintsSources) -> dict[str, Any]:
    """Replay a manifest exclusively from already-captured source state."""

    api_capture = sources.api
    hierarchy_capture = sources.hierarchy
    xml_capture = sources.interpro_xml
    kdat = sources.kdat
    api_rows = _parse_prints_api_rows(api_capture.raw, api_capture.path)
    api_by_accession = {row["accession"]: row for row in api_rows}
    hierarchy_rows = _parse_hierarchy_jsonl(hierarchy_capture.raw, hierarchy_capture.path)
    hierarchy_by_accession = {row["accession"]: row for row in hierarchy_rows}
    xml = _parse_interpro_xml_bytes(xml_capture.raw, xml_capture.path)

    api_accessions = set(api_by_accession)
    kdat_accessions = set(kdat.fingerprints)
    hierarchy_accessions = set(hierarchy_by_accession)
    if not (api_accessions == kdat_accessions == hierarchy_accessions):
        raise PrintsSnapshotError(
            "PRINTS API, KDAT, and hierarchy accession sets do not match exactly"
        )
    code_mismatches = [
        accession
        for accession in sorted(kdat_accessions)
        if hierarchy_by_accession[accession]["code"] != kdat.fingerprints[accession].code
    ]
    if code_mismatches:
        raise PrintsSnapshotError(f"KDAT/hierarchy code mismatches for {code_mismatches[:5]!r}")

    prints_dbinfo = xml["prints_dbinfo"]
    if prints_dbinfo["version"] != PRINTS_42_0_RELEASE:
        raise PrintsSnapshotError(
            f"local InterPro XML declares PRINTS {prints_dbinfo['version']!r}, "
            f"expected {PRINTS_42_0_RELEASE}"
        )
    if prints_dbinfo["entry_count"] != len(api_rows):
        raise PrintsSnapshotError(
            "local InterPro XML PRINTS count does not match exact API/KDAT count"
        )

    api_integrations = {
        accession: row["integrated"]
        for accession, row in api_by_accession.items()
        if row["integrated"] is not None
    }
    xml_integrations = xml["integrations"]
    if api_integrations != xml_integrations:
        raise PrintsSnapshotError(
            "captured API integrations do not replay exactly from the local InterPro XML"
        )

    accession_projection = sorted(api_accessions)
    accession_sha = value_sha256(accession_projection)
    hierarchy_projection_sha = value_sha256(hierarchy_rows)
    api_integration_sha = _projection_sha(api_integrations)
    xml_integration_sha = _projection_sha(xml_integrations)
    motif_count = sum(len(item.motifs) for item in kdat.fingerprints.values())
    final_instance_count = sum(
        len(motif.instances) for item in kdat.fingerprints.values() for motif in item.motifs
    )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": MANIFEST_KIND,
        "artifacts": {
            "prints_api": {
                "path": API_ARTIFACT,
                "source": API_ENDPOINT,
                "sha256": api_capture.sha256,
                "bytes": api_capture.size,
                "row_count": len(api_rows),
            },
            "prints_kdat": {
                "path": KDAT_ARTIFACT,
                "source": KDAT_SOURCE,
                "sha256": kdat.source_artifact_sha256,
                "bytes": kdat.source_artifact_size,
                "record_count": len(kdat.fingerprints),
                "alternate_accession_count": sum(
                    len(item.alternate_accessions) for item in kdat.fingerprints.values()
                ),
                "motif_count": motif_count,
                "final_instance_count": final_instance_count,
            },
            "prints_hierarchy": {
                "path": HIERARCHY_ARTIFACT,
                "source": HIERARCHY_SOURCE,
                "sha256": hierarchy_capture.sha256,
                "bytes": hierarchy_capture.size,
                "row_count": len(hierarchy_rows),
            },
            "interpro_xml": {
                "path": INTERPRO_XML_ARTIFACT,
                "sha256": xml_capture.sha256,
                "bytes": xml_capture.size,
                "declared_interpro_entry_count": xml["interpro_dbinfo"]["entry_count"],
                "observed_interpro_entry_count": xml["observed_interpro_entries"],
            },
        },
        "release_evidence": {
            "prints_release": PRINTS_42_0_RELEASE,
            "prints_release_status": "DECLARED_BY_LOCAL_INTERPRO_XML_DBINFO",
            "prints_file_date": prints_dbinfo["file_date"],
            "interpro_release": xml["interpro_dbinfo"]["version"],
            "interpro_release_status": "DECLARED_BY_LOCAL_INTERPRO_XML_DBINFO",
            "interpro_file_date": xml["interpro_dbinfo"]["file_date"],
            "api_declared_release": None,
            "api_release_status": "NOT_DECLARED_IN_CAPTURED_API_PAYLOAD",
            "api_consistency_inference": {
                "status": "INFERRED_FROM_CONTENT_EQUALITY_NOT_API_RELEASE_METADATA",
                "basis": (
                    "exact primary-accession equality with checksum-pinned PRINTS 42.0 "
                    "KDAT, normalized hierarchy, and local XML dbinfo count"
                ),
                "accession_count": len(api_accessions),
                "accession_projection_sha256": accession_sha,
            },
        },
        "replay_evidence": {
            "accessions": {
                "api_count": len(api_accessions),
                "kdat_primary_count": len(kdat_accessions),
                "hierarchy_count": len(hierarchy_accessions),
                "exact_set_match": True,
                "projection_sha256": accession_sha,
            },
            "hierarchy": {
                "exact_accession_and_code_match": True,
                "projection_sha256": hierarchy_projection_sha,
            },
            "integrations": {
                "api_integrated_count": len(api_integrations),
                "api_unintegrated_count": len(api_rows) - len(api_integrations),
                "xml_prints_member_count": len(xml_integrations),
                "exact_mapping_match_count": len(api_integrations),
                "mismatch_count": 0,
                "api_projection_sha256": api_integration_sha,
                "xml_projection_sha256": xml_integration_sha,
            },
        },
    }
    return _with_manifest_id(payload)


def build_prints_manifest(
    *,
    api_path: Path,
    kdat_path: Path,
    hierarchy_path: Path,
    interpro_xml_path: Path,
) -> dict[str, Any]:
    """Build a manifest only when every cross-artifact replay is exact."""

    sources = _capture_prints_sources(
        api_path=api_path,
        kdat_path=kdat_path,
        hierarchy_path=hierarchy_path,
        interpro_xml_path=interpro_xml_path,
    )
    return _build_prints_manifest_from_sources(sources)


def dump_manifest(manifest: Mapping[str, Any]) -> bytes:
    return (canonical_json(dict(manifest)) + "\n").encode("utf-8")


def _load_manifest_receipt(
    manifest_path: Path,
    *,
    expected_manifest_id: str,
) -> tuple[bytes, dict[str, Any]]:
    """Capture and authenticate the receipt before any source artifact is read."""

    try:
        with manifest_path.open("rb") as handle:
            raw = handle.read()
        manifest = json.loads(raw)
    except FileNotFoundError as error:
        raise PrintsSnapshotError(f"missing PRINTS snapshot manifest: {manifest_path}") from error
    except (OSError, json.JSONDecodeError) as error:
        raise PrintsSnapshotError(f"cannot read PRINTS snapshot manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise PrintsSnapshotError("PRINTS snapshot manifest is not an object")
    if raw != dump_manifest(manifest):
        raise PrintsSnapshotError("PRINTS snapshot manifest is not canonical JSON")
    expected_top = {
        "schema_version",
        "kind",
        "manifest_id",
        "artifacts",
        "release_evidence",
        "replay_evidence",
    }
    if set(manifest) != expected_top:
        raise PrintsSnapshotError("PRINTS snapshot manifest fields differ from contract")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("kind") != MANIFEST_KIND:
        raise PrintsSnapshotError("PRINTS snapshot manifest version/kind mismatch")
    manifest_id = manifest.get("manifest_id")
    if not isinstance(manifest_id, str) or not re.fullmatch(
        rf"{re.escape(MANIFEST_ID_PREFIX)}[0-9a-f]{{64}}", manifest_id
    ):
        raise PrintsSnapshotError("PRINTS snapshot manifest_id is malformed")
    payload = {key: value for key, value in manifest.items() if key != "manifest_id"}
    expected_id = MANIFEST_ID_PREFIX + value_sha256(payload)
    if manifest_id != expected_id:
        raise PrintsSnapshotError(
            f"PRINTS snapshot manifest content-address mismatch; expected {expected_id}"
        )
    # Check the durable production allowlist before parsing any source artifact.
    # This makes a different but self-consistent receipt fail closed cheaply.
    require_expected_manifest_id(manifest_id, expected_manifest_id)
    return raw, manifest


def load_verified_prints_snapshot(
    manifest_path: Path,
    *,
    expected_manifest_id: str,
    api_path: Path,
    kdat_path: Path,
    hierarchy_path: Path,
    interpro_xml_path: Path,
) -> VerifiedPrintsSnapshot:
    """Return manifest-bound captures for every downstream PRINTS read.

    Live source paths are each read once.  The manifest replay and the returned
    consumer accessors share those exact captures, closing the verifier-to-user
    same-path replacement window.
    """

    manifest_raw, manifest = _load_manifest_receipt(
        manifest_path,
        expected_manifest_id=expected_manifest_id,
    )
    sources = _capture_prints_sources(
        api_path=api_path,
        kdat_path=kdat_path,
        hierarchy_path=hierarchy_path,
        interpro_xml_path=interpro_xml_path,
    )
    replayed = _build_prints_manifest_from_sources(sources)
    manifest_id = manifest["manifest_id"]
    assert isinstance(manifest_id, str)

    if manifest != replayed:
        raise PrintsSnapshotError(
            "PRINTS snapshot manifest does not match the exact current artifacts; "
            f"expected {replayed['manifest_id']}, found {manifest_id}"
        )
    return VerifiedPrintsSnapshot(
        _manifest_raw=manifest_raw,
        _sources=sources,
    )


def verify_prints_manifest(
    manifest_path: Path,
    *,
    expected_manifest_id: str,
    api_path: Path,
    kdat_path: Path,
    hierarchy_path: Path,
    interpro_xml_path: Path,
) -> dict[str, Any]:
    """Fail closed unless the manifest and all four current files replay exactly."""

    verified = load_verified_prints_snapshot(
        manifest_path,
        expected_manifest_id=expected_manifest_id,
        api_path=api_path,
        kdat_path=kdat_path,
        hierarchy_path=hierarchy_path,
        interpro_xml_path=interpro_xml_path,
    )
    return verified.manifest


def materialize_local_snapshot(
    *,
    expected_manifest_id: str,
    api_path: Path,
    kdat_path: Path,
    hierarchy_source_path: Path,
    hierarchy_path: Path,
    interpro_xml_path: Path,
    manifest_path: Path,
    apply: bool,
) -> dict[str, Any]:
    """Normalize and manifest already-downloaded sources without network access.

    Both derived files are staged and fully replayed first. On apply, the
    normalized hierarchy is installed before the manifest, ensuring an
    interrupted update cannot leave a manifest that blesses mismatched bytes.
    """

    resolved_inputs = {
        "api": api_path.resolve(),
        "kdat": kdat_path.resolve(),
        "hierarchy_source": hierarchy_source_path.resolve(),
        "interpro_xml": interpro_xml_path.resolve(),
    }
    resolved_hierarchy_output = hierarchy_path.resolve()
    resolved_manifest_output = manifest_path.resolve()
    if resolved_hierarchy_output == resolved_manifest_output:
        raise PrintsSnapshotError("hierarchy and manifest outputs must be distinct paths")
    for label, input_path in resolved_inputs.items():
        if input_path in {resolved_hierarchy_output, resolved_manifest_output}:
            raise PrintsSnapshotError(f"snapshot output aliases the {label} input: {input_path}")
    if (
        hierarchy_path.name != HIERARCHY_NAME
        or manifest_path.name != MANIFEST_NAME
        or resolved_hierarchy_output.parent != resolved_manifest_output.parent
    ):
        raise PrintsSnapshotError(
            "snapshot outputs must use the canonical names in one common directory"
        )
    stage_parent: Path | None = None
    if apply:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        hierarchy_path.parent.mkdir(parents=True, exist_ok=True)
        stage_parent = manifest_path.parent
    with tempfile.TemporaryDirectory(prefix=".prints-local-snapshot-", dir=stage_parent) as tmp:
        stage = Path(tmp)
        staged_hierarchy = stage / HIERARCHY_NAME
        staged_manifest = stage / MANIFEST_NAME
        hierarchy_source_capture = _capture_artifact(
            hierarchy_source_path, "upstream PRINTS hierarchy source"
        )
        hierarchy_rows = parse_hierarchy_source(hierarchy_source_capture.raw)
        staged_hierarchy.write_bytes(dump_hierarchy_jsonl(hierarchy_rows))
        manifest = build_prints_manifest(
            api_path=api_path,
            kdat_path=kdat_path,
            hierarchy_path=staged_hierarchy,
            interpro_xml_path=interpro_xml_path,
        )
        require_expected_manifest_id(manifest.get("manifest_id"), expected_manifest_id)
        staged_manifest.write_bytes(dump_manifest(manifest))
        verify_prints_manifest(
            staged_manifest,
            expected_manifest_id=expected_manifest_id,
            api_path=api_path,
            kdat_path=kdat_path,
            hierarchy_path=staged_hierarchy,
            interpro_xml_path=interpro_xml_path,
        )
        if apply:
            staged_hierarchy.replace(hierarchy_path)
            staged_manifest.replace(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize and content-address an already-downloaded local PRINTS snapshot; "
            "no network requests are made."
        )
    )
    parser.add_argument(
        "--api", type=Path, default=REPO_ROOT / API_ARTIFACT, help="captured prints.jsonl"
    )
    parser.add_argument(
        "--kdat",
        type=Path,
        default=REPO_ROOT / KDAT_ARTIFACT,
        help="pinned PRINTS 42.0 KDAT",
    )
    parser.add_argument(
        "--hierarchy-source",
        type=Path,
        default=REPO_ROOT / "data/raw/interpro_members/FingerPRINTShierarchy21Feb2012",
        help="downloaded upstream pipe hierarchy",
    )
    parser.add_argument(
        "--hierarchy-output",
        type=Path,
        default=REPO_ROOT / HIERARCHY_ARTIFACT,
        help="normalized hierarchy JSONL",
    )
    parser.add_argument(
        "--interpro-xml",
        type=Path,
        default=REPO_ROOT / INTERPRO_XML_ARTIFACT,
        help="exact local InterPro XML consumed by the seeder",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "data/raw/interpro_members" / MANIFEST_NAME,
        help="content-addressed manifest output",
    )
    parser.add_argument("--apply", action="store_true", help="install derived files")
    args = parser.parse_args()
    try:
        manifest = materialize_local_snapshot(
            expected_manifest_id=EXPECTED_PRINTS_SNAPSHOT_ID,
            api_path=args.api,
            kdat_path=args.kdat,
            hierarchy_source_path=args.hierarchy_source,
            hierarchy_path=args.hierarchy_output,
            interpro_xml_path=args.interpro_xml,
            manifest_path=args.manifest,
            apply=args.apply,
        )
    except PrintsSnapshotError as error:
        parser.error(str(error))
    action = "installed" if args.apply else "verified (dry run)"
    print(f"{action}: {manifest['manifest_id']}")
    if not args.apply:
        print("pass --apply to install the normalized hierarchy and manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
