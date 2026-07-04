# Trait EQUIVALENCE and CONTAINMENT for the STRUCTURE axis — numeric cutoffs and subsumption

**Scope.** Defines, with primary-source citations, when two STRUCTURE-axis
`ProteinTraitRecord`s are the *same* trait (equivalence) and when one is
*contained in* another (containment/subsumption). Covers the operators named in
`.claude/skills/merge-within-axis/` for STRUCTURE:
`STRUCT_FOLD`, `STRUCT_TOPOLOGY`, `STRUCT_HOMOLOGOUS_SUPERFAMILY`, `STRUCT_DOMAIN`
(CATH / SCOPe / ECOD / TED); `STRUCT_SECONDARY`; and local features
`STRUCT_ACTIVE_SITE`, `STRUCT_BINDING_SITE`, `STRUCT_METAL_SITE`.

The repo's current thresholds are Foldseek **TM-score ≥ 0.5 → `close_match` (fold)**
and **TM-score ≥ 0.7 → `close_match` (superfamily)**
(`.claude/skills/merge-within-axis/reference/axis-operators.md`, rows for
`STRUCT_FOLD`/`STRUCT_TOPOLOGY` and `STRUCT_HOMOLOGOUS_SUPERFAMILY`/`STRUCT_DOMAIN`).
Those two numbers are examined and critiqued below.

---

## 1. Equivalence cutoffs — when two structural traits are the SAME

### 1.1 TM-score (fold-level equivalence)

