"""Assumptions about the machine, caught before the machine differs.

Five defects in the grounding thread were the same shape: code that was correct
on the laptop that wrote it and wrong somewhere else. Three (#610, #611, #613)
were caught by CI, which is the real gate for this class -- a clean Linux
checkout with no gitignored downloads. Two were not: #607 only failed once the
work was committed, and #616 needed a deletion that no CI run happened to
perform.

CI stays the gate. These are the two cases where a static check is strictly
faster or strictly wider than waiting for a job to fail: a path whose case is
wrong is invisible on a case-insensitive filesystem no matter what runs, and a
strict resolve of a gitignored root is a crash waiting for the first clean
checkout even if no current test touches it.

Deliberately narrow. A check that guesses at "environment dependency" in general
would fire on the many tests that legitimately build fixtures under paths shaped
like production ones, and a gate with false positives gets suppressed.
"""

from __future__ import annotations

import ast
import functools
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent

# `REPO / "name"`, `REPO_ROOT / "name"`, `repo_root / "name"` -- the forms used to
# reach a top-level entry of this repository from code.
_REPO_JOIN = re.compile(r'(?:REPO|REPO_ROOT|repo_root)\s*/\s*"([^"/]+)"')


def _tracked(*globs: str) -> list[str]:
    """Repository-relative paths of tracked files matching ``globs``."""
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", *globs],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.split("\n") if line]


@functools.lru_cache(maxsize=1)
def _tracked_paths() -> frozenset[str]:
    """Every tracked path, read once. One `git ls-files` beats one per constant."""
    return frozenset(_tracked())


def _absent_from_a_clean_checkout(relative: str) -> bool:
    """True when a fresh clone would not create this path.

    Not `git check-ignore`: `reports/` is not ignored, it simply has no tracked
    files, so git never materialises the directory -- and that is the condition
    that made `REPORTS_ROOT.resolve(strict=True)` raise. Asking whether anything
    tracked lives beneath the path answers the question that actually matters,
    for ignored and merely-empty directories alike. (Found by mutation-testing
    this file: the check-ignore version passed while the defect was reinstated.)
    """
    prefix = relative.rstrip("/") + "/"
    return not any(
        tracked == relative or tracked.startswith(prefix) for tracked in _tracked_paths()
    )


