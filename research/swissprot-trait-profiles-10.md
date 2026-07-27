---
date: 2026-07-26
issue: "#7 — the residue frame, and an intervention that fails for a structural reason"
prior: swissprot-trait-profiles-9.md
---

# Swiss-Prot trait profiles — Phase 10: feeding the residue frame, and two results that say "no"

Three items: Path 1 (carried since phase 4 and never touched), acting on phase 9's
source-stratification finding, and re-checking phase 6's ortholog-leakage claim on
the broadened matrix.

## 1. Path 1 was starved of coordinates, not of exemplars

`build_sequence_structure_alignment.py` links two records when they share a
`canonical_examples` protein **and overlap on that protein's residue
coordinates**. The carried task was to feed it the exemplars phases 5-9 added.
Those exemplars are there in quantity:

| | |
|---|--:|
| records with `canonical_examples` | 131,773 |
| distinct exemplar proteins | 64,725 |
| **proteins shared by ≥2 records** | **34,227** |
| implied record pairs (upper bound) | 1,560,050 |

But the shared proteins were never the binding constraint. The offline `stored`
provider reads residue coordinates from `canonical_examples[].sequence` and
`[].features`, and the `SWISSPROT_PROFILE` exemplars carry neither — they were
written from `profiles.jsonl`, which has no sequence and no feature table. Across
the whole corpus **33 records have a stored sequence**. Path 1 could not see any
of the 34,227 shared proteins.

So the work was not "re-run the builder" but "give it a coordinate source".

### A sidecar, not inlined data

`scripts/fetch_residue_frame.py` (`just fetch-residue-frame --organisms --apply`)
crawls the ten matrix proteomes once for each entry's sequence and feature table,
routes every FT interval to a `trait_category` with the same mapping
`seed_uniprot.py` uses, and writes
`data/raw/align_cache/residue_frame.json` (gitignored, regenerable).

Keyed by accession rather than inlined into records, because one protein is an
exemplar of up to **574** records — inlining would repeat the same sequence and
feature table hundreds of times and add tens of MB of YAML for data that is
identical every time.

A new `profile` provider in the aligner reads it, localizing a record on each
exemplar by (a) its `sequence_pattern` regex against the sidecar sequence and
(b) sidecar FT intervals whose routed category equals the record's own — exactly
the two mechanisms `stored` uses, sourced differently.

### Two things the first cut got wrong

**The feature parser was keyed off the wrong names.** UniProt's JSON `type` is a
human-readable label (`"Active site"`, `"Disulfide bond"`), not the flat-file FT
keyword (`ACT_SITE`, `DISULFID`) that `seed_uniprot.py` uses. Keying off the
flat-file names silently produced a sidecar with **zero** active sites, binding
sites, modified residues, disulfides or glycosylation — every category Path 1
most needs — while 75% of what it did collect was secondary structure. Caught by
inspecting the interval composition rather than the interval count; the count
alone (377,276) looked like a success.

**Two categories are deliberately not routed**, because a category match would
localize a record *falsely* rather than precisely:

* **Domain** — 12,055 of 30,574 proteins carry more than one, so matching on
  category alone would hand a record every domain of the protein rather than its
  own. The right coordinate source for a domain or family record is the
  `interpro` provider, which knows which signature matched where.
* **Helix / Beta strand / Turn** — tens per protein; matching a `STRUCT_SECONDARY`
  record to all of them localizes nothing meaningful.

### What Path 1 can and cannot reach

Even with a correct sidecar, only **23.2%** of the 131,773 records with exemplars
have a `trait_category` that any routed FT interval can match (or a
`sequence_pattern` to match with). The largest unreachable buckets:

| records | category | why unreachable |
|--:|---|---|
| 34,781 | `SEQ_DOMAIN` | Pfam/InterPro domains — needs `interpro` coordinates |
| 20,000 | `SEQ_EPITOPE` | IEDB epitopes, no UniProt FT counterpart |
| 15,452 | `FUNC_PATHWAY` | GO biological process — not a residue range at all |
| 13,860 | `STRUCT_FOLD` | CATH/ECOD folds — needs SIFTS or TED coordinates |

The `SEQ_DOMAIN` case is worth stating precisely because it looks like a bug and
is not. The repo's "axis follows representation" rule makes a Pfam domain
`SEQ_DOMAIN`, while a UniProt FT `DOMAIN` line routes to `STRUCT_DOMAIN`. A
Pfam record and a UniProt domain interval describing *the same region of the same
protein* therefore never match on category. Relaxing the match would be wrong for
the reason above — ambiguity, not naming. **Path 1's ceiling is set by which
record categories are residue-localizable at all, not by how many exemplars they
share.** That reframes the item that has been carried since phase 4: it was never
one run away from paying off.

### What the provider is worth

Measured on the func-sites overlay, each run a full pass over the 131,773
candidate records:

| providers | records localized | func-site edges |
|---|--:|--:|
| `stored` | 2,254 | 123 |
| `stored,biolip` | 4,507 | 394 |
| **`stored,profile,biolip`** | **6,432** | **773** |
| committed file (`…,interpro,sifts,biolip`) | — | 778 |

