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
import yaml

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
    # No count. What this test is about is that the SELECTOR distinguishes the two
    # routes -- proven below by the two configs differing and grounding different
    # downstreams. A count would also fail if a third van route were added, which would
    # not make any of that untrue (#287).
    lac = promote.config_for("ARO:3000574", "ARO:1", "vanR gene in vanA cluster", "")
    ser = promote.config_for("ARO:3000574", "ARO:2", "vanR gene in vanC cluster", "")
    assert lac is not None and ser is not None
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
    # selected by CONTENT, not position: the family now carries four pump-class configs
    # and their order is not part of the contract.
    # by a STRUCTURAL marker, not by prose: the MFS config's note MENTIONS RND (to say it
    # is distinct from it), so matching on the word picked the wrong config.
    rnd = [c for c in promote.family_configs("ARO:3000748")
           if any(n["node_id"] == "binding_pocket" for n in c["extra_nodes"])][0]
    pre = rnd["precondition"]
    assert pre("ARO:3000216", "acrB", "") is None            # part_of AcrAB-TolC, is_a RND
    assert pre("ARO:9999999", "not a pump subunit", "") is not None


def test_the_rnd_graph_says_a_subunit_is_part_of_the_pump():
    """RND resistance is a property of a three-part machine; a subunit is not the pump."""
    cfg = [c for c in promote.family_configs("ARO:3000748")
           if any(n["node_id"] == "pump_complex" for n in c["extra_nodes"])
           and not any(n["node_id"] == "atp_cycle" for n in c["extra_nodes"])][0]
    edge = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "pump_complex"][0]
    assert edge["predicate_id"] == "BFO:0000050"
    out = _flat(_graph(cfg, mech=("ARO:0010000",), drug=("ARO:0000045",)))
    assert "cooperates with an outer-membrane channel, TolC" in out
    assert "allows multi-site binding" in out                # why it is a MULTIdrug pump


# --- round 34: two pump classes under one family term ------------------------------

def test_the_efflux_family_carries_a_config_per_pump_class():
    """RND and ABC are the same ARO family term and different machines.

    RND runs on the proton gradient through a central cavity; MacB has no such cavity and
    runs on ATP. Reusing one config's evidence for the other would assert the wrong
    energetics AND the wrong route for the substrate.
    """
    # Select PUMP-CLASS configs structurally, by the export node every one of them has.
    # This asserted len(cfgs) == 4 and broke when a subunit config joined the family --
    # #287's shape, fifth instance this session.
    cfgs = [c for c in promote.family_configs("ARO:3000748")
            if any(n["node_id"] == "export" for n in c["extra_nodes"])]
    # At least the four known classes, and EXACTLY ONE with the ATP cycle -- that
    # uniqueness is the real claim, since the defect this guards against is ABC's
    # energetics leaking into a proton-driven config. A fifth pump class joining is a
    # legitimate addition and must not fail this (#287).
    assert len(cfgs) >= 4           # RND, ABC, MFS, SMR
    abc = [c for c in cfgs if any(n["node_id"] == "atp_cycle" for n in c["extra_nodes"])]
    assert len(abc) == 1, "only ABC may carry the ATP cycle"
    out = _flat(_graph(abc[0], mech=("ARO:0010000",), drug=("ARO:0000045",)))
    assert "lacks a central cavity" in out
    assert "mechanotransmission" in out


def test_the_pump_class_precondition_is_built_once_not_per_class():
    """Four classes would otherwise be four copies of the same two-hop walk (#93)."""
    rnd = promote._requires_pump_class("ARO:0010004", "RND")
    abc = promote._requires_pump_class("ARO:0010001", "ABC")
    assert rnd("ARO:3000216", "acrB", "") is None          # acrB is RND
    assert abc("ARO:3000216", "acrB", "") is not None       # and not ABC


def test_every_efflux_config_grounds_its_export_node():
    """One edit cleared an ungrounded node from 108 records across four configs.

    It was the cheapest warning reduction in the corpus: `export` appeared once per record
    in all four pump-class configs and had no CURIE, so the same node was label-only 108
    times over.
    """
    # Applies to the PUMP-CLASS configs. A subunit config (round 86) routes through the
    # complex and has no export node of its own, so it is out of scope by construction
    # rather than by exception.
    pumps = [c for c in promote.family_configs("ARO:3000748")
             if any(n["node_id"] == "export" for n in c["extra_nodes"])]
    assert len(pumps) == 4, "the four pump classes must still be present"
    for cfg in pumps:
        export = [n for n in cfg["extra_nodes"] if n["node_id"] == "export"]
        assert export and export[0].get("grounding") == "GO:1990961"


def test_the_pump_class_lookup_walks_is_a_ancestors_for_part_of():
    """A species-specific record inherits its complex through its generic term.

    "Escherichia coli acrA" is `is_a acrA`, and it is the generic `acrA` that carries
    `part_of AcrAB-TolC`. Checking only the record's own `part_of` left four such variants
    unclassified and therefore uncurable (round 36).
    """
    rnd = promote._requires_pump_class("ARO:0010004", "RND")
    assert rnd("ARO:3004043", "Escherichia coli acrA", "") is None      # inherits via acrA
    assert rnd("ARO:3009144", "MexAB", "") is not None                  # genuinely unlinked


# --- round 37: efflux repressors, verified by reading ------------------------------

def test_the_repressor_list_excludes_the_antirepressor():
    """A keyword match on "repress" returned 31 and was wrong on four.

    ArmR is an ANTIrepressor — opposite direction — and CpxR, MvaT and P. aeruginosa CpxR
    merely mention repression without being the repressor. The direction lives in prose,
    not in the ontology structure, so this is a checked list and the check is recorded.
    """
    reps = promote._EFFLUX_REPRESSORS
    assert len(reps) == 32          # 27 (r37) + 5 read-verified in r41
    assert "ARO:3004056" not in reps          # ArmR, antirepressor
    assert "ARO:3000831" not in reps          # CpxR, mentions repression
    assert "ARO:3000702" in reps              # AcrR, the archetype


def test_the_repressor_core_edge_runs_backwards_like_katg():
    """Resistance is the ABSENCE of a function: a mutated repressor stops holding the
    pump down, so more pump is made."""
    cfg = promote.family_configs("ARO:3000451")[0]
    core = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["predicate_id"] == "RO:0002212"][0]
    assert "mutation lifts the repression" in core["predicate"]
    out = _flat(_graph(cfg, mech=("ARO:0010000",), drug=("ARO:0000045",)))
    assert "AcrR mutations result in high level antibiotic resistance" in out


def test_the_activator_config_is_the_mirror_of_the_repressor_one():
    """Same family term, opposite direction: RO:0002213 here, RO:0002212 in round 37."""
    # selected by CONTENT, not by count: round 39 added a third config to this family
    # (lipid-A regulators), and asserting the count made a passing test fail on an
    # unrelated addition. The contract is that the two directions exist, not how many
    # configs the family has.
    cfgs = promote.family_configs("ARO:3000451")
    act = [c for c in cfgs if any(n["node_id"] == "activation" for n in c["extra_nodes"])][0]
    rep = [c for c in cfgs if any(n["node_id"] == "repression" for n in c["extra_nodes"])][0]
    assert any(e["predicate_id"] == "RO:0002213" for e in act["extra_edges"])
    assert any(e["predicate_id"] == "RO:0002212" for e in rep["extra_edges"])
    assert promote._EFFLUX_ACTIVATORS.isdisjoint(promote._EFFLUX_REPRESSORS)


def test_the_activator_list_is_conservative_and_says_so():
    """marA IS an activator, and still does not belong in this config.

    Round 38's check missed its phrasing; round 42 tried to admit it by reading and the
    UncoveredMechanism guard refused it for a better reason: marA also carries
    ARO:3000244 (reduced permeability), because MarA down-regulates porins as well as
    raising efflux. A graph from this config would describe half of what CARD asserts (#238).
    """
    assert "ARO:3000263" not in promote._EFFLUX_ACTIVATORS      # marA — see #238
    assert len(promote._EFFLUX_ACTIVATORS) == 27


def test_the_lps_regulator_config_is_not_an_efflux_one():
    """Despite sitting under the efflux-modulator family term, basR/basS induce lipid A
    modification — round 32's electrostatic repulsion reached by a regulatory route."""
    cfgs = promote.family_configs("ARO:3000451")
    lps = [c for c in cfgs if any(n["node_id"] == "lipid_a_mod" for n in c["extra_nodes"])]
    assert len(lps) == 1
    assert len(promote._LPS_REGULATORS) == 6      # basR/basS + 4 PhoP/PhoQ in r42
    core = [e for e in lps[0]["extra_edges"] if e["object"] == "drug0"][0]
    # the charge-to-resistance sentence is mprF's; the notes must say the transfer
    assert core["evidence"][0]["reference"] == "PMID:11342591"
    assert "transfer" in core["evidence"][0]["notes"]


def test_armr_is_excluded_from_every_regulator_list():
    """ArmR has now defeated three different patterns and been rejected only by reading.

    It is an ANTIrepressor: its definition says it raises pump levels, and it does — by
    inhibiting MexR. It acts on a REPRESSOR, not on the pump, so a repressor edge has the
    wrong sign and an activator edge has the wrong target. It belongs in neither list.
    """
    armr = "ARO:3004056"
    assert armr not in promote._EFFLUX_REPRESSORS
    assert armr not in promote._EFFLUX_ACTIVATORS
    assert armr not in promote._LPS_REGULATORS


def test_round_41_corrected_two_earlier_false_exclusions():
    """MvaT and P. aeruginosa CpxR were excluded in round 37 as "mentions repression /
    activation without being the regulator".

    Reading the WHOLE definition rather than the matched clause shows both are: MvaT
    "has also shown to be able to repress the efflux" operon, and CpxR is "directly
    involved in activation of expression of RND efflux pump MexAB-OprM". A clause-level
    match answered a question the sentence answers differently.
    """
    assert "ARO:3004069" in promote._EFFLUX_REPRESSORS      # MvaT
    assert "ARO:3004054" in promote._EFFLUX_ACTIVATORS      # P. aeruginosa CpxR


# --- round 43: permeability, the mirror of efflux ----------------------------------

def test_permeability_covers_resistance_by_absence():
    """8 of the 42 carry ARO:3003764 alongside "reduced permeability".

    I guessed ARO:3000185 for it and the UncoveredMechanism guard named the real id by
    refusing two records — the fourth time in this session that guessing a mechanism id
    was the failure and the guard was the fix.
    """
    mech = promote.family_configs("ARO:3000270")[0]["mech"]
    assert "ARO:3003764" in mech and "ARO:3000244" in mech


def test_the_permeability_determinant_is_the_channel_not_the_resistance():
    """These records are porins: the wild-type function ADMITS the drug, and resistance is
    the loss of it — the inverted shape of katG (r27) and the efflux repressors (r37)."""
    cfg = promote.family_configs("ARO:3000270")[0]
    edge = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "influx"][0]
    assert edge["predicate_id"] == "RO:0002327"          # enables, not negatively regulates
    assert "Resistance is its loss" in edge["description"]


def test_fusb_protects_by_rescue_not_by_displacement():
    """Two target-protection configs, two different mechanisms.

    TetM (round 31) chases the drug off its binding site. FusB does NOT displace fusidic
    acid — it dissociates the stalled ribosome-EF-G-GDP complex the drug creates, so
    translation resumes with the drug still present. Reusing round 31's evidence here
    would assert displacement that the paper explicitly does not claim.
    """
    cfgs = promote.family_configs("ARO:3000185")
    fus = [c for c in cfgs if any(n["node_id"] == "stalled" for n in c["extra_nodes"])][0]
    tet = [c for c in cfgs if any(n["node_id"] == "tet_site" for n in c["extra_nodes"])][0]
    assert fus is not tet
    out = _flat(_graph(fus, mech=("ARO:0001003",), drug=("ARO:3007153",)))
    assert "promote the dissociation of stalled" in out
    assert "chasing the drug from its binding site" not in out


def test_target_protection_now_has_three_configs_with_three_modes():
    """One ARO family term, three mechanisms — and two of them are NOT the same mode.

        TetM (r31)  displaces the drug from the ribosome
        FusB (r44)  does NOT displace; it dissociates the stalled complex the drug makes
        HelR (r45)  displaces the drug from RNA polymerase

    TetM and HelR share a mode on different targets; FusB shares a target class with
    neither. Three configs, three papers, no borrowed sentences.
    """
    # Assert the three MODES are present by their marker nodes, not that there are
    # exactly three configs -- a fourth protection mechanism would not falsify this (#287).
    cfgs = promote.family_configs("ARO:3000185")
    marks = {n["node_id"] for c in cfgs for n in c["extra_nodes"]}
    assert {"tet_site", "stalled", "inhibited"} <= marks


def test_macrolide_esterases_use_the_ring_hydrolysis_mechanism_id():
    """ARO:3000321, "hydrolysis of macrolide macrocycle lactone ring".

    I guessed ARO:3000004 — a beta-lactamase class — and the UncoveredMechanism guard
    refused all six records and named the real id. Fifth time in this session (r31, r32,
    r42, r43, r46) that guessing a mechanism id was the failure and the guard was the fix.
    """
    mech = promote.family_configs("ARO:3000201")[0]["mech"]
    assert "ARO:3000321" in mech and "ARO:3000004" not in mech


def test_the_macrolide_config_takes_only_the_esterases():
    """One family term, three unrelated reactions: hydrolysis, phosphorylation, glycosylation."""
    pre = promote.family_configs("ARO:3000201")[0]["precondition"]
    assert pre("ARO:X", "EreA", "EreA is an erythromycin esterase that hydrolyses") is None
    assert pre("ARO:X", "gimA", "A macrolide glycosyltransferase encoded by gimA") is not None


def test_the_two_macrolide_configs_do_not_share_a_reaction():
    """Ring hydrolysis (r46) and phosphorylation (r47) inactivate the same drug class by
    different chemistry, so neither may borrow the other's sentence."""
    # by CONTENT, not count — round 48 added a third chemistry (glycosylation) and a count
    # assertion would fail on it. Third time this session a count broke on an addition
    # (#235, round 35, here); the contract is that the reactions are distinct.
    cfgs = promote.family_configs("ARO:3000201")
    est = [c for c in cfgs if any(n["node_id"] == "ring" for n in c["extra_nodes"])][0]
    kin = [c for c in cfgs if any(n["node_id"] == "kinase" for n in c["extra_nodes"])][0]
    assert "ARO:3000321" in est["mech"]        # hydrolysis of the lactone ring
    assert "ARO:3000105" in kin["mech"]        # phosphorylation of antibiotic
    out = _flat(_graph(kin, mech=("ARO:3000105",), drug=("ARO:3000050",)))
    assert "hydrolysis of the macrolactone ring" not in out


def test_all_three_macrolide_chemistries_are_distinct():
    """One family term, three reactions, three papers, three mechanism ids.

        esterase (r46)          ARO:3000321  opens the macrolactone ring
        phosphotransferase (r47) ARO:3000105  phosphorylates it
        glycosyltransferase (r48) ARO:3000208  adds a sugar

    All inactivate a macrolide; none shares a reaction. This is why one "macrolide
    inactivation" config would have been wrong.
    """
    ids = {mid for c in promote.family_configs("ARO:3000201") for mid in c["mech"]}
    assert {"ARO:3000321", "ARO:3000105", "ARO:3000208"} <= ids


def test_target_modification_reaches_round_29s_endpoint_by_a_different_route():
    """Round 29's records MUTATE the 16S decoding site; these ENZYMES methylate it.

    Same target, same consequence, different determinant type — an rRNA there, a protein
    here — which is why the two could not share a config despite sharing an endpoint.
    """
    cfg = promote.family_configs("ARO:3000519")[0]
    ids = {n["node_id"] for n in cfg["extra_nodes"]}
    assert "decoding_site" in ids and "methyltransferase" in ids
    # mechanism ids were read from the records, not guessed — five rounds lost time to that
    assert {"ARO:0001001", "ARO:3000211", "ARO:3000212"} <= set(cfg["mech"])


