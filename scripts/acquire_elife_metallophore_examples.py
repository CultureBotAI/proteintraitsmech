#!/usr/bin/env python3
"""Acquire a bounded source-member panel; dry-run unless --apply is supplied.

Discovery queries only choose accessions. Every candidate is subsequently fetched
by exact accession with its UniProt release header and complete response retained.
Only ignored staging is written; this script never writes canonical examples.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from elife_metallophores import (
    DOMAIN_MODELS, RAW, digest, sha256, source_facts, verified_archive, write_jsonl,
)


def fetch(url: str, cache: Path) -> dict:
    path = cache / (sha256(url.encode()) + ".json")
    if path.exists():
        result = json.loads(path.read_text())
        if result["request_url"] != url or result["body_sha256"] != sha256(result["body"].encode()):
            raise ValueError("corrupt acquisition cache")
        return result
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
        headers = {k.lower(): v for k, v in response.headers.items()}
        if not re.fullmatch(r"\d{4}_\d{2}", headers.get("x-uniprot-release", "")):
            raise ValueError("response has no valid UniProt release header")
        result = {"request_url": url, "resolved_url": response.url, "headers": headers,
                  "body": body, "body_sha256": sha256(body.encode())}
    cache.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True))
    return result


def panel(members: list[dict], limit: int) -> list[dict]:
    groups = {}
    for row in members:
        if "source_accession" not in row:
            continue
        if row["model"] in DOMAIN_MODELS and "source_interval" not in row:
            continue
        groups.setdefault(row["model"], []).append(row)
    selected = []
    for model, rows in groups.items():
        rows.sort(key=lambda r: (
            (model in {"GrbE", "VbsL"} and r["source_kind"] != "bgc_annotation"),
            not r["source_header"].startswith("sp|"),
            r["source_accession"] not in {"Q9I185", "Q9I188", "A9CFJ0", "Q7CT24"},
            r["source_namespace"] != "UniProtKB",
        ))
        selected.extend(rows[:limit])
    return selected


def acquire(selected: list[dict], cache: Path, expected_release: str) -> list[dict]:
    outputs = []
    for row in selected:
        accession = row["source_accession"]
        result = {"candidate_id": row["candidate_id"], "model": row["model"],
                  "source_accession": accession, "responses": []}
        try:
            if row["source_namespace"] == "UniProtKB":
                accessions = [accession]
            else:
                namespace = row["source_namespace"].lower()
                query = f"xref:{namespace}-{accession}"
                url = "https://rest.uniprot.org/uniprotkb/search?" + urllib.parse.urlencode(
                    {"query": query, "format": "json", "size": 5})
                discovery = fetch(url, cache)
                result["discovery_response_sha256"] = digest(discovery)
                entries = json.loads(discovery["body"]).get("results", [])
                accessions = [e["primaryAccession"] for e in entries]
            for acc in accessions:
                response = fetch(f"https://rest.uniprot.org/uniprotkb/{acc}.json", cache)
                release = response["headers"]["x-uniprot-release"]
                if release != expected_release:
                    raise ValueError(f"release {release} differs from expected {expected_release}")
                if json.loads(response["body"]).get("primaryAccession") != acc:
                    raise ValueError(f"exact accession {acc} redirected or obsolete")
                result["responses"].append(response)
            if not accessions:
                result["issue"] = "no exact database cross-reference found"
        except (ValueError, OSError) as error:
            result["issue"] = str(error)
        outputs.append(result)
        print(row["model"], accession, len(result["responses"]), result.get("issue", ""), flush=True)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--per-model", type=int, default=3)
    parser.add_argument("--expect-release", required=True)
    parser.add_argument("--raw", type=Path, default=RAW)
    args = parser.parse_args()
    if not 1 <= args.per_model <= 10:
        parser.error("--per-model must be between 1 and 10")
    with verified_archive(args.raw / "nrp-metallophore-SI.zip") as archive:
        _, members = source_facts(archive)
    selected = panel(members, args.per_model)
    if not args.apply:
        print(json.dumps({"selected": [{k: r[k] for k in ("candidate_id", "model", "source_accession")}
                                       for r in selected], "expect_release": args.expect_release}))
        return 0
    results = acquire(selected, args.raw / "uniprot", args.expect_release)
    write_jsonl(args.raw / "acquired_examples.jsonl", results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
