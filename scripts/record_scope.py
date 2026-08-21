"""Cheap, explicit record-path scoping for corpus checks.

The corpus layout is ``data/traits/<axis>/<category>/<source>/...``.  A check may use
this helper only when its invariant is completely determined by a known set of source
directories.  It deliberately does not pretend that a CURIE prefix always matches a
directory name: records such as PROSITE overlay subjects can live elsewhere.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path


def records_in_source_directories(
    traits_root: Path, source_directories: Iterable[str]
) -> Iterator[Path]:
    """Yield YAML records below explicitly named source directories.

    Only the stable axis/category levels are enumerated.  Large category directories are
    never recursively walked unless their source-directory name is selected.  Callers
    must name every source that can carry the data their check examines.
    """
    wanted = tuple(sorted(set(source_directories)))
    if not traits_root.is_dir() or not wanted:
        return

    seen: set[Path] = set()
    for axis in sorted(path for path in traits_root.iterdir() if path.is_dir()):
        for category in sorted(path for path in axis.iterdir() if path.is_dir()):
            for source in wanted:
                source_root = category / source
                if not source_root.is_dir():
                    continue
                for path in sorted(source_root.rglob("*.yaml")):
                    if path.is_file() and path not in seen:
                        seen.add(path)
                        yield path
