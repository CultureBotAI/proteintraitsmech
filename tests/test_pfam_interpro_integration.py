"""Which InterPro entry does a Pfam record borrow its prose from? (#344)

`pfam2interpro.tsv` is the union of two relations that mean opposite things:

    <member_list><db_xref db="PFAM" dbkey="PF00575" name="S1"/></member_list>
        IPR003029 IS the integration of PF00575
    <abstract>... associated with <db_xref db="PFAM" dbkey="PF00575"/> ...</abstract>
        IPR059328 merely MENTIONS PF00575 in prose

Three scripts read that file; two of them last-wins. The mention won 407 times, and each
of those records took a NEIGHBOURING domain's abstract as its own definition -- fluent,
on-topic prose that says, if you read it, that it is about something else:

    Pfam:PF13646 "HEAT repeats"
      -> "This domain is found in conserved virulence factors. It is often found in
          association with Pfam:PF13646 and Pfam:PF08712."

Every fixture here is built from XML shaped like the real release, so the tests fail if
the member_list/abstract distinction is ever collapsed again.
"""

from __future__ import annotations

import gzip
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from interpro_text import load_member_integration  # noqa: E402

# The shape that matters: PF00575 is a MEMBER of IPR003029 and is MENTIONED by IPR059328.
FIXTURE_XML = """<?xml version="1.0"?>
<interprodb>
<interpro id="IPR003029" short_name="S1_domain" type="Domain">
  <abstract><p>The S1 domain binds RNA.</p></abstract>
  <member_list>
    <db_xref protein_count="112789" db="PFAM" dbkey="PF00575" name="S1"/>
  </member_list>
</interpro>
<interpro id="IPR059328" short_name="DUF8284" type="Domain">
  <abstract><p>Uncharacterised, often associated with <db_xref db="PFAM" dbkey="PF00575"/>.</p></abstract>
  <member_list>
    <db_xref protein_count="12" db="PFAM" dbkey="PF99999" name="DUF8284"/>
  </member_list>
</interpro>
<interpro id="IPR000111" short_name="Orphan" type="Domain">
  <abstract><p>Mentions <db_xref db="PFAM" dbkey="PF88888"/> but integrates nothing.</p></abstract>
</interpro>
</interprodb>
"""


def _xml(tmp_path):
    p = tmp_path / "interpro.xml.gz"
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        fh.write(FIXTURE_XML)
    return p


def test_member_list_wins_over_a_mention_in_an_abstract(tmp_path):
    """The whole defect in one assertion.

    A naive sweep for `db_xref db="PFAM"` returns PF00575 twice -- IPR003029 and
    IPR059328 -- and last-wins picks the abstract mention. `load_member_integration`
    must return only the member_list one.
    """
    got = load_member_integration(_xml(tmp_path))
    assert got["PF00575"] == "IPR003029", "an abstract mention was taken as an integration"
    assert got["PF99999"] == "IPR059328"
    # a signature that appears ONLY inside prose is not integrated at all, and must be
    # absent rather than mapped to the entry that mentions it
    assert "PF88888" not in got
    assert len(got) == 2


