"""Focused tests for checksum-pinned source-aware record-content gates."""

from __future__ import annotations

import gzip
import hashlib
import importlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
gate_module = importlib.import_module("uniprot_record_content_gate")


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def source_config(tmp_path):
    long_abstract = " ".join(f"word{index}" for index in range(500))
    xml = tmp_path / "interpro.xml.gz"
    xml_text = f"""\
<interprodb>
  <interpro id="IPR000001" type="Family" short_name="Full_family">
    <name>Full family</name><abstract><p>{long_abstract}</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00001" name="Full_family"/></member_list>
  </interpro>
  <interpro id="IPR000002" type="Domain" short_name="STR4_C">
    <name>STR4 C-terminal domain</name><abstract><p>Complete positional definition.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00002" name="STR4_N"/></member_list>
  </interpro>
  <interpro id="IPR000003" type="Domain" short_name="T2SSM_N">
    <name>T2SSM N-terminal domain</name><abstract><p>Complete scope definition.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00003" name="T2SSM_N"/></member_list>
  </interpro>
  <interpro id="IPR000004" type="Domain" short_name="REP_N">
    <name>REP N-terminal domain</name><abstract><p>Complete local definition.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00004" name="REP_N"/></member_list>
  </interpro>
  <interpro id="IPR000005" type="Domain" short_name="RIPR_EGF-like_9th">
    <name>RIPR, EGF-like 9th domain</name><abstract><p>The ninth domain.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00005" name="RIPR_EGF-like_10th"/></member_list>
  </interpro>
  <interpro id="IPR000006" type="Domain" short_name="PAIR_EGF-like_2nd">
    <name>PAIR EGF-like second domain</name><abstract><p>The second domain.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00006" name="PAIR_EGF-like_2nd"/></member_list>
  </interpro>
  <interpro id="IPR000007" type="Family" short_name="ARTD/PARP">
    <name>ADP-ribosyltransferase diphtheria toxin-like</name>
    <abstract><p>ARTD/PARP fixture family.</p></abstract>
    <member_list><db_xref db="PANTHER" dbkey="PTHR10459" name="ARTD/PARP"/></member_list>
  </interpro>
  <interpro id="IPR000008" type="Family" short_name="ARTD/PARP">
    <name>ADP-ribosyltransferase family</name>
    <abstract><p>ARTD/PARP fixture family.</p></abstract>
    <member_list><db_xref db="PANTHER" dbkey="PTHR10460" name="ARTD/PARP"/></member_list>
  </interpro>
  <interpro id="IPR000009" type="Family" short_name="DNA_ligase">
    <name>DNA ligase family</name>
    <abstract><p>DNA ligase fixture family.</p></abstract>
    <member_list><db_xref db="PANTHER" dbkey="PTHR10461" name="DNA ligase"/></member_list>
  </interpro>
  <interpro id="IPR000010" type="Domain" short_name="Malformed_terminal">
    <name>Malformed terminal domain</name>
    <abstract><p>Citation-stripped terminal artifact (.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00007" name="Malformed_terminal"/></member_list>
  </interpro>
  <interpro id="IPR000011" type="Family" short_name="Malformed_inline">
    <name>Malformed inline family</name>
    <abstract><p>Citation-stripped inline artifact [,. Members continue.</p></abstract>
  </interpro>
  <interpro id="IPR000012" type="Family" short_name="Inline_parenthesis">
    <name>Inline parenthesis family</name>
    <abstract><p>Literal-like inline (. continuation remains prose.</p></abstract>
  </interpro>
  <interpro id="IPR000013" type="Domain" short_name="Missing_noun">
    <name>Missing noun domain</name>
    <abstract><p>This entry represents a of approximately 85 residues.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00008" name="Missing_noun"/></member_list>
  </interpro>
  <interpro id="IPR000014" type="Family" short_name="Polysacc_deacetylase_ArnD">
    <name>Polysaccharide deacetylase, ArnD subfamily</name>
    <abstract><p>Polysaccharide deacetylase fixture family.</p></abstract>
    <member_list><db_xref db="PANTHER" dbkey="PTHR10587" name="Polysacc_deacetylase_ArnD"/></member_list>
  </interpro>
  <interpro id="IPR031140" type="Family" short_name="IDD1-16">
    <name>Protein indeterminate-domain 1-16</name>
    <abstract><p>This is a family of plant-specific transcription factors including protein indeterminate-domain 1-16 with the conserved INDETERMINATE DOMAIN (IDD) and four zinc finger motifs.</p></abstract>
    <member_list><db_xref db="PANTHER" dbkey="PTHR10593" name=""/></member_list>
  </interpro>
  <interpro id="IPR004544" type="Family" short_name="TF_aIF-2_arc">
    <name>Translation initiation factor aIF-2, archaea</name>
    <abstract><p>This entry represents the Probable translation initiation factor IF-2 mostly found in archaea (aIF-2). In archaea, aIF-2, and aIF-5B are separate factors. aIF-2 promotes the GTP-dependent binding of the initiator tRNA. This GTPase is a is a heterotrimer formed by three subunits.</p></abstract>
    <member_list><db_xref db="HAMAP" dbkey="MF_00100_A" name="IF_2_A"/></member_list>
  </interpro>
  <interpro id="IPR000016" type="Family" short_name="TIF_IF2">
    <name>Translation initiation factor IF-2</name>
    <abstract><p>This entry represents the monomeric bacterial translation initiation factor IF-2.</p></abstract>
    <member_list><db_xref db="HAMAP" dbkey="MF_00100_B" name="IF_2_B"/></member_list>
  </interpro>
  <interpro id="IPR000017" type="Domain" short_name="Repeated_word">
    <name>Repeated-word domain</name>
    <abstract><p>This is a domain found found at the C-terminal of a fixture protein.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00009" name="Repeated_word"/></member_list>
  </interpro>
  <interpro id="IPR000018" type="Domain" short_name="Broken_word">
    <name>Broken-word domain</name>
    <abstract><p>The subunits form a methyltrans- ferase with fixed stoichiometry.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00010" name="Broken_word"/></member_list>
  </interpro>
  <interpro id="IPR000019" type="Domain" short_name="Fixture_C">
    <name>Fixture C-terminal domain</name>
    <abstract><p>This entry represents the C-terminal region of a fixture protein. Background sentence. This N-terminal region mediates an unrelated interaction.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00011" name="Fixture_C"/></member_list>
  </interpro>
  <interpro id="IPR000020" type="Domain" short_name="Context_C">
    <name>Context C-terminal domain</name>
    <abstract><p>This entry represents the C-terminal region of a fixture protein. It interacts with the protein's N-terminal region.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00012" name="Context_C"/></member_list>
  </interpro>
  <interpro id="IPR000021" type="Domain" short_name="Broken_complex">
    <name>Broken-complex domain</name>
    <abstract><p>The protein forms RTT101(MMS1- MMS22) and related complexes.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00013" name="Broken_complex"/></member_list>
  </interpro>
  <interpro id="IPR000022" type="Domain" short_name="Broken_cofactor">
    <name>Broken-cofactor domain</name>
    <abstract><p>The enzyme uses S- adenosyl-L-methionine as a methyl donor.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00014" name="Broken_cofactor"/></member_list>
  </interpro>
  <interpro id="IPR000023" type="Domain" short_name="Broken_association">
    <name>Broken-association domain</name>
    <abstract><p>The protein forms a membrane- associated complex.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00015" name="Broken_association"/></member_list>
  </interpro>
  <interpro id="IPR000024" type="Domain" short_name="Coordinated_hyphen">
    <name>Coordinated-hyphen domain</name>
    <abstract><p>The proteins form homo- and heterodimers.</p></abstract>
    <member_list><db_xref db="PFAM" dbkey="PF00016" name="Coordinated_hyphen"/></member_list>
  </interpro>
</interprodb>
"""
    with gzip.open(xml, "wt", encoding="utf-8") as handle:
        handle.write(xml_text)

    clans = tmp_path / "Pfam-A.clans.tsv.gz"
    with gzip.open(clans, "wt", encoding="utf-8") as handle:
        handle.write("PF00001\tCL0001\tFixture\tFull_family\tFull family\n")
        handle.write("PF00002\tCL0001\tFixture\tSTR4_N\tSTR4 N-terminal domain\n")
        handle.write("PF00003\tCL0001\tFixture\tT2SSM_N\tT2SSM family\n")
        handle.write("PF00004\tCL0001\tFixture\tREP_N\tREP N-terminal domain\n")
        handle.write("PF00005\tCL0001\tFixture\tRIPR_EGF-like_10th\tRIPR EGF-like 10th domain\n")
        handle.write("PF00006\tCL0001\tFixture\tPAIR_EGF-like_2nd\tPAIR EGF-like second domain\n")
        handle.write("PF00007\tCL0001\tFixture\tMalformed_terminal\tMalformed terminal domain\n")
        handle.write("PF00008\tCL0001\tFixture\tMissing_noun\tMissing noun domain\n")
        handle.write("PF00009\tCL0001\tFixture\tRepeated_word\tRepeated-word domain\n")
        handle.write("PF00010\tCL0001\tFixture\tBroken_word\tBroken-word domain\n")
        handle.write("PF00011\tCL0001\tFixture\tFixture_C\tFixture C-terminal domain\n")
        handle.write("PF00012\tCL0001\tFixture\tContext_C\tContext C-terminal domain\n")
        handle.write("PF00013\tCL0001\tFixture\tBroken_complex\tBroken-complex domain\n")
        handle.write("PF00014\tCL0001\tFixture\tBroken_cofactor\tBroken-cofactor domain\n")
        handle.write("PF00015\tCL0001\tFixture\tBroken_association\tBroken-association domain\n")
        handle.write("PF00016\tCL0001\tFixture\tCoordinated_hyphen\tCoordinated-hyphen domain\n")
    types = tmp_path / "pfam_types.tsv"
    types.write_text(
        "PF00001\tFamily\nPF00002\tDomain\nPF00003\tFamily\nPF00004\tDomain\n"
        "PF00005\tDomain\nPF00006\tDomain\nPF00007\tDomain\nPF00008\tDomain\n"
        "PF00009\tDomain\nPF00010\tDomain\nPF00011\tDomain\nPF00012\tDomain\n"
        "PF00013\tDomain\nPF00014\tDomain\nPF00015\tDomain\nPF00016\tDomain\n",
        encoding="utf-8",
    )
    panther = tmp_path / "PANTHER19.0_HMM_classifications"
    panther.write_text(
        "PTHR10036\tFixture family\n"
        "PTHR10098\tRAPSYN-RELATED\n"
        "PTHR10185\tPHOSPHOLIPASE D - RELATED\n"
        "PTHR10459\tDNA LIGASE\n"
        "PTHR10459:SF1\tPOLY [ADP-RIBOSE] POLYMERASE 1\n"
        "PTHR10459:SF2\tPROTEIN ADP-RIBOSYLTRANSFERASE PARP3\n"
        "PTHR10460\tDNA LIGASE\n"
        "PTHR10460:SF1\tPOLY [ADP-RIBOSE] POLYMERASE 1\n"
        "PTHR10460:SF2\tUNCHARACTERIZED PROTEIN\n"
        "PTHR10461\tDNA LIGASE\n"
        "PTHR10461:SF1\tPOLY [ADP-RIBOSE] POLYMERASE 1\n"
        "PTHR10587\tGLYCOSYL TRANSFERASE-RELATED\n"
        "PTHR10587:SF1\tCHITIN DEACETYLASE\n"
        "PTHR10587:SF2\tCHITOOLIGOSACCHARIDE DEACETYLASE\n"
        "PTHR10587:SF3\t4-DEOXY-4-FORMAMIDO-L-ARABINOSE-PHOSPHOUNDECAPRENOL DEFORMYLASE ARND-RELATED\n"
        "PTHR10587:SF4\tSECRETED PROTEIN\n"
        "PTHR10593\tSERINE/THREONINE-PROTEIN KINASE RIO\n"
        "PTHR10593:SF1\tPROTEIN SHOOT GRAVITROPISM 5\n"
        "PTHR10593:SF2\tZINC FINGER PROTEIN MAGPIE\n"
        "PTHR10593:SF3\tPROTEIN INDETERMINATE-DOMAIN 14\n",
        encoding="utf-8",
    )
    return (
        gate_module.SourceConfig(
            interpro_xml=xml,
            interpro_xml_sha256=_sha256(xml),
            pfam_clans=clans,
            pfam_clans_sha256=_sha256(clans),
            pfam_types=types,
            pfam_types_sha256=_sha256(types),
            panther_classifications=panther,
            panther_classifications_sha256=_sha256(panther),
        ),
        long_abstract,
    )


