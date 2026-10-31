#!/usr/bin/env python3
"""Bounded official CAVER manual-source check, 2026-10-31, PR1205/PROV-001.

Input: one official CAVER3.01 ZIP (32MB), selected because the retained manual
documents3.0/3.01. Download at most40MiB into memory; never execute or extract
archive members to disk. Output: new metadata-only JSON alongside this helper,
with URL, time, archive/member hashes, filenames, manual-source candidates and
license/permission-marker locators. Original archive/PDF bytes stay unmodified
and are not newly redistributed by this helper. No Git/network mutation.
"""
import argparse
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

URL = "https://www.caver.cz/fil/download/caver30/301/caver_3.0.zip"
HERE = Path(__file__).resolve().parent
MAX_BYTES = 40 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    out = args.output.resolve()
    if out.parent != HERE or out.exists():
        raise SystemExit("Require new output directly inside owned provenance directory")
    result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "reference": "PR1205 PROV-001 bounded official-distribution check", "url": URL,
              "helper_sha256": digest(Path(__file__).read_bytes()), "download_limit_bytes": MAX_BYTES,
              "archive_retention": "No raw ZIP/member bytes retained; metadata-only verification, not an offline source distribution."}
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "ProteinTraitsMech-PR1205-provenance-audit"})
        with urllib.request.urlopen(req, timeout=45) as response:
            result.update(resolved_url=response.url, headers=dict(response.headers))
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Official archive exceeded bounded acquisition size")
        result.update(archive_bytes=len(data), archive_sha256=digest(data))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = []
            notices = []
            for info in archive.infolist():
                item = {"path": info.filename, "bytes": info.file_size, "compressed_bytes": info.compress_size}
                suffix = Path(info.filename).suffix.lower()
                relevant = bool(re.search(r"manual|guide|licen[cs]e|readme|copying|source|\.docx?$|\.odt$|\.tex$|\.rst$|\.md$", info.filename, re.I))
                item["manual_or_license_or_source_candidate"] = relevant
                if relevant and not info.is_dir() and info.file_size <= 6 * 1024 * 1024:
                    payload = archive.read(info)
                    item["sha256"] = digest(payload)
                    if suffix in {".txt", ".md", ".rst", ".html", ".htm", ""}:
                        content = payload.decode("utf8", "replace")
                        markers = []
                        for index, line in enumerate(content.splitlines(), 1):
                            if re.search(r"documentation|manual|redistribut|preferred|permission|source form|source code|general public license|29 June 2007", line, re.I):
                                markers.append({"line": index, "text": line[:300]})
                        if markers:
                            notices.append({"path": info.filename, "markers": markers})
                members.append(item)
            result.update(member_count=len(members), members=members, notice_markers=notices,
                          editable_document_filename_candidates=[m["path"] for m in members if Path(m["path"]).suffix.lower() in {".doc", ".docx", ".odt", ".tex", ".rst", ".md", ".rtf"}])
        result["status"] = "inspected"
    except Exception as exc:
        result.update(status="retrieval_or_inspection_failed", error=repr(exc))
    with out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"members", "notice_markers"}}, indent=2))
    if result["status"] != "inspected":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
