"""Fetch BioLiP residue-level SIFTS XML fail-closed."""

from __future__ import annotations

import gzip
import importlib
import sys
import urllib.error
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
fetcher = importlib.import_module("fetch_biolip_residue_sifts")


def _canonical_request(pdb_id: str = "1c1e") -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": fetcher.SCHEMA_VERSION,
        "kind": fetcher.FETCH_REQUEST_KIND,
        "stage_status": "RESIDUE_LEVEL_SIFTS_FETCH_REQUIRED",
        "qualification_claimed": False,
        "network_action_performed": False,
        "structure_id": f"PDB:{pdb_id}",
        "pdb_id": pdb_id,
        "requested_artifact_kind": "PDBe_SIFTS_RESIDUE_LEVEL_XML_GZIP",
        "requested_source_root": fetcher.SIFTS_SOURCE_ROOT,
        "requested_relative_path": f"{pdb_id}.xml.gz",
        "fetch_manifest_required": True,
        "required_fetch_manifest_semantics": (
            "COMPLETE_CANONICAL_CONTENT_ADDRESSED_MANIFEST_BINDING_EVERY_REQUESTED_FILE"
        ),
        "source_occurrence_count": 1,
        "source_occurrence_ids": ["biolip-missing-protein-source-occurrence:fixture"],
        "source_occurrence_ids_sha256": fetcher.value_sha256(
            ["biolip-missing-protein-source-occurrence:fixture"]
        ),
        "source_line_and_trait_bindings": [],
        "source_line_and_trait_bindings_sha256": fetcher.value_sha256([]),
        "artifact_bindings": [],
    }
    prefix = "biolip-residue-sifts-fetch-request:"
    row["fetch_request_id"] = prefix + fetcher.value_sha256(row)
    row["fetch_request_row_sha256"] = fetcher.value_sha256(row)
    return row


def _summary(requests: list[dict[str, Any]]) -> dict[str, Any]:
    pdb_ids = sorted(row["pdb_id"] for row in requests)
    return {
        "schema_version": fetcher.SCHEMA_VERSION,
        "kind": fetcher.SUMMARY_KIND,
        "stage_id": "biolip-missing-protein-stage:fixture",
        "combined_non_summary_rows_sha256": fetcher.value_sha256(requests),
        "residue_level_sifts_fetch_request_count": len(requests),
        "residue_level_sifts_requested_pdb_ids_sha256": fetcher.value_sha256(pdb_ids),
    }


def _write_stage(path: Path, *requests: dict[str, Any]) -> None:
    rows = [*requests, _summary(list(requests))]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(fetcher.canonical_json(row) + "\n" for row in rows))


def _sifts_xml(pdb_id: str = "1c1e") -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd"
       xmlns:dc="http://purl.org/dc/elements/1.1/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       dbSource="PDBe"
       dbCoordSys="PDBe"
       dbAccessionId="{pdb_id}"
       date="2026-09-02">
  <listDB>
    <db dbSource="UniProt" dbVersion="2026.03"/>
  </listDB>
  <dc:rights rdf:resource="http://pdbe.org/sifts">PDBe SIFTS terms</dc:rights>
