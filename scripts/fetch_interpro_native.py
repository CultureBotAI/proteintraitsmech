#!/usr/bin/env python3
"""Capture complete native InterPro locations for one exact existing reference.

Dry-run prints a digest-bound request plan without network or writes. --apply
requires that exact plan. Each GET's raw body and headers are saved together;
bundle.json is published only after release, pagination and sequence checks and
an independent replay from saved files. Failed acquisitions retain failure.json
and their partial raw files, never a usable bundle. Use a new output directory
for a retry; existing acquisitions are immutable and cannot be overwritten.

This is acquisition/discovery only. It cannot write traits or grounding registries,
and does not infer coordinates, map trait identities, or approve occurrences.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from interpro_native_capture import (
    ACCESSION, BASE, CATALOG_URL, ResponseCapture, discover_capture_bundle,
    read_capture, read_response, url_key,
)
from interpro_native_groups import NativeCaptureError, digest, require
from validate_uniprot_grounding import validate_protein_reference

ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data/raw/interpro_native"
SCHEMA_VERSION = 1
PRODUCER_FILES = ("fetch_interpro_native.py", "interpro_native_capture.py",
                  "interpro_native_groups.py")
RETRY_STATUS = {408, 429, 500, 502, 503, 504}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def strict_json(raw: bytes):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "duplicate JSON key")
            value[key] = item
        return value

    def constant(value):
        raise NativeCaptureError(f"nonfinite JSON value: {value}")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=constant)


def selected_reference(registry: Path, protein_id: str) -> tuple[dict, str]:
    """Bind a full validated ProteinReference to the exact registry bytes read."""
    raw = registry.read_bytes()
    matches = []
    for line, text in enumerate(raw.splitlines(), 1):
        if not text.strip():
            continue
        value = strict_json(text)
        require(isinstance(value, dict), f"registry line {line} is not an object")
        if value.get("protein_id") == protein_id:
            findings = validate_protein_reference(value, path=registry, line=line)
            require(not findings, f"invalid selected ProteinReference: {findings}")
            matches.append(value)
    require(len(matches) == 1, "registry must contain the exact reference once")
    return matches[0], sha256(raw)


def request_plan(registry: Path, protein_id: str, output: Path, *, release: str,
                 minor: str, page_size: int = 200, max_pages: int = 100,
                 attempts: int = 3, timeout: int = 30) -> dict:
    require(isinstance(protein_id, str) and protein_id.startswith("UniProtKB:"),
            "exact UniProtKB protein ID required")
    accession = protein_id.split(":", 1)[1]
    require(bool(ACCESSION.fullmatch(accession)), "invalid exact accession")
    require(bool(re.fullmatch(r"[0-9]+\.[0-9]+", release)), "invalid InterPro release")
    require(bool(re.fullmatch(r"0|[1-9][0-9]*", minor)), "invalid InterPro minor release")
    for value, limit, label in ((page_size, 200, "page size"), (max_pages, 100, "page limit"),
                                (attempts, 5, "attempts"), (timeout, 60, "timeout")):
        require(type(value) is int and 1 <= value <= limit, f"invalid {label}")
    reference, registry_sha = selected_reference(registry, protein_id)
    output = output.absolute()
    require(not output.is_symlink(), "symlink output is not allowed")
    resolved = output.resolve()
    require(resolved.is_relative_to(RAW_ROOT.resolve()) and resolved != RAW_ROOT.resolve(),
            "output must be a new directory below data/raw/interpro_native")
    require(not output.exists(), "output already exists; replay it or choose a new directory")
    producer = {name: sha256((ROOT / "scripts" / name).read_bytes()) for name in PRODUCER_FILES}
    payload = {
        "schema_version": SCHEMA_VERSION, "scope": "Native acquisition only; no qualification",
        "protein_id": protein_id, "reference": reference,
        "reference_sha256": digest(reference), "registry_path": str(registry.resolve()),
        "registry_sha256": registry_sha, "output": str(resolved),
        "interpro_release": release, "interpro_minor_release": minor,
        "page_size": page_size, "max_pages": max_pages,
        "attempts": attempts, "timeout_seconds_per_operation": timeout,
        "max_body_bytes": 4_000_000, "producer_sha256": producer,
        "catalog_url": CATALOG_URL,
        "protein_url": BASE + f"protein/uniprot/{accession}/?format=json",
        "entries_url": BASE + f"entry/all/protein/uniprot/{accession}/"
                               f"?page_size={page_size}&format=json",
    }
    return {**payload, "plan_sha256": digest(payload)}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise NativeCaptureError("redirect refused; exact native endpoint required")


def get_response(url: str, *, attempts: int, timeout: int, opener=None,
                 sleep=time.sleep) -> tuple[ResponseCapture, list[dict]]:
    """Bound retries; headers and bytes always originate from the same GET."""
    opener = opener or build_opener(NoRedirect())
    errors = []
    for attempt in range(attempts):
        request = Request(url, method="GET", headers={
            "Accept": "application/json", "Accept-Encoding": "identity",
            "User-Agent": "ProteinTraitsMech-native-InterPro/1.0",
        })
        try:
            with opener.open(request, timeout=timeout) as response:
                return read_response(request, response), errors
        except HTTPError as exc:
            status = exc.code
            exc.close()
            if status not in RETRY_STATUS:
                raise
            errors.append({"attempt": attempt + 1, "http_status": status})
        except (URLError, TimeoutError, ConnectionError, http.client.IncompleteRead) as exc:
            errors.append({"attempt": attempt + 1, "error_type": type(exc).__name__,
                           "message": str(exc)})
        if attempt + 1 < attempts:
            sleep(2 ** attempt)
    raise NativeCaptureError(f"GET failed after {attempts} attempts: {url}; {errors}")


def write_new(path: Path, raw: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def save_capture(directory: Path, name: str, capture: ResponseCapture, attempts: list) -> dict:
    body_file, receipt_file = f"{name}.body.json", f"{name}.capture.json"
    metadata = asdict(capture)
    del metadata["body"]
    metadata.update(body_file=body_file, body_sha256=sha256(capture.body),
                    body_bytes=len(capture.body), failed_attempts=attempts)
    receipt = json_bytes(metadata)
    write_new(directory / body_file, capture.body)
    write_new(directory / receipt_file, receipt)
    return {body_file: sha256(capture.body), receipt_file: sha256(receipt)}


def saved_capture(directory: Path, name: str, files: dict) -> ResponseCapture:
    def read(filename):
        path = directory / filename
        require(not path.is_symlink() and path.is_file(), "missing regular capture file")
        raw = path.read_bytes()
        require(sha256(raw) == files.get(filename), "saved capture digest mismatch")
        return raw

    body_file = f"{name}.body.json"
    raw = read(body_file)
    metadata = strict_json(read(f"{name}.capture.json"))
    require(metadata.pop("body_file") == body_file, "saved body path mismatch")
    require(metadata.pop("body_sha256") == sha256(raw), "saved body checksum mismatch")
    require(metadata.pop("body_bytes") == len(raw), "saved body length mismatch")
    require(isinstance(metadata.pop("failed_attempts"), list), "missing attempt history")
    metadata["headers"] = tuple(tuple(pair) for pair in metadata["headers"])
    return ResponseCapture(body=raw, **metadata)


def replay_manifest(directory: Path, manifest: dict) -> dict:
    """Derive discovery again from the immutable raw files, never the projection."""
    require(manifest.get("schema_version") == SCHEMA_VERSION, "unsupported bundle version")
    plan = manifest["plan"]
    require(digest({k: v for k, v in plan.items() if k != "plan_sha256"})
            == plan["plan_sha256"], "request plan digest mismatch")
    require(digest(plan["reference"]) == plan["reference_sha256"], "reference digest mismatch")
    require(not validate_protein_reference(plan["reference"], path=directory, line=1),
            "invalid saved ProteinReference")
    page_count = manifest["page_count"]
    require(type(page_count) is int and 1 <= page_count <= plan["max_pages"] <= 100,
            "invalid saved page count")
    names = ["catalog-before", "protein", *[f"page-{i:04d}" for i in range(page_count)],
             "catalog-after"]
    expected_files = {f"{name}.{kind}.json" for name in names for kind in ("body", "capture")}
    require(set(manifest["files"]) == expected_files, "incomplete saved capture inventory")
    captures = {name: saved_capture(directory, name, manifest["files"]) for name in names}
    result = discover_capture_bundle(
        captures["catalog-before"], [captures[f"page-{i:04d}"] for i in range(page_count)],
        captures["protein"], captures["catalog-after"], plan["reference"],
        release=plan["interpro_release"], minor=plan["interpro_minor_release"],
        page_size=plan["page_size"], max_pages=plan["max_pages"],
    )
    require(result == manifest["result"], "saved discovery does not replay")
    return result


def replay_bundle(directory: Path, *, expected_sha256: str) -> dict:
    path = directory / "bundle.json"
    require(not path.is_symlink() and path.is_file(), "complete bundle required")
    raw = path.read_bytes()
    require(sha256(raw) == expected_sha256, "bundle digest mismatch")
    return replay_manifest(directory, strict_json(raw))


def acquire(plan: dict, *, opener=None, sleep=time.sleep) -> dict:
    """Execute a validated plan; publish a complete immutable bundle last."""
    fresh = request_plan(
        Path(plan["registry_path"]), plan["protein_id"], Path(plan["output"]),
        release=plan["interpro_release"], minor=plan["interpro_minor_release"],
        page_size=plan["page_size"], max_pages=plan["max_pages"],
        attempts=plan["attempts"], timeout=plan["timeout_seconds_per_operation"],
    )
    require(fresh == plan, "request plan changed; rerun the dry run")
    output = Path(plan["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()  # Exclusive ownership; never replace an existing acquisition.
    files = {}

    def capture(name, url, path, page_size=None):
        url_key(url, path, page_size)  # Validate before executing pagination URLs.
        cap, failed_attempts = get_response(url, attempts=plan["attempts"],
                                           timeout=plan["timeout_seconds_per_operation"],
                                           opener=opener, sleep=sleep)
        files.update(save_capture(output, name, cap, failed_attempts))
        value, _ = read_capture(cap, url, path, plan["interpro_release"],
                                plan["interpro_minor_release"], page_size)
        return cap, value

    try:
        write_new(output / "request-plan.json", json_bytes(plan))
        before, _ = capture("catalog-before", CATALOG_URL, "/interpro/api/")
        accession = plan["protein_id"].split(":", 1)[1]
        protein, _ = capture("protein", plan["protein_url"],
                             f"/interpro/api/protein/uniprot/{accession}/")
        pages, visited = [], set()
        url = plan["entries_url"]
        entry_path = f"/interpro/api/entry/all/protein/uniprot/{accession}/"
        while url is not None:
            require(len(pages) < plan["max_pages"], "page limit exceeded")
            key = url_key(url, entry_path, plan["page_size"])
            require(key not in visited, "pagination cycle")
            visited.add(key)
            cap, value = capture(f"page-{len(pages):04d}", url, entry_path, plan["page_size"])
            pages.append(cap)
            require("next" in value, "missing pagination state")
            url = value["next"]
        after, _ = capture("catalog-after", CATALOG_URL, "/interpro/api/")
        result = discover_capture_bundle(before, pages, protein, after, plan["reference"],
                                         release=plan["interpro_release"],
                                         minor=plan["interpro_minor_release"],
                                         page_size=plan["page_size"], max_pages=plan["max_pages"])
        manifest = {"schema_version": SCHEMA_VERSION, "plan": plan,
                    "page_count": len(pages), "files": files, "result": result}
        replay_manifest(output, manifest)
        raw = json_bytes(manifest)
        write_new(output / ".bundle.part", raw)
        os.rename(output / ".bundle.part", output / "bundle.json")
        return {"output": str(output), "bundle_sha256": sha256(raw),
                "capture_id": result["capture_id"], "pages": len(pages),
                "entries": len(result["discovery"]["source_entries"]),
                "scope": "Acquisition and replay complete; no qualified coordinates"}
    except BaseException as exc:
        write_new(output / "failure.json", json_bytes({"error_type": type(exc).__name__,
                   "message": str(exc), "complete_bundle": False, "saved_files": files}))
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--protein", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expect-release", required=True)
    parser.add_argument("--expect-minor", required=True)
    parser.add_argument("--page-size", type=int, default=200)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--request-plan", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = request_plan(args.registry, args.protein, args.out, release=args.expect_release,
                            minor=args.expect_minor, page_size=args.page_size,
                            max_pages=args.max_pages, attempts=args.attempts, timeout=args.timeout)
        if args.apply:
            require(args.request_plan is not None, "--apply requires the reviewed --request-plan")
            require(strict_json(args.request_plan.read_bytes()) == plan,
                    "request plan changed; rerun the dry run")
            print(json.dumps(acquire(plan), indent=2))
        else:
            require(args.request_plan is None, "--request-plan is only used with --apply")
            print(json.dumps(plan, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Native InterPro capture refused: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
