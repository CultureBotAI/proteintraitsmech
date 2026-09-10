---
name: ground-protein-example
description: Add a release-pinned canonical protein example, with source-asserted trait coordinates, to ProteinTraitsMech trait records through the fail-closed candidate to resolve to review to promote workflow. Use when asked to add/ground/qualify a protein exemplar for a record, to prefer a bacterial or archaeal exemplar, or to get trait coordinates onto a named trait. Read-only and dry-run by default; promotion requires separate explicit human authorization.
allowed-tools: Bash, Read, Grep, Glob
metadata:
  category: grounding
  requires_database: false
  requires_internet: true
  version: 1.0.0
---

# Ground a protein example onto a trait record

Attach a UniProt exemplar to a `ProteinTraitRecord` such that the example is
`QUALIFIED` — a release-pinned accession, a checksummed sequence, and a
`TraitOccurrence` that locates *this record's* trait on *that* protein with
dereferenceable evidence. Anything short of that is a `LEGACY_UNVERIFIED`
example, which is not evidence that the record's trait occurs on the protein.

The authority for this workflow is
`research/uniprot-organism-protein-grounding-plan.md`. Read its current
execution checkpoint before starting; it records which batches are staged,
which durable claims are hard debt, and what is blocked.

## Boundaries

- **Coordinates are never computed here.** Every occurrence interval is copied
  from a source that already asserts it — InterPro match locations, a source's
  native UniProt-frame coordinates, or residue-by-residue SIFTS mapping. There
  is no local alignment, HMM scan, or regex-against-sequence route: see #655 for
  the three `TraitOccurrenceMappingMethodEnum` members that are validator-legal
  with no producer. Do not invent one to satisfy a request for "computed"
  coordinates; say which asserted route applies instead.
- **`seed_uniprot.py` is retired**, and `fetch_uniprot_examples.py` /
  `suggest_canonical_examples.py` write candidate ledgers only. A new canonical
  example enters the corpus solely through the workflow below.
- **Dry-run by default at every stage, and the stages are not equally
  consequential.** `--apply` on select, fetch, and finalize writes only
  gitignored staging under `reports/uniprot-grounding/` (`.gitignore:38`) plus
  its receipt. Only `promote --apply` mutates `data/traits/` and the durable
  registries under `data/grounding/`. Promotion requires explicit human
  authorization *in the current conversation* — general approval of the
  grounding task is not authorization to promote. Say plainly which stage you
  are about to make durable.
- **A batch is not a record.** The selector emits at most 1,000 unique trait
  records with at least 25 per available source (`MINIMUM_PER_SOURCE` at
  `scripts/select_uniprot_review_batch.py:75`, `MAX_REVIEW_BATCH` at `:76`).
  Grounding "one named record" means finding it inside a bounded batch, not
  carving it out.
- **Never edit `resolved.jsonl`, the evidence ledger, or the registries by hand.**
  They are content-addressed; an edited row breaks its `resolution_digest` and the
  promotion gate will reject it — correctly. What *is* curator-editable depends on
  the adjudication path (step 7): `.approved.tsv` on the direct path, the
  `--decisions` JSONL partitions on the finalize path. Never both for one batch.
- Record writes go through an audited route (`just audit-writers`). The promoter
  is a registered validated writer; nothing else may touch `canonical_examples`.
- **This skill stops at the review artifact.** Its toolset is deliberately
  read-only, so it carries the workflow through step 6 and hands back a
  `.review.tsv` plus a plain statement of what it found. Steps 7 and 8 document
  what happens next; performing them takes a human, or a follow-up run
  explicitly authorized to write. Say this at the hand-off rather than letting
  the reader discover it mid-batch, after the expensive fetch has run.

## Read before starting

- `CLAUDE.md` safety rules;
- `CanonicalExample`, `TraitOccurrence`, `GroundingEvidence`,
  `TraitOccurrenceMappingMethodEnum`, and `GroundingEvidenceProviderKindEnum` in
  `src/proteintraitsmech/schema/proteintraitsmech.yaml`;
- `data/grounding/README.md` and the two durable registries beside it;
- the target record in full.

## Workflow

### 1. Baseline the record

```bash
just validate data/traits/<axis>/<category>/<slug>.yaml
grep -n "canonical_examples" -A 40 data/traits/<axis>/<category>/<slug>.yaml
```

State what is already there: no examples, `LEGACY_UNVERIFIED` examples (present
but unproven), or a `QUALIFIED` one (then the ask is a second exemplar, not a
first). Absence of `qualification_status` means `LEGACY_UNVERIFIED`.

### 2. Refresh the candidate queue

Check the three provider artifacts first — all are gitignored and regenerable, so
a fresh checkout has none of them:

```bash
ls -l data/raw/align_cache/residue_frame.json \
      data/raw/align_cache/interpro_frame.json \
      data/profiles/profiles.jsonl
```

Any that are missing must be produced before the audit can run, and *that* is the
network-bound part of this workflow — `fetch_interpro_frame.py`'s own docstring
puts its crawl at 15,120 protein calls. Regenerating them is a batch: canary one
before fanning out, and get authorization first.

```bash
just audit-uniprot-grounding
```

Read-only once its inputs exist. Writes
`reports/uniprot-grounding/candidates.jsonl` (gitignored) from the three provider
artifacts and their release stamps. Candidacy is derived from what the providers
assert about the protein, not from sequence similarity.