def test_no_signature_is_integrated_twice_in_the_real_release():
    """The invariant the repair relies on. If InterPro ever put one Pfam in two member
    lists, `load_member_integration`'s last-wins dict would silently pick one and the
    repair would rewrite records to a coin flip."""
    import pytest
    xml = REPO / "data" / "raw" / "interpro" / "interpro.xml.gz"
    if not xml.exists():
        pytest.skip("data/raw/interpro/interpro.xml.gz absent; run `just fetch-interpro`")
    import re
    seen, dupes = {}, []
    inside, ipr = False, None
    with gzip.open(xml, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.search(r'<interpro id="(IPR\d+)"', line)
            if m:
                ipr = m.group(1)
            if "<member_list>" in line:
                inside = True
            if "</member_list>" in line:
                inside = False
            if inside:
                for pf in re.findall(r'dbkey="(PF\d{5})"', line):
                    if pf in seen and seen[pf] != ipr:
                        dupes.append((pf, seen[pf], ipr))
                    seen[pf] = ipr
    assert dupes == [], f"a Pfam signature is in two member lists: {dupes[:5]}"


def test_the_audit_fires_on_a_mention_and_passes_on_a_member(tmp_path):
    """Both directions, through the CLI, so the exit code is what is asserted.

    A detector with no failing case is decoration -- the lesson #433 was filed for.
    """
    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    rec = traits / "s1-pf00575.yaml"

    def _run():
        return subprocess.run(
            [sys.executable, str(REPO / "scripts" / "audit_pfam_interpro.py"),
             "--traits-root", str(tmp_path / "traits"), "--xml", str(_xml(tmp_path))],
            capture_output=True, text=True, cwd=REPO)

    good = ('identifier: Pfam:PF00575\n'
            'definition_source: "InterPro:IPR003029 abstract (Pfam PF00575 maps to this '
            'entry via pfam2interpro)"\n'
            'mapped_xrefs:\n'
            '- object: InterPro:IPR003029\n'
            '  mapping_source: pfam2interpro\n')
    rec.write_text(good, encoding="utf-8")
    ok = _run()
    assert ok.returncode == 0, ok.stdout
    assert "Pfam records examined:        1" in ok.stdout, ok.stdout

    # the definition side alone
    rec.write_text(good.replace('"InterPro:IPR003029 abstract',
                                '"InterPro:IPR059328 abstract'), encoding="utf-8")
    bad = _run()
    assert bad.returncode == 1, bad.stdout
    assert "definition_source names a non-integrating entry: 1" in bad.stdout

    # the xref side alone
    rec.write_text(good.replace("- object: InterPro:IPR003029",
                                "- object: InterPro:IPR059328"), encoding="utf-8")
    bad2 = _run()
    assert bad2.returncode == 1, bad2.stdout
    assert "mapped_xrefs assert a non-integrating entry:     1" in bad2.stdout

    # an UNINTEGRATED family may assert neither
    rec.write_text(good.replace("PF00575", "PF88888"), encoding="utf-8")
    bad3 = _run()
    assert bad3.returncode == 1, bad3.stdout
    assert "(no entry integrates it)" in bad3.stdout


def test_the_audit_refuses_rather_than_passing_when_the_release_is_absent(tmp_path):
    """#432's lesson, applied on the way in: this check IS a comparison against the
    release, so without it there is nothing to compare and 0 would be a lie."""
    traits = tmp_path / "traits"
    traits.mkdir()
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_pfam_interpro.py"),
         "--traits-root", str(traits), "--xml", str(tmp_path / "absent.xml.gz")],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 1
    assert "cannot report anything" in out.stdout


def test_the_xref_repair_repoints_a_mention_and_removes_an_unintegrated_one():
    """The two shapes need opposite treatments, and getting them backwards is plausible:
    'repoint to the nearest entry' is exactly how an unintegrated family would acquire a
    permanent wrong mapping."""
    import repair_pfam_interpro_xrefs as R

    text = ("identifier: Pfam:PF00575\n"
            "mapped_xrefs:\n"
            "- object: GO:0003723\n"
            "  mapping_source: pfam2go\n"
            "- object: InterPro:IPR059328\n"
            "  mapping_source: pfam2interpro\n"
            "license: public domain\n")
    out, reason = R.repair_text(text, "IPR003029")
    assert reason == "repaired"
    assert "- object: InterPro:IPR003029" in out
    assert "IPR059328" not in out
    assert "- object: GO:0003723" in out, "an unrelated xref was disturbed"

    # unintegrated: the assertion goes, and with it a key that would be left empty
    only = ("identifier: Pfam:PF88888\n"
            "mapped_xrefs:\n"
            "- object: InterPro:IPR000111\n"
            "  mapping_source: pfam2interpro\n"
            "license: public domain\n")
    out2, _ = R.repair_text(only, None)
    assert "InterPro" not in out2
    assert "mapped_xrefs:" not in out2, "a dangling mapped_xrefs key would not parse"
    assert out2 == "identifier: Pfam:PF88888\nlicense: public domain\n"

    # an xref from another source is never touched, even when it names InterPro
    other = ("identifier: Pfam:PF00575\n"
             "mapped_xrefs:\n"
             "- object: InterPro:IPR059328\n"
             "  mapping_source: interpro2go\n"
             "license: public domain\n")
    assert R.repair_text(other, "IPR003029")[0] is None


def test_the_repair_refuses_to_change_anything_outside_mapped_xrefs():
    """Guard 3. The first version of the mask re-inserted a marker before `license:`, which
    worked for 4 of 31 records and mis-skipped the other 27 -- so the mask itself is pinned
    here, in both the has-xrefs and the key-removed states."""
    import repair_pfam_interpro_xrefs as R
    with_xrefs = ("identifier: Pfam:PF1\n"
                  "mapped_xrefs:\n- object: InterPro:IPR1\n  mapping_source: pfam2interpro\n"
                  "license: cc0\n")
    without = "identifier: Pfam:PF1\nlicense: cc0\n"
    assert R._mask(with_xrefs) == R._mask(without) == without