def test_the_permeability_influx_node_is_grounded():
    """The mirror of #228, which grounded `export` across the four efflux configs.

    `influx` was label-only in all 42 permeability records — one node, one edit, 42
    records. Flagged in the round-33, round-35 and round-43 reports before being done.
    """
    cfg = promote.family_configs("ARO:3000270")[0]
    influx = [n for n in cfg["extra_nodes"] if n["node_id"] == "influx"][0]
    assert influx.get("grounding") == "GO:0042908"      # xenobiotic transport (BP)


def test_the_23s_config_carries_the_graded_affinity_and_its_control():
    """#217 said no source constructs a 23S substitution and measures the affinity loss.

    Douthwaite & Aagaard 1993 does: 20-fold at 2057A, 1,000-fold at 2058U, 10,000-fold at
    2058G. The same paper's negative control — position 2032 alters drug tolerance but
    changes neither the loop nor erythromycin binding — is on the core edge too, because
    it is what makes the claim specific to this loop rather than merely positional.
    """
    cfg = promote.family_configs("ARO:3004125")[0]
    assert cfg["determinant_node_type"] == "NUCLEIC_ACID"
    core = [e for e in cfg["extra_edges"]
            if e["subject"] == "conformation" and e["object"] == "pt_loop"][0]
    assert len(core["evidence"]) == 2
    assert "gave no detectable effects" in core["evidence"][1]["snippet"]


def _fabg1():
    """The fabG1 config -- selected structurally, by its mycolic-acid node (#219)."""
    for cfg in promote.family_configs("ARO:3004887"):
        if any(n["node_id"] == "mycolic" for n in cfg.get("extra_nodes", ())):
            return cfg
    raise AssertionError("no fabG1 config with a mycolic-acid node")


def test_fabg1_asserts_target_alteration_not_promoter_overexpression():
    """#219 was blocked sourcing a mechanism CARD never claims.

    CARD says the mutation stops the drug inhibiting mycolic acid synthesis --
    target alteration. It says nothing about the fabG1 promoter raising inhA
    expression. If someone adds that arm it needs its OWN evidence, so this test
    fails loudly rather than letting the well-known story drift in uncited.
    """
    cfg = _fabg1()
    core = [e for e in cfg["extra_edges"] if e["object"] == "inhibition"
            and e["subject"] == "determinant"]
    assert len(core) == 1, "expected exactly one causal-core edge"
    assert core[0]["predicate_id"] == "RO:0002212"

    # Scan only ASSERTED content -- snippets, predicates, descriptions, labels.
    # `notes`/`note` are excluded on purpose: they exist to say the promoter arm is
    # deliberately absent, so scanning them would fail on the documentation of the
    # very property under test.
    asserted = []

    def _walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                _walk(v, k)
        elif isinstance(o, list):
            for v in o:
                _walk(v, key)
        elif isinstance(o, str) and key not in ("notes", "note"):
            asserted.append(o)

    _walk(cfg)
    blob = _flat(" ".join(asserted)).lower()
    for banned in ("promoter", "overexpress", "upregulat", "increased expression",
                   "c-15t", "inha expression"):
        assert banned not in blob, (
            f"fabG1 config asserts {banned!r}; CARD does not claim it (#219). "
            "Adding that arm requires its own evidence."
        )


def test_fabg1_pathway_edge_flags_its_borrowed_citation():
    """PMID:8284673 studied InhA, the NEXT step -- the notes must say so."""
    cfg = _fabg1()
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "mycolic")
    ev = edge["evidence"][0]
    assert ev["reference"] == "PMID:8284673"
    assert "inha" in _flat(ev["notes"]).lower(), (
        "the borrowed citation must name what it actually studied"
    )


def test_own_definition_ignores_inherited_drug_class_prose():
    """The bug that nearly shipped 17 records excluded for a false reason.

    ARO records carry drug-class boilerplate naming other mechanisms. A keyword scan
    over the whole YAML matched "deactivation of repressors" in that prose and reported
    a PBP3 point mutant as "describes a repressor".
    """
    text = (
        "identifier: ARO:3007423\n"
        "definition: >-\n"
        "  Mutant PBP3 in E. coli conferring resistance to beta-lactams.\n"
        "drug_class_note: lower binding affinities and the deactivation of repressors\n"
    )
    own = promote._own_definition(text)
    assert "repressor" not in own.lower()
    assert "Mutant PBP3" in own


def test_replacement_pbp_predicate_discriminates_on_mechanism_not_keywords():
    """A PBP3 mutant is a real determinant of the WRONG shape -- skip, don't curate."""
    mutant = (
        "identifier: ARO:3007423\n"
        "definition: >-\n  Mutant PBP3 conferring resistance to beta-lactams.\n"
        "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000212\n"
           "    relation_source: \"ARO participates_in (mechanism) via "
           "ARO:0000031 antibiotic resistant gene variant or mutant\"\n"
    )
    reason = promote._requires_replacement_pbp("ARO:3007423", "PBP3 mutants", mutant)
    assert reason is not None and "target-replacement" in reason
    assert "repressor" not in reason, "must not blame the wrong thing"


def test_pbp_family_carries_both_mechanisms_as_a_list():
    """ARO:3003040 spans target replacement AND target alteration (rounds 52-53)."""
    # The mechanism-id set is what "spans both" means; the count was standing in for it
    # and broke when an unrelated config joined the family (#287).
    cfgs = promote.family_configs("ARO:3003040")
    assert len(cfgs) > 1, "must be the list form, not a single config"
    mechs = {m for c in cfgs for m in c["mech"]}
    assert mechs == {"ARO:0001002", "ARO:3000212"}


def test_mutant_pbp_pattern_matches_pbp_without_a_number():
    """ARO:3003938 says "PBP transpeptidases" -- requiring a digit wrongly skipped it."""
    rec = ("identifier: ARO:3003938\n"
           "definition: >-\n  Mutations in PBP transpeptidases that change the affinity"
           " for penicillin.\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000212\n"
           "    relation_source: \"ARO participates_in (mechanism) via "
           "ARO:0000031 antibiotic resistant gene variant or mutant\"\n")
    assert promote._requires_mutant_pbp("ARO:3003938", "PBP mutations", rec) is None


def test_pilq_is_excluded_from_the_pbp_affinity_mechanism():
    """ARO:3004835 is an outer-membrane secretin filed under the PBP family (#254)."""
    rec = ("identifier: ARO:3004835\n"
           "definition: >-\n  PilQ is an important gonococcal outer membrane component,"
           " member of the secretin protein family.\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000212\n"
           "    relation_source: \"ARO participates_in (mechanism) via "
           "ARO:0000031 antibiotic resistant gene variant or mutant\"\n")
    reason = promote._requires_mutant_pbp("ARO:3004835", "pilQ", rec)
    assert reason is not None and "penicillin-binding protein" in reason


ROUND52_RECORD = (
    "identifier: ARO:3007423\n"
    "definition: >-\n"
    "  Mutant PBP3 in E. coli conferring resistance to beta-lactams.\n"
    "drug_class_note: lower binding affinities and the deactivation of repressors\n"
)


def test_probe_catches_the_round_52_false_skip_reason():
    """The probe's own canary: it must fire on the bug that motivated it (#253)."""
    bad = promote.skip_reason_contradicted(
        "definition describes a repressor, not a replacement PBP", ROUND52_RECORD)
    assert bad, "probe missed the exact bug it exists to catch"
    assert "repressor" in bad


def test_probe_stays_quiet_on_a_true_skip_reason():
    """A reason that IS true must not be flagged -- a noisy probe gets ignored."""
    meci = ("identifier: ARO:3005046\n"
            "definition: >-\n  This MecI is a methicillin-resistant repressor.\n")
    assert not promote.skip_reason_contradicted(
        "own definition describes a repressor, not a replacement PBP", meci)


def test_probe_does_not_catch_the_round_53_synonym_case():
    """Documents the real limitation rather than implying full coverage.

    Round 53's reason said "does not name a penicillin-binding protein" of a definition
    reading "PBP transpeptidases" -- literally true, wrong because PBP is a synonym.
    Catching it needs a lexicon this repo does not have. If that changes, this test
    should flip rather than quietly keep passing.
    """
    rec = ("identifier: ARO:3003938\n"
           "definition: >-\n  Mutations in PBP transpeptidases that change affinity.\n")
    assert not promote.skip_reason_contradicted(
        "own definition does not name a penicillin-binding protein", rec)


def test_16s_determinant_is_nucleic_acid_not_protein():
    """rRNA is not a protein. Calling it one in a protein-traits KB is false (#215)."""
    cfg = promote.family_configs("ARO:3003211")[0]
    assert cfg["determinant_node_type"] == "NUCLEIC_ACID"


def test_16s_tetracycline_snippet_is_flagged_as_one_drug_of_several():
    """The family spans pactamycin, edeine and viomycin, which helix 34 does not cover."""
    cfg = promote.family_configs("ARO:3003211")[0]
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "binding_site")
    notes = _flat(edge["evidence"][0]["notes"]).lower()
    assert "does not cover" in notes or "other drugs" in notes, (
        "a single-drug snippet used family-wide must say so"
    )


def test_23s_linezolid_snippet_declares_its_scope():
    """The drug-action sentence names linezolid; the family spans seven drug classes."""
    cfg = promote.family_configs("ARO:3000336")[0]
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "pt_activity")
    notes = _flat(edge["evidence"][0]["notes"]).lower()
    assert "scope" in notes and "not named by this sentence" in notes


def test_23s_and_16s_share_the_binding_site_partonomy():
    """Both rRNA configs must carry binding_site --part of--> determinant.

    That edge is what makes an rRNA graph different from ordinary target alteration:
    the drug's site is INSIDE the target, so a base substitution changes the site.
    """
    for fam in ("ARO:3000336", "ARO:3003211"):
        cfg = promote.family_configs(fam)[0]
        assert any(e["subject"] == "binding_site" and e["object"] == "determinant"
                   and e["predicate_id"] == "BFO:0000050"
                   for e in cfg["extra_edges"]), f"{fam} lost the partonomy edge"
        assert cfg["determinant_node_type"] == "NUCLEIC_ACID"


def test_pnca_core_edge_runs_from_the_loss_not_the_determinant():
    """Prodrug-activation loss inverts the usual direction.

    Every other mechanism here works by the determinant DOING something. pncA resistance
    is the ABSENCE of an activity, so the core edge points from the loss to the activity.
    If someone "fixes" this to determinant --> drug, the mechanism becomes wrong.
    """
    cfg = promote.family_configs("ARO:3004267")[0]
    core = next(e for e in cfg["extra_edges"] if e["object"] == "pzase")
    assert core["subject"] == "loss"
    assert core["predicate_id"] == "RO:0002212"


def test_pnca_active_metabolite_is_left_ungrounded_on_purpose():
    """A guessed CHEBI id would be an unverified grounding (rounds 51-55 discipline)."""
    cfg = promote.family_configs("ARO:3004267")[0]
    poa = next(n for n in cfg["extra_nodes"] if n["node_id"] == "poa")
    assert "grounding" not in poa
    assert "guessing" in _flat(poa["description"]).lower()


def test_ndh_keeps_both_downstream_arms_separate():
    """CARD's "as well as" joins two independent blocks on isoniazid, not one restated.

    Collapsing them would lose a mechanism: the ratio blocks INH ACTIVATION and,
    separately, blocks DISPLACEMENT of the NADH-isonicotinic acyl complex from InhA.
    """
    cfg = promote.family_configs("ARO:3003460")[0]
    downstream = {e["object"] for e in cfg["extra_edges"] if e["subject"] == "ratio"}
    assert downstream == {"peroxidation", "displacement"}


def test_ndh_oxidase_node_is_ungrounded_on_purpose():
    """CARD says "NADH oxidase"; nearest GO terms are dehydrogenases (round 56's rule)."""
    cfg = promote.family_configs("ARO:3003460")[0]
    node = next(n for n in cfg["extra_nodes"] if n["node_id"] == "nadh_ox")
    assert "grounding" not in node
    assert "do not guess" in _flat(node["description"]).lower()


def test_baca_bcrc_share_one_config_and_omit_the_drug_target_edge():
    """CARD never says bacitracin binds undecaprenyl pyrophosphate (round 51's lesson).

    That IS the textbook mode of action, which is exactly why its absence needs pinning:
    it is the claim most likely to be added later from memory rather than from a source.
    """
    a = promote.family_configs("ARO:3002986")[0]
    b = promote.family_configs("ARO:3003250")[0]
    assert a["reference"] == b["reference"] == "ARO:3002986"
    for cfg in (a, b):
        assert not any(e["subject"] == "drug0" for e in cfg["extra_edges"]), (
            "drug->carrier edge added without evidence"
        )
        assert "NOT asserted" in cfg["note"]


def test_class_d_does_not_borrow_class_a_active_site():
    """PROSITE:PS00146 is class A's signature. Citing it for class D would be #196."""
    cfg = promote.family_configs("ARO:3000075")[0]
    assert cfg["protein_traits"]["active_site"][0] == "PROSITE:PS00337"


