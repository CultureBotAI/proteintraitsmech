# Equivalence & Containment Cutoffs — SEQUENCE axis

**Scope.** How to decide, for the SEQUENCE axis, (1) when two sequence traits are the
**SAME** (equivalence → `biolink:close_match`, or `same_as`/R1/R2 for definitional identity)
and (2) when one is **CONTAINED IN / NARROWER THAN** another (subsumption → `subclass_of`,
`narrow_match`, `part_of`/`has_part`, `member_of`). Operators in scope, per
[`.claude/skills/merge-within-axis`](../.claude/skills/merge-within-axis/reference/axis-operators.md):

- **Signature families:** `SEQ_DOMAIN`, `SEQ_FAMILY`, `SEQ_HOMOLOGOUS_SUPERFAMILY`, `SEQ_MOTIF`, `SEQ_CONSERVATION`
- **Localized features:** `SEQ_REPEAT`, `SEQ_PTM_SITE`, `SEQ_MODIFIED_RESIDUE`, `SEQ_GLYCOSYLATION_SITE`, `SEQ_CROSSLINK_SITE`

Decision rule from the skill: **only `same_as` / R1 (identical `identifier`) / R2 (byte-identical
`sequence_pattern`) auto-merge. `close_match` is a review candidate the axis operator must confirm
with a second signal. Everything narrower (`narrow_match`, `part_of`, `member_of`) is a relation,
never a merge.**

---

## (a) Cutoffs table — when two SEQUENCE traits are the SAME

