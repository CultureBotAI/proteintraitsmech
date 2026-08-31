"""The corpus map's hover tooltip, checked where a browser is not available.

`docs/map.html` serves all three maps — full-record corpus, definition-only
corpus, and proteins — from one canvas and one tooltip, so these checks cover
every map at once. The identifier in the tooltip is tinted with the marker
colour of the point under the cursor; that only helps if the tint is the colour
actually painted, and if every hue in every palette stays legible on the
tooltip's own background.
"""

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP_HTML = ROOT / "docs" / "map.html"
PROTEIN_MAP = ROOT / "scripts" / "build_protein_map.py"
MAP_DATA = ROOT / "docs" / "data"

# Tooltip text is .78rem bold — under 18.66px, so WCAG's large-text 3:1
# allowance does not apply and normal-text AA is the bar.
MIN_CONTRAST = 4.5
# --stage-bg in each theme, the only colours a translucent tooltip can sit on.
STAGE_BG = {"light": "#f8f9fa", "dark": "#17201e"}


def _rgb(value: str) -> tuple[int, int, int]:
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _relative_luminance(color: str) -> float:
    def channel(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(fg: str, bg: str) -> float:
    a, b = _relative_luminance(fg), _relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _tooltip_backgrounds() -> list[str]:
    """Every colour the tooltip text can actually sit on.

    An opaque background is one colour; a translucent one composites over the
    stage in each theme, which is what dropped the palette's blue below AA
    before the tooltip was made opaque.
    """
    css = MAP_HTML.read_text(encoding="utf-8")
    rule = re.search(r"#tip\{([^}]*)\}", css)
    assert rule, "docs/map.html no longer has a #tip rule"
    decl = re.search(r"background:([^;]+);", rule.group(1))
    assert decl, "#tip has no background declaration"
    value = decl.group(1).strip()

    if value.startswith("#"):
        return [value]
    rgba = re.fullmatch(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", value)
    assert rgba, f"unhandled #tip background {value!r}"
    r, g, b, alpha = (*(int(rgba.group(i)) for i in (1, 2, 3)), float(rgba.group(4)))
    composited = []
    for stage in STAGE_BG.values():
        sr, sg, sb = _rgb(stage)
        composited.append(
            "#%02x%02x%02x"
            % tuple(round(f * alpha + s * (1 - alpha)) for f, s in ((r, sr), (g, sg), (b, sb)))
        )
    return composited


def _palette(text: str, name: str) -> dict[str, str]:
    """Parse a flat name -> hex palette, refusing to read it partially.

    Skipping an entry the pattern cannot match would let the contrast check pass
    having measured fewer hues than the palette holds -- green because it looked
    at less, the failure shape of #540 and #573. So every declared key must come
    back with a colour.
    """
    block = re.search(rf"{name}\s*=\s*\{{(.*?)\}}", text, re.S)
    assert block, f"{name} not found"
    body = block.group(1)
    parsed = dict(re.findall(r'"?([A-Za-z_]+)"?\s*:\s*"(#[0-9a-fA-F]{3,6})"', body))
    unreadable = sorted(set(re.findall(r'"?([A-Za-z_][A-Za-z_0-9]*)"?\s*:', body)) - set(parsed))
    assert not unreadable, (
        f"{name} declares {unreadable} but they did not parse as double-quoted "
        f"hex; the contrast check would silently skip those hues"
    )
    return parsed


def _shipped_palettes() -> dict[str, str]:
    """Hues in the built map files, which are what `colorOf` actually returns.

    The source constants and the built JSON agree today only because
    build_protein_map.py wrote the JSON. A hand-edited file, or a future map
    whose palette comes from elsewhere, would render hues no source constant
    mentions -- so the shipped data is checked directly.
    """
    shipped: dict[str, str] = {}
    for path in sorted(MAP_DATA.glob("*map*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("colors", "colors_dark"):
            for group, color in (data.get(key) or {}).items():
                shipped[f"{path.name} {key}:{group}"] = color
    return shipped


def _all_marker_colors() -> dict[str, str]:
    """Marker hues across all three maps, keyed by palette:group."""
    html = MAP_HTML.read_text(encoding="utf-8")
    protein = PROTEIN_MAP.read_text(encoding="utf-8")
    palettes = {
        "AXIS_COLORS_LIGHT": _palette(html, "AXIS_COLORS_LIGHT"),
        "AXIS_COLORS_DARK": _palette(html, "AXIS_COLORS_DARK"),
        "DOMAIN_COLORS_LIGHT": _palette(protein, "DOMAIN_COLORS_LIGHT"),
        "DOMAIN_COLORS_DARK": _palette(protein, "DOMAIN_COLORS_DARK"),
    }
    # colorOf's last resort when a map names a group no palette covers.
    fallback = re.search(r'AXIS_COLORS\[g\]\s*\|\|\s*"(#[0-9a-fA-F]{6})"', html)
    assert fallback, "colorOf no longer has a literal fallback colour"
    flat = {f"colorOf fallback:{fallback.group(1)}": fallback.group(1)}
    for pal, entries in palettes.items():
        assert entries, f"{pal} parsed empty"
        for group, color in entries.items():
            flat[f"{pal}:{group}"] = color
    flat.update(_shipped_palettes())
    return flat


def test_light_and_dark_palettes_cover_the_same_groups():
    """An asymmetry is how a silently dropped palette entry shows itself.

    A hue present in one theme and missing from the other is either an entry the
    parser could not read or a group with no dark-mode colour. Both are worth
    failing on, and neither is visible to a check that only measures what it
    managed to read.
    """
    html = MAP_HTML.read_text(encoding="utf-8")
    protein = PROTEIN_MAP.read_text(encoding="utf-8")
    for source, light, dark in (
        (html, "AXIS_COLORS_LIGHT", "AXIS_COLORS_DARK"),
        (protein, "DOMAIN_COLORS_LIGHT", "DOMAIN_COLORS_DARK"),
    ):
        assert set(_palette(source, light)) == set(_palette(source, dark)), (
            f"{light} and {dark} cover different groups"
        )


def test_tooltip_identifier_is_tinted_with_the_hovered_marker_colour():
    """The tint must come from the same expression that paints the marker.

    Two separate colour lookups would drift the first time a palette changes;
    one shared call cannot.
    """
    html = MAP_HTML.read_text(encoding="utf-8")
    paint = "ctx.fillStyle=colorOf(DATA.axes[p[2]])"
    tint = 'tip.style.setProperty("--tip-id", colorOf(DATA.axes[p[2]]))'
    assert paint in html, "draw() no longer colours markers with colorOf(DATA.axes[p[2]])"
    assert tint in html, "the tooltip identifier is no longer tinted with the marker colour"
    assert re.search(r"#tip b\{color:var\(--tip-id,", html), (
        "#tip b must consume --tip-id, or the tint set on hover is inert"
    )

    # The tint is set once per mousemove, so a palette change repaints the
    # markers underneath it while the identifier keeps the previous theme's hue.
    # Reaching the theme toggle fires mouseleave; an OS-driven flip does not.
    assert "tip.style.opacity=0; buildLegend(); draw();" in html, (
        "a palette change must hide the tooltip, or the tint outlives its marker"
    )
    assert html.count("MutationObserver(repaint)") == 1
    assert html.count('.addEventListener("change", repaint)') == 1


def test_every_marker_hue_stays_legible_on_the_tooltip():
    """A hue that is fine on the stage can be illegible on the tooltip.

    The tooltip's ground is near-black in both themes while the light palette is
    tuned for a near-white stage, so tinting the identifier moves each hue onto a
    background it was never checked against.
    """
    backgrounds = _tooltip_backgrounds()
    too_dim = [
        f"{label} {color} on {bg}: {_contrast(color, bg):.2f}:1"
        for label, color in sorted(_all_marker_colors().items())
        for bg in backgrounds
        if _contrast(color, bg) < MIN_CONTRAST
    ]
    assert not too_dim, "marker hues below AA on the tooltip:\n  " + "\n  ".join(too_dim)


# Fetched map JSON reaching innerHTML is the one injection surface on this page:
# `axes`, `cats`, `orgs`, and `colors` all come from docs/data/*.json.
_INNER_HTML_ASSIGNMENT = re.compile(r"\.innerHTML\s*=\s*(`(?:[^`\\]|\\.)*`)", re.S)
_INTERPOLATION = re.compile(r"\$\{\s*([^}]*)\}")
# esc() escapes & < > "; fmt() formats a number through toLocaleString.
_SAFE_INTERPOLATION = re.compile(r"^(esc|fmt)\s*\(")


def test_no_fetched_value_reaches_innerHTML_unescaped():
    """Every interpolation into markup must go through esc() or fmt().

    buildLegend used to interpolate a group name and a palette colour straight
    into an innerHTML template (#602) -- the only place on the page where fetched
    data reached markup unescaped, while every other interpolation already used
    esc().
    """
    html = MAP_HTML.read_text(encoding="utf-8")
    assignments = _INNER_HTML_ASSIGNMENT.findall(html)
    assert assignments, "no templated innerHTML assignment found; has the page changed shape?"
    raw = [
        expression.strip()
        for template in assignments
        for expression in _INTERPOLATION.findall(template)
        if not _SAFE_INTERPOLATION.match(expression.strip())
    ]
    assert not raw, "values interpolated into innerHTML without esc()/fmt():\n  " + "\n  ".join(raw)


def test_the_legend_is_built_from_nodes_not_markup():
    """A colour assigned through CSSOM cannot add declarations; one written into
    a style attribute can, and esc() would not stop it. textContent cannot express
    markup at all. Structural, so it does not depend on remembering to call esc().
    """
    html = MAP_HTML.read_text(encoding="utf-8")
    assert "sw.style.background=colorOf(ax)" in html
    assert "cnt.textContent=fmt(axisCount(ax))" in html
    assert "b.append(sw," in html
    assert 'style="background:${' not in html, (
        "a palette colour is being written into a style attribute again"
    )