def _mapped_record(pfam_accession: str, interpro_accession: str, *, definition: str) -> dict:
    return {
        "identifier": f"Pfam:{pfam_accession}",
        "label": f"Fixture {pfam_accession}",
        "definition": definition,
        "definition_source": f"InterPro:{interpro_accession} abstract (seed_pfam.py)",
        "mapped_xrefs": [
            {
                "predicate": "skos:closeMatch",
                "object": f"InterPro:{interpro_accession}",
                "mapping_source": "pfam2interpro",
            }
        ],
    }


def _mapped_panther_record(
    panther_accession: str,
    interpro_accession: str,
    *,
    label: str = "DNA LIGASE",
) -> dict:
    definition = (
        f"{label} — a full-length protein family modelled by the PANTHER 19.0 "
        f"profile HMM {panther_accession}. PANTHER protein class: fixture enzyme."
    )
    return {
        "identifier": f"PANTHER:{panther_accession}",
        "label": label,
        "definition": definition,
        "definition_source": "PANTHER 19.0 composed seeder output",
        "definitions": [{"text": definition, "method": "GENERATED"}],
        "mapped_xrefs": [
            {
                "predicate": "skos:closeMatch",
                "object": f"InterPro:{interpro_accession}",
                "mapping_source": "interpro-member-list",
            }
        ],
    }


