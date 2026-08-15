"""One cached GET-JSON client, and the distinction it exists to make.

`build_sequence_structure_alignment` had the only implementation, embedded, and #445
needed the same thing for the InterPro entry API. Writing a second one is the mistake this
repo documents more than any other -- `interpro_text` counts three copies of one cleaner
that had diverged, `yaml_emit` counts ten of `yaml_escape` and twenty-eight of `slugify`.
So it moved to `scripts/http_cache.py` and both callers share it.

THE DESIGN POINT: a 404 and a timeout are not the same failure. The original cached both
as `null`, with the comment "misses/404s are cached as null so absent mappings aren't
re-fetched". For a 404 that is right. For a timeout it is poisoning -- one flaky minute
becomes a permanent hole indistinguishable from an absent resource.
"""

from __future__ import annotations

import io
import json
import pathlib
import sys
import urllib.error

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from http_cache import Http, TransientHttpError  # noqa: E402


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch(monkeypatch, script):
    """`script` maps url -> payload dict, or an Exception instance to raise."""
    calls = []

    def _open(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else req
        calls.append(url)
        outcome = script[url]
        if isinstance(outcome, Exception):
            raise outcome
        return _Resp(json.dumps(outcome).encode())

    monkeypatch.setattr("http_cache.urllib.request.urlopen", _open)
    return calls


def test_a_hit_does_not_call_the_network(monkeypatch, tmp_path):
    calls = _patch(monkeypatch, {"http://x/u": {"v": 1}})
    http = Http(tmp_path / "c.json", sleep=0)
    assert http.get("http://x/u") == {"v": 1}
    assert http.get("http://x/u") == {"v": 1}
    assert calls == ["http://x/u"], "the second get went to the network"
    assert (http.hits, http.misses) == (1, 1)


def test_a_404_is_cached_as_absent_but_a_TIMEOUT_IS_NOT(monkeypatch, tmp_path):
    """The distinction the module exists for. A 404 means the resource is not there and
    asking again is waste; a timeout means we do not know, and caching it as `null` makes
    a transient failure permanent and indistinguishable from absence."""
    gone = urllib.error.HTTPError("http://x/404", 404, "Not Found", {}, None)
    flaky = TimeoutError("timed out")
    calls = _patch(monkeypatch, {"http://x/404": gone, "http://x/flaky": flaky})
    http = Http(tmp_path / "c.json", sleep=0)

    assert http.get("http://x/404") is None
    assert http.get("http://x/404") is None
    assert calls.count("http://x/404") == 1, "an absent resource was re-fetched"

    assert http.get("http://x/flaky") is None
    assert http.get("http://x/flaky") is None
    assert calls.count("http://x/flaky") == 2, "a timeout was cached as absent"
    assert "http://x/flaky" not in http.cache


def test_strict_raises_on_transient_and_still_returns_None_on_404(monkeypatch, tmp_path):
    """A caller assembling a COMPLETE artefact must be able to tell the two apart, or it
    writes a hole and reports success -- which is what #445's fetch would have done."""
    gone = urllib.error.HTTPError("http://x/404", 404, "Not Found", {}, None)
    _patch(monkeypatch, {"http://x/404": gone, "http://x/500": urllib.error.HTTPError(
        "http://x/500", 503, "Service Unavailable", {}, None)})
    http = Http(tmp_path / "c.json", sleep=0)
    assert http.get("http://x/404", strict=True) is None
    with pytest.raises(TransientHttpError, match="503"):
        http.get("http://x/500", strict=True)


def test_the_cache_survives_a_flush_and_reload(monkeypatch, tmp_path):
    """The run this protects is the one that gets killed, so what is on disk mid-run is
    what matters."""
    path = tmp_path / "c.json"
    calls = _patch(monkeypatch, {"http://x/u": {"v": 1}})
    a = Http(path, sleep=0)
    a.get("http://x/u")
    a.flush()
    assert path.exists()
    b = Http(path, sleep=0)
    assert b.get("http://x/u") == {"v": 1}
    assert calls == ["http://x/u"], "the reloaded cache did not serve the hit"
    # flushing twice does not rewrite
    b.flush()


def test_a_corrupt_cache_is_a_performance_problem_not_a_crash(tmp_path):
    """Every entry is re-fetchable by construction, so a truncated file must degrade to an
    empty cache rather than take the run down."""
    path = tmp_path / "c.json"
    path.write_text("{not json", encoding="utf-8")
    assert Http(path, sleep=0).cache == {}


def test_cache_missing_as_none_False_keeps_absences_out_of_the_cache(monkeypatch, tmp_path):
    """`build_sequence_structure_alignment` has a 34k-entry cache on disk built when a
    null meant "asked, absent". The default preserves that; the opt-out exists for a caller
    that would rather re-ask."""
    gone = urllib.error.HTTPError("http://x/u", 404, "Not Found", {}, None)
    calls = _patch(monkeypatch, {"http://x/u": gone})
    http = Http(tmp_path / "c.json", sleep=0, cache_missing_as_none=False)
    assert http.get("http://x/u") is None
    assert http.get("http://x/u") is None
    assert calls == ["http://x/u", "http://x/u"]
    assert http.cache == {}


def test_both_callers_use_the_shared_class():
    """The extraction is only worth anything if nothing kept a private copy."""
    import build_sequence_structure_alignment as align
    import fetch_interpro_missing_abstracts as fetch
    assert align.Http.__module__ == "http_cache"
    assert fetch.Http.__module__ == "http_cache"
    src = (REPO / "scripts" / "build_sequence_structure_alignment.py").read_text()
    assert "class Http" not in src, "the embedded copy came back"


def test_a_404_storm_refuses_to_overwrite_a_good_artefact(monkeypatch, tmp_path):
    """The failure `http_cache` does NOT classify, reached through the fetch script.

    `strict=True` separates transient from absent and the fetch guard covers transient. A
    404 lands in `missing` instead -- and 404s ARE cached. So if the API path ever changes
    shape, every accession 404s, the nulls go into the cache, `got` is empty, `{}`
    overwrites the 209-entry artefact, and the run exits 0. Every later run then serves the
    poisoned nulls at no cost and reports the same clean success.
    """
    import fetch_interpro_missing_abstracts as F

    artefact = tmp_path / "missing_abstracts.json"
    artefact.write_text('{"IPR000001": {"description": []}}', encoding="utf-8")
    before = artefact.read_text(encoding="utf-8")

    gone = urllib.error.HTTPError("http://x/a", 404, "Not Found", {}, None)
    monkeypatch.setattr("http_cache.urllib.request.urlopen",
                        lambda req, timeout=30: (_ for _ in ()).throw(gone))
    monkeypatch.setattr(F, "entries_without_abstract",
                        lambda xml: ["IPR000001", "IPR000002", "IPR000003"])
    monkeypatch.setattr(F.XML_GZ.__class__, "exists", lambda self: True, raising=False)
    monkeypatch.setattr(sys, "argv", [
        "fetch", "--sleep", "0", "--out", str(artefact),
        "--cache", str(tmp_path / "cache.json")])

    assert F.main() == 1, "a 404 storm reported success"
    assert artefact.read_text(encoding="utf-8") == before, "THE ARTEFACT WAS OVERWRITTEN"
