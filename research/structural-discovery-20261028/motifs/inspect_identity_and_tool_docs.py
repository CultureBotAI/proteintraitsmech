#!/usr/bin/env python3
"""Bounded official-source reads for identity and invocation verification only."""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent
SOURCES = {
    "so-20260807.obo": "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.obo",
    "so-license.txt": "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/LICENSE",
    "hbplus-official-docs.tar.gz": "https://raw.githubusercontent.com/RomanLas/HBPLUS/main/docs.tar.gz",
}

def main():
    rows = []
    for name, url in SOURCES.items():
        target = HERE / name
        if target.exists():
            raise FileExistsError(target)
        with urllib.request.urlopen(url, timeout=35) as response:
            data = response.read(5_000_001)
            if len(data) > 5_000_000:
                raise ValueError("Unexpectedly large artifact")
            row = {"url": url, "resolved_url": response.url,
                   "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "file": name}
        target.write_bytes(data)
        if name.endswith(".obo"):
            blocks = data.decode().split("[Term]")
            row["identity_blocks"] = [b.strip() for b in blocks if re.search(r"^id: SO:(0000912|0001141)\s*$", b, re.M)]
            row["beta_arch_name_or_synonym_hits"] = [b.strip() for b in blocks if re.search(r"^(?:name|synonym):.*(?:beta|β)[_ -]arch\b", b, re.M|re.I)]
        if name.endswith(".tar.gz"):
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as bundle:
                row["members"] = bundle.getnames()
                extracts = []
                for member in bundle.getmembers():
                    if member.isfile() and member.name.lower().endswith((".html", ".man", ".txt")):
                        content = bundle.extractfile(member).read().decode(errors="replace")
                        if any(word in content.lower() for word in ("command-line", "hbplus.exe", "quick instructions")):
                            extracts.append({"member": member.name, "text": content})
                (HERE / "hbplus-official-doc-text.json").write_text(json.dumps(extracts, indent=2) + "\n")
        rows.append(row)
    (HERE / "identity-tool-doc-retrieval.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps([{k:v for k,v in r.items() if k != "members"} for r in rows], indent=2))

if __name__ == "__main__":
    main()
