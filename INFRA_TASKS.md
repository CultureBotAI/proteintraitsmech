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
  disposition: 'Source-limited and network-fetch-gated: RHEA (34,578 mechanism records) and GO (45,931 records) require receipt-locked UNIPROT_REST fetch generations; M-CSA (732 ungrounded active-site mechanism records) lacks residue_frame.json sequences; ARO (1,539 mechanism records) uses NCBI/CARD model accessions without 1:1 reviewed UniProt mappings; SFLD, PRINTS, and ECOD/SIFTS remain fail-closed at promotion.'
- task_id: proteintraitsmech-infra-0003
  summary: 'Repair upstream CDD definition defects on 8 held CDD records (cd00656, cd12872, cd16652, cd20534, cd16523, cd09530, cd21551, cd18592) and re-resolve their 10 held UniProt candidate examples.'
  status: open
  issue_url: https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition: 'Held at Stage 3 review per ground-protein-example fail-closed policy due to upstream CDD prose defects (truncated sentences, leaked PSSM-IDs, double spaces, or misleading domain labels); requires guarded definition repair and fresh resolution before promotion.'
```
<!-- mech-infra-tasks:end -->

## Tasks

### `proteintraitsmech-infra-0001` — Re-fetch `cross-mech-complex-20261013` with v2 `fragment` status and re-resolve `CPX-2267`

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 1, Stage 3 (`protein_examples`, `goal-3006`)
- **Status**: `deferred`
- **Issue**: https://github.com/CultureBotAI/proteintraitsmech/issues/1114 (with companion scientific holds https://github.com/CultureBotAI/proteintraitsmech/issues/1115 and https://github.com/CultureBotAI/proteintraitsmech/issues/1116; fragment-status gate landed in https://github.com/CultureBotAI/proteintraitsmech/issues/1081 / PR #1084)
- **Priority**: P1
- **Dependencies**: Live UniProt REST v2 fetch generation (`scripts/fetch_uniprot_grounding_registry.py --apply`) and independent scientific review of the 36-candidate ComplexPortal partition
- **Observation**:
  - `reports/uniprot-grounding/review-batches/cross-mech-complex-20261013` stages 36 `WHOLE_PROTEIN` subunit candidates across 25 `ComplexPortal` mechanism-graph records (33 recommended approvals across 22 records; 3 holds on `ComplexPortal:CPX-2267`, `ComplexPortal:CPX-1279`, and `ComplexPortal:CPX-2437`).
  - Because `cross-mech-complex-20261013.protein_registry.jsonl` and `cross-mech-complex-20261013.resolved.jsonl` were generated under a v1 fetch receipt prior to `#1081` / PR `#1084`, the resolved rows carry `uniprot_fragment: null`. Running `scripts/ground_uniprot_examples.py promote` fails closed at preflight with `missing:uniprot_fragment_status_for_whole_protein` for all 33 approved rows, and modifying `protein_registry.jsonl` in place is rightly rejected by `_verify_resolved_fetch_receipt_provenance` (`protein_registry sha256 mismatch`).
  - Additionally, `ComplexPortal:CPX-2267` was updated in PR `#1122` (`#1114`) to fix the superoxide dismutase reaction products, invalidating its historical preimage digest until re-resolved.
- **Desired outcome**:
  - Re-run `fetch_uniprot_grounding_registry.py` and `ground_uniprot_examples.py resolve` for the `cross-mech-complex-20261013` candidate cohort to capture `fragment: true|false` under a schema-v2 fetch receipt and bind the updated `CPX-2267` preimage, then complete independent review and promote the qualified ComplexPortal subunit examples.
- **Evidence paths**:
  - `reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl`
  - `reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.uniprot_fetch_receipt.json`
  - `reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml`
  - `research/cross-mech-protein-examples.md`
  - `scripts/ground_uniprot_examples.py`

