"""Re-promotion must not overwrite a graph it did not write (#204).

#205 fixed two thirds of this: re-promotion merges instead of splicing, so OTHER graphs
and the whole `curation_history` survive. It left the case the issue calls the one that
loses work — an edit to the promoter's own `resistance` graph, which is replaced wholesale
on every `--repromote`.

`is_ours` cannot see it. It establishes that this promoter *once* wrote a graph here, not
that the content is still that graph, and a curator who improves a promoted graph leaves
both of its markers in place.

WHY A FINGERPRINT AND NOT "does it still match the config"
-----------------------------------------------------------
Because the second question has two answers and cannot tell them apart: the config moved
(a legitimate re-promotion target) or a curator edited the graph (must not be overwritten).
`emitted_hash` records what the promoter actually wrote, so the two separate.

The fallback for records promoted before the field existed is the weaker test, and it is
deliberately conservative: equal to the config's output means the rewrite is a no-op and
safe whatever the history; anything else is refused and listed.
"""

from __future__ import annotations

import importlib
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

promote = importlib.import_module("promote_family_drafts")

GRAPH = {"graph_id": "resistance", "nodes": [{"node_id": "determinant"}],
         "edges": [{"subject": "determinant", "object": "resistance",
                    "evidence": [{"reference": "ARO:1", "snippet": "s"}]}]}


# --- the fingerprint itself ---------------------------------------------------------------

def test_the_fingerprint_is_stable_across_calls():
    assert promote.graph_fingerprint(GRAPH) == promote.graph_fingerprint(dict(GRAPH))


def test_the_fingerprint_changes_when_ANY_part_of_the_graph_changes():
    """Including inside an evidence snippet, which is the edit a curator most often makes
    and the one a coarser check (node count, edge count) would miss."""
    edited = {**GRAPH, "edges": [{**GRAPH["edges"][0],
                                  "evidence": [{"reference": "ARO:1", "snippet": "BETTER"}]}]}
    assert promote.graph_fingerprint(edited) != promote.graph_fingerprint(GRAPH)


def test_the_fingerprint_is_over_the_EMITTED_bytes():
    """Hashed over `_dump`, which is what reaches disk -- so it answers "is the file still
    what I wrote" rather than a question about Python object identity."""
    import hashlib
    expected = hashlib.sha256("\n".join(promote._dump(GRAPH)).encode()).hexdigest()
    assert promote.graph_fingerprint(GRAPH) == expected


def test_the_curation_entry_carries_the_hash_only_when_given_a_graph():
    """A caller that has no graph must not write a field claiming to fingerprint one."""
    assert "emitted_hash" not in promote.curation_entry({})
    assert promote.curation_entry({}, GRAPH)["emitted_hash"] == promote.graph_fingerprint(GRAPH)


# --- reading it back ----------------------------------------------------------------------

def test_promoter_wrote_this_returns_None_when_the_field_is_absent():
    """None means CANNOT TELL, not "unedited". Every record promoted before #204 lacks the
    field, so a caller that reads None as permission would protect nothing that exists."""
    doc = {"curation_history": [{"curator": "edison-causal-graphs", "action": "x"}]}
    assert promote.promoter_wrote_this(doc) is None


def test_promoter_wrote_this_ignores_another_curators_event():
    doc = {"curation_history": [{"curator": "someone-else", "emitted_hash": "deadbeef"}]}
    assert promote.promoter_wrote_this(doc) is None


def test_promoter_wrote_this_takes_the_LATEST_of_its_own_events():
    """A record promoted twice carries two events; the current content corresponds to the
    last one. Taking the first would refuse every twice-promoted record forever."""
    doc = {"curation_history": [
        {"curator": "edison-causal-graphs", "emitted_hash": "old"},
        {"curator": "edison-causal-graphs", "emitted_hash": "new"},
    ]}
    assert promote.promoter_wrote_this(doc) == "new"


def test_promoter_wrote_this_survives_a_malformed_history_entry():
    doc = {"curation_history": ["not a mapping",
                                {"curator": "edison-causal-graphs", "emitted_hash": "h"}]}
    assert promote.promoter_wrote_this(doc) == "h"


# --- the guard, end to end through the real CLI -------------------------------------------

OBO = REPO / "data" / "raw" / "aro" / "aro.obo"
pytestmark_obo = pytest.mark.skipif(
    not OBO.exists(), reason="data/raw/aro/aro.obo absent (gitignored); run just fetch-aro")


