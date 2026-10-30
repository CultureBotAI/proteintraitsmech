# Post-remediation scientific review of 14 Cycle 3 Stage 5 CDD sequence-domain records (8 carry-forwards F1, F2, F13-F18 and 6 newly remediated tandem-repeat/subfamily siblings F19-F24)

- Review: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-30T11:45:00Z
- Finished UTC: 2026-10-30T11:55:00Z
- Reviewer: Antigravity (self_review)
- Completion: completed
- Verdict: pass
- Scientific review: true

## Summary

Post-remediation scientific review of all 14 eligible CDD sequence-domain records in the Cycle 3 Stage 4/5 cohort (8 resolved carry-forwards from Cycle 1/2: CDD:cd00104, CDD:cd00959, CDD:cd20535, CDD:cd15885, CDD:cd17151, CDD:cd17154, CDD:cd17149, and CDD:cd18593, plus 6 newly remediated tandem-repeat and paralog-subfamily siblings in Cycle 3 Stage 5: CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, and CDD:cd18601). All 6 new upstream NCBI CDD source-definition errata findings (F19-F24, tracked in #1210 under #605) are now resolved via scripts/cdd_errata.py and scripts/repair_cdd_errata.py, bringing the canonical CDD errata table to 24 entries and advancing all 6 newly repaired records from SEEDED to PROPOSED with literature-backed evidence and append-only curation_history provenance. All 8 carry-forward findings (F1-F2 under #1172 and F13-F18 under #1188) remain verified resolved on disk. All 14 cohort records pass strict LinkML schema validation, UniProt grounding replay, causal-graph audit, writer audit, and curation-history validation with 0 errors.

## Scope And Provenance

Frozen 14-record Cycle 3 Stage 4 CDD SEQ_DOMAIN inventory comprising the 8 resolved carry-forward records from Cycle 2 Stage 5 (CDD:cd00104, CDD:cd00959, CDD:cd20535, CDD:cd15885, CDD:cd17151, CDD:cd17154, CDD:cd17149, CDD:cd18593) and 6 unpromoted tandem-repeat/subfamily sibling records of the Cycle 1/2 CDD cohorts (CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, CDD:cd18601).

Selection: Every CDD record carried forward from Cycle 2 Stage 5 (F1, F2, F13-F18) plus every remaining tandem-repeat or paralog-subfamily CDD sibling in the DCX_DCDC2/DCDC2B/DCDC2C, SNARE_SNAP25/SNAP23, and ABC_6TM_MRP4/5/8/9 clades that retained upstream CDD template prose defects after Cycle 1 and Cycle 2 remediation.
Coverage: full; 14 reviewed / 14 in the declared population.
Source: working_tree at Git base 334fabd4fe53db189c1e6d4a10cda521ddbe9091.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| CDD:cd00104 | data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml | generated | KAZAL_FS |
| CDD:cd00959 | data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml | generated | DeoC |
| CDD:cd15884 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml | generated | SNARE_SNAP23C |
| CDD:cd15885 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml | generated | SNARE_SNAP25C |
| CDD:cd15895 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml | generated | SNARE_SNAP23N |
| CDD:cd17149 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml | generated | DCX1_DCDC2 |
| CDD:cd17151 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml | generated | DCX1_DCDC2C |
| CDD:cd17152 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml | generated | DCX2_DCDC2 |
| CDD:cd17153 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml | generated | DCX2_DCDC2B |
| CDD:cd17154 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml | generated | DCX2_DCDC2C |
| CDD:cd18593 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml | generated | ABC_6TM_MRP4_D1_like |
| CDD:cd18599 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml | generated | ABC_6TM_MRP5_8_9_D2 |
| CDD:cd18601 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml | generated | ABC_6TM_MRP4_D2_like |
| CDD:cd20535 | data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml | generated | CYCLIN_CCNM_CCNQ_rpt2 |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Strict LinkML and OAK ontology-binding validation | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535 | All 14 target CDD records pass closed LinkML schema validation and OAK term-label bindings with 0 errors. |
| Release-pinned UniProt grounding and binding replay | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535 | 14 files scanned, 13,293 registry proteins, 22,635 source evidence objects, 22,635 qualified record bindings, 431 UniProt membership objects, and 0 semantic findings. |
| Causal-graph structural and semantic audit | passed | False | CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535 | 0 records with causal_graphs, 0 errors, 0 warnings across the 14-record cohort. |
| Registered write-route audit | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535 | 620 scripts examined (51 seeders, 9 registered editors, 2 transactional promoters, 52 declared bypasses), OK with 0 unguarded writer findings. |
| Append-only curation history schema validation | passed | False | CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535 | All 20 append-only history YAML files validate cleanly against HistoryRecord. |
| CDD errata repair idempotence and unit/guard test suite | passed | True | CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535 | All 24 CDD errata entries report 'already corrected; no history appended' on dry-run replay, and all 190 unit and writer-guard tests pass. |

## Scientific And Domain Assessments

### Category placement and tandem-repeat/subfamily boundary distinctness across all 14 CDD records

scope: supported. Targets: CDD:cd00104, CDD:cd00959, CDD:cd15884, CDD:cd15885, CDD:cd15895, CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154, CDD:cd18593, CDD:cd18599, CDD:cd18601, CDD:cd20535.

All 14 records are genuine conserved protein sequence domain profiles (trait_axis: SEQUENCE, trait_category: SEQ_DOMAIN; parent_traits=CDD:cl00097, CDD:cl21457, CDD:cl40454, CDD:cl22856, CDD:cl28922, and CDD:cl38913) with distinct CDD PSSM identifiers and non-overlapping repeat intervals or paralog-subfamily scopes. None should be merged or lumped with sibling CDD profiles.

### Verification of Cycle 1 and Cycle 2 carry-forward findings F1, F2, and F13-F18

consistency: supported. Targets: CDD:cd00104, CDD:cd00959, CDD:cd15885, CDD:cd17149, CDD:cd17151, CDD:cd17154, CDD:cd18593, CDD:cd20535.

All 8 carry-forward records from Cycle 1 Stage 6 (#1172) and Cycle 2 Stage 5 (#1188) — CDD:cd00104 (F1), CDD:cd00959 (F2), CDD:cd20535 (F13), CDD:cd15885 (F14), CDD:cd17151 (F15), CDD:cd17154 (F16), CDD:cd17149 (F17), and CDD:cd18593 (F18) — remain verified resolved in the Stage 5 working tree with entries in scripts/cdd_errata.py, literature-backed evidence, and append-only curation_history events.

### Resolution of upstream CDD nomenclature, paralog-scope, and structural/biochemical contradictions across the 6 Cycle 3 sibling CDD records (F19-F24)

consistency: supported. Targets: CDD:cd15884, CDD:cd15895, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601.

All 6 sibling CDD records audited in Cycle 3 Stage 4 (CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, CDD:cd18601) have now been repaired in place in Cycle 3 Stage 5 (#1210) via scripts/cdd_errata.py and scripts/repair_cdd_errata.py: the off-target ubiquitin protein-modifier digression on CDD:cd17152, the unqualified DCDC2B-&gt;DCDC2 paralog disease switch on CDD:cd17153, the false Qb/Qc transmembrane-domain claims on CDD:cd15884 and CDD:cd15895, and the MRP7=ABCC7/CFTR misassignment plus MRP1-MRP9 multidrug-resistance overclaim on CDD:cd18599 and CDD:cd18601 are all resolved with grounded evidence and append-only curation_history provenance.

## Findings

### F1: CDD:cd00104 definition misspells chymotrypsin and lists avian ovomucoids as target serine proteases

minor / resolved / confirmed; issue key: cdd-cd00104-kazal-definition-typo-and-inhibitor-target-confusion.

CDD:cd00104 previously stated 'Kazal inhibitors inhibit serine proteases, such as, trypsin, chyomotrypsin, avian ovomucoids, and elastases', misspelling 'chymotrypsin' and listing 'avian ovomucoids' (Kazal-type inhibitor proteins, PMID:6192856) as target enzymes.

Disposition: Repaired CDD:cd00104 via scripts/cdd_errata.py and scripts/repair_cdd_errata.py in Cycle 1 Stage 6 (#1172, PR #1175), correcting 'chyomotrypsin' to 'chymotrypsin', distinguishing avian ovomucoids as canonical Kazal-type inhibitors rather than target proteases (PMID:6192856), and updating all 39 durable qualified_record_bindings.jsonl.d receipts (covering all 26 QUALIFIED canonical examples out of 28 total canonical_examples on the record) to the new record_sha256 (62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26).

### F2: CDD:cd00959 definition repeats its opening title sentence verbatim

minor / resolved / confirmed; issue key: cdd-cd00959-dera-duplicated-opening-sentence.

CDD:cd00959 previously began with the duplicated sentence '2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family.' due to upstream CDD title+description concatenation.

Disposition: Repaired CDD:cd00959 via scripts/cdd_errata.py and scripts/repair_cdd_errata.py in Cycle 1 Stage 6 (#1172, PR #1175), removing the duplicated opening title sentence and updating both durable qualified_record_bindings.jsonl.d receipts (covering the 2 QUALIFIED canonical examples out of 5 total canonical_examples on the record) to the new record_sha256 (3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f).

### F13: CDD:cd20535 (CYCLIN_CCNM_CCNQ_rpt2) conflates the second cyclin box of Cyclin-Q/Cyclin-M (CCNQ/FAM58A) with the CNNM1-4 (ACDP) magnesium transporter family

major / resolved / confirmed; issue key: cdd-cd20535-ccnq-rpt2-cnnm-acdp-magnesium-transporter-conflation.

CDD:cd20535 (label=CYCLIN_CCNM_CCNQ_rpt2, parent_traits=[CDD:cl40454]) models the C-terminal second cyclin box of Cyclin-Q/Cyclin-M (CCNQ/FAM58A; unpromoted seed examples Mus musculus UniProtKB:Q8QZR8 and Homo sapiens UniProtKB:Q8N1B3), the activating cyclin partner of CDK10 mutated in X-linked STAR syndrome (PMID:23912459), but sentence 2 of its upstream CDD definition states 'The CCNM family proteins, also called ancient conserved domain proteins (ACDPs), are evolutionarily conserved Mg2+ transporters', conflating CCNM/CCNQ with the unrelated CNNM1-4 (ACDP) CBS-pair magnesium transporter family (contrasted with CDD:cd04590 in repaired sibling CDD:cd20534).

Disposition: Repaired CDD:cd20535 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1188): replaced the false CNNM1-4/ACDP magnesium transporter sentence with the accurate CDK10-activating cyclin CCNQ/FAM58A description, added PMID:23912459 evidence, and recorded curation_history action source_erratum_cd20535.

### F14: CDD:cd15885 (SNARE_SNAP25C) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 is membrane-anchored via palmitoylated cysteines

major / resolved / confirmed; issue key: cdd-cd15885-snap25c-transmembrane-domain-overclaim.

CDD:cd15885 (label=SNARE_SNAP25C, parent_traits=[CDD:cl22856]) models the C-terminal Qc SNARE motif of SNAP25 (unpromoted seed examples Mus musculus UniProtKB:P60879, Homo sapiens UniProtKB:P60880, and Drosophila melanogaster UniProtKB:P36975), but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25-family Qb/Qc t-SNAREs lack a transmembrane domain and attach to membranes via palmitoylated cysteines in the inter-motif linker between the N-terminal Qb (CDD:cd15894) and C-terminal Qc (CDD:cd15885) SNARE motifs (PMID:9759094).

Disposition: Repaired CDD:cd15885 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1188): replaced the false transmembrane-domain claim with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP25 is membrane-anchored via palmitoylated cysteines in its inter-motif linker, added PMID:9759094 evidence, and recorded curation_history action source_erratum_cd15885.

### F15: CDD:cd17151 (DCX1_DCDC2C) misspells Doublecortin-like as Dublecortin-like in definition and switches to paralog DCDC2 disease genetics

major / resolved / confirmed; issue key: cdd-cd17151-dcdc2c-typo-and-dcdc2-paralog-disease-switch.

CDD:cd17151 (label=DCX1_DCDC2C, parent_traits=[CDD:cl28922]) models the N-terminal first doublecortin-like domain (DCX1) of human DCDC2C (unpromoted seed example UniProtKB:A8MYV0, HGNC:33863), but its definition begins with the typo 'Dublecortin-like domain 1 found in doublecortin domain-containing protein 2C (DCDC2C).' and immediately switches in sentence 2 to paralog DCDC2 ('DCDC2 is a member of doublecortin (DCX) family.' and 'DCDC2 genetic variation in humans is associated with reading disability, attention deficit hyperactivity disorder (ADHD), and difficulties in mathematics.') without distinguishing DCDC2C from DCDC2 (UniProtKB:Q9UHG0, CDD:cd17149/CDD:cd17152).

Disposition: Repaired CDD:cd17151 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1188): corrected 'Dublecortin-like' to 'Doublecortin-like', distinguished DCDC2C (UniProtKB:A8MYV0) from its paralog DCDC2 (UniProtKB:Q9UHG0) in the phenotype summary, added UniProtKB:A8MYV0 evidence, and recorded curation_history action source_erratum_cd17151.

### F16: CDD:cd17154 (DCX2_DCDC2C) switches mid-definition from DCDC2C to paralog DCDC2 reading-disability and ADHD genetics

major / resolved / confirmed; issue key: cdd-cd17154-dcdc2c-rpt2-dcdc2-paralog-disease-switch.

CDD:cd17154 (label=DCX2_DCDC2C, parent_traits=[CDD:cl28922]) models the C-terminal second doublecortin-like domain (DCX2) of human DCDC2C (unpromoted seed example UniProtKB:A8MYV0, HGNC:33863), but sentence 2 switches without qualification to paralog DCDC2 ('DCDC2 is a member of the doublecortin (DCX) family.' and 'DCDC2 genetic variation in humans is associated with reading disability, attention deficit hyperactivity disorder (ADHD), and difficulties in mathematics.') without distinguishing DCDC2C from DCDC2 (UniProtKB:Q9UHG0, CDD:cd17149/CDD:cd17152).

Disposition: Repaired CDD:cd17154 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1188): distinguished DCDC2C (UniProtKB:A8MYV0) from its paralog DCDC2 (UniProtKB:Q9UHG0) in the domain description and human genetics phenotype summary, added UniProtKB:A8MYV0 evidence, and recorded curation_history action source_erratum_cd17154.

### F17: CDD:cd17149 (DCX1_DCDC2) misspells Doublecortin-like as Dublecortin-like in definition and interpolates an off-target ubiquitin protein-modifier sentence

minor / resolved / confirmed; issue key: cdd-cd17149-dcdc2-typo-and-ubiquitin-modifier-digression.

CDD:cd17149 (label=DCX1_DCDC2, parent_traits=[CDD:cl28922]) models the N-terminal first doublecortin-like domain (DCX1) of human DCDC2 (unpromoted seed example UniProtKB:Q9UHG0, HGNC:18141), begins its definition with the typo 'Dublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2).', and interpolates an off-target sentence defining the ubiquitin protein modifier ('Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.') even though DCX domains only adopt a ubiquitin-like beta-grasp fold and do not function as ubiquitin protein modifiers.

Disposition: Repaired CDD:cd17149 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1188): corrected 'Dublecortin-like' to 'Doublecortin-like', replaced the off-target ubiquitin protein-modifier digression with the tandem DCX ubiquitin-like beta-grasp repeat description, added PMID:16278295 evidence, and recorded curation_history action source_erratum_cd17149.

