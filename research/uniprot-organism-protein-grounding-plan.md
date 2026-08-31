---
topic: UniProt organism, protein, sequence, and trait-coordinate grounding
date: 2026-08-23
status: executing
scope: data/traits and data/grounding
---

# UniProt organism and protein grounding plan

## Recommendation

Adopt a fail-closed **candidate -> resolve -> validate -> promote** workflow.
Do not run a corpus-wide `suggest-examples --apply` or `fetch-examples --apply`
until promotion is gated on the same-example presence of:

1. an exact, current UniProt accession or explicitly resolved isoform;
2. a UniProt-derived protein label, NCBITaxon identifier, and scientific name;
3. the full sequence from a pinned UniProt release, with length and checksum; and
4. record-specific evidence locating the trait in that sequence, where the trait
   is residue-localizable.

Current `canonical_examples` that lack this evidence should be treated as
`LEGACY_UNVERIFIED`, not as proof that the record has a qualified example.

## Current execution checkpoint (2026-08-26)

The baseline below records the state from which this plan started; it is not a claim
that corpus-wide grounding is complete. The latest exact structural audit still
classifies the 429,271 records as 297,375 `NO_PROTEIN`, 131,769
`LEGACY_UNVERIFIED`, and 127 declared `QUALIFIED`. Current source-aware gate replay
now shows that seven of those historical Batch-001 claims are hard-invalid, however,
so only 120 declared claims pass both the structural validator and the current content
gate. The legacy group includes 33,748 records whose organism facts are incomplete.

- The only durable declared-qualified state remains 126 ProteinReferences and 127
  GroundingEvidence rows. Their SHA-256 values are
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c` and
  `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  Four truncated definitions, one template-only PANTHER definition, and two
  Pfam/InterPro scope conflicts make seven of these claims current-gate hard debt.
- Review batches 002--011 are finalized only in ignored staging reports. Together they
  contain 2,040 decisions: 851 approvals and 1,189 rejections across 1,000
  adjudication groups, including 149 all-reject adjudications. The approved
  candidate/record/evidence identities are pairwise disjoint. A structural no-write
  merge with unchanged Batch 001 would produce 829 ProteinReferences and 978
  GroundingEvidence rows, with SHA-256 values
  `30508c5c141beb272f0f59f24995fbe271ed3f6a09487ae9f4f4da3e45bebb3a` and
  `10a4b64bdfdb8b8bb91d3f7b59bf20ffb56052dbe746ae2dd215ad1f4f9b18b8`.
  Promotion remains prohibited until the seven durable-base failures are repaired,
  explicitly re-reviewed, covered by a fail-closed durable content receipt, **and
  explicit promotion authorization is separately granted**.
- Batch 011's 100 records/209 alternatives resolve to 179 qualified alternatives and 30
  machine-hard rejections; full-file review finalized 85 approvals and 124 rejections,
  including 15 all-rejected record groups. Its decision-aware gate has zero hard-approved
  candidates, but the batch remains staging-only for the same durable-base and
  authorization reasons.
- Batch 012 is mechanical staging only: its deterministic shard contains 100 records and
  201 alternatives, but no UniProt registry fetch, resolution, or review has occurred.
  The attempted normal fetch failed before startup on sandbox-denied `uv` cache access;
  permission escalation was denied, so no workaround was used and no fetch result is
  claimed. Existing pinned registries cover only 106/197 accessions, leaving 91 that
  require a fresh fetch. Source-content preflight already identifies 19 hard record
  groups/45 rows, but no decision ledger can be bound before complete resolution. The
  no-network fetch plan, generation receipt, and bounded resolver are now fail-closed and
  selector-bound as recorded below; all nine Batch-012 fetch/resolution outputs remain
  absent.
- The current checksum-pinned content gate evaluates 62,696 queued records/137,341
  candidate rows and blocks 6,675 records/16,007 rows. The unchanged immutable candidate
  queue SHA-256 is `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e`.
  Most direct functional-provider phases and the much larger no-protein queue remain
  future work. Rhea now has a deterministic, stdout-only direct Rhea-to-UniProtKB/
  Swiss-Prot candidate stage, a no-network acquisition plan, and a standalone read-only
  verifier for a future content-addressed acquisition receipt. The required mapping/
  release-contract artifacts and receipt remain absent, and the standalone verifier is
  intentionally not represented in the central grounding boundary. PRINTS now has
  a deterministic no-write source-model migration preflight, SFLD has a source-bound
  alignment/site diagnostic, and ComplexPortal has a release-blocked candidate-
  membership stage. All four stay fail-closed pending the source-specific execution/
  release receipts, review, and separately authorized migrations described below.
  SCOPe's v3 source-native, `!`-column-aware SQ stage now
  binds the protected registry, emits 3,585 deduplicated ProteinReference requests, and
  is closed by an unconditional SIFTS/provider-receipt gate; CATH has a bounded local
  annotation lane but lacks native boundary/SIFTS inputs; and 3did has a proven
  53-missing/47-spurious source-model defect that must be repaired before full-set
  grounding. BioLiP now has a source-native, no-write missing-protein stage covering all
  445 traits without examples: 638 exact rows are ready only for a future residue-level
  SIFTS resolver, three exact rows are source-residue blockers, and no protein identity
  is qualified. ECOD residue XML remains unavailable.
- ELM and DisProt now each have a checksum-pinned, stdout-only source-native candidate
  stage and an unconditional central provider-receipt deny gate. DisProt replays all
  9,387 IDPO regions without collapsing duplicate coordinates: 61 rows match the local
  ProteinReference registry, 7,616 exact-frame rows lack a reference, 1,699 are absent
  from the local residue frame, and 11 disagree with it. The 61 matches remain
  candidate-only, 3,191 missing-reference requests are staged, and zero evidence or
  qualification is emitted. Both stages remain blocked on provider acquisition and
  verified UniProt-registry receipts as detailed below.
- ComplexPortal's earlier v2 projection has been superseded by a provenance-hardened
  v3 stage and unconditional central deny gate. The exact 28-file curated snapshot
  still yields 20,234 candidates and 916 blocked tokens; 24 memberships across 19
  proteins intersect the local registry, while 20,210 memberships produce 10,341
  deduplicated ProteinReference requests. All 20,579 namespace traits are content-bound,
  all 5,295 curated source traits replay their historical paths and bytes exactly, and
  zero evidence is emitted. Provider acquisition, release-pinned file-list, and verified
  registry receipts remain separate blockers as detailed below.
- Do not infer completion from the review-batch checkpoints below. Trait and durable
  grounding writes remain pending explicit authorization, and scientific completion
  requires the remaining provider and corpus phases in this plan.

The execution authorization boundary is independent of technical readiness: source,
tests, this plan, and ignored review/staging reports may be changed while executing the
plan. Any write to `data/traits` or durable `data/grounding`, any promoter `--apply`, and
any commit or pull request requires separate explicit authorization. Passing every gate
does not grant that authorization.

## Current baseline

A read-only audit of all 429,271 trait YAML records produced the following
mutually exclusive funnel. Each record is assigned to the highest state reached
by one of its examples using fields currently stored inline.

| Best current inline state | Records | Percent |
|---|---:|---:|
| No valid UniProt protein | 297,502 | 69.30% |
| Protein present, organism incomplete | 33,748 | 7.86% |
| Protein and organism present, no valid inline sequence | 92,246 | 21.49% |
| Sequence present, no category-matched in-bounds coordinate | 5,492 | 1.28% |
| Passes the strict inline shape check | 283 | 0.07% |

Additional corpus facts:

- 131,774 files contain `canonical_examples`; 131,769 contain a syntactically
  valid UniProt protein identifier.
- Five empty example blocks are MetalPDB osmium/sodium records.
- There are 409,005 example items and 15,264 inline sequences across 7,115
  records.
- The 283 strict-inline records comprise 251 `SEQ_MOTIF` records and 32
  `SEQ_DISORDER` records.
- The 283 count is only a syntactic upper bound. A feature with the same broad
  category can still be unrelated to the exact trait represented by the record.

The largest missing-protein categories are:

| Category | Records without a protein |
|---|---:|
| `STRUCT_FOLD` | 41,875 |
| `SEQ_DOMAIN` | 41,150 |
| `FUNC_ORTHOLOG_GROUP` | 31,819 |
| `SEQ_FAMILY` | 29,410 |
| `FUNC_PROTEIN_FAMILY` | 26,360 |
| `STRUCT_INTERFACE` | 20,639 |
| `FUNC_INTERACTION_PARTNER` | 20,579 |
| `FUNC_ENZYMATIC_ACTIVITY` | 20,046 |
| `STRUCT_DOMAIN` | 13,514 |
| `FUNC_PATHWAY` | 12,646 |
| `STRUCT_HOMOLOGOUS_SUPERFAMILY` | 11,218 |

The largest source queues are ECOD 34,959; NCBIfam 31,823; CDD 25,121; SCOPe
22,810; 3did 20,638; ComplexPortal 20,579; OrthoDB 20,004; Rhea 18,558;
PANTHER 15,489; GO 13,602; Pfam 13,508; and InterPro 10,630. The earlier
directory-only SCOPe count of 20,442 omitted 2,368 superfamily records stored in
the shared `structure/homologous_superfamily/` directory.

## Why the current shape is insufficient

Only `protein_id` and `protein_label` are required in `CanonicalExample`.
Organism, sequence, sequence length, source, and features are optional. The
schema does not enforce sequence-length agreement, `start <= end`, bounds
against the sequence, residue identity, coordinate frame, or correspondence
between an example feature and the record's exact trait.

The current feature list is the protein's general UniProt feature track. It is
useful for display, but is not a normalized assertion that "this record's trait
occurs at these residues on this example." In particular:

- `fetch_uniprot_examples.py` initially writes metadata-only examples. Its
  `--refresh-sequences` pass later adds the protein's full generic FT collection.
- `suggest_canonical_examples.py` writes ranked carriers with organism and length
  metadata, but no sequence or occurrence coordinates.
- `build_sequence_structure_alignment.py` can match features by broad category.
  This is deliberately disabled for domains and secondary structure because a
  protein may contain many such features; the same ambiguity also means that a
  category match alone cannot qualify an example.

## Definition of a qualified example

### Localized traits

A localized example is qualified only when all of the following are true:

1. The exact accession, including any isoform suffix, resolves in UniProt.
2. Protein label, taxon identifier, taxon label, sequence, and sequence length
   come from the same resolved entry.
3. The sequence is associated with a UniProt release/version and SHA-256.
4. The occurrence identifies the exact record trait or an explicitly documented
   descendant used to instantiate an ancestor trait.
5. Coordinates are in a declared UniProt canonical or UniProt isoform frame.
6. Every interval satisfies `1 <= start <= end <= sequence_length`.
7. Discontinuous domains and residue sets remain discontinuous; they are not
   collapsed into a misleading minimum-to-maximum span.
8. Expected residues, peptides, patterns, or designated sites match the sequence.
9. PDB-derived evidence uses chain-aware SIFTS residue mapping. Raw PDB author
   numbers are never compared directly with UniProt positions.
10. Every trait-defining residue is mapped; partial site mappings do not qualify.

Generic same-category features, parent-family hits, co-occurrence, text
similarity, or an unconfirmed pattern match remain candidates.

### Whole-protein traits

The schema explicitly defines the FUNCTION axis as entry-level and not localized
to a residue range. Evolution traits and some protein-family/group traits also
require a whole-protein or entity-level interpretation.

These examples require the same exact accession, organism, full sequence,
release, and checksum, plus exact source membership or annotation evidence. They
should use `scope: WHOLE_PROTEIN`; a fabricated `[1, sequence_length]` interval
must not be represented as a localized trait occurrence. If the browser needs a
numeric extent, store it separately as `sequence_extent`.

## Data model

Normalize protein facts once in a versioned registry instead of repeating a full
sequence in hundreds of trait files:

```text
ProteinReference
  protein_id
  protein_label
  taxon_id
  taxon_label
  sequence
  sequence_length
  sequence_sha256
  isoform
  reviewed
  uniprot_release
  sequence_version
```

Add a small record-specific occurrence object under an example, or in an
authoritative sidecar keyed by `(trait_id, protein_id)`:

```text
TraitOccurrence
  trait_id
  protein_id
  scope: LOCALIZED | WHOLE_PROTEIN
  coordinate_frame: UNIPROT_CANONICAL | UNIPROT_ISOFORM
  intervals and/or residue_positions
  source_trait_id
  mapping_method
  evidence_source
  source_release
  sequence_sha256
  qualification_status
```

Use an external candidate ledger. Only qualified examples belong in
`canonical_examples`. During migration, unmarked existing examples are
interpreted as `LEGACY_UNVERIFIED`.

Suggested state machine:

```text
NO_PROTEIN
  -> CANDIDATE_PROTEIN
  -> PROTEIN_RESOLVED
  -> SEQUENCE_VERIFIED
  -> LOCATION_SOURCED
  -> LOCATION_VERIFIED
  -> QUALIFIED
```

Whole-protein assertions branch from `SEQUENCE_VERIFIED` to
`WHOLE_PROTEIN_EVIDENCE_VERIFIED` and then `QUALIFIED`.

## Priority order

### 1. Promote the locally resolvable missing-protein queue

The existing UniProt `2026_02` residue frame and InterPro `109.0` frame already
provide an exact trait-ID match, full sequence, complete organism metadata, and
bounded interval for 13,562 currently protein-less records. This table is the
historical **mechanical-candidate** inventory measured before source review; it
must not be read as a claim that every namespace is currently review-ready:

| Namespace | Initial mechanical candidates |
|---|---:|
| PANTHER | 8,845 |
| HAMAP | 1,862 |
| PRINTS | 1,585 |
| InterPro | 638 |
| Pfam | 441 |
| SFLD | 166 |
| NCBIfam | 24 |
| CDD | 1 |

PANTHER, HAMAP, InterPro, Pfam, NCBIfam, and CDD can enter bounded review under
the exact-match resolver. PRINTS and SFLD cannot: PRINTS remains hard-gated until
an ordered source fingerprint is represented and replayed against a complete
ordered occurrence, while SFLD remains hard-gated until its executable profile,
hierarchy level, and site model are mapped directly to protein coordinates. An
exact InterPro/member identifier or interval alone is insufficient for either
source.

Another 2,670 records already have an exact sequence and coordinate match and
need only UniProt organism metadata. These two groups are the first production
batches because they prioritize records with no protein while requiring little
or no new network work.

The current Swiss-Prot profile matrix is exhausted for this purpose: its 80,066
proteins carry 83,583 unique corpus trait IDs, and 83,582 already have examples.
The only remaining carried record is generic `GO:0005634`, intentionally skipped
by the prevalence guard. Rerunning `suggest_canonical_examples.py` on this matrix
will not close the backlog.

### 2. Expand exact signature resolution

There are 102,586 additional missing-protein records with signature-shaped
identifiers in InterPro-supported member namespaces. This is candidate capacity,
not a promised yield.

Support exact matches for InterPro, Pfam, CDD, NCBIfam, PANTHER, PROSITE, HAMAP,
SMART, SUPERFAMILY, and CATH/Gene3D. Require exact identifiers; a parent-family
or mapped-InterPro association is only a candidate unless explicit inheritance
is recorded. PRINTS and SFLD require their stricter source-native replay rules
above and never qualify through this generic exact-signature path.

### 3. Resolve structure-derived records through source occurrences

For ECOD, SCOPe, CATH, 3did, BioLiP, M-CSA, MetalPDB, RepeatsDB, and other
PDB-derived sources:

1. Reparse a concrete source occurrence, retaining PDB identifier, chain, native
   ranges, contact residues, and insertion codes.
2. Map the exact chain/residues through SIFTS.
3. Resolve the mapped UniProt entry and sequence.
4. Verify amino-acid identity and reject gaps or unmapped defining residues.
5. Propagate a verified descendant occurrence to an ancestor fold/class only
   with an explicit hierarchy path.

ECOD, 3did, and SCOPe alone account for 78,407 records without proteins.

### 4. Ground whole-protein functional records

Use exact source associations:

- GO: direct GOA/UniProt annotation, retaining the evidence code;
- Rhea: exact Rhea-to-UniProt or UniProt catalytic-activity annotation;
- Reactome: exact physical-entity participant;
- ComplexPortal: exact UniProt component;
- OrthoDB/COG: exact member mapping;
- CARD/ARO: curated reference protein or variant-model sequence;
- TCDB: asserted member mapping or verified sequence identity.

These records receive `scope: WHOLE_PROTEIN`, not residue coordinates. EC-only,
textual, homology-only, or generic pathway inference remains candidate evidence.

### 5. Repair existing partial examples without displacing the missing-protein queue

Use the same protein registry to fill the 33,748 records with incomplete organism
metadata and to resolve sequence references for existing examples. The local
residue sidecar records 10,238 accessions absent from its UniProt release; do not
silently substitute them. Require an official accession mapping and revalidate
the trait occurrence on the replacement sequence, otherwise reject the example.

Exclude the 53 currently known out-of-bounds generic FT intervals in the residue
sidecar until they are source-reviewed.

## Source-specific evidence levels

| Evidence tier | Examples | Promotion rule |
|---|---|---|
| A | Exact UniProt FT tied to the record occurrence; exact InterPro/member-database match; source-native UniProt coordinates | May qualify after sequence/taxon/bounds/residue validation |
| B | Exact PDB/source occurrence mapped residue-by-residue through SIFTS | May qualify when all defining residues map and match |
| C | Unique peptide or pattern match on a source-confirmed carrier | Requires manual/source-stratified review before qualification |
| D | Parent/xref first hit, same-category FT, profile co-occurrence, generic homology or prediction | Candidate only |

Specific rules:

- InterPro/Pfam/CDD/PANTHER/NCBIfam/PROSITE/HAMAP/CATH use exact
  `(protein, trait identifier)` matches from the InterPro frame. PRINTS additionally
  requires a complete ordered fingerprint occurrence matching the pinned KDAT
  model. SFLD additionally requires direct executable-profile and source-site
  replay; neither source may qualify from the InterPro interval alone.
- A PANTHER/NCBIfam full-protein family may be `WHOLE_PROTEIN` even when the HMM
  match footprint is retained as supporting evidence.
- PROSITE pattern-only scanning is not sufficient when multiple matches exist.
- ELM and DisProt source coordinates are strong candidates but still require
  exact comparison with the resolved canonical or isoform sequence.
- M-CSA partner proteins are not examples unless their own catalytic residue set
  maps completely.
- Complex, operon, cassette, or pathway records that no single protein can
  instantiate must be remodeled for multi-protein examples or explicitly
  adjudicated; an arbitrary member must not be forced in as an exemplar.

## Implementation plan

### Audit command

Add `scripts/audit_uniprot_grounding.py`, using a cheap streaming scan over the
full 2.1 GB trait corpus and full YAML parsing only for records with examples or
records in the current batch.

Proposed interface:

```bash
uv run python scripts/audit_uniprot_grounding.py \
  --traits data/traits \
  --residue-frame data/raw/align_cache/residue_frame.json \
  --interpro-frame data/raw/align_cache/interpro_frame.json \
  --profiles data/profiles/profiles.jsonl \
  --out reports/uniprot-grounding
```

Outputs:

- `summary.tsv`: counts by state, axis, category, and source;
- `records.tsv`: one row per trait and its best grounding state;
- `candidates.jsonl`: evidence-ranked candidate proteins;
- `blocked.tsv`: dead accessions, ambiguous matches, missing mappings,
  non-instantiable records, and other unresolved cases.

### Resolver and promoter

Add `scripts/ground_uniprot_examples.py` with separate, resumable operations:

```bash
uv run python scripts/ground_uniprot_examples.py resolve \
  --queue reports/uniprot-grounding/candidates.jsonl \
  --providers protein-registry,interpro \
  --batch ready-local

uv run python scripts/ground_uniprot_examples.py promote \
  --resolved reports/uniprot-grounding/resolved.jsonl \
  --approved reports/uniprot-grounding/approved.tsv \
  --apply
```

`resolve` must never modify trait files. `promote` is the only writer and must
validate each full record before atomically replacing it.

Modify `suggest_canonical_examples.py` and `fetch_uniprot_examples.py` so their
default product is the candidate ledger. Expand query dispatch to all exact
signature namespaces and use Gene3D, not a raw CATH query, for CATH-backed
matches.

Before a new network crawl, inspect the release checks and planned work:

```bash
just fetch-residue-frame --top-up
just fetch-interpro-frame
```

Only after accepting the release/rebuild implications:

```bash
just fetch-residue-frame --top-up --apply
just fetch-interpro-frame --apply
```

The existing fetchers refuse to mix cached coordinates from different releases
unless explicitly overridden; do not use `--allow-stale` for promotion data.

### Semantic validator

Add `scripts/validate_uniprot_grounding.py` and call it from strict validation or
CI. It must dereference the protein registry and enforce:

- accession/isoform resolution;
- taxon ID and label agreement;
- sequence length and checksum agreement;
- coordinate bounds and declared coordinate frame;
- exact record trait/source identity;
- residue, peptide, or pattern agreement;
- complete SIFTS mapping for structure-derived occurrences;
- permitted `WHOLE_PROTEIN` use by category;
- no `QUALIFIED` example with missing provenance.

LinkML should enforce object shape; the semantic validator must enforce
cross-object and sequence-dependent invariants.

## Review protocol

For each source resolver:

1. Review at least 25 examples, plus every isoform, multi-hit, discontinuous,
   partial-SIFTS, and ancestor-inheritance case.
2. Stop the source batch on the first semantic mismatch and fix the resolver.
3. Promote no more than 1,000 records in one review batch.
4. Run the semantic validator, `just validate-all <batch-path>`, and the grounding
   audit after every batch.
5. Require idempotent output from the same release-stamped inputs.

The organism must always come from the selected UniProt entry. A trait's taxon or
clade xref is not evidence for the example protein's organism.

## Completion criteria

The grounding effort is complete only when the audit reports:

- no valid protein: 0;
- incomplete organism: 0;
- missing full sequence/checksum: 0;
- localized trait without a verified record-specific occurrence: 0;
- whole-protein trait without exact annotation or membership evidence: 0;
- out-of-bounds, sequence-mismatched, or stale-release coordinates: 0.

Records that no single protein can scientifically instantiate must remain visible
in `blocked.tsv` until the model is changed or the record is adjudicated. They do
not count as successfully grounded merely because an associated protein was
found.

## Execution log

### 2026-08-24 — fail-closed foundation and first review batch

- The pre-promotion 429,271-record audit was regenerated twice from UniProt `2026_02`
  and InterPro `109.0`; all four output SHA-256 values were byte-identical between
  runs. Its corrected candidate funnel contained 137,576 candidate rows and 482,794
  blocked rows.
- Flattened multi-location InterPro evidence is no longer promotion-ready. The corrected
  queue contains 13,470 unique `ready-local` records and 1,441 unique
  `needs-grouped-interpro` records. The 92-record reduction from the planned 13,562 first
  batch is deliberate: those records cannot be represented faithfully from the compact
  sidecar.
- Review batch `ready-local-review-001` selected 1,000 source-stratified records across
  PANTHER, HAMAP, InterPro, Pfam, SFLD, NCBIfam, and CDD. Selector v2 retained every
  alternative for those records: 2,065 candidate rows. The exact-accession UniProt
  snapshot resolved 1,758 proteins with zero blocked accessions and emitted 27,695
  same-response membership rows. A repeated live fetch at release `2026_02` was
  byte-identical.
- The resolver produced 2,065/2,065 machine-qualified alternatives and was
  byte-idempotent. Fixed-seed source review made explicit decisions for 162 unique
  records and all six flagged multi-hit records: 127 alternatives were approved, 195
  rejected, and 1,743 remain undecided. The approved set contains one exemplar per
  record across CDD (1), HAMAP (27), InterPro (24), NCBIfam (24), PANTHER (27), and
  Pfam (24). SFLD remains stopped: all 59 alternatives in the 25 reviewed records were
  rejected because of source-wide content/routing defects, despite zero mechanical
  provenance discrepancies.
- Promotion installed 126 content-addressed ProteinReference rows and 127
  GroundingEvidence rows before adding 127 QUALIFIED examples to 127 trait records.
  A second apply wrote zero registry artifacts and zero trait records; aggregate trait
  and registry hashes were unchanged. Semantic replay, strict LinkML validation of all
  127 changed records, writer auditing, and `git diff --check` passed. The focused
  grounding regression suite passed 175 tests.
- Two post-promotion full audits were byte-identical. They report exactly 127 QUALIFIED
  records (23 FUNCTION and 104 SEQUENCE), 137,341 remaining candidates, and 482,721
  blocked rows. The inline-shape funnel still reports these records as lacking an inline
  sequence by design: the full sequences are deduplicated in the durable protein
  registry and replayed by the semantic validator.
- The ECOD phase-3 adapter now parses ECOD manual representatives and residue-level
  SIFTS XML into content-addressed candidate, mapping, evidence, and blocked ledgers.
  Production ECOD promotion remains fail-closed until the durable ProteinReference
  registry covers its accessions and 12,968 authoritative residue-level SIFTS XML files
  are snapshotted. Existing segment-level SIFTS JSON cannot satisfy residue mapping.

### 2026-08-24 — deterministic PRINTS review and source-wide stop

- Selector v3 assigns records, rather than individual alternatives, to deterministic
  SHA-256 shards. The first PRINTS shard contains 755 complete record groups and 1,765
  alternatives; the complementary shard contains 747 groups and 1,771 alternatives.
  Their 1,502-record union is disjoint, and every special-case alternative remains with
  its siblings.
- The shard's exact-accession UniProt snapshot contains 1,648 requested proteins and
  29,539 same-response membership rows at release `2026_02`, with zero blocked
  accessions. Two live fetches were byte-identical. The resolver replayed all
  1,765 alternatives as mechanically `QUALIFIED`, and a second run was byte-identical.
- Three disjoint full-file review partitions then inspected all 755 YAML records and
  all 1,765 alternatives. Their sizes were 252/600, 252/595, and 251/570
  records/alternatives. A union check found zero missing, extra, duplicate, or
  overlapping candidate IDs. Every decision is explicitly `REJECTED`; there are no
  PRINTS approvals and no PRINTS trait writes. Exact candidate identity, resolution
  digest, UniProt `2026_02` membership, InterPro `109.0` intervals, ProteinReference,
  GroundingEvidence, sequence checksum, and whole-protein projection replayed without
  a mechanical discrepancy for all 1,765 candidates.
- The source stop is semantic. In the reviewed shard, 295 definitions are exactly
  1,799/1,800 characters and 292 visibly end nonterminally; subtype-specific text can
  be lost after a generic family preamble. Every reviewed record also lacks a
  structured PRINTS fingerprint representation. Reviewers found generated
  label-restatement definitions, fingerprints with fewer observed intervals than their
  declared motif count, InterPro Domain entries routed as whole-protein `SEQ_FAMILY`
  records, explicit superfamilies routed as families, and several literal candidate or
  record-scope conflicts. Repairing only the truncation is therefore insufficient to
  reopen this source.
- The three canonical decision-ledger SHA-256 values are
  `aeeccf670e51b8c2b210bd221ff58af5dba2040a30e4155dab87075b1e881b40`,
  `795aedd14175338befda8634e667e63488136d816e4f28c544770bcac24848b9`, and
  `5eaab073927bc1c0ebd4b0ad9886461509d77a637c0efef213f42e5cbc89b9a4`.
  They are ignored review artifacts; the central review template and all PRINTS YAML
  inputs remained unchanged.

### 2026-08-24 — guarded InterPro-member repair groundwork

- `seed_interpro_members.py` now preserves complete curator-reviewed InterPro
  abstracts instead of slicing them at 1,800 characters. The cap remains only for
  unreviewed generated abstracts. A regression test covers a long curated abstract
  whose discriminating tail would previously have been lost.
- `repair_interpro_member_truncations.py` is now diagnostic-only. Its exact-match plan
  identifies pristine seeded records whose paired definition fields both equal the
  historical first-1,800-character fold, but `--apply` refuses before loading source
  inputs or writing anything. Later source review proved that completing a borrowed
  InterPro abstract is not a valid PRINTS repair.
- Against the current corpus, its dry run would repair 733 exact truncations, protect
  12 nonmatching records, classify 1,149 records as already within the source length,
  and leave 212 records whose current definition is not the mapped member abstract.
  Every PRINTS 42.0 entry instead has a non-empty, source-native description; distinct
  PRINTS fingerprints can share one integrating InterPro entry and were therefore given
  identical borrowed definitions. **There is no valid `--apply` path for this diagnostic.**
  PRINTS must be reseeded from the pinned KDAT descriptions and ordered fingerprint
  models, followed by a fresh full audit, deterministic selection, release-pinned
  resolve, full-file review, semantic validation, and idempotency check.

### 2026-08-24 — source-model audits and immediate deny gates

- The fixed PRINTS 42.0 KDAT is 63,577,121 bytes with SHA-256
  `47b4f0c32002bce2f9b85f335c942cc52deae8bed54c2b4b2eec5e36c5810771`.
  It contains 2,106 source-native descriptions and 12,444 ordered final motif
  blocks. The structured `COMPOUND(n)` count equals the final-block count for all
  records. The current seeder instead borrowed an integrating InterPro abstract for
  1,894 records and generated boilerplate for 212. Ten InterPro entries integrate 21
  distinct PRINTS signatures, so those distinct records inherited identical text even
  though every KDAT description differs. Source-native `gd;` text, not the mapped
  InterPro abstract, is therefore authoritative for reseeding.
- Comparing the reviewed PRINTS shard's anonymous flattened InterPro intervals with the
  KDAT length vectors found 1,521/1,765 shape-compatible candidates, 243 with fewer
  intervals than motifs, and one (`PRINTS:PR01573` / `UniProtKB:O00295`) with the full
  count but a final interval of 17 residues where the model motif length is 23. This was
  **not an ordered fingerprint replay**: the frame discarded hit grouping and motif
  identity, so ascending starts, count, and lengths cannot establish which motif or
  occurrence each range represents. Future qualification requires grouped matcher
  output with motif identities plus the source post-processing policy; training-gap
  extrema and anonymous interval shape remain review diagnostics only.
- The SFLD review stop is also a source-model error. The corpus flattens 15
  superfamilies, 133 groups/subgroups, and 155 families into 303 whole-protein
  `FUNC_PROTEIN_FAMILY` records, although the source models enzyme functional domains
  and distinguishes shared-chemistry superfamilies from reaction-specific families.
  Of 303 records, 140 have generated label-restatement definitions; even four sourced
  records borrow an InterPro Domain abstract at a different granularity. The 355 current
  SFLD candidates were derived from localized intervals, but whole-protein projection
  would discard those coordinates; 73 intervals cover under 75% of their proteins.
- Until SFLD hierarchy/definition/routing and site-aware evidence are repaired, the
  resolver now marks every SFLD candidate `REJECTED` with
  `unqualifiable:sfld_source_model_repair_required`. Promotion independently rejects
  SFLD identity from namespace or CURIE before any registry or trait write, including a
  tampered, digest-consistent legacy `QUALIFIED` row. The full grounding test module
  passes 53 tests after this gate. Production reseeding also remains blocked because the
  original release-pinned `sfld.jsonl` and source-site snapshot are absent.

### 2026-08-24 — content-addressed PRINTS snapshot and diagnostic replay

- **Historical and invalidated:** the first `prints_snapshot.py` contract treated the
  API JSONL, checksum-pinned KDAT, then-misparsed hierarchy JSONL, and local InterPro XML
  as one raw snapshot. Its former contract ID was
  `prints-snapshot:2aa5f9a9a11482ca4807122373a6759698ff5667aba09d1c7abdaf11be289906`.
  This ID and its hierarchy projection must not be used; the corrected schema-v2
  snapshot in the latest checkpoint below supersedes it.
  It formerly bound API, KDAT, hierarchy, and XML SHA-256 values `708b9d575c74eac6f94eacc51fb52b9cad1d655a2834e0d55040ed12aab383de`,
  `47b4f0c32002bce2f9b85f335c942cc52deae8bed54c2b4b2eec5e36c5810771`,
  `e0278570fff541ea35dd7358831be629e232e6b56bc22706768e87e21041d33d`, and
  `c77fe193c1a0de8df903deff9325f734bfca3c9fbf59fd4ce697489c33ef0d87`.
  All 2,106 accession/code identities and all 1,937 API-to-InterPro integration
  assignments replay exactly; the other 169 API entries are exactly the unintegrated
  set. The API payload itself declares no release, so the contract records PRINTS 42.0
  consistency as an inference from exact content equality rather than inventing API
  release metadata. The obsolete manifest ID is no longer the production allowlist.
- Fetching installs the manifest last after staging and verifying all inputs. A
  no-network local command materializes and verifies an already downloaded snapshot.
  The seeder verifies the corrected schema-v2 contract before every PRINTS dry run, but
  every PRINTS `--apply` invocation now refuses before loading source files. This is
  necessary because the generic reseed merge regards the bad historical definition as an enrichment and
  would otherwise preserve it even under `--force`; a dedicated preflighted migration is
  required instead. No PRINTS trait was written.
- The resolver has a `prints-snapshot` diagnostic provider. It binds the model comparison
  to the manifest and raw KDAT record, but labels the result only as anonymous interval
  shape compatibility. It records count, inclusive-length vector, and ascending-start
  comparisons plus whether the trait record carries the exact structured source
  representation; it explicitly records motif identity unverified, occurrence grouping
  unverified, and grounding ineligible. It cannot qualify or emit a ProteinReference
  while the unconditional PRINTS gate is active.
- The earlier two 755-record/1,765-alternative runs remain useful only for the aggregate
  1,521/243/1 shape partition described above. Their
  `EXACT_ORDERED_COUNT_AND_LENGTH`/`PARTIAL_MOTIF_SET` labels and resolved/review ledger
  hashes are invalidated and must not be reused because they overstated anonymous range
  shape as motif replay. The corrected statuses are
  `ANONYMOUS_INTERVAL_SHAPE_COMPATIBLE`, `ANONYMOUS_INTERVAL_COUNT_SHORT`, and
  `ANONYMOUS_INTERVAL_LENGTH_VECTOR_MISMATCH`. Two corrected resolver runs are now
  byte-identical: 1,521, 243, and one row respectively, with all 1,765 rows explicitly
  reporting motif identity and occurrence grouping unverified, a missing committed
  representation, and grounding ineligible. All 1,765 remain rejected; 644 also retain
  the independent source-definition-truncation finding. Corrected resolved/review
  SHA-256 values are
  `57b168f9536a5f38afa25849e7bc258dae7a387739a582b90dc2fc984f7f00dc` and
  `2c96a439fe760e4b5fafc24e1ec8c0894964015b42fd69521da5d9ece5e469df`;
  both ProteinReference and occurrence-evidence outputs are empty. The two runs wrote
  only temporary staging files outside the repository.
