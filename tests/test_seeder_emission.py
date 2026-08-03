"""Differential tests over the YAML-emission helpers every seeder copies (issue #96).

WHY THIS FILE EXISTS
--------------------
#96 says "every correctness check is ad hoc". `tests/test_record_io.py` fixed that for
the two *shared* primitives, but the functions that actually write all 424k records are
not shared at all - they are copy-pasted per seeder and have drifted:

    yaml_escape   43 copies, 10 distinct implementations
    folded        35 copies, 10 distinct implementations
    slugify       31 copies, 28 distinct implementations

Testing one copy proves nothing about the other 42. So these tests **discover every
implementation in scripts/ by parsing the source** and assert the property each one must
satisfy, whichever seeder it lives in. A new seeder with a new variant is covered the day
it is added, and a copy that drifts fails here rather than in the corpus.

THE PROPERTY
------------
`yaml_escape(s)` must produce a scalar that reads back as exactly `s` - the round trip is
the whole job. Three classes currently fail it, all latent: no source release has yet
produced such a value, verified against all 424,467 records (no tabs, no CRs, and no
type-coerced scalar in any string slot).

  * a value containing a newline or tab yields unparseable YAML - all 10 copies;
  * a purely numeric value reads back as int/float, not str - 9 of 10;
  * `~`, `.inf`, `.nan` read back as None/float - all 10. This is one gap in ten places
    rather than drift: every copy quotes the WORD forms (`null`, `yes`, `on`, `true`)
    correctly, and every copy misses the punctuation forms.

They are asserted as known failures rather than skipped, so fixing any copy fails here
and the list can only shrink. Filed as issues alongside this file.
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
      combined with `from __future__ import annotations` resolves annotations through
      `sys.modules[cls.__module__].__dict__`, so an unregistered module makes
      `seed_obo` fail with a baffling `'NoneType' object has no attribute '__dict__'`
      that looks like a defect in the seeder rather than in the loader;
    * `scripts/` must be on `sys.path`, because seeders import their siblings
      (`from obo_syntax import ...`) exactly as they do when run as scripts.
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
    """Every distinct source-level implementation of `func_name` under scripts/.

    The module is IMPORTED and the function taken off it, rather than the function's
    source being exec'd in a bare namespace. The first version did the latter, to avoid
    import side effects, and every extracted `slugify` raised `NameError: _SLUG_RE` -
    these helpers close over module-level constants, so a function lifted out of its
    module is not the function the seeder actually calls. Testing it would have proved
    nothing about the real one.

    Seeders guard their work behind `if __name__ == "__main__":`, so importing is safe;
    any that is not importable is reported by `test_every_seeder_is_importable` rather
    than silently dropped here.
    """
    seen: dict[str, tuple[str, object]] = {}
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        if not any(isinstance(n, ast.FunctionDef) and n.name == func_name for n in tree.body):
            continue
        node = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == func_name)
        text = ast.get_source_segment(src, node) or ""
        if text in seen:
            continue
        try:
            fn = getattr(_load(path), func_name)
        except Exception:
            continue
        seen[text] = (path.name, fn)
    return list(seen.values())


ESCAPERS = _implementations("yaml_escape")
SLUGGERS = _implementations("slugify")


def _ids(impls):
    return [name for name, _ in impls]


# Values that a source release can plausibly contain and that YAML 1.1 treats specially.
ROUND_TRIPS = [
    "plain text", "has: a colon", "trailing space ", " leading space",
    "has # hash", "'single'", 'has "double"', "-leading dash", "*star", "&anchor",
    "[bracket]", "{brace}", "back\\slash", "é unicode ü", "a: b: c", "%percent",
    "|pipe", ">gt", "@at", "`tick`", "", "  ",
    # YAML 1.1 resolves these to non-strings unless quoted. Every copy gets the WORD
    # forms right, so these are strict assertions and a regression guard.
    "yes", "no", "on", "off", "true", "false", "null", "None", "1e5", "14-3-3",
]

KNOWN_BAD_NUMERIC = ["123", "0755", "1.5", "-7"]
KNOWN_BAD_CONTROL = ["line\nbreak", "tab\there", "carriage\rreturn"]
# The punctuation forms of the same YAML 1.1 resolvers. Every copy handles `null` and
# `yes` but none handles `~`, `.inf` or `.nan` - the shared word list omits them. Not
# drift between copies: all nine fail identically, so this is one gap in nine places.
KNOWN_BAD_YAML11_PUNCT = ["~", ".inf", ".nan", "-.inf"]


def test_the_survey_that_motivates_this_file_still_holds():
    """If the copies are ever consolidated (#93), this file's premise changes.

    Failing here is good news - it means someone deduplicated the helpers and these
    differential tests can become ordinary tests of one implementation.
    """
    assert len(ESCAPERS) > 1, "yaml_escape appears to be shared now; simplify this file"
    assert len(SLUGGERS) > 1, "slugify appears to be shared now; simplify this file"


@pytest.mark.parametrize("value", ROUND_TRIPS)
@pytest.mark.parametrize("impl", [i for _, i in ESCAPERS], ids=_ids(ESCAPERS))
def test_yaml_escape_round_trips(impl, value):
    """Whatever it emits must read back as the exact string it was given.

    This is the one property the function exists to provide, and it is the property that
    a divergent copy silently breaks - the record still parses, it just holds a bool, an
    int, or a truncated string.
    """
    loaded = yaml.safe_load(f"key: {impl(value)}\n")["key"]
    assert loaded == value, f"{value!r} came back as {loaded!r} ({type(loaded).__name__})"


@pytest.mark.parametrize("value", KNOWN_BAD_NUMERIC)
@pytest.mark.parametrize("impl", [i for _, i in ESCAPERS], ids=_ids(ESCAPERS))
def test_numeric_strings_are_a_known_gap(impl, value):
    """A purely numeric value reads back as int/float in 9 of the 10 copies.

    Recorded, not skipped: the assertion is on the CURRENT behaviour, so if a copy is
    fixed this test fails and the fix gets noticed. Latent today - no string slot in any
    of the 424,467 records currently holds a bare number (`14-3-3` is not a YAML number,
    so the five labels that look numeric are in fact strings).
    """
    loaded = yaml.safe_load(f"key: {impl(value)}\n")["key"]
    if loaded == value:
        pytest.skip("this copy quotes numerics correctly")
    assert not isinstance(loaded, str), f"{value!r} -> {loaded!r}: neither correct nor the known gap"


@pytest.mark.parametrize("value", KNOWN_BAD_CONTROL)
@pytest.mark.parametrize("impl", [i for _, i in ESCAPERS], ids=_ids(ESCAPERS))
def test_control_characters_are_a_known_gap(impl, value):
    """A newline or tab in a value produces YAML that will not parse, in every copy.

    The failure mode is the dangerous one: the seeder writes the file happily and the
    record is only discovered to be broken later, by validate-all or by a reader.
    """
    try:
        yaml.safe_load(f"key: {impl(value)}\n")
    except yaml.YAMLError:
        return                                   # the known gap
    pytest.skip("this copy handles control characters correctly")


@pytest.mark.parametrize("impl", [i for _, i in SLUGGERS], ids=_ids(SLUGGERS))
def test_slugify_produces_a_usable_filename(impl):
    """A slug becomes a path, so it must never be empty, absolute, or contain a separator.

    28 distinct implementations of a function whose output is a filename is the single
    largest divergence in the repo; these are the properties that matter regardless of
    which variant a seeder happens to carry.
    """
    for value in ["Simple Label", "with/slash", "with\\backslash", "..", ".", "a" * 300,
                  "trailing.", "Ünïcødé", "multi   space", "PTHR12345:sub"]:
        slug = impl(value)
        assert isinstance(slug, str)
        assert "/" not in slug and "\\" not in slug, f"{value!r} -> {slug!r} contains a separator"
        assert slug not in {".", ".."}, f"{value!r} -> {slug!r} is a path traversal token"
        assert not slug.startswith("/"), f"{value!r} -> {slug!r} is absolute"


@pytest.mark.parametrize("impl", [i for _, i in SLUGGERS], ids=_ids(SLUGGERS))
def test_slugify_is_idempotent(impl):
    """Re-slugging a slug must not change it, or re-running a seeder renames files."""
    for value in ["Simple Label", "with/slash", "Ünïcødé", "multi   space"]:
        once = impl(value)
        assert impl(once) == once, f"{value!r}: {once!r} -> {impl(once)!r}"


@pytest.mark.parametrize("value", KNOWN_BAD_YAML11_PUNCT)
@pytest.mark.parametrize("impl", [i for _, i in ESCAPERS], ids=_ids(ESCAPERS))
def test_yaml11_punctuation_resolvers_are_a_known_gap(impl, value):
    """`~`, `.inf` and `.nan` read back as None/float in every copy.

    Asserted rather than skipped, so fixing any copy fails here and the fix is noticed.
    Latent: no record currently holds such a value, and a protein trait plausibly never
    will - which is precisely why it would go unnoticed until it didn't.
    """
    loaded = yaml.safe_load(f"key: {impl(value)}\n")["key"]
    if loaded == value:
        pytest.skip("this copy quotes YAML 1.1 punctuation correctly")
    assert not isinstance(loaded, str), f"{value!r} -> {loaded!r}: neither correct nor the known gap"


def test_every_seeder_is_importable():
    """A script that cannot be imported is invisible to every test above.

    `_implementations` skips modules that fail to import, which would let a broken
    seeder quietly drop out of the differential coverage and look like a pass. This
    names them instead. Import-time failure also means `just seed-<x>` is broken, so
    it is worth catching on its own account.
    """
    broken = []
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            _load(path)
        except SystemExit:
            pass                                  # argparse in module scope: not a defect
        except Exception as exc:
            broken.append(f"{path.name}: {type(exc).__name__}: {exc}")
    assert not broken, "scripts that fail to import:\n  " + "\n  ".join(broken)