- **TM-score range and the 0.5 "same fold" cutoff.** The TM-score scale runs
  0–1. Scores **< 0.17** correspond to randomly chosen, unrelated protein pairs;
  scores **> 0.5** correspond to protein pairs that "generally" share the same
  fold in SCOP/CATH. This is the canonical Zhang–Skolnick interpretation.
  Source: Zhang & Skolnick, "Scoring function for automated assessment of protein
  structure template quality," *Proteins* 2004, 57:702–710,
  DOI [10.1002/prot.20264](https://doi.org/10.1002/prot.20264); scale summary on
  the TM-score server, https://zhanggroup.org/TM-score/ .

- **Random baseline ≈ 0.17.** The mean TM-score of random (gapless-aligned)
  structure pairs is ~0.17, at which the P-value approaches 1 (indistinguishable
  from noise). Same sources as above.

- **Length normalization (d0).** TM-score normalizes the per-residue distance by
  a length-dependent scale
  **d0(L) = 1.24·(L − 15)^(1/3) − 1.8** (L = length of the target/reference
  chain), which removes the protein-size dependence that afflicts RMSD/GDT and
  makes the ~0.17 random baseline length-independent.
  Source: Zhang & Skolnick 2004 (above); TM-align paper, Zhang & Skolnick,
  *Nucleic Acids Res.* 2005, 33:2302–2309, DOI
  [10.1093/nar/gki524](https://doi.org/10.1093/nar/gki524),
  https://academic.oup.com/nar/article/33/7/2302/2401364 .

- **Statistical basis of TM-score = 0.5 (Xu & Zhang 2010).** TM-scores of
  unrelated pairs follow an **extreme-value distribution** with location
  **μ = 0.1512** and scale **σ = 0.0242**. At **TM-score = 0.5** the **P-value is
  5.5 × 10⁻⁷** (≈ 1 in 1.8 million random pairs). The *posterior* probability
  that two proteins share a fold given TM = 0.5 is only **~13% (SCOP)** / **~37%
  (CATH)** / **~15% (consensus)** — i.e. 0.5 is the *onset* of fold-level
  similarity, not a confident call; the posterior jumps to **80–90% at TM ≈ 0.6**.
  Source: Xu & Zhang, "How significant is a protein structure similarity with
  TM-score = 0.5?," *Bioinformatics* 2010, 26(7):889–895, DOI
  [10.1093/bioinformatics/btq066](https://doi.org/10.1093/bioinformatics/btq066),
  https://academic.oup.com/bioinformatics/article/26/7/889/213219 ;
  PubMed https://pubmed.ncbi.nlm.nih.gov/20164152/ .

  **Critique of the repo's ≥ 0.5 fold cutoff.** Statistically defensible as the
  *fold-onset* threshold (P ≈ 5×10⁻⁷). But because the same-fold *posterior* at
  exactly 0.5 is only 13–37%, a ≥ 0.5 hit is a genuine `close_match` **review
  candidate**, not an auto-merge — which matches the skill's rule ("never merge on
  `close_match` alone"). Tightening the auto-consider point toward **0.6** would
  raise same-fold confidence to 80–90%. Note TM-score is **asymmetric**
  (normalized by the chosen reference length); the merge operator should use the
  larger of the two directions or symmetrize, or the call can flip with reference
  choice (Xu & Zhang 2010; TM-align 2005).

- **Foldseek defaults and the fold vs superfamily distinction.** Foldseek's
  defaults are sensitivity **-s 9.5**, E-value **-e 10** (permissive; the paper's
  benchmark run used `-s 9.5 -e 10 --max-seqs 2000`), and it ranks hits by
  structural bit score. It reports a **homology probability** from a two-gamma
  mixture model fit on **SCOPe40** true/false positives — this is a *homology*
  probability, **not** a TM-score. Global TM-score alignment is the optional
  **`--alignment-type 1`** (accelerated TM-align) mode. Crucially, Foldseek's
  paper does **not** publish a TM-score (or probability) cutoff that separates
  "same superfamily" from "same fold"; it benchmarks family/superfamily/fold as
  *SCOPe label agreement* (family = same family; superfamily = same superfamily,
  different family; fold = same fold, different superfamily; FP = different fold)
  via ROC-to-first-FP.
  Source: van Kempen et al., "Fast and accurate protein structure search with
  Foldseek," *Nat. Biotechnol.* 2024, 42:243–246, DOI
  [10.1038/s41587-023-01773-0](https://doi.org/10.1038/s41587-023-01773-0),
  https://www.nature.com/articles/s41587-023-01773-0 ;
  PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC10869269/ .

  **Critique of the repo's ≥ 0.7 superfamily cutoff.** There is **no canonical
  TM-score that means "same superfamily."** Superfamily is an *evolutionary*
  (homology) claim; TM-score measures *geometry* only and cannot by itself
  establish common ancestry (Xu & Zhang 2010; SCOP definition below). Using a
  *higher* TM-score (0.7) for the *more specific* superfamily level is internally
  consistent (more geometric similarity → tighter grouping) and empirically
  reasonable (0.7 is deep in the same-fold-with-high-confidence regime), but the
  number itself is a **repo heuristic**, not a threshold published by Foldseek,
  CATH, SCOP or ECOD. To assert *superfamily* (homology) rather than *fold*
  (topology), a second evolutionary signal (shared CATH-H / SCOP-superfamily /
  ECOD-H id, or Foldseek homology probability, or sequence/functional evidence)
  should corroborate the TM-score — consistent with the skill's "TM-score AND a
  second signal" promotion rule. **Flagged UNVERIFIED as a published cutoff.**

### 1.2 DALI Z-score

Holm's recommended interpretation of the DALI Z-score:

| Z-score | Interpretation |
|---|---|
| **> 20** | Structures are "definitely homologous" |
| **8 – 20** | Structures "probably homologous" |
| **2 – 8** | "Gray zone" — candidates for homology, need further analysis |
| **< 2** | Not significant (no meaningful structural similarity) |

DALI **fold types** are built by agglomerative clustering such that members have
**average pairwise Z-score > 2** (empirically chosen to group topologically
similar structures). So **Z > 2** is the same-fold floor and **Z ≳ 8** the
practical homology (superfamily-ish) signal.
Source: Holm, "Using Dali for protein structure comparison," *Methods Mol. Biol.*
2020 / "Dali server: structural unification of protein families," *Nucleic Acids
Res.* 2022, 50:W210–W215, DOI
[10.1093/nar/gkac387](https://doi.org/10.1093/nar/gkac387),
https://academic.oup.com/nar/article/50/W1/W210/6591528 ; Holm 2023, *Protein
Sci.* 32:e4519, DOI [10.1002/pro.4519](https://doi.org/10.1002/pro.4519),
https://onlinelibrary.wiley.com/doi/full/10.1002/pro.4519 ; Dali Domain
Dictionary v3, *Nucleic Acids Res.* 2001, PMC
https://pmc.ncbi.nlm.nih.gov/articles/PMC29815/ .

### 1.3 CATH assignment thresholds

CATH clusters domains into a **Homologous superfamily (H)** when **two or more**
of these hold (structural overlap ≥ 60% of the larger domain equivalent to the
smaller throughout):

- **Sequence identity ≥ 35%** (+ 60% overlap); **or**
- **SSAP score ≥ 80.0 and sequence identity ≥ 20%** (+ 60% overlap); **or**
- **SSAP score ≥ 70.0** (+ 60% overlap) with related function (literature /
  Pfam-informed).

Within a superfamily, sequence families ("S" level) are cut at **≥ 35% sequence
identity**. SSAP is a residue-residue structural-alignment score on a 0–100
scale; **≥ 80 with ≥ 20% identity** is treated as a confident homolog even in
"superfold" families, whereas SSAP 70–80 also catches analogues (same fold, no
homology) and needs manual/functional review.
Source: Orengo et al., "CATH — a hierarchic classification of protein domain
structures," *Structure* 1997, 5:1093–1108, DOI
[10.1016/S0969-2126(97)00260-8](https://doi.org/10.1016/S0969-2126(97)00260-8),
https://www.sciencedirect.com/science/article/pii/S0969212697002608 ;
"Classifying a Protein in the CATH Database of Domain Structures," *Acta Cryst.
D* 1998, https://journals.iucr.org/d/issues/1998/06/01/ba0008/index.html ;
Dawson et al., CATH 2017, *Nucleic Acids Res.* 45:D289–D295,
PMC https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5210570/ .

### 1.4 SCOP / SCOPe — fold (topology) vs superfamily (evolution)

SCOP is **manually curated**; its levels have **no single numeric cutoff** —
they are expert judgements:

- **Family** — clear common evolutionary origin, usually detectable by sequence
  (BLAST/PSI-BLAST/HMMER); operationally often ≳ **30% pairwise sequence
  identity**, but also lower when function/structure make ancestry clear.
- **Superfamily** — *probable* common evolutionary origin despite low sequence
  identity; inferred from shared structural features **plus** conserved
  active/binding-site architecture or oligomerization mode. **Evolutionary**
  claim.
- **Fold** — major structural similarity: same **secondary-structure
  composition, architecture and topology** of the domain core. **Geometric**
  claim; a shared fold does **not** imply common ancestry.

So SCOP fold = topology, SCOP superfamily = evolution — the same fold/superfamily
distinction the repo's `STRUCT_FOLD`/`STRUCT_TOPOLOGY` vs
`STRUCT_HOMOLOGOUS_SUPERFAMILY` categories encode. Quantitatively, QSCOP shows
structural similarity decreases monotonically Family → Superfamily → Fold, but no
hard TM/Z cut defines the boundaries.
Source: Murzin et al., "SCOP: a structural classification of proteins database,"
*J. Mol. Biol.* 1995, 247:536–540, DOI
[10.1016/S0022-2836(05)80134-2](https://doi.org/10.1016/S0022-2836(05)80134-2);
SCOP 2020, *Nucleic Acids Res.* 48:D376–D382, DOI
[10.1093/nar/gkz1064](https://doi.org/10.1093/nar/gkz1064),
https://academic.oup.com/nar/article/48/D1/D376/5625529 ; SCOPe help,
https://scop.berkeley.edu/help/ ; QSCOP, *Bioinformatics* 2007,
https://academic.oup.com/bioinformatics/article/23/4/513/180254 .

### 1.5 ECOD — X / H / T / F group criteria

ECOD hierarchy (top → bottom): **A** (architecture) → **X** (possible homology) →
**H** (homology) → **T** (topology) → **F** (family):

- **X-group** — domains with **weak-to-moderate** evidence of homology (possible
  homologs / structurally similar); ancestry uncertain.
- **H-group** — **strong** evidence of homology (definite common ancestry).
- **T-group** — homologous domains split by **topological** differences (ECOD's
  signature feature: it lets homologs — same H — occupy *different* topologies).
- **F-group** — sequence **family**, since 2017 defined by direct **Pfam**
  collaboration (deprecating the former ECODf library).

Key contrast with CATH/SCOP: in ECOD **homology (H) sits ABOVE topology (T)** —
homologs may differ in topology — whereas in CATH topology (T) sits above
homologous superfamily (H). This inversion matters for containment direction
(§2).
Source: Cheng et al., "ECOD: An Evolutionary Classification of Protein Domains,"
*PLoS Comput. Biol.* 2014, 10:e1003926, DOI
[10.1371/journal.pcbi.1003926](https://doi.org/10.1371/journal.pcbi.1003926),
https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003926 ;
"ECOD: new developments," *Nucleic Acids Res.* 2017, 45:D296–D302, DOI
[10.1093/nar/gkw1137](https://doi.org/10.1093/nar/gkw1137),
https://academic.oup.com/nar/article/45/D1/D296/2605814 ; ECOD 2025, *Nucleic
Acids Res.* 53:D411, https://academic.oup.com/nar/article/53/D1/D411/7905311 .

### 1.6 Secondary structure — DSSP 8→3 reduction, topology-string identity, STRIDE

- **DSSP 8-state alphabet:** **H** (α-helix), **G** (3₁₀-helix), **I** (π-helix),
  **E** (β-strand, extended), **B** (isolated β-bridge), **T** (H-bonded turn),
  **S** (bend), **C**/blank (coil/loop).
  Source: Kabsch & Sander, "Dictionary of protein secondary structure," *Biopolymers*
  1983, 22:2577–2637, DOI
  [10.1002/bip.360221211](https://doi.org/10.1002/bip.360221211).

- **8 → 3 reduction (most common rule):** helix **H = {H, G, I}**, strand
  **E = {E, B}**, coil **C = {T, S, C, blank}**. Variant reductions exist (e.g.
  strict "H=H only, E=E only, rest coil"; or moving G to coil), and the choice
  measurably changes downstream numbers — so the reduction rule must be stated
  when calling two SS strings equal.
  Source: JPred SS references (8→3 reduction comparison),
  https://www.compbio.dundee.ac.uk/jpred/references/prot_html/node17.html ;
  Zhou & Troyanskaya, 8-state prediction, PMC
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6090794/ .

- **When two SS traits are "the same".** For `STRUCT_SECONDARY`, equivalence is
  **string identity after a fixed 8→3 reduction**: two elements are the same if
  same 3-state type over the same region (`close_match`); a **topology string**
  (ordered SS-element sequence, e.g. `βαβαβ` / the "β-α-β" motif) is the same
  when the ordered reduced-state strings match. One string being a **contiguous
  substring** of the other is `narrow_match` (containment, §2). This is exactly
  the repo's `build_secondary_structure_equivalence.py` topology-string /
  SS-string operator.

- **STRIDE vs DSSP (why the reduction/tool must be pinned).** DSSP assigns from
  H-bond energy alone; **STRIDE combines H-bond energy with φ/ψ backbone-torsion
  statistics**. They **disagree on ~5–20% of residues**, chiefly at helix ends,
  the α vs 3₁₀ distinction, turns, and short parallel strands. STRIDE matched the
  authors' own assignments for 58% of chains vs 31% for DSSP; only 11% of chains
  agree residue-for-residue between the two. **Consequence:** two SS records are
  only comparable if assigned by the **same tool + same reduction rule**;
  cross-tool SS-string equality is unreliable and should not be auto-merged.
  Source: Frishman & Argos, "Knowledge-based protein secondary structure
  assignment," *Proteins* 1995, 23:566–579, DOI
  [10.1002/prot.340230412](https://doi.org/10.1002/prot.340230412),
  https://pubmed.ncbi.nlm.nih.gov/8749853/ ; STRIDE web server, *Nucleic Acids
  Res.* 2004, 32:W500–W502, https://academic.oup.com/nar/article/32/suppl_2/W500/1040640 ;
  Zacharias & Knapp, DSSP/STRIDE/KAKSI comparison, *J. Comput. Chem.* 2014,
  https://www.sciencedirect.com/science/article/abs/pii/S1093326314001648 .

### 1.7 Local features (active / binding / metal sites)

No structural-superposition cutoff applies; equivalence is **same catalytic /
ligand residues on the same region of the same protein(s)** — Phase-2 member
overlap **plus mandatory Tier-2 same-region coordinate confirmation**
(`verify_region_overlap.py`), optionally anchored to a mechanism/ontology id
(M-CSA, EC, Rhea, ChEBI, GO). High member overlap alone is the localized-feature
trap. Source: repo skill `reference/axis-operators.md` (STRUCTURE local-feature
row + Trap 1); M-CSA, Ribeiro et al., *Nucleic Acids Res.* 2018, 46:D618–D623,
DOI [10.1093/nar/gkx1012](https://doi.org/10.1093/nar/gkx1012).

---

## 2. Containment / subsumption — "structure X contained in Y"

Two distinct partonomies apply on the STRUCTURE axis:
(a) **classification subsumption** — a *more specific* class is a `subclass_of` a
*less specific* one (is-a); and (b) **compositional partonomy** — a physical
*part* is `part_of` a whole (has-part inverse). They must not be conflated: a
CATH family is *a kind of* its superfamily (is-a), whereas a domain is *a part
of* a chain (part-of).

### 2.1 Classification hierarchies (is-a / `subclass_of`)

- **CATH:** Class ⊃ Architecture ⊃ Topology(fold) ⊃ Homologous-superfamily ⊃
  (sequence family). Each finer level `subclass_of` its parent. So a homologous
  superfamily is `subclass_of` a topology/fold; a fold `subclass_of` an
  architecture; etc. Source: Orengo 1997 / CATH 2017 (§1.3).
- **SCOP/SCOPe:** Class ⊃ Fold ⊃ Superfamily ⊃ Family ⊃ (protein/species/domain).
  A superfamily is `subclass_of` its fold; a family `subclass_of` its superfamily.
  Source: Murzin 1995 / SCOP 2020 (§1.4).
- **ECOD:** A ⊃ X ⊃ H ⊃ T ⊃ F. Because **H is above T**, an ECOD **T-group is
  `subclass_of` its H-group** (topology variant within one homology group) — the
  reverse nesting from CATH, where the homologous superfamily is nested *inside*
  the topology. Source: Cheng 2014 / ECOD 2017 (§1.5).

Direction rule: **finer/narrower class → coarser/broader class** is
`biolink:subclass_of`. When two records are the *same source level* across
sources and one denotes a strictly broader grouping, use `biolink:narrow_match`
(the narrower record subsumed by the broader) rather than `subclass_of` — reserve
`subclass_of` for a genuine within-hierarchy parent.

### 2.2 Compositional partonomy (`part_of` / `has_part`)

| Whole | Part | Relation |
|---|---|---|
| Multi-domain chain / protein | a constituent **domain** | domain `part_of` chain |
| Architecture (spatial arrangement) | its **domains/SSEs** | element `part_of` architecture |
| Fold / super-secondary motif | its **SS elements** (helix, strand) | helix/strand `part_of` motif |
| **β-sheet** | a **β-hairpin** / β-strand | β-hairpin `part_of` β-sheet |
| **Coiled-coil** | a constituent **α-helix** | helix `part_of` coiled-coil |
| **Domain** | its **active / binding / metal site** | site `part_of` domain |
| **Active / binding site** (as a trait) | its catalytic **residues** | residue `has_part` site (skill's `has_part`) |

Note the **β-hairpin ⊂ β-sheet** and **helix ⊂ coiled-coil** cases are
*compositional* (`part_of`), not *is-a*: a hairpin is not "a kind of" sheet, it is
a piece of one; a single helix is a component of the coiled-coil assembly. RO
grounding: `part_of` = **RO:0002131** / **BFO:0000050**; `has_part` =
**RO:0002130** / **BFO:0000051**. Biolink `biolink:part_of` maps to BFO:0000050
and `biolink:has_part` to BFO:0000051.
Source: Relation Ontology, https://oborel.github.io/ ; Biolink Model predicates,
https://biolink.github.io/biolink-model/predicate/ .

### 2.3 Biolink / RO mapping summary

Biolink match predicates are subproperties of `biolink:related_to` and mirror
SKOS mapping granularity (`close_match`↔skos:closeMatch, `narrow_match`↔
skos:narrowMatch, `broad_match`↔skos:broadMatch, `exact_match`↔skos:exactMatch).
- **Same trait, cross-source, per the axis operator** → `biolink:close_match`
  (review-then-merge; not auto).
- **One subsumes the other (is-a within a classification)** → `biolink:subclass_of`
  (or `biolink:narrow_match` for the narrower of a cross-source pair).
- **Physical part / whole** → `biolink:part_of` (BFO:0000050) /
  `biolink:has_part` (BFO:0000051).
- **Membership without merge** → `biolink:member_of`.
Source: https://biolink.github.io/biolink-model/using-the-modeling-language/ ;
https://biolink.github.io/biolink-model/curating-the-model/ ;
predicate page https://biolink.github.io/biolink-model/predicate/ .

---

## (a) Cutoffs table — equivalence

| Operator | Equivalence rule + numeric cutoff | Source |
|---|---|---|
| **TM-score (fold)** | Same fold onset at **TM ≥ 0.5** (P = 5.5×10⁻⁷); random baseline mean ≈ **0.17**; same-fold posterior only ~13% (SCOP)/~37% (CATH) at 0.5, ~80–90% at **0.6**. d0(L)=1.24·(L−15)^⅓−1.8. Asymmetric. | Xu & Zhang 2010, DOI 10.1093/bioinformatics/btq066; Zhang & Skolnick 2004, DOI 10.1002/prot.20264 |
| **TM-score (superfamily) — repo ≥ 0.7** | **No canonical superfamily TM cutoff exists.** 0.7 is a repo heuristic (tighter → more specific); superfamily = homology, needs a 2nd evolutionary signal. **UNVERIFIED as published.** | Foldseek, DOI 10.1038/s41587-023-01773-0; Xu & Zhang 2010 (posterior); SCOP (homology≠geometry) |
| **Foldseek defaults** | -s 9.5, -e 10, ranks by struct. bit score; homology **probability** from 2-gamma fit on SCOPe40 (not a TM cutoff); global TM via `--alignment-type 1`. No published superfamily/fold TM boundary. | van Kempen et al. 2024, DOI 10.1038/s41587-023-01773-0 |
| **DALI Z-score** | Significant **Z > 2** (same-fold floor; fold clusters have avg pairwise Z > 2); 2–8 gray zone; 8–20 probable homolog; **> 20** definite homolog. | Holm 2022, DOI 10.1093/nar/gkac387; Holm 2023, DOI 10.1002/pro.4519 |
| **CATH homologous superfamily** | ≥2 of: seq-id **≥ 35%** (+60% overlap); **SSAP ≥ 80** & seq-id ≥ 20% (+60%); **SSAP ≥ 70** (+60%) + related function. Sequence family ("S") at **≥ 35%** id. | Orengo et al. 1997, DOI 10.1016/S0969-2126(97)00260-8; CATH 2017 |
| **SCOP/SCOPe** | Manual; **no numeric cut.** Family = clear ancestry (~≥30% id, sequence-detectable); Superfamily = probable ancestry (structure + site/oligomer features); Fold = same SS composition+architecture+topology (geometry, not ancestry). | Murzin et al. 1995, DOI 10.1016/S0022-2836(05)80134-2; SCOP 2020, DOI 10.1093/nar/gkz1064 |
| **ECOD X/H/T/F** | X = weak/moderate homology evidence; H = strong homology; T = topology split within H; F = family (Pfam). **H above T** (homologs may differ in topology). No fixed numeric cut. | Cheng et al. 2014, DOI 10.1371/journal.pcbi.1003926; ECOD 2017, DOI 10.1093/nar/gkw1137 |
| **Secondary structure (STRUCT_SECONDARY)** | 8-state DSSP {H,G,I,E,B,T,S,C} → 3-state via **H={H,G,I}, E={E,B}, C={T,S,C}**; same trait = SS/topology-string **identity after the fixed reduction**; substring → containment. Must fix tool (DSSP vs STRIDE disagree ~5–20%) + reduction rule. | Kabsch & Sander 1983, DOI 10.1002/bip.360221211; Frishman & Argos 1995, DOI 10.1002/prot.340230412 |
| **Local sites (active/binding/metal)** | No superposition cutoff; same residues on same region of same protein(s) — member overlap **+ mandatory Tier-2 region confirmation**; optional M-CSA/EC/Rhea anchor. | repo `reference/axis-operators.md`; M-CSA, DOI 10.1093/nar/gkx1012 |

## (b) Relationships table — containment / subsumption

| Containment case | Direction | Predicate | Source |
|---|---|---|---|
| CATH family within homologous superfamily | family → superfamily | `biolink:subclass_of` | Orengo 1997 |
| CATH homologous superfamily within topology(fold) | superfamily → fold | `biolink:subclass_of` | Orengo 1997 |
| CATH topology within architecture within class | finer → coarser | `biolink:subclass_of` | Orengo 1997 |
| SCOP family within superfamily within fold within class | finer → coarser | `biolink:subclass_of` | Murzin 1995 |
| ECOD F within T within H within X within A | finer → coarser | `biolink:subclass_of` | Cheng 2014 |
| ECOD **topology (T) within homology (H)** | T → H (H is broader) | `biolink:subclass_of` | ECOD 2017 (H above T) |
| Cross-source: narrower grouping vs broader grouping | narrower → broader | `biolink:narrow_match` | Biolink / SKOS |
| Domain within a multi-domain chain/protein | domain → chain | `biolink:part_of` (RO:0002131/BFO:0000050) | RO; Biolink predicate page |
| SS element / domain within an architecture | element → architecture | `biolink:part_of` | RO; CATH |
| Helix/strand within a super-secondary (fold) motif | SSE → motif | `biolink:part_of` | RO |
| **β-hairpin (or strand) within a β-sheet** | hairpin → sheet | `biolink:part_of` (not is-a) | RO |
| **α-helix within a coiled-coil** | helix → coiled-coil | `biolink:part_of` (not is-a) | RO |
| SS topology-string as substring of a longer one | shorter → longer | `biolink:narrow_match` | Biolink / SKOS |
| Active/binding/metal site within a domain | site → domain | `biolink:part_of` | RO; repo skill |
| Catalytic residues within a site trait | residue → site | `biolink:has_part` (RO:0002130/BFO:0000051) | repo `reference/axis-operators.md`; RO |

## (c) Verification log — flagged numbers

| Claim | Status | Note |
|---|---|---|
| TM ≥ 0.5 = fold onset; P = 5.5×10⁻⁷; baseline ≈ 0.17; EVD μ=0.1512, σ=0.0242; posteriors 13% SCOP/37% CATH, 80–90% @0.6 | **VERIFIED** | Xu & Zhang 2010 (fetched abstract + Zhang–Skolnick 2004 scale) |
| d0 = 1.24·(L−15)^⅓ − 1.8 | **VERIFIED** (well-established) | Zhang & Skolnick 2004 / TM-align 2005; formula from primary literature, not re-derived here |
| Repo **TM ≥ 0.7 → superfamily** `close_match` | **UNVERIFIED as a published cutoff** | No CATH/SCOP/ECOD/Foldseek source publishes a superfamily TM threshold; it is a repo heuristic. Superfamily=homology needs a 2nd (evolutionary) signal. Recommend documenting it as such and requiring corroboration. |
| Foldseek defaults -s 9.5, -e 10, prob from 2-gamma on SCOPe40 | **VERIFIED** | Nat. Biotechnol. 2024 / PMC10869269 (benchmark run used -e 10) |
| DALI: Z>2 same-fold floor; 8–20 probable; >20 definite homolog | **VERIFIED** | Holm 2022 NAR + Holm 2023 Protein Sci; exact band edges (8 vs 10, 20) vary slightly by Holm publication — treat as guidance bands, not hard cuts |
| CATH: seq-id ≥35%, SSAP ≥80 & id≥20%, SSAP ≥70 + function; ≥2 criteria + 60% overlap | **VERIFIED** | Orengo 1997 + IUCr 1998 protocol |
| SCOP has **no numeric** fold/superfamily/family cutoff; ~30% id for family is a soft heuristic | **VERIFIED (qualitative)** | Murzin 1995 / SCOP 2020; the ~30% family sequence-id figure is a common heuristic, not a hard SCOP rule — flagged as soft |
| ECOD X/H/T/F, **H above T** | **VERIFIED** | Cheng 2014 / ECOD 2017 |
| DSSP 8-state letters + H={H,G,I}/E={E,B}/C=rest reduction | **VERIFIED** | Kabsch & Sander 1983 + JPred/PMC reduction refs; note multiple valid reductions exist (choice affects results) |
| STRIDE vs DSSP disagree ~5–20% of residues (helix ends, α/3₁₀, turns) | **VERIFIED (range)** | Frishman & Argos 1995 + 2014 comparison; the "58% vs 31% match author assignment / 11% identical" figures are from Frishman & Argos 1995 on a 226-chain set — dataset-specific, not universal constants |
| Biolink match predicates ↔ SKOS granularity; part_of=BFO:0000050, has_part=BFO:0000051 | **VERIFIED** | Biolink model docs + RO/BFO |

---

### Practical recommendation for the repo

1. **Keep TM ≥ 0.5 for `STRUCT_FOLD`/`STRUCT_TOPOLOGY`** as the `close_match`
   *candidate* onset, but treat 0.5–0.6 as low-confidence (13–37% same-fold
   posterior) — never auto-merge; consider raising the "second-signal-not-needed"
   bar toward 0.6.
2. **Re-label the 0.7 "superfamily" cutoff as a repo heuristic** and require a
   corroborating evolutionary signal (shared CATH-H / SCOP-superfamily / ECOD-H
   id, Foldseek homology probability, or sequence/functional evidence) before
   asserting superfamily-level equivalence — TM-score alone proves geometry, not
   homology.
3. **Pin the SS tool + 8→3 reduction rule** in `STRUCT_SECONDARY` comparison; do
   not compare DSSP-derived against STRIDE-derived SS strings for auto-merge.
4. Symmetrize/normalize TM-score (use the max over both reference directions) to
   avoid reference-length flip in the fold operator.
