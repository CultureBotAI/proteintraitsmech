"""The InterPro member-database seeder (#162).

Six sources (PIRSF, PRINTS, SUPERFAMILY, SFLD, SMART, HAMAP) share one seeder, so
a defect here is a defect in all six at once. The tests cover the three things
that decide what a record says: which axis it lands on, whose licence it carries,
and whether an unreviewed machine-written abstract can reach `definition`.
"""

from __future__ import annotations

import gzip
import hashlib
import pathlib
import sys
from types import MappingProxyType

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from seed_interpro_members import (  # noqa: E402
    DB_OVERRIDE,
    LICENSES,
    MEMBER_DBS,
    TYPE_MAP,
    UNSETTLED,
    build_yaml,
    is_curated_abstract,
)
from validate_strict import validate_one  # noqa: E402

ABSTRACT = "A curated description of the family, written by a person."


def sig(accession="PIRSF000005", name="Cytochrome c4", type_="family", integrated="IPR024167"):
    return {"accession": accession, "name": name, "type": type_, "integrated": integrated}


def entry(abstract=ABSTRACT, llm=False, reviewed=False, name="Cytochrome c4"):
    return {"name": name, "abstract": abstract, "llm": llm, "reviewed": reviewed}


# --- the laundering guard ----------------------------------------------------------


def test_a_curator_written_abstract_becomes_the_definition():
    text, _, _ = build_yaml("sfld", sig("SFLDF00001", "x"), entry())
    r = yaml.safe_load(text)
    assert r["definition"] == ABSTRACT
    assert r["definitions"][0]["method"] == "SOURCED"


def test_a_long_curated_abstract_is_never_head_truncated():
    """The defining subtype text can be at the end of an InterPro abstract."""
    abstract = "General family preamble. " + ("context " * 300) + "Subtype definition."
    text, _, _ = build_yaml(
        "prints", sig("PR01893", "Wnt-10", "family", "IPR013302"), entry(abstract)
    )
    record = yaml.safe_load(text)
    assert record["definition"] == abstract
    assert record["definitions"][0]["text"] == abstract


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


@pytest.mark.parametrize(
    "type_,category",
    [
        ("family", "SEQ_FAMILY"),
        ("domain", "SEQ_DOMAIN"),
        ("homologous_superfamily", "SEQ_HOMOLOGOUS_SUPERFAMILY"),
        ("repeat", "SEQ_REPEAT"),
    ],
)
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
    text, _, _ = build_yaml(
        "prints", sig("PR00001", "Something", "homologous_superfamily"), entry()
    )
    r = yaml.safe_load(text)
    assert r["trait_axis"] == "SEQUENCE"
    assert r["trait_category"] == "SEQ_HOMOLOGOUS_SUPERFAMILY"


def test_sfld_overrides_the_type_and_goes_to_the_function_axis():
    """SFLD classes are defined by conserved chemistry, the same test that routes
    NCBIfam equivalogs to FUNC_PROTEIN_FAMILY. Its signatures are typed 'family'
    by InterPro, so without the override they would land on SEQUENCE."""
    text, subdir, _ = build_yaml("sfld", sig("SFLDF00001", "mannonate dehydratase"), entry())
    r = yaml.safe_load(text)
    assert r["trait_axis"] == "FUNCTION"
    assert r["trait_category"] == "FUNC_PROTEIN_FAMILY"
    assert subdir == "function/protein_family/sfld"
    assert DB_OVERRIDE["sfld"][1] == "FUNC_PROTEIN_FAMILY"


def test_every_routing_target_is_a_real_schema_category():
    schema = yaml.safe_load(
        (REPO / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml").read_text(
            encoding="utf-8"
        )
    )
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
            f"redistribution rights nobody has verified"
        )


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
    r = yaml.safe_load(text)  # would raise, or lose the value, if wrong
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


def test_the_immediate_parent_is_the_deepest_ancestor_not_the_last(tmp_path, monkeypatch):
    """EBI's file lists ANCESTORS, unordered. Taking the last token would be the
    obvious reading and is wrong: `SFLDF00425: SFLDS00029 SFLDG01116` happens to
    end with the group, but `SFLDF00045: SFLDG01129 SFLDG01135 SFLDS00003` ends
    with the superfamily. Depth is derived from the file itself -- an ancestor's
    own ancestor count.
    """
    import seed_interpro_members as sim

    f = tmp_path / "h.txt"
    f.write_text(
        "SFLDS00003:\n"  # root, no ancestors
        "SFLDG01129: SFLDS00003\n"  # group under the root
        "SFLDG01135: SFLDS00003 SFLDG01129\n"  # nested group, deeper
        "SFLDF00045: SFLDG01129 SFLDG01135 SFLDS00003\n",  # ends with the ROOT
        encoding="utf-8",
    )
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
    text, _, _ = build_yaml("sfld", sig("SFLDG01162", "I"), entry(), {"SFLDG01162": "SFLDS00036"})
    r = yaml.safe_load(text)
    assert r["parent_traits"] == ["SFLD:SFLDS00036"]