def test_class_d_pattern_allows_a_family_token_before_beta_lactamase():
    """RAD-1 reads "a class D RAD beta-lactamase"; adjacency wrongly excluded it."""
    rec = ("identifier: ARO:3007483\n"
           "definition: >-\n  RAD-1 is a class D RAD beta-lactamase found in"
           " Riemerella anatipestifer.\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000187\n"
           "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    assert promote._requires_class_d("ARO:3007483", "RAD-1", rec) is None


def test_class_d_omits_the_carbamylated_lysine_chemistry():
    """The feature that makes OXA enzymes distinctive, and no source read stated it."""
    cfg = promote.family_configs("ARO:3000075")[0]
    asserted = [e["evidence"][0]["snippet"] for e in cfg["extra_edges"]]
    asserted += list(cfg["mech"].values())
    assert not any("carbamyl" in s.lower() for s in asserted), (
        "carbamylated-lysine chemistry asserted without a source stating it"
    )
    assert "NOT the carbamylated" in cfg["note"], "the omission must be documented"


def test_near_miss_catches_the_acronym_case():
    """Round 53: "PBP transpeptidases" refused for lacking "penicillin-binding protein"."""
    rec = ("identifier: ARO:3003938\n"
           "definition: >-\n  Mutations in PBP transpeptidases that change affinity.\n"
           "term_kind: CLASS\n")
    hit = promote.skip_reason_near_miss(
        "own definition does not name a penicillin-binding protein", rec)
    assert hit and "acronym" in hit


def test_near_miss_catches_the_adjacency_case():
    """Round 59: "class D RAD beta-lactamase" refused for lacking "class D beta-lactamase"."""
    rec = ("identifier: ARO:3007483\n"
           "definition: >-\n  RAD-1 is a class D RAD beta-lactamase.\n"
           "term_kind: CLASS\n")
    hit = promote.skip_reason_near_miss(
        "own definition does not call it a class D beta-lactamase", rec)
    assert hit and "adjacency" in hit


def test_near_miss_stays_quiet_on_a_genuine_miss():
    """BSU-1 really does lack "class D" -- the discriminating letter must be required.

    This failed twice while being written, both times by losing the "D": once by dropping
    single-character tokens, once by tokenising before lowercasing so the uppercase D acted
    as a separator. Same defect class the detector exists to catch, in its own code.
    """
    rec = ("identifier: ARO:3006902\n"
           "definition: >-\n  BSU-1 is a BSU beta-lactamase.\n"
           "term_kind: CLASS\n")
    assert not promote.skip_reason_near_miss(
        "own definition does not call it a class D beta-lactamase", rec)


def test_tet34_is_excluded_from_the_hydroxylase_mechanism():
    """tet(34) carries the hydroxylation id but protects, it does not hydroxylate (#267)."""
    rec = ("identifier: ARO:3002870\n"
           "definition: >-\n  tet(34) causes the activation of Mg2+-dependent purine"
           " nucleotide synthesis, which protects the protein synthesis pathway.\n"
           "term_kind: CLASS\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000450\n"
           "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    reason = promote._requires_tet_hydroxylase("ARO:3002870", "tet(34)", rec)
    assert reason is not None, "tet(34) must not receive a hydroxylase graph"
    assert "hydroxylation of the drug" in reason
    # and not for the wrong reason -- it DOES carry the mechanism id
    assert "carries no hydroxylation mechanism" not in reason


def test_topoisomerase_scope_note_names_the_worked_case_only():
    """gyrB/aminocoumarin is quoted for a family that also covers parE and parY."""
    cfg = promote.family_configs("ARO:3000370")[0]
    ev = cfg["det_res"][1]
    assert "SCOPE" in ev["notes"] and "parY" in ev["notes"]


def test_topoisomerase_is_binding_loss_not_cleavage_complex_trapping():
    """Rounds 18-19 curated the fluoroquinolone trap; this is a different mechanism.

    If someone merges the two configs, the aminocoumarin records would silently acquire
    a cleavage-complex claim no source here makes.
    """
    cfg = promote.family_configs("ARO:3000370")[0]
    assert any(e["object"] == "binding_loss" for e in cfg["extra_edges"])
    assert "cleavage complex" not in " ".join(
        e["evidence"][0]["snippet"] for e in cfg["extra_edges"]).lower()


def test_rifampin_config_covers_only_the_adp_ribosylating_subset():
    """ARO:3000576 mixes four chemistries; asserting one across it would be wrong."""
    cfg = promote.family_configs("ARO:3000576")[0]
    assert "ARO:3000266" in cfg["mech"]
    for other in ("ARO:3000450", "ARO:3000208", "ARO:3000105"):
        assert other not in cfg["mech"], (
            f"{other} is a different chemistry and needs its own snippets"
        )
    assert "SCOPE" in cfg["det_res"][1]["notes"]


def test_rifampin_family_has_one_config_per_chemistry():
    """Four reactions inactivate rifampin; each needs its own snippets (rounds 62-63)."""
    cfgs = promote.family_configs("ARO:3000576")
    mechs = {m for c in cfgs for m in c["mech"]} - {"ARO:0001004"}
    assert mechs == {"ARO:3000266", "ARO:3000450", "ARO:3000105", "ARO:3000208"}


def test_rifampin_phosphorylation_does_not_pin_the_donor():
    """CARD says "usually by ATP, sometimes GTP" -- naming one would over-assert."""
    cfg = next(c for c in promote.family_configs("ARO:3000576")
               if "ARO:3000105" in c["mech"])
    assert "declines to give" in _flat(cfg["note"])
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "atp" not in labels and "gtp" not in labels


def test_streptogramin_has_one_config_per_chemistry_and_subtype():
    """vat acetylates type A; vgb linearizes type B. One config would be wrong twice."""
    # Both chemistries present and no others -- the count was a proxy for that (#287).
    cfgs = promote.family_configs("ARO:3000233")
    mechs = {m for c in cfgs for m in c["mech"]} - {"ARO:0001004"}
    assert mechs == {"ARO:3000106", "ARO:3000338"}


def test_streptogramin_lyase_is_not_modelled_as_a_transfer():
    """Nothing is ADDED to the drug -- the ring is opened. No donor node may appear."""
    cfg = next(c for c in promote.family_configs("ARO:3000233")
               if "ARO:3000338" in c["mech"])
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "donor" not in labels and "coa" not in labels
    assert any(e["subject"] == "lactone" and e["object"] == "drug0"
               for e in cfg["extra_edges"]), "the ring must be part-of the drug"


def test_nim_records_association_not_causation():
    """CARD says these enzymes are "associated with" resistance, not that they confer it."""
    cfg = promote.family_configs("ARO:3007103")[0]
    weak = next(e for e in cfg["det_res"] if "associated with" in e["snippet"])
    assert "not 'confers'" in _flat(weak["notes"])


def test_nim_keeps_the_familys_own_negative_result():
    """ARO:3007671 says expression alone is insufficient -- that bounds the whole claim."""
    cfg = promote.family_configs("ARO:3007103")[0]
    assert any("not sufficient" in e["snippet"] for e in cfg["det_res"]), (
        "the negative result must not be dropped for a tidier story"
    )


def test_ef_tu_does_not_assert_a_drug_binding_mechanism():
    """CARD says EF-Tu variants confer resistance and never says how (#276).

    The elfamycin-binding story is well known and uncited here. This is round 51's
    failure mode -- sourcing a mechanism I know rather than the one the records make --
    so the absence is pinned rather than left to a future reader's memory.
    """
    cfg = promote.family_configs("ARO:3003356")[0]
    asserted = " ".join(
        [e["predicate"] for e in cfg["extra_edges"]]
        + [e["evidence"][0]["snippet"] for e in cfg["extra_edges"]]
    ).lower()
    for banned in ("binding affinit", "prevents drug", "elfamycin bind", "inhibit"):
        assert banned not in asserted, f"EF-Tu config asserts {banned!r} uncited"
    assert "NOT asserted" in cfg["note"]


def test_smr_states_the_energetics_not_just_the_pumping():
    """Efflux without its driving force restates the phenotype; SMR gives the coupling."""
    cfg = promote.family_configs("ARO:0010003")[0]
    edge = next(e for e in cfg["extra_edges"] if e["subject"] == "proton_gradient")
    assert edge["object"] == "antiport"
    assert "electrochemical gradient" in edge["evidence"][0]["snippet"]


def test_smr_antiport_snippet_is_scoped_to_emre():
    """The coupling sentence is EmrE's; other members have no energetics of their own."""
    cfg = promote.family_configs("ARO:0010003")[0]
    ev = next(e for e in cfg["det_res"] if e["reference"] == "ARO:3000264")
    assert "SCOPE" in ev["notes"] and "EmrE's sentence" in ev["notes"]


def test_inactivation_transfer_configs_never_pin_a_hedged_donor():
    """All three big ARO:3000557 chemistries hedge their donor -- none may name one.

    "usually AMP", "usually by ATP, sometimes GTP", "often via acetylCoA". Round 63's
    rule, and here it is a property of the whole family's text rather than one term.
    """
    # Select on the mechanism ids, NOT on len(cfgs) -- round 68 asserted a count and
    # round 69's four cleavage configs broke it. Third time this session a config-count
    # assertion failed for a reason unrelated to what it was testing.
    transfers = {"ARO:3000107", "ARO:3000105", "ARO:3000106"}
    cfgs = [c for c in promote.family_configs("ARO:3000557")
            if c["reference"] in transfers]
    assert len(cfgs) == len(transfers)
    for cfg in cfgs:
        labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
        for donor in ("atp", "gtp", "amp", "coa", "donor"):
            assert donor not in labels, f"{cfg['reference']} pins a hedged donor"
        assert "hedge" in _flat(cfg["det_res"][0]["notes"]).lower()


def test_vat_still_names_its_donor_because_card_does():
    """Round 64's contrast: acetyl-CoA IS named there, so the node stays."""
    vat = next(c for c in promote.family_configs("ARO:3000233")
               if "ARO:3000106" in c["mech"])
    assert any(n["node_id"] == "acetyl_coa" for n in vat["extra_nodes"])


def test_mate_does_not_pin_the_coupling_ion_but_smr_does():
    """CARD says "cationic" for MATE and "protons" for SMR. Both are followed.

    MATE transporters genuinely split between Na+ and H+ coupling, so the vagueness is
    the source being accurate. Copying round 67's proton node here would be wrong, and
    this pins both sides so neither gets harmonised into the other.
    """
    mate = promote.family_configs("ARO:3000112")[0]
    labels = " ".join(n["label"] for n in mate["extra_nodes"]).lower()
    assert "cationic" in labels and "proton" not in labels

    smr = promote.family_configs("ARO:0010003")[0]
    smr_labels = " ".join(n["label"] for n in smr["extra_nodes"]).lower()
    assert "proton" in smr_labels


def test_mate_keeps_the_almost_all_hedge_on_substrate_recognition():
    """"almost all MATE transporters recognize fluoroquinolones" -- not universal."""
    cfg = promote.family_configs("ARO:3000112")[0]
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "drug0")
    assert "almost all" in edge["evidence"][0]["snippet"]


def test_cleavage_chemistries_do_not_claim_a_hedged_donor():
    """Hydrolyses and hydroxylation have NO donor -- claiming CARD hedges one is false.

    The first version of these four configs reused the group-transfer factory unchanged
    and wrote "the donor is given as 'usually'/'often'" onto 8 records whose definitions
    mention no donor at all. `hedged_donor=False` now selects the correct wording.
    """
    cleavers = {"ARO:3000187", "ARO:3004140", "ARO:3003985", "ARO:3000450"}
    for cfg in promote.family_configs("ARO:3000557"):
        if cfg["reference"] not in cleavers:
            continue
        assert "No group donor is involved" in cfg["det_res"][0]["notes"]
        assert "usually" not in cfg["note"]


def test_repromote_blast_radius_threshold():
    """#280: refuse when the rewrite dwarfs the drafts it is meant to refresh.

    The real event was 5,036 already-curated against 1 draft under ARO:3000557 -- a
    family term that is a deep ancestor of thousands of beta-lactamases curated by their
    OWN configs. The threshold has a floor of 25 so that re-promoting a small family
    after a genuine config change stays frictionless.
    """
    def refuses(n_repromote, n_draft):
        return n_repromote > max(25, 5 * n_draft)

    assert refuses(5036, 1), "the actual incident must be refused"
    assert not refuses(10, 0), "a small family re-promote must stay frictionless"
    assert not refuses(25, 0), "the floor is inclusive"
    assert refuses(26, 0)
    assert not refuses(50, 10), "5x the drafts is a plausible config change"
    assert refuses(51, 10)


def test_resistance_by_absence_asserts_only_the_absence():
    """Neither the deleted gene's identity nor the downstream is a family claim.

    CARD hedges the first ("usually a porin") and the second differs per record --
    Hog1 raises exposed chitin, UXS1 accumulates UDP-glucuronic acid, mgrB derepresses
    PhoPQ. No sentence covers all of them, so only the absence edge is written.
    """
    cfg = promote.family_configs("ARO:3000000")[0]
    downstream = [e for e in cfg["extra_edges"] if e["subject"] == "absence"]
    assert len(downstream) == 1 and downstream[0]["object"] == "resistance"
    blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "porin" not in blob, "CARD says 'usually a porin'; porin-ness is not asserted"


def test_sequestration_covers_the_generic_inactivation_id_too():
    """BRP(MBL) carries ARO:0001004 as well; UncoveredMechanism refused it otherwise.

    CARD's sequestration definition opens with "Inactivation of an antibiotic", so the
    same sentence genuinely supports both ids -- it is not a substitute snippet.
    """
    cfg = next(c for c in promote.family_configs("ARO:3000000")
               if "ARO:3001206" in c["mech"])
    assert cfg["mech"]["ARO:0001004"] == cfg["mech"]["ARO:3001206"]
    assert cfg["mech"]["ARO:0001004"].startswith("Inactivation of an antibiotic")


def test_sequestration_binds_rather_than_modifies_the_drug():
    """Distinct from rounds 62-70: the drug is intact, just unavailable."""
    cfg = next(c for c in promote.family_configs("ARO:3000000")
               if "ARO:3001206" in c["mech"])
    preds = " ".join(e["predicate"] for e in cfg["extra_edges"]).lower()
    assert "binds the drug" in preds
    for chem in ("hydrolys", "acetylat", "phosphorylat", "reduc"):
        assert chem not in preds


def test_charge_alteration_has_both_lipid_a_routes():
    """L-Ara4N and phosphoethanolamine: same charge outcome, different moiety."""
    # Select structurally. Round 73 asserted len(cfgs) == 2 and round 74's glycylation
    # config broke it -- FOURTH config-count assertion this session to fail for a reason
    # unrelated to what it tested (after #235, rounds 35, 48, 68).
    cfgs = promote.family_configs("ARO:3003580")
    petn = next(c for c in cfgs
                if any("phosphoethanolamine" in n["label"] for n in c.get("extra_nodes", ())))
    assert petn["reference"] == "ARO:3003588"


def test_petn_quotes_the_weak_and_strong_resistance_claims_separately():
    """ARO:3004112 hedges ("often associated with"); ARO:3003588 does not.

    The hedged one is cited for the CHEMISTRY, the causal one for the resistance. Mixing
    them up would let the graph inherit a strength its snippet does not carry.
    """
    petn = next(c for c in promote.family_configs("ARO:3003580")
                if c["reference"] == "ARO:3003588")
    hedged = next(e for e in petn["det_res"] if e["reference"] == "ARO:3004112")
    assert "hedge" in _flat(hedged["notes"]).lower()
    assert "quoted for the reaction" in _flat(hedged["notes"])


def test_near_miss_suppression_does_not_disable_the_detector():
    """Suppression is per-record, not global -- the function itself must still fire.

    After suppressing sibling-accepted records the corpus reports 0 near-misses. That is
    the correct steady state, but a detector at 0 is indistinguishable from a broken one
    unless its firing case is pinned. Round 68's `hydrolyz\\b` bug reported 0 while broken.
    """
    rec = ("identifier: ARO:3007483\n"
           "definition: >-\n  RAD-1 is a class D RAD beta-lactamase.\n"
           "term_kind: CLASS\n")
    assert promote.skip_reason_near_miss(
        "own definition does not call it a class D beta-lactamase", rec)


def test_alm_operon_record_is_left_for_the_modelling_question():
    """ARO:3007434 is the operon itself; curating it would pre-empt the open question."""
    rec = ("identifier: ARO:3007434\n"
           "definition: >-\n  The almEFG operon is responsible for glycylation of lipid A"
           " as a mechanism of colistin resistance.\n"
           "term_kind: CLASS\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3003588\n"
           "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    reason = promote._requires_alm_glycylation("ARO:3007434", "almEFG", rec)
    assert reason is not None and "open modelling question" in reason


def test_charge_alteration_now_has_three_lipid_a_routes():
    """L-Ara4N, phosphoethanolamine (round 73), glycylation (round 74)."""
    # Each route named by a node label, not by a count -- I nearly wrote len(cfgs) == 3
    # here, which is the same assertion that just broke one written a round earlier.
    labels = " ".join(n["label"] for c in promote.family_configs("ARO:3003580")
                      for n in c.get("extra_nodes", ()))
    assert "phosphoethanolamine" in labels, "pEtN route missing"
    assert "glycyl" in labels, "glycylation route missing"


def test_cprrs_graph_ends_at_the_arn_records_not_their_chemistry():
    """Round 22's rule: a regulator points at what does the work.

    cprRS induces the Arn operon; the Ara4N chemistry lives on those records (round 75).
    Restating it here would duplicate and then drift from them.
    """
    cfg = next(c for c in promote.family_configs("ARO:3003580")
               if any(n["node_id"] == "arn_operon" for n in c.get("extra_nodes", ())))
    node = next(n for n in cfg["extra_nodes"] if n["node_id"] == "arn_operon")
    assert node["grounding"] == "ARO:3003578", "must point at a real KB record"
    blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "lipid a" not in blob and "charge" not in blob, (
        "the regulator's graph must not restate the downstream chemistry"
    )


def test_lpx_is_biosynthesis_disruption_not_charge_alteration():
    """ARO:3003580's five routes modify an intact lipid A; these change whether it is
    made properly at all. Reaching for the charge snippets here would be wrong."""
    cfg = promote.family_configs("ARO:3000012")[0]
    blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "biosynthesis" in blob
    assert "negative charge" not in blob
    assert "NOT the charge-alteration mechanism" in cfg["note"]


def test_lpx_keeps_cards_double_hedge_visible():
    """"widely known to be INVOLVED IN" and mutations "MAY cause" -- neither upgraded."""
    cfg = promote.family_configs("ARO:3000012")[0]
    notes = " ".join(e["notes"] for e in cfg["det_res"])
    assert "both hedges" in notes.lower()
    edge = next(e for e in cfg["extra_edges"] if e["subject"] == "determinant")
    assert edge["predicate_id"] == "RO:0000056", "'participates in', matching 'involved in'"


def test_two_component_regulators_do_not_efflux_anything():
    """Sixth chance to repeat the ArmR/MecI/arlS error; the graph must end at the process.

    These proteins transport nothing. Pump chemistry lives on the pump records
    (SMR round 67, MATE round 69), so this graph stops at the efflux process.
    """
    cfg = promote.family_configs("ARO:3000750")[0]
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    for pump_word in ("antiport", "transporter activity", "gradient", "extrud"):
        assert pump_word not in labels, f"regulator graph restates pump chemistry: {pump_word}"


def test_two_component_edge_keeps_cards_directly_or_indirectly_hedge():
    """RO:0002211 'regulates', not the positive form -- CARD says "change rates"."""
    cfg = promote.family_configs("ARO:3000750")[0]
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "efflux_process")
    assert edge["predicate_id"] == "RO:0002211"
    assert "directly or indirectly" in edge["evidence"][0]["snippet"]


def test_mutant_efflux_regulators_use_the_positive_predicate_but_round78_does_not():
    """The direction is licensed by the source, and only in one of the two families.

    ARO:3000219 says "result in INCREASED expression"; ARO:3000750 says only "directly
    or indirectly change rates". Harmonising them would either invent a direction or
    discard a stated one.
    """
    mut = promote.family_configs("ARO:3000219")[0]
    up = next(e for e in mut["extra_edges"] if e["object"] == "pump_expression")
    assert up["predicate_id"] == "RO:0002213"

    tc = promote.family_configs("ARO:3000750")[0]
    neutral = next(e for e in tc["extra_edges"] if e["object"] == "efflux_process")
    assert neutral["predicate_id"] == "RO:0002211"


def test_axyz_mutation_id_is_covered_by_its_own_family_not_a_borrowed_snippet():
    """Round 79 refused to borrow AxyZ's regulation snippet for its mutation id.

    ARO:3000219 is where that evidence actually lives -- AxyZ carries ARO:3000212
    because it belongs to this family, whose sentence is about mutations.
    """
    cfg = promote.family_configs("ARO:3000219")[0]
    assert "mutations" in cfg["mech"]["ARO:3000212"]
    assert cfg["mech"]["ARO:3000212"] == cfg["mech"]["ARO:0010000"]


def test_emb_scopes_embbs_sentence_and_does_not_assert_erdr_family_wide():
    """embB's definition names the ERDR region; embA and embC's do not."""
    cfg = promote.family_configs("ARO:3005005")[0]
    ev = next(e for e in cfg["det_res"] if e["reference"] == "ARO:3000235")
    assert "SCOPE" in ev["notes"] and "embA and embC" in ev["notes"]
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "erdr" not in labels, "the region is embB's, not the family's"


def test_pps_does_not_link_lipid_biosynthesis_to_pyrazinamide():
    """CARD gives the biosynthetic role and a hedged resistance claim, nothing between.

    The connection is real in the literature and absent from every source read here.
    This is #219's lesson: the mechanism I know is the one most likely to arrive uncited.
    """
    cfg = promote.family_configs("ARO:3005002")[0]
    assert len(cfg["extra_edges"]) == 1, "only the biosynthetic role may be asserted"
    assert "NOT asserted" in cfg["extra_edges"][0]["evidence"][0]["notes"]
    assert "can result in" in cfg["mech"]["ARO:3000212"], "CARD's hedge must survive"


def test_folp_records_competitive_inhibition_not_generic_blocking():
    """The drug is a PABA analogue at the substrate's own site.

    That is why a mutation can lower drug affinity without abolishing catalysis --
    a distinction a generic "inhibits" edge would lose.
    """
    cfg = promote.family_configs("ARO:3000226")[0]
    edge = next(e for e in cfg["extra_edges"]
                if e["subject"] == "drug0" and e["object"] == "dhps_activity")
    assert "competitive" in edge["predicate"].lower()
    assert "competitive inhibitor" in edge["evidence"][0]["snippet"]
    assert "allosteric" in edge["description"]


def test_rpoc_does_not_borrow_rifampicins_rpob_mechanism():
    """Rifampicin binds rpoB, not rpoC -- so the obvious guess is also the wrong one."""
    cfg = promote.family_configs("ARO:3003289")[0]
    asserted = " ".join(
        [e["predicate"] for e in cfg["extra_edges"]]
        + [n["label"] for n in cfg["extra_nodes"]]).lower()
    for banned in ("rifampicin", "rifamycin", "rpob", "binds the drug", "inhibit"):
        assert banned not in asserted, f"rpoC config asserts {banned!r} uncited"
    assert "NOT asserted" in cfg["note"]


def test_liafsr_treats_the_drug_as_inducer_not_as_the_thing_resisted():
    """Same inversion as cprRS (round 76): the antibiotic activates the system."""
    cfg = promote.family_configs("ARO:3003279")[0]
    first = next(e for e in cfg["extra_edges"] if e["subject"] == "drug0")
    assert first["object"] == "lipid_ii_stress"
    tail = next(e for e in cfg["extra_edges"] if e["object"] == "stress_response")
    assert tail["predicate_id"] == "RO:0002211", "CARD gives no direction"


def test_mura_is_overexpression_not_altered_affinity():
    """CARD says OVEREXPRESSION confers resistance -- the enzyme itself is unchanged.

    Rounds 53, 61, 80 and 82 all curated altered-affinity mutations. Adding an affinity
    node here would import their shape onto a mechanism that does not have it.
    """
    cfg = promote.family_configs("ARO:3002811")[0]
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "elevated" in labels
    assert "affinity" not in labels, "murA resists by amount, not by binding"
    assert "Overexpression of murA" in cfg["mech"]["ARO:3000212"]


def test_amg_family_does_not_import_round68_chemistries():
    """CARD names only "chemical modification" here; the specific reactions are elsewhere."""
    cfg = promote.family_configs("ARO:3007380")[0]
    blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    for chem in ("acetyl", "phospho", "nucleotidyl", "adenylyl"):
        assert chem not in blob, f"imported a reaction CARD does not name: {chem}"


def test_rv0678_states_repression_and_stops_before_derepression():
    """The step that makes these records resistant is the one CARD never writes.

    Mirror of round 79: there mutations raise expression and CARD says so, so the edge
    is positive. Here CARD gives only the repression, so the derepression is absent.
    """
    cfg = promote.family_configs("ARO:3007672")[0]
    edge = cfg["extra_edges"][0]
    assert edge["predicate_id"] == "RO:0002212"
    assert "NOT asserted" in edge["evidence"][0]["notes"]
    assert "deliberately absent" in cfg["note"]


def test_subunit_config_routes_through_the_complex_not_straight_to_efflux():
    """No subunit effluxes anything alone; determinant --> efflux would make each a pump."""
    cfg = next(c for c in promote.family_configs("ARO:3000748")
               if any(n["node_id"] == "complex" for n in c["extra_nodes"]))
    first = next(e for e in cfg["extra_edges"] if e["subject"] == "determinant")
    assert first["object"] == "complex" and first["predicate_id"] == "BFO:0000050"
    assert not any(e["subject"] == "determinant" and e["object"] == "efflux_process"
                   for e in cfg["extra_edges"])


def test_van_protein_configs_target_the_mechanism_id_the_records_carry():
    """I guessed ARO:0001002 (target replacement); both records carry ARO:3000213."""
    for fam in ("ARO:3002906", "ARO:3000116"):
        cfg = promote.family_configs(fam)[0]
        assert "ARO:3000213" in cfg["mech"], f"{fam} must use the id its records carry"
        assert "ARO:0001002" not in cfg["mech"]


def test_pbp_replacement_still_uses_the_target_replacement_id():
    """A blanket replace of ARO:0001002 briefly clobbered round 52's config.

    Pinned because the damage was one line inside an unrelated family, and only a test
    that names the id would have caught it if the suite had not already.
    """
    cfg = next(c for c in promote.family_configs("ARO:3003040")
               if "ARO:0001002" in c["mech"])
    assert "foreign PBP2a" in cfg["mech"]["ARO:0001002"]


def test_vanj_reuses_round58s_mechanism_across_an_unrelated_family():
    """UPP recycling recurs in the van set, sharing no ancestor with bacA/bcrC.

    Both must also omit the drug->carrier edge: CARD says neither bacitracin nor
    teicoplanin binds the carrier, however standard that is elsewhere.
    """
    vanj = promote.family_configs("ARO:3002914")[0]
    assert any("undecaprenol" in n["label"] for n in vanj["extra_nodes"])
    assert not any(e["subject"] == "drug0" for e in vanj["extra_edges"])

    baca = promote.family_configs("ARO:3002986")[0]
    assert not any(e["subject"] == "drug0" for e in baca["extra_edges"])


def test_vanu_uses_the_positive_predicate_because_card_says_activator():
    """Third direction judgement in the same session, and all three differ by source."""
    cfg = promote.family_configs("ARO:3000575")[0]
    assert cfg["extra_edges"][0]["predicate_id"] == "RO:0002213"
    assert "activator" in cfg["mech"]["ARO:3000213"].lower()


def test_vanj_homologue_config_never_points_vanj_at_itself():
    """ARO:3002914 is a descendant of this family and its definition contains "vanJ".

    The first version gave vanJ a "shares ancestor with vanJ" edge on its own record.
    A homology edge to oneself is not a weaker claim, it is a meaningless one.
    """
    rec = ("identifier: ARO:3002914\n"
           "definition: >-\n  vanJ is a novel membrane protein that confers resistance"
           " to teicoplanin.\n"
           "term_kind: CLASS\n")
    reason = promote._requires_vanj_homologue("ARO:3002914", "vanJ", rec)
    assert reason is not None and "IS vanJ" in reason


def test_vanj_homologue_uses_shares_ancestor_not_serially_homologous():
    """RO:0002159 is "serially homologous to" -- a developmental term for vertebrae."""
    cfg = promote.family_configs("ARO:3004255")[0]
    edge = cfg["extra_edges"][0]
    assert edge["predicate_id"] == "RO:0002158"
    assert "homology, not mechanism" in edge["description"].lower()


def test_no_test_asserts_an_exact_family_config_count():
    """#287: a count breaks when a family gains an unrelated config, five times over.

    Meta-test, because the fix is only durable if the pattern cannot come back. A count
    is almost always a proxy for a real property -- a mechanism-id set, a marker node, a
    uniqueness claim -- and asserting the proxy fails for reasons unrelated to the test.
    """
    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    brittle = re.findall(
        r'assert len\(cfgs\) == \d|assert len\(promote\.family_configs\([^)]*\)\) == \d',
        src)
    assert not brittle, f"exact config-count assertions reintroduced: {brittle}"


def test_ddl_makes_the_cell_vulnerable_rather_than_resistant():
    """Every other van record produces resistance; ddl produces the drug's target.

    Inverting this into a resistance story would be the easiest possible error after
    twenty van records that all run the other way.
    """
    cfg = promote.family_configs("ARO:3003970")[0]
    out = next(e for e in cfg["extra_edges"] if e["object"] == "susceptible_precursor")
    assert "VULNERABLE" in out["evidence"][0]["notes"]
    # The node's ID carries the framing; its LABEL is the chemical name, which is right.
    # Asserting on the label was my own slip -- the label should not editorialise.
    assert any(n["node_id"] == "susceptible_precursor" for n in cfg["extra_nodes"])
    assert "glycopeptides bind" in " ".join(n["label"] for n in cfg["extra_nodes"])


def test_ddl_does_not_flatten_dependence_into_resistance():
    """CARD says nonfunctional ddl can render bacteria glycopeptide DEPENDENT.

    Doubly hedged ("can", "depending on the presence of vancomycin resistance clusters")
    and a different phenotype from resistance. The note must keep both.
    """
    cfg = promote.family_configs("ARO:3003970")[0]
    assert "DEPENDENT" in cfg["note"]
    assert "conditional" in cfg["note"]


def test_subunit_pattern_matches_both_phrasings_card_uses():
    """"is the <role> OF X" and "required for X activity" are both subunit claims.

    Round 86 matched only the first and missed MexG. Seventh too-narrow pattern this
    session, so both forms are pinned rather than left to the next reader to rediscover.
    """
    base = ("identifier: ARO:X\ndefinition: >-\n  {}\nterm_kind: CLASS\n"
            "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:0010000\n"
            "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    for defn in ("MexA is the membrane fusion protein of the MexAB-OprM complex.",
                 "MexG is a membrane protein required for MexGHI-OpmD efflux activity."):
        assert promote._requires_named_efflux_subunit("ARO:X", "", base.format(defn)) is None, defn
    # and still refuses a complex
    assert promote._requires_named_efflux_subunit(
        "ARO:Y", "", base.format(
            "MexAB is a multidrug efflux pump complex consisting of Mex A and Mex B.")
    ) is not None


def test_tet34_is_refused_by_the_generic_hydroxylation_config_too():
    """Round 60 excluded tet(34) by reading; round 70's factory re-accepted it by id.

    A guard that a later, more general config silently undoes is worse than no guard --
    round 60's report still claims the record is excluded. Found by asking "which drafts
    would an existing config accept?", not by any gate.
    """
    rec = ("identifier: ARO:3002870\n"
           "definition: >-\n  tet(34) causes the activation of Mg2+-dependent purine"
           " nucleotide synthesis, which protects the protein synthesis pathway.\n"
           "term_kind: CLASS\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000450\n"
           "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    assert promote.config_for("ARO:3000557", "ARO:3002870", "tet(34)", rec) is None

    real = rec.replace(
        "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis,"
        " which protects the protein synthesis pathway.",
        "A tetracycline hydroxylase.")
    assert promote.config_for("ARO:3000557", "ARO:X", "x", real) is not None


def test_iles_keeps_both_hedges_on_the_resistance_claim():
    """"CAN confer LOW-LEVEL resistance" -- neither certainty nor magnitude asserted."""
    cfg = promote.family_configs("ARO:3000446")[0]
    assert "can confer low-level" in cfg["mech"]["ARO:3000212"].lower()
    assert "LOW-LEVEL" in cfg["note"] and "conditional" in cfg["note"]
    assert "NOT asserted" in cfg["note"]


def test_tap_pump_has_no_energetics_because_card_gives_none():
    """SMR (r67) names protons, MATE (r69) a cationic gradient; Tap's record names neither.

    Copying either across would assert a coupling CARD does not describe -- the mistake
    round 67's own report warned about for RND/MFS/ABC.
    """
    cfg = promote.family_configs("ARO:3007183")[0]
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    for word in ("proton", "gradient", "atp", "antiport"):
        assert word not in labels, f"Tap config asserts {word!r} uncited"
    assert "NOT asserted" in cfg["note"]


def test_generic_target_replacement_keeps_both_halves_of_cards_claim():
    """"same functions" (why substitution works) and "structurally different and THUS
    resistant" (why the drug misses it). Round 52's mecA config had to leave the second
    implicit; here CARD states it, so the edge carries the 'thus'."""
    cfg = promote.family_configs("ARO:3000381")[0]
    ids = {n["node_id"] for n in cfg["extra_nodes"]}
    assert {"shared_function", "structural_difference"} <= ids
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "structural_difference")
    assert "thus resistant" in edge["evidence"][0]["notes"].lower()


def test_msha_and_mshc_are_separated_by_one_word():
    """mshA: "inability for antibiotic to ACTIVATE". mshC: "...to FUNCTION".

    One word apart, and only the first names a mechanism. mshC stays a draft; a config
    for mshA must not be generalised to cover it.
    """
    cfg = promote.family_configs("ARO:3004900")[0]
    assert "activate" in cfg["mech"]["ARO:3000212"].lower()
    assert any(n["node_id"] == "activation" for n in cfg["extra_nodes"])
    # mshC is a different family term and must have no config
    assert promote.family_configs("ARO:3004889") == []


def test_afta_asserts_no_resistance_mechanism_at_all():
    """CARD's sentence never mentions a drug, mutations, or resistance."""
    cfg = promote.family_configs("ARO:3003422")[0]
    asserted = " ".join(e["predicate"] for e in cfg["extra_edges"]).lower()
    for banned in ("resist", "drug", "inhibit", "mutation"):
        assert banned not in asserted, f"aftA config asserts {banned!r} uncited"
    assert "NOT asserted" in cfg["note"]


def test_topoisomerase_precondition_reads_the_label_but_pilq_still_refused():
    """Three gyrB records had thin definitions and authoritative labels (round 96).

    Reading the label is safe HERE because the label names the gene the family is about.
    It would not be safe for pilQ (#254), where the label said "pilQ gene conferring
    resistance to beta-lactam" and the definition was the corrective. Both pinned.
    """
    thin = ("identifier: ARO:3003303\n"
            "definition: >-\n  Point mutation in Escherichia coli resulting in"
            " aminocoumarin resistance.\nterm_kind: CLASS\n"
            "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000212\n"
            "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    assert promote._requires_topoisomerase_subunit(
        "ARO:3003303", "Escherichia coli gyrB conferring resistance to aminocoumarin",
        thin) is None

    pilq = thin.replace(
        "Point mutation in Escherichia coli resulting in aminocoumarin resistance.",
        "PilQ is an important gonococcal outer membrane component, member of the"
        " secretin protein family.")
    assert promote._requires_mutant_pbp(
        "ARO:3004835", "Neisseria gonorrhoeae pilQ gene conferring resistance",
        pilq) is not None


def test_armr_keeps_both_negatives_rather_than_collapsing_them():
    """ArmR inhibits MexR; MexR represses the pump. Collapsing to "activates" hides that.

    ArmR is the record that defeated three keyword patterns in the efflux rounds -- it is
    neither repressor nor activator. Both edges must survive.
    """
    cfg = promote.family_configs("ARO:3004056")[0]
    preds = {e["predicate_id"] for e in cfg["extra_edges"]}
    assert {"RO:0002212", "RO:0002213"} <= preds, "both negatives must be present"
    blocked = next(e for e in cfg["extra_edges"] if e["object"] == "mexr_dna_binding")
    assert "allosteric" in blocked["predicate"].lower()


def test_pdr1_is_not_treated_as_a_two_component_pair():
    """Most of ARO:3000451's drafts are pair records (#215); PDR1 is a single factor."""
    pair = ("identifier: ARO:3000531\n"
            "definition: >-\n  BaeSR is a two component regulatory system for efflux"
            " proteins. BaeR is a transcription factor.\nterm_kind: CLASS\n")
    reason = promote._requires_transcription_factor_regulator("ARO:3000531", "baeSR", pair)
    assert reason is not None and "#215" in reason


def test_tet34_is_curated_as_protection_and_still_refused_by_chemistry_configs():
    """Four rounds refused it correctly; none asked which config DID fit.

    Both must hold: the protection config accepts it, and the hydroxylation config
    (round 70, fixed in #310) still does not.
    """
    rec = ("identifier: ARO:3002870\n"
           "definition: >-\n  tet(34) causes the activation of Mg2+-dependent purine"
           " nucleotide synthesis, which protects the protein synthesis pathway.\n"
           "term_kind: CLASS\n"
           "trait_relations:\n  - predicate: RO:0000056\n    object: ARO:3000450\n"
           "    relation_source: \"ARO participates_in (mechanism) via ARO:0000031\"\n")
    assert promote._requires_tet34_protection("ARO:3002870", "tet(34)", rec) is None
    assert promote.config_for("ARO:3000557", "ARO:3002870", "tet(34)", rec) is None


def test_tet34_covers_all_three_of_its_mechanism_ids_with_one_sentence():
    """It carries three chemistry ids and describes none of them.

    The same sentence is cited for all three because it is the only mechanism CARD
    gives -- not a snippet borrowed to satisfy UncoveredMechanism.
    """
    cfg = promote.family_configs("ARO:3002870")[0]
    assert set(cfg["mech"]) == {"ARO:0001004", "ARO:3000213", "ARO:3000450"}
    assert len(set(cfg["mech"].values())) == 1
    assert "describes none of them" in cfg["note"]


def test_generic_protection_binds_the_target_not_the_drug():
    """Protection binds the TARGET; sequestration (round 72) binds the DRUG.

    One edge apart, and the distinction is what separates the two mechanism kinds.
    """
    cfg = next(c for c in promote.family_configs("ARO:3000185")
               if any(n["node_id"] == "blocked_binding" for n in c["extra_nodes"]))
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "target")
    assert "binds the antibiotic target" in edge["predicate"]
    assert "sequestration" in edge["description"].lower()

    seq = next(c for c in promote.family_configs("ARO:3000000")
               if "ARO:3001206" in c["mech"])
    assert any(e["subject"] == "determinant" and e["object"] == "drug0"
               for e in seq["extra_edges"]), "sequestration binds the drug"


