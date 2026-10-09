"""GO true-path inheritance for exact UniProt GO facts (#1002).

UniProt usually annotates a protein to a more specific GO term than the one a corpus
record names. GO's true-path rule makes an ``is_a`` or ``part_of`` ancestor hold for
every protein annotated to the descendant, so an exact, evidence-qualifying fact on the
descendant supports the record's term through an explicit ``inheritance_path``.

Two artifacts carry the hierarchy:

* the pinned ``go-basic.obo`` release (gitignored, under ``data/raw/``), which the
  resolver and promoter read to find and prove a path; and
* ``data/grounding/go_true_path_edges.jsonl``, the tracked subset of edges that
  qualified examples use, which the validator replays without the OBO file.

Only ``is_a`` and ``part_of`` between two live terms of the same GO namespace count.
go-basic keeps those relations acyclic and true-path safe; ``regulates`` and
``has_part`` never support inheritance. (``go_hierarchy.py`` is unrelated: it ranks
terms in composed definitions and follows ``is_a`` alone.)

    uv run python scripts/go_true_path.py check [--obo data/raw/go-basic.obo]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from obo_syntax import strip_comment  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GO_OBO = REPO_ROOT / "data" / "raw" / "go-basic.obo"
DEFAULT_GO_EDGES = REPO_ROOT / "data" / "grounding" / "go_true_path_edges.jsonl"
GO_BASIC_SOURCE = "http://purl.obolibrary.org/obo/go/go-basic.obo"
INHERITING_RELATIONS = frozenset({"is_a", "part_of"})

_GO_ID = re.compile(r"^GO:[0-9]{7}$")
_RELEASE = re.compile(r"^releases/[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_EDGE_FIELDS = ("child", "parent", "relation", "go_release", "source")


class GoTruePathError(ValueError):
    """A GO release or edge snapshot is malformed or does not prove an edge."""


@dataclass
class GoRelease:
    """Direct ``is_a``/``part_of`` parents of every live term in one GO release."""

    release: str
    parents: dict[str, dict[str, str]] = field(default_factory=dict)
    namespace: dict[str, str] = field(default_factory=dict)

    def relation(self, child: str, parent: str) -> str | None:
        """The inheriting relation of one direct edge, or None."""

        return self.parents.get(child, {}).get(parent)

    def path(self, source: str, target: str) -> list[str] | None:
        """Shortest inclusive ``source -> ... -> target`` path, or None.

        Breadth-first over sorted parents, so ties resolve identically every run.
        Every step stays inside the source's GO namespace.
        """

        if source == target or source not in self.namespace or target not in self.namespace:
            return None
        aspect = self.namespace[source]
        if self.namespace[target] != aspect:
            return None
        previous: dict[str, str] = {}
        queue: deque[str] = deque([source])
        seen = {source}
        while queue:
            term = queue.popleft()
            for parent in sorted(self.parents.get(term, {})):
                if parent in seen or self.namespace.get(parent) != aspect:
                    continue
                seen.add(parent)
                previous[parent] = term
                if parent == target:
                    path = [target]
                    while path[-1] != source:
                        path.append(previous[path[-1]])
                    return list(reversed(path))
                queue.append(parent)
        return None

    def edge_rows(self, path: list[str]) -> list[dict[str, str]]:
        """The durable edge rows proving one path; raises if any step is unproven."""

        rows: list[dict[str, str]] = []
        for child, parent in zip(path, path[1:]):
            relation = self.relation(child, parent)
            if relation is None:
                raise GoTruePathError(
                    f"GO {self.release} has no is_a/part_of edge {child} -> {parent}"
                )
            if self.namespace.get(child) != self.namespace.get(parent):
                raise GoTruePathError(f"GO edge {child} -> {parent} crosses namespaces")
            rows.append(
                {
                    "child": child,
                    "parent": parent,
                    "relation": relation,
                    "go_release": self.release,
                    "source": GO_BASIC_SOURCE,
                }
            )
        return rows


def load_go_obo(path: Path = DEFAULT_GO_OBO) -> GoRelease:
    """Parse the live ``is_a``/``part_of`` graph of one ``go-basic.obo`` release."""

    if not path.is_file():
        raise GoTruePathError(f"GO release is not present: {path} (fetch go-basic.obo first)")
    release = ""
    parents: dict[str, dict[str, str]] = {}
    namespace: dict[str, str] = {}
    obsolete: set[str] = set()
    current: str | None = None
    in_term = False
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if line.startswith("["):
                in_term = line.strip() == "[Term]"
                current = None
                continue
            if not in_term:
                if not release and line.startswith("data-version: "):
                    release = line.removeprefix("data-version: ").strip()
                continue
            value = strip_comment(line).strip()
            if value.startswith("id: "):
                current = value.removeprefix("id: ").strip()
                parents.setdefault(current, {})
            elif current is None:
                continue
            elif value.startswith("namespace: "):
                namespace[current] = value.removeprefix("namespace: ").strip()
            elif value == "is_obsolete: true":
                obsolete.add(current)
            elif value.startswith("is_a: "):
                parents[current][value.removeprefix("is_a: ").split()[0]] = "is_a"
            elif value.startswith("relationship: part_of "):
                parent = value.removeprefix("relationship: part_of ").split()[0]
                # An is_a edge to the same parent is the stronger statement; keep it.
                parents[current].setdefault(parent, "part_of")
    if _RELEASE.fullmatch(release) is None:
        raise GoTruePathError(f"{path}: data-version {release!r} is not releases/YYYY-MM-DD")
    live = {term for term in parents if _GO_ID.fullmatch(term) and term not in obsolete}
    return GoRelease(
        release=release,
        parents={
            term: {parent: rel for parent, rel in parents[term].items() if parent in live}
            for term in live
        },
        namespace={term: namespace[term] for term in live if term in namespace},
    )


def _edge_errors(row: object) -> list[str]:
    if not isinstance(row, dict):
        return ["edge row is not an object"]
    errors: list[str] = []
    if set(row) != set(_EDGE_FIELDS):
        errors.append(f"edge fields must be exactly {sorted(_EDGE_FIELDS)}")
    for key in ("child", "parent"):
        if not isinstance(row.get(key), str) or _GO_ID.fullmatch(row[key]) is None:
            errors.append(f"{key} must be a GO:NNNNNNN identifier")
    if row.get("child") == row.get("parent"):
        errors.append("child and parent must differ")
    if row.get("relation") not in INHERITING_RELATIONS:
        errors.append("relation must be is_a or part_of")
    release = row.get("go_release")
    if not isinstance(release, str) or _RELEASE.fullmatch(release) is None:
        errors.append("go_release must have form releases/YYYY-MM-DD")
    if row.get("source") != GO_BASIC_SOURCE:
        errors.append(f"source must be {GO_BASIC_SOURCE}")
    return errors


def merge_edges(*collections: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Validate, deduplicate, and deterministically sort edge rows."""

    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for collection in collections:
        for raw in collection:
            row = dict(raw)
            errors = _edge_errors(row)
            if errors:
                raise GoTruePathError("; ".join(errors))
            key = (row["child"], row["parent"])
            if key in by_key and by_key[key] != row:
                raise GoTruePathError(
                    f"conflicting GO edge rows for {row['child']} -> {row['parent']}"
                )
            by_key[key] = row
    return [by_key[key] for key in sorted(by_key)]


