"""Materialize historical review blobs in the isolated partial clone.

Purpose/date/issues: native provenance environment preparation, 2026-10-31,
PR1205 and #1206. Inputs: all existing native review.yaml source git_commit
pins, including hidden/ignored bundles, and this checkout's configured origin.
Outputs: Git objects (never refs or worktree files) plus a new timestamped JSON
receipt beside this retained helper. Native record_review.py intentionally sets
GIT_NO_LAZY_FETCH=1; this explicit preparation does not weaken that validator.
Historical absence/mismatch is an error. Requires network if a blob is missing;
not a claim that remote historical objects will remain available indefinitely.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main() -> None:
    inputs = []
    blobs = {}
    for path in sorted((ROOT / "reviews/structured").rglob("review.yaml")):
        raw = path.read_bytes()
        review = yaml.safe_load(raw)
        source = review["source"]
        if source["state"] != "git_commit":
            continue
        revision = source["git_revision"]
        assert re.fullmatch(r"[0-9a-f]{40}", revision), revision
        inputs.append({"path": str(path.relative_to(ROOT)),
                       "sha256": hashlib.sha256(raw).hexdigest()})
        for item in source["inputs"]:
            relative = Path(item["path"])
            assert not relative.is_absolute() and ".." not in relative.parts
            key = revision + ":" + item["path"]
            expected = blobs.setdefault(key, item["sha256"])
            assert expected == item["sha256"], key
    materialized = []
    environment = {**os.environ, "GIT_NO_LAZY_FETCH": "0", "GIT_TERMINAL_PROMPT": "0"}
    for key, expected in sorted(blobs.items()):
        result = subprocess.run(["git", "cat-file", "blob", key], cwd=ROOT,
                                env=environment, capture_output=True, check=True)
        observed = hashlib.sha256(result.stdout).hexdigest()
        assert observed == expected, key
        materialized.append({"git_blob": key, "sha256": observed})
    now = dt.datetime.now(dt.timezone.utc)
    report = {"created_utc": now.isoformat(), "issue": 1206, "pr": 1205,
              "purpose": __doc__, "inputs": inputs, "materialized": materialized,
              "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "note": "Object preparation only; separate native check remains mandatory."}
    output = HERE / ("historical-blob-materialization-" + now.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"report": str(output.relative_to(ROOT)),
                      "reviews": len(inputs), "unique_verified_blobs": len(materialized)}))


if __name__ == "__main__":
    main()