def _mapped_hamap_if2_record(
    hamap_accession: str,
    interpro_accession: str,
    *,
    definition: str,
) -> dict:
    return {
        "identifier": f"HAMAP:{hamap_accession}",
        "label": "Translation initiation factor IF-2 [infB]",
        "definition": definition,
        "definition_source": f"InterPro:{interpro_accession} abstract (fixture)",
        "mapped_xrefs": [
            {
                "predicate": "skos:closeMatch",
                "object": f"InterPro:{interpro_accession}",
                "mapping_source": "interpro-member-list",
            }
        ],
    }


def test_hard_rules_and_conservative_negative_controls(source_config):
    config, long_abstract = source_config
    truncated = {
        "identifier": "InterPro:IPR000001",
        "label": "Full family",
        "definition": long_abstract[:1799].rstrip() + "…",
        "definition_source": "InterPro:IPR000001 abstract (seed_interpro.py)",
    }
    panther_template = {
        "identifier": "PANTHER:PTHR10036",
        "label": "Fixture family",
        "definition": (
            "Fixture family — a full-length protein family modelled by the PANTHER "
            "19.0 profile HMM PTHR10036."
        ),
        "definition_source": "PANTHER 19.0 profile HMM PTHR10036",
        "definitions": [
            {
                "text": (
                    "Fixture family — a full-length protein family modelled by the "
                    "PANTHER 19.0 profile HMM PTHR10036."
                ),
                "method": "GENERATED",
            }
        ],
    }
    redundant_class_panther = {
        "identifier": "PANTHER:PTHR10185",
        "label": "PHOSPHOLIPASE D - RELATED",
        "definition": (
            "PHOSPHOLIPASE D - RELATED — a full-length protein family modelled by "
            "the PANTHER 19.0 profile HMM PTHR10185. PANTHER protein class: "
            "phospholipase."
        ),
        "definition_source": "PANTHER 19.0 composed seeder output",
        "definitions": [
            {
                "text": (
                    "PHOSPHOLIPASE D - RELATED — a full-length protein family modelled "
                    "by the PANTHER 19.0 profile HMM PTHR10185. PANTHER protein class: "
                    "phospholipase."
                ),
                "method": "GENERATED",
            }
        ],
    }
    unresolved_placeholder = {
        "identifier": "HAMAP:MF_00026",
        "label": "DNA-binding protein <locus_tag>",
        "definition": "A substantive family definition.",
        "definition_source": "Fixture",
    }
    pfam_template = {
        "identifier": "Pfam:PF00001",
        "label": "Full family",
        "definition": "Full family. Pfam family family Full_family (Pfam:PF00001).",
        "definition_source": "Pfam",
    }
    positional_conflict = _mapped_record(
        "PF00002", "IPR000002", definition="Complete positional definition."
    )
    scope_conflict = _mapped_record("PF00003", "IPR000003", definition="Complete scope definition.")
    consistent_local = _mapped_record(
        "PF00004", "IPR000004", definition="Complete local definition."
    )
    ordinal_conflict = _mapped_record("PF00005", "IPR000005", definition="The ninth domain.")
    consistent_ordinal = _mapped_record("PF00006", "IPR000006", definition="The second domain.")
    substantive_panther = {
        **panther_template,
        "definition": "A curated catalytic family with a PANTHER profile.",
        "definitions": [
            {"text": "A curated catalytic family with a PANTHER profile.", "method": "GENERATED"}
        ],
    }
    informative_class_panther = {
        **redundant_class_panther,
        "label": "Fixture family",
        "definition": (
            "Fixture family — a full-length protein family modelled by the PANTHER "
            "19.0 profile HMM PTHR10185. PANTHER protein class: phospholipase."
        ),
        "definitions": [
            {
                "text": (
                    "Fixture family — a full-length protein family modelled by the "
                    "PANTHER 19.0 profile HMM PTHR10185. PANTHER protein class: "
                    "phospholipase."
                ),
                "method": "GENERATED",
            }
        ],
    }
    go_bearing_panther = {
        **redundant_class_panther,
        "definition": redundant_class_panther["definition"]
        + " Members are annotated with the molecular function lipase activity.",
        "definitions": [
            {
                "text": redundant_class_panther["definition"]
                + " Members are annotated with the molecular function lipase activity.",
                "method": "GENERATED",
            }
        ],
    }
    full_interpro = {
        **truncated,
        "definition": long_abstract,
    }
    records = [
        truncated,
        panther_template,
        redundant_class_panther,
        unresolved_placeholder,
        pfam_template,
        positional_conflict,
        scope_conflict,
        consistent_local,
        ordinal_conflict,
        consistent_ordinal,
        substantive_panther,
        informative_class_panther,
        go_bearing_panther,
        full_interpro,
    ]
    gate = gate_module.RecordContentGate(records, config)

    assert [finding.code for finding in gate.evaluate(truncated)] == ["SOURCE_DEFINITION_TRUNCATED"]
    assert [finding.code for finding in gate.evaluate(panther_template)] == [
        "DEFINITION_TEMPLATE_ONLY"
    ]
    assert [finding.code for finding in gate.evaluate(redundant_class_panther)] == [
        "DEFINITION_TEMPLATE_ONLY"
    ]
    assert [finding.code for finding in gate.evaluate(unresolved_placeholder)] == [
        "UNRESOLVED_SOURCE_PLACEHOLDER"
    ]
    assert [finding.code for finding in gate.evaluate(pfam_template)] == [
        "DEFINITION_TEMPLATE_ONLY"
    ]
    assert [finding.code for finding in gate.evaluate(positional_conflict)] == [
        "SOURCE_POSITIONAL_IDENTITY_CONFLICT"
    ]
    assert [finding.code for finding in gate.evaluate(scope_conflict)] == ["SOURCE_SCOPE_CONFLICT"]
    assert gate.evaluate(consistent_local) == []
    assert [finding.code for finding in gate.evaluate(ordinal_conflict)] == [
        "SOURCE_POSITIONAL_IDENTITY_CONFLICT"
    ]
    assert gate.evaluate(consistent_ordinal) == []
    assert gate.evaluate(substantive_panther) == []
    assert gate.evaluate(informative_class_panther) == []
    assert gate.evaluate(go_bearing_panther) == []
    assert gate.evaluate(full_interpro) == []
    assert gate_module.hard_reasons(gate.evaluate(positional_conflict)) == [
        "unqualifiable:record_content:source_positional_identity_conflict"
    ]


