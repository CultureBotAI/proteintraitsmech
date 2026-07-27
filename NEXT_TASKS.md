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
   Phase 4 DONE (2026-07-22): materialised the empirical cross-axis rules as
   `data/equivalence/trait_cooccurrence.tsv` (516 edges: 284 seq-encodes-fold +
   232 trait-implies-function, `biolink:related_to`, conf/lift in relation_source;
   auto-loaded by build_docs_index). See `research/swissprot-trait-profiles-4.md`.
   Phase 5 DONE (2026-07-24, branch `swissprot-canonical-examples`):
   `scripts/suggest_canonical_examples.py` (`just suggest-examples`) wrote
   **86,580 `canonical_examples` onto 44,929 trait records** (coverage 14.6% →
   25.6%; all 2,342 observed CATH fold records had none before). New
   `SWISSPROT_PROFILE` provenance; carriers ranked by cross-axis rule coverage,
   then focus / annotation depth weighted by axis. Only 671 picks are rule-backed —
   see the report for that limitation. See `research/swissprot-trait-profiles-5.md`.
   Phase 6 DONE (2026-07-25, branch `swissprot-multi-organism`): matrix rebuilt over
   four organisms (48,962 proteins: human/mouse/yeast/*E. coli*; `just build-profiles
   --organisms`). **Held-out-organism tests**: `scripts/test_rule_generalization.py`
   (`just test-rule-generalization`) shows seq-encodes-fold replicates at 96–99%
   outside human but trait-implies-function only 81–88%, failing on GO
   cellular-component / lineage-specific terms — that overlay is partly annotation
   practice, not mechanism. `train_trait_go_tree.py --holdout-taxon` shows macro-F1
   0.44 (mouse) → 0.32 (yeast) → 0.21 (*E. coli*) vs 0.44 random, i.e. a random split
   leaks orthologs. Overlay re-mined: 516 → 1,506 edges. Exemplars re-ranked with
   within-proteome normalisation (absolute GO counts handed picks to whichever
   community annotates hardest — mouse 16.1 vs human 12.6 mean GO).
   See `research/swissprot-trait-profiles-6.md` + `research/rule-generalization-1.md`.
   Phase 7 DONE (2026-07-25, branch `swissprot-balanced-rules`): function edges
   **split by GO aspect** (482 molecular-function / 148 biological-process / 65
   localization / 13 enzymatic-activity), so consumers can filter to the edges
   phase 6 showed replicate. Organism-balanced confidence is computed and emitted
   (`balanced=`, `organisms=`) but **gating on it is a null result** — pooling four
   proteomes already excludes every organism-specific rule phase 6 flagged, so
   `--min-balanced-conf` defaults off. Fixed a phase-4 bug where the miner filtered
   endpoints by CURIE prefix only, letting 27 edges point at GO terms with no
   record in the corpus. Overlay 1,506 → 1,479 edges, 0 dangling.
   See `research/swissprot-trait-profiles-7.md`.
   Phase 8 DONE (2026-07-25, branch `swissprot-protein-map`): **protein×trait map**
   (`just protein-map` → `docs/data/protein_map.json`, "Proteins" tab on
   docs/map.html) — 47,768 proteins, SVD→PaCMAP, coloured by organism, filterable
   by CATH class. Measured rather than eyeballed: neighbour purity (k=25) shows
   **CATH class organises the space 2.29× above chance vs organism's 1.42×**, and
   the 2-D projection understates both (2.09 / 1.36) rather than inventing them.
   Hand-reviewed the 65 `trait-implies-localization` edges → **keep all 65**: phase
   6's offenders are already gone from pooled mining, and what survives is
   domain→compartment (tubulin→microtubule, connexin→connexin complex). The 4
   single-proteome edges are lineage-specific by biology (pilus/fungal cell
   wall/keratin), so an automatic `organisms>=2` filter would delete correct edges.
   See `research/swissprot-trait-profiles-8.md`.
   Phase 9 DONE (2026-07-26, branch `swissprot-broaden-matrix`): matrix broadened to
   **10 organisms / 80,066 proteins** (adds Arabidopsis, Drosophila, C. elegans,
   B. subtilis, *M. jannaschii* (archaeon), *P. falciparum*); vertebrate share
   76% → 47%. Held-out test across the tree: **seq-encodes-fold 97.2% aggregate,
   100% in the archaeon**; trait-implies-function 84.8%, falling to **59% in the
   archaeon** — the phase-6 split, now unambiguous. Overlay 1,479 → 2,590 edges.
   **Withdrew a phase-8 claim**: "structure organises the protein map 1.6× more than
   organism" was an artefact of a 4-organism matrix; at 10 organisms it is 2.34× vs
   2.27×, i.e. about equal. Controlled check (same 4 organisms re-extracted)
   reproduces phase 8 exactly, so the measurement was right and the generalisation
   was not. New `just measure-map`: the corpus map is strongly source-stratified
   (within STRUCTURE, 99% of a record's neighbours share its database) — but the
   embedding still ranks a known cross-source equivalent #1 68% of the time, so it
   is not blind across sources. Definition-only embedding is equally stratified:
   the signal is house style in the prose, not identifiers.
   See `research/swissprot-trait-profiles-9.md`, `research/map-structure-1.md`.
   Phase 10 DONE (2026-07-26, branch `swissprot-residue-frame`): Path 1 was starved
   of *coordinates*, not exemplars — 34,227 proteins are shared by ≥2 records but only
   **33 records in the corpus had a stored sequence**. New
   `scripts/fetch_residue_frame.py` (`just fetch-residue-frame`) builds a gitignored
   sidecar (80,066 proteins, 530,588 FT intervals routed to trait categories) and a
   new `profile` provider in the aligner reads it: func-site edges **394 → 768
   (+95%)** over the offline providers. The overlay was **deliberately not
   regenerated** — a `stored,profile,biolip` run keeps 394 committed edges, loses 384
   InterPro-derived ones and adds 374, so writing it would destroy real data for a
   net −10. Ceiling found: only **23.2%** of records with exemplars are
   residue-localizable at all (`SEQ_DOMAIN` 34,781 needs InterPro; `FUNC_PATHWAY`
   15,452 is not a residue range). Source residualisation **fails structurally** —
   per-source centering cuts source lift 26% but axis lift 18%, because 25 of 28
   sources are axis-pure so most axis signal is between-source; axis is nonetheless
   real (1.83–1.85× within CDD/NCBIfam). Phase 6's ortholog-leakage claim **holds** at
   47% vertebrate (mouse 0.45 vs random 0.43).
   See `research/swissprot-trait-profiles-10.md`.
   Phase 11 DONE (2026-07-27, branch `swissprot-interpro-frame`): **Path 1 is now
   real.** `scripts/fetch_interpro_frame.py` (`just fetch-interpro-frame`) crawls
   InterPro **per protein** rather than per (signature, protein) and only for
   edge-capable proteins — 104,176 calls → 27,498 — into a sidecar (392,277
   signature matches) read by a new `interpro_frame` provider. Residue frame topped
   up to 98,922 proteins, which also unblocked 19,371 `SEQ_EPITOPE` records (items 2
   and 3 were one job: epitopes already carry the peptide as `sequence_pattern` and
   needed only the antigen's sequence — no localizer required).
   **`seq_struct_func_sites.tsv` 778 → 6,982 edges (clean superset, 0 lost);
   `seq_struct_alignment.tsv` 0 → 12,424 edges**, the base signature↔fold overlay
   populated for the first time, including **1,747 identical-residue-set
   `related_to`** links. 61,015 records localized (was 6,424). Found #54 (nine
   MetalPDB exemplars are `UNS…` placeholders, invisible to validate-all) and a
   regex of mine that skipped **27,325 records** because PyYAML writes list items at
   column 0 — phase 10's corpus figures understated by ~30% (exemplar proteins
   64,725 → 93,150). See `research/swissprot-trait-profiles-11.md`.
   Phase 12 DONE (2026-07-27, branch `swissprot-residue-curation`): adjudicated the
   1,747 identical-residue links. **None of them were in `cross_source.tsv`** — the
   residue frame found them independently of every identifier mapping. Checked each
   against InterPro's published Gene3D membership (`just verify-residue-identity`):
   **1,640 confirmed (97.6%)**, 40 refuted (those entries integrate *no* Gene3D
   signature — SUPERFAMILY-based), 0 unresolved. Confirmed pairs emitted as
   `data/equivalence/residue_identity.tsv` with `biolink:close_match` — relate-only,
   never a merge, per merge-within-axis. Support ceiling is 3 because
   `--max-examples 3` caps exemplars, so n=3 means *all* evidence agrees (1,052 of
   1,640). #54 closed: the nine `UNS…` exemplars are **rRNA chains** (16S/23S) that
   have no UniProt accession because they are not proteins — 34 removed across 22
   records, and the schema pattern is now UniProt's real accession syntax (verified
   to reject exactly those 9 of 93,150 values). `--dry-run` no longer hits the
   network. See `research/swissprot-trait-profiles-12.md`.
   **Phase 13 (next):** top up the residue frame with the **24,908** exemplar
   accessions still missing (phase 11's regex fix made 27,325 records visible) and
   rebuild the overlays; #57 (release-stamp the sidecars, refuse to resume across
   releases); check the 40 refuted pairs against SUPERFAMILY membership to close
   them.

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