### F18: CDD:cd18593 (ABC_6TM_MRP4_D1_like) misassigns MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9 members

major / resolved / confirmed; issue key: cdd-cd18593-mrp4-abcc-mrp7-cftr-misassignment-and-mdr-overclaim.

CDD:cd18593 (label=ABC_6TM_MRP4_D1_like, parent_traits=[CDD:cl38913]) models TMD1 of MRP4/ABCC4 (unpromoted seed examples Homo sapiens UniProtKB:O15439 and Mus musculus UniProtKB:E9Q236), but carries the corrupted upstream CDD ABCC template text stating 'On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 7, respectively) have an additional N-terminal five transmembrane segments in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic linker (L0)' and claiming 'The MRP subfamily (ABCC subfamily) is composed of 13 members, of which MRP1 to MRP9 are the major transporters that cause multidrug resistance in tumor cells by pumping anticancer drugs out of the cell.' In HGNC/UniProt nomenclature, ABCC7 is CFTR (an epithelial chloride channel lacking TMD0), whereas MRP7 is ABCC10 (UniProtKB:Q5T3U5), MRP8 is ABCC11, and MRP9 is ABCC12 (a paralog whose physiological substrates and transport activity remain less characterized, PMID:16984901).

Disposition: Repaired CDD:cd18593 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1188): corrected the false mapping of MRP7 to ABCC7 (MRP7 is ABCC10; ABCC7 is CFTR), qualified the overgeneralized tumor multidrug-resistance efflux claim across MRP1-MRP9, added PMID:16984901 evidence, and recorded curation_history action source_erratum_cd18593.

### F19: CDD:cd17152 (DCX2_DCDC2) interpolates an off-target ubiquitin protein-modifier definition sentence into a microtubule-binding DCX repeat profile

minor / resolved / confirmed; issue key: cdd-cd17152-dcdc2-rpt2-ubiquitin-modifier-digression.

CDD:cd17152 (label=DCX2_DCDC2, parent_traits=[CDD:cl28922]) models the C-terminal second doublecortin-like domain (DCX2) of DCDC2 (unpromoted seed examples Homo sapiens UniProtKB:Q9UHG0 and Mus musculus UniProtKB:Q5DU00), a microtubule-associated protein with tandem ubiquitin-like beta-grasp DCX repeats associated with human reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition interpolates the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.' even though DCX domains only adopt a ubiquitin-like beta-grasp fold and do not function as ubiquitin protein modifiers, and the record lacks an evidence block citing PMID:16278295.

Disposition: Repaired CDD:cd17152 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210): replaced the off-target ubiquitin protein-modifier digression with the tandem DCX ubiquitin-like beta-grasp repeat description matching N-terminal repeat 1 sibling CDD:cd17149, added PMID:16278295 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd17152.

### F20: CDD:cd17153 (DCX2_DCDC2B) switches mid-definition from DCDC2B to paralog DCDC2 reading-disability and ADHD genetics

major / resolved / confirmed; issue key: cdd-cd17153-dcdc2b-rpt2-dcdc2-paralog-disease-switch.

CDD:cd17153 (label=DCX2_DCDC2B, parent_traits=[CDD:cl28922]) models the C-terminal second doublecortin-like domain (DCX2) of DCDC2B (Homo sapiens UniProtKB:A2VCK2, HGNC:33489, carried on N-terminal repeat 1 sibling CDD:cd17150), but sentence 2 switches without qualification to paralog DCDC2 ('DCDC2 is a member of the doublecortin (DCX) family.' and 'DCDC2 genetic variation in humans is associated with reading disability, attention deficit hyperactivity disorder (ADHD), and difficulties in mathematics. A genetic variant of DCDC2 associates with dyslexia, a common neurobehavioral disorder of reading.') without distinguishing DCDC2B from DCDC2 (UniProtKB:Q9UHG0, HGNC:18141, modeled by CDD:cd17149 and CDD:cd17152), and lacks a grounded evidence block.

Disposition: Repaired CDD:cd17153 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210): distinguished DCDC2B (UniProtKB:A2VCK2) from its paralog DCDC2 (UniProtKB:Q9UHG0) in the domain description and human reading-disability/ADHD genetics summary matching N-terminal repeat 1 sibling CDD:cd17150 and paralog repeat 2 sibling CDD:cd17154, added UniProtKB:A2VCK2 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd17153.

### F21: CDD:cd15884 (SNARE_SNAP23C) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines

major / resolved / confirmed; issue key: cdd-cd15884-snap23c-transmembrane-domain-overclaim.

CDD:cd15884 (label=SNARE_SNAP23C, parent_traits=[CDD:cl22856]) models the C-terminal Qc SNARE motif of SNAP23 (unpromoted seed examples Mus musculus UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family Qb/Qc t-SNAREs lack a transmembrane domain and SNAP23 attaches to membranes via palmitoylated cysteine residues in the inter-motif linker between its N-terminal Qb (CDD:cd15895) and C-terminal Qc (CDD:cd15884) SNARE motifs (PMID:9159129, PMID:9759094).

Disposition: Repaired CDD:cd15884 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210): replaced the false transmembrane-domain claim with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP23 is anchored to target membranes via palmitoylated cysteine residues in the linker between its two SNARE motifs, added PMID:9159129 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd15884.

### F22: CDD:cd15895 (SNARE_SNAP23N) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines

major / resolved / confirmed; issue key: cdd-cd15895-snap23n-transmembrane-domain-overclaim.

CDD:cd15895 (label=SNARE_SNAP23N, parent_traits=[CDD:cl22856]) models the N-terminal Qb SNARE motif of SNAP23 (unpromoted seed examples Mus musculus UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family Qb/Qc t-SNAREs lack a transmembrane domain and SNAP23 attaches to membranes via palmitoylated cysteine residues in the inter-motif linker between its N-terminal Qb (CDD:cd15895) and C-terminal Qc (CDD:cd15884) SNARE motifs (PMID:9159129, PMID:9759094).

Disposition: Repaired CDD:cd15895 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210): replaced the false transmembrane-domain claim with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP23 is anchored to target membranes via palmitoylated cysteine residues in the linker between its two SNARE motifs, added PMID:9159129 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd15895.

### F23: CDD:cd18599 (ABC_6TM_MRP5_8_9_D2) misassigns MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9 members

major / resolved / confirmed; issue key: cdd-cd18599-mrp5-8-9-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim.

CDD:cd18599 (label=ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913]) models C-terminal TMD2 of MRPs 5, 8, and 9 (unpromoted seed examples Homo sapiens ABCC5 UniProtKB:O15440, Mus musculus ABCC5 UniProtKB:Q9R1X5, Homo sapiens ABCC11 UniProtKB:Q96J66, Caenorhabditis elegans mrp-5 UniProtKB:G5EE72, Homo sapiens ABCC12 UniProtKB:Q96J65, and Mus musculus ABCC12 UniProtKB:Q80WJ6), but carries the corrupted upstream CDD ABCC template text stating 'On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 7, respectively) have an additional N-terminal five transmembrane segments in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic linker (L0)' and claiming 'The MRP subfamily (ABCC subfamily) is composed of 13 members, of which MRP1 to MRP9 are the major transporters that cause multidrug resistance in tumor cells by pumping anticancer drugs out of the cell.' In HGNC/UniProt nomenclature, ABCC7 is CFTR (an epithelial chloride channel lacking TMD0), whereas MRP7 is ABCC10 (UniProtKB:Q5T3U5), MRP8 is ABCC11, and MRP9 is ABCC12 (a paralog whose physiological substrates and transport activity remain less characterized, PMID:16984901).

Disposition: Repaired CDD:cd18599 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210): corrected the false mapping of MRP7 to ABCC7 (MRP7 is ABCC10; ABCC7 is CFTR) and qualified the overgeneralized tumor multidrug-resistance efflux claim across MRP1-MRP9 matching N-terminal TMD1 sibling CDD:cd18592, added PMID:16984901 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd18599.

### F24: CDD:cd18601 (ABC_6TM_MRP4_D2_like) misassigns MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9 members

major / resolved / confirmed; issue key: cdd-cd18601-mrp4-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim.

CDD:cd18601 (label=ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913]) models C-terminal TMD2 of MRP4/ABCC4 (unpromoted seed examples Homo sapiens UniProtKB:O15439 and Mus musculus UniProtKB:E9Q236), but carries the identical corrupted upstream CDD ABCC template text stating 'On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 7, respectively) have an additional N-terminal five transmembrane segments in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic linker (L0)' and claiming 'The MRP subfamily (ABCC subfamily) is composed of 13 members, of which MRP1 to MRP9 are the major transporters that cause multidrug resistance in tumor cells by pumping anticancer drugs out of the cell.' In HGNC/UniProt nomenclature, ABCC7 is CFTR (an epithelial chloride channel lacking TMD0), whereas MRP7 is ABCC10 (UniProtKB:Q5T3U5), MRP8 is ABCC11, and MRP9 is ABCC12 (PMID:16984901).

Disposition: Repaired CDD:cd18601 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210): corrected the false mapping of MRP7 to ABCC7 (MRP7 is ABCC10; ABCC7 is CFTR) and qualified the overgeneralized tumor multidrug-resistance efflux claim across MRP1-MRP9 matching N-terminal TMD1 sibling CDD:cd18593, added PMID:16984901 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd18601.

## Recommended Actions And Acceptance Checks

## Category Boundaries

