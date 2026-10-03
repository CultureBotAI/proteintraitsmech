"""The public landing must describe the exact browser facets without JavaScript."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_docs_landing", ROOT / "scripts/render_docs_landing.py")
LANDING = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LANDING)


def facets():
    return {
        "total": 3,
        "counts": {"axis": {"SEQUENCE": 2, "FUNCTION": 1},
                   "cat": {"NEW_CATEGORY": 2, "FUNC_BINDING": 1},
                   "src": {"Known": 1, 'New & <source> "x"': 2}},
        "cube": None,
        "shards": [{"axis": "SEQUENCE", "categories": ["NEW_CATEGORY"]},
                   {"axis": "FUNCTION", "categories": ["FUNC_BINDING"]}],
    }


def metadata():
    return [{"source": "Known", "integrations": [{"description": "Original description (CC-BY 4.0)",
              "directory": "data/traits/sequence/{a,b}/"}, {"description": "Another integration <note>",
              "directory": "data/traits/structure/example/"}]}]


def test_new_categories_sources_and_accurate_totals_render_without_a_fetch():
    page = (ROOT / "docs/index.html").read_text()
    rendered = LANDING.render_page(page, facets(), metadata())
    assert '<b data-count="total">3</b>' in rendered
    assert '<b data-count="sources">2</b>' in rendered
    assert 'browse.html#cat=NEW_CATEGORY">2</a>' in rendered
    assert 'browse.html#src=New%20%26%20%3Csource%3E%20%22x%22">2</a>' in rendered
    assert 'New &amp; &lt;source&gt; &quot;x&quot;' in rendered
    assert "Original description (CC-BY 4.0)" in rendered
    assert "Another integration &lt;note&gt;" in rendered
    assert "data/traits/sequence/{a,b}/" in rendered
    assert 'fetch("data/facets.json")' not in rendered
    assert "demo retired" in rendered
    # Category axis comes from the shard contract, including when cube=None.
    assert '<code>NEW_CATEGORY</code></th><td>SEQUENCE</td>' in rendered
    assert '<th scope="row">Total corpus</th><td><a href="browse.html">3</a>' in rendered
    assert LANDING.render_page(rendered, facets(), metadata()) == rendered


@pytest.mark.parametrize("mutation", ["headline", "category_count", "source_count", "missing_category", "new_source"])
def test_check_refuses_every_kind_of_count_or_coverage_drift(tmp_path, mutation):
    data = facets()
    page = LANDING.render_page((ROOT / "docs/index.html").read_text(), data, metadata())
    if mutation == "headline":
        page = page.replace('data-count="total">3', 'data-count="total">999')
    elif mutation == "category_count":
        page = page.replace('cat=NEW_CATEGORY">2', 'cat=NEW_CATEGORY">999')
    elif mutation == "source_count":
        page = page.replace('src=Known">1', 'src=Known">999')
    elif mutation == "missing_category":
        page = re.sub(r'<tr><th scope="row"><code>NEW_CATEGORY.*?</tr>', '', page)
    else:
        data["counts"]["src"]["Added source"] = 1
    site = tmp_path / "index.html"
    index = tmp_path / "facets.json"
    sources = tmp_path / "sources.json"
    site.write_text(page)
    index.write_text(json.dumps(data))
    sources.write_text(json.dumps(metadata()))
    args = ["--page", str(site), "--facets", str(index), "--sources", str(sources)]
    assert LANDING.main([*args, "--check"]) == 1
    assert site.read_text() == page, "check mode must not rewrite a stale page"
    assert LANDING.main(args) == 0
    assert LANDING.main([*args, "--check"]) == 0


def test_removed_sources_and_categories_do_not_leave_dead_filter_links():
    page = (ROOT / "docs/index.html").read_text()
    rendered = LANDING.render_page(page, facets(), metadata())
    assert "cat=UPPER" not in rendered
    assert "src=PROSITE" not in rendered
    assert 'role="region" tabindex="0" aria-label="Trait categories"' in rendered
    assert 'role="region" tabindex="0" aria-label="Corpus sources"' in rendered


def test_marker_damage_is_rejected_before_a_write():
    page = (ROOT / "docs/index.html").read_text().replace("<!-- landing:sources:end -->", "")
    with pytest.raises(ValueError, match="marker pair"):
        LANDING.render_page(page, facets(), metadata())


def test_current_build_and_publication_render_then_check_the_same_facets():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text()
    recipe = (ROOT / "justfile").read_text().split("build-docs:\n", 1)[1].split("\n\n", 1)[0]
    for text in [workflow, recipe]:
        assert text.index("scripts/build_docs_index.py") < text.index("scripts/render_docs_landing.py")
        assert "scripts/render_docs_landing.py --check" in text
    assert '"scripts/render_docs_landing.py"' in workflow
    assert '"conf/landing_sources.json"' in workflow
