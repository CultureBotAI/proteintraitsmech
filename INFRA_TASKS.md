# ProteinTraitsMech infrastructure tasks

This versioned ledger collects repository requirements and upgrades discovered
during every goal. The workflow profile and its parent govern intake, stage 6
implementation, closure and cycle restart.

## Intake protocol

- Give each actionable task a stable ID such as `proteintraitsmech-infra-0001` and retain it
  across cycles. Record the originating run, cycle and goal, observation,
  desired outcome, evidence paths, priority, dependencies and status.
- Link each task to an actual issue in https://github.com/CultureBotAI/proteintraitsmech/issues.
  Search existing open and closed issues before creating one. If access fails,
  retain an explicit pending-link blocker; never invent an issue number or URL.
- Preserve resolved and deferred entries with their issue, implementation PR,
  validation and disposition. Do not overwrite previous cycle evidence.
- At stage 6, freeze a bounded snapshot, write a dependency-aware plan and
  acceptance criteria, implement selected work, validate, and complete the
  commit sequence, write the closure receipt and stop; only the supervisor
  dispatches another goal. New arrivals after the cutoff enter the next cycle;
  never expand the frozen task-ID scope. A new blocking prerequisite requires
  an explicit deferred disposition for the selected task. Carry unfinished work
  forward explicitly.

## Machine-readable task inventory

This fenced mapping is the inventory stage 6 freezes and reconciles. Each task
uses `task_id`, `summary`, `status` (`note`, `open`, `deferred`, or `resolved`),
optional `issue_url`, and optional `disposition`. Status `note` may have a
pending issue link; all other statuses require a real issue URL. Keep richer
notes below keyed by the same stable task ID.