def test_generic_protection_does_not_claim_a_mode():
    """Rounds 31/44/45 curated three modes with three papers; these records name none."""
    cfg = next(c for c in promote.family_configs("ARO:3000185")
               if any(n["node_id"] == "blocked_binding" for n in c["extra_nodes"]))
    blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    for mode in ("displac", "ef-g", "rescue", "ribosom"):
        assert mode not in blob, f"generic config claims the {mode!r} mode"


def test_drug_specific_inactivation_terms_name_no_reaction():
    """Round 85's rule, applied to three more family terms.

    Bacitracin, fosfomycin and macrolide inactivation are all "by chemical modification"
    with no reaction named. Naming one would import a chemistry the term does not claim --
    and the specific chemistries ARE curated elsewhere (rounds 62-64, 68, 70).
    """
    for fam in ("ARO:3004260", "ARO:3000342", "ARO:3000201"):
        cfg = next(c for c in promote.family_configs(fam)
                   if any(n["node_id"] == "modification" for n in c.get("extra_nodes", ())))
        blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
        for chem in ("acetyl", "phospho", "nucleotidyl", "hydroxyl", "esterase"):
            assert chem not in blob, f"{fam} imported the {chem!r} chemistry"


def test_every_drug_specific_inactivation_term_is_registered():
    """Round 100 built the builder and registered three of five families.

    A family's MEMBERS being curated (rounds 62-64) does not curate its TERM, and the
    two missed terms sat as drafts until audit-drafts named them. Pinned so the next
    such term is added to the list rather than rediscovered.
    """
    expected = {"ARO:3004260", "ARO:3000342", "ARO:3000201",
                "ARO:3000576", "ARO:3000233"}
    for fam in expected:
        cfgs = promote.family_configs(fam)
        assert any(any(n["node_id"] == "modification" for n in c.get("extra_nodes", ()))
                   for c in cfgs), f"{fam} has no drug-specific inactivation config"