def dump_edges(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in merge_edges(rows)
    )


def load_edges(path: Path = DEFAULT_GO_EDGES) -> list[dict[str, str]]:
    """Load the tracked edge snapshot fail-closed; a missing file is empty."""

    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise GoTruePathError(f"{path}:{number}: invalid JSON: {exc.msg}") from exc
    try:
        merged = merge_edges(rows)
    except GoTruePathError as exc:
        raise GoTruePathError(f"{path}: {exc}") from exc
    if text != dump_edges(merged):
        raise GoTruePathError(f"{path}: not in canonical sorted form")
    return merged


def edge_index(rows: Iterable[Mapping[str, Any]]) -> dict[str, frozenset[str]]:
    """Child-to-direct-parent index in the shape of the trait hierarchy index."""

    index: dict[str, set[str]] = {}
    for row in rows:
        index.setdefault(str(row["child"]), set()).add(str(row["parent"]))
    return {child: frozenset(parents) for child, parents in index.items()}


def union_index(
    trait_index: Mapping[str, Iterable[str]], go_rows: Iterable[Mapping[str, Any]]
) -> dict[str, frozenset[str]]:
    """Trait ``parent_traits`` edges plus tracked GO edges between GO terms."""

    merged = {child: set(parents) for child, parents in trait_index.items()}
    for child, parents in edge_index(go_rows).items():
        merged.setdefault(child, set()).update(parents)
    return {child: frozenset(parents) for child, parents in merged.items()}


def check(edges_path: Path, obo_path: Path) -> list[str]:
    """Every tracked edge must exist, with its relation, in the release it names."""

    rows = load_edges(edges_path)
    if not rows:
        return []
    release = load_go_obo(obo_path)
    problems: list[str] = []
    for row in rows:
        if row["go_release"] != release.release:
            problems.append(
                f"{row['child']} -> {row['parent']}: pinned to {row['go_release']}, "
                f"local OBO is {release.release}"
            )
        elif release.relation(row["child"], row["parent"]) != row["relation"]:
            problems.append(
                f"{row['child']} -> {row['parent']}: not a {row['relation']} edge in "
                f"{release.release}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="replay tracked edges against the OBO release")
    check_parser.add_argument("--edges", type=Path, default=DEFAULT_GO_EDGES)
    check_parser.add_argument("--obo", type=Path, default=DEFAULT_GO_OBO)
    args = parser.parse_args(argv)
    try:
        problems = check(args.edges, args.obo)
    except GoTruePathError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"OK: {len(load_edges(args.edges)):,} GO edge(s) replay against {args.obo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
