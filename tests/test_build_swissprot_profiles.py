"""Offline acquisition contracts: frozen inputs, release consistency and completeness."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from email.message import Message
from pathlib import Path
from urllib.parse import urlencode

import pytest
import yaml

SPEC = importlib.util.spec_from_file_location(
    "build_swissprot_profiles", Path(__file__).resolve().parents[1] / "scripts/build_swissprot_profiles.py"
)
assert SPEC and SPEC.loader
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
INDEX = {"CDD:cd01049": ["SEQUENCE", "SEQ_DOMAIN"]}
QUERY = "organism_id:9606"


def entry(acc="P12345", *, reviewed=True):
    return {
        "primaryAccession": acc,
        "entryType": "UniProtKB reviewed (Swiss-Prot)" if reviewed else "UniProtKB unreviewed (TrEMBL)",
        "proteinDescription": {"recommendedName": {"fullName": {"value": "A protein"}}},
        "organism": {"taxonId": 9606, "scientificName": "Homo sapiens"},
        "sequence": {"length": 100},
        "uniProtKBCrossReferences": [{"database": "CDD", "id": "cd01049"}],
    }


def page(entries, *, total=None, release="2026_03", next_url=None):
    body = {"results": entries}
    return body, {
        "sha256": hashlib.sha256(json.dumps(body).encode()).hexdigest(),
        "release": release, "total": str(len(entries) if total is None else total),
        "link": f'<{next_url}>; rel="next"' if next_url else "",
    }


def next_link(query=QUERY, cursor="next"):
    return F.SEARCH_URL + "?" + urlencode({"query": query, "cursor": cursor})


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("offline test attempted network access")
    monkeypatch.setattr(F.urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(F.time, "sleep", lambda _: None)


def mock_pages(monkeypatch, pages):
    pending = iter(pages)
    calls = []

    def get(url):
        calls.append(url)
        value = next(pending)
        if isinstance(value, Exception):
            raise value
        body, meta = value
        return body, {**meta, "url": url}

    monkeypatch.setattr(F, "_get", get)
    return calls


def test_complete_pagination(monkeypatch):
    calls = mock_pages(monkeypatch, [
        page([entry()], total=2, next_url=next_link()), page([entry("Q54321")], total=2)
    ])
    receipt = {}
    assert len(list(F.stream_swissprot(QUERY, 0, receipt=receipt))) == 2
    assert receipt["complete"] and receipt["returned_rows"] == receipt["total"] == 2
    assert len(receipt["pages"]) == len(calls) == 2
    assert receipt["release"] == "2026_03"
    assert "xref_prints" in calls[0]


@pytest.mark.parametrize("key,value,match", [
    ("release", None, "release header"), ("release", "bad", "release header"),
    ("release", "2026_02", "release changed"), ("total", None, "total-results header"),
    ("total", "-1", "total-results header"), ("total", "many", "total-results header"),
])
def test_reject_bad_headers(monkeypatch, key, value, match):
    body, meta = page([entry()])
    meta[key] = value
    mock_pages(monkeypatch, [(body, meta)])
    with pytest.raises(F.AcquisitionError, match=match):
        list(F.stream_swissprot(QUERY, 5, expect_release="2026_03"))


@pytest.mark.parametrize("second,match", [
    (page([entry("Q54321")], total=2, release="2026_04"), "release changed"),
    (page([entry("Q54321")], total=3), "total-results changed"),
    (page([], total=2), "empty page"),
    (page([entry()], total=2), "duplicate accession"),
])
def test_page_drift(monkeypatch, second, match):
    mock_pages(monkeypatch, [page([entry()], total=2, next_url=next_link()), second])
    with pytest.raises(F.AcquisitionError, match=match):
        list(F.stream_swissprot(QUERY, 5))


@pytest.mark.parametrize("response,match", [
    (page([entry()], total=2), "pagination ended"),
    (page([entry()], next_url=next_link()), "after advertised total"),
    (page([entry(), entry("Q54321")], total=1), "more entries"),
    (page([entry("../../bad")]), "invalid accession"),
    (page([entry()], total=2, next_url="https://evil.example/?query=x"), "changed origin"),
    (page([entry()], total=2, next_url=next_link("wrong query")), "changed origin"),
])
def test_invalid_pagination(monkeypatch, response, match):
    mock_pages(monkeypatch, [response])
    with pytest.raises(F.AcquisitionError, match=match):
        list(F.stream_swissprot(QUERY, 5))


def test_repeated_page_url(monkeypatch):
    mock_pages(monkeypatch, [
        page([entry()], total=3, next_url=next_link()),
        page([entry("Q54321")], total=3, next_url=next_link()),
    ])
    with pytest.raises(F.AcquisitionError, match="repeated pagination URL"):
        list(F.stream_swissprot(QUERY, 5))


def test_explicit_cap_is_incomplete(monkeypatch):
    calls = mock_pages(monkeypatch, [page([entry()], total=2, next_url=next_link())])
    stats = {}
    assert len(list(F.stream_swissprot(QUERY, 1, receipt=stats))) == 1
    assert not stats["complete"] and stats["returned_rows"] == 1 and stats["total"] == 2
    assert len(calls) == 1


def test_require_complete_rejects_cap_before_yield(monkeypatch):
    mock_pages(monkeypatch, [page([entry()], total=2, next_url=next_link())])
    with pytest.raises(F.AcquisitionError, match="exceeding complete-query limit"):
        next(F.stream_swissprot(QUERY, 1, require_complete=True))


def test_zero_results(monkeypatch):
    mock_pages(monkeypatch, [page([])])
    stats = {}
    assert list(F.stream_swissprot(QUERY, 0, receipt=stats)) == []
    assert stats["complete"] and stats["total"] == 0


def test_fetch_hash_and_case_insensitive_headers(monkeypatch):
    body = json.dumps({"results": [entry()]}).encode()
    headers = Message()
    headers["X-UniProt-Release"] = "2026_03"
    headers["X-Total-Results"] = "1"

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return body

    Response.headers = headers
    monkeypatch.setattr(F.urllib.request, "urlopen", lambda *a, **kw: Response())
    data, meta = F._get(F.SEARCH_URL)
    assert data["results"][0]["primaryAccession"] == "P12345"
    assert meta["sha256"] == hashlib.sha256(body).hexdigest()
    assert meta["release"] == "2026_03" and meta["total"] == "1"


def test_fetch_exhaustion_raises(monkeypatch):
    def failed(*args, **kwargs):
        raise OSError("connection closed")
    monkeypatch.setattr(F.urllib.request, "urlopen", failed)
    with pytest.raises(F.AcquisitionError, match="connection closed"):
        F._get(F.SEARCH_URL, tries=2)


@pytest.mark.parametrize("name", ["yes", "null", "a\nb", 'a"b', "x: β", "001"])
def test_yaml_strings_round_trip(name):
    e = entry(reviewed=False)
    e["proteinDescription"] = {"submissionNames": [{"fullName": {"value": name}}]}
    p = F.profile(e, INDEX)
    assert p["protein_name"] == name
    assert not p["reviewed"] and "TrEMBL" in p["profile_source"]
    assert yaml.safe_load(F.to_yaml(p))["protein_name"] == name
    assert F.matrix_row(p)["traits"] == ["CDD:cd01049"]


@pytest.mark.parametrize("key,value", [
    ("primaryAccession", "../bad"), ("entryType", "unknown"), ("organism", {}),
    ("sequence", {"length": 0}), ("sequence", {"length": True}),
])
def test_invalid_profile_metadata(key, value):
    e = entry()
    e[key] = value
    with pytest.raises(F.AcquisitionError):
        F.profile(e, INDEX)


@pytest.fixture
def acquisition(tmp_path):
    cache = tmp_path / "frozen-index.json"
    cache.write_text(json.dumps(INDEX))
    out = tmp_path / "new-bundle"
    return cache, out, ["--query", QUERY, "--index-cache", str(cache), "--out-dir", str(out)]


@pytest.mark.parametrize("jsonl_only", [False, True])
def test_publish_bundle(monkeypatch, acquisition, jsonl_only):
    cache, out, args = acquisition
    original = cache.read_bytes()
    mock_pages(monkeypatch, [page([entry()])])
    assert F.main(args + ["--apply"] + (["--jsonl-only"] if jsonl_only else [])) == 0
    receipt = json.loads((out / "acquisition.json").read_text())
    assert receipt["complete"] and receipt["profiles"] == 1
    assert receipt["profiles_sha256"] == hashlib.sha256((out / "profiles.jsonl").read_bytes()).hexdigest()
    assert receipt["trait_index_sha256"] == hashlib.sha256((out / "trait_index.json").read_bytes()).hexdigest()
    assert (out / "P12345.yaml").exists() != jsonl_only
    assert cache.read_bytes() == original
    assert not list(out.parent.glob(".protein-profiles-*"))


@pytest.mark.parametrize("kind", ["directory", "file", "dangling-symlink"])
def test_existing_output_refused_before_fetch(monkeypatch, acquisition, kind):
    _, out, args = acquisition
    if kind == "directory":
        out.mkdir()
        (out / "profiles.jsonl").write_text("frozen")
    elif kind == "file":
        out.write_text("frozen")
    else:
        out.symlink_to(out.parent / "absent")
    calls = mock_pages(monkeypatch, [])
    with pytest.raises(SystemExit):
        F.main(args + ["--apply"])
    assert not calls
    if kind == "directory":
        assert (out / "profiles.jsonl").read_text() == "frozen"
    elif kind == "file":
        assert out.read_text() == "frozen"
    else:
        assert out.is_symlink()


def test_mid_fetch_failure_does_not_publish(monkeypatch, acquisition):
    cache, out, args = acquisition
    original = cache.read_bytes()
    mock_pages(monkeypatch, [
        page([entry()], total=2, next_url=next_link()), F.AcquisitionError("offline")
    ])
    assert F.main(args + ["--apply"]) == 2
    assert not out.exists() and cache.read_bytes() == original
    assert not list(out.parent.glob(".protein-profiles-*"))


def test_output_appearing_during_fetch_is_preserved(monkeypatch, acquisition):
    _, out, args = acquisition
    def get(url):
        out.mkdir()
        (out / "sentinel").write_text("concurrent writer")
        return page([entry()])
    monkeypatch.setattr(F, "_get", get)
    assert F.main(args + ["--apply"]) == 2
    assert [p.name for p in out.iterdir()] == ["sentinel"]


@pytest.mark.parametrize("conflict", [False, True])
def test_query_overlap(monkeypatch, acquisition, conflict):
    _, out, args = acquisition
    second = entry()
    if conflict:
        second["sequence"]["length"] = 99
    mock_pages(monkeypatch, [page([entry()]), page([second])])
    result = F.main(args + ["--query", "other query", "--apply"])
    assert result == (2 if conflict else 0)
    assert out.exists() != conflict
    if not conflict:
        receipt = json.loads((out / "acquisition.json").read_text())
        assert receipt["profiles"] == 1
        assert [q["new_profiles"] for q in receipt["queries"]] == [1, 0]


def test_cross_query_release_drift(monkeypatch, acquisition):
    _, out, args = acquisition
    mock_pages(monkeypatch, [page([]), page([], release="2026_04")])
    assert F.main(args + ["--query", "other", "--apply"]) == 2
    assert not out.exists()


def test_dry_run_never_writes_even_without_index(monkeypatch, tmp_path):
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "trait.yaml").write_text("identifier: CDD:cd01049\ntrait_axis: SEQUENCE\ntrait_category: SEQ_DOMAIN\n")
    monkeypatch.setattr(F, "TRAITS", traits)
    cache, out = tmp_path / "cache" / "index.json", tmp_path / "out" / "bundle"
    mock_pages(monkeypatch, [page([entry()])])
    assert F.main(["--index-cache", str(cache), "--out-dir", str(out)]) == 0
    assert not cache.parent.exists() and not out.parent.exists()


def test_corrupt_cache_rejected_not_overwritten(tmp_path, monkeypatch):
    cache = tmp_path / "cache.json"
    cache.write_text("bad")
    monkeypatch.setattr(F, "TRAITS", tmp_path / "empty")
    with pytest.raises(F.AcquisitionError, match="refresh-index"):
        F.build_trait_index(cache=cache)
    assert F.build_trait_index(refresh=True, cache=cache) == {}
    assert cache.read_text() == "bad"


@pytest.mark.parametrize("args", [["--limit", "-1"], ["--expect-release", "latest"]])
def test_invalid_cli_options(args):
    with pytest.raises(SystemExit):
        F.main(args)
