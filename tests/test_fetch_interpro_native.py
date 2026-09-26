"""Network-free acquisition, immutable publication, and native receipt replay."""

import copy
from dataclasses import replace
import io
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_interpro_native as fetch
from interpro_native_groups import NativeCaptureError
from test_interpro_native_capture import (
    FakeResponse, body, change_body, change_header, paginated, synthetic_bundles,
)


class Response(FakeResponse):
    closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True


class Opener:
    def __init__(self, bundle, prefix=()):
        self.items = [*prefix, bundle[0], bundle[2], *bundle[1], bundle[3]]
        self.calls = []
        self.responses = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        assert request.full_url == item.requested_url
        assert request.get_method() == "GET"
        assert request.data is None
        assert request.get_header("Accept-encoding") == "identity"
        response = Response(item)
        self.responses.append(response)
        return response


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "RAW_ROOT", tmp_path / "raw")
    bundle = copy.deepcopy(synthetic_bundles()["P05719"])
    registry = tmp_path / "references.jsonl"
    registry.write_text(json.dumps(bundle[4]) + "\n")
    plan = fetch.request_plan(registry, bundle[4]["protein_id"], tmp_path / "raw/run/P05719",
                              release="110.0", minor="0")
    return bundle, plan


def test_plan_and_cli_dry_run_have_no_network_or_output(prepared, capsys, monkeypatch):
    bundle, plan = prepared
    monkeypatch.setattr(fetch, "build_opener", lambda *a: pytest.fail("dry-run network"))
    assert not Path(plan["output"]).exists()
    assert fetch.main(["--registry", plan["registry_path"], "--protein", plan["protein_id"],
                       "--out", plan["output"], "--expect-release", "110.0",
                       "--expect-minor", "0"]) == 0
    assert json.loads(capsys.readouterr().out) == plan
    assert not Path(plan["output"]).parent.exists()
    assert plan["reference"] == bundle[4]


def test_complete_capture_replays_from_raw_files_and_closes_responses(prepared):
    bundle, plan = prepared
    opener = Opener(paginated(bundle))
    result = fetch.acquire(plan, opener=opener)
    assert result["pages"] == 2 and result["entries"] == 10
    assert len(opener.calls) == 5 and all(r.closed for r in opener.responses)
    directory = Path(result["output"])
    replay = fetch.replay_bundle(directory, expected_sha256=result["bundle_sha256"])
    locations = next(e for e in replay["discovery"]["source_entries"]
                     if e["native_accession"] == "IPR000055")["locations"]
    assert [p["intervals"] for p in locations] == [[{"start": 7, "end": 190}],
                                                  [{"start": 348, "end": 403}]]
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    with pytest.raises(NativeCaptureError, match="already exists"):
        fetch.acquire(plan, opener=Opener(bundle))
    assert {p.name: p.read_bytes() for p in directory.iterdir()} == before


@pytest.mark.parametrize("mutation,match", [
    ("missing_header", "missing or duplicate interpro-version"),
    ("changed_minor", "minor-release drift"),
    ("sequence", "native protein sequence mismatch"),
    ("count", "captures disagree"),
    ("cycle", "pagination cycle"),
    ("foreign_next", "unexpected URL origin"),
    ("truncated", "incomplete response body"),
    ("redirect", "unexpected URL endpoint"),
    ("wrong_protein_next", "unexpected URL endpoint"),
])
def test_failure_cannot_publish_a_bundle(prepared, mutation, match):
    bundle, plan = prepared
    if mutation == "missing_header":
        bundle[1][0] = change_header(bundle[1][0], "InterPro-Version", None)
    elif mutation == "changed_minor":
        bundle[1][0] = change_header(bundle[1][0], "InterPro-Version-Minor", "1")
    elif mutation == "sequence":
        value = body(bundle[2])
        value["metadata"]["sequence"] = "A" + value["metadata"]["sequence"][1:]
        bundle[2] = change_body(bundle[2], value)
    elif mutation == "count":
        value = body(bundle[2])
        value["metadata"]["counters"]["entries"] += 1
        bundle[2] = change_body(bundle[2], value)
    elif mutation in {"cycle", "foreign_next", "wrong_protein_next"}:
        cap = bundle[1][0]
        value = body(cap)
        value["next"] = cap.requested_url
        if mutation == "foreign_next":
            value["next"] = value["next"].replace("www.ebi.ac.uk", "example.org")
        elif mutation == "wrong_protein_next":
            value["next"] = value["next"].replace("P05719", "Q796K8")
        bundle[1][0] = change_body(cap, value)
    elif mutation == "truncated":
        bundle[1][0] = change_header(bundle[1][0], "Content-Length", "999999")
    elif mutation == "redirect":
        cap = bundle[1][0]
        bundle[1][0] = replace(cap, resolved_url=cap.resolved_url.replace("P05719", "Q796K8"))
    opener = Opener(bundle)
    with pytest.raises(NativeCaptureError, match=match):
        fetch.acquire(plan, opener=opener)
    output = Path(plan["output"])
    assert not (output / "bundle.json").exists()
    assert json.loads((output / "failure.json").read_text())["complete_bundle"] is False
    assert all(r.closed for r in opener.responses)
    assert all("example.org" not in r.full_url and "Q796K8" not in r.full_url
               for r, _ in opener.calls)


