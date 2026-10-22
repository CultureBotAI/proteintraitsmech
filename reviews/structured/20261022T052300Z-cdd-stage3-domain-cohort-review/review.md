# Cohort scientific review of 12 Stage 3 CDD sequence-domain records with upstream prose and nomenclature defects

- Review: 20261022T052300Z-cdd-stage3-domain-cohort-review
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-22T05:06:00Z
- Finished UTC: 2026-10-22T05:23:00Z
- Reviewer: Antigravity (independent)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Full cohort review of all 12 eligible CDD sequence-domain records in the frozen Stage 4 inventory (10 records held at Stage 3 grounding review due to upstream CDD definition contradictions plus 2 promoted records with minor upstream typographical/wording defects). All 12 records pass strict LinkML schema validation and represent genuine, distinct conserved sequence domain classes (SEQ_DOMAIN on SEQUENCE) that should be retained as separate records rather than lumped with sibling CDD profiles. Twelve open findings (F1-F12: 9 major, 3 minor) share a single root cause in scripts/seed_cdd.py and are preserved for Stage 5 grouped remediation.

## Scope And Provenance

Frozen 12-record CDD SEQ_DOMAIN cohort surfaced during Stage 3 UniProt grounding batches human-ecoli-yeast-complete-cdd-058of128 and 066of128 and tracked under proteintraitsmech-infra-0003.

Selection: Every CDD record in Stage 3 batches 058of128 and 066of128 that exhibited an upstream CDD definition, nomenclature, paralog-scope, or substrate/pathway defect (10 held records blocking 12 human/yeast UniProt examples plus 2 promoted records with minor prose defects).
Coverage: full; 12 reviewed / 12 in the declared population.
Source: git_commit at Git base 32b4f33a71b846acf59b96b7da7282f293ea2165.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| CDD:cd00104 | data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml | generated | Kazal-type serine protease inhibitors and follistatin-like domains |
| CDD:cd00959 | data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml | generated | 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family |
| CDD:cd09530 | data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml | generated | SAM domain of SAMD14 subfamily |
| CDD:cd13344 | data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml | generated | Myotubularian (MTM)-related 7 protein (MTMR7) Pleckstrin homology-Glucosyltransferases, Rab-like GTPase activators and Myotubularins (PH-GRAM) domain |
| CDD:cd14999 | data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml | generated | Urotensin-II receptor, member of the class A family of seven-transmembrane G protein-coupled receptors |
| CDD:cd15894 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml | generated | N-terminal SNARE motif of SNAP25 |
| CDD:cd16523 | data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml | generated | RING finger, HC subclass, found in myosin regulatory light chain interacting protein (MYLIP) and similar proteins |
| CDD:cd16652 | data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml | generated | Degenerated RING (dRING) finger found in Saccharomyces cerevisiae required for meiotic nuclear division protein 5 (Rmd5p) and similar proteins |
| CDD:cd17150 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml | generated | Dublecortin-like domain 1 found in doublecortin domain-containing protein 2B (DCDC2B) and similar proteins |
| CDD:cd18592 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml | generated | Six-transmembrane helical domain 1 (TMD1) of multidrug resistance-associated proteins MRP5, MRP8, and MRP9 |
| CDD:cd20534 | data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml | generated | First cyclin box found in cyclin-M (CCNM) family |
| CDD:cd21551 | data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml | generated | VEFS (VRN2-EMF2-FIS2-Su(z)12) box found in suppressor of zeste 12 protein homolog (SUZ12) and similar proteins |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Strict LinkML and OAK ontology-binding validation across all 12 cohort records | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551 | All 12 CDD cohort records pass closed LinkML schema validation and OAK ontology-term checks with 0 errors. |
| Release-pinned UniProt grounding and binding replay across all 12 cohort records | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551 | 12 files scanned, 21,331 qualified record bindings verified, 0 semantic findings; promoted examples on CDD:cd00104 and CDD:cd00959 replay cleanly and the 10 held records remain unpromoted as expected. |
| Causal-graph audit across all 12 cohort records | passed | False | CDD:cd00104, CDD:cd00959, CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551 | 0 records with causal_graphs, 0 errors, 0 warnings. |
| Registered write-route audit | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551 | 616 scripts examined, 0 unguarded writer findings. |
| Append-only curation history validation | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551 | All 13 history records validate against src/proteintraitsmech/schema/history.yaml with 0 errors. |

## Scientific And Domain Assessments

### Category placement and subfamily boundary distinctness across all 12 CDD records

scope: supported. Targets: CDD:cd00104, CDD:cd00959, CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551.

All 12 records are genuine conserved protein sequence domain profiles (trait_axis: SEQUENCE, trait_category: SEQ_DOMAIN, so_term: SO:0000417) with distinct CDD PSSM identifiers and non-redundant domain intervals or paralog subfamily scopes. None should be merged or lumped with sibling CDD profiles.

### Minor typographical and target-list prose defects on promoted records CDD:cd00104 and CDD:cd00959

consistency: concern. Targets: CDD:cd00104, CDD:cd00959.

CDD:cd00104 (3 qualified human examples) and CDD:cd00959 (2 qualified E. coli/human examples) have valid biological groundings, but carry upstream CDD typos/duplications ('chyomotrypsin' and 'avian ovomucoids' in cd00104; duplicated title sentence in cd00959).

### Upstream CDD nomenclature, paralog-scope, and biochemical contradictions on 10 held records

consistency: concern. Targets: CDD:cd09530, CDD:cd13344, CDD:cd14999, CDD:cd15894, CDD:cd16523, CDD:cd16652, CDD:cd17150, CDD:cd18592, CDD:cd20534, CDD:cd21551.

Ten CDD records contain upstream CDD prose defects that conflict with their matched Swiss-Prot carriers or biochemical mechanisms, blocking promotion of 12 Stage 3 human/yeast UniProt candidates until repaired via a guarded CDD errata module and re-resolved.

## Findings

### F1: CDD:cd00104 definition misspells chymotrypsin and lists avian ovomucoids as target serine proteases

minor / open / confirmed; issue key: cdd-cd00104-kazal-definition-typo-and-inhibitor-target-confusion.

CDD:cd00104 definition states 'Kazal inhibitors inhibit serine proteases, such as, trypsin, chyomotrypsin, avian ovomucoids, and elastases', misspelling 'chymotrypsin' and listing 'avian ovomucoids' (which are Kazal-type inhibitor proteins, PMID:6192856) as target enzymes.

### F2: CDD:cd00959 definition repeats its opening title sentence verbatim

minor / open / confirmed; issue key: cdd-cd00959-dera-duplicated-opening-sentence.

CDD:cd00959 definition begins with the duplicated sentence '2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family.' due to upstream CDD title+description concatenation in scripts/seed_cdd.py.

### F3: CDD:cd09530 names Samd14 in label/definition whereas its human carrier is SAMD15 (Q9P1V8) and human SAMD14 (Q8IZD0) matches CDD:cd09512

major / open / confirmed; issue key: cdd-cd09530-samd14-vs-samd15-nomenclature-conflict.

CDD:cd09530 (short_name SAM_Samd14) defines the domain as 'SAM domain of Samd14 (sterile alpha motif domain-containing protein 14) and similar proteins', without noting that human SAMD14 (UniProtKB:Q8IZD0) is classified under sibling CDD:cd09512 (SAM_Neurabin-like) while the actual human protein matched by CDD:cd09530 in InterPro/CDD is SAMD15/FAM15A (UniProtKB:Q9P1V8, residues 543-609). This nomenclature conflict blocked Stage 3 promotion of candidate ug-261dc8be43fe67ef5a89ce9ecdbdd8107e3ab08802277a3f574bf5c5f9b8c78b.

### F4: CDD:cd13344 (PH-GRAM_MTMR7) switches mid-definition to paralog MTMR6 and ends with a self-contradictory phosphoinositide-binding sentence

major / open / confirmed; issue key: cdd-cd13344-mtmr7-paralog-mtmr6-contradiction.

CDD:cd13344 represents the PH-GRAM domain of MTMR7 (human Q9Y216, 29-113), but sentences 2 and 5 switch without qualification to paralog MTMR6 catalytic activity and end with the self-contradictory statement 'It is not clear if the PH-GRAM domain of MTMR6 binds to phosphoinositides, with a study showing that the PH-GRAM domain of MTMR6 does not bind to phosphoinositides', blocking Stage 3 promotion of candidate ug-dc9e5d1720249523285386416d18a96bb231173b464db6621df6a3f0ba42c240.

### F5: CDD:cd14999 erroneously aliases urotensin-II receptor (UTS2R/GPR14) as the hypocretin receptor

major / open / confirmed; issue key: cdd-cd14999-uts2r-hypocretin-receptor-misaliasing.