@pytestmark_obo
def test_a_repromote_REFUSES_records_it_did_not_write():
    """The measured case, and it is not the latent one #204 describes.

    That issue looked for records with more than one GRAPH and found none. The real shape
    is more than one CONFIG claiming one graph. On ARO:3000076 a `--repromote` would
    rewrite 1,599 records, and 1,346 of them hold a graph this config did not write --
    every one reproducing from a different claiming config, none of them in #408's drifted
    set. The default now refuses those and writes the other 253.
    """
    import re
    import subprocess
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "promote_family_drafts.py"),
         "--family", "ARO:3000076", "--repromote"],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout[-800:]
    refused = set(re.findall(r"REFUSED (ARO:\d+):", out.stdout))
    assert len(refused) > 1_000, f"the guard refused only {len(refused)}"
    assert "REFUSED (edited since promotion, or unverifiable)" in out.stdout
    written = re.search(r"family ARO:3000076 .*?: ([\d,]+) records written", out.stdout)
    assert written and 0 < int(written.group(1).replace(",", "")) < len(refused), (
        "the guard must not refuse everything -- a re-promotion that can never run is not "
        f"a safer re-promotion\n{out.stdout[-400:]}")


@pytestmark_obo
def test_repromote_edited_is_the_documented_way_through():
    """The escape must actually escape, or curators will reach for `git checkout` instead."""
    import re
    import subprocess
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "promote_family_drafts.py"),
         "--family", "ARO:3000076", "--repromote", "--repromote-edited"],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout[-800:]
    assert "REFUSED" not in out.stdout
    written = re.search(r"family ARO:3000076 .*?: ([\d,]+) records written", out.stdout)
    assert written and int(written.group(1).replace(",", "")) > 1_500, out.stdout[-400:]


@pytestmark_obo
def test_the_guard_leaves_the_corpus_alone_without_apply():
    """Belt and braces on a test that runs the real promoter over the real corpus: a
    dry-run must write nothing, or these tests are themselves the destructive path."""
    import subprocess
    before = subprocess.run(["git", "status", "--porcelain", "--", "data/traits"],
                            capture_output=True, text=True, cwd=REPO).stdout
    subprocess.run([sys.executable, str(REPO / "scripts" / "promote_family_drafts.py"),
                    "--family", "ARO:3000076", "--repromote"],
                   capture_output=True, text=True, cwd=REPO)
    after = subprocess.run(["git", "status", "--porcelain", "--", "data/traits"],
                           capture_output=True, text=True, cwd=REPO).stdout
    assert before == after, "a dry run modified the corpus"


@pytestmark_obo
def test_a_written_record_CARRIES_the_hash_of_the_graph_it_got(tmp_path, monkeypatch):
    """The forward-protection half, and nothing tested it: removing `graph` from the
    `curation_entry` call left all eleven other tests green. A fingerprint that is checked
    but never written protects exactly nothing, and every record promoted from now on
    would have fallen back to the weak test forever.

    Runs the real promoter with --apply against a COPY of one record, so the assertion is
    about bytes on disk rather than about a return value.
    """
    import shutil
    import yaml
    src = REPO / "data" / "traits" / "function" / "resistance" / "aro"
    # a record this family re-promotes cleanly today (not one of the 1,346 refused)
    import re
    import subprocess
    probe = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "promote_family_drafts.py"),
         "--family", "ARO:3000076", "--repromote"],
        capture_output=True, text=True, cwd=REPO)
    refused = set(re.findall(r"REFUSED (ARO:\d+):", probe.stdout))
    sandbox = tmp_path / "aro"
    sandbox.mkdir()
    # SELECTED BY ANCESTRY, not just "the first re-promotable record". The first version
    # took any `is_ours` record in the directory -- which need not be under this family at
    # all, so the promoter's ancestry check skipped it and the run wrote nothing while
    # every counter stayed 0. A test that exercises no code path reads exactly like one
    # that passes.
    import enrich_aro_resistance as E
    terms = E.parse_obo(E.OBO)
    chosen = None
    for path in sorted(src.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', text, re.M)
        if not m or m.group(1) in refused:
            continue
        if "ARO:3000076" not in E.ancestry(terms, m.group(1)):
            continue
        if "graph_id: resistance\n" in text and "curator: edison-causal-graphs" in text:
            chosen = path
            break
    assert chosen is not None, "no re-promotable in-family record found for the write path"
    shutil.copy(chosen, sandbox / chosen.name)

    monkeypatch.setattr(promote, "ARO_DIR", sandbox)
    monkeypatch.setattr(sys, "argv", ["promote_family_drafts.py", "--family", "ARO:3000076",
                                      "--repromote", "--apply"])
    assert promote.main() == 0

    doc = yaml.safe_load((sandbox / chosen.name).read_text(encoding="utf-8"))
    graph = next(g for g in doc["causal_graphs"] if g["graph_id"] == "resistance")
    recorded = promote.promoter_wrote_this(doc)
    assert recorded is not None, "the written record carries no emitted_hash"
    assert recorded == promote.graph_fingerprint(graph), (
        "the recorded hash does not match the graph actually written -- the fingerprint "
        "would refuse this record on the next re-promotion")
