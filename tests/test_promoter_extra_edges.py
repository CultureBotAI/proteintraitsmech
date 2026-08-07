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



def _flat(text: str) -> str:
    """Collapse whitespace before matching a quoted phrase.

    `yaml.safe_dump(width=100)` wraps long snippets, so a phrase from the middle of one is
    split across lines and a raw substring test fails on text that is actually present.
    The same trap as #199, where prose-grepping a wrapped `action:` string was the defect.
    """
    return " ".join(text.split())


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
    out = _graph(promote.family_configs(family)[0], mech=("ARO:3000213",), drug=("ARO:3000081",))
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
    out = _graph(promote.family_configs(family)[0], mech=("ARO:3000213",), drug=("ARO:3000081",))
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
    pre = promote.family_configs("ARO:3000574")[0]["precondition"]
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
        for cfg in promote.family_configs(fam):       # two each since #208
            assert "exclude" not in cfg
            assert callable(cfg["precondition"])


def test_a_precondition_skip_is_not_a_verify_failure():
    """The guard refusing a record is it WORKING, not a problem to fix.

    vanR/vanS correctly refuse 12 records every run. Counting those as failures would
    leave `just verify-family-drafts` permanently red, and a gate that is always red is a
    gate nobody reads. Only an unresolved CURIE — a config grounding a node to something
    that is not a record — is an error.
    """
    cfg = promote.family_configs("ARO:3000574")[0]
    candidates = [("ARO:3002922", "vanR gene in vanC cluster", ""),
                  ("ARO:3002919", "vanR gene in vanA cluster", "")]
    # seed the corpus index rather than letting `verify` build it: the real one reads one
    # line from each of 429k files (~70s), which is fine for a pre-round check and absurd
    # in a unit test. Seeding also makes this hermetic — it tests the exit-code rule, not
    # what happens to be in data/traits today.
    promote._IDENTIFIER_INDEX = set(promote.config_curies(cfg))
    try:
        assert promote.verify("ARO:3000574", cfg, {}, candidates) == 0
    finally:
        promote._IDENTIFIER_INDEX = None


def test_config_curies_sees_list_form_standard_edge_evidence():
    """Since #190 a standard edge may carry a list, and an item can cite a KB record."""
    cfg = _cfg(det_res=[{"reference": "NCBIfam:NF000492", "snippet": "s", "notes": "n"},
                        {"reference": "PMID:1", "snippet": "s", "notes": "n"}])
    curies = promote.config_curies(cfg)
    assert "NCBIfam:NF000492" in curies and "PMID:1" not in curies


# --- Codex review of #202: what five self-review rounds missed --------------------

def test_an_uncovered_mechanism_raises_instead_of_substituting_another_snippet():
    """The promoter used to write ANOTHER mechanism's evidence and stamp it REVIEWED.

    `cfg["mech"].get(mid) or next(iter(cfg["mech"].values()))` — a family member carrying
    a mechanism the config has no snippet for silently got the config's *first* snippet,
    with `notes: Family mechanism <the uncovered id>` asserting a provenance nobody
    established. 1,044 already-promoted records did (#203); the promotion path now skips.
    """
    with pytest.raises(promote.UncoveredMechanism) as exc:
        _graph(_cfg(), mech=("ARO:3000212", "ARO:9999999"))
    assert exc.value.mechanism_id == "ARO:9999999"


def test_the_van_precondition_fails_closed_on_an_unparsed_cluster_label():
    """A label that names a cluster but does not parse must be refused, not passed.

    It returned None for any unmatched label, so a future shape (`vanC1`, a case change)
    would fail OPEN and receive the vanH/vanX graph.
    """
    pre = promote.family_configs("ARO:3000574")[0]["precondition"]
    assert pre("ARO:X", "vanR gene in vanQ1 cluster", "") is not None
    assert pre("ARO:X", "vanR", "") is None          # genuinely no cluster: still passes