CDD:cd14999 (7tmA_UII-R) states 'The urotensin-II receptor (also known as G-protein coupled receptor 14, GPR14, or the hypocretin receptor) is a receptor for the cyclic undecapeptide urotensin-II'. Hypocretin/orexin receptors (HCRTR1/HCRTR2) are distinct GPCRs; UTS2R/GPR14 is not the hypocretin receptor. This misaliasing blocked Stage 3 promotion of human UTS2R candidate ug-4ca0bc07c3ff11d11874a90b7bcbb2b3c258f9ecae390a173ba6162ff34f887d (Q9UKP6, 53-337).

### F6: CDD:cd15894 (SNARE_SNAP25N) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 is membrane-anchored via palmitoylated cysteines

major / open / confirmed; issue key: cdd-cd15894-snap25-transmembrane-domain-overclaim.

CDD:cd15894 states 'Both, Qb/Qc SNAREs consist of 2 coiled-coil helices (which form a single SNARE domain) and a transmembrane domain'. SNAP25 (human P60880, 19-81) is a t-SNARE containing an N-terminal Qb SNARE motif (cd15894) and a C-terminal Qc SNARE motif (sibling cd15885) linked by a palmitoylated cysteine-rich region and lacks any transmembrane domain. This overclaim blocked Stage 3 promotion of candidate ug-e252e4d82e1d26e10002d5abaa0877a146c31f0fd970400dc106954f6c8a85e7.

### F7: CDD:cd16523 (RING-HC_MYLIP) sentence 2 claims proteasomal degradation of LDLR, VLDLR, and LRP8, contradicting sentence 4 (lysosomal degradation)

major / open / confirmed; issue key: cdd-cd16523-mylip-proteasomal-vs-lysosomal-ldlr-degradation.

In CDD:cd16523, sentence 2 claims that MYLIP/IDOL mediates 'ubiquitination and subsequent proteasomal degradation of myosin regulatory light chain (MRLC), low density lipoprotein receptor (LDLR), very low-density lipoprotein receptor (VLDLR) and low density lipoprotein receptor-related protein 8 (LRP8)', contradicting sentence 4 ('triggers the ubiquitination and degradation of LDLR in lysosomes') and primary literature (PMID:20884618, PMID:23225852) showing ESCRT/MVB-dependent lysosomal degradation of lipoprotein receptors. Blocked candidate: ug-75a40219c6b45df1ff1c607cf4d9a3e5e07de73f79ba1367231206244ab507c9 (Q8WY64, 383-434).

### F8: CDD:cd16652 (dRING_Rmd5p-like) contains malformed substrate/enzyme text ('fructose-1, 6-bisphosphate by fructose-1, 6-bisphosphatase (FBPase)')

minor / open / confirmed; issue key: cdd-cd16652-rmd5-malformed-fbpase-substrate-phrase.

CDD:cd16652 states that yeast Rmd5p/GID2 mediates 'the polyubiquitination and subsequent proteasomal degradation of fructose-1, 6-bisphosphate by fructose-1, 6-bisphosphatase (FBPase), phosphoenolpyruvate carboxykinase (PEPCK), cytoplasmic malate dehydrogenase'. FBPase (the enzyme, not the metabolite fructose-1,6-bisphosphate) is the ubiquitinated target. Blocked candidate: ug-4e3f322fa6f3b0c46798f889e3994a15bc8dfbeae6e94e0c6bb5eb1342632b8d (Q12508, 359-406).

### F9: CDD:cd17150 (DCX1_DCDC2B) misspells Doublecortin as Dublecortin in label/definition and switches to paralog DCDC2 disease genetics

major / open / confirmed; issue key: cdd-cd17150-dcdc2b-typo-and-dcdc2-paralog-disease-switch.

CDD:cd17150 has the typo 'Dublecortin-like domain 1' in both label and definition and switches mid-definition from DCDC2B (human A2VCK2, 17-102) to paralog DCDC2 ciliary localization and reading-disability/ADHD genetics. Blocked candidate: ug-9bf8f0912858b90c6bb97f3bf8493bd6a4c05ebcc6a5a44d6bc37cf1dc2db84e.

### F10: CDD:cd18592 (ABC_6TM_MRP5_8_9_D1) misassigns MRP7-9 to ABCC7-9 (CFTR/SUR1/SUR2) instead of ABCC10-12 and overclaims MDR efflux for ABCC12

major / open / confirmed; issue key: cdd-cd18592-abcc-mrp7-cftr-misassignment-and-mdr-overclaim.

CDD:cd18592 states 'Nine human MRPs have been identified (MRP1-9, also known as ABCC1-6 and ABCC7-9, respectively)', misassigning MRP7, MRP8, and MRP9 to ABCC7 (CFTR), ABCC8 (SUR1), and ABCC9 (SUR2) instead of ABCC10, ABCC11, and ABCC12, and attributes blanket anticancer-drug efflux across all members including ABCC12/MRP9. Blocked candidates: O15440 (ABCC5, 181-467), Q96J66 (ABCC11, 165-451), and Q96J65 (ABCC12, 125-411).

### F11: CDD:cd20534 (CYCLIN_CCNM_CCNQ_rpt1) conflates Cyclin-Q/Cyclin-M (CCNQ/FAM58A) with the CNNM1-4 (ACDP) magnesium transporter family

major / open / confirmed; issue key: cdd-cd20534-ccnq-cnnm-acdp-magnesium-transporter-conflation.

CDD:cd20534 models the first cyclin box of CCNQ/FAM58A (human Q8N1B3, 27-128, the CDK10-activating cyclin mutated in STAR syndrome), but its upstream CDD definition and PMID:14695534 evidence describe the unrelated CNNM1-4 (ACDP) CBS-pair magnesium transporter family (properly modeled by CDD:cd04590) and urofacial/hypomagnesemia/Jalili syndromes. Blocked candidate: ug-4bd7ba713556d491efbc4d9fd7d719ff9353c2fb4545d42deaa66a6c31e3a16e.

### F12: CDD:cd21551 (VEFS-box_SUZ12) claims PRC2 directly methylates both H3K9 and H3K27

major / open / confirmed; issue key: cdd-cd21551-suz12-prc2-h3k9-methylation-overclaim.

CDD:cd21551 states 'The PRC2 complex methylates Lys-9 (H3K9) and Lys-27 (H3K27) of histone H3', whereas canonical PRC2 (EZH1/EZH2 stimulated by the SUZ12 VEFS box) catalyzes H3K27me1/2/3 and reported H3K9me3 reductions upon SUZ12 loss reflect indirect cross-talk rather than intrinsic PRC2 H3K9 methyltransferase activity. Blocked candidate: ug-44aa2243f55dd0bb095beac3f1d82993fc80a2db2cb5e276dcde11e61a26c8bb (Q15022, 563-684).

## Recommended Actions And Acceptance Checks

### add-cdd-errata-and-repair-held-records

Create a guarded CDD errata module (scripts/cdd_errata.py) and registered repair script (scripts/repair_cdd_errata.py) shared with scripts/seed_cdd.py to repair the 10 held CDD records (F3-F12) with literature-backed evidence and curation_history events, then re-resolve their 12 held Stage 3 UniProt candidates.

- All 10 held CDD records carry accurate, paralog-specific definitions and literature citations.
- scripts/seed_cdd.py applies the shared CDD errata table so reseeding is idempotent and preserves curated definitions.
- scripts/validate_strict.py, scripts/validate_uniprot_grounding.py, and scripts/audit_writers.py pass with 0 errors.

### repair-promoted-cdd-typos-and-rebind

Include CDD:cd00104 (F1) and CDD:cd00959 (F2) in the shared CDD errata table and update their qualified_record_bindings.jsonl.d receipts so durable UniProt grounding validation passes against the corrected record preimages.

- CDD:cd00104 and CDD:cd00959 definitions are repaired via the registered CDD errata pathway.
- qualified_record_bindings.jsonl.d receipts match the updated record SHA-256 digests and validate_uniprot_grounding.py exits 0.

## Category Boundaries

