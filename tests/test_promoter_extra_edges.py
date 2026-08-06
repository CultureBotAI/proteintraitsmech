"""`promote_family_drafts`'s family-specific node/edge extension (round 18).

The promoter's graph shape was written for enzymatic INACTIVATION — an active site
that hydrolyses the drug — and every family in `FAMILY_SNIPPETS` until gyrA fitted it.
Target alteration does not: the determinant *is* the drug's target, and the causation
runs through a region of that target and a drug–target complex, neither of which the
fixed shape has a place for. `extra_nodes`/`extra_edges` are that place.

The one behaviour worth pinning is the guard. Mechanism and drug nodes are derived
per record from its OWN ARO relations, so a family member need not carry the node an
extra edge names. Without the guard the promoter would emit an edge pointing at a
node that does not exist in that record — which `just validate` does NOT catch,
because `subject`/`object` are plain strings in the schema. Only `just audit-graphs`
would, and only after the record was written.
"""

from __future__ import annotations

import importlib
import pathlib
import re
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

promote = importlib.import_module("promote_family_drafts")


def _cfg(**over):
    cfg = {
        "reference": "PMID:1",
        "mech": {"ARO:3000212": "mech snippet"},
        "mech_res": "mech-res snippet",
        "det_res": "det-res snippet",
        "res_drug": "res-drug snippet",
        "note": "note",
    }
    cfg.update(over)
    return cfg


def _graph(cfg, mech=("ARO:3000212",), drug=("ARO:0000001",)):
    return "\n".join(promote.promoted_graph(
        "ARO:9999999", "test determinant", list(mech), list(drug),
        {"ARO:3000212": "mutation conferring antibiotic resistance",
         "ARO:0000001": "fluoroquinolone antibiotic"}, cfg))


def test_extra_nodes_and_edges_are_emitted():
    out = _graph(_cfg(
        extra_nodes=[{"node_id": "qrdr", "label": "QRDR", "node_type": "MOTIF"}],
        extra_edges=[{"subject": "qrdr", "object": "determinant",
                      "predicate": "part of", "predicate_id": "BFO:0000050",
                      "evidence": [{"reference": "PMID:2", "snippet": "s", "notes": "n"}]}]))
    assert "node_id: qrdr" in out
    assert "subject: qrdr" in out and "object: determinant" in out
    assert "reference: PMID:2" in out


def test_an_extra_edge_with_a_missing_endpoint_is_skipped_not_dangled():
    """A member without the drug node must not get an edge pointing at `drug0`.

    This is the guard's whole purpose: `drug0` exists only if the record's own ARO
    relations produced a drug, and family members differ.
    """
    cfg = _cfg(extra_edges=[{"subject": "drug0", "object": "determinant",
                             "predicate": "p", "predicate_id": "RO:0002436",
                             "evidence": [{"reference": "PMID:3", "snippet": "s",
                                           "notes": "n"}]}])
    with_drug = _graph(cfg, drug=("ARO:0000001",))
    without_drug = _graph(cfg, drug=())
    assert "subject: drug0" in with_drug
    assert "subject: drug0" not in without_drug
    assert "node_id: drug0" not in without_drug      # and nothing dangles at it


def test_a_node_without_a_grounding_emits_no_grounding_key():
    """Ungrounded is a deliberate state (the QRDR has no ontology term), not a blank.

    An empty `grounding:` would fail the CURIE pattern in closed-mode validation.
    """
    out = _graph(_cfg(extra_nodes=[
        {"node_id": "qrdr", "label": "QRDR", "node_type": "MOTIF"},
        {"node_id": "act", "label": "activity", "node_type": "MOLECULAR_FUNCTION",
         "grounding": "GO:0003918"}]))
    qrdr_block = out.split("node_id: qrdr", 1)[1].split("- node_id:", 1)[0]
    assert "grounding:" not in qrdr_block
    assert "grounding: GO:0003918" in out


def test_the_two_regressions_the_canary_found_stay_fixed():
    """Promoting a draft must not LOSE what the draft already had.

    The auto-draft grounds its phenotype node to GO:0046677 and gives its drug edge a
    `predicate_id`; the promoter dropped both, so promotion *added* two audit warnings
    to a record that did not have them. Found by applying the promoter to ONE record
    and auditing it before running the other 24 — neither shows up in `just validate`.
    """
    out = _graph(_cfg())
    assert "grounding: GO:0046677" in out
    # one `predicate:` line per edge, and every one of them a `predicate_id:` too
    assert out.count("predicate: ") == out.count("predicate_id: ") > 0