<!-- mech-infra-tasks:start -->
```yaml
schema_version: '1.0.0'
tasks:
- task_id: proteintraitsmech-infra-0001
  summary: 'Re-fetch cross-mech-complex-20261013 under v2 UniProt receipt with fragment status and re-resolve CPX-2267 after #1122 chemistry repair so ComplexPortal mechanism-graph subunit examples can be promoted.'
  status: deferred
  issue_url: https://github.com/CultureBotAI/proteintraitsmech/issues/1114
  disposition: 'Blocked on live UniProt REST v2 fetch-generation refresh for cross-mech-complex-20261013 (to populate ProteinReference.fragment required by #1081/#1084) and independent scientific sign-off on the 36-candidate ComplexPortal partition (#1114, #1115, #1116).'
- task_id: proteintraitsmech-infra-0002
  summary: 'Acquire receipt-locked UniProt REST membership snapshots and expanded residue_frame.json sequences for mechanism-graph sources (RHEA, GO, M-CSA, ARO) and fail-closed signature/structure sources (SFLD, PRINTS, ECOD/SIFTS).'
  status: deferred
  issue_url: https://github.com/CultureBotAI/proteintraitsmech/issues/652
  disposition: 'Source-limited and network-fetch-gated: across 39,641 causal_graphs records in Cycle 2 Stage 3, RHEA (18,465 ungrounded of 18,558 with causal_graphs) and GO (GO:7770085) require receipt-locked UNIPROT_REST fetch generations; M-CSA (732 ungrounded QUALIFIED of 1,003 with causal_graphs) lacks residue_frame.json sequences; ARO (7,342 with causal_graphs) uses NCBI/CARD model accessions without 1:1 reviewed UniProt mappings; EC (1,104 ungrounded of 6,888 with causal_graphs) and 44 proteintraitsmech:* classes lack source-shipped UniProt residue-interval tables; SFLD, PRINTS, and ECOD/SIFTS remain fail-closed at promotion.'
- task_id: proteintraitsmech-infra-0003
  summary: 'Repair upstream CDD definition defects on 10 held CDD records (cd13344, cd14999, cd15894, cd17150, cd09530, cd16523, cd16652, cd18592, cd20534, cd21551) and re-resolve their 12 held UniProt candidate examples.'
  status: resolved
  issue_url: https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition: 'Resolved in Cycle 1 Stages 5-6 (#1172, PR #1173): repaired upstream CDD prose defects on all 10 held CDD records plus CDD:cd00104 and CDD:cd00959 (with transactional re-binding of 41 durable qualified_record_bindings receipts), restored read-only v1 signature-only fetch receipt verification in scripts/fetch_uniprot_registry.py, re-resolved batches 058of128 and 066of128, and promoted all 12 held Homo sapiens and Saccharomyces cerevisiae examples across the 10 repaired CDD records.'
- task_id: proteintraitsmech-infra-0004
  summary: 'Key causal_graphs list-union deduplication in scripts/record_io.py merge_on_reseed by graph_id so seeder upgrades to an existing causal graph update nodes and edges in place rather than appending a duplicate graph_id.'
  status: note
  disposition: 'Observed in Cycle 2 Stage 2 (causal_graphs, goal-167a): _union_list_keys in scripts/record_io.py deduplicates causal_graphs by full JSON serialization rather than graph_id identity; upgrading an existing graph_id in seed_foundational_traits.py requires replacing matching graph_id entries in place while preserving distinct curator-added graph_id entries.'
- task_id: proteintraitsmech-infra-0005
  summary: 'Check stem-prefixed <batch>.protein_registry.jsonl siblings before unprefixed directory defaults in scripts/ground_uniprot_examples.py main() (lines 5330-5338) and re-resolve partially superseded localized review batches (cnp-017..020, cdd-042..050, prosite-065).'
  status: note
  disposition: 'Observed in Cycle 2 Stage 3 (protein_examples, goal-9220): (1) in scripts/ground_uniprot_examples.py:5330-5338, main() defaults args.protein_registry, args.evidence_registry, args.membership_registry, and args.sifts_registry to unprefixed args.resolved.resolve().parent / "protein_registry.jsonl" (etc.) rather than checking stem-prefixed <batch>.protein_registry.jsonl siblings first, so _provider_cache (line 2953) skips non-existent unprefixed files in review-batches/ and _verify_provider_evidence (line 3023) fails with stale:provider_missing:protein_registry unless passed explicitly; (2) remaining localized batches cnp-017..020, cdd-042..050, and prosite-065 contain valid unpromoted rows alongside rows superseded by later promotions, requiring re-resolution against current record preimages.'
```
<!-- mech-infra-tasks:end -->

## Tasks

