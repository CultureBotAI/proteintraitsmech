---
name: proteintraitsmech-cross-mech-proteins
description: Review sibling Mech protein coverage in ProteinTraitsMech, publish accession and source links with available annotated sequences, and ground missing trait examples through the reviewed UniProt pipeline. Use inside ProteinTraitsMech for cross-Mech protein synchronization or completeness audits, not to curate sibling records.
---

# Cross-Mech proteins and trait examples

Read `CLAUDE.md`, `research/cross-mech-protein-examples.md`, and
`data/cross_mech/README.md`. Use the maintained recipes; do not create another
fleet list, accession extractor, or unguarded trait writer.

## Scope and discovery

1. Check the worktree and live PTM main/open PRs. Preserve unrelated edits and
   incorporate relevant merged grounding changes before measuring coverage.
2. Run `just scan-cross-mech-proteins --fetch --apply` for a requested refresh;
   omit `--apply` for an audit-only request. The fleet manifest owns membership
   and record globs; the scan reads pinned git objects, not sibling worktrees.
   Never edit sibling records as part of this task.
3. Run `just check-cross-mech-proteins --local` and inspect every unclassified
   path. Add a tested channel only after inspecting its schema and actual
   record context. Replay changed rules at the same pins with
   `just scan-cross-mech-proteins --at-manifest data/cross_mech/manifest.json --apply`.
4. Run `just audit-cross-mech-proteins`. Read all status buckets, including
   `TRAIT_NOT_IN_PTM` and `NOT_A_PTM_NAMESPACE`. A rejected or absent-trait pair
   is not a successful import. An old rejection must not be reversed without
   inspecting its rationale and changed evidence.

Keep every detected protein in the inventory, including compound targets,
substrates, graph endpoints, references, and text mentions. Explicit accessions
inside prose/UniProt URLs are references only; never infer family membership
from their surrounding description. Do not guess accessions from gene names,
family IDs, homologs, or a nearby taxon. Report these identifier-resolution gaps.
"All" means all recognized identifiers in the declared, pinned scope—not every
possible protein in the literature. Completeness/absence searches include hidden
and ignored files.

## Protein-first links and annotated sequences

For an existing published inventory, read `coverage.json` first and preserve its
optional input lanes and all review-batch prefixes. Use the full command in
`data/cross_mech/README.md`; the builder refuses to silently drop annotations or
review history. A minimal first build in a new output directory can use
`just build-cross-mech-inventory --apply`. If a local release-stamped UniProt
residue frame exists, add
`--residue-frame data/raw/align_cache/residue_frame.json` to include its available
sequence/feature tracks. Use the same inputs with `--check` for reproducibility.
This builds `data/cross_mech/{protein_inventory,protein_sequences}.jsonl` and
`coverage.{json,md}` without editing a trait or qualifying anything.

For fresh sequence/feature coverage beyond local caches, run a one-accession
canary using `just discover-cross-mech-sequences --all-proteins
--include-annotations --protein UniProtKB:<accession> --out <unique-staging-path>
--apply`, then omit `--protein` for the full cohort. Pass the resulting
`.entries.json` to the builder with `--uniprot-discovery`. Inactive accessions
remain unavailable; never substitute a replacement without an identity review.
Add `--candidate-queue reports/uniprot-grounding/cross-mech/candidates.jsonl`
to publish discovery-only trait links alongside canonical examples. The
candidate snapshot is not an adjudication ledger: retain and consult saved
review decisions before reconsidering a known rejection.
After finalizing decisions, pass `--review-batch <staging-prefix>` (repeatable)
to preserve digest-verified dispositions in the tracked inventory. A saved
approval and an installed canonical example are separate states.

- Join **all** existing PTM examples by exact accession, including isoform suffix,
  not only traits explicitly named by the sibling. Preserve legacy labels.
- Source links use sibling commit permalinks and JSON pointers/text spans.
- ProteinReference owns qualified sequences. A generic annotation is not a
  record-specific occurrence. Frame tracks must match both sequence and release;
  report rejected tracks, never silently graft them onto a newer sequence.
- Whole-protein functions have no fabricated residue interval. Localized
  occurrences retain exact bounds/residue sets and their evidence identifiers.
- Keep unavailable sequences and missing source coordinates visible. Raw downloads
  stay ignored; publish only normalized, provenance-bearing derived artifacts.
- Browser detail shows at most five examples, with qualified examples first.
  Verify completeness against the uncapped inventory and canonical records, not
  the visible page sample; never remove or duplicate records to evade that cap.

## Missing examples: guarded inclusion

Before any new qualification, read `.claude/skills/ground-protein-example/SKILL.md`
and its required grounding/schema references. It owns the release-pinned
select → fetch → resolve → review → promote contract and structured review output.

```bash
just discover-cross-mech-sequences                 # inspect request count
just discover-cross-mech-sequences --apply
just stage-cross-mech-candidates --apply
just select-cross-mech-review-batch <unique-id> --apply
```

Do not stop at sibling-named traits. For protein-first coverage, stage with
`--entry-annotations reports/uniprot-grounding/cross-mech/discovery.entries.json`
after full-cohort discovery. This adds exact GO/Rhea/ComplexPortal facts that
match existing PTM records, preserving `UNIPROT_EXACT_ENTRY_DISCOVERY` provenance
instead of attributing them to the sibling. These are still candidates; they
need the ordinary independent registry fetch, resolution and review. Signature
membership without source coordinates is not a whole-protein functional fact.

To prioritize proteins lacking any qualified example, stage a **separate** queue
with `--coverage-inventory data/cross_mech/protein_inventory.jsonl --out
reports/uniprot-grounding/cross-mech/protein-coverage-candidates.jsonl`. Keep the
unabridged queue. This selects one independent exact-entry candidate per uncovered
protein, preferring complex membership, then Rhea, then GO. It is a transparent
coverage priority, not evidence ranking or scientific approval. Pass this queue
explicitly to `scripts/select_uniprot_review_batch.py --queue ... --batch
cross-mech --batch-id <unique-id>` and preserve its source-stratified limits.
A rejected choice does not qualify the protein or authorize its next alternative.

Use the ordinary fetch-plan, fetch, resolve, finalize and promote recipes next.
Canary new network/provider behavior before a larger batch. Inspect the exact
target record and source assertion; do not approve rows just because resolution
passed. Review every inheritance, isoform, multi-component activity and unusual
coordinate case. Exact mapping through a pinned Rhea/GO source is allowed; label
similarity, a sibling citation, and generic feature/category overlap are not.

Review artifacts are staging, not qualification. Promotion requires **separate
explicit authorization in the current conversation**, plus the native evidence
and content gates. Never hand-edit resolved ledgers or durable registries. Reject
unsupported alternatives explicitly; retain their reasons. No automatic commit,
PR, external issues, merge, or branch deletion is authorized by this skill.

After authorized promotion, validate the changed records/registries, run writer
audit, regenerate the biophysical registry pin and browser artifacts if affected,
then rebuild both cross-Mech audit and protein inventory. Stop when every pair
in the pinned scope has a disposition; do not repeatedly retry unchanged evidence
or weaken the policy to force an empty backlog.

## Handoff

Report the fleet pins/scope, total distinct proteins, qualified vs legacy vs
discovery-only coverage, new examples promoted (not merely found), available
sequences and localized annotations, rejection/blocker counts, skill path and
checks actually run. Preserve a structured review for adjudicated candidates.
Never present an inventory or a passing mechanical resolver as a complete
scientific review. If inputs or providers block completion, name the remaining
bounded work rather than claiming all proteins are qualified.