| Operator / category | Equivalence rule + numeric cutoff | Primary source |
|---|---|---|
| **Sequence-identity zones** (background theory; governs whether ID-based equivalence is even safe) | Long alignments: **>40% identity** → same structure/family, unambiguous "safe zone". **Twilight zone = 20–35% identity** — signal is blurred, identity alone cannot call homology. Above **~30%**, 90% of pairs are homologous; below **25%**, <10% are. In the twilight zone >95% of detected pairs had *different* structures. Threshold is **length-dependent** (per-residue curve), not a flat number. | Rost 1999, *Twilight zone of protein sequence alignments*, Protein Eng 12(2):85–94. [PubMed 10195279](https://pubmed.ncbi.nlm.nih.gov/10195279/) · [full text](https://www.rostlab.org/papers/1999_twilight/paper.html) |
| **`SEQ_FAMILY` / `SEQ_DOMAIN` membership (Pfam)** | A sequence is a family member iff its HMMER **bit score ≥ the family's curated gathering threshold (GA)**, set by hand per family. Two per-family cutoffs exist: a **sequence GA** and a **domain GA**. **TC** = score of the lowest true member above GA; **NC** = highest scoring non-member below GA. Bit scores (not E-values) are used because they are DB-size-independent. → Two records that resolve to the **same Pfam accession** are the same signature trait. | Pfam Documentation, *Pfam scores*. [pfam-docs scores](https://pfam-docs.readthedocs.io/en/latest/scores.html) · [glossary](https://pfam-docs.readthedocs.io/en/latest/glossary.html) |
| **Cross-source signature equivalence (`SEQ_*` families, Phase 1)** | Signatures from different member DBs (Pfam / PROSITE / SMART / CDD / PRINTS / NCBIFAM) that **describe the same biological entity are integrated into one InterPro entry**. Membership in the same InterPro accession is the deterministic cross-source "SAME" signal. Example: CUB domain — cd00041 (CDD), PS01180 (PROSITE), PF00431 (Pfam), SM00042 (SMART) → **IPR000859**. Integration is **manual curation** (matches vs latest UniProtKB, false-positive removal), not a single numeric cutoff. | InterPro 2025, *NAR* 53(D1):D444. [NAR](https://academic.oup.com/nar/article/53/D1/D444/7905301) · [PMC11701551](https://pmc.ncbi.nlm.nih.gov/articles/PMC11701551/) |
| **Related-but-not-same families (Pfam clan / SCOOP)** — *review, not merge* | Clan membership = families from a common ancestor, linked by **all-against-all profile–profile comparison**; an edge is drawn at a "significant" profile–profile score. SCOOP (shared-hit overlap): **score >30 → 95% of relationships true; >60 → 99%; >100 → very reliable.** These call *relatedness* (clan), **not identity** — same clan ≠ same family. | SCOOP: Bateman & Finn, *BMC Bioinformatics* 2007. [PMC2603044](https://pmc.ncbi.nlm.nih.gov/articles/PMC2603044/) · Pfam clans: [NAR 34:D247](https://academic.oup.com/nar/article/34/suppl_1/D247/1133922) |
| **Profile–profile / HMM–HMM homology (deep equivalence below twilight zone)** | HHsearch/HHpred **probability ≥ 95% → homology "nearly certain"**. Practical rule: take a hit seriously if **prob >50%**, or **prob >30% and among top-3 hits**. Probability preferred over E-value (folds in secondary structure); at **E-value <1**, matches become marginally significant. Use to *propose* equivalence for divergent signatures; still a `close_match` candidate needing a second signal. | HH-suite wiki. [hh-suite wiki](https://github.com/soedinglab/hh-suite/wiki) · HHpred server: [PMC1160169](https://pmc.ncbi.nlm.nih.gov/articles/PMC1160169/) |
| **Localized-feature same-region overlap** (`SEQ_MOTIF`, `SEQ_CONSERVATION`, `SEQ_REPEAT`, `SEQ_PTM_SITE`, `SEQ_MODIFIED_RESIDUE`, `SEQ_GLYCOSYLATION_SITE`, `SEQ_CROSSLINK_SITE`) | Two features are the "same region" only under **≥50% reciprocal overlap (RO)**: each interval must cover **≥50%** of the other (bedtools `intersect -f 0.5 -r`). Point features (single-residue PTM/modified-residue/crosslink) require **exact residue coincidence** (identical position on the same protein), not RO. Member-set **Jaccard** may *nominate* a candidate but is **never sufficient** — see trap below. | 50% RO convention: [bedtools intersect](https://bedtools.readthedocs.io/en/latest/content/tools/intersect.html) · CNV RO usage [PMC4021055](https://pmc.ncbi.nlm.nih.gov/articles/PMC4021055/) |
| **The localized-feature trap (why member-Jaccard alone is UNSAFE)** | High member-set Jaccard (two records over the *same proteins*) does **not** imply same trait: the two records can annotate **different residues** of those proteins (e.g. a phospho-site vs a glyco-site on the same kinase). **Mandatory Tier-2 confirmation:** promote a member-overlap hit only after `verify_region_overlap.py` confirms same-region (≥50% RO) or same-residue coincidence. | merge-within-axis skill, trap catalogue #1 (`reference/axis-operators.md`) |

---

## (b) Relationships table — CONTAINMENT / SUBSUMPTION

Direction convention: **A → B** reads "A is contained in / narrower than B" (A is the child/part/member).

| Containment case | Direction (child → parent) | Biolink / RO predicate | Source |
|---|---|---|---|
| InterPro entry that matches a **subset** of a parent entry's proteins | specific entry → broader entry | **`biolink:subclass_of`** (also `biolink:narrow_match` for the mapping edge) | InterPro parent/child hierarchy: [entries_info](https://interpro-documentation.readthedocs.io/en/latest/entries_info.html) |
| InterPro **functional subfamily** ⊂ family; **structural/functional subclass of a domain** ⊂ domain | subfamily/subclass → family/domain | **`biolink:subclass_of`** / `narrow_match` | [InterPro entry types](https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/what-is-an-interpro-entry/interpro-entry-types/) |
| Homologous-superfamily entry **overlaps** a family/domain entry (auto, by Jaccard + containment index) | narrower set → broader set (per containment index direction) | `biolink:narrow_match` / `broad_match`; `related_to` when only Jaccard-overlapping | [Overlapping homologous superfamilies](https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/what-is-an-interpro-entry/overlapping-homologous-superfamilies/) |
| A short **`SEQ_MOTIF`/site contained within a `SEQ_DOMAIN`** (region of the motif ⊂ region of the domain) | motif → domain | **`BFO:0000050` `part_of`** (inverse `has_part` on the domain); RO `RO:0002131` *overlaps* if only partial | InterPro entry types (site vs domain); RO/BFO partonomy |
| A **PROSITE pattern** as a subset of a **PROSITE/other profile** covering the same signature | pattern → profile | `biolink:narrow_match` (pattern is a narrower, more specific realization) | InterPro integration example (CUB): pattern PS01180 ⊂ entry with profile [IPR000859](https://academic.oup.com/nar/article/53/D1/D444/7905301) |
| A single **`SEQ_DOMAIN`** as a constituent of a larger **multi-domain `SEQ_FAMILY`** | domain → multi-domain family | `BFO:0000050` `part_of` (`has_part` inverse) — **partonomy, not subclass** | InterPro family-vs-domain modelling [entry types](https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/what-is-an-interpro-entry/interpro-entry-types/) |
| A **`SEQ_REPEAT` unit within a repeat region** (one period ⊂ the tandem array) | unit → region | `BFO:0000050` `part_of` (`has_part`) | InterPro "repeat" entry type [entry types](https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/what-is-an-interpro-entry/interpro-entry-types/) |
| A **protein instance's feature is a member of** a trait class (e.g. UniProt site ∈ signature family) | instance → class | **`biolink:member_of`** (never merge) | merge-within-axis tier table; RO `RO:0002350` *member of* |
| Two **Pfam families in the same clan** (common ancestor, not nested) | sibling ↔ sibling | `biolink:related_to` (or `member_of` the clan); **not** subclass | Pfam clans [NAR 34:D247](https://academic.oup.com/nar/article/34/suppl_1/D247/1133922) |

**When RO (not Biolink) is needed.** Biolink has clean predicates for `subclass_of`, `part_of`/`has_part`,
`member_of`, and the SKOS-derived mapping set (`exact/close/narrow/broad/related_match`). Reach for **RO**
for finer partonomy/overlap semantics Biolink does not distinguish — `RO:0002131` *overlaps*,
`RO:0002093` *directly overlaps*, `RO:0002350` *member of* (vs `RO:0002351` *has member*) — and use
**BFO:0000050 `part_of`** as the canonical parthood IRI backing `biolink:part_of`. Biolink mapping
predicates trace to SKOS (`skos:closeMatch`, `skos:narrowMatch`, `skos:exactMatch`).
Source: [Biolink Model paper](https://arxiv.org/pdf/2203.13906), [biolink:exact_match](https://biolink.github.io/biolink-model/docs/exact_match.html),
[SSSOM mapping predicates](https://mapping-commons.github.io/sssom/mapping-predicates/).

---

## (c) Verification log

Each numeric cutoff → the primary source that states it; unverifiable ones flagged **UNVERIFIED**.

| Cutoff | Value | Verified against primary source? |
|---|---|---|
| Twilight zone identity band | **20–35%** | **VERIFIED** — Rost 1999 abstract/text, [PubMed 10195279](https://pubmed.ncbi.nlm.nih.gov/10195279/) |
| "Safe zone" identity for long alignments | **>40%** | **VERIFIED** — Rost 1999, [full text](https://www.rostlab.org/papers/1999_twilight/paper.html) |
| Above ~30% → 90% homologous; below 25% → <10% | **30% / 25%** | **VERIFIED** — Rost 1999 abstract |
| Twilight-zone false-positive rate | **>95% different structure** | **VERIFIED** — Rost 1999 abstract |
| Identity threshold is length-dependent (curve, not flat) | qualitative | **VERIFIED** — Rost 1999 (per-residue HSSP-curve formulation) |
| Pfam membership = bit score ≥ GA; TC/NC definitions; separate sequence & domain GA | GA/TC/NC | **VERIFIED** — [pfam-docs scores](https://pfam-docs.readthedocs.io/en/latest/scores.html) (verbatim quotes captured) |
| InterPro integration = manual, "same biological entity → one entry" (CUB → IPR000859) | qualitative | **VERIFIED** — [InterPro 2025 NAR](https://academic.oup.com/nar/article/53/D1/D444/7905301) / [PMC11701551](https://pmc.ncbi.nlm.nih.gov/articles/PMC11701551/) |
| InterPro overlap/hierarchy uses **Jaccard + containment index** | qualitative | **VERIFIED (method named)** — [Overlapping homologous superfamilies](https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/what-is-an-interpro-entry/overlapping-homologous-superfamilies/) |
| InterPro Jaccard / containment **numeric thresholds** | (specific %) | **UNVERIFIED** — no public InterPro doc/paper states the numeric cutoffs; the indexes are named but their trigger values are not published in the sources found. Do not hard-code a number; treat InterPro's own parent/child + overlap assignments as authoritative rather than recomputing. |
| HHsearch/HHpred "nearly certain" homology | **prob ≥ 95%** | **VERIFIED** — [HH-suite wiki](https://github.com/soedinglab/hh-suite/wiki) |
| HHpred practical rules | **>50%**, or **>30% & top-3** | **VERIFIED** — HH-suite wiki |
| HHsearch E-value marginal significance | **E < 1** | **VERIFIED** — HH-suite wiki |
| SCOOP reliability | **>30 → 95% true; >60 → 99%; >100 reliable** | **VERIFIED** — [SCOOP, PMC2603044](https://pmc.ncbi.nlm.nih.gov/articles/PMC2603044/) |
| Localized-feature same-region overlap | **≥50% reciprocal overlap** | **PARTIALLY VERIFIED** — the 50% RO convention is a **genomics-interval** standard ([bedtools](https://bedtools.readthedocs.io/en/latest/content/tools/intersect.html), CNV lit [PMC4021055](https://pmc.ncbi.nlm.nih.gov/articles/PMC4021055/)); there is **no protein-feature-specific standard** mandating exactly 50%. Adopt 50% RO as the project convention, and require **exact-residue coincidence** for point PTM/crosslink features. **Flag: the 50% value is convention-borrowed, not a protein-domain primary standard — UNVERIFIED for proteins specifically.** |
| Member-set Jaccard as identity | — | **VERIFIED UNSAFE** — localized-feature trap (skill `reference/axis-operators.md` #1); use only to *nominate*, confirm with region/residue overlap. |
| Biolink close/narrow/exact_match ← SKOS | qualitative | **VERIFIED** — [Biolink paper](https://arxiv.org/pdf/2203.13906), [SSSOM predicates](https://mapping-commons.github.io/sssom/mapping-predicates/) |

### Adversarial notes
- **Rost's "30%" is not a flat cutoff.** The paper's real contribution is a length-dependent
  curve; single-number quotes (30%, 25%, 40%) are convenient summaries of that curve at long-alignment
  regimes. Do not apply a flat % identity to short motifs/sites — use the family/InterPro operator instead.
- **Pfam GA is per-family and hand-curated**, so there is no global bit-score cutoff to hard-code;
  the deterministic equivalence signal is *same Pfam/InterPro accession*, not a recomputed score.
- **InterPro integration is manual**, so cross-source "SAME" is authoritative-by-curation, not by a
  reproducible numeric threshold — the right project move is to trust InterPro's member2entry mapping
  (Phase 1 `build_equivalence.py`) rather than reinvent an overlap cutoff.
- **50% RO is imported from genomics**; it is a reasonable default but should be documented as a
  project convention, and point features must use exact-residue equality, not RO.
</content>
</invoke>
