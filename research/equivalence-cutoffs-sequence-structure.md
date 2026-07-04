---
topic: Trait EQUIVALENCE and CONTAINMENT cutoffs for the SEQUENCE_STRUCTURE axis (MIXED_* categories)
date: 2026-07-04
axis: SEQUENCE_STRUCTURE
categories: [MIXED_STRUCTURAL_REPEAT, MIXED_COILED_COIL, MIXED_TRANSMEMBRANE]
status: research report (cited, adversarially verified) — no code/record changes
scope: >-
  Defines when two SEQUENCE_STRUCTURE ("MIXED") traits are the SAME (equivalence
  cutoffs) and when one is CONTAINED in another (subsumption / partonomy), with a
  Biolink/RO mapping. Backs the per-axis operator in
  .claude/skills/merge-within-axis (MIXED row: "repeat-unit / coiled-coil register
  + supercoil topology; member overlap once populated").
---

# Equivalence & containment cutoffs — SEQUENCE_STRUCTURE axis

## 0. Framing

The three MIXED categories are **structure-anchored** but **sequence-detectable**:
a periodic sequence signal maps to a specific 3-D arrangement. That dual nature is
exactly why they are their own axis (`SEQUENCE_STRUCTURE`) and must not be merged
into either the pure `SEQ_*` or pure `STRUCT_*` axes (skill trap #5, the "bridge
trap"). The merge-within-axis operator for this axis is *repeat-unit / coiled-coil
register + supercoil topology*, with member overlap as a secondary signal once the
categories are populated (`skill.md` §SEQUENCE_STRUCTURE; `reference/axis-operators.md`
§SEQUENCE_STRUCTURE).

A recurring honest caveat runs through this report: **two of the three categories
have no single hard numeric equivalence cutoff.** Repeats have a discrete
classification (RepeatsDB) that *is* the equivalence test; coiled coils and
transmembrane spans have detector probability thresholds that gate *detection*, not
*trait identity*. Section D (verification log) flags every soft or unverified number.

---

## A. Cutoffs table — when two MIXED traits are the SAME trait

| # | Category | Equivalence is decided by | Hard cutoff / rule | Source |
|---|----------|---------------------------|--------------------|--------|
| A1 | `MIXED_STRUCTURAL_REPEAT` | Same RepeatsDB branch **Class → Topology → Fold → Clan**. Same *fold* (and ideally same *clan*) ⇒ same structural-repeat trait. | Discrete classification match, **not** a numeric score. Class is set by repeat period: I ≈1–2 aa, II 3–7 aa, III 5–40 aa, IV 30–60 aa (closed/toroid), V >50 aa (beads-on-a-string, independently folding domains). | RepeatsDB 2021 [1]; RepeatsDB 2025 [2] |
| A2 | `MIXED_STRUCTURAL_REPEAT` (seq detection of the periodicity) | Independent sequence-periodicity detectors agree a region is repetitive; used to *populate/confirm*, not to assert identity. | HHrepID: P-value ≤ 1e-3 (repeat family), suboptimal-alignment P ≤ 0.1, T=0.5. Benchmarked 0.1% FPR cutoffs: HHrepID P ≤ 8.7e-12; TRUST score ≥ 789.29; RADAR total score ≥ 586.04. | Biegert & Söding 2008 [3]; Frontiers benchmark 2015 [4] |
| A3 | `MIXED_COILED_COIL` | Same **heptad register phase** (abcdefg with hydrophobic a/d core), same **oligomeric state** (2/3/4-stranded) and same **orientation** (parallel/antiparallel), confirmed by knobs-into-holes packing. | **No single numeric identity cutoff.** SOCKET/Socket2 knobs-into-holes packing-cutoff default = **7 Å** (a residue is a "knob" if its side-chain centroid lies within 7 Å of the 4 side chains forming the "hole"). That gates *whether a CC exists & its geometry*, not trait-vs-trait identity. | Walshaw & Woolfson SOCKET [5]; Socket2 [6]; CC critical-assessment [7] |
| A4 | `MIXED_COILED_COIL` (seq detection) | Predictor probability that a residue/segment is coiled-coil; used for detection/populate, **not** identity. | NCOILS threshold 0.5; MultiCoil2 0.25; PairCoil2 max 0.025; Marcoil ≥ 90 (posterior %). All run at 21-aa window except Marcoil/MultiCoil2 (windowless). DeepCoil/CoCoNat emit per-residue propensity with **no fixed published cutoff** (users pick, commonly 0.5). | CC critical-assessment [7]; DeepCoil [8]; CoCoNat [9] |
| A5 | `MIXED_TRANSMEMBRANE` | Same TM **class** (α-helical vs β-barrel) AND same **topology** (number of spans + in/out orientation string). Different class ⇒ never the same family; same class + same span count/topology ⇒ same TM-architecture trait. | Class + topology-string match, **not** a numeric score. DeepTMHMM per-residue label set: S(signal), I(inside), M(α-membrane), B(β-membrane), P(periplasm), O(outside) — B vs M encodes the α/β split. | DeepTMHMM [10]; TMHMM 2.0 [11]; Phobius [12] |
| A6 | `MIXED_TRANSMEMBRANE` (seq detection) | Predictor calls the spans; used to populate/confirm, not identity. | TMHMM heuristic: expected #residues in TM helices **> 18** ⇒ likely a real TM protein; expected TM-aa in first 60 residues **> 10** ⇒ warn N-terminal span may be a signal peptide (SP/TM confusion is 25–65% at proteome scale). DeepTMHMM outperforms TMHMM/Phobius on span count + topology. | TMHMM 2.0 [11]; Phobius [12]; DeepTMHMM [10] |

**Cross-category rule (all three):** equivalence is asserted only **same-axis AND
same-category** (skill.md). A `MIXED_COILED_COIL` is never equivalent to a
`MIXED_STRUCTURAL_REPEAT` even though both are periodic — different topology class.

---

## B. Relationships table — containment / subsumption

Legend for direction: `A → B` means the edge is stored subject=A, object=B (read
"A <predicate> B"). Biolink CURIEs from the Biolink Model association-slot
vocabulary [13]; RO used only where Biolink lacks a crisp partonomy predicate [14].

| # | Case | Direction (subject → object) | Predicate | Rationale / source |
|---|------|------------------------------|-----------|--------------------|
| B1 | A single repeat **UNIT** inside its repeat **REGION** | unit → region | `biolink:part_of` (BFO:0000050 *part of* / inverse `has_part` BFO:0000051) | A unit is "the smallest structural building block forming the repeat region"; a region is the ordered set of units + insertions [1]. Partonomy, never merge. |
| B2 | A repeat **REGION** inside the **DOMAIN / chain** | region → domain | `biolink:part_of` | RepeatsDB records region start/end within the chain; the chain/domain contains ≥1 region [1][2]. |
| B3 | A **fold** vs its narrower **clan** (RepeatsDB hierarchy) | clan → fold | `biolink:narrow_match` | Clan = "a subfold that groups protein structures having a common sequence motif within the repeat" → subclass of Fold [1]. Hierarchy edge, NEVER merge (tier table: narrow_match = keep as hierarchy). |
| B4 | A **topology** vs its narrower **fold** | fold → topology | `biolink:narrow_match` | Fold = "a refinement of 'topology'" [1]. |
| B5 | A single **coiled-coil segment** inside a **multi-segment coiled-coil** trait | segment → multi-segment CC | `biolink:part_of` | A protein may carry several discrete CC segments; each is part of the protein's CC content [6][7]. |
| B6 | A coiled-coil **segment/region** inside the **protein** | CC segment → protein | `biolink:part_of` | SOCKET CC hits are sub-regions of the chain; note CC *prediction* regions are longer than SOCKET knobs-into-holes hits [7]. |
| B7 | One **TM span** inside the **TM topology** (whole-protein span set) | one TM span → TM topology | `biolink:part_of` | The topology string is the ordered set of spans + loops; one span is a part [10][11]. |
| B8 | A specific CC **oligomeric-state trait** (e.g. antiparallel dimer) vs generic "coiled coil" | specific CC → generic CC | `biolink:narrow_match` | Oligomeric state (parallel dimer / antiparallel dimer / trimer / tetramer) subclasses the generic CC trait [9]. |
| B9 | A specific TM **class** (β-barrel) vs generic "transmembrane" | β-barrel TM → generic TM | `biolink:narrow_match` | α-helical vs β-barrel are the two TM classes; each is narrower than "membrane-spanning" [10]. |
| B10 | **Cross-axis bridge:** a sequence-only `SEQ_REPEAT` vs the structural `MIXED_STRUCTURAL_REPEAT` for the same periodic signal | SEQ_REPEAT → MIXED_STRUCTURAL_REPEAT | `biolink:related_to` (or `biolink:narrow_match` if the seq signal is provably a strict subset of the structural region) | **Must NOT merge — different axis by design** (skill trap #5). A sequence-periodicity call (SEQ) and a structurally-verified repeat (MIXED) describe the same phenomenon at different evidence layers; relate, don't collapse [1][3]; merge-within-axis skill.md §SEQUENCE_STRUCTURE / trap catalogue #5. |

**Promotion rule (from the skill):** only `same_as`/R1/R2 auto-merge. Every
`part_of`, `narrow_match`, `related_to` edge above stays as a `trait_relations`
edge — it is a hierarchy/partonomy, never a merge. `close_match` (the equivalence
tier for A1/A3/A5) is a **review candidate** that the axis operator plus a second
signal must confirm before merging.

---

## C. Per-category detail (evidence)

### C1. Structural tandem repeats — RepeatsDB
- **Classification is the equivalence test.** RepeatsDB assigns every repeat region
  to a branch of a 4-level hierarchy **Class → Topology → Fold → Clan** (a 5th
  level, *Family*, groups homologous repeats by sequence similarity but is not yet
  fully annotated) [1][2]. Two `MIXED_STRUCTURAL_REPEAT` traits are the *same trait*
  when they share **Fold** (strongly, when they share **Clan**); sharing only Class
  or Topology is `narrow_match`/`related_to`, not identity.
  - Class: "general shape, mode of interaction between the repetitive elements and
    the oligomerization state depending on the repeat length" [1].
  - Topology: "general path of the polypeptide chain and type of the secondary
    structure in a repetitive unit" [1].
  - Fold: "a refinement of 'topology', differing in secondary structure arrangement
    and/or overall structure (e.g. twist)" [1].
  - Clan: "a subfold that groups protein structures having a common sequence motif
    within the repeat (or part thereof)" [1].
- **Five classes by repeat period (Kajava scheme)** [1]:
  I ≈1–2 aa (crystalline aggregates); II 3–7 aa (fibrous, inter-chain stabilized);
  III 5–40 aa (elongated solenoids, units mutually dependent); IV 30–60 aa (closed/
  toroid, circular arrangement, units mutually dependent); V >50 aa (beads-on-a-
  string, units fold independently as domains).
- **Unit / region / insertion** [1]: a *repeat unit* is "the smallest structural
  building block forming the repeat region"; the *repeat region* runs start→end and
  may contain *insertions* (non-repeated segments between/within units); the
  *period* = "the number of amino acids contained in each repeat." Copy number is
  the count of units in the region (class-dependent, not a fixed threshold).
- **Detection thresholds (populate/confirm, not identity)** [2][3][4]: RepeatsDB
  2025 detection uses **STRPsearch** — a curated Tri-Unit Library + Foldseek
  structural alignment, E-value < 1e-5 for AlphaFoldDB. Sequence-only detectors:
  HHrepID (HMM self-matching) default P ≤ 1e-3 repeat-family, suboptimal P ≤ 0.1,
  T=0.5 [3]; benchmark 0.1%-FPR cutoffs HHrepID P ≤ 8.7e-12, TRUST ≥ 789.29,
  RADAR ≥ 586.04 [4]. TRUST/RADAR use self-alignment sub-optimal alignments;
  HHrepID builds/matches HMMs of repeating substrings [3][4].

### C2. Coiled coils
- **The structural definition** is **knobs-into-holes (KIH)** packing (Crick 1953):
  a "knob" side chain packs into a "hole" of four side chains on the neighbouring
  helix; SOCKET/Socket2 detect KIH with a default **packing cutoff of 7 Å** and
  from the KIH network assign the **heptad register a–g** and report **oligomeric
  order** and **parallel/antiparallel** topology [5][6][7].
- **Equivalence has no hard numeric cutoff.** Two CC traits are the same when they
  share heptad-register phase + oligomeric state + orientation; these are
  categorical, established from KIH geometry, not a score [6][7]. Note CC
  *prediction* regions are systematically longer than the SOCKET KIH hit within
  them [7] — a containment (B6), not a mismatch.
- **Prediction probability thresholds gate detection only** [7][8][9]: NCOILS 0.5;
  MultiCoil2 0.25; PairCoil2 ≤ 0.025; Marcoil ≥ 90 (HMM 9FAM, posterior %); window
  21 aa except Marcoil/MultiCoil2 (windowless). Modern deep models: DeepCoil emits
  raw + sharpened per-residue propensity and per-residue a/d core channels, **no
  fixed cutoff** [8]; CoCoNat predicts CC boundaries, register a–g (per-label
  MCC 0.83–0.84), and 4 oligomeric classes (parallel dimer / antiparallel dimer /
  trimer / tetramer; MCC 0.46–0.70), outperforming Marcoil/PCOILS/DeepCoil2/
  CoCoPRED [9]. **Field verdict: coiled-coil trait equivalence is register+
  oligomer+orientation identity, not a probability threshold.**

### C3. Transmembrane
- **Two classes, then topology.** α-helical bundles vs β-barrels are structurally
  distinct families; DeepTMHMM encodes the split directly in its label alphabet
  {S, I, M(α), B(β), P, O} [10]. Same-family equivalence therefore requires **same
  class**, then **same topology** = same number of spans + same in/out orientation
  string. Different class ⇒ never the same family (A5).
- **Detection conventions** [10][11][12]: TMHMM 2.0 heuristics — expected #residues
  in TM helices **> 18** ⇒ likely genuine TM protein; expected TM-aa in first 60
  residues **> 10** ⇒ N-terminal span may be a signal peptide (SP↔TM confusion
  25–65% proteome-wide; TMHMM1 miscalls >30% of SPs as TM helices). Phobius is an
  HMM that jointly models SP + TM to resolve that confusion [12]. DeepTMHMM
  (encoder–decoder, per-residue labels) improves span-count + topology over both
  and adds β-barrel topology and SP prediction [10].

---

## D. Verification log

| Claim | Status | Note |
|-------|--------|------|
| RepeatsDB 4 levels Class→Topology→Fold→Clan; definitions verbatim | **VERIFIED** | Two independent primary sources [1][2], verbatim quotes captured. |
| Class period ranges (I 1–2, II 3–7, III 5–40, IV 30–60, V >50 aa) | **VERIFIED** | RepeatsDB 2021 [1], verbatim. |
| RepeatsDB *Family* = 5th level (sequence homology, not fully annotated) | **VERIFIED** | [1]. |
| HHrepID P ≤ 1e-3 / suboptimal 0.1 / T=0.5 | **VERIFIED** | Biegert & Söding 2008 [3]. |
| Benchmark 0.1%-FPR cutoffs HHrepID 8.7e-12 / TRUST 789.29 / RADAR 586.04 | **VERIFIED (single benchmark)** | Frontiers 2015 [4]; values are dataset-specific — treat as illustrative, re-derive per corpus. |
| STRPsearch E-value < 1e-5 (RepeatsDB 2025) | **VERIFIED** | [2]. |
| SOCKET/Socket2 default packing cutoff 7 Å; knob=within-cutoff-of-4-side-chains | **VERIFIED** | Socket2 [6] + CC critical-assessment [7] both state default 7 Å verbatim. |
| CC predictor thresholds (NCOILS 0.5, MultiCoil2 0.25, PairCoil2 0.025, Marcoil ≥90, window 21) | **VERIFIED** | CC critical-assessment Methods [7], verbatim. |
| DeepCoil has **no** fixed published cutoff (raw/sharpened propensity) | **VERIFIED (negative)** | Repo docs [8]; the common "0.5" default is a *convention*, UNVERIFIED as an official recommendation. |
| CoCoNat register MCC 0.83–0.84; oligomer MCC 0.46–0.70; 4 classes | **VERIFIED** | CoCoNat paper [9]. |
| DeepTMHMM label set {S,I,M,B,P,O}; α/β split via M vs B | **VERIFIED** | DeepTMHMM bioRxiv [10]. |
| TMHMM "expected TM-aa > 18 ⇒ TM protein" | **UNVERIFIED (primary source)** | Widely-cited TMHMM heuristic; QIAGEN manual fetch [11] did not surface the exact "18" verbatim — the ">10 in first 60 aa ⇒ signal-peptide warning" *was* verified. Confirm "18" against Krogh et al. 2001 or the DTU TMHMM output page before quoting as canonical. |
| TMHMM first-60 expected-TM-aa > 10 ⇒ SP warning; SP/TM overlap 25–65% | **VERIFIED** | Phobius/TMHMM sources [11][12]. |
| Biolink predicates close_match / narrow_match / related_to / part_of / has_part | **VERIFIED (model spec)** | Biolink Model [13]; part_of/has_part map to BFO:0000050 / BFO:0000051 [14]. |
| "Coiled-coil equivalence has no hard numeric cutoff" | **VERIFIED as field-state** | No source defines a numeric CC trait-identity threshold; identity is categorical (register+oligomer+orientation). Stated honestly per task instruction. |
| Bridge SEQ_REPEAT ↔ MIXED_STRUCTURAL_REPEAT = relate-not-merge | **VERIFIED (project rule)** | merge-within-axis skill.md + axis-operators.md trap #5. |

**Honest gaps flagged:** (1) TMHMM ">18" number needs a primary-source confirm
(row above). (2) The 0.1%-FPR repeat-detector cutoffs [4] are benchmark-specific,
not universal constants. (3) No numeric equivalence cutoff exists for coiled coils
or for transmembrane *trait identity* — both are decided categorically, and the
detector probabilities (A4, A6) govern detection, not sameness. (4) RepeatsDB
*Family* level and member-overlap seeding for MIXED are not yet populated in this
corpus, so A1/A2 identity is available today only via the RepeatsDB classification,
not via member-set Jaccard.

---

## Sources

1. RepeatsDB in 2021: improved data and extended classification for protein tandem repeat structures. *Nucleic Acids Res* 49(D1):D452. https://pmc.ncbi.nlm.nih.gov/articles/PMC7778985/
2. RepeatsDB in 2025: expanding annotations of structured tandem repeat proteins on AlphaFoldDB. *Nucleic Acids Res* 53(D1):D575. https://pmc.ncbi.nlm.nih.gov/articles/PMC11701623/
3. Biegert A, Söding J. De novo identification of highly diverged protein repeats by probabilistic consistency (HHrepID). *Bioinformatics* 24(6):807. https://academic.oup.com/bioinformatics/article/24/6/807/194276
4. Tandem Repeats in Proteins: Prediction Algorithms and Biological Role. *Front Bioeng Biotechnol* 3:143 (2015). https://pmc.ncbi.nlm.nih.gov/articles/PMC4585158/
5. Walshaw J, Woolfson DN. SOCKET: identifying and analysing coiled-coil motifs within protein structures (packing-cutoff 7 Å). https://www.researchgate.net/publication/12042392
6. Kumar P, Woolfson DN. Socket2: locating, visualizing and analyzing coiled-coil interfaces. *Bioinformatics* 37(23):4575. https://academic.oup.com/bioinformatics/article/37/23/4575/6366542
7. Critical assessment of coiled-coil predictions based on protein structure data. *Sci Rep* 11 (2021). https://pmc.ncbi.nlm.nih.gov/articles/PMC8203680
8. Ludwiczak J et al. DeepCoil (repo + docs). https://github.com/labstructbioinf/DeepCoil ; paper https://academic.oup.com/bioinformatics/article/35/16/2790/5270664
9. Madeo G et al. CoCoNat: deep learning for coiled-coil prediction. *Bioinformatics* 39(8):btad495. https://academic.oup.com/bioinformatics/article/39/8/btad495/7237258
10. Hallgren J et al. DeepTMHMM predicts alpha and beta transmembrane proteins using deep neural networks. *bioRxiv* 2022.04.08.487609. https://www.biorxiv.org/content/10.1101/2022.04.08.487609v1.full
11. TMHMM 2.0 (Krogh et al. 2001) — DTU Health Tech / QIAGEN manual. https://services.healthtech.dtu.dk/services/TMHMM-2.0/
12. Käll L, Krogh A, Sonnhammer ELL. Phobius: combined transmembrane topology and signal peptide prediction. *Nucleic Acids Res* 35:W429. https://pmc.ncbi.nlm.nih.gov/articles/PMC1933244/
13. Biolink Model — association predicates (close_match, narrow_match, related_to, part_of, has_part). https://biolink.github.io/biolink-model/
14. BFO / Relations Ontology — part of BFO:0000050 / has part BFO:0000051 (Biolink `part_of`/`has_part` map to these); RO:0002131 is *overlaps*. https://oborel.github.io/
</content>
</invoke>