### `proteintraitsmech-infra-0001` — Re-fetch `cross-mech-complex-20261013` with v2 `fragment` status and re-resolve `CPX-2267`

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 1, Stage 3 (`protein_examples`, `goal-3006`)
- **Status**: `deferred`
- **Issue**: https://github.com/CultureBotAI/proteintraitsmech/issues/1114 (with companion scientific holds https://github.com/CultureBotAI/proteintraitsmech/issues/1115 and https://github.com/CultureBotAI/proteintraitsmech/issues/1116; fragment-status gate landed in https://github.com/CultureBotAI/proteintraitsmech/issues/1081 / PR #1084)
- **Priority**: P1
- **Dependencies**: Live UniProt REST v2 fetch generation (`scripts/fetch_uniprot_registry.py --apply`) and independent scientific review of the 36-candidate ComplexPortal partition
- **Observation**:
  - `reports/uniprot-grounding/review-batches/cross-mech-complex-20261013` stages 36 `WHOLE_PROTEIN` subunit candidates across 25 `ComplexPortal` mechanism-graph records (33 recommended approvals across 22 records; 3 holds on `ComplexPortal:CPX-2267`, `ComplexPortal:CPX-1279`, and `ComplexPortal:CPX-2437`).
  - Because `cross-mech-complex-20261013.protein_registry.jsonl` and `cross-mech-complex-20261013.resolved.jsonl` were generated under a v1 fetch receipt prior to `#1081` / PR `#1084`, the resolved rows carry `uniprot_fragment: null`. Running `scripts/ground_uniprot_examples.py promote` fails closed at preflight with `missing:uniprot_fragment_status_for_whole_protein` for all 33 approved rows, and modifying `protein_registry.jsonl` in place is rightly rejected by `_verify_resolved_fetch_receipt_provenance` (`protein_registry sha256 mismatch`).
  - Additionally, `ComplexPortal:CPX-2267` was updated in PR `#1122` (`#1114`) to fix the superoxide dismutase reaction products, invalidating its historical preimage digest until re-resolved.
  - **Cycle 2 Stage 3 (`goal-9220`) Update**: Exhaustive preflight of all 235 review batches in `reports/uniprot-grounding/review-batches/` confirmed that all remaining unpromoted `WHOLE_PROTEIN` batches (`cross-mech-complex-20261013`, `ready-local-review-077-2026-03-panther`, `repair-existing-local-review-177-2026-03-topup`, `repair-existing-local-review-179-2026-03-topup`, `human-ecoli-yeast-repair-mixed-038`, `human-ecoli-yeast-repair-mixed-040`, `human-ecoli-yeast-repair-mixed-042`, `human-ecoli-yeast-repair-panther-021..037`, `human-ecoli-yeast-complete-panther-001..005`, `human-ecoli-yeast-complete-go-008..021`, `human-ecoli-yeast-complete-rhea-035..054`, and `human-ecoli-yeast-complete-complexportal-006`) fail closed with `missing:uniprot_fragment_status_for_whole_protein` because their v1 fetch receipts lack `ProteinReference.fragment`.
- **Desired outcome**:
  - Re-run `scripts/fetch_uniprot_registry.py` and `scripts/ground_uniprot_examples.py resolve` for the `cross-mech-complex-20261013` candidate cohort (and remaining `WHOLE_PROTEIN` cohorts) to capture `fragment: true|false` under a schema-v2 fetch receipt and bind the updated `CPX-2267` preimage, then complete independent review and promote the qualified examples.
- **Evidence paths**:
  - `reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl`
  - `reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.uniprot_fetch_receipt.json`
  - `reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml`
  - `research/cross-mech-protein-examples.md`
  - `research/stage3-protein-examples-cycle2-coverage-2026-10-25.md`
  - `scripts/fetch_uniprot_registry.py`
  - `scripts/ground_uniprot_examples.py`