# ---------------------------------------------------------------------------------------
# Review follow-ups (#344 review): the branches most likely to be wrong were the untested
# ones, and two gates could report a false clean.
# ---------------------------------------------------------------------------------------

def test_one_entry_per_signature_is_ENFORCED_not_merely_true(tmp_path):
    """The whole repair rests on this: `load_member_integration` is a last-wins dict, so a
    signature in two member lists would be rewritten to whichever entry the parser saw
    last -- a coin flip, applied to a record's definition.

    It was measured true across the release (0 of 29,105) and enforced nowhere, and the
    test that checked it SKIPS in CI because it needs data/raw. So the check moved into
    the loader, where it runs on every call, and this pins it on a fixture that needs
    nothing.
    """
    import pytest
    xml = tmp_path / "dupe.xml.gz"
    with gzip.open(xml, "wt", encoding="utf-8") as fh:
        fh.write("""<?xml version="1.0"?>
<interprodb>
<interpro id="IPR000001" short_name="A" type="Domain">
  <member_list><db_xref db="PFAM" dbkey="PF00001" name="a"/></member_list>
</interpro>
<interpro id="IPR000002" short_name="B" type="Domain">
  <member_list><db_xref db="PFAM" dbkey="PF00001" name="a"/></member_list>
</interpro>
</interprodb>
""")
    with pytest.raises(ValueError, match="more than one member_list"):
        load_member_integration(xml)


def test_the_gates_see_an_xref_that_carries_a_predicate():
    """`MappedXref` has an optional `predicate` slot and 127 xrefs in this very field
    already use the 3-key shape (the Pfam->InterPro->CAZY ones). Both regexes required
    `mapping_source:` to follow `- object:` IMMEDIATELY, so one curation step would have
    made a wrong record invisible -- the audit printing 0 and exiting 0.

    A trailing space did the same thing to the audit, whose `$` under re.M is exact.
    """
    import audit_pfam_interpro as A
    import repair_pfam_interpro_xrefs as R

    three_key = ("identifier: Pfam:PF00575\n"
                 "mapped_xrefs:\n"
                 "- object: InterPro:IPR059328\n"
                 "  predicate: skos:relatedMatch\n"
                 "  mapping_source: pfam2interpro\n"
                 "license: cc0\n")
    assert [m.group("ipr") for m in A.XREF.finditer(three_key)] == ["IPR059328"]
    out, reason = R.repair_text(three_key, "IPR003029")
    assert reason == "repaired" and "InterPro:IPR003029" in out
    assert "predicate: skos:relatedMatch" in out, "the predicate line was dropped"

    trailing = three_key.replace("mapping_source: pfam2interpro\n",
                                 "mapping_source: pfam2interpro \n")
    assert [m.group("ipr") for m in A.XREF.finditer(trailing)] == ["IPR059328"]


def test_the_audit_refuses_a_traits_root_holding_no_pfam_records(tmp_path):
    """#418's silent bypass, one axis over. `is_dir()` was ported and "0 records examined"
    was not, so a REAL directory with no Pfam records printed "0 examined, 0 wrong" and
    exited 0 -- and the recipe forwards {{args}}."""
    empty = tmp_path / "traits"
    (empty / "function").mkdir(parents=True)
    (empty / "function" / "x.yaml").write_text("identifier: ARO:1\n", encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_pfam_interpro.py"),
         "--traits-root", str(empty), "--xml", str(_xml(tmp_path))],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 1, out.stdout
    assert "examined nothing" in out.stdout


def test_the_boilerplate_comes_from_the_release_not_from_a_quoted_yaml_label():
    """The revert path reproduces `seed_pfam.build_yaml`. Recovering the description by
    stripping quotes off the record's `label:` line is not a YAML parse: 1,276 Pfam labels
    are quoted and PF00313's -- whose description really contains single quotes -- decodes
    wrong, leaving a doubled quote in the middle of the sentence.
    """
    import pytest
    import enrich_pfam_definitions as E
    if not E.PFAM_CLANS.exists():
        pytest.skip("data/raw/pfam/Pfam-A.clans.tsv.gz absent; run `just fetch-pfam`")
    got = E.pfam_boilerplate("PF00313")
    assert got == "'Cold-shock' DNA-binding domain. Pfam domain family CSD (Pfam:PF00313)."
    assert "''" not in got, "a YAML-escaped quote leaked into the definition"
    # signature takes the accession only -- passing record text invited reading it back
    assert E.pfam_boilerplate("PF99999999") is None


