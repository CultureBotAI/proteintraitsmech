# Cross-Mech protein snapshot

What the sibling Mechs say about proteins, pinned to exact commits. Strategy, channel
rules, statuses, and the inclusion route: [research/cross-mech-protein-examples.md](../../research/cross-mech-protein-examples.md).

- `protein_mentions.jsonl` — one canonical-JSON row per UniProtKB protein mention in a
  sibling record (`mech`, `record_path`, JSON `pointer`, `protein_id`, the classifying
  `channel`, `role`, `relation`, and the sibling `annotations` that name its trait).
  Schema v2 adds `text_span`: null for structured values or a zero-based,
  end-exclusive character span within the string at `pointer`. Explicit UniProt
  identifiers in prose and URLs are discovery references, never trait assertions.
  Rows are sorted by (`mech`, `record_path`, `pointer`, text-span start).
- `manifest.json` — the claw fleet-manifest pin, each Mech's scanned commit and record
  globs, the channel-rule digest, the SHA-256 of `protein_mentions.jsonl`, and counts.

Never hand-edit either file. Regenerate both together and commit the diff:

```bash
just scan-cross-mech-proteins --fetch --apply   # rescan every sibling at origin/main
just check-cross-mech-proteins --local          # integrity + drift against checkouts
just audit-cross-mech-proteins                  # statuses -> reports/cross-mech/ (ignored)
```

If the raw Rhea directions table is missing, run `just fetch-rhea-directions`
before auditing or rebuilding the inventory. It restores the existing release-141
checksum from the official historical archive, not the newer live table. This is
direction-to-master normalization only, never protein-trait qualification.

A sibling assertion recorded here is discovery provenance only. Nothing in this
directory qualifies a canonical example; that happens only through the UniProt
grounding funnel.

## Protein-first coverage

`just build-cross-mech-inventory` joins every detected protein—not only
the sibling's explicitly named traits—to all its existing PTM examples. The
search includes hidden and ignored trait YAMLs. Generated outputs:

- [coverage.md](coverage.md): linked accession table, per-Mech provenance and
  qualified/legacy example counts.
- [protein_inventory.jsonl](protein_inventory.jsonl): exact accession, sibling
  commit permalinks and pointers, PTM trait links, qualification labels, and
  qualified occurrences with their evidence identifiers. Separate discovery
  candidates retain their origin (sibling assertion versus independent UniProt
  annotation); they are not canonical examples. `current_uniprot_resolution`
  preserves inactive/deleted/split status separately from historical sequences.
- [protein_sequences.jsonl](protein_sequences.jsonl): deduplicated full sequences
  with release/checksum, plus generic annotations where the frame agrees.
- [coverage.json](coverage.json): input hashes, counts and explicit limitations.

For available generic UniProt tracks, supply
`--residue-frame data/raw/align_cache/residue_frame.json`. To discover current
sequences/annotations for the entire accession cohort, canary and then run:

```bash
just discover-cross-mech-sequences --all-proteins --include-annotations \
  --out reports/uniprot-grounding/cross-mech/refresh-20261013/discovery.jsonl --apply
just stage-cross-mech-candidates \
  --discovery reports/uniprot-grounding/cross-mech/refresh-20261013/discovery.jsonl \
  --entry-annotations reports/uniprot-grounding/cross-mech/refresh-20261013/discovery.entries.json \
  --out reports/uniprot-grounding/cross-mech/refresh-20261013/candidates.jsonl --apply
just build-cross-mech-inventory --residue-frame data/raw/align_cache/residue_frame.json \
  --uniprot-discovery reports/uniprot-grounding/cross-mech/refresh-20261013/discovery.entries.json \
  --candidate-queue reports/uniprot-grounding/cross-mech/refresh-20261013/candidates.jsonl \
  --review-batch reports/uniprot-grounding/review-batches/cross-mech-refresh-20261010 \
  --review-batch reports/uniprot-grounding/review-batches/cross-mech-complex-20261010 --apply
```