### `proteintraitsmech-infra-0002` — Source-limited and writer/receipt blockers for mechanism-graph and corpus-wide protein examples

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 1, Stage 3 (`protein_examples`, `goal-3006`)
- **Status**: `deferred`
- **Issue**: https://github.com/CultureBotAI/proteintraitsmech/issues/652
- **Priority**: P2
- **Dependencies**: Receipt-locked `UNIPROT_REST` membership acquisition runs, `residue_frame.json` sequence cache expansion, and upstream coordinate/mapping tables
- **Observation**:
  - Across the 429,377 trait records in `data/traits/**/*.yaml` (including **39,641 records with `causal_graphs`** after Cycle 2 Stages 1–3; durable `protein_registry.jsonl`: **13,208** proteins; durable `qualified_record_bindings.jsonl.d/`: **22,314** bindings after promoting `human-ecoli-yeast-repair-mixed-039` across 971 `InterPro` records in Cycle 2 Stage 3), `scripts/ground_uniprot_examples.py` enforces strict source-asserted provenance and coordinate gates (`--require-qualified`):
    1. `RHEA` (`34,591` records, `18,558` with `causal_graphs`; `93` with `causal_graphs` currently have `canonical_examples` and `18,465` have `0` examples) and `GO` (`45,931` records, `1` with `causal_graphs` — `GO:7770085` protocatechuate 3,4-dioxygenase complex, `0` examples) use `WHOLE_PROTEIN` functional grounding via `uniprot_membership_snapshot.py` (`UNIPROT_REST`), which requires a cryptographically bound v2 `.uniprot_fetch_receipt.json` (with `fragment` status) and `uniprot_memberships.jsonl` per batch.
    2. `M-CSA` (`1,003` records in `data/traits/structure/active_site/mcsa`, all `1,003` with `causal_graphs` and `canonical_examples`: `265` grounded with `QUALIFIED` examples + `738` legacy seeded) has `732` remaining records whose reference UniProt catalytic-residue accessions are absent from `data/raw/align_cache/residue_frame.json`, causing `resolve` to classify them as `BLOCKED` (`missing_protein_sequence`).
    3. `ARO` (`7,452` records, `7,342` with `causal_graphs`, `0` with `canonical_examples`) stores antimicrobial-resistance reference sequences in `data/raw/card/aro.json` via NCBI protein/nucleotide accessions and CARD model IDs without a reviewed 1:1 Swiss-Prot accession + coordinate table, so `ground_uniprot_examples.py` has no `ARO` candidate emitter.
    4. `EC` (`8,225` records, `6,888` with `causal_graphs`: `5,784` with `canonical_examples` and `1,104` with `0` examples) has `1,104` mechanism-graph records lacking Swiss-Prot `DR` cross-references in `data/raw/expasy/enzyme.dat` and lacks source-shipped residue intervals for `QUALIFIED` promotion.
    5. `BioLiP` (`5,572` records with `causal_graphs`, `100%` with `canonical_examples`), `MetalPDB` (`228` records with `causal_graphs`, `100%` with `canonical_examples`), and `UNIPROT_FT_SEQ_*` (`5` records with `causal_graphs`, `100%` with 15 `canonical_examples` each) are 100% populated with legacy/source examples, while the **44 `proteintraitsmech:*` single-file mechanism-graph classes** (`8` root/cavity classes + `8` Cycle 1 Stage 1 structural leaf classes + `28` Cycle 2 Stage 1 sequence feature leaf classes) define general mechanism/site classes without source-shipped UniProt residue-interval tables in `data/raw/`.
    6. `SFLD` (`302` records), `PRINTS` (`2,106` records), and `ECOD` (`16,580` records) are explicitly fail-closed at promotion in `scripts/ground_uniprot_examples.py` (`SFLD` family HMM membership lacks residue coordinates; `PRINTS` fingerprint motif intervals are not bundled in InterPro `protein2ipr.dat`; `ECOD` PDB chain intervals require SIFTS PDB-to-UniProt residue mapping).
- **Desired outcome**:
  - Expand `data/raw/align_cache/residue_frame.json` to cover the remaining 732 `M-CSA` reference UniProt accessions, run receipted v2 `UNIPROT_REST` membership batches for additional `RHEA`/`GO` cohorts, and add SIFTS / CARD-to-Swiss-Prot mapping support where exact organism, sequence, and claim scope can be preserved.
- **Evidence paths**:
  - `scripts/ground_uniprot_examples.py`
  - `scripts/uniprot_membership_snapshot.py`
  - `data/raw/align_cache/residue_frame.json`
  - `data/cross_mech/coverage.json`
  - `research/cycle2-stage1-add-records-frontier.md`
  - `research/stage3-protein-examples-cycle2-coverage-2026-10-25.md`