- retain: CDD:cd09530. Retain CDD:cd09530 as a distinct SAM domain subfamily record separate from sibling CDD:cd09512 (SAM_Neurabin-like, which covers human SAMD14 Q8IZD0). Do not lump cd09530 into cd09512; instead clarify in cd09530's definition that despite the upstream CDD short_name SAM_Samd14, its human carrier is SAMD15/FAM15A (UniProtKB:Q9P1V8, 543-609).
- retain: CDD:cd20534. Retain CDD:cd20534 (first cyclin box of CCNQ/FAM58A, residues 27-128) as distinct from both sibling CDD:cd20535 (second cyclin box of CCNQ/FAM58A, residues 136-214) and CDD:cd04590 (CBS_pair_ACDP in CNNM1-4 magnesium transporters). Repair the conflated CNNM/ACDP prose and PMID:14695534 citation on cd20534 without merging domain records.
- retain: CDD:cd15894. Retain CDD:cd15894 (N-terminal Qb SNARE motif of SNAP25, residues 19-81) as distinct from sibling CDD:cd15885 (C-terminal Qc SNARE motif of SNAP25, residues 140-202) because they represent non-overlapping tandem coiled-coil SNARE domains on the same protein family.
- retain: CDD:cd17150. Retain CDD:cd17150 (DCX1_DCDC2B, human DCDC2B A2VCK2 17-102) as a distinct paralog-subfamily domain profile separate from sibling CDD:cd17151 (DCX1_DCDC2C), and correct the DCDC2 paralog switch and 'Dublecortin' typo in place.
- retain: CDD:cd00104, CDD:cd00959, CDD:cd13344, CDD:cd14999, CDD:cd16523, CDD:cd16652, CDD:cd18592, CDD:cd21551. Each of the remaining 8 CDD records represents a well-bounded conserved sequence domain class with a unique CDD PSSM accession and InterPro/Pfam hierarchy placement; their defects are definition-level prose errors requiring accession-scoped errata rather than category splitting or lumping.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| ev-cd00104 | data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml; definition, canonical_examples, evidence (PMID:6192856) | partial | Promoted CDD record (3 qualified human examples) with 'chyomotrypsin' typo and 'avian ovomucoids' mislisted as target proteases. |
| ev-cd00959 | data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml; definition, canonical_examples, ec_Anchor (EC:4.1.2.4) | partial | Promoted CDD record (2 qualified examples: E. coli P0A6L0, human Q9Y315) whose definition repeats its opening title sentence verbatim. |
| ev-cd09530 | data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml; label, short_name, definition | refutes | Names Samd14 in label and definition, whereas human SAMD14 (Q8IZD0) matches sibling CDD:cd09512 (SAM_Neurabin-like) and the sole human match for CDD:cd09530 is SAMD15/FAM15A (Q9P1V8, 543-609). |
| ev-cd09512-sibling | data/traits/sequence/domain/cdd/sam-domain-of-sam-neurabin-like-subfamily-sam-sterile-alpha-motif-doma-cd09512.yaml; id, short_name, definition | supports | Sibling CDD record cd09512 (SAM_Neurabin-like) explicitly covers human SAMD14 (Q8IZD0), confirming that cd09530 is a distinct SAM subfamily whose human member is SAMD15/FAM15A (Q9P1V8). |
| ev-cd13344 | data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml; label, short_name, definition | refutes | Record is scoped to MTMR7 (PH-GRAM_MTMR7, matching human MTMR7 Q9Y216 at 29-113), but its definition switches mid-paragraph to paralog MTMR6 and ends with a self-contradictory sentence on MTMR6 PH-GRAM phosphoinositide binding. |
| ev-cd14999 | data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml; label, short_name, definition | refutes | Erroneously aliases urotensin-II receptor (UTS2R/GPR14, Q9UKP6) as 'the hypocretin receptor' (which denotes orexin/hypocretin receptors HCRTR1/HCRTR2). |
| ev-cd15894 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml; label, short_name, definition | refutes | CDD:cd15894 (SNARE_SNAP25N, human P60880 at 19-81) states that Qb/Qc SNAREs contain a transmembrane domain, whereas SNAP25 family proteins lack a transmembrane domain and attach to membranes via palmitoylated cysteines linking the N-terminal Qb (cd15894) and C-terminal Qc (cd15885) SNARE motifs. |
| ev-cd15885-sibling | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml; id, short_name, definition | supports | Sibling CDD:cd15885 models the C-terminal Qc SNARE motif of SNAP25 (140-202), confirming that cd15894 (N-terminal Qb motif, 19-81) and cd15885 are non-overlapping tandem domain models on SNAP25. |
| ev-cd16523 | data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml; label, short_name, definition, evidence (PMID:20884618, PMID:23225852) | refutes | Sentence 2 asserts proteasomal degradation of LDLR, VLDLR, and LRP8, directly contradicting sentence 4 ('degradation of LDLR in lysosomes') and primary literature showing ESCRT/MVB lysosomal degradation of lipoprotein receptors by MYLIP/IDOL. |
| ev-cd16652 | data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml; label, short_name, definition | partial | Contains malformed enzyme/substrate text ('degradation of fructose-1, 6-bisphosphate by fructose-1, 6-bisphosphatase (FBPase)') in the list of gluconeogenic enzymes ubiquitinated by the yeast GID/CTLH complex (Rmd5p/Q12508). |
| ev-cd17150 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml; label, short_name, definition | refutes | Begins with typo 'Dublecortin-like domain 1' in both label and definition, and switches mid-definition from DCDC2B (human A2VCK2, 17-102) to paralog DCDC2 ciliary/dyslexia/ADHD claims. |
| ev-cd17151-sibling | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml; id, short_name, label, definition | supports | Sibling CDD:cd17151 (DCX1_DCDC2C) models the first DCX domain of paralog DCDC2C, confirming that cd17150 (DCX1_DCDC2B) and cd17151 are distinct paralog-subfamily domain profiles. |
| ev-cd18592 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml; label, short_name, definition | refutes | Misassigns MRP7-9 to ABCC7-9 (where ABCC7 is CFTR and ABCC8/ABCC9 are SUR1/SUR2 sulfonylurea receptors) instead of ABCC10-12 (MRP7=ABCC10, MRP8=ABCC11, MRP9=ABCC12), and overclaims multidrug-resistance drug export across all members including ABCC12 (Q96J65). |
| ev-cd20534 | data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml; label, short_name, definition, evidence (PMID:14695534) | refutes | CDD:cd20534 (CYCLIN_CCNM_CCNQ_rpt1, matching human CCNQ/FAM58A Q8N1B3 at 27-128) conflates Cyclin-Q/Cyclin-M (CCNQ/FAM58A, the CDK10-activating cyclin mutated in STAR syndrome) with the unrelated CNNM1-4 (ACDP) magnesium transporter family and cites an ACDP paper (PMID:14695534). |
| ev-cd20535-cd04590-siblings | data/traits/sequence/domain/cdd/two-tandem-repeats-of-the-cystathionine-beta-synthase-cbs-pair-domains-cd04590.yaml; CDD:cd04590 (CBS_pair_ACDP) and CDD:cd20535 (CYCLIN_CCNM_CCNQ_rpt2) | supports | CDD:cd04590 (CBS_pair_ACDP) legitimately models the CNNM/ACDP magnesium transporter CBS-pair domain, whereas CDD:cd20534 and CDD:cd20535 model the first and second cyclin boxes of CCNQ/FAM58A. |
| ev-cd21551 | data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml; label, short_name, definition, evidence (PMID:14998897, PMID:16630888) | refutes | CDD:cd21551 (VEFS-box_SUZ12, human Q15022 at 563-684) claims direct PRC2 methylation of both H3K9 and H3K27, whereas PRC2/EZH2 catalyzes H3K27me1/2/3 and H3K9me3 changes upon SUZ12 knockdown reflect secondary/indirect cross-talk. |
| ev-cdd-batch058 | INFRA_TASKS.md; proteintraitsmech-infra-0003 (Stage 3 batch 058of128 holds for cd09530, cd16523, cd16652, cd18592, cd20534, cd21551 and promotion for cd00959) | supports | Committed Stage 3 infrastructure intake entry (proteintraitsmech-infra-0003) recording HOLD_FOR_PROSE_CURATION decisions for 8 candidate rows across 6 CDD records and approved promotions for CDD:cd00959 in batch 058of128. |
| ev-cdd-batch066 | INFRA_TASKS.md; proteintraitsmech-infra-0003 (Stage 3 batch 066of128 holds for cd13344, cd14999, cd15894, cd17150 and promotion for cd00104) | supports | Committed Stage 3 infrastructure intake entry (proteintraitsmech-infra-0003) recording HOLD_PROSE_REVIEW decisions for 4 candidate rows across 4 CDD records and approved promotions for CDD:cd00104 in batch 066of128. |
| ev-seed-cdd-cohort | scripts/seed_cdd.py; seed_cdd() | supports | scripts/seed_cdd.py ingests raw CDD descriptions from cddid_all.tbl without an accession-keyed errata override table, making all 12 CDD prose defects share a single seeder/repair root cause. |

## Limits And Additional Notes

- This review covers the frozen 12-record CDD SEQ_DOMAIN inventory surfaced during Stage 3 grounding review; other CDD records outside this cohort were not re-audited.
- No scientific trait records under data/traits/ were edited during Stage 4; all 12 findings remain open for Stage 5 grouped remediation.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261022T052300Z-cdd-stage3-domain-cohort-review
kind: category
repository: CultureBotAI/proteintraitsmech
title: Cohort scientific review of 12 Stage 3 CDD sequence-domain records with upstream
  prose and nomenclature defects
started_at: '2026-10-22T05:06:00Z'
finished_at: '2026-10-22T05:23:00Z'
reviewer:
  identity: Antigravity
  kind: agent
  model: Claude Opus 4.6
  independence: independent
  independence_basis: Stage 4 cohort scientific review of the frozen 12-record CDD
    SEQ_DOMAIN inventory and 5 sibling CDD boundary records without modifying scientific
    records.