def test_verify_flags_a_family_with_no_candidates_and_a_stale_exclude():
    """Zero candidates is unchecked, not verified — a renamed family id reads as healthy."""
    promote._IDENTIFIER_INDEX = set()
    try:
        assert promote.verify("ARO:0000000", _cfg(), {}, []) >= 1
        assert promote.verify("ARO:0000000", _cfg(exclude=("ARO:1234567",)), {},
                              [("ARO:7654321", "x", "")]) >= 1
    finally:
        promote._IDENTIFIER_INDEX = None


def test_a_quoted_identifier_is_still_matched():
    """`identifier: "ARO:3001234"` is valid YAML; the regex used to miss it entirely,
    silently omitting the record from both verification and promotion."""
    import re as _re
    pat = _re.compile(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', _re.M)
    assert pat.search('identifier: "ARO:3001234"\n').group(1) == "ARO:3001234"
    assert pat.search("identifier: ARO:3001234\n").group(1) == "ARO:3001234"


# --- #204: re-promotion must not destroy what it did not write --------------------

def _record_with_two_graphs() -> str:
    return (
        "identifier: ARO:3009999\n"
        'label: "test determinant"\n'
        "mapping_status: REVIEWED\n"
        "causal_graphs:\n"
        "- graph_id: reaction_chemistry\n"
        "  title: a builder's graph\n"
        "  nodes:\n"
        "  - node_id: a\n"
        "    label: a\n"
        "    node_type: PROTEIN\n"
        "  edges: []\n"
        "- graph_id: resistance\n"
        "  title: the promoter's graph\n"
        "  nodes: []\n"
        "  edges: []\n"
        "curation_history:\n"
        "- timestamp: '2026-01-01T00:00:00Z'\n"
        "  curator: a-human\n"
        "  action: hand-checked the residue numbering\n"
        "  llm_assisted: false\n"
        "license: CC-BY 4.0\n")


def test_re_promotion_preserves_another_builders_graph_and_prior_history():
    """The old write path took every line between `causal_graphs:` and `license:`.

    That destroys any OTHER graph on the record and the whole curation_history — which is
    why every promoted record carried exactly one event however many times it had been
    promoted. Invisible in the diff of a record that only ever had our graph, which is how
    it survived six rounds (#204).
    """
    import yaml as _yaml
    text = _record_with_two_graphs()
    doc = _yaml.safe_load(text)
    graphs = [g for g in doc["causal_graphs"] if g.get("graph_id") != "resistance"]
    graphs.append({"graph_id": "resistance", "title": "rewritten", "nodes": [], "edges": []})
    history = list(doc["curation_history"]) + [promote.curation_entry({})]
    new = promote.RIO.replace_block(
        text, "causal_graphs", "\n".join(promote._dump({"causal_graphs": graphs})))
    new = promote.RIO.replace_block(
        new, "curation_history", "\n".join(promote._dump({"curation_history": history})))
    out = _yaml.safe_load(new)
    assert [g["graph_id"] for g in out["causal_graphs"]] == ["reaction_chemistry", "resistance"]
    assert out["causal_graphs"][0]["title"] == "a builder's graph"     # untouched
    assert out["causal_graphs"][1]["title"] == "rewritten"             # ours, replaced
    assert [h["curator"] for h in out["curation_history"]] == ["a-human", "edison-causal-graphs"]
    assert out["license"] == "CC-BY 4.0"


def test_the_same_curation_event_is_not_appended_twice():
    """Re-promoting repeatedly must not grow the history without bound."""
    ev = promote.curation_entry({"curated": "2026-08-06T00:00:00Z"})
    history = [ev]
    if ev not in history:
        history.append(ev)
    assert len(history) == 1


def test_promoting_a_draft_removes_the_draft_graph():
    """The promoter owns BOTH ids: it consumes `resistance-draft` and produces `resistance`.

    Filtering only `resistance` left a promoted draft carrying its own superseded draft
    graph beside the curated one. The canary missed it because it exercised the
    RE-promote path, where the graph is already `resistance` — not the primary
    promote-a-draft path, which is the one with 1,133 records still to run through it.
    """
    assert promote.OWNED_GRAPH_IDS == {"resistance", "resistance-draft"}
    graphs = [{"graph_id": "resistance-draft"}, {"graph_id": "reaction_chemistry"}]
    kept = [g for g in graphs if g.get("graph_id") not in promote.OWNED_GRAPH_IDS]
    assert [g["graph_id"] for g in kept] == ["reaction_chemistry"]


def test_a_duplicated_causal_graphs_key_is_refused_not_silently_collapsed():
    """`yaml.safe_load` keeps the LAST duplicate block and discards the earlier one.

    Merging through a loader would therefore quietly delete graphs on exactly the
    corrupted record `record_io.graph_ids` was written to catch. 0 records carry a
    duplicate today; the point is not to be the tool that hides it.
    """
    dup = ("identifier: ARO:3009999\n"
           "causal_graphs:\n- graph_id: a\n"
           "causal_graphs:\n- graph_id: b\n"
           "license: CC-BY 4.0\n")
    with pytest.raises(promote.RIO.RecordError):
        promote.RIO.graph_ids(dup)


# --- #188: the extra-edge guard checks identity, not just existence ---------------

def test_an_edge_is_skipped_when_its_required_grounding_does_not_match():
    """`drug0` is POSITIONAL — whatever that record's ARO relations produced, in order.

    An edge naming it therefore gets that record's first drug, whatever it is, and a
    drug-specific snippet would be attached to the wrong drug. Every fluoroquinolone and
    glycopeptide family was verified to carry the drug its snippet is about, but nothing
    enforced it, and the van clusters carry several drug classes each.
    """
    cfg = _cfg(extra_edges=[{
        "subject": "drug0", "object": "determinant", "predicate": "p",
        "predicate_id": "RO:0002436", "requires": {"drug0": "ARO:0000001"},
        "evidence": [{"reference": "PMID:1", "snippet": "s", "notes": "n"}]}])
    right = _graph(cfg, drug=("ARO:0000001",))          # the drug the edge was written for
    wrong = _graph(cfg, drug=("ARO:3000081",))          # a different drug class
    assert "subject: drug0" in right
    assert "subject: drug0" not in wrong


@pytest.mark.parametrize("family,node,want", [
    ("ARO:3003292", "drug0", "ARO:0000001"),    # gyrA — quinolone snippet
    ("ARO:3000011", "drug0", "ARO:3000081"),    # vanX — glycopeptide snippet
    ("ARO:3000006", "drug0", "ARO:3000081"),    # vanH — vancomycin Kd
])
def test_drug_specific_edges_state_the_drug_they_were_written_for(family, node, want):
    reqs = [e.get("requires") for e in promote.FAMILY_SNIPPETS[family]["extra_edges"]
            if e.get("requires")]
    assert {node: want} in reqs


# --- #196: a part-of snippet must support a MEMBERSHIP claim ----------------------

def test_verify_flags_a_bare_entry_title_as_thin_partof_evidence(capsys):
    """"Beta-lactamase class-A active site" identifies a signature.

    It does not say this determinant carries it, which is what the part-of edge asserts.
    27 of 33 families cite such a title (#196). Reported, not failed: the fix is per
    family — substitute the source abstract, as vanX does with the InterPro:IPR000755
    text that names VanX outright.
    """
    promote._IDENTIFIER_INDEX = {"PROSITE:PS00146"}
    try:
        cfg = _cfg(protein_traits={
            "primary_key": "active_site",
            "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature",
                            "MOTIF", "Beta-lactamase class-A active site")})
        assert promote.verify("ARO:1", cfg, {}, [("ARO:2", "x", "")]) == 0   # not a failure
        assert "thin part-of evidence" in capsys.readouterr().out
    finally:
        promote._IDENTIFIER_INDEX = None


