"""The records and the equivalence overlay must agree (#447).

`data/equivalence/cross_source.tsv` and a record's `mapped_xrefs` assert the same thing --
*this member signature is the same entry as that InterPro entry* -- and both derive from
`interpro.xml`'s `member_list`. Nothing compared them, and they disagreed for the whole
life of #344: `build_equivalence.py` parsed `member_list` correctly from the start, so the
COMMITTED TSV held the right answer while 335 Pfam records asserted the entry that merely
mentions them.

These tests run without `data/raw`, which is the point. `audit-pfam-interpro` is the
stronger check and cannot run in CI; this one can, and would have caught #344.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

SCRIPT = REPO / "scripts" / "audit_equivalence_consistency.py"

TSV = ("subject\tpredicate\tobject\trelation_source\n"
       "Pfam:PF00575\tbiolink:close_match\tInterPro:IPR003029\tinterpro:pfam\n"
       "Pfam:PF00246\tbiolink:close_match\tInterPro:IPR000834\tinterpro:pfam\n")


def _rec(ipr):
    return ("identifier: Pfam:PF00575\n"
            "mapped_xrefs:\n"
            f"- object: InterPro:{ipr}\n"
            "  mapping_source: pfam2interpro\n")


def _run(tmp_path, record_text, tsv=TSV):
    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True, exist_ok=True)
    (traits / "r.yaml").write_text(record_text, encoding="utf-8")
    t = tmp_path / "cs.tsv"
    t.write_text(tsv, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--traits-root", str(tmp_path / "traits"),
         "--tsv", str(t)], capture_output=True, text=True, cwd=REPO)


def test_it_fires_on_the_disagreement_that_was_344(tmp_path):
    """IPR059328 is the entry whose ABSTRACT mentions PF00575; IPR003029 is the one whose
    member_list contains it. This is the exact shape of all 335."""
    bad = _run(tmp_path, _rec("IPR059328"))
    assert bad.returncode == 1, bad.stdout
    assert "DISAGREE:                     1" in bad.stdout, bad.stdout
    assert "IPR003029" in bad.stdout and "IPR059328" in bad.stdout


def test_it_passes_when_they_agree(tmp_path):
    ok = _run(tmp_path, _rec("IPR003029"))
    assert ok.returncode == 0, ok.stdout
    assert "DISAGREE:                     0" in ok.stdout


def test_it_refuses_when_nothing_is_comparable(tmp_path):
    """A gate that compared nothing must not report a clean corpus -- #418 and #432, which
    this repo has now shipped twice."""
    out = _run(tmp_path, "identifier: Pfam:PF99999\n", tsv=TSV)
    assert out.returncode == 1, out.stdout
    assert "nothing was comparable" in out.stdout


def test_it_reports_what_it_could_not_check(tmp_path):
    """The overlay only holds a pair when BOTH records exist, so most record xrefs have
    nothing to compare against. A gate silently covering a fraction of its subject is how
    '0 failures' comes to mean nothing.

    (An earlier version built an unused `extra` string ending in a YAML `---` and asserted
    it was non-empty -- a tautology, and the residue of a multi-document case that was
    never written. That case is a real latent gap: `IDENT.search` takes the FIRST match,
    so a multi-doc record would attribute every xref to the first document's identifier.
    0 such records exist, so it is noted rather than tested.)
    """
    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    (traits / "a.yaml").write_text(_rec("IPR003029"), encoding="utf-8")
    (traits / "b.yaml").write_text(
        "identifier: Pfam:PF11111\n"
        "mapped_xrefs:\n- object: InterPro:IPR999999\n  mapping_source: pfam2interpro\n",
        encoding="utf-8")
    t = tmp_path / "cs.tsv"
    t.write_text(TSV, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--traits-root", str(tmp_path / "traits"),
         "--tsv", str(t)], capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout
    assert "record asserts an xref, no overlay row" in out.stdout, out.stdout
    assert "  1  record asserts an xref" in out.stdout, out.stdout


def test_it_sees_an_xref_carrying_a_predicate(tmp_path):
    """Same latent hole the #344 gates had: `MappedXref` has an optional `predicate` slot
    and 127 xrefs in this field already use it, so requiring adjacency makes a wrong
    record invisible."""
    three_key = ("identifier: Pfam:PF00575\n"
                 "mapped_xrefs:\n"
                 "- object: InterPro:IPR059328\n"
                 "  predicate: skos:relatedMatch\n"
                 "  mapping_source: pfam2interpro\n")
    out = _run(tmp_path, three_key)
    assert out.returncode == 1, out.stdout
    assert "DISAGREE:                     1" in out.stdout


def test_the_committed_corpus_agrees_with_the_committed_overlay():
    """The real thing, on committed files only -- no data/raw, so this runs in CI.

    Asserts the probe FIRED as well as passing: 0 comparable subjects would exit 1 by the
    script's own guard, but pinning the count here means a future change that quietly
    narrows the sweep is visible rather than silently green.
    """
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=REPO)
    assert out.returncode == 0, out.stdout[-1500:]
    import re
    def _n(label):
        m = re.search(rf"^{label}:\s+([\d,]+)", out.stdout, re.M)
        assert m, f"{label} missing from output:\n{out.stdout[:800]}"
        return int(m.group(1).replace(",", ""))

    # Pin BOTH SIDES, not just the comparable count. A change that silently dropped every
    # non-Pfam subject would leave `COMPARABLE` untouched and go green, which is the shape
    # of narrowing this file is written against.
    assert _n(r"COMPARABLE \(in both\)") >= 17_000, out.stdout
    assert _n("overlay subjects") >= 24_000, out.stdout
    assert _n("records asserting an xref") >= 43_000, out.stdout
    # and the two uncovered directions are REPORTED, not just computed
    assert "source outside the overlay's vocabulary" in out.stdout
    assert "overlay row, record asserts no xref" in out.stdout


# ---------------------------------------------------------------------------------------
# Review follow-ups (#451 review): the regex fails OPEN on any shape it was not written
# for, and a pool worker's exception was undiagnosable.
# ---------------------------------------------------------------------------------------

def test_an_unreadable_xref_shape_fails_loud_instead_of_silently_counting_zero(tmp_path):
    """`XREF` is a regex over YAML text. For `mapping_source` before `object`, a quoted
    object, CRLF or flow style it matches nothing -- and "matches nothing" is
    indistinguishable from "no xrefs here", which turns the gate's entire output ("0
    disagreements") into a lie.

    Nothing in the corpus uses those shapes today. The counter exists so that the day one
    does, the run says so rather than absorbing it.
    """
    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    (traits / "r.yaml").write_text(
        "identifier: Pfam:PF00575\n"
        "mapped_xrefs:\n"
        "- mapping_source: pfam2interpro\n"          # key order reversed
        "  object: InterPro:IPR003029\n", encoding="utf-8")
    t = tmp_path / "cs.tsv"
    t.write_text(TSV, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--traits-root", str(tmp_path / "traits"),
         "--tsv", str(t)], capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 1, out.stdout
    assert "not matched by XREF" in out.stderr, out.stderr[-600:]
    assert "do not raise the threshold" in out.stderr


def test_a_read_error_names_the_file(tmp_path):
    """Unhandled, a pool worker gives a traceback whose deepest frame is inside
    `concurrent.futures`, and CI cannot tell it from a real disagreement."""
    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    (traits / "x.yaml").mkdir()                      # a directory where a file is expected
    t = tmp_path / "cs.tsv"
    t.write_text(TSV, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--traits-root", str(tmp_path / "traits"),
         "--tsv", str(t)], capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 1
    assert "could not read" in out.stderr and "x.yaml" in out.stderr, out.stderr[-400:]


def test_the_coverage_report_names_both_uncovered_directions(tmp_path):
    """The first version printed one gap and framed the other away: a denominator padded
    with 14,949 subjects that can never be comparable, and total silence about the 6,329
    overlay rows no record asserts. Both must be named, with counts."""
    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    # one comparable, one whose source the overlay cannot represent
    (traits / "a.yaml").write_text(_rec("IPR003029"), encoding="utf-8")
    (traits / "b.yaml").write_text(
        "identifier: PANTHER:PTHR10000\n"
        "mapped_xrefs:\n- object: InterPro:IPR000001\n"
        "  mapping_source: interpro-member-list\n", encoding="utf-8")
    t = tmp_path / "cs.tsv"
    t.write_text(TSV, encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--traits-root", str(tmp_path / "traits"),
         "--tsv", str(t)], capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout
    assert "source outside the overlay's vocabulary (PANTHER 1)" in out.stdout, out.stdout
    assert "overlay row, record asserts no xref (Pfam 1)" in out.stdout, out.stdout
    # and the percentage is over what it COULD compare, not over a padded denominator
    assert "of the 1 this check COULD compare, it compares 100.0%" in out.stdout, out.stdout