def test_low_information_source_definition_is_review_only():
    record = {
        "identifier": "Pfam:PF29189",
        "label": "FliF N-terminal domain",
        "definition": ("This entry represents a small N-terminal domain found in FliF proteins."),
        "definition_source": "Fixture",
    }
    findings = gate_module.RecordContentGate([record]).evaluate(record)

    assert [(finding.code, finding.severity) for finding in findings] == [
        ("LOW_INFORMATION_SOURCE_DEFINITION", "REVIEW")
    ]
    assert gate_module.hard_reasons(findings) == []


def test_only_substantively_incomplete_interpro_artifacts_are_hard(
    source_config,
):
    config, _ = source_config
    terminal_definition = "Citation-stripped terminal artifact (."
    terminal_direct = {
        "identifier": "InterPro:IPR000010",
        "label": "Malformed terminal domain",
        "definition": terminal_definition,
        "definition_source": "InterPro",
    }
    terminal_mapped = _mapped_record("PF00007", "IPR000010", definition=terminal_definition)
    inline_direct = {
        "identifier": "InterPro:IPR000011",
        "label": "Malformed inline family",
        "definition": "Citation-stripped inline artifact [,. Members continue.",
        "definition_source": "InterPro",
    }
    missing_noun_definition = "This entry represents a of approximately 85 residues."
    missing_noun_direct = {
        "identifier": "InterPro:IPR000013",
        "label": "Missing noun domain",
        "definition": missing_noun_definition,
        "definition_source": "InterPro",
    }
    missing_noun_mapped = _mapped_record("PF00008", "IPR000013", definition=missing_noun_definition)
    repeated_word_definition = (
        "This is a domain found found at the C-terminal of a fixture protein."
    )
    repeated_word_mapped = _mapped_record(
        "PF00009", "IPR000017", definition=repeated_word_definition
    )
    broken_word_definition = "The subunits form a methyltrans- ferase with fixed stoichiometry."
    broken_word_mapped = _mapped_record("PF00010", "IPR000018", definition=broken_word_definition)
    broken_complex_definition = "The protein forms RTT101(MMS1- MMS22) and related complexes."
    broken_complex_mapped = _mapped_record(
        "PF00013", "IPR000021", definition=broken_complex_definition
    )
    broken_cofactor_definition = "The enzyme uses S- adenosyl-L-methionine as a methyl donor."
    broken_cofactor_mapped = _mapped_record(
        "PF00014", "IPR000022", definition=broken_cofactor_definition
    )
    broken_association_definition = "The protein forms a membrane- associated complex."
    broken_association_mapped = _mapped_record(
        "PF00015", "IPR000023", definition=broken_association_definition
    )
    coordinated_hyphen_definition = "The proteins form homo- and heterodimers."
    coordinated_hyphen = _mapped_record(
        "PF00016", "IPR000024", definition=coordinated_hyphen_definition
    )
    corrected_missing_noun = {
        **missing_noun_direct,
        "definition": "This entry represents a domain of approximately 85 residues.",
    }
    corrected_local_definition = {
        **terminal_direct,
        "definition": "Citation-stripped terminal artifact (fixture).",
    }
    nonterminal_parenthesis = {
        "identifier": "InterPro:IPR000012",
        "label": "Inline parenthesis family",
        "definition": "Literal-like inline (. continuation remains prose.",
        "definition_source": "InterPro",
    }
    unsourced_local_artifact = {
        "identifier": "HAMAP:MF_FIXTURE",
        "label": "Fixture family",
        "definition": (
            "Locally authored prose [,. says is a is a, found found, and "
            "methyltrans- ferase; RTT101(MMS1- MMS22), S- adenosyl-L-methionine, and "
            "membrane- associated complex have no InterPro source replay."
        ),
        "definition_source": "Fixture",
    }
    gate = gate_module.RecordContentGate(
        [
            terminal_direct,
            terminal_mapped,
            inline_direct,
            missing_noun_direct,
            missing_noun_mapped,
            repeated_word_mapped,
            broken_word_mapped,
            broken_complex_mapped,
            broken_cofactor_mapped,
            broken_association_mapped,
            coordinated_hyphen,
            corrected_missing_noun,
            corrected_local_definition,
            nonterminal_parenthesis,
            unsourced_local_artifact,
        ],
        config,
    )

    for record, artifact, entry_id in (
        (terminal_direct, "(.", "InterPro:IPR000010"),
        (terminal_mapped, "(.", "InterPro:IPR000010"),
        (inline_direct, "[,.", "InterPro:IPR000011"),
        (missing_noun_direct, "represents a of", "InterPro:IPR000013"),
        (missing_noun_mapped, "represents a of", "InterPro:IPR000013"),
    ):
        findings = gate.evaluate(record)
        assert [(finding.code, finding.severity) for finding in findings] == [
            ("SOURCE_DEFINITION_MALFORMED", "HARD")
        ]
        assert f"artifact {artifact!r}" in findings[0].detail
        assert findings[0].source_bindings[0]["kind"] == "INTERPRO_XML"
        assert findings[0].source_bindings[0]["entry_id"] == entry_id
        assert findings[0].source_bindings[0]["entry_sha256"]
        assert gate_module.hard_reasons(findings) == [
            "unqualifiable:record_content:source_definition_malformed"
        ]

    assert gate.evaluate(corrected_local_definition) == []
    assert gate.evaluate(corrected_missing_noun) == []
    assert gate.evaluate(nonterminal_parenthesis) == []
    assert gate.evaluate(unsourced_local_artifact) == []
    assert gate.evaluate(coordinated_hyphen) == []
    for typography_only in (
        repeated_word_mapped,
        broken_word_mapped,
        broken_complex_mapped,
        broken_cofactor_mapped,
        broken_association_mapped,
    ):
        assert gate.evaluate(typography_only) == []


