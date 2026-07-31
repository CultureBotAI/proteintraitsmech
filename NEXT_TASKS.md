# NEXT_TASKS

Durable backlog of deferred / next work for ProteinTraitsMech. **Maintenance
convention:** update an item when work on it starts or ships (mark
`DONE (YYYY-MM-DD, PR #NN)` or move it out); add any new work thread as its own
section with enough context to pick it up cold; keep absolute dates. Reconcile
against merged PRs + `git log` before trusting it.

_Last reconciled: 2026-07-30 (against `git log` + `just audit-graphs`; counts below
were re-measured, not carried forward)._

---

## Where the mechanism layer stands (2026-07-30)

**Every mechanism-rich source now carries causal graphs.** Rounds 12–17 took the
corpus from 0 to **39,647 records · 40,115 graphs · 347,473 nodes · 368,920 edges**,
audit **0 errors**, **368,920/368,920 edges snippet-cited**.

| source | records w/ graph | round | PR |
|---|--:|--:|---|
| Rhea | 18,558 | 16 | #89 *(open)* |
| ARO / CARD | 7,399 of 7,452 | 14 | #80, #84 |
| EC | 6,888 of 7,375 | 16 | #89 *(open)* |
| BioLiP | 5,571 | 15 | #86 |
| M-CSA | 1,003 | 12–13 | #77, #81, #82 |
| MetalPDB | 228 | 15 | #87 |

Round 17 added no new records — it **cross-linked** two existing sources: 427 Rhea
records gained 468 `catalytic_residues` graphs carrying the M-CSA residues that
perform them, joined on exact ChEBI set equality.

All 5,845 audit warnings are **ungrounded-node** warnings (5,845 = 347,473 −
341,628 grounded), unchanged across rounds 16 and 17. There are **zero**
missing-snippet and zero missing-`predicate_id` warnings left, so `--strict` is now
purely a grounding gate — a change from when the Refinements note below was written.

---

## Next up (actionable, ranked)

_Issue #7 (Swiss-Prot population + multi-trait families) was **closed 2026-07-27**
after 15 phases; the per-protein-YAML ask was answered with measurements rather
than deferred (see `research/docs-scalability-audit-1.md`). Issue #5 is all but
cleared._

1. **Per-gene curation of the remaining 1,219 resistance causal-graph drafts.**
   Still open — **re-counted 2026-07-30, unchanged at 1,219.** The family-level
   promotion is done (6,180 REVIEWED). PR #84 made every draft edge *cited* (the
   corpus is 100% snippet-covered), so these are no longer defective — they are
   simply still `graph_id: resistance-draft` rather than family-wired graphs.
   The tail is genuinely per-gene: `ARO:0000031` gene-variant point mutants
   (gyrA/rpoB/16S/23S — each a different target protein), efflux subunits,
   two-component regulators, rRNA mutations, single genes. No shared family config
   fits — needs per-gene evidence.
   Tracker: `grep -rl "graph_id: resistance-draft" data/traits/function/resistance/aro/`.
   Skill: `edison-causal-graphs`; promoter: `promote_family_drafts.py`
   (`FAMILY_SNIPPETS`).

2. ~~**Join Rhea reaction chemistry to the M-CSA catalytic residues that perform
   it.**~~ **DONE (2026-07-30, round 17, PR #89)** — 427 Rhea records gained 468
   `catalytic_residues` graphs / 2,871 edges, joined on **exact ChEBI set equality**
   (M-CSA reactant set == one Rhea side, product set == the other). Residue nodes are
   reused verbatim from the M-CSA records' SIFTS-resolved graphs.
   `scripts/build_rhea_mcsa_residue_graphs.py`; `research/causal-graphs-round17.md`.

   **This item's stated premise was wrong and the round corrected it.** It claimed
   the join would answer *"which residue attacks which substrate"*. **M-CSA cannot
   support that**: residue `roles` give a function, a `function_type`
   (reactant/interaction/spectator) and an EMO id but **never a target compound**;
   `marvin_xml` is a *filename* (max 107 chars), not atom-mapped arrow-pushing; and
   the only place a residue and a compound co-occur is free-text step prose that
   names compounds as jargon rather than by ChEBI. What was written instead is what
   M-CSA does assert: *this residue is causally responsible for this reaction*.

   **The residue→substrate edge is therefore still unwritten and still wanted** —
   see the follow-ups below. Do not re-attempt it from M-CSA.

3. **Close the residue→substrate gap from a source that actually states it.**
   The corpus still has **no `RESIDUE → CHEMICAL` edge**. Candidates, none yet
   assessed: UniProt `ACT_SITE` comments that name the attacked bond; MACiE / EzCatDB;
   Rhea's `rh:reactivePart` (used in round 16, but it describes generic
   `[protein]-…` participants, not catalytic residues). **First step is a source
   assessment, not a build** — the round-17 lesson is to check that the field exists
   before writing the task.

