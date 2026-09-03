#!/usr/bin/env python3
"""Fail when a built Pages artifact exceeds documented size/file-count budgets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE = ROOT / "docs"
DEFAULT_BUDGETS = ROOT / "conf" / "pages_budgets.json"
# Fraction of a budget at which a metric is reported as WARN rather than OK. The
# largest budget, site_total_bytes, is set to GitHub Pages' hard 1 GB ceiling, so
# without a band the first signal would be a failed deploy at the platform limit.
DEFAULT_WARN_FRACTION = 0.8


def measure(site: Path) -> dict[str, int]:
    """Measure the built site against the budgeted dimensions.

    `site_file_count` and `site_total_bytes` cover every file the site serves, not
    only what build_docs_index.py wrote this run: GitHub Pages hosts and bills for
    all of it, including committed sidecars from other build steps (corpus_map,
    neighbors, chebi) and Jekyll's rendered HTML. Naming the count for what it
    measures matters — as `generated_file_count` it read as a builder-output count
    while reporting roughly twice that.
    """
    data = site / "data"
    site_files = [path for path in site.rglob("*") if path.is_file()]
    browse = [path for path in data.glob("records.*.json") if path.is_file()]
    detail = [path for path in (data / "detail").glob("*.json") if path.is_file()]
    sizes = {path: path.stat().st_size for path in site_files}
    return {
        "site_total_bytes": sum(sizes.values()),
        "site_file_count": len(site_files),
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


def near_budget(metrics: dict[str, int], budgets: dict[str, int],
                fraction: float) -> set[str]:
    """Budgeted metrics that are within `fraction` of their limit without exceeding
    it. Exceeding is a failure, not a warning, so the two sets never overlap."""
    near = set()
    for name, limit in budgets.items():
        actual = metrics.get(name)
        if actual is None or limit <= 0 or actual > limit:
            continue
        if actual >= fraction * limit:
            near.add(name)
    return near


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE)
    parser.add_argument("--budgets", type=Path, default=DEFAULT_BUDGETS)
    parser.add_argument(
        "--warn-fraction",
        type=float,
        default=DEFAULT_WARN_FRACTION,
        help="report WARN at this fraction of a budget (0 < f <= 1); still exits 0",
    )
    args = parser.parse_args()
    if not 0 < args.warn_fraction <= 1:
        parser.error(f"--warn-fraction must be in (0, 1]: {args.warn_fraction}")
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
    near = near_budget(metrics, budgets, args.warn_fraction)
    print("Pages artifact budget report:")
    for name, limit in budgets.items():
        actual = metrics.get(name)
        if actual is None:
            # audit() already recorded this as a failure; the per-line report must
            # not read OK for the one metric that is broken.
            print(f"  FAIL  {name:36s} {'unmeasured':>15s} / {limit:,}")
            continue
        state = "FAIL" if actual > limit else "WARN" if name in near else "OK"
        print(f"  {state:4s}  {name:36s} {actual:>15,} / {limit:,}")
    print(f"  INFO  {'browse_shards':36s} {metrics['browse_shards']:>15,}")
    print(f"  INFO  {'detail_buckets':36s} {metrics['detail_buckets']:>15,}")
    if near:
        print(
            f"\nWARN: within {args.warn_fraction:.0%} of budget: "
            + ", ".join(sorted(near))
        )
    if failures:
        print("\nFAIL: " + "; ".join(failures))
        return 1
    if not near:
        print("\nOK: Pages artifact is within all budgets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