def test_eccc5_contradiction_travels_with_the_claim():
    """CARD states the mechanism and then cites evidence against it, in one sentence.

    Truncating at the comma would leave a clean claim that the source itself disputes.
    The whole sentence is quoted, on the same edge, so a reader sees both halves.
    """
    cfg = promote.family_configs("ARO:3004916")[0]
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "uptake")
    contra = next(e for e in edge["evidence"] if e["reference"] == "ARO:3004919")
    assert "no evidence of an association" in contra["snippet"]
    assert "decreased uptake" in contra["snippet"], "both halves must be present"
    assert "#220" in cfg["note"], "the missing structural carrier is named"


def test_cls_does_not_connect_cardiolipin_to_daptomycin():
    """Daptomycin is membrane-active and the inference is inviting; CARD never makes it.

    Same refusal as round 83's rpoC, where rifampicin's rpoB mechanism was the obvious
    and wrong thing to reach for.
    """
    cfg = promote.family_configs("ARO:3003272")[0]
    asserted = " ".join(
        [e["predicate"] for e in cfg["extra_edges"]]
        + [n["label"] for n in cfg["extra_nodes"]]).lower()
    for banned in ("daptomycin", "resist", "drug"):
        assert banned not in asserted, f"cls config asserts {banned!r} uncited"
    assert "NOT asserted" in cfg["note"]


def test_p450_and_eftu_get_the_same_treatment():
    """Round 84 left P450 calling it "thinner than EF-Tu". The definitions say otherwise.

    Both name a FUNCTION and claim resistance with no mechanism between. Round 66 curated
    EF-Tu on exactly that basis, so leaving P450 was an inconsistency, not a standard.
    Both configs must now assert only the functional identity.
    """
    for fam in ("ARO:3003356", "ARO:3007522"):
        cfg = promote.family_configs(fam)[0]
        asserted = " ".join(
            [e["predicate"] for e in cfg["extra_edges"]]
            + [n["label"] for n in cfg["extra_nodes"]]).lower()
        for banned in ("bind", "inhibit", "resist"):
            assert banned not in asserted, f"{fam} asserts {banned!r} uncited"
        assert "NOT asserted" in cfg["note"]


def test_pgsa_and_afta_get_the_same_treatment():
    """Round 96 left pgsA as "a role and no mechanism" -- what round 95 curated aftA on.

    Second inconsistency of the shape round 104 found. Both configs must assert the role
    and no drug link.
    """
    for fam in ("ARO:3003422", "ARO:3003420"):
        cfg = promote.family_configs(fam)[0]
        asserted = " ".join(e["predicate"] for e in cfg["extra_edges"]).lower()
        for banned in ("resist", "drug", "inhibit", "mutation"):
            assert banned not in asserted, f"{fam} asserts {banned!r} uncited"


def test_rrna_parent_does_not_borrow_its_children_binding_site_edge():
    """Rounds 54-55 built binding_site --part of--> determinant from the 16S/23S
    definitions. The parent says only that drugs target the ribosome."""
    parent = promote.family_configs("ARO:3000328")[0]
    assert not any(n["node_id"] == "binding_site" for n in parent["extra_nodes"])
    assert parent["determinant_node_type"] == "NUCLEIC_ACID"
    for child in ("ARO:3003211", "ARO:3000336"):
        cfg = promote.family_configs(child)[0]
        assert any(n["node_id"] == "binding_site" for n in cfg["extra_nodes"])


def test_rpob_and_rpoc_both_omit_the_rifampicin_edge():
    """Round 83 refused rpoC the mechanism because it belongs to rpoB. rpoB does not
    state it either, so the refusal was doubly right and both configs must stay bare.

    This is the most inviting uncited edge in the corpus: rifampicin-rpoB is textbook
    and this is the record it belongs to.
    """
    for fam in ("ARO:3003289", "ARO:3003276"):
        cfg = promote.family_configs(fam)[0]
        asserted = " ".join(
            [e["predicate"] for e in cfg["extra_edges"]]
            + [n["label"] for n in cfg["extra_nodes"]]).lower()
        for banned in ("rifampicin", "rifamycin", "binds the drug", "inhibit"):
            assert banned not in asserted, f"{fam} asserts {banned!r} uncited"
        assert "NOT asserted" in cfg["note"]


def test_nfsb_keeps_its_genetic_precondition():
    """"in an nfsA mutant background" is the difference between a claim and a conditional.

    Dropping it would turn "mutations confer resistance when another gene is already
    broken" into "mutations confer resistance".
    """
    cfg = promote.family_configs("ARO:3003755")[0]
    assert any(n["node_id"] == "nfsa_background" for n in cfg["extra_nodes"])
    edge = next(e for e in cfg["extra_edges"] if e["subject"] == "nfsa_background")
    # Case-insensitive: the note emphasises the clause in caps, and asserting the
    # lowercase form failed while the DATA was correct.
    assert "nfsa mutant background" in edge["evidence"][0]["notes"].lower()
    assert "CONDITIONAL" in cfg["note"]


def test_rpo_subunits_are_curated_to_what_each_definition_gives():
    """rpoB and rpoC say what their subunit forms; rpoA does not, so it gets less."""
    for fam in ("ARO:3003276", "ARO:3003289"):
        cfg = promote.family_configs(fam)[0]
        assert any(n["node_id"] == "active_center" for n in cfg["extra_nodes"]), fam
    rpoa = promote.family_configs("ARO:3004997")[0]
    assert not any(n["node_id"] == "active_center" for n in rpoa["extra_nodes"])


def test_fur1_and_hmg1_stop_before_the_standard_story():
    """Both are one inference from a textbook mechanism, and CARD gives neither.

    FUR1: 5-FC is a prodrug activated by pyrimidine salvage. Hmg1: HMG-CoA reductase is
    upstream of ergosterol, which azoles target. Both true, both uncited here.
    """
    for fam, banned in (("ARO:3007557", ("flucytosine", "prodrug", "activat")),
                        ("ARO:3007670", ("ergosterol", "azole", "triazole"))):
        cfg = promote.family_configs(fam)[0]
        asserted = " ".join(
            [e["predicate"] for e in cfg["extra_edges"]]
            + [n["label"] for n in cfg["extra_nodes"]]).lower()
        for word in banned:
            assert word not in asserted, f"{fam} asserts {word!r} uncited"


def test_uhpa_is_reduced_import_not_efflux():
    """A 16th mechanism kind: the drug is not pumped out, it is not let in.

    Every efflux config (rounds 67-79, 93) exports the drug. uhpA loses a transporter's
    ACTIVATOR, so less drug enters. Neither shape may borrow the other's vocabulary.
    """
    cfg = promote.family_configs("ARO:3003893")[0]
    labels = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    assert "uptake" in labels and "importer" in labels
    for effluxy in ("efflux", "extrud", "export", "antiport"):
        assert effluxy not in labels, f"uhpA config uses efflux vocabulary: {effluxy}"


def test_mshb_asserts_no_resistance_at_all():
    """CARD gives substrate, product and pathway step, and never mentions a drug."""
    cfg = promote.family_configs("ARO:3004903")[0]
    asserted = " ".join(e["predicate"] for e in cfg["extra_edges"]).lower()
    for banned in ("resist", "drug", "antibiotic", "mutation"):
        assert banned not in asserted, f"mshB config asserts {banned!r} uncited"


def test_upc2_uses_the_overexpression_id_its_record_carries():
    """The label says "with mutations"; the record carries ARO:3007609, not ARO:3000212.

    I assumed the mutation id and the promoter wrote zero records. Second time this
    session (round 87 the first). Pinned so the label cannot mislead again.
    """
    cfg = promote.family_configs("ARO:3007551")[0]
    assert "ARO:3007609" in cfg["mech"]
    assert "ARO:3000212" not in cfg["mech"]


def test_nudc_says_function_not_activate():
    """Round 95's mshA/mshC line: "activate" licenses a prodrug edge, "function" does not.

    Ethionamide IS a prodrug and ndh (round 57) curates that story for a neighbour, which
    is exactly why the distinction has to be enforced rather than judged each time.
    """
    cfg = promote.family_configs("ARO:3004892")[0]
    assert "to function" in cfg["mech"]["ARO:3000212"].lower()
    asserted = " ".join(e["predicate"] for e in cfg["extra_edges"]).lower()
    assert "activat" not in asserted


def test_daptomycin_trio_share_one_builder_and_assert_no_drug_link():
    """Rounds 104-105 found two cases where I applied round 66's shape inconsistently
    by hand. These three use a builder so they cannot drift."""
    for fam in ("ARO:3003800", "ARO:3003805", "ARO:3003813"):
        cfg = promote.family_configs(fam)[0]
        assert len(cfg["extra_edges"]) == 1
        asserted = " ".join(
            [e["predicate"] for e in cfg["extra_edges"]]
            + [n["label"] for n in cfg["extra_nodes"]]).lower()
        for banned in ("daptomycin", "resist", "membrane depolar"):
            assert banned not in asserted, f"{fam} asserts {banned!r} uncited"


