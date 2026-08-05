"""In-place definition editors must refuse a curated record (#175).

Four `enrich_*_definitions.py` scripts REPLACE a record's `definition` in place.
Seeders get protection from that for free — `write_record` routes through
`merge_on_reseed`, which keeps a curated record's `definition`,
`definition_source`, `mapping_status` and `definitions[]` (#100). An in-place
editor bypasses that choke point by design, because the default merge would
revert the very edit it is making (#148). So it has to ask.

WHY THIS FILE TESTS THE CALLER, NOT `is_curated`
------------------------------------------------
Mutation testing on #173 found that six tests exercising a helper directly could
not catch the main loop failing to PASS an argument to it — and that omission was
the entire defect. The same shape applies here: `is_curated` is already tested in
`test_record_io.py`, and testing it again would prove nothing about whether these
four scripts consult it.

So each script exposes `should_enrich(text)`, and this file checks both halves:

  * behaviour — `should_enrich` refuses a curated record and accepts a seeded one;
  * wiring — the module's `main` actually calls it, asserted against the AST, so
    deleting the call from the loop fails a test rather than passing quietly.

At the time of writing the guard protects nothing: 0 of 31,025 Pfam, 38,394
NCBIfam, 38,218 CDD and 6,139 PROSITE records show curation. It is prevention,
and the test is what keeps it from silently rotting before it is needed.
"""

from __future__ import annotations

import ast
import importlib
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

EDITORS = [
    "enrich_pfam_definitions",
    "enrich_ncbifam_definitions",
    "enrich_cdd_ortholog_definitions",
    "enrich_prosite_definitions",
]

SEEDED = """identifier: Pfam:PF00001
label: x
definition: >-
  a seeded definition
definition_source: Pfam
mapping_status: SEEDED
license: public domain
"""

# The two independent signals `is_curated` recognises. Both are tested because a
# record can carry either without the other: the graph builders add
# `causal_graphs` without touching `mapping_status`, which is exactly the case
# that broke an earlier draft of merge_on_reseed.
CURATED_BY_STATUS = SEEDED.replace("mapping_status: SEEDED",
                                   "mapping_status: REVIEWED")
CURATED_BY_HISTORY = SEEDED.replace(
    "license: public domain",
    'curation_history:\n  - timestamp: "t"\n    curator: c\nlicense: public domain')


@pytest.mark.parametrize("module", EDITORS)
def test_a_seeded_record_is_enriched(module):
    assert importlib.import_module(module).should_enrich(SEEDED)


@pytest.mark.parametrize("module", EDITORS)
@pytest.mark.parametrize("record,why", [
    (CURATED_BY_STATUS, "mapping_status past SEEDED"),
    (CURATED_BY_HISTORY, "a curation_history entry"),
])
def test_a_curated_record_is_refused(module, record, why):
    mod = importlib.import_module(module)
    assert not mod.should_enrich(record), (
        f"{module} would overwrite a record showing {why}; a curator's rewrite "
        f"is discarded with no warning and no trace outside git")


@pytest.mark.parametrize("module", EDITORS)
def test_the_main_loop_actually_calls_the_guard(module):
    """THE MUTATION-DRIVEN HALF. Behaviour tests above pass even if `main` never
    calls `should_enrich` — which is precisely the failure #173 showed a helper
    test cannot see. Asserted against the AST so removing the call from the loop
    fails here.
    """
    src = (REPO / "scripts" / f"{module}.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    main = next((n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    assert main is not None, f"{module} has no main()"
    called = {n.func.id for n in ast.walk(main)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "should_enrich" in called, (
        f"{module}.main() does not call should_enrich; the guard exists but "
        f"nothing consults it")


@pytest.mark.parametrize("module", EDITORS)
def test_the_guard_delegates_rather_than_reimplementing(module):
    """`is_curated` is the one definition of "curated" in this repo (#100). A
    local reimplementation here would drift from it, which is the failure mode
    record_io.py and yaml_emit.py exist to prevent."""
    src = (REPO / "scripts" / f"{module}.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "should_enrich")
    called = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "is_curated" in called, f"{module}.should_enrich reimplements curation"