def test_a_snippet_that_names_the_domain_is_not_flagged(capsys):
    promote._IDENTIFIER_INDEX = {"Pfam:PF01427"}
    try:
        cfg = _cfg(protein_traits={
            "primary_key": "domain",
            "domain": ("Pfam:PF01427", "D-Ala-D-Ala dipeptidase domain (MEROPS M15D)", "DOMAIN",
                       "This group of metallopeptidases belong to MEROPS peptidase family M15 "
                       "(clan MD), subfamily M15D (vanX D-Ala-D-Ala dipeptidase).")})
        promote.verify("ARO:1", cfg, {}, [("ARO:2", "x", "")])
        assert "thin part-of evidence" not in capsys.readouterr().out
    finally:
        promote._IDENTIFIER_INDEX = None


# --- round 23: the D-Ala-D-Ser route ----------------------------------------------

SER_FAMILIES = ["ARO:3002979", "ARO:3000372", "ARO:3000496"]   # ligase, vanT, vanXY


@pytest.mark.parametrize("family", SER_FAMILIES)
def test_the_ser_families_refuse_a_d_ala_d_lac_cluster(family):
    """Written BEFORE the fan-out this time, unlike round 22's (#201).

    A cluster carrying vanH is the depsipeptide route of rounds 20–21, and its genes are
    not these.
    """
    pre = promote.FAMILY_SNIPPETS[family]["precondition"]
    assert pre("ARO:X", "vanT gene in vanC cluster", "") is None        # D-Ala-D-Ser
    assert pre("ARO:X", "vanH gene in vanA cluster", "") is not None    # D-Ala-D-Lac
    assert pre("ARO:X", "vanT", "") is None                             # family-level term


