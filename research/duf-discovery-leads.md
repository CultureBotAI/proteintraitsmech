---
topic: Routing DUFMech's UniProt candidates onto Pfam DUF trait records as discovery leads
date: 2026-10-11
status: lane implemented; first review batch resolved, unreviewed, not promoted
scope: scripts/duf_leads.py, reports/uniprot-grounding/duf-leads, the UniProt grounding funnel
---

# DUF discovery leads

## Question

Pfam "domain of unknown function" (DUF) families have trait records here, but almost
none has a qualified canonical example. Why can't the grounding funnel reach them, and
how can DUFMech's candidate proteins get onto those records without weakening the
fail-closed contract?

## Why the ordinary funnel misses them

`just audit-uniprot-grounding` finds candidates only in the local provider frames.
Those frames are crawled for the proteins of a fixed ten-organism Swiss-Prot panel
(`build_swissprot_profiles.py`, `fetch_residue_frame.py`, `fetch_interpro_frame.py`).
DUF families are carried mostly by uncharacterized bacterial and environmental
TrEMBL entries outside that panel, so nearly every Pfam DUF record ends up
`NO_LOCAL_EXACT_TRAIT_MATCH`. Filtering the queue harder cannot fix that. The missing
proteins have to enter from somewhere else.

DUFMech froze such a list on 2026-10-07: `uniprot-duf-example-candidates-2026-10-07`.
For each DUF family that ProteinTraitsMech has a record for but no example carrying
the family, it gives up to three UniProtKB 2026_03 entries that carry the family's Pfam
cross-reference, ranked by annotation score. DUFMech's own provenance note says
these are "candidates for review ... not curated, representative or functionally
characterized examples". For 3,266 of 4,788 families the top pick has the minimum
annotation score, so ties are broken by accession.

## Policy

A DUFMech row is a **discovery lead, never qualification evidence**. This is the rule
already used for sibling-Mech proteins (CLAUDE.md;
[cross-Mech protein examples](cross-mech-protein-examples.md)). A lead tells the funnel
which accession to look at. Whether that accession carries the record's trait is
decided only by a release-pinned InterPro assertion. Promotion then still needs human
review in the ordinary batch, and separate explicit authorization.

## The lane

| Stage | Recipe | Network | Writes |
| --- | --- | --- | --- |
| Pin and audit | `just audit-duf-leads --apply` | none | `reports/uniprot-grounding/duf-leads/{leads.jsonl,summary.json}` |
| Bounded plan + identity | `just discover-duf-leads --max-records N --apply` | UniProt REST, 1 request per 100 accessions | `discovery-plan.json`, `accessions.txt`, `discovery.jsonl`, `discovery.receipt.json` |
| InterPro crawl | `just fetch-duf-interpro-frame [--limit 1] --apply` | InterPro API, 1+ request per accession | `data/raw/align_cache/duf-leads/{interpro_frame,interpro_grouped_locations}.json` |
| Candidates | `just stage-duf-candidates --apply` | none | `candidates.jsonl`, `rejected.jsonl`, `candidates.summary.json` |
| Batch | `just select-duf-review-batch <id> --max-records 100 --apply` | none | ordinary `review-batches/<id>.*` |
| Fetch | `just fetch-uniprot-review-batch <id> ...` | UniProt REST | unchanged recipe |
| Resolve | `just resolve-duf-review-batch <id>` | none | unchanged resolver; DUF InterPro sidecar bound |

Every output is gitignored staging. Nothing in the lane writes `data/traits/`,
`canonical_examples`, or the durable registries under `data/grounding/`.

### Pinning the input

The snapshot is read from git objects in the sibling DUFMech checkout
(`--dufmech-repo`, default `../DUFMech`), never from its working tree or a moving
path. `scripts/duf_leads.py` pins:

- repository `CultureBotAI/DUFMech`. The checkout's `origin` must be this repository.
- commit `217c2cc5cfc2fc43b7196e46fac57ee2a71efe0b`, which must be an ancestor of
  `origin/main`. This is DUFMech PR #137, which froze the snapshot.