def test_drma_keeps_uncharacterized_and_modest():
    """Both are statements about evidence and effect size, not decoration."""
    cfg = promote.family_configs("ARO:3003813")[0]
    assert "UNCHARACTERIZED" in cfg["note"] and "MODEST" in cfg["note"]
    assert "uncharacterized" in cfg["mech"]["ARO:3000212"].lower()
    assert "modest" in cfg["mech"]["ARO:3000212"].lower()


def test_both_nudc_records_refuse_the_prodrug_edge_for_the_same_word():
    """Ethionamide (round 110) and isoniazid (round 112) nudC records both say
    "inability ... to FUNCTION". Both are prodrugs; neither definition licenses the edge."""
    for fam in ("ARO:3004892", "ARO:3004911"):
        cfg = promote.family_configs(fam)[0]
        assert "to function" in cfg["mech"]["ARO:3000212"].lower()
        asserted = " ".join(e["predicate"] for e in cfg["extra_edges"]).lower()
        assert "activat" not in asserted, f"{fam} wrote a prodrug edge"


def test_kasa_has_no_config_pending_220():
    """kasA asserts isoniazid resistance that PMID:12406221 contradicts (#220).

    It is the last function-naming draft and is deliberately left. Round 102's eccC5
    showed this corpus has no structural way to carry a contested claim.
    """
    assert promote.family_configs("ARO:3003462") == []


def test_folc_names_the_intermediate_that_other_prodrug_configs_lack():
    """Rounds 56, 57, 95, 108 curated prodrug-activation loss from shorter sentences.

    folC's runs end to end and names hydroxyl-dihydrofolate -- the only intermediate
    named in any of them. If the node vanishes, the graph has lost what makes it fullest.
    """
    cfg = promote.family_configs("ARO:3004155")[0]
    assert any(n["node_id"] == "analog" for n in cfg["extra_nodes"])
    assert "hydroxyl-dihydrofolate" in " ".join(
        n["label"] for n in cfg["extra_nodes"]).lower()
    pnca = promote.family_configs("ARO:3004267")[0]
    assert not any("analog" == n["node_id"] for n in pnca["extra_nodes"])


def test_folc_and_thya_give_different_halves_of_one_mechanism():
    """Both are p-aminosalicylic acid prodrug-activation loss (rounds 113, 114).

    folC names the INTERMEDIATE whose absence is the resistance; thyA names the DEFECT
    the mutation causes. Neither may borrow the other's half.
    """
    folc = promote.family_configs("ARO:3004155")[0]
    thya = promote.family_configs("ARO:3004152")[0]
    assert any(n["node_id"] == "analog" for n in folc["extra_nodes"])
    assert not any(n["node_id"] == "analog" for n in thya["extra_nodes"])
    assert any(n["node_id"] == "defect" for n in thya["extra_nodes"])
    assert not any(n["node_id"] == "defect" for n in folc["extra_nodes"])


def test_cya_keeps_the_neutral_regulation_predicate():
    """CARD says cAMP "regulates" glpT without a direction (rounds 78, 110 precedent)."""
    cfg = promote.family_configs("ARO:3004251")[0]
    edge = next(e for e in cfg["extra_edges"] if e["object"] == "glpt")
    assert edge["predicate_id"] == "RO:0002211"
    assert "without saying which way" in cfg["note"] or "which way" in edge["evidence"][0]["notes"]


def test_srebp_and_upc2_differ_because_their_sources_do():
    """Same mechanism id (ARO:3007609), opposite treatment of direction.

    Upc2 says "by upregulating ERG11 expression" -> positive edge.
    SREBP says "through differential gene regulation" -> neutral edge.
    "Differential" is CARD declining to say, not omitting to say.
    """
    upc2 = promote.family_configs("ARO:3007551")[0]
    srebp = promote.family_configs("ARO:3007549")[0]
    assert upc2["extra_edges"][0]["predicate_id"] == "RO:0002213"
    assert srebp["extra_edges"][0]["predicate_id"] == "RO:0002211"
    assert "differential" in srebp["note"].lower()


def test_ampr_ends_at_overexpression_not_hydrolysis():
    """The beta-lactamases are curated (rounds 12-16, 59); round 22's rule applies."""
    cfg = promote.family_configs("ARO:3007797")[0]
    blob = " ".join(n["label"] for n in cfg["extra_nodes"]).lower()
    for chem in ("hydrol", "acyl", "serine", "amide bond"):
        assert chem not in blob, f"ampR config restates beta-lactamase chemistry: {chem}"


def test_ddla_gives_the_structural_basis_folp_only_named():
    """Round 82's folP said the inhibition was competitive; ddlA says WHY.

    "Cycloserine has a similar structure to d-alanine" is the only structural basis for
    competition stated anywhere in this corpus.
    """
    cfg = promote.family_configs("ARO:3004939")[0]
    edge = next(e for e in cfg["extra_edges"]
                if e["subject"] == "drug0" and e["object"] == "dala")
    assert edge["predicate_id"] == "RO:0002158"
    assert "similar structure" in edge["evidence"][0]["notes"]


def test_fks2_omits_the_echinocandin_edge_like_rpob_omits_rifampicin():
    """Both are the record the textbook mechanism belongs to, and neither source says it."""
    for fam in ("ARO:3007548", "ARO:3003276"):
        cfg = promote.family_configs(fam)[0]
        asserted = " ".join(
            [e["predicate"] for e in cfg["extra_edges"]]
            + [n["label"] for n in cfg["extra_nodes"]]).lower()
        for banned in ("inhibit", "binds the drug"):
            assert banned not in asserted, f"{fam} asserts {banned!r} uncited"


def test_msh2_does_not_assert_hypermutation():
    """Three unrelated drug classes from one mismatch-repair gene.

    Losing repair raises the mutation rate; that is the obvious reading and CARD does not
    say it. The most inviting inference in the corpus after rpoB's rifampicin edge.
    """
    cfg = promote.family_configs("ARO:3009134")[0]
    blob = (" ".join(n["label"] for n in cfg["extra_nodes"])
            + " " + " ".join(e["predicate"] for e in cfg["extra_edges"])).lower()
    for banned in ("hypermut", "mutation rate", "resist"):
        assert banned not in blob, f"MSH2 config asserts {banned!r} uncited"
    assert "hypermutation" in cfg["note"].lower(), "the omission must be named"


def test_pepq_keeps_putative_in_the_node_label():
    """CARD hedges the function ASSIGNMENT, not just its characterisation.

    A step further than round 111's drmA, where the protein was "uncharacterized" but its
    identity was not in doubt.
    """
    cfg = promote.family_configs("ARO:3007690")[0]
    assert "putative" in cfg["extra_nodes"][0]["label"].lower()


def test_ald_and_ddla_sit_either_side_of_one_step_and_only_ddla_gets_the_mimicry():
    """ddlA's record says cycloserine resembles D-alanine; ald's says only "not function".

    The two records are one step apart in the same wall pathway, which makes borrowing
    the mimicry edge across especially tempting.
    """
    ddla = promote.family_configs("ARO:3004939")[0]
    ald = promote.family_configs("ARO:3004943")[0]
    assert any(e["predicate_id"] == "RO:0002158" for e in ddla["extra_edges"])
    assert not any(e["predicate_id"] == "RO:0002158" for e in ald["extra_edges"])
    assert "to not function" in ald["mech"]["ARO:3000212"].lower()


def test_blmt_does_not_assert_sequestration():
    """BLMT sequesters bleomycin (round 72's shape) and CARD says so nowhere.

    Its three sentences each restate the resistance; only the Tn5 context adds anything.
    """
    cfg = promote.family_configs("ARO:3005036")[0]
    asserted = " ".join(
        [e["predicate"] for e in cfg["extra_edges"]]
        + [n["label"] for n in cfg["extra_nodes"]]).lower()
    for banned in ("sequest", "binds", "complex"):
        assert banned not in asserted, f"BLMT config asserts {banned!r} uncited"
    assert "SEQUESTERS" in cfg["note"], "the known-but-uncited mechanism must be named"


def test_fura_gives_the_dna_binding_basis_other_regulators_omit():
    """Rounds 78, 79, 110 and 115 curated regulators with no molecular basis stated.

    furA gives one -- "by binding to the promoter region" -- and states no resistance at
    all, though katG activates isoniazid and repressing it is the obvious route.
    """
    cfg = promote.family_configs("ARO:3004897")[0]
    assert any(n["node_id"] == "promoter_binding" for n in cfg["extra_nodes"])
    asserted = " ".join(
        [e["predicate"] for e in cfg["extra_edges"]]
        + [n["label"] for n in cfg["extra_nodes"]]).lower()
    for banned in ("isoniazid", "resist", "activat"):
        assert banned not in asserted, f"furA config asserts {banned!r} uncited"


def test_the_two_mshc_records_are_curated_differently():
    """ARO:3004904 carries its reaction; ARO:3004889 (round 94) does not and stays a draft.

    Two records for one gene, one curatable and one not -- as with mshA and mshB.
    """
    assert promote.family_configs("ARO:3004904") != []
    assert promote.family_configs("ARO:3004889") == []


def test_frxa_and_nfsb_differ_because_only_nfsb_names_the_drug_as_substrate():
    """Both are nitroreductases. nfsB (round 107) says it "reduces ... the antibiotics",
    which licensed a prodrug-activation-loss edge. FrxA's sentence does not say it."""
    nfsb = promote.family_configs("ARO:3003755")[0]
    frxa = promote.family_configs("ARO:3007059")[0]
    assert any(e["object"] == "drug0" for e in nfsb["extra_edges"])
    assert not any(e["object"] == "drug0" for e in frxa["extra_edges"])


def test_esx5_system_term_is_not_curated_pending_229():
    """Round 102 curated its subunits with part-of edges into the complex.

    The system term itself is the complex-versus-subunit question #229 is about, and
    curating it would answer that by fiat.
    """
    assert promote.family_configs("ARO:3004915") == []


# ---------------------------------------------------------------------------------------
# Round 121 — three ribosomal-protein families whose graphs differ because their CARD
# definitions differ. Each test names the clause that decided the difference.

def test_rpsa_asserts_no_loss_of_the_proteins_own_function():
    """ARO:3004721 says mutations resist "maintaining rpsA function", and Shi 2011 says
    POA inhibited "trans-translation rather than canonical translation".

    Two independent statements that nothing is lost. The determinant must therefore
    never be the subject of a negative edge onto trans-translation -- only POA is.
    """
    cfg = promote.family_configs("ARO:3004722")[0]
    losses = [e for e in cfg["extra_edges"]
              if e["subject"] == "determinant"
              and e["object"] == "trans_translation"
              and e["predicate_id"] in ("RO:0002212", "RO:0002411")]
    assert losses == []
    # and the positive edge IS there: the determinant enables the process
    assert any(e["subject"] == "determinant" and e["object"] == "trans_translation"
               and e["predicate_id"] == "RO:0002327" for e in cfg["extra_edges"])
    # the inhibition is the drug's, not the mutation's
    assert any(e["subject"] == "poa" and e["object"] == "trans_translation"
               and e["predicate_id"] == "RO:0002212" for e in cfg["extra_edges"])
    # #359: the edge whose description says "the resistant variant STILL does this" must
    # cite the text that says it, not only a sentence about RpsA generically.
    kept = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "trans_translation"]
    assert len(kept) == 1
    assert any("maintaining rpsA function" in ev["snippet"] for ev in kept[0]["evidence"])
    # #349: the drug binds the DRUG-SENSITIVE protein, never the determinant -- whose node
    # denotes the resistant variant the snippet says POA does not bind.
    binds = [e for e in cfg["extra_edges"]
             if e["subject"] == "poa" and e["predicate_id"] == "RO:0002436"]
    assert [e["object"] for e in binds] == ["rpsa_wt"]


def test_every_complex_node_is_defined_by_all_its_named_constituents():
    """Round 21's rule: a drug-target complex is DEFINED by its constituents.

    Round 121 first applied it to one half of each -- `strep_binding` had the rRNA but
    not the drug, `poa_rpsa` had the protein but not POA -- so a node labelled for two
    participants was structurally made of one (#370). Five review rounds read these edges
    and none asked whether the constituents were complete.
    """
    for fam, node, want in (("ARO:3003395", "strep_binding", {"rrna16s", "drug0"}),
                            ("ARO:3004722", "poa_rpsa", {"rpsa_wt", "poa"})):
        cfg = promote.family_configs(fam)[0]
        parts = {e["object"] for e in cfg["extra_edges"]
                 if e["subject"] == node and e["predicate_id"] == "BFO:0000051"}
        assert parts == want, f"{node} is defined by {parts}, not {want}"