def test_vant_ends_at_the_ligase_record_curated_in_the_same_round():
    """Cross-round citation, now within a round: vanT supplies the ligase's substrate."""
    out = _graph(promote.FAMILY_SNIPPETS["ARO:3000372"],
                 mech=("ARO:3000213",), drug=("ARO:3000081",))
    assert "grounding: ARO:3002979" in out
    edge = [b for b in out.split("\n  - subject: ")[1:] if "object: ligase_gene" in b][0]
    assert "RO:0002411" in edge


def test_vanxy_cites_the_negative_result_that_makes_the_pathway_coherent():
    """The enzyme clears the D-Ala route WITHOUT destroying the D-Ser precursor.

    Same device as round 20's vanX: a graph recording only what an enzyme does cannot
    explain why the cell survives its own clean-up.
    """
    out = _graph(promote.FAMILY_SNIPPETS["ARO:3000496"],
                 mech=("ARO:3000213",), drug=("ARO:3000081",))
    assert "very low dipeptidase activity against D-Ala-D-Ser" in _flat(out)


def test_ec_and_the_other_record_prefixes_are_checked_by_verify():
    """`EC:` was missing, so `EC:6.3.2.35` was written unchecked — found by running the
    guard on this round's own configs before promoting."""
    for prefix in ("EC:", "GO:", "SFLD:", "PANTHER:", "HAMAP:"):
        assert prefix in promote.KB_PREFIXES
    assert "EC:6.3.2.35" in promote.config_curies(promote.FAMILY_SNIPPETS["ARO:3002979"])


# --- #208: a family may carry several configs, chosen by their preconditions -------

def test_a_family_can_carry_two_configs_selected_by_precondition():
    """vanR/vanS span BOTH van routes, and the right downstream is a property of the
    RECORD, not the family. The `precondition` each config already has for #201 is the
    selector — the predicate that refuses a record is what chooses between configs."""
    assert len(promote.family_configs("ARO:3000574")) == 2
    lac = promote.config_for("ARO:3000574", "ARO:1", "vanR gene in vanA cluster", "")
    ser = promote.config_for("ARO:3000574", "ARO:2", "vanR gene in vanC cluster", "")
    assert lac is not ser
    lac_ids = {n.get("grounding") for n in lac["extra_nodes"]}
    ser_ids = {n.get("grounding") for n in ser["extra_nodes"]}
    assert {"ARO:3000006", "ARO:3000011"} <= lac_ids            # vanH, vanX
    assert {"ARO:3002979", "ARO:3000372", "ARO:3000496"} <= ser_ids   # ligase, vanT, vanXY
    assert not (lac_ids & ser_ids & {"ARO:3000006", "ARO:3002979"})


