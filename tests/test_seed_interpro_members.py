"""The InterPro member-database seeder (#162).

Six sources (PIRSF, PRINTS, SUPERFAMILY, SFLD, SMART, HAMAP) share one seeder, so
a defect here is a defect in all six at once. The tests cover the three things
that decide what a record says: which axis it lands on, whose licence it carries,
and whether an unreviewed machine-written abstract can reach `definition`.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from seed_interpro_members import (  # noqa: E402
    DB_OVERRIDE, LICENSES, MEMBER_DBS, TYPE_MAP, UNSETTLED, build_yaml,
    is_curated_abstract,
)

ABSTRACT = "A curated description of the family, written by a person."


def sig(accession="PIRSF000005", name="Cytochrome c4", type_="family",
        integrated="IPR024167"):
    return {"accession": accession, "name": name, "type": type_,
            "integrated": integrated}


def entry(abstract=ABSTRACT, llm=False, reviewed=False, name="Cytochrome c4"):
    return {"name": name, "abstract": abstract, "llm": llm, "reviewed": reviewed}


# --- the laundering guard ----------------------------------------------------------

def test_a_curator_written_abstract_becomes_the_definition():
    text, _, _ = build_yaml("sfld", sig("SFLDF00001", "x"), entry())
    r = yaml.safe_load(text)
    assert r["definition"] == ABSTRACT
    assert r["definitions"][0]["method"] == "SOURCED"


def test_an_unreviewed_llm_abstract_is_never_promoted():
    """THE POINT. Stamping machine text as `definition_source: InterPro` would
    launder it into a curated KB in a way nobody could later detect (#92). It is
    kept in definitions[] so a curator can promote it deliberately."""
    text, _, _ = build_yaml("sfld", sig("SFLDF00001", "x"), entry(llm=True, reviewed=False))
    r = yaml.safe_load(text)
    assert r["definition"] != ABSTRACT
    assert "no curated interpro abstract" in r["definition"].lower()
    kept = [d for d in r["definitions"] if ABSTRACT in d["text"]]
    assert len(kept) == 1, "the LLM abstract must still be carried"
    assert "not curator-reviewed" in kept[0]["source"]


def test_a_reviewed_llm_abstract_is_allowed():
    assert is_curated_abstract(entry(llm=True, reviewed=True))
    assert not is_curated_abstract(entry(llm=True, reviewed=False))
    assert not is_curated_abstract(entry(abstract=""))
    assert not is_curated_abstract(None)


# --- axis routing ------------------------------------------------------------------

@pytest.mark.parametrize("type_,category", [
    ("family", "SEQ_FAMILY"),
    ("domain", "SEQ_DOMAIN"),
    ("homologous_superfamily", "SEQ_HOMOLOGOUS_SUPERFAMILY"),
    ("repeat", "SEQ_REPEAT"),
])
def test_routing_follows_the_signature_type(type_, category):
    """PRINTS alone spans domain, family and repeat, so routing cannot be
    per-database."""
    text, _, _ = build_yaml("prints", sig("PR00001", "GLABLOOD", type_), entry())
    r = yaml.safe_load(text)
    assert r["trait_category"] == category
    assert r["trait_axis"] == "SEQUENCE"


def test_superfamily_is_a_sequence_trait_not_a_structure_one():
    """SUPERFAMILY's class boundaries come from SCOP, but the model is an HMM.
    Axis follows the representation, so STRUCT_HOMOLOGOUS_SUPERFAMILY -- which is
    reserved for classifications grouped from 3D coordinates -- would be wrong."""
    text, _, _ = build_yaml("prints", sig("PR00001", "Something", "homologous_superfamily"),
                            entry())
    r = yaml.safe_load(text)
    assert r["trait_axis"] == "SEQUENCE"
    assert r["trait_category"] == "SEQ_HOMOLOGOUS_SUPERFAMILY"


def test_sfld_overrides_the_type_and_goes_to_the_function_axis():
    """SFLD classes are defined by conserved chemistry, the same test that routes
    NCBIfam equivalogs to FUNC_PROTEIN_FAMILY. Its signatures are typed 'family'
    by InterPro, so without the override they would land on SEQUENCE."""
    text, subdir, _ = build_yaml("sfld", sig("SFLDF00001", "mannonate dehydratase"),
                                 entry())
    r = yaml.safe_load(text)
    assert r["trait_axis"] == "FUNCTION"
    assert r["trait_category"] == "FUNC_PROTEIN_FAMILY"
    assert subdir == "function/protein_family/sfld"
    assert DB_OVERRIDE["sfld"][1] == "FUNC_PROTEIN_FAMILY"


def test_every_routing_target_is_a_real_schema_category():
    schema = yaml.safe_load(
        (REPO / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml")
        .read_text(encoding="utf-8"))
    permitted = set(schema["enums"]["ProteinTraitCategoryEnum"]["permissible_values"])
    for _, cat, _ in list(TYPE_MAP.values()) + list(DB_OVERRIDE.values()):
        assert cat in permitted, cat


# --- licence -----------------------------------------------------------------------

def test_licence_is_per_source_not_blanket_public_domain():
    """Seeding via InterPro does NOT make a member database CC0. InterPro's
    dedication names exactly four resources -- InterPro, Pfam, PRINTS, SFLD --
    and says signature collections may carry different terms."""
    assert "CC0" in LICENSES["sfld"] and "CC0" in LICENSES["prints"]
    assert "CC-BY 4.0" in LICENSES["hamap"] and "CC0" not in LICENSES["hamap"]
    for db in ("pirsf", "ssf", "smart"):
        assert db not in LICENSES, (
            f"{db} has no settled licence; giving it one here would assert "
            f"redistribution rights nobody has verified")


def test_the_record_carries_its_own_source_licence():
    text, _, _ = build_yaml("sfld", sig("SFLDF00001", "x"), entry())
    assert yaml.safe_load(text)["license"] == LICENSES["sfld"]


# --- emission ----------------------------------------------------------------------

def test_the_nested_definitions_block_is_indented_for_its_depth():
    """THE SHIPPED BUG, caught by the canary. `folded` indents by two, correct for
    a top-level key; a definitions[] entry is one list level deeper and needs six.
    Emitting four put the text at the same depth as its own `text:` key, so the
    record either failed to parse or parsed with the value lost."""
    text, _, _ = build_yaml("sfld", sig("SFLDF00001", "x"), entry())
    r = yaml.safe_load(text)               # would raise, or lose the value, if wrong
    assert r["definitions"][0]["text"] == ABSTRACT
    assert "\n      " in text.split("definitions:")[1]


def test_identifier_uses_the_corpus_canonical_prefix():
    for db in LICENSES:
        prefix = MEMBER_DBS[db][0]
        acc = {"prints": "PR00001", "sfld": "SFLDF00001", "hamap": "MF_00001"}[db]
        _, _, ident = build_yaml(db, sig(acc, "x", "family"), entry())
        assert ident == f"{prefix}:{acc}"


def test_a_database_with_no_settled_licence_cannot_be_seeded():
    """Enforced in code, not by memory: publishing without redistribution rights
    is not something a later run can undo."""
    assert set(UNSETTLED) == {"smart", "pirsf", "ssf"}
    assert not (set(UNSETTLED) & set(LICENSES))
    for db in UNSETTLED:
        with pytest.raises(KeyError):
            build_yaml(db, sig("PIRSF000005", "x", "family"), entry())


def test_an_unintegrated_signature_still_gets_a_record():
    """303 SFLD signatures exist but only 163 are integrated into InterPro. The
    other 140 have no abstract to inherit and must not be silently dropped."""
    text, _, _ = build_yaml("sfld", sig("SFLDF00099", "orphan", integrated=None), None)
    r = yaml.safe_load(text)
    assert r["identifier"] == "SFLD:SFLDF00099"
    assert "mapped_xrefs" not in r, "nothing to cross-reference without an entry"
    assert r["definitions"][0]["method"] == "GENERATED"


# --- SFLD hierarchy (#162 review) ---------------------------------------------------

def test_the_immediate_parent_is_the_deepest_ancestor_not_the_last(tmp_path,
                                                                   monkeypatch):
    """EBI's file lists ANCESTORS, unordered. Taking the last token would be the
    obvious reading and is wrong: `SFLDF00425: SFLDS00029 SFLDG01116` happens to
    end with the group, but `SFLDF00045: SFLDG01129 SFLDG01135 SFLDS00003` ends
    with the superfamily. Depth is derived from the file itself -- an ancestor's
    own ancestor count.
    """
    import seed_interpro_members as sim
    f = tmp_path / "h.txt"
    f.write_text(
        "SFLDS00003:\n"                       # root, no ancestors
        "SFLDG01129: SFLDS00003\n"            # group under the root
        "SFLDG01135: SFLDS00003 SFLDG01129\n"  # nested group, deeper
        "SFLDF00045: SFLDG01129 SFLDG01135 SFLDS00003\n",  # ends with the ROOT
        encoding="utf-8")
    monkeypatch.setattr(sim, "SFLD_HIERARCHY", f)
    parents = sim.sfld_parents()
    assert parents["SFLDF00045"] == "SFLDG01135", "took the last token, not the deepest"
    assert parents["SFLDG01135"] == "SFLDG01129"
    assert parents["SFLDG01129"] == "SFLDS00003"
    assert "SFLDS00003" not in parents, "a root has no parent"


def test_a_missing_hierarchy_file_is_not_fatal(tmp_path, monkeypatch):
    """The hierarchy is an enrichment; its absence must not stop a seed."""
    import seed_interpro_members as sim
    monkeypatch.setattr(sim, "SFLD_HIERARCHY", tmp_path / "absent.txt")
    assert sim.sfld_parents() == {}


def test_parent_traits_is_emitted_as_a_curie_list():
    text, _, _ = build_yaml("sfld", sig("SFLDG01162", "I"), entry(),
                            {"SFLDG01162": "SFLDS00036"})
    r = yaml.safe_load(text)
    assert r["parent_traits"] == ["SFLD:SFLDS00036"]


def test_no_parent_traits_key_when_there_is_no_parent():
    text, _, _ = build_yaml("sfld", sig("SFLDS00036", "enolase superfamily"), entry(), {})
    assert "parent_traits" not in yaml.safe_load(text)