# --- round 19: the four fluoroquinolone target-alteration families ------------------

FQ_FAMILIES = ["ARO:3003292", "ARO:3000619", "ARO:3000864", "ARO:3003313"]  # gyrA parC gyrB parE


@pytest.mark.parametrize("family", FQ_FAMILIES)
def test_no_duplicate_node_ids(family):
    """`protein_traits` and `extra_nodes` must not both define the same node.

    They did: the shared `_fq_shared_nodes` helper emitted a `domain` node while
    `protein_traits["primary_key"]` was also `domain`, so every record got
    `node_id: domain` twice. **`just validate` accepts that** — the schema has no
    uniqueness constraint on `node_id` — and only `just audit-graphs` calls it an error.
    It reached three records because one per family was promoted before the rest.
    """
    out = _graph(promote.FAMILY_SNIPPETS[family])
    ids = [ln.split("node_id: ", 1)[1] for ln in out.splitlines() if "- node_id: " in ln]
    assert len(ids) == len(set(ids)), f"{family}: duplicates {sorted(set(i for i in ids if ids.count(i) > 1))}"


@pytest.mark.parametrize("family", FQ_FAMILIES)
def test_every_edge_of_a_shipped_family_is_cited(family):
    """The corpus invariant (369,291/369,291 snippet-cited) held at the config level."""
    out = _graph(promote.FAMILY_SNIPPETS[family])
    blocks = out.split("\n  - subject: ")[1:]
    assert blocks, "no edges emitted"
    for b in blocks:
        assert "snippet: " in b, f"{family}: an edge has no snippet"


def test_the_a_and_b_subunits_do_not_share_a_domain_node():
    """gyrB/parE must NOT route through the A-subunit domain, and vice versa.

    The B subunit carries the ATPase and TOPRIM domains, not the active-site tyrosine and
    not the water–metal ion bridge pair, so reusing gyrA's `Pfam:PF00521` node there would
    assert the wrong protein trait — and citing the A-subunit affinity experiment on a
    gyrB record would cite the wrong experiment.
    """
    a = {f: promote.FAMILY_SNIPPETS[f]["protein_traits"]["domain"][0]
         for f in ("ARO:3003292", "ARO:3000619")}
    b = {f: promote.FAMILY_SNIPPETS[f]["protein_traits"]["domain"][0]
         for f in ("ARO:3000864", "ARO:3003313")}
    assert set(a.values()) == {"Pfam:PF00521"}
    assert set(b.values()) == {"Pfam:PF00204"}


# --- #190: a standard edge may carry more than one EvidenceItem --------------------

def test_a_string_snippet_still_makes_exactly_one_evidence_item():
    """Backward compatibility is the whole safety property here.

    28 of the 32 families write a plain string and must keep emitting byte-identical
    output, or re-promoting any of them would rewrite records for no reason.
    """
    out = _graph(_cfg())
    blocks = out.split("\n  - subject: ")[1:]
    for b in blocks:
        assert b.count("- reference: ") == 1


def test_a_list_snippet_makes_one_item_per_entry_with_its_own_reference():
    out = _graph(_cfg(det_res=[
        {"reference": "PMID:11", "snippet": "observed", "notes": "association"},
        {"reference": "PMID:22", "snippet": "measured", "notes": "mechanism"},
    ]))
    edge = [b for b in out.split("\n  - subject: ")[1:] if "confers resistance" in b][0]
    assert edge.count("- reference: ") == 2
    assert "PMID:11" in edge and "PMID:22" in edge
    assert "association" in edge and "mechanism" in edge


@pytest.mark.parametrize("family,n", [("ARO:3000864", 2), ("ARO:3003313", 2),
                                      ("ARO:3003292", 1), ("ARO:3000619", 1)])
def test_the_b_subunits_cite_two_sources_for_their_causal_edge(family, n):
    """gyrB and parE each need two: the substitutions, and why they cause resistance.

    gyrB: Yoshida 1991 found the substitutions, Pantel 2012 measured that they confer
    resistance. parE: Eaves 2004 observed them in isolates, and the mechanism is carried
    across from GyrB by the subunit homology Aldred 2014 states — parE has no
    reconstituted-enzyme measurement of its own, which is exactly what the second item
    makes visible instead of burying in prose.
    """
    out = _graph(promote.FAMILY_SNIPPETS[family])
    edge = [b for b in out.split("\n  - subject: ")[1:] if "confers resistance" in b][0]
    assert edge.count("- reference: ") == n