def test_a_catch_all_config_may_not_shadow_a_specific_one():
    """A config without a precondition matches everything, so it must be last.

    Checked at import (`_check_config_order`) rather than left to be discovered when a
    family silently stops using the config that was written for it.
    """
    promote.FAMILY_SNIPPETS["ARO:9999999"] = [dict(_cfg()), dict(_cfg())]
    try:
        with pytest.raises(ValueError, match="must be last"):
            promote._check_config_order()
    finally:
        del promote.FAMILY_SNIPPETS["ARO:9999999"]


def test_every_shipped_family_passes_the_config_order_check():
    promote._check_config_order()


# --- round 25: vanY, and the mirror precondition -----------------------------------

def test_vany_refuses_a_d_ala_d_ser_cluster():
    """PMID:10094630 measured R-D-Ala-D-Ala and R-D-Ala-D-Lac substrates, not D-Ser.

    The one vanY draft in a vanG cluster is held back rather than given a graph whose
    evidence does not cover its substrate — caught before the first `--apply`, unlike
    round 22.
    """
    pre = promote.family_configs("ARO:3000077")[0]["precondition"]
    assert pre("ARO:X", "vanY gene in vanA cluster", "") is None        # D-Ala-D-Lac
    reason = pre("ARO:X", "vanY gene in vanG cluster", "")
    assert reason and "D-Ala-D-Ser route" in reason


def test_vany_records_why_two_d_d_peptidases_are_not_redundant():
    out = _graph(promote.family_configs("ARO:3000077")[0],
                 mech=("ARO:3000213",), drug=("ARO:3000081",))
    assert "non-overlapping functions" in _flat(out)          # VanX vs VanY division of labour
    assert "17- to 67-fold higher" in _flat(out)              # the quantified preference
    assert "but not the dipeptide D-Ala-D-Ala" in _flat(out)  # the negative result


# --- round 26: rpoB, and two mechanism ids on one record --------------------------

def test_rpob_supplies_a_snippet_for_both_of_its_mechanism_ids():
    """These records carry ARO:0001002 AND ARO:3000212.

    The UncoveredMechanism guard (#203) refuses to substitute one mechanism's evidence for
    another, so both had to be written. Before that guard this round would silently have
    cited one for both.
    """
    cfg = promote.family_configs("ARO:3000210")[0]
    assert {"ARO:0001002", "ARO:3000212"} <= set(cfg["mech"])
    out = _graph(cfg, mech=("ARO:0001002", "ARO:3000212"), drug=("ARO:3000157",))
    assert "graph_id: resistance" in out


def test_rpob_records_that_the_inhibition_is_allosteric():
    """>12 Å from the active site: the drug obstructs the transcript, not the chemistry.

    That is what explains rifampicin blocking initiation rather than ongoing elongation,
    and a graph saying only "drug inhibits enzyme" would lose it.
    """
    out = _graph(promote.family_configs("ARO:3000210")[0],
                 mech=("ARO:0001002", "ARO:3000212"), drug=("ARO:3000157",))
    assert "more than 12 A away from the active site" in _flat(out)
    assert "2 to 3 nt in length" in _flat(out)


# --- round 27: katG, resistance by losing a function -------------------------------

def test_katg_causal_core_runs_backwards():
    """The determinant confers resistance by NOT doing something.

    Every earlier round's core edge is something the determinant does; katG's is a
    negative regulation BY the determinant of a step it would otherwise perform.
    """
    cfg = promote.family_configs("ARO:3004266")[0]
    core = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "peroxidase"][0]
    assert core["predicate_id"] == "RO:0002212"          # negatively regulates
    assert "cannot activate" in core["predicate"]