def test_retry_uses_a_new_get_and_records_failures(prepared):
    bundle, plan = prepared
    failed_body = io.BytesIO(b"busy")
    opener = Opener(bundle, prefix=[HTTPError(fetch.CATALOG_URL, 503, "busy", {}, failed_body)])
    sleeps = []
    result = fetch.acquire(plan, opener=opener, sleep=sleeps.append)
    assert len(opener.calls) == 5 and sleeps == [1] and failed_body.closed
    receipt = json.loads((Path(result["output"]) / "catalog-before.capture.json").read_text())
    assert receipt["failed_attempts"] == [{"attempt": 1, "http_status": 503}]
    assert receipt["method"] == "GET"


def test_retry_exhaustion_retains_failure_without_success(prepared):
    bundle, plan = prepared
    opener = Opener(bundle, prefix=[URLError("offline")] * 3)
    sleeps = []
    with pytest.raises(NativeCaptureError, match="failed after 3 attempts"):
        fetch.acquire(plan, opener=opener, sleep=sleeps.append)
    assert len(opener.calls) == 3 and sleeps == [1, 2]
    assert not (Path(plan["output"]) / "bundle.json").exists()


def test_no_retry_for_a_permanent_http_failure(prepared):
    bundle, plan = prepared
    stream = io.BytesIO(b"missing")
    opener = Opener(bundle, prefix=[HTTPError(fetch.CATALOG_URL, 404, "missing", {}, stream)])
    with pytest.raises(HTTPError):
        fetch.acquire(plan, opener=opener, sleep=lambda t: pytest.fail("permanent retry"))
    assert len(opener.calls) == 1 and stream.closed


def test_redirect_handler_refuses_before_following():
    with pytest.raises(NativeCaptureError, match="redirect refused"):
        fetch.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.org")


def test_changed_registry_or_producer_cannot_execute_saved_plan(prepared, monkeypatch):
    bundle, plan = prepared
    registry = Path(plan["registry_path"])
    registry.write_text(registry.read_text() + "\n")
    with pytest.raises(NativeCaptureError, match="plan changed"):
        fetch.acquire(plan, opener=Opener(bundle))
    assert not Path(plan["output"]).exists()
    registry.write_text(json.dumps(bundle[4]) + "\n")
    monkeypatch.setattr(fetch, "PRODUCER_FILES", ("fetch_interpro_native.py",))
    with pytest.raises(NativeCaptureError, match="plan changed"):
        fetch.acquire(plan, opener=Opener(bundle))
    assert not Path(plan["output"]).exists()


@pytest.mark.parametrize("filename", ["page-0000.body.json", "protein.capture.json", "bundle.json"])
def test_altered_saved_files_fail_replay(prepared, filename):
    bundle, plan = prepared
    result = fetch.acquire(plan, opener=Opener(bundle))
    output = Path(result["output"])
    path = output / filename
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(NativeCaptureError, match="digest mismatch"):
        fetch.replay_bundle(output, expected_sha256=result["bundle_sha256"])


def test_missing_or_symlink_raw_file_fails_replay(prepared, tmp_path):
    bundle, plan = prepared
    result = fetch.acquire(plan, opener=Opener(bundle))
    output = Path(result["output"])
    raw = output / "page-0000.body.json"
    other = tmp_path / "external.json"
    other.write_bytes(raw.read_bytes())
    raw.unlink()
    raw.symlink_to(other)
    with pytest.raises(NativeCaptureError, match="regular capture file"):
        fetch.replay_bundle(output, expected_sha256=result["bundle_sha256"])


def test_plan_rejects_duplicate_reference_and_outside_destination(prepared, tmp_path):
    _, plan = prepared
    registry = Path(plan["registry_path"])
    with pytest.raises(NativeCaptureError, match="below data/raw/interpro_native"):
        fetch.request_plan(registry, plan["protein_id"], tmp_path / "outside",
                           release="110.0", minor="0")
    registry.write_text(registry.read_text() * 2)
    with pytest.raises(NativeCaptureError, match="exact reference once"):
        fetch.request_plan(registry, plan["protein_id"], Path(plan["output"]),
                           release="110.0", minor="0")


def test_page_limit_refuses_partial_capture(prepared):
    bundle, old = prepared
    plan = fetch.request_plan(Path(old["registry_path"]), old["protein_id"], Path(old["output"]),
                              release="110.0", minor="0", max_pages=1)
    opener = Opener(paginated(bundle))
    with pytest.raises(NativeCaptureError, match="page limit exceeded"):
        fetch.acquire(plan, opener=opener)
    assert len(opener.calls) == 3
    assert not (Path(plan["output"]) / "bundle.json").exists()
