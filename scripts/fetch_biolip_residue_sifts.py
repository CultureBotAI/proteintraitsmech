#!/usr/bin/env python3
"""Fetch manifest-bound residue-level SIFTS XML for BioLiP.

This consumes the no-write ``BIOLIP_RESIDUE_LEVEL_SIFTS_FETCH_REQUEST`` rows
emitted by ``stage_biolip_missing_protein_candidates.py`` and snapshots exactly
those official PDBe XML gzip files. It does not map BioLiP
coordinates, pick UniProt accessions, or emit grounding evidence; a complete
snapshot is only the raw residue-level SIFTS acquisition boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import build_ecod_sifts_candidates as ecod_sifts


REPO_ROOT = Path(__file__).resolve().parents[1]
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
GROUNDING_ROOT = REPO_ROOT / "data" / "grounding"
DEFAULT_STAGE = REPO_ROOT / "reports" / "uniprot-grounding" / ("biolip-missing-protein-stage.jsonl")
DEFAULT_SNAPSHOT_ROOT = REPO_ROOT / "data" / "raw" / "biolip-sifts-xml"
SIFTS_SOURCE_ROOT = "https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml"
FETCH_REQUEST_KIND = "BIOLIP_RESIDUE_LEVEL_SIFTS_FETCH_REQUEST"
SUMMARY_KIND = "BIOLIP_MISSING_PROTEIN_STAGE_SUMMARY"
MANIFEST_NAME = "manifest.json"
SCHEMA_VERSION = 1
SNAPSHOT_ID_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,78}[A-Za-z0-9])?$")
PDB_RE = re.compile(r"^[0-9][a-z0-9]{3}$")

MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "kind",
        "snapshot_id",
        "source",
        "source_root",
        "stage_path",
        "stage_sha256",
        "stage_id",
        "stage_combined_non_summary_rows_sha256",
        "fetch_request_count",
        "fetch_request_ids_sha256",
        "requested_pdb_count",
        "requested_pdb_ids_sha256",
        "entries",
        "failures",
        "complete",
    }
)
ENTRY_FIELDS = frozenset(
    {
        "pdb_id",
        "path",
        "sha256",
        "size_bytes",
        "sifts_entry_date",
        "sifts_uniprot_release",
        "sifts_uniprot_version",
        "url",
    }
)


class BioLipSiftsFetchError(ValueError):
    """BioLiP SIFTS acquisition cannot produce a canonical snapshot."""


@dataclass(frozen=True)
class StageRequests:
    stage_sha256: str
    stage_id: str
    combined_non_summary_rows_sha256: str
    requests: tuple[dict[str, Any], ...]

    @property
    def pdb_ids(self) -> tuple[str, ...]:
        return tuple(row["pdb_id"] for row in self.requests)

    @property
    def request_ids(self) -> tuple[str, ...]:
        return tuple(row["fetch_request_id"] for row in self.requests)


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


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _reject_protected_target(path: Path, *, label: str) -> None:
    resolved = path.resolve()
    for root, name in ((TRAITS_ROOT, "data/traits"), (GROUNDING_ROOT, "data/grounding")):
        root_resolved = root.resolve()
        if resolved == root_resolved or _is_under(resolved, root_resolved):
            raise BioLipSiftsFetchError(f"{label} must not be inside {name}: {path}")


def _validate_snapshot_id(value: str) -> str:
    if SNAPSHOT_ID_RE.fullmatch(value) is None or Path(value).name != value:
        raise BioLipSiftsFetchError(
            "snapshot-id must be one safe 1-80 character path component "
            "(letters, digits, dot, underscore, or hyphen; alphanumeric ends)"
        )
    return value


def _validate_fetch_request(row: dict[str, Any], *, line_number: int) -> None:
    without_hash = dict(row)
    row_hash = without_hash.pop("fetch_request_row_sha256", None)
    if row_hash != value_sha256(without_hash):
        raise BioLipSiftsFetchError(f"line {line_number}: fetch_request_row_sha256 mismatch")
    without_id = dict(without_hash)
    fetch_request_id = without_id.pop("fetch_request_id", None)
    expected_id = "biolip-residue-sifts-fetch-request:" + value_sha256(without_id)
    if fetch_request_id != expected_id:
        raise BioLipSiftsFetchError(f"line {line_number}: fetch_request_id mismatch")
    if row.get("kind") != FETCH_REQUEST_KIND:
        raise BioLipSiftsFetchError(f"line {line_number}: not a BioLiP SIFTS fetch request")
    if row.get("schema_version") != SCHEMA_VERSION:
        raise BioLipSiftsFetchError(f"line {line_number}: unsupported schema_version")
    if row.get("requested_source_root") != SIFTS_SOURCE_ROOT:
        raise BioLipSiftsFetchError(f"line {line_number}: unexpected requested_source_root")
    if row.get("requested_artifact_kind") != "PDBe_SIFTS_RESIDUE_LEVEL_XML_GZIP":
        raise BioLipSiftsFetchError(f"line {line_number}: unexpected requested_artifact_kind")
    if row.get("fetch_manifest_required") is not True:
        raise BioLipSiftsFetchError(f"line {line_number}: fetch manifest is not required")
    if row.get("network_action_performed") is not False:
        raise BioLipSiftsFetchError(f"line {line_number}: stage already claims a network action")
    pdb_id = row.get("pdb_id")
    if not isinstance(pdb_id, str) or PDB_RE.fullmatch(pdb_id) is None:
        raise BioLipSiftsFetchError(f"line {line_number}: invalid PDB id {pdb_id!r}")
    if row.get("structure_id") != f"PDB:{pdb_id}":
        raise BioLipSiftsFetchError(f"line {line_number}: structure_id/PDB mismatch")
    if row.get("requested_relative_path") != f"{pdb_id}.xml.gz":
        raise BioLipSiftsFetchError(f"line {line_number}: requested path/PDB mismatch")


def load_stage_requests(path: Path) -> StageRequests:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BioLipSiftsFetchError(f"cannot read BioLiP stage {path}: {exc}") from exc

    requests: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        if not line.strip():
            raise BioLipSiftsFetchError(f"line {line_number}: blank rows are not allowed")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BioLipSiftsFetchError(f"line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise BioLipSiftsFetchError(f"line {line_number}: row is not an object")
        if line != (canonical_json(row) + "\n").encode("utf-8"):
            raise BioLipSiftsFetchError(f"line {line_number}: row is not canonical JSONL")
        kind = row.get("kind")
        if kind == FETCH_REQUEST_KIND:
            _validate_fetch_request(row, line_number=line_number)
            requests.append(row)
        elif kind == SUMMARY_KIND:
            if summary is not None:
                raise BioLipSiftsFetchError("BioLiP stage contains multiple summary rows")
            summary = row

    if not requests:
        raise BioLipSiftsFetchError("BioLiP stage contains no SIFTS fetch requests")
    if summary is None:
        raise BioLipSiftsFetchError("BioLiP stage summary is missing")

    requests = sorted(requests, key=lambda row: row["pdb_id"])
    pdb_ids = [row["pdb_id"] for row in requests]
    if len(set(pdb_ids)) != len(pdb_ids):
        raise BioLipSiftsFetchError("BioLiP stage contains duplicate PDB fetch requests")
    if summary.get("residue_level_sifts_fetch_request_count") != len(requests):
        raise BioLipSiftsFetchError("BioLiP summary fetch request count does not match rows")
    if summary.get("residue_level_sifts_requested_pdb_ids_sha256") != value_sha256(pdb_ids):
        raise BioLipSiftsFetchError("BioLiP summary PDB digest does not match rows")

    return StageRequests(
        stage_sha256=hashlib.sha256(raw).hexdigest(),
        stage_id=str(summary.get("stage_id")),
        combined_non_summary_rows_sha256=str(summary.get("combined_non_summary_rows_sha256")),
        requests=tuple(requests),
    )


def _manifest_contract(
    *, snapshot_id: str, stage_path: Path, stage: StageRequests
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "BIOLIP_RESIDUE_LEVEL_SIFTS_SNAPSHOT",
        "snapshot_id": snapshot_id,
        "source": "PDBe SIFTS residue-level XML",
        "source_root": SIFTS_SOURCE_ROOT,
        "stage_path": _display_path(stage_path),
        "stage_sha256": stage.stage_sha256,
        "stage_id": stage.stage_id,
        "stage_combined_non_summary_rows_sha256": stage.combined_non_summary_rows_sha256,
        "fetch_request_count": len(stage.requests),
        "fetch_request_ids_sha256": value_sha256(stage.request_ids),
        "requested_pdb_count": len(stage.pdb_ids),
        "requested_pdb_ids_sha256": value_sha256(stage.pdb_ids),
    }


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _manifest_entry(entry: ecod_sifts.SiftsEntry, *, path: Path) -> dict[str, Any]:
    return {
        "pdb_id": entry.pdb_id,
        "path": path.name,
        "sha256": entry.xml_sha256,
        "size_bytes": path.stat().st_size,
        "sifts_entry_date": entry.entry_date,
        "sifts_uniprot_release": entry.uniprot_release,
        "sifts_uniprot_version": entry.uniprot_version,
        "url": f"{SIFTS_SOURCE_ROOT}/{entry.pdb_id}.xml.gz",
    }


def _validate_entry(entry: Mapping[str, Any]) -> None:
    if set(entry) != ENTRY_FIELDS:
        raise BioLipSiftsFetchError("SIFTS manifest entry fields mismatch")
    pdb_id = entry.get("pdb_id")
    if not isinstance(pdb_id, str) or PDB_RE.fullmatch(pdb_id) is None:
        raise BioLipSiftsFetchError("SIFTS manifest entry has invalid PDB ID")
    if entry.get("path") != f"{pdb_id}.xml.gz":
        raise BioLipSiftsFetchError("SIFTS manifest entry path/PDB mismatch")
    if entry.get("url") != f"{SIFTS_SOURCE_ROOT}/{pdb_id}.xml.gz":
        raise BioLipSiftsFetchError("SIFTS manifest entry URL mismatch")
    if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] <= 0:
        raise BioLipSiftsFetchError("SIFTS manifest entry size is invalid")
    if not isinstance(entry.get("sha256"), str) or not re.fullmatch(
        r"^[0-9a-f]{64}$", entry["sha256"]
    ):
        raise BioLipSiftsFetchError("SIFTS manifest entry SHA-256 is invalid")


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        manifest = json.loads(raw)
    except OSError as exc:
        raise BioLipSiftsFetchError(f"cannot read SIFTS manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BioLipSiftsFetchError(f"invalid SIFTS manifest {path}: {exc}") from exc
    if raw != (canonical_json(manifest) + "\n").encode("utf-8"):
        raise BioLipSiftsFetchError(f"SIFTS manifest is not canonical JSON: {path}")
    return manifest


def _validate_manifest(
    manifest: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    requested_pdb_ids: set[str],
) -> None:
    if set(manifest) != MANIFEST_FIELDS:
        raise BioLipSiftsFetchError("SIFTS manifest fields mismatch")
    for key, value in contract.items():
        if manifest.get(key) != value:
            raise BioLipSiftsFetchError(
                f"SIFTS manifest contract mismatch for {key}: {manifest.get(key)!r} != {value!r}"
            )
    entries = manifest.get("entries")
    failures = manifest.get("failures")
    if not isinstance(entries, list) or not isinstance(failures, list):
        raise BioLipSiftsFetchError("SIFTS manifest entries/failures must be lists")
    if any(not isinstance(item, dict) for item in entries):
        raise BioLipSiftsFetchError("SIFTS manifest entry is not an object")
    if any(not isinstance(item, dict) for item in failures):
        raise BioLipSiftsFetchError("SIFTS manifest failure is malformed")
    if [item.get("pdb_id") for item in entries] != sorted(item.get("pdb_id") for item in entries):
        raise BioLipSiftsFetchError("SIFTS manifest entries are not sorted")
    if [item.get("pdb_id") for item in failures] != sorted(item.get("pdb_id") for item in failures):
        raise BioLipSiftsFetchError("SIFTS manifest failures are not sorted")

    entry_ids = set()
    for entry in entries:
        _validate_entry(entry)
        entry_ids.add(entry["pdb_id"])
    failure_ids = set()
    for failure in failures:
        if not isinstance(failure, dict) or set(failure) != {"pdb_id", "error"}:
            raise BioLipSiftsFetchError("SIFTS manifest failure is malformed")
        pdb_id = failure["pdb_id"]
        if not isinstance(pdb_id, str) or not isinstance(failure["error"], str):
            raise BioLipSiftsFetchError("SIFTS manifest failure is malformed")
        failure_ids.add(pdb_id)
    if entry_ids & failure_ids:
        raise BioLipSiftsFetchError("SIFTS manifest has conflicting entries/failures")
    if not entry_ids <= requested_pdb_ids or not failure_ids <= requested_pdb_ids:
        raise BioLipSiftsFetchError("SIFTS manifest contains unrequested PDB IDs")
    complete = manifest.get("complete")
    if type(complete) is not bool:
        raise BioLipSiftsFetchError("SIFTS manifest complete flag is invalid")
    if complete and (failure_ids or entry_ids != requested_pdb_ids):
        raise BioLipSiftsFetchError("completed SIFTS manifest is incomplete")


def _write_manifest(
    path: Path,
    contract: Mapping[str, Any],
    entries: Mapping[str, Mapping[str, Any]],
    failures: Mapping[str, str],
) -> dict[str, Any]:
    manifest = {
        **contract,
        "entries": [entries[pdb_id] for pdb_id in sorted(entries)],
        "failures": [{"pdb_id": pdb_id, "error": failures[pdb_id]} for pdb_id in sorted(failures)],
        "complete": len(entries) == contract["requested_pdb_count"] and not failures,
    }
    _atomic_write(path, canonical_json(manifest) + "\n")
    return manifest


def _validate_xml_against_entry(path: Path, entry: Mapping[str, Any]) -> None:
    _validate_entry(entry)
    try:
        parsed = ecod_sifts.load_sifts_xml(path)
    except ecod_sifts.EcodSiftsError as exc:
        raise BioLipSiftsFetchError(str(exc)) from exc
    actual = _manifest_entry(parsed, path=path)
    if actual != dict(entry):
        raise BioLipSiftsFetchError(f"SIFTS XML does not match manifest entry: {path}")


def _fetch_one(url: str, target: Path, *, timeout: int) -> ecod_sifts.SiftsEntry:
    descriptor = -1
    temporary: Path | None = None
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ProteinTraitsMech/1.0"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.stem}.", suffix=".xml.gz", dir=target.parent
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        parsed = ecod_sifts.load_sifts_xml(temporary)
        os.replace(temporary, target)
        temporary = None
        return parsed
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _verify_completed(
    snapshot_dir: Path,
    entries: Mapping[str, Mapping[str, Any]],
    pdb_ids: Sequence[str],
) -> None:
    for pdb_id in pdb_ids:
        entry = entries[pdb_id]
        target = snapshot_dir / entry["path"]
        if not target.is_file():
            raise BioLipSiftsFetchError(f"completed SIFTS snapshot is missing {target}")
        _validate_xml_against_entry(target, entry)


def fetch(args: argparse.Namespace) -> int:
    snapshot_id = _validate_snapshot_id(args.snapshot_id)
    _reject_protected_target(args.snapshot_dir, label="SIFTS snapshot root")
    snapshot_dir = args.snapshot_dir / snapshot_id
    _reject_protected_target(snapshot_dir, label="SIFTS snapshot path")

    stage = load_stage_requests(args.stage)
    pdb_ids = stage.pdb_ids[: args.limit] if args.limit is not None else stage.pdb_ids
    if not pdb_ids:
        raise BioLipSiftsFetchError("requested PDB set is empty")
    wanted_pdb_ids = set(pdb_ids)
    limited_stage = StageRequests(
        stage_sha256=stage.stage_sha256,
        stage_id=stage.stage_id,
        combined_non_summary_rows_sha256=stage.combined_non_summary_rows_sha256,
        requests=tuple(row for row in stage.requests if row["pdb_id"] in wanted_pdb_ids),
    )
    contract = _manifest_contract(
        snapshot_id=snapshot_id,
        stage_path=args.stage,
        stage=limited_stage,
    )

    print(f"BioLiP: plan {len(pdb_ids):,} residue-level SIFTS XML file(s) under {snapshot_dir}")
    if not args.apply:
        print("dry-run; no files written (pass --apply to fetch)")
        for pdb_id in pdb_ids[:5]:
            print(f"  {SIFTS_SOURCE_ROOT}/{pdb_id}.xml.gz")
        return 0

    if snapshot_dir.exists() and not snapshot_dir.is_dir():
        raise BioLipSiftsFetchError(f"SIFTS snapshot path is not a directory: {snapshot_dir}")
    manifest_path = snapshot_dir / MANIFEST_NAME
    if manifest_path.is_file():
        manifest = _load_manifest(manifest_path)
        _validate_manifest(
            manifest,
            contract=contract,
            requested_pdb_ids=set(pdb_ids),
        )
    else:
        try:
            existing = list(snapshot_dir.iterdir()) if snapshot_dir.is_dir() else []
        except OSError as exc:
            raise BioLipSiftsFetchError(f"cannot inspect {snapshot_dir}: {exc}") from exc
        if existing:
            raise BioLipSiftsFetchError(f"refusing unmanifested files in {snapshot_dir}")
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        manifest = _write_manifest(manifest_path, contract, {}, {})

    entries = {item["pdb_id"]: item for item in manifest["entries"]}
    failures = {item["pdb_id"]: item["error"] for item in manifest["failures"]}
    if manifest["complete"]:
        _verify_completed(snapshot_dir, entries, pdb_ids)
        print(f"fetched/verified={len(entries):,}; failures=0 (immutable snapshot)")
        return 0

    for number, pdb_id in enumerate(pdb_ids, 1):
        target = snapshot_dir / f"{pdb_id}.xml.gz"
        url = f"{SIFTS_SOURCE_ROOT}/{pdb_id}.xml.gz"
        existing_entry = entries.get(pdb_id)
        if existing_entry is not None:
            if not target.is_file():
                raise BioLipSiftsFetchError(f"manifest-bound SIFTS file is missing: {target}")
            _validate_xml_against_entry(target, existing_entry)
            failures.pop(pdb_id, None)
            _write_manifest(manifest_path, contract, entries, failures)
            continue

        try:
            if target.is_file():
                parsed = ecod_sifts.load_sifts_xml(target)
                if parsed.pdb_id != pdb_id:
                    raise BioLipSiftsFetchError(
                        f"existing file contains PDB {parsed.pdb_id}, expected {pdb_id}"
                    )
                entries[pdb_id] = _manifest_entry(parsed, path=target)
            else:
                parsed = _fetch_one(url, target, timeout=args.timeout)
                if parsed.pdb_id != pdb_id:
                    raise BioLipSiftsFetchError(
                        f"downloaded PDB {parsed.pdb_id}, expected {pdb_id}"
                    )
                entries[pdb_id] = _manifest_entry(parsed, path=target)
            failures.pop(pdb_id, None)
        except (
            OSError,
            urllib.error.URLError,
            BioLipSiftsFetchError,
            ecod_sifts.EcodSiftsError,
        ) as exc:
            failures[pdb_id] = str(exc)
        _write_manifest(manifest_path, contract, entries, failures)
        if number % 100 == 0:
            print(f"  checked {number:,}/{len(pdb_ids):,}")

    manifest = _write_manifest(manifest_path, contract, entries, failures)
    print(f"fetched/verified={len(entries):,}; failures={len(failures):,}")
    if manifest["complete"]:
        print(f"immutable manifest: {manifest_path}")
    return 1 if failures else 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, default=DEFAULT_STAGE)
    ap.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    ap.add_argument("--snapshot-id", required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--apply", action="store_true")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        print("refusing to fetch BioLiP SIFTS XML: --limit must be positive", file=sys.stderr)
        return 2
    try:
        return fetch(args)
    except BioLipSiftsFetchError as exc:
        print(f"refusing to fetch BioLiP SIFTS XML: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