**`profile` nearly doubles the yield of the providers that can run offline** —
394 → 773 edges, +96%. That is the deliverable.

### The overlay was deliberately not regenerated

773 is suspiciously close to the committed 778, and that closeness is a trap. The
two sets are not the same edges:

| | edges |
|---|--:|
| in both | 394 |
| **only in the committed file** (InterPro-derived) | **384** |
| only in a `stored,profile,biolip` run | 379 |

Writing the new run would have destroyed 384 real edges to add 379 — a net change
of −5 that looks harmless in a line count and is not. The committed overlay is
left untouched.

Regenerating it properly needs `stored,profile,interpro,sifts,biolip` in one
pass, which would yield an estimated **1,157 edges (+48%)**. The obstacle is
`interpro`: its 18,108 cached URLs cover the *old* exemplar set, and
`located_residues` queries per (signature, protein) pair, so the exemplar growth
of phases 5-9 turns a cached replay into a large uncached crawl. That crawl is
the next phase's work, not a side effect of this one.

## 2. Source residualisation does not work, and the reason is structural

Phase 9 measured the corpus map as strongly source-stratified and left "act on it"
as the follow-up. The obvious action is to residualise: subtract each source's
mean vector so provenance cannot dominate the geometry. Tried, on 40,000 records:

| | axis lift | source lift |
|---|--:|--:|
| original | 2.76× | 9.68× |
| per-source mean-centred | 2.26× (**−18%**) | 7.19× (**−26%**) |

It damages both, and the ratio barely moves (3.51 → 3.18). **The intervention
fails.**

The reason is not a tuning problem. Per-source centering is a *translation*, so it
cannot disturb geometry *within* a source at all — and indeed axis structure
survives there:

| source | records | axes | axis purity | chance | lift |
|---|--:|--:|--:|--:|--:|
| CDD | 6,647 | 2 | 0.963 | 0.527 | **1.83×** |
| NCBIfam | 6,697 | 2 | 0.950 | 0.513 | **1.85×** |

What centering destroys is the *between-source* alignment. And since **25 of the
28 source namespaces emit exactly one axis**, most of the apparent axis structure
in the map is inherited from source: knowing a record is from Pfam already tells
you it is SEQUENCE. Remove the between-source component and you remove most of
what made axis look organised, which is precisely the 2.76× → 2.26× drop.

Two things follow, and they are worth separating:

* **Axis semantics are real** — within CDD and NCBIfam, where a single source
  spans two axes and provenance cannot explain anything, neighbourhoods still sort
  by axis at ~1.85×. The embedding does encode more than which database a record
  came from.
* **No linear correction can un-confound the map**, because the confound is in the
  corpus, not the model. A real fix is corpus-level — more records from different
  sources describing the same trait — or a supervised objective that is told axis
  and source separately.

Recording this as a negative result so the next person does not spend a phase
rediscovering it. The map stays as it is; what changes is that its README-level
claim can now be stated honestly.

## 3. Phase 6's ortholog-leakage claim survives the broader matrix

Phase 6 found that holding out mouse scored the *same* as a random split and
concluded a random split leaks orthologs. That was measured when the matrix was
76% vertebrate — exactly the condition that would produce it artefactually. At 47%
vertebrate:

| split | macro-F1 |
|---|--:|
| random 75/25 | 0.43 |
| held out *Mus musculus* | **0.45** |
| held out *S. cerevisiae* | 0.33 |
| held out *M. jannaschii* | 0.29 |
| held out *A. thaliana* | 0.29 |
| held out *E. coli* | 0.22 |

Mouse still matches — indeed slightly exceeds — a random split, while every
genuinely distant proteome falls far below it. **The claim holds**, and unlike the
phase-8 claim withdrawn last phase, broadening the matrix strengthened rather than
overturned it.

One anomaly worth not over-reading: the archaeon (0.29) scores *above* *E. coli*
(0.22), which a simple phylogenetic-distance story does not predict. Both rest on
17 surviving targets, so the ordering between them is weak; the gap from mouse to
either is the robust part.

## Gate

* The aligner's offline self-test passes with the new provider registered.
* The residue-frame sidecar is gitignored and rebuilt by one recipe; nothing in
  `data/traits/` changed for it.
* Residualisation and within-source measurements are read-only analyses over the
  committed embedding.

## Caveats

* The sidecar covers only the ten matrix proteomes. Exemplars outside them (older
  `CURATOR` / `UNIPROTKB_API` picks from other organisms) get no coordinates from
  it and still depend on `stored` / `interpro`.
* FT coverage is uneven by organism — well-curated human entries carry far more
  intervals than *M. jannaschii* — so Path 1's yield will be biased toward
  the same proteomes everything else in this pipeline is biased toward.

## Next

- **Run the InterPro crawl over the expanded exemplar set and regenerate the
  overlay from all five providers** (~1,157 edges, +48%). This is the one action
  that both banks this phase's 379 new edges and keeps the 384 existing ones.
- Extend the residue frame beyond the matrix proteomes to cover `CURATOR`
  exemplars from other organisms.
- `SEQ_EPITOPE` (20,000 records) has coordinates in IEDB but no UniProt FT
  counterpart; a dedicated localizer would be the single largest unlock after
  InterPro.