- Remaining PRINTS blockers are semantic migration and routing, not raw-source identity:
  the committed records still lack structured representations, 109 API/member-vs-mapped
  InterPro type conflicts require adjudication, explicit superfamilies remain routed as
  families, and durable GroundingEvidence does not yet preserve an ordered fingerprint
  occurrence for independent promotion replay. Both resolver and promoter gates stay on.

### 2026-08-24 — pinned SFLD profile/site/hierarchy source model

- `sfld_release.py` now parses SFLD 4 as an inseparable three-artifact model rather
  than treating the InterPro API label as a whole-protein family assertion. The locally
  installed, gitignored HMM, hierarchy, and site artifacts have pinned SHA-256 values
  `e011a4139e6477a526710b32e8aeaa68203329c799305b015ec35c3b6d09672f`,
  `e9d379421227fb9eb3c5eb259d2a925c321a7bf1e697055d361f7397b53f86b9`, and
  `60ee2408e5bb2bed2eba4ee2101e219b74dcee7abb2bc03aba9e3e905dcf8c66`.
  Their deterministic source-model manifest SHA-256 is
  `8b492f010c965f5d76f21e6d5665976570f7c14f25dc7499e9ecd6105ab685ad`.
  A no-network CLI verifies these production paths; its atomically installed canonical
  manifest has file SHA-256
  `dd483d58b4afd3d56cf2744d210a60cb9e328662128155c62a09fe0ac49ef9e9`.
- Exact replay yields 299 HMM/site models: 15 source superfamilies, 132 subgroups,
  and 152 families, with model lengths 119--3,378. Of these, 274 carry 1,368 ordered
  HMM match-state SITE positions and 372 allowed FEATURE residue tuples. FEATURE
  strings remain correlated tuples; flattening them into independent residue alphabets
  would create combinations absent from the source. The hierarchy has 266 children,
  580 ancestor relations, and direct edges F-to-G 142, F-to-S 3, G-to-G 48, and
  G-to-S 73; 25 models are isolated.
- Four of the 303 InterPro API signatures have no executable HMM/site model in the
  archived release: `SFLDF00030`, `SFLDF00034`, `SFLDF00109`, and `SFLDG01106`.
  They cannot be treated as profile-qualified exemplars. The source representation now
  has schema and strict cross-field validation for model hashes, native S/G/F level,
  GA sequence/domain thresholds, HMM metadata, ordered model positions, correlated
  site tuples, and direct-model-only site evidence.
- This is source-only groundwork. It does not reroute or reseed the 303 legacy records,
  map HMM match states to protein residues, or lift either grounding gate. Every SFLD
  seeder invocation, including dry run, now refuses before source loading or record
  writing; a dedicated hierarchy/profile/site-aware migration and fresh full-file review
  are still required.

### 2026-08-24 — trusted iterative selection and second review-batch staging

- Selector v4 originally accepted prior review state as a content-addressed candidates +
  manifest + decisions triplet. The current contract is stricter: every prior batch is
  supplied as an ordered candidates + manifest + resolved + decisions quadruple. It
  verifies the exact resolved-row digest for every candidate and requires each decision
  to copy that digest, in addition to verifying the candidate snapshot and manifest.
  It requires an explicit decision for every alternative in any reviewed record group
  and rejects partial, duplicate, unknown, multiply approved, or stale approved groups.
  Only a complete group with exactly one `APPROVED` alternative can be removed from the
  current queue. Complete all-`REJECTED` groups remain eligible after source repair.
- The original triplet replay of `ready-local-review-001` accounted for all 322 explicit decisions in 162
  complete groups: 127 one-approved groups are already absent from the post-promotion
  queue, while 35 all-rejected groups/87 historical alternatives remain. The three-file
  legacy three-file exclusion-set SHA-256 was
  `386d8be95b988ba740e2c0d2506c84028d4b3e160ea5285e794cbbf9918f9ae7`.
- An initial unsharded `ready-local-review-002` staging batch was deliberately
  superseded before review or trait writes because it reselected the known-unrepaired
  `HAMAP:MF_00008` definition blocker. Its ignored staging files remain an audit trail;
  they are not promotion inputs. Deterministic shard 1 of 3 avoids every one of the 35
  known all-rejected groups while retaining the required source coverage.
- The operative `ready-local-review-002-s1of3` batch contains exactly 100 complete
  record groups and 208 alternatives: 25 records each from HAMAP, InterPro, PANTHER,
  and Pfam. Its queue and selected-candidate SHA-256 values are
  `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e` and
  `0622c60ecaecfa0972708fc0a3ea859fd07378776ee30d5bba3a4487d70356d6`;
  all selector invariants are true.
- Two live UniProt fetches at release `2026_02` were byte-identical. They resolved all
  205 requested exact accessions, emitted 3,045 same-response membership facts, and
  blocked zero accessions. Registry, membership, and empty-blocked SHA-256 values are
  `69fcf56f31133b4fa18a5c8ddd7fa17afd86ea9397ee52baab278a61dbd451c0`,
  `9e3f34842b33f5c8cd78cb3151f8ac6266807bd69d87b1957b4b555dbdbc4d94`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
  Two resolver runs were also byte-identical and mechanically qualified all 208
  alternatives. Their resolved/review/evidence SHA-256 values are
  `546cefc738e45dc9bde94dd82378eceea6c34959d4e0a36d7728ebea87e119c7`,
  `4dc6e8b0e4a6c99929e86c8e822faba5f305a733f307d57b472669b46ace0578`, and
  `5c7545885da298799a001859a22c7c54a133a36fcf654a95a0766f3678bc958b`.
  Two disjoint full-file reviews then decided all 208 alternatives exactly once.
  Independent pre-promotion replay stopped the initial 89-approval result and found ten
  additional record-level defects: seven exact historical 1,800-character truncations,
  one reverted PANTHER name-only stub, one Pfam label/definition/coordinate
  contradiction, and one further Pfam label-restatement definition. The reviewers
  explicitly revised every affected alternative to `REJECTED` before finalization.
- The final decision set contains 79 approvals and 129 rejections across all 100
  complete groups: HAMAP 22, InterPro 24, PANTHER 15, and Pfam 18 approved exemplars;
  21 groups are all rejected. Approved candidate-ID set SHA-256 is
  `cc7d5fe8b426051b70cb19aeba0db03e27416c90a73f7aa73eb5b36bba457550`.
  The HAMAP/InterPro and revised PANTHER/Pfam partition SHA-256 values are
  `9d0a9d22ed23c4f4073b7844e4a425dc8fbad5d37e3ea4a400e41e23c23fd2a0` and
  `5632013f0f2a358c63851eb4e6a318147393ebce443258bb5b2f29f181c0b6e5`.
  Every remaining approval passed provider replay, current-record digest, definition,
  route/scope, interval, sequence, registry-collision, and in-memory semantic-install
  checks. None was already qualified or overlapped a pre-existing dirty target path.
- `finalize_uniprot_review_batch.py` now validates resolved-row digests, exact and
  disjoint decision coverage, record keys, required review metadata, sole-approved
  primary semantics, legal all-rejected groups, and the blank resolver TSV before
  atomically emitting canonical artifacts. Two runs were byte-identical. Canonical
  decision and approval TSV SHA-256 values are
  `3066e943108fe5838f97b8c8359fcc074531f1e68ebcd784def853c6e7bef0d2` and
  `b19475f305e9cc8e34c0198dfef2a38042c5e0a850c0bfd0368f6498a8aba07a`.
- The exact no-write promoter preflight (`--max-batch 79 --min-source-reviews 25`)
  reports source coverage 25/25 for all four sources, 79 record writes, no already
  present example, and conflict-free merged totals of 202 ProteinReference and 206
  GroundingEvidence rows. All 79 mappings use exact `INTERPRO_MATCH`; no membership
  ledger row would be promoted. **Apply remains intentionally pending:** the governing
  action-safety instruction forbids trait/data writes without new explicit authority.
  The attempted command was rejected before process creation. Durable registry hashes
  remain `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`,
  and the 79-target aggregate YAML hash remains
  `848bd9d0f76132a564c85ad85531bd3707175d7c570daf33e43ae8e4a114c1cd`.
- The five named review-batch `just` recipes now discard their shell-level named
  `batch_id` before forwarding variadic CLI arguments. Live fetch and local resolve
  exercised the repaired wrappers; no-write finalize and promote preflights exercised
  the added paths. A static regression test covers select, fetch, resolve, finalize, and
  promote.
- Consolidated regression verification passed 332 tests in 5m07s, followed by 72
  finalizer/selector/writer tests after the last utility and wrapper changes. Ruff,
  byte-compilation, `git diff --check`, the 27-class/24-enum schema audit, the
  182-script writer audit, and the 76-block/55-source registry check all passed. The
  expected source/licensing inventory still reports its 16 pre-existing warnings. A
  real serial strict-validation run scanned all 100 selected YAML files with
  `--workers 1` and emitted zero errors.

### 2026-08-24 — macOS serial-validator portability

- `validate_strict.py --workers 1` now runs validation in-process instead of creating a
  `ProcessPoolExecutor`. This preserves the same validation path while avoiding the
  macOS sandbox semaphore probe (`os.sysconf`) that can fail even when serial validation
  itself is permitted. Values below one fail argument validation. A focused regression
  test covers the serial path; this is a portability repair, not a relaxation of any
  schema or semantic check.

### 2026-08-24 — source-aware record-content gate and digest-bound review provenance

- `uniprot_record_content_gate.py` now replays five objective record defects against
  checksum-pinned source images before a candidate can qualify:
  `SOURCE_DEFINITION_TRUNCATED`, `DEFINITION_TEMPLATE_ONLY`,
  `UNRESOLVED_SOURCE_PLACEHOLDER`,
  `SOURCE_POSITIONAL_IDENTITY_CONFLICT`, and `SOURCE_SCOPE_CONFLICT`. The exact
  InterPro XML, Pfam clans, and Pfam type SHA-256 values are
  `c77fe193c1a0de8df903deff9325f734bfca3c9fbf59fd4ce697489c33ef0d87`,
  `86062b7ef1a0e0caee0c28cef479ac0d294c80789c51cbf75e513b368ce3a6f6`, and
  `5cce3b49fb64afd2c43157600d7a43bee572765b1bc6e918b3e4210bd12313b9`.
  A requested source that is missing, changed, or not exactly replayable aborts the
  resolver; it cannot silently produce an empty finding set. The conservative
  `LOW_INFORMATION_SOURCE_DEFINITION` signal remains review-only.
- Production replay over the original 100-record/208-alternative batch-002 resolution
  found exactly 18 hard-blocked records/42 alternatives: 11 truncated definitions,
  five exact templates, one positional-identity conflict, and one source-scope conflict.
  It also found one review-only low-information definition. All 79 final approvals were
  outside the hard set. This exactly recovers the objective subset of the independent
  full-file review without encoding the less reliable PANTHER semantic judgments as
  brittle automatic rules.
- The resolver now places the structured finding list and its checksum-pinned source
  bindings inside every resolved row and its `resolution_digest`; hard findings add a
  stable `unqualifiable:record_content:*` reason. The promoter independently reparses
  the current YAML and the pinned sources before any registry or trait mutation, so a
  stale or tampered resolved artifact cannot bypass the gate.
- Two canonical re-resolutions of `ready-local-review-002-s1of3` were byte-identical:
  166 alternatives remained `QUALIFIED`, while the 42 hard alternatives changed from
  `QUALIFIED` to `REJECTED`; no trait-record SHA changed. The new resolved and review
  SHA-256 values are
  `2ad3f29c3c5068343b2f9bfc295e808f46354a66af0cf9b62015fe33d1a670b9` and
  `3c7c0064b7d0e73efbc04811122af748505193d3d02d9c57f0dece11f708bc24`.
  The unchanged staging ProteinReference and evidence artifacts retain SHA-256 values
  `69fcf56f31133b4fa18a5c8ddd7fa17afd86ea9397ee52baab278a61dbd451c0` and
  `5c7545885da298799a001859a22c7c54a133a36fcf654a95a0766f3678bc958b`.
  All pre-gate artifacts were preserved under content-addressed ignored filenames.
- `finalize_uniprot_review_batch.py` now requires every decision to copy the exact
  recomputed resolved-row `resolution_digest`; `select_uniprot_review_batch.py` accepts
  prior review state only as positional candidate/manifest/resolved/decision
  quadruples. It verifies exact candidate-ID and record-key projection, every resolved
  digest, every decision binding, complete decided groups, and records the resolved
  path/SHA/count in the next manifest. `bind_uniprot_review_digests.py` is a dry-run-first,
  output-restricted migration utility for legacy ignored review ledgers.
- Digest binding produced 322 exact rows for review-001 and 97 + 111 exact partition
  rows for review-002, with SHA-256 values
  `9c45934f13cc5d118e5d7a34903e3b40877e83f2a52de3cf82bae5c2363b64e4`,
  `f8917c96c17660b4054d7b853987774452a2206a103a5bac511b38fae735f8de`, and
  `0ad12adbefb8d6d50245cf1dc4da2a5052ba80273154d79f84c7f3f6cc6dbcba`.
  Re-finalization was byte-idempotent and retained the same 79 approvals/129 rejections;
  its canonical decision and approval SHA-256 values are now
  `04fa18076d2a87b77a72d94aea378dc0563f58032340b581ad639b63110be329` and
  `c3542d9c92e0e0f239d4559288f3c8d4ffc11e0b287bad988f508ecf1af56f7c`.
  The full no-write promoter preflight again passed with 25/25 reviewed records per
  source and 79 prospective writes. No trait or durable registry was modified.

### 2026-08-24 — third review-batch staging and full-file review

- Quadruple-bound replay of the first two reviews selected
  `ready-local-review-003-s0of6` deterministically: 100 records/210 alternatives, with
  25 records each from HAMAP, InterPro, PANTHER, and Pfam. The candidate SHA-256 is
  `7d8c703e6b66ef1d961d809238e061dfe7a4f189ec896bec962516f90391daf2`;
  its TSV and JSON manifest SHA-256 values are
  `7e084948ba27cc6d48887baca131b98eaa7528492f5d44301e352488fa22637e` and
  `387c2a58f593ff7a8b0291e8a09b7ce81242da9a1a87318a6e232bf277d3b51f`.
  The new digest-bound review-ledger set SHA-256 is
  `eb206cce44a1ba2fbcb43ba36015c842932ba68238784914ac4ab39d6dd3913e`.
  All selector invariants are true; no previously approved current-queue record or
  known reviewed all-rejected blocker is in the selection.
- Two official UniProt fetches at release `2026_02` were byte-identical. They returned
  all 206 exact requested accessions, 2,996 exact database memberships, and zero blocked
  accessions. Registry, membership, and empty-blocked SHA-256 values are
  `0e01c86dae1de2b680be7f37641ae7efe679f04ac8b9fae1847315dfcee563c7`,
  `1c0ec29f3e72011ff9b09c7b14bb907077999412ef0ae5454bae2fd2769c4baa`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- The first two local resolutions were byte-identical. Independent full-file review then
  found two objective defects that the initial gate missed: `HAMAP:MF_00026` retained a
  literal `<locus_tag>` placeholder in its primary label, and `PANTHER:PTHR10185` had
  only the generated label/model template plus a lexically redundant `phospholipase`
  class. The gate now detects both conservatively: angle-bracket placeholder syntax is
  exact, and the PANTHER rule fires only when the generated definition has no GO or
  other sentence and its class tokens add nothing beyond the label. Batch-002 replay is
  unchanged and still blocks zero of its 79 approvals.
- Two post-extension resolutions were byte-identical. The content gate rejected 37
  alternatives across 14 all-rejected records: 29 rows in ten truncated records, four
  rows in two template-only records, three rows in one scope-conflict record, and one
  unresolved-placeholder row. The other 173 alternatives across 86 records qualified
  mechanically.
  Resolved, review, staging ProteinReference, and evidence SHA-256 values are
  `ac39ffde466cc2d915e96993f5663a6ac8db841059ee03fd1241d4ad362382a4`,
  `5ffc215cd5cbf8425c7168583118e41446e4b620c35a94399314247cf1645345`,
  `a6dbe9217cb2ba83a19f51854ba2cd184364efe74d6d85162464147f051f259a`, and
  `89e4a962a76281df59b3e6dccbd5b9af434a6f85f688aa3ddea8487d6e73ba35`.
- Two disjoint source-stratified full-file reviews plus an independent all-record audit
  decided all 210 alternatives: 86 approvals and 124 rejections, with approval counts
  HAMAP 19, InterPro 25, PANTHER 19, and Pfam 23. Fourteen records are all rejected:
  `MF_00002`, `MF_00003`, `MF_00026`, `MF_00049_B`, `MF_00118_A`, `MF_00140_B`,
  `PTHR10009`, `PTHR10031`, `PTHR10102`, `PTHR10185`, `PTHR10221`, `PTHR10264`,
  `PF29471`, and `PF29997`. Besides the automated reason for `MF_00118_A`, review also
  confirmed its EF-Tu/`tuf` label conflicts with the eukaryotic/archaeal EF1A source and
  candidates. Candidate-level review selected monofunctional rather than fused HAMAP
  carriers and the directly named source identity in mixed-family cases.
- The re-attested HAMAP/InterPro and PANTHER/Pfam partitions have SHA-256 values
  `86cfd861ac454d4f9827a991f425d5bcd659bf63025b70d330fae67ec636bb02` and
  `4f0a94e09c6de5e7169f54cd6cbbc5cd371466ebb7f07c11ddb500e6d2ca90a8`.
  The content-gate decision replay reports 86 approvals and zero hard-approved rows.
  Canonical finalization was byte-idempotent; decision JSONL and approval TSV SHA-256
  values are `1fd242c8497a9791427e9ebb50164dbc328987ae0169b2bc28a7e3e5d2af9b77`
  and `02037d390d0ee4a1517ccfa3306f3f9e492f6c31c4aae8c6ceabe2c1410c821d`.
- The exact no-write promoter preflight passed with 25/25 decided records per source,
  86 prospective record writes, zero already present examples, and conflict-free merged
  totals of 207 ProteinReference and 213 GroundingEvidence rows. No trait or durable
  registry write was authorized or attempted.
- Consolidated verification passed 381 focused tests (211 grounding/review tests and
  170 source-model/schema/writer tests); the 66 directly affected content-gate and
  grounding tests were then repeated after formatting and passed again. Ruff lint and
  format checks, byte-compilation, `git diff --check`, and Just parsing passed. The
  schema audit remains coherent at 27 classes/24 enums; the writer audit now accounts
  for 184 scripts, 49 seeders, six editors, one validated promoter, and 50 declared
  bypasses. The 76-block/55-source inventory passed with its 16 existing warnings.
  Closed-schema validation scanned all 100 selected records with zero errors.
- The corpus-wide semantic grounding validator scanned all 429,271 records and reported
  zero findings against the still-unchanged durable registries (126 ProteinReference
  and 127 GroundingEvidence rows). None of the 86 approved target paths overlaps a
  dirty trait path; their deterministic aggregate YAML hash is
  `703289e48ce4d3e384eebb4c1a391fcbff8e906703a716c823fee6fe405555ab`.
  Durable registry SHA-256 values remain
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.

### 2026-08-24 — exact batch staging and repair-aware review deferral

- Named review-batch resolution now passes `--replace-staging-outputs`. This mode rejects
  debug `--limit`, ignores any historical output rows, builds the exact final
  `QUALIFIED` ProteinReference/GroundingEvidence projection, checks exact key sets,
  embedded evidence, reference links, and sequence checksums, and then uses atomic
  artifact replacement. The generic resolver retains its explicitly cumulative default.
- Exact rebuilding pruned stale rows that had survived earlier candidate changes without
  altering any signed resolved or review byte. Batch-002 is now 163 ProteinReferences and
  166 evidence rows, with SHA-256 values
  `b744f0d086b67efc50a2d97560648a4fcdec9a5c3b090f5f619ea12c11b28a6f` and
  `54389953b7735930397531b9b32cd05493cd0ca9d4988f468977c4552e965688`;
  batch-003 is now 169 and 173, with values
  `410f60287ffe547a4286acef7ab773142f678b9485e78b0441ef163092a3af64` and
  `c6001b29dc2d0e70a167b837117f0112583d84723ac0397bf8e3471ce85ab0bc`.
  Two rebuilds were byte-identical. Their resolved/review SHA-256 values remain exactly
  `2ad3f29c3c5068343b2f9bfc295e808f46354a66af0cf9b62015fe33d1a670b9` /
  `3c7c0064b7d0e73efbc04811122af748505193d3d02d9c57f0dece11f708bc24`
  and `ac39ffde466cc2d915e96993f5663a6ac8db841059ee03fd1241d4ad362382a4` /
  `5ffc215cd5cbf8425c7168583118e41446e4b620c35a94399314247cf1645345`.
  Re-finalization and current-gate no-write promotion preflights still pass.
- The selector has an opt-in `--defer-unchanged-all-rejected` mode. Every alternative in
  an all-rejected group must bind one valid `record_sha256`; a stable read of the current
  normalized `data/traits` path must match it exactly. Changed bytes explicitly reopen
  the group, while unsafe/missing paths, mixed identities/hashes, and stale resolved
  digests fail closed. Deferred and reopened sets are independently content-addressed in
  schema-v4 manifests. The option deliberately covers record edits only: it must be
  omitted after any source snapshot, content-gate, provider, or resolver change so an
  upstream repair reopens the group. Default behavior still reopens every all-rejected
  group.

### 2026-08-24 — fourth review-batch staging and full-file review

- The policy-preserving selector default chose `ready-local-review-004-s8of9`, the first
  complete shard among shard counts 1--9 with zero overlap against all 70 previously
  all-rejected records. It contains 100 new records/192 alternatives/191 distinct
  proteins, with 25 records each from HAMAP, InterPro, PANTHER, and Pfam. It has zero
  overlap with 740 prior decided candidate IDs, 362 prior decided record groups, and 127
  dirty trait paths. Candidate, manifest JSON, and manifest TSV SHA-256 values are
  `52eb4a294426be974dce66add4670843981368dd658dabf42de8b5e0936c0353`,
  `113e52105283a1bbd83b279423b2f34fcef0f1c7d8f85475c7b3306b9242b949`, and
  `87ef8b7f51c581da62003b7be0e7e7926de87feb9d835327e11e2bdf9146e1bf`.
- Two official UniProt fetches at release `2026_02` were byte-identical. All 191 exact
  requested accessions were returned, with 2,926 exact database memberships and zero
  blocked accessions. Registry, membership, and empty-blocked SHA-256 values are
  `fb9f8b9d3bce89c25d80b53b373b2f0c3478ca3cad18fb0eeda8bda5c15dba86`,
  `b3e7ab9e76ba25b56fb6d2d280ec9f760fa8404840824e91cef4dbbf221315a2`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Independent review found one objective defect beyond the initial batch replay:
  `Pfam:PF29991` and its exact Pfam member name say RIPR EGF-like **10th** domain, while
  mapped `InterPro:IPR063500` says **9th** in its short name, name, and abstract. The
  positional-identity gate now conservatively compares explicit numeric/spelled ordinal
  identities as well as N/C-terminal identities, with matching-ordinal negative controls.
  Batch-002 and batch-003 replay unchanged and still have zero hard-approved rows.
  `PANTHER:PTHR10339` retains malformed citation text present in the pinned InterPro XML;
  review classified this as non-blocking upstream text-normalization debt because its
  family identity and evidence remain complete.
- Two post-extension resolutions were byte-identical: 169 alternatives qualified and 23
  were rejected across 11 all-rejected records. Exact staging contains 168
  ProteinReferences and 169 evidence rows. Resolved, review, registry, and evidence
  SHA-256 values are
  `d5b88c5ce7b1ec080da9875a564dd841905708954946cf17250a14f15bc67f50`,
  `a52db7221fe13261fd54a9780bd3e8c224a2c23d213c8a456ac7e031ba904d38`,
  `eec14ac96e9335ccb6c01b3a1d62fab53ffd54695840e14ba4b65fbf03155f2b`, and
  `792283231a04590a7ed49e0e3d7f1e5e1122af6c46b67ceb7c4057276cb81188`.
- Two disjoint full-file reviews plus an independent all-record audit decided all 192
  alternatives: 89 approvals and 103 rejections. Approval counts are HAMAP 20, InterPro
  25, PANTHER 21, and Pfam 23. The 11 all-rejected records are `MF_00029`, `MF_00046`,
  `MF_00054_B`, `MF_00120`, `MF_00280`, `PTHR10093`, `PTHR10121`, `PTHR10202`,
  `PTHR10258`, `PF29991`, and `PF30342`. The reviewer-partition SHA-256 values are
  `b362766caae0f555d9097483c9833da0c4c1b2ae1b220e424b29054d66d0f74e` and
  `75e344cc8adf85b1d198399248cfaeccb3d365831c4a1c0fd8d003ab3ee4c3d0`.
  All 192 source intervals, provider digests, UniProt projections, sequence lengths, and
  sequence checksums replay exactly; the independent audit found no remaining decision
  discrepancy or gate false positive.
- Canonical finalization was byte-idempotent. Decision JSONL and completed approval TSV
  SHA-256 values are `b17ba755f41a7e3febf67fe06a5fc553ff060e9c9ae7aaa9322abba9529604e1`
  and `aa9429cbae85883cfbc4da0f3e4e72f9b8b2b492618dc03a06dc6aa1a137df80`.
  Current-gate no-write promotion passes with 25/25 reviewed records per source, 89
  prospective record writes, zero already present, and conflict-free totals of 207
  ProteinReferences and 216 GroundingEvidence rows when merged independently with the
  current durable state. None of the 89 target paths is dirty; the SHA-256 of the sorted
  per-file checksum manifest is
  `8229eb64becb5f44c08ab9f8b463b156fd0195ce52605807976d659af47865b1`.
- Consolidated verification passed 395 focused tests. Ruff lint/format checks,
  byte-compilation, Just parsing, and `git diff --check` passed. Closed-schema validation
  scanned all 100 selected files with zero errors; schema, writer, and source-registry
  audits remain green at 27 classes/24 enums, 184 scripts/49 seeders/six editors/one
  validated promoter/50 declared bypasses, and 76 blocks/55 sources with the same 16
  known warnings. The semantic grounding validator scanned all 429,271 trait files and
  emitted zero findings against the unchanged durable state. Durable SHA-256 values
  remain `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  No batch-002, batch-003, or batch-004 promotion `--apply` was authorized or attempted.

### 2026-08-24 — full-queue content-gate performance replay

- The source-aware content gate now uses PyYAML's C-backed safe loader when available,
  with an exact `SafeLoader` fallback, and caches repeated resolution of the same raw
  record path. The rule set, source projections, and fail-closed findings are unchanged.
  A 2,000-record object comparison found no parsed-value differences between the two
  loaders; parsing that slice fell from 9.044 seconds to 0.817 seconds (11.07x).
- An independent full replay of the immutable 137,341-row/62,696-record candidate queue
  completed in 49.72 seconds wall time (`user` 43.24 seconds, `sys` 3.96 seconds), versus
  the 297.997-second pre-change baseline. A separate post-change run took 53.858 seconds.
  The queue SHA-256 remains
  `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e`.
- Finding counts replay exactly: 6,650 hard-blocked records/15,947 rows, comprising
  1,209 template-only records, 3,112 truncated-definition records, 15 positional
  conflicts, 2,450 scope conflicts, and 53 unresolved-placeholder records, plus two
  review-only low-information records. The canonical summary SHA-256 is
  `4536d6537b7db89ffa495c99abdf93e5f54bdfd62b0a89089e5db872e7cf2133`.
  The 72 directly affected content-gate/resolver tests, Ruff lint and formatting,
  byte-compilation, and `git diff --check` all passed.

### 2026-08-24 — cumulative no-write promotion audit for batches 002--004

- The three signed decision sets contain 610 decisions and 254 approvals. Their record,
  candidate, and evidence identities are pairwise disjoint; every target is clean and
  still matches its bound preimage. Repeated ProteinReferences are byte-identical, so
  the staged ledgers contain no cross-batch conflict.
- A purely in-memory sequential merge against the current durable 126-reference/
  127-evidence state produced these expected checkpoints without writing them:
  batch-002 -> 202/206 rows (`c09b17811680314b01308776e852005405ec4eaac1e38e8c000bbc9b703f5156` /
  `9cc130092f883bb07f723968024b598787e83d9213ed316cb4a688f076fc6c3b`),
  batch-003 -> 282/292 rows (`b823d32a4329512caa804b77553fde6cb064b0297442d84c9b785e2e62c56f1a` /
  `5012333ea2e2fa807015e2aab366d2e3dce3e240374dba632b61125a75e0b802`),
  and batch-004 -> 360/381 rows
  (`ab746d827e0c0a3ac343d3f7770a68fede88b4cc0bf1d7f4c90eb1a3acef8fad` /
  `93b2064aec031dc8d231c9b266bf37bb74d5b1f09a3e0067a5dd6a8c3e2058da`).
- The combined 254-file preimage-manifest SHA-256 is
  `95a79c8855fc4b48b4cd0235b8346b5f29a4d4c03ad1469ebee3aa5ab22c85d2`;
  its simulated postimage value is
  `76e1f519fbf491f3b029899334463ce051d24a388342a5d87d7245104f572357`.
  If promotion is explicitly authorized, each batch must first pass a fresh no-write
  preflight and then be applied, validated, and checked against these sequential hashes.
  No durable write was authorized or attempted during this audit.

### 2026-08-24 — fifth review-batch staging, review, and gate extension

- Quadruple-bound replay of the first four review states selected
  `ready-local-review-005-s7of14` deterministically: 100 records/200 alternatives/197
  distinct proteins, with 25 records each from HAMAP, InterPro, PANTHER, and Pfam. The
  candidate, JSON-manifest, and TSV-manifest SHA-256 values are
  `e97786212555c20afbb636b3f523497edcda4091feac2415835a340907ff76f9`,
  `f65f2e952ab759de1579b94597fd6c2fdb02dc0fdbf373047aeddcbfd32d8d6e`, and
  `490e0a37baeb1e30af784c8e993eef965c50ecc0ea85a48312334fa7635b24e1`.
  The immutable full-queue SHA-256 remains
  `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e`.
- Two live UniProt fetches at release `2026_02` were byte-identical. They returned every
  exact requested accession, emitted 3,106 exact membership facts, and blocked none.
  Registry, membership, and empty-blocked SHA-256 values are
  `738e8cf62ef69967d0a1fbabfbacefad6fece868c2ae02e0e04e75c27bc76a58`,
  `9531300ce1abe6452a8338c93b6d77bee6070279c409ddb6dfeb3ed6926e1ac9`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Independent full-file review found two source-aware cases that the prior gate did not
  express. `PANTHER:PTHR10459` says `DNA LIGASE`, although every classified child,
  every candidate, and exact integrating InterPro entry `IPR050800` identify the family
  as PARP/ARTD ADP-ribosyltransferases. A new conservative hard
  `SOURCE_FAMILY_IDENTITY_CONFLICT` rule requires unanimous alternate child identity
  plus exact InterPro corroboration; the checksum-pinned PANTHER 19.0 classification
  SHA-256 is
  `94b0c70dc84b9888bf2a784a3ba52f775412546b07bc1bad19302a04353cc07c`.
  `PANTHER:PTHR10098` is a legitimate `RAPSYN-RELATED` root, but its only candidate's
  family footprint covers 500/2,481 residues (20.153%). The candidate-specific
  `LOW_WHOLE_PROTEIN_FAMILY_COVERAGE` signal is review-only: coverage alone is not a
  safe hard blocker for giant or repeat-rich proteins.
- The resolver still evaluates record-level hard findings before occurrence resolution,
  preserving historical rejected-row shape and digests; candidate-dependent review
  findings run only after authoritative occurrence normalization. Two exact
  post-extension resolutions were byte-identical: 176 alternatives qualified and 24
  were rejected across 12 hard-blocked records. Exact staging contains 175
  ProteinReferences and 176 evidence rows. Resolved, review, staging-reference, and
  staging-evidence SHA-256 values are
  `0953e1597eb64d461b60be62c36fe55d07da1aea70bc9045551ffd16612a1f8f`,
  `997509bd7c0bd750364cf4a23d3d1127fa0487b4106d8d9c7b31230090ea1d7d`,
  `b0b57af62786ffd1aa9422795c0e508e20a5488d07a9e2f0eacdbff07870fc2f`, and
  `584bd07bc3328520ed2c61bb748346f51ae8fb3509fe29377809a6ef42860ca9`.
- Two disjoint source-stratified full-file reviews plus an independent 100-record audit
  decided all 200 alternatives: 87 approvals and 113 rejections. Approval counts are
  HAMAP 23, InterPro 25, PANTHER 20, and Pfam 19. Thirteen records are all rejected:
  `MF_00263`, `MF_00385`, `PTHR10098`, `PTHR10233`, `PTHR10261`, `PTHR10454`,
  `PTHR10459`, `PF29298`, `PF29395`, `PF30433`, `PF30454`, `PF30674`, and
  `PF31257`. All 200 source intervals and record hashes, all 197 distinct UniProt source
  records, all 3,106 membership facts, and all qualified registry/evidence projections
  replayed.
  HAMAP/InterPro and final PANTHER/Pfam partition SHA-256 values are
  `78eea2aa249b4e26789daf2c2890f43e0e301a81315ed34799cc29ddd13c5101` and
  `1bd0a5cf6b3a710e22c845396cdd2daac58ed9de21e12c957af60271e627de5a`.
- Canonical finalization was byte-idempotent. Decision JSONL and completed approval TSV
  SHA-256 values are `93d7b07943852b473d2b6ce16ab403dda8865dccaf1dab44e350d9f69cfaca45`
  and `0dcbf3d0067d20caac45f5e3226437ca0a8a125df8d420fdfb92d6c4549439b1`.
  Decision-aware gate replay reports 24 hard rows/12 hard records and zero hard-approved
  candidates. The exact no-write promoter preflight passed with 25/25 decided records
  per source, 87 prospective record writes, zero already present, and conflict-free
  totals of 209 ProteinReferences and 214 GroundingEvidence rows when merged with the
  current durable state. None of the 87 target paths is dirty or differs from its bound
  preimage; its sorted per-file preimage-manifest SHA-256 is
  `beef1bac5f1591b24722c438d41faf85eba94a3c0fbed58b054f94436431e06c`.
- A cumulative in-memory replay of batches 002--005 proved all 341 approved candidates,
  target records, and evidence rows pairwise disjoint. The batch-002 through batch-004
  checkpoints exactly reproduced the prior audit. Adding batch-005 yields 437 references
  and 468 evidence rows, with SHA-256 values
  `4b57b3a1e6dcb4e03534baf816424e9b76f8f5fdf8771c068481de13aa0a398e` and
  `9282f04001ffc869bbaf03f968d63a8b4819f951a1307a2ed4f37f7eb69e0f07`.
  The combined 341-file preimage-manifest SHA-256 is
  `487559536de43664eda6a44d2bd9369c4d2ad9bde40048e3e6cf608c25ae40b6`.
- Two post-extension full-queue replays were exact. The compact second run completed in
  49.65 seconds wall time (`user` 45.27 seconds, `sys` 3.98 seconds); the independent
  first run took 58.94 seconds. Across 137,341 rows/62,696 records, the current gate
  finds 6,651 hard records/15,950 hard rows: 1,209 template-only, 3,112 truncated,
  one family-identity conflict, 15 positional conflicts, 2,450 scope conflicts, and 53
  unresolved-placeholder findings. It also reports two low-information and 108
  low-whole-protein-coverage review findings. The canonical summary SHA-256 is
  `3f8cda7aa31dc6c7d944bb7c6c3a4b8b534f68672e2d9d854514bc9774ca418a`.
- Consolidated verification passed 404 focused tests in 5m18s; the final directly
  affected 80-test slice was repeated after formatting and passed in 22.08 seconds.
  Ruff lint and format checks, byte-compilation, Just parsing,
  `git diff --check`, and closed-schema validation of all 100 selected records passed.
  Production audits remain green at 27 classes/24 enums, 184 scripts/49 seeders/six
  editors/one validated promoter/50 declared bypasses, and 76 blocks/55 sources with
  the same 16 advisory source/licensing warnings. A fresh full audit reproduced the
  429,271-record ledgers byte-for-byte, and the corpus semantic validator scanned all
  429,271 trait files with zero findings.
  The durable registries remain unchanged at 126 references/127 evidence rows, with
  SHA-256 values `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  No promotion `--apply` was authorized or attempted.