def test_no_parent_traits_key_when_there_is_no_parent():
    text, _, _ = build_yaml("sfld", sig("SFLDS00036", "enolase superfamily"), entry(), {})
    assert "parent_traits" not in yaml.safe_load(text)


# --- PRINTS: titles and hierarchy from the source release ---------------------------


def _kdat_record(code, accession, count, title, description):
    motifs = "".join(
        f"fc; {code}{ordinal}\n"
        "fl; 2\n"
        f"ft; {title} motif {ordinal}\n"
        "fd; AC PROTEIN 1 1\n"
        f"KD; INTER_MOTIF_DISTANCE REGION={ordinal - 1}-{ordinal}; MIN=1; MAX=1\n"
        for ordinal in range(1, count + 1)
    )
    return (
        f"gc; {code}\n"
        f"gx; {accession}\n"
        f"gn; COMPOUND({count})\n"
        f"gt; {title}\n"
        f"gd; {description}\n"
        "fm; FINAL MOTIF-SETS\n"
        "fm; ----------------\n"
        f"{motifs}"
    )


KDAT = _kdat_record(
    "11SGLOBULIN",
    "PR00439",
    6,
    "11-S seed storage protein family signature",
    "Source-native seed storage description.",
) + _kdat_record(
    "GLABLOOD",
    "PR00001",
    4,
    "Coagulation factor GLA domain signature",
    "Source-native GLA description.",
)


def _authenticate_synthetic_prints_fixture(monkeypatch, source_bytes):
    """Test-only allowlist entry for parser-authenticated compact KDAT bytes."""
    import prints_kdat

    fixture_sha256 = hashlib.sha256(source_bytes).hexdigest()
    monkeypatch.setattr(
        prints_kdat,
        "_CANONICAL_RELEASE_FINGERPRINTS",
        MappingProxyType({prints_kdat.PRINTS_42_0_RELEASE: fixture_sha256}),
    )
    return fixture_sha256


def test_prints_titles_come_from_the_kdat_not_the_api(tmp_path, monkeypatch):
    """The API's `name` for a fingerprint is its CODE. PR00001 comes back as
    "GLABLOOD", and the detail endpoint shows `{"name": null, "short":
    "GLABLOOD"}` -- there is no full name there at all. Seeding from the API
    alone would label 2,106 records RETINOIDXR, MTVERTEBRATE and the like."""
    import seed_interpro_members as sim

    f = tmp_path / "k.kdat"
    f.write_text(KDAT, encoding="utf-8")
    monkeypatch.setattr(sim, "PRINTS_KDAT", f)
    fixture_sha256 = _authenticate_synthetic_prints_fixture(monkeypatch, KDAT.encode())
    monkeypatch.setattr(sim, "PRINTS_42_0_SHA256", fixture_sha256)
    titles = sim.prints_titles()
    assert titles["PR00001"]["title"] == "Coagulation factor GLA domain signature"
    assert titles["PR00439"]["motifs"] == 6


def test_the_label_and_the_filename_are_derived_from_the_same_string(tmp_path, monkeypatch):
    """THE CANARY'S FINDING. The first run produced
    `label: "Coagulation factor GLA domain signature"` inside a file named
    `glablood-pr00001.yaml`, because the path was slugified from the API code
    while the label came from the release title."""
    import seed_interpro_members as sim

    titles = {"PR00001": {"title": "Coagulation factor GLA domain signature", "motifs": 4}}
    s = sig("PR00001", "GLABLOOD", "domain")
    assert sim.resolve_label(s, titles) == "Coagulation factor GLA domain signature"
    text, _, _ = build_yaml("prints", s, entry(), None, titles)
    assert yaml.safe_load(text)["label"] == sim.resolve_label(s, titles)


