"""Offline boundary tests: research acquisition is not grounding promotion."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_slc10_pilot as pilot


def test_registered_panel():
    rows = pilot.sources()
    assert len(rows) == 13
    assert len({r["url"] for r in rows}) == 13


def test_dry_run_never_requests_or_creates(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "ROOT", tmp_path)
    monkeypatch.setattr(pilot, "RAW", tmp_path / "data/raw/slc10")
    monkeypatch.setattr(pilot, "sources", lambda: [])
    monkeypatch.setattr(pilot.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network"))
    result = pilot.acquire("test", "2026_03")
    assert result["qualification"] == "NONE_RESEARCH_INPUTS_ONLY"
    assert not pilot.RAW.exists()


@pytest.mark.parametrize("name", ["../escape", "/tmp/example", "", "has space"])
def test_bad_snapshot_names(name):
    with pytest.raises(ValueError):
        pilot.acquire(name, "2026_03")


class Response:
    status = 200
    headers = {"X-UniProt-Release": "2026_03"}

    def __init__(self, accession="Q14973"):
        self.raw = json.dumps({"primaryAccession": accession,
                               "sequence": {"value": "ACD", "length": 3},
                               "entryAudit": {"sequenceVersion": 1}}).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.raw[:limit]

    def geturl(self):
        return "https://rest.uniprot.org/uniprotkb/Q14973.json"


@pytest.mark.parametrize("release,accession", [("2026_02", "Q14973"), ("2026_03", "Q96EP9")])
def test_wrong_release_or_accession_fails(monkeypatch, release, accession):
    monkeypatch.setattr(pilot.urllib.request, "urlopen", lambda *a, **k: Response(accession))
    with pytest.raises(ValueError):
        pilot.uniprot_response("Q14973", release)


def test_retains_exact_response_hash(monkeypatch):
    monkeypatch.setattr(pilot.urllib.request, "urlopen", lambda *a, **k: Response())
    raw, receipt = pilot.uniprot_response("Q14973", "2026_03")
    assert receipt["sha256"] == pilot.hashlib.sha256(raw).hexdigest()
    assert receipt["uniprot_release"] == "2026_03"


def test_partial_acquisition_has_no_completion_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "ROOT", tmp_path)
    monkeypatch.setattr(pilot, "RAW", tmp_path / "data/raw/slc10")
    monkeypatch.setattr(pilot, "sources", lambda: [{"local_name": "Q14973.json"}])
    def fail(*args):
        raise ValueError("source unavailable")
    monkeypatch.setattr(pilot, "uniprot_response", fail)
    with pytest.raises(ValueError, match="source unavailable"):
        pilot.acquire("partial", "2026_03", apply=True)
    assert not (pilot.RAW / "partial/manifest.json").exists()
    with pytest.raises(ValueError, match="existing"):
        pilot.acquire("partial", "2026_03")
