# NEXT_TASKS

Durable backlog of deferred / next work for ProteinTraitsMech. **Maintenance
convention:** update an item when work on it starts or ships (mark
`DONE (YYYY-MM-DD, PR #NN)` or move it out); add any new work thread as its own
section with enough context to pick it up cold; keep absolute dates. Reconcile
against merged PRs + `git log` before trusting it.

_Last reconciled: 2026-07-27._

---

## Next up (actionable, ranked)

1. **Per-gene curation of the remaining ~1,219 resistance causal-graph drafts.**
   The family-level promotion is done (6,180 REVIEWED). The tail is genuinely
   per-gene: `ARO:0000031` gene-variant point mutants (gyrA/rpoB/16S/23S — each a
   different target protein), efflux subunits, two-component regulators, rRNA
   mutations, single genes. No shared family config fits — needs per-gene evidence.
   Tracker: `grep -rl "graph_id: resistance-draft" data/traits/function/resistance/aro/`;
   `just audit-graphs --strict` lists every snippet-pending edge. Skill:
   `edison-causal-graphs`; promoter: `promote_family_drafts.py` (`FAMILY_SNIPPETS`).

2. **Swiss-Prot trait profiles (issue #7) — phases 1–14 shipped; phase 15 is small.**
   The thread is delivered end-to-end (protein×trait matrix → cross-axis rules →
   canonical_examples → 10-organism validation → residue-frame alignment). See
   "Recently shipped" for the summary and `research/swissprot-trait-profiles-{1..14}.md`
   for the detail. What is left is cleanup, not capability:
   - **Cache the ~10,238 permanently-absent UniProt accessions.** They return no
     result inside an otherwise-successful batch, so nothing records that they are
     dead and `fetch_residue_frame.py --top-up` re-requests them every run. Unlike
     the 9 malformed ones (#54, fixed) they fail silently.
   - **Check the 68 SUPERFAMILY-based refutations** from `residue_identity` against
     SUPERFAMILY↔CATH mappings — would either confirm them as equivalences or close
     them for good. `just verify-residue-identity` holds the current verdicts.
   - **Revisit the docs projection** now the exemplar payload has doubled
     (169,177 → 309,535 examples; detail buckets +33%). `_project_example` in
     `build_docs_index.py` is where to trim.

3. **Web design review — dataviz / artifact-design findings (issue #5).**
   Docs-site polish on `docs/browse.*` + landing. Self-contained.

## Refinements (small, opportunistic)

- **Confirm MCR / APH causal-graph folds** vs the crystal structures before treating
  those REVIEWED graphs as gold (`CATH:3.40.720.10` MCR, `CATH:3.90.1200` APH).
- **B3-specific MBL domain node**: `CDD:cd07708` exists if a GOB/B3-specific (rather
  than pan-MBL `Pfam:PF00753`) domain node is wanted on GOB-10 / subclass-B3 graphs.
- **STATE / PHENOTYPE causal nodes are label-only** (no CURIE) — a MONDO/HP/reaction-
  intermediate grounding could be added; audit reports them as warnings, not errors.
- **`scripts/audit_causal_graphs.py`** is now the mechanism-layer gate — run
  `just audit-graphs --strict` in CI if the causal layer should be gated on snippets.

## Recently shipped (DONE)

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