def test_the_motif_count_is_stated_when_a_definition_is_composed():
    """A fingerprint IS an ordered set of motifs; the count is what distinguishes
    it from a single-motif signature, and it is the only substantive thing we can
    say about one with no abstract."""
    titles = {"PR00099": {"title": "Some signature", "motifs": 5}}
    text, _, _ = build_yaml(
        "prints", sig("PR00099", "CODE", "family", integrated=None), None, None, titles
    )
    assert "5-element fingerprint" in yaml.safe_load(text)["definition"]


def test_prints_gd_precedes_interpro_and_the_ordered_model_is_emitted(tmp_path, monkeypatch):
    import seed_interpro_members as sim
    import validate_strict

    source = tmp_path / "k.kdat"
    source.write_text(KDAT, encoding="utf-8")
    monkeypatch.setattr(sim, "PRINTS_KDAT", source)
    fixture_sha256 = _authenticate_synthetic_prints_fixture(monkeypatch, KDAT.encode())
    monkeypatch.setattr(sim, "PRINTS_42_0_SHA256", fixture_sha256)
    monkeypatch.setattr(validate_strict, "PRINTS_42_0_SHA256", fixture_sha256)
    titles = sim.prints_titles()

    text, _, _ = build_yaml(
        "prints",
        sig("PR00001", "GLABLOOD", "domain"),
        entry("Broader integrating InterPro abstract."),
        titles=titles,
    )
    record = yaml.safe_load(text)
    assert record["definition"] == "Source-native GLA description."
    assert record["definition_source"].startswith("PRINTS:PR00001 gd description")
    assert record["definitions"][1]["text"] == "Broader integrating InterPro abstract."
    representation = record["sequence_fingerprint_representations"][0]
    assert representation["source_accession"] == "PRINTS:PR00001"
    assert representation["representation_type"] == "PRINTS_FINAL_ORDERED_MOTIF_SETS"
    assert representation["motif_count"] == 4
    assert [motif["ordinal"] for motif in representation["motifs"]] == [1, 2, 3, 4]
    assert [motif["length"] for motif in representation["motifs"]] == [2, 2, 2, 2]
    assert representation["motifs"][0]["inter_motif_distance_constraint"] == {
        "region_start_ordinal": 0,
        "region_end_ordinal": 1,
        "minimum": 1,
        "maximum": 1,
        "repeat_qualified": False,
    }
    assert "sequence_pattern" not in record
    emitted = tmp_path / "prints-record.yaml"
    emitted.write_text(text, encoding="utf-8")
    assert validate_one(emitted) == []


HIER = """# Last update 21-02-2012
TOP|PR00010|1e-04|2|MID,LEAF
MID|PR00020|1e-04|1|LEAF
LEAF|PR00030|1e-04|0|*
"""


def test_prints_postprocessing_relations_are_not_emitted_as_parent_traits(tmp_path, monkeypatch):
    """InterProScan calls field 5 sibling/hierarchical relations, not descendants."""
    import seed_interpro_members as sim
    import prints_snapshot as snapshot

    f = tmp_path / "h.txt"
    f.write_bytes(
        snapshot.dump_hierarchy_jsonl(snapshot.parse_hierarchy_source(HIER.encode("utf-8")))
    )
    monkeypatch.setattr(sim, "PRINTS_HIERARCHY", f)
    parents = sim.prints_parents()
    assert parents == {}


def test_a_missing_prints_model_or_hierarchy_release_is_fatal(tmp_path, monkeypatch):
    import seed_interpro_members as sim

    monkeypatch.setattr(sim, "PRINTS_KDAT", tmp_path / "absent")
    monkeypatch.setattr(sim, "PRINTS_HIERARCHY", tmp_path / "absent")
    with pytest.raises(sim.PrintsKdatError, match="missing pinned PRINTS source"):
        sim.prints_titles()
    with pytest.raises(sim.PrintsSnapshotError, match="missing normalized PRINTS hierarchy"):
        sim.prints_parents()


def test_prints_main_refuses_to_continue_without_the_pinned_model(tmp_path, monkeypatch):
    import seed_interpro_members as sim

    monkeypatch.setattr(sim, "PRINTS_KDAT", tmp_path / "absent")
    monkeypatch.setattr(sim, "load_signatures", lambda _db: [sig("PR00001", "GLABLOOD")])
    monkeypatch.setattr(
        sim,
        "interpro_entries",
        lambda: pytest.fail("InterPro parsing happened before raw snapshot verification"),
    )
    monkeypatch.setattr(
        sim,
        "write_record",
        lambda *_args, **_kwargs: pytest.fail("write happened before raw snapshot verification"),
    )
    monkeypatch.setattr(sys, "argv", ["seed_interpro_members.py", "--db", "prints"])
    assert sim.main() == 2


