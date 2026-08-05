#!/usr/bin/env python3
"""GO `is_a` ancestry, for ranking terms in composed definitions (#152).

Composed definitions show at most three GO terms per aspect. Which three was
previously decided by list order -- PANTHER's own for the family composer, and
CURIE sort order for the subfamily consensus, where a set has no order and
something deterministic was needed. Sorting for determinism quietly became a
decision about content: the three shown were the three lowest GO IDs, which
tracks when a term was minted and not how much it says. Across the 228 records
in #154 the cap discarded 3,130 agreed-on terms chosen that way.

This gives the composers enough of the ontology to choose on merit:

  * drop a term that is an ANCESTOR of another term already in the list --
    "catalytic activity" says nothing beside "exonuclease activity";
  * rank what remains by depth, most specific first, so the cap keeps the three
    that carry the most information.

Stdlib-only, like every seeder. Reads `data/raw/go-basic.obo` (gitignored, fetched
by `just fetch-obo`). go-basic is the right file: it is the filtered release with
cyclic and cross-aspect relations removed, so `is_a` alone is a DAG per aspect.

Only `is_a` is followed. `part_of` would also be defensible for BP/CC, but mixing
the two makes "ancestor" mean two different things in one list, and `is_a` is what
"X is a kind of Y, so Y adds nothing" actually licenses.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from obo_syntax import strip_comment, strip_suffixes  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
GO_OBO = REPO_ROOT / "data" / "raw" / "go-basic.obo"


def parse_is_a(path: Path | None = None) -> dict[str, set[str]]:
    """GO id -> its direct `is_a` parents. Obsolete terms are skipped."""
    path = path or GO_OBO
    parents: dict[str, set[str]] = {}
    cur: str | None = None
    obsolete = False
    in_term = False
    for raw in path.open(encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("["):
            if cur and not obsolete:
                parents.setdefault(cur, set())
            in_term = line.strip() == "[Term]"
            cur, obsolete = None, False
            continue
        if not in_term:
            continue
        if line.startswith("id: "):
            cur = line[4:].strip()
        elif line.startswith("is_obsolete: true"):
            obsolete = True
        elif line.startswith("is_a: ") and cur:
            parent = strip_comment(strip_suffixes(line[6:])).strip()
            if parent:
                parents.setdefault(cur, set()).add(parent)
    if cur and not obsolete:
        parents.setdefault(cur, set())
    return parents


def ancestors_of(parents: dict[str, set[str]]) -> dict[str, frozenset[str]]:
    """Transitive `is_a` closure, memoised iteratively.

    Recursion would be the obvious way and is wrong here: GO is ~48k terms deep
    enough to blow the default limit on a handful of chains, and a malformed or
    hand-edited release could contain a cycle. This tolerates both.
    """
    closure: dict[str, frozenset[str]] = {}
    for start in parents:
        if start in closure:
            continue
        stack = [start]
        while stack:
            node = stack[-1]
            pending = [p for p in parents.get(node, ()) if p not in closure]
            if pending:
                # Guard against a cycle: a node already on the stack cannot be
                # waited on, so treat the back-edge as contributing nothing.
                pending = [p for p in pending if p not in stack]
                if pending:
                    stack.extend(pending)
                    continue
            acc: set[str] = set()
            for p in parents.get(node, ()):
                acc.add(p)
                acc |= closure.get(p, frozenset())
            closure[node] = frozenset(acc)
            stack.pop()
    return closure


def depth_of(closure: dict[str, frozenset[str]]) -> dict[str, int]:
    """How specific a term is: the size of its ancestor set.

    Not the longest path to the root. Ancestor count is monotonic along any
    `is_a` chain -- a child always has strictly more ancestors than its parent --
    which is the only property the ranking needs, and it costs nothing extra
    once the closure exists.
    """
    return {go: len(anc) for go, anc in closure.items()}


class GoRanker:
    """Prune redundant GO terms and order the rest most-specific-first."""

    def __init__(self, path: Path | None = None):
        self.parents = parse_is_a(path)
        self.ancestors = ancestors_of(self.parents)
        self.depth = depth_of(self.ancestors)

    def rank(self, terms: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """`[(name, GO:id), ...]` -> pruned, most specific first.

        A term is dropped when another term in the SAME list is a descendant of
        it. Ties break on the CURIE so the output stays byte-stable across runs,
        which is what the previous sort was protecting and is still required.
        Terms absent from the release (obsolete, or a newer GO than the file)
        keep depth 0 and sort last rather than being dropped -- losing a term
        because the local ontology is stale would be worse than showing it.
        """
        seen: set[str] = set()
        uniq: list[tuple[str, str]] = []
        for name, go in terms:
            if go not in seen:
                seen.add(go)
                uniq.append((name, go))
        ids = {go for _, go in uniq}
        kept = [(n, go) for n, go in uniq
                if not (ids - {go}) & _descendant_marker(self.ancestors, go, ids)]
        return sorted(kept, key=lambda t: (-self.depth.get(t[1], 0), t[1]))


def _descendant_marker(ancestors, go, ids) -> set[str]:
    """The ids in `ids` that have `go` as an ancestor, i.e. that make `go` redundant."""
    return {other for other in ids if other != go and go in ancestors.get(other, ())}


if __name__ == "__main__":
    r = GoRanker()
    print(f"terms: {len(r.parents):,}", file=sys.stderr)
    sample = [("catalytic activity", "GO:0003824"),
              ("nuclease activity", "GO:0004518"),
              ("exonuclease activity", "GO:0004527"),
              ("hydrolase activity", "GO:0016787")]
    for name, go in r.rank(sample):
        print(f"  {go}  depth={r.depth.get(go)}  {name}")
