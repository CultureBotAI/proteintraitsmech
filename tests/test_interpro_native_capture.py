"""Synthetic native API fixtures; these tests are not acquisition evidence."""

import copy
from dataclasses import replace
from email.message import Message
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from interpro_native_fixtures import synthetic_canaries
from urllib.request import Request

import pytest

from interpro_native_capture import (
    BASE,
    CATALOG_URL,
    ResponseCapture,
    discover_capture_bundle,
    read_response,
)
from interpro_native_groups import NativeCaptureError

TIME = "2026-09-17T11:00:00+00:00"

def capture(url, body, *, minor="0"):
    raw = body if isinstance(body, bytes) else json.dumps(body).encode()
    return ResponseCapture(
        "GET",
        url,
        url,
        200,
        (
            ("Content-Type", "application/json; charset=utf-8"),
            ("InterPro-Version", "110.0"),
            ("InterPro-Version-Minor", minor),
            ("Content-Length", str(len(raw))),
        ),
        raw,
        TIME,
    )


def body(cap):
    return json.loads(cap.body)


def change_body(cap, value):
    raw = value if isinstance(value, bytes) else json.dumps(value).encode()
    headers = tuple(
        (name, str(len(raw)) if name.lower() == "content-length" else value)
        for name, value in cap.headers
    )
    return replace(cap, body=raw, headers=headers)


def change_header(cap, name, value):
    headers = tuple((key, val) for key, val in cap.headers if key.lower() != name.lower())
    if value is not None:
        headers += ((name, value),)
    return replace(cap, headers=headers)


def synthetic_bundles():
    result = {}
    for acc, (entries, protein, reference) in synthetic_canaries().items():
        root = {"databases": {name: {"version": version} for name, version in (
            ("interpro", "110.0"), ("uniprot", "2026_03"),
            ("reviewed", "2026_03"), ("unreviewed", "2026_03"))}}
        entry_url = BASE + f"entry/all/protein/uniprot/{acc}/?page_size=200&format=json"
        protein_url = BASE + f"protein/uniprot/{acc}/?format=json"
        result[acc] = [capture(CATALOG_URL, root), [capture(entry_url, entries)],
                       capture(protein_url, protein), capture(CATALOG_URL, root), reference]
    return result


@pytest.fixture(scope="module")
def native():
    return synthetic_bundles()


def run(bundle, **kwargs):
    return discover_capture_bundle(*bundle, release="110.0", minor="0", **kwargs)


def paginated(bundle):
    result = copy.deepcopy(bundle)
    first = result[1][0]
    entries = body(first)
    next_url = first.requested_url + "&cursor=next-token"
    reverse_url = first.requested_url + "&cursor=reverse-token"
    result[1] = [
        capture(
            first.requested_url, {**entries, "results": entries["results"][:4], "next": next_url}
        ),
        capture(next_url, {**entries, "results": entries["results"][4:], "previous": reverse_url}),
    ]
    return result


def entry(result, acc):
    return next(x for x in result["discovery"]["source_entries"] if x["native_accession"] == acc)


def test_synthetic_groups_survive_response_contract(native):
    repeated = run(native["P05719"])
    discontinuous = run(native["Q796K8"])
    assert len(entry(repeated, "IPR000055")["locations"]) == 2
    assert entry(discontinuous, "SSF56519")["locations"][0]["intervals"] == [
        {"start": 59, "end": 121},
        {"start": 212, "end": 341},
    ]
    assert entry(discontinuous, "IPR036138")["locations"][0]["intervals"] == [
        {"start": 59, "end": 341}
    ]
    assert repeated["native_uniprot_release"] == "2026_03"
    receipt = repeated["receipts"]["pages"][0]
    assert receipt["body_sha256"] == hashlib.sha256(native["P05719"][1][0].body).hexdigest()
    assert receipt["source_headers"]["interpro-version-minor"] == "0"


def test_complete_two_page_capture_preserves_native_locations(native):
    result = run(paginated(native["P05719"]))
    assert (
        result["discovery"]["source_entries"]
        == run(native["P05719"])["discovery"]["source_entries"]
    )
    assert [p["page_entries"] for p in result["receipts"]["pages"]] == [4, 6]
    assert result["entry_projection_is_complete_page_assembly"] is True


def test_exact_sequence_across_releases_keeps_both_release_labels(native):
    bundle = copy.deepcopy(native["P05719"])
    bundle[4]["uniprot_release"] = "2026_02"
    result = run(bundle)
    assert result["native_uniprot_release"] == "2026_03"
    assert result["reference_uniprot_release"] == "2026_02"


def test_minor_release_participates_in_capture_identity(native):
    bundle = copy.deepcopy(native["P05719"])
    bundle[0], bundle[2], bundle[3] = [
        change_header(bundle[i], "InterPro-Version-Minor", "1") for i in (0, 2, 3)
    ]
    bundle[1] = [change_header(c, "InterPro-Version-Minor", "1") for c in bundle[1]]
    changed = discover_capture_bundle(*bundle, release="110.0", minor="1")
    assert changed["capture_id"] != run(native["P05719"])["capture_id"]
    assert changed["discovery"] == run(native["P05719"])["discovery"]