### `proteintraitsmech-infra-0002` — Source-limited and writer/receipt blockers for mechanism-graph and corpus-wide protein examples

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 1, Stage 3 (`protein_examples`, `goal-3006`)
- **Status**: `deferred`
- **Issue**: https://github.com/CultureBotAI/proteintraitsmech/issues/652
- **Priority**: P2
- **Dependencies**: Receipt-locked `UNIPROT_REST` membership acquisition runs, `residue_frame.json` sequence cache expansion, and upstream coordinate/mapping tables
- **Observation**:
  - Across the 429,359 trait records in `data/traits/**/*.yaml` (including 39,616 records with `causal_graphs`), `scripts/ground_uniprot_examples.py` enforces strict source-asserted provenance and coordinate gates (`--require-qualified`):
    1. `RHEA` (`34,591` records, `34,578` with `causal_graphs`; `151` currently grounded with `QUALIFIED` examples) and `GO` (`45,931` records, `1` with `causal_graphs`; `467` currently grounded with `QUALIFIED` examples) use `WHOLE_PROTEIN` functional grounding via `uniprot_membership_snapshot.py` (`UNIPROT_REST`), which requires a cryptographically bound `.uniprot_fetch_receipt.json` and `uniprot_memberships.jsonl` per batch.
    2. `M-CSA` (`997` records, `996` with `causal_graphs`; `265` currently grounded with `QUALIFIED` examples) has `732` remaining records whose reference UniProt catalytic-residue accessions are absent from `data/raw/align_cache/residue_frame.json`, causing `resolve` to classify them as `BLOCKED` (`missing_protein_sequence`).
    3. `ARO` (`7,452` records, `1,539` with `causal_graphs`) stores antimicrobial-resistance reference sequences in `data/raw/card/aro.json` via NCBI protein/nucleotide accessions and CARD model IDs without a reviewed 1:1 Swiss-Prot accession + coordinate table, so `ground_uniprot_examples.py` has no `ARO` candidate emitter.
    4. `proteintraitsmech` foundational trait classes (`66` records, `46` with `causal_graphs`), `BioLiP` (`29` records, `6` with `causal_graphs`), `MetalPDB` (`15` records, `6` with `causal_graphs`), and `EC` (`8,225` records, `4` with `causal_graphs`) define general mechanism/site classes without source-shipped UniProt residue-interval tables in `data/raw/`.
    5. `SFLD` (`302` records), `PRINTS` (`2,106` records), and `ECOD` (`16,580` records) are explicitly fail-closed at promotion in `scripts/ground_uniprot_examples.py` (`SFLD` family HMM membership lacks residue coordinates; `PRINTS` fingerprint motif intervals are not bundled in InterPro `protein2ipr.dat`; `ECOD` PDB chain intervals require SIFTS PDB-to-UniProt residue mapping).
- **Desired outcome**:
  - Expand `data/raw/align_cache/residue_frame.json` to cover the remaining 732 `M-CSA` reference UniProt accessions, run receipted `UNIPROT_REST` membership batches for additional `RHEA`/`GO` cohorts, and add SIFTS / CARD-to-Swiss-Prot mapping support where exact organism, sequence, and claim scope can be preserved.
- **Evidence paths**:
  - `scripts/ground_uniprot_examples.py`
  - `scripts/uniprot_membership_snapshot.py`
  - `data/raw/align_cache/residue_frame.json`
  - `data/cross_mech/coverage.json`

### `proteintraitsmech-infra-0003` — Remediate upstream CDD prose defects on 8 held `CDD` records before promoting their 10 held candidates

- **Originating run / cycle / stage**: `mech-goal-sequence-20261019`, Cycle 1, Stage 3 (`protein_examples`, `goal-3006`)
- **Status**: `open`
- **Issue**: https://github.com/CultureBotAI/proteintraitsmech/issues/605
- **Priority**: P2
- **Dependencies**: Guarded trait-definition curation repair (`scripts/trait_record_writer.py`) and fresh `ground_uniprot_examples.py resolve` run on the 8 updated records
- **Observation**:
  - During Stage 3 review and promotion of `human-ecoli-yeast-complete-cdd-066of128` (147 approved examples promoted across 69 records) and `human-ecoli-yeast-complete-cdd-058of128` (136 approved examples promoted across 71 records), 10 candidate rows across 8 `CDD` records were held (`REJECTED` in the batch partition with explicit hold rationales) per `.claude/skills/ground-protein-example/SKILL.md` because their seeded upstream CDD definitions or labels have defects that would invalidate preimage hashes if edited mid-promotion:
    - Batch `066of128`: `CDD:cd00656` (`2` candidates: `UniProtKB:P13807`, `UniProtKB:P23368`; truncated sentence ending `"and in the."`) and `CDD:cd12872` (`1` candidate: `UniProtKB:P07741`; leaked internal CDD hierarchy string `"(PSSM-ID: 212423)"` in definition).
    - Batch `058of128`: `CDD:cd16652` (`1` candidate: `UniProtKB:P42345`; double-space typo in definition), `CDD:cd20534` (`1` candidate: `UniProtKB:O75643`; truncated trailing clause), `CDD:cd16523` (`1` candidate: `UniProtKB:Q8TDN6`; double-space typo), `CDD:cd09530` (`2` candidates: `UniProtKB:P52292`, `UniProtKB:O60684`; truncated sentence), `CDD:cd21551` (`1` candidate: `UniProtKB:Q9UBB4`; misleading `ATXN10` domain label for C-terminal 14-3-3 binding region), and `CDD:cd18592` (`1` candidate: `UniProtKB:Q14676`; truncated sentence).
- **Desired outcome**:
  - Apply a guarded definition/label repair to the 8 `CDD` records, re-run `ground_uniprot_examples.py resolve` against the updated record preimages, and promote the 10 held `Homo sapiens`, `Escherichia coli`, and `Saccharomyces cerevisiae` examples.
- **Evidence paths**:
  - `reports/uniprot-grounding/review-batches/human-ecoli-yeast-complete-cdd-066of128.review-decisions.jsonl`
  - `reports/uniprot-grounding/review-batches/human-ecoli-yeast-complete-cdd-058of128.review-decisions.jsonl`
  - `data/traits/sequence/domain/cdd/`

