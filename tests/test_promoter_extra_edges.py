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
    blocks = out.split("      - subject: ")[1:]
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
    blocks = out.split("      - subject: ")[1:]
    for b in blocks:
        assert b.count("- reference: ") == 1


def test_a_list_snippet_makes_one_item_per_entry_with_its_own_reference():
    out = _graph(_cfg(det_res=[
        {"reference": "PMID:11", "snippet": "observed", "notes": "association"},
        {"reference": "PMID:22", "snippet": "measured", "notes": "mechanism"},
    ]))
    edge = [b for b in out.split("      - subject: ")[1:] if "confers resistance" in b][0]
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
    edge = [b for b in out.split("      - subject: ")[1:] if "confers resistance" in b][0]
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
    edge = [b for b in out.split("      - subject: ")[1:] if "confers resistance" in b][0]
    assert edge.count("- reference: ") == 2
    assert "Insertional inactivation of vanX" in edge