Use the same builder inputs with `--check` to verify reproducibility. Existing
input lanes and previous review batches cannot be silently omitted when replacing
an existing inventory; a minimal/cold build must use a separate `--out` directory.
Discovery snapshots/receipts are ignored; normalized sequences and annotations credit
[UniProt (CC BY 4.0)](https://www.uniprot.org/help/license). They are **not**
promotion evidence. Generic annotations retain source features/evidence codes,
and uncertain bounds or mismatched sequence/releases are reported, not overlaid.
Whole-protein traits never acquire fabricated residue intervals.

Join `protein_inventory.jsonl` to `protein_sequences.jsonl` on `sequence_key` /
`protein_id`. Canonical trait occurrences are in `ptm_examples`; generic UniProt
tracks are in `generic_features`. Both use the exact accession (isoform suffixes
are significant). Feature intervals are 1-based inclusive, with source evidence
retained; a generic active-site feature is not proof of any particular PTM trait.
`review_dispositions` retains finalized approvals/rejections and their native
resolution digests. `--review-batch` is repeatable; contradictory history is
retained, not silently overwritten. Review approval alone is not installation:
only `ptm_examples` projects what is actually present in the canonical records.
New staging runs preserve overlapping sibling and exact-entry discovery as
`SIBLING_ASSERTION_AND_UNIPROT_EXACT_ENTRY_DISCOVERY`, so retaining sibling
context cannot exclude an independently supported candidate from coverage
planning. Previously finalized snapshots retain their original provenance;
reproduction does not rewrite their decisions or grant a new qualification.
The inventory is uncapped. Browser trait pages display at most five examples,
prioritizing qualified examples; an accession missing from that page sample may
still be installed and present here.

The 2026-10-13 snapshot covers 13 sibling repositories, 656,222 declared records,
16,082 mentions and 2,602 distinct accessions. All 2,047 previous accessions remain;
555 were added to the inventory, not promoted to new canonical examples. Of the
2,602 proteins, 943 have existing qualified examples, 663 have only legacy
examples and 996 remain discovery-only. UniProt release `2026_03` returned
2,484 active sequences; 118 accessions were inactive (115 deleted, two merged,
one split). No replacement accession was substituted.
The normalized store preserves five existing `2026_02` ProteinReferences
(P00909, P02918, P11446, P17443, P42858), alongside 2,479 `2026_03` sequences.
Their release mismatch is explicit; current-release annotations are not grafted
onto these older references. 2,419 sequences have usable generic annotations
in the combined inputs; 316 proteins have existing localized qualified traits,
which are not necessarily residue-level causal explanations. Both prior batches'
71 approvals and 180 rejections remain in the inventory. Full
refresh scope, qualifications, review limits and follow-up are recorded in the
[cross-Mech research checkpoint](../../research/cross-mech-protein-examples.md).

The subsequent [36-candidate scientific self-review](../../reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.md)
recommends 33 approvals and three holds. These are **not finalized or installed**;
the finalizer was run only in dry-run mode pending independent review. They do
not change this inventory's disposition or qualification counts. The holds cover
an incorrect SOD1 reaction description and unresolved TRX2-LMA1 / mixed-CK2
variant evidence. See the review for exact claims, sources and limitations.

The [2026-10-14 SOD1 follow-up](../../research/cross-mech-protein-examples.md#sod1-chemistry-follow-up--2026-10-14)
corrects the reaction products through a shared source erratum and guarded writer.
It does not retire the old candidate hold: that snapshot requires fresh resolution
and independent review. No inventory approval or protein qualification is added.

"All" is bounded by the fleet's declared record globs and explicit UniProt
accession recognition. Gene names, other identifier namespaces, family IDs and
uncommitted sibling work are not silently resolved or treated as protein entries.
Missing sequences, absent PTM traits, unsupported evidence and unclassified
fields remain visible; this inventory does not certify scientific completeness.

## Annotated sequence example: E. coli Lpp

[UniProtKB:P69776](https://www.uniprot.org/uniprotkb/P69776/entry), release
`2026_03`, 78 residues. This protein already has a qualified whole-protein
[HAMAP:MF_00843 family example](../traits/sequence/family/hamap/major-outer-membrane-lipoprotein-lpp-lpp-mf_00843.yaml).
That qualification is separate from the generic feature annotations below.

```fasta
>UniProtKB:P69776 release=2026_03 length=78
MKATKLVLGAVILGSTLLAGCSSNAKIDQLSSDVQTLNAKVDQLSNDVNAMRSDVQAAKDDAAR
ANQRLDNMATKYRK
```

| Precursor-sequence position (1-based) | UniProt feature | Source evidence retained by UniProt |
| --- | --- | --- |
| 1–20 | Signal peptide | ECO:0000269: [PMID:4261992](https://pubmed.ncbi.nlm.nih.gov/4261992/), [PMID:4575979](https://pubmed.ncbi.nlm.nih.gov/4575979/); also HAMAP-rule ECO:0000255 |
| C21 | N-palmitoyl cysteine and S-diacylglycerol cysteine | ECO:0000269: [PMID:4575979](https://pubmed.ncbi.nlm.nih.gov/4575979/); also HAMAP-rule ECO:0000255 |
| K78 | N6-murein peptidoglycan lysine | ECO:0000269: [PMID:4245367](https://pubmed.ncbi.nlm.nih.gov/4245367/), [PMID:4261992](https://pubmed.ncbi.nlm.nih.gov/4261992/); also HAMAP-rule ECO:0000255 |

These are feature assertions in the acquired UniProt entry, not a fresh review
of the cited papers or newly qualified PTM residue-level causal claims. Full
feature payloads and evidence codes are preserved in `protein_sequences.jsonl`.
Sequence SHA-256:
`f2a3cf3329c2e936e11047c239362e181343e6076e1f6e7ecdb58de57611177e`.

Reusable workflow: [proteintraitsmech-cross-mech-proteins skill](../../.claude/skills/proteintraitsmech-cross-mech-proteins/SKILL.md).

## Annotated sequence example: human calcineurin B1

[UniProtKB:P63098](https://www.uniprot.org/uniprotkb/P63098/entry), release
`2026_03`, 170 residues. Its qualified membership in the
[gamma/R1 calcineurin complex](../traits/function/interaction_partner/complexportal/calcineurin-calmodulin-complex-gamma-r1-variant-cpx-1001.yaml)
was installed after the
[complex-membership review](../../reviews/structured/20261010T203945Z-cross-mech-complex-membership/review.md).
The inventory preserves both the approval and the installed canonical example.
Calcineurin B1 is regulatory, not the phosphatase catalytic chain.

```fasta
>UniProtKB:P63098 release=2026_03 length=170
MGNEASYPLEMCSHFDADEIKRLGKRFKKLDLDNSGSLSVEEFMSLPELQQNPLVQRVID
IFDTDGNGEVDFKEFIEGVSQFSVKGDKEQKLRFAFRIYDMDKDGYISNGELFQVLKMMV
GNNLKDTQLQQIVDKTIINADKDGDGRISFEEFCAVVGGLDIHKKMVVDV
```

| Canonical-sequence position (1-based) | Generic UniProt annotation | Evidence retained by UniProt |
| --- | --- | --- |
| G2 | N-myristoyl glycine | ECO:0000269; [PMID:25255805](https://pubmed.ncbi.nlm.nih.gov/25255805/) |
| 18–46, 50–85, 87–122, 128–163 | EF-hands 1–4 | ECO:0000255, PROSITE-ProRule PRU00448 (rule-derived) |
| D31, D33, S35, S37, E42 | Binding sites for calcium ligand 1 | Experimental, structural and rule-derived evidence; examples: [PMID:8524402](https://pubmed.ncbi.nlm.nih.gov/8524402/), [PDB:1AUI](https://www.rcsb.org/structure/1AUI) |

This is a selected feature track, not all calcium sites. The complete annotations
and evidence lists are in `protein_sequences.jsonl`. No new localized PTM
occurrence or residue-level causal explanation is implied, and these source-linked
papers were not independently reread for the feature table. Sequence SHA-256:
`92f6a360fad8f02d816c5f321ba13dc7f5dad0f59e934ad4c0d80349806b495a`.
