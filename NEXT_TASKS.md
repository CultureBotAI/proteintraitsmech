# NEXT_TASKS

Durable backlog of deferred / next work for ProteinTraitsMech. **Maintenance
convention:** update an item when work on it starts or ships (mark
`DONE (YYYY-MM-DD, PR #NN)` or move it out); add any new work thread as its own
section with enough context to pick it up cold; keep absolute dates. Reconcile
against merged PRs + `git log` before trusting it.

_Last reconciled: 2026-07-21._

---

## Next up (actionable, ranked)

1. **Swiss-Prot multi-trait profiles (issue #7) — phase 1 shipped, phase 2 next.**
   Phase 1 DONE (2026-07-21, branch `swissprot-trait-profiles`): `ProteinProfile`
   schema class + `scripts/build_swissprot_profiles.py` (`just build-profiles`) →
   1,000-protein pilot (`data/profiles/`), the protein×trait matrix, with real
   trait↔GO correlation (kinase→ATP-binding, conf 1.0) and domain-architecture
   families (GPCR/homeobox/EF-hand). See `research/swissprot-trait-profiles-1.md`.
   Phase 2 DONE (2026-07-21, branch `swissprot-trait-tree`): scaled the matrix to
   20,000 reviewed human proteins (`--jsonl-only`; matrix gitignored, regenerable) +
   `scripts/train_trait_go_tree.py` (`just train-trait-tree`) — interpretable trait→GO
   decision trees (GPCR F1 0.90, olfactory 0.94, kinase/Ca/Zn/ATP 0.70–0.78; generic
   GO poorly, as expected). See `research/swissprot-trait-profiles-2.md`.
   Phase 3 DONE (2026-07-21): `scripts/analyze_trait_correlations.py`
   (`just trait-correlations`) — cross-axis correlation; **226 sequence signatures
   that always encode a specific fold** (conf ≥0.99, lift 500–625×) + 419
   sequence/structure→function rules. See `research/swissprot-trait-profiles-3.md`.
   **Phase 4 (next):** materialise the ≥0.99 sequence→fold rules as `trait_relations`
   between the signature and fold records (data-backed cross-axis overlay); multi-
   organism confirmation + held-out-organism decision-tree test; protein×trait browser
   map. Also feeds item 4 (shared Swiss-Prot exemplars → base overlay).

2. **Per-gene curation of the remaining ~1,219 resistance causal-graph drafts.**
   The family-level promotion is done (6,180 REVIEWED). The tail is genuinely
   per-gene: `ARO:0000031` gene-variant point mutants (gyrA/rpoB/16S/23S — each a
   different target protein), efflux subunits, two-component regulators, rRNA
   mutations, single genes. No shared family config fits — needs per-gene evidence.
   Tracker: `grep -rl "graph_id: resistance-draft" data/traits/function/resistance/aro/`;
   `just audit-graphs --strict` lists every snippet-pending edge. Skill:
   `edison-causal-graphs`; promoter: `promote_family_drafts.py` (`FAMILY_SNIPPETS`).

3. **Web design review — dataviz / artifact-design findings (issue #5).**
   Docs-site polish on `docs/browse.*` + landing. Self-contained.

4. **Empty base overlay `data/equivalence/seq_struct_alignment.tsv`.**
   Zero residue-overlap edges — a data-coverage fact, not a bug (0 shared proteins;
   see item 1). Two paths: (a) item 1 (shared Swiss-Prot exemplars), or (b) a
   structure-fold localizer using TED's stored `residue_range` on the AlphaFold
   frame. Path-2 co-membership (`seq_struct_comembership.tsv`, 13,400 edges) already
   connects signatures↔folds by CATH grounding instead.

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

- **Full `interpro,sifts` crawl to populate the base overlay** — measured ~33k API
  calls that would yield **0** base edges (SEQ signatures and STRUCT folds share no
  exemplar proteins). Superseded by item 1 / the co-membership overlay. Do not run.
- **Fold data-gaps (`CATH:3.40.50.300`, `CATH:3.20.20.70`, Qnr β-helix)** — turned
  out to be false alarms; all existed and the ABC/qnr graphs were re-grounded
  (2026-07-21). Closed.
