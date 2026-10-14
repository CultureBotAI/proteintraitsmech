#!/usr/bin/env python3
"""Render the landing page from the browser's already generated facet index."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
AXES = {
    "STRUCTURE": "Structure", "SEQUENCE": "Sequence",
    "SEQUENCE_STRUCTURE": "Seq+Struct", "FUNCTION": "Function", "EVOLUTION": "Evolution",
}


def browse_link(field: str, value: str) -> str:
    return f"browse.html#{field}={quote(value, safe='')}"


def count_link(field: str, value: str, count: int) -> str:
    return f'<a href="{browse_link(field, value)}">{count:,}</a>'


def _table(identifier: str, caption: str, headings: list[str], rows: list[str]) -> str:
    header = "".join(f'<th scope="col">{html.escape(h)}</th>' for h in headings)
    return (f'<table id="{identifier}"><caption>{html.escape(caption)}</caption>'
            f'<thead><tr>{header}</tr></thead>\n<tbody>\n' + "\n".join(rows)
            + "\n</tbody></table>")


def render_regions(facets: dict, sources: list[dict]) -> dict[str, str]:
    """Project only landing markup; never rewrite scientific index payloads."""
    total = facets["total"]
    counts = facets["counts"]
    if type(total) is not int or total < 0:
        raise ValueError("facet total must be a nonnegative integer")
    for field in ("axis", "cat", "src"):
        if not isinstance(counts[field], dict) or any(
            not isinstance(k, str) or type(v) is not int or not 0 < v <= total
            for k, v in counts[field].items()
        ):
            raise ValueError(f"invalid facet counts: {field}")
    axes = list(AXES) + sorted(set(counts["axis"]) - set(AXES))
    stats = ['<a class="stat" href="browse.html"><b data-count="total">'
             f'{total:,}</b><span>trait records</span></a>']
    for axis in axes:
        if axis not in counts["axis"]:
            continue
        stats.append(f'<a class="stat" href="{browse_link("axis", axis)}">'
                     f'<b data-count="{html.escape(axis, quote=True)}">{counts["axis"][axis]:,}</b>'
                     f'<span>{html.escape(AXES.get(axis, axis))}</span></a>')
    stats.append('<a class="stat" href="#sources"><b data-count="sources">'
                 f'{len(counts["src"]):,}</b><span>sources</span></a>')

    # The shard manifest remains authoritative even when the optional count cube
    # is omitted above its size ceiling. Do not guess an axis from category names.
    category_axes: dict[str, set[str]] = {cat: set() for cat in counts["cat"]}
    for shard in facets["shards"]:
        if shard.get("axis"):
            for cat in shard.get("categories", []):
                if cat in category_axes:
                    category_axes[cat].add(shard["axis"])
    category_rows = []
    for cat, count in sorted(counts["cat"].items(), key=lambda item: (-item[1], item[0])):
        axis = ", ".join(sorted(category_axes[cat])) or "—"
        category_rows.append(f'<tr><th scope="row"><code>{html.escape(cat)}</code></th>'
                             f'<td>{html.escape(axis)}</td><td>{count_link("cat", cat, count)}</td></tr>')

    metadata = {}
    for source in sources:
        key = source["source"]
        if key in metadata:
            raise ValueError(f"duplicate source metadata: {key}")
        metadata[key] = source
    source_order = [key for key in metadata if key in counts["src"]]
    source_order += sorted(set(counts["src"]) - set(metadata))
    source_rows = []
    for source in source_order:
        meta = metadata.get(source, {})
        notes = "".join(
            f'<dt>{html.escape(entry["description"])}</dt>'
            f'<dd><code>{html.escape(entry["directory"])}</code></dd>'
            for entry in meta.get("integrations", [])
        )
        details = f'<dl class="source-notes">{notes}</dl>' if notes else "—"
        source_rows.append(f'<tr><th scope="row">{html.escape(source)}</th>'
                           f'<td>{count_link("src", source, counts["src"][source])}</td>'
                           f'<td>{details}</td></tr>')
    source_rows.append('<tr><th scope="row">Total corpus</th>'
                       f'<td><a href="browse.html">{total:,}</a></td><td></td></tr>')
    return {
        "stats": "\n".join(stats),
        "categories": _table("cat-table", "Current trait categories", ["Category", "Axis", "Records"], category_rows),
        "sources": _table("src-table", "Current corpus sources", ["Source", "Records", "Integration notes and directories"], source_rows),
    }


def render_page(page: str, facets: dict, sources: list[dict]) -> str:
    for name, content in render_regions(facets, sources).items():
        start, end = f"<!-- landing:{name}:start -->", f"<!-- landing:{name}:end -->"
        if page.count(start) != 1 or page.count(end) != 1:
            raise ValueError(f"expected one landing marker pair: {name}")
        page, replaced = re.subn(re.escape(start) + r".*?" + re.escape(end),
                                 lambda _: f"{start}\n{content}\n{end}", page, flags=re.S)
        if replaced != 1:
            raise ValueError(f"invalid landing marker order: {name}")
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facets", type=Path, default=ROOT / "docs/data/facets.json")
    parser.add_argument("--page", type=Path, default=ROOT / "docs/index.html")
    parser.add_argument("--sources", type=Path, default=ROOT / "conf/landing_sources.json")
    parser.add_argument("--check", action="store_true", help="fail if any generated landing region is stale")
    args = parser.parse_args(argv)
    original = args.page.read_text(encoding="utf-8")
    rendered = render_page(original, json.loads(args.facets.read_text(encoding="utf-8")),
                           json.loads(args.sources.read_text(encoding="utf-8")))
    if args.check:
        if rendered != original:
            print("Landing page differs from the browser facet index; run scripts/render_docs_landing.py")
            return 1
        print("Landing page matches the browser facet index")
    else:
        args.page.write_text(rendered, encoding="utf-8")
        print(f"Rendered landing counts and filter links → {args.page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
