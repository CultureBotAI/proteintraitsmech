#!/usr/bin/env python3
"""Score and rank records by causal-graph completeness and evidence quality.

The structural ``audit_causal_graphs.py`` gate answers "is this graph internally
consistent?" This report answers "which graph-bearing YAML records need curation
first?" by assigning each record a 0-100 score and sorting the lowest scores
first.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

import audit_causal_graphs as graph_audit
from record_io import extract_block

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader


REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
FIELDS = (
    "score",
    "file",
    "identifier",
    "label",
    "trait_axis",
    "trait_category",
    "mapping_status",
    "graphs",
    "nodes",
    "edges",
    "grounded_nodes",
    "groundable_nodes",
    "grounded_groundable_nodes",
    "predicate_id_edges",
    "evidenced_edges",
    "multi_reference_edges",
    "snippet_edges",
    "described_edges",
    "documented_graphs",
    "structural_errors",
    "quality_warnings",
    "reasons",
)
_ROOT_META = re.compile(
    r"^(identifier|label|trait_axis|trait_category|mapping_status):[ \t]*(.+)[ \t]*$",
    re.M,
)
_VALID_NODE_TYPES: set[str] | None = None


@dataclass(frozen=True)
class CausalGraphScore:
    score: int
    file: str
    identifier: str = ""
    label: str = ""
    trait_axis: str = ""
    trait_category: str = ""
    mapping_status: str = ""
    graphs: int = 0
    nodes: int = 0
    edges: int = 0
    grounded_nodes: int = 0
    groundable_nodes: int = 0
    grounded_groundable_nodes: int = 0
    predicate_id_edges: int = 0
    evidenced_edges: int = 0
    multi_reference_edges: int = 0
    snippet_edges: int = 0
    described_edges: int = 0
    documented_graphs: int = 0
    structural_errors: int = 0
    quality_warnings: int = 0
    reasons: tuple[str, ...] = ()

    def row(self) -> dict[str, object]:
        row = self.__dict__.copy()
        row["reasons"] = "; ".join(self.reasons)
        return row


def _yaml_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in {".yaml", ".yml"} and not path.is_symlink():
                files.append(path)
            continue
        if path.is_dir():
            files.extend(
                candidate
                for candidate in path.rglob("*.yaml")
                if candidate.is_file() and not candidate.is_symlink()
            )
            continue
        print(f"Skipping missing path: {path}", file=sys.stderr)
    return sorted(files)


def _graph_bearing_yaml_files(paths: Iterable[Path]) -> list[Path] | None:
    rg = shutil.which("rg")
    if rg is None:
        return None

    files: set[Path] = set()
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in {".yaml", ".yml"} and not path.is_symlink():
                files.add(path)
            continue
        if not path.is_dir():
            print(f"Skipping missing path: {path}", file=sys.stderr)
            continue

        proc = subprocess.run(
            [
                rg,
                "--files-with-matches",
                "--fixed-strings",
                "--hidden",
                "--no-ignore",
                "--no-config",
                "-g",
                "*.yaml",
                "causal_graphs:",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 1:
            continue
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            return None
        files.update(Path(line) for line in proc.stdout.splitlines())
    return sorted(path for path in files if not path.is_symlink())


def candidate_files(paths: Iterable[Path], *, include_missing: bool = False) -> list[Path]:
    paths = list(paths)
    if include_missing:
        return _yaml_files(paths)
    return _graph_bearing_yaml_files(paths) or _yaml_files(paths)


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _nodes(graphs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [node for graph in graphs for node in _dicts(graph.get("nodes"))]


def _edges(graphs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [edge for graph in graphs for edge in _dicts(graph.get("edges"))]


def _references(edge: dict[str, Any]) -> set[str]:
    return {
        str(evidence["reference"])
        for evidence in _dicts(edge.get("evidence"))
        if evidence.get("reference")
    }


def _has_snippet(edge: dict[str, Any]) -> bool:
    return any(bool(evidence.get("snippet")) for evidence in _dicts(edge.get("evidence")))


def _needs_grounding(node: dict[str, Any]) -> bool:
    """Return True when an ungrounded node should reduce the grounding score.

    Some graphs legitimately need source-local nodes that do not have stable
    ontology/database CURIEs:

    * M-CSA catalytic graphs carry one described STATE node per curator-authored
      arrow-pushing step.
    * BioLiP and MetalPDB binding-site graphs carry RESIDUE nodes in PDB author
      numbering when SIFTS/UniProt residue coordinates are not asserted.
    * Rhea protein-substrate graphs can carry described RESIDUE nodes for
      reactive groups inside generic protein participants.

    Treating those local coordinates like an ungrounded protein, chemical, or
    molecular-function node pushes already-complete generated graphs to the
    bottom of the queue.
    """
    node_type = node.get("node_type")
    if node_type == "STATE" and node.get("description"):
        return False
    if node_type == "RESIDUE":
        label = str(node.get("label") or "")
        if node.get("description"):
            return False
        if "no UniProt position asserted" in label:
            return False
        if "UniProt position not established" in label:
            return False
    return True


def _ratio(points: float, numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return points * numerator / denominator


def _reason_count(label: str, numerator: int, denominator: int) -> str | None:
    if denominator == 0 or numerator == denominator:
        return None
    return f"{label}={numerator}/{denominator}"


def _record_value(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    return "" if value is None else str(value)


def _record_stub(text: str, graph_block: str | None) -> dict[str, Any]:
    metadata = "\n".join(match.group(0) for match in _ROOT_META.finditer(text))
    record = yaml.load(metadata, Loader=Loader) if metadata else {}
    if not isinstance(record, dict):
        record = {}

    if graph_block is not None:
        graph_record = yaml.load(graph_block, Loader=Loader) or {}
        if isinstance(graph_record, dict):
            record["causal_graphs"] = graph_record.get("causal_graphs")
    return record


def _valid_node_types() -> set[str]:
    global _VALID_NODE_TYPES

    if _VALID_NODE_TYPES is None:
        _VALID_NODE_TYPES = graph_audit.node_type_enum()
    return _VALID_NODE_TYPES


def score_path(path: Path) -> CausalGraphScore:
    rel = str(path)
    try:
        rel = str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        pass

    try:
        text = path.read_text(encoding="utf-8")
        graph_block = extract_block(text, "causal_graphs")
        record = _record_stub(text, graph_block)
    except Exception as exc:  # noqa: BLE001 - keep batch scoring resilient.
        return CausalGraphScore(score=0, file=rel, structural_errors=1, reasons=(str(exc),))

    graphs = _dicts(record.get("causal_graphs"))
    edges = _edges(graphs)
    nodes = _nodes(graphs)
    groundable_nodes = [node for node in nodes if _needs_grounding(node)]
    grounded_groundable_nodes = sum(1 for node in groundable_nodes if node.get("grounding"))
    predicate_id_edges = sum(1 for edge in edges if edge.get("predicate_id"))
    evidenced_edges = sum(1 for edge in edges if _dicts(edge.get("evidence")))
    multi_reference_edges = sum(1 for edge in edges if len(_references(edge)) > 1)
    snippet_edges = sum(1 for edge in edges if _has_snippet(edge))
    described_edges = sum(1 for edge in edges if edge.get("description"))
    documented_graphs = sum(
        1 for graph in graphs if graph.get("title") and graph.get("description")
    )

    errors: list[str] = []
    warnings: list[str] = []
    stats = {"records": 0, "graphs": 0, "nodes": 0, "edges": 0, "grounded": 0, "snippet_edges": 0}
    if graph_block is not None:
        graph_audit.audit_record(
            record,
            rel,
            _valid_node_types(),
            errors,
            warnings,
            stats,
        )

    if not graphs:
        score = 0
    else:
        raw_score = (
            _ratio(20, grounded_groundable_nodes, len(groundable_nodes))
            + _ratio(15, predicate_id_edges, len(edges))
            + _ratio(15, evidenced_edges, len(edges))
            + _ratio(15, snippet_edges, len(edges))
            + _ratio(15, described_edges, len(edges))
            + _ratio(10, multi_reference_edges, len(edges))
            + _ratio(10, documented_graphs, len(graphs))
        )
        score = max(0, round(raw_score) - min(40, 10 * len(errors)))

    reasons = [
        reason
        for reason in (
            f"structural_errors={len(errors)}" if errors else None,
            f"quality_warnings={len(warnings)}" if warnings else None,
            _reason_count("grounded_groundable_nodes", grounded_groundable_nodes, len(groundable_nodes)),
            _reason_count("predicate_id_edges", predicate_id_edges, len(edges)),
            _reason_count("evidenced_edges", evidenced_edges, len(edges)),
            _reason_count("multi_reference_edges", multi_reference_edges, len(edges)),
            _reason_count("snippet_edges", snippet_edges, len(edges)),
            _reason_count("described_edges", described_edges, len(edges)),
            _reason_count("documented_graphs", documented_graphs, len(graphs)),
            "no causal_graphs" if not graphs else None,
        )
        if reason is not None
    ]

    return CausalGraphScore(
        score=score,
        file=rel,
        identifier=_record_value(record, "identifier"),
        label=_record_value(record, "label"),
        trait_axis=_record_value(record, "trait_axis"),
        trait_category=_record_value(record, "trait_category"),
        mapping_status=_record_value(record, "mapping_status"),
        graphs=len(graphs),
        nodes=len(nodes),
        edges=len(edges),
        grounded_nodes=sum(1 for node in nodes if node.get("grounding")),
        groundable_nodes=len(groundable_nodes),
        grounded_groundable_nodes=grounded_groundable_nodes,
        predicate_id_edges=predicate_id_edges,
        evidenced_edges=evidenced_edges,
        multi_reference_edges=multi_reference_edges,
        snippet_edges=snippet_edges,
        described_edges=described_edges,
        documented_graphs=documented_graphs,
        structural_errors=len(errors),
        quality_warnings=len(warnings),
        reasons=tuple(reasons),
    )


def write_scores(scores: Iterable[CausalGraphScore], out: Any) -> None:
    writer = csv.DictWriter(out, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for score in sorted(scores, key=lambda item: (item.score, item.file)):
        writer.writerow(score.row())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="files or directories to score")
    parser.add_argument(
        "--include-missing",
        action="store_true",
        help="include YAML records that lack causal_graphs and score them as 0",
    )
    parser.add_argument("--workers", type=int, default=0, help="parallel workers; default: CPU count")
    parser.add_argument("--limit", type=int, help="write only the N lowest-scoring rows")
    parser.add_argument("--out", type=Path, help="write TSV to this path instead of stdout")
    args = parser.parse_args(argv)

    paths = args.paths or [TRAITS]
    files = candidate_files(paths, include_missing=args.include_missing)
    if args.workers == 1:
        scores = [score_path(path) for path in files]
    else:
        with ProcessPoolExecutor(max_workers=args.workers or None) as pool:
            scores = list(pool.map(score_path, files))

    scores = sorted(scores, key=lambda item: (item.score, item.file))
    if args.limit is not None:
        scores = scores[:args.limit]

    if args.out is None:
        write_scores(scores, sys.stdout)
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="") as handle:
            write_scores(scores, handle)
        print(f"wrote {len(scores)} causal-graph quality rows to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
