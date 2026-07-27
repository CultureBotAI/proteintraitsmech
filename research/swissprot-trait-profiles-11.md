---
date: 2026-07-27
issue: "#7 — finishing the residue frame"
prior: swissprot-trait-profiles-10.md
---

# Swiss-Prot trait profiles — Phase 11: the InterPro frame, and three items that were one

Phase 10 built a residue-frame sidecar that took Path 1's offline yield from 394
to 768 edges, and left three follow-ups: crawl InterPro for domain/family
coordinates, extend the frame to exemplars outside the ten proteomes, and write
an IEDB localizer for the 20,000 epitope records. The second and third turned out
to be the same job, and the first turned out to be a different job than it looked.

## 1. The InterPro crawl was the wrong shape, not just expensive

Phase 10 estimated the crawl as the obstacle. It was — but because of how it was
being asked, not how much there was to ask.

The aligner's existing `interpro` provider queries one URL per **(signature,
protein)** pair. Over the exemplar set phases 5-9 produced that is **104,176
calls**, and the 18,108 URLs already cached cover only the old, smaller set. Two
observations shrink it:

* InterPro's `entry/all/protein/uniprot/{acc}/?page_size=200` returns **every**
  member-DB match on a protein, with coordinates, in one request. Per protein
  rather than per pair: 104,176 → 38,357.
* A residue-frame edge needs two *comparable* records localized on one protein. A
  protein hosting records of only one trait category can never supply that pair,
  so fetching it is pure cost: 38,357 → **15,120**.

That is a **6.9× reduction**, and it is arithmetic on the corpus rather than a
faster network.

Then measurement corrected the plan again. Serial latency is **1.04 s/protein**,
so 15,120 proteins is ~5 hours, not the ~75 minutes projected from an assumed
0.3 s. Six concurrent workers bring it under an hour at ~5 req/s. The crawl
checkpoints every 500 and resumes from the sidecar, so switching strategy
mid-run cost nothing.

`scripts/fetch_interpro_frame.py` (`just fetch-interpro-frame --apply`) →
`data/raw/align_cache/interpro_frame.json`, `{ACC: {CURIE: [[start, end], …]}}`.
A new `interpro_frame` provider in the aligner reads it. Unlike the residue frame
— which matches a record to intervals of its own *category* — this matches a
record to the interval of its own *signature*, so a domain record lands exactly
where that signature hit rather than anywhere a domain sits. That is why phase 10
could not route UniProt `DOMAIN` intervals and this can.

**A bug caught before the crawl ran:** InterPro reports CATH-Gene3D as
`G3DSA:1.10.510.10`, while the corpus keys on the bare `CATH:1.10.510.10`. Every
CATH lookup would have silently missed. Verified after fixing: all six prefixes
the corpus actually contains (CATH, CDD, InterPro, NCBIfam, PROSITE, Pfam) match
real record identifiers 100%.

## 2. Items 2 and 3 were one job

The queued list had "extend the frame to `CURATOR` exemplars" and "an IEDB
localizer for the 20,000 `SEQ_EPITOPE` records" as separate work. Looking at an
epitope record makes them collapse:

```yaml
identifier: IEDB:220613
sequence_pattern: VDESNLQRQIIHGTS         # the peptide, already here
canonical_examples:
  - protein_id: UniProtKB:L7N674          # the source antigen
    source: CURATOR
```

The peptide is already the record's `sequence_pattern` and the antigen is already
its exemplar. No localizer is needed — the existing regex path localizes an
epitope exactly, given the antigen's **sequence**. What was missing was the
sequence, because the antigen lies outside the ten matrix proteomes.

**19,371 epitope records were blocked by 4,324 missing antigens**, inside 19,711
missing exemplar proteins overall. Fetched with UniProt's
`/uniprotkb/accessions` endpoint at 100 accessions per request — ~200 requests
for 19,711 proteins, rather than a proteome crawl.

| | proteins in the residue frame |
|---|--:|
| phase 10 (ten proteomes) | 80,066 |
| **+ corpus top-up** | **98,922** |

## What it is worth

| stage | records localized | func-site edges | base-alignment edges |
|---|--:|--:|--:|
| phase 10 end | 6,424 | 768 | **0** |
| + corpus top-up | 21,585 | 965 | 0 |
| **+ InterPro frame** | **61,015** | **6,982** | **12,424** |

Two results, and the second is the larger one.

`seq_struct_func_sites.tsv` grows **778 → 6,982 edges (9×)**, a clean superset:
all 778 committed edges retained, none lost.

