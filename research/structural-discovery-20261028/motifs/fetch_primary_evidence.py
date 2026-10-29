#!/usr/bin/env python3
"""Retrieve two bounded primary-source evidence artifacts, retaining provenance.

This is evidence collection, not provider-panel ingestion. Files stay beside
this helper; archive contents are listed/selected in memory, never extracted.
"""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
SOURCES = {
    "motivated-proteins-2009-supplement5.zip":
        "https://media.springernature.com/original/springer-static/esm/art%3A10.1186%2F1471-2105-10-60/MediaObjects/12859_2008_2790_MOESM5_ESM.zip",
    "natcomm-2022-immunoglobulin.xml":
        "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9530121/fullTextXML",
}

def main():
    rows = []
    for name, url in SOURCES.items():
        target = HERE / name
        if target.exists():
            raise FileExistsError(target)
        request = urllib.request.Request(url, headers={"User-Agent": "ProteinTraitsMech-bounded-evidence-review/1.0"})
        with urllib.request.urlopen(request, timeout=40) as response:
            data = response.read(5_000_001)
            if len(data) > 5_000_000:
                raise ValueError("Unexpectedly large bounded artifact")
            row = {"url": url, "resolved_url": response.url,
                   "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "content_type": response.headers.get("Content-Type"),
                   "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "file": name}
        target.write_bytes(data)
        if name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as bundle:
                row["archive_members"] = bundle.namelist()
        rows.append(row)
    (HERE / "primary-artifact-retrieval.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps(rows, indent=2))

if __name__ == "__main__":
    main()
