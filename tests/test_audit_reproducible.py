"""Does each promoter-owned record match what its config would emit today? (#408)

Nothing related a record on disk to the config that claims it. `--verify-all` checks that a
config's CURIEs RESOLVE and never that the records it owns match what it would write, so
config edits landed without a `--repromote` and the corpus drifted silently.

THE BUCKETS ARE THE DESIGN, and a scalar would have been actively misleading: when #408 was
first classified, 449 records differed by TEXT and only 78 differed once parsed — the rest
was YAML layout from before the dumper was standardised (#194). Re-promoting 371 no-ops
would have read as progress while a real semantic drift hid in the same total.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import audit_reproducible as A  # noqa: E402

SCRIPT = REPO / "scripts" / "audit_reproducible.py"
BASELINE = REPO / "audit" / "reproducible-baseline.json"
OBO = REPO / "data" / "raw" / "aro" / "aro.obo"


def _graph(**over):
    g = {"graph_id": "resistance", "title": "t", "description": "d",
         "nodes": [{"node_id": "determinant"}],
         "edges": [{"subject": "determinant", "object": "resistance",
                    "evidence": [{"reference": "ARO:1", "snippet": "s", "notes": "n"}]}]}
    g.update(over)
    return g


def test_classify_separates_layout_from_prose_from_evidence_from_structure():
    """The four outcomes that must not be collapsed into one number."""
    old = _graph()
    assert A.classify(old, _graph()) == "reproduces"

    # graph-level prose moved: the config's wording evolved after promotion
    assert A.classify(old, _graph(description="different")) == "description"
    assert A.classify(old, _graph(title="different")) == "description"

    # an edge's evidence differs -- a snippet, reference or note
    ev = _graph()
    ev["edges"][0]["evidence"][0]["notes"] = "changed"
    assert A.classify(old, ev) == "evidence"

    # the graph itself differs -- this is the bucket that matters
    st = _graph()
    st["edges"].append({"subject": "determinant", "object": "drug0"})
    assert A.classify(old, st) == "structure"
    nodes = _graph(nodes=[{"node_id": "determinant"}, {"node_id": "extra"}])
    assert A.classify(old, nodes) == "structure"
    # an edge whose PREDICATE moved is structural, not evidence
    pred = _graph()
    pred["edges"][0]["predicate_id"] = "RO:0002411"
    assert A.classify(old, pred) == "structure"


def test_a_prose_change_is_not_reported_as_structural():
    """`description` and `structure` carry opposite consequences: one is a trivial
    re-promotion, the other may destroy a curator's work (#204). Conflating them is how a
    re-promotion sweep eats hand-added literature."""
    old = _graph()
    new = _graph(description="the config's prose evolved")
    assert A.classify(old, new) == "description"
    assert A.classify(old, new) != "structure"


def test_the_baseline_key_carries_the_bucket():
    """A record moving from `description` to `structure` is a NEW fact, not the same one at
    a different severity -- so the bucket is part of its identity."""
    p = pathlib.Path("data/traits/function/resistance/aro/x.yaml")
    a = A.baseline_key("description", "ARO:1", p)
    b = A.baseline_key("structure", "ARO:1", p)
    assert a != b
    assert A.baseline_key("description", "ARO:1", p) == a


def test_diff_baseline_reports_both_directions():
    known = {"description|ARO:1|p": 1, "structure|ARO:2|p": 1}
    fixed, new = A.diff_baseline(dict(known), known)
    assert (fixed, new) == ([], [])
    # a SWAP: one fixed, one appeared, total unchanged -- the case a ceiling cannot see
    swapped = {"description|ARO:1|p": 1, "structure|ARO:3|p": 1}
    fixed, new = A.diff_baseline(swapped, known)
    assert new == ["structure|ARO:3|p"] and fixed == ["structure|ARO:2|p"]


def test_it_refuses_a_tree_with_no_promoter_owned_records(tmp_path):
    """#418 and #432: a check that examined nothing must not report a clean corpus. The
    recipe forwards {{args}}, so a typo'd --aro-dir would otherwise be a silent bypass."""
    empty = tmp_path / "aro"
    empty.mkdir()
    (empty / "x.yaml").write_text("identifier: ARO:1\n", encoding="utf-8")
    out = subprocess.run([sys.executable, str(SCRIPT), "--aro-dir", str(empty)],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 1, out.stdout
    assert "examined nothing" in out.stdout


@pytest.mark.skipif(not OBO.exists(), reason="data/raw/aro/aro.obo absent; run just fetch-aro")
def test_the_committed_baseline_matches_the_corpus_and_the_probe_fired():
    """The real thing. Asserts the sweep actually examined the corpus as well as passing --
    'DRIFTED: 0 of 0' would satisfy a naive check."""
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--max-drift", "31", "--baseline", str(BASELINE)],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout[-1500:]
    assert "0 NEW" in out.stdout, out.stdout[-800:]
    import re
    m = re.search(r"promoter-owned records examined: ([\d,]+)", out.stdout)
    assert m and int(m.group(1).replace(",", "")) >= 7_000, out.stdout[:400]
    m2 = re.search(r"DRIFTED: ([\d,]+) of ([\d,]+) comparable", out.stdout)
    assert m2, out.stdout[:600]
    assert int(m2.group(2).replace(",", "")) >= 1_000, "the comparable set collapsed"


@pytest.mark.skipif(not OBO.exists(), reason="aro.obo absent")
def test_the_baseline_is_not_empty_and_names_real_records():
    """An empty baseline would make the identity gate vacuous while the ceiling still
    passed. And a key naming a record that no longer exists is stale, not clean."""
    known = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert known, "an empty baseline makes the identity gate vacuous"
    for key in known:
        bucket, ident, rel = key.split("|", 2)
        assert bucket in A.BUCKETS, bucket
        assert ident.startswith("ARO:"), ident
        assert (REPO / rel).exists(), f"baseline names a missing record: {rel}"