### 3. Find the record's alternatives, and choose the organism

Each queue row is one (record, protein, source assertion) alternative and already
carries `taxon_id` / `taxon_label`:

```bash
python3 - <<'PY'
import json
TARGET = "data/traits/<axis>/<category>/<slug>.yaml"
for line in open("reports/uniprot-grounding/candidates.jsonl"):
    row = json.loads(line)
    if row.get("record_path") != TARGET:
        continue
    print(row["protein_id"], row["taxon_label"], row["mapping_method"],
          row["scope"], row.get("intervals"), row["evidence_source"],
          row["source_release"], sep="\t")
PY
```

**Bacterial or archaeal preference is a manual step today.** The selector ignores
taxon entirely (#656), so if a prokaryotic exemplar is wanted, filter these rows
yourself on `taxon_id` and carry the chosen accession forward. Two things to be
honest about when reporting:

- the queue is drawn from a fixed organism panel, so "no prokaryotic candidate"
  means none *in the panel*, not none in UniProt. The panel enters the corpus
  through `build_swissprot_profiles.py:67-76`, whose `SWISSPROT_PROFILE`
  exemplars are what `fetch_interpro_frame.py` then crawls;
  `fetch_residue_frame.py:107` mirrors the same tuple. Widening the panel means
  changing it there and re-fetching, not filtering harder here;
- not every record has one. Measure it for the target rather than assuming, and
  say so if the only alternatives are eukaryotic.

### 4. Select a bounded, deterministic batch

```bash
just select-uniprot-review-batch <BATCH_ID>            # dry-run
just select-uniprot-review-batch <BATCH_ID> --apply    # ignored staging only
```

Pass the exclusion quadruples for every previously reviewed batch, or the same
records will be re-selected. `--shard-count` / `--shard-index` narrow the draw
deterministically. Confirm the target record is in the manifest before going on.

### 5. Fetch the release-pinned registry

```bash
just fetch-uniprot-review-batch <BATCH_ID> > reports/uniprot-grounding/review-batches/<BATCH_ID>.uniprot_fetch_plan.json
# review that plan, then, with authorization:
just fetch-uniprot-review-batch <BATCH_ID> --request-plan <that file> --apply
```

On a warm checkout this is the first stage that touches the network (step 2's
artifacts are the other), and it is the one that fails on credentials or sandbox
permissions. **Canary it**: run the plan-only form
first, and after `--apply` verify the registry JSONL exists, is non-empty, and
contains the target accession — an exit code of 0 is not evidence that anything
was written. The pinned release is fixed by the recipe (`--expect-release`); a
mismatch is a hard failure, not something to override.

### 6. Resolve into immutable review inputs

```bash
just resolve-uniprot-review-batch <BATCH_ID>
```

Writes `.resolved.jsonl`, `.review.tsv`, `.protein_registry.jsonl`, and
`.occurrence_evidence.jsonl`. Never modifies `data/traits/` or the durable
registries. Every resolved row binds a `resolution_digest`.

### 7. Adjudicate — pick one path

Reviewing, on either path, means checking that the source assertion is about
*this record's* trait: an `inheritance_path` that reaches the record through a
parent family, a `scope` of `LOCALIZED` with intervals that do not span the whole
protein, and a definition that actually matches. Rejecting is a normal outcome,
not a failed batch.

**Direct** — a batch adjudicated in one sitting. Copy `.review.tsv` to
`.approved.tsv` and edit *that copy*; `promote-uniprot-review-batch` reads it.

**Partitioned** — a batch split across reviewers or sessions. Write explicit
decision ledgers, each row copying its resolved row's `resolution_digest`
verbatim, then reconcile them:

```bash
just finalize-uniprot-review-batch <BATCH_ID> --decisions <partition>.jsonl
```

Dry-run unless `--apply`. Note the direction: finalize *emits* `.approved.tsv`
(its `--approved-out`), so on this path do not hand-edit that file — your
decisions are the `--decisions` rows, and finalize would overwrite the edit.

### 8. Promote, then prove it

```bash
just promote-uniprot-review-batch <BATCH_ID>            # preflight
just promote-uniprot-review-batch <BATCH_ID> --apply    # authorized only
```

Then gate it:

```bash
just validate data/traits/<axis>/<category>/<slug>.yaml
just validate-uniprot-grounding data/traits/<axis>/<category>/<slug>.yaml --require-qualified
just audit-writers
```

**Add `--hierarchy-traits data/traits` only if the occurrence carries an
`inheritance_path`** — that is, if its `source_trait_id` differs from its
`trait_id`, meaning the source asserted a descendant and the claim climbs to
this record. The validator defaults its inheritance edges to the *input* paths,
so in that case a single-file run cannot see the parent and a correct occurrence
fails.

When `source_trait_id` equals `trait_id` there is nothing to climb, and the flag
only costs: it walks the entire corpus, turning a seconds-long check into a
tens-of-minutes one. Do not pay that by default.

`--require-qualified` is the completion gate: it dereferences the example's
`sequence_sha256` against the registry and every occurrence fact against the
content-addressed evidence object. If it passes for the target and the durable
registries grew by the expected number of rows, the example is grounded.

## Report

Name the record, the accession and organism, the mapping method and the source
that asserted the coordinates, the pinned release, and the gate output. State
explicitly which stages ran dry and which were applied, and — if the exemplar is
not bacterial or archaeal — whether that was a preference the queue could not
satisfy or a choice.
