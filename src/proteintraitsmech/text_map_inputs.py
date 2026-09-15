"""Export versioned semantic text for the fleet map; no model inference.

The temporary SQLite path/identity index bounds memory independently of corpus
size. Full exports are the default; selected subsets are reported as subsets.
The existing domain renderer defines each document; selection changes coverage,
not the meaning or text checksum of a selected record.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sqlite3
import sys
import tempfile
from collections.abc import Iterator, Mapping
from contextlib import ExitStack
from pathlib import Path
from urllib.parse import quote

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_VERSION = "proteintraitsmech-existing-full-text-v1"
CORPUS = "traits"


def clean(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        record = yaml.load(handle, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    if not isinstance(record, dict):
        raise ValueError(f"record is not a mapping: {path}")
    for field in ("identifier", "label"):
        if (field == "identifier" and not isinstance(record.get(field), str)) or not clean(
            record.get(field)
        ):
            raise ValueError(f"record has no nonempty {field}: {path}")
    return record


def _discover(directory: Path) -> Iterator[Path]:
    """Yield paths without a list of all YAML files or following symlinks."""
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_symlink():
                if entry.name.endswith(".yaml") or entry.is_dir():
                    raise ValueError(f"symlink in corpus: {entry.path}")
                continue
            if entry.is_dir(follow_symlinks=False):
                yield from _discover(Path(entry.path))
            elif entry.name.endswith(".yaml") and entry.is_file(follow_symlinks=False):
                yield Path(entry.path)


def _record_path(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"record leaves the corpus: {relative}")
    path = root / relative
    corpus_root = root / "data" / CORPUS
    if path.suffix != ".yaml" or not path.is_file():
        raise ValueError(f"not a corpus YAML file: {relative}")
    try:
        path.resolve().relative_to(corpus_root.resolve())
        path.relative_to(corpus_root)
    except ValueError as exc:
        raise ValueError(f"record leaves the corpus: {relative}") from exc
    if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root.parent):
        raise ValueError(f"symlink in record path: {relative}")
    return path


CATEGORY_FIELD = "trait_category"


def build_context(root: Path) -> Mapping:
    """Load the shared document renderer and the browser's direct ChEBI names."""
    spec = importlib.util.spec_from_file_location(
        "_proteintraitsmech_embedding_documents", REPO_ROOT / "scripts" / "embedding_documents.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    names_file = root / "docs" / "data" / "chebi.json"
    with names_file.open(encoding="utf-8") as stream:
        chemical_data = json.load(stream)
    if not isinstance(chemical_data, dict):
        raise ValueError("docs/data/chebi.json must map chemical identifiers to metadata")
    names = {
        identifier: re.sub(r"<[^>]+>", "", metadata["name"])
        for identifier, metadata in chemical_data.items()
        if isinstance(metadata, dict) and isinstance(metadata.get("name"), str) and metadata["name"]
    }
    return {"builder": module.build_document, "names": names}


def semantic_text(record: dict, context: Mapping) -> str:
    """Project current YAML to the same selected fields as the existing full map.

    The browser normalizes/caps its definition at 500 characters and keeps six
    synonyms. Preserve that existing representation while reading fresh YAML,
    rather than depending on an old generated record-shard snapshot.
    """
    definition = " ".join(str(record.get("definition") or "").split())
    if len(definition) > 500:
        definition = definition[:499].rstrip() + "…"
    chemical_names = list(
        dict.fromkeys(
            context["names"][item["chebi"]]
            for item in (record.get("chemical_participants") or [])
            if item.get("chebi") in context["names"]
        )
    )
    row = {
        "id": record["identifier"],
        "label": record.get("label"),
        "cat": record.get("trait_category"),
        "axis": record.get("trait_axis"),
        "chem": chemical_names,
    }
    detail = {
        "def": definition,
        "defs": [
            [item.get("kind"), item.get("text"), item.get("source")]
            for item in (record.get("definitions") or [])
            if isinstance(item, dict) and item.get("text")
        ],
        "syn": [
            item["synonym_text"]
            for item in (record.get("synonyms") or [])
            if isinstance(item, dict) and item.get("synonym_text")
        ][:6],
        "pat": record.get("sequence_pattern"),
        "pt": [[identifier] for identifier in (record.get("parent_traits") or [])]
        + [
            [item["object"]] for item in (record.get("trait_relations") or []) if item.get("object")
        ],
        "xr": list(record.get("xrefs") or []),
        "mx": [
            [item["object"]] for item in (record.get("mapped_xrefs") or []) if item.get("object")
        ],
    }
    text, _used_label_fallback = context["builder"](row, detail, "full")
    return text


def page_target(record: dict, source_path: str) -> str:
    # docs/browse.js reads '#record=' using decodeURIComponent; no per-record HTML exists.
    return "browse.html#record=" + quote(record["identifier"], safe="")


def iter_inputs(
    root: Path = REPO_ROOT, *, records: list[str] | None = None, limit: int | None = None
) -> Iterator[dict]:
    """Yield the exact fleet JSONL contract, with stable order and unique IDs."""
    root = root.resolve()
    corpus_root = root / "data" / CORPUS
    if not corpus_root.is_dir() or corpus_root.is_symlink() or (root / "data").is_symlink():
        raise ValueError(f"missing real corpus directory: {corpus_root}")
    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer")
    context = build_context(root)
    with tempfile.TemporaryDirectory(prefix="proteintraitsmech-map-inputs-") as directory:
        connection = sqlite3.connect(str(Path(directory) / "index.sqlite"))
        try:
            connection.execute("CREATE TABLE paths (path TEXT PRIMARY KEY)")
            connection.execute("CREATE TABLE ids (identifier TEXT PRIMARY KEY)")
            paths = (
                (_record_path(root, path) for path in records)
                if records
                else _discover(corpus_root)
            )
            for path in paths:
                relative = path.relative_to(root).as_posix()
                try:
                    connection.execute("INSERT INTO paths VALUES (?)", (relative,))
                except sqlite3.IntegrityError as exc:
                    raise ValueError(f"duplicate selected path: {relative}") from exc
            connection.commit()
            query = "SELECT path FROM paths ORDER BY path"
            if limit is not None:
                query += " LIMIT ?"
            for (relative,) in connection.execute(query, (limit,) if limit is not None else ()):
                record = _load(_record_path(root, relative))
                identifier = record["identifier"]
                try:
                    connection.execute("INSERT INTO ids VALUES (?)", (identifier,))
                except sqlite3.IntegrityError as exc:
                    raise ValueError(f"duplicate record identifier: {identifier}") from exc
                text = semantic_text(record, context)
                yield {
                    "identifier": identifier,
                    "label": clean(record["label"]),
                    "category": clean(record.get(CATEGORY_FIELD)) or "UNKNOWN",
                    "page": page_target(record, relative),
                    "source_path": relative,
                    "text": text,
                    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "adapter_version": ADAPTER_VERSION,
                }
        finally:
            connection.close()


def export_inputs(
    root: Path, output: Path | None, *, records: list[str] | None = None, limit: int | None = None
) -> dict:
    """Validate a preview or atomically publish JSONL after all rows pass."""
    destination = output.resolve() if output is not None else None
    if destination is not None and destination.suffix != ".jsonl":
        raise ValueError("output must have a .jsonl suffix")
    temporary = None
    handle = None
    digest = hashlib.sha256()
    count = 0
    try:
        with ExitStack() as stack:
            if destination is not None:
                destination.parent.mkdir(parents=True, exist_ok=True)
                handle = stack.enter_context(
                    tempfile.NamedTemporaryFile(
                        mode="wb",
                        prefix=".text-map-",
                        dir=destination.parent,
                        delete=False,
                    )
                )
                temporary = Path(handle.name)
            for record in iter_inputs(root, records=records, limit=limit):
                payload = (json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n").encode(
                    "utf-8"
                )
                digest.update(payload)
                count += 1
                if handle is not None:
                    handle.write(payload)
            if not count:
                raise ValueError("selection contains no corpus records")
            if handle is not None:
                handle.close()
                temporary.replace(destination)
            return {
                "mode": "export" if destination is not None else "preview",
                "scope": "subset" if records or limit is not None else "full",
                "records": count,
                "adapter_version": ADAPTER_VERSION,
                "jsonl_sha256": digest.hexdigest(),
                "output": str(destination) if destination is not None else None,
            }
    finally:
        if handle is not None:
            handle.close()
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="repository containing data/" + CORPUS
    )
    parser.add_argument(
        "--output", type=Path, help="publish JSONL atomically; otherwise validate a preview"
    )
    parser.add_argument(
        "--record", action="append", help="repo-relative YAML path; repeat for a canary subset"
    )
    parser.add_argument(
        "--limit", type=int, help="canary: select this many paths before parsing selected records"
    )
    args = parser.parse_args(argv)
    try:
        result = export_inputs(args.root, args.output, records=args.record, limit=args.limit)
    except (OSError, ValueError, yaml.YAMLError, sqlite3.Error) as exc:
        print(f"text-map inputs refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