def test_prints_main_requires_the_allowlisted_manifest_before_loading_signatures(
    monkeypatch, capsys
):
    import seed_interpro_members as sim

    def reject_unapproved_manifest(_manifest_path, *, expected_manifest_id, **_paths):
        assert expected_manifest_id == sim.EXPECTED_PRINTS_SNAPSHOT_ID
        raise sim.PrintsSnapshotError("different self-consistent manifest is not pinned")

    monkeypatch.setattr(sim, "load_verified_prints_snapshot", reject_unapproved_manifest)
    monkeypatch.setattr(
        sim,
        "load_signatures",
        lambda _db: pytest.fail("PRINTS signatures loaded before manifest allowlist rejection"),
    )
    monkeypatch.setattr(
        sim,
        "interpro_entries",
        lambda: pytest.fail("InterPro source processed before manifest allowlist rejection"),
    )
    monkeypatch.setattr(sys, "argv", ["seed_interpro_members.py", "--db", "prints"])

    assert sim.main() == 2
    assert "different self-consistent manifest is not pinned" in capsys.readouterr().err


def _prints_main_snapshot_fixture(tmp_path, monkeypatch):
    """Install one compact, fully authenticated snapshot for main()-level tests."""
    import prints_snapshot as snapshot
    import seed_interpro_members as sim

    source_dir = tmp_path / "raw"
    source_dir.mkdir()
    api_path = source_dir / "prints.jsonl"
    kdat_path = source_dir / "prints42_0.kdat"
    hierarchy_path = source_dir / snapshot.HIERARCHY_NAME
    xml_path = source_dir / "interpro.xml.gz"
    manifest_path = source_dir / snapshot.MANIFEST_NAME

    source_kdat = _kdat_record(
        "GLABLOOD",
        "PR00001",
        4,
        "Coagulation factor GLA domain signature",
        "Source-native GLA description.",
    ).encode("latin-1")
    api_row = sig("PR00001", "GLABLOOD", "domain", "IPR000001") | {"source_database": "prints"}
    api_path.write_bytes((snapshot.canonical_json(api_row) + "\n").encode("ascii"))
    kdat_path.write_bytes(source_kdat)
    hierarchy_path.write_bytes(
        snapshot.dump_hierarchy_jsonl(
            snapshot.parse_hierarchy_source(b"GLABLOOD|PR00001|1e-04|0|*\n")
        )
    )
    xml_path.write_bytes(
        gzip.compress(
            b"""<?xml version="1.0" encoding="UTF-8"?>
<interprodb>
<release>
  <dbinfo version="42.0" dbname="PRINTS" entry_count="1" file_date="14-JUN-12"/>
  <dbinfo version="109.0" dbname="INTERPRO" entry_count="1" file_date="11-JUN-26"/>
</release>
<interpro id="IPR000001" protein_count="1" short_name="Test" type="Domain">
  <name>Test integrating entry</name>
  <abstract>Captured InterPro abstract.</abstract>
  <member_list>
    <db_xref protein_count="1" db="PRINTS" dbkey="PR00001" name="GLABLOOD"/>
  </member_list>
</interpro>
</interprodb>
""",
            mtime=0,
        )
    )

    source_sha256 = _authenticate_synthetic_prints_fixture(monkeypatch, source_kdat)
    monkeypatch.setattr(snapshot, "PRINTS_42_0_SHA256", source_sha256)
    manifest = snapshot.build_prints_manifest(
        api_path=api_path,
        kdat_path=kdat_path,
        hierarchy_path=hierarchy_path,
        interpro_xml_path=xml_path,
    )
    manifest_path.write_bytes(snapshot.dump_manifest(manifest))

    monkeypatch.setattr(sim, "MEMBERS_DIR", source_dir)
    monkeypatch.setattr(sim, "PRINTS_KDAT", kdat_path)
    monkeypatch.setattr(sim, "PRINTS_HIERARCHY", hierarchy_path)
    monkeypatch.setattr(sim, "PRINTS_MANIFEST", manifest_path)
    monkeypatch.setattr(sim, "INTERPRO", xml_path)
    monkeypatch.setattr(sim, "TRAITS_DIR", tmp_path / "traits")
    monkeypatch.setattr(sim, "PRINTS_42_0_SHA256", source_sha256)
    monkeypatch.setattr(sim, "EXPECTED_PRINTS_SNAPSHOT_ID", manifest["manifest_id"])
    return {
        "api": api_path,
        "kdat": kdat_path,
        "hierarchy": hierarchy_path,
        "xml": xml_path,
    }


