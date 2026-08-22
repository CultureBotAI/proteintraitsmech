#!/usr/bin/env python3
"""Report current corpus and generated-site metrics as deterministic JSON."""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
DOCS_DATA = ROOT / "docs" / "data"

AXIS = re.compile(rb"^trait_axis:[ \t]*[\"']?([A-Z_]+)", re.M)
STATUS = re.compile(rb"^mapping_status:[ \t]*[\"']?([A-Z_]+)", re.M)
GRAPH_BLOCK = re.compile(rb"^causal_graphs:[ \t]*(?:#.*)?$", re.M)
GRAPH_ID = re.compile(rb"^[ \t]*- graph_id:", re.M)
RG_FIELDS = (
    r"^(?:trait_axis|mapping_status):[ \t]*[\"']?[A-Z_]+"
    r"|^causal_graphs:[ \t]*(?:#.*)?$|^[ \t]*- graph_id:"
)


def _record_metrics(path: Path) -> tuple[str, str, bool, int]:
    raw = path.read_bytes()
    axis = AXIS.search(raw)
    status = STATUS.search(raw)
    return (
        axis.group(1).decode("ascii") if axis else "_MISSING",
        status.group(1).decode("ascii") if status else "_MISSING",
        GRAPH_BLOCK.search(raw) is not None,
        len(GRAPH_ID.findall(raw)),
    )


def _record_count(traits: Path) -> int:
    return sum(
        name.endswith(".yaml")
        for _directory, _subdirs, files in os.walk(traits)
        for name in files
    )


def _metrics_from_rg_lines(lines, records: int) -> dict:
    """Aggregate ripgrep's contiguous per-file matches with per-record semantics."""
    axes: collections.Counter[str] = collections.Counter()
    statuses: collections.Counter[str] = collections.Counter()
    records_with_graphs = 0
    graphs = 0
    current_path: bytes | None = None
    current_axis: str | None = None
    current_status: str | None = None
    current_has_graphs = False
    current_graphs = 0

    def finish_record() -> None:
        nonlocal records_with_graphs, graphs
        if current_path is None:
            return
        if current_axis is not None:
            axes[current_axis] += 1
        if current_status is not None:
            statuses[current_status] += 1
        records_with_graphs += int(current_has_graphs)
        graphs += current_graphs

    # ripgrep emits all matches for one file contiguously. Keep only the first axis and
    # status match, like re.search in the Python backend, while graph IDs remain a count.
    for raw in lines:
        path, separator, line = raw.partition(b"\0")
        if not separator:
            continue
        if path != current_path:
            finish_record()
            current_path = path
            current_axis = None
            current_status = None
            current_has_graphs = False
            current_graphs = 0
        if current_axis is None and (match := AXIS.match(line)):
            current_axis = match.group(1).decode("ascii")
        elif current_status is None and (match := STATUS.match(line)):
            current_status = match.group(1).decode("ascii")
        elif GRAPH_BLOCK.match(line):
            current_has_graphs = True
        elif GRAPH_ID.match(line):
            current_graphs += 1
    finish_record()

    missing_axes = records - sum(axes.values())
    missing_statuses = records - sum(statuses.values())
    if missing_axes > 0:
        axes["_MISSING"] = missing_axes
    if missing_statuses > 0:
        statuses["_MISSING"] = missing_statuses
    return {
        "records": records,
        "by_axis": dict(sorted(axes.items())),
        "by_mapping_status": dict(sorted(statuses.items())),
        "records_with_causal_graphs": records_with_graphs,
        "causal_graphs": graphs,
    }


def _corpus_metrics_rg(traits: Path) -> dict | None:
    """Use one native streaming scan when ripgrep is available.

    `--null` separates each filename from its matching line without assuming paths cannot
    contain colons. The required axis/status fields make missing-field counts derivable
    without retaining hundreds of thousands of paths in memory.
    """
    rg = shutil.which("rg")
    if not rg:
        return None
    process = subprocess.Popen(
        [
            rg,
            "--no-heading",
            "--no-line-number",
            "--color=never",
            "--null",
            "-g",
            "*.yaml",
            RG_FIELDS,
            str(traits),
        ],
        stdout=subprocess.PIPE,
    )
    assert process.stdout is not None
    metrics = _metrics_from_rg_lines(process.stdout, _record_count(traits))
    returncode = process.wait()
    if returncode not in (0, 1):
        raise subprocess.CalledProcessError(returncode, process.args)

    return metrics


def _corpus_metrics_python(traits: Path, workers: int | None) -> dict:
    """Portable fallback for environments without ripgrep."""
    paths = [path for path in traits.rglob("*.yaml") if path.is_file()]
    axes: collections.Counter[str] = collections.Counter()
    statuses: collections.Counter[str] = collections.Counter()
    records_with_graphs = 0
    graphs = 0
    worker_count = workers or min(32, (os.cpu_count() or 1) + 4)
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        for axis, status, has_graphs, graph_count in pool.map(
            _record_metrics, paths, chunksize=256
        ):
            axes[axis] += 1
            statuses[status] += 1
            records_with_graphs += int(has_graphs)
            graphs += graph_count
    return {
        "records": len(paths),
        "by_axis": dict(sorted(axes.items())),
        "by_mapping_status": dict(sorted(statuses.items())),
        "records_with_causal_graphs": records_with_graphs,
        "causal_graphs": graphs,
    }


def _docs_metrics(root: Path) -> dict:
    files = sorted(path for path in root.rglob("*.json") if path.is_file()) if root.is_dir() else []
    shards = [path for path in files if path.name.startswith("records.")]
    details = [path for path in files if path.parent.name == "detail"]
    sizes = {path: path.stat().st_size for path in files}
    return {
        "json_files": len(files),
        "bytes": sum(sizes.values()),
        "record_shards": len(shards),
        "largest_record_shard_bytes": max((sizes[path] for path in shards), default=0),
        "detail_buckets": len(details),
        "detail_bytes": sum(sizes[path] for path in details),
        "largest_detail_bucket_bytes": max((sizes[path] for path in details), default=0),
    }


def collect_stats(traits: Path, docs_data: Path, workers: int | None = None) -> dict:
    corpus = _corpus_metrics_rg(traits) or _corpus_metrics_python(traits, workers)
    return {
        "schema_version": 1,
        "corpus": corpus,
        "artifacts": {"docs_data": _docs_metrics(docs_data)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traits", type=Path, default=TRAITS)
    parser.add_argument("--docs-data", type=Path, default=DOCS_DATA)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--output", default="-", help="JSON path, or - for stdout")
    args = parser.parse_args()
    if not args.traits.is_dir():
        parser.error(f"traits directory does not exist: {args.traits}")
    if args.workers is not None and args.workers < 1:
        parser.error("--workers must be at least 1")

    rendered = json.dumps(
        collect_stats(args.traits, args.docs_data, args.workers), indent=2, sort_keys=True
    ) + "\n"
    if args.output == "-":
        print(rendered, end="")
    else:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
