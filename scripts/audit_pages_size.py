#!/usr/bin/env python3
"""Fail when a built Pages artifact exceeds documented size/file-count budgets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE = ROOT / "docs"
DEFAULT_BUDGETS = ROOT / "conf" / "pages_budgets.json"


def measure(site: Path) -> dict[str, int]:
    data = site / "data"
    site_files = [path for path in site.rglob("*") if path.is_file()]
    browse = [path for path in data.glob("records.*.json") if path.is_file()]
    detail = [path for path in (data / "detail").glob("*.json") if path.is_file()]
    sizes = {path: path.stat().st_size for path in site_files}
    return {
        "site_total_bytes": sum(sizes.values()),
        "generated_file_count": len(site_files),
        "browse_index_total_bytes": sum(sizes[path] for path in browse),
        "largest_browse_shard_bytes": max((sizes[path] for path in browse), default=0),
        "detail_total_bytes": sum(sizes[path] for path in detail),
        "largest_detail_bucket_bytes": max((sizes[path] for path in detail), default=0),
        "browse_shards": len(browse),
        "detail_buckets": len(detail),
    }


def audit(site: Path, budgets: dict[str, int]) -> tuple[dict[str, int], list[str]]:
    metrics = measure(site)
    failures = []
    if metrics["browse_shards"] == 0:
        failures.append("no browse record shards found")
    if metrics["detail_buckets"] == 0:
        failures.append("no detail buckets found")
    for name, limit in budgets.items():
        actual = metrics.get(name)
        if actual is None:
            failures.append(f"unknown budget metric: {name}")
        elif actual > limit:
            failures.append(f"{name}: {actual:,} > {limit:,}")
    return metrics, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE)
    parser.add_argument("--budgets", type=Path, default=DEFAULT_BUDGETS)
    args = parser.parse_args()
    if not args.site.is_dir():
        parser.error(f"site directory does not exist: {args.site}")
    try:
        budgets = json.loads(args.budgets.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"could not read budgets from {args.budgets}: {exc}")
    if not isinstance(budgets, dict) or not all(
        isinstance(key, str) and isinstance(value, int) and value >= 0
        for key, value in budgets.items()
    ):
        parser.error("budgets must be a JSON object of non-negative integer limits")

    metrics, failures = audit(args.site, budgets)
    print("Pages artifact budget report:")
    for name, limit in budgets.items():
        actual = metrics.get(name, 0)
        state = "FAIL" if actual > limit else "OK"
        print(f"  {state:4s}  {name:36s} {actual:>15,} / {limit:,}")
    print(f"  INFO  {'browse_shards':36s} {metrics['browse_shards']:>15,}")
    print(f"  INFO  {'detail_buckets':36s} {metrics['detail_buckets']:>15,}")
    if failures:
        print("\nFAIL: " + "; ".join(failures))
        return 1
    print("\nOK: Pages artifact is within all budgets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
