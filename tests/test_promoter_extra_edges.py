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
