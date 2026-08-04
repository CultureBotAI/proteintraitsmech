"""The seeders' emission helpers, now that there is one of each (#93, #109, #110).

WHAT THIS FILE USED TO BE
-------------------------
A differential harness: it discovered every copy of `yaml_escape`, `folded` and
`slugify` by parsing `scripts/`, and asserted the property each had to satisfy wherever
it lived — because there were 43, 35 and 31 of them, and testing one proved nothing
about the other 42.

That worked. It found three real gaps in `yaml_escape` (#109) and measured that
`slugify` had 28 distinct implementations deciding record FILENAMES (#110). Both are now
consolidated into `scripts/yaml_emit.py`, so the harness is no longer how the behaviour
is tested. It is kept for one job: proving the copies have not come back.

WHY `slugify` STILL HAS 28 DEFINITIONS
---------------------------------------
Deliberately. The 28 differed in exactly two parameters — `max_len` and the `fallback`
for an empty slug — and in nothing else. Picking one would have renamed records under
`ecod/` (34,959), `prosite/` (3,425), `mcsa/` (1,003) and `cazy/` (557). So each seeder
keeps a one-line wrapper passing its own two values to the shared implementation: the
logic is shared, the parameters stay visible at the call site, and nothing is renamed.
`test_every_slugify_delegates_to_the_shared_one` is what stops real logic reappearing.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
import yaml

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def _load(path):
    """Import a script by path, the way the interpreter would when running it.

    Two details are load-bearing and both were learned by getting them wrong:

    * the module must be registered in `sys.modules` BEFORE `exec_module`. `@dataclass`
      with `from __future__ import annotations` resolves annotations through
      `sys.modules[cls.__module__].__dict__`, so an unregistered module makes `seed_obo`
      fail with a baffling `'NoneType' object has no attribute '__dict__'` that reads
      like a defect in the seeder rather than in the loader;
    * `scripts/` must be on `sys.path`, because seeders import their siblings
      (`from yaml_emit import ...`) exactly as they do when run as scripts.
    """
    import importlib.util
    import sys

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    name = f"_ptm_{path.stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _implementations(func_name: str) -> list[tuple[str, object]]:
    """Every distinct source-level implementation of `func_name` under scripts/."""
    seen: dict[str, tuple[str, object]] = {}
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        node = next((n for n in tree.body
                     if isinstance(n, ast.FunctionDef) and n.name == func_name), None)
        if node is None:
            continue
        text = ast.get_source_segment(src, node) or ""
        if text in seen:
            continue
        try:
            fn = getattr(_load(path), func_name)
        except Exception:
            continue
        seen[text] = (path.name, fn)
    return list(seen.values())


_emit = _load(SCRIPTS / "yaml_emit.py")
yaml_escape, folded, slugify = _emit.yaml_escape, _emit.folded, _emit.slugify


# --- the copies must not come back ----------------------------------------------

def test_yaml_escape_has_exactly_one_implementation():
    """43 copies, 10 of them different, is how the three #109 gaps survived unseen."""
    impls = [n for n, _ in _implementations("yaml_escape")]
    assert impls == ["yaml_emit.py"], f"yaml_escape reappeared in: {impls}"