- `data/worklists/uniprot-duf-example-candidates-2026-10-07.json`, SHA-256
  `0c9e637106357244f3b70f34b14c29e034e9bfdd4fec6b977b5f323174d55cbe`.
- its manifest, SHA-256
  `1004848bc569d67505929c529fcf7e7012537b3053d4c423e22dd7abb84aa45f`. The manifest's
  own byte count, digest, row total and single release (`2026_03`) are also checked.

Every row's shape is validated. A changed byte, a different origin, an unpublished
commit, or a duplicated lead fails closed. Every candidate row carries this provenance
under `duf_lead_provenance`, outside the candidate identity.

### Audit statuses

Each lead gets exactly one status:

| Status | Meaning |
| --- | --- |
| `TARGET_ABSENT_FROM_TRAIT` | exact `Pfam:<id>` record, no QUALIFIED example, protein not on it |
| `TARGET_LEGACY_ON_TRAIT` | as above, protein already there as an unproven legacy example |
| `RECORD_ALREADY_QUALIFIED` | the record already has a QUALIFIED example |
| `RECORD_CONTENT_BLOCKED` | the pinned record-content gate hard-blocks the record's own text |
| `AMBIGUOUS_TRAIT_RECORD` | more than one record carries the identifier |
| `TRAIT_NOT_IN_PTM` | no record carries the identifier |
| `OUT_OF_SCOPE_REASON` | DUFMech selected the row only as a renamed TraitMech family |

The content gate is the one the audit and resolver already use
(`uniprot_record_content_gate.py`, pinned InterPro 109.0 XML, Pfam clans and types,
PANTHER 19.0). Running it before any fetch means no request is spent on a record that
cannot qualify.

Scope comes from the record: `SEQ_FAMILY` and `SEQ_HOMOLOGOUS_SUPERFAMILY` records are
`WHOLE_PROTEIN`, and everything else (in practice `SEQ_DOMAIN`) is `LOCALIZED`. The
mapping method is always `INTERPRO_MATCH`. This is the route the plan already uses for
Pfam, including the whole-protein Pfam examples promoted in batches 014–016.

### Qualification is InterPro's, not DUFMech's

`stage-duf-candidates` turns a lead into a candidate only when the lane's InterPro
sidecar, stamped with the pinned `interpro_grounding_release` (110.0), asserts an exact
match of the record's own `Pfam:<id>` on that accession. Coordinates are copied from
the sidecar and are never computed. A `LOCALIZED` claim needs either one grouped
InterPro location, emitted with its `interpro_location_id`, or a single interval.
Sequence length, checksum and release come from the pinned UniProt discovery. Organism,
label and review status are never taken from the DUFMech row: the selector-bound
registry fetch supplies them. Rejections are reported with a reason:

- `NOT_RETURNED_BY_PINNED_UNIPROT`
- `ACCESSION_NOT_IN_INTERPRO_FRAME`
- `NO_EXACT_INTERPRO_MATCH`
- `MALFORMED_INTERPRO_INTERVAL`
- `INTERPRO_INTERVAL_OUT_OF_BOUNDS`
- `UNGROUPED_INTERPRO_LOCATIONS`

A release mismatch in either provider is a hard error, not a rejection.

The lane's InterPro sidecar is separate from the organism-panel frame
(`data/raw/align_cache/interpro_frame.json`). Lead accessions are not panel proteins,
and a partial crawl written into the panel frame would make the ordinary audit read
absence where there was only no crawl. `resolve-duf-review-batch` is the ordinary
resolver with that sidecar bound and both InterPro paths fixed. The resolver records
the sidecar path in each row's provider evidence, so a later promotion can re-check it.

### Bounds