### `proteintraitsmech-infra-0003` — Remediate upstream CDD prose defects on 10 held `CDD` records before promoting their 12 held candidates

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 1, Stage 3 (`protein_examples`, `goal-3006`)
- **Status**: `resolved`
- **Issue**: https://github.com/CultureBotAI/proteintraitsmech/issues/605 (batch tracking in https://github.com/CultureBotAI/proteintraitsmech/issues/1167; remediation tracked in https://github.com/CultureBotAI/proteintraitsmech/issues/1172 / PR #1173)
- **Priority**: P2
- **Dependencies**: Guarded trait-definition curation repair (`scripts/trait_record_writer.py`, `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`) and fresh `scripts/ground_uniprot_examples.py resolve` + `promote` run on the updated records
- **Observation**:
  - During Stage 3 review and promotion of `human-ecoli-yeast-complete-cdd-066of128` (`147` approved examples promoted across `69` records out of `294` decision rows across `91` records) and `human-ecoli-yeast-complete-cdd-058of128` (`136` approved examples promoted across `71` records out of `289` decision rows across `104` records), **12 target-taxon (`Homo sapiens` / `Saccharomyces cerevisiae`) candidate rows across 10 `CDD` records** were held (`REJECTED` in the batch partition with `HOLD_PROSE_REVIEW` / `HOLD_FOR_PROSE_CURATION` notes, alongside non-target-taxon `DEFER_OUTSIDE_TARGET_TAXA` and pre-existing `DEFER_ALREADY_SATISFIED` rows) per `.claude/skills/ground-protein-example/SKILL.md` because their seeded upstream CDD definitions had biological/prose defects that would invalidate preimage hashes if edited mid-promotion:
    - Batch `066of128` (**4 held CDD records, 4 target-taxon candidate rows**):
      1. `CDD:cd13344` (`1` candidate: `UniProtKB:Q9Y216`, human MTMR7 at `1-103`): MTMR7 PH-GRAM record switched to MTMR6 binding/activity wording (`HOLD_PROSE_REVIEW`).
      2. `CDD:cd14999` (`1` candidate: `UniProtKB:Q9UKP6`, human UTS2R at `53-326`): source-derived urotensin-II receptor definition gave a conflicting hypocretin-receptor alias (`HOLD_PROSE_REVIEW`).
      3. `CDD:cd15894` (`1` candidate: `UniProtKB:P60880`, human SNAP25 at `10-82`): generalized a transmembrane domain to Qb/Qc SNARE proteins whereas SNAP25 has two SNARE domains and palmitoylation (`HOLD_PROSE_REVIEW`).
      4. `CDD:cd17150` (`1` candidate: `UniProtKB:A2VCK2`, human DCDC2B at `9-87`): DCDC2B-specific first-domain record switched to DCDC2 gene/disease prose and started with typo `Dublecortin-like domain 1` (`HOLD_PROSE_REVIEW`).
    - Batch `058of128` (**6 held CDD records, 8 target-taxon candidate rows**):
      1. `CDD:cd09530` (`1` candidate: `UniProtKB:Q9P1V8`, human SAMD15/FAM15A at `543-609`): `SAM_Samd14` / `"SAM domain of SAMD14 subfamily"` nomenclature conflict with its sole human match `SAMD15` (`HGNC:18631`, whereas human `SAMD14` `Q8IZD0` matches `cd09512`; `HOLD_FOR_PROSE_CURATION`).
      2. `CDD:cd16523` (`1` candidate: `UniProtKB:Q8WY64`, human MYLIP/IDOL at `383-434`): sentence 2 claimed blanket proteasomal degradation of MRLC, LDLR, VLDLR, and LRP8, contradicting sentence 4 and primary literature (`DOI:10.1074/jbc.M110.123729`) showing lysosomal MVB degradation of LDLR/VLDLR/LRP8 (`HOLD_FOR_PROSE_CURATION`).
      3. `CDD:cd16652` (`1` candidate: `UniProtKB:Q12508`, yeast RMD5/GID2 at `359-406`): malformed substrate prose (`"fructose-1, 6-bisphosphate by fructose-1, 6-bisphosphatase"`) in enzyme list (`HOLD_FOR_PROSE_CURATION`).
      4. `CDD:cd18592` (`3` candidates: `UniProtKB:O15440` ABCC5 at `181-467`, `UniProtKB:Q96J66` ABCC11 at `165-451`, `UniProtKB:Q96J65` ABCC12 at `125-411`): upstream CDD prose conflated `MRP7` (`ABCC10`) with `CFTR` (`ABCC7`) and overstated anticancer-drug export for `ABCC12`/`MRP9` (`HOLD_FOR_PROSE_CURATION`).
      5. `CDD:cd20534` (`1` candidate: `UniProtKB:Q8N1B3`, human CCNQ/FAM58A at `26-135`): conflated STAR-syndrome Cyclin-M/Cyclin-Q (`CCNQ`/`FAM58A`) with the `CNNM1-4` (`ACDP`) magnesium-transporter family (`HOLD_FOR_PROSE_CURATION`).
      6. `CDD:cd21551` (`1` candidate: `UniProtKB:Q15022`, human SUZ12 at `563-684`): conflated SUZ12's indirect H3K9 effect (`DOI:10.1007/s10577-007-1126-1`) with PRC2/EZH2 H3K27me3 catalysis (`HOLD_FOR_PROSE_CURATION`).
  - Additionally, two promoted CDD records carried minor non-blocking upstream CDD typographical defects in `definition` (`CDD:cd00104`: `chyomotrypsin` typo and listing `avian ovomucoids` in the target protease list; `CDD:cd00959`: duplicated opening sentence) that required transactional re-binding of their `qualified_record_bindings.jsonl.d/` preimage hashes.
