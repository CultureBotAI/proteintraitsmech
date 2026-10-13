"""Completeness stamp of the UniProt residue frame (issue #1070). Offline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "fetch_residue_frame.py"
sys.path.insert(0, str(REPO / "scripts"))
SPEC = importlib.util.spec_from_file_location("fetch_residue_frame", SCRIPT)
assert SPEC and SPEC.loader
R = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = R
SPEC.loader.exec_module(R)

ENTRIES = [
    {"primaryAccession": f"P0000{n}", "sequence": {"value": "MAAA"}, "features": []}
    for n in range(3)
]


def _run(tmp_path, monkeypatch, *extra, total=3, fail=False):
    def get(url, tries=4):
        if fail:
            return None, ""
        return {"results": ENTRIES, "total": total}, ""

    out = tmp_path / "residue.json"
    monkeypatch.setattr(R, "_get", get)
    monkeypatch.setattr(R.time, "sleep", lambda *_: None)
    monkeypatch.setattr(R.sidecar, "uniprot_release", lambda: "2026_03")
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--query", "q", "--out", str(out),
                                    "--apply", *extra])
    return R.main(), out


def _stamp(path):
    return json.loads(path.read_text())["_meta"]["completeness"]


def test_a_query_paginated_to_its_end_is_complete(tmp_path, monkeypatch, capsys):
    status, out = _run(tmp_path, monkeypatch)
    assert status == 0
    stamp = _stamp(out)
    assert stamp["complete"] is True and stamp["queries"] == ["q"]
    assert stamp["truncated_queries"] == [] and stamp["incomplete_queries"] == []
    blob = json.loads(out.read_text())
    assert f"content sha256 {R.sidecar.content_sha256(blob)}" in capsys.readouterr().out


def test_a_limit_canary_is_stamped_incomplete(tmp_path, monkeypatch):
    status, out = _run(tmp_path, monkeypatch, "--limit", "2")
    assert status == 0
    stamp = _stamp(out)
    assert stamp["complete"] is False and stamp["truncated_queries"] == ["q"]
    assert len(json.loads(out.read_text())["proteins"]) == 2


def test_a_cap_equal_to_the_reported_total_is_not_truncation(tmp_path, monkeypatch):
    status, out = _run(tmp_path, monkeypatch, "--limit", "3", total=3)
    assert status == 0 and _stamp(out)["complete"] is True


def test_a_cap_without_a_reported_total_counts_as_truncation(tmp_path, monkeypatch):
    status, out = _run(tmp_path, monkeypatch, "--limit", "3", total=None)
    assert status == 0 and _stamp(out)["complete"] is False


def test_an_aborted_query_written_with_allow_partial_is_incomplete(tmp_path, monkeypatch):
    status, out = _run(tmp_path, monkeypatch, "--allow-partial", fail=True)
    assert status == 0
    stamp = _stamp(out)
    assert stamp["complete"] is False and stamp["incomplete_queries"] == ["q"]


def test_fetch_residue_frame_parser_refuses_abbreviations(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["fetch_residue_frame.py", "--app"])
    with pytest.raises(SystemExit):
        R.main()