def test_repair_text_handles_a_duplicate_and_an_already_correct_neighbour():
    """Two branches the first pass left unexercised, both plausible to get wrong."""
    import repair_pfam_interpro_xrefs as R

    # the correct entry is ALREADY present alongside a wrong one -> drop the wrong one,
    # do not add a second copy of the right one
    both = ("identifier: Pfam:PF00575\n"
            "mapped_xrefs:\n"
            "- object: InterPro:IPR003029\n"
            "  mapping_source: pfam2interpro\n"
            "- object: InterPro:IPR059328\n"
            "  mapping_source: pfam2interpro\n"
            "license: cc0\n")
    out, _ = R.repair_text(both, "IPR003029")
    assert out.count("InterPro:IPR003029") == 1
    assert "IPR059328" not in out

    # TWO wrong ones and no right one -> exactly one becomes the right one, the other goes
    two_wrong = both.replace("- object: InterPro:IPR003029", "- object: InterPro:IPR000111")
    out2, _ = R.repair_text(two_wrong, "IPR003029")
    assert out2.count("InterPro:IPR003029") == 1
    assert "IPR000111" not in out2 and "IPR059328" not in out2


def test_enrich_returns_nonzero_when_it_strands_a_record(monkeypatch, tmp_path):
    """It printed the record and returned 0, so `just repair-pfam-interpro` would have
    exited clean while announcing a record it knowingly left wrong.

    Driven through `main()` with the release readers stubbed, rather than by grepping the
    source for `return 1` -- a test that reads the code it is testing proves only that the
    string is present.
    """
    import enrich_pfam_definitions as E

    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    # cites IPR059328; its real entry is IPR003029, whose abstract is absent here; and
    # the Pfam release knows nothing about it, so no boilerplate can be rebuilt
    (traits / "x-pf00575.yaml").write_text(
        "identifier: Pfam:PF00575\n"
        "label: S1\n"
        "definition: >-\n  something borrowed\n"
        'definition_source: "InterPro:IPR059328 abstract (Pfam PF00575 maps to this entry '
        'via pfam2interpro)"\n', encoding="utf-8")

    monkeypatch.setattr(E, "TRAITS", tmp_path / "traits")
    monkeypatch.setattr(E, "XML_GZ", tmp_path)                  # exists() -> True
    monkeypatch.setattr(E, "load_pf2ipr", lambda: {"PF00575": "IPR003029"})
    # returns (abstracts, from_api) since #445 -- the second element records
    # which came from the API and must be cited as a description, not an abstract
    monkeypatch.setattr(E, "load_ipr_abstracts", lambda wanted: ({}, set()))
    monkeypatch.setattr(E, "_PFAM_META", {})                    # nothing rebuildable
    monkeypatch.setattr(sys, "argv", ["enrich_pfam_definitions.py"])

    rc = E.main()
    assert rc == 1, "a run that stranded a record reported success"


def test_enrich_returns_zero_when_it_strands_nothing(monkeypatch, tmp_path):
    """The other half, so the test above cannot pass by the script always failing."""
    import enrich_pfam_definitions as E

    traits = tmp_path / "traits" / "sequence" / "domain" / "pfam"
    traits.mkdir(parents=True)
    (traits / "x-pf00575.yaml").write_text(
        "identifier: Pfam:PF00575\n"
        "label: S1\n"
        "definition: >-\n  something borrowed\n"
        'definition_source: "InterPro:IPR059328 abstract (Pfam PF00575 maps to this entry '
        'via pfam2interpro)"\n', encoding="utf-8")

    monkeypatch.setattr(E, "TRAITS", tmp_path / "traits")
    monkeypatch.setattr(E, "XML_GZ", tmp_path)
    monkeypatch.setattr(E, "load_pf2ipr", lambda: {"PF00575": "IPR003029"})
    monkeypatch.setattr(
        E, "load_ipr_abstracts",
        lambda wanted: ({"IPR003029": "The S1 domain binds RNA, at length."}, set()))
    monkeypatch.setattr(sys, "argv", ["enrich_pfam_definitions.py"])
    assert E.main() == 0
