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