def test_panther_unanimous_child_and_interpro_identity_conflict_is_hard(source_config):
    config, _ = source_config
    record = _mapped_panther_record("PTHR10459", "IPR000007")

    finding = gate_module.RecordContentGate([record], config).evaluate(record)[0]

    assert finding.code == "SOURCE_FAMILY_IDENTITY_CONFLICT"
    assert finding.severity == "HARD"
    assert "all 2 informative PANTHER 19.0 child names" in finding.detail
    assert [binding["kind"] for binding in finding.source_bindings] == [
        "PANTHER_HMM_CLASSIFICATIONS",
        "INTERPRO_XML",
    ]
    assert all(binding["entry_sha256"] for binding in finding.source_bindings)
    assert gate_module.hard_reasons([finding]) == [
        "unqualifiable:record_content:source_family_identity_conflict"
    ]


def test_panther_informative_children_can_outvote_one_exact_generic_child(source_config):
    config, _ = source_config
    record = _mapped_panther_record("PTHR10587", "IPR000014", label="GLYCOSYL TRANSFERASE-RELATED")

    findings = gate_module.RecordContentGate([record], config).evaluate(record)

    assert [(finding.code, finding.severity) for finding in findings] == [
        ("SOURCE_FAMILY_IDENTITY_CONFLICT", "HARD")
    ]
    assert "all 3 informative PANTHER 19.0 child names (of 4; 1 exact generic ignored)" in (
        findings[0].detail
    )
    assert "CARBOHYDRATE_DEACYLASE" in findings[0].detail
    assert [binding["entry_id"] for binding in findings[0].source_bindings] == [
        "PANTHER:PTHR10587",
        "InterPro:IPR000014",
    ]