def test_katg_cites_both_directions_of_the_1992_experiment():
    """Gain restores sensitivity; loss confers resistance. Both, or it is correlative."""
    out = _graph(promote.family_configs("ARO:3004266")[0],
                 mech=("ARO:3000212",), drug=("ARO:3000157",))
    assert "restored sensitivity to INH" in _flat(out)
    assert "Deletion of katG from the chromosome" in _flat(out)


def test_katg_records_that_its_core_evidence_is_a_deletion():
    """Clinical katG resistance is usually a point substitution that REDUCES activity.

    A reader who took "deletion confers resistance" as the mechanism of every katG allele
    would be wrong about the commonest one, so the edge's notes say which it is.
    """
    cfg = promote.family_configs("ARO:3004266")[0]
    core = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "peroxidase"][0]
    assert "point substitutions" in core["evidence"][0]["notes"]


# --- round 28: inhA, two routes on one determinant ---------------------------------

def test_inha_carries_both_resistance_routes_as_separate_edges():
    """Target alteration AND titration by overexpression, from one 1994 paper.

    A record showing only one would misdescribe half the clinical alleles.
    """
    cfg = promote.family_configs("ARO:3003417")[0]
    alter = [e for e in cfg["extra_edges"]
             if e["subject"] == "determinant" and e["predicate_id"] == "RO:0002212"]
    over = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["predicate_id"] == "RO:0002213"]
    assert len(alter) == 1 and len(over) == 1
    out = _flat(_graph(cfg, mech=("ARO:3000212",), drug=("ARO:3007152",)))
    assert "A missense mutation within the mycobacterial inhA gene" in out
    assert "transferred on a multicopy plasmid vector" in out


def test_inha_records_that_its_inhibitor_depends_on_katg():
    """The adduct exists only because katG activated the prodrug — round 27's record."""
    cfg = promote.family_configs("ARO:3003417")[0]
    edge = [e for e in cfg["extra_edges"] if e["object"] == "inha_activity"
            and e["subject"] == "inh_nad"][0]
    assert "ARO:3004266" in edge["evidence"][0]["notes"]


# --- round 29: a determinant that is not a protein ---------------------------------

def test_an_rrna_determinant_is_not_called_a_protein():
    """105 draft records have an rRNA determinant; the node type was hardcoded (#215)."""
    cfg = promote.family_configs("ARO:3003666")[0]
    assert cfg["determinant_node_type"] == "NUCLEIC_ACID"
    out = _graph(cfg, mech=("ARO:3000212",), drug=("ARO:3000104",))
    block = out.split("- node_id: determinant", 1)[1].split("- node_id:", 1)[0]
    assert "node_type: NUCLEIC_ACID" in block


def test_the_default_determinant_node_type_is_unchanged():
    """Every earlier family must keep emitting PROTEIN."""
    out = _graph(_cfg())
    block = out.split("- node_id: determinant", 1)[1].split("- node_id:", 1)[0]
    assert "node_type: PROTEIN" in block


def test_the_16s_graph_keeps_the_eukaryotic_parallel():
    """The resistance substitution makes the bacterial site look eukaryotic.

    The same fact explains why aminoglycosides are selective AND how bacteria escape them;
    a graph recording only "substitution lowers affinity" would lose it.
    """
    out = _flat(_graph(promote.family_configs("ARO:3003666")[0],
                       mech=("ARO:3000212",), drug=("ARO:3000104",)))
    assert "an adenosine in prokaryotic ribosomes and a guanosine in eukaryotic ribosomes" in out


# --- round 30: ethA, and the isoniazid/ethionamide triangle ------------------------

def test_etha_points_at_the_shared_target_record():
    """Ethionamide and isoniazid converge on InhA, curated in round 28."""
    cfg = promote.family_configs("ARO:3003456")[0]
    out = _graph(cfg, mech=("ARO:3000212",), drug=("ARO:3007156",))
    assert "grounding: ARO:3003417" in out
    edge = [e for e in cfg["extra_edges"] if e["object"] == "inha_gene"][0]
    assert "PMID:8284673" in edge["evidence"][0]["notes"]      # where the target ID comes from


