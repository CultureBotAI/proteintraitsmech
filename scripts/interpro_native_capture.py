"""Validate same-response InterPro release receipts and complete native page chains.

Acquisition and raw-file persistence belong to fetch_interpro_native.py.
This contract preserves native location groups and produces no qualified evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any
from urllib.parse import parse_qsl, urlsplit
from urllib.request import Request

from interpro_native_groups import NativeCaptureError, digest, discover_groups, require

BASE = "https://www.ebi.ac.uk/interpro/api/"
CATALOG_URL = BASE + "?format=json"
ACCESSION = re.compile(
    r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-[1-9][0-9]*)?"
)


@dataclass(frozen=True)
class ResponseCapture:
    method: str
    requested_url: str
    resolved_url: str
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    captured_at_utc: str


def read_response(
    request: Request, response: Any, *, max_body_bytes: int = 4_000_000
) -> ResponseCapture:
    """Copy final headers and bounded body bytes from one actual response object.

    The caller owns transport and context-manager cleanup. This function cannot
    attest that a caller executed a request; a registered runner must record that.
    """
    require(isinstance(request, Request) and request.get_method() == "GET", "GET request required")
    require(request.data is None, "GET body is not allowed")
    require(type(max_body_bytes) is int and max_body_bytes > 0, "invalid body limit")
    headers = tuple(response.headers.raw_items())
    resolved_url, status = response.geturl(), response.status
    body = response.read(max_body_bytes + 1)
    require(isinstance(body, bytes) and len(body) <= max_body_bytes, "body exceeds capture limit")
    return ResponseCapture(
        "GET",
        request.full_url,
        resolved_url,
        status,
        headers,
        body,
        datetime.now(timezone.utc).isoformat(),
    )


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise NativeCaptureError(f"nonfinite JSON value: {value}")


def url_key(url: str, path: str, page_size: int | None = None):
    require(isinstance(url, str) and bool(url), "missing URL")
    require(all(32 < ord(c) < 127 for c in url), "unsafe URL characters")
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and parsed.netloc == "www.ebi.ac.uk", "unexpected URL origin")
    require(not parsed.fragment and parsed.path == path, "unexpected URL endpoint")
    try:
        pairs = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True)
    except ValueError as exc:
        raise NativeCaptureError("invalid URL query") from exc
    query = {}
    for name, value in pairs:
        require(name not in query, "duplicate URL query parameter")
        query[name] = value
    allowed = {"format"} if page_size is None else {"format", "page_size", "cursor"}
    require(query.keys() <= allowed and query.get("format") == "json", "unexpected URL query")
    if page_size is not None:
        require(query.get("page_size") == str(page_size), "page-size mismatch")
        if "cursor" in query:
            require(
                bool(query["cursor"]) and all(32 < ord(c) < 127 for c in query["cursor"]),
                "invalid pagination cursor",
            )
    return parsed.path, tuple(sorted(query.items()))


def read_capture(
    capture: ResponseCapture,
    expected_url: str,
    path: str,
    release: str,
    minor: str,
    page_size: int | None = None,
):
    require(isinstance(capture, ResponseCapture), "response capture required")
    require(capture.method == "GET", "GET capture required")
    require(type(capture.status) is int and capture.status == 200, "incomplete HTTP response")
    expected = url_key(expected_url, path, page_size)
    require(url_key(capture.requested_url, path, page_size) == expected, "requested URL mismatch")
    require(url_key(capture.resolved_url, path, page_size) == expected, "resolved URL mismatch")
    headers = {}
    for name, value in capture.headers:
        require(isinstance(name, str) and isinstance(value, str), "invalid response header")
        require("\r" not in value and "\n" not in value, "multiline response header")
        headers.setdefault(name.lower(), []).append(value.strip())

    def one(name):
        values = headers.get(name, [])
        require(len(values) == 1 and bool(values[0]), f"missing or duplicate {name} header")
        return values[0]

    require(one("interpro-version") == release, "InterPro release drift")
    require(one("interpro-version-minor") == minor, "InterPro minor-release drift")
    require(
        one("content-type").split(";", 1)[0].strip().lower() == "application/json",
        "non-JSON response content type",
    )
    require(isinstance(capture.body, bytes) and bool(capture.body), "missing response body")
    if "content-length" in headers:
        length = one("content-length")
        require(
            bool(re.fullmatch(r"[0-9]+", length)) and int(length) == len(capture.body),
            "incomplete response body",
        )
    require(
        headers.get("content-encoding", ["identity"]) == ["identity"],
        "unsupported encoded response body",
    )
    require(isinstance(capture.captured_at_utc, str), "capture time must be text")
    try:
        observed = datetime.fromisoformat(capture.captured_at_utc.replace("Z", "+00:00"))
        require(
            observed.tzinfo is not None and observed.utcoffset().total_seconds() == 0,
            "capture time must be UTC",
        )
        body = json.loads(
            capture.body.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_constant
        )
    except (UnicodeDecodeError, ValueError, TypeError) as exc:
        if isinstance(exc, NativeCaptureError):
            raise
        raise NativeCaptureError("invalid capture time or JSON body") from exc
    require(isinstance(body, dict), "JSON response must be an object")
    receipt = {
        "method": capture.method,
        "requested_url": capture.requested_url,
        "resolved_url": capture.resolved_url,
        "status": capture.status,
        "captured_at_utc": capture.captured_at_utc,
        "body_bytes": len(capture.body),
        "body_sha256": hashlib.sha256(capture.body).hexdigest(),
        "headers_sha256": digest(capture.headers),
        "source_headers": {
            name: headers[name][0]
            for name in ("interpro-version", "interpro-version-minor", "content-type")
        },
    }
    return body, receipt


def discover_capture_bundle(
    catalog_before: ResponseCapture,
    pages: list[ResponseCapture],
    protein: ResponseCapture,
    catalog_after: ResponseCapture,
    reference: dict,
    *,
    release: str,
    minor: str,
    page_size: int = 200,
    max_pages: int = 100,
) -> dict:
    """Validate release consistency and complete pagination, then preserve groups.

    Native and reference UniProt releases remain separately reported; the full
    sequence, exact accession, taxon, length and review status must agree. A
    different release label alone does not override an exact-sequence comparison.
    No qualification or canonical trait mapping is produced here.
    """
    require(
        isinstance(release, str) and bool(re.fullmatch(r"[0-9]+\.[0-9]+", release)),
        "invalid expected InterPro release",
    )
    require(
        isinstance(minor, str) and bool(re.fullmatch(r"0|[1-9][0-9]*", minor)),
        "invalid expected minor release",
    )
    require(type(page_size) is int and 1 <= page_size <= 200, "invalid page size")
    require(type(max_pages) is int and max_pages > 0, "invalid page limit")
    require(
        isinstance(pages, list) and 0 < len(pages) <= max_pages,
        "missing pages or page limit exceeded",
    )
    require(isinstance(reference, dict), "reference object required")
    protein_id = reference.get("protein_id", "")
    require(
        isinstance(protein_id, str) and protein_id.startswith("UniProtKB:"), "invalid reference ID"
    )
    accession = protein_id.split(":", 1)[1]
    require(bool(ACCESSION.fullmatch(accession)), "invalid exact accession")
    root_path = "/interpro/api/"
    before, before_receipt = read_capture(catalog_before, CATALOG_URL, root_path, release, minor)
    after, after_receipt = read_capture(catalog_after, CATALOG_URL, root_path, release, minor)
    require(catalog_before.body == catalog_after.body, "catalogue changed during capture")
    databases = before.get("databases")
    require(isinstance(databases, dict), "missing source catalogue")
    require(
        databases.get("interpro", {}).get("version") == release, "catalogue/header release mismatch"
    )
    uniprot_release = databases.get("uniprot", {}).get("version")
    require(
        isinstance(uniprot_release, str)
        and bool(re.fullmatch(r"[0-9]{4}_[0-9]{2}", uniprot_release)),
        "missing source UniProt release",
    )
    require(
        all(
            databases.get(k, {}).get("version") == uniprot_release
            for k in ("reviewed", "unreviewed")
        ),
        "inconsistent source UniProt release",
    )
    require(
        isinstance(reference.get("uniprot_release"), str)
        and bool(re.fullmatch(r"[0-9]{4}_[0-9]{2}", reference["uniprot_release"])),
        "missing reference UniProt release",
    )
    protein_path = root_path + f"protein/uniprot/{accession}/"
    protein_body, protein_receipt = read_capture(
        protein,
        "https://www.ebi.ac.uk" + protein_path + "?format=json",
        protein_path,
        release,
        minor,
    )
    entry_path = root_path + f"entry/all/protein/uniprot/{accession}/"
    next_url = "https://www.ebi.ac.uk" + entry_path + f"?page_size={page_size}&format=json"
    visited, results, page_receipts = set(), [], []
    total = None
    for index, capture in enumerate(pages):
        require(next_url is not None, "unexpected extra page")
        key = url_key(next_url, entry_path, page_size)
        require(key not in visited, "pagination cycle")
        visited.add(key)
        body, receipt = read_capture(capture, next_url, entry_path, release, minor, page_size)
        require("previous" in body and "next" in body, "missing pagination state")
        if index == 0:
            require(body["previous"] is None, "first page is not the beginning")
        else:
            url_key(body["previous"], entry_path, page_size)
        count, entries = body.get("count"), body.get("results")
        require(type(count) is int and count >= 0, "invalid source count")
        if total is None:
            total = count
        require(count == total, "source count changed between pages")
        require(isinstance(entries, list) and len(entries) <= page_size, "invalid result page")
        require(bool(entries) or total == 0, "empty intermediate result page")
        results.extend(entries)
        require(len(results) <= total, "source count exceeded")
        next_url = body["next"]
        if next_url is not None:
            next_key = url_key(next_url, entry_path, page_size)
            require(next_key not in visited, "pagination cycle")
        receipt.update(
            page_index=index,
            source_count=count,
            page_entries=len(entries),
            previous=body["previous"],
            next=next_url,
        )
        page_receipts.append(receipt)
    require(next_url is None and len(results) == total, "incomplete page chain")
    def instant(capture):
        return datetime.fromisoformat(capture.captured_at_utc.replace("Z", "+00:00"))

    start, finish = instant(catalog_before), instant(catalog_after)
    require(
        start <= finish and all(start <= instant(c) <= finish for c in [*pages, protein]),
        "capture timestamps are outside catalogue bracket",
    )
    require(
        all(instant(a) <= instant(b) for a, b in zip(pages, pages[1:])),
        "page captures are out of time order",
    )
    combined = {"count": total, "next": None, "previous": None, "results": results}
    discovery = discover_groups(combined, protein_body, reference)
    receipts = {
        "catalog_before": before_receipt,
        "pages": page_receipts,
        "protein": protein_receipt,
        "catalog_after": after_receipt,
    }
    identity = {
        "interpro_release": release,
        "interpro_minor_release": minor,
        "native_uniprot_release": uniprot_release,
        "reference_uniprot_release": reference["uniprot_release"],
        "reference_sha256": digest(reference),
        "receipts": receipts,
    }
    return {
        "scope": "Native response and pagination contract replayed; no qualified coordinates.",
        "capture_id": "interpro-native-capture:" + digest(identity),
        **identity,
        "entry_projection_is_complete_page_assembly": True,
        "discovery": discovery,
        "remaining_requirements": [
            "Replay the saved acquisition bundle against its independently reviewed checksum.",
            "Source licensing and explicit canonical trait mapping review.",
            "Per-location evidence and complete-location-set promotion.",
        ],
    }