`discover-duf-leads --max-records` (default 150) decides which target records are
crawled. Records with a reviewed (Swiss-Prot) lead come first, then the rest in
`trait_id` order, and every target lead of a chosen record is included. The batch
itself goes through the ordinary selector, with its existing limits: at most 1,000
records, at least 25 per available source, every alternative decided for a promoted
record, and at most one approved exemplar per record. Keep the discovery bound equal to
the batch bound. The selector draws records in hash order, so a larger discovery set
loses the reviewed-first preference. An earlier dry pass discovered 120 records for a
100-record batch and kept only 2 of the 15 records with a reviewed lead.

## Measurement, 2026-10-11

Pinned snapshot as above; `data/traits` at `origin/main` `8d03f717945`.

| Status | Leads | Families |
| --- | ---: | ---: |
| TARGET_ABSENT_FROM_TRAIT | 12,247 | 4,091 |
| TARGET_LEGACY_ON_TRAIT | 2 | 1 |
| RECORD_CONTENT_BLOCKED | 2,035 | 685 |
| OUT_OF_SCOPE_REASON | 24 | 8 |
| RECORD_ALREADY_QUALIFIED | 12 | 4 |
| TRAIT_NOT_IN_PTM, AMBIGUOUS_TRAIT_RECORD | 0 | 0 |

The family with a legacy lead also has absent leads, so there are 4,091 target records:
2,254 whole-protein and 1,837 localized. Of the 685 content-blocked records, 645 are
`source_scope_conflict` and 47 `definition_template_only` (a record can carry both).
Only 22 target leads, on 15 records, are reviewed Swiss-Prot entries.

### Batch `duf-leads-review-001`

All of this is gitignored staging; only the SHA-256s below are tracked.

- **Discovery.** `--max-records 100` chose 100 target records: all 15 with a reviewed
  lead, then 85 in `trait_id` order. That gave 300 leads and 300 accessions. UniProt
  2026_03 returned all 300 in 3 requests, after a 1-record canary of 1 request. The
  InterPro 110.0 crawl ran as a 1-protein canary, then the rest. It covered 360
  accessions because an earlier 120-record plan was crawled first, with 0 failures.
- **Candidates.** All 300 leads have an exact InterPro 110.0 match of the record's
  Pfam signature, with 0 rejections. They give 335 candidates: 222 whole-protein,
  plus 113 localized split by grouped InterPro location.
- **Selection.** The ordinary selector took 100 of 100 records and 335 alternatives.
  The queue SHA-256 is
  `3682b042313e81b8a34e5760646f9778e6d61e124a65f07c378e6fff449507bc`.
  There are 74 `SEQ_FAMILY`, 22 `SEQ_DOMAIN`, 3 `SEQ_REPEAT` and 1 `SEQ_MOTIF` records.
- **Fetch.** One selector-bound registry fetch of 3 requests produced 299
  ProteinReferences at 2026_03 and 3,287 membership rows. One accession, A0AA39LTJ5
  (Pfam:PF04789), was blocked with `FACT_SNAPSHOT_FAILED`: UniProt gives two distinct
  cross-references for RHEA:17989.
- **Resolve.** 334 alternatives are `QUALIFIED` and 1 is `REJECTED` (A0AA39LTJ5:
  no versioned sequence or metadata provider after the blocked fetch). Every record
  keeps at least one qualified alternative. 221 qualified alternatives are whole-protein
  and 113 localized. 22 are reviewed Swiss-Prot entries, on 15 records, and 312 are
  TrEMBL. 11 alternatives on 7 records are flagged `MULTI_INTERVAL_OR_HIT`. No record
  has a content-gate finding. Nine qualified proteins are also in the rebuilt residue
  frame, and their sequences match it.

The resolver reports these as `QUALIFIED` only in the mechanical sense: release,
sequence, checksum and exact InterPro occurrence all replay. **No human or scientific
review has been done.** `.review.tsv` has an empty `decision` column for every row. No
`.approved.tsv` or decision ledger exists. Promotion needs that review and a separate
explicit authorization.