def test_exact_panther_rio_root_vs_idd_source_hierarchy_conflict_is_hard(source_config):
    config, _ = source_config
    definition = (
        "This is a family of plant-specific transcription factors including protein "
        "indeterminate-domain 1-16 with the conserved INDETERMINATE DOMAIN (IDD) and "
        "four zinc finger motifs."
    )
    conflict = {
        "identifier": "PANTHER:PTHR10593",
        "label": "SERINE/THREONINE-PROTEIN KINASE RIO",
        "definition": definition,
        "definition_source": "InterPro:IPR031140 abstract (fixture)",
        "mapped_xrefs": [
            {
                "object": "InterPro:IPR031140",
                "mapping_source": "interpro-member-list",
            }
        ],
    }
    corrected = {
        **conflict,
        "label": "Protein indeterminate-domain 1-16",
    }

    gate = gate_module.RecordContentGate([conflict, corrected], config)
    findings = gate.evaluate(conflict)

    assert [(finding.code, finding.severity) for finding in findings] == [
        ("SOURCE_FAMILY_IDENTITY_CONFLICT", "HARD")
    ]
    assert "RIO kinase" in findings[0].detail
    assert "plant IDD/C2H2 transcription-factor family" in findings[0].detail
    assert [binding["entry_id"] for binding in findings[0].source_bindings] == [
        "PANTHER:PTHR10593",
        "InterPro:IPR031140",
    ]
    assert all(binding["entry_sha256"] for binding in findings[0].source_bindings)
    assert gate_module.hard_reasons(findings) == [
        "unqualifiable:record_content:source_family_identity_conflict"
    ]
    assert gate.evaluate(corrected) == []