- **Resolution & Validation**:
  - In Stage 5 ([#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172), PR [#1173](https://github.com/CultureBotAI/proteintraitsmech/pull/1173)) and Stage 6, all 12 CDD records (`10` held + `CDD:cd00104` and `CDD:cd00959`) were added to `ERRATA` in `scripts/cdd_errata.py` and repaired via `scripts/repair_cdd_errata.py --apply` with transactional re-binding of 41 durable `qualified_record_bindings.jsonl.d/` receipts.
  - Read-only verification of pre-#971 20-field signature-only `schema_version=1` UniProt fetch plans was restored in `scripts/fetch_uniprot_registry.py` (`LEGACY_SIGNATURE_RETURN_FIELDS`), batches `human-ecoli-yeast-complete-cdd-058of128` and `human-ecoli-yeast-complete-cdd-066of128` were re-resolved and finalized (`144` approved across `77` records in `058of128`; `151` approved across `73` records in `066of128`), and all 12 held `Homo sapiens` / `Saccharomyces cerevisiae` examples were promoted into the 10 repaired `CDD` records via `scripts/ground_uniprot_examples.py promote --apply`.
- **Evidence paths**:
  - `scripts/cdd_errata.py`
  - `scripts/repair_cdd_errata.py`
  - `scripts/fetch_uniprot_registry.py`
  - `reports/uniprot-grounding/review-batches/human-ecoli-yeast-complete-cdd-066of128.review-decisions.jsonl`
  - `reports/uniprot-grounding/review-batches/human-ecoli-yeast-complete-cdd-058of128.review-decisions.jsonl`
  - `data/traits/sequence/domain/cdd/`

### `proteintraitsmech-infra-0004` — Key `causal_graphs` list-union deduplication in `scripts/record_io.py` by `graph_id`

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 2, Stage 2 (`causal_graphs`, `goal-167a`)
- **Status**: `note`
- **Issue**: pending-link (non-blocking writer ergonomics note; related to causal-graph curation in https://github.com/CultureBotAI/proteintraitsmech/issues/1066)
- **Priority**: P3
- **Dependencies**: None
- **Observation**:
  - `scripts/record_io.py` defines `_MERGE_LIST_UNION_KEYS = ("xrefs", "go_terms", "evidence", "detection_methods", "canonical_examples", "causal_graphs", "parent_traits", "aliases")` and deduplicates list items in `_union_list_keys` by full canonical JSON serialization (`json.dumps(item, sort_keys=True)`).
  - When a registered seeder (`scripts/seed_foundational_traits.py`, `scripts/seed_localstructuralfeature.py`, `scripts/seed_uniprot_peptide_classes.py`) upgrades nodes, edges, or snippet evidence inside an existing `CausalGraph` while keeping the same `graph_id`, running `merge_on_reseed(fresh, on_disk)` treats the old and new `CausalGraph` dicts as distinct items and appends a second graph with the same `graph_id` (which then fails `scripts/audit_causal_graphs.py` with `duplicate graph_id`).
- **Desired outcome**:
  - In `_union_list_keys` (`scripts/record_io.py`), when `key == "causal_graphs"` and items are dicts containing a non-empty `graph_id`, deduplicate or merge by `graph_id` (preferring the updated graph or unioning its `nodes` by `node_id` and `edges` by `(subject, predicate, object)`) while still preserving any curator-added `CausalGraph` with a distinct `graph_id`.
- **Evidence paths**:
  - `scripts/record_io.py`
  - `scripts/seed_foundational_traits.py`
  - `scripts/seed_localstructuralfeature.py`
  - `scripts/seed_uniprot_peptide_classes.py`
  - `research/causal-graphs-round125.md`

### `proteintraitsmech-infra-0005` — Check stem-prefixed `<batch>.protein_registry.jsonl` siblings in `scripts/ground_uniprot_examples.py` `main()` and re-resolve partially superseded localized review batches

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 2, Stage 3 (`protein_examples`, `goal-9220`)
- **Status**: `note`
- **Issue**: pending-link (non-blocking promoter CLI ergonomics and batch re-resolution note; related to https://github.com/CultureBotAI/proteintraitsmech/issues/652)
- **Priority**: P3
- **Dependencies**: None
- **Observation**:
  1. `scripts/ground_uniprot_examples.py promote -h` documents `--protein-registry`, `--evidence-registry`, `--membership-registry`, and `--sifts-registry` as `(default: beside --resolved)`, and `main()` (`scripts/ground_uniprot_examples.py:5330-5338`) populates those defaults before calling `promote(args)` using unprefixed directory-level filenames (`args.resolved.resolve().parent / "protein_registry.jsonl"`, `"occurrence_evidence.jsonl"`, `"uniprot_memberships.jsonl"`, `"sifts_mappings.jsonl"`). When `args.resolved` is a stem-prefixed review-batch file such as `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.resolved.jsonl`, the sibling artifacts on disk are `<batch>.protein_registry.jsonl` and `<batch>.occurrence_evidence.jsonl`, whereas unprefixed `review-batches/protein_registry.jsonl` does not exist. Consequently, `_provider_cache` (`line 2953: if not path.is_file(): continue`) skips loading the provider registries and `_verify_provider_evidence` (`line 3023`) rejects every row with `stale:provider_missing:protein_registry` unless `--protein-registry` and `--evidence-registry` are passed explicitly.
  2. Several historical `LOCALIZED` review batches (`human-ecoli-yeast-repair-cnp-017..020`, `repair-existing-local-review-042..050-2026-03-cdd`, and `repair-existing-local-review-065-2026-03-prosite`) contain valid unpromoted `InterPro`/`CDD`/`PROSITE` candidate rows alongside rows whose target records were subsequently promoted by another batch (`conflict:different_qualified_trait_occurrence` or `stale:record_changed_since_resolve`). Because `promote` fails closed at whole-batch preflight if any approved row's preimage is stale or conflicts with a different promoted protein occurrence, promoting the remaining ungrounded rows from those batches requires re-running `resolve` against current on-disk record preimages.
- **Desired outcome**:
  - In `scripts/ground_uniprot_examples.py:5330-5338`, check for stem-prefixed `<batch>.protein_registry.jsonl` (and corresponding `.occurrence_evidence.jsonl`, `.uniprot_memberships.jsonl`, `.sifts_mappings.jsonl`) siblings beside `--resolved` before falling back to unprefixed `protein_registry.jsonl`, and re-resolve the remaining ungrounded candidates in `cnp-017..020`, `cdd-042..050`, and `prosite-065` against current on-disk record preimages.
- **Evidence paths**:
  - `scripts/ground_uniprot_examples.py`
  - `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.resolved.jsonl`
  - `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-017.resolved.jsonl`
  - `research/stage3-protein-examples-cycle2-coverage-2026-10-25.md`