# --- round 20: vanX, a mechanism that is neither inactivation nor target alteration ---

def test_vanx_routes_through_its_own_domain_and_not_a_topoisomerase_one():
    """Each family's `domain` node must be the trait that carries ITS mechanism.

    Four families now share the `domain` node id, so a copy-paste that left
    `Pfam:PF00521` on vanX would still emit a valid, cited, non-duplicated graph — and
    assert that a vancomycin dipeptidase is a DNA gyrase subunit. No gate would catch it.
    """
    assert promote.FAMILY_SNIPPETS["ARO:3000011"]["protein_traits"]["domain"][0] == "Pfam:PF01427"


def test_vanx_cites_the_loss_of_function_experiment_for_its_causal_edge():
    """The inactivation result is what makes the edge causal rather than correlative."""
    out = _graph(promote.FAMILY_SNIPPETS["ARO:3000011"],
                 mech=("ARO:3000213",), drug=("ARO:3000081",))
    edge = [b for b in out.split("\n  - subject: ")[1:] if "confers resistance" in b][0]
    assert edge.count("- reference: ") == 2
    assert "Insertional inactivation of vanX" in edge


# --- round 21: vanH, a family node rather than a domain node ----------------------

def test_vanh_uses_member_of_a_family_not_part_of_a_domain():
    """A determinant is a MEMBER of a protein family, not composed of one.

    `protein_traits` only emits `domain part of determinant`, so vanH deliberately has no
    `protein_traits` block: its KB trait is `NCBIfam:NF000492`, a family. The obvious
    alternative — `Pfam:PF00389`, the D-isomer 2-hydroxyacid dehydrogenase catalytic
    domain — is **not** used, because its abstract never names VanH and citing it for a
    membership claim is the defect filed as #196.
    """
    cfg = promote.FAMILY_SNIPPETS["ARO:3000006"]
    assert "protein_traits" not in cfg
    out = _graph(cfg, mech=("ARO:3000213",), drug=("ARO:3000081",))
    assert "grounding: NCBIfam:NF000492" in out
    assert "Pfam:PF00389" not in out
    edge = [b for b in out.split("\n  - subject: ")[1:] if "object: family" in b][0]
    assert "RO:0002350" in edge                       # member of, not BFO:0000050
    assert edge.count("- reference: ") == 2           # paper + NCBIfam, joined explicitly


# --- #194 / #191: layout parity with the builders, and per-family curation dates ----

def test_the_promoter_emits_the_same_layout_as_the_builders():
    """Hand-built indentation drifted from what the 40,115 existing graphs use (#194).

    The five `build_*_causal_graphs.py` scripts all dump with `default_flow_style=False`,
    which does NOT indent sequences under a mapping key. The promoter indented them, so
    re-promoting one record changed ~150 lines with no change of content. Both now go
    through the same dumper, so a re-promotion diff shows content and nothing else.
    """
    out = _graph(_cfg())
    assert out.startswith("causal_graphs:\n- graph_id: resistance")
    assert "\n  nodes:\n  - node_id: determinant" in out
    assert "\n  edges:\n  - subject: determinant" in out


def test_edge_keys_are_in_the_builders_order():
    """`subject, predicate, predicate_id, object, [description], evidence`.

    The ~6,180 records promoted before round 18 carry a different order — predicate_id and
    description AFTER evidence — but the 34,000+ builder-written graphs use this one, so
    the promoter converges on the majority rather than preserving its own outlier.
    """
    out = _graph(_cfg())
    edge = out.split("\n  - subject: ")[1]
    keys = [ln.strip().split(":")[0] for ln in edge.splitlines() if re.match(r"^    \w", ln)]
    assert keys[:3] == ["predicate", "predicate_id", "object"]