@pytest.mark.parametrize("artifact", ["api", "kdat", "hierarchy", "xml"])
def test_prints_main_consumes_manifest_bound_capture_after_same_path_swap(
    tmp_path, monkeypatch, capsys, artifact
):
    """A verified live path may change, but it must never change emitted records."""
    import prints_kdat
    import prints_snapshot as snapshot
    import seed_interpro_members as sim

    paths = _prints_main_snapshot_fixture(tmp_path, monkeypatch)
    target = paths[artifact]
    replacement = b"same path, different unverified bytes\n"
    swapped = False

    if artifact == "kdat":
        original_read = prints_kdat._read_source_bytes

        def read_then_swap(path):
            nonlocal swapped
            raw = original_read(path)
            if pathlib.Path(path) == target and not swapped:
                target.write_bytes(replacement)
                swapped = True
            return raw

        monkeypatch.setattr(prints_kdat, "_read_source_bytes", read_then_swap)
    else:
        original_capture = snapshot._capture_artifact

        def capture_then_swap(path, label):
            nonlocal swapped
            capture = original_capture(path, label)
            if pathlib.Path(path) == target and not swapped:
                target.write_bytes(replacement)
                swapped = True
            return capture

        monkeypatch.setattr(snapshot, "_capture_artifact", capture_then_swap)

    monkeypatch.setattr(
        sys,
        "argv",
        ["seed_interpro_members.py", "--db", "prints", "--limit", "1"],
    )
    assert sim.main() == 0
    output = capsys.readouterr()
    assert swapped is True
    assert target.read_bytes() == replacement
    assert "identifier: PRINTS:PR00001" in output.out
    assert "Source-native GLA description." in output.out
    assert "prints-snapshot:" in output.err


def test_prints_apply_refuses_before_loading_sources_or_writing(monkeypatch, capsys):
    import seed_interpro_members as sim

    monkeypatch.setenv("PTM_RESEED_REFRESH_DEFINITIONS", "1")
    monkeypatch.setattr(
        sim,
        "load_signatures",
        lambda _db: pytest.fail("PRINTS --apply loaded sources before refusing"),
    )
    monkeypatch.setattr(
        sim,
        "write_record",
        lambda *_args, **_kwargs: pytest.fail("PRINTS --apply wrote a record"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["seed_interpro_members.py", "--db", "prints", "--apply", "--force"],
    )
    assert sim.main() == 2
    error = capsys.readouterr().err
    assert "dedicated validated source-model migration" in error
    assert "--force" in error
    assert "PTM_RESEED_REFRESH_DEFINITIONS" in error


@pytest.mark.parametrize("extra_args", [[], ["--apply", "--force"]])
def test_sfld_seeding_refuses_before_loading_sources_or_writing(monkeypatch, capsys, extra_args):
    import seed_interpro_members as sim

    monkeypatch.setattr(
        sim,
        "load_signatures",
        lambda _db: pytest.fail("SFLD --apply loaded sources before refusing"),
    )
    monkeypatch.setattr(
        sim,
        "write_record",
        lambda *_args, **_kwargs: pytest.fail("SFLD --apply wrote a record"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["seed_interpro_members.py", "--db", "sfld", *extra_args],
    )

    assert sim.main() == 2
    error = capsys.readouterr().err
    assert "pinned hierarchy/profile/site source model" in error
    assert "before even dry-run output" in error


# --- HAMAP variant rules (#162 review) ----------------------------------------------


@pytest.mark.parametrize("acc", ["MF_00001", "MF_00036_A", "MF_00036_B"])
def test_hamap_variant_rules_are_not_excluded(acc):
    """THE SHIPPED BUG, caught by the seeder's own skip counter. The pattern was
    `^MF_\\d+$`, which silently excluded 102 accessions of the form MF_00036_A /
    MF_00036_B -- HAMAP's variant rules, 51 pairs.

    They are not duplicates of something already seeded: NONE of the 102 has a
    base rule in the release. `MF_00036` does not exist; only _A and _B do. So
    the pattern dropped 102 families outright, and a silent `continue` would have
    hidden it. The counter is what surfaced it.
    """
    assert MEMBER_DBS["hamap"][2].match(acc), acc


def test_the_hamap_pattern_still_rejects_a_foreign_accession():
    for acc in ("PR00001", "SFLDF00001", "MF_", "MF_00036_"):
        assert not MEMBER_DBS["hamap"][2].match(acc), acc
