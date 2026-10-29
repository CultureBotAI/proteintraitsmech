#!/usr/bin/env python3
"""2026-10-29: retain exact primary inputs for the parent-owned discovery goal.

Related coordination: #1200, #1201, #1204; no issue closure implied.
Inputs: bounded public PNAS article and RCSB7WLI metadata URLs below.
Outputs: new evidence files and source-retrieval JSON in this script's directory.
No /tmp inputs, corpus edits, provider panels, detector execution or Git writes.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
OUT = Path(__file__).resolve().parent
sources = [
    ("fenestration-pnas-2401591121.html", "https://www.pnas.org/doi/10.1073/pnas.2401591121"),
    ("fenestration-rcsb-7wli-entry.json", "https://data.rcsb.org/rest/v1/core/entry/7WLI"),
]
result = {"timestamp": datetime.now(timezone.utc).isoformat(), "goal": "Parent-owned structural discovery goal; #1200/#1201/#1204 coordination", "tmp_inputs": [], "sources": []}
for filename, url in sources:
    path = OUT / filename
    assert not path.exists(), "Refuse overwriting evidence"
    item = {"url": url, "path": str(path)}
    try:
        request = Request(url, headers={"User-Agent": "ProteinTraitsMech bounded scientific review"})
        with urlopen(request, timeout=30) as response:
            body = response.read(5_000_001)
            assert len(body) <= 5_000_000
            item["resolved_url"] = response.url
            item["content_type"] = response.headers.get("Content-Type")
        with path.open("xb") as stream:
            stream.write(body)
        item.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    except Exception as exc:
        item["error"] = str(exc)
    result["sources"].append(item)
with (OUT / "fenestration-source-retrieval.json").open("x") as stream:
    json.dump(result, stream, indent=2)
    stream.write("\n")
print(json.dumps(result, indent=2))