def _root_constants(text: str) -> dict[str, str]:
    """CONSTANT -> repository-relative path, for constants rooted at REPO_ROOT.

    Parsed rather than matched. The first version of this used a single-line
    regex and silently skipped five real constants written across lines --
    including DEFAULT_PANTHER_CLASSIFICATIONS, one of the four pinned sources the
    record-content replay verifies (#619). A gate that is green because it looked
    at less than it claimed to is the failure this whole file exists to prevent,
    so it must not be built on a pattern that can quietly miss a shape.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:  # pragma: no cover
        return {}

    def segments(node: ast.AST) -> list[str] | None:
        """The path parts of a `REPO_ROOT / "a" / "b"` chain, or None."""
        if isinstance(node, ast.Name):
            return [] if node.id == "REPO_ROOT" else None
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left = segments(node.left)
            if left is None or not isinstance(node.right, ast.Constant):
                return None
            if not isinstance(node.right.value, str):
                return None
            return [*left, node.right.value]
        return None

    found: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or not target.id.isupper():
            continue
        parts = segments(node.value)
        if parts:
            found[target.id] = "/".join(parts)
    return found


def _function_sources(text: str) -> dict[str, str]:
    """name -> source for every function defined in the module."""
    try:
        tree = ast.parse(text)
    except SyntaxError:  # pragma: no cover - a syntax error is another test's problem
        return {}
    sources: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            segment = ast.get_source_segment(text, node)
            if segment:
                sources[node.name] = segment
    return sources


def _effective_source(name: str, sources: dict[str, str]) -> str:
    """A function's source plus that of the module functions it calls.

    One hop, not a full call graph: the guard is sometimes in the test and
    sometimes in a helper it calls -- `_require_physical_case_alias` holds the
    skip for one of these test files -- and following a single level covers that
    without the exception quietly widening.
    """
    body = sources.get(name, "")
    try:
        tree = ast.parse(body)
    except SyntaxError:  # pragma: no cover
        return body
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    return body + "".join(sources.get(callee, "") for callee in sorted(called))


def _deliberate_case_alias(source: str) -> bool:
    """True when this function exists to test case-varied physical aliases.

    Those functions build `REPO_ROOT / "DATA" / "TRAITS"` on purpose, to prove the
    tools reject an alias a case-insensitive filesystem would otherwise accept,
    and they skip where the filesystem will not produce one. Excusing them by that
    skip -- not by name, and not by an allowlist -- ties the exception to the
    reason it exists, so a function that stops skipping stops being excused.
    """
    if "skip" not in source:
        return False
    return any(marker in source for marker in ("case-sensitive", "case-varied", "case_alias"))


def test_repo_path_references_match_the_filesystems_case():
    """A path whose case is wrong resolves on macOS and cannot on Linux (#610).

    `REPO / "Justfile"` read correctly here and failed in CI, in a file that
    deliberately uses uppercase aliases five times, which is exactly the context
    where a real one blends in. No test needs to exercise the path for this to
    fire, which is why it is worth having even though CI eventually caught it.
    """
    entries = {path.name for path in ROOT.iterdir()}
    by_lower = {name.lower(): name for name in entries}
    wrong: list[str] = []
    for relative_path in _tracked("scripts/*.py", "tests/*.py"):
        path = ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        sources = _function_sources(text)
        excused = {
            joined
            for function_name in sources
            if _deliberate_case_alias(_effective_source(function_name, sources))
            for joined in _REPO_JOIN.findall(sources[function_name])
        }
        for match in _REPO_JOIN.finditer(text):
            name = match.group(1)
            if name in entries or name.lower() not in by_lower or name in excused:
                continue
            line = text[: match.start()].count("\n") + 1
            wrong.append(
                f"{path.relative_to(ROOT)}:{line} refers to {name!r}; "
                f"the repository has {by_lower[name.lower()]!r}"
            )
    assert not wrong, (
        "repository paths that only resolve on a case-insensitive filesystem:\n  "
        + "\n  ".join(wrong)
    )


def test_no_root_absent_from_a_clean_checkout_is_resolved_strictly():
    """`strict=True` on a directory the repository does not commit is a crash (#610).

    `REPORTS_ROOT.resolve(strict=True)` raised FileNotFoundError in a clean
    checkout before the containment check it guarded could run, and took 13 tests
    with it. The containment question -- is this path beneath that root -- has a
    correct answer when the root is absent, so the strictness bought nothing and
    cost the whole module.
    """
    offenders: list[str] = []
    for relative_path in _tracked("scripts/*.py", "tests/*.py"):
        path = ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        for name, relative in sorted(_root_constants(text).items()):
            if not re.search(rf"\b{re.escape(name)}\.resolve\(strict=True\)", text):
                continue
            if _absent_from_a_clean_checkout(relative):
                offenders.append(
                    f"{path.relative_to(ROOT)}: {name} -> {relative!r} has no tracked "
                    f"files, so a clean checkout lacks it, but it is resolved with strict=True"
                )
    assert not offenders, (
        "strict resolves of paths absent from a clean checkout:\n  " + "\n  ".join(offenders)
    )


def test_root_constants_are_found_in_every_shape_they_are_written():
    """Pins #619: the regex this replaced saw only single-line assignments.

    It silently skipped five real constants, `DEFAULT_PANTHER_CLASSIFICATIONS`
    among them, and the gate passed having checked fewer paths than exist. A gate
    green because it looked at less than it claimed to is the failure this file
    exists to prevent, so the parser is pinned against the shapes rather than
    trusted.
    """
    module = (
        "REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent\n"
        'ONE_LINE = REPO_ROOT / "reports"\n'
        "MULTI = (\n"
        '    REPO_ROOT / "data" / "raw" / "panther" / "classifications.tsv"\n'
        ")\n"
        'DEEP = REPO_ROOT / "data" / "grounding"\n'
        'NOT_A_PATH = "reports"\n'
        'NOT_ROOTED = SOMEWHERE_ELSE / "reports"\n'
        'lowercase = REPO_ROOT / "reports"\n'
    )
    found = _root_constants(module)
    assert found == {
        "ONE_LINE": "reports",
        "MULTI": "data/raw/panther/classifications.tsv",
        "DEEP": "data/grounding",
    }, found


def test_the_clean_checkout_predicate_distinguishes_tracked_from_untracked():
    """`reports/` has no tracked files; `data/grounding/` and `scripts/` do.

    The distinction the gate turns on, asserted against the real repository so a
    change to what is committed cannot quietly invert it.
    """
    assert _absent_from_a_clean_checkout("reports")
    assert not _absent_from_a_clean_checkout("data/grounding")
    assert not _absent_from_a_clean_checkout("scripts")
    # A prefix must not match a sibling that merely starts with the same letters.
    assert _absent_from_a_clean_checkout("script")
