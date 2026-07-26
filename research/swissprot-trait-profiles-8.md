---
date: 2026-07-25
issue: "#7 — the other half of the matrix, and a verdict on localization edges"
prior: swissprot-trait-profiles-7.md
---

# Swiss-Prot trait profiles — Phase 8: the protein map, and keeping the localization edges

Two items carried from earlier phases: the protein × trait browser map, open since
phase 4, and the hand-review of `trait-implies-localization` edges that phase 7
made possible by separating them.

## 1. The protein map

`just protein-map` → `docs/data/protein_map.json`, rendered by a new **Proteins**
tab on `docs/map.html`. One point per Swiss-Prot protein (47,768 with ≥1 corpus
trait), positioned by which corpus traits it carries, coloured by organism and
filterable by CATH structural class.

Pipeline: binary protein × trait incidence (25,345 traits with ≥5 carriers;
921,364 nonzero, 0.076% dense) → TruncatedSVD to 50 dims → PaCMAP to 2-D, the
same primary projection the corpus map uses. ~15s end to end.

The corpus map plots trait *classes*; this plots the *proteins*, which is what
makes the following question askable.

### Does the map show organisms or biology?

Phases 6-7 repeatedly caught parts of this pipeline tracking proteome membership
and curation practice rather than mechanism. So the map should not be eyeballed —
it should be measured. Neighbour purity at k=25, against the purity expected from
label proportions alone:

| space | organism purity | CATH-class purity |
|---|--:|--:|
| 50-d SVD (**pre-projection**) | 0.470 (chance 0.331) → **1.42×** | 0.584 (chance 0.255) → **2.29×** |
| 2-d PaCMAP (what is rendered) | 0.450 → 1.36× | 0.532 → 2.09× |

**Structural class organises the space about 1.6× more strongly than organism
does.** Proteins group by what they are built like more than by which proteome
they came from — the trait profiles carry structure that survives the species
boundary. Organism signal is real (1.42× is not nothing) but secondary.

The second row is the guard against over-reading a 2-D scatter: PaCMAP *understates*
both purities relative to the space it was computed from (2.29 → 2.09, 1.42 → 1.36).
The projection loses neighbour structure, as projections do; it does not
manufacture it, and it does not reorder the two effects. Anyone quoting the
picture should quote the 50-d numbers.

`docs/map.html` was generalised rather than duplicated: a map file may now carry
`colors`, `link`, `group_label`, `cat_label`, `unit` and `id_strip_prefix`, and
the two corpus maps — which omit all of them — keep their trait-axis palette and
`browse.html` click-through unchanged. Protein points link out to UniProtKB.

## 2. Verdict on the localization edges: keep them

Phase 7 left an open question — phase 6 showed `trait-implies-function` rules
failing on cellular-component terms, so should the 65 `trait-implies-localization`
edges be in the overlay at all? Reviewed by hand; the answer is **yes, keep all
65**, and the reasoning matters more than the count.

**The edges phase 6 caught are already gone.** Its worst offenders
(`PROSITE:PS00657 → GO:0000785` at 0.03 held-out, `Pfam:PF01825 → GO:0016020` at
0.23) were mined on human alone and do not survive pooled mining — phase 7 showed
this. What is left is a different population: 61 of 65 sit at conf ≥0.95 with
balanced confidence to match.

**What survived is domain → compartment, where the compartment follows from the
domain.** The commonest consequents are extracellular matrix (11), cell surface
(7), chromatin (6), connexin complex (4), microtubule (3). Spot-checks:
`Pfam:PF03953` (tubulin C-terminal) → microtubule; connexin domains → connexin
complex; T-box/histone-fold domains → chromatin. These are not annotation drift —
the localisation is a consequence of what the domain *is*.

**"Backed by one proteome" is not the same as "unreliable".** Four edges have
`organisms=1`, and every one is lineage-specific by biology, not by sampling:

| edge | only organism | why |
|---|---|---|
| `CATH:2.60.40.1090 → GO:0009289` (pilus) | *E. coli* | pili are bacterial |
| `PROSITE:PS00724 → GO:0009277` (fungal cell wall) | yeast | fungal-specific |
| `Pfam:PF00660 → GO:0009277` | yeast | Seripauperin/TIP1 is a yeast cell-wall family |
| `Pfam:PF13885 → GO:0045095` (keratin filament) | vertebrate | keratins are vertebrate |

A pilus edge *cannot* be backed by more than one organism in a matrix with one
bacterium. The `organisms=` field phase 7 added distinguishes "narrow because the
biology is narrow" from "narrow because the matrix is narrow" only with a human
reading it — worth recording, because an automatic filter on `organisms>=2` would
have deleted four correct edges.

## Gate

* Map JSON checked against the page's contract: 5-element points, coordinates in
  [0,1], group and category indices in range.
* `docs/map.html` inline JS parses; corpus-map behaviour is unchanged (the new
  fields are absent from those files and every use is a fallback).
* Fixed a latent crash in two scripts: `outp.relative_to(REPO_ROOT)` raises for an
  `--out` / `--emit-overlay` path outside the repo. It never fired in CI because
  both are normally written inside the repo, and it was masked here by a
  `>/dev/null` in phase 7's scratch runs.

## Caveats

* Neighbour purity is one summary statistic. It says the space is more organised
  by fold class than by organism; it does not say the map has no organism
  artefacts, and clusters should not be read as claims without checking members.
* CATH class is available for 36,475 of 47,768 proteins; the remaining 11,293
  ("No CATH fold assigned") form their own category and are included in the
  chance baseline, which makes the CATH purity figure conservative.
* The matrix is still four organisms — the standing limitation since phase 6.

## Next

- Broaden the matrix beyond four organisms (no archaea, plants, parasites) — the
  longest-standing open item, now blocking little else.
- Feed shared `canonical_examples` proteins into the residue-frame base overlay
  (Path 1), open since phase 4.
- Consider a trait-side companion to the purity measurement: do trait *classes*
  cluster by axis more than by source database? The corpus map has never been
  measured the way this one now is.