- retain: CDD:cd00104, CDD:cd00959, CDD:cd20535. Retain resolved carry-forward records CDD:cd00104 (KAZAL_FS, parent_traits=[CDD:cl00097]), CDD:cd00959 (DeoC, parent_traits=[CDD:cl21457]), and CDD:cd20535 (CYCLIN_CCNM_CCNQ_rpt2, parent_traits=[CDD:cl40454], C-terminal second cyclin box of CCNQ/FAM58A) as distinct conserved domain families.
- retain: CDD:cd15884, CDD:cd15885, CDD:cd15895. Retain CDD:cd15895 (label=SNARE_SNAP23N, N-terminal Qb SNARE motif of SNAP23) and CDD:cd15884 (label=SNARE_SNAP23C, C-terminal Qc SNARE motif of SNAP23) as non-overlapping tandem coiled-coil SNARE domains on SNAP23 (Homo sapiens O00161, Mus musculus O09044) under parent_traits [CDD:cl22856], and retain both as distinct paralog-subfamily profiles separate from the neuronal SNAP25 N-terminal Qb (CDD:cd15894) and C-terminal Qc (CDD:cd15885) SNARE motif profiles.
- retain: CDD:cd17149, CDD:cd17151, CDD:cd17152, CDD:cd17153, CDD:cd17154. Retain all 5 target doublecortin-like repeat profiles under parent_traits [CDD:cl28922] — CDD:cd17149 (DCX1_DCDC2, repeat 1 of DCDC2), CDD:cd17152 (DCX2_DCDC2, repeat 2 of DCDC2), CDD:cd17153 (DCX2_DCDC2B, repeat 2 of DCDC2B; sibling of repeat 1 CDD:cd17150), CDD:cd17151 (DCX1_DCDC2C, repeat 1 of DCDC2C), and CDD:cd17154 (DCX2_DCDC2C, repeat 2 of DCDC2C) — because each models a distinct N-terminal vs C-terminal tandem repeat position or a distinct human/mammalian paralog subfamily (DCDC2, DCDC2B, DCDC2C).
- retain: CDD:cd18593, CDD:cd18599, CDD:cd18601. Retain CDD:cd18593 (ABC_6TM_MRP4_D1_like, N-terminal TMD1 of MRP4/ABCC4), CDD:cd18601 (ABC_6TM_MRP4_D2_like, C-terminal TMD2 of MRP4/ABCC4), and CDD:cd18599 (ABC_6TM_MRP5_8_9_D2, C-terminal TMD2 of MRPs 5/8/9, ABCC5/ABCC11/ABCC12; sibling of N-terminal TMD1 CDD:cd18592) under parent_traits [CDD:cl38913] because they represent non-overlapping N-terminal TMD1 vs C-terminal TMD2 six-helix bundles and distinct ABCC subfamily clades.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| ev-cd00104 | data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml; identifier, label, definition, evidence, mapping_status, curation_history (source_erratum_cd00104) | supports | CDD:cd00104 (label KAZAL_FS, parent_traits=[CDD:cl00097], PROPOSED) remains verified resolved on disk with corrected chymotrypsin spelling, avian ovomucoids distinguished as inhibitors (PMID:6192856), and 39 valid sharded qualified_record_bindings receipts. |
| ev-cd00959 | data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml; identifier, label, definition, mapping_status, curation_history (source_erratum_cd00959) | supports | CDD:cd00959 (label DeoC, parent_traits=[CDD:cl21457], PROPOSED) remains verified resolved on disk with deduplicated opening title sentence and 2 valid sharded qualified_record_bindings receipts. |
| ev-cd20535 | data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml; identifier, label, definition, evidence (PMID:23912459), mapping_status, curation_history (source_erratum_cd20535) | supports | CDD:cd20535 (label CYCLIN_CCNM_CCNQ_rpt2, parent_traits=[CDD:cl40454], PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair. |
| ev-cd15885 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml; identifier, label, definition, evidence (PMID:9759094), mapping_status, curation_history (source_erratum_cd15885) | supports | CDD:cd15885 (label SNARE_SNAP25C, parent_traits=[CDD:cl22856], PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair. |
| ev-cd17151 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml; identifier, label, definition, evidence (UniProtKB:A8MYV0), mapping_status, curation_history (source_erratum_cd17151) | supports | CDD:cd17151 (label DCX1_DCDC2C, parent_traits=[CDD:cl28922], PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair. |
| ev-cd17154 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml; identifier, label, definition, evidence (UniProtKB:A8MYV0), mapping_status, curation_history (source_erratum_cd17154) | supports | CDD:cd17154 (label DCX2_DCDC2C, parent_traits=[CDD:cl28922], PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair. |
| ev-cd17149 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml; identifier, label, definition, evidence (PMID:16278295), mapping_status, curation_history (source_erratum_cd17149) | supports | CDD:cd17149 (label DCX1_DCDC2, parent_traits=[CDD:cl28922], PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair. |
| ev-cd18593 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml; identifier, label, definition, evidence (PMID:16984901), mapping_status, curation_history (source_erratum_cd18593) | supports | CDD:cd18593 (label ABC_6TM_MRP4_D1_like, parent_traits=[CDD:cl38913], PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair. |
| ev-cd17152 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml; identifier, label, definition, evidence (PMID:16278295), mapping_status, curation_history (source_erratum_cd17152) | supports | CDD:cd17152 (label DCX2_DCDC2, parent_traits=[CDD:cl28922], PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation: the off-target ubiquitin protein-modifier digression has been replaced with the accurate tandem DCX ubiquitin-like beta-grasp fold description, PMID:16278295 evidence is attached, and curation_history records source_erratum_cd17152. |
| ev-cd17153 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml; identifier, label, definition, evidence (UniProtKB:A2VCK2), mapping_status, curation_history (source_erratum_cd17153) | supports | CDD:cd17153 (label DCX2_DCDC2B, parent_traits=[CDD:cl28922], PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation: DCDC2B is explicitly distinguished from its paralog DCDC2 in the domain description and human reading-disability/ADHD genetics summary, UniProtKB:A2VCK2 evidence is attached, and curation_history records source_erratum_cd17153. |
| ev-cd15884 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml; identifier, label, definition, evidence (PMID:9159129), mapping_status, curation_history (source_erratum_cd15884) | supports | CDD:cd15884 (label SNARE_SNAP23C, parent_traits=[CDD:cl22856], PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation: the false Qb/Qc transmembrane-domain claim has been replaced with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP23 is anchored to target membranes via palmitoylated cysteine residues in its inter-motif linker, PMID:9159129 evidence is attached, and curation_history records source_erratum_cd15884. |
| ev-cd15895 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml; identifier, label, definition, evidence (PMID:9159129), mapping_status, curation_history (source_erratum_cd15895) | supports | CDD:cd15895 (label SNARE_SNAP23N, parent_traits=[CDD:cl22856], PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation: the false Qb/Qc transmembrane-domain claim has been replaced with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP23 is anchored to target membranes via palmitoylated cysteine residues in its inter-motif linker, PMID:9159129 evidence is attached, and curation_history records source_erratum_cd15895. |
| ev-cd18599 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml; identifier, label, definition, evidence (PMID:16984901), mapping_status, curation_history (source_erratum_cd18599) | supports | CDD:cd18599 (label ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913], PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation: the false MRP7=ABCC7 (CFTR) assignment is corrected to MRP7=ABCC10, the MRP1-MRP9 multidrug-resistance efflux overclaim is qualified, PMID:16984901 evidence is attached, and curation_history records source_erratum_cd18599. |
| ev-cd18601 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml; identifier, label, definition, evidence (PMID:16984901), mapping_status, curation_history (source_erratum_cd18601) | supports | CDD:cd18601 (label ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913], PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation: the false MRP7=ABCC7 (CFTR) assignment is corrected to MRP7=ABCC10, the MRP1-MRP9 multidrug-resistance efflux overclaim is qualified, PMID:16984901 evidence is attached, and curation_history records source_erratum_cd18601. |
| ev-cd15894-sibling | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml; identifier, label, definition, evidence (PMID:9759094) | supports | Cycle 1 remediated sibling CDD:cd15894 (SNARE_SNAP25N, #1171) establishing the palmitoylated inter-motif linker membrane-anchoring wording for Qb/Qc SNAREs (PMID:9759094). |
| ev-cd17150-sibling | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml; identifier, label, definition, canonical_examples (UniProtKB:A2VCK2), evidence | supports | Cycle 1 remediated N-terminal first-repeat sibling CDD:cd17150 (label DCX1_DCDC2B, carrying human DCDC2B UniProtKB:A2VCK2, #1171) establishing the paralog-qualified DCDC2B vs DCDC2 wording needed on C-terminal second-repeat sibling CDD:cd17153 (F20). |
| ev-cd18592-sibling | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml; identifier, label, definition, evidence (PMID:16984901) | supports | Cycle 1 remediated N-terminal TMD1 sibling CDD:cd18592 (label ABC_6TM_MRP5_8_9_D1, #1171) establishing the corrected MRP7=ABCC10 / CFTR=ABCC7 nomenclature and qualified MRP1-MRP9 efflux phrasing needed on TMD2 sibling CDD:cd18599 (F23). |
| ev-cd20534-cd04590-siblings | data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml; CDD:cd20534 (CYCLIN_CCNM_CCNQ_rpt1) and CDD:cd04590 (CBS_pair_CorC_HlyC_assoc) | supports | Boundary-contrast siblings CDD:cd20534 (N-terminal cyclin box 1 of CCNQ/FAM58A) and CDD:cd04590 (CBS-pair domain of CNNM/ACDP magnesium transporters) supporting resolved finding F13 on CDD:cd20535. |
| ev-prior-stage4-cd00104 | reviews/structured/20261022T052200Z-cdd-cd00104-record-review/review.yaml; finding F1 | supports | Cycle 1 Stage 4 single-record review of CDD:cd00104 (F1). |
| ev-prior-stage4-cohort | reviews/structured/20261022T052300Z-cdd-stage3-domain-cohort-review/review.yaml; findings F1-F12 | supports | Cycle 1 Stage 4 cohort review of 12 CDD records (F1-F12). |
| ev-prior-stage5-cohort | reviews/structured/20261022T081000Z-cdd-stage5-remediation-review/review.yaml; findings F1-F12 | supports | Cycle 1 Stage 5 post-remediation review resolving F3-F12 and deferring F1-F2. |
| ev-cycle1-stage6-evidence | reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/evidence.yaml; proteintraitsmech-infra-0003 resolution (#1172, PR #1175) | supports | Cycle 1 Stage 6 workflow evidence documenting the resolution of F1 (CDD:cd00104) and F2 (CDD:cd00959). |
| ev-cycle2-stage4-cohort | reviews/structured/20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review/review.yaml; findings F1, F2, F13-F18 | supports | Cycle 2 Stage 4 cohort review of 8 CDD records (F1, F2 resolved; F13-F18 opened). |
| ev-cycle2-stage5-cohort | reviews/structured/20261025T233000Z-cdd-cycle2-stage5-remediation-review/review.yaml; findings F1, F2, F13-F18 resolved (#1188) | supports | Cycle 2 Stage 5 post-remediation review verifying F1, F2, and F13-F18 resolved on disk. |
| ev-cycle2-stage5-evidence | reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-05/revision-0001/evidence.yaml; findings F1, F2, F13-F18 resolved (PR #1189) | supports | Predecessor Cycle 2 Stage 5 workflow evidence manifest from which findings F1, F2, and F13-F18 are carried forward. |
| ev-cdd-errata-infrastructure | scripts/cdd_errata.py; CDD_ERRATA table (24 entries), scripts/repair_cdd_errata.py, scripts/seed_cdd.py, and tests/test_cdd_errata.py | supports | scripts/cdd_errata.py now contains 24 accession-keyed CDD errata entries (12 from Cycle 1, 6 from Cycle 2, and 6 from Cycle 3 #1210) wired into scripts/seed_cdd.py and scripts/repair_cdd_errata.py and verified by 190 unit and writer-guard tests. |
| ev-cycle3-stage4-cd17152 | reviews/structured/20261030T092000Z-cdd-cd17152-record-review/review.yaml; finding F19 | supports | Cycle 3 Stage 4 single-record scientific review of CDD:cd17152 identifying finding F19. |
| ev-cycle3-stage4-cohort | reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml; findings F1, F2, F13-F24 | supports | Cycle 3 Stage 4 cohort review of 14 CDD records (F1, F2, F13-F18 verified resolved; F19-F24 opened). |
| ev-cycle3-stage4-evidence | reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-04/revision-0001/evidence.yaml; findings F1, F2, F13-F18 resolved; F19-F24 open (PR #1208) | supports | Predecessor Cycle 3 Stage 4 workflow evidence manifest from which findings F1, F2, and F13-F24 are carried forward into Stage 5. |

## Limits And Additional Notes

- This post-remediation review covers the frozen 14-record Cycle 3 Stage 4/5 CDD SEQ_DOMAIN cohort (8 resolved Cycle 1/2 carry-forwards and 6 newly remediated tandem-repeat/subfamily siblings).
- All 14 cohort findings (F1-F2 under #1172, F13-F18 under #1188, and F19-F24 under #1210) are resolved on disk; broader NCBI CDD corpus screening across other CDD families remains tracked under umbrella issue #605.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
kind: category
repository: CultureBotAI/proteintraitsmech
title: Post-remediation scientific review of 14 Cycle 3 Stage 5 CDD sequence-domain
  records (8 carry-forwards F1, F2, F13-F18 and 6 newly remediated tandem-repeat/subfamily
  siblings F19-F24)
started_at: '2026-10-30T11:45:00Z'
finished_at: '2026-10-30T11:55:00Z'
reviewer:
  identity: Antigravity
  kind: agent
  model: Claude Opus 4.6
  independence: self_review
  independence_basis: Post-remediation verification review performed in Cycle 3 Stage
    5 after extending scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210)
    to repair F19-F24 across the 6 sibling CDD domain records while verifying that
    carry-forward findings F1-F2 (#1172) and F13-F18 (#1188) remain resolved.
skill: review-yaml-category
completion: completed
verdict: pass
native_verdict: COHORT_PASS_ALL_14_FINDINGS_RESOLVED
scientific_review: true
summary: 'Post-remediation scientific review of all 14 eligible CDD sequence-domain
  records in the Cycle 3 Stage 4/5 cohort (8 resolved carry-forwards from Cycle 1/2:
  CDD:cd00104, CDD:cd00959, CDD:cd20535, CDD:cd15885, CDD:cd17151, CDD:cd17154, CDD:cd17149,
  and CDD:cd18593, plus 6 newly remediated tandem-repeat and paralog-subfamily siblings
  in Cycle 3 Stage 5: CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599,
  and CDD:cd18601). All 6 new upstream NCBI CDD source-definition errata findings
  (F19-F24, tracked in #1210 under #605) are now resolved via scripts/cdd_errata.py
  and scripts/repair_cdd_errata.py, bringing the canonical CDD errata table to 24
  entries and advancing all 6 newly repaired records from SEEDED to PROPOSED with
  literature-backed evidence and append-only curation_history provenance. All 8 carry-forward
  findings (F1-F2 under #1172 and F13-F18 under #1188) remain verified resolved on
  disk. All 14 cohort records pass strict LinkML schema validation, UniProt grounding
  replay, causal-graph audit, writer audit, and curation-history validation with 0
  errors.'
source:
  git_revision: 334fabd4fe53db189c1e6d4a10cda521ddbe9091
  state: working_tree
  inputs:
  - path: data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    sha256: 3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f
    role: target
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    sha256: e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510
    role: target
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
    sha256: 78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    sha256: 082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    sha256: d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
    sha256: 6ec1fd4e6c77d35fcd3c65b0387f517870965eeb622e47e122665a32b27c1f1d
    role: target
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
    sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
    role: target
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    sha256: fe5af61fd44b4a50b6c9f0ab06ddd1d717895a010f788b8096ff64d3f68e4756
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    sha256: 6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d
    role: target
  - path: data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
    sha256: 72fbd3487668c097281cf6ee45a4daf0366a2bcc80866330f8ed4832141d7e88
    role: context
  - path: data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    sha256: 62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26
    role: target
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    sha256: 5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b
    role: target
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
    sha256: d11a67560ebb84bf867f67027f23109a5631b72953aa870075b96116cd599368
    role: context
  - path: data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
    sha256: 5d4cdbce834a6183b6fa860b8ee439da3c8ea5eb44634f692c08d320180b0249
    role: target
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
    sha256: fad0b6039c5386b3caf40fc650099ec7bfd126ff7854d42aeb805708a18c3f9a
    role: context
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
    sha256: 5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb
    role: target
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    sha256: ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585
    role: target
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    sha256: d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099
    role: target
  - path: data/traits/sequence/domain/cdd/two-tandem-repeats-of-the-cystathionine-beta-synthase-cbs-pair-domains-cd04590.yaml
    sha256: 5bfd6d04f6c15aad7dd69ca34e3c88ae6dbad3d07023a8e1cba85eee3a719274
    role: context
  - path: reviews/structured/20261022T052200Z-cdd-cd00104-record-review/review.yaml
    sha256: f8340019e447b9a37ab1eb333826a61f818c58aa365e43480917f69d87da8fa9
    role: context
  - path: reviews/structured/20261022T052300Z-cdd-stage3-domain-cohort-review/review.yaml
    sha256: ce693cda666fcc7f5ad2d22b11e67b9a9d0b9d32859b1d0ca5e3e982f04dfa8e
    role: context
  - path: reviews/structured/20261022T081000Z-cdd-stage5-remediation-review/review.yaml
    sha256: 438b6712ef02fc88990c1bf5e054fc2b901925f85b2eed0f4da2cc3015be6330
    role: context
  - path: reviews/structured/20261025T202200Z-cdd-cd20535-record-review/review.yaml
    sha256: 3350c8a9e1f827e75f8586e63b061e22165dd7668b71af380c71c87e85b61a57
    role: context
  - path: reviews/structured/20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review/review.yaml
    sha256: 2722da7d2d32c603f417b4efaefc9001bc2fa2751bc3184b5ba2f23a8cdcb7b0
    role: context
  - path: reviews/structured/20261025T233000Z-cdd-cycle2-stage5-remediation-review/review.yaml
    sha256: 513cb559af7f1c2dfa19a4307c1fd06a164ea68ec5f07770649038200ed1899e
    role: context
  - path: reviews/structured/20261030T092000Z-cdd-cd17152-record-review/review.yaml
    sha256: c06176c3073f1ec5d26954550500e22ecb07649a53c18e3700fd1ee352ada514
    role: context
  - path: reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml
    sha256: 2d8fe1c367294f3e5660badc28211c13c97763d788ce0eb9ca3ef1cd134587f8
    role: context
  - path: reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/evidence.yaml
    sha256: 3cded5bbfd329238d0e695ce9bc64098886a7724b03dacd1b524f91ca7903201
    role: context
  - path: reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-04/revision-0001/evidence.yaml
    sha256: 60a2374cb7b0c3289dbcf5c785da8aaf475658639107d70766e5e19fd92b49d9
    role: context
  - path: reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-05/revision-0001/evidence.yaml
    sha256: 37cf6670f427c35fabdccb772c188323d7d5128d595e571f39561fab61fc709c
    role: context
  - path: reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-04/revision-0001/evidence.yaml
    sha256: 675d9c6efc52c8ad25d7e0a13f9306fe0d92d901a3f629ec9a5328230feec9e9
    role: context
  - path: scripts/cdd_errata.py
    sha256: 332155e8c1f1a119ca0f3c4394b49fa775bcc8d9f4c68e1f43183bd97b64d962
    role: context
  - path: scripts/record_io.py
    sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
    role: context
  - path: scripts/repair_cdd_errata.py
    sha256: 0a7fcce6f8f00a4d20b1a4f94a6ec77f32c6ab62d9edc2fd4a228fbda48cea9d
    role: context
  - path: scripts/seed_cdd.py
    sha256: 4fd337316239794623aaa2ad8afed44bb96ead33a1b387921272f26f8731365a
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
  - path: tests/test_cdd_errata.py
    sha256: 606aa0308bcfdd67447ae37c9c5dd64e476d9445464e98bea7405ea667116ac2
    role: context
scope:
  description: Frozen 14-record Cycle 3 Stage 4 CDD SEQ_DOMAIN inventory comprising
    the 8 resolved carry-forward records from Cycle 2 Stage 5 (CDD:cd00104, CDD:cd00959,
    CDD:cd20535, CDD:cd15885, CDD:cd17151, CDD:cd17154, CDD:cd17149, CDD:cd18593)
    and 6 unpromoted tandem-repeat/subfamily sibling records of the Cycle 1/2 CDD
    cohorts (CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, CDD:cd18601).
  selection: Every CDD record carried forward from Cycle 2 Stage 5 (F1, F2, F13-F18)
    plus every remaining tandem-repeat or paralog-subfamily CDD sibling in the DCX_DCDC2/DCDC2B/DCDC2C,
    SNARE_SNAP25/SNAP23, and ABC_6TM_MRP4/5/8/9 clades that retained upstream CDD
    template prose defects after Cycle 1 and Cycle 2 remediation.
  coverage: full
  population_size: 14
  reviewed_target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  exclusions:
  - target: 10 Cycle 1 G1 CDD records already resolved in Cycle 1 Stage 5 (cd09530,
      cd13344, cd14999, cd15894, cd16523, cd16652, cd17150, cd18592, cd20534, cd21551)
      plus CBS-pair contrast record cd04590
    reason: 'Already remediated and verified in Cycle 1 Stage 5 (20261022T081000Z-cdd-stage5-remediation-review)
      and promoted in Cycle 1 Stage 6 (#1171, #1172); cd15894, cd17150, cd18592, cd20534,
      and cd04590 are included here as boundary-contrast context inputs.'
targets:
- target_id: CDD:cd00104
  path: data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
  label: KAZAL_FS
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd00959
  path: data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
  label: DeoC
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd15884
  path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
  label: SNARE_SNAP23C
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd15885
  path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
  label: SNARE_SNAP25C
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd15895
  path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
  label: SNARE_SNAP23N
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd17149
  path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
  label: DCX1_DCDC2
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd17151
  path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
  label: DCX1_DCDC2C
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd17152
  path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
  label: DCX2_DCDC2
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd17153
  path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
  label: DCX2_DCDC2B
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd17154
  path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
  label: DCX2_DCDC2C
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 6ec1fd4e6c77d35fcd3c65b0387f517870965eeb622e47e122665a32b27c1f1d
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd18593
  path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
  label: ABC_6TM_MRP4_D1_like
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd18599
  path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
  label: ABC_6TM_MRP5_8_9_D2
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd18601
  path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
  label: ABC_6TM_MRP4_D2_like
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
- target_id: CDD:cd20535
  path: data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
  label: CYCLIN_CCNM_CCNQ_rpt2
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: 5d4cdbce834a6183b6fa860b8ee439da3c8ea5eb44634f692c08d320180b0249
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file in the
      Stage 5 working tree.
checks:
- check_id: schema
  name: Strict LinkML and OAK ontology-binding validation
  command: .venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv
    data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
  exit_code: 0
  status: passed
  required: true
  summary: All 14 target CDD records pass closed LinkML schema validation and OAK
    term-label bindings with 0 errors.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd15884
  - ev-cd15885
  - ev-cd15895
  - ev-cd17149
  - ev-cd17151
  - ev-cd17152
  - ev-cd17153
  - ev-cd17154
  - ev-cd18593
  - ev-cd18599
  - ev-cd18601
  - ev-cd20535
- check_id: semantic
  name: Release-pinned UniProt grounding and binding replay
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv
    data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
  exit_code: 0
  status: passed
  required: true
  summary: 14 files scanned, 13,293 registry proteins, 22,635 source evidence objects,
    22,635 qualified record bindings, 431 UniProt membership objects, and 0 semantic
    findings.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd15884
  - ev-cd15885
  - ev-cd15895
  - ev-cd17149
  - ev-cd17151
  - ev-cd17152
  - ev-cd17153
  - ev-cd17154
  - ev-cd18593
  - ev-cd18599
  - ev-cd18601
  - ev-cd20535
- check_id: graphs
  name: Causal-graph structural and semantic audit
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
    data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
  exit_code: 0
  status: passed
  required: false
  summary: 0 records with causal_graphs, 0 errors, 0 warnings across the 14-record
    cohort.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd15884
  - ev-cd15885
  - ev-cd15895
  - ev-cd17149
  - ev-cd17151
  - ev-cd17152
  - ev-cd17153
  - ev-cd17154
  - ev-cd18593
  - ev-cd18599
  - ev-cd18601
  - ev-cd20535
- check_id: writer-audit
  name: Registered write-route audit
  command: .venv/bin/python scripts/audit_writers.py
  exit_code: 0
  status: passed
  required: true
  summary: 620 scripts examined (51 seeders, 9 registered editors, 2 transactional
    promoters, 52 declared bypasses), OK with 0 unguarded writer findings.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cdd-errata-infrastructure
- check_id: history
  name: Append-only curation history schema validation
  command: .venv/bin/python -c "import glob, sys, linkml.validator as v; files = sorted(glob.glob('history/**/*.yaml',
    recursive=True)); sys.exit(sum(1 for f in files for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml',
    'HistoryRecord').results))"
  exit_code: 0
  status: passed
  required: false
  summary: All 20 append-only history YAML files validate cleanly against HistoryRecord.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cdd-errata-infrastructure
- check_id: cdd-errata-idempotence-and-tests
  name: CDD errata repair idempotence and unit/guard test suite
  command: .venv/bin/python scripts/repair_cdd_errata.py && .venv/bin/pytest -q tests/test_cdd_errata.py
    tests/test_inplace_editor_guards.py
  exit_code: 0
  status: passed
  required: true
  summary: All 24 CDD errata entries report 'already corrected; no history appended'
    on dry-run replay, and all 190 unit and writer-guard tests pass.
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cdd-errata-infrastructure
evidence:
- evidence_id: ev-cd00104
  kind: record_content
  reference: data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml
  locator: identifier, label, definition, evidence, mapping_status, curation_history
    (source_erratum_cd00104)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26
  support: supports
  quote: Kazal type serine protease inhibitors and follistatin-like domains. Kazal
    inhibitors (such as avian ovomucoids and pancreatic secretory trypsin inhibitor)
    inhibit serine proteases such as trypsin, chymotrypsin, and elastases. The inhibitory
    domain has one reactive site peptide bond, which serves the cognate enzyme as
    substrate. The reactive site peptide bond is a combining loop which has an identical
    conformation in all Kazal inhibitors and in all enzyme/inhibitor complexes. These
    Kazal domains (small hydrophobic core of alpha/beta structure with 3 to 4 disulfide
    bonds) often occur in tandem arrays. Similar domains are also present in follistatin
    (FS) and follistatin-like family members, which play an important role in tissue
    specific regulation. The FS domain consists of an N-terminal beta hairpin (FOLN/EGF-like
    domain) and a Kazal-like domain and has five disulfide bonds. Although the Kazal-like
    FS substructure is similar to Kazal proteinase inhibitors, no FS domain has yet
    been shown to be a proteinase inhibitor. Follistatin-like family members include
    SPARC, also known as, BM-40 or osteonectin, the Gallus gallus Flik protein, as
    well as, agrin which has a long array of FS domains. The kazal-type inhibitor
    domain has also been detected in an extracellular loop region of solute carrier
    21 (SLC21) family members (organic anion transporters) , which may regulate the
    specificity of anion uptake. The distant homolog, Ascidian trypsin inhibitor,
    is included in this CD
  summary: CDD:cd00104 (label KAZAL_FS, parent_traits=[CDD:cl00097], PROPOSED) remains
    verified resolved on disk with corrected chymotrypsin spelling, avian ovomucoids
    distinguished as inhibitors (PMID:6192856), and 39 valid sharded qualified_record_bindings
    receipts.
- evidence_id: ev-cd00959
  kind: record_content
  reference: data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml
  locator: identifier, label, definition, mapping_status, curation_history (source_erratum_cd00959)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f
  support: supports
  quote: 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family. DERA belongs
    to the class I aldolases and catalyzes a reversible aldol reaction between acetaldehyde
    and glyceraldehyde 3-phosphate to generate 2-deoxyribose 5-phosphate. DERA is
    unique in catalyzing the aldol reaction between two aldehydes, and its broad substrate
    specificity confers considerable utility as a biocatalyst, offering an environmentally
    benign alternative to chiral transition metal catalysis of the asymmetric aldol
    reaction
  summary: CDD:cd00959 (label DeoC, parent_traits=[CDD:cl21457], PROPOSED) remains
    verified resolved on disk with deduplicated opening title sentence and 2 valid
    sharded qualified_record_bindings receipts.
- evidence_id: ev-cd20535
  kind: record_content
  reference: data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml
  locator: identifier, label, definition, evidence (PMID:23912459), mapping_status,
    curation_history (source_erratum_cd20535)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 5d4cdbce834a6183b6fa860b8ee439da3c8ea5eb44634f692c08d320180b0249
  support: supports
  quote: second cyclin box found in cyclin-M (CCNM) family. Cyclin-M (CCNM), officially
    designated cyclin-Q (CCNQ, formerly FAM58A; distinct from the CNNM1-4/ACDP magnesium
    transporter family in CDD:cd04590), is the CDK10-activating cyclin that associates
    with CDK10 to promote its protein kinase activity. Members of this family contain
    two cyclin boxes. This model corresponds to the second one. The cyclin box is
    a protein binding domain
  summary: CDD:cd20535 (label CYCLIN_CCNM_CCNQ_rpt2, parent_traits=[CDD:cl40454],
    PROPOSED) remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata
    repair.
- evidence_id: ev-cd15885
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
  locator: identifier, label, definition, evidence (PMID:9759094), mapping_status,
    curation_history (source_erratum_cd15885)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b
  support: supports
  quote: C-terminal SNARE motif of SNAP25. C-terminal SNARE motifs of SNAP25, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. SNAP25 interacts with Syntaxin-1 (Qa) and the R-SNARE
    VAMP2 (also called synaptobrevin-2). The complex plays a role in transport of
    secretory granule from trans-Golgi network to the plasma membrane. Qb/Qc SNAREs
    consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb
    subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and lack a transmembrane domain; SNAP25 is anchored
    to target membranes via palmitoylated cysteine residues in the linker between
    its two SNARE motifs. In general, the SNARE complex mediates membrane fusion,
    important for trafficking of newly synthesized proteins, recycling of pre-existing
    proteins and organelle formation. SNARE proteins are classified into four groups,
    Qa-, Qb-, Qc- and R-SNAREs, depending on whether the residue in the hydrophilic
    center layer of the four-helical bundle is a glutamine (Q) or arginine (R). Qa-,
    as well as Qb- and Qc-SNAREs, are localized to target organelle membranes, while
    R-SNARE is localized to vesicle membranes. They form unique complexes consisting
    of one member of each subgroup, that mediate fusion between a specific type of
    vesicles and their target organelle. Their SNARE motifs form twisted and parallel
    heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are SNAP23,
    SNAP29, SNAP47 and SEC9
  summary: CDD:cd15885 (label SNARE_SNAP25C, parent_traits=[CDD:cl22856], PROPOSED)
    remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair.
- evidence_id: ev-cd17151
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
  locator: identifier, label, definition, evidence (UniProtKB:A8MYV0), mapping_status,
    curation_history (source_erratum_cd17151)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d
  support: supports
  quote: Doublecortin-like domain 1 found in doublecortin domain-containing protein
    2C (DCDC2C). DCDC2C is a member of the doublecortin (DCX) family closely related
    to its paralog DCDC2, a microtubule-associated protein (MAP) with stable double
    tandem DCX repeats of ubiquitin-like tertiary fold. Microtubules are key components
    of the cytoskeleton that are involved in cell movement, shape determination, division
    and transport. In the paralogous DCDC2 gene, human genetic variation is associated
    with reading disability (dyslexia), attention deficit hyperactivity disorder (ADHD),
    and difficulties in mathematics. DCDC2 protein interacts with many of the same
    cytoskeleton related proteins that other members of the DCX family interact with
  summary: CDD:cd17151 (label DCX1_DCDC2C, parent_traits=[CDD:cl28922], PROPOSED)
    remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair.
- evidence_id: ev-cd17154
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
  locator: identifier, label, definition, evidence (UniProtKB:A8MYV0), mapping_status,
    curation_history (source_erratum_cd17154)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 6ec1fd4e6c77d35fcd3c65b0387f517870965eeb622e47e122665a32b27c1f1d
  support: supports
  quote: Doublecortin-like domain 2 found in doublecortin domain-containing protein
    2C (DCDC2C). DCDC2C is a member of the doublecortin (DCX) family closely related
    to its paralog DCDC2, a microtubule-associated protein (MAP) with stable double
    tandem DCX repeats of a ubiquitin-like tertiary fold. Microtubules are key components
    of cytoskeleton that are involved in cell movement, shape determination, division
    and transport. In the paralogous DCDC2 gene, human genetic variation is associated
    with reading disability (dyslexia), attention deficit hyperactivity disorder (ADHD),
    and difficulties in mathematics. DCDC2 protein interacts with many of the same
    cytoskeleton related proteins that other members of the DCX family interact with
  summary: CDD:cd17154 (label DCX2_DCDC2C, parent_traits=[CDD:cl28922], PROPOSED)
    remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair.
- evidence_id: ev-cd17149
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
  locator: identifier, label, definition, evidence (PMID:16278295), mapping_status,
    curation_history (source_erratum_cd17149)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
  support: supports
  quote: Doublecortin-like domain 1 found in doublecortin domain-containing protein
    2 (DCDC2). DCDC2 is a member of the doublecortin (DCX) family. It is a microtubule-associated
    protein (MAP) with stable double tandem DCX repeats adopting a ubiquitin-like
    beta-grasp tertiary fold. Microtubules are key components of the cytoskeleton
    that are involved in cell movement, shape determination, division and transport.
    DCDC2 genetic variation in humans is associated with reading disability, attention
    deficit hyperactivity disorder (ADHD), and difficulties in mathematics. A genetic
    variant of DCDC2 associates with dyslexia, a common neurobehavioral disorder of
    reading. DCDC2 protein interacts with many of the same cytoskeleton related proteins
    that other members of the DCX family interact with
  summary: CDD:cd17149 (label DCX1_DCDC2, parent_traits=[CDD:cl28922], PROPOSED) remains
    verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair.
- evidence_id: ev-cd18593
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
  locator: identifier, label, definition, evidence (PMID:16984901), mapping_status,
    curation_history (source_erratum_cd18593)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb
  support: supports
  quote: Six-transmembrane helical domain 1 (TMD1) of multidrug resistance-associated
    protein 4 (MRP4) and similar proteins. This group represents the six-transmembrane
    domain 1 (TMD1) of multidrug resistance-associated protein 4 (MRP4), which belongs
    to the subfamily C of the ATP-binding cassette (ABC) transporter superfamily.
    The human ABCC subfamily includes nine multidrug resistance-associated proteins
    (MRP1-MRP6 corresponding to ABCC1-ABCC6, and MRP7-MRP9 corresponding to ABCC10-ABCC12,
    whereas ABCC7 is the CFTR chloride channel and ABCC8/ABCC9 are the sulfonylurea
    receptors SUR1/SUR2). Several MRP members (notably MRP1-MRP5, MRP7/ABCC10, and
    MRP8/ABCC11) function as ATP-dependent efflux pumps for endogenous organic anions,
    cyclic nucleotides, and xenobiotics, whereas physiological substrates and transport
    activity of MRP9 (ABCC12) remain less characterized. MRP family can be divided
    into two groups, depending on their structural architecture. MRP4, MRP5, MRP8,
    and MRP9 (ABCC4, 5, 11 and 12, respectively) have a typical ABC transporter structure
    and each composed of two transmembrane domains (TMD1 and TMD2) and two nucleotide
    domains (NBD1 and NBD2). On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3,
    6 and 10, respectively) have an additional N-terminal five transmembrane segments
    in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic linker
    (L0)
  summary: CDD:cd18593 (label ABC_6TM_MRP4_D1_like, parent_traits=[CDD:cl38913], PROPOSED)
    remains verified resolved on disk after Cycle 2 Stage 5 (#1188) errata repair.
- evidence_id: ev-cd17152
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
  locator: identifier, label, definition, evidence (PMID:16278295), mapping_status,
    curation_history (source_erratum_cd17152)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c
  support: supports
  quote: Doublecortin-like domain 2 found in doublecortin domain-containing protein
    2 (DCDC2). DCDC2 is a member of the doublecortin (DCX) family. It is a microtubule-associated
    protein (MAP) with stable double tandem DCX repeats adopting a ubiquitin-like
    beta-grasp tertiary fold. Microtubules are key components of the cytoskeleton
    that are involved in cell movement, shape determination, division and transport.
    DCDC2 genetic variation in humans is associated with reading disability, attention
    deficit hyperactivity disorder (ADHD), and difficulties in mathematics. A genetic
    variant of DCDC2 associates with dyslexia, a common neurobehavioral disorder of
    reading. DCDC2 protein interacts with many of the same cytoskeleton related proteins
    that other members of the DCX family interact with
  summary: 'CDD:cd17152 (label DCX2_DCDC2, parent_traits=[CDD:cl28922], PROPOSED)
    is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation:
    the off-target ubiquitin protein-modifier digression has been replaced with the
    accurate tandem DCX ubiquitin-like beta-grasp fold description, PMID:16278295
    evidence is attached, and curation_history records source_erratum_cd17152.'
- evidence_id: ev-cd17153
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
  locator: identifier, label, definition, evidence (UniProtKB:A2VCK2), mapping_status,
    curation_history (source_erratum_cd17153)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75
  support: supports
  quote: Doublecortin-like domain 2 found in doublecortin domain-containing protein
    2B (DCDC2B). DCDC2B is a member of the doublecortin (DCX) family closely related
    to its paralog DCDC2, a microtubule-associated protein (MAP) with stable double
    tandem DCX repeats of a ubiquitin-like tertiary fold. Microtubules are key components
    of cytoskeleton that are involved in cell movement, shape determination, division
    and transport. In the paralogous DCDC2 gene, human genetic variation is associated
    with reading disability (dyslexia), attention deficit hyperactivity disorder (ADHD),
    and difficulties in mathematics. DCDC2 protein interacts with many of the same
    cytoskeleton related proteins that other members of the DCX family interact with
  summary: 'CDD:cd17153 (label DCX2_DCDC2B, parent_traits=[CDD:cl28922], PROPOSED)
    is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation:
    DCDC2B is explicitly distinguished from its paralog DCDC2 in the domain description
    and human reading-disability/ADHD genetics summary, UniProtKB:A2VCK2 evidence
    is attached, and curation_history records source_erratum_cd17153.'
- evidence_id: ev-cd15884
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
  locator: identifier, label, definition, evidence (PMID:9159129), mapping_status,
    curation_history (source_erratum_cd15884)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510
  support: supports
  quote: C-terminal SNARE motif of SNAP23. C-terminal SNARE motifs of SNAP23, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. SNAP23 interacts with Syntaxin-4 (Qa) and the R-SNARE
    VAMP8. The complex plays a role in exocytosis of secretory granule. Qb/Qc SNAREs
    consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb
    subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and lack a transmembrane domain; SNAP23 is anchored
    to target membranes via palmitoylated cysteine residues in the linker between
    its two SNARE motifs. In general, the SNARE complex mediates membrane fusion,
    important for trafficking of newly synthesized proteins, recycling of pre-existing
    proteins and organelle formation. SNARE proteins are classified into four groups,
    Qa-, Qb-, Qc- and R-SNAREs, depending on whether the residue in the hydrophilic
    center layer of the four-helical bundle is a glutamine (Q) or arginine (R). Qa-,
    as well as Qb- and Qc-SNAREs, are localized to target organelle membranes, while
    R-SNARE is localized to vesicle membranes. They form unique complexes consisting
    of one member of each subgroup, that mediate fusion between a specific type of
    vesicles and their target organelle. Their SNARE motifs form twisted and parallel
    heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are SNAP25,
    SNAP29, SNAP47 and SEC9
  summary: 'CDD:cd15884 (label SNARE_SNAP23C, parent_traits=[CDD:cl22856], PROPOSED)
    is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation:
    the false Qb/Qc transmembrane-domain claim has been replaced with the accurate
    statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP23 is anchored
    to target membranes via palmitoylated cysteine residues in its inter-motif linker,
    PMID:9159129 evidence is attached, and curation_history records source_erratum_cd15884.'
- evidence_id: ev-cd15895
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
  locator: identifier, label, definition, evidence (PMID:9159129), mapping_status,
    curation_history (source_erratum_cd15895)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b
  support: supports
  quote: N-terminal SNARE motif of SNAP23. N-terminal SNARE motifs of SNAP23, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. SNAP23 interacts with Syntaxin-4 (Qa) and the R-SNARE
    VAMP8. The complex plays a role in exocytosis of secretory granule. Qb/Qc SNAREs
    consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb
    subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and lack a transmembrane domain; SNAP23 is anchored
    to target membranes via palmitoylated cysteine residues in the linker between
    its two SNARE motifs. In general, the SNARE complex mediates membrane fusion,
    important for trafficking of newly synthesized proteins, recycling of pre-existing
    proteins and organelle formation. SNARE proteins are classified into four groups,
    Qa-, Qb-, Qc- and R-SNAREs, depending on whether the residue in the hydrophilic
    center layer of the four-helical bundle is a glutamine (Q) or arginine (R). Qa-,
    as well as Qb- and Qc-SNAREs, are localized to target organelle membranes, while
    R-SNARE is localized to vesicle membranes. They form unique complexes consisting
    of one member of each subgroup, that mediate fusion between a specific type of
    vesicles and their target organelle. Their SNARE motifs form twisted and parallel
    heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are SNAP25,
    SNAP29, SNAP47 and SEC9
  summary: 'CDD:cd15895 (label SNARE_SNAP23N, parent_traits=[CDD:cl22856], PROPOSED)
    is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation:
    the false Qb/Qc transmembrane-domain claim has been replaced with the accurate
    statement that Qb/Qc SNAREs lack a transmembrane domain and that SNAP23 is anchored
    to target membranes via palmitoylated cysteine residues in its inter-motif linker,
    PMID:9159129 evidence is attached, and curation_history records source_erratum_cd15895.'
- evidence_id: ev-cd18599
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
  locator: identifier, label, definition, evidence (PMID:16984901), mapping_status,
    curation_history (source_erratum_cd18599)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585
  support: supports
  quote: Six-transmembrane helical domain 2 (TMD2) of multidrug resistance-associated
    proteins (MRPs) 5, 8, and 9. This group represents the six-transmembrane domain
    2 (TMD2) of multidrug resistance-associated proteins (MRPs) 5, 8, and 9, all of
    which are belonging to the subfamily C of the ATP-binding cassette (ABC) transporter
    superfamily. The human ABCC subfamily includes nine multidrug resistance-associated
    proteins (MRP1-MRP6 corresponding to ABCC1-ABCC6, and MRP7-MRP9 corresponding
    to ABCC10-ABCC12, whereas ABCC7 is the CFTR chloride channel and ABCC8/ABCC9 are
    the sulfonylurea receptors SUR1/SUR2). Several MRP members (notably MRP1-MRP5,
    MRP7/ABCC10, and MRP8/ABCC11) function as ATP-dependent efflux pumps for endogenous
    organic anions, cyclic nucleotides, and xenobiotics, whereas physiological substrates
    and transport activity of MRP9 (ABCC12) remain less characterized. MRP family
    can be divided into two groups, depending on their structural architecture. MRP4,
    MRP5, MRP8, and MRP9 (ABCC4, 5, 11 and 12, respectively) have a typical ABC transporter
    structure and each composed of two transmembrane domains (TMD1 and TMD2) and two
    nucleotide domains (NBD1 and NBD2). On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1,
    2, 3, 6 and 10, respectively) have an additional N-terminal five transmembrane
    segments in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic
    linker (L0)
  summary: 'CDD:cd18599 (label ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913], PROPOSED)
    is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation:
    the false MRP7=ABCC7 (CFTR) assignment is corrected to MRP7=ABCC10, the MRP1-MRP9
    multidrug-resistance efflux overclaim is qualified, PMID:16984901 evidence is
    attached, and curation_history records source_erratum_cd18599.'
- evidence_id: ev-cd18601
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
  locator: identifier, label, definition, evidence (PMID:16984901), mapping_status,
    curation_history (source_erratum_cd18601)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099
  support: supports
  quote: Six-transmembrane helical domain 2 (TMD2) of multidrug resistance-associated
    protein 4 (MRP4) and similar proteins. This group represents the six-transmembrane
    domain 2 (TMD2) of multidrug resistance-associated protein 4 (MRP4), which belongs
    to the subfamily C of the ATP-binding cassette (ABC) transporter superfamily.
    The human ABCC subfamily includes nine multidrug resistance-associated proteins
    (MRP1-MRP6 corresponding to ABCC1-ABCC6, and MRP7-MRP9 corresponding to ABCC10-ABCC12,
    whereas ABCC7 is the CFTR chloride channel and ABCC8/ABCC9 are the sulfonylurea
    receptors SUR1/SUR2). Several MRP members (notably MRP1-MRP5, MRP7/ABCC10, and
    MRP8/ABCC11) function as ATP-dependent efflux pumps for endogenous organic anions,
    cyclic nucleotides, and xenobiotics, whereas physiological substrates and transport
    activity of MRP9 (ABCC12) remain less characterized. MRP family can be divided
    into two groups, depending on their structural architecture. MRP4, MRP5, MRP8,
    and MRP9 (ABCC4, 5, 11 and 12, respectively) have a typical ABC transporter structure
    and each composed of two transmembrane domains (TMD1 and TMD2) and two nucleotide
    domains (NBD1 and NBD2). On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3,
    6 and 10, respectively) have an additional N-terminal five transmembrane segments
    in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic linker
    (L0)
  summary: 'CDD:cd18601 (label ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913],
    PROPOSED) is verified repaired on disk after Cycle 3 Stage 5 (#1210) errata remediation:
    the false MRP7=ABCC7 (CFTR) assignment is corrected to MRP7=ABCC10, the MRP1-MRP9
    multidrug-resistance efflux overclaim is qualified, PMID:16984901 evidence is
    attached, and curation_history records source_erratum_cd18601.'
- evidence_id: ev-cd15894-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
  locator: identifier, label, definition, evidence (PMID:9759094)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: d11a67560ebb84bf867f67027f23109a5631b72953aa870075b96116cd599368
  support: supports
  summary: 'Cycle 1 remediated sibling CDD:cd15894 (SNARE_SNAP25N, #1171) establishing
    the palmitoylated inter-motif linker membrane-anchoring wording for Qb/Qc SNAREs
    (PMID:9759094).'
- evidence_id: ev-cd17150-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
  locator: identifier, label, definition, canonical_examples (UniProtKB:A2VCK2), evidence
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: fe5af61fd44b4a50b6c9f0ab06ddd1d717895a010f788b8096ff64d3f68e4756
  support: supports
  quote: Doublecortin-like domain 1 found in doublecortin domain-containing protein
    2B (DCDC2B). DCDC2B is a member of the doublecortin (DCX) family closely related
    to its paralog DCDC2, a microtubule-associated protein (MAP) with stable double
    tandem DCX repeats of ubiquitin-like tertiary fold. Microtubules are key components
    of the cytoskeleton that are involved in cell movement, shape determination, division
    and transport. In the paralogous DCDC2 gene, human genetic variation is associated
    with reading disability (dyslexia), attention deficit hyperactivity disorder (ADHD),
    and difficulties in mathematics. DCDC2 protein interacts with many of the same
    cytoskeleton related proteins that other members of the DCX family interact with
  summary: 'Cycle 1 remediated N-terminal first-repeat sibling CDD:cd17150 (label
    DCX1_DCDC2B, carrying human DCDC2B UniProtKB:A2VCK2, #1171) establishing the paralog-qualified
    DCDC2B vs DCDC2 wording needed on C-terminal second-repeat sibling CDD:cd17153
    (F20).'
- evidence_id: ev-cd18592-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
  locator: identifier, label, definition, evidence (PMID:16984901)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: fad0b6039c5386b3caf40fc650099ec7bfd126ff7854d42aeb805708a18c3f9a
  support: supports
  summary: 'Cycle 1 remediated N-terminal TMD1 sibling CDD:cd18592 (label ABC_6TM_MRP5_8_9_D1,
    #1171) establishing the corrected MRP7=ABCC10 / CFTR=ABCC7 nomenclature and qualified
    MRP1-MRP9 efflux phrasing needed on TMD2 sibling CDD:cd18599 (F23).'
- evidence_id: ev-cd20534-cd04590-siblings
  kind: record_content
  reference: data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml
  locator: CDD:cd20534 (CYCLIN_CCNM_CCNQ_rpt1) and CDD:cd04590 (CBS_pair_CorC_HlyC_assoc)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 72fbd3487668c097281cf6ee45a4daf0366a2bcc80866330f8ed4832141d7e88
  support: supports
  summary: Boundary-contrast siblings CDD:cd20534 (N-terminal cyclin box 1 of CCNQ/FAM58A)
    and CDD:cd04590 (CBS-pair domain of CNNM/ACDP magnesium transporters) supporting
    resolved finding F13 on CDD:cd20535.
- evidence_id: ev-prior-stage4-cd00104
  kind: record_content
  reference: reviews/structured/20261022T052200Z-cdd-cd00104-record-review/review.yaml
  locator: finding F1
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: f8340019e447b9a37ab1eb333826a61f818c58aa365e43480917f69d87da8fa9
  support: supports
  summary: Cycle 1 Stage 4 single-record review of CDD:cd00104 (F1).
- evidence_id: ev-prior-stage4-cohort
  kind: record_content
  reference: reviews/structured/20261022T052300Z-cdd-stage3-domain-cohort-review/review.yaml
  locator: findings F1-F12
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: ce693cda666fcc7f5ad2d22b11e67b9a9d0b9d32859b1d0ca5e3e982f04dfa8e
  support: supports
  summary: Cycle 1 Stage 4 cohort review of 12 CDD records (F1-F12).
- evidence_id: ev-prior-stage5-cohort
  kind: record_content
  reference: reviews/structured/20261022T081000Z-cdd-stage5-remediation-review/review.yaml
  locator: findings F1-F12
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 438b6712ef02fc88990c1bf5e054fc2b901925f85b2eed0f4da2cc3015be6330
  support: supports
  summary: Cycle 1 Stage 5 post-remediation review resolving F3-F12 and deferring
    F1-F2.
- evidence_id: ev-cycle1-stage6-evidence
  kind: record_content
  reference: reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/evidence.yaml
  locator: 'proteintraitsmech-infra-0003 resolution (#1172, PR #1175)'
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 3cded5bbfd329238d0e695ce9bc64098886a7724b03dacd1b524f91ca7903201
  support: supports
  summary: Cycle 1 Stage 6 workflow evidence documenting the resolution of F1 (CDD:cd00104)
    and F2 (CDD:cd00959).
- evidence_id: ev-cycle2-stage4-cohort
  kind: record_content
  reference: reviews/structured/20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review/review.yaml
  locator: findings F1, F2, F13-F18
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 2722da7d2d32c603f417b4efaefc9001bc2fa2751bc3184b5ba2f23a8cdcb7b0
  support: supports
  summary: Cycle 2 Stage 4 cohort review of 8 CDD records (F1, F2 resolved; F13-F18
    opened).
- evidence_id: ev-cycle2-stage5-cohort
  kind: record_content
  reference: reviews/structured/20261025T233000Z-cdd-cycle2-stage5-remediation-review/review.yaml
  locator: findings F1, F2, F13-F18 resolved (#1188)
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 513cb559af7f1c2dfa19a4307c1fd06a164ea68ec5f07770649038200ed1899e
  support: supports
  summary: Cycle 2 Stage 5 post-remediation review verifying F1, F2, and F13-F18 resolved
    on disk.
- evidence_id: ev-cycle2-stage5-evidence
  kind: record_content
  reference: reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-05/revision-0001/evidence.yaml
  locator: 'findings F1, F2, F13-F18 resolved (PR #1189)'
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 37cf6670f427c35fabdccb772c188323d7d5128d595e571f39561fab61fc709c
  support: supports
  summary: Predecessor Cycle 2 Stage 5 workflow evidence manifest from which findings
    F1, F2, and F13-F18 are carried forward.
- evidence_id: ev-cdd-errata-infrastructure
  kind: record_content
  reference: scripts/cdd_errata.py
  locator: CDD_ERRATA table (24 entries), scripts/repair_cdd_errata.py, scripts/seed_cdd.py,
    and tests/test_cdd_errata.py
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 332155e8c1f1a119ca0f3c4394b49fa775bcc8d9f4c68e1f43183bd97b64d962
  support: supports
  summary: 'scripts/cdd_errata.py now contains 24 accession-keyed CDD errata entries
    (12 from Cycle 1, 6 from Cycle 2, and 6 from Cycle 3 #1210) wired into scripts/seed_cdd.py
    and scripts/repair_cdd_errata.py and verified by 190 unit and writer-guard tests.'
- evidence_id: ev-cycle3-stage4-cd17152
  kind: record_content
  reference: reviews/structured/20261030T092000Z-cdd-cd17152-record-review/review.yaml
  locator: finding F19
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: c06176c3073f1ec5d26954550500e22ecb07649a53c18e3700fd1ee352ada514
  support: supports
  summary: Cycle 3 Stage 4 single-record scientific review of CDD:cd17152 identifying
    finding F19.
- evidence_id: ev-cycle3-stage4-cohort
  kind: record_content
  reference: reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml
  locator: findings F1, F2, F13-F24
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 2d8fe1c367294f3e5660badc28211c13c97763d788ce0eb9ca3ef1cd134587f8
  support: supports
  summary: Cycle 3 Stage 4 cohort review of 14 CDD records (F1, F2, F13-F18 verified
    resolved; F19-F24 opened).
- evidence_id: ev-cycle3-stage4-evidence
  kind: record_content
  reference: reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-04/revision-0001/evidence.yaml
  locator: 'findings F1, F2, F13-F18 resolved; F19-F24 open (PR #1208)'
  accessed_at: '2026-10-30T11:52:00Z'
  snapshot_sha256: 675d9c6efc52c8ad25d7e0a13f9306fe0d92d901a3f629ec9a5328230feec9e9
  support: supports
  summary: Predecessor Cycle 3 Stage 4 workflow evidence manifest from which findings
    F1, F2, and F13-F24 are carried forward into Stage 5.
assessments:
- assessment_id: cohort-boundaries-and-identity
  area: scope
  topic: Category placement and tandem-repeat/subfamily boundary distinctness across
    all 14 CDD records
  outcome: supported
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  - CDD:cd20535
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd15884
  - ev-cd15885
  - ev-cd15895
  - ev-cd17149
  - ev-cd17151
  - ev-cd17152
  - ev-cd17153
  - ev-cd17154
  - ev-cd18593
  - ev-cd18599
  - ev-cd18601
  - ev-cd20535
  - ev-cd15894-sibling
  - ev-cd17150-sibling
  - ev-cd18592-sibling
  - ev-cd20534-cd04590-siblings
  summary: 'All 14 records are genuine conserved protein sequence domain profiles
    (trait_axis: SEQUENCE, trait_category: SEQ_DOMAIN; parent_traits=CDD:cl00097,
    CDD:cl21457, CDD:cl40454, CDD:cl22856, CDD:cl28922, and CDD:cl38913) with distinct
    CDD PSSM identifiers and non-overlapping repeat intervals or paralog-subfamily
    scopes. None should be merged or lumped with sibling CDD profiles.'
- assessment_id: carry-forward-f1-f2-f13-f18-resolved-on-disk
  area: consistency
  topic: Verification of Cycle 1 and Cycle 2 carry-forward findings F1, F2, and F13-F18
  outcome: supported
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd15885
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17154
  - CDD:cd18593
  - CDD:cd20535
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd15885
  - ev-cd17149
  - ev-cd17151
  - ev-cd17154
  - ev-cd18593
  - ev-cd20535
  - ev-cycle1-stage6-evidence
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  summary: All 8 carry-forward records from Cycle 1 Stage 6 (#1172) and Cycle 2 Stage
    5 (#1188) — CDD:cd00104 (F1), CDD:cd00959 (F2), CDD:cd20535 (F13), CDD:cd15885
    (F14), CDD:cd17151 (F15), CDD:cd17154 (F16), CDD:cd17149 (F17), and CDD:cd18593
    (F18) — remain verified resolved in the Stage 5 working tree with entries in scripts/cdd_errata.py,
    literature-backed evidence, and append-only curation_history events.
- assessment_id: new-cycle3-sibling-cdd-records-upstream-prose-defects
  area: consistency
  topic: Resolution of upstream CDD nomenclature, paralog-scope, and structural/biochemical
    contradictions across the 6 Cycle 3 sibling CDD records (F19-F24)
  outcome: supported
  target_ids:
  - CDD:cd15884
  - CDD:cd15895
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd15884
  - ev-cd15895
  - ev-cd17152
  - ev-cd17153
  - ev-cd18599
  - ev-cd18601
  - ev-cd15894-sibling
  - ev-cd17149
  - ev-cd17150-sibling
  - ev-cd17154
  - ev-cd18592-sibling
  - ev-cd18593
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cd17152
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  summary: 'All 6 sibling CDD records audited in Cycle 3 Stage 4 (CDD:cd17152, CDD:cd17153,
    CDD:cd15884, CDD:cd15895, CDD:cd18599, CDD:cd18601) have now been repaired in
    place in Cycle 3 Stage 5 (#1210) via scripts/cdd_errata.py and scripts/repair_cdd_errata.py:
    the off-target ubiquitin protein-modifier digression on CDD:cd17152, the unqualified
    DCDC2B->DCDC2 paralog disease switch on CDD:cd17153, the false Qb/Qc transmembrane-domain
    claims on CDD:cd15884 and CDD:cd15895, and the MRP7=ABCC7/CFTR misassignment plus
    MRP1-MRP9 multidrug-resistance overclaim on CDD:cd18599 and CDD:cd18601 are all
    resolved with grounded evidence and append-only curation_history provenance.'
boundary_decisions:
- action: retain
  target_ids:
  - CDD:cd00104
  - CDD:cd00959
  - CDD:cd20535
  evidence_ids:
  - ev-cd00104
  - ev-cd00959
  - ev-cd20535
  - ev-cd20534-cd04590-siblings
  rationale: Retain resolved carry-forward records CDD:cd00104 (KAZAL_FS, parent_traits=[CDD:cl00097]),
    CDD:cd00959 (DeoC, parent_traits=[CDD:cl21457]), and CDD:cd20535 (CYCLIN_CCNM_CCNQ_rpt2,
    parent_traits=[CDD:cl40454], C-terminal second cyclin box of CCNQ/FAM58A) as distinct
    conserved domain families.
- action: retain
  target_ids:
  - CDD:cd15884
  - CDD:cd15885
  - CDD:cd15895
  evidence_ids:
  - ev-cd15884
  - ev-cd15885
  - ev-cd15895
  - ev-cd15894-sibling
  rationale: Retain CDD:cd15895 (label=SNARE_SNAP23N, N-terminal Qb SNARE motif of
    SNAP23) and CDD:cd15884 (label=SNARE_SNAP23C, C-terminal Qc SNARE motif of SNAP23)
    as non-overlapping tandem coiled-coil SNARE domains on SNAP23 (Homo sapiens O00161,
    Mus musculus O09044) under parent_traits [CDD:cl22856], and retain both as distinct
    paralog-subfamily profiles separate from the neuronal SNAP25 N-terminal Qb (CDD:cd15894)
    and C-terminal Qc (CDD:cd15885) SNARE motif profiles.
- action: retain
  target_ids:
  - CDD:cd17149
  - CDD:cd17151
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd17154
  evidence_ids:
  - ev-cd17149
  - ev-cd17151
  - ev-cd17152
  - ev-cd17153
  - ev-cd17154
  - ev-cd17150-sibling
  rationale: Retain all 5 target doublecortin-like repeat profiles under parent_traits
    [CDD:cl28922] — CDD:cd17149 (DCX1_DCDC2, repeat 1 of DCDC2), CDD:cd17152 (DCX2_DCDC2,
    repeat 2 of DCDC2), CDD:cd17153 (DCX2_DCDC2B, repeat 2 of DCDC2B; sibling of repeat
    1 CDD:cd17150), CDD:cd17151 (DCX1_DCDC2C, repeat 1 of DCDC2C), and CDD:cd17154
    (DCX2_DCDC2C, repeat 2 of DCDC2C) — because each models a distinct N-terminal
    vs C-terminal tandem repeat position or a distinct human/mammalian paralog subfamily
    (DCDC2, DCDC2B, DCDC2C).
- action: retain
  target_ids:
  - CDD:cd18593
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd18593
  - ev-cd18599
  - ev-cd18601
  - ev-cd18592-sibling
  rationale: Retain CDD:cd18593 (ABC_6TM_MRP4_D1_like, N-terminal TMD1 of MRP4/ABCC4),
    CDD:cd18601 (ABC_6TM_MRP4_D2_like, C-terminal TMD2 of MRP4/ABCC4), and CDD:cd18599
    (ABC_6TM_MRP5_8_9_D2, C-terminal TMD2 of MRPs 5/8/9, ABCC5/ABCC11/ABCC12; sibling
    of N-terminal TMD1 CDD:cd18592) under parent_traits [CDD:cl38913] because they
    represent non-overlapping N-terminal TMD1 vs C-terminal TMD2 six-helix bundles
    and distinct ABCC subfamily clades.
findings:
- finding_id: F1
  issue_key: cdd-cd00104-kazal-definition-typo-and-inhibitor-target-confusion
  category: consistency
  severity: minor
  status: resolved
  certainty: confirmed
  title: CDD:cd00104 definition misspells chymotrypsin and lists avian ovomucoids
    as target serine proteases
  description: CDD:cd00104 previously stated 'Kazal inhibitors inhibit serine proteases,
    such as, trypsin, chyomotrypsin, avian ovomucoids, and elastases', misspelling
    'chymotrypsin' and listing 'avian ovomucoids' (Kazal-type inhibitor proteins,
    PMID:6192856) as target enzymes.
  target_ids:
  - CDD:cd00104
  field_paths:
  - data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml#/definition
  evidence_ids:
  - ev-cd00104
  - ev-prior-stage4-cd00104
  - ev-prior-stage4-cohort
  - ev-prior-stage5-cohort
  - ev-cycle1-stage6-evidence
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  disposition_reason: 'Repaired CDD:cd00104 via scripts/cdd_errata.py and scripts/repair_cdd_errata.py
    in Cycle 1 Stage 6 (#1172, PR #1175), correcting ''chyomotrypsin'' to ''chymotrypsin'',
    distinguishing avian ovomucoids as canonical Kazal-type inhibitors rather than
    target proteases (PMID:6192856), and updating all 39 durable qualified_record_bindings.jsonl.d
    receipts (covering all 26 QUALIFIED canonical examples out of 28 total canonical_examples
    on the record) to the new record_sha256 (62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26).'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261022T052200Z-cdd-cd00104-record-review
    finding_id: F1
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261022T052300Z-cdd-stage3-domain-cohort-review
    finding_id: F1
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261022T081000Z-cdd-stage5-remediation-review
    finding_id: F1
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F1
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F1
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F1
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1172
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F2
  issue_key: cdd-cd00959-dera-duplicated-opening-sentence
  category: consistency
  severity: minor
  status: resolved
  certainty: confirmed
  title: CDD:cd00959 definition repeats its opening title sentence verbatim
  description: CDD:cd00959 previously began with the duplicated sentence '2-deoxyribose-5-phosphate
    aldolase (DERA) of the DeoC family. 2-deoxyribose-5-phosphate aldolase (DERA)
    of the DeoC family.' due to upstream CDD title+description concatenation.
  target_ids:
  - CDD:cd00959
  field_paths:
  - data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml#/definition
  evidence_ids:
  - ev-cd00959
  - ev-prior-stage4-cohort
  - ev-prior-stage5-cohort
  - ev-cycle1-stage6-evidence
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  disposition_reason: 'Repaired CDD:cd00959 via scripts/cdd_errata.py and scripts/repair_cdd_errata.py
    in Cycle 1 Stage 6 (#1172, PR #1175), removing the duplicated opening title sentence
    and updating both durable qualified_record_bindings.jsonl.d receipts (covering
    the 2 QUALIFIED canonical examples out of 5 total canonical_examples on the record)
    to the new record_sha256 (3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f).'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261022T052300Z-cdd-stage3-domain-cohort-review
    finding_id: F2
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261022T081000Z-cdd-stage5-remediation-review
    finding_id: F2
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F2
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F2
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F2
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1172
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F13
  issue_key: cdd-cd20535-ccnq-rpt2-cnnm-acdp-magnesium-transporter-conflation
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd20535 (CYCLIN_CCNM_CCNQ_rpt2) conflates the second cyclin box of Cyclin-Q/Cyclin-M
    (CCNQ/FAM58A) with the CNNM1-4 (ACDP) magnesium transporter family
  description: CDD:cd20535 (label=CYCLIN_CCNM_CCNQ_rpt2, parent_traits=[CDD:cl40454])
    models the C-terminal second cyclin box of Cyclin-Q/Cyclin-M (CCNQ/FAM58A; unpromoted
    seed examples Mus musculus UniProtKB:Q8QZR8 and Homo sapiens UniProtKB:Q8N1B3),
    the activating cyclin partner of CDK10 mutated in X-linked STAR syndrome (PMID:23912459),
    but sentence 2 of its upstream CDD definition states 'The CCNM family proteins,
    also called ancient conserved domain proteins (ACDPs), are evolutionarily conserved
    Mg2+ transporters', conflating CCNM/CCNQ with the unrelated CNNM1-4 (ACDP) CBS-pair
    magnesium transporter family (contrasted with CDD:cd04590 in repaired sibling
    CDD:cd20534).
  target_ids:
  - CDD:cd20535
  field_paths:
  - data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml#/definition
  evidence_ids:
  - ev-cd20535
  - ev-cd20534-cd04590-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage4-cohort
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1188
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd20535 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1188): replaced the false CNNM1-4/ACDP magnesium
    transporter sentence with the accurate CDK10-activating cyclin CCNQ/FAM58A description,
    added PMID:23912459 evidence, and recorded curation_history action source_erratum_cd20535.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202200Z-cdd-cd20535-record-review
    finding_id: F13
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F13
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F13
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F13
- finding_id: F14
  issue_key: cdd-cd15885-snap25c-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd15885 (SNARE_SNAP25C) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP25 is membrane-anchored via palmitoylated cysteines
  description: CDD:cd15885 (label=SNARE_SNAP25C, parent_traits=[CDD:cl22856]) models
    the C-terminal Qc SNARE motif of SNAP25 (unpromoted seed examples Mus musculus
    UniProtKB:P60879, Homo sapiens UniProtKB:P60880, and Drosophila melanogaster UniProtKB:P36975),
    but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil
    helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging
    to the Qc subgroup), which mediate the interactions with other SNARE proteins,
    and a transmembrane domain.' SNAP25-family Qb/Qc t-SNAREs lack a transmembrane
    domain and attach to membranes via palmitoylated cysteines in the inter-motif
    linker between the N-terminal Qb (CDD:cd15894) and C-terminal Qc (CDD:cd15885)
    SNARE motifs (PMID:9759094).
  target_ids:
  - CDD:cd15885
  field_paths:
  - data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml#/definition
  evidence_ids:
  - ev-cd15885
  - ev-cd15894-sibling
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage4-cohort
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1188
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd15885 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1188): replaced the false transmembrane-domain
    claim with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain
    and that SNAP25 is membrane-anchored via palmitoylated cysteines in its inter-motif
    linker, added PMID:9759094 evidence, and recorded curation_history action source_erratum_cd15885.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F14
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F14
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F14
- finding_id: F15
  issue_key: cdd-cd17151-dcdc2c-typo-and-dcdc2-paralog-disease-switch
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd17151 (DCX1_DCDC2C) misspells Doublecortin-like as Dublecortin-like
    in definition and switches to paralog DCDC2 disease genetics
  description: CDD:cd17151 (label=DCX1_DCDC2C, parent_traits=[CDD:cl28922]) models
    the N-terminal first doublecortin-like domain (DCX1) of human DCDC2C (unpromoted
    seed example UniProtKB:A8MYV0, HGNC:33863), but its definition begins with the
    typo 'Dublecortin-like domain 1 found in doublecortin domain-containing protein
    2C (DCDC2C).' and immediately switches in sentence 2 to paralog DCDC2 ('DCDC2
    is a member of doublecortin (DCX) family.' and 'DCDC2 genetic variation in humans
    is associated with reading disability, attention deficit hyperactivity disorder
    (ADHD), and difficulties in mathematics.') without distinguishing DCDC2C from
    DCDC2 (UniProtKB:Q9UHG0, CDD:cd17149/CDD:cd17152).
  target_ids:
  - CDD:cd17151
  field_paths:
  - data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml#/definition
  evidence_ids:
  - ev-cd17151
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage4-cohort
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1188
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd17151 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1188): corrected ''Dublecortin-like'' to ''Doublecortin-like'',
    distinguished DCDC2C (UniProtKB:A8MYV0) from its paralog DCDC2 (UniProtKB:Q9UHG0)
    in the phenotype summary, added UniProtKB:A8MYV0 evidence, and recorded curation_history
    action source_erratum_cd17151.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F15
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F15
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F15
- finding_id: F16
  issue_key: cdd-cd17154-dcdc2c-rpt2-dcdc2-paralog-disease-switch
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd17154 (DCX2_DCDC2C) switches mid-definition from DCDC2C to paralog
    DCDC2 reading-disability and ADHD genetics
  description: CDD:cd17154 (label=DCX2_DCDC2C, parent_traits=[CDD:cl28922]) models
    the C-terminal second doublecortin-like domain (DCX2) of human DCDC2C (unpromoted
    seed example UniProtKB:A8MYV0, HGNC:33863), but sentence 2 switches without qualification
    to paralog DCDC2 ('DCDC2 is a member of the doublecortin (DCX) family.' and 'DCDC2
    genetic variation in humans is associated with reading disability, attention deficit
    hyperactivity disorder (ADHD), and difficulties in mathematics.') without distinguishing
    DCDC2C from DCDC2 (UniProtKB:Q9UHG0, CDD:cd17149/CDD:cd17152).
  target_ids:
  - CDD:cd17154
  field_paths:
  - data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml#/definition
  evidence_ids:
  - ev-cd17154
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage4-cohort
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1188
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd17154 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1188): distinguished DCDC2C (UniProtKB:A8MYV0)
    from its paralog DCDC2 (UniProtKB:Q9UHG0) in the domain description and human
    genetics phenotype summary, added UniProtKB:A8MYV0 evidence, and recorded curation_history
    action source_erratum_cd17154.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F16
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F16
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F16
- finding_id: F17
  issue_key: cdd-cd17149-dcdc2-typo-and-ubiquitin-modifier-digression
  category: consistency
  severity: minor
  status: resolved
  certainty: confirmed
  title: CDD:cd17149 (DCX1_DCDC2) misspells Doublecortin-like as Dublecortin-like
    in definition and interpolates an off-target ubiquitin protein-modifier sentence
  description: CDD:cd17149 (label=DCX1_DCDC2, parent_traits=[CDD:cl28922]) models
    the N-terminal first doublecortin-like domain (DCX1) of human DCDC2 (unpromoted
    seed example UniProtKB:Q9UHG0, HGNC:18141), begins its definition with the typo
    'Dublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2).',
    and interpolates an off-target sentence defining the ubiquitin protein modifier
    ('Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various
    cellular processes, including transcriptional regulation, cell cycle control,
    and DNA repair.') even though DCX domains only adopt a ubiquitin-like beta-grasp
    fold and do not function as ubiquitin protein modifiers.
  target_ids:
  - CDD:cd17149
  field_paths:
  - data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml#/definition
  evidence_ids:
  - ev-cd17149
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage4-cohort
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1188
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd17149 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1188): corrected ''Dublecortin-like'' to ''Doublecortin-like'',
    replaced the off-target ubiquitin protein-modifier digression with the tandem
    DCX ubiquitin-like beta-grasp repeat description, added PMID:16278295 evidence,
    and recorded curation_history action source_erratum_cd17149.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F17
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F17
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F17
- finding_id: F18
  issue_key: cdd-cd18593-mrp4-abcc-mrp7-cftr-misassignment-and-mdr-overclaim
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd18593 (ABC_6TM_MRP4_D1_like) misassigns MRP7 to ABCC7 (CFTR) instead
    of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9
    members
  description: CDD:cd18593 (label=ABC_6TM_MRP4_D1_like, parent_traits=[CDD:cl38913])
    models TMD1 of MRP4/ABCC4 (unpromoted seed examples Homo sapiens UniProtKB:O15439
    and Mus musculus UniProtKB:E9Q236), but carries the corrupted upstream CDD ABCC
    template text stating 'On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1, 2, 3, 6
    and 7, respectively) have an additional N-terminal five transmembrane segments
    in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic linker
    (L0)' and claiming 'The MRP subfamily (ABCC subfamily) is composed of 13 members,
    of which MRP1 to MRP9 are the major transporters that cause multidrug resistance
    in tumor cells by pumping anticancer drugs out of the cell.' In HGNC/UniProt nomenclature,
    ABCC7 is CFTR (an epithelial chloride channel lacking TMD0), whereas MRP7 is ABCC10
    (UniProtKB:Q5T3U5), MRP8 is ABCC11, and MRP9 is ABCC12 (a paralog whose physiological
    substrates and transport activity remain less characterized, PMID:16984901).
  target_ids:
  - CDD:cd18593
  field_paths:
  - data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml#/definition
  evidence_ids:
  - ev-cd18593
  - ev-cd18592-sibling
  - ev-cdd-errata-infrastructure
  - ev-cycle2-stage4-cohort
  - ev-cycle2-stage5-cohort
  - ev-cycle2-stage5-evidence
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1188
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd18593 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1188): corrected the false mapping of MRP7 to ABCC7
    (MRP7 is ABCC10; ABCC7 is CFTR), qualified the overgeneralized tumor multidrug-resistance
    efflux claim across MRP1-MRP9, added PMID:16984901 evidence, and recorded curation_history
    action source_erratum_cd18593.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
    finding_id: F18
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
    finding_id: F18
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F18
- finding_id: F19
  issue_key: cdd-cd17152-dcdc2-rpt2-ubiquitin-modifier-digression
  category: consistency
  severity: minor
  status: resolved
  certainty: confirmed
  title: CDD:cd17152 (DCX2_DCDC2) interpolates an off-target ubiquitin protein-modifier
    definition sentence into a microtubule-binding DCX repeat profile
  description: CDD:cd17152 (label=DCX2_DCDC2, parent_traits=[CDD:cl28922]) models
    the C-terminal second doublecortin-like domain (DCX2) of DCDC2 (unpromoted seed
    examples Homo sapiens UniProtKB:Q9UHG0 and Mus musculus UniProtKB:Q5DU00), a microtubule-associated
    protein with tandem ubiquitin-like beta-grasp DCX repeats associated with human
    reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition
    interpolates the off-target sentence 'Ubiquitin (Ub) is a protein modifier in
    eukaryotes that is involved in various cellular processes, including transcriptional
    regulation, cell cycle control, and DNA repair.' even though DCX domains only
    adopt a ubiquitin-like beta-grasp fold and do not function as ubiquitin protein
    modifiers, and the record lacks an evidence block citing PMID:16278295.
  target_ids:
  - CDD:cd17152
  field_paths:
  - data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml#/definition
  evidence_ids:
  - ev-cd17152
  - ev-cd17149
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cd17152
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1210
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd17152 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1210): replaced the off-target ubiquitin protein-modifier
    digression with the tandem DCX ubiquitin-like beta-grasp repeat description matching
    N-terminal repeat 1 sibling CDD:cd17149, added PMID:16278295 evidence, advanced
    mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd17152.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092000Z-cdd-cd17152-record-review
    finding_id: F19
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F19
- finding_id: F20
  issue_key: cdd-cd17153-dcdc2b-rpt2-dcdc2-paralog-disease-switch
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd17153 (DCX2_DCDC2B) switches mid-definition from DCDC2B to paralog
    DCDC2 reading-disability and ADHD genetics
  description: CDD:cd17153 (label=DCX2_DCDC2B, parent_traits=[CDD:cl28922]) models
    the C-terminal second doublecortin-like domain (DCX2) of DCDC2B (Homo sapiens
    UniProtKB:A2VCK2, HGNC:33489, carried on N-terminal repeat 1 sibling CDD:cd17150),
    but sentence 2 switches without qualification to paralog DCDC2 ('DCDC2 is a member
    of the doublecortin (DCX) family.' and 'DCDC2 genetic variation in humans is associated
    with reading disability, attention deficit hyperactivity disorder (ADHD), and
    difficulties in mathematics. A genetic variant of DCDC2 associates with dyslexia,
    a common neurobehavioral disorder of reading.') without distinguishing DCDC2B
    from DCDC2 (UniProtKB:Q9UHG0, HGNC:18141, modeled by CDD:cd17149 and CDD:cd17152),
    and lacks a grounded evidence block.
  target_ids:
  - CDD:cd17153
  field_paths:
  - data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml#/definition
  evidence_ids:
  - ev-cd17153
  - ev-cd17150-sibling
  - ev-cd17154
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1210
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd17153 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1210): distinguished DCDC2B (UniProtKB:A2VCK2)
    from its paralog DCDC2 (UniProtKB:Q9UHG0) in the domain description and human
    reading-disability/ADHD genetics summary matching N-terminal repeat 1 sibling
    CDD:cd17150 and paralog repeat 2 sibling CDD:cd17154, added UniProtKB:A2VCK2 evidence,
    advanced mapping_status from SEEDED to PROPOSED, and recorded curation_history
    action source_erratum_cd17153.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F20
- finding_id: F21
  issue_key: cdd-cd15884-snap23c-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd15884 (SNARE_SNAP23C) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines
  description: CDD:cd15884 (label=SNARE_SNAP23C, parent_traits=[CDD:cl22856]) models
    the C-terminal Qc SNARE motif of SNAP23 (unpromoted seed examples Mus musculus
    UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), but its upstream CDD definition
    states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one
    belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate
    the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family
    Qb/Qc t-SNAREs lack a transmembrane domain and SNAP23 attaches to membranes via
    palmitoylated cysteine residues in the inter-motif linker between its N-terminal
    Qb (CDD:cd15895) and C-terminal Qc (CDD:cd15884) SNARE motifs (PMID:9159129, PMID:9759094).
  target_ids:
  - CDD:cd15884
  field_paths:
  - data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml#/definition
  evidence_ids:
  - ev-cd15884
  - ev-cd15885
  - ev-cd15894-sibling
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1210
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd15884 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1210): replaced the false transmembrane-domain
    claim with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain
    and that SNAP23 is anchored to target membranes via palmitoylated cysteine residues
    in the linker between its two SNARE motifs, added PMID:9159129 evidence, advanced
    mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd15884.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F21
- finding_id: F22
  issue_key: cdd-cd15895-snap23n-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd15895 (SNARE_SNAP23N) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines
  description: CDD:cd15895 (label=SNARE_SNAP23N, parent_traits=[CDD:cl22856]) models
    the N-terminal Qb SNARE motif of SNAP23 (unpromoted seed examples Mus musculus
    UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), but its upstream CDD definition
    states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one
    belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate
    the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family
    Qb/Qc t-SNAREs lack a transmembrane domain and SNAP23 attaches to membranes via
    palmitoylated cysteine residues in the inter-motif linker between its N-terminal
    Qb (CDD:cd15895) and C-terminal Qc (CDD:cd15884) SNARE motifs (PMID:9159129, PMID:9759094).
  target_ids:
  - CDD:cd15895
  field_paths:
  - data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml#/definition
  evidence_ids:
  - ev-cd15895
  - ev-cd15885
  - ev-cd15894-sibling
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1210
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd15895 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1210): replaced the false transmembrane-domain
    claim with the accurate statement that Qb/Qc SNAREs lack a transmembrane domain
    and that SNAP23 is anchored to target membranes via palmitoylated cysteine residues
    in the linker between its two SNARE motifs, added PMID:9159129 evidence, advanced
    mapping_status from SEEDED to PROPOSED, and recorded curation_history action source_erratum_cd15895.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F22
- finding_id: F23
  issue_key: cdd-cd18599-mrp5-8-9-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd18599 (ABC_6TM_MRP5_8_9_D2) misassigns MRP7 to ABCC7 (CFTR) instead
    of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9
    members
  description: CDD:cd18599 (label=ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913])
    models C-terminal TMD2 of MRPs 5, 8, and 9 (unpromoted seed examples Homo sapiens
    ABCC5 UniProtKB:O15440, Mus musculus ABCC5 UniProtKB:Q9R1X5, Homo sapiens ABCC11
    UniProtKB:Q96J66, Caenorhabditis elegans mrp-5 UniProtKB:G5EE72, Homo sapiens
    ABCC12 UniProtKB:Q96J65, and Mus musculus ABCC12 UniProtKB:Q80WJ6), but carries
    the corrupted upstream CDD ABCC template text stating 'On the other hand, MRP1,
    2, 3, 6 and 7 (ABCC1, 2, 3, 6 and 7, respectively) have an additional N-terminal
    five transmembrane segments in a single domain (TMD0) connected to the core (TMD-NBD)
    by a cytoplasmic linker (L0)' and claiming 'The MRP subfamily (ABCC subfamily)
    is composed of 13 members, of which MRP1 to MRP9 are the major transporters that
    cause multidrug resistance in tumor cells by pumping anticancer drugs out of the
    cell.' In HGNC/UniProt nomenclature, ABCC7 is CFTR (an epithelial chloride channel
    lacking TMD0), whereas MRP7 is ABCC10 (UniProtKB:Q5T3U5), MRP8 is ABCC11, and
    MRP9 is ABCC12 (a paralog whose physiological substrates and transport activity
    remain less characterized, PMID:16984901).
  target_ids:
  - CDD:cd18599
  field_paths:
  - data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml#/definition
  evidence_ids:
  - ev-cd18599
  - ev-cd18592-sibling
  - ev-cd18593
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1210
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd18599 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1210): corrected the false mapping of MRP7 to ABCC7
    (MRP7 is ABCC10; ABCC7 is CFTR) and qualified the overgeneralized tumor multidrug-resistance
    efflux claim across MRP1-MRP9 matching N-terminal TMD1 sibling CDD:cd18592, added
    PMID:16984901 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded
    curation_history action source_erratum_cd18599.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F23
- finding_id: F24
  issue_key: cdd-cd18601-mrp4-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: CDD:cd18601 (ABC_6TM_MRP4_D2_like) misassigns MRP7 to ABCC7 (CFTR) instead
    of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9
    members
  description: CDD:cd18601 (label=ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913])
    models C-terminal TMD2 of MRP4/ABCC4 (unpromoted seed examples Homo sapiens UniProtKB:O15439
    and Mus musculus UniProtKB:E9Q236), but carries the identical corrupted upstream
    CDD ABCC template text stating 'On the other hand, MRP1, 2, 3, 6 and 7 (ABCC1,
    2, 3, 6 and 7, respectively) have an additional N-terminal five transmembrane
    segments in a single domain (TMD0) connected to the core (TMD-NBD) by a cytoplasmic
    linker (L0)' and claiming 'The MRP subfamily (ABCC subfamily) is composed of 13
    members, of which MRP1 to MRP9 are the major transporters that cause multidrug
    resistance in tumor cells by pumping anticancer drugs out of the cell.' In HGNC/UniProt
    nomenclature, ABCC7 is CFTR (an epithelial chloride channel lacking TMD0), whereas
    MRP7 is ABCC10 (UniProtKB:Q5T3U5), MRP8 is ABCC11, and MRP9 is ABCC12 (PMID:16984901).
  target_ids:
  - CDD:cd18601
  field_paths:
  - data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml#/definition
  evidence_ids:
  - ev-cd18601
  - ev-cd18593
  - ev-cd18592-sibling
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage4-evidence
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1210
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
  disposition_reason: 'Repaired CDD:cd18601 in place via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py (#1210): corrected the false mapping of MRP7 to ABCC7
    (MRP7 is ABCC10; ABCC7 is CFTR) and qualified the overgeneralized tumor multidrug-resistance
    efflux claim across MRP1-MRP9 matching N-terminal TMD1 sibling CDD:cd18593, added
    PMID:16984901 evidence, advanced mapping_status from SEEDED to PROPOSED, and recorded
    curation_history action source_erratum_cd18601.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F24
actions: []
limitations:
- This post-remediation review covers the frozen 14-record Cycle 3 Stage 4/5 CDD SEQ_DOMAIN
  cohort (8 resolved Cycle 1/2 carry-forwards and 6 newly remediated tandem-repeat/subfamily
  siblings).
- 'All 14 cohort findings (F1-F2 under #1172, F13-F18 under #1188, and F19-F24 under
  #1210) are resolved on disk; broader NCBI CDD corpus screening across other CDD
  families remains tracked under umbrella issue #605.'
related_reviews:
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
  relationship: Predecessor Cycle 3 Stage 4 cohort review of the 14-record CDD inventory
    (opening F19-F24 and verifying F1, F2, and F13-F18).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261030T092000Z-cdd-cd17152-record-review
  relationship: Companion Cycle 3 Stage 4 single-record deep review of CDD:cd17152
    (finding F19).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
  relationship: Cycle 2 Stage 5 post-remediation cohort review resolving F13-F18 and
    verifying F1-F2.
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review
  relationship: Cycle 2 Stage 4 cohort review of the 8-record CDD sibling inventory
    (findings F13-F18).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261022T052300Z-cdd-stage3-domain-cohort-review
  relationship: Cycle 1 Stage 4 cohort review of the 12-record CDD inventory (findings
    F1-F12).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261022T081000Z-cdd-stage5-remediation-review
  relationship: Cycle 1 Stage 5 post-remediation review resolving F3-F12 and deferring
    F1-F2.
links:
- https://github.com/CultureBotAI/proteintraitsmech/issues/1210
- https://github.com/CultureBotAI/proteintraitsmech/issues/1188
- https://github.com/CultureBotAI/proteintraitsmech/issues/1172
- https://github.com/CultureBotAI/proteintraitsmech/issues/605
```