def test_panther_identity_rule_requires_unanimity_and_interpro_corroboration(source_config):
    config, _ = source_config
    consistent = _mapped_panther_record(
        "PTHR10459", "IPR000007", label="ADP-ribosyltransferase PARP"
    )
    unknown_child = _mapped_panther_record("PTHR10460", "IPR000008")
    interpro_disagrees = _mapped_panther_record("PTHR10461", "IPR000009")

    gate = gate_module.RecordContentGate([consistent, unknown_child, interpro_disagrees], config)

    assert gate.evaluate(consistent) == []
    assert gate.evaluate(unknown_child) == []
    assert gate.evaluate(interpro_disagrees) == []


def test_exact_hamap_interpro_if2_identity_conflict_is_hard(source_config):
    config, _ = source_config
    bad_definition = (
        "This entry represents the Probable translation initiation factor IF-2 mostly found "
        "in archaea (aIF-2). In archaea, aIF-2, and aIF-5B are separate factors. aIF-2 "
        "promotes the GTP-dependent binding of the initiator tRNA. This GTPase is a is a "
        "heterotrimer formed by three subunits."
    )
    conflict = _mapped_hamap_if2_record("MF_00100_A", "IPR004544", definition=bad_definition)
    corrected = {**conflict, "definition": "Correct monomeric IF-2 family definition."}
    sibling = _mapped_hamap_if2_record(
        "MF_00100_B",
        "IPR000016",
        definition="This entry represents the monomeric bacterial translation initiation factor IF-2.",
    )

    gate = gate_module.RecordContentGate([conflict, corrected, sibling], config)
    findings = gate.evaluate(conflict)

    assert [(finding.code, finding.severity) for finding in findings] == [
        ("SOURCE_FAMILY_IDENTITY_CONFLICT", "HARD")
    ]
    assert "monomeric translation initiation factor IF-2/infB" in findings[0].detail
    assert [binding["entry_id"] for binding in findings[0].source_bindings] == [
        "InterPro:IPR004544"
    ]
    assert findings[0].source_bindings[0]["entry_sha256"] == gate_module._value_sha256(
        gate.interpro_entries["IPR004544"].hamap_projection()
    )
    assert gate_module.hard_reasons(findings) == [
        "unqualifiable:record_content:source_family_identity_conflict"
    ]
    assert gate.evaluate(corrected) == []
    assert gate.evaluate(sibling) == []


def test_exact_interpro_deictic_opposite_terminal_conflict_is_hard(source_config):
    config, _ = source_config
    conflict_definition = (
        "This entry represents the C-terminal region of a fixture protein. Background "
        "sentence. This N-terminal region mediates an unrelated interaction."
    )
    direct = {
        "identifier": "InterPro:IPR000019",
        "label": "Fixture C-terminal domain",
        "definition": conflict_definition,
        "definition_source": "InterPro",
    }
    mapped = _mapped_record("PF00011", "IPR000019", definition=conflict_definition)
    corrected = {
        **direct,
        "definition": "This entry represents the C-terminal region of a fixture protein.",
    }
    contextual_definition = (
        "This entry represents the C-terminal region of a fixture protein. It interacts "
        "with the protein's N-terminal region."
    )
    contextual = _mapped_record("PF00012", "IPR000020", definition=contextual_definition)
    gate = gate_module.RecordContentGate([direct, mapped, corrected, contextual], config)

    for record in (direct, mapped):
        findings = gate.evaluate(record)
        assert [(finding.code, finding.severity) for finding in findings] == [
            ("SOURCE_POSITIONAL_IDENTITY_CONFLICT", "HARD")
        ]
        assert "title and opening sentence identify a C-terminal trait" in findings[0].detail
        assert "This N-terminal region" in findings[0].detail
        assert findings[0].source_bindings[0]["entry_id"] == "InterPro:IPR000019"

    assert gate.evaluate(corrected) == []
    assert gate.evaluate(contextual) == []


