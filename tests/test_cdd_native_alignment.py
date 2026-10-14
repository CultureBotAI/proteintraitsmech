"""Synthetic source-format fixtures, NOT release snapshots/acquisition receipts.

The four FHA display strings were inspected at the public cd22708 viewer on
2026-10-03/04; markup and hierarchy fixtures below are deliberately minimal.
Tests require no network, ignored research reports, or local protein cache.
"""

from __future__ import annotations

import copy
import hashlib
import html
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cdd_native_alignment as cdd  # noqa: E402
import validate_uniprot_grounding as grounding  # noqa: E402


def node(acc, pssmid, name, *, selected=False, children=None):
    value = {"accession": acc, "pssmid": pssmid, "name": name, "isc": selected}
    if children is not None:
        value["children"] = children
    return value


@pytest.fixture
def hierarchy():
    return {"hasError": False, "rootAccession": "cd00060", "hierarchy":
            node("cd00060", 438714, "FHA", children=[
                node("cd22708", 438760, "FHA_KIF16", selected=True, children=[
                    node("cd22731", 438783, "FHA_KIF16A_STARD9"),
                    node("cd22732", 438784, "FHA_KIF16B"),
                ])]), "seqtree": {"ignored": "layout, not a family-parent assertion"}}


def parse_tree(value):
    return cdd.parse_hierarchy(json.dumps(value).encode(), requested_accession="cd22708")


def test_native_hierarchy_preserves_immediate_parent_not_root(hierarchy):
    before = copy.deepcopy(hierarchy)
    tree = parse_tree(hierarchy)
    assert tree.source_sha256 == hashlib.sha256(json.dumps(hierarchy).encode()).hexdigest()
    assert tree.root_accession == "cd00060" and tree.requested_accession == "cd22708"
    assert [n.accession for n in tree.nodes] == ["cd00060", "cd22708", "cd22731", "cd22732"]
    assert tree.nodes[0].parent is None
    assert tree.nodes[1].parent == "cd00060"
    for leaf in tree.nodes[2:]:
        assert leaf.parent == "cd22708"
        assert leaf.path == ("cd00060", "cd22708", leaf.accession)
    assert not hasattr(tree, "release")
    assert hierarchy == before


@pytest.mark.parametrize("damage", [
    "error", "missing_status", "wrong_root", "bad_root", "missing_tree", "children",
    "duplicate_acc", "cycle", "duplicate_pssm", "bool_pssm", "negative_pssm", "name",
    "selected_other", "selected_none", "selected_many", "bad_selected", "collapsed",
])
def test_invalid_hierarchy_rejected(hierarchy, damage):
    parent = hierarchy["hierarchy"]["children"][0]
    child = parent["children"][0]
    if damage == "error":
        hierarchy["hasError"] = True
    elif damage == "missing_status":
        hierarchy.pop("hasError")
    elif damage == "wrong_root":
        hierarchy["rootAccession"] = "cd22708"
    elif damage == "bad_root":
        hierarchy["rootAccession"] = "cl00062"
    elif damage == "missing_tree":
        hierarchy.pop("hierarchy")
    elif damage == "children":
        parent["children"] = {"cd22731": child}
    elif damage == "duplicate_acc":
        parent["children"].append(copy.deepcopy(child))
    elif damage == "cycle":
        child["accession"] = "cd00060"
    elif damage == "duplicate_pssm":
        child["pssmid"] = parent["pssmid"]
    elif damage == "bool_pssm":
        child["pssmid"] = True
    elif damage == "negative_pssm":
        child["pssmid"] = -1
    elif damage == "name":
        child["name"] = ""
    elif damage == "selected_other":
        parent["isc"], child["isc"] = False, True
    elif damage == "selected_none":
        parent["isc"] = False
    elif damage == "selected_many":
        child["isc"] = True
    elif damage == "bad_selected":
        child["isc"] = 0
    else:
        parent["collapsed"] = True
    with pytest.raises(cdd.CDDParseError):
        parse_tree(hierarchy)


@pytest.mark.parametrize("raw", [
    b"", b"\xff", b"not JSON", b"[]", b'{"x":1,"x":2}', b'{"x":NaN}',
    bytearray(b"{}"), "{}",
])
def test_bad_capture_or_json_rejected(raw):
    with pytest.raises(cdd.CDDParseError):
        cdd.parse_hierarchy(raw, requested_accession="cd22708")


# Source-printed parent intervals differ from child intervals 471..589 / 446..562.
FHA_BLOCKS = [
    [
        ("Q9P2P6", "378405232", "9606", 471,
         "GVVIDSSLPHLMALEDDv-lSTGVVLYHLKeGTTKIGRIDSdqeqd------ivlqGQWIERDHCTITSAc---------", 534),
        ("Q96L93", "50403793", "9606", 446,
         "GVVLDSELPHLIGIDDDl-lSTGIILYHLKeGQTYVGRDDAsteqd------ivlhGLDLESEHCIFENIg---------", 509),
    ],
    [
        ("Q9P2P6", "378405232", "9606", 535,
         "-GVVVLRPArgARCTVNGREVTaSCRLTQGAVITLGkAQKFRFNHP", 579),
        ("Q96L93", "50403793", "9606", 510,
         "-GTVTLIPLsgSQCSVNGVQIVeATHLNQGAVILLGrTNMFRFNHP", 554),
    ],
]