</entry>
""".encode()


class _Response:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def test_dry_run_plans_without_writing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stage = tmp_path / "biolip-stage.jsonl"
    snapshot_dir = tmp_path / "snapshots"
    _write_stage(stage, _canonical_request())

    result = fetcher.main(
        [
            "--stage",
            str(stage),
            "--snapshot-dir",
            str(snapshot_dir),
            "--snapshot-id",
            "fixture-2026-09-24",
        ]
    )

    assert result == 0
    assert not snapshot_dir.exists()
    out = capsys.readouterr().out
    assert "dry-run; no files written" in out
    assert f"{fetcher.SIFTS_SOURCE_ROOT}/1c1e.xml.gz" in out


def test_apply_fetches_canonical_manifest_and_is_immutable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stage = tmp_path / "biolip-stage.jsonl"
    snapshot_dir = tmp_path / "snapshots"
    _write_stage(stage, _canonical_request())
    payload = gzip.compress(_sifts_xml())
    hits = 0

    def urlopen(request: Any, *, timeout: int) -> _Response:
        nonlocal hits
        hits += 1
        assert request.full_url == f"{fetcher.SIFTS_SOURCE_ROOT}/1c1e.xml.gz"
        assert timeout == 7
        return _Response(payload)

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", urlopen)
    args = [
        "--stage",
        str(stage),
        "--snapshot-dir",
        str(snapshot_dir),
        "--snapshot-id",
        "fixture-2026-09-24",
        "--timeout",
        "7",
        "--apply",
    ]

    assert fetcher.main(args) == 0
    manifest_path = snapshot_dir / "fixture-2026-09-24" / fetcher.MANIFEST_NAME
    manifest = fetcher._load_manifest(manifest_path)
    assert manifest["complete"] is True
    assert manifest["failures"] == []
    assert manifest["entries"][0]["pdb_id"] == "1c1e"
    assert manifest_path.read_text() == fetcher.canonical_json(manifest) + "\n"

    def no_network(*_args: Any, **_kwargs: Any) -> _Response:
        raise AssertionError("completed snapshot should verify offline")

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", no_network)
    assert fetcher.main(args) == 0
    assert hits == 1


def test_manifest_bound_xml_corruption_fails_without_rewriting_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stage = tmp_path / "biolip-stage.jsonl"
    snapshot_dir = tmp_path / "snapshots"
    _write_stage(stage, _canonical_request("1c1e"), _canonical_request("2def"))
    first_payload = gzip.compress(_sifts_xml("1c1e"))

    def first_urlopen(request: Any, *, timeout: int) -> _Response:
        del timeout
        if request.full_url == f"{fetcher.SIFTS_SOURCE_ROOT}/1c1e.xml.gz":
            return _Response(first_payload)
        raise urllib.error.URLError("transient 2def failure")

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", first_urlopen)
    args = [
        "--stage",
        str(stage),
        "--snapshot-dir",
        str(snapshot_dir),
        "--snapshot-id",
        "fixture-2026-09-24",
        "--apply",
    ]

    assert fetcher.main(args) == 1
    manifest_path = snapshot_dir / "fixture-2026-09-24" / fetcher.MANIFEST_NAME
    manifest_before = fetcher._load_manifest(manifest_path)
    assert [entry["pdb_id"] for entry in manifest_before["entries"]] == ["1c1e"]
    assert [failure["pdb_id"] for failure in manifest_before["failures"]] == ["2def"]

    target = manifest_path.parent / "1c1e.xml.gz"
    target.write_bytes(gzip.compress(b"not SIFTS XML"))

    def no_network(*_args: Any, **_kwargs: Any) -> _Response:
        raise AssertionError("manifest-bound corruption must fail before retrying failures")

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", no_network)
    assert fetcher.main(args) == 2
    assert fetcher._load_manifest(manifest_path) == manifest_before


def test_duplicate_manifest_pdb_rows_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stage = tmp_path / "biolip-stage.jsonl"
    snapshot_dir = tmp_path / "snapshots"
    _write_stage(stage, _canonical_request())
    payload = gzip.compress(_sifts_xml())

    def urlopen(_request: Any, *, timeout: int) -> _Response:
        del timeout
        return _Response(payload)

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", urlopen)
    args = [
        "--stage",
        str(stage),
        "--snapshot-dir",
        str(snapshot_dir),
        "--snapshot-id",
        "fixture-2026-09-24",
        "--apply",
    ]

    assert fetcher.main(args) == 0
    manifest_path = snapshot_dir / "fixture-2026-09-24" / fetcher.MANIFEST_NAME
    manifest = fetcher._load_manifest(manifest_path)
    manifest["complete"] = False
    manifest["entries"].append(dict(manifest["entries"][0]))
    manifest_path.write_text(fetcher.canonical_json(manifest) + "\n")
    assert fetcher.main(args) == 2

    manifest["entries"] = []
    manifest["failures"] = [
        {"pdb_id": "1c1e", "error": "first"},
        {"pdb_id": "1c1e", "error": "second"},
    ]
    manifest_path.write_text(fetcher.canonical_json(manifest) + "\n")
    assert fetcher.main(args) == 2


def test_wrong_stage_source_root_fails_closed(tmp_path: Path) -> None:
    request = _canonical_request()
    request["requested_source_root"] = (
        "https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml_remediated"
    )
    base = {
        k: v
        for k, v in request.items()
        if k not in {"fetch_request_id", "fetch_request_row_sha256"}
    }
    request["fetch_request_id"] = "biolip-residue-sifts-fetch-request:" + fetcher.value_sha256(base)
    request["fetch_request_row_sha256"] = fetcher.value_sha256(
        {k: v for k, v in request.items() if k != "fetch_request_row_sha256"}
    )
    stage = tmp_path / "stage.jsonl"
    _write_stage(stage, request)

    with pytest.raises(fetcher.BioLipSiftsFetchError, match="requested_source_root"):
        fetcher.load_stage_requests(stage)


def test_noncanonical_stage_jsonl_fails_closed(tmp_path: Path) -> None:
    request = _canonical_request()
    stage = tmp_path / "stage.jsonl"
    stage.write_text(fetcher.canonical_json(request) + "\n{}\n")

    with pytest.raises(fetcher.BioLipSiftsFetchError, match="summary"):
        fetcher.load_stage_requests(stage)