`seq_struct_alignment.tsv` — the **base** signature↔fold overlay — goes from
**empty to 12,424 edges**. It has been an empty file since it was created,
because relating a sequence signature to a structural fold on a shared protein
requires knowing *which* signature matched *where*, and nothing in the corpus
carried that. Its predicate mix is the interesting part:

| predicate | edges | meaning |
|---|--:|---|
| `biolink:part_of` | 7,615 | one region wholly inside the other |
| `biolink:overlaps` | 3,062 | partial overlap |
| `biolink:related_to` | **1,747** | **identical residue set** |

Those 1,747 are the cross-axis link this knowledge base exists to express: the
same physical stretch of protein, described once as a sequence signature and once
as a structural fold, now asserted as such from residue coordinates rather than
inferred from shared groundings.

Localization grows faster than edges throughout, because an edge needs two
*comparable* records on one protein — two epitopes on the same antigen are
same-axis, same-category, and the aligner correctly refuses to relate them.

## 3. A regex that skipped 27,325 records

Verifying the rebuilt overlay against the committed one turned up 226 edges the
new run could not reproduce. They were not stale: both endpoints still cited the
shared protein. The InterPro sidecar simply had no entry for it, because
`target_proteins()` had never asked for it.

The scanner matched exemplars with `^\s+-\s+protein_id:` — at least one leading
space. `fetch_uniprot_examples.py` writes its blocks through PyYAML, which emits
list items at **column 0**:

```yaml
canonical_examples:
- protein_id: UniProtKB:P13835      # no indent — invisible to `\s+`
  protein_label: Avirulence protein B
```

**27,325 records** — every `UNIPROTKB_API` exemplar block in the corpus — were
skipped by every regex-based scan I wrote this phase and last. The aligner itself
was never affected: it parses with PyYAML. Only the crawl-target selectors were,
which is why the sidecar had holes rather than the overlay having wrong edges.

Corrected figures, against what phase 10 reported:

| | phase 10 report | corrected |
|---|--:|--:|
| distinct exemplar proteins | 64,725 | **93,150** |
| shared by ≥2 records | 34,227 | **40,183** |
| InterPro crawl targets | 15,120 | **27,498** |

The phase-10 numbers understated the corpus by ~30%. The conclusions drawn from
them do not change — Path 1 was still starved of coordinates, and the sidecar
still fixed that — but the scale was larger than reported.

Two smaller measurement lessons from the same verification:

* 23 of the 226 "lost" edges were not lost at all, only re-oriented
  (subject/object swapped). The overlay is loaded bidirectionally, so this is
  semantically irrelevant — but a directed set comparison reports it as loss plus
  addition, and I nearly acted on that.
* A first attempt to test "do both records still cite this protein?" searched the
  whole file text, so it matched `xrefs` entries as well as exemplars and
  answered "yes, all 203" when the truth was the opposite. Scoping the check to
  the `canonical_examples` block reversed the answer.

## 4. Nine exemplars are not UniProt accessions

The batch fetcher rejected an entire 100-accession request, which is how these
announced themselves: nine `protein_id` values across the MetalPDB records are
`UNS…` placeholders — PDB chains with no UniProt mapping — emitted with a
`UniProtKB:` prefix. They sit beside genuine accessions in the same block.

They pass `just validate-all` because the schema pattern is
`^UniProtKB:[A-Z0-9]+([-][0-9]+)?$`, which any alphanumeric string satisfies;
UniProt's real accession syntax is far narrower. Filed as **#54** with both parts
of the fix (tighten the pattern; decide what the seeder should emit for a chain
with no UniProt mapping — most likely nothing).

Two consequences for the tooling, both fixed here:

* **Batch atomicity.** UniProt rejects the whole request if any accession in it
  is bad, so a flat retry discarded 99 good proteins to lose 1. The fetcher now
  splits a failed batch recursively, isolating the offender in ~7 extra requests.
* **A wrong guard of my own.** Phase 10's partial-write guard (#53) treated "this
  accession does not exist" as "the network failed" and refused to write. Those
  are different facts and only the second should block a write; unfetchable
  accessions are now reported as corpus data errors and do not block.

## Gate

* Aligner self-test passes with both new providers registered.
* All six corpus-present InterPro prefixes verified against real record
  identifiers after the G3DSA fix.
* The committed overlay is not written until a combined run is confirmed a
  superset — the phase-10 discipline, for the same reason.

## Caveats

* The InterPro crawl covers the 15,120 edge-capable proteins, not all 38,357
  exemplar proteins. A record on a single-category protein stays unlocalized;
  that is correct for edge-building but means the sidecar is not a general
  coordinate source.
* `--top-up` performs network fetches during a dry run, matching the existing
  fetchers' behaviour (they always fetched and gated only the write). Consistent,
  but "dry run" ought to mean "no network" across all of them.