### 2026-08-24 — sixth review-batch staging, review, and malformed-definition gate

- Exact replay of the first five review states selected
  `ready-local-review-006-s5of15` deterministically: shard 5 of 15 contains 100
  records/206 alternatives/206 distinct proteins, with 25 records each from HAMAP,
  InterPro, PANTHER, and Pfam. `Pfam:PF29414`, previously all-rejected, was deliberately
  re-opened and freshly adjudicated. Candidate, JSON-manifest, and TSV-manifest SHA-256
  values are `5438ef451865cdaaa3e272e931ecba79b9475570960ebf7cc1b19ce8c549e904`,
  `bade83a85fd3a3468a76d341cda21bcb4924c78c10f9290f0debaa6378607a46`, and
  `2d3872843a81288c0183b1bb071a3390e0094b0e27883a89c9297f0858d2226d`.
  The immutable full-queue SHA-256 remains
  `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e`.
- Two live UniProt fetches at release `2026_02` were byte-identical. They returned all
  206 exact accessions and 3,001 exact membership facts, with no blocked accession.
  Registry, membership, and empty-blocked SHA-256 values are
  `7d3cf07fdb54fadc54d8bd179026aaab316b76519831a309df89225a9145baa4`,
  `82d461c37c0ec91a07fe388e896ddbcb2454a875321bc9e78da0d0717086c017`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Full-file review found two exact InterPro-derived source definitions whose citation
  stripping corrupts substantive prose. `InterPro:IPR063291` ends `interaction with
  TRAPPC2L (.`; the definition inherited by `PANTHER:PTHR10657` contains `processes
  [,. Members`. New hard finding `SOURCE_DEFINITION_MALFORMED` is deliberately narrow:
  it fires only when the normalized current definition exactly equals the
  checksum-pinned InterPro abstract and contains literal `[,.` or terminal `(.`.
  Corrected local prose, non-terminal `(.`, and unsourced text are negative controls.
  The gate and focused-test file SHA-256 values are
  `bec469aa8651751b60be41dd95c93bec4e0fc0bfd58096eca3d20f90f46f5f37`
  and `3c57b8e1da92219079ee613d952ce560e5505051ca5a4c60fb786d01d69ef5da`.
- `PANTHER:PTHR10113` remains non-hard source repair debt by explicit policy: its
  approximately 780-character definition is semantically complete, and only a
  redundant bibliography lead-in (`For more information see.`) is damaged.
  `PTHR10484`'s irrelevant H3-length sentence and `PTHR10751`'s generated-class
  `heterotrimeric G-protein` imprecision are also non-hard provider-text debt. Do not
  broaden the hard gate for these cases without a corpus-wide policy and regression
  scan.
- Two post-gate resolutions were byte-identical: 171 alternatives qualified and 35
  were hard-rejected across 16 records. Exactly five rows changed from the initial
  batch resolution: two for `IPR063291` and three for `PTHR10657`. Exact staging
  contains 171 ProteinReferences and 171 evidence rows. Resolved, blank-review,
  staging-reference, and staging-evidence SHA-256 values are
  `0e1d93ce744763457830bac049ad933e4ef0fafaae9716ffa2189dc4e3657530`,
  `ad5b57b350c43fdf8452f3dbd28c2558c147a7038c3cbb809c14b03a2e8068e6`,
  `10ac73e723ad3e96fec191dc78f0d87e75ced715251012a11f34d41ff5feba12`, and
  `d5b7da3770bc6272bfca2469b247320447ca9fb987cf9fd46ec54cf6a7d9c37f`.
- Two disjoint source-stratified full-file reviews plus an independent all-record audit
  decided all 206 alternatives: 84 approvals and 122 rejections. Approval counts are
  HAMAP 18, InterPro 24, PANTHER 23, and Pfam 19. Sixteen records are all-rejected:
  `MF_00079`, `MF_00254`, `MF_00260`, `MF_00327`, `MF_00343`, `MF_00436`,
  `MF_00453`, `IPR063291`, `PTHR10168`, `PTHR10657`, `PF28614`, `PF29056`,
  `PF29414`, `PF30109`, `PF30444`, and `PF30753`. Independent replay passed all
  206 candidate IDs, digests, YAML hashes, UniProt metadata/sequences, ProteinReference
  digests, and InterPro-frame intervals; all 171 qualified registry/evidence projections
  and all 3,001 membership facts also replayed. HAMAP/InterPro and PANTHER/Pfam review
  partition SHA-256 values are
  `398a0086057878672807578cd209b1432a00a3afc91e845386d39df0cf1886dd` and
  `fc0ca0b40479eda3d78bf1a8f59335c5fdc127b469bcd45ab09ba1c9152ec34c`.
- Canonical finalization was byte-idempotent. Decision JSONL and completed approval TSV
  SHA-256 values are `779b7c67f70b62202597edd3bba6ad3c3edc4cc8b2bd8e6255523eecbf566c9e`
  and `ebc389935a53c86d42a1ac576641429bc0ea6f4a5aa867b734eaa113de370ff2`.
  Decision-aware gate replay reports 35 hard rows/16 hard records and zero hard-approved
  candidates. The exact no-write promoter preflight passed with 25/25 decided records
  per source, 84 prospective record writes, zero already present, and conflict-free
  standalone totals of 207 ProteinReferences and 211 GroundingEvidence rows when merged
  with the current durable state. None of the 84 target paths is dirty or differs from
  its bound preimage; its sorted per-file preimage-manifest SHA-256 is
  `1d1005e7116291f25fc3e032d1db4c28937aa13eae5ded06875f5f65f2eb336e`.
- Cumulative in-memory replay of batches 002--006 proved all 425 approved candidate IDs,
  target records, and evidence IDs pairwise disjoint. It exactly reproduced every prior
  checkpoint. Adding batch 006 yields 505 references and 552 evidence rows, with
  SHA-256 values `3988b2ceceba03941fb9e33980445179871ebbef245aac9eaaefcce139ed20b3`
  and `886e023c94ba7a4f7670eff445656266aa5f737785619bdb4a0af6280e7f3c02`.
  The combined 425-file preimage-manifest SHA-256 is
  `ebc9677da21f9321d13ed23d639cfb778dae601ac4f69987b3ee4ea115a51c6c`.
- Two post-extension full-queue replays were exact. The compact second run completed in
  50.67 seconds wall time (`user` 46.61 seconds, `sys` 4.02 seconds); the independent
  first run took 60.54 seconds. Across 137,341 rows/62,696 records, the current gate
  finds 6,668 hard records/15,992 hard rows: 1,209 template-only, 18 malformed, 3,112
  truncated, one family-identity conflict, 15 positional conflicts, 2,450 scope
  conflicts, and 53 unresolved-placeholder findings. It also reports two
  low-information and 108 low-whole-protein-coverage review findings. The SHA-256 over
  the compact, sorted-key JSON projection of record/row counts and finding counts is
  `78f745b5f4a90a1f7a56feb36ae52fb57a1b868c2abc52125b63a542bd0fcaea`.
- Consolidated verification passed 329 focused tests in 21.07 seconds; an independent
  gate/resolver slice passed 81 tests in 17.39 seconds. Ruff lint and format checks,
  byte-compilation, Just parsing, `git diff --check`, and closed-schema validation of
  all 100 selected records passed. The durable registries remain unchanged at 126
  references/127 evidence rows, with SHA-256 values
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c` and
  `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  No promotion `--apply` was authorized or attempted.

### 2026-08-24 — seventh review batch, selector-history repair, and two exact content gates

- Exact exclusion replay exposed one composability defect in the batch selector:
  `Pfam:PF29414` had been all-rejected in both batches 001 and 006, and the previous
  implementation treated the repeated, fully rejected candidate history as an
  ambiguous duplicate. Selector schema/selection/exclusion algorithms are now v5.
  Each exclusion bundle is still independently checksum-bound and fail-closed, but a
  repeated record group is coalesced only when every occurrence is complete and every
  decision is `REJECTED`; any approval, conflict, partial decision set, stale digest,
  inconsistent bound record SHA, or cross-record candidate reuse still fails. The
  selector and test SHA-256 values are
  `9f79da6338015a6924d45dcee8854cb667ff6199f4f72b687617ba061181ffcd` and
  `c4334658a347ed631fad4d3a920a3123e2ed9d0acdc9e6e7d3f2130351b7595b`;
  all 58 selector tests pass. Across the exact first-six history there are 1,338
  physical decision rows/1,336 unique candidate IDs, 552 approved records, and 109
  unique all-rejected groups. `PF29414` is the sole repeat. The canonical repeat-history
  and ledger-set SHA-256 values are
  `ae592bee1202fec2d6ecfc48bb29dbdaa7b36719ed24079682ac5bc94094bd04` and
  `0261f2b73c40cd1d6815600a062cdf77218daec7efc37a054f7fe3f22ccdd865`.
- Deterministic selection scanned shard counts 1--100. Ninety-three shardings could
  satisfy the complete 25-record-per-source quota; the global minimum reopened-group
  count was two, and the first optimal tuple was shard 8 of 14. The resulting batch,
  `ready-local-review-007-s8of14`, contains 100 records, 204 alternatives, and 199
  distinct proteins: 25 records each from HAMAP, InterPro, PANTHER, and Pfam, with
  candidate-row counts 51, 36, 72, and 45. It deliberately reopens the previously
  all-rejected `HAMAP:MF_00049_B` and `HAMAP:MF_00054_B`; both are independently
  rejected again. The candidate, JSON-manifest, and TSV-manifest SHA-256 values are
  `68d3ef6480cdc612915ff28577d4d864cc3f9e023e6b573fd4d2dcd55834889f`,
  `d434925d1071ba6bb2fdf236e9f26fdc23d2427eb01401ffcf50315bf1b6fcc6`, and
  `f7322256ae6085f8803b1979dc09550535042ee7216f9c4c6a40cf8029c644c6`.
  Reversed exclusion arguments and a second selection run were byte-identical. After
  all six exclusion states, 11,250 four-source records/24,174 candidate rows remain.
- Two live exact-accession fetches against UniProt release `2026_02` were byte-identical.
  All 199 requested accessions resolved, no accession was blocked, and 3,095 exact
  membership rows were retained. UniProt-registry, membership, and empty-blocked
  SHA-256 values are
  `9686ec5264f858982ccd3c9aa9058fb7f60020d8c45e381322a8328316e087c4`,
  `dcd939fa7976d9fc820f018e5f01606f385cf96110bdd247b2388a043dc7df20`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Full-file review discovered two objective defects that the prior content gate missed.
  `PANTHER:PTHR10587` labels its root `GLYCOSYL TRANSFERASE-RELATED`, while eight of
  eight informative pinned PANTHER 19.0 children are deacetylases or the homologous
  ArnD deformylase; its ninth child is exactly the low-information `SECRETED PROTEIN`.
  Exact integrating InterPro:IPR050248 is `Polysaccharide deacetylase, ArnD subfamily`,
  names PTHR10587 as that exact member, and all three candidate UniProt proteins are
  deacetylases. A strict scan of 477 queued PANTHER transferase-root groups/1,148 rows
  found PTHR10587 as the sole case satisfying the source and candidate corroboration.
  The runtime gate remains source-stable: record/PANTHER root identity, at least two
  unanimously classified informative children, no unclassified child, the exact
  PANTHER member name, and integrating InterPro identity must all establish the same
  mutually exclusive alternative; only exact `SECRETED PROTEIN` is ignored. The
  bifunctional PTHR10605 family and the earlier one-PARP-plus-uncharacterized fixture
  are negative controls.