def display_row(acc, gi, taxon, start, seq, end):
    return (f'<a href="/protein/{html.escape(gi)}?report=GenPept">{html.escape(acc)}</a> '
            f'<span style="color:#229922"> {start} </span>'
            f'<span>{html.escape(seq)}</span> <span>{end}</span> '
            f'<a href="/Taxonomy/Browser/wwwtax.cgi?id={taxon}">human</a>')


def viewer(blocks=None, **updates):
    meta = {"accession": "cd22708", "pssmId": 438760, "isCluster": False,
            "isCuratedCD": True, "hasQuery": False, "totalSeqRows": 15,
            "totalSequences": 14, "maxAlnSeq": 15}
    meta.update(updates)
    if blocks is None:
        blocks = FHA_BLOCKS
    pres = "".join("<tr><td><pre>\n" + "\n".join(display_row(*row) for row in block)
                   + "\n</pre></td></tr>" for block in blocks)
    return (f'<html><head><script>var CDD={json.dumps(meta)};</script></head>'
            f'<body><div id="seqalign"><table>{pres}</table></div></body></html>').encode()


def parse_display(raw=None):
    return cdd.parse_alignment(raw if raw is not None else viewer(), requested_accession="cd22708")


def test_parent_source_numbering_case_gaps_and_capture_hash():
    alignment = parse_display()
    assert alignment.source_sha256 == hashlib.sha256(viewer()).hexdigest()
    assert alignment.accession == "cd22708" and alignment.pssmid == 438760
    assert alignment.total_seq_rows == 15 and alignment.total_sequences == 14
    # Parsing a subset never certifies all-row display, all carriers, or a release.
    assert len(alignment.rows) == 2
    assert not hasattr(alignment, "complete") and not hasattr(alignment, "release")
    a, b = alignment.rows
    assert (a.native_accession, a.start, a.end) == ("Q9P2P6", 471, 579)
    assert (b.native_accession, b.start, b.end) == ("Q96L93", 446, 554)
    assert len(a.sequence) == len(b.sequence) == 109
    assert a.chunks[0].display_sequence == FHA_BLOCKS[0][0][4]
    assert "DSSLPHLMALEDDVLSTG" in a.sequence  # lowercase retained as residues, gap removed
    assert a.protein_link == "/protein/378405232?report=GenPept"
    assert a.taxon_id == "NCBITaxon:9606"


def test_repeated_domains_are_distinct_rows_not_merged_by_accession():
    blocks = [[("P12345", "123", "9606", 2, "ACd-", 4),
               ("P12345", "123", "9606", 20, "ACd-", 22)],
              [("P12345", "123", "9606", 5, "EF", 6),
               ("P12345", "123", "9606", 23, "EF", 24)]]
    rows = parse_display(viewer(blocks)).rows
    assert [(r.row_index, r.start, r.end, r.sequence) for r in rows] == [
        (0, 2, 6, "ACDEF"), (1, 20, 24, "ACDEF")]


@pytest.mark.parametrize("damage", [
    "missing_row", "row_order", "identity", "taxon", "link", "gap", "overlap",
    "zero", "bounds", "compact", "width", "bad_residue", "all_gap",
])
def test_inconsistent_or_unsupported_display_rejected(damage):
    blocks = [[list(row) for row in block] for block in FHA_BLOCKS]
    row = blocks[1][0]
    if damage == "missing_row":
        blocks[1].pop()
    elif damage == "row_order":
        blocks[1].reverse()
    elif damage == "identity":
        row[0] = "Q96FW1"
    elif damage == "taxon":
        row[2] = "10090"
    elif damage == "link":
        row[1] = "111"
    elif damage == "gap":
        row[3] += 1
        row[5] += 1
    elif damage == "overlap":
        row[3] -= 1
        row[5] -= 1
    elif damage == "zero":
        row[3] = 0
    elif damage == "bounds":
        row[5] += 1
    elif damage == "compact":
        row[4] = row[4].replace("rg", "[2]")
    elif damage == "width":
        row[4] += "-"
    elif damage == "bad_residue":
        row[4] = row[4].replace("G", "?", 1)
    else:
        row[4] = "-" * len(row[4])
    with pytest.raises(cdd.CDDParseError):
        parse_display(viewer(blocks))


@pytest.mark.parametrize("field,value", [
    ("accession", "cd22731"), ("pssmId", True), ("pssmId", 0),
    ("isCuratedCD", False), ("isCluster", True), ("hasQuery", True),
    ("totalSeqRows", 1), ("totalSeqRows", "15"), ("maxAlnSeq", 1),
    ("maxAlnSeq", -1), ("totalSequences", 0),
])
def test_bad_alignment_metadata_rejected(field, value):
    with pytest.raises(cdd.CDDParseError):
        parse_display(viewer(**{field: value}))


