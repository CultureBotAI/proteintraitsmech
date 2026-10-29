#!/usr/bin/env python3
"""Retain bounded public primary sources already inspected for canary review."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

OUT = Path(__file__).resolve().parent
SOURCES = [
    ("caver2012-plos-primary.html", "https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002708"),
    ("rcsb-1cqw-entry.json", "https://data.rcsb.org/rest/v1/core/entry/1CQW"),
    ("caver-biotools-registry.json", "https://bio.tools/api/tool/caver/?format=json"),
]
result = {"timestamp": datetime.now(timezone.utc).isoformat(), "sources": []}
for name, url in SOURCES:
    path = OUT / name
    assert not path.exists(), "Do not overwrite retained evidence"
    item = {"url": url, "path": str(path)}
    try:
        request = Request(url, headers={"User-Agent": "ProteinTraitsMech read-only scientific source verification"})
        with urlopen(request, timeout=30) as response:
            body = response.read(5_000_001)
            assert len(body) <= 5_000_000, "Source exceeds bounded fetch"
            item["resolved_url"] = response.url
            item["content_type"] = response.headers.get("Content-Type")
        with path.open("xb") as stream:
            stream.write(body)
        item.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    except Exception as exc:
        item["error"] = str(exc)
    result["sources"].append(item)
for name in ("caver-discovery-userguide.pdf", "caver-discovery-userguide.txt"):
    original = Path("/tmp") / name
    body = original.read_bytes()
    retained = OUT / name
    with retained.open("xb") as stream:
        stream.write(body)
    result["sources"].append({"url": "https://www.caver.cz/fil/download/manual/caver_userguide.pdf", "copied_from": str(original), "path": str(retained), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
with (OUT / "canary-source-retention-20261029T0704Z.json").open("x") as stream:
    json.dump(result, stream, indent=2)
    stream.write("\n")
print(json.dumps(result, indent=2))