def test_etha_core_edge_records_that_the_evidence_is_the_converse():
    """Overproduction gives HYPERsensitivity; loss giving resistance is the inference.

    Not the same sentence, and a reader should see which direction was measured.
    """
    cfg = promote.family_configs("ARO:3003456")[0]
    core = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["predicate_id"] == "RO:0002212"][0]
    assert "converse" in core["evidence"][0]["notes"]


# --- round 31: target protection, and one family term with three mechanisms --------

def test_target_protection_config_takes_only_the_tetracycline_records():
    """ARO:3000185 covers ribosomal (tetracycline), RNA-polymerase (rifamycin) and EF-G
    (fusidane) protection. One config cannot describe all three."""
    pre = promote.family_configs("ARO:3000185")[0]["precondition"]
    assert pre("ARO:X", "TetM", "  grounding: ARO:3000050\n") is None
    assert pre("ARO:X", "FusB", "  grounding: ARO:3000034\n") is not None


def test_target_protection_records_the_superseded_model_too():
    """The paper's framing is a correction; citing only the new reading would hide that
    this was a live question and that the evidence is a 7.2 A structure."""
    out = _flat(_graph(promote.family_configs("ARO:3000185")[0],
                       mech=("ARO:0001003",), drug=("ARO:3000050",)))
    assert "chasing the drug from its binding site" in out
    assert "drug release is indirect" in out


def test_target_protection_uses_the_mechanism_id_the_records_carry():
    """The first draft guessed ARO:0000002; --verify reported all 193 candidates as
    uncovered, because the real id is ARO:0001003 (#203 doing its job on new work)."""
    assert "ARO:0001003" in promote.family_configs("ARO:3000185")[0]["mech"]


# --- round 32: mprF, electrostatic repulsion ---------------------------------------

def test_mprf_config_takes_only_mprf_records():
    """ArnT/PmrF, the ICR transferases and PhoP share the principle, not the chemistry."""
    pre = promote.family_configs("ARO:3003580")[0]["precondition"]
    assert pre("ARO:X", "Staphylococcus aureus mprF", "") is None
    assert pre("ARO:X", "ArnT", "") is not None


def test_mprf_uses_the_mechanism_ids_the_records_carry():
    """My first four were guesses; the guard refused all 10 records and wrote nothing."""
    mech = promote.family_configs("ARO:3003580")[0]["mech"]
    assert {"ARO:3003588", "ARO:0001001"} <= set(mech)


def test_mprf_core_edge_is_repulsion_not_destruction():
    out = _flat(_graph(promote.family_configs("ARO:3003580")[0],
                       mech=("ARO:3003588",), drug=("ARO:3000053",)))
    assert "reduced negative charge of the membrane surface" in out
    assert "no longer modifies phosphatidylglycerol with l-lysine" in out


# --- round 33: efflux, and a class that is two hops away --------------------------

def test_rnd_precondition_reads_the_complex_not_the_subunit():
    """Efflux subunits carry no pump-class ancestry; their COMPLEXES do (#223 corrected).

    subunit --part_of--> complex --is_a--> RND. Two hops, fully derivable from the release,
    which is why this is a precondition and not a hand-maintained name list.
    """
    pre = promote.family_configs("ARO:3000748")[0]["precondition"]
    assert pre("ARO:3000216", "acrB", "") is None            # part_of AcrAB-TolC, is_a RND
    assert pre("ARO:9999999", "not a pump subunit", "") is not None


def test_the_rnd_graph_says_a_subunit_is_part_of_the_pump():
    """RND resistance is a property of a three-part machine; a subunit is not the pump."""
    cfg = promote.family_configs("ARO:3000748")[0]
    edge = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "pump_complex"][0]
    assert edge["predicate_id"] == "BFO:0000050"
    out = _flat(_graph(cfg, mech=("ARO:0010000",), drug=("ARO:0000045",)))
    assert "cooperates with an outer-membrane channel, TolC" in out
    assert "allows multi-site binding" in out                # why it is a MULTIdrug pump