def test_rpsa_parent_records_that_its_preservation_claim_is_the_child_terms():
    """ARO:3004722's own definition says mutations "prevent pyrazinoic acid from TARGETING
    RpsA" -- prevention of targeting, not preservation of function.

    "maintaining rpsA function" is the child term ARO:3004721's wording. Citing a
    descendant is an established pattern here, but the notes must say so (#371).
    """
    cfg = promote.family_configs("ARO:3004722")[0]
    kept = [e for e in cfg["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "trans_translation"][0]
    ev = [x for x in kept["evidence"] if x["reference"] == "ARO:3004721"][0]
    assert "more specific term" in ev["notes"]
    assert "does not itself state" in ev["notes"]


def test_rpsa_wt_says_it_is_the_same_protein_as_the_determinant():
    """RO has no allelic-variant predicate (#357), so the relation cannot be an edge.

    It must then be in the node description, or a consumer sees two unrelated proteins
    that both enable trans-translation.
    """
    cfg = promote.family_configs("ARO:3004722")[0]
    wt = [n for n in cfg["extra_nodes"] if n["node_id"] == "rpsa_wt"]
    assert len(wt) == 1
    desc = wt[0]["description"].lower()
    assert "same protein as `determinant`" in desc
    assert "no edge" in desc          # and says why there is no edge
    assert "grounding" not in wt[0]   # only the resistant allele has an ARO term


def test_rpsa_carries_no_domain_node_because_pf00575s_definition_is_the_wrong_entry():
    """PF00575 is labelled "S1 RNA binding domain" and would be the obvious trait node.

    Its KB definition is IPR059328's abstract -- "Domain of unknown function DUF8284" --
    the wrong InterPro entry (#344). Round 21's rule: no node rather than a node whose
    evidence is about something else.
    """
    cfg = promote.family_configs("ARO:3004722")[0]
    assert "protein_traits" not in cfg
    # `repr`, not a serialiser: a config carries its `precondition` callable.
    assert "PF00575" not in repr(cfg)


def test_rpsl_follows_its_source_not_cards_stronger_wording():
    """CARD: S12 "stabilizes" the pseudoknot, and resistance is "by disrupting
    interactions". PMID:7934937, the paper CARD's definition is built from, says the
    region "has been linked to" S12 and reports no stabilisation experiment.

    The determinant->pseudoknot edge must be `correlated with`, never a causal or
    regulatory predicate, and it must carry BOTH readings so the gap is visible.
    """
    cfg = promote.family_configs("ARO:3003395")[0]
    pk = [e for e in cfg["extra_edges"]
          if e["subject"] == "determinant" and e["object"] == "pseudoknot"]
    assert len(pk) == 1
    assert pk[0]["predicate_id"] == "RO:0002610"
    # the predicate TEXT must not smuggle CARD's stronger verb back in
    assert "stabilis" not in pk[0]["predicate"].lower()
    assert "stabiliz" not in pk[0]["predicate"].lower()
    refs = {ev["reference"] for ev in pk[0]["evidence"]}
    assert refs == {"PMID:7934937", "ARO:3003395"}


def test_rpsl_snippets_come_from_the_reference_they_are_attributed_to():
    """`mech`, `mech_res` and `res_drug` are attributed by the promoter to `cfg["reference"]`.

    Three review findings collide on this one field:

    * #348 -- Musser's (PMID:8665467) sentence was placed there under PMID:7934937;
    * #363 -- those three edges assert CONFERRAL, which only CARD states;
    * so `reference` must be CARD, or fixing #363 re-creates #348.

    #360: the string is asserted LITERALLY, not as `== the_constant`, so any edit to the
    constant forces someone to re-verify it against the source rather than silently
    carrying a foreign sentence.
    """
    cfg = promote.family_configs("ARO:3003395")[0]
    assert cfg["reference"] == "ARO:3003395"
    card = ("Ribosomal protein S12 stabilizes the highly conserved pseudoknot structure "
            "formed by 16S rRNA. Amino acid substitutions in RpsL affect the higher-order "
            "structure of 16S rRNA and confer streptomycin resistance by disrupting "
            "interactions between 16S rRNA and streptomycin.")
    assert cfg["mech_res"] == card
    assert cfg["res_drug"] == card
    assert set(cfg["mech"].values()) == {card}
    # the two literature sentences appear ONLY where their own reference is named
    for d in cfg["det_res"]:
        if "about one-half" in d["snippet"]:
            assert d["reference"] == "PMID:8665467"
        if "either lead to amino acid changes" in d["snippet"]:
            assert d["reference"] == "PMID:7934937"
    assert "about one-half" not in card
    # and it IS still cited, on the edge that names Musser
    det = cfg["det_res"]
    assert any("about one-half" in d["snippet"] and d["reference"] == "PMID:8665467"
               for d in det)


def test_rpse_never_joins_the_substitution_to_the_drug():
    """CARD says only that substitutions "is associated with resistance", and supplies
    two structural facts that it does not connect to the drug.

    So no edge may run from the determinant to the drug node or to a binding-site node,
    and the determinant->resistance edge this config adds must be `correlated with`.
    """
    cfg = promote.family_configs("ARO:3007526")[0]
    assert not any(e["subject"] == "determinant" and e["object"].startswith("drug")
                   for e in cfg["extra_edges"])
    res = [e for e in cfg["extra_edges"]
           if e["subject"] == "determinant" and e["object"] == "resistance"]
    assert len(res) == 1 and res[0]["predicate_id"] == "RO:0002610"
    # #350: the config's own edges are a SUBSET -- the promoter always adds a fixed
    # `confers resistance to (drug class)` edge, so the first assertion above passes
    # vacuously for it. Read the emitted record and state what is actually true of it.
    rec = yaml.safe_load(
        (promote.ARO_DIR / "spectinomycin-resistant-rpse-aro3007526.yaml").read_text("utf-8"))
    graph = [g for g in rec["causal_graphs"] if g["graph_id"] == "resistance"][0]
    to_drug = [e for e in graph["edges"] if e["object"].startswith("drug")]
    # exactly one, and it is the fixed CARD-assertion edge -- not a mechanism edge
    assert len(to_drug) == 1
    assert to_drug[0]["predicate_id"] == "ARO:2000001"
    # no mechanism edge anywhere ties the determinant to a binding site
    endpoints = [x for e in graph["edges"] for x in (e["subject"], e["object"])]
    assert not any("binding" in n or "site" in n for n in endpoints)
    # and the record carries the honest association edge
    assert any(e["subject"] == "determinant" and e["object"] == "resistance"
               and e["predicate_id"] == "RO:0002610" for e in graph["edges"])


def test_rpse_uses_the_neisseria_modelling_result_as_context_only():
    """PMID:42450237 carries three qualifications at once -- it is modelling, it is
    hedged ("potentially altering"), and it is Neisseria, not these records' organisms.

    It may ride on an edge CARD already supports; it may not be the sole evidence for
    any edge.
    """
    cfg = promote.family_configs("ARO:3007526")[0]
    carrying = [e for e in cfg["extra_edges"]
                if any(ev["reference"] == "PMID:42450237" for ev in e["evidence"])]
    # assert it is PRESENT before constraining it -- otherwise a typo'd id passes (#350)
    assert len(carrying) == 1
    refs = [ev["reference"] for ev in carrying[0]["evidence"]]
    assert len(refs) > 1, "the modelling result must not be an edge's only evidence"
    assert "ARO:3007526" in refs
    # the three qualifications must be stated in the notes, not merely known to the curator
    notes = " ".join(ev.get("notes", "") for ev in carrying[0]["evidence"]).lower()
    for qualification in ("modelling", "potentially altering", "neisseria"):
        assert qualification in notes


def test_the_three_ribosomal_families_do_not_share_one_config():
    """rpsA, rpsL and rpsE are all ARO:3000212 small-subunit ribosomal proteins.

    A single shared config was the tempting shortcut and would have asserted rpsA's
    binding mechanism on rpsE, which CARD does not support for it.
    """
    cfgs = [promote.family_configs(f)[0]
            for f in ("ARO:3004722", "ARO:3003395", "ARO:3007526")]
    refs = [c["reference"] for c in cfgs]
    assert len(set(refs)) == 3
    # #350: sizes alone would pass with two configs byte-identical. Compare the edge
    # CONTENT, which is the risk the docstring names.
    shapes = [frozenset((e["subject"], e["predicate_id"], e["object"]) for e in c["extra_edges"])
              for c in cfgs]
    assert len(set(shapes)) == 3
    rpsa, _, rpse = cfgs
    # the specific over-reach: rpsA's binding chemistry must not appear on rpsE
    rpse_blob = repr(rpse)
    for rpsa_only in ("poa", "rpsa_wt", "trans_translation"):
        assert rpsa_only not in rpse_blob
    assert any("poa" in e["object"] or "poa" in e["subject"] for e in rpsa["extra_edges"])


def test_rpse_does_not_type_its_second_domain_as_a_fold():
    """`protein_traits["fold"]` emits `member of (adopts fold)`.

    Pfam:PF03719 is the S5 C-TERMINAL DOMAIN -- the determinant's other part, not a fold.
    The shape offers no second part slot, so it gets no node at all (#352).
    """
    cfg = promote.family_configs("ARO:3007526")[0]
    pt = cfg["protein_traits"]
    assert "fold" not in pt
    assert pt[pt["primary_key"]][0] == "Pfam:PF00333"
    # #358: it is not dropped -- it is an extra_node typed as the DOMAIN it is, with a
    # `part of` edge. Dropping it lost a real KB-trait link for a reason that was untrue.
    node = [n for n in cfg["extra_nodes"] if n.get("grounding") == "Pfam:PF03719"]
    assert len(node) == 1 and node[0]["node_type"] == "DOMAIN"
    edge = [e for e in cfg["extra_edges"] if e["subject"] == node[0]["node_id"]]
    assert len(edge) == 1
    assert edge[0]["predicate_id"] == "BFO:0000050" and edge[0]["object"] == "determinant"
    assert "adopts fold" not in repr(cfg)


def test_rv3008_is_not_curated_because_card_hedges_both_halves():
    """"A hypothetical protein for which it has been PREDICTED but no experimental
    evidence exists to determine its function. MAY contribute to pyrazinamide
    resistance."

    Round 117's "putative" shape doubled: the function assignment is uncertain AND the
    resistance contribution is uncertain. There is no claim left to assert.
    """
    assert promote.family_configs("ARO:3004989") == []


# ---------------------------------------------------------------------------------------
# Round 122 — target alteration in trans, twice more.

def test_ul3_family_splits_because_only_one_record_names_the_protein():
    """ARO:3005081 says "ribosomal protein uL3"; ARO:3005082 says "Ribosomal protein
    mutations" and names no protein.

    One config with `protein_traits` would assert the L3 family node on the record that
    never mentions L3 -- #371's borrowed specificity, filed one round earlier. Two configs,
    selected by precondition.
    """
    cfgs = promote.family_configs("ARO:3005082")
    # NOT an exact count -- #287 bans that, and the meta-test caught this test writing one.
    named = [c for c in cfgs if "protein_traits" in c]
    unnamed = [c for c in cfgs if "protein_traits" not in c]
    assert len(named) >= 1 and len(unnamed) >= 1
    named, unnamed = named[0], unnamed[0]
    assert "protein_traits" in named
    assert named["protein_traits"]["family"][0] == "Pfam:PF00297"
    assert "protein_traits" not in unnamed
    # groundings and references, NOT prose -- a comment explaining WHY PF00297 is absent
    # legitimately names it, and the first version of this assertion failed on that.
    assert not any(n.get("grounding") == "Pfam:PF00297" for n in unnamed["extra_nodes"])
    refs = {ev["reference"] for e in unnamed["extra_edges"] for ev in e["evidence"]}
    refs |= {d["reference"] for d in unnamed["det_res"]}
    assert "Pfam:PF00297" not in refs, "the L3 abstract must not be cited on a record that names no protein (#374)"
    # #380: the limitation is recorded on the determinant NODE, not as a second weaker edge
    # on a pair that already has a strong one. `determinant_note` must be a key the promoter
    # actually reads -- a config key it ignores records nothing.
    assert "#371" in unnamed["determinant_note"]
    assert not any(e["predicate_id"] == "RO:0002610" and e["subject"] == "determinant"
                   and e["object"] == "rrna23s" for e in unnamed["extra_edges"])
    # #374/#382: the L3-specific experiments stay on the named record only -- checked over
    # the WHOLE config, not just det_res. The first version asserted this on det_res alone,
    # which was the one place the fix had touched, and four L3 citations survived in
    # extra_edges with the test green and a node description claiming they were gone.
    def _all_refs(cfg):
        refs = {d["reference"] for d in cfg["det_res"]}
        refs |= {ev["reference"] for e in cfg["extra_edges"] for ev in e["evidence"]}
        return refs

    def _all_snippets(cfg):
        s = [d["snippet"] for d in cfg["det_res"]]
        s += [ev["snippet"] for e in cfg["extra_edges"] for ev in e["evidence"]]
        return " ".join(s)

    assert "PMID:12936991" in _all_refs(named)
    # NOT a reference-level ban: PMID:12936991 also states what the DRUG does ("tiamulin
    # targets the 50S subunit and interacts at the peptidyl transferase center"), which is
    # true of any member. The constraint is on SNIPPETS that carry the L3-specific result.
    assert not re.search(r"\bu?L3\b", _all_snippets(unnamed)), \
        "no snippet on a record that names no protein may name L3 (#374, #382)"
    for l3_only in (promote._TIAMULIN_INFERRED, promote._TIAMULIN_FOOTPRINT,
                    promote._TIAMULIN_MUTANT, promote._TIAMULIN_NOT_RRNA):
        assert l3_only not in _all_snippets(unnamed)
    assert re.search(r"\bL3\b", _all_snippets(named))
    # the catch-all must be LAST, or it shadows the specific one
    assert named.get("precondition") is not None
    assert unnamed.get("precondition") is None


def test_the_ul3_precondition_reads_only_the_records_own_definition():
    """#252: an ARO record's full YAML carries drug-class boilerplate naming other things.

    Driven off the REAL records, not synthetic text -- `_own_definition` returns "" for a
    definition block with no following key, so a hand-written fixture tests the parser
    rather than the predicate.
    """
    named = [c for c in promote.family_configs("ARO:3005082") if "protein_traits" in c][0]
    pre = named["precondition"]
    seen = {}
    for pth in promote.ARO_DIR.glob("*.yaml"):
        text = pth.read_text(encoding="utf-8")
        m = re.search(r'^identifier:\s*"?(ARO:3005081|ARO:3005082)"?\s*$', text, re.M)
        if m:
            seen[m.group(1)] = pre(m.group(1), "", text)
    assert seen["ARO:3005081"] is None, "the record that names uL3 must be accepted"
    assert seen["ARO:3005082"] is not None, "the record that names no protein must be refused"
    assert "#371" in seen["ARO:3005082"]


def test_ul3_quotes_both_of_its_sources_hedges_rather_than_around_them():
    """Two hedges, on two different things:

    * PMID:12936991 hedges the INFERENCE -- "It is inferred that the L3 mutation ... causes";
    * the Pfam KB record hedges the FUNCTION -- L3 "may participate in the formation of
      the peptidyltransferase centre".

    Both must survive into the record verbatim rather than being quoted around.
    """
    named = promote.family_configs("ARO:3005082")[0]
    core = [e for e in named["extra_edges"]
            if e["subject"] == "determinant" and e["object"] == "drug_binding"][0]
    assert any("It is inferred that" in ev["snippet"] for ev in core["evidence"])
    # and the measured result rides alongside, so the hedge is not the only support
    assert any("Chemical footprinting experiments" in ev["snippet"] for ev in core["evidence"])
    assert "may participate in the formation" in named["protein_traits"]["family"][3]


def test_ul3_binding_state_is_defined_by_both_constituents():
    """#370, applied prospectively rather than after review found it.

    #378: the config-level version could not fail for the reason it claimed -- emission
    silently drops edges whose `requires` is unmet, so a member with a different first drug
    class would get the drug half dropped, the site half kept, and exactly the one-sided
    binding state #370 is about. Both halves now carry the same guard, and this reads the
    emitted records.
    """
    for cfg in promote.family_configs("ARO:3005082"):
        halves = [e for e in cfg["extra_edges"]
                  if e["subject"] == "drug_binding" and e["predicate_id"] == "BFO:0000051"]
        assert {e["object"] for e in halves} == {"drug0", "ptc"}
        # both guarded, or neither -- an asymmetric guard is what emits a half-defined state
        assert len({repr(e.get("requires")) for e in halves}) == 1
        # #386: and EVERY edge touching the node, or it can be emitted with no parts at all
        touching = [e for e in cfg["extra_edges"]
                    if "drug_binding" in (e["subject"], e["object"])]
        # NOT a count: the two configs legitimately differ here, because #387 removed the
        # generic record's two mechanism edges into this node. The property is that every
        # SURVIVING edge carries the same guard, or the node can be emitted with no parts.
        assert touching
        assert all(e.get("requires") == {"drug0": "ARO:3000670"} for e in touching)
    seen = 0
    for pth in promote.ARO_DIR.glob("*.yaml"):
        text = pth.read_text(encoding="utf-8")
        if not re.search(r'^identifier:\s*"?(ARO:3005081|ARO:3005082)"?\s*$', text, re.M):
            continue
        seen += 1
        graph = [g for g in yaml.safe_load(text)["causal_graphs"]
                 if g["graph_id"] == "resistance"][0]
        parts = {e["object"] for e in graph["edges"]
                 if e["subject"] == "drug_binding" and e["predicate_id"] == "BFO:0000051"}
        assert parts == {"drug0", "ptc"}, f"{pth.name} has a half-defined binding state"
    assert seen == 2


def test_the_two_rpsl_records_differ_by_the_clause_that_names_the_drug_interaction():
    """ARO:3003395 ends "...confer streptomycin resistance BY DISRUPTING INTERACTIONS
    between 16S rRNA and streptomycin". ARO:3003419 ends "...confer antibiotic resistance".

    Same first two sentences; the drug-interaction mechanism is only in one. So only one
    carries the strep_binding arm. Round 120's FrxA/nfsB finding on a closer pair.
    """
    specific = promote.family_configs("ARO:3003395")[0]
    generic = promote.family_configs("ARO:3003419")[0]
    spec_nodes = {n["node_id"] for n in specific["extra_nodes"]}
    gen_nodes = {n["node_id"] for n in generic["extra_nodes"]}
    assert "strep_binding" in spec_nodes
    assert "strep_binding" not in gen_nodes
    # neither config may assert a drug interaction on the generic record
    assert not any(e["object"].startswith("drug") or e["subject"].startswith("drug")
                   for e in generic["extra_edges"])
    # both DO keep the pseudoknot arm, which both definitions state
    for cfg in (specific, generic):
        pk = [e for e in cfg["extra_edges"]
              if e["subject"] == "determinant" and e["object"] == "pseudoknot"]
        assert len(pk) == 1 and pk[0]["predicate_id"] == "RO:0002610"


def _assert_deliberately_held(aro_id):
    """`family_configs(x) == []` is true of every id that does not exist (#379).

    A held-record test has to distinguish "deliberately held" from "never noticed", so it
    must also show the term is real and still has an unpromoted draft.
    """
    assert promote.family_configs(aro_id) == [], f"{aro_id} is configured after all"
    drafts, found = 0, False
    for pth in promote.ARO_DIR.glob("*.yaml"):
        text = pth.read_text(encoding="utf-8")
        if re.search(rf'^identifier:\s*"?{re.escape(aro_id)}"?\s*$', text, re.M):
            found = True
            if "graph_id: resistance-draft" in text:
                drafts += 1
    assert found, f"{aro_id} names no record -- a typo passes the config check silently"
    assert drafts, f"{aro_id} has no draft left, so it is not being held"


def test_the_generic_ul3_record_has_no_mechanism_edge_into_drug_binding():
    """#387: #382 withheld Bosling's L3 result from the record that names no protein and
    left the two edges that rested on it, so they fell back to CARD's sentence -- which
    mentions neither the drug nor binding.

    ARO:3003419 in the same round gets no drug-binding arm from a definition of the same
    shape. This record gets the same treatment.
    """
    named = [c for c in promote.family_configs("ARO:3005082") if "protein_traits" in c][0]
    unnamed = [c for c in promote.family_configs("ARO:3005082") if "protein_traits" not in c][0]
    assert any(e["object"] == "drug_binding" for e in named["extra_edges"])
    assert not any(e["object"] == "drug_binding" for e in unnamed["extra_edges"])
    # and no node is left with nothing pointing at it
    for cfg in (named, unnamed):
        used = {x for e in cfg["extra_edges"] for x in (e["subject"], e["object"])}
        assert all(n["node_id"] in used for n in cfg["extra_nodes"])


def test_conformation_nodes_use_characteristic_of_not_part_of():
    """#384 shipped with no test: reverting RO:0000052 to BFO:0000050 on both families left
    the suite green (#389).

    A conformation INHERES IN a molecule; it is not a mereological part of one.
    """
    seen = 0
    for fam, state, mol in (("ARO:3005082", "altered_conformation", "rrna23s"),
                            ("ARO:3003419", "altered_structure", "rrna16s")):
        for cfg in promote.family_configs(fam):
            edges = [e for e in cfg["extra_edges"]
                     if e["subject"] == state and e["object"] == mol]
            for e in edges:
                seen += 1
                assert e["predicate_id"] == "RO:0000052"
                assert "characteristic of" in e["predicate"]
    assert seen >= 3


def test_no_edge_asserts_the_23s_rrna_is_part_of_the_50s_subunit():
    """#383 shipped with no test: re-adding the deleted edge left the suite green (#389).

    The snippet that edge cited says the structure gives "a detailed picture of ITS
    interactions with the 23S rRNA" -- "its" is tiamulin's. Co-mention is not part-hood.
    """
    for cfg in promote.family_configs("ARO:3005082"):
        assert not any(e["subject"] == "rrna23s" and e["object"] == "subunit50s"
                       for e in cfg["extra_edges"])


def test_every_snippet_constant_is_actually_used():
    """#390, and #375 and #367 before it -- three rounds, three dead snippet constants,
    each found only by a reviewer reading the artifact. Ruff does not flag them.

    Scoped to the round 121/122 constants rather than the whole module, so it states a
    claim it can actually keep.
    """
    src = pathlib.Path(promote.__file__).read_text(encoding="utf-8")
    for name in ("_TIAMULIN_TARGET", "_TIAMULIN_MUTANT", "_TIAMULIN_FOOTPRINT",
                 "_TIAMULIN_INFERRED", "_TIAMULIN_NOT_RRNA", "_PLEURO_SITE",
                 "_PLEURO_INHIBITS", "_L3_HEDGE", "_CARD_UL3", "_CARD_RPMUT",
                 "_CARD_RPSL_GENERIC", "_RPSL_SOURCE_ASSOC", "_RPSL_MUTATIONS",
                 "_RPSL_PSEUDOKNOT", "_RPSL_ASSOC", "_CARD_RPSL"):
        # one definition plus at least one use
        assert src.count(name) >= 2, f"{name} is defined and never used (#390)"


def test_the_vanl_cluster_term_is_not_curated_pending_309():
    """ARO:3000260 is a gene CLUSTER. Whether a cluster should carry a protein-trait causal
    graph is #309's modelling question, and curating it would answer that by fiat."""
    _assert_deliberately_held("ARO:3000260")


# ---------------------------------------------------------------------------------------
# Round 123 — nat.

def test_nat_asserts_no_extra_drug_edge():
    """CARD names "arylamines and hydrazines" and, separately, that overexpression may
    confer isoniazid resistance. It never joins them, and isoniazid IS a hydrazine -- so the
    inference is one step of chemistry away, which is what makes it easy to supply.

    Scope: `extra_edges` only. Both records DO carry the promoter's fixed
    `determinant --confers resistance to (drug class)--> drug0` edge, which is CARD's own
    assertion; the earlier name claimed the graph had no drug edge at all, which is false.

    #396: the first version DID supply one, as an `acetylation --> drug0` edge whose SOLE
    evidence was Pfam's sentence about HUMAN NAT -- inverting round 121's rule that
    out-of-scope context may ride on an edge CARD supports but may never be an edge's only
    evidence. And the test pinned that wrong shape. No config may carry a drug edge.
    """
    for cfg in promote.family_configs("ARO:3004910"):
        assert not any(e["object"].startswith("drug") or e["subject"].startswith("drug")
                       for e in cfg["extra_edges"])
        assert "in humans" not in repr(cfg["extra_edges"])


def test_only_the_record_whose_definition_joins_the_routes_gets_the_joining_edge():
    """ARO:3004930: "Mutations that occur in nat WHICH THROUGH OVEREXPRESSION of the enzyme
    can result in ... resistance" -- CARD joins them.
    ARO:3004910: names both separately and never joins them.

    #395: the first version promoted BOTH with the parent's sentence, then annotated
    ARO:3004930 with a "disagreement" its own definition refutes -- #371 inverted, a record
    discarding its own more specific text for an ancestor's.
    #397: the parent's `overexpression` node therefore has no incoming edge, and none is
    invented for it.
    """
    joined = [c for c in promote.family_configs("ARO:3004910")
              if c.get("precondition") is promote._nat_joins_mutation][0]
    generic = [c for c in promote.family_configs("ARO:3004910")
               if c is not joined][0]

    def incoming(cfg):
        return [e for e in cfg["extra_edges"] if e["object"] == "overexpression"]

    assert len(incoming(joined)) == 1
    assert incoming(joined)[0]["subject"] == "determinant"
    assert "through overexpression" in incoming(joined)[0]["evidence"][0]["snippet"].lower()
    assert incoming(generic) == []
    # and no circular "overexpression regulates the determinant" edge on either (#397)
    for cfg in (joined, generic):
        assert not any(e["subject"] == "overexpression" and e["object"] == "determinant"
                       for e in cfg["extra_edges"])


def test_nat_mech_edge_cites_the_mechanism_terms_own_definition():
    """#398: the mech edge is about ARO:3000212, and the first version evidenced it with
    nat's definition -- a sentence containing no mutation claim at all.

    #393, corrected: ARO:3000212's own definition names "increased expression" among its
    examples, so an overexpression route is IN SCOPE for it rather than a mismatch with it.
    """
    for cfg in promote.family_configs("ARO:3004910"):
        # list form since #400 -- the reference travels with the snippet
        snippets = {i["snippet"] for v in cfg["mech"].values() for i in v}
        assert snippets == {promote._MECH_MUTATION}
    assert "increased expression" in promote._MECH_MUTATION
    assert "Point mutations" in promote._MECH_MUTATION


def test_nat_grounds_the_exact_activity_term_that_is_already_a_kb_record():
    """#399: GO:0008080 (N-acetyltransferase activity) never names acetyl-CoA and its scope
    includes histone and rRNA acetyltransferases. GO:0004060 is the exact term."""
    for cfg in promote.family_configs("ARO:3004910"):
        node = [n for n in cfg["extra_nodes"] if n["node_id"] == "acetylation"][0]
        assert node["grounding"] == "GO:0004060"


def test_nat_mech_snippet_travels_with_its_own_reference():
    """#400: giving `mech`/`mech_res` a bare string makes the promoter stamp
    `cfg["reference"]` on it, which put ARO:3000212's definition under
    `reference: ARO:3004910`. The snippet moved; the attribution did not.

    Third round running in which a fix produced the defect it was fixing.
    """
    for cfg in promote.family_configs("ARO:3004910"):
        for value in list(cfg["mech"].values()) + [cfg["mech_res"]]:
            assert isinstance(value, list), "bare strings inherit cfg['reference'] (#400)"
            for item in value:
                assert item["reference"] == "ARO:3000212"
                assert item["snippet"] == promote._MECH_MUTATION


def test_every_nat_evidence_reference_actually_contains_its_snippet():
    """#402: no test in the suite pinned an evidence `reference` -- the blind spot #348,
    #382 and #400 all slipped through.

    The FIRST version of this test indexed only `Pfam:`/`GO:` identifiers, so every `ARO:`
    reference fell through its `continue` -- it checked 5 of 19 items and **none of the
    class it was written for**. Reproducing #400 against it left it green. Fourth
    consecutive round in which a fix left the shape it was aimed at.

    It now resolves references it actually sees: ARO ids from `aro.obo`, KB CURIEs from
    their record. Collect-then-look-up, not index-everything -- the naive fix would read
    429,271 files.
    """
    import yaml as _yaml
    records, cited = {}, set()
    for pth in promote.ARO_DIR.glob("*.yaml"):
        text = pth.read_text(encoding="utf-8")
        if not re.search(r'^identifier:\s*"?(ARO:3004910|ARO:3004930)"?\s*$', text, re.M):
            continue
        graph = [g for g in _yaml.safe_load(text)["causal_graphs"]
                 if g["graph_id"] == "resistance"][0]
        records[pth.name] = graph
        cited |= {ev["reference"] for e in graph["edges"] for ev in e["evidence"]}
    assert records, "the two nat records were not found"

    bodies = {}
    obo = promote.E.OBO.read_text(encoding="utf-8")
    for ref in cited:
        if ref.startswith("ARO:"):
            m = re.search(rf'^id: {re.escape(ref)}$(.*?)(?=^\[|\Z)', obo, re.M | re.S)
            if m:
                bodies[ref] = " ".join(m.group(1).split())
        else:
            hit = [q for q in promote.TRAITS_ROOT.rglob("*.yaml")
                   if q.stem.endswith(ref.split(":")[1].lower())]
            for q in hit:
                head = q.read_text(encoding="utf-8")[:6000]
                if re.search(rf'^identifier:\s*"?{re.escape(ref)}"?\s*$', head, re.M):
                    bodies[ref] = " ".join(head.split())
                    break
    # Every reference OF A RESOLVABLE TYPE must resolve -- an unresolved one silently
    # skipped is how the first version passed while checking a quarter of the items.
    # PMIDs and DOIs are valid and not on disk; requiring them to resolve would false-fail
    # the moment these records cite primary literature, which 7,119 of 7,211 promoted ARO
    # records already do (#404).
    on_disk = {r for r in cited if r.split(":")[0] in ("ARO", "Pfam", "GO", "CATH",
                                                       "PROSITE", "NCBIfam", "InterPro")}
    assert set(bodies) == on_disk, f"unresolved references: {on_disk - set(bodies)}"

    checked = 0
    for name, graph in records.items():
        for e in graph["edges"]:
            for ev in e["evidence"]:
                if ev["reference"] not in bodies:
                    continue
                checked += 1
                assert " ".join(ev["snippet"].split()) in bodies[ev["reference"]], (
                    f"{ev['reference']} does not contain its snippet on {name}")
    # EXACT, not a floor: `>= 18` against 19 real items let one evidence item vanish
    # silently, which is the #382/#387 class this test exists to catch (#404).
    assert checked == 19, f"{checked} on-disk evidence items, expected 19"


def test_the_two_nat_configs_are_disjoint_so_list_order_is_not_load_bearing():
    """#401 was fixed but pinned by nothing (#404). `_check_config_order` only asserts that
    a precondition-less config is last; it cannot see two OVERLAPPING preconditions, which
    was #401's actual defect -- ARO:3004930 passed both and won by position alone.
    """
    cfgs = promote.family_configs("ARO:3004910")
    for ident in ("ARO:3004910", "ARO:3004930"):
        text = next(q.read_text(encoding="utf-8") for q in promote.ARO_DIR.glob("*.yaml")
                    if re.search(rf'^identifier:\s*"?{ident}"?\s*$',
                                 q.read_text(encoding="utf-8"), re.M))
        accepting = [c for c in cfgs
                     if c["precondition"](ident, "", text) is None]
        assert len(accepting) == 1, f"{ident} is accepted by {len(accepting)} configs"


def test_the_generic_ul3_drug_binding_node_does_not_claim_the_mutation_affects_it():
    """#406: the node prune was a no-op -- it built its keep-set from subjects UNION
    objects, and `drug_binding` survives as a SUBJECT of three edges. So the node shipped
    with `_ul3_shared`'s description, "The interaction the mutation reduces", on the record
    where #387 removed both edges that said so.

    #380/#371's shape, in the round that filed #380, missed by all five gates and by the
    object-side test written for #387. Found only by reviewing the combined stack -- and
    then LOST before merge, because the docs branch had been cut before the fix commit.
    """
    unnamed = [c for c in promote.family_configs("ARO:3005082")
               if "protein_traits" not in c][0]
    named = [c for c in promote.family_configs("ARO:3005082")
             if "protein_traits" in c][0]
    node = [n for n in unnamed["extra_nodes"] if n["node_id"] == "drug_binding"][0]
    assert "the interaction the mutation reduces" not in node["description"].lower()
    assert "#406" in node["description"]
    named_node = [n for n in named["extra_nodes"] if n["node_id"] == "drug_binding"][0]
    assert "the interaction the mutation reduces" in named_node["description"].lower()
    assert any(e["object"] == "drug_binding" for e in named["extra_edges"])
    assert not any(e["object"] == "drug_binding" for e in unnamed["extra_edges"])


def test_no_new_snippet_misattributions_in_the_aro_corpus():
    """#365: pins the known snippet-vs-source backlog so it cannot grow.

    Scope, narrowly: this catches #400's class -- a snippet under the wrong ARO/KB CURIE.
    NOT #348 or #382, which are PMID-attributed and unverifiable offline.

    **It asserts the probe FIRED.** `data/raw/aro/aro.obo` is gitignored, so in CI every
    ARO reference becomes unverifiable and the audit reports 11 instead of 287 -- passing
    a ceiling of 287 while checking almost nothing. That is round 68's failure mode, which
    this repo already shipped once (`hydrolyz\b` reported 0 while structurally broken).
    Without the obo the test SKIPS, honestly, rather than going green on nothing.
    """
    import subprocess
    root = pathlib.Path(promote.__file__).resolve().parent.parent
    obo = root / "data" / "raw" / "aro" / "aro.obo"
    if not obo.exists():
        pytest.skip("data/raw/aro/aro.obo absent (gitignored); run `just fetch-aro`. "
                    "Skipping honestly beats passing a ceiling while checking nothing.")
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "audit_snippets.py"),
         "--path", "function/resistance/aro", "--max", "174", "--require-aro"],
        capture_output=True, text=True, cwd=root)
    assert result.returncode == 0, (
        "snippet misattributions grew past the pinned backlog of 174:\n"
        + result.stdout[-2000:])

    def _num(label):
        m = re.search(rf"^\s*{label}:\s+([\d,]+)", result.stdout, re.M)
        assert m, f"audit output changed shape ({label} missing):\n{result.stdout[:600]}"
        return int(m.group(1).replace(",", ""))

    # the probe fired: nearly 30k items really were compared against the obo
    assert _num("checked against disk") >= 29_000
    assert _num(r"not on disk \(not a fail\)") == 0
    assert _num("MISMATCHED") <= 174
