#!/usr/bin/env python3
"""Read-only GitHub coordination snapshot for the structural discovery goal.

Date: 2026-10-29 UTC (2026-10-28 America/Los_Angeles).
Reference: standalone structural-discovery goal, thread
01a183c4-7ea5-7943-9580-927303425d81; follow-up context PTM issues #1200/#1201.
Inputs: authenticated gh CLI; repository argument; current GitHub main, open PRs
and open issues. Outputs: timestamped JSON in --output; no remote mutations.
The snapshot is advisory coordination evidence, never an ID reservation.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess


def gh(*args: str):
    return json.loads(subprocess.check_output(["gh", *args], text=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="CultureBotAI/proteintraitsmech")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prs = gh("pr", "list", "--repo", args.repo, "--state", "open", "--limit", "1000",
             "--json", "number,title,body,headRefName,headRefOid,url")
    issues = gh("issue", "list", "--repo", args.repo, "--state", "open", "--limit", "1000",
                "--json", "number,title,body,url")
    if len(prs) == 1000 or len(issues) == 1000:
        raise SystemExit("Listing reached explicit cap; do not claim complete coverage")

    def files(pr):
        pages = gh("api", "--paginate", "--slurp",
                   f"repos/{args.repo}/pulls/{pr['number']}/files?per_page=100")
        return {**pr, "files": [f for page in pages for f in page]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        enriched = list(pool.map(files, prs))
    main_sha = gh("api", f"repos/{args.repo}/commits/main")["sha"]
    report = {
        "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": args.repo,
        "main_sha": main_sha,
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "All open PR and issue titles/bodies up to explicit 1000 cap; paginated PR file patches. Private/unpushed work is not remotely observable.",
        "coordination_limits": "Snapshot only; not a durable ID reservation, lock, or write authorization.",
        "pull_requests": enriched,
        "issues": issues,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"main_sha": main_sha, "prs": len(prs), "issues": len(issues),
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