def test_low_whole_protein_family_coverage_is_candidate_review_only(source_config):
    config, _ = source_config
    record = _mapped_panther_record("PTHR10098", "IPR000007", label="RAPSYN-RELATED")
    # This record has no integrating InterPro mapping in production. Keep this
    # fixture focused on coverage and avoid requesting irrelevant membership.
    record.pop("mapped_xrefs")
    candidate = {
        "trait_id": "PANTHER:PTHR10098",
        "source_trait_id": "PANTHER:PTHR10098",
        "mapping_method": "INTERPRO_MATCH",
        "scope": "WHOLE_PROTEIN",
        "sequence_length": 2481,
        "intervals": [{"start": 224, "end": 723}],
    }
    gate = gate_module.RecordContentGate([record], config)

    findings = gate.evaluate_candidate(record, candidate)

    assert [(finding.code, finding.severity) for finding in findings] == [
        ("LOW_WHOLE_PROTEIN_FAMILY_COVERAGE", "REVIEW")
    ]
    assert "500/2481 residues (20.2%)" in findings[0].detail
    assert findings[0].source_bindings[0]["kind"] == "PANTHER_HMM_CLASSIFICATIONS"
    assert gate_module.hard_reasons(findings) == []

    exactly_quarter = {
        **candidate,
        "sequence_length": 400,
        "intervals": [{"start": 1, "end": 50}, {"start": 51, "end": 100}],
    }
    assert gate.evaluate_candidate(record, exactly_quarter) == []
    assert gate.evaluate_candidate(record, {**candidate, "scope": "LOCALIZED"}) == []
    assert (
        gate.evaluate_candidate(record, {**candidate, "mapping_method": "SOURCE_MEMBERSHIP"}) == []
    )


def test_requested_source_replay_fails_closed_on_hash_mismatch(source_config):
    config, long_abstract = source_config
    record = {
        "identifier": "InterPro:IPR000001",
        "definition": long_abstract,
        "definition_source": "InterPro:IPR000001 abstract (seed_interpro.py)",
    }
    changed = gate_module.SourceConfig(
        interpro_xml=config.interpro_xml,
        interpro_xml_sha256="0" * 64,
        pfam_clans=config.pfam_clans,
        pfam_clans_sha256=config.pfam_clans_sha256,
        pfam_types=config.pfam_types,
        pfam_types_sha256=config.pfam_types_sha256,
    )

    with pytest.raises(gate_module.ContentGateError, match="source SHA-256 mismatch"):
        gate_module.RecordContentGate([record], changed)


def test_requested_panther_replay_fails_closed_on_hash_mismatch(source_config):
    config, _ = source_config
    record = _mapped_panther_record("PTHR10459", "IPR000007")
    changed = gate_module.SourceConfig(
        interpro_xml=config.interpro_xml,
        interpro_xml_sha256=config.interpro_xml_sha256,
        pfam_clans=config.pfam_clans,
        pfam_clans_sha256=config.pfam_clans_sha256,
        pfam_types=config.pfam_types,
        pfam_types_sha256=config.pfam_types_sha256,
        panther_classifications=config.panther_classifications,
        panther_classifications_sha256="0" * 64,
    )

    with pytest.raises(gate_module.ContentGateError, match="source SHA-256 mismatch"):
        gate_module.RecordContentGate([record], changed)


def test_disjoint_review_decision_jsonl_partitions_are_supported(tmp_path):
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    first.write_text(
        json.dumps({"candidate_id": "candidate-1", "decision": "APPROVED"}) + "\n",
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"candidate_id": "candidate-2", "decision": "REJECTED"}) + "\n",
        encoding="utf-8",
    )

    assert gate_module._decision_map(None, [first, second]) == {
        "candidate-1": "APPROVED",
        "candidate-2": "REJECTED",
    }

    second.write_text(
        json.dumps({"candidate_id": "candidate-1", "decision": "REJECTED"}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(gate_module.ContentGateError, match="duplicate candidate_id"):
        gate_module._decision_map(None, [first, second])


def test_replay_uses_safe_loader_and_resolves_repeated_raw_path_once(tmp_path, monkeypatch):
    traits = tmp_path / "traits"
    traits.mkdir()
    record = traits / "record.yaml"
    record.write_text(
        "identifier: HAMAP:MF_FIXTURE\n"
        "label: DNA-binding protein <locus_tag>\n"
        "definition: >-\n"
        "  A folded fixture definition.\n"
        "definition_source: Fixture\n",
        encoding="utf-8",
    )
    expected_record = gate_module.yaml.safe_load(record.read_text(encoding="utf-8"))
    assert gate_module._load_record(record) == expected_record

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(
        "\n".join(
            json.dumps({"candidate_id": candidate_id, "record_path": "record.yaml"})
            for candidate_id in ("candidate-1", "candidate-2")
        )
        + "\n",
        encoding="utf-8",
    )
    original_record_path = gate_module._record_path
    resolved: list[str] = []

    def counted_record_path(value, root):
        resolved.append(value)
        return original_record_path(value, root)

    monkeypatch.setattr(gate_module, "_record_path", counted_record_path)
    monkeypatch.setattr(
        gate_module.yaml,
        "safe_load",
        lambda *_args, **_kwargs: pytest.fail("replay used the pure-Python safe_load path"),
    )

    summary = gate_module.replay_ledger(
        ledger,
        traits=traits,
        config=gate_module.SourceConfig(),
    )

    assert resolved == ["record.yaml"]
    assert summary["record_count"] == 1
    assert summary["candidate_row_count"] == 2
    assert summary["hard_record_count"] == 1
    assert summary["hard_candidate_row_count"] == 2
    assert summary["findings_by_code"] == {"UNRESOLVED_SOURCE_PLACEHOLDER": 1}