- `Pfam:PF31018` exactly replays InterPro:IPR063693's malformed sentence `This entry
  represents a of approximately 85 residues`, with the required noun absent. The new
  rule is not a free-text grammar heuristic: it fires only when the normalized record
  definition exactly equals the checksum-pinned InterPro abstract and contains the
  exact word-boundary sequence `represents a of`. An exhaustive scan of 54,190 pinned
  InterPro entries/54,068 nonempty abstracts found only IPR063693; exactly two queue
  records inherit it (`PF31018` and `IPR063693`), for six candidate rows and no source-
  scan false positive. Corrected local prose and non-InterPro prose are negative
  controls. Final content-gate and focused-test SHA-256 values are
  `691516a98a5030619a9360c15633b78711d82e7891618df5b71c5342aae429a1` and
  `f95509d8c020b3cbaf22541480db60dd6a5cf34a29a5c1f8420109f3ff5ad475`.
- Final-code batch resolution was repeated twice after narrowing the generic-child
  exception and was byte-identical: 160 alternatives qualified and 44 were hard-
  rejected across 16 records. Exact staging contains 155 distinct ProteinReferences
  and 160 GroundingEvidence rows. Resolved, blank-review, staging-reference, and
  staging-evidence SHA-256 values are
  `d4801a2f8d59d0a357a5b8dfbcd9d3aff75e39532144a96aad63cabb09ddba3d`,
  `ddf67bb941b76519e258a4f36bb80ee86e4f37dc5a865a4ea76cd088204f0db3`,
  `3c2551fa9b731ab183788ce31d4245f39fc4432f8e36b1c747d85a87d7a8aee4`, and
  `51468b9b458bd29dacdc7a69acb6b91ccd3f10aca8307be8072fc28000fa947d`.
  Independent scratch resolution reproduced all rows, findings, source bindings,
  staging projections, and resolution digests; all 100 current YAML byte hashes, 199
  UniProt entries, and 3,095 memberships replay exactly, with zero selected-record
  dirty overlap.
- Two disjoint source-stratified full-file reviews decide all 204 alternatives: 84
  approvals and 120 rejections. Approval counts are HAMAP 20, InterPro 25, PANTHER 20,
  and Pfam 19. Sixteen records are all-rejected: `MF_00049_B`, `MF_00054_B`,
  `MF_00291_B`, `MF_00368`, `MF_00371`, `PTHR10110`, `PTHR10239`, `PTHR10535`,
  `PTHR10587`, `PTHR10638`, `PF30494`, `PF30495`, `PF30676`, `PF30871`,
  `PF31018`, and `PF31234`. HAMAP/InterPro and PANTHER/Pfam partition SHA-256 values
  are `4306ed2d8a4483ee2d5bf8231187e88351d6a23aad747f8ee3e97e573c006b1c`
  and `c91ec5a99359bbb8d7a0a7f590c15cc9bfb2d5f46b84bcb9d9f054e3059fcc82`.
  A blind independent reviewer initially matched 198/204 row decisions and 97/100
  group choices; exact subfamily evidence resolved the three primary-only differences
  (`PTHR10388`, `PTHR10489`, and `PTHR10694`) in favor of the partitions, yielding
  final independent endorsement of all 204 decisions. There was no approve-versus-
  all-reject disagreement.
- Canonical finalization was byte-idempotent. Decision JSONL and completed approval TSV
  SHA-256 values are `21e3f0bfb31fafb218e3154254c1a16d759d4d38ca5305091e5110455a6238a9`
  and `0afad2998f7172a7e488eeb69541ce6a71d8282976f55bcdb78065512b00552e`.
  Decision-aware replay reports 44 hard rows/16 hard records and zero hard-approved
  candidates. Two exact no-write promoter runs report 25/25 decided records per source,
  84 prospective record writes, zero already present, and conflict-free standalone
  totals of 205 ProteinReferences and 211 GroundingEvidence rows. Canonical standalone
  registry SHA-256 values are
  `f99a40644a36223f2f853ab459b7017958dc5f1ebc3eccddc814a0111ba8e8da` and
  `736b75c538bbfb25c0e8de329189709469d2c385cfb8fe6d68f4130b5446f9e4`.
  The batch's 84-file sorted preimage-manifest SHA-256 is
  `23a25b3b659f7a9fee3af96138856ce0dcb78d304b6ddb3f69450159d04bb9f6`.
- Cumulative in-memory replay of batches 002--007 proves all 509 approved candidate IDs,
  target records, and evidence IDs pairwise disjoint; all 509 current files still match
  their bound preimages and none is dirty. The selected projections contain 459 unique
  ProteinReference IDs; 35 recur across batches (40 extra occurrences), always as
  byte-identical rows. The sequential replay exactly reproduces every prior checkpoint
  and yields 574 references and 636 evidence rows, with SHA-256 values
  `b92a29314c675e60bb66b4ee8004da4dbacfeb830abdaa26e6ab73ef471c9d1e` and
  `266f26a6cb716ce3f489ad4e623d0fac1c0d81e611d265c91e3ed73f28e290bc`.
  The combined 509-file preimage-manifest SHA-256 is
  `cb8cd470fd8629a9a227d34aaefe9aaa7f33da20c3f6993344a82d542466ca38`.
- Two final-code full-queue replays are exact and took approximately 58.9 and 54.4
  seconds wall time. Across 137,341 rows/62,696 records, the gate now finds 6,671 hard
  records/16,001 hard rows: 1,209 template-only, 20 malformed, 3,112 truncated, two
  family-identity conflicts, 15 positional conflicts, 2,450 scope conflicts, and 53
  unresolved placeholders. It also reports two low-information and 108 low-whole-
  protein-coverage review findings. Relative to batch 006's final gate, only the two
  exact malformed records/six rows and PTHR10587/three rows are added. The SHA-256 over
  the compact sorted-key projection of record/row counts and finding counts is
  `0828e3507738251e9eb76a8e79f352efcba9cd42659dbc68cd9d8d704fe252c6`.
- Final verification passed 250 focused UniProt grounding tests in 20.33 seconds; an
  independent current-byte gate/resolver slice passed 82 tests. Ruff lint and format
  checks, byte-compilation, Just parsing, `git diff --check`, and closed-schema
  validation of all 100 selected records passed. The durable registries remain
  unchanged at 126 references/127 evidence rows and retain SHA-256 values
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  Finalization wrote only ignored review artifacts. No promotion `--apply`, trait write,
  durable-registry write, commit, or pull request was authorized or attempted.

### 2026-08-24 — eighth review batch, semantic gate boundary, and durable-base audit

- Selector v5 deterministically staged `ready-local-review-008-s9of18`: 100 records,
  204 alternatives, and 198 distinct proteins, with exactly 25 records per source and
  candidate-row counts HAMAP 51, InterPro 44, PANTHER 69, and Pfam 40. Candidate,
  JSON-manifest, and TSV-manifest SHA-256 values are
  `4b5801a897e14646e92f2f232d64977cd1f339a242f919918dc7f06157300c41`,
  `a9056b2feb86d4161f39ea66ea16047099cb20211724e56be55973f0b3692ff2`, and
  `76c1e70c7011d79f47d1163952e7002c7d3299e8d99b6617e2fc5250ebdb02cd`.
  The immutable full-queue SHA-256 remains
  `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e`.
- Two live exact-accession UniProt fetches at release `2026_02` were byte-identical.
  All 198 requested proteins resolved, 2,670 exact membership rows were retained, and
  no accession was blocked. Registry, membership, and header-only-blocked SHA-256
  values are
  `ca269840873d45add43bf0aeb05e22abd24ffefc52f59aa76749e20a40496bba`,
  `84f30b46088d6994479d9cc2cfe90b5b16d6a4ab2ef62c0d2ca93fe8d275e91b`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Full-file review found two new substantive, source-bound defects.
  `HAMAP:MF_00100_A` labels monomeric IF-2/infB, but exact member MF_00100_A is
  integrated into InterPro:IPR004544, whose copied abstract distinguishes aIF-2 from
  aIF-5B and identifies archaeal aIF-2 as a heterotrimer. The normal and HAMAP-aware
  InterPro projection SHA-256 values are
  `fa536b31536e660a28b1fe2a23507d1c352a44614e04fedd28b1e1f8b7d7a51d` and
  `2d6875b1d76374c98afd3f31863103aa555e6c91d1e4b2d07255ab72bd63714e`.
  The narrowly exact `SOURCE_FAMILY_IDENTITY_CONFLICT` rule does not affect sibling
  `MF_00100_B` or corrected local prose.
- InterPro:IPR063510 and mapped `Pfam:PF30280` identify a CNN1 C-terminal domain in
  their titles and opening sentence, but the same exact source abstract later says
  `This N-terminal region` in text copied from the separate N-terminal entry. The
  `SOURCE_POSITIONAL_IDENTITY_CONFLICT` extension requires one explicit title
  direction, the same opening-sentence direction, and one opposite deictic `This
  <direction>-terminal region`; ordinary mentions of the opposite terminus remain
  clean. IPR063510's projection SHA-256 is
  `0c91d9317b9d419adb489b862e9eb7d070439f7df07b4e573add1722470a64eb`.
  Exhaustive replay of all 54,190 pinned InterPro entries found only IPR063510 under
  this exact rule. Both extensions bind InterPro XML SHA-256
  `c77fe193c1a0de8df903deff9325f734bfca3c9fbf59fd4ce697489c33ef0d87`.
- The same corpus-wide source audit fixed an important policy error before finalization:
  duplicated words and readable split-hyphen spacing are upstream typography debt,
  not hard content defects when the family/domain identity and occurrence evidence
  remain complete. `is a is a`, `found found`, `methyltrans- ferase`,
  `RTT101(MMS1- MMS22)`, `S- adenosyl-L-methionine`, and
  `membrane- associated complex` therefore remain non-hard. The one-letter
  BACC1-to-ACC1 typo in IPR060630/PF27797 and MP6-to-M6P transposition in IPR060126
  are likewise unambiguous provider-text debt, not competing trait identities. This
  preserves valid Batch-001 `PF29583` and Batch-007 `PF31156` approvals. Hard malformed
  checks remain restricted to substantive corruption: literal `[,.`, terminal `(.`,
  and `represents a of`. Final gate and focused-test SHA-256 values are
  `595757928ad316800b2966dac3de9a23838f3af8f537916a841996d3e566e5a9` and
  `7dcfc3bd354c6402e034edf6c915062b9b415642efc37ac12c4c26a93ee56bd4`.
- Final resolution was repeated twice and is byte-identical: 174 alternatives qualify
  and 30 are hard-rejected across 14 records. Staging contains 170 distinct
  ProteinReferences and 174 GroundingEvidence rows. Resolved, blank-review,
  staging-reference, and staging-evidence SHA-256 values are
  `5c178ddf7c490dbfa77e6a22c42c067ef6ec85cfd429137f0f5247d7a4fabb0b`,
  `75f108fcaea76caae4be216b3f1add4fac392c91befc6c9acadbaf16cef56822`,
  `d6841bc85d59934f5bca8739f241050975ad96eb03f772ab753b8b25edf2c78d`, and
  `b036f8b07c3831d0f66a3e4449e502c8645c49ccc9d50f2d2d1e05e2a3abe8a2`.
  Independent scratch replay reproduced every current YAML hash, source binding,
  UniProt sequence/checksum, interval, staging projection, and resolution digest; none
  of the selected records overlaps the 127 dirty Batch-001 targets.
- Two disjoint source-stratified full-file reviews decide all 204 alternatives: 85
  approvals and 119 rejections. Approval counts are HAMAP 18, InterPro 24, PANTHER 21,
  and Pfam 22. HAMAP/InterPro and PANTHER/Pfam partition SHA-256 values are
  `9e5ae0b792c7e280a0361424a0ea730b10c37aec2e6d0018d8733b018a4ae357` and
  `ce24b614ed12445d4eb3af643dd948c740e9947904cffa01e58b3dce45cc267b`.
  Fifteen records are all-rejected: `MF_00055`, `MF_00100_A`, `MF_00245`,
  `MF_00273`, `MF_00441`, `MF_00508`, `MF_00537`, `IPR061276`, `PTHR10000`,
  `PTHR10134`, `PTHR10265`, `PTHR10394`, `PF29395`, `PF30280`, and `PF31016`.
  `PTHR10000` is the sole manual addition to the 14 machine-hard groups: its pinned
  root says phosphoserine phosphatase, but every selected child/candidate is another
  phosphatase or HAD identity. The pinned PANTHER projection SHA-256 is
  `f0d433bfdb30d9628b5658a06210a277046386fdd4e564bf210d38de6717a508`.
- Independent arbitration endorsed all decisions. Three primary choices needing
  explicit evidence were `PTHR10131` -> UniProtKB:P39429 (TRAF2/SF21 and 466/501
  whole-family footprint), `PF29299` -> UniProtKB:O15111 (IKK-alpha and exact 75-aa
  model), and `PF30919` -> UniProtKB:Q9SAF6 (literal CRWN2 match). Canonical
  finalization is invariant to partition order. Decision JSONL and completed approval
  TSV SHA-256 values are
  `6d4f2ee7d2f7b546d8280114970497bdc91b8fa1a604c5fe3d9195a870ace636` and
  `be794ed6ac1cfe54c8f1f7c9cdc6e7a540193c343c261f317b4468d119847049`.
  Decision-aware replay finds 30 hard rows/14 hard records and zero Batch-008
  hard-approved candidates.
- Two final-code full-queue replays were exact and took 56.38 and 54.28 seconds wall
  time. Across 137,341 rows/62,696 records, the gate now finds 6,674 hard records and
  16,004 hard rows: 1,209 template-only, 20 malformed, 3,112 truncated, three
  family-identity conflicts, 17 positional conflicts, 2,450 scope conflicts, and 53
  unresolved placeholders, plus two low-information and 108 low-coverage review
  findings. The compact sorted projection SHA-256 is
  `85b35a1925fa73cb8bc1bfe279971af959d923f2635994f7740f4a4809eaa630`.
  Relative to Batch 007, only MF_00100_A and direct/mapped IPR063510/PF30280 add
  three hard records/rows.
- The selected-only no-write promoter preflight passes twice with 25/25 reviewed
  records per source, 85 prospective writes, zero already present, and standalone
  totals of 207 references/212 evidence rows. Canonical standalone SHA-256 values are
  `76bf7dcc39efa55cab527d7d8d0a8f7a21375e311afcffd354422e52fe6fdacb` and
  `b7346cf83472abea4064c5aab03fb2d85a7b1e24d2a616008971b747ac9630d1`;
  the 85-file preimage-manifest SHA-256 is
  `43b77e8f451ab3b8c14aa272e2940e6e9b557001767e2b90391dee8312b6f782`.
  This selected-only success is not a sufficient durable promotion authorization due
  to the historical-base failure below.
- Cumulative in-memory replay of batches 002--008 is internally clean: 594 approvals
  and 830 rejections, with approved candidate IDs, 594 target paths, and 594 evidence
  IDs pairwise disjoint; all 700 reviewed current files retain their bound preimages and
  none is dirty. The selected projections contain 528 unique ProteinReference IDs; 45
  recur across batches (54 extra occurrences), always byte-identically. The structural
  merge yields 642 references and 721 evidence rows, with SHA-256 values
  `86b3e2ce2bdc8122e8203ea1fe1372d0c7c11726563735a85d50068a315f5ca8` and
  `bb9e98a2e8a076237bab8973709693733a77a2112595b0a5f041b48889cffcf1`.
  The combined 594-file preimage-manifest SHA-256 is
  `54075cb13eedbb188f328d8bbf5ff0e75adc69ab7af15fa70efbcda5de25e5b7`.
- A new retrospective current-gate replay exposes seven hard-approved claims in the
  already-durable Batch-001 state: `MF_00025`, `MF_00150`, `PTHR10057`, and
  `PTHR10136` have exact historical InterPro definition truncations; `PTHR10352` has a
  template-only definition; `PF30519` and `PF30678` assert Pfam Family/WHOLE_PROTEIN
  scope while their integrating InterPro entries are Domain/LOCALIZED. All seven
  current examples and evidence rows are still marked `QUALIFIED`; all seven files are
  among the 127 dirty Batch-001 targets. Batch-001 `PF29583` and Batch-007 `PF31156`
  are clean under the corrected typography policy. Batches 002--008 each have zero
  hard-approved candidates.
- Durable promotion is now prohibited even though the selected-only preflight passes.
  Repair the seven records, explicitly re-review their examples, and add a transactional
  `qualified_record_bindings.jsonl`-style receipt registry keyed by evidence ID before
  any future `--apply`. Each receipt must bind candidate ID, trait ID, repo-relative
  record path, and approved content-gate projection/digest. The promoter must fail
  closed when durable evidence lacks a unique receipt and must replay every receipt-
  listed durable record plus newly selected rows through one pinned gate before any
  mutation. This makes the check proportional to durable claims rather than scanning
  all 429,271 YAML files and prevents the precise Batch-001 blind spot; there must be no
  bypass for existing hard debt.
- Verification passed 252 focused UniProt grounding tests in 22.94 seconds, Ruff
  format/lint, byte-compilation, `git diff --check`, and strict closed-schema validation
  of all 100 selected records. Full semantic validation of all `data/traits` returned
  only its TSV header in 119.48 seconds; that validator does not yet enforce the
  source-aware content gate and therefore does not clear the seven-item debt. Durable
  registries remain byte-unchanged at 126 references/127 evidence rows with SHA-256
  values `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  No promotion `--apply`, trait write, durable-registry write, commit, or pull request
  was authorized or attempted.

### 2026-08-24 — review batches 009--011, selector v6, and receipt hardening

- Selector v5 replayed finalized batches 001--008 as exact, checksum-bound exclusion
  quadruples and scanned shard counts 1--100. Sixty-eight quota-satisfying tuples were
  found; the global minimum was four reopened groups and the first optimum was zero-based
  shard 6 of 14. The resulting batch, `ready-local-review-009-s6of14`, contains 100
  records, 196 alternatives, and 193 proteins: 25 records per source and candidate-row
  counts HAMAP 54, InterPro 33, PANTHER 73, and Pfam 36. It deliberately reopened
  `IPR063291`, `PTHR10031`, `PTHR10052`, and `PTHR10093`. Candidate, JSON-manifest, and
  TSV-manifest SHA-256 values are
  `4fd467c531b35663a618c702856595326b03b5ae078403308d8b26a97a06e8ba`,
  `9288364db457dbcc044c3a90dc00731fdaaaa156c30929dc0fa1efdde3f45c88`, and
  `6ab2631eaf93c14306d97a3b6484a6364d93394f5d2f535f214788a95fb380af`.
  Repeated selection and reversed exclusion order were byte-identical, and no selected
  path overlaps the 127 dirty Batch-001 targets.
- Two exact UniProt fetches were byte-identical at release `2026_02`: all 193 requested
  accessions resolved, 2,821 membership rows were retained, and none was blocked.
  Registry, membership, and empty-blocked SHA-256 values are
  `94fc191aa2dab45205f8181ab314f073ed005a0f6feee51cfef81855ce861846`,
  `69b798fbd18a0b6fbeef883290f32346610480fed095802ae09f295415653960`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Final-code resolution was repeated twice and was byte-identical: 151 alternatives
  qualify and 45 are machine-hard across 17 records. Exact staging contains 148
  ProteinReferences and 151 GroundingEvidence rows. Resolved, blank-review,
  staging-reference, and staging-evidence SHA-256 values are
  `a072e01589da28b2b74d4407d6b666c9bbeebf8a8d3d6b3dd6a1ce95edbb677c`,
  `1060eb1845c842b9dc332e00a79e62a55ccd92c9ca733af93a989803f39bef47`,
  `8c0cae0f22036169fd1c665070a3b772cd083ae2f805684c738af84216df55f1`, and
  `06690ea0d6cd71db7d5a4aec86f23a90d483580536b9950c11a255f5a86580c3`.
  Independent replay verified every record, candidate, protein, sequence, provider,
  interval, digest, and staging projection.
- Two disjoint full-file source reviews decide all 196 alternatives: 83 approvals and
  113 rejections, with source approvals HAMAP 18, InterPro 24, PANTHER 17, and Pfam 24.
  HAMAP/InterPro and PANTHER/Pfam partition SHA-256 values are
  `8051b3b00cd24e4ddf1557edb1dda5d2b0a97f36ba7fab5982ebeda92ca371aa` and
  `2e0786667c7808333a4711511458bfec6e1a000b5f948215ba79ae3b4ed4e276`.
  The 17 all-rejected records are `MF_00099`, `MF_00177`, `MF_00197`, `MF_00251`,
  `MF_00294`, `MF_00360`, `MF_00452`, `IPR063291`, `PTHR10031`, `PTHR10052`,
  `PTHR10093`, `PTHR10374`, `PTHR10515`, `PTHR10634`, `PTHR10792`, `PTHR10836`,
  and `PF31006`. Thirteen have truncated definitions, three are template-only, and
  `IPR063291` has the exact terminal `(.` source artifact. All four reopened records
  were independently reconfirmed all-reject.
- A blind all-196 audit agreed on every all-reject decision and 78 of 83 initial
  primaries. Source arbitration retained `MF_00435` -> UniProtKB:P05793 because the
  pinned KARI source names E. coli K-12 as a key species; retained `PTHR10270` ->
  UniProtKB:O15370, `PTHR10540` -> UniProtKB:O04202, and `PTHR10555` ->
  UniProtKB:O60749 because exact named-child identity was tied but their family spans
  were stronger; and selected `PTHR10676` -> UniProtKB:Q19542 because its resolved
  cytoplasmic-dynein identity outweighed the small coverage advantage of a
  heavy-chain-like alternative. `PF29750`'s TasA/TapA opening token, `PF30683`'s omitted
  human-readable "domain 4", and `PF30356`'s GPT2/SCT1 breadth are non-hard prose debt:
  their exact bound carrier/member identities remain unambiguous.
- Canonical finalization was invariant to partition order. Decision JSONL and completed
  approval TSV SHA-256 values are
  `f74912d184e15e06c59f266cb47b66c9f9e93b0bb8fbcddbf6864d4eb0effaf2` and
  `5ddda86a0992ddd716c872dc802161059f77f69be699ac4ff694c7484d1607a5`.
  Two decision-aware content-gate replays find 17 hard records/45 hard rows and zero
  hard-approved candidates. Closed-schema validation passed all 100 selected records.
- A fresh full-queue replay preserves the exact 6,674 hard records/16,004 hard rows and
  finding counts recorded after Batch 008. Its longer 107.31-second wall time occurred
  under concurrent selector, cumulative, and test workloads; it is not a new standalone
  performance baseline. The compact result remains the prior
  `85b35a1925fa73cb8bc1bfe279971af959d923f2635994f7740f4a4809eaa630`
  projection.
- An independent cumulative replay of batches 002--010 reconstructed every finalizer
  output and current record preimage. The 1,831 decisions comprise 766 approvals and
  1,065 rejections across 900 physical review groups, with 134 all-reject adjudications.
  Approved candidate IDs, 766 target paths, and 766 evidence IDs are pairwise disjoint
  across these batches and have zero overlap with Batch 001. The selected projections
  contain 659 unique ProteinReferences; 74 protein IDs recur across selected batches and
  17 overlap the durable base, with every repeated reference byte-identical. Structural
  merge with the unchanged durable base yields 768 references and 893 evidence rows,
  with SHA-256 values
  `61c38d51e0fc21fa35c6eb2fdeb56a284716bae6c73a0ab933fc840acf14c9c5` and
  `8aad65d195df8155d554e52f5bb3c2c8a59a7576dfa1f1bc2c655b8085dc702a`.
  Batch 010's selected 89-file and all-100-file preimage-manifest SHA-256 values are
  `9392e40d1b43af1274df34cbb34e053611b270dc0deaa30322191623941466c6` and
  `4a9824b9256925a88b9cf8df53b2a55117e7057d50bab40549ef562bcf841dc9`;
  the combined selected batches-002--010 value is
  `439c55821476c5134d341a84a72567605b23164b14502265b892cc864a72fad4`.
  The canonical manifest is the global record-path sort of
  `<record_sha256><two spaces><record_path>\n`. The through-Batch009 structural hashes
  still reproduce exactly. The older batches-002--005 value `487559536...` remains
  stale: current immutable bindings reconstruct
  `1c0c75276a3033942f43c7a1392e70a563653270abe591f1cb9a55fb317fec89`,
  while the through-006, -007, -008, and -009 checkpoints reproduce exactly.
- With Batch 009 finalized, selector v5 replayed exact batches 001--009 and exhaustively
  evaluated all 5,050 shard tuples for Batch 010. Fifty-nine tuples met the four-source
  quota; the unique global optimum reopens five records at zero-based shard 7 of 12.
  `ready-local-review-010-s7of12` contains 100 records, 211 alternatives, and 204
  proteins: exactly 25 records/source and candidate rows HAMAP 58, InterPro 42, PANTHER
  69, and Pfam 42. The reopened records are `MF_00059`, `PTHR10117`, `PTHR10201`,
  `PTHR10459`, and `PF30433`. Three runs, including reversed exclusions, were
  byte-identical; all 15 manifest invariants pass and dirty/prior-approved overlaps are
  zero. Candidate, JSON-manifest, and TSV-manifest SHA-256 values are
  `c3468c977e80e7c8593119f3f207c8f86b6424fd59132cf25b7bac1b437eaaf2`,
  `83b903de4947f858af25a6d531b47c2692c716e259b5ddec9e83e4dc3f32b60f`, and
  `ba70dbb7d5873f89fda27cf508afba279af4feb72be66d48fe8b05769142d8b3`.
- Two Batch-010 UniProt fetches were byte-identical at release `2026_02`: all 204 exact
  accessions resolved, 2,848 unique memberships were retained, and none was blocked.
  Registry and membership SHA-256 values are
  `1fe5937ea5a14e9c247378d738a424fb8cd467ebde53697fb55740ad78cc2e4c` and
  `fe8145f99507b0a600e0e119508fc5b96dba4c52e8f8ee9a014086a3d3b3f851`.
  Two resolver runs were byte-identical: 184 alternatives qualify and 27 are machine-
  hard across 11 records; staging contains 179 references/184 evidence rows. Resolved,
  blank-review, reference, and evidence SHA-256 values are
  `be16b6e61b959714c5368157c58d514bb3a835525f7a5644424bc497b4e82aae`,
  `0591dbc639649acde0555a558fb71f4e2e0fb2778e754cb952d5b4bd5351360f`,
  `1b4aa50da312e6aee04c5f6a83a05624f218a2a957601560b5f3e687d9706461`, and
  `8641e56fce18d0a277b8df2446cd935085ad2d518f771c9e6be3b98b67da43f7`.
  All 211 record/digest bindings, 1,028 provider bindings, staging projections, and 100
  closed-schema records replay exactly.
- Two disjoint full-file reviews finalized all 211 Batch-010 alternatives as 89 approvals
  and 122 rejections, with source approvals HAMAP 22, InterPro 25, PANTHER 21, and Pfam
  21. HAMAP/InterPro and PANTHER/Pfam partition SHA-256 values are
  `8f6fe0b4967d2881ce13a1bbd97c5c2c1b9d8322d7e2da7f3a1a6163ba88b3b1` and
  `3110e15e70f9095474ee385904cc0fda3a0af758e294e3517e0b3d9829d807d0`.
  The 11 all-rejected records are `MF_00059`, `MF_00264`, `MF_00283`, `PTHR10117`,
  `PTHR10459`, `PTHR10519`, `PTHR10589`, `PF29594`, `PF29961`, `PF30379`, and
  `PF30433`: five truncated definitions, three template-only definitions, one unresolved
  placeholder, one family-identity conflict, and one scope conflict.
- A blind cross-audit initially differed on five primaries. Exact source arbitration
  retained `MF_00159` -> UniProtKB:F4K0E8 as the only explicit ferredoxin/EC 1.17.7.1
  match; `PTHR10472` -> UniProtKB:P0A6M4, `PTHR10510` -> UniProtKB:P14406,
  `PTHR10605` -> UniProtKB:P52848, and `PTHR10682` -> UniProtKB:P51003 on the exact
  named-child/source-superfamily evidence. Canonical finalization was partition-order
  invariant. Decision JSONL and completed approval TSV SHA-256 values are
  `d0dd9f0a31d0def8ca89f654d50a5c08e7e0d5da102a2e703846dfdb7c51f76d` and
  `2a1fe9a9a339da30db3a8c2ded19498e50c90e56b8db9f2794fbd61a860b4e9d`.
- Two decision-aware gate replays find the same 27 hard rows/11 hard records and zero
  hard-approved candidates; every one of the 211 stored finding projections matches a
  fresh gate result. Serial strict validation passed all 100 files with zero errors (the
  parallel run's semaphore `PermissionError` was a sandbox limitation, not a validation
  failure). A real no-write promoter replay reaches 25/25 source coverage and then stops
  only because the unchanged 127-row durable base lacks its qualified-record receipt
  registry. Against an isolated empty durable directory, dry run succeeds for 89 record
  writes, 86 proteins, 89 evidence rows, and 89 receipts and writes nothing.
- Adding finalized Batch 010 to the exact exclusion history exposed a selector-v5 design
  gap: `PTHR10201` was all-rejected in Batch 001, repaired/reopened, and then approved in
  Batch 010, but v5 accepted repeated histories only when every adjudication was
  all-rejected. Selector v6 now permits exactly one independently complete approved
  adjudication to terminally supersede one or more independently complete all-rejected
  adjudications for the same trait ID and path, independent of artifact order. It binds
  current exclusion only to the approved candidate snapshot, removes the mixed history
  from all-reject/defer/reopen state, records both sides in a content-addressed JSON/TSV
  projection, and still rejects a second approved adjudication, partial/stale/unknown
  decisions, changed current approved alternatives, and cross-record candidate reuse.
  For `PTHR10201`, the Batch-001 all-reject -> Batch-010 UniProtKB:O60882 history SHA-256
  is `5e744ce72307428882b045efc7070dcf8830e5257e8bc9e82a11dad23d71a65d`.
- The selector schema, selection algorithm, and exclusion algorithm are all literal v6.
  The 60 focused tests, an independent semantic audit, `py_compile`, Ruff lint/format,
  and whitespace checks pass. Exact batches 001--010 replay both forward and reversed
  with identical selection. Selector and test SHA-256 values are
  `0a38007aa79f2de3482d3389aa558a53b8456d89fd658926cbae78e80f17ad56` and
  `d405d932aa5bac1fbc8363fe9fbe39010786f8983a19041627378fd6ff7199db`.
- Exhaustive Batch-011 selection evaluated 5,050 shard tuples; 48 met all four source
  quotas, two minimized reopened all-reject histories at six groups, and the first
  deterministic optimum was shard 10 of 14. `ready-local-review-011-s10of14` contains
  100 records/209 alternatives/209 proteins, exactly 25 records per source and candidate
  rows HAMAP 46, InterPro 47, PANTHER 74, and Pfam 42. The reopened records are
  `MF_00254`, `MF_00436`, `PTHR10258`, `PTHR10264`, `PF29189`, and `PF30753`.
  Three selector staging applies, including reversed exclusions, were byte-identical;
  all 17 invariants pass and overlap with Batch-001 targets or all 893 prior approved
  paths/candidates is zero. Candidate, TSV-manifest, and JSON-manifest SHA-256 values are
  `b408d2382dafe0f4b5eda19bdc6e73ec25e54a301350188d81ae444e8f157cf5`,
  `7e85a233824a72b24171ca41930df97ef81eff36c340079b702bfe418a038edc`, and
  `4fcb24aac86f930d1ad09ca96914a39cd6145d1913667a057328f1df950e18d4`;
  the exclusion-ledger-set SHA-256 is
  `08d4ff42d9b69120ff850e3e174e2772ef6526ed2325ce3986223cd8248f566f`.
  All 100 current record preimages match; their canonical manifest SHA-256 is
  `5a761cb294ded1e9ad4f3b5bece4e187c590414f39bff1c05834c84ece47953b`.
- Two Batch-011 UniProt fetches were byte-identical at release `2026_02`: all 209 exact
  accessions resolved, 2,868 memberships were retained, and none was blocked. Registry,
  membership, and empty blocked-ledger SHA-256 values are
  `6834691d04d4d6a73d3a5123b493c5d091b31a2b8d52a9dc6a3fc511f6e5fce6`,
  `32b67f32322eb7647339cb88c861bb180749a1483a8c520f72003f4d18ced858`, and
  `2d4a91a7c04e3e4f1b85500104ff1322ae6334c36b6ec5f488d969425fa7a8d6`.
- Batch-011 review exposed one exact source-family contradiction. `PANTHER:PTHR10593`
  is labelled `SERINE/THREONINE-PROTEIN KINASE RIO`, but exact mapped
  `InterPro:IPR031140`, the offered proteins, and pinned PANTHER children (`IDD`,
  `SGR5`, `MAGPIE`, and related names) identify plant IDD/C2H2 transcription factors;
  no child identifies a RIO kinase. A narrow source-bound
  `SOURCE_FAMILY_IDENTITY_CONFLICT` rule now hard-blocks its three alternatives. The
  rule was added test-first and explains both the Batch-011 resolver change from
  182/27 to 179/30 and the global delta of one hard record, three hard rows, and one
  family-identity finding. Gate source and focused-test SHA-256 values are
  `e4ea930dc54eedf840f464a289c11be3f47edc2abd6870c545070e3c7a8c5b51` and
  `f27a421355c95d564a888db8f21eb868bde57526f443666af66618f94352f5a1`.
- Two refreshed Batch-011 resolver runs were byte-identical: 179 alternatives qualify
  and 30 are hard across 15 record groups. Staging contains 179 ProteinReferences and
  179 GroundingEvidence rows, with every selected protein ID unique. Resolved,
  blank-review, reference, and evidence SHA-256 values are
  `16c2ed42a0fdb0ac181347d12e2515d6d68e2f7274ef45a42e7f7fbd91b75c3f`,
  `8a75d99a13725288067d721402fc754cbdafbf11770a4adf4fbbd6ed9e34e704`,
  `6670b9493a0bc1c24adccf735db02f1745adf1192d36b3c80314de84bc077f95`, and
  `733098bd16ff048c3a5798e093e21ba0a8547ca11d26412819fa6d593de5d6f4`.
  Fresh content-gate replay reproduces all 30 hard rows/15 records plus one review-only
  low-information finding on `PF29189`; serial strict closed-schema validation passes
  all 100 records with zero errors.
- Two disjoint full-file reviews decide all 209 Batch-011 alternatives as 85 approvals
  and 124 rejections. The HAMAP/InterPro partition contains 93 decisions/50 groups,
  44 approvals/49 rejections (HAMAP 19/27, InterPro 25/22), with SHA-256
  `3f90a881842522ea849a1ff77a3fcf51452c569cb4d4339e4ea39ce3fea69f4c`.
  Its all-rejects are `MF_00220_B`, `MF_00254`, `MF_00349`, `MF_00358`,
  `MF_00403_A`, and `MF_00436`. The PANTHER/Pfam partition contains 116
  decisions/50 groups, 41 approvals/75 rejections (PANTHER 20/54, Pfam 21/21),
  with final refreshed SHA-256
  `3e517f705e6ad29884d8e62bbcd5a435b9f33e46a1f95d58bfb2c604e2bc689e`.
  Its all-rejects are `PTHR10258`, `PTHR10264`, `PTHR10593`, `PTHR10867`,
  `PTHR10954`, `PF30333`, `PF30459`, `PF30636`, and `PF30753`. The 15 causes are
  ten truncated definitions, two template-only definitions, one family-identity
  conflict, and two scope conflicts.
- A blind cross-audit agreed on the biological outcome for all 100 groups and endorsed
  the review ledgers' five defensible representative tie-breaks. In particular, the
  final ledger keeps `PF30487` -> UniProtKB:Q9BZX4 as the more literal ropporin-1B
  exemplar and `PF30644` -> UniProtKB:O34673 as the first-named, slightly longer
  altronate-carrier occurrence. Canonical finalization and reversed reviewer-partition
  order are byte-identical. Decision JSONL and completed approval TSV SHA-256 values are
  `7e36798e9edd9afdf2ab8e913bcac27c873a91ccb1686f3b8ed5f69c8123648b` and
  `4e333c897e4571797927e1b6b16505755b37d539edcdd9d781644f2df5b4828c`.
  Dry run validated 209 decisions/100 groups/85 approvals/15 all-rejects without output;
  the actual finalizer wrote only ignored staging artifacts. Decision-aware replay over
  both canonical and partitioned inputs covers all 209 rows/100 records, finds the same
  30 hard rows/15 records, and has zero hard-approved candidates. No trait or durable
  grounding file was written.
- A fresh read-only cumulative reconstruction of Batches 002--011 reproduces all ten
  canonical finalizer outputs byte-for-byte. The 2,040 decisions comprise 851 approvals
  and 1,189 rejections across 1,000 adjudication groups, including 149 all-reject
  adjudications; repeated histories reduce these to 983 unique reviewed record keys and
  133 unique all-rejected keys. Approved candidate IDs, record paths, and evidence IDs
  are each unique across all 851 selections and have zero overlap with Batch 001. All
  851 current target files retain their bound preimages, whose canonical combined
  manifest SHA-256 is
  `9c4637fc2b318aa44ca6b4d9c94a4e54c53c4ee32dca79afc68969aefdad63f2`.
  Batch 011's selected-85 manifest SHA-256 is
  `8aa57485a1ffbb468fa06af9395e1f471a9d36b7460cba1681518626ac82685b`.
  The selected projections contain 721 unique ProteinReferences; 91 protein IDs recur
  for 130 extra occurrences and 18 overlap Batch 001, always byte-identically. A
  hypothetical structural merge with the unchanged durable base yields 829 references
  and 978 evidence rows, with SHA-256 values
  `30508c5c141beb272f0f59f24995fbe271ed3f6a09487ae9f4f4da3e45bebb3a` and
  `10a4b64bdfdb8b8bb91d3f7b59bf20ffb56052dbe746ae2dd215ad1f4f9b18b8`.
  The through-Batch010 counts and hashes reproduce exactly as a control. This is a
  no-write integrity result, not a promotion or authorization.
- A measured post-`PTHR10593` full-queue replay took approximately 74 seconds. Across
  137,341 rows/62,696 records, it finds 6,675 hard records and 16,007 hard rows: 1,209
  template-only, 20 malformed, 3,112 truncated, four family-identity, 17 positional,
  2,450 scope, and 53 unresolved-placeholder findings, plus two review-only
  low-information and 108 low-coverage findings. The immutable candidate queue SHA-256
  remains
  `5e4537c6538700f9953c1ca0e7e3e9439380dae3d42f073213fdd8250fab519e`.
  Gate-focused tests pass 14/14; the current selector/finalizer/gate/validator/promoter
  suite passes 212/212 in 23.95 seconds. Ruff lint/format, byte-compilation, and
  whitespace checks pass.
- The Batch-011 promoter rehearsal remains unmeasured in this sandbox. The attempted
  `just promote-uniprot-review-batch ready-local-review-011-s10of14` command failed
  before promoter startup because `uv` could not read its external cache; permission
  escalation was denied, so neither a direct workaround nor the isolated-empty-durable
  rehearsal was run. This is not a promoter failure or success. The attempt changed no
  files: durable registries retain their pinned hashes and the qualified-record receipt
  remains absent. A no-`--apply` production-base rehearsal followed by an isolated
  empty-durable rehearsal is still required for this batch.
- The promoter now implements the fail-closed durable receipt required by the Batch-001
  audit. It defines `data/grounding/qualified_record_bindings.jsonl` as exact-schema
  JSONL keyed uniquely by evidence ID, but that durable file does not yet exist. Every
  future row binds candidate ID, trait ID, canonical repo-relative record path, the
  complete post-promotion record SHA-256, a reviewable current content-gate projection,
  and its digest. A missing registry is permitted only when durable
  evidence is empty; missing, extra, duplicate, malformed, digest-tampered, stale-record,
  stale-policy, and hard-current-content receipts all fail before mutation. Every receipt
  must dereference exactly one installed `QUALIFIED` occurrence equal to its durable
  GroundingEvidence row.
- Whole-protein evidence intentionally omits its supporting HMM interval, while the
  content gate needs that interval for coverage checks. The receipt retains this exact
  resolved interval, but replay accepts it only when coordinates are canonical integers,
  sorted and in bounds, and when the complete identity reconstructed from durable
  evidence, ProteinReference, and the bound interval reproduces `candidate_id`. Newly
  selected rows must also reproduce their candidate IDs before a receipt can be created.
  Durable and newly selected records are then evaluated together by one pinned
  `RecordContentGate`; there is no selected-only or existing-durable bypass.
- Promotion apply now snapshots exact bytes or nonexistence for every changed registry,
  receipt, and trait target and restores all attempted targets on an in-process install
  failure. Each individual replacement is atomic, but sudden process/OS failure is not
  truly multi-file crash-atomic without a journal; the implementation states this limit
  explicitly. Promoter source and test SHA-256 values are
  `db8ff983ce8f09497cb71543f3c64cbc18c6b165b3d49e1d611919bfaf58b701`
  and `39f677d6e69a4e922a2e13a5c5298f167ddaacdab930cff4be732ed706f93813`.
  Independent verification passed all 81 promoter tests and a broader 332-test UniProt
  suite, Ruff lint/format, byte-compilation, and whitespace checks. Tests cover absent,
  duplicate, tampered, stale, out-of-bounds, changed-coverage, hard-debt, clean-idempotent,
  race, and injected rollback cases.
- The real Batch-009 no-write promoter now reaches 25/25 reviewed records for each source
  and then exits 2 because 127 durable evidence rows have no receipt registry. No receipt
  file or durable/trait output is created. Against an isolated empty durable directory,
  the same preflight passes with 83 prospective record writes, 81 proteins, 83 evidence
  rows, and 83 receipts, then writes nothing because it is a dry run. This distinguishes
  a clean selected batch from the unsafe durable base without weakening either gate.
- A read-only Batch-001 migration audit mapped all 127 durable evidence IDs uniquely back
  to the exact digest-bound approved candidate, current installed occurrence, record, and
  protein. There are zero missing, duplicate, staging/durable, occurrence, or byte-drift
  mismatches; replaying each approved edit on its exact Git preimage reproduces every
  current record byte-for-byte. The gate partitions these claims into 120 clean and the
  same seven hard debts. Canonical theoretical receipt-image SHA-256 values are
  `bbac03ec6d82e3e8e43a07b5fcd4b887c3ceee5f8537517ea41fb98e304416e9`
  for all 127, `a677ca273c0d401faca9d200c94093c73d6c27864ff38c04f3a3387b38e37d8c`
  for the clean 120, and
  `0d24186e637cb1a4e6372e8efcd21fe0e6095e790abb929837f7630f88cf4f01`
  for the hard seven. The production loader accepts the theoretical full shape, then the
  production gate rejects exactly those seven. These hashes are forensic evidence only;
  no receipt artifact was written.
- The conservative repair path is to restore the complete pinned InterPro abstracts for
  the four truncated records and re-review their complete 18-row record groups; demote
  the template-only `PTHR10352` and scope-conflicted `PF30519`/`PF30678` rather than
  laundering them through a receipt. The expected conservative result is four retained
  approvals and three removed claims, leaving 124 evidence rows/123 proteins before new
  staged batches. Repair must generate new resolution digests and decisions, pass the
  current gate and semantic/strict validators, and install repaired traits, pruned
  registries, and a complete 124-row receipt image in one rollback-capable transaction.
  It still requires explicit authorization; the receipt registry must not be bootstrapped
  separately first.
- `scripts/bootstrap_uniprot_record_bindings.py` now makes that separation mechanically
  enforceable without pretending to repair the durable state. It accepts only the six
  exact checksum- and cardinality-pinned Batch-001 resolved, digest-bound decision,
  staging, and durable inputs; reconstructs all 127 reviewed installs from their Git
  preimages; proves global installed-occurrence uniqueness; rederives candidate and
  receipt identities with production helpers; and replays the current pinned gate. Dry
  run is the default. Its optional `--write-staging` mode can write only an incomplete
  clean-receipt JSONL, an explicit hard-blocked JSONL, and a manifest beneath the ignored
  review-batch report directory, uses the production rollback transaction, and still
  exits 3 because coverage is incomplete. Complete, durable, trait-tree, and
  `data/grounding` outputs are categorically refused.
- The real Batch-001 dry run reproduced 120 clean and seven hard-blocked claims and the
  same forensic all-receipt SHA-256
  `bbac03ec6d82e3e8e43a07b5fcd4b887c3ceee5f8537517ea41fb98e304416e9`; no report,
  trait, receipt, or durable artifact was written. The focused bootstrap suite passed 18
  tests in 71.05 seconds, including the approximately 70-second real-fixture replay;
  an independent direct rerun of that real-fixture test passed in 70.34 seconds. Nine
  production-receipt compatibility tests passed in 2.43 seconds, and Ruff, formatting,
  byte-compilation, and whitespace checks pass. Bootstrap source and test SHA-256 values
  are `9acb8c322c543c33ebb56f0460413a09d2ea479356d3996050b65a38d39ec527` and
  `cf6bfef81c0e862725e65c42a64352c2d0699c1658f24cf1b4728b12421c2261`.
- Immediately before any optional staging write, the bootstrap rehashes all six inputs
  and all 127 receipt-covered records. This closes ordinary concurrent-curation races
  for the claims it can emit, but it is not a lock over all ungrounded YAML files. The
  reused transaction provides exact rollback for Python/I/O failures; as with the
  promoter, a sudden process or OS crash remains non-journaled and therefore is not
  truly multi-file crash-atomic.
- Durable registries remain byte-unchanged at 126 references/127 evidence rows with
  SHA-256 values `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`.
  The seven Batch-001 hard-approved claims and absent durable receipt registry still
  prohibit promotion. No promotion `--apply`, trait write, durable-registry write,
  commit, or pull request was attempted.

### 2026-08-24 — Batch 012 mechanical staging

- Selector v6 replayed all finalized exclusion histories through Batch 011. A control
  scan reproduced Batch 011's published 48 quota-feasible shard tuples, minimum-six
  reopening cost, and `(14,10)`/`(14,12)` optima. The Batch-012 exhaustive scan covered
  all 5,050 shard tuples, found 37 quota-feasible tuples, and found a unique minimum-six
  optimum at zero-based shard 12 of 14.
- `ready-local-review-012-s12of14` contains 100 records, 201 alternatives, and 197 unique
  proteins: exactly 25 records per source, with row counts HAMAP 49, InterPro 43,
  PANTHER 69, and Pfam 40. It deliberately reopens `MF_00140_B`, `MF_00280`,
  `PTHR10036`, `PTHR10066`, `PF26121`, and `PF29471`. Forward repeat and
  reversed-history selector staging are byte-identical; all 17 manifest invariants pass.
  Selected candidate/path overlap is zero against all 978 previously approved claims,
  the 127 Batch-001 targets, and all 127 dirty trait paths.
- Candidate, TSV-manifest, and JSON-manifest SHA-256 values are
  `363187699b9e1c772f3c2543d5f594f3afdd6c21cbd3ae0ca3c4f284c7171e9d`,
  `0c04b105a129b69372e706c77fc339d20edc8e3d5f8b98be84f975516f58e20c`, and
  `dc2bb4c1c5e7217a32f6c9b21ef112d2352395af6a3fae3b94a191d70e28b82d`.
  The 11-ledger exclusion-set SHA-256 is
  `fcf1dd6a6f3b6bed7b4fb613807d764351ffb8076e3720600b50de82031e9cec`;
  the canonical 100-file current-preimage SHA-256 is
  `3acc74b81051131e6643e28dd4b4198358761701aaf464613add2d42dbaa4e51`.
- The normal live fetch command failed before the fetcher started because this sandbox
  could not read the external `uv` cache. Its one scoped escalation request was denied
  and explicitly prohibited a workaround, so the registry, membership, and blocked
  outputs remain absent. Release, accession, double-fetch identity, and fetch-output
  hashes therefore remain unverified. No trait, durable grounding, source, test, or plan
  file other than this checkpoint was changed by Batch-012 work.
- A read-only audit of all 13 prior UniProt registries and membership snapshots finds
  release-`2026_02` ProteinReferences for only 106 of the 197 Batch-012 accessions,
  covering 110/201 candidate rows. All repeated rows and per-accession membership blocks
  are byte-identical, and all covered candidate metadata/checksums agree. The partial
  106-reference and 1,480-membership projections have SHA-256 values
  `6f22cb82a2715b4ddabcd6958efddd0ecac62072914bbc7d89db6faa62d1101c` and
  `435a62fec4f7ba31a52d0ee08be17b251fe16f3e26704f4a1de4dc8424a16126`.
  The other 91 accessions have no local release-stamped ProteinReference. All candidates
  use `INTERPRO_MATCH`, so missing exact UniProt source-trait membership is not the
  decisive blocker; missing versioned protein metadata is.
- No safe offline synthesis closes that 91-accession gap. The pinned residue frame has
  exact release-`2026_02` sequence/checksum/length for all 91 and `profiles.jsonl`
  independently corroborates labels, taxa, review status, and length, but profiles has
  no release provenance. The resolver correctly refuses to manufacture a versioned
  metadata assertion by joining those independently fetched sources. Across 603 trait
  files/779 legacy examples, only 23 accessions have exact inline sequences; none has a
  complete release-stamped ProteinReference. No raw UniProt offline-response fixture
  exists, and the current fetcher does not persist one. A fresh pinned fetch remains
  necessary before canonical resolution.
- Checksum-pinned source-content replay is nevertheless conclusive for the selected
  records: 19 groups/45 rows are hard and the remaining 81 groups/156 rows have no
  current finding. The hard partition is 11 `SOURCE_DEFINITION_TRUNCATED` groups/31
  rows, five `DEFINITION_TEMPLATE_ONLY` groups/eight rows, two
  `SOURCE_SCOPE_CONFLICT` groups/five rows, and one
  `UNRESOLVED_SOURCE_PLACEHOLDER` group/one row. The affected groups are seven HAMAP
  (`MF_00140_B`, `MF_00192`, `MF_00252`, `MF_00280`, `MF_00342`, `MF_00500`,
  `MF_00503`), six PANTHER (`PTHR10036`, `PTHR10498`, `PTHR10732`, `PTHR10759`,
  `PTHR10803`, `PTHR10889`), and six Pfam (`PF26121`, `PF29471`, `PF29847`,
  `PF30269`, `PF30382`, `PF30460`); InterPro has zero hard groups. These are
  provisional all-reject expectations until exact resolver digests exist.
- A read-only preliminary HAMAP/InterPro biological freeze selects 43 likely primaries
  and the seven gate-mandated HAMAP all-rejects. It found only representative tie debt,
  not another source-validity defect. This is intentionally not a review ledger: no
  decision can be canonical until the complete fetched registry is resolved and every
  row is bound to its exact `resolution_digest`.
- A separate preliminary PANTHER/Pfam freeze selects 38 likely primaries and the 12
  gate-mandated all-rejects. Its substantive representative ambiguities are limited to
  `PTHR10405`, `PTHR10656`, `PTHR10666`, `PTHR10916`, `PF29300`, and `PF31093`;
  each has multiple source-valid carriers rather than a hidden content conflict.
  Combined preliminary biology is therefore 81 likely primaries/19 hard all-rejects,
  but these counts remain hypotheses until every alternative qualifies or rejects under
  the complete fetched snapshot and both review partitions are digest-bound. The exact
  100-group mapping is preserved only as the explicitly non-canonical ignored note
  `ready-local-review-012-s12of14.preliminary-freeze.md`, SHA-256
  `815c46ba09db8f13c10e5ba639f1dbdfd931fb3ce3046a650074b5e1e2021131`.
  Its 100 trait keys and all 81 proposed trait/protein pairs replay exactly against the
  candidate ledger; it categorically forbids finalizer/promoter use.
- At this checkpoint a fresh release-`2026_02` live fetch remained the next operation,
  but the sandbox still required explicit network/cache permission. The hardened
  saved-plan/apply command contract immediately below supersedes the earlier idea of a
  direct `--apply` invocation. Do not substitute profile metadata, a synthesized offline
  response, or a partial registry.

### 2026-08-24 — Batch 012 request-plan, receipt, and resolver boundary

- `scripts/fetch_uniprot_registry.py` now makes dry-run a canonical stdout-only,
  no-network request plan. Apply requires both `--request-plan FILE` and `--apply`, and
  rederives the exact plan before the first response and again before installation. The
  plan binds the canonical candidate queue, exact selector-v6 manifest, expected UniProt
  release, all 197 target projections, two exact request URLs, all four output paths, and
  each output-parent device/inode. Because output directories are deliberately bound,
  replacing the review-batches directory invalidates a saved plan rather than silently
  retargeting it.
- The fetcher now validates the complete selector-v6 contract rather than only three
  correlated fields: exact schema 6, `batch_id`, `source_batch`, queue SHA-256, 201
  candidate rows, 100 one-to-one trait/record identities, per-record alternative counts,
  all 17 literal-true selector invariants, and both literal-true downstream review
  requirements. Every candidate must also provide a valid accession and complete
  sequence length/SHA-256/release triple before any request can be planned.
- All input and installed-output reads use component-by-component descriptor-relative
  `O_DIRECTORY | O_NOFOLLOW` traversal. Output parents are retained and rechecked through
  installation or verification; existing inode aliases, input/output aliases, parent
  symlinks, leaf symlinks, path swaps, and same-byte inode substitutions fail closed.
  Temporary files are created relative to the retained parent with `O_EXCL | O_NOFOLLOW`,
  fully written, file-`fsync`ed, descriptor-renamed, and directory-`fsync`ed. This removes
  the earlier close/reopen and parent-symlink races.
- Installation first replaces any prior receipt with a canonical content-addressed
  `UNIPROT_REGISTRY_FETCH_GENERATION_PENDING` marker, installs and re-verifies the
  ProteinReference JSONL, membership JSONL, and blocked TSV, and installs the completed
  receipt last. A failure before invalidation leaves the previous complete generation;
  a failure after invalidation leaves a pending marker that no verifier accepts. This is
  an enforced generation boundary for in-process/I/O failure, not a claim of a
  journaled multi-file transaction under sudden filesystem loss.
- Offline response fixtures are descriptor-captured and explicitly plan/receipt-bound as
  `OFFLINE_FIXTURE`, with their path, size, and SHA-256; their response URL is null and
  `network_action_performed` is false. Production Just recipes categorically reject
  offline fixtures and every reserved-option override before Python starts. Live plans
  use `UNIPROT_REST`, null offline provenance, official exact-accession URLs, and still
  record `network_action_performed: false` until apply actually receives responses.
- `verify_fetch_receipt(receipt_path=..., request_plan_path=...)` is a strict, read-only,
  no-network verifier. It independently rederives the plan; rejects pending,
  noncanonical, duplicate-key, type-confused, wrongly addressed, wrong-release, or
  inconsistent acquisition/response receipts; holds plan-matched descriptors for all
  four outputs; validates exact output paths/hashes/sizes/row counts and canonical
  serialization; and proves that references plus blocked rows form the exact target
  partition. Every installed ProteinReference is rebound to its planned accession,
  sequence length/SHA-256, and REST release; blocked candidate metadata and every
  membership/reference release/checksum join are exact. Readdressed impossible response
  counts, Boolean ordinals, and unexpected/requested accession overlap also fail.
- The bounded `resolve-uniprot-review-batch` recipe now requires that receipt, its saved
  request plan, selector manifest, candidate queue, all three normalized fetch outputs,
  exact batch, and release agree before any resolver I/O. It rejects trailing overrides.
  `VerifiedFetchReceipt` passes immutable byte images of the candidate queue, protein
  registry, and membership registry to the resolver, so resolution never reopens those
  paths between its first and final receipt checks. Stable evidence paths come lexically
  from the plan. Queue/registry/membership swap-and-restore and symlink-target attacks
  therefore cannot affect resolved facts. The generic historical resolver remains
  available only through the explicit `--allow-unreceipted-inputs` mode and cannot claim
  receipt provenance.
- A direct production dry replay was byte-identical twice and made no network request or
  write. It emitted 86,494 bytes with SHA-256
  `063f6d25832bfe5bf75bf9a7036608ddb159ae2819f03af679d7aa5ecfbc2ed1`.
  The plan ID is
  `uniprot-registry-fetch-plan:94d79883fe525c176af25d67d0f5ea83e85437ea5bc725590c98bb5fed06b904`;
  it contains 197 exact targets and two requests of 100 and 97. Request and target-row
  SHA-256 values are
  `23bccb895bc49ab5b499455b07e910b879075e18ffcef17751c91f1cc65cf593`
  and `8bc78d683e26acd8925bca8fc08c680d2a293bbe61171996622cca0ae0d51e4a`.
  Queue and selector SHA-256 values remain
  `363187699b9e1c772f3c2543d5f594f3afdd6c21cbd3ae0ca3c4f284c7171e9d`
  and `dc2bb4c1c5e7217a32f6c9b21ef112d2352395af6a3fae3b94a191d70e28b82d`.
- The final focused fetch/resolver/grounding-validator run passed 219 tests in 22.07
  seconds. Ruff lint and format, Python compilation, Just parsing, and whitespace checks
  pass. The fetcher, fetch tests, resolver, resolver tests, validator, validator tests,
  and shared Justfile SHA-256 values are respectively
  `1562a76b75e0d82ae22a5399c7de32b2c57f50961ee18b0d4dac0981b7b7d392`,
  `afb99d6ad7a510b4d8c368ee8a0a3def487075cd2ca9db4862540a49eded0820`,
  `630d70b02c1ee0f53d33cab35f63be274c05b70d94d743c068bd73a836ae2de5`,
  `aff84350bf0c57ae4e9a426fcaa6c60e5eacbea5f80495e3fa2294df43d1eb71`,
  `bc42b23b289f188b7d0b990460c119f15089d5a1330bca0728aabb73824f8a93`,
  `0fa460daa60cbf131edee49fe6cd275c5cb19b5f9446300e4479f57486f7b4ce`,
  and `1d62b4aa6589fe3723ca40fbb4f7d27708643a361a6767258385918b02bdc416`.
  An independent adversarial re-audit reports no remaining High or Medium finding.
- The first clean repository-wide run exposed exactly two compatibility failures in
  `tests/test_uniprot_membership_snapshot.py`: both fixtures still invoked the retired
  unreceipted fetch interface and therefore failed before exercising their intended
  membership assertions. The fixtures now construct canonical selector-v6 manifests,
  derive and save an offline-bound request plan, require the exact 2026_03 release,
  install a completed receipt, and verify that a malformed generation preserves the
  prior protein, membership, blocked, and receipt bytes. The migrated module hashes to
  `08155c3977943088b4f2b23ab50b3a6903b77d944ee075db449788574e9346e5`;
  its focused membership/fetch run passed all 84 tests in 2.23 seconds. A second clean
  repository-wide run then passed all 1,833 tests with zero failures and 25 third-party
  deprecation warnings in 2,180.82 seconds (36:20). This closes the integration gate
  for the Batch-012 request-plan/receipt boundary.
- One response-audit limitation is explicit: raw live HTTP bodies are not retained, so
  the verifier cannot later reconstruct `returned_exact_accessions_sha256` or disprove
  an inflated raw result total beyond its exact type, disjointness, and lower-bound
  checks. This limits third-party replay of response-level claims, but not resolver
  generation integrity: the normalized bytes are captured, receipt-bound, semantically
  validated, and rebound to every planned target. Persist content-addressed raw response
  bodies if independent response replay becomes a requirement.
- The structure-derived evidence namespace gate now recognizes the actual `MCSA`
  spelling as well as the legacy `M-CSA` alias. Both require
  `SIFTS_RESIDUE_MAPPING`; neither can bypass residue mapping through
  `SOURCE_NATIVE_COORDINATES`. The focused validator suite passes all 37 tests, including
  a non-structure ELM control.
- All nine Batch-012 fetch/resolution artifacts are still absent. The actual Just dry
  recipe still cannot reach Python inside this sandbox because `uv` cannot read its
  external cache; the system-Bash executed regression test proves the Bash-3.2 dry branch
  itself, and both fetch-offline and bounded-resolver override probes exit 2 before
  Python. The next operation remains: save the exact dry plan, review it, then run
  `just fetch-uniprot-review-batch ready-local-review-012-s12of14 --request-plan <plan> --apply`
  twice under explicitly permitted network/cache access and compare the normalized
  outputs and completed receipts. No network workaround, apply, report output, trait
  write, durable-grounding write, commit, or pull request occurred here.

### 2026-08-24 — corrected PRINTS/SFLD contracts and ComplexPortal staging

- Adversarial review invalidated the first PRINTS migration replay before any trait or
  grounding write. Its descendant-tree interpretation, 828/198 hierarchy partition,
  1,805-ready count, and all associated row/plan/stdout hashes were scientifically
  wrong and must not be reused. InterProScan's official
  `FingerPRINTSHierarchyDBParser` defines source columns 3--5 as an e-value cutoff,
  minimum motif count, and hierarchical/sibling post-processing relations; `*` is a
  domain flag. They are not subclass descendants. The corrected normalized snapshot
  has 2,106 rows, 97 domain flags, 31 nonzero motif minima, and 1,026 rows/2,546 tokens
  of post-processing relations.
- Snapshot schema v2 preserves those exact fields and validates finite nonnegative
  e-values, relation targets, domain-flag exclusivity, canonical bytes, and disjoint
  materialization paths. API, hierarchy, KDAT, and compressed XML inputs are each
  captured once; parsing, byte count, checksum, and manifest facts all derive from that
  same immutable capture. The installed ignored normalized snapshot and manifest replay
  as `prints-snapshot:05fdb2bd7460d07294708bc6143b2d8ef1fcfdea28cb28d1042fec67715c8b10`;
  their file SHA-256 values are
  `158ea305f3ddd9d07b0007c0f3a9f7dd7b67a689a108caea966333b1ef6acc29`
  and `a5e4200341e0487d7420441a74d4c6d257538102972a1819532dd2a377a43ead`.
- The binary-safe KDAT parser hashes and parses one immutable byte capture, exposes its
  captured size, makes the fingerprint mapping read-only, and binds the release fields
  and mapping identity to private parser provenance. Only the immutable official 42.0
  digest allowlist can produce the canonical status required by record projection;
  public construction, field reparenting, and noncanonical fixtures fail closed. It
  preserves 2,106 fingerprints, 12,444 motifs, and 12,438 explicit
  `KD; INTER_MOTIF_DISTANCE` constraints. Forty-seven constraints carry
  `/R`; the only six motifs without `KD` are PR01474's VCAM11--VCAM16. Source-declared
  KD bounds remain separate from observed `fd` training-row extrema: 57 motifs in 30
  records differ. Malformed, duplicate, wrong-region, and inverted KD rows fail closed.
- The exact checksum-pinned historical seeder bug reproduces all 1,026 current PRINTS
  parents with zero mismatches, including 233 reciprocal two-node cycles. This replay is
  used only to prove generated-state provenance. The corrected relation table emits
  zero subclass parents; every confirmed generated parent is a blocked deletion
  candidate, while any unproven parent is preserved for review. Every final proposed
  YAML hash remains null because this command is plan-only; a separately labelled
  canonical-semantic content hash is not presented as an output-file hash.
- The compact `SequenceFingerprintRepresentation` is now explicitly a pinned KDAT
  motif-summary contract, not a fully replayable InterProScan matcher. The unexecuted
  EMBOSS compatibility reference is named `compatible_derivation_tool_hint`; it does
  not claim that `printsextract` ran or that it matches InterProScan's
  fingerPRINTScan/`prints.pval` execution. PRINTS qualification therefore remains
  closed pending a versioned executable policy and post-processing binding.
- `scripts/migrate_prints_source_model.py` has no apply or writer path. It captures each
  source once before verification/parsing, rejects duplicate YAML keys and semantic
  shadow records (including escaped/UTF-16 forms), rejects YAML-native dates, sets,
  non-string keys, alias cycles, and non-finite values, compares JSON values
  type-strictly, and rehashes every prefilter candidate rather than only records already
  classified as PRINTS. It rejects every symlink below the trait root before scanning,
  does not ask the prefilter to follow symlinks, and validates both lexical and resolved
  containment before opening every reported candidate. Candidate bytes are read through
  component-by-component descriptor-relative `O_NOFOLLOW` opens from one bound trait-root
  descriptor, so a path swapped to an external symlink between validation and open is
  rejected before its bytes are read. The planner fails at startup on platforms lacking
  `O_NOFOLLOW`, `O_DIRECTORY`, or descriptor-relative open support rather than silently
  weakening that contract; the whole-tree symlink/root-binding guards are
  repeated around the drift recheck. This is not an atomic filesystem snapshot: the
  documented execution contract requires a quiescent trait tree because an uncooperative
  concurrent writer can always mutate the candidate set after a final scan. Lexical and
  resolved route containment are also
  checked separately, so symlinked route components cannot masquerade as the expected
  member directory. The
  planner composes content, routing, hierarchy, and path review requirements without
  masking one another. Two complete
  provenance-hardened production replays are byte-identical. They classify 2,103 records
  as exact legacy and three (`PR00706`, `PR00734`, and `PR01066`) as label-review-only;
  989 rows are content-migration-ready, 1,026 have a proven generated-parent repair,
  and 109 have routing review, with overlaps represented explicitly rather than added as
  disjoint totals. The exact summary reports 1,117 review-required rows and no wrong-path
  rows. The canonical row stream SHA-256 is
  `bc6a2ec25c65f1e3dc909baf53859e6416bc499dee60547183f5eceda32eb332`, the plan ID is
  `prints-migration-plan:8b2eb81daf94ab100d85496af644144ff0534071a21455971799beb137508ed6`,
  and two independently generated complete stdout streams both hash to
  `c9aac17fd5f2771b71800b08d8065b744cf2aba74438cc3d352a018777a2d07f`.
  Observed wall times were 41.58 and 54.61 seconds for summary replays and 54.73 and
  44.27 seconds for complete-stream replays; the slower pair overlapped in time. Every
  final proposed YAML hash remains null because this is still a plan, not a serializer.
  An artifact-conditional local production golden test executes the complete planner
  and compares all 2,106 emitted representations field-for-field with the canonical
  KDAT projection; it reproduced the same plan/row/stdout hashes and passed in 43.83
  seconds. This is not a clean-CI acceptance gate: the six pinned production inputs are
  gitignored and the current checks workflow does not download them. A checksum-pinned
  CI source setup or committed production-derived attestation remains required before
  these golden hashes can catch pull-request drift.
- The resolver no longer calls anonymous flattened InterPro locations a fingerprint
  replay. Its `prints_interval_shape_diagnostic` can report only count/length-vector and
  ascending-start compatibility and explicitly records motif identity unverified,
  occurrence grouping unverified, and grounding ineligible. Exact ordered occurrence
  replay remains impossible until matcher output retains motif identities and hit
  grouping.
- `scripts/audit_prints_representations.py` is a separate read-only pre-promotion gate.
  It requires explicit trait, KDAT, and manifest inputs; authenticates the allowlisted
  manifest and canonical parser-sealed KDAT; exhaustively indexes the PRINTS namespace;
  and compares every global, record, motif, training-extrema, and KD field with the
  source projection using type- and key-exact semantics. It re-scans and rehashes all
  inputs before returning one deterministic PASS receipt and has no writer. Its 34
  focused and 79 combined parser/snapshot/auditor tests pass. The production invocation
  correctly exits closed at current `PRINTS:PR00001` because the unapplied corpus has no
  serialized representation; this is the expected pre-migration result, not a pass.
- The generic PRINTS seeder now consumes one manifest-bound immutable capture of API,
  KDAT, normalized hierarchy, and compressed InterPro XML instead of verifying live
  paths and reopening them. Adversarial same-path replacements of each artifact remain
  bound to the approved captured bytes. Boolean hierarchy motif counts are rejected.
  The broader updated PRINTS/grounding/migration/strict suite passes 215 tests, and a
  production dry run verifies all 2,106 signatures against the pinned snapshot.
- `scripts/sfld_match.py` now accepts exactly one canonical HMMER domain-subsequence
  target `parent/start-end`, requires its reported span to equal the ungapped aligned
  domain length, and validates every interleaved Stockholm block as exactly one target
  fragment followed by one equal-length RF fragment. Coordinates are explicitly
  `ONE_BASED_HMMSEARCH_DOMAIN_SUBSEQUENCE`; reported parent bounds are carried with
  `parent_sequence_binding_verified: false` and never promoted to global coordinates.
  Correlated site-tuple matches and potential ancestor projections remain diagnostic:
  every projection says `grounding_eligible: false` with a null threshold decision.
- The missing SFLD execution layer is one content-addressed
  `hmmsearch --cut_ga -A <alignment> --domtblout <domains>` run, not a separate
  full-protein `hmmalign`. One run receipt must bind executable/version, exact argv,
  HMM and FASTA bytes, full main/Stockholm/domtblout outputs, the selected domtbl row,
  model and domain scores, and the full target-sequence registry digest before any
  SFLD membership or ancestor projection can qualify.
- `scripts/stage_complexportal_grounding_candidates.py` is staging-only and uses the
  official ComplexTAB expanded participant list (column 19), retaining column 5 only
  as direct-versus-expanded provenance. Across 28 curated files and 5,295 complexes it
  emits 20,234 candidate memberships for 10,360 proteins (144 isoforms) and 916
  content-addressed blocked rows: 799 processed chains, 115 composites, one internal
  identifier, and one exact ECO code/label mismatch. It covers 5,090 complexes and
  reports 205 uncovered. Unknown `(0)` stoichiometry is null/unknown, never zero copies.
  Candidate and blocked-row SHA-256 values are
  `47acdcc7fa432eeb492d97b0bf6bd861018b38fe6413b7ff07a200f50eeeb269`
  and `2fde2fb8211787804cc22da797f1216b84025739860fa6d47096c90ca0c3e7af`;
  the stage ID is
  `complexportal-grounding-stage:97284f234e1e9ac95e3e4087eef895961b8bf90f267b54d0fbdb4334c524533e`.
  All rows remain `CANDIDATE_PROTEIN` with
  `STAGING_ONLY_MISSING_PROVIDER_RELEASE`; the moving `/current/` files are not a
  qualification receipt.
- After formatter normalization, the earlier integrated PRINTS, SFLD, ComplexPortal,
  seeder, grounding, and strict-validation suite passed 254 tests in 60.68 seconds;
  the newer focused suites above cover the subsequent hardening. A repository-wide run
  reached 1,607 passes and one stale module-cache failure because `prints_snapshot.py`
  changed after pytest collection; the exact failed importability test passes in a fresh
  process. A final clean full-suite rerun remains pending after the concurrent source
  changes settle. Targeted Ruff lint/format and `git diff --check` pass. A safety replay confirms
  that the protected state is unchanged: 126 ProteinReferences and 127 occurrence rows
  retain the checkpointed SHA-256 values, the qualified-binding registry is absent, and
  `git diff --binary -- data/traits` still hashes to
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`.
- No PRINTS, SFLD, or ComplexPortal trait, durable grounding registry,
  qualified-record receipt, or review decision was written. PRINTS migration still
  needs a reviewed routing/parent repair ledger, transactional full-corpus apply
  implementation, and explicit trait-write authorization. SFLD needs the pinned search
  receipt above; ComplexPortal needs a complete release-pinned provider file-list/index
  receipt before either source can enter promotion.

### 2026-08-24 — SCOPe staging and CATH/3did structure-source audit

- The final PRINTS path audit closed the remaining static escape gap. The planner now
  rejects every symlink under the trait root, removes ripgrep symlink following, binds
  one trait-root descriptor, opens every path component with
  `O_DIRECTORY|O_NOFOLLOW`, requires a regular final file, and fails rather than
  weakening this contract on a platform without descriptor-relative no-follow support.
  A deterministic swap-at-open test proves that external bytes are not consumed. The
  documented execution contract still requires a quiescent tree because no userspace
  scan can create an atomic snapshot against an uncooperative concurrent writer.
  Eighteen focused index tests pass; the artifact-backed full golden remained byte-exact
  before the final capability guard. The repository-wide run reported below closes the
  integration gate for this checkpoint.
- `scripts/stage_scope_sq_grounding_candidates.py` is a no-writer, canonical-JSONL
  SCOPe 2.08 stage. It binds the three official source files to SHA-256 values
  `4d68d96829e9c0cdba7b941185eb6debb91dadb3c98e01f9d4d4ca45244382f1`,
  `41aad433fda2d30eb05fb5a4d03692345e0cce39134a8f7cddb2ec140b5c8af8`,
  and `adf535bde5d8284c84d08cca70dfa45c59ea007a27174c66c48a0484d8ea56de`;
  verifies the complete 397,955-node description/hierarchy contract; exhaustively
  indexes all 22,810 modeled SCOP traits across their exact routes; and binds every
  source, trait, and explicit ProteinReference registry through descriptor-relative
  no-follow reads. Registry order is normalized, source pins are mandatory, semantic
  identity shadows anywhere under `data/traits` are rejected, and the quiescent-tree
  limitation is explicit.
- SCOPe `dir.com` is an exclamation-delimited comment table; whitespace around `!` is
  presentation, not marker grammar. The corrected schema-v2 parser splits fields first,
  trims only ASCII space/tab for its semantic field hash, and retains the full physical
  line and artifact hashes separately. This admits both ordinary fields on source line
  301422 (`SQ Q8AVN9 2-73!SQ Q8AVN9 74-128`) instead of inventing a malformed-marker
  false negative. The source contains 6,523 exact `SQ` fields and 68 separate incidental
  prose/annotation `SQ` tokens, which remain
  `NOT_A_PROVIDER_SQ_FIELD` diagnostics. Of the exact fields, 4,656 are admitted (4,654
  unique source occurrences) and 1,867 are blocked. Exact
  `sp -> dm -> fa -> sf -> cf -> cl` propagation yields 23,280 raw and 23,192 unique
  prospective trait/protein/interval projections.
- The final SCOPe partition emits 23,162 candidates: 22,177 lack a local
  ProteinReference and 985 have one. `READY_LOCAL_REFERENCE` means registry availability
  only, never mapping-review readiness. Five source assertions with known local proteins
  are out of bounds and block 25 projections. One SCOPe source assertion assigns human
  prothrombin `P00734` to the cow node `SCOP:50533`; it is isolated as one exact
  source/registry taxon-conflict row covering the five ancestor projections
  `SCOP:48724`, `SCOP:50493`, `SCOP:50494`, `SCOP:50514`, and `SCOP:50531`.
  The 985 availability rows further partition into 713 exact taxon matches, five source
  taxa unavailable, and 267 unresolved mismatches that require a pinned NCBI Taxonomy
  lineage closure. Taxon-pair counts now deduplicate candidate IDs rather than counting
  source-comparison edges; the three production pair counts are 45, 45, and 177 and sum
  exactly to those 267 candidates. In total 1,015 unique prospective projections have
  local registry rows when READY, OOB, and the explicit conflict are counted together.
- SCOPe row-stream hashes are candidates
  `58efeab226f38bde2217822dbbb7be3986194687574d5cc6d8b6fc92bd614ee3`,
  blocked clauses `25cb29062039eed1d472727f588c39223e2241a540f24b22e40f8864a9dc5f4d`,
  OOB `cf78002342422c4c0921c45d27b3e51545264a0d6b3448b0a755bde7fbf8655a`,
  taxon conflict `7efa0db2f2c492f6c4c36bc811f7aac2621b48af953854fef25d973c62b18017`,
  and unmarked diagnostics
  `6b0bcc8add48f9fbd71bd0eba8c175249a18d4b3e4e0dc37ddd893f2fcaa528b`.
  The stage ID is
  `scope-sq-grounding-stage:13bdee92a19239eac754e9238b4afbd7944c81d554013fa3c47e752541aa2132`
  and full canonical stream SHA-256 is
  `9d9b8b492466c833e889c98c3fe1231d7727b47490d0a98cf1732d69859f674d`.
  Every emitted candidate, blocker, conflict, and diagnostic directly binds the comments,
  descriptions, and hierarchy artifacts; `source_node_description` is no longer
  mislabeled as a species description on non-species blockers; and both `.yaml` and
  `.yml` semantic shadows are scanned. Two independent production replays were stable:
  89.168 seconds standalone and 35 tests in 97.97 seconds. This golden is
  artifact-conditional rather than a clean-CI gate
  because the SCOPe sources and review registries are gitignored. No SCOP mapping is
  qualified: source-field semantic review, taxon resolution, sequence/location replay,
  and the plan's structure-evidence requirements remain open.
- The checksum-pinned CATH names source is v4.4.0 dated 2024-12-16, 8,167 lines and
  402,564 bytes, SHA-256
  `9a7b68548a4b755ceda673cfcaba3f19733e1d571f6fafca34e54f62675cdd3a`.
  Its 8,151 exact nodes (5 class, 43 architecture, 1,472 topology, and 6,631
  H-superfamily) match the current CATH trait identity set exactly. Of those traits,
  3,959 have 19,140 current Gene3D/Swiss-Prot examples and 4,192 have none.
- A local annotation-discovery lane is possible but is not native CATH/PDB evidence.
  Exact CATH four-level identifiers in the pinned InterPro 109.0 frame
  (`8d350d73ed5e0525f15885bcff847913d7de208bf58e0155955b47426a382cc0`)
  yield 953 observations for 379 of the 4,192 no-example traits and 415 proteins. All
  proteins have an in-bounds sequence in the UniProt 2026_02 residue frame
  (`35f053876b234b92267c0f18e94bc8f085316f39343aa98668b714c610ba7848`),
  but none has a local profile or ProteinReference. The partition is 813
  single-location observations and 140 flattened multi-location observations; the
  latter additionally remain blocked on lost occurrence grouping. All alternatives
  must be retained. The canonical all/single/multi inventory hashes are
  `859e841a207eba51976c58ed4ff3d9cac9fb6e6c2507042ec040f517e5469103`,
  `81ac1e8ecdecc10ddee5be23010db657c4b697e64397764097dae19d2478165a`,
  and `4fa621f0ac86414f36d4b911aac722d9fd087ea0382ac6c1b9a1403e489a65a0`.
  `scripts/stage_cath_grounding_candidates.py` now emits this discovery lane and the
  native blocker lane as canonical JSONL on stdout only. It has no output-file, writer,
  apply, or qualification path. Its broadened semantic-shadow prefilter parses every
  `.yaml`/`.yml` file containing literal `CATH`, a backslash, or NUL, plus every expected
  route record: 84,508 production candidates rather than only syntactically obvious
  identifiers. Tests cover quoted, flow, block/continued, explicit-complex-key, and
  numeric-anchor identities. Source, frame, trait, route, and candidate-membership
  reads remain descriptor-relative and no-follow, but this is not an atomic filesystem
  snapshot: the stage and its content-addressed summary explicitly require a quiescent
  trait tree. The first broadened artifact-backed suite passed all eight tests in
  529.20 seconds; the final post-hardening production golden passed in 515.96 seconds,
  and an intervening independent summary-only replay took approximately 386 seconds.
  The 953 annotation rows hash to
  `d3ab87f1bcdf8c460b90913a0ee98425125c00e7525765e110956ce273ea5022`,
  the 4,192 native blocker rows to
  `7b459f44c1cdf5b03d6f4fc23ca341233fe531aece9c903e69ce76c17ee46e6a`,
  all 8,151 CATH trait bindings to
  `0393f4b4a505c12698868594965877a119248cffb9266b3a4cf8114f1cd379c8`,
  and the 4,192 no-example trait bindings to
  `2ce522975ace7ded750f6218bc050d40a1cd16510ff19c416a78d3d82c43ac63`.
  The stage ID is
  `cath-grounding-discovery-stage:c121e3fa6ec4e94cf2730d9ddada1316a666ef7189ca432816419c776e5059cd`.
  This remains an artifact-conditional local golden because its raw sources/frames are
  ignored. In particular, the derived InterPro frame does not retain raw provider
  responses or occurrence grouping, so these rows are not independently replayable
  native CATH/PDB evidence. Exact UniProt metadata fetch for the 415 proteins plus a
  raw-response/generator manifest are the next annotation-lane resolver dependencies.
- Native CATH grounding is locally blocked. CATH names provide representative domain
  IDs but not the domain-list classification replay or native/discontinuous boundaries.
  The 209 cached PDBe SIFTS JSON files are coarse, unmanifested segment mappings, not
  residue-level mappings; only 10 of 3,145 representative PDBs for the no-example scope
  intersect them, and no matching accession has a ProteinReference. Before a native
  stage, fetch versioned v4.4.0 `cath-domain-list.txt`, the dedicated CATH domain
  boundary/CDF files and format README, plus manifest-bound residue-level SIFTS XML.
  Never substitute mutable `latest-release`, CDDF metadata alone, or the local segment
  JSON for residue-complete evidence.
- The current 20,638 3did traits replay a legacy parser bug, not the source-native pair
  set. The 71,887,209-byte gzip has SHA-256
  `092d404d77a36971053404bf3c45e5c8aeb7ea6ca0b9d54c26a3d24bfb96d433`;
  its 665,819,102 decompressed bytes hash to
  `1eba61d08a11291ea194ad5922e30ca71614c82ac7c397886c067e43cd69a689`.
  Its gzip metadata names `3did_flat_Mar_3_2025.dat`, but the payload has no internal
  release, checksum, or license header and the provider pages state no explicit license.
  The mutable `/current/` recipe and license therefore remain promotion blockers.
- Exact five-tab-field `#=ID` parsing yields 20,644 true unordered Pfam pairs. The old
  seeder regex-scanned domain names for `PF`-like substrings, leaving exactly 20,591
  source-correct current traits, 53 missing true pairs, and 47 spurious current IDs;
  six later source rows collapsed onto five earlier legacy IDs. Corrected labels and
  paths are unique and collision-free. Corrected/current/missing/spurious pair-set
  SHA-256 values are
  `986a7b567e36381679b7daddfada68b9cb3fdc5a6863d59fc92566b3c2764185`,
  `5e144abb42a94abfae96fa9fe7cf600e0c05761e1d790c934e826ae576c0b2bd`,
  `c947201fe2df34758bb7a2631140494127d8852cda426956ab71922dd7b09a25`,
  and `e05a831d703f9ea0dc51772bd83f90385c9ba3601e73ca3b27c19cee8f126da6`;
  the 53-row source/legacy/corrected map hashes to
  `13ba01b5cff0a0a62c5ca81f290de237ba202dcb2d5e5bb65b7b3a55db7e099e`.
  Keep the current-corpus ECOD+SCOPe+3did queue at 78,407; after an authorized repair
  the source-correct target becomes 78,413.
- `scripts/plan_3did_source_model_repair.py` is the deterministic no-write repair
  planner. It captures the 71.9 MB gzip component-by-component through retained
  descriptor-relative `O_DIRECTORY|O_NOFOLLOW` bindings, copies/decompresses exactly
  once, pins both compressed and 665.8 MB decompressed bytes plus gzip metadata, and
  rechecks the entire source path identity. Deterministic intermediate-directory and
  final-file swap tests prove by inode that external bytes are never consumed; the
  command fails closed where those platform primitives are unavailable. It then audits
  every current 3did trait against exact historical generated YAML bytes and emits only
  canonical JSONL current-index and corrected-proposal rows. There is no writer,
  apply, delete, fetch, or output-file mode.
- The final repair partition is 20,591 exact source-native rows, 42 direct repair
  proposals, five collision-primary proposals, and six collision-suppressed proposals
  across five legacy collision keys. The source block index hashes to
  `f7556c6bf5859bb17d9bd68d6f6bd9ffa1c51a95068a7cde740add3615011690`,
  the exhaustive current-trait byte index to
  `3b7aef732375a21c9eaeeb4974959d9afea79d026343d201299f875f34286062`,
  source repair rows to
  `2e35bc93745fc358dc28943b38a1f57e8a0c531a0e64ca4ca9f04d50193ca04a`,
  collapse provenance to
  `e0b72b8007e8dd1f1e71c1e1d45ae98cc9111aa53b1106081b282e2b84e009a2`,
  and the combined non-summary rows to
  `ecfbca83d54c2669b37a61de448b553ed0d60e10ca9a0dc920aebf68ad02dfed`.
  The plan ID is
  `3did-source-model-repair-plan:9467cbed048ff0e904895b84519095745934758a6d9029230690e409a32d980b`.
  All 23 focused tests pass and the artifact-backed production golden passes in
  119.93 seconds. This is an artifact-conditional local golden, and source-model repair
  review plus explicit trait-write authorization remain prerequisites to full-set
  grounding.
- The 3did source has 1,038,439 exact `#=3D` occurrences, 37,507,421 contact rows,
  139,318 PDBs, and 391,338 block/PDB supports. Local segment-level SIFTS hints overlap
  only 5,685 PDBs and cannot map insertion codes, gaps, or every contact residue; exact
  qualifying mappings are therefore zero. Only 48 source occurrences across 13
  source-correct traits have both sides hinted to the durable 2026_02 registry, over PDBs
  `1nlm`, `1oiz`, `2f2h`, `5ujj`, and `8bvx`. Those five are a download-prioritization
  tranche only. A later stage must replay both participant domains and every ordered
  contact endpoint through release-manifested residue-level SIFTS, verify PDB and
  UniProt residues, and route interchain homo/heteromer cases to participant-model
  review. Generic Pfam/InterPro co-membership is never 3did interface evidence.
- No SCOPe, CATH, or 3did trait, durable grounding row, qualified receipt, or review
  decision was written. The new work consists only of read-only inventories, no-writer
  staging/planning source, tests, and this execution log. Every future trait migration,
  promoter action, network fetch, commit, or pull request remains behind its existing
  explicit authorization gate. The post-suite safety replay retained the 126/127
  durable registry/evidence line counts and their checkpoint hashes above, found no
  additional durable grounding files, and retained the pre-existing `data/traits`
  binary-diff SHA-256
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`.
- The final repository-wide integration run after the SCOPe schema-v2 correction, CATH
  hardening, and 3did repair planner completed with 1,727 tests passed in 2,223.57
  seconds (37:03). Its 25 warnings are third-party deprecations from `sssom_schema`,
  pandas, and `funowl`; there were no test failures. The separate focused integration
  run completed with 64 tests passed and three expensive production goldens deselected,
  and Ruff check/format plus `git diff --check` were clean.

### 2026-08-24 — BioLiP missing-protein staging and the residue-level SIFTS boundary

- The local BioLiP nonredundant table is 49,699,998 bytes and 86,458 physical rows,
  SHA-256
  `4688b8c3c3acf68a6e3816780cc0ddbba8d2ba6aaa40a41daba741b099d33099`.
  The accompanying 21-column README hashes to
  `120b22b3e26cf0d0ce7edfde122925963cdd81e6e5a8f4165d16f3238406c161`.
  All physical rows have exactly 21 fields. Exact-byte aggregation produces 86,375
  unique rows and retains all line numbers for the 83 duplicate extras; it never uses
  the legacy weak `(PDB, receptor chain, ligand)` key.
- The source has 6,020 distinct ligand classes and the current corpus has the same 6,020
  exact BioLiP trait identities. Of these, 445 traits lack `canonical_examples`. They
  bind 643 physical source rows represented by 641 unique exact rows, including two
  exact duplicate extras. Every one of the 641 unique rows has a missing BioLiP column
  18 UniProt field, so the stage makes **zero protein-identity, UniProt-coordinate, or
  qualification claims**.
- Pairwise all-or-nothing validation of BioLiP columns 8, 9, and 21 admits 638 unique
  source rows covering 443 traits and 480 PDB structures. Three complete rows are
  blocked rather than partially repaired: source line 71,437 for
  `proteintraitsmech:BIOLIP_GG2`, line 80,885 for
  `proteintraitsmech:BIOLIP_A1AT9`, and line 81,564 for
  `proteintraitsmech:BIOLIP_ESC`. `BIOLIP_GG2` has another ready occurrence, which is
  why the 443 ready-trait and three blocked-trait sets overlap across 445 total traits.
  Negative author residue numbers and insertion codes are retained verbatim and kept
  distinct from one-based BioLiP receptor-sequence positions.
- `scripts/stage_biolip_missing_protein_candidates.py` is the deterministic stdout-only
  stage. It emits 641 source-occurrence rows, 480 deduplicated official-SIFTS fetch
  requests, and one summary: 1,122 canonical JSONL rows total. It exposes no write,
  output-file, fetch, network, apply, protein-ID, or qualification path. The 480 requests
  target the official PDBe remediated residue-level SIFTS XML namespace documented by
  [PDBe SIFTS Quick Access](https://www.ebi.ac.uk/pdbe/docs/sifts/quick.html):
  `https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml_remediated/{pdb}.xml.gz`.
  A future fetch must be complete, canonical, and content-addressed; merely creating a
  partial cache cannot unlock any candidate.
- The final content partitions are occurrence rows
  `d23d161fd7dfe61e43a63bb1e081d00c327e86f20b6be4d7aca49c186fc47325`,
  fetch requests
  `f135281921caa6b974d71026aedb78263ea948a2c2d6058dacd208332f989726`,
  and combined non-summary rows
  `fcc804932d40efba7c2585307a9c10c1ee07d09d6d8430dfa22f80a38e61da2e`.
  All-trait and no-example trait bindings hash to
  `0671a0a53d026bae51be05d81e4501f091f80d27581c8b3f057a12b084dca856`
  and `bcb586ace9ee5803e4774579ac36e6e83b626a48ff4ec95bf9e79c04472bc097`.
  The stage ID is
  `biolip-missing-protein-stage:f9fc94db49a9c066fba504596d88dc2f2ffeba46841e8f1359031eccd2b311dc`,
  and the rendered 1,122-row stream hashes to
  `3cb24236f59e0c72b88a00583a1d7fd8c6001763d0e7ac36777e21fd963271fb`.
- Trait/source binding is exact rather than merely prefix-shaped. The stage verifies
  deterministic seeded filenames, source-derived identities, exact route membership,
  current trait bytes, and exact xref lists. The status partition is 6,019
  `EXACT_SEEDER_SOURCE_XREFS` and one
  `EXPLICIT_CURRENT_POLYMER_DNA_COLLISION_XREF_EXCEPTION`: the existing polymer-DNA
  record carries both `CHEBI:16991` and the historical `pdb.ligand:DNA` collision xref,
  while the distinct CCD-DNA trait exists separately. That one exact ordered list is
  visible in the stage but is not normalized or silently generalized; changing the
  order, adding another xref, or placing a non-BioLiP identity in the exact route fails
  closed. Repairing the current DNA trait remains a trait-write and review action
  requiring explicit authorization.
- The local `data/raw/align_cache/biolip_sifts.json` hashes to
  `66f9f6f88d5fca735672424c22d034abf2dbbdd271d9e64048cbe644d64ed6c4`.
  It contains 8,236 REST-cache keys, 8,159 nonempty entries, 77 null entries, and 31,255
  segment mappings; 21,642 segments lack at least one author endpoint. None of 63,141
  inspected mapping objects contains a per-residue collection, and the 445-trait target
  scope has zero exact chain/accession hints. The stage therefore names this cache as
  excluded input and a malicious-cache regression proves output invariance. Diagnostic
  affine interpolation is also unsafe: among complete-looking rows, 1,371 have identity
  below 1, 203 of 6,403 have unequal spans, 330 of 5,732 local-sequence rows mismatch or
  fall out of bounds, and 642 lack the needed residue frame.
- Existing derived overlays remain discovery-only. The current sequence/structure
  equivalence TSV has 7,018 BioLiP edges across 2,093 classes, but none is bound to
  BioLiP/SIFTS residue-level provenance. The older BioLiP causal-graph builder's weak
  key collapses 28,564 rows across 14,201 ambiguous groups and can partially discard
  invalid residues. Neither artifact may be promoted into evidence; the new stage uses
  neither.
- Filesystem and source contracts are fail-closed: exact checksum pins, exhaustive
  semantic-shadow parsing, unique YAML keys, descriptor-relative `O_NOFOLLOW` reads,
  complete-tree symlink rejection, content and membership rechecks, deterministic
  duplicate aggregation, and an explicit quiescent-tree limitation. Tests include
  descriptor symlink swaps, required-platform capability, arbitrary/reordered xrefs,
  the exact DNA exception, malformed residues, weak-key peers, malicious cache content,
  and the artifact-backed production golden. The final focused run passed all 18 tests
  in 69.86 seconds; Ruff check/format, `git diff --check`, and an independent final audit
  found no High or Medium issue.
- BioLiP still lacks a provider release receipt and has academic-use terms without an
  explicit open license. These remain independent promotion blockers alongside the
  missing remediated SIFTS manifest, release-pinned ProteinReferences, residue replay,
  and scientific review. No network fetch was performed and no trait, durable grounding
  row, qualification receipt, review decision, commit, or pull request was written.
  The safety replay retained 126/127 durable registry/evidence lines and their SHA-256
  values from the checkpoint, found no additional durable grounding data files, and
  retained the pre-existing `data/traits` binary-diff SHA-256
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`.
- The final repository-wide integration run, including every local artifact-backed
  production golden, completed with 1,745 tests passed and zero failures in 2,174.30
  seconds (36:14). Its 25 warnings are the same third-party `sssom_schema`, pandas, and
  `funowl` deprecations recorded at the prior checkpoint. The combined fast SCOPe,
  CATH, 3did, and BioLiP source-stage suite separately passed 81 tests with four
  production goldens deselected in 3.52 seconds.

### 2026-08-24 — ELM source-native candidate staging and receipt boundary

- The exact local ELM class and instance exports are 88,298 bytes and 944,144 bytes,
  with SHA-256 values
  `70b52085abf7c11ccac30feb7a81eb88c405cd029e99d6f8be95c2f613edf9d8` and
  `272e2de87817cabdb236984419c5be7e82dc6fd3b85ecab34b655db48022c7c3`.
  Both identify export format 1.4 and origin `asimov`; their timestamps are
  `2026-07-03 14:22:05.578160` and `2026-07-03 16:15:11.938794`. They do not
  declare a formal database release, checksum, license, source sequence, taxon ID, or
  provider acquisition receipt. The stage therefore binds the bytes as
  `elm-source-snapshot:986d677b81851ceeb339b02e9c00a8541323365ca2d1bb2046a3491e8565aadd`
  but does not treat that content address as a provider receipt.
- The source has 353 classes: 11 CLV, 33 DEG, 42 DOC, 199 LIG, 40 MOD, and 28
  TRG. All 353 exact trait identities, deterministic paths, routes, labels,
  whitespace-normalized source definitions, regular expressions, license fields, and
  historical first-15 projections replay. The instance export has 4,277 rows: 4,047
  true positive, 73 false positive, 33 true negative, and 124 unknown. True positives
  cover 2,605 exact `Primary_Acc` protein identities, including 96 isoform rows;
  `Primary_Acc`, including its isoform suffix, remains authoritative even when the
  alias field omits it.
- The historical cap selected 2,774 examples and omitted 1,273 true-positive rows.
  Of the selected examples, 2,742 carry inline sequence; those collapse to 1,965
  unique proteins without conflicting sequence bytes, while 32 examples lack an inline
  sequence. Legacy ELM examples remain non-qualifying and must have exactly the
  historical seeder shape; unexpected or grounding-shaped fields fail closed.
- `scripts/stage_elm_source_native_grounding.py` is a deterministic stdout-only stage.
  It retains all 4,277 source rows, preserves non-positive source logic, and emits 2,599
  deduplicated missing-ProteinReference requests carrying the expected UniProt release
  `2026_02`. It has no writer, output-file, fetch, network, apply, promotion, or
  GroundingEvidence mode. Every ProteinReference row must be valid canonical JSON and
  name release `2026_02`; a mixed or wrong release aborts the stage.
- The local 126-row ProteinReference registry intersects six ELM true-positive proteins
  and nine source occurrences. All nine have exact in-bounds source spans, full-protein
  regex matches, matching registry taxon labels, and no inline/reference conflict.
  They are emitted only as `ELM_LOCAL_REGISTRY_SEQUENCE_MATCH` candidates. The resolved
  interval string and digest are explicitly labeled
  `LOCAL_PROTEIN_REFERENCE_NOT_ELM_EXPORT`, and the candidate shape deliberately omits
  occurrence-evidence `intervals`, `expected_sequence`, `sequence_sha256`, and
  `source_release` fields. The stage emits **zero GroundingEvidence rows** and claims no
  qualification.
- Two independent receipt blockers apply to each of the nine local matches:
  `MISSING_ELM_PROVIDER_ACQUISITION_RECEIPT` and
  `MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT`. The registry is reported honestly
  as `LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING`, not as a
  provider-verified registry. The central validator unconditionally reports
  `elm_provider_receipt_required` for ELM evidence, so copying a candidate into a
  `QUALIFIED` example cannot bypass the missing provenance.
- ELM patterns are evaluated at the one-based closed source interval against the full
  protein. This preserves biological `^` and `$` semantics while an endpoint-constrained
  lookahead permits valid greedy and alternation backtracking to the exact annotated
  end. Adversarial controls cover a C-terminal anchor in the middle of a protein, an
  N-terminal anchor away from residue one, greedy endpoint backtracking, and alternation.
  The inferred one-based closed coordinate convention remains explicit because the TSV
  exports do not declare it.
- The canonical occurrence, request, and combined non-summary row hashes are
  `ab49eb78d5a5d320619f1cdd745a68a0fe22951314d34a401685fa0f7920a9cb`,
  `c7f1282dac56d6af8616a167933e2b38c6d5169f147fc843012de4127572a869`, and
  `a330a9c651321c632080025eaebed97631b73c10d9e6204fb8f3f6b45cb932f8`.
  The stage ID is
  `elm-source-native-stage:7c518e862c108773f83d0ab1bf8aa70ace75b51c0a43658eacf06d937f90ab0d`.
  Two independent complete 6,877-row stdout replays both hashed to
  `5f3491644cacc100804bb0c7b75ba2fdbdbd98b5e31d6bce5ff1e7ed9f430835`.
- The integrated ELM stage, central validator, UniProt fetcher, and grounding resolver
  suite passed all 235 tests in 61.85 seconds. Ruff check/format, compilation, and
  `git diff --check` were clean. The stage uses descriptor-relative no-follow reads,
  content rechecks, semantic-shadow parsing, and sampled membership rechecks, but it is
  explicitly not an atomic snapshot against an uncooperative filesystem writer; any
  future promotion-capable implementation requires a mutation lock or retained
  descriptor-relative tree capture.
- Final adversarial review found and closed two qualification-boundary bypasses before
  this checkpoint was accepted. First, an evidence object could label its provider
  source `ELM` while using non-ELM trait IDs and avoid the namespace-only receipt gate;
  ELM rules now trigger from either exact source identity or namespace and require an
  exact `ELM:ELME######` source trait. Second, quoted or escaped YAML qualification keys
  could miss a raw-text regular-expression prefilter. The migration-safe prefilter is
  now conservative, every possible qualification-bearing document is parsed before
  registry, hierarchy, membership, or validation decisions, parsed objects are reused,
  and recursively discovered lowercase `.yaml` and `.yml` files are both covered.
  Direct plain, quoted, `\u005f`-escaped, anchor/merge, and reverse-source tests pass.
  The independent post-fix re-audit found no remaining High or Medium issue.
- A future ELM receipt verifier must bind the exact source pair paths, sizes, hashes,
  content-addressed pair ID, physical instance-line digest, ELMI identity, ELM class,
  exact primary accession, and coordinates, plus a provider acquisition record. It must
  also bind the local ProteinReference registry to a verified UniProt fetch and
  membership receipt. A Boolean receipt flag or an arbitrary `elm-source-snapshot:*`
  string must never unlock qualification. No network request, trait write, durable
  grounding write, promotion, review decision, commit, or pull request occurred in this
  phase.
- The final repository-wide suite after both boundary repairs passed all 1,849 tests
  with zero failures in 2,650.88 seconds (44:10). Its 25 warnings are the existing
  third-party `sssom_schema`, pandas, and `funowl` deprecations; none came from the ELM
  stage or validator changes.

### 2026-08-25 — DisProt source-native candidate staging and receipt boundary

- The local `data/raw/disprot.entries.json` export is 28,164,899 bytes with SHA-256
  `aeb8773ae59b2f569203c13a6515d3c2b1374168bd921f63daf4c2a0543e8844`.
  The repository declares the source URL as
  `https://disprot.org/api/search?release=current&format=json` and registers CC-BY-4.0,
  but the captured bytes themselves have no global provider release, declared license,
  or acquisition receipt. The stage binds them as
  `disprot-source-snapshot:254ad2ada4746010e4971ebe7745b8ae180ca982a0ae730567bacb002804bcfb`
  without treating that content address as a provider receipt. Per-entry and per-region
  `released` values remain source metadata and are never promoted to `source_release`.
- The source array contains 3,199 unique entries and 13,396 unique `region_id` rows:
  9,387 IDPO and 4,009 GO. The IDPO rows cover 3,198 proteins, 32 exact terms, all three
  source namespaces, and 4,689 trait/protein pairs. All entry sequences are present and
  length-exact, and every IDPO interval is in bounds. The one-based closed coordinate
  convention is explicitly an inference from source replay and the historical seeder,
  not a provider declaration.
- `regions_counter` is not physical-array cardinality or a completeness receipt. It
  exceeds the array length in 946 entries by 3,815 total. Duplicate coordinates are
  also scientifically distinct: 1,067 `(protein, term, start, end)` groups contain
  1,735 extra regions. `scripts/stage_disprot_source_native_grounding.py` therefore
  retains one source-order row per IDPO `region_id`, including every citation, ECO
  assertion, `validated`/`unpublished` value, experimental-context field, and raw
  cross-reference. It never parses irregular PDB cross-reference text into a
  `structure_id`.
- The current 32 IDPO term records and three namespace-parent records replay exactly.
  The historical seeder aggregates source-order features per `(term, protein)`, sorts
  proteins by `(-feature_count, accession)`, and caps each term at 30. This reproduces
  500 examples, 384 unique selected proteins, 1,401 selected feature rows, and 4,189
  omitted trait/protein pairs. All 35 validated trait paths and byte hashes are now
  content-bound; the combined binding-row SHA-256 is
  `4894fa7c480a49718b760c9691e4d099ca913e12ba31599dd5dc9105034e962b`.
  Sparse source `term_def` fields and the two `term_not_annotate` rows are preserved but
  cannot alter trait identities or definitions because no authoritative local IDPO
  ontology snapshot is available.
- The pinned `data/raw/align_cache/residue_frame.json` has SHA-256
  `35f053876b234b92267c0f18e94bc8f085316f39343aa98668b714c610ba7848`,
  release `2026_02`, 113,592 sequences, and 10,238 declared-absent accessions. Among
  IDPO region rows, 7,677 source sequences match the frame exactly, 1,699 are not in the
  frame (nine rows explicitly absent and 1,690 unlisted), and 11 disagree. Frame absence
  or mismatch dominates even when a local reference exists.
- Seven DisProt proteins have exact source/frame/local-ProteinReference sequence and
  taxon agreement, covering 61 regions. Those rows emit only nested
  `DISPROT_LOCAL_REGISTRY_SEQUENCE_MATCH` candidates with exact
  `trait_id == source_trait_id == IDPO:#######`, `SOURCE_NATIVE_COORDINATES`, localized
  scope, the inferred source interval, and an interval string/digest. Candidate objects
  deliberately omit GroundingEvidence-shaped `intervals`, `source_release`, provider
  fields, and a bare full-protein `sequence_sha256`; `source_evidence_id` is null and
  qualification is `CANDIDATE_ONLY`. The remaining exact-frame rows include 7,616
  missing-reference occurrences. All 3,191 IDPO proteins absent from the registry get
  one sorted, content-addressed ProteinReference request for release `2026_02`, including
  frame-absent and frame-mismatch proteins; the stage emits zero GroundingEvidence.
- Structured experimental context is present on 1,857 IDPO rows; construct alterations
  and/or opaque construct-sequence text occur on 787, `uniprot_changed` is true on 108,
  and `term_not_annotate` is true on two. These fields are preserved and add explicit
  review blockers. `validated` and heterogeneous `unpublished` source fields are not
  interpreted as acceptance semantics. Citation counts are 9,364 PMID, 20 MobiDB, and
  three DOI rows; all 112 ECO ID/name identities are stable.
- The stage is descriptor-safe and fail-closed: duplicate JSON/YAML keys, non-finite
  JSON, source/term/ECO identity drift, coordinate errors, release/hash mismatches,
  semantic IDPO shadows, uppercase YAML suffixes, escaped identifiers, merge constructs,
  symlinks, registry contradictions, and concurrent candidate mutation are covered.
  It builds the complete result before stdout and has no output path, network, fetch,
  apply, promotion, or writer mode. The Just recipe uses
  `uv run --frozen --offline --no-sync` so environment bootstrap cannot add network or
  synchronization side effects.
- Provider qualification remains categorically closed. Every local candidate carries
  `MISSING_DISPROT_PROVIDER_ACQUISITION_RECEIPT` and
  `MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT`, along with the mutable-release,
  completeness, coordinate, and missing-IDPO-snapshot blockers. The central validator
  triggers from either exact `evidence_source: DisProt` or the IDPO namespace, requires
  exact IDPO trait/source equality, `SOURCE_NATIVE_COORDINATES`, localized scope,
  `provider_kind: SOURCE_DATABASE`, and equal provider/source release, then
  unconditionally reports `disprot_provider_receipt_required`.
- Canonical occurrence, ProteinReference-request, and combined non-summary row hashes
  are `23fa981b0237976bd051a3686f1c08a5adb6416bfb4ddff5c3d18f6e59bff5ab`,
  `669eb58514fa6fa8a5986fa902d13b8e5fffcddba9dff7d6243fae1561e98b97`,
  and `3aaa94feb5f757f525ba0bda32dd12388643f7a63400b1da4cc55d82619282ea`.
  The summary row hashes to
  `1ee6d608a105b157d8146cffa2ba60241a3718744554f36dd1c9292e6c2691e8`,
  and the stage ID is
  `disprot-source-native-stage:ae6b733744487ea1aa7c3f63569aaaa95d607f9b47204aa219124340aed372e1`.
  Two complete 12,579-row stdout replays were byte-identical at
  `378a843980f6f3288e8270a85f4b5111e4a8c9977db18b71adfc18fe5ffcd095`.
- The settled stage/validator integration run passed all 73 tests in 51.18 seconds;
  Ruff lint/format, Python compilation, Just execution, and `git diff --check` passed.
  Independent adversarial review found and closed two Medium provenance races before
  acceptance: the first version omitted the three namespace-parent artifact hashes from
  the stage identity, and initially irrelevant semantic-prefilter files were not
  end-rechecked. Dedicated regressions now prove that parent-byte changes alter the
  stage and that an irrelevant file mutating into an IDPO shadow fails on digest drift.
  The final audit found no remaining High or Medium issue.
- Final source/test/validator/validator-test/Justfile SHA-256 values are
  `35137d52ae87acbbf9b67ac7a81b178518c2b019af93c22fcc01835c895a500c`,
  `f74860c5001ddaf159ed2f817e834e8d24e8be43f7fc3739e6607c3b7f919e0b`,
  `6edff75a60cd304b23af37bb9a3bafa3c67469aede80e2b5a406db817d430e24`,
  `9cf6b3fc3063a344c58e2a3af1ef7b2c78ec565d8e8e0462972e96b8a0e0bd96`,
  and `eb50ca2943ba3610d15fcafd3fc53672fb92b4d17ef5803f9f4fbc718fe14450`.
  The repository-wide integration run then passed all 1,878 tests with zero failures
  in 2,522.91 seconds (42:02). Its 25 warnings are the same third-party
  `sssom_schema`, pandas, and `funowl` deprecations recorded at earlier checkpoints;
  none came from the DisProt stage or validator gate.
- No network request, trait write, durable grounding write, evidence row, qualification,
  review decision, commit, or pull request occurred. Protected registries remain at
  126/127 lines and their recorded SHA-256 values; the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`.
  All nine Batch-012 fetch/resolution outputs remain absent. A future DisProt receipt
  verifier must bind the exact source URL, bytes, provider release, acquisition time,
  response headers/body, region identity/payload digest, authoritative IDPO snapshot,
  and a verified UniProt ProteinReference receipt before any candidate can qualify.

### 2026-08-25 — ComplexPortal v3 source-native staging and receipt boundary

- This checkpoint explicitly supersedes the historical ComplexPortal v2 row and stage
  hashes in the 2026-08-24 log; that earlier log remains as execution history and must
  not be used as the current golden. The v3 stage admits exactly 28 numeric curated
  ComplexTAB files plus the required-but-categorically-excluded
  `9606_predicted.tsv`. Every curated filename and SHA-256 is pinned in
  `scripts/stage_complexportal_grounding_candidates.py`. The curated bytes came from
  the repository's mutable ComplexPortal `/current/complextab` fetch recipe without
  response metadata, release identity, or provider file index, so their content address
  `complexportal-source-snapshot:a2bed4f99a9cd86074213668597e0eceffef228df8f757c24f00db4e32542541`
  is explicitly a local snapshot, never a provider receipt or release.
- The 28 curated files contain 5,295 disjoint complex rows. Column 19, the expanded
  participant list, is the sole membership assertion; column 5 remains only
  direct-versus-expanded provenance. The 21,150 expanded tokens partition into 20,235
  UniProt-shaped accessions, 799 processed chains, 115 composites, and one internal
  identifier. One exact ECO code/label mismatch blocks the otherwise UniProt-shaped
  CPX-12/P84022 row. The resulting scientific projection is therefore unchanged at
  20,234 candidates, 916 blocked rows, 5,090 covered complexes, and 205 uncovered
  complexes. It contains 10,360 unique proteins and 144 isoform memberships across 94
  unique isoform identities. Unknown `(0)` stoichiometry remains null/unknown rather
  than zero copies.
- The exact local release-`2026_02` ProteinReference registry is parsed as strict,
  canonical JSONL and content-bound at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`.
  It intersects 24 candidate memberships across 19 proteins. The other 20,210
  memberships cover 10,341 unique proteins and produce exactly one sorted,
  content-addressed request per full `UniProtKB:` identity; a dedicated regression
  proves that a protein occurring in multiple complexes aggregates its candidate,
  trait, taxon, and source-artifact bindings without duplicate requests. The stage does
  not claim that this registry has a verified fetch receipt.
- Complex taxonomy and protein organism are intentionally separate facts. Each source
  row still requires column 4 to equal its numeric filename taxon, but a component
  ProteinReference taxon is never required to equal the complex taxon because host-virus
  complexes legitimately cross that boundary. The stage emits an explicitly
  informational comparison. The current 24 local-reference memberships happen to be
  identical and the remaining 20,210 have no local reference; this observed equality is
  not promoted into an acceptance invariant.
- The trait boundary is exhaustive and source-derived. All 20,579 exact
  `ComplexPortal:` records must occupy one flat, regular, lowercase-`.yaml` route and
  their sorted path/hash binding rows hash to
  `1db5b4990d5422d6a9d73a07d1e03441567e1d4457e9d22208f686220bd0e5ef`.
  For all 5,295 curated source complexes, the historical seeder's filename and complete
  YAML bytes replay with no exception; those binding rows hash to
  `656c395cb232d63604e6d762c08703568d6ea1c72e7d48f3543089baa2b3a062`.
  The other 15,284 records are predicted-source traits and cannot generate candidates,
  but their paths and hashes still affect the stage identity. This closes the prior
  risk that label, definition, parent, direct-list relation, xref, extra qualification
  field, rename, or outside-snapshot trait drift could be invisible.
- Source, trait, and registry reads are descriptor-relative and require
  `O_NOFOLLOW`, `O_DIRECTORY`, and `dir_fd` support. The stage rejects symlinks, duplicate
  YAML/JSON keys, non-JSON YAML values, escaped/case-varied semantic shadows, non-flat
  route entries, noncanonical CR/blank/missing-terminal-LF source rows, source/checksum
  drift, registry release/identity contradictions, and candidate membership drift.
  Physical provider-entry digests bind the raw UTF-8 line excluding its canonical LF
  terminator and state that basis explicitly. Every conservative prefilter artifact is
  end-rehashed, and retained trait/root descriptors are identity-checked around the
  final scan. The documented execution contract still requires a quiescent trait tree:
  userspace enumeration is not an atomic filesystem snapshot against an uncooperative
  concurrent writer.
- Receipt requirements are separate rather than collapsed. Every candidate carries
  `MISSING_COMPLEXPORTAL_PROVIDER_ACQUISITION_RECEIPT`,
  `MISSING_COMPLEXPORTAL_RELEASE_PINNED_FILE_LIST_RECEIPT`, and
  `MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT`; missing local references add their
  own blocker. The central validator triggers from exact `evidence_source: ComplexPortal`
  or either trait/source namespace, including reverse-source attempts. It requires
  exact `trait_id == source_trait_id == ComplexPortal:CPX-<positive decimal integer>`,
  `SOURCE_MEMBERSHIP`, `SOURCE_DATABASE`, `WHOLE_PROTEIN`, exact source name, and equal
  provider/source releases, then unconditionally reports
  `complexportal_provider_receipt_required`. An arbitrary local snapshot string cannot
  unlock qualification.
- The stage builds the complete result before stdout and has no network, fetch, output
  path, apply, promotion, or GroundingEvidence writer mode. Its Just recipe is exactly
  `uv run --frozen --offline --no-sync`. Every candidate and blocker says
  `grounding_evidence_emitted: false`; the summary evidence count is zero. Candidate,
  blocked, request, and combined non-summary row SHA-256 values are
  `adae937c316379ae88d9e6445afcbfed81f5d051646e507b4e822bc676e89c62`,
  `2e4e65dab51d843028e6bdf4aa0896e6d6b49ad5f6005209c2be630f42906669`,
  `8228f6f22b2552041f25a2c95e374084c2b2614f3c2664c67ff80c0e70e628b0`,
  and `3132f42a7518706f43518025b613a7e0ad59db10344be70bf2c4d527c3583d36`.
  The summary row hashes to
  `e6446834bc2485e2bf56c62802c93133758aeb968b888b4490776a7a0748fce0`,
  and the stage ID is
  `complexportal-grounding-stage:d8d543ce0da5925d978b2a6129745e76053d8dd535a177f6b46f47542328e936`.
  Two independent complete 31,492-line stdout replays were byte-identical at
  `ebf9e64258ef0ce5e8350792e997410f8e1d510c39bddcd10bff2e5aa027ac4f`.
- The artifact-backed production golden and adversarial fixtures cover the exact default
  inventory, source-row projection, trait replay, semantic shadows, descriptor swaps,
  registry partition, multi-membership request aggregation, every row content address,
  zero-evidence closure, parser/Just safety, and a before/after fixture-tree no-write
  proof. The settled stage-plus-central-validator integration run passed 102 tests in
  79.69 seconds before the final aggregation regression; all 31 nonproduction stage
  tests then passed in 0.86 seconds. Two independent final audits found no remaining
  High or Medium implementation defect. The production golden is artifact-conditional
  because the exact source inputs are gitignored; a checksum-pinned CI setup remains
  necessary for clean-CI drift coverage.
- Final stage/test/validator/validator-test/Justfile SHA-256 values are
  `19c3608737a9ddd744d222c5ec446e3efcb699108b5e48d4a4ba71aa99e48940`,
  `5fd324e081ed5da57f0681bc99185e0bb7c08a215458fa12c9898a00f132b81e`,
  `aedf340a0d40bdf1aa929017ab50927f8439cca3fcbf4825546bd05c56150a8f`,
  `0c9eb2a62dd3dbbd4abe1f6f7080e475eb1c7d440a70f3159796caa4feeb3a77`,
  and `82ec2a47fb9f5ff1089e185f46199091652706f6c56129c81585889496b42e77`.
  The repository-wide suite completed 1,915 tests successfully and exposed one unrelated
  history-scaffolder collision: two identical invocations inside one second reused a
  filename. The default ID now retains microseconds, and the scaffolder prefers the
  active environment's `linkml-validate` over an unnecessary `uv` cache lookup; three
  focused collision replays passed. Final repository integration is rerun after the
  SCOPe checkpoint below so both changes share one conclusive gate.
- No network request, trait write, durable grounding write, evidence row, qualification,
  review decision, commit, or pull request occurred. ComplexPortal cannot qualify until
  a future receipt verifier binds an authentic provider release, the complete
  release-pinned file list/index, acquisition metadata and bytes, and a verified
  UniProt-registry fetch receipt. Promotion would additionally require review and
  separate explicit write authorization.

### 2026-08-25 — SCOPe v3 protected-registry requests and SIFTS receipt boundary

- This checkpoint supersedes the SCOPe schema-v2 row and stage hashes in the 2026-08-24
  execution log for the current default command. The earlier 17-registry replay remains
  useful historical evidence, but it mixed the protected durable registry with 16
  ignored review-batch registries. SCOPe v3 deliberately accepts exactly one
  checksum-pinned registry. The default is the protected 126-row UniProt `2026_02`
  registry at
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`;
  its checksum proves local content identity, not a verified fetch receipt.
- The source model remains the exact SCOPe 2.08 three-file snapshot: comments
  `4d68d96829e9c0cdba7b941185eb6debb91dadb3c98e01f9d4d4ca45244382f1`,
  descriptions
  `41aad433fda2d30eb05fb5a4d03692345e0cce39134a8f7cddb2ec140b5c8af8`,
  and hierarchy
  `adf535bde5d8284c84d08cca70dfa45c59ea007a27174c66c48a0484d8ea56de`.
  The release/date headers are source facts, while the content address
  `scope-source-snapshot:feb7ab9116aaf530653f8b0e7354e0f5ab5265a2395a2c750b64a1cbd461d2b0`
  is explicitly a local snapshot without an acquisition receipt. Every one of the
  22,810 modeled SCOP trait records contributes its exact route and byte digest to the
  trait-binding hash
  `cf063a943352cf8010e2840805e36686dd10e81d2d073d6f58ca34ec1809d80c`.
- The protected-registry projection retains all 4,656 admitted clauses, 4,654 unique
  source occurrences, 1,867 blocked clauses, 68 unmarked diagnostics, and 23,192 unique
  trait/protein/interval candidates. Only 15 candidates across three proteins and 14
  traits have an exact protected local ProteinReference; ten are exact taxon matches and
  five retain the unresolved `NCBITaxon:562 -> NCBITaxon:83333` lineage review. The
  other 23,177 candidates cover 3,585 proteins and 7,601 traits. They now produce exactly
  3,585 sorted, content-addressed ProteinReference requests, one per full UniProt
  identity, aggregating every candidate, target/direct-source trait, source node,
  interval, line/segment digest, source taxon, and all three source artifacts.
- Every present or missing candidate and every missing-protein request binds the exact
  registry path, SHA-256, size, expected release, and explicit
  `NOT_VERIFIED_BY_THIS_STAGE` receipt status. An adversarial two-registry regression
  proves that two valid pinned registries which both omit the same protein now produce
  different missing-candidate and request identities. The semantic-shadow scanner uses
  case-insensitive YAML suffix discovery and SCOP/SCOPe prefiltering, then requires the
  exact canonical `SCOP:` namespace and lowercase `.yaml` suffix. Uppercase `.YAML`,
  mixed-case `sCoP:`, and `SCOPe:` alias shadows all fail closed.
- All candidate, blocker, diagnostic, and request rows state
  `grounding_evidence_emitted: false`, `network_action_performed: false`, and
  `write_action_performed: false`. Global blockers are
  `MISSING_SCOPE_PROVIDER_ACQUISITION_RECEIPT`,
  `MISSING_VERIFIED_PROTEIN_REGISTRY_FETCH_RECEIPT`,
  `MISSING_EXACT_SCOP_PX_PDB_CHAIN_BINDING`,
  `MISSING_RELEASE_MANIFESTED_RESIDUE_LEVEL_SIFTS_REPLAY`, and
  `DIRECT_SCOP_COMMENT_MAPPING_REVIEW_REQUIRED`; missing references add their own exact
  blocker. The source-native coordinates remain candidate/source facts only and are
  never emitted as GroundingEvidence.
- The central validator now locks whenever `evidence_source` is exactly `SCOPe` or
  either trait/source identity uses the `SCOP` or `SCOPe` namespace, including reverse
  source attempts. It requires exact source `SCOPe`, source release `2.08`, independently
  canonical `SCOP:<positive decimal>` target and source identities,
  `SIFTS_RESIDUE_MAPPING`, provider kind `SIFTS`, `LOCALIZED` scope, and
  `UNIPROT_CANONICAL` coordinates. It intentionally does not require target and source
  trait equality: direct domain occurrences may propagate through a verified inclusive
  `dm -> fa -> sf -> cf -> cl` inheritance path. It also does not equate the SIFTS
  provider release with SCOPe 2.08. Existing generic structure checks still require an
  exact structure and chain, `COMPLETE` mapping, and equal positive source/mapped residue
  counts; the lock then unconditionally emits `scope_provider_receipt_required`.
- Final v3 row-family SHA-256 values are candidates
  `11551cecefc190770f72ef1c6d08fb7d28588e21ac18ff15f044e7c5c540cdca`,
  blocked clauses
  `5b17b6c144e58e0af55c7e0173407231ade952dfc4c9833201c14655a70e80a7`,
  empty OOB and taxon-conflict families
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`,
  diagnostics
  `e737b18f13d4dc37128eb7130b0e1be65d014be6c9ac25e9187c937bc1ddfd5c`,
  and requests
  `fa57769b5619658f20187ed904e3b389bdce0a98d9926b30140fe8dc5eb6f418`.
  The combined non-summary hash is
  `b4ae4dcb1d76135ed66e229ccb78e1f6f328e1c29e434148c6a3c3ae59a470c5`,
  the summary hash is
  `67a660da88aad7d79acf2f9fe7be13988691c197e07e349fcbde4d877913f898`,
  and the stage ID is
  `scope-sq-grounding-stage:8c22574f759f23481934e3b1d432cdc072597bcab633b108c0b81bc29a92fcfb`.
  Two independent complete 28,713-line replays agreed at
  `358123ed156919cbcfa4a3c3c6779e0484b896ff2e3cb4ff67b1c17022d78efb`.
- All 39 SCOPe stage tests passed in 99.88 seconds. The final combined
  artifact-backed stage and central-validator suite passed 133 tests in 109.37 seconds;
  an independent audit replay passed the same 133 tests in 109.79 seconds. Two
  independent post-fix audits found no remaining High or Medium defect. The exact Just
  recipe is `uv run --frozen --offline --no-sync`; the command has no fetch, output,
  apply, promote, writer, or GroundingEvidence mode. Final stage/test/validator/
  validator-test/Justfile/history-scaffolder SHA-256 values are
  `9bc72c8d64c70aadb6553aa5b87100083c0082150e946b1fb40173a83a97d600`,
  `7fe487d35e935fc4aff7e8f3d91593a930bcdf8b6d951a57660a8e77bd9a7e6f`,
  `a8ee4bc11b47e0485c4312d845ced33ad9f654f607cbfbddb8e0264cb15597f5`,
  `55d896b01ea9803e11613d4523cb524df01e7523e8d343b91f33c9821c8ad66c`,
  `28c2f2a4b749a7ca5f587f1427db380359104c631f0d64e19ad6d96b7c4f6b4e`,
  and `9dddaaf897bdf9e060f7ae8c6a78b400abe018c8ffcfaa8a7cbec622ca73f183`.
  The final repository-wide integration gate passed all 1,943 tests with zero
  failures in 2,305.94 seconds (38:25). Its 25 warnings are the same third-party
  `sssom_schema`, pandas, and `funowl` deprecations recorded at earlier checkpoints;
  none came from the SCOPe stage, central receipt lock, or history-scaffolder repair.
- No network request, trait write, durable grounding write, evidence row, qualification,
  review decision, commit, or pull request occurred. The protected registries remain at
  126/127 rows with their checkpoint hashes, the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  and all nine Batch-012 fetch/resolution outputs remain absent. SCOPe qualification
  remains closed until authentic provider acquisition, verified UniProt registry,
  exact px/PDB-chain selection, release-manifested residue-level SIFTS, sequence/taxon
  review, and authoritative hierarchy receipts are represented and verified.

### 2026-08-25 — CATH v2 protected-registry requests and dual-lane receipt boundary

- This checkpoint supersedes the CATH schema-v1 annotation, native-blocker, and stage
  hashes in the 2026-08-24 log. The source envelope is unchanged: CATH names v4.4.0
  hashes to
  `9a7b68548a4b755ceda673cfcaba3f19733e1d571f6fafca34e54f62675cdd3a`,
  the derived InterPro 109.0 frame to
  `8d350d73ed5e0525f15885bcff847913d7de208bf58e0155955b47426a382cc0`,
  and the UniProt `2026_02` residue frame to
  `35f053876b234b92267c0f18e94bc8f085316f39343aa98668b714c610ba7848`.
  Their content address
  `cath-local-source-snapshot:3728064f9a055ee03aaf7754b3cee5bdff09c02fa1cab630c7556566f5f2d252`
  explicitly describes local pinned bytes and derived frames without CATH/InterPro
  acquisition receipts or InterPro/UniProt frame-generation receipts; it is not a
  provider receipt.
- CATH v2 binds exactly one protected ProteinReference registry: the 126-row,
  121,024-byte UniProt `2026_02` file at
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`.
  It parses canonical LF-terminated JSONL with exact fields, accessions, sequence
  lengths/checksums/versions, release, duplicate-key/identity, path, no-follow, and
  drift checks. None of the 415 exact CATH/Gene3D proteins is present. All 953 direct
  H-superfamily observations therefore have status `MISSING_LOCAL_PROTEIN_REFERENCE`
  and produce 415 sorted, content-addressed ProteinReference requests. Each request
  binds the exact absence-establishing registry plus every source discovery ID, trait,
  interval, InterPro observation digest, trait record, CATH names row, and source/frame
  artifact. Of the requests, 175 aggregate more than one observation and the maximum is
  15. A two-observation fixture and two distinct pinned registries that both omit the
  same proteins prove aggregation and absence-binding identity.
- The direct annotation partition remains exactly 813 single-location and 140 flattened
  multi-location observations across 379 H-superfamilies. The latter retain the
  independent `INTERPRO_LOCATIONS_ARE_FLATTENED_WITHOUT_FRAGMENT_GROUPING` blocker.
  All annotation rows separately require CATH and InterPro acquisition receipts,
  InterPro and UniProt frame-generation receipts, and a verified ProteinReference
  fetch receipt; missing references add their own blocker. Their fields are deliberately
  named `discovery_mapping_method`, `discovery_coordinate_frame`, and
  `residue_frame_sequence_*`, so a row is not shaped like copyable GroundingEvidence.
  All 4,192 no-example traits still receive a separate native blocker requiring CATH
  domain boundaries and release-manifested residue-level SIFTS; native rows do not
  falsely claim the InterPro-frame dependencies of the annotation lane.
- This v2 phase is intentionally the direct exact-match lane recorded above, not the
  complete ancestor-expansion phase. Propagating these 953 proven source observations
  through explicit CATH paths would yield 3,812 source-distinct rows, including 2,859
  ancestor rows and 3,204 unique target/protein pairs, across 5 classes, 27
  architectures, 205 topologies, and 379 H-superfamilies. Expanding all 62,357 exact
  CATH/Gene3D frame observations against no-example ancestors would instead yield
  188,024 source-distinct rows over 35,071 proteins, 34,966 of them absent from the
  protected registry. That is a separately bounded future phase; v2 does not imply that
  ancestor grounding is complete.
- The central validator now closes both CATH scientific lanes. An InterPro lane requires
  exact `INTERPRO_MATCH`, source/provider `InterPro`/`INTERPRO`, releases exactly
  `109.0`, `LOCALIZED`, canonical UniProt coordinates, a canonical one-to-four-level
  target, and an exact four-level H-superfamily source identity. A shorter target is
  allowed only through the existing authoritative record-level inheritance path. A
  native lane requires `SIFTS_RESIDUE_MAPPING`, source `CATH`, source release exactly
  `v4.4.0`, provider `SIFTS`, localized canonical coordinates, canonical CATH identities,
  a structure and chain, complete mapping, and equal positive residue counts; the SIFTS
  provider release remains an independent axis. Either lane unconditionally reports
  `cath_provider_receipt_required`. Exact source/namespace reverse triggers prevent
  hand-copied evidence from bypassing the lock.
- Filesystem and output claims remain fail-closed. The semantic-shadow scan recognizes
  case-varied CATH spellings and YAML suffixes but requires exact `CATH:` and lowercase
  `.yaml`; it passes `--no-config` to ripgrep so `RIPGREP_CONFIG_PATH` cannot inject an
  exclusion. A hostile `--max-filesize=1` config regression proves that an outside-route
  shadow is still rejected. The command emits canonical JSONL to stdout only, exposes no
  fetch/output/apply/promote/write option, and the exact Just recipe is
  `uv run --frozen --offline --no-sync`. Every candidate, blocker, and request says zero
  evidence, network, and write actions; the summary reports the same zero counts.
- Final v2 annotation, native-blocker, request, and combined non-summary row SHA-256
  values are
  `2353d5b87145ead27efde2a53ac4fec9ba65fbc3ccd9fa89097ad8a42772ad22`,
  `e0621a95c7a41252166c38fe58151d6c80c56e55aa64b70f66bbef4dc2194893`,
  `057cc96e77c3f552560e0834e2c9f0bb249be1a6db252d801d22edfa84c19dee`,
  and `933a27907206e4dd4006c11824a2a32ef8c2e33f8abf72d0deb52e803c0665ca`.
  The unchanged all/scope trait-binding hashes are
  `0393f4b4a505c12698868594965877a119248cffb9266b3a4cf8114f1cd379c8`
  and `2ce522975ace7ded750f6218bc050d40a1cd16510ff19c416a78d3d82c43ac63`.
  The summary row hashes to
  `e984a7a08797feffd80515fd9e27f45043ec2a65d3dbd20479b883729dbe508b`,
  the stage ID is
  `cath-grounding-discovery-stage:992c025a015c871d78c181bc11f6049d2887f53f3d843b5aa352b8da3d004fdf`,
  and the complete 5,561-row stream hashes to
  `2bf8ed6204f0216a43794616840c9d131869bde20a517df54fe690528e49c062`.
  Two independent complete builds agreed on every summary value after the final
  hardening; the artifact-backed stage module then passed all 18 tests in 517.08 seconds.
  The full validator module passed 138 tests in 2.93 seconds, and the final fast combined
  stage/validator gate passed 155 tests with the production golden deselected in 3.90
  seconds. Ruff lint/format and `git diff --check` are clean, and independent adversarial
  review reports no remaining High or Medium issue.
- Final stage/test/validator/validator-test/Justfile SHA-256 values are
  `a9a56b6bfc2eea4be32208707dd3153636300fd169116abb0edbd1fb0dc089e2`,
  `74b5e5732b1d9f5e39795434b6449caacbe091f4150b6da07d7fedd2415fa2e8`,
  `3f5b0f5502c3ef47df6a8d7e3b510a94eb39b425a1220ae04a3ac642b7156dd8`,
  `78f2859e086ba5e3b81c4e4277fa602904770153d1e29c47ebcb78579b0a793c`,
  and `eae67bf66e95281c8161ac0ef3108d804275bf31b66e5295b757c85a6a07679d`.
  The later repository-wide integration gate recorded in the PRINTS checkpoint below
  passed all 2,204 tests and closes this checkpoint's pending suite requirement.
- No network request, trait write, durable grounding write, evidence row, qualification,
  review decision, commit, or pull request occurred. The protected registries retain
  their 126/127 rows and checkpoint hashes, the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  and all nine Batch-012 fetch/resolution outputs remain absent. Annotation qualification
  remains closed until the raw InterPro responses and generator receipt, CATH provider
  receipt, verified ProteinReference receipt, occurrence grouping, and review exist;
  native qualification additionally requires the versioned CATH domain/boundary
  release and residue-complete SIFTS replay described above.

### 2026-08-25 — consolidated provider-receipt boundary and protected staging paths

- A read-only adversarial replay showed that otherwise well-shaped evidence from
  pending source providers could cross the generic semantic boundary without an
  acquisition receipt. The central validator now has one exact, table-driven lock for
  each pending provider: `prints_provider_receipt_required`,
  `sfld_provider_receipt_required`, `ecod_provider_receipt_required`,
  `threedid_provider_receipt_required`, `biolip_provider_receipt_required`,
  `mcsa_provider_receipt_required`, `metalpdb_provider_receipt_required`, and
  `repeatsdb_provider_receipt_required`. Each lock is triggered once by an exact
  evidence source, exact trait/source-trait namespace, or the exact repository-local
  3did, BioLiP, or MetalPDB identifier pattern. `MCSA`/`M-CSA` and
  `3did`/`ThreeDID` aliases are explicit; near misses remain unmatched.
- Existing source-specific ELM, DisProt, ComplexPortal, SCOPe, and CATH contracts and
  finding codes remain authoritative and suppress generic duplicate findings. An
  otherwise unmatched `SIFTS_RESIDUE_MAPPING` or `SIFTS` provider now reports
  `sifts_provider_receipt_required`; any other unmatched `SOURCE_DATABASE` provider
  reports `source_database_contract_required`. Exact ordinary PROSITE, Pfam, HAMAP,
  Gene3D, and other InterPro evidence, plus UniProt feature and membership evidence,
  remains clean. The protected 127-row evidence registry is entirely `INTERPRO` and
  replays with zero findings.
- Every repository call site that constructs GroundingEvidence now immediately invokes
  the central validator. This closed a reachable non-SIFTS resolver bypass: the current
  candidate ledger contains 9,556 CATH InterPro candidates, and a direct four-level
  CATH row had previously been marked `QUALIFIED` during resolution even though its
  emitted evidence independently reported `cath_provider_receipt_required`. CATH,
  PRINTS, and SFLD InterPro candidates now become `REJECTED`, retain their exact stable
  blocker codes, emit no embedded occurrence/evidence projection, and contribute no
  staging ProteinReference or GroundingEvidence row. Ordinary Pfam InterPro and UniProt
  membership controls still qualify.
- ECOD residue-level staging remains useful without pretending to qualify. The builder
  accepts exactly the ordered singleton `ecod_provider_receipt_required` and treats any
  absent, different, duplicate, or additional semantic finding as
  `GROUNDING_EVIDENCE_INVALID`; it can therefore retain the content-addressed mapping
  and evidence candidate without weakening the shared validator. The top candidate is
  `CANDIDATE_PROTEIN`, and its embedded occurrence is now `LOCATION_VERIFIED`, not
  `QUALIFIED`. The resolver reconstructs a prospective `QUALIFIED` occurrence only
  internally, converts the receipt finding to
  `invalid:sifts_grounding_evidence:ecod_provider_receipt_required`, withholds both
  projections, writes empty staging protein/evidence ledgers for that rejected row,
  and preserves exact SIFTS provider replay for review diagnostics. Promotion retains
  its independent SIFTS and central-semantic denials.
- The adversarial audit also found that caller-selected staging paths could bypass the
  promoter by targeting `data/traits` or `data/grounding`, including by using
  case-varied physical aliases on this case-insensitive APFS volume. All four ECOD
  builder outputs and all four resolver outputs now reject canonical trait storage,
  the selected trait root, canonical durable grounding storage, input aliases, and
  mutual output aliases before I/O. Promotion's four durable outputs use the same
  physical checks against trait roots and staging inputs. Containment combines lexical
  resolution with nearest-existing-ancestor `samefile` identity; output identity uses
  ancestor device/inode plus a case-folded, NFC-normalized unresolved tail. Direct,
  symlink, existing-input-alias, APFS case-alias, prospective case-only collision, and
  prospective NFC/NFD collision regressions prove the no-write boundary. All APFS
  existing-input-alias tests executed on this machine rather than skipping.
- The final focused validator, ECOD builder, resolver/promoter, and audit gate passed
  all 442 tests in 19.48 seconds. Ruff lint and format checks are clean across all eight
  affected production/test files. Independent final adversarial review reports no
  remaining High, Medium, or Low finding in this phase. Final validator/test,
  ECOD-builder/test, resolver/test, audit/test, and Justfile SHA-256 pairs are
  `f360f09d89d53ddc8430cac6d0da766ac5ccedd4909f2659fa67bb8c06345df1` /
  `8bcd02551c51dddc97dcde98a4267f7b071946d41540a9c6be7369fd18d70976`,
  `5142b1efc31f94d0cfe6e0b0f3f4af2d30a8cdf197c1d85c4b75adbb2d21d0a4` /
  `6ef94dc02ff79bcd9b1564d482a1a1c00176b2d0244bdd95e26d0c1902f4a6f1`,
  `8f17c6ca599287134be43de1b6e78ce5d57b849f5b9a3b1ddf9f69b0761cf993` /
  `77946ef887ed4e54f1b2946c3ade29ef8a14aa965c74f7e8f450624bc5ed4ae2`,
  `fc9e45ca70a2daa9e2c420ea6398666c8e88c6558ab969d528567c700fb9e2a3` /
  `0aaaa7d3c0ea3b02a299cb62e1cea4935cb21497e83b7839bab17fefd0c0dbf2`,
  and `eae67bf66e95281c8161ac0ef3108d804275bf31b66e5295b757c85a6a07679d`.
  The later repository-wide integration gate recorded in the PRINTS checkpoint below
  passed all 2,204 tests and closes this checkpoint and the preceding CATH v2 suite
  requirement.
- No network request, trait write, durable grounding write, evidence qualification,
  review decision, commit, or pull request occurred. No no-write probe file exists in
  either protected root. The ProteinReference and evidence registries remain exactly
  126 and 127 rows with SHA-256 values
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  and all nine Batch-012 fetch/resolution outputs remain absent.

### 2026-08-25 — Batch-001 staging compatibility and PRINTS semantic-review boundary

- The first repository-wide run after the CATH/provider-receipt phase found one exact
  compatibility regression and no other failure: 2,157 tests passed and
  `test_real_batch001_dry_run_when_ignored_fixture_is_available` expected the historical
  Batch-001 dry run to reach its 120-clean/7-blocked content partition, but the bootstrap
  loader stopped earlier on the newly unconditional SFLD provider lock. The durable
  evidence registry remains 127 rows and validates with zero semantic findings. The
  checksum-pinned historical staging ledger has 2,065 unique evidence rows: 1,710 are
  current-clean and 355 have exactly one
  `sfld_provider_receipt_required` finding. None of those 355 identities occurs in the
  durable registry.
- `scripts/bootstrap_uniprot_record_bindings.py` now admits that historical staging
  state through one narrow compatibility envelope only: the exact singleton SFLD
  receipt finding, on a staging-only evidence identity, after the production caller has
  authenticated the exact historical artifact hash and row count. Durable evidence has
  no exception; an approved/durable identity, malformed row, duplicate identity,
  digest mismatch, different finding, or additional finding remains fatal. The real
  no-write Batch-001 replay is again 120 clean and seven blocked. Its focused module
  passes all 19 tests. Final script/test SHA-256 values are
  `c6d5922db5b8b79a5fe98c1043a474598b3bc5f9b0b9c8830a65af9d541e95a2`
  and `bff16aba61039676665e8f9d162e8a3fab215562f6db33f1e59d6f5b3a2ab07b`.
- The PRINTS migration planner is now schema v3 and remains canonical-JSONL,
  stdout-only, and apply-incapable. Every row binds the exact normalized hierarchy row
  and hash, its `domain_flag`, the member type's domain interpretation, and an explicit
  `AGREES`/`DISAGREES` alignment. REVIEW_ONLY rows expose exact current, legacy, and
  proposed value projections rather than only mismatch names. The production plan has
  2,106 rows, 1,117 review-required rows, 989 content-ready rows, 1,026 hierarchy
  repairs, and 109 routing reviews. All-record hierarchy/member alignment is
  2,087/19; the routing-review partition is exactly 102/7. The seven routing conflicts
  are `PRINTS:PR00163`, `PRINTS:PR00205`, `PRINTS:PR00379`, `PRINTS:PR00929`,
  `PRINTS:PR01021`, `PRINTS:PR01452`, and `PRINTS:PR01542`.
- Planner discovery now invokes ripgrep with `--no-config`, recognizes case-varied
  `.yaml`/`.yml` candidates, and rejects noncanonical suffixes and namespace spellings.
  Manifest, API, KDAT, normalized hierarchy, InterPro XML, and legacy hierarchy inputs
  are bounded, regular-file, component-no-follow, stable descriptor captures. An
  independent adversarial replay then proved one verifier-to-consumer race in the first
  private-copy design: mutating the captured API after manifest verification changed
  route counts and rows while retaining the old snapshot ID. The final implementation
  consumes `load_verified_prints_snapshot`'s immutable manifest-bound API/hierarchy/XML
  captures and parser-sealed KDAT object; both InterPro consumers receive the same
  captured gzip bytes. Dedicated post-verification API, hierarchy, and XML path-mutation
  regressions pass. The production output is unchanged: normalized hierarchy projection
  SHA-256
  `fa21deb29c23f39f01acd8f85fd4319ef40af7700a5e221d6fd80b4b6343d665`,
  rows SHA-256
  `b36ad35933fa3408fb6cc4c0eacf26eef1bafafe7140da259a889365a4d66d49`,
  plan ID
  `prints-migration-plan:fcce6d6d5ecb5443ca1eb659e35bfce5a424a9e621662b15b5a3febc9b8e6fbf`,
  and full stdout SHA-256
  `011a373efd2e2d901b42ca02c15e0114ad778a625cf7a577bc993f91bc470308`.
  Final planner/test SHA-256 values are
  `419731731f9767f586efb96976f5e60b89e9275d2919d34abcd03adb056b1b33`
  and `fea88639f741cde63880d9726f83ea7d3fe3a239b379d580d99a7bd2a1936781`.
- The separate PRINTS review compiler is schema v2 and also stdout-only. It requires the
  complete schema-v3 plan context and emits exactly three decision dimensions:
  three `RECORD_REVIEW`, 109 `ROUTING_REVIEW`, and 1,026 `HIERARCHY_REPAIR`
  decisions, covering the 1,117-row union in 1,138 decisions. Structurally valid BLOCK
  or REQUEST_REPLAN decisions produce `VALID_NON_ACCEPTING`, exit 3, no review-set ID,
  and no next-phase acceptance. Positive decisions are proposal-compatible only when
  their exact bound source and hierarchy projections agree; in particular, a
  KEEP_PRINTS_MEMBER_ROUTE decision cannot accept any of the seven domain conflicts.
  A fully compatible ledger can emit `ACCEPTED_SEMANTIC_PLAN_ONLY`, but still declares
  `apply_authorized:false`, `serialization_status:NOT_PERFORMED`, and zero writes. The
  ledger reader is bounded, regular-file/no-follow, stable-capture, duplicate-key
  rejecting, canonical JSON, and exact-LF framed; CR/CRLF and Unicode line separators
  fail closed. The production template rows SHA-256 is
  `bd3a3cecf949f4cebc028e8a81ea3abe53f0e4cbba054ee346ae7d7782d0afb4`
  and its ID is
  `prints-migration-review-template:e473d5f1b613fc97b63b077f3a3b963df6170db5152d93cbb813873e2068f262`.
  Final compiler/test SHA-256 values are
  `79cacb16a47cc6b2e715048eff39e9c7f6bef81c47d91b90493198d98d5f8396`
  and `c9db1ce1721acc83eb16953977355ea64380242d5ce17859450a824b881162db`.
- The final combined bootstrap/planner/review gate passed all 97 tests in 262.27
  seconds. Ruff lint/format and whitespace checks pass across all six files. The one
  stable repository-wide integration run then passed all 2,204 tests with zero failures
  and 25 unchanged third-party deprecation warnings in 2,700.14 seconds (45:00). This
  closes the pending repository-wide gates for CATH v2 and the consolidated provider
  receipt phase.
- No reviewed PRINTS decision ledger was invented or materialized: the emitted template
  is not a human review. No serializer exists, no migration/apply authorization was
  inferred, and the seven routing disagreements still require explicit replan decisions
  or a future expanded routing proposal. No network request, trait write, durable
  grounding write, qualification, review decision, commit, or pull request occurred.
  No protected-root no-write probe exists. The protected registries remain exactly
  126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  and all nine Batch-012 fetch/resolution outputs remain absent.

### 2026-08-25 — 3did source-model repair review boundary

- `scripts/review_3did_source_model_repair.py` now supplies the missing no-write review
  boundary for the existing schema-v1 3did repair plan. It freshly replays the pinned
  71,887,209-byte March-2025 gzip and the exact legacy trait tree; authenticates the
  planner plan ID and every current/source row hash plus the combined row digests; and
  cross-binds every corrected proposal to the exact spurious current trait byte index.
  It never consumes a saved plan as authority and therefore cannot validate stale plan
  rows against a newer source or trait snapshot.
- The production template is the exact atomic repair partition: 53
  `ADD_CORRECTED_TRAIT` decisions and 47 `REMOVE_SPURIOUS_LEGACY_TRAIT` decisions. The
  additions retain the planner's 42 direct, five collision-primary, and six
  collision-suppressed classifications. Every removal binds all dependent source-record
  IDs, so the five legacy collision keys and six collapsed extra source records remain
  explicit rather than being silently treated as one-to-one replacements. All 100
  decisions must be the proposal-compatible actions before the ledger can be accepted.
- A structurally valid BLOCK, KEEP_LEGACY_TRAIT, or REQUEST_SOURCE_MODEL_REPLAN action
  produces `VALID_NON_ACCEPTING`, exit 3, no review-set ID, and no next-phase
  acceptance. A complete compatible ledger can produce only
  `ACCEPTED_SEMANTIC_PLAN_ONLY`: every receipt still declares
  `apply_authorized:false`, `serialization_status:NOT_PERFORMED`, zero writes, and the
  unchanged 3did repair/review/authorization/residue-level-SIFTS grounding gate. This
  compiler has no output-file, writer, serializer, apply, delete, fetch, grounding, or
  promotion mode.
- Completed ledgers are bounded to 32 MiB and captured as stable regular files through
  component-relative no-follow descriptors. The parser requires canonical JSON with
  unique keys, finite JSON values, exact LF termination, no blank rows, and no CR/CRLF
  or Unicode line aliases. It rejects symlink and FIFO inputs, path replacement during
  capture, altered/reordered/duplicate bindings, stale summaries, incomplete or invalid
  reviewer metadata, and any mismatch between the captured ledger bytes and their
  supplied decision objects. The receipt content-addresses both immutable template
  bindings and all reviewer/action/timestamp/comment decisions.
- The exact production template has 100 rows and is 353,474 bytes. Binding SHA-256 is
  `de54f7f8aac865f29a4396a444d6945e634845054e7287e5cf523d0fcf8a0975`,
  template-row SHA-256 is
  `4236d7f40c1d9d42705799f78576320ea3c8c2802332255487b9ab72286eb1ad`,
  complete stream SHA-256 is
  `848a8882f5b16bd4c69a708512a5e607d557d590b9d7afa9d0a488e4d51a05e1`,
  and the template ID is
  `3did-source-model-repair-review-template:c6d60b4ad9c84155b711cb9a81f8d57aab697c51c51e30173caf442b990f808f`.
  The full review module passed all 19 tests, including the pinned production golden,
  in 157.93 seconds; the planner/review fast gate passed 41 tests with the two production
  goldens deselected. Ruff lint/format and whitespace checks pass, and the repository
  writer audit remains clean across 197 scripts. Final review compiler/test SHA-256
  values are
  `642c265d849972c5f8ce23e85b32efdfbd006cf35cc2e20726f0d06aca07d1d9`
  and `08b5a49d7ad2f48de0ba1163826fb66f1c6927f572808186aa3f9192f6aebbc4`.
  The final repository-wide integration gate passed all 2,223 tests with zero failures
  and 25 unchanged third-party deprecation warnings in 3,595.70 seconds (59:55).
- No completed 3did review ledger was created and no decision was inferred from the
  blank template. No serializer, network request, trait write, durable grounding write,
  qualification, commit, or pull request occurred. The protected registries remain
  exactly 126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  and all nine Batch-012 fetch/resolution outputs remain absent.

### 2026-08-25 — SFLD source-model migration preflight

- `scripts/sfld_release.py` now has one canonical
  `build_sfld_profile_representation` projection shared by migration and future
  execution work. It serializes the exact HMM record hash, GA sequence/domain
  thresholds, HMM metadata, source-wide artifact hashes, ordered model-coordinate
  SITE rows, and whole correlated FEATURE tuples. It is explicitly a source fact,
  not a protein match. A strict-validator regression proves that the projection is
  schema-valid, while an accession without an executable model fails closed.
- `scripts/plan_sfld_source_model_migration.py` is a schema-v1, canonical-JSONL,
  stdout-only planner with no serializer, output-file, apply, grounding, or promotion
  option. It authenticates bounded regular-file/no-follow captures of the HMM,
  hierarchy, sites, installed canonical manifest, and the already pinned InterPro XML.
  All three SFLD parsers consume immutable temporary copies of the verified bytes, so
  replacing a source path after capture cannot change the plan under the old manifest.
  Trait discovery is namespace-semantic rather than route-trusting: a repository-wide
  ripgrep prefilter admits escaped/UTF candidates, every admitted YAML rejects duplicate
  keys and non-JSON values, all path components are no-follow, and candidate bytes and
  the complete candidate set are rechecked before return. The quiescence limitation is
  stated in every summary rather than overstating this as an atomic filesystem snapshot.
- Production replay gives the exact closed partition. All 299 executable SFLD 4 models
  have one current record and there are no source-only models. The only current-only
  records are the four allowlisted InterPro signatures without a release model:
  `SFLD:SFLDF00030`, `SFLD:SFLDF00034`, `SFLD:SFLDF00109`, and
  `SFLD:SFLDG01106`; an arbitrary fifth exception is fatal. All 299 executable rows
  lack the source-profile serialization, all 266 applicable current parent edges match
  the source hierarchy, all 303 files occupy the legacy whole-protein function route,
  298 labels exactly equal the HMM description, and one differs only by whitespace.
  Definition provenance is exactly 140 generated signature restatements, 159 integrating
  InterPro Family abstracts, and four integrating InterPro Domain abstracts. The four
  Domain cases remain explicit granularity-review rows rather than being accepted as
  family definitions.
- Every one of the 303 rows requires semantic routing and definition review. The 299
  executable rows additionally expose the full source-native profile projection for
  review; the four model-less rows require an explicit disposition and carry no invented
  profile. The summary therefore reports 303 review-required, zero content-ready,
  `serialization_status:NOT_PERFORMED`, `writer_available:false`,
  `apply_authorized:false`, and `grounding_eligible:false`. It also preserves the
  independent requirement for a content-addressed `hmmsearch --cut_ga` execution receipt
  before any membership can qualify.
- Two independent production CLI runs were byte-identical: 304 JSONL lines,
  1,609,428 bytes, row-stream SHA-256
  `ca0ec92ab934e1715ff389a842d5c3fb5fbc9359f981513b557aee1d273c7dee`,
  full stdout SHA-256
  `b38be21eb1566da741157bd7e2f14706cab11c980af357eeed39a8652a6af84b`,
  and plan ID
  `sfld-source-model-migration-plan:d7511e342fcaacf49c11041ef10b21fd54006fe94bde3e36f2a1f6628801ef61`.
  The source-model projection SHA-256 is
  `256cd8b2d7480af586bdf0ad73cbaa26f4b33cc3340bbbd0f0a884dcc20914ac`,
  and the exact current trait binding SHA-256 is
  `b3064d9df6510ad24567973c42b170dd8e6f59fc194c5b05f092889b4fb8007d`.
- The focused parser/planner modules pass all 32 tests. The broader writer/strict/seeder/
  SFLD-match/parser/planner gate passes all 138 tests in 27.02 seconds; Ruff lint and
  format checks and `git diff --check` are clean. The repository writer audit remains
  clean across 198 scripts. Final planner/test and release-helper/test SHA-256 pairs are
  `df1b4344ab4de11c5d0f21d581227932a82ad8fb02386d42cdaf86315cf6a7a4` /
  `20be9d68bb7fd979074c0ebb1c0c702956873ddc86008aa51afccbc0c63ee29f`
  and `06cda9aad186fcb5f5c4da5a2916099c3882bab4e5e3f0d8e4620a1a0f38800f` /
  `c0800fd230c90d77481f5a6ee49cea81537d33cc28db98554fc22019ead8391c`.
- No SFLD review ledger or decision was invented, and no trait gained a profile
  representation. No network request, trait write, durable grounding write,
  qualification, commit, or pull request occurred. The protected registries remain
  exactly 126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  all 303 legacy SFLD records remain byte-bound and unmodified, and all nine Batch-012
  fetch/resolution outputs remain absent. The semantic-review and repository-wide gates
  that close this preflight are recorded in the checkpoint immediately below.

### 2026-08-25 — SFLD semantic-review boundary

- `scripts/review_sfld_source_model_migration.py` freshly replays the complete
  authenticated SFLD plan and never accepts a saved plan as authority. It validates the
  planner plan ID, all 303 row hashes, the row stream, definition/profile projections,
  exact 299/4 executable/model-less partition, closed writer/grounding state, and every
  planner review requirement. A future unhandled requirement fails closed instead of
  disappearing from the review template.
- The blank production template contains 909 independent decisions: 303
  `SEMANTIC_ROUTING`, 303 `LABEL_AND_DEFINITION`, 299
  `SOURCE_PROFILE_REPRESENTATION`, and four `MODELLESS_DISPOSITION` rows. Routing offers
  only explicit current-schema targets: the legacy functional-protein-family route,
  functional enzymatic activity, sequence domain, sequence family, or sequence
  homologous superfamily. Reviewers can keep the exact bound current label/definition,
  approve the exact source-profile projection, and retain a model-less signature only
  as a permanently unexecutable/reference-only class; every dimension also has block or
  replan actions. No choice is prefilled, and the template itself is not a review.
- A complete positive ledger can produce only `ACCEPTED_SEMANTIC_PLAN_ONLY`. Every
  retained source parent edge must have identical selected child/parent routes; a mixed
  route across any SFLD hierarchy edge is structurally valid input but produces
  `VALID_NON_ACCEPTING`, no review-set ID, and an explicit hierarchy-replan finding.
  Any block or replan action likewise remains non-accepting. Even an accepted receipt
  declares `apply_authorized:false`, `serialization_status:NOT_PERFORMED`, zero writes,
  and `grounding_eligible:false`; it cannot replace the independent content-addressed
  `hmmsearch --cut_ga` execution receipt.
- Completed ledgers are bounded to 64 MiB and captured as stable regular files through
  component-relative no-follow descriptors. Canonical JSON, unique keys, finite values,
  exact LF termination, complete immutable bindings, real UTC-second timestamps, and
  exact byte/object agreement are mandatory. Symlink, non-regular, CR/CRLF, Unicode-line-
  separator, stale-summary, altered/reordered binding, duplicate-item, malformed
  metadata, and new-contract drift cases fail closed.
- Two independent production template runs were byte-identical: 910 JSONL lines,
  3,153,297 bytes, binding SHA-256
  `163b3b01c9e31ccbae35bebd4bc62dfd70cf333dbe8c49479e8488bed87683f4`,
  template-row SHA-256
  `1d6eb3f3cbfb2518e1eb8f1bbd6fa74b79b42789b851722e0cbf8623e284d792`,
  complete stream SHA-256
  `52a3a6635c1dc6a48fe935c2d16272e91d6f97cb2c71768ef9d0380aa5c243e2`,
  and template ID
  `sfld-source-model-migration-review-template:d03f627eb86ac294290fe978a44ac89f30ec71abbae4b5aa4e70138506267259`.
- The focused review module passes all 16 tests; the broader writer/strict/seeder/SFLD
  parser/matcher/planner/review gate passes all 154 tests in 24.91 seconds. Ruff
  lint/format and whitespace checks are clean, and the repository writer audit remains
  clean across 199 scripts. Final review compiler/test SHA-256 values are
  `64db24b2887ff3cf9431f2dc1cfc968e67a8dcb1133319c1495ab5487fdc7077`
  and `19daf608b89f6df208cee4a34927c305c5c6aee48f15c63ad25a5064c49aaa08`.
  The repository-wide integration gate then passed all 2,255 tests with zero failures
  and the same 25 third-party deprecation warnings in 2,676.24 seconds (44:36).
- No completed SFLD review ledger or human decision was created. No profile
  representation was serialized into any of the 303 current records, and no network
  request, trait write, durable grounding write, qualification, commit, or pull request
  occurred. The protected registries remain exactly 126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  all SFLD profile fields remain absent from the trait tree, and all nine Batch-012
  fetch/resolution outputs remain absent.

### 2026-08-25 — SFLD `hmmsearch --cut_ga` execution-receipt preflight

- `scripts/validate_sfld_hmmsearch_receipt.py` defines the first strict, read-only
  content/semantic verification boundary for a future SFLD profile-search execution.
  It does not run HMMER, create the target FASTA, install a receipt, serialize a profile
  into a trait, or promote grounding. Its pure `build_receipt_value` helper exists only
  so a future controlled runner can construct the exact value it must install last;
  verification independently recaptures and rederives that value. Parsing the already
  captured SFLD bytes uses automatically removed temporary copies because the existing
  release parser is path-based; no repository or durable artifact is written.
- The schema-v1 receipt content-addresses the exact executable bytes and permission
  mode; complete `hmmsearch -h` stdout/stderr; HMMER version; literal argv and
  `LC_ALL=C`; exit, standard-stream, and no-network attestations; pinned HMM,
  hierarchy, and correlated-site artifacts; the canonical ProteinReference registry
  and its exact full-registry FASTA projection; complete main stdout, stderr,
  Stockholm `-A`, and `--domtblout` bytes; one physical selected domain-table row; its
  model, target, scores, coordinates, and registry subsequence; and the exact
  `sfld_match` correlated-site evaluation derived from a single-target Stockholm
  projection. Every source/receipt path is captured through component-relative
  `O_NOFOLLOW`, bounded regular-file reads; lexical aliases, hard-link aliases,
  noncanonical or duplicate-key JSON, non-finite values, source/profile drift, and
  same-path mutation or replacement through the final recheck fail closed.
- The exact execution contract, after the controlled-runner hardening recorded below,
  is `hmmsearch --cut_ga --cpu 0 --seed 42 --tformat fasta -A <stockholm>
  --domtblout <domains> <pinned-hmm> <canonical-full-registry-fasta>`. Official HMMER
  source defines `--cut_ga` as using
  the profile GA gathering cutoffs for all thresholding and records the HMM, target,
  `-A`, domain-table, and `GA cutoffs` paths in main output
  ([`hmmsearch.c`](https://github.com/EddyRivasLab/hmmer/blob/master/src/hmmsearch.c)).
  The official man page states that GA1/GA2 set per-sequence/per-domain reporting and
  inclusion thresholds and that `-A` saves significant included hits
  ([`hmmsearch` manual](https://github.com/EddyRivasLab/hmmer/blob/master/documentation/man/hmmsearch.man.in)).
  HMMER's alignment code includes only included domains and its alignment-display code
  constructs sequence names as `<target>/<alignment-start>-<alignment-end>`, which is
  the identifier this verifier joins to the selected domain-table row
  ([`p7_tophits.c`](https://github.com/EddyRivasLab/hmmer/blob/master/src/p7_tophits.c),
  [`p7_alidisplay.c`](https://github.com/EddyRivasLab/hmmer/blob/master/src/p7_alidisplay.c)).
- Current production replay is pinned to 299 SFLD models and manifest SHA-256
  `8b492f010c965f5d76f21e6d5665976570f7c14f25dc7499e9ecd6105ab685ad`.
  The current 126-row registry remains SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`;
  its deterministic header-only FASTA projection is 79,906 bytes at SHA-256
  `0aa2b6f9d1ce74ebc132184284475de53f55ccc62d0ecd7498d79d522ef18e9f`.
  Receipt score replay allows only the half-unit implied by HMMER's displayed decimal
  precision; a visibly sub-GA sequence or domain score is rejected. The selected
  ungapped alignment must exactly equal the registry substring at the declared
  alignment coordinates, and a correlated-site mismatch remains a valid profile-hit
  diagnostic but is explicitly non-grounding.
- The verifier deliberately reports the exact provenance limit
  `CONTENT_AND_SEMANTIC_BINDINGS_VERIFIED;PROCESS_EXECUTION_ATTESTED_BY_PRODUCER_NOT_REEXECUTED_OR_AUTHENTICATED`.
  It cannot prove that the bound executable actually produced the bound output, and an
  opaque producer implementation hash is not authentication. At this pre-runner
  checkpoint, no controlled runner, production FASTA, HMMER output, or production
  receipt existed. One receipt binds
  one selected physical domain row; a future runner must either install one
  independently addressed receipt per candidate row from a shared complete run or add
  a separately reviewed, equally strict multi-row receipt schema. Either path still
  requires the independent provider-acquisition receipt, accepted SFLD semantic review
  and authorized migration, qualified-record binding, and human review.
- `hmmsearch`, `hmmalign`, and `hmmscan` are not installed on this machine, so no real
  execution or timing claim was made. HMMER 3.4's official release notes state native
  Apple Silicon M1/M2 support
  ([release notes](https://github.com/EddyRivasLab/hmmer/blob/master/release-notes/RELEASE-3.4.md)),
  but that compatibility statement was not locally exercised. No package was installed
  and no network action occurred.
- All 24 verifier tests pass, including the real installed SFLD release/manifest and
  current registry/FASTA projections, ten material artifact mutations, invalid GA
  scores, alignment/registry disagreement, correlated-site mismatch, malformed or
  noncanonical receipt inputs, impossible timestamps, executable-version disagreement,
  symlink/hard-link rejection, CLI no-durable-write behavior, and a mutation between
  semantic replay and final recapture. The broader SFLD/planner/review/grounding/
  strict/writer gate passes all 324 tests in 21.09 seconds. Ruff lint/format,
  `git diff --check`, and the repository writer audit are clean; the audit now covers
  200 scripts. Verifier/test SHA-256 values are
  `47f52d6c6e9478d349e2494e8f7ea0fa1e16a4f1a88fa417b9ce55958b9d977c`
  and `09c46d8406f436f4e8ac81c0aec59b04dcec14cecb4958a15b012ffddd02de96`.
  The final repository-wide integration gate passes all 2,279 tests with zero failures
  and the same 25 third-party deprecation warnings in 2,575.41 seconds (42:55).
- No HMMER process, production receipt, profile migration, review decision, network
  request, trait write, durable grounding write, qualification, commit, or pull request
  occurred. The protected registries remain exactly 126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  all 303 SFLD traits still lack `sequence_profile_representations`, and all nine
  Batch-012 fetch/resolution outputs remain absent.

### 2026-08-25 to 2026-08-26 — controlled SFLD HMMER runner boundary

- `scripts/run_sfld_hmmsearch.py` now closes the source/test portion of the missing
  process boundary. Default invocation performs no process execution and no persistent
  write: it prints one canonical, content-addressed schema-v1 execution plan. Apply is
  unavailable unless the operator supplies both `--apply` and that exact saved
  `--execution-plan`, and the current executable bytes match a separately supplied
  lowercase `--approved-executable-sha256`. The approval digest is explicitly labelled
  operator selection, not producer authentication or executable source provenance.
  Plans also bind all input paths/hashes/sizes, executable and runner modes, output
  parent device/inode, every output path, exact selector, full-registry FASTA digest,
  timeout, working directory, environment, and literal argv.
- Apply creates one previously absent directory beneath `reports/` or the system
  temporary root through a retained component-relative `O_DIRECTORY|O_NOFOLLOW` parent
  binding. It never opens an existing generation for update or replaces an existing
  leaf. Before execution it installs self-contained copies of the approved executable,
  runner, saved plan, pinned SFLD HMM/hierarchy/sites, exact ProteinReference registry,
  and derived FASTA. The copied executable—not the mutable source path—is executed from
  the bound run directory with the exact environment `LC_ALL=C` and stdin at EOF. Every
  input/output inode and every copied input byte digest is checked after execution;
  each file and directory is `fsync`ed before receipt construction.
- The runner first captures and validates `hmmsearch -h`; a nonzero exit, stderr byte,
  version other than exactly HMMER 3.4, or missing `--cut_ga`, `--cpu`, `--seed`, or
  `--tformat` capability prevents the search. The search is then pinned to
  `hmmsearch --cut_ga --cpu 0 --seed 42 --tformat fasta -A <stockholm>
  --domtblout <domains> <pinned-hmm> <canonical-fasta>`. Serial execution, the fixed
  default RNG seed made explicit, and explicit FASTA parsing remove machine-core-count,
  seed, and format-autodetection ambiguity. The verifier now requires the main-output
  declarations `GA cutoffs`, random seed 42, target format `fasta`, and zero worker
  threads, and content-addresses the executable permission mode and attested working
  directory as well as its bytes. HMMER's official 3.4 source declares `--cpu`, `--seed`,
  and `--tformat` and prints `# number of worker threads: <n>` when `--cpu` is used
  ([`hmmsearch.c`](https://github.com/EddyRivasLab/hmmer/blob/master/src/hmmsearch.c));
  the official release is tag `hmmer-3.4`, commit `9acd8b6`
  ([release](https://github.com/EddyRivasLab/hmmer/releases/tag/hmmer-3.4)).
- The planned selector is one exact `(SFLD model accession, ProteinReference ID, domain
  number)`. After the one complete multi-model/full-registry search, exactly one
  physical domain-table row must match. The existing receipt verifier then replays all
  content, score, coordinate, sequence, and correlated-site semantics. The runner first
  writes the receipt at a nonauthoritative candidate path, fully verifies it there,
  then installs the authoritative receipt with a no-overwrite hard-link operation and
  removes the candidate name. It immediately verifies the final path again. A crash,
  process failure, unsupported version, absent/ambiguous selector, changed inode/input,
  or semantic failure before candidate verification can leave a new
  `RUN_STARTED_RECEIPT_ABSENT` staging directory but no authoritative receipt and cannot
  alter a prior generation. Once the no-overwrite link succeeds, its bytes have already
  passed full verification; an interruption can leave both candidate and final names,
  and every consumer must still rerun final-path verification rather than trusting file
  presence alone.
- A no-hit run currently leaves that explicit receipt-absent staging bundle; it is not
  misrepresented as a verified negative biological result. If durable negative SFLD
  evidence becomes necessary, it needs a separate schema that binds the complete
  successful run and exact absent selector. Likewise, this deliberately singular
  positive receipt is not a high-throughput multi-row receipt. Reusing one completed
  run for many grounding claims will require a separately reviewed batch receipt/index
  rather than rerunning all 299 models once per claim.
- Exact executable hash approval does not prove how the binary was acquired or built.
  Both the receipt and run result therefore keep grounding false and now name
  `HMMER_EXECUTABLE_BUILD_OR_ACQUISITION_RECEIPT_REQUIRED` in addition to the SFLD
  provider-acquisition, semantic-migration/apply, qualified-record-binding, and human-
  review gates. The verifier still reports that process execution is producer-attested,
  not independently reexecuted or authenticated.
- Synthetic controlled executions in automatically removed pytest directories exercise
  the real subprocess and filesystem path. Fifteen runner tests cover deterministic
  no-execution planning, exact executable approval, exact saved-plan replay,
  self-contained post-source-drift verification, receipt-last installation, source and
  output mutation, inode replacement, nonzero exit, absent selector, unsupported or
  incomplete HMMER capability, version stderr, noncanonical/readdressed plans, existing
  outputs, symlink parents, and apply-without-plan denial. Twenty-seven verifier tests
  additionally cover permission-mode and HMMER-policy drift. The artifact-conditional
  production dry-plan test replays all 299 installed SFLD models and the exact current
  126-protein/79,906-byte FASTA projection without executing its synthetic placeholder
  executable or creating the planned directory.
- The combined runner/verifier focused gate passes all 42 tests; the broader
  SFLD/release/matcher/planner/review/grounding/strict/writer gate passes all 342 tests
  in 29.56 seconds. Ruff lint/format and `git diff --check` pass, and the repository
  writer audit remains clean across 201 scripts. Current verifier/runner and paired test
  SHA-256 values are
  `34fa293d805e270c44c989620602560ed116407f89892c7fbc014831bba2eb13` /
  `2a4a4e5c59402341563a176f91e6e47a1271c6dd66c34805256b175c326f9fd3`
  and `bb9df3c60c63d935aae88a8889ccbf669a2de2ed2b9c6d3a15bd6b07b7bfc8da` /
  `8f6feed27928ef8e3a5707290c0d0ed04d229d02c5898815df6346d1769d9f31`.
  The repository-wide integration gate then passes all 2,297 tests with zero failures
  and the same 25 third-party deprecation warnings in 2,759.52 seconds (45:59).
- No production HMMER executable is installed, no production execution plan or run
  directory was materialized, and no real SFLD search or runtime measurement was made.
  Only read-only official HMMER source/release browsing and synthetic temporary process
  tests occurred. No provider fetch, profile migration, review decision, trait write,
  durable grounding write, qualification, commit, or pull request occurred. The
  protected registries remain exactly 126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  all 303 SFLD traits remain without `sequence_profile_representations`, and all nine
  Batch-012 fetch/resolution outputs remain absent.

### 2026-08-26 — direct Rhea/UniProtKB source-native acquisition and staging boundary

- A local source audit selected Rhea as the next safe high-value lane. The available
  OrthoDB cache contains levels and an orthologous-group catalogue but no group-member
  response; the NCBIfam, PANTHER, CDD, and Pfam caches are model/catalogue metadata;
  Reactome is represented only by hierarchy/descriptive JSON; the condensed RepeatsDB
  cache has 74 representative PDB/chain rows but has discarded exact repeat boundaries
  and only three representatives have local SIFTS; and the OMA cache contains group
  metadata and member URLs rather than member response bytes. None supports an exact
  new protein-membership claim from the installed bytes.
- An EC bridge was explicitly rejected as a substitute for a direct Rhea association.
  The local experiment found 5,136 EC classes with Rhea mappings, producing 190,653
  candidate rows over 4,198 Rhea traits and 179,025 unique accessions, but only 34 rows
  (30 accessions and 32 traits) intersect the protected ProteinReference registry. More
  importantly, EC-only association is an indirect class bridge under this plan and
  remains candidate evidence; it cannot establish exact Rhea source membership.
- Rhea's official [download documentation](https://www.rhea-db.org/help/download) lists
  the UniProtKB cross-reference export and states that Rhea/UniProtKB links come from
  UniProt curation. The official [TSV contract](https://ftp.expasy.org/databases/rhea/tsv/README.txt)
  defines the cross-reference columns `RHEA_ID`, `DIRECTION`, `MASTER_ID`, and `ID`;
  the [release properties](https://ftp.expasy.org/databases/rhea/rhea-release.properties)
  identify release 141 dated 2026-06-10; and the official
  [license](https://ftp.expasy.org/databases/rhea/LICENSE.txt) is CC BY 4.0. The current
  [TSV directory](https://ftp.expasy.org/databases/rhea/tsv/) exposes the exact
  `rhea2uniprot_sprot.tsv` source required by this lane. These links were inspected
  read-only; no provider byte was fetched into the workspace.
- `scripts/stage_rhea_uniprot_grounding.py --acquisition-plan` prints one canonical,
  content-addressed, no-network/no-write release-141 acquisition plan. It names the
  mapping, release properties, TSV README, license, directions, and reactions artifacts;
  requires raw response URL/status/header/size/digest and release-coherence semantics in
  a future acquisition receipt; and forbids EC, synthetic, or partial-export
  substitutions. Its plan ID is
  `rhea-uniprot-source-acquisition-plan:f1c4ab1847503d811f13d466f6dc1ac47c59edb25b8902da832ee89a5f29cb4f`,
  plan-row SHA-256 is
  `019b9ed111c7bb8706fbd5dfb3db11737ee2884393ab5805486355be27484cad`,
  and canonical stdout SHA-256 is
  `d19077cbb2c76f4ce1083c36605e8789ea36fe3fbba3d6a3d5759480409fe98e`.
  The mapping, release-properties, README, and license targets are currently absent, so
  normal production staging fails closed at the missing mapping and cannot synthesize
  an input.
- Once all six artifacts are present, the normal stage requires the exact 141/
  2026-06-10 release declaration, README and CC BY contract text, a complete unique
  Rhea direction quartet for every reaction, exact direction/master agreement for every
  physical mapping row, and equality of the 18,558 direction, reaction-master, and Rhea
  trait identifier sets. It inventories the exact flat lowercase-`.yaml` Rhea route and
  exhaustively prefilters hidden, ignored, alternate-extension, escaped, and UTF-encoded
  identity candidates across the complete trait tree. Every candidate is parsed as YAML
  to reject quoted/folded/escaped semantic shadows, duplicates, and symlinks; each exact
  Rhea trait must also validate the seeded equation/definition/source/axis/category/kind/
  license projection. The pinned `2026_02` ProteinReference registry is parsed
  canonically. Source, registry, selected trait, and namespace-candidate bytes are
  captured through no-follow, regular-file, single-link reads. Before output, the stage
  rescans the exhaustive candidate/route path inventory and replays every captured inode
  and content digest without redundantly decoding all YAML a second time. The quiescence
  check is deliberately documented as practical drift detection, not an atomic
  filesystem snapshot.
- Multiple directional physical rows are aggregated into one exact `(master Rhea trait,
  UniProtKB protein)` candidate. Only Rhea traits without an existing canonical example
  enter this missing-protein lane. Each output remains `CANDIDATE_ONLY`, uses direct
  `SOURCE_MEMBERSHIP` at `WHOLE_PROTEIN` scope, retains the physical source rows and
  their line digests, and emits neither invented coordinates nor GroundingEvidence.
  Missing current-release ProteinReferences become deduplicated fetch requests. The
  command has no apply, network, output-file, trait-writer, promotion, or evidence-writer
  mode and writes canonical JSONL only to stdout.
- The release number is presently only a content-bound co-located property, not a
  cryptographic binding between the future mapping response and release declaration.
  Candidates and their source snapshot therefore state
  `COLOCATED_RELEASE_PROPERTY_CONTENT_BOUND_WITHOUT_ACQUISITION_RECEIPT`. Promotion is
  unconditionally blocked on the absent Rhea acquisition receipt, a verified
  ProteinReference fetch receipt, the absent acquisition-receipt verifier in the
  grounding boundary, human review, and separate promotion authorization. The exact
  central Rhea `SOURCE_DATABASE` shape contract recorded in the next checkpoint replaces
  the former generic deny finding but retains an unconditional source-specific receipt
  lock; this stage does not enable qualification.
- Twenty-seven focused tests pass in 271.33 seconds (4:31) after the central-contract
  blocker vocabulary update. They cover deterministic aggregation,
  content addressing, missing-reference partitioning, existing-example exclusion,
  source/release/license/direction/trait/registry failures, duplicate keys, semantic
  shadows in plain, quoted, hidden, ignored, alternate-extension, and escaped forms,
  exact-route inventory, symlink/hard-link and source/identity-candidate mutation
  rejection, exact hash pins, no-write CLI behavior, and absent-production-artifact
  denial. The production-compatibility case uses one clearly synthetic mapping row only
  in pytest's temporary directory while replaying the real 18,558 release-141 direction
  rows, reactions, complete Rhea trait tree, and current registry. It proves catalogue/
  trait compatibility and candidate traversal; it is not evidence that the missing
  direct mapping was fetched or that any real Rhea membership was staged. The exhaustive
  semantic inventory increased the measured focused-gate cost from the earlier narrow
  39.12-second scan; eliminating only a redundant second YAML decode reduced the first
  hardened 517.76-second/24-test baseline to 270.56 seconds for 25 tests, without
  weakening the initial parse or final path/inode/content replay. Explicit folded and
  UTF-16 shadow cases bring the final gate to the current 27-test timing above. Current
  stage/test SHA-256 values are
  `c63f98b35e3fbb4a09a2b3e52aa6969d0dc3c10690425c843b7b808a3f6ed7f4`
  and `63a6c297e934021b5303ce207084d539150b6c208a0090bfda24b72d6d657fbe`.
  Before the central-contract change, the post-namespace-hardening provider-stage,
  central-validator, strict-validator, and writer gate passed all 395 then-present tests
  in 1,180.12 seconds (19:40); the later folded/UTF-16 assertions passed in the focused
  and repository-wide gates. Current Ruff lint/format, Python compilation, and
  `git diff --check` pass, and the repository writer audit remains clean across 202
  scripts. Fresh central-contract integration results are recorded below.
- No provider fetch, trait write, durable grounding write, evidence emission,
  qualification, review decision, commit, or pull request occurred. The protected
  registries remain exactly 126/127 rows at SHA-256
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c`
  and `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`;
  the pre-existing trait diff remains
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  all 303 SFLD traits still lack `sequence_profile_representations`, and all nine
  Batch-012 fetch/resolution artifacts remain absent. The four newly required Rhea
  mapping/release-properties/README/license artifacts also remain absent. The staging-
  phase repository-wide integration gate passed all 2,324 tests with zero failures and the
  same 25 third-party `sssom_schema`, pandas, and `funowl` deprecation warnings in
  2,726.23 seconds (45:26). A post-suite replay reproduced both durable row counts and
  hashes, the exact trait-diff hash, the 303/0 SFLD record/profile partition, all nine
  Batch-012 absences, all four Rhea absences, and the final stage/test/acquisition-stdout
  hashes above.

### 2026-08-26 — central Rhea `SOURCE_DATABASE` contract and receipt-verifier lock

- `scripts/validate_uniprot_grounding.py` now recognizes Rhea only from the exact
  `evidence_source: Rhea` reverse claim or an exact uppercase `RHEA` namespace on either
  `trait_id` or `source_trait_id`. A shaped claim must use direct `SOURCE_MEMBERSHIP`,
  exact equal `RHEA:<positive decimal integer>` trait/source IDs,
  `provider_kind: SOURCE_DATABASE`, `scope: WHOLE_PROTEIN`, source and provider release
  exactly `141`, and the canonical provider path
  `data/raw/rhea/rhea2uniprot_sprot.tsv`. Inheritance, structure, chain, mapping-
  completeness, and residue-count provenance are categorically invalid in this direct
  whole-protein lane; the existing generic whole-protein gate independently rejects
  coordinate and residue fields.
- Matching is fail-closed in both directions. An exact Rhea namespace with a false
  provider name still gets `rhea_source_mismatch`; the exact `Rhea` provider name with
  false IDs still gets `rhea_source_trait_mismatch`. Case, suffix, legacy-spelling, and
  descriptive near misses do not capture another provider and continue to receive the
  generic `source_database_contract_required` denial. A correctly shaped claim no
  longer gets that generic finding; it gets exactly `rhea_provider_receipt_required`.
- The Rhea receipt finding is unconditional. It explicitly requires an authentic
  release-141 provider acquisition receipt, exact physical mapping-row replay, a
  verified ProteinReference fetch receipt, and a receipt verifier in the central
  grounding boundary. No receipt field, loader, verifier, approval, or success branch
  was invented in this phase, so no evidence can satisfy the lock and no qualification
  path was opened. `scripts/stage_rhea_uniprot_grounding.py` correspondingly replaces
  the stale `MISSING_RHEA_SOURCE_DATABASE_VALIDATOR_CONTRACT` candidate blocker with
  `MISSING_RHEA_ACQUISITION_RECEIPT_VERIFIER_IN_GROUNDING_BOUNDARY`; the independently
  absent provider and registry receipts, human review, and promotion authorization stay
  separate blockers.
- Twenty-four targeted Rhea/generic-contract tests pass in 0.96 seconds, and the complete
  central grounding-validator module passes all 209 tests in 1.32 seconds. They cover
  every required Rhea field, invalid zero/leading-zero IDs, reverse source/namespace
  triggers, exact near-miss isolation, forbidden inheritance and structural provenance,
  retention of the source-specific receipt lock on malformed rows, and preservation of
  the unmatched-source generic deny gate. The updated 27-test Rhea stage gate passes in
  271.33 seconds (4:31), including the real 18,558-trait catalogue replay. Current
  validator/test and stage/test SHA-256 pairs are
  `73c01aec0814336054a6428e28183999cfb4c8200391f2ac4d98f0ee73bb60bd` /
  `c4df479d3541d494550f2f11cf11c7bcc0c8a3eabcb7f2862e3ea71ac5132704`
  and `c63f98b35e3fbb4a09a2b3e52aa6969d0dc3c10690425c843b7b808a3f6ed7f4` /
  `63a6c297e934021b5303ce207084d539150b6c208a0090bfda24b72d6d657fbe`.
  The acquisition-plan stdout remains byte-identical at SHA-256
  `d19077cbb2c76f4ce1083c36605e8789ea36fe3fbba3d6a3d5759480409fe98e`.
- No provider byte or receipt was fetched or synthesized, and no trait, durable
  grounding, review, qualification, commit, or pull-request action occurred. The exact
  provider-stage, central-validator, strict-validator, and writer integration gate
  passes all 420 tests in 1,132.49 seconds (18:52). The repository-wide integration
  gate then passes all 2,347 tests with zero failures and the same 25 third-party
  `sssom_schema`, pandas, and `funowl` deprecation warnings in 2,746.78 seconds (45:46).
  Final Ruff lint/format, Python compilation, `git diff --check`, and the 202-script
  writer audit are clean. The post-suite protected-state replay reproduces the exact
  126/127 registry rows and SHA-256 values, the
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`
  trait-diff hash, the 303/0 SFLD record/profile partition, all nine Batch-012 output
  absences, all four Rhea acquisition-artifact absences, and every final source/test/
  acquisition-plan hash above.

### 2026-08-26 — standalone Rhea provider-acquisition receipt verifier boundary

- `scripts/validate_rhea_acquisition_receipt.py` adds a strict, read-only verifier for
  one future canonical receipt at
  `data/raw/rhea/rhea-provider-acquisition-receipt.json`. It binds the exact six-role
  release-141 acquisition plan (UniProtKB/Swiss-Prot mapping, release properties, TSV
  README, license, directions, and reactions), official request/final URLs, ordered
  UTC-second response timestamps, integer-200 producer attestations, a bounded normalized
  response-header projection with HTTP `Date`, raw response-body byte counts and
  SHA-256 values, the acquisition-plan ID/hash, and one opaque producer implementation
  claim. The receipt is exact one-line canonical JSON with a content-derived receipt ID;
  the CLI has no network, apply, or output-file mode.
- Verification replays the release/date, TSV, license, direction, reaction, and physical
  mapping-row parsers rather than trusting receipt-derived counts. Under the production
  contract it requires the exact 18,558-master direction/reaction catalogues and their
  pinned release-141 byte digests, equal master sets, direction consistency, and the
  content-bound mapping projection. Every source and receipt path is canonical and read
  through descriptor-relative no-follow, bounded, regular-file, single-link capture;
  source/source and source/receipt aliases are rejected, and inode/metadata/content are
  replayed after semantic verification to detect concurrent drift.
- Passing this standalone verifier proves only internal content and semantic consistency
  of a producer's supplied HTTPS attestation. It does **not** authenticate the producer,
  reconstruct TLS, prove that Rhea served those bytes, or independently repeat a network
  request. The exact machine-readable limit is
  `CONTENT_AND_SEMANTIC_BINDINGS_VERIFIED;HTTPS_ACQUISITION_ATTESTED_BY_PRODUCER_NOT_REEXECUTED_OR_AUTHENTICATED`.
  Its result therefore always reports `producer_authenticated: false`,
  `central_grounding_eligible: false`, and no verifier network action or writes. The
  central validator has not been taught to load this receipt and retains its
  unconditional `rhea_provider_receipt_required` finding; the stage retains
  `MISSING_RHEA_ACQUISITION_RECEIPT_VERIFIER_IN_GROUNDING_BOUNDARY`. No qualification or
  promotion path was opened.
- Thirty-one focused tests pass in 0.59 seconds. They cover deterministic content
  addressing, mutation of every response body and receipt policy/derived field, exact
  URL/status/timestamp/header and producer-claim shapes, noncanonical/duplicate/CRLF
  JSON, symlink/hard-link/path aliasing, concurrent source mutation, production release
  enforcement, CLI denial, and stable acquisition-plan binding. One compatibility test
  replays the real installed 18,558-master release-141 direction/reaction catalogues
  with one clearly synthetic mapping row only inside pytest's temporary directory; it
  is not a provider fetch or biological evidence. The broader Rhea-stage, standalone-
  verifier, central-validator, strict-validator, and writer-audit gate passes all 306
  tests in 301.07 seconds (5:01). Ruff lint/format, Python compilation, and
  `git diff --check` pass for the new files, and the repository writer audit remains
  clean across 203 scripts. Current verifier/test SHA-256 values are
  `4c15a4c0f1850c9482740f1c330981ef99c75b72f02b29b3cd3843f2afe5ebf7` and
  `59cb3649ba6a5ddaf2f43cc92dee6b362489228311d3213cc72f8cfa8dced72f`.
- The default production verifier fails closed because the receipt is absent. No
  provider fetch or source/receipt artifact was created; no trait, durable grounding,
  review, qualification, commit, or pull-request action occurred. The repository-wide
  integration gate passes all 2,378 tests with zero failures and the same 25 third-party
  `sssom_schema`, pandas, and `funowl` deprecation warnings in 2,756.59 seconds (45:56).
  Final repository-wide Ruff lint, focused format/compilation, `git diff --check`, and
  the 203-script writer audit are clean. The post-suite protected-state replay reproduces
  the exact 126/127 durable row counts and SHA-256 values
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c` /
  `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`,
  the unchanged trait-diff SHA-256
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`,
  the 303/0 SFLD record/profile partition, all nine Batch-012 output absences, and
  absence of the four planned Rhea source artifacts plus the receipt itself.

### 2026-08-26 — controlled Rhea acquisition-runner boundary

- `scripts/acquire_rhea_sources.py` supplies the execution boundary for the existing
  six-artifact acquisition plan. Default invocation performs no network request and no
  write and prints one canonical execution plan. Apply is unavailable without both
  `--apply` and that exact saved `--execution-plan`; the saved plan is independently
  content-addressed and freshly rederived before the first response and again after all
  responses. It binds the provider plan ID/row hash, exact production repository/root
  targets, output-parent device/inode, present/absent source state, runner bytes, byte
  limits, timeout, release enforcement, and an explicit no-trait/no-grounding safety
  boundary. The production CLI exposes no repository-root or output-path override.
- Apply uses exact HTTPS `GET` URLs with `Accept-Encoding: identity`, requires exact
  final URLs and integer-200 responses, captures an allowlisted normalized header
  projection with HTTP `Date`, enforces declared content length when present, and reads
  every body under the verifier's role-specific bound. All six responses must complete
  before the first temporary or target write. The complete downloaded bundle is first
  installed in an automatically removed, resolved system-temporary repository, parsed,
  content-addressed, and passed through the standalone verifier. Invalid release/date,
  README, license, catalogue, mapping, response-header, timestamp, or semantic content
  therefore aborts before any production target is created.
- Immediately before installation, the runner rederives the saved plan, rechecks the
  saved-plan and runner bytes, validates every absent target and every pre-existing
  target's exact inode/hash/size and equality to its HTTPS response, and only then
  creates missing source leaves with descriptor-relative `O_EXCL | O_NOFOLLOW` writes.
  It recaptures all six installed/pre-existing bodies and installs the canonical receipt
  last without replacement, then invokes the standalone verifier over the production
  paths. A target race or partial source installation leaves the receipt absent and is
  categorically non-grounding; recovery requires deriving and reviewing a fresh plan.
  The runner is deliberately first-generation-only and refuses to replace any existing
  receipt rather than silently refreshing provenance.
- A successful run would still produce only the same unauthenticated producer
  attestation described in the preceding checkpoint. Its result always reports
  `producer_authenticated: false` and `central_grounding_eligible: false`; neither the
  central validator nor the candidate stage was changed, and no review, qualification,
  or promotion branch was added.
- The current production dry plan is byte-identical across two independent invocations:
  4,599 bytes at SHA-256
  `8dbe4120834a61d9dff9e9fd9ad9253625b96b3b6f5c98b7eeb2a02fb509e2df`,
  with plan ID
  `rhea-provider-acquisition-execution-plan:ca8c4a5d417fe1cc2c22a6deb923c2de54f9c87e9ca121cb0113665b1b8a7b47`.
  It records the pinned direction/reaction files as present and the mapping, release
  properties, README, license, and receipt as absent. No saved production plan was
  written.
- Nineteen focused tests pass in 0.48 seconds. They cover dry determinism/no-network/
  no-write behavior, all-responses-before-write and receipt-last ordering, preservation
  of matching pre-existing inodes, pre-write rejection of a mismatching late-role file,
  transport/status/final-URL/header/date/size/body failures, bounded reads, exact saved-
  plan serialization and replay, plan/source/parent drift, installation races, symlink/
  hard-link defenses, CLI option closure, second-generation refusal, and a real
  18,558-master release-141 catalogue replay with one synthetic mapping row only in
  pytest's temporary directory. The combined runner/verifier/Rhea-stage/central/strict/
  writer gate passes all 325 tests in 293.23 seconds (4:53). Repository-wide Ruff lint,
  focused formatting/compilation, `git diff --check`, and the writer audit are clean
  across 204 scripts. Current runner/test SHA-256 values are
  `6c2156cb549872d829d6475af4908ed3d617a8ef5d4107f30a5e07c6591a8e83` and
  `00e60e6a39a08f4e4791076b3b64f9da4d4250f49384ec95f5cd2329e5fb0c45`.
- No production `--apply`, network request, provider/source/receipt write, trait or
  durable-grounding write, review, qualification, commit, or pull-request action
  occurred. Repository-wide regression and final protected-state replay results for
  this runner checkpoint are recorded after the gate below.
- The repository-wide integration gate passes all 2,397 tests with zero failures and the
  same 25 third-party `sssom_schema`, pandas, and `funowl` deprecation warnings in
  2,833.35 seconds (47:13). That is the preceding checkpoint's 2,378-test gate plus the
  19 runner cases, and the runtime stays within the 45:46/45:56 profile of the two prior
  full runs. Collection reports exactly 2,397 tests, so no case was skipped or lost.
- The project lint gate (`ruff check scripts/ tests/`) passes repository-wide, focused
  formatting of the six Rhea runner/verifier/stage modules and their tests is clean,
  `python -m compileall` over `scripts`, `src`, and `tests` exits zero, `git diff --check`
  is clean, and the writer audit is clean across 204 scripts (49 seeders, 6 registered
  editors, 1 registered validated promoter, 50 declared bypasses). Repository-wide
  `ruff format --check` is deliberately not treated as a gate here: it reports 214
  pre-existing files that predate this work and are outside the project's declared lint
  surface.
- The post-suite protected-state replay reproduces every checkpointed invariant exactly:
  126 ProteinReference rows at
  `d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c` and 127 occurrence
  rows at `a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47`, the
  unchanged trait-diff SHA-256
  `8185bfa48e10794a171402b337f742e856e2c010c24763e5193b5f35bc370859`, the 303/0 SFLD
  record/profile partition with `sequence_profile_representations` still absent from the
  trait tree, all nine Batch-012 fetch/resolution outputs absent with only the four
  mechanical staging inputs present, and the runner/test/verifier SHA-256 values
  `6c2156cb549872d829d6475af4908ed3d617a8ef5d4107f30a5e07c6591a8e83`,
  `00e60e6a39a08f4e4791076b3b64f9da4d4250f49384ec95f5cd2329e5fb0c45`, and
  `4c15a4c0f1850c9482740f1c330981ef99c75b72f02b29b3cd3843f2afe5ebf7`.
- The production dry plan is byte-identical across three independent invocations spanning
  the full suite -- two before it and one after -- at 4,599 bytes and SHA-256
  `8dbe4120834a61d9dff9e9fd9ad9253625b96b3b6f5c98b7eeb2a02fb509e2df` with plan ID
  `rhea-provider-acquisition-execution-plan:ca8c4a5d417fe1cc2c22a6deb923c2de54f9c87e9ca121cb0113665b1b8a7b47`.
  All seven output bindings still agree with the plan's declared state: the pinned
  direction and reaction files present and byte-bound, and the mapping, release
  properties, README, license, and receipt absent. `data/raw/rhea` holds only the four
  files it held before this checkpoint. The default standalone verifier still fails
  closed at exit 2 on the absent receipt.
- No production `--apply`, network request, provider/source/receipt write, trait or
  durable-grounding write, review, qualification, commit, or pull-request action occurred
  at this checkpoint. The controlled Rhea acquisition-runner boundary is complete and
  fully replayed; the next operation remains a separately authorized `--apply` against a
  saved and reviewed execution plan under explicitly permitted network access.