@pytest.mark.parametrize(
    "mutation,match",
    [
        ("head", "GET capture"),
        ("status", "incomplete HTTP"),
        ("missing_major", "missing or duplicate interpro-version"),
        ("missing_minor", "missing or duplicate interpro-version-minor"),
        ("duplicate_major", "missing or duplicate interpro-version"),
        ("major", "release drift"),
        ("minor", "minor-release drift"),
        ("html", "non-JSON response"),
        ("length", "incomplete response body"),
        ("encoding", "unsupported encoded"),
        ("header_newline", "multiline response"),
        ("duplicate_json", "duplicate JSON key"),
        ("nonfinite", "nonfinite JSON value"),
        ("json_list", "must be an object"),
        ("naive_time", "capture time must be UTC"),
        ("missing_time", "capture time must be text"),
        ("outside_time", "outside catalogue bracket"),
        ("redirect", "unexpected URL endpoint"),
        ("foreign_origin", "unexpected URL origin"),
        ("http", "unexpected URL origin"),
        ("userinfo", "unexpected URL origin"),
        ("query_filter", "unexpected URL query"),
        ("duplicate_query", "duplicate URL query"),
        ("wrong_page_size", "page-size mismatch"),
        ("url_control", "unsafe URL characters"),
        ("catalog_change", "catalogue changed"),
        ("catalog_release", "catalogue/header release"),
        ("source_uniprot", "inconsistent source UniProt"),
        ("sequence", "native protein sequence mismatch"),
        ("first_previous", "first page is not the beginning"),
        ("truncated", "incomplete page chain"),
    ],
)
def test_rejects_unbound_or_incomplete_captures(native, mutation, match):
    bundle = copy.deepcopy(native["P05719"])
    cap = bundle[1][0]
    if mutation == "head":
        cap = replace(cap, method="HEAD")
    elif mutation == "status":
        cap = replace(cap, status=206)
    elif mutation == "missing_major":
        cap = change_header(cap, "InterPro-Version", None)
    elif mutation == "missing_minor":
        cap = change_header(cap, "InterPro-Version-Minor", None)
    elif mutation == "duplicate_major":
        cap = replace(cap, headers=cap.headers + (("InterPro-Version", "110.0"),))
    elif mutation == "major":
        cap = change_header(cap, "InterPro-Version", "109.0")
    elif mutation == "minor":
        cap = change_header(cap, "InterPro-Version-Minor", "1")
    elif mutation == "html":
        cap = change_header(cap, "Content-Type", "text/html")
    elif mutation == "length":
        cap = change_header(cap, "Content-Length", "1")
    elif mutation == "encoding":
        cap = change_header(cap, "Content-Encoding", "gzip")
    elif mutation == "header_newline":
        cap = change_header(cap, "ETag", "abc\r\ndef")
    elif mutation == "duplicate_json":
        cap = change_body(cap, b'{"count":10,"count":0}')
    elif mutation == "nonfinite":
        cap = change_body(cap, b'{"count":NaN}')
    elif mutation == "json_list":
        cap = change_body(cap, b"[]")
    elif mutation == "naive_time":
        cap = replace(cap, captured_at_utc="2026-09-17T11:00:00")
    elif mutation == "missing_time":
        cap = replace(cap, captured_at_utc=None)
    elif mutation == "outside_time":
        cap = replace(cap, captured_at_utc="2026-09-17T11:01:00Z")
    elif mutation == "redirect":
        cap = replace(cap, resolved_url=cap.resolved_url.replace("P05719", "Q796K8"))
    elif mutation == "foreign_origin":
        cap = replace(cap, requested_url=cap.requested_url.replace("www.ebi.ac.uk", "example.org"))
    elif mutation == "http":
        cap = replace(cap, requested_url=cap.requested_url.replace("https:", "http:"))
    elif mutation == "userinfo":
        cap = replace(cap, requested_url=cap.requested_url.replace("//www", "//user@www"))
    elif mutation == "query_filter":
        cap = replace(cap, requested_url=cap.requested_url + "&search=partial")
    elif mutation == "duplicate_query":
        cap = replace(cap, requested_url=cap.requested_url + "&format=json")
    elif mutation == "wrong_page_size":
        cap = replace(cap, requested_url=cap.requested_url.replace("200", "20"))
    elif mutation == "url_control":
        cap = replace(cap, requested_url=cap.requested_url + "\n")
    elif mutation == "catalog_change":
        value = body(bundle[3])
        value["extra"] = True
        bundle[3] = change_body(bundle[3], value)
    elif mutation in {"catalog_release", "source_uniprot"}:
        for index in (0, 3):
            value = body(bundle[index])
            key = "interpro" if mutation == "catalog_release" else "reviewed"
            value["databases"][key]["version"] = "109.0" if key == "interpro" else "2026_02"
            bundle[index] = change_body(bundle[index], value)
    elif mutation == "sequence":
        value = body(bundle[2])
        value["metadata"]["sequence"] = "A" + value["metadata"]["sequence"][1:]
        bundle[2] = change_body(bundle[2], value)
    elif mutation in {"first_previous", "truncated"}:
        value = body(cap)
        key = "previous" if mutation == "first_previous" else "next"
        value[key] = cap.requested_url + "&cursor=other"
        cap = change_body(cap, value)
    bundle[1][0] = cap
    with pytest.raises(NativeCaptureError, match=match):
        run(bundle)