def test_every_slugify_delegates_to_the_shared_one():
    """A `slugify` may pass parameters; it may not contain logic.

    This is what keeps the 28 wrappers honest. A seeder that grows a real implementation
    again — a different regex, a different strip, a different truncation — starts
    silently deciding filenames on its own, which is #110.
    """
    offenders = []
    for path in sorted(SCRIPTS.glob("*.py")):
        if path.name == "yaml_emit.py":
            continue
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if not (isinstance(node, ast.FunctionDef) and node.name == "slugify"):
                continue
            body = [n for n in node.body
                    if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
            ok = (len(body) == 1 and isinstance(body[0], ast.Return)
                  and isinstance(body[0].value, ast.Call)
                  and getattr(body[0].value.func, "id", "") == "_slugify")
            if not ok:
                offenders.append(path.name)
    assert not offenders, f"these carry their own slugify logic: {offenders}"


def test_folded_copies_are_only_the_ones_with_a_different_signature():
    """Three remain, and all three are genuinely different functions, not stale copies.

    `seed_secondary_structure` returns a string where the shared one returns a list of
    lines; the `enrich_*` and `review_*` ones take (key, text) and emit a whole block.
    Folding those in would change their callers, not remove duplication.
    """
    names = sorted(n for n, _ in _implementations("folded"))
    assert names == ["enrich_scop_structural_defs.py", "review_llm_abstracts.py",
                     "seed_secondary_structure.py", "yaml_emit.py"], names


def test_every_seeder_is_importable():
    """A script that cannot be imported is invisible to every test above."""
    broken = []
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            _load(path)
        except SystemExit:
            pass
        except Exception as exc:
            broken.append(f"{path.name}: {type(exc).__name__}: {exc}")
    assert not broken, "scripts that fail to import:\n  " + "\n  ".join(broken)


# --- the shared implementation ---------------------------------------------------

ROUND_TRIPS = [
    "plain text", "has: a colon", "trailing space ", " leading space",
    "has # hash", "'single'", 'has "double"', "-leading dash", "*star", "&anchor",
    "[bracket]", "{brace}", "back\\slash", "é unicode ü", "a: b: c", "%percent",
    "|pipe", ">gt", "@at", "`tick`", "", "  ",
    "yes", "no", "on", "off", "true", "false", "null", "None", "1e5", "14-3-3",
    # the three classes that were broken in EVERY copy until this consolidation (#109)
    "123", "0755", "1.5", "-7", "1:30",
    "~", ".inf", ".nan", "-.inf",
    "line\nbreak", "tab\there", "carriage\rreturn",
]


@pytest.mark.parametrize("value", ROUND_TRIPS)
def test_yaml_escape_round_trips(value):
    """The one property the function exists to provide, now with no exceptions.

    The last three groups are the #109 gaps, asserted rather than recorded as a
    baseline because they are fixed. Fixing them changed no existing record: nothing in
    the corpus is a bare numeric, a YAML 1.1 punctuation resolver, or a value carrying a
    control character.
    """
    loaded = yaml.safe_load(f"key: {yaml_escape(value)}\n")["key"]
    assert loaded == value, f"{value!r} came back as {loaded!r} ({type(loaded).__name__})"


def test_folded_collapses_whitespace_so_a_newline_cannot_break_the_block():
    assert folded("one\ntwo   three\n\nfour") == [">-", "  one two three four"]
    assert folded("") == [">-", "  "]


@pytest.mark.parametrize("value", ["Simple Label", "with/slash", "with\\backslash", "..",
                                   ".", "a" * 300, "trailing.", "Ünïcødé", "multi   space",
                                   "PTHR12345:sub"])
def test_slugify_produces_a_usable_filename(value):
    slug = slugify(value)
    assert "/" not in slug and "\\" not in slug, f"{value!r} -> {slug!r}"
    assert slug not in {".", ".."}, f"{value!r} -> {slug!r}"
    assert not slug.startswith("/")


def test_slugify_is_idempotent():
    """Re-slugging a slug must not change it, or a re-run renames files."""
    for value in ["Simple Label", "with/slash", "Ünïcødé", "multi   space"]:
        once = slugify(value)
        assert slugify(once) == once


@pytest.mark.parametrize("max_len,expected", [(60, 60), (70, 70), (80, 80), (None, 300)])
def test_slugify_truncation_is_a_parameter(max_len, expected):
    """The whole reason 28 wrappers survive instead of one hardcoded length.

    ecod/mcsa/obo truncate at 80, cazy at 60, prosite not at all. Hardcoding 70 — the
    23-seeder majority — would have renamed records in all four of those directories.
    """
    assert len(slugify("x" * 300, max_len)) == expected


def test_slugify_fallback_is_a_parameter():
    assert slugify("", 70, "cath") == "cath"
    assert slugify("!!!", 70, "pfam") == "pfam"