skill: review-yaml-category
completion: completed
verdict: needs_curation
native_verdict: COHORT_NEEDS_CURATION_12_OPEN_FINDINGS
scientific_review: true
summary: 'Full cohort review of all 12 eligible CDD sequence-domain records in the
  frozen Stage 4 inventory (10 records held at Stage 3 grounding review due to upstream
  CDD definition contradictions plus 2 promoted records with minor upstream typographical/wording
  defects). All 12 records pass strict LinkML schema validation and represent genuine,
  distinct conserved sequence domain classes (SEQ_DOMAIN on SEQUENCE) that should
  be retained as separate records rather than lumped with sibling CDD profiles. Twelve
  open findings (F1-F12: 9 major, 3 minor) share a single root cause in scripts/seed_cdd.py
  and are preserved for Stage 5 grouped remediation.'
source:
  git_revision: 32b4f33a71b846acf59b96b7da7282f293ea2165
  state: git_commit
  inputs:
  - path: INFRA_TASKS.md
    sha256: 8393fd14c2c14e94415284edce027f2365cdc11d34db1a8fa65c4843240bfc38
    role: context
  - path: data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    sha256: e131f3ec97c0e75830bc67a3f73046509ce0ddd3fc148f7b8e5f3cf05eba5ab0
    role: target
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
    sha256: 91529c2545061d6f49418adfef6db7d2ab2e530d5c7eee801862fb0a3255edea
    role: context
  - path: data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml
    sha256: e15b95997315b996a6488ab375071f3e7db65f626e84d91703a9d6168e6b0029
    role: target
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    sha256: 587b8c22dc5e29192acb9f1b74ffeeb815729223f478bc32020aacb8e6fe6e0b
    role: target
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    sha256: 6b23146bd71c843c2675704f6fbbea6b32f4fe113894c8bbeebf85ab6cb8438d
    role: context
  - path: data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
    sha256: e960b87e4e30cb1624627e3a4b8e01ac2a181c0ffe6bdedba3082edd7fa06f11
    role: target
  - path: data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    sha256: d610ab5380c1acad721ab560c9bcbde995d73d47906cc947f56ada7b20158e52
    role: target
  - path: data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml
    sha256: 25f25b4811e49099c08936c3489d0d1d02339cc8449e5621d2452941c9d6d2d2
    role: target
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
    sha256: 1c763a03debd0194ab731f4cd1facdc5a506578a252388a409fe3ceb9f30425d
    role: target
  - path: data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml
    sha256: 3620b0d7f29bbc2778450e3a9730a1433348af1f13ba8786e3a09106ca0583e4
    role: target
  - path: data/traits/sequence/domain/cdd/sam-domain-of-sam-neurabin-like-subfamily-sam-sterile-alpha-motif-doma-cd09512.yaml
    sha256: 93169846893c6adcec5e674c004b89357f4a2cef1001e5137d1e76a980c312e4
    role: context
  - path: data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml
    sha256: 36e62ccee26da135fc9a3d26f625be68fcdbf7966d35fabb13971dd13c443957
    role: target
  - path: data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
    sha256: 8424b28b9d91f750c4edcdb8cafa59d9d340f4cacb46938cc3355f2d65457074
    role: context
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
    sha256: 819db68ddb4bd173baa067ff5908f9a7e90de8781735097ff24bed8e2c7f4c1f
    role: target
  - path: data/traits/sequence/domain/cdd/two-tandem-repeats-of-the-cystathionine-beta-synthase-cbs-pair-domains-cd04590.yaml
    sha256: 5bfd6d04f6c15aad7dd69ca34e3c88ae6dbad3d07023a8e1cba85eee3a719274
    role: context
  - path: data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml
    sha256: 29cb639a3bbf2158faa5680b179a1d1e4c6c392928321359db55344eb23e5df5
    role: target
  - path: data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml
    sha256: ff603a20dd777948e50bd44c88575bdd8b4cf442e46f70d3df62bfba5a85e7d4
    role: target
  - path: scripts/record_io.py
    sha256: ef18d4a2224810768232337f1007cb757425bff87aa96edd1e6b193da14863bf
    role: context
  - path: scripts/seed_cdd.py
    sha256: 09dfcecfb251e8b86a9b15de1a07e63c5c28fcd81ca5f4a13c91f32091729274
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Frozen 12-record CDD SEQ_DOMAIN cohort surfaced during Stage 3 UniProt
    grounding batches human-ecoli-yeast-complete-cdd-058of128 and 066of128 and tracked
    under proteintraitsmech-infra-0003.
  selection: Every CDD record in Stage 3 batches 058of128 and 066of128 that exhibited
    an upstream CDD definition, nomenclature, paralog-scope, or substrate/pathway
    defect (10 held records blocking 12 human/yeast UniProt examples plus 2 promoted
    records with minor prose defects).
  coverage: full
  population_size: 12
  reviewed_target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  exclusions:
  - target: Remaining 128 promoted CDD records in batches 058of128 and 066of128 without
      prose defects
    reason: Already passed Stage 3 scientific review and promotion without prose or
      nomenclature holds.
  - target: Sibling CDD records cd09512, cd04590, cd20535, cd15885, and cd17151
    reason: Inspected as boundary-contrast context inputs; sibling propagation for
      cd15885, cd17151, and cd20535 is documented in findings F6, F9, and F11.
targets:
- target_id: CDD:cd00104
  path: data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
  label: Kazal-type serine protease inhibitors and follistatin-like domains
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: d610ab5380c1acad721ab560c9bcbde995d73d47906cc947f56ada7b20158e52
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd00959
  path: data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
  label: 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: e131f3ec97c0e75830bc67a3f73046509ce0ddd3fc148f7b8e5f3cf05eba5ab0
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd09530
  path: data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml
  label: SAM domain of SAMD14 subfamily
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 36e62ccee26da135fc9a3d26f625be68fcdbf7966d35fabb13971dd13c443957
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd13344
  path: data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml
  label: Myotubularian (MTM)-related 7 protein (MTMR7) Pleckstrin homology-Glucosyltransferases,
    Rab-like GTPase activators and Myotubularins (PH-GRAM) domain
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 25f25b4811e49099c08936c3489d0d1d02339cc8449e5621d2452941c9d6d2d2
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd14999
  path: data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml
  label: Urotensin-II receptor, member of the class A family of seven-transmembrane
    G protein-coupled receptors
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 29cb639a3bbf2158faa5680b179a1d1e4c6c392928321359db55344eb23e5df5
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd15894
  path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
  label: N-terminal SNARE motif of SNAP25
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 1c763a03debd0194ab731f4cd1facdc5a506578a252388a409fe3ceb9f30425d
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd16523
  path: data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml
  label: RING finger, HC subclass, found in myosin regulatory light chain interacting
    protein (MYLIP) and similar proteins
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 3620b0d7f29bbc2778450e3a9730a1433348af1f13ba8786e3a09106ca0583e4
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd16652
  path: data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml
  label: Degenerated RING (dRING) finger found in Saccharomyces cerevisiae required
    for meiotic nuclear division protein 5 (Rmd5p) and similar proteins
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: e15b95997315b996a6488ab375071f3e7db65f626e84d91703a9d6168e6b0029
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd17150
  path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
  label: Dublecortin-like domain 1 found in doublecortin domain-containing protein
    2B (DCDC2B) and similar proteins
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 587b8c22dc5e29192acb9f1b74ffeeb815729223f478bc32020aacb8e6fe6e0b
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd18592
  path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
  label: Six-transmembrane helical domain 1 (TMD1) of multidrug resistance-associated
    proteins MRP5, MRP8, and MRP9
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 819db68ddb4bd173baa067ff5908f9a7e90de8781735097ff24bed8e2c7f4c1f
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd20534
  path: data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
  label: First cyclin box found in cyclin-M (CCNM) family
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: e960b87e4e30cb1624627e3a4b8e01ac2a181c0ffe6bdedba3082edd7fa06f11
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd21551
  path: data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml
  label: VEFS (VRN2-EMF2-FIS2-Su(z)12) box found in suppressor of zeste 12 protein
    homolog (SUZ12) and similar proteins
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: ff603a20dd777948e50bd44c88575bdd8b4cf442e46f70d3df62bfba5a85e7d4
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
checks:
- check_id: schema
  name: Strict LinkML and OAK ontology-binding validation across all 12 cohort records
  command: .venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv
    data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml
    data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml
    data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
    data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml
    data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
    data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
    data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml
  exit_code: 0
  status: passed
  required: true
  summary: All 12 CDD cohort records pass closed LinkML schema validation and OAK
    ontology-term checks with 0 errors.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd09530
  - ev-cd09512-sibling
  - ev-cd13344
  - ev-cd14999
  - ev-cd15894
  - ev-cd15885-sibling
  - ev-cd16523
  - ev-cd16652
  - ev-cd17150
  - ev-cd17151-sibling