@pytest.mark.parametrize(
    "mutation,match",
    [
        ("cycle", "pagination cycle"),
        ("minor", "minor-release drift"),
        ("count", "source count changed"),
        ("missing_result", "incomplete page chain"),
        ("extra_page", "unexpected extra page"),
        ("missing_page", "incomplete page chain"),
        ("foreign_next", "unexpected URL origin"),
        ("wrong_next_protein", "unexpected URL endpoint"),
        ("wrong_requested_cursor", "requested URL mismatch"),
        ("duplicate_entry", "duplicate native entry identity"),
        ("missing_previous", "missing URL"),
        ("missing_state", "missing pagination state"),
        ("empty_page", "empty intermediate result page"),
        ("time_order", "out of time order"),
    ],
)
def test_rejects_broken_page_chains(native, mutation, match):
    bundle = paginated(native["P05719"])
    first, last = bundle[1]
    value = body(last)
    if mutation == "cycle":
        value["next"] = first.requested_url
    elif mutation == "minor":
        last = change_header(last, "InterPro-Version-Minor", "1")
    elif mutation == "count":
        value["count"] += 1
    elif mutation == "missing_result":
        value["results"].pop()
    elif mutation == "extra_page":
        bundle[1].append(copy.deepcopy(last))
    elif mutation == "missing_page":
        bundle[1].pop()
    elif mutation == "foreign_next":
        value["next"] = last.requested_url.replace("www.ebi.ac.uk", "example.org")
    elif mutation == "wrong_next_protein":
        value["next"] = last.requested_url.replace("P05719", "Q796K8")
    elif mutation == "wrong_requested_cursor":
        last = replace(last, requested_url=last.requested_url + "-wrong")
    elif mutation == "duplicate_entry":
        value["results"][0] = body(first)["results"][0]
    elif mutation == "missing_previous":
        value["previous"] = None
    elif mutation == "missing_state":
        del value["next"]
    elif mutation == "empty_page":
        value["results"] = []
    elif mutation == "time_order":
        bundle[3] = replace(bundle[3], captured_at_utc="2026-09-17T11:02:00Z")
        bundle[1][0] = replace(first, captured_at_utc="2026-09-17T11:01:00Z")
    if mutation != "missing_page":
        bundle[1][1] = change_body(last, value)
    with pytest.raises(NativeCaptureError, match=match):
        run(bundle)


@pytest.mark.parametrize(
    "kwargs,match",
    [
        ({"page_size": True}, "invalid page size"),
        ({"page_size": 201}, "invalid page size"),
        ({"max_pages": True}, "invalid page limit"),
        ({"max_pages": 1}, "page limit exceeded"),
    ],
)
def test_page_bounds_do_not_silently_truncate(native, kwargs, match):
    with pytest.raises(NativeCaptureError, match=match):
        run(paginated(native["P05719"]), **kwargs)


def test_chunked_json_without_content_length_remains_verifiable(native):
    bundle = copy.deepcopy(native["P05719"])
    bundle[1][0] = change_header(bundle[1][0], "Content-Length", None)
    assert len(run(bundle)["discovery"]["source_entries"]) == 10


class FakeResponse:
    def __init__(self, cap):
        self.headers = Message()
        for name, value in cap.headers:
            self.headers[name] = value
        self.status = cap.status
        self.url = cap.resolved_url
        self.body = cap.body
        self.read_sizes = []

    def geturl(self):
        return self.url

    def read(self, count):
        self.read_sizes.append(count)
        return self.body[:count]


def test_reads_headers_and_body_from_same_response_object(native):
    cap = native["P05719"][1][0]
    response = FakeResponse(cap)
    result = read_response(Request(cap.requested_url, method="GET"), response)
    assert result.body == cap.body and result.headers == cap.headers
    response.headers.replace_header("InterPro-Version", "109.0")
    response.body = b"changed"
    assert result.body == cap.body and dict(result.headers)["InterPro-Version"] == "110.0"
    assert response.read_sizes == [4_000_001]


def test_head_request_never_becomes_get_evidence(native):
    cap = native["P05719"][1][0]
    response = FakeResponse(cap)
    with pytest.raises(NativeCaptureError, match="GET request"):
        read_response(Request(cap.requested_url, method="HEAD"), response)
    assert response.read_sizes == []


def test_capture_limit_refuses_oversized_body(native):
    cap = native["P05719"][1][0]
    with pytest.raises(NativeCaptureError, match="body exceeds capture limit"):
        read_response(
            Request(cap.requested_url, method="GET"), FakeResponse(cap), max_body_bytes=10
        )