| Artifact (`reports/uniprot-grounding/review-batches/`) | SHA-256 |
| --- | --- |
| `duf-leads-review-001.candidates.jsonl` | `cc01356d620dc20e5205fb51d63d5ab5b6660ee420d8afbdc20fca7240105292` |
| `duf-leads-review-001.manifest.json` | `302a85bbc281e8ac042fc4236c172aca096e88943c064b6c393e771c371d3178` |
| `duf-leads-review-001.uniprot_fetch_plan.json` | `a501dfd3764fc0472912cd13f85ff3dd7a873be94bc3b3caed95591cc033f80b` |
| `duf-leads-review-001.uniprot_fetch_receipt.json` | `c887b02da2737faa2de2d1cb12b4aa97f0d676b8303c6d87dca70f7c7a56483a` |
| `duf-leads-review-001.uniprot_registry.jsonl` | `769d73683bdb644f05ab63e833f6ca2152606c344ffbd64b4489ac22b985b840` |
| `duf-leads-review-001.uniprot_memberships.jsonl` | `1b01b776b33d30da4a1e9227a9947003fccc17062d1de54f968146f11f479429` |
| `duf-leads-review-001.registry_blocked.tsv` | `04cd0b604dda621e092f4d743790f5a7d1c05b02f21853adb1ed0ea934abdd15` |
| `duf-leads-review-001.resolved.jsonl` | `ed14eae77e004c9bc7b007c7afc2be8d2deda5d6de1efb77bd92ac3c2e1cc885` |
| `duf-leads-review-001.review.tsv` | `1bc9e707b836926c74d598cf9fc72ed7828db692d60f04ffa7d501dd49629e37` |
| `duf-leads-review-001.protein_registry.jsonl` | `769d73683bdb644f05ab63e833f6ca2152606c344ffbd64b4489ac22b985b840` |
| `duf-leads-review-001.occurrence_evidence.jsonl` | `318f0454fe0f372815ecc606ad96b6f79cd574d76f4a100acc3b8c0ccb596ab6` |
| `data/raw/align_cache/duf-leads/interpro_frame.json` (InterPro 110.0, 360 proteins) | `96fded0d926e9bb14073457217edbb777e07218f7cde68da94187268c3ff28ee` |
| `data/raw/align_cache/duf-leads/interpro_grouped_locations.json` | `eff24b35b6df1a0a8613661a5bc862c4a53494a6683cb807b73b52c5eea5fe2c` |
| `data/raw/align_cache/residue_frame.json` (UniProt 2026_03, 113,695 proteins) | `69edb24bad2535929a6654b53e5d748760552271bf9869b36739504ca1ff81b1` |

The rebuilt residue frame does not reproduce the plan's 2026-09-24 pin
(`4fc4d2fb…`). The sidecar embeds its build date, and its top-up set depends on the
corpus at build time. Byte-pinned consumers such as
`stage_cath_grounding_candidates.py` will therefore not accept it.

## Limits and open questions

- **InterPro agreement is expected, not informative.** UniProtKB's Pfam
  cross-references are derived from InterPro's member-database matches, so a lead
  chosen by `xref:pfam-<id>` will almost always have an exact InterPro match.
  Qualifying through the lane establishes that the protein *carries the family at a
  pinned release*, with source coordinates. It establishes nothing about function,
  and nothing about whether the family defines the protein.
- **Whole-protein scope on multi-domain proteins.** DUFMech notes that large
  multi-domain families surface proteins whose main identity is another domain. A
  `SEQ_FAMILY` record grounded `WHOLE_PROTEIN` on such a protein is technically
  correct under the current contract, but a poor exemplar. Reviewers should prefer
  single-domain carriers, and reject or defer the rest.
- **Arbitrary picks.** Most leads are minimum-annotation-score TrEMBL entries. A
  record whose three leads are all poor should be rejected, not forced to an exemplar.
- **Panel frames are not complete.** The pinned-release residue frame was rebuilt.
  The panel InterPro frame was only canaried, because a full crawl is about 41,600
  proteins. The lane does not need it, but `audit-uniprot-grounding` does.
- **Content gate is InterPro 109.0.** The gate replays the pinned 109.0 XML while
  occurrences come from 110.0. Earlier Pfam batches had the same split.