- check_id: semantic
  name: Release-pinned UniProt grounding and binding replay across all 12 cohort records
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv
    data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml
    data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml
    data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
    data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml
    data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
    data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
    data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml
  exit_code: 0
  status: passed
  required: true
  summary: 12 files scanned, 21,331 qualified record bindings verified, 0 semantic
    findings; promoted examples on CDD:cd00104 and CDD:cd00959 replay cleanly and
    the 10 held records remain unpromoted as expected.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cdd-batch058
  - ev-cdd-batch066
- check_id: graphs
  name: Causal-graph audit across all 12 cohort records
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml
    data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml
    data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
    data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml
    data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
    data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
    data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml
  exit_code: 0
  status: passed
  required: false
  summary: 0 records with causal_graphs, 0 errors, 0 warnings.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd09530
  - ev-cd09512-sibling
  - ev-cd13344
  - ev-cd14999
  - ev-cd15894
  - ev-cd15885-sibling
  - ev-cd16523
  - ev-cd16652
  - ev-cd17150
  - ev-cd17151-sibling
- check_id: writer-audit
  name: Registered write-route audit
  command: .venv/bin/python scripts/audit_writers.py
  exit_code: 0
  status: passed
  required: true
  summary: 616 scripts examined, 0 unguarded writer findings.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-seed-cdd-cohort
- check_id: history
  name: Append-only curation history validation
  command: .venv/bin/python -c "import glob, sys, linkml.validator as v; sys.exit(sum(1
    for f in sorted(glob.glob('history/*.yaml')) for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml',
    'CurationHistoryRecord').results))"
  exit_code: 0
  status: passed
  required: true
  summary: All 13 history records validate against src/proteintraitsmech/schema/history.yaml
    with 0 errors.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-seed-cdd-cohort
evidence:
- evidence_id: ev-cd00104
  kind: record_content
  reference: data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
  locator: definition, canonical_examples, evidence (PMID:6192856)
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: d610ab5380c1acad721ab560c9bcbde995d73d47906cc947f56ada7b20158e52
  support: partial
  quote: Kazal inhibitors inhibit serine proteases, such as, trypsin, chyomotrypsin,
    avian ovomucoids, and elastases
  summary: Promoted CDD record (3 qualified human examples) with 'chyomotrypsin' typo
    and 'avian ovomucoids' mislisted as target proteases.
- evidence_id: ev-cd00959
  kind: record_content
  reference: data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
  locator: definition, canonical_examples, ec_Anchor (EC:4.1.2.4)
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: e131f3ec97c0e75830bc67a3f73046509ce0ddd3fc148f7b8e5f3cf05eba5ab0
  support: partial
  quote: 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. 2-deoxyribose-5-phosphate
    aldolase (DERA) of the DeoC family.
  summary: 'Promoted CDD record (2 qualified examples: E. coli P0A6L0, human Q9Y315)
    whose definition repeats its opening title sentence verbatim.'
- evidence_id: ev-cd09530
  kind: record_content
  reference: data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 36e62ccee26da135fc9a3d26f625be68fcdbf7966d35fabb13971dd13c443957
  support: refutes
  quote: SAM (sterile alpha motif) domain of Samd14 (sterile alpha motif domain-containing
    protein 14) and similar proteins.
  summary: Names Samd14 in label and definition, whereas human SAMD14 (Q8IZD0) matches
    sibling CDD:cd09512 (SAM_Neurabin-like) and the sole human match for CDD:cd09530
    is SAMD15/FAM15A (Q9P1V8, 543-609).
- evidence_id: ev-cd09512-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/sam-domain-of-sam-neurabin-like-subfamily-sam-sterile-alpha-motif-doma-cd09512.yaml
  locator: id, short_name, definition
  accessed_at: '2026-10-22T05:11:00Z'
  snapshot_sha256: 93169846893c6adcec5e674c004b89357f4a2cef1001e5137d1e76a980c312e4
  support: supports
  quote: SAM (sterile alpha motif) domain of Neurabin-I, Spinophilin (also known as
    Neurabin-II), Samd14 (sterile alpha motif domain-containing protein 14) and similar
    proteins.
  summary: Sibling CDD record cd09512 (SAM_Neurabin-like) explicitly covers human
    SAMD14 (Q8IZD0), confirming that cd09530 is a distinct SAM subfamily whose human
    member is SAMD15/FAM15A (Q9P1V8).
- evidence_id: ev-cd13344
  kind: record_content
  reference: data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 25f25b4811e49099c08936c3489d0d1d02339cc8449e5621d2452941c9d6d2d2
  support: refutes
  quote: Within the MTM family, MTMR6 is catalytically active and dephosphorylates
    phosphatidylinositol 3-phosphate (PI(3)P) and PI(3,5)P2... It is not clear if
    the PH-GRAM domain of MTMR6 binds to phosphoinositides, with a study showing that
    the PH-GRAM domain of MTMR6 does not bind to phosphoinositides.
  summary: Record is scoped to MTMR7 (PH-GRAM_MTMR7, matching human MTMR7 Q9Y216 at
    29-113), but its definition switches mid-paragraph to paralog MTMR6 and ends with
    a self-contradictory sentence on MTMR6 PH-GRAM phosphoinositide binding.
- evidence_id: ev-cd14999
  kind: record_content
  reference: data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 29cb639a3bbf2158faa5680b179a1d1e4c6c392928321359db55344eb23e5df5
  support: refutes
  quote: The urotensin-II receptor (also known as G-protein coupled receptor 14, GPR14,
    or the hypocretin receptor) is a receptor for the cyclic undecapeptide urotensin-II.
  summary: Erroneously aliases urotensin-II receptor (UTS2R/GPR14, Q9UKP6) as 'the
    hypocretin receptor' (which denotes orexin/hypocretin receptors HCRTR1/HCRTR2).
- evidence_id: ev-cd15894
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 1c763a03debd0194ab731f4cd1facdc5a506578a252388a409fe3ceb9f30425d
  support: refutes
  quote: Both, Qb/Qc SNAREs consist of 2 coiled-coil helices (which form a single
    SNARE domain) and a transmembrane domain.
  summary: CDD:cd15894 (SNARE_SNAP25N, human P60880 at 19-81) states that Qb/Qc SNAREs
    contain a transmembrane domain, whereas SNAP25 family proteins lack a transmembrane
    domain and attach to membranes via palmitoylated cysteines linking the N-terminal
    Qb (cd15894) and C-terminal Qc (cd15885) SNARE motifs.
- evidence_id: ev-cd15885-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
  locator: id, short_name, definition
  accessed_at: '2026-10-22T05:11:00Z'
  snapshot_sha256: 91529c2545061d6f49418adfef6db7d2ab2e530d5c7eee801862fb0a3255edea
  support: supports
  summary: Sibling CDD:cd15885 models the C-terminal Qc SNARE motif of SNAP25 (140-202),
    confirming that cd15894 (N-terminal Qb motif, 19-81) and cd15885 are non-overlapping
    tandem domain models on SNAP25.
- evidence_id: ev-cd16523
  kind: record_content
  reference: data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml
  locator: label, short_name, definition, evidence (PMID:20884618, PMID:23225852)
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 3620b0d7f29bbc2778450e3a9730a1433348af1f13ba8786e3a09106ca0583e4
  support: refutes
  quote: MYLIP functions as an E3 ubiquitin-protein ligase that mediates ubiquitination
    and subsequent proteasomal degradation of myosin regulatory light chain (MRLC),
    low density lipoprotein receptor (LDLR), very low-density lipoprotein receptor
    (VLDLR) and low density lipoprotein receptor-related protein 8 (LRP8)... It triggers
    the ubiquitination and degradation of LDLR in lysosomes.
  summary: Sentence 2 asserts proteasomal degradation of LDLR, VLDLR, and LRP8, directly
    contradicting sentence 4 ('degradation of LDLR in lysosomes') and primary literature
    showing ESCRT/MVB lysosomal degradation of lipoprotein receptors by MYLIP/IDOL.