def test_a_family_carries_its_own_curation_date():
    """One hardcoded constant made 6,235 records claim 2026-07-21, 53 of them wrongly (#191).

    Per-family instead of `now()`, because every builder hardcodes its round's date on
    purpose: a re-run must not churn timestamps.
    """
    assert promote.curation_event({"curated": "2026-08-05T00:00:00Z"})[1].endswith(
        "2026-08-05T00:00:00Z'")
    assert promote.LEGACY_PROMOTION in promote.curation_event({})[1]
    for fam in ["ARO:3003292", "ARO:3000619", "ARO:3000864", "ARO:3003313",
                "ARO:3000011", "ARO:3000006"]:
        assert promote.FAMILY_SNIPPETS[fam]["curated"] == "2026-08-05T00:00:00Z"


# --- round 22: vanR/vanS, regulation, and graphs that point at earlier rounds ------

@pytest.mark.parametrize("family", ["ARO:3000574", "ARO:3000071"])   # vanR, vanS
def test_the_regulators_end_at_the_enzyme_records_they_induce(family):
    """vanR/vanS confer no resistance themselves — they transcribe the genes that do.

    Those genes are already curated records here (vanH round 21, vanX round 20), so the
    graph ends at their ARO ids rather than restating their mechanisms. This is the first
    round whose graphs point at earlier rounds' output, and it is the property that would
    silently break if someone replaced the nodes with free-text labels.
    """
    out = _graph(promote.FAMILY_SNIPPETS[family], mech=("ARO:3000213",), drug=("ARO:3000081",))
    assert "grounding: ARO:3000006" in out          # vanH, round 21
    assert "grounding: ARO:3000011" in out          # vanX, round 20
    downstream = [b for b in out.split("\n  - subject: ")[1:] if "object: resistance" in b]
    assert any("vanh_gene" in b or "vanx_gene" in b for b in downstream)


@pytest.mark.parametrize("family", ["ARO:3000574", "ARO:3000071"])
def test_the_regulator_families_are_fully_grounded(family):
    """Every node has a CURIE — the first families in this thread for which that is true.

    Rounds 18–21 each added 1–2 label-only nodes per record (the QRDR, the pentapeptide,
    the drug–target complex) because no ontology names them. A regulatory story has no
    such gap: GO has the processes, ARO has the genes, NCBIfam has the families.
    """
    out = _graph(promote.FAMILY_SNIPPETS[family], mech=("ARO:3000213",), drug=("ARO:3000081",))
    blocks = out.split("\n  - node_id: ")[1:]
    ungrounded = [b.splitlines()[0] for b in blocks if "grounding:" not in b]
    assert not ungrounded, f"{family}: label-only nodes {ungrounded}"


# --- #201 / #199: the verify guard, and structural self-identification -------------

def test_config_curies_collects_groundings_and_references():
    curies = promote.config_curies(promote.FAMILY_SNIPPETS["ARO:3000006"])   # vanH
    assert "NCBIfam:NF000492" in curies          # a node grounding
    assert not any(c.startswith("PMID") for c in curies)   # papers are not KB records


def test_the_vanrs_precondition_derives_the_exclusions_that_were_hand_written():
    """The 12 records round 22 held back are now DERIVED, not listed (#201).

    A hand-maintained `exclude` tuple is correct only until the corpus changes under it.
    The predicate asks the corpus the same question every run: does this record's cluster
    contain the genes my downstream nodes name?
    """
    pre = promote.FAMILY_SNIPPETS["ARO:3000574"]["precondition"]
    # a D-Ala-D-Lac cluster has both, so it passes
    assert pre("ARO:3002919", "vanR gene in vanA cluster", "") is None
    # a D-Ala-D-Ser cluster has neither, so it is refused with a reason naming them
    reason = pre("ARO:3002922", "vanR gene in vanC cluster", "")
    assert reason and "vanH" in reason and "vanX" in reason
    # vanI has vanX but no vanH — the partial case, which a letter-based rule would miss.
    # Assert on the "has no ..." clause, not the whole string: the reason also lists the
    # genes the cluster DOES have, and vanX is one of them.
    reason = pre("ARO:3003728", "vanR gene in vanI cluster", "")
    assert reason and "has no vanH (" in reason and "has no vanH or vanX" not in reason
    # the family-level record carries no cluster and is the term the evidence describes
    assert pre("ARO:3000574", "vanR", "") is None


def test_neither_van_config_still_carries_a_hand_written_exclude_list():
    for fam in ("ARO:3000574", "ARO:3000071"):
        assert "exclude" not in promote.FAMILY_SNIPPETS[fam]
        assert callable(promote.FAMILY_SNIPPETS[fam]["precondition"])
