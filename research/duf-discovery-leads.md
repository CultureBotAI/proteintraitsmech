---
topic: Routing DUFMech's UniProt candidates onto Pfam DUF trait records as discovery leads
date: 2026-10-11
status: lane implemented; first review batch resolved, unreviewed, not promoted; follow-ups #1069-#1080 addressed 2026-10-12
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
- commit `217c2cc5cfc2fc43b7196e46fac57ee2a71efe0b`, which must be an ancestor of the
  checkout's local `origin/main` ref. This is DUFMech PR #137, which froze the snapshot.
- `data/worklists/uniprot-duf-example-candidates-2026-10-07.json`, SHA-256
  `0c9e637106357244f3b70f34b14c29e034e9bfdd4fec6b977b5f323174d55cbe`.
- its manifest, SHA-256
  `1004848bc569d67505929c529fcf7e7012537b3053d4c423e22dd7abb84aa45f`. The manifest's
  own byte count, digest, row total and single release (`2026_03`) are also checked.

Every row's shape is validated. A changed byte, a different origin, a commit missing
from the checkout or not under its local `origin/main`, or a duplicated lead fails
closed.

What this guarantees, precisely: the bytes read are exactly the pinned bytes (both
SHA-256 pins, read from git objects), so the input cannot drift. It does **not**
prove that the commit is published on GitHub. `origin/main` is the checkout's local
remote-tracking ref; it is as fresh as the last `git fetch` and can be moved by hand
(the tests do). The ancestry check is an offline consistency check that catches an
unfetched or local-only commit, nothing more. The pinned commit being DUFMech PR #137
is a fact recorded when the pin was chosen, not something the lane re-verifies (#1077). Every candidate row carries this provenance
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

- `NOT_A_TARGET:<status>`
- `NOT_RETURNED_BY_PINNED_UNIPROT`
- `NO_EXACT_INTERPRO_MATCH`
- `MALFORMED_INTERPRO_INTERVAL`
- `INTERPRO_INTERVAL_OUT_OF_BOUNDS`
- `MALFORMED_INTERPRO_GROUPED_LOCATION`
- `INTERPRO_GROUPED_LOCATION_OUT_OF_BOUNDS`: a grouped fragment outside
  `1 <= start <= end <= length`, the same check flat intervals get (#1078)
- `INTERPRO_GROUPED_LOCATION_NOT_IN_FLAT_MATCH`: a grouped fragment that is not one
  of the compact frame's intervals for the same signature. The crawler writes both
  frames from the same fragments, so disagreement means a corrupt or mixed sidecar
- `UNGROUPED_INTERPRO_LOCATIONS`

These are hard errors, not rejections:

- a release mismatch in either provider;
- a planned accession missing from the DUF sidecar. The crawler stores a protein
  without matches as `{}`, so absence means the crawl has not reached it (a canary, a
  failure or an interruption). Finish `fetch-duf-interpro-frame` before staging;
- a compact or grouped sidecar entry that is not a JSON object;
- an audit run with `--no-content-gate`, or a `summary.json` or `discovery-plan.json`
  that does not record the pinned DUFMech snapshot;
- a `leads.jsonl` that changed after discovery (its `leads_sha256` no longer matches).

The lane's InterPro sidecar is separate from the organism-panel frame
(`data/raw/align_cache/interpro_frame.json`). Lead accessions are not panel proteins,
and a partial crawl written into the panel frame would make the ordinary audit read
absence where there was only no crawl. `resolve-duf-review-batch` is the ordinary
resolver with that sidecar bound and both InterPro paths fixed. The resolver records
the sidecar path in each row's provider evidence, so a later promotion can re-check it.
A candidate whose accession is not in the bound frame at all is rejected with
`missing:interpro_frame_entry` (the frame never reached it), distinct from
`missing:exact_interpro_match` (reached, no such signature).

### Reviewing a DUF batch

When a resolved batch carries `duf_lead_provenance`, `.review.tsv` gains six columns
before `reviewer` (#1072). Every other lane's review TSV keeps its usual columns, and
the finalizer carries extra columns through unchanged. None of them is part of the
resolution digest.

| Column | Content |
| --- | --- |
| `duf_lead_status` | the audit status of the lead (`TARGET_ABSENT_FROM_TRAIT` or `TARGET_LEGACY_ON_TRAIT`) |
| `duf_lead_rank` | DUFMech's rank of the lead within its family (1-3) |
| `duf_lead_reviewed` | whether DUFMech saw a Swiss-Prot entry (`true`/`false`) |
| `duf_snapshot` | `<snapshot_id>@<commit>` of the pinned DUFMech snapshot |
| `other_pfam_signatures` | every other `Pfam:` signature the bound InterPro frame places on the protein |
| `multi_domain_whole_protein` | for `WHOLE_PROTEIN` rows: `yes` if `other_pfam_signatures` is non-empty, `no` if empty, `unknown` if the frame has no entry; blank for `LOCALIZED` rows |

`other_pfam_signatures` lists Pfam only. The frame also holds InterPro entries and
other member databases, and those routinely integrate the DUF itself, so they would
read as a second family when there is none.

**Review rule for whole-protein carriers.** A `SEQ_FAMILY` (or
`SEQ_HOMOLOGOUS_SUPERFAMILY`) record is grounded `WHOLE_PROTEIN`: the claim is that the
family describes the protein. On a carrier whose `multi_domain_whole_protein` is `yes`,
that claim is contract-valid but often a poor exemplar, because the protein's identity
may be another domain.

1. Prefer a `no` alternative of the same record over any `yes` one. Approve at most
   one exemplar per record, as the selector already requires.
2. Approve a `yes` row only if no `no` alternative qualified, and only when
   `review_notes` says why the DUF still defines the protein (for example, the DUF
   interval covers most of the sequence and the other signatures are short or
   peripheral). Otherwise mark it `REJECTED` (or leave the record undecided with
   `SKIP`), with the competing signatures named in `review_notes`.
3. `unknown` means the bound frame has no entry for the protein. The resolver will
   already have rejected the row; do not approve it.
4. `LOCALIZED` rows are not affected: their claim is the located interval, not the
   protein's identity.

Lead provenance is context, never evidence. `duf_lead_reviewed = true` or rank 1
makes a row easier to check, not more likely to be correct.

### Bounds

`discover-duf-leads --max-records` (default 100) decides which target records are
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
corpus at build time. Since 2026-10-12 (#1071), byte-pinned frame consumers can also
pin a *content* digest: `python3 scripts/sidecar.py content-sha256 <frame>` hashes
the canonical JSON without the volatile `_meta` keys (`built`, `completeness`, and
the interim top-level `complete`/`targets` marker).
`stage_cath_grounding_candidates.py` keeps the `4fc4d2fb…` byte pin and also accepts
the rebuilt frame's content digest
`a640a2ea9f8d1f6a552f583531c50e2d98a38642534a2c028aea96878886dcc2`.

What this guarantees: a rebuild at the same release with an identical payload binds
whatever day it was built. A rebuild whose top-up differs, or any other change in
sequences, features, release or absent list, still fails closed. So does a frame
that lacks a sequence the CATH stage consumes, through the stage's own count
contract and per-observation checks. A new frame needs a new, reviewed content pin.
The original `4fc4d2fb…` bytes were not retained, so its content digest is unknown.
The rebuilt `69edb24b…` bytes are retained outside the repository with this batch's
other artifacts. The production CATH stage was not re-run against the rebuilt frame:
it also needs the 2026-09-24 panel InterPro frame (`bc2d66…`), which was not
available to this change.

## Limits and open questions

- **InterPro agreement is expected, not informative.** UniProtKB's Pfam
  cross-references are derived from InterPro's member-database matches, so a lead
  chosen by `xref:pfam-<id>` will almost always have an exact InterPro match.
  Qualifying through the lane establishes that the protein *carries the family at a
  pinned release*, with source coordinates. It establishes nothing about function,
  and nothing about whether the family defines the protein.
- **Whole-protein scope on multi-domain proteins.** Handled by the review rule in
  [Reviewing a DUF batch](#reviewing-a-duf-batch): the TSV flags each multi-domain
  whole-protein carrier, and the rule decides it. The flag is not enforced in code.
- **Arbitrary picks.** Most leads are minimum-annotation-score TrEMBL entries. A
  record whose three leads are all poor should be rejected, not forced to an exemplar.
- **Panel frames are not complete.** The pinned-release residue frame was rebuilt.
  The panel InterPro frame was only canaried, because a full crawl is about 41,600
  proteins. The lane does not need it, but `audit-uniprot-grounding` does. Since
  2026-10-12 (#1070) every InterPro frame write records `_meta.completeness`, which
  is `complete: true` only when every target is in both the compact and grouped
  frames. `audit-uniprot-grounding` refuses a frame that is not stamped complete
  *for the organism-panel target set* (`target_set: organism-panel-exemplars`),
  including any frame written before the marker existed and any frame stamped for an
  accession list, such as a DUF sidecar (#1097). PR #1095 briefly wrote a simpler
  top-level `_meta.complete`/`_meta.targets` marker. It records a count but no target
  set, so the audit treats such a frame as unstamped and refuses it until it is
  certified. Certification drops those keys and adds the `completeness` stamp. A
  residue frame stamped incomplete (`completeness.complete` false, or the interim
  `complete: false`) is also refused. An unstamped residue frame is accepted,
  because a protein missing from it is reported as missing and never read as a
  negative. A `--top-up` run without queries carries the extended frame's stamp
  forward and leaves an unstamped frame unstamped (#1108). When the grouped frame's path
  exists, it must carry the same stamp (target set, count, `targets_sha256`); when it
  does not exist, the audit skips it, which only leaves multi-location localized
  matches ungrouped (#1102). The audit also re-derives the panel targets from
  `--traits` and prints a WARNING, not a refusal, if their digest differs from the
  stamp: proteins added to the corpus since the crawl were not crawled.
  `--allow-incomplete-interpro-frame` overrides the refusal for diagnostics and marks
  each `NO_LOCAL_EXACT_TRAIT_MATCH` as uninformative.

  "Complete" is narrow. The panel target set is the exemplar proteins that carry a
  member-database record and records of two or more trait categories
  (`fetch_interpro_frame.target_proteins`). A complete frame says each of those
  proteins was crawled. It says nothing about carriers outside that set, so
  `NO_LOCAL_EXACT_TRAIT_MATCH` still means "no match among the panel targets", not
  "no carrier exists". A finished crawl from an older
  script is stamped offline with `just certify-interpro-frame --apply`: it
  re-derives the target set from `data/traits`, checks coverage of both frames, and
  only then stamps `basis: offline-certification`. It certifies the panel only:
  `--accessions` is refused by the recipe, and by the script whenever the output is
  the panel frame path. The DUF sidecar is certified with
  `just fetch-duf-interpro-frame --certify`. Certification leaves the payload and
  `built` unchanged, so neither the content digest nor any provider evidence changes.
  The bytes do change, though. `stage_cath_grounding_candidates.py` byte-pins the
  2026-09-24 panel frame `bc2d66…`, and has no content pin for it, because those bytes
  were not retained and could not be found on this machine. So a certified (or
  re-crawled) panel frame is refused by the CATH stage, with an error that says so,
  until a reviewed byte or content pin is added (#1098). If `data/traits` changed after the crawl started, the new targets show up
  as missing, and resuming the crawl fetches only those. The resolver needs no
  global marker: it checks each candidate's own accession (see above).

  To certify a crawl that finished in another checkout with the pre-marker script,
  run the updated script from a checkout that has this change, and point it at that
  crawl's frames and at the trait tree the crawl's targets came from. Dry run first,
  then stamp:

  ```bash
  CRAWL=../ProteinTraitsMech-interpro-crawl
  just certify-interpro-frame \
    --out "$CRAWL/data/raw/align_cache/interpro_frame.json" \
    --grouped-out "$CRAWL/data/raw/align_cache/interpro_grouped_locations.json" \
    --traits "$CRAWL/data/traits"
  # exit 0 and "covers its target set" -> re-run with --apply; exit 1 lists missing targets
  ```

  The target scan reads the whole trait tree and takes about two minutes. On a copy of
  the 1-protein canary frame it refused, as it should: 1 of 41,601 targets present.
- **Content gate is InterPro 109.0.** The gate replays the pinned 109.0 XML while
  occurrences come from 110.0. Earlier Pfam batches had the same split.