@pytest.mark.parametrize("old,new", [
    (b'</div>', b''), (b'</pre>', b''), (b'var CDD=', b'var other='),
    (b'id="seqalign"', b'id="other"'),
    (b'<pre>', b'<pre><script>alert(1)</script>'),
    (b'<pre>', b'<pre><img src="x"/>'),
    (b'<pre>', b'<pre><!-- compact display -->'),
    (b'<span>', b'<span><span>'),
    (b'"/protein/378405232?', b'"https://example.org/protein/378405232?'),
    (b'id=9606', b'id=9606&amp;id=562'),
    (b'id=9606', b'id=9606&amp;id='),
    (b'report=GenPept', b'report=GenPept&amp;report='),
    (b'>Q9P2P6</a>', b'>Q9P2P6 Q96L93</a>'),
    (b'<div id="seqalign">', b'<div id="seqalign" id="seqalign">'),
])
def test_malformed_markup_and_links_rejected(old, new):
    with pytest.raises(cdd.CDDParseError):
        parse_display(viewer().replace(old, new))


def test_unrelated_page_chrome_does_not_affect_evidence_parser():
    raw = viewer().replace(b'<body>', b'<body><input size="3" size="4">')
    assert parse_display(raw).rows == parse_display().rows


def test_duplicate_alignment_container_rejected():
    raw = viewer().replace(b'</body>', b'<div id="seqalign"><pre></pre></div></body>')
    with pytest.raises(cdd.CDDParseError, match="duplicate"):
        parse_display(raw)


def test_duplicate_viewer_metadata_rejected():
    raw = viewer().replace(b'</head>', b'<script>var CDD={};</script></head>')
    with pytest.raises(cdd.CDDParseError, match="duplicate"):
        parse_display(raw)


def reference_for(row, **updates):
    sequence = "M" * (row.start - 1) + row.sequence + "M"
    ref = {"protein_id": "UniProtKB:" + row.native_accession, "protein_label": "Synthetic protein",
           "taxon_id": row.taxon_id, "taxon_label": "Homo sapiens", "sequence": sequence,
           "sequence_length": len(sequence), "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
           "uniprot_release": "2026_03", "sequence_version": 2, "reviewed": True}
    if "-" in row.native_accession:
        ref["isoform"] = int(row.native_accession.rsplit("-", 1)[1])
    ref.update(updates)
    return ref


def test_source_slice_check_does_not_change_reference_or_qualify():
    row = parse_display().rows[0]
    ref = reference_for(row)
    before = copy.deepcopy(ref)
    assert cdd.verify_uniprot_slice(row, ref) is None
    assert ref == before
    assert "qualification_status" not in ref


@pytest.mark.parametrize("field,value", [
    ("protein_id", "UniProtKB:Q96L93"), ("taxon_id", "NCBITaxon:562"),
    ("sequence_sha256", "0" * 64), ("sequence_length", 42),
    ("uniprot_release", "latest"),
])
def test_reference_mismatch_rejected(field, value):
    row = parse_display().rows[0]
    with pytest.raises(cdd.CDDParseError):
        cdd.verify_uniprot_slice(row, reference_for(row, **{field: value}))


def test_equal_sequence_elsewhere_does_not_shift_source_coordinates():
    row = parse_display().rows[0]
    ref = reference_for(row)
    ref["sequence"] = "M" + ref["sequence"]
    ref["sequence_length"] += 1
    ref["sequence_sha256"] = hashlib.sha256(ref["sequence"].encode()).hexdigest()
    with pytest.raises(cdd.CDDParseError, match="source slice mismatch"):
        cdd.verify_uniprot_slice(row, ref)


@pytest.mark.parametrize("native", ["4I6L_A", "XP_019630709", "44888285", "gi|44888285"])
def test_non_uniprot_source_frame_never_relabelled_from_sequence_match(native):
    row = parse_display(viewer([[(native, "123", "9606", 5, "ACD", 7)]])).rows[0]
    ref = reference_for(row, protein_id="UniProtKB:Q96FW1")
    with pytest.raises(cdd.CDDParseError, match="mapping required"):
        cdd.verify_uniprot_slice(row, ref)


def test_explicit_isoform_is_not_canonical_fallback():
    row = parse_display(viewer([[('P12345-2', '123', '9606', 5, 'ACD', 7)]])).rows[0]
    ref = reference_for(row)
    cdd.verify_uniprot_slice(row, ref)
    ref.pop("isoform")
    ref["protein_id"] = "UniProtKB:P12345"
    with pytest.raises(cdd.CDDParseError, match="exact accession/isoform"):
        cdd.verify_uniprot_slice(row, ref)


def test_native_cdd_provider_stays_denied():
    errors = grounding._provider_contract_errors({
        "provider_kind": "SOURCE_DATABASE", "evidence_source": "NCBICDD",
        "mapping_method": "SOURCE_NATIVE_COORDINATES", "scope": "LOCALIZED",
        "trait_id": "CDD:cd22708", "source_trait_id": "CDD:cd22708",
    })
    assert "source_database_contract_required" in {code for code, _ in errors}