- evidence_id: ev-cd16652
  kind: record_content
  reference: data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: e15b95997315b996a6488ab375071f3e7db65f626e84d91703a9d6168e6b0029
  support: partial
  quote: mediates the polyubiquitination and subsequent proteasomal degradation of
    fructose-1, 6-bisphosphate by fructose-1, 6-bisphosphatase (FBPase), phosphoenolpyruvate
    carboxykinase (PEPCK), cytoplasmic malate dehydrogenase, and incoming proteins
  summary: Contains malformed enzyme/substrate text ('degradation of fructose-1, 6-bisphosphate
    by fructose-1, 6-bisphosphatase (FBPase)') in the list of gluconeogenic enzymes
    ubiquitinated by the yeast GID/CTLH complex (Rmd5p/Q12508).
- evidence_id: ev-cd17150
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 587b8c22dc5e29192acb9f1b74ffeeb815729223f478bc32020aacb8e6fe6e0b
  support: refutes
  quote: Dublecortin-like domain 1 found in doublecortin domain-containing protein
    2B (DCDC2B) and similar proteins. DCDC2B is a member of the doublecortin family...
    DCDC2 is localized to the ciliary axoneme... Mutations in DCDC2 have been associated
    with reading disability (RD) and attention-deficit/hyperactivity disorder (ADHD).
  summary: Begins with typo 'Dublecortin-like domain 1' in both label and definition,
    and switches mid-definition from DCDC2B (human A2VCK2, 17-102) to paralog DCDC2
    ciliary/dyslexia/ADHD claims.
- evidence_id: ev-cd17151-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
  locator: id, short_name, label, definition
  accessed_at: '2026-10-22T05:11:00Z'
  snapshot_sha256: 6b23146bd71c843c2675704f6fbbea6b32f4fe113894c8bbeebf85ab6cb8438d
  support: supports
  summary: Sibling CDD:cd17151 (DCX1_DCDC2C) models the first DCX domain of paralog
    DCDC2C, confirming that cd17150 (DCX1_DCDC2B) and cd17151 are distinct paralog-subfamily
    domain profiles.
- evidence_id: ev-cd18592
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
  locator: label, short_name, definition
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: 819db68ddb4bd173baa067ff5908f9a7e90de8781735097ff24bed8e2c7f4c1f
  support: refutes
  quote: Nine human MRPs have been identified (MRP1-9, also known as ABCC1-6 and ABCC7-9,
    respectively)... They are unidirectional efflux transporters that mediate the
    ATP-dependent export of organic anions, including cytotoxic and antiviral drugs,
    and confer resistance to multiple anticancer drugs in tumor cells.
  summary: Misassigns MRP7-9 to ABCC7-9 (where ABCC7 is CFTR and ABCC8/ABCC9 are SUR1/SUR2
    sulfonylurea receptors) instead of ABCC10-12 (MRP7=ABCC10, MRP8=ABCC11, MRP9=ABCC12),
    and overclaims multidrug-resistance drug export across all members including ABCC12
    (Q96J65).
- evidence_id: ev-cd20534
  kind: record_content
  reference: data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
  locator: label, short_name, definition, evidence (PMID:14695534)
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: e960b87e4e30cb1624627e3a4b8e01ac2a181c0ffe6bdedba3082edd7fa06f11
  support: refutes
  quote: The CCNM family proteins, also known as ancient conserved domain-containing
    proteins (ACDPs), are involved in magnesium homeostasis. Mutations in CCNM1 (also
    known as ACDP1) are associated with urofacial syndrome, while mutations in CCNM2
    and CCNM4 are associated with hypomagnesemia and Jalili syndrome, respectively.
  summary: CDD:cd20534 (CYCLIN_CCNM_CCNQ_rpt1, matching human CCNQ/FAM58A Q8N1B3 at
    27-128) conflates Cyclin-Q/Cyclin-M (CCNQ/FAM58A, the CDK10-activating cyclin
    mutated in STAR syndrome) with the unrelated CNNM1-4 (ACDP) magnesium transporter
    family and cites an ACDP paper (PMID:14695534).
- evidence_id: ev-cd20535-cd04590-siblings
  kind: record_content
  reference: data/traits/sequence/domain/cdd/two-tandem-repeats-of-the-cystathionine-beta-synthase-cbs-pair-domains-cd04590.yaml
  locator: CDD:cd04590 (CBS_pair_ACDP) and CDD:cd20535 (CYCLIN_CCNM_CCNQ_rpt2)
  accessed_at: '2026-10-22T05:11:00Z'
  snapshot_sha256: 5bfd6d04f6c15aad7dd69ca34e3c88ae6dbad3d07023a8e1cba85eee3a719274
  support: supports
  summary: CDD:cd04590 (CBS_pair_ACDP) legitimately models the CNNM/ACDP magnesium
    transporter CBS-pair domain, whereas CDD:cd20534 and CDD:cd20535 model the first
    and second cyclin boxes of CCNQ/FAM58A.
- evidence_id: ev-cd21551
  kind: record_content
  reference: data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml
  locator: label, short_name, definition, evidence (PMID:14998897, PMID:16630888)
  accessed_at: '2026-10-22T05:10:00Z'
  snapshot_sha256: ff603a20dd777948e50bd44c88575bdd8b4cf442e46f70d3df62bfba5a85e7d4
  support: refutes
  quote: The PRC2 complex methylates 'Lys-9' (H3K9) and 'Lys-27' (H3K27) of histone
    H3, leading to transcriptional repression of the affected target genes.
  summary: CDD:cd21551 (VEFS-box_SUZ12, human Q15022 at 563-684) claims direct PRC2
    methylation of both H3K9 and H3K27, whereas PRC2/EZH2 catalyzes H3K27me1/2/3 and
    H3K9me3 changes upon SUZ12 knockdown reflect secondary/indirect cross-talk.
- evidence_id: ev-cdd-batch058
  kind: record_content
  reference: INFRA_TASKS.md
  locator: proteintraitsmech-infra-0003 (Stage 3 batch 058of128 holds for cd09530,
    cd16523, cd16652, cd18592, cd20534, cd21551 and promotion for cd00959)
  accessed_at: '2026-10-22T05:14:00Z'
  snapshot_sha256: 8393fd14c2c14e94415284edce027f2365cdc11d34db1a8fa65c4843240bfc38
  support: supports
  summary: Committed Stage 3 infrastructure intake entry (proteintraitsmech-infra-0003)
    recording HOLD_FOR_PROSE_CURATION decisions for 8 candidate rows across 6 CDD
    records and approved promotions for CDD:cd00959 in batch 058of128.
- evidence_id: ev-cdd-batch066
  kind: record_content
  reference: INFRA_TASKS.md
  locator: proteintraitsmech-infra-0003 (Stage 3 batch 066of128 holds for cd13344,
    cd14999, cd15894, cd17150 and promotion for cd00104)
  accessed_at: '2026-10-22T05:14:00Z'
  snapshot_sha256: 8393fd14c2c14e94415284edce027f2365cdc11d34db1a8fa65c4843240bfc38
  support: supports
  summary: Committed Stage 3 infrastructure intake entry (proteintraitsmech-infra-0003)
    recording HOLD_PROSE_REVIEW decisions for 4 candidate rows across 4 CDD records
    and approved promotions for CDD:cd00104 in batch 066of128.
- evidence_id: ev-seed-cdd-cohort
  kind: record_content
  reference: scripts/seed_cdd.py
  locator: seed_cdd()
  accessed_at: '2026-10-22T05:15:00Z'
  snapshot_sha256: 09dfcecfb251e8b86a9b15de1a07e63c5c28fcd81ca5f4a13c91f32091729274
  support: supports
  summary: scripts/seed_cdd.py ingests raw CDD descriptions from cddid_all.tbl without
    an accession-keyed errata override table, making all 12 CDD prose defects share
    a single seeder/repair root cause.
assessments:
- assessment_id: cohort-boundaries-and-identity
  area: scope
  topic: Category placement and subfamily boundary distinctness across all 12 CDD
    records
  outcome: supported
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd09530
  - ev-cd09512-sibling
  - ev-cd13344
  - ev-cd14999
  - ev-cd15894
  - ev-cd15885-sibling
  - ev-cd16523
  - ev-cd16652
  - ev-cd17150
  - ev-cd17151-sibling
  - ev-cd18592
  - ev-cd20534
  - ev-cd20535-cd04590-siblings
  - ev-cd21551
  - ev-cdd-batch058
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  summary: 'All 12 records are genuine conserved protein sequence domain profiles
    (trait_axis: SEQUENCE, trait_category: SEQ_DOMAIN, so_term: SO:0000417) with distinct
    CDD PSSM identifiers and non-redundant domain intervals or paralog subfamily scopes.
    None should be merged or lumped with sibling CDD profiles.'
- assessment_id: promoted-records-minor-prose-defects
  area: consistency
  topic: Minor typographical and target-list prose defects on promoted records CDD:cd00104
    and CDD:cd00959
  outcome: concern
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cdd-batch058
  - ev-cdd-batch066
  summary: CDD:cd00104 (3 qualified human examples) and CDD:cd00959 (2 qualified E.
    coli/human examples) have valid biological groundings, but carry upstream CDD
    typos/duplications ('chyomotrypsin' and 'avian ovomucoids' in cd00104; duplicated
    title sentence in cd00959).
- assessment_id: held-records-major-prose-and-nomenclature-defects
  area: consistency
  topic: Upstream CDD nomenclature, paralog-scope, and biochemical contradictions
    on 10 held records
  outcome: concern
  target_ids:
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  evidence_ids:
  - ev-cd09530
  - ev-cd09512-sibling
  - ev-cd13344
  - ev-cd14999
  - ev-cd15894
  - ev-cd15885-sibling
  - ev-cd16523
  - ev-cd16652
  - ev-cd17150
  - ev-cd17151-sibling
  - ev-cd18592
  - ev-cd20534
  - ev-cd20535-cd04590-siblings
  - ev-cd21551
  - ev-cdd-batch058
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  summary: Ten CDD records contain upstream CDD prose defects that conflict with their
    matched Swiss-Prot carriers or biochemical mechanisms, blocking promotion of 12
    Stage 3 human/yeast UniProt candidates until repaired via a guarded CDD errata
    module and re-resolved.
boundary_decisions:
- action: retain
  target_ids:
  - CDD:cd09530
  evidence_ids:
  - ev-cd09530
  - ev-cd09512-sibling
  - ev-cdd-batch058
  rationale: Retain CDD:cd09530 as a distinct SAM domain subfamily record separate
    from sibling CDD:cd09512 (SAM_Neurabin-like, which covers human SAMD14 Q8IZD0).
    Do not lump cd09530 into cd09512; instead clarify in cd09530's definition that
    despite the upstream CDD short_name SAM_Samd14, its human carrier is SAMD15/FAM15A
    (UniProtKB:Q9P1V8, 543-609).
- action: retain
  target_ids:
  - CDD:cd20534
  evidence_ids:
  - ev-cd20534
  - ev-cd20535-cd04590-siblings
  - ev-cdd-batch058
  rationale: Retain CDD:cd20534 (first cyclin box of CCNQ/FAM58A, residues 27-128)
    as distinct from both sibling CDD:cd20535 (second cyclin box of CCNQ/FAM58A, residues
    136-214) and CDD:cd04590 (CBS_pair_ACDP in CNNM1-4 magnesium transporters). Repair
    the conflated CNNM/ACDP prose and PMID:14695534 citation on cd20534 without merging
    domain records.
- action: retain
  target_ids:
  - CDD:cd15894
  evidence_ids:
  - ev-cd15894
  - ev-cd15885-sibling
  - ev-cdd-batch066
  rationale: Retain CDD:cd15894 (N-terminal Qb SNARE motif of SNAP25, residues 19-81)
    as distinct from sibling CDD:cd15885 (C-terminal Qc SNARE motif of SNAP25, residues
    140-202) because they represent non-overlapping tandem coiled-coil SNARE domains
    on the same protein family.
- action: retain
  target_ids:
  - CDD:cd17150
  evidence_ids:
  - ev-cd17150
  - ev-cd17151-sibling
  - ev-cdd-batch066
  rationale: Retain CDD:cd17150 (DCX1_DCDC2B, human DCDC2B A2VCK2 17-102) as a distinct
    paralog-subfamily domain profile separate from sibling CDD:cd17151 (DCX1_DCDC2C),
    and correct the DCDC2 paralog switch and 'Dublecortin' typo in place.
- action: retain
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd18592
  - CDD:cd21551
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd13344
  - ev-cd14999
  - ev-cd16523
  - ev-cd16652
  - ev-cd18592
  - ev-cd21551
  rationale: Each of the remaining 8 CDD records represents a well-bounded conserved
    sequence domain class with a unique CDD PSSM accession and InterPro/Pfam hierarchy
    placement; their defects are definition-level prose errors requiring accession-scoped
    errata rather than category splitting or lumping.
findings:
- finding_id: F1
  issue_key: cdd-cd00104-kazal-definition-typo-and-inhibitor-target-confusion
  category: consistency
  severity: minor
  status: open
  certainty: confirmed
  title: CDD:cd00104 definition misspells chymotrypsin and lists avian ovomucoids
    as target serine proteases
  description: CDD:cd00104 definition states 'Kazal inhibitors inhibit serine proteases,
    such as, trypsin, chyomotrypsin, avian ovomucoids, and elastases', misspelling
    'chymotrypsin' and listing 'avian ovomucoids' (which are Kazal-type inhibitor
    proteins, PMID:6192856) as target enzymes.
  target_ids:
  - CDD:cd00104
  field_paths:
  - data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml#/definition
  evidence_ids:
  - ev-cd00104
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F2
  issue_key: cdd-cd00959-dera-duplicated-opening-sentence
  category: consistency
  severity: minor
  status: open
  certainty: confirmed
  title: CDD:cd00959 definition repeats its opening title sentence verbatim
  description: CDD:cd00959 definition begins with the duplicated sentence '2-deoxyribose-5-phosphate
    aldolase (DERA) of the DeoC family. 2-deoxyribose-5-phosphate aldolase (DERA)
    of the DeoC family.' due to upstream CDD title+description concatenation in scripts/seed_cdd.py.
  target_ids:
  - CDD:cd00959
  field_paths:
  - data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml#/definition
  evidence_ids:
  - ev-cd00959
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F3
  issue_key: cdd-cd09530-samd14-vs-samd15-nomenclature-conflict
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd09530 names Samd14 in label/definition whereas its human carrier is
    SAMD15 (Q9P1V8) and human SAMD14 (Q8IZD0) matches CDD:cd09512
  description: CDD:cd09530 (short_name SAM_Samd14) defines the domain as 'SAM domain
    of Samd14 (sterile alpha motif domain-containing protein 14) and similar proteins',
    without noting that human SAMD14 (UniProtKB:Q8IZD0) is classified under sibling
    CDD:cd09512 (SAM_Neurabin-like) while the actual human protein matched by CDD:cd09530
    in InterPro/CDD is SAMD15/FAM15A (UniProtKB:Q9P1V8, residues 543-609). This nomenclature
    conflict blocked Stage 3 promotion of candidate ug-261dc8be43fe67ef5a89ce9ecdbdd8107e3ab08802277a3f574bf5c5f9b8c78b.
  target_ids:
  - CDD:cd09530
  field_paths:
  - data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml#/definition
  evidence_ids:
  - ev-cd09530
  - ev-cd09512-sibling
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F4
  issue_key: cdd-cd13344-mtmr7-paralog-mtmr6-contradiction
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd13344 (PH-GRAM_MTMR7) switches mid-definition to paralog MTMR6 and
    ends with a self-contradictory phosphoinositide-binding sentence
  description: CDD:cd13344 represents the PH-GRAM domain of MTMR7 (human Q9Y216, 29-113),
    but sentences 2 and 5 switch without qualification to paralog MTMR6 catalytic
    activity and end with the self-contradictory statement 'It is not clear if the
    PH-GRAM domain of MTMR6 binds to phosphoinositides, with a study showing that
    the PH-GRAM domain of MTMR6 does not bind to phosphoinositides', blocking Stage
    3 promotion of candidate ug-dc9e5d1720249523285386416d18a96bb231173b464db6621df6a3f0ba42c240.
  target_ids:
  - CDD:cd13344
  field_paths:
  - data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml#/definition
  evidence_ids:
  - ev-cd13344
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F5
  issue_key: cdd-cd14999-uts2r-hypocretin-receptor-misaliasing
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd14999 erroneously aliases urotensin-II receptor (UTS2R/GPR14) as the
    hypocretin receptor
  description: CDD:cd14999 (7tmA_UII-R) states 'The urotensin-II receptor (also known
    as G-protein coupled receptor 14, GPR14, or the hypocretin receptor) is a receptor
    for the cyclic undecapeptide urotensin-II'. Hypocretin/orexin receptors (HCRTR1/HCRTR2)
    are distinct GPCRs; UTS2R/GPR14 is not the hypocretin receptor. This misaliasing
    blocked Stage 3 promotion of human UTS2R candidate ug-4ca0bc07c3ff11d11874a90b7bcbb2b3c258f9ecae390a173ba6162ff34f887d
    (Q9UKP6, 53-337).
  target_ids:
  - CDD:cd14999
  field_paths:
  - data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml#/definition
  evidence_ids:
  - ev-cd14999
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F6
  issue_key: cdd-cd15894-snap25-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd15894 (SNARE_SNAP25N) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP25 is membrane-anchored via palmitoylated cysteines
  description: CDD:cd15894 states 'Both, Qb/Qc SNAREs consist of 2 coiled-coil helices
    (which form a single SNARE domain) and a transmembrane domain'. SNAP25 (human
    P60880, 19-81) is a t-SNARE containing an N-terminal Qb SNARE motif (cd15894)
    and a C-terminal Qc SNARE motif (sibling cd15885) linked by a palmitoylated cysteine-rich
    region and lacks any transmembrane domain. This overclaim blocked Stage 3 promotion
    of candidate ug-e252e4d82e1d26e10002d5abaa0877a146c31f0fd970400dc106954f6c8a85e7.
  target_ids:
  - CDD:cd15894
  field_paths:
  - data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml#/definition
  evidence_ids:
  - ev-cd15894
  - ev-cd15885-sibling
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F7
  issue_key: cdd-cd16523-mylip-proteasomal-vs-lysosomal-ldlr-degradation
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd16523 (RING-HC_MYLIP) sentence 2 claims proteasomal degradation of
    LDLR, VLDLR, and LRP8, contradicting sentence 4 (lysosomal degradation)
  description: 'In CDD:cd16523, sentence 2 claims that MYLIP/IDOL mediates ''ubiquitination
    and subsequent proteasomal degradation of myosin regulatory light chain (MRLC),
    low density lipoprotein receptor (LDLR), very low-density lipoprotein receptor
    (VLDLR) and low density lipoprotein receptor-related protein 8 (LRP8)'', contradicting
    sentence 4 (''triggers the ubiquitination and degradation of LDLR in lysosomes'')
    and primary literature (PMID:20884618, PMID:23225852) showing ESCRT/MVB-dependent
    lysosomal degradation of lipoprotein receptors. Blocked candidate: ug-75a40219c6b45df1ff1c607cf4d9a3e5e07de73f79ba1367231206244ab507c9
    (Q8WY64, 383-434).'
  target_ids:
  - CDD:cd16523
  field_paths:
  - data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml#/definition
  evidence_ids:
  - ev-cd16523
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F8
  issue_key: cdd-cd16652-rmd5-malformed-fbpase-substrate-phrase
  category: consistency
  severity: minor
  status: open
  certainty: confirmed
  title: CDD:cd16652 (dRING_Rmd5p-like) contains malformed substrate/enzyme text ('fructose-1,
    6-bisphosphate by fructose-1, 6-bisphosphatase (FBPase)')
  description: 'CDD:cd16652 states that yeast Rmd5p/GID2 mediates ''the polyubiquitination
    and subsequent proteasomal degradation of fructose-1, 6-bisphosphate by fructose-1,
    6-bisphosphatase (FBPase), phosphoenolpyruvate carboxykinase (PEPCK), cytoplasmic
    malate dehydrogenase''. FBPase (the enzyme, not the metabolite fructose-1,6-bisphosphate)
    is the ubiquitinated target. Blocked candidate: ug-4e3f322fa6f3b0c46798f889e3994a15bc8dfbeae6e94e0c6bb5eb1342632b8d
    (Q12508, 359-406).'
  target_ids:
  - CDD:cd16652
  field_paths:
  - data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml#/definition
  evidence_ids:
  - ev-cd16652
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F9
  issue_key: cdd-cd17150-dcdc2b-typo-and-dcdc2-paralog-disease-switch
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd17150 (DCX1_DCDC2B) misspells Doublecortin as Dublecortin in label/definition
    and switches to paralog DCDC2 disease genetics
  description: 'CDD:cd17150 has the typo ''Dublecortin-like domain 1'' in both label
    and definition and switches mid-definition from DCDC2B (human A2VCK2, 17-102)
    to paralog DCDC2 ciliary localization and reading-disability/ADHD genetics. Blocked
    candidate: ug-9bf8f0912858b90c6bb97f3bf8493bd6a4c05ebcc6a5a44d6bc37cf1dc2db84e.'
  target_ids:
  - CDD:cd17150
  field_paths:
  - data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml#/label
  - data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml#/definition
  evidence_ids:
  - ev-cd17150
  - ev-cd17151-sibling
  - ev-cdd-batch066
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F10
  issue_key: cdd-cd18592-abcc-mrp7-cftr-misassignment-and-mdr-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd18592 (ABC_6TM_MRP5_8_9_D1) misassigns MRP7-9 to ABCC7-9 (CFTR/SUR1/SUR2)
    instead of ABCC10-12 and overclaims MDR efflux for ABCC12
  description: 'CDD:cd18592 states ''Nine human MRPs have been identified (MRP1-9,
    also known as ABCC1-6 and ABCC7-9, respectively)'', misassigning MRP7, MRP8, and
    MRP9 to ABCC7 (CFTR), ABCC8 (SUR1), and ABCC9 (SUR2) instead of ABCC10, ABCC11,
    and ABCC12, and attributes blanket anticancer-drug efflux across all members including
    ABCC12/MRP9. Blocked candidates: O15440 (ABCC5, 181-467), Q96J66 (ABCC11, 165-451),
    and Q96J65 (ABCC12, 125-411).'
  target_ids:
  - CDD:cd18592
  field_paths:
  - data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml#/definition
  evidence_ids:
  - ev-cd18592
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F11
  issue_key: cdd-cd20534-ccnq-cnnm-acdp-magnesium-transporter-conflation
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd20534 (CYCLIN_CCNM_CCNQ_rpt1) conflates Cyclin-Q/Cyclin-M (CCNQ/FAM58A)
    with the CNNM1-4 (ACDP) magnesium transporter family
  description: 'CDD:cd20534 models the first cyclin box of CCNQ/FAM58A (human Q8N1B3,
    27-128, the CDK10-activating cyclin mutated in STAR syndrome), but its upstream
    CDD definition and PMID:14695534 evidence describe the unrelated CNNM1-4 (ACDP)
    CBS-pair magnesium transporter family (properly modeled by CDD:cd04590) and urofacial/hypomagnesemia/Jalili
    syndromes. Blocked candidate: ug-4bd7ba713556d491efbc4d9fd7d719ff9353c2fb4545d42deaa66a6c31e3a16e.'
  target_ids:
  - CDD:cd20534
  field_paths:
  - data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml#/definition
  - data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml#/evidence
  evidence_ids:
  - ev-cd20534
  - ev-cd20535-cd04590-siblings
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F12
  issue_key: cdd-cd21551-suz12-prc2-h3k9-methylation-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd21551 (VEFS-box_SUZ12) claims PRC2 directly methylates both H3K9 and
    H3K27
  description: 'CDD:cd21551 states ''The PRC2 complex methylates Lys-9 (H3K9) and
    Lys-27 (H3K27) of histone H3'', whereas canonical PRC2 (EZH1/EZH2 stimulated by
    the SUZ12 VEFS box) catalyzes H3K27me1/2/3 and reported H3K9me3 reductions upon
    SUZ12 loss reflect indirect cross-talk rather than intrinsic PRC2 H3K9 methyltransferase
    activity. Blocked candidate: ug-44aa2243f55dd0bb095beac3f1d82993fc80a2db2cb5e276dcde11e61a26c8bb
    (Q15022, 563-684).'
  target_ids:
  - CDD:cd21551
  field_paths:
  - data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml#/definition
  evidence_ids:
  - ev-cd21551
  - ev-cdd-batch058
  - ev-seed-cdd-cohort
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
actions:
- action_id: add-cdd-errata-and-repair-held-records
  description: Create a guarded CDD errata module (scripts/cdd_errata.py) and registered
    repair script (scripts/repair_cdd_errata.py) shared with scripts/seed_cdd.py to
    repair the 10 held CDD records (F3-F12) with literature-backed evidence and curation_history
    events, then re-resolve their 12 held Stage 3 UniProt candidates.
  finding_ids:
  - F3
  - F4
  - F5
  - F6
  - F7
  - F8
  - F9
  - F10
  - F11
  - F12
  target_ids:
  - CDD:cd09530
  - CDD:cd13344
  - CDD:cd14999
  - CDD:cd15894
  - CDD:cd16523
  - CDD:cd16652
  - CDD:cd17150
  - CDD:cd18592
  - CDD:cd20534
  - CDD:cd21551
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  acceptance_checks:
  - All 10 held CDD records carry accurate, paralog-specific definitions and literature
    citations.
  - scripts/seed_cdd.py applies the shared CDD errata table so reseeding is idempotent
    and preserves curated definitions.
  - scripts/validate_strict.py, scripts/validate_uniprot_grounding.py, and scripts/audit_writers.py
    pass with 0 errors.
- action_id: repair-promoted-cdd-typos-and-rebind
  description: Include CDD:cd00104 (F1) and CDD:cd00959 (F2) in the shared CDD errata
    table and update their qualified_record_bindings.jsonl.d receipts so durable UniProt
    grounding validation passes against the corrected record preimages.
  finding_ids:
  - F1
  - F2
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform (requires accession-level errata support)
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  acceptance_checks:
  - CDD:cd00104 and CDD:cd00959 definitions are repaired via the registered CDD errata
    pathway.
  - qualified_record_bindings.jsonl.d receipts match the updated record SHA-256 digests
    and validate_uniprot_grounding.py exits 0.
limitations:
- This review covers the frozen 12-record CDD SEQ_DOMAIN inventory surfaced during
  Stage 3 grounding review; other CDD records outside this cohort were not re-audited.
- No scientific trait records under data/traits/ were edited during Stage 4; all 12
  findings remain open for Stage 5 grouped remediation.
related_reviews:
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261022T052200Z-cdd-cd00104-record-review
  relationship: Companion single-record deep review of CDD:cd00104 (finding F1).
links:
- https://github.com/CultureBotAI/proteintraitsmech/issues/605
```