4. **Recover some of the 289 EC-agreeing M-CSA↔Rhea pairs whose ChEBI sets differ.**
   Round 17 dropped them deliberately (38% of EC-agreeing pairs do not share
   chemistry, which is why EC alone is not a join key). Some are genuine granularity
   differences — protonation state, conjugate acid/base, cofactor inclusion — that a
   ChEBI-hierarchy-aware comparison could close. The ChEBI ontology is already in
   `data/raw/chebi/`. Keep set equality as the strict tier and report any looser tier
   separately; do not merge the tiers.

5. **Swiss-Prot trait profiles (issue #7) — phases 1–14 shipped; issue NOT complete.**
   Delivered: protein×trait matrix over 10 proteomes, trait↔GO correlation,
   trait→function decision trees (held-out-organism validated), cross-axis feature
   correlations, residue-frame alignment. See "Recently shipped" and
   `research/swissprot-trait-profiles-{1..14}.md`.
   **Two of the issue's own asks remain open** (checked 2026-07-27, not assumed):
   - ~~**Multi-trait family clustering — never built.**~~ **DONE (2026-07-27,
     PR #63):** `scripts/cluster_trait_families.py` (`just cluster-families`)
     implements DiviK (doi:10.1186/s12859-022-05093-z) — divisive top-down
     splitting with local feature re-selection per node → **1,837 families with
     a shared trait core** over 29,313 proteins. Validated against held-out GO
     terms (excluded from the features): **81% of families have ≥80% of members
     sharing a GO term**, median 1.00. 57% of proteins are reported *unassigned*
     rather than forced into families. Was: the issue title says
     "+ build multi-trait families" and names doi:10.1186/s12859-022-05093-z.
     What exists is *exact signature-architecture matching* on the 1,000-protein
     pilot (45 families, `research/swissprot-trait-profiles-1.md` §Signal 2) —
     computed ad-hoc in that report, never a script. Phase 1 explicitly queued
     "replace exact-architecture matching with trait-set similarity (Jaccard /
     the s12859 method) for fuzzy families" and no phase did it. There is no
     clustering script in `scripts/`. The protein map (phase 8) is a 2-D
     projection, not clustering.
   - **Per-protein YAML coverage.** The issue asks for "a YAML record for each
     SwissProt protein". We have the `ProteinProfile` class and 1,000 committed
     YAMLs; the other 80,066 live in the gitignored `profiles.jsonl`, and
     Swiss-Prot has ~570k reviewed entries. The jsonl-only decision was made
     deliberately in phase 2 for scale — but it is a departure from the ask and
     should be confirmed rather than assumed settled.
   Remaining cleanup **DONE (2026-07-27, PR #65)** — see
   `research/swissprot-trait-profiles-15.md`:
   - Dead-accession cache: `--top-up` recorded 10,238 accessions UniProt does not
     serve into `_meta.absent` and now skips them (10,238 → 0 re-requests).
   - The 68 `residue_identity` refutations are **closed as not-actionable**: 46 are
     InterPro *domain* entries (never candidates), and the 22 SUPERFAMILY-based
     superfamilies cannot be confirmed on principle — SUPERFAMILY is SCOP-derived,
     CATH is independent, neither publishes a mapping, and InterPro's
     `overlaps_with` is co-occurrence (one superfamily "overlaps" a domain, a
     family and another domain). They stay `related_to` permanently.
   - Docs projection: exemplars were **58% of every detail bucket** (measured live;
     a stale local copy said 28% and gave the opposite answer). The browser now
     projects the top 5 of 8 — the cap was raised for protein sharing, not for
     display — cutting ~13% per bucket. Records keep all 8.

   **Scope call ANSWERED (2026-07-27, `research/docs-scalability-audit-1.md`):**
   issue #7 asks for "a YAML record for each SwissProt protein". Measured: a
   `ProteinProfile` averages 3,810 B, so 570k of them is ~2.2 GB and would take
   the repo to **980,494 tracked files — 2× the 500k threshold** where git and the
   GitHub UI degrade. **Keep the jsonl-only decision.** If more coverage must be
   committed, bucket it (~256 multi-record files, as the detail sidecars already
   do) rather than minting 570k tiny files. This is the `scalability-check`
   skill's tier D. Nothing else blocks closing #7.

6. **Web design review — dataviz / artifact-design findings (issue #5).**
   **Mostly cleared (2026-07-27, PR #68.)** CVD-unsafe palettes fixed via the
   `dataviz` validator: blue↔purple was ΔE 2.6 (protan), green↔teal ΔE 10.8
   (normal vision). Axis pills → reference slots 1–5, worst adjacent CVD ΔE 9.1
   light / 8.4 dark; the protein map → **domain of life** (3 hues, all-pairs
   ΔE 13.2 both modes) because no 10-hue set — and in dark mode no 5-hue set —
   passes all-pairs, with organism kept on the tooltip + CSV. Fixed a live
   regression found while measuring: six of ten proteomes were rendering as the
   same `#888` grey after phase 9 grew the matrix. Landing count fallbacks
   refreshed (were 47% stale).
   **Recorded as exceptions, not doing:** 4 landing cards (the corpus map is a
   real top-level destination with two tabs; reconciling to 3 would hide a view
   to satisfy a count); 1.4px canvas markers (the ≥8px rule is for dot plots — at
   78k points that is a solid blob, and the hover hit radius is already far
   larger than the mark). The Cayman→teal/amber rebrand stays **deferred by
   request**, and is all that remains on #5.

## Open threads from rounds 15–16 (context, ranked within themselves)

- **METPO records should link to TraitMech, not get graphs here.** The 70 METPO
  records sitting in `FUNC_ENZYMATIC_ACTIVITY` (acetogenesis, aerobic respiration)
  were the only enzymatic-activity records round 16 left without graphs, and
  deliberately: they are metabolic strategies, not protein traits, so their causal
  graphs belong in the sibling **TraitMech** repo. **The work is an outbound
  cross-reference**, not local graph authoring. Separately, their categorisation as
  `FUNC_ENZYMATIC_ACTIVITY` looks wrong — a `review-source-categories` question.
- **`chemical_participants` cannot express reaction direction (schema question).**
  All 18,558 Rhea records still say `role: SUBSTRATE_OR_PRODUCT`, which is *correct*
  for an undirected master reaction — but the round-16 graph now carries the side
  assignment (cited to Rhea's directional child), so the record's own field is
  strictly less informative than its graph. Decide whether the seeder gains a
  directional variant or the field defers to the graph. Do not "fix" the field by
  copying the graph: the master reaction genuinely has no direction.
- **BioLiP coverage: 445 records** whose PDB/chain/ligand is absent from the
  non-redundant `BioLiP_nr.txt`. The full BioLiP release would cover them (round 15).
- **MetalPDB coverage: 63 records** where no site matched both metal and nuclearity
  with a protein ligand (round 15).
- **689 EC records assert no chemistry** because Rhea has no reaction for them, and
  **487 more got no graph at all** (410 class-level `EC:x.x.x.-` nodes, 77 leaf
  entries with no reaction, no `DR` protein and no GO mapping). Rhea covers the EC
  hierarchy incompletely; nothing local fixes this.
- **1,063 multi-reaction EC classes show at most 3 of their reactions.** Stated in
  each graph's description — a display cap, not a data limit.

## Refinements (small, opportunistic)

- **Confirm MCR / APH causal-graph folds** vs the crystal structures before treating
  those REVIEWED graphs as gold (`CATH:3.40.720.10` MCR, `CATH:3.90.1200` APH).
- **B3-specific MBL domain node**: `CDD:cd07708` exists if a GOB/B3-specific (rather
  than pan-MBL `Pfam:PF00753`) domain node is wanted on GOB-10 / subclass-B3 graphs.
- **The 5,845 ungrounded causal nodes are the whole warning list** — 4,023 M-CSA
  STATE nodes (reaction intermediates), 1,817 BioLiP fusion-chain residues (BioLiP
  names several accessions for a chimeric chain and does not say which half a residue
  belongs to), 5 hand-curated intermediates. MONDO/HP/reaction-intermediate grounding
  would close the first group; the BioLiP group needs the source to disambiguate.
- **`just audit-graphs --strict` is now purely a grounding gate.** Snippet and
  `predicate_id` coverage both reached 100% in round 16, so turning `--strict` on in
  CI today would gate solely on the 5,845 ungrounded nodes above. Gating on snippets
  (the original intent of this note) can be done with plain `just audit-graphs`.

## Recently shipped (DONE)

- **Causal-graph mechanism layer, rounds 12–16** (2026-07-28 → 2026-07-30, PRs
  #77, #80–#89) — the mechanism layer went from 6,180 to **39,647** records with
  graphs and from ~0 to **366,049** cited edges, covering four distinct kinds of
  mechanism:
  - **Catalysis — M-CSA, 1,003 records** (rounds 12–13, PRs #77/#81/#82, closes
    #78/#79): stepwise mechanisms transcribed with residue roles; the last 265
    entries recovered via `mechanism_text`; residue frames reconciled to UniProt
    through SIFTS.
  - **Resistance — CARD/ARO** (round 14, PRs #80/#84): drug edges re-based on
    CARD's own assertion rather than ours, and every remaining edge given a
    snippet (corpus reached 100% cited). 1,219 drafts remain drafts — see Next up #1.
  - **Interaction — BioLiP 5,571 + MetalPDB 228** (round 15, PRs #86/#87): residue-
    level ligand contacts and metal coordination. Established the rule the later
    rounds run on — **do not quote your own seeder's text as evidence** — and the
    practice of verifying against a source's own internal redundancy.
  - **Transformation — Rhea 18,558 + EC 6,888** (round 16, **PR #89, open**):
    substrate→product chemistry. Rhea master reactions are undirected, so every
    input/output edge is cited to Rhea's *directional child*, which is where Rhea
    itself states which side is consumed. New `scripts/rhea_rdf.py` (stdlib
    streaming reader for `rhea.rdf.gz`); all 18,558 reactions verified by
    re-rendering Rhea's own equation string from the parsed participants.
  Reports: `research/causal-graphs-round{12..16}.md`.

- **Swiss-Prot trait profiles, phases 1–14** (2026-07-21 → 2026-07-27, PRs #29–#33,
  #37, #41, #45, #48, #51, #55, #58, #59, #61, #62). Protein×trait matrix over
  **10 proteomes / 80,066 proteins** (`build_swissprot_profiles.py`); cross-axis
  rule overlay `trait_cooccurrence.tsv` (2,590 edges, split by GO aspect);
  **309,535 `canonical_examples`** on 72,003 records (`suggest_canonical_examples.py`);
  held-out-organism validation (`test_rule_generalization.py` — seq-encodes-fold
  replicates 97.2% incl. 100% in an archaeon, trait-implies-function 84.8%);
  protein map (`build_protein_map.py`, "Proteins" tab); corpus-map structure audit
  (`measure_map_structure.py`); **residue-frame alignment** —
  `seq_struct_alignment.tsv` **0 → 16,350** and `seq_struct_func_sites.tsv`
  778 → **9,798** edges via the `profile` + `interpro_frame` providers and two
  release-stamped sidecars (`fetch_residue_frame.py`, `fetch_interpro_frame.py`,
  `sidecar.py`); **1,697 adjudicated `close_match`** CATH↔InterPro equivalences
  (`verify_residue_identity.py`) that no identifier mapping in the corpus had.
  Closed #54, #56, #57, #60. Reports: `research/swissprot-trait-profiles-{1..14}.md`.
  **Issue #7 itself stays open** — its clustering ask was never built (see Next up #2).

- **Causal-graph mechanism layer, rounds 1–11** (2026-07-21, PR #24/#28 + direct to
  main): `edison-causal-graphs` skill, `audit_causal_graphs.py` (`just audit-graphs`),
  `enrich_aro_resistance.py`, `draft_aro_causal_graphs.py`, `promote_family_drafts.py`.
  6,180 REVIEWED resistance graphs across all 6 CARD mechanism classes, every one
  routed through KB SEQUENCE/STRUCTURE trait records; audit 0 errors. Reports
  `research/causal-graphs-round{1..11}.md`.
- **Three-way SEQ/STRUCT/FUNC alignment + overlays** (2026-07-21, PR #24): Path-1
  residue-frame `seq_struct_func_sites.tsv` (778) + Path-2 co-membership
  `seq_struct_comembership.tsv` (13,400); `build_seq_struct_comembership.py`,
  interpro/sifts/biolip providers.
- **3did interfaces** (#23), **MEROPS cleavage sites** (#22), **orthology overlay**
  (#21, closes #20), **5 round-4 sources** (#17) — all 2026-07-20.
- **Deleted the superseded `seq-struct-alignment-step2` branch** (2026-07-21) — its
  providers were ported to `main`; its BioLiP record-mutation approach was replaced
  by the read-only `biolip` provider.

## Blocked / not actionable (kept for context — do not recommend as "next")

- ~~**Full `interpro,sifts` crawl to populate the base overlay** — ~33k API calls
  yielding 0 base edges; do not run.~~ **This was wrong and is now retracted
  (2026-07-27).** The measurement was sound for its moment and did not generalise:
  it assumed the *per-(signature, protein)* query shape and the pre-phase-5
  exemplar set, when signatures and folds genuinely shared no exemplars. Phase 11
  ran the crawl **per protein** over the exemplars phases 5–9 added and the base
  overlay went 0 → 12,424 edges (16,350 after phase 14). Kept here, struck through,
  because "do not run" sat in the backlog for a week over work that turned out to
  be the single largest win of the thread.
- **Fold data-gaps (`CATH:3.40.50.300`, `CATH:3.20.20.70`, Qnr β-helix)** — turned
  out to be false alarms; all existed and the ABC/qnr graphs were re-grounded
  (2026-07-21). Closed.
