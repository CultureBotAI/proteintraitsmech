# Cohort scientific review of 12 Cycle 4 Stage 4 CDD sequence-domain records (6 resolved Cycle 3 G4 records and 6 parent/paralog sibling records)

- Review: 20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-31T04:29:00Z
- Finished UTC: 2026-10-31T04:39:00Z
- Reviewer: Antigravity (independent)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Full cohort review of all 12 eligible CDD sequence-domain records in the frozen Cycle 4 Stage 4 inventory (6 resolved Cycle 3 Stage 5 G4 records: CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, and CDD:cd18601, plus 6 unpromoted subfamily-parent and paralog-sibling CDD records in the DCX_DCDC2_like and SNARE_SNAP25/SNAP23/SNAP29 clades: CDD:cd17071, CDD:cd16113, CDD:cd15855, CDD:cd15889, CDD:cd15856, and CDD:cd15887). All 12 records pass strict LinkML schema validation, UniProt grounding replay, causal-graph audit, writer audit, and curation-history validation, and each represents a genuine, non-redundant conserved sequence domain class (SEQ_DOMAIN on SEQUENCE) that should be retained as a distinct record. Cycle 3 G4 findings F19-F24 remain verified resolved on disk at 5869b9c877b532972a405523c7c6e21945c177e4. Six new open findings (F25-F30: 4 major, 2 minor) across the 6 newly audited parent/paralog sibling CDD records share a single root cause in upstream NCBI CDD template descriptions and are preserved open for Cycle 4 Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.

## Scope And Provenance

Frozen 12-record Cycle 4 Stage 4 CDD SEQ_DOMAIN inventory comprising the 6 resolved Cycle 3 Stage 5 G4 records (CDD:cd17152, CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, CDD:cd18601) and 6 unpromoted parent/paralog sibling records in the DCX_DCDC2_like and SNARE_SNAP25/SNAP23/SNAP29 clades (CDD:cd17071, CDD:cd16113, CDD:cd15855, CDD:cd15889, CDD:cd15856, CDD:cd15887).

Selection: Every CDD record remediated in Cycle 3 Stage 5 (F19-F24) plus every remaining subfamily-parent or paralog-sibling CDD record in the DCX_DCDC2_like (cd17071, cd16113) and Qb/Qc SNARE_SNAP25/SNAP23/SNAP29 (cd15855, cd15889, cd15856, cd15887) clades that retained upstream CDD template prose defects after Cycle 1-3 remediation.
Coverage: full; 12 reviewed / 12 in the declared population.
Source: git_commit at Git base 5869b9c877b532972a405523c7c6e21945c177e4.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| CDD:cd15855 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml | generated | SNARE_SNAP25C_23C |
| CDD:cd15856 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml | generated | SNARE_SNAP29C |
| CDD:cd15884 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml | generated | SNARE_SNAP23C |
| CDD:cd15887 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml | generated | SNARE_SNAP29N |
| CDD:cd15889 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml | generated | SNARE_SNAP25N_23N |
| CDD:cd15895 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml | generated | SNARE_SNAP23N |
| CDD:cd16113 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml | generated | DCX2_DCDC2_like |
| CDD:cd17071 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml | generated | DCX1_DCDC2_like |
| CDD:cd17152 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml | generated | DCX2_DCDC2 |
| CDD:cd17153 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml | generated | DCX2_DCDC2B |
| CDD:cd18599 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml | generated | ABC_6TM_MRP5_8_9_D2 |
| CDD:cd18601 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml | generated | ABC_6TM_MRP4_D2_like |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Strict LinkML and OAK ontology-binding validation | passed | True | CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895, CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601 | All 12 target records pass closed LinkML schema validation and OAK term-label bindings with 0 errors. |
| Release-pinned UniProt grounding and binding replay | passed | True | CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895, CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601 | 12 files scanned; 23,062 corpus qualified_record_bindings verify across 13,532 registry proteins with 0 semantic findings. |
| Causal-graph structural and semantic audit | passed | False | CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895, CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601 | 0 records with causal_graphs, 0 errors, 0 warnings across the 12-record cohort. |
| Registered write-route audit | passed | True | CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895, CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601 | 620 scripts examined (51 seeders, 9 registered editors, 2 transactional promoters, 52 declared bypasses), OK with 0 unguarded writer findings. |
| Append-only curation history schema validation | passed | False | CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895, CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601 | All 21 append-only history YAML files validate cleanly against HistoryRecord. |

## Scientific And Domain Assessments

### Cohort lumping/splitting and tandem-repeat / subfamily-parent / paralog-subfamily boundaries

scope: supported. Targets: CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895, CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601.

All 12 target records represent genuine, non-redundant NCBI CDD conserved sequence-domain models (SEQ_DOMAIN on SEQUENCE) distinguished by tandem repeat position (DCX1 vs DCX2; N-terminal Qb vs C-terminal Qc SNARE helix; TMD1 vs TMD2 6TM bundle) and hierarchy/paralog level (DCX1/2_DCDC2_like parent profiles vs DCDC2/DCDC2B/DCDC2C child profiles; combined SNAP25/SNAP23 vs specific SNAP25, SNAP23, and SNAP29 profiles; MRP4 vs MRP5/8/9). None should be merged or deprecated.

### Verification of resolved Cycle 3 Stage 5 G4 findings F19-F24 on disk

consistency: supported. Targets: CDD:cd15884, CDD:cd15895, CDD:cd17152, CDD:cd17153, CDD:cd18599, CDD:cd18601.

All 6 records remediated in Cycle 3 Stage 5 (#1210, PR #1211) remain verified resolved on disk at 5869b9c877b532972a405523c7c6e21945c177e4 with corrected definitions, literature evidence blocks, and curation_history entries.

### Upstream NCBI CDD template defects in 6 newly audited parent/paralog sibling domain records

consistency: concern. Targets: CDD:cd15855, CDD:cd15856, CDD:cd15887, CDD:cd15889, CDD:cd16113, CDD:cd17071.

Six parent/paralog sibling CDD records (CDD:cd17071, CDD:cd16113, CDD:cd15855, CDD:cd15889, CDD:cd15856, CDD:cd15887) propagate the same upstream NCBI CDD template descriptions whose defects were repaired on their child/sibling profiles in Cycles 1-3, yielding 6 new open findings (F25-F30: 4 major, 2 minor) preserved for Cycle 4 Stage 5 grouped remediation.

## Findings

### F19: CDD:cd17152 (DCX2_DCDC2) interpolates an off-target ubiquitin protein-modifier definition sentence into a microtubule-binding DCX repeat profile

minor / resolved / confirmed; issue key: cdd-cd17152-dcdc2-rpt2-ubiquitin-modifier-digression.

CDD:cd17152 (label=DCX2_DCDC2, parent_traits=[CDD:cl28922]) models the C-terminal second doublecortin-like domain (DCX2) of DCDC2 (unpromoted seed examples Homo sapiens UniProtKB:Q9UHG0 and Mus musculus UniProtKB:Q5DU00), a microtubule-associated protein with tandem ubiquitin-like beta-grasp DCX repeats associated with human reading disability/dyslexia (PMID:16278295). Its upstream CDD definition interpolated the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.' and lacked a PMID:16278295 evidence block.

Disposition: Repaired CDD:cd17152 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210, PR #1211): replaced the off-target ubiquitin protein-modifier sentence with the tandem DCX ubiquitin-like beta-grasp repeat description, added PMID:16278295 evidence, and recorded curation_history action source_erratum_cd17152.

### F20: CDD:cd17153 (DCX2_DCDC2B) switches mid-definition from DCDC2B to paralog DCDC2 reading-disability and ADHD genetics

major / resolved / confirmed; issue key: cdd-cd17153-dcdc2b-rpt2-dcdc2-paralog-disease-switch.

CDD:cd17153 (label=DCX2_DCDC2B, parent_traits=[CDD:cl28922]) models the C-terminal second doublecortin-like domain (DCX2) of DCDC2B (Homo sapiens UniProtKB:A2VCK2, HGNC:33489, carried on N-terminal repeat 1 sibling CDD:cd17150), but sentence 2 switched without qualification to paralog DCDC2 reading-disability/ADHD/dyslexia genetics and lacked a grounded evidence block.

Disposition: Repaired CDD:cd17153 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210, PR #1211): distinguished DCDC2B from paralog DCDC2 in sentence 2 and qualified the dyslexia/ADHD human genetic association as applying to paralogous DCDC2, added UniProtKB:A2VCK2 evidence, and recorded curation_history action source_erratum_cd17153.

### F21: CDD:cd15884 (SNARE_SNAP23C) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines

major / resolved / confirmed; issue key: cdd-cd15884-snap23c-transmembrane-domain-overclaim.

CDD:cd15884 (label=SNARE_SNAP23C, parent_traits=[CDD:cl22856]) models the C-terminal Qc SNARE motif of SNAP23 (unpromoted seed examples Mus musculus UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), and its upstream CDD definition falsely stated that Qb/Qc SNAREs contain a transmembrane domain whereas SNAP23 lacks a transmembrane domain and attaches to membranes via palmitoylated cysteines in its inter-motif linker (PMID:9159129, PMID:9759094).

Disposition: Repaired CDD:cd15884 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210, PR #1211): replaced the false transmembrane-domain claim with palmitoylated inter-motif linker membrane anchoring, added PMID:9159129 evidence, and recorded curation_history action source_erratum_cd15884.

### F22: CDD:cd15895 (SNARE_SNAP23N) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines

major / resolved / confirmed; issue key: cdd-cd15895-snap23n-transmembrane-domain-overclaim.

CDD:cd15895 (label=SNARE_SNAP23N, parent_traits=[CDD:cl22856]) models the N-terminal Qb SNARE motif of SNAP23 (unpromoted seed examples Mus musculus UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), and its upstream CDD definition falsely stated that Qb/Qc SNAREs contain a transmembrane domain whereas SNAP23 lacks a transmembrane domain and attaches to membranes via palmitoylated cysteines in its inter-motif linker (PMID:9159129, PMID:9759094).

Disposition: Repaired CDD:cd15895 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210, PR #1211): replaced the false transmembrane-domain claim with palmitoylated inter-motif linker membrane anchoring, added PMID:9159129 evidence, and recorded curation_history action source_erratum_cd15895.

### F23: CDD:cd18599 (ABC_6TM_MRP5_8_9_D2) misassigns MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9 members

major / resolved / confirmed; issue key: cdd-cd18599-mrp5-8-9-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim.

CDD:cd18599 (label=ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913]) models C-terminal TMD2 of MRPs 5, 8, and 9, and carried the corrupted upstream CDD ABCC template text misassigning MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaiming tumor multidrug-resistance efflux across all MRP1-MRP9 members (PMID:16984901).

Disposition: Repaired CDD:cd18599 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210, PR #1211): corrected MRP7=ABCC10 / CFTR=ABCC7 nomenclature, qualified the MRP1-MRP9 efflux claim, added PMID:16984901 evidence, and recorded curation_history action source_erratum_cd18599.

### F24: CDD:cd18601 (ABC_6TM_MRP4_D2_like) misassigns MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaims anticancer multidrug-resistance efflux across all MRP1-MRP9 members

major / resolved / confirmed; issue key: cdd-cd18601-mrp4-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim.

CDD:cd18601 (label=ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913]) models C-terminal TMD2 of MRP4/ABCC4, and carried the identical corrupted upstream CDD ABCC template text misassigning MRP7 to ABCC7 (CFTR) instead of ABCC10 and overclaiming tumor multidrug-resistance efflux across all MRP1-MRP9 members (PMID:16984901).

Disposition: Repaired CDD:cd18601 in place via scripts/cdd_errata.py and scripts/repair_cdd_errata.py (#1210, PR #1211): corrected MRP7=ABCC10 / CFTR=ABCC7 nomenclature, qualified the MRP1-MRP9 efflux claim, added PMID:16984901 evidence, and recorded curation_history action source_erratum_cd18601.

### F25: CDD:cd17071 (DCX1_DCDC2_like) starts its definition with typo 'Dublecortin-like' and interpolates an off-target ubiquitin protein-modifier sentence into a microtubule-binding DCX repeat profile

minor / open / confirmed; issue key: cdd-cd17071-dcx1-dcdc2-like-typo-and-ubiquitin-modifier-digression.

CDD:cd17071 (label=DCX1_DCDC2_like, parent_traits=[CDD:cl28922], 0 canonical_examples) models the N-terminal first doublecortin-like domain subfamily of DCDC2 and similar proteins (grouping child profiles CDD:cd17149 on DCDC2, CDD:cd17150 on DCDC2B, and CDD:cd17151 on DCDC2C), microtubule-associated proteins with tandem ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated with reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition starts with the typographical error 'Dublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2) and similar proteins.', interpolates the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.' even though DCX domains only adopt a ubiquitin-like beta-grasp fold and do not function as ubiquitin protein modifiers, and lacks an evidence block citing PMID:16278295.

### F26: CDD:cd16113 (DCX2_DCDC2_like) interpolates an off-target ubiquitin protein-modifier definition sentence into a microtubule-binding DCX repeat profile

minor / open / confirmed; issue key: cdd-cd16113-dcx2-dcdc2-like-ubiquitin-modifier-digression.

CDD:cd16113 (label=DCX2_DCDC2_like, parent_traits=[CDD:cl28922], 0 canonical_examples) models the C-terminal second doublecortin-like domain subfamily of DCDC2 and similar proteins (grouping child profiles CDD:cd17152 on DCDC2, CDD:cd17153 on DCDC2B, and CDD:cd17154 on DCDC2C), microtubule-associated proteins with tandem ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated with reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition interpolates the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes including transcriptional regulation, cell cycle control, and DNA repair.' even though DCX domains only adopt a ubiquitin-like beta-grasp fold and do not function as ubiquitin protein modifiers, and lacks an evidence block citing PMID:16278295.

### F27: CDD:cd15855 (SNARE_SNAP25C_23C) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 and SNAP23 are membrane-anchored via palmitoylated cysteines

major / open / confirmed; issue key: cdd-cd15855-snap25c-23c-transmembrane-domain-overclaim.

CDD:cd15855 (label=SNARE_SNAP25C_23C, parent_traits=[CDD:cl22856], 0 canonical_examples) models the combined C-terminal Qc SNARE motif subfamily of SNAP25 and SNAP23 (grouping child profiles CDD:cd15885 and CDD:cd15884), but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family Qb/Qc t-SNAREs lack a transmembrane domain and attach to membranes via palmitoylated cysteine residues in the central linker between their N-terminal Qb and C-terminal Qc SNARE motifs (PMID:9759094, PMID:9159129).

### F28: CDD:cd15889 (SNARE_SNAP25N_23N) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 and SNAP23 are membrane-anchored via palmitoylated cysteines

major / open / confirmed; issue key: cdd-cd15889-snap25n-23n-transmembrane-domain-overclaim.

CDD:cd15889 (label=SNARE_SNAP25N_23N, parent_traits=[CDD:cl22856], unpromoted seed example Drosophila melanogaster Snap25 UniProtKB:P36975) models the combined N-terminal Qb SNARE motif subfamily of SNAP25 and SNAP23 (grouping child profiles CDD:cd15894 and CDD:cd15895), but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family Qb/Qc t-SNAREs lack a transmembrane domain and attach to membranes via palmitoylated cysteine residues in the central linker between their N-terminal Qb and C-terminal Qc SNARE motifs (PMID:9759094, PMID:9159129).

### F29: CDD:cd15856 (SNARE_SNAP29C) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane anchors

major / open / confirmed; issue key: cdd-cd15856-snap29c-transmembrane-domain-overclaim.

CDD:cd15856 (label=SNARE_SNAP29C, parent_traits=[CDD:cl22856], unpromoted seed examples Homo sapiens SNAP29 UniProtKB:O95721, Mus musculus Snap29 UniProtKB:Q9ERB0, and Allochromatium vinosum UniProtKB:P83351) models the C-terminal Qc SNARE motif of SNAP29, but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' Qb/Qc SNAREs lack a transmembrane domain, and SNAP29 specifically lacks both a transmembrane domain and the palmitoylated cysteine cluster of SNAP25/SNAP23, associating with membranes via protein-protein interactions with syntaxins and Rab GTPases (PMID:9736707, PMID:9759094).

### F30: CDD:cd15887 (SNARE_SNAP29N) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane anchors

major / open / confirmed; issue key: cdd-cd15887-snap29n-transmembrane-domain-overclaim.

CDD:cd15887 (label=SNARE_SNAP29N, parent_traits=[CDD:cl22856], unpromoted seed examples Homo sapiens SNAP29 UniProtKB:O95721, Mus musculus Snap29 UniProtKB:Q9ERB0, and Allochromatium vinosum UniProtKB:P83351) models the N-terminal Qb SNARE motif of SNAP29, and propagates the identical false upstream CDD template claim 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' Qb/Qc SNAREs lack a transmembrane domain, and SNAP29 lacks both a transmembrane domain and palmitoylated membrane-anchoring cysteines (PMID:9736707, PMID:9759094).

## Recommended Actions And Acceptance Checks

### extend-cdd-errata-and-repair-cycle4-sibling-records

Add accession-keyed errata entries for CDD:cd17071 (F25), CDD:cd16113 (F26), CDD:cd15855 (F27), CDD:cd15889 (F28), CDD:cd15856 (F29), and CDD:cd15887 (F30) to scripts/cdd_errata.py and apply them in place via scripts/repair_cdd_errata.py with literature-backed evidence and curation_history entries.

- All 6 parent/paralog sibling CDD records (cd17071, cd16113, cd15855, cd15889, cd15856, cd15887) carry accurate, paralog- and repeat-specific definitions and grounded literature citations.
- scripts/seed_cdd.py and scripts/repair_cdd_errata.py replay all 30 CDD errata entries deterministically and idempotently.
- scripts/validate_strict.py, scripts/validate_uniprot_grounding.py, and scripts/audit_writers.py pass with 0 errors.

## Category Boundaries

- retain: CDD:cd16113, CDD:cd17071, CDD:cd17152, CDD:cd17153. Retain subfamily parent profiles CDD:cd17071 (DCX1_DCDC2_like, N-terminal repeat 1) and CDD:cd16113 (DCX2_DCDC2_like, C-terminal repeat 2) alongside paralog-specific repeat-2 child profiles CDD:cd17152 (DCX2_DCDC2) and CDD:cd17153 (DCX2_DCDC2B) under parent_traits [CDD:cl28922] because they model non-overlapping N-terminal vs C-terminal tandem DCX repeats and distinct CDD subfamily hierarchy levels.
- retain: CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15887, CDD:cd15889, CDD:cd15895. Retain combined SNAP25/SNAP23 N-terminal Qb (CDD:cd15889) and C-terminal Qc (CDD:cd15855) profiles, paralog-specific SNAP23 N-terminal Qb (CDD:cd15895) and C-terminal Qc (CDD:cd15884) profiles, and paralog-specific SNAP29 N-terminal Qb (CDD:cd15887) and C-terminal Qc (CDD:cd15856) profiles under parent_traits [CDD:cl22856] because they distinguish non-overlapping N-terminal Qb vs C-terminal Qc SNARE helices and distinct CDD subfamily/paralog scopes.
- retain: CDD:cd18599, CDD:cd18601. Retain C-terminal six-helix transmembrane bundle (TMD2) profiles CDD:cd18599 (ABC_6TM_MRP5_8_9_D2, MRPs 5/8/9, ABCC5/ABCC11/ABCC12) and CDD:cd18601 (ABC_6TM_MRP4_D2_like, MRP4/ABCC4) under parent_traits [CDD:cl38913] as distinct ABCC subfamily TMD2 profiles non-overlapping with their N-terminal TMD1 counterparts (CDD:cd18592 and CDD:cd18593).

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| ev-cd17152 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml; identifier, label, definition, evidence (PMID:16278295), mapping_status, curation_history (source_erratum_cd17152) | supports | CDD:cd17152 (label DCX2_DCDC2, parent_traits=[CDD:cl28922], PROPOSED) remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair. |
| ev-cd17153 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml; identifier, label, definition, evidence (UniProtKB:A2VCK2), mapping_status, curation_history (source_erratum_cd17153) | supports | CDD:cd17153 (label DCX2_DCDC2B, parent_traits=[CDD:cl28922], PROPOSED) remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair. |
| ev-cd15884 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml; identifier, label, definition, evidence (PMID:9159129), mapping_status, curation_history (source_erratum_cd15884) | supports | CDD:cd15884 (label SNARE_SNAP23C, parent_traits=[CDD:cl22856], PROPOSED) remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair. |
| ev-cd15895 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml; identifier, label, definition, evidence (PMID:9159129), mapping_status, curation_history (source_erratum_cd15895) | supports | CDD:cd15895 (label SNARE_SNAP23N, parent_traits=[CDD:cl22856], PROPOSED) remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair. |
| ev-cd18599 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml; identifier, label, definition, evidence (PMID:16984901), mapping_status, curation_history (source_erratum_cd18599) | supports | CDD:cd18599 (label ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913], PROPOSED) remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair. |
| ev-cd18601 | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml; identifier, label, definition, evidence (PMID:16984901), mapping_status, curation_history (source_erratum_cd18601) | supports | CDD:cd18601 (label ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913], PROPOSED) remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair. |
| ev-cd17071 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml; identifier, label, definition, parent_traits | partial | CDD:cd17071 (label DCX1_DCDC2_like, parent_traits=[CDD:cl28922], SEEDED, 0 canonical_examples) models the N-terminal first DCX repeat subfamily profile of DCDC2 and similar proteins (grouping child profiles cd17149, cd17150, cd17151), but starts its definition with the typo 'Dublecortin-like domain 1...', interpolates an off-target sentence defining the ubiquitin protein modifier, and lacks a PMID:16278295 evidence block (finding F25). |
| ev-cd16113 | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml; identifier, label, definition, parent_traits | partial | CDD:cd16113 (label DCX2_DCDC2_like, parent_traits=[CDD:cl28922], SEEDED, 0 canonical_examples) models the C-terminal second DCX repeat subfamily profile of DCDC2 and similar proteins (grouping child profiles cd17152, cd17153, cd17154), but interpolates an off-target sentence defining the ubiquitin protein modifier and lacks a PMID:16278295 evidence block (finding F26). |
| ev-cd15855 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml; identifier, label, definition, parent_traits | partial | CDD:cd15855 (label SNARE_SNAP25C_23C, parent_traits=[CDD:cl22856], SEEDED, 0 canonical_examples) models the combined C-terminal Qc SNARE motif subfamily of SNAP25 and SNAP23 (grouping child profiles cd15885 and cd15884), but falsely states that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 and SNAP23 lack a transmembrane domain and are anchored to membranes via palmitoylated cysteines in their central inter-motif linker (PMID:9759094, PMID:9159129; finding F27). |
| ev-cd15889 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml; identifier, label, definition, parent_traits, canonical_examples | partial | CDD:cd15889 (label SNARE_SNAP25N_23N, parent_traits=[CDD:cl22856], SEEDED, unpromoted seed example Drosophila melanogaster Snap25 UniProtKB:P36975) models the combined N-terminal Qb SNARE motif subfamily of SNAP25 and SNAP23 (grouping child profiles cd15894 and cd15895) and propagates the identical false claim that Qb/Qc SNAREs contain a transmembrane domain (PMID:9759094, PMID:9159129; finding F28). |
| ev-cd15856 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml; identifier, label, definition, parent_traits, canonical_examples | partial | CDD:cd15856 (label SNARE_SNAP29C, parent_traits=[CDD:cl22856], SEEDED, unpromoted seed examples Homo sapiens SNAP29 O95721, Mus musculus Snap29 Q9ERB0, and Allochromatium vinosum P83351) models the C-terminal Qc SNARE motif of SNAP29, but falsely states that Qb/Qc SNAREs have a transmembrane domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane-anchoring cysteines and associates with membranes via protein-protein interactions with syntaxins and Rab GTPases (PMID:9736707, PMID:9759094; finding F29). |
| ev-cd15887 | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml; identifier, label, definition, parent_traits, canonical_examples | partial | CDD:cd15887 (label SNARE_SNAP29N, parent_traits=[CDD:cl22856], SEEDED, unpromoted seed examples Homo sapiens SNAP29 O95721, Mus musculus Snap29 Q9ERB0, and Allochromatium vinosum P83351) models the N-terminal Qb SNARE motif of SNAP29 and propagates the identical false claim that Qb/Qc SNAREs contain a transmembrane domain (PMID:9736707, PMID:9759094; finding F30). |
| ev-dcx-child-siblings | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml; CDD:cd17149 (DCX1_DCDC2), CDD:cd17150 (DCX1_DCDC2B), CDD:cd17151 (DCX1_DCDC2C), and CDD:cd17154 (DCX2_DCDC2C) | supports | Paralog-specific child repeat-1 profiles CDD:cd17149, CDD:cd17150, and CDD:cd17151 and repeat-2 profile CDD:cd17154 repaired in Cycles 1-2 (#1171, #1188), establishing the tandem DCX ubiquitin-like beta-grasp repeat wording and PMID:16278295 citation needed on subfamily parent profiles CDD:cd17071 (F25) and CDD:cd16113 (F26). |
| ev-snap25-siblings | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml; CDD:cd15885 (SNARE_SNAP25C) and CDD:cd15894 (SNARE_SNAP25N) | supports | Remediated SNAP25 child profiles CDD:cd15885 (#1188) and CDD:cd15894 (#1171) establishing the palmitoylated inter-motif linker membrane-anchoring wording for Qb/Qc SNAREs (PMID:9759094). |
| ev-mrp-tmd1-siblings | data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml; CDD:cd18592 (ABC_6TM_MRP5_8_9_D1) and CDD:cd18593 (ABC_6TM_MRP4_D1_like) | supports | Remediated N-terminal TMD1 siblings CDD:cd18592 (#1171) and CDD:cd18593 (#1188) supporting verified resolved findings F23 (CDD:cd18599) and F24 (CDD:cd18601). |
| ev-cycle3-stage4-cohort | reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml; findings F19-F24 | supports | Cycle 3 Stage 4 cohort review of the 14-record CDD sibling inventory (findings F19-F24). |
| ev-cycle3-stage5-cohort | reviews/structured/20261030T115500Z-cdd-cycle3-stage5-remediation-review/review.yaml; findings F19-F24 resolved | supports | Cycle 3 Stage 5 post-remediation cohort review resolving F19-F24 (#1210, PR #1211). |
| ev-cycle3-stage5-evidence | reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-05/revision-0001/evidence.yaml; findings F19-F24 (resolved) and carry_forward_ids [] | supports | Cycle 3 Stage 5 workflow evidence manifest recording resolution of F19-F24. |
| ev-cdd-errata-infrastructure | scripts/cdd_errata.py; CDD_ERRATA table (24 entries) and scripts/repair_cdd_errata.py | supports | scripts/cdd_errata.py (24 entries) and scripts/repair_cdd_errata.py provide the registered writer route for both the 6 verified resolved Cycle 3 G4 records and the 6 new open findings F25-F30. |

## Limits And Additional Notes

- This cohort review covers the frozen 12-record Cycle 4 Stage 4 CDD SEQ_DOMAIN inventory (6 resolved Cycle 3 G4 records and 6 newly audited parent/paralog sibling records).
- No scientific trait records under data/traits/ were edited during Stage 4; findings F25-F30 remain open for Stage 5 grouped remediation.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review
kind: category
repository: CultureBotAI/proteintraitsmech
title: Cohort scientific review of 12 Cycle 4 Stage 4 CDD sequence-domain records
  (6 resolved Cycle 3 G4 records and 6 parent/paralog sibling records)
started_at: '2026-10-31T04:29:00Z'
finished_at: '2026-10-31T04:39:00Z'
reviewer:
  identity: Antigravity
  kind: agent
  model: Claude Opus 4.6
  independence: independent
  independence_basis: Cycle 4 Stage 4 cohort scientific review of the frozen 12-record
    CDD SEQ_DOMAIN inventory and 8 sibling CDD boundary records without modifying
    scientific records.
skill: review-yaml-category
completion: completed
verdict: needs_curation
native_verdict: COHORT_NEEDS_CURATION_6_RESOLVED_6_OPEN_FINDINGS
scientific_review: true
summary: 'Full cohort review of all 12 eligible CDD sequence-domain records in the
  frozen Cycle 4 Stage 4 inventory (6 resolved Cycle 3 Stage 5 G4 records: CDD:cd17152,
  CDD:cd17153, CDD:cd15884, CDD:cd15895, CDD:cd18599, and CDD:cd18601, plus 6 unpromoted
  subfamily-parent and paralog-sibling CDD records in the DCX_DCDC2_like and SNARE_SNAP25/SNAP23/SNAP29
  clades: CDD:cd17071, CDD:cd16113, CDD:cd15855, CDD:cd15889, CDD:cd15856, and CDD:cd15887).
  All 12 records pass strict LinkML schema validation, UniProt grounding replay, causal-graph
  audit, writer audit, and curation-history validation, and each represents a genuine,
  non-redundant conserved sequence domain class (SEQ_DOMAIN on SEQUENCE) that should
  be retained as a distinct record. Cycle 3 G4 findings F19-F24 remain verified resolved
  on disk at 5869b9c877b532972a405523c7c6e21945c177e4. Six new open findings (F25-F30:
  4 major, 2 minor) across the 6 newly audited parent/paralog sibling CDD records
  share a single root cause in upstream NCBI CDD template descriptions and are preserved
  open for Cycle 4 Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.'
source:
  git_revision: 5869b9c877b532972a405523c7c6e21945c177e4
  state: git_commit
  inputs:
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    sha256: e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510
    role: target
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
    sha256: 306f687472e4fb91d6dcad19fa7ea13f99eb85fbafb7e86440302296b710b267
    role: target
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
    sha256: 78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b
    role: context
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
    sha256: 84d8d25d5f6ce8934609c55719a0d4a09b385e2ba1cbb5134c2649573d8327c0
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
    sha256: d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    sha256: 082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    sha256: d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75
    role: target
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml
    sha256: 6ec1fd4e6c77d35fcd3c65b0387f517870965eeb622e47e122665a32b27c1f1d
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
    sha256: deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50
    role: target
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
    sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    sha256: fe5af61fd44b4a50b6c9f0ab06ddd1d717895a010f788b8096ff64d3f68e4756
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    sha256: 6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d
    role: context
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    sha256: 5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b
    role: target
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml
    sha256: a7de1d8068c056d075c9ddfc6e5f1a0cb9f9bb4102e6779f92fd06fd75acbd6e
    role: target
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml
    sha256: d11a67560ebb84bf867f67027f23109a5631b72953aa870075b96116cd599368
    role: context
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml
    sha256: edd0ed8a35d333d4f87c1ac2a4aee0d30f5af17a5a6c9a169007401798101519
    role: target
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
    sha256: fad0b6039c5386b3caf40fc650099ec7bfd126ff7854d42aeb805708a18c3f9a
    role: context
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml
    sha256: 5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb
    role: context
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    sha256: ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585
    role: target
  - path: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    sha256: d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099
    role: target
  - path: reviews/structured/20261030T092000Z-cdd-cd17152-record-review/review.yaml
    sha256: c06176c3073f1ec5d26954550500e22ecb07649a53c18e3700fd1ee352ada514
    role: context
  - path: reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml
    sha256: 2d8fe1c367294f3e5660badc28211c13c97763d788ce0eb9ca3ef1cd134587f8
    role: context
  - path: reviews/structured/20261030T115500Z-cdd-cycle3-stage5-remediation-review/review.yaml
    sha256: 3b8044daaa98388d401119aa8f726fe0aa55ccf798ba732e629822c042d2944a
    role: context
  - path: reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-04/revision-0001/evidence.yaml
    sha256: 675d9c6efc52c8ad25d7e0a13f9306fe0d92d901a3f629ec9a5328230feec9e9
    role: context
  - path: reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-05/revision-0001/evidence.yaml
    sha256: b2fff9f04946591e53a630873434c36df162f32a1e75d2eda4a425686b49e8dc
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
scope:
  description: Frozen 12-record Cycle 4 Stage 4 CDD SEQ_DOMAIN inventory comprising
    the 6 resolved Cycle 3 Stage 5 G4 records (CDD:cd17152, CDD:cd17153, CDD:cd15884,
    CDD:cd15895, CDD:cd18599, CDD:cd18601) and 6 unpromoted parent/paralog sibling
    records in the DCX_DCDC2_like and SNARE_SNAP25/SNAP23/SNAP29 clades (CDD:cd17071,
    CDD:cd16113, CDD:cd15855, CDD:cd15889, CDD:cd15856, CDD:cd15887).
  selection: Every CDD record remediated in Cycle 3 Stage 5 (F19-F24) plus every remaining
    subfamily-parent or paralog-sibling CDD record in the DCX_DCDC2_like (cd17071,
    cd16113) and Qb/Qc SNARE_SNAP25/SNAP23/SNAP29 (cd15855, cd15889, cd15856, cd15887)
    clades that retained upstream CDD template prose defects after Cycle 1-3 remediation.
  coverage: full
  population_size: 12
  reviewed_target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  exclusions:
  - target: 18 Cycle 1-2 CDD records already resolved and verified across Cycles 1-3
      (cd00104, cd00959, cd09530, cd13344, cd14999, cd15885, cd15894, cd16523, cd16652,
      cd17149, cd17150, cd17151, cd17154, cd18592, cd18593, cd20534, cd20535, cd21551)
    reason: 'Already remediated and verified in Cycles 1-3 (#1171, #1172, #1188, #1210);
      cd15885, cd15894, cd17149, cd17150, cd17151, cd17154, cd18592, and cd18593 are
      included here as boundary-contrast context inputs.'
targets:
- target_id: CDD:cd15855
  path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
  label: SNARE_SNAP25C_23C
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
    sha256: 306f687472e4fb91d6dcad19fa7ea13f99eb85fbafb7e86440302296b710b267
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd15856
  path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
  label: SNARE_SNAP29C
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
    sha256: 84d8d25d5f6ce8934609c55719a0d4a09b385e2ba1cbb5134c2649573d8327c0
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
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
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd15887
  path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml
  label: SNARE_SNAP29N
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
    sha256: edd0ed8a35d333d4f87c1ac2a4aee0d30f5af17a5a6c9a169007401798101519
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd15889
  path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml
  label: SNARE_SNAP25N_23N
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
    sha256: a7de1d8068c056d075c9ddfc6e5f1a0cb9f9bb4102e6779f92fd06fd75acbd6e
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
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
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd16113
  path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
  label: DCX2_DCDC2_like
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
    sha256: d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
- target_id: CDD:cd17071
  path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  label: DCX1_DCDC2_like
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
    sha256: deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
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
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
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
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
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
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
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
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
checks:
- check_id: schema
  name: Strict LinkML and OAK ontology-binding validation
  command: .venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml
  exit_code: 0
  status: passed
  required: true
  summary: All 12 target records pass closed LinkML schema validation and OAK term-label
    bindings with 0 errors.
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd15855
  - ev-cd15856
  - ev-cd15884
  - ev-cd15887
  - ev-cd15889
  - ev-cd15895
  - ev-cd16113
  - ev-cd17071
  - ev-cd17152
  - ev-cd17153
  - ev-cd18599
  - ev-cd18601
- check_id: semantic
  name: Release-pinned UniProt grounding and binding replay
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml
  exit_code: 0
  status: passed
  required: true
  summary: 12 files scanned; 23,062 corpus qualified_record_bindings verify across
    13,532 registry proteins with 0 semantic findings.
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd15855
  - ev-cd15856
  - ev-cd15884
  - ev-cd15887
  - ev-cd15889
  - ev-cd15895
  - ev-cd16113
  - ev-cd17071
  - ev-cd17152
  - ev-cd17153
  - ev-cd18599
  - ev-cd18601
- check_id: graphs
  name: Causal-graph structural and semantic audit
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
    data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
    data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
    data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml
  exit_code: 0
  status: passed
  required: false
  summary: 0 records with causal_graphs, 0 errors, 0 warnings across the 12-record
    cohort.
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd15855
  - ev-cd15856
  - ev-cd15884
  - ev-cd15887
  - ev-cd15889
  - ev-cd15895
  - ev-cd16113
  - ev-cd17071
  - ev-cd17152
  - ev-cd17153
  - ev-cd18599
  - ev-cd18601
- check_id: writer-audit
  name: Registered write-route audit
  command: .venv/bin/python scripts/audit_writers.py
  exit_code: 0
  status: passed
  required: true
  summary: 620 scripts examined (51 seeders, 9 registered editors, 2 transactional
    promoters, 52 declared bypasses), OK with 0 unguarded writer findings.
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
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
  summary: All 21 append-only history YAML files validate cleanly against HistoryRecord.
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cdd-errata-infrastructure
evidence:
- evidence_id: ev-cd17152
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml
  locator: identifier, label, definition, evidence (PMID:16278295), mapping_status,
    curation_history (source_erratum_cd17152)
  accessed_at: '2026-10-31T04:30:00Z'
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
  summary: CDD:cd17152 (label DCX2_DCDC2, parent_traits=[CDD:cl28922], PROPOSED) remains
    verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair.
- evidence_id: ev-cd17153
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml
  locator: identifier, label, definition, evidence (UniProtKB:A2VCK2), mapping_status,
    curation_history (source_erratum_cd17153)
  accessed_at: '2026-10-31T04:30:00Z'
  snapshot_sha256: d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75
  support: supports
  quote: Doublecortin-like domain 2 found in doublecortin domain-containing protein
    2B (DCDC2B). DCDC2B is a member of the doublecortin (DCX) family closely related
    to its paralog DCDC2, a microtubule-associated protein (MAP) with stable double
    tandem DCX repeats of a ubiquitin-like tertiary fold. Microtubules are key components
    of the cytoskeleton that are involved in cell movement, shape determination, division
    and transport. In the paralogous DCDC2 gene, human genetic variation is associated
    with reading disability (dyslexia), attention deficit hyperactivity disorder (ADHD),
    and difficulties in mathematics. DCDC2 protein interacts with many of the same
    cytoskeleton related proteins that other members of the DCX family interact with
  summary: CDD:cd17153 (label DCX2_DCDC2B, parent_traits=[CDD:cl28922], PROPOSED)
    remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair.
- evidence_id: ev-cd15884
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
  locator: identifier, label, definition, evidence (PMID:9159129), mapping_status,
    curation_history (source_erratum_cd15884)
  accessed_at: '2026-10-31T04:30:00Z'
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
  summary: CDD:cd15884 (label SNARE_SNAP23C, parent_traits=[CDD:cl22856], PROPOSED)
    remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair.
- evidence_id: ev-cd15895
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml
  locator: identifier, label, definition, evidence (PMID:9159129), mapping_status,
    curation_history (source_erratum_cd15895)
  accessed_at: '2026-10-31T04:30:00Z'
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
  summary: CDD:cd15895 (label SNARE_SNAP23N, parent_traits=[CDD:cl22856], PROPOSED)
    remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair.
- evidence_id: ev-cd18599
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml
  locator: identifier, label, definition, evidence (PMID:16984901), mapping_status,
    curation_history (source_erratum_cd18599)
  accessed_at: '2026-10-31T04:30:00Z'
  snapshot_sha256: ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585
  support: supports
  quote: Six-transmembrane helical domain 2 (TMD2) of multidrug resistance-associated
    proteins (MRPs) 5, 8, and 9. This group represents the six-transmembrane domain
    2 (TMD2) of multidrug resistance-associated proteins (MRPs) 5, 8, and 9, all of
    which belong to the subfamily C of the ATP-binding cassette (ABC) transporter
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
  summary: CDD:cd18599 (label ABC_6TM_MRP5_8_9_D2, parent_traits=[CDD:cl38913], PROPOSED)
    remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair.
- evidence_id: ev-cd18601
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml
  locator: identifier, label, definition, evidence (PMID:16984901), mapping_status,
    curation_history (source_erratum_cd18601)
  accessed_at: '2026-10-31T04:30:00Z'
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
  summary: CDD:cd18601 (label ABC_6TM_MRP4_D2_like, parent_traits=[CDD:cl38913], PROPOSED)
    remains verified resolved on disk after Cycle 3 Stage 5 (#1210) errata repair.
- evidence_id: ev-cd17071
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  locator: identifier, label, definition, parent_traits
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50
  support: partial
  quote: Dublecortin-like domain 1 found in doublecortin domain-containing protein
    2 (DCDC2) and similar proteins. DCDC2 is a member of the doublecortin (DCX) family.
    It is a microtubule-associated protein (MAP) with a stable ubiquitin-like tertiary
    fold. Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various
    cellular processes, including transcriptional regulation, cell cycle control,
    and DNA repair. Microtubules are key components of cytoskeleton that are involved
    in cell movement, shape determination, division and transport. DCDC2 genetic variation
    in humans is associated with reading disability, attention deficit hyperactivity
    disorder (ADHD), and difficulties in mathematics. A genetic variant of DCDC2 associates
    with dyslexia, a common neurobehavioral disorder of reading. DCDC2 protein interacts
    with many of the same cytoskeleton related proteins that other members of the
    DCX family interact with
  summary: CDD:cd17071 (label DCX1_DCDC2_like, parent_traits=[CDD:cl28922], SEEDED,
    0 canonical_examples) models the N-terminal first DCX repeat subfamily profile
    of DCDC2 and similar proteins (grouping child profiles cd17149, cd17150, cd17151),
    but starts its definition with the typo 'Dublecortin-like domain 1...', interpolates
    an off-target sentence defining the ubiquitin protein modifier, and lacks a PMID:16278295
    evidence block (finding F25).
- evidence_id: ev-cd16113
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
  locator: identifier, label, definition, parent_traits
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f
  support: partial
  quote: Doublecortin-like domain 2 found in doublecortin domain-containing protein
    2 (DCDC2) and similar proteins. DCDC2 is a member of the doublecortin (DCX) family.
    It is a microtubule-associated protein (MAP) with a stable ubiquitin-like tertiary
    fold. Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various
    cellular processes including transcriptional regulation, cell cycle control, and
    DNA repair. Microtubules are key components of cytoskeleton that are involved
    in cell movement, shape determination, division and transport. DCDC2 genetic variation
    in humans is associated with reading disability, attention deficit hyperactivity
    disorder (ADHD), and difficulties in mathematics. A genetic variant of DCDC2 associates
    with dyslexia, a common neurobehavioral disorder of reading. DCDC2 protein interacts
    with many of the same cytoskeleton related proteins that other members of the
    DCX family interact with
  summary: CDD:cd16113 (label DCX2_DCDC2_like, parent_traits=[CDD:cl28922], SEEDED,
    0 canonical_examples) models the C-terminal second DCX repeat subfamily profile
    of DCDC2 and similar proteins (grouping child profiles cd17152, cd17153, cd17154),
    but interpolates an off-target sentence defining the ubiquitin protein modifier
    and lacks a PMID:16278295 evidence block (finding F26).
- evidence_id: ev-cd15855
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
  locator: identifier, label, definition, parent_traits
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: 306f687472e4fb91d6dcad19fa7ea13f99eb85fbafb7e86440302296b710b267
  support: partial
  quote: C-terminal SNARE motif of SNAP25 and SNAP23. C-terminal SNARE motifs of SNAP25
    and SNAP23, members of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive
    factor attachment protein receptor) proteins. SNAP25 and SNAP23 play a role in
    transport of secretory granule from trans-Golgi network to the plasma membrane
    and in exocytosis of secretory granule. Qb/Qc SNAREs consist of 2 coiled-coil
    helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging
    to the Qc subgroup), which mediate the interactions with other SNARE proteins,
    and a transmembrane domain. In general, the SNARE complex mediates membrane fusion,
    important for trafficking of newly synthesized proteins, recycling of pre-existing
    proteins and organelle formation. SNARE proteins are classified into four groups,
    Qa-, Qb-, Qc- and R-SNAREs, depending on whether the residue in the hydrophilic
    center layer of the four-helical bundle is a glutamine (Q) or arginine (R). Qa-,
    as well as Qb- and Qc-SNAREs, are localized to target organelle membranes, while
    R-SNARE is localized to vesicle membranes. They form unique complexes consisting
    of one member of each subgroup, that mediate fusion between a specific type of
    vesicles and their target organelle. Their SNARE motifs form twisted and parallel
    heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are SNAP29,
    SNAP47 and SEC9
  summary: CDD:cd15855 (label SNARE_SNAP25C_23C, parent_traits=[CDD:cl22856], SEEDED,
    0 canonical_examples) models the combined C-terminal Qc SNARE motif subfamily
    of SNAP25 and SNAP23 (grouping child profiles cd15885 and cd15884), but falsely
    states that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 and SNAP23
    lack a transmembrane domain and are anchored to membranes via palmitoylated cysteines
    in their central inter-motif linker (PMID:9759094, PMID:9159129; finding F27).
- evidence_id: ev-cd15889
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml
  locator: identifier, label, definition, parent_traits, canonical_examples
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: a7de1d8068c056d075c9ddfc6e5f1a0cb9f9bb4102e6779f92fd06fd75acbd6e
  support: partial
  quote: N-terminal SNARE motif of SNAP25 and SNAP23. N-terminal SNARE motifs of SNAP25
    and SNAP23, members of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive
    factor attachment protein receptor) proteins. SNAP25 and SNAP23 play a role in
    transport of secretory granule from trans-Golgi network to the plasma membrane
    and in exocytosis of secretory granule. Qb/Qc SNAREs consist of 2 coiled-coil
    helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging
    to the Qc subgroup), which mediate the interactions with other SNARE proteins,
    and a transmembrane domain. In general, the SNARE complex mediates membrane fusion,
    important for trafficking of newly synthesized proteins, recycling of pre-existing
    proteins and organelle formation. SNARE proteins are classified into four groups,
    Qa-, Qb-, Qc- and R-SNAREs, depending on whether the residue in the hydrophilic
    center layer of the four-helical bundle is a glutamine (Q) or arginine (R). Qa-,
    as well as Qb- and Qc-SNAREs, are localized to target organelle membranes, while
    R-SNARE is localized to vesicle membranes. They form unique complexes consisting
    of one member of each subgroup, that mediate fusion between a specific type of
    vesicles and their target organelle. Their SNARE motifs form twisted and parallel
    heterotetrameric helix bundles. Other members of the Qb/Qc SNAREs are SNAP29,
    SNAP47 and SEC9
  summary: CDD:cd15889 (label SNARE_SNAP25N_23N, parent_traits=[CDD:cl22856], SEEDED,
    unpromoted seed example Drosophila melanogaster Snap25 UniProtKB:P36975) models
    the combined N-terminal Qb SNARE motif subfamily of SNAP25 and SNAP23 (grouping
    child profiles cd15894 and cd15895) and propagates the identical false claim that
    Qb/Qc SNAREs contain a transmembrane domain (PMID:9759094, PMID:9159129; finding
    F28).
- evidence_id: ev-cd15856
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
  locator: identifier, label, definition, parent_traits, canonical_examples
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: 84d8d25d5f6ce8934609c55719a0d4a09b385e2ba1cbb5134c2649573d8327c0
  support: partial
  quote: C-terminal SNARE motif of SNAP29. C-terminal SNARE motif of SNAP29, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. SNAP29 interacts with syntaxin-3, -4, -6, -7, -13
    and VAMP8. It is involved in multiple membrane trafficking steps, for example,
    in endocytic recycling and wrapper membrane maturation during autophagy. Qb/Qc
    SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to
    the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and a transmembrane domain. In general, the SNARE complex
    mediates membrane fusion, important for trafficking of newly synthesized proteins,
    recycling of pre-existing proteins and organelle formation. SNARE proteins are
    classified into four groups, Qa-, Qb-, Qc- and R-SNAREs, depending on whether
    the residue in the hydrophilic center layer of the four-helical bundle is a glutamine
    (Q) or arginine (R). Qa-, as well as Qb- and Qc-SNAREs, are localized to target
    organelle membranes, while R-SNARE is localized to vesicle membranes. They form
    unique complexes consisting of one member of each subgroup, that mediate fusion
    between a specific type of vesicles and their target organelle. Their SNARE motifs
    form twisted and parallel heterotetrameric helix bundles. Other members of the
    Qb/Qc SNAREs are SNAP23, SNAP25, SNAP47 and SEC9
  summary: CDD:cd15856 (label SNARE_SNAP29C, parent_traits=[CDD:cl22856], SEEDED,
    unpromoted seed examples Homo sapiens SNAP29 O95721, Mus musculus Snap29 Q9ERB0,
    and Allochromatium vinosum P83351) models the C-terminal Qc SNARE motif of SNAP29,
    but falsely states that Qb/Qc SNAREs have a transmembrane domain whereas SNAP29
    lacks both a transmembrane domain and palmitoylated membrane-anchoring cysteines
    and associates with membranes via protein-protein interactions with syntaxins
    and Rab GTPases (PMID:9736707, PMID:9759094; finding F29).
- evidence_id: ev-cd15887
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml
  locator: identifier, label, definition, parent_traits, canonical_examples
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: edd0ed8a35d333d4f87c1ac2a4aee0d30f5af17a5a6c9a169007401798101519
  support: partial
  quote: N-terminal SNARE motif of SNAP29. N-terminal SNARE motif of SNAP29, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. SNAP29 interacts with syntaxin-3, -4, -6, -7, -13
    and VAMP8. It is involved in multiple membrane trafficking steps, for example,
    in endocytic recycling and wrapper membrane maturation during autophagy. Qb/Qc
    SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to
    the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and a transmembrane domain. In general, the SNARE complex
    mediates membrane fusion, important for trafficking of newly synthesized proteins,
    recycling of pre-existing proteins and organelle formation. SNARE proteins are
    classified into four groups, Qa-, Qb-, Qc- and R-SNAREs, depending on whether
    the residue in the hydrophilic center layer of the four-helical bundle is a glutamine
    (Q) or arginine (R). Qa-, as well as Qb- and Qc-SNAREs, are localized to target
    organelle membranes, while R-SNARE is localized to vesicle membranes. They form
    unique complexes consisting of one member of each subgroup, that mediate fusion
    between a specific type of vesicles and their target organelle. Their SNARE motifs
    form twisted and parallel heterotetrameric helix bundles. Other members of the
    Qb/Qc SNAREs are SNAP23, SNAP25, SNAP47 and SEC9
  summary: CDD:cd15887 (label SNARE_SNAP29N, parent_traits=[CDD:cl22856], SEEDED,
    unpromoted seed examples Homo sapiens SNAP29 O95721, Mus musculus Snap29 Q9ERB0,
    and Allochromatium vinosum P83351) models the N-terminal Qb SNARE motif of SNAP29
    and propagates the identical false claim that Qb/Qc SNAREs contain a transmembrane
    domain (PMID:9736707, PMID:9759094; finding F30).
- evidence_id: ev-dcx-child-siblings
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
  locator: CDD:cd17149 (DCX1_DCDC2), CDD:cd17150 (DCX1_DCDC2B), CDD:cd17151 (DCX1_DCDC2C),
    and CDD:cd17154 (DCX2_DCDC2C)
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
  support: supports
  summary: 'Paralog-specific child repeat-1 profiles CDD:cd17149, CDD:cd17150, and
    CDD:cd17151 and repeat-2 profile CDD:cd17154 repaired in Cycles 1-2 (#1171, #1188),
    establishing the tandem DCX ubiquitin-like beta-grasp repeat wording and PMID:16278295
    citation needed on subfamily parent profiles CDD:cd17071 (F25) and CDD:cd16113
    (F26).'
- evidence_id: ev-snap25-siblings
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml
  locator: CDD:cd15885 (SNARE_SNAP25C) and CDD:cd15894 (SNARE_SNAP25N)
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: 78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b
  support: supports
  summary: Remediated SNAP25 child profiles CDD:cd15885 (#1188) and CDD:cd15894 (#1171)
    establishing the palmitoylated inter-motif linker membrane-anchoring wording for
    Qb/Qc SNAREs (PMID:9759094).
- evidence_id: ev-mrp-tmd1-siblings
  kind: record_content
  reference: data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml
  locator: CDD:cd18592 (ABC_6TM_MRP5_8_9_D1) and CDD:cd18593 (ABC_6TM_MRP4_D1_like)
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: fad0b6039c5386b3caf40fc650099ec7bfd126ff7854d42aeb805708a18c3f9a
  support: supports
  summary: Remediated N-terminal TMD1 siblings CDD:cd18592 (#1171) and CDD:cd18593
    (#1188) supporting verified resolved findings F23 (CDD:cd18599) and F24 (CDD:cd18601).
- evidence_id: ev-cycle3-stage4-cohort
  kind: record_content
  reference: reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml
  locator: findings F19-F24
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: 2d8fe1c367294f3e5660badc28211c13c97763d788ce0eb9ca3ef1cd134587f8
  support: supports
  summary: Cycle 3 Stage 4 cohort review of the 14-record CDD sibling inventory (findings
    F19-F24).
- evidence_id: ev-cycle3-stage5-cohort
  kind: record_content
  reference: reviews/structured/20261030T115500Z-cdd-cycle3-stage5-remediation-review/review.yaml
  locator: findings F19-F24 resolved
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: 3b8044daaa98388d401119aa8f726fe0aa55ccf798ba732e629822c042d2944a
  support: supports
  summary: 'Cycle 3 Stage 5 post-remediation cohort review resolving F19-F24 (#1210,
    PR #1211).'
- evidence_id: ev-cycle3-stage5-evidence
  kind: record_content
  reference: reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-05/revision-0001/evidence.yaml
  locator: findings F19-F24 (resolved) and carry_forward_ids []
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: b2fff9f04946591e53a630873434c36df162f32a1e75d2eda4a425686b49e8dc
  support: supports
  summary: Cycle 3 Stage 5 workflow evidence manifest recording resolution of F19-F24.
- evidence_id: ev-cdd-errata-infrastructure
  kind: record_content
  reference: scripts/cdd_errata.py
  locator: CDD_ERRATA table (24 entries) and scripts/repair_cdd_errata.py
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: 332155e8c1f1a119ca0f3c4394b49fa775bcc8d9f4c68e1f43183bd97b64d962
  support: supports
  summary: scripts/cdd_errata.py (24 entries) and scripts/repair_cdd_errata.py provide
    the registered writer route for both the 6 verified resolved Cycle 3 G4 records
    and the 6 new open findings F25-F30.
assessments:
- assessment_id: cohort-boundary-and-non-redundancy
  area: scope
  topic: Cohort lumping/splitting and tandem-repeat / subfamily-parent / paralog-subfamily
    boundaries
  outcome: supported
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd15855
  - ev-cd15856
  - ev-cd15884
  - ev-cd15887
  - ev-cd15889
  - ev-cd15895
  - ev-cd16113
  - ev-cd17071
  - ev-cd17152
  - ev-cd17153
  - ev-cd18599
  - ev-cd18601
  - ev-dcx-child-siblings
  - ev-snap25-siblings
  - ev-mrp-tmd1-siblings
  summary: All 12 target records represent genuine, non-redundant NCBI CDD conserved
    sequence-domain models (SEQ_DOMAIN on SEQUENCE) distinguished by tandem repeat
    position (DCX1 vs DCX2; N-terminal Qb vs C-terminal Qc SNARE helix; TMD1 vs TMD2
    6TM bundle) and hierarchy/paralog level (DCX1/2_DCDC2_like parent profiles vs
    DCDC2/DCDC2B/DCDC2C child profiles; combined SNAP25/SNAP23 vs specific SNAP25,
    SNAP23, and SNAP29 profiles; MRP4 vs MRP5/8/9). None should be merged or deprecated.
- assessment_id: cycle3-g4-remediation-verification
  area: consistency
  topic: Verification of resolved Cycle 3 Stage 5 G4 findings F19-F24 on disk
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
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
  summary: 'All 6 records remediated in Cycle 3 Stage 5 (#1210, PR #1211) remain verified
    resolved on disk at 5869b9c877b532972a405523c7c6e21945c177e4 with corrected definitions,
    literature evidence blocks, and curation_history entries.'
- assessment_id: parent-and-paralog-sibling-template-propagation
  area: consistency
  topic: Upstream NCBI CDD template defects in 6 newly audited parent/paralog sibling
    domain records
  outcome: concern
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd16113
  - CDD:cd17071
  evidence_ids:
  - ev-cd15855
  - ev-cd15856
  - ev-cd15887
  - ev-cd15889
  - ev-cd16113
  - ev-cd17071
  - ev-dcx-child-siblings
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
  summary: 'Six parent/paralog sibling CDD records (CDD:cd17071, CDD:cd16113, CDD:cd15855,
    CDD:cd15889, CDD:cd15856, CDD:cd15887) propagate the same upstream NCBI CDD template
    descriptions whose defects were repaired on their child/sibling profiles in Cycles
    1-3, yielding 6 new open findings (F25-F30: 4 major, 2 minor) preserved for Cycle
    4 Stage 5 grouped remediation.'
boundary_decisions:
- action: retain
  target_ids:
  - CDD:cd16113
  - CDD:cd17071
  - CDD:cd17152
  - CDD:cd17153
  evidence_ids:
  - ev-cd16113
  - ev-cd17071
  - ev-cd17152
  - ev-cd17153
  - ev-dcx-child-siblings
  rationale: Retain subfamily parent profiles CDD:cd17071 (DCX1_DCDC2_like, N-terminal
    repeat 1) and CDD:cd16113 (DCX2_DCDC2_like, C-terminal repeat 2) alongside paralog-specific
    repeat-2 child profiles CDD:cd17152 (DCX2_DCDC2) and CDD:cd17153 (DCX2_DCDC2B)
    under parent_traits [CDD:cl28922] because they model non-overlapping N-terminal
    vs C-terminal tandem DCX repeats and distinct CDD subfamily hierarchy levels.
- action: retain
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15884
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd15895
  evidence_ids:
  - ev-cd15855
  - ev-cd15856
  - ev-cd15884
  - ev-cd15887
  - ev-cd15889
  - ev-cd15895
  - ev-snap25-siblings
  rationale: Retain combined SNAP25/SNAP23 N-terminal Qb (CDD:cd15889) and C-terminal
    Qc (CDD:cd15855) profiles, paralog-specific SNAP23 N-terminal Qb (CDD:cd15895)
    and C-terminal Qc (CDD:cd15884) profiles, and paralog-specific SNAP29 N-terminal
    Qb (CDD:cd15887) and C-terminal Qc (CDD:cd15856) profiles under parent_traits
    [CDD:cl22856] because they distinguish non-overlapping N-terminal Qb vs C-terminal
    Qc SNARE helices and distinct CDD subfamily/paralog scopes.
- action: retain
  target_ids:
  - CDD:cd18599
  - CDD:cd18601
  evidence_ids:
  - ev-cd18599
  - ev-cd18601
  - ev-mrp-tmd1-siblings
  rationale: Retain C-terminal six-helix transmembrane bundle (TMD2) profiles CDD:cd18599
    (ABC_6TM_MRP5_8_9_D2, MRPs 5/8/9, ABCC5/ABCC11/ABCC12) and CDD:cd18601 (ABC_6TM_MRP4_D2_like,
    MRP4/ABCC4) under parent_traits [CDD:cl38913] as distinct ABCC subfamily TMD2
    profiles non-overlapping with their N-terminal TMD1 counterparts (CDD:cd18592
    and CDD:cd18593).
findings:
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
    reading disability/dyslexia (PMID:16278295). Its upstream CDD definition interpolated
    the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that
    is involved in various cellular processes, including transcriptional regulation,
    cell cycle control, and DNA repair.' and lacked a PMID:16278295 evidence block.
  target_ids:
  - CDD:cd17152
  field_paths:
  - data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml#/definition
  evidence_ids:
  - ev-cd17152
  - ev-dcx-child-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
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
    scripts/repair_cdd_errata.py (#1210, PR #1211): replaced the off-target ubiquitin
    protein-modifier sentence with the tandem DCX ubiquitin-like beta-grasp repeat
    description, added PMID:16278295 evidence, and recorded curation_history action
    source_erratum_cd17152.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092000Z-cdd-cd17152-record-review
    finding_id: F19
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F19
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
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
    but sentence 2 switched without qualification to paralog DCDC2 reading-disability/ADHD/dyslexia
    genetics and lacked a grounded evidence block.
  target_ids:
  - CDD:cd17153
  field_paths:
  - data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml#/definition
  evidence_ids:
  - ev-cd17153
  - ev-dcx-child-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
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
    scripts/repair_cdd_errata.py (#1210, PR #1211): distinguished DCDC2B from paralog
    DCDC2 in sentence 2 and qualified the dyslexia/ADHD human genetic association
    as applying to paralogous DCDC2, added UniProtKB:A2VCK2 evidence, and recorded
    curation_history action source_erratum_cd17153.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F20
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
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
    UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), and its upstream CDD definition
    falsely stated that Qb/Qc SNAREs contain a transmembrane domain whereas SNAP23
    lacks a transmembrane domain and attaches to membranes via palmitoylated cysteines
    in its inter-motif linker (PMID:9159129, PMID:9759094).
  target_ids:
  - CDD:cd15884
  field_paths:
  - data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml#/definition
  evidence_ids:
  - ev-cd15884
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
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
    scripts/repair_cdd_errata.py (#1210, PR #1211): replaced the false transmembrane-domain
    claim with palmitoylated inter-motif linker membrane anchoring, added PMID:9159129
    evidence, and recorded curation_history action source_erratum_cd15884.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F21
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
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
    UniProtKB:O09044 and Homo sapiens UniProtKB:O00161), and its upstream CDD definition
    falsely stated that Qb/Qc SNAREs contain a transmembrane domain whereas SNAP23
    lacks a transmembrane domain and attaches to membranes via palmitoylated cysteines
    in its inter-motif linker (PMID:9159129, PMID:9759094).
  target_ids:
  - CDD:cd15895
  field_paths:
  - data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml#/definition
  evidence_ids:
  - ev-cd15895
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
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
    scripts/repair_cdd_errata.py (#1210, PR #1211): replaced the false transmembrane-domain
    claim with palmitoylated inter-motif linker membrane anchoring, added PMID:9159129
    evidence, and recorded curation_history action source_erratum_cd15895.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F22
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
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
    models C-terminal TMD2 of MRPs 5, 8, and 9, and carried the corrupted upstream
    CDD ABCC template text misassigning MRP7 to ABCC7 (CFTR) instead of ABCC10 and
    overclaiming tumor multidrug-resistance efflux across all MRP1-MRP9 members (PMID:16984901).
  target_ids:
  - CDD:cd18599
  field_paths:
  - data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml#/definition
  evidence_ids:
  - ev-cd18599
  - ev-mrp-tmd1-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
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
    scripts/repair_cdd_errata.py (#1210, PR #1211): corrected MRP7=ABCC10 / CFTR=ABCC7
    nomenclature, qualified the MRP1-MRP9 efflux claim, added PMID:16984901 evidence,
    and recorded curation_history action source_erratum_cd18599.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F23
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
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
    models C-terminal TMD2 of MRP4/ABCC4, and carried the identical corrupted upstream
    CDD ABCC template text misassigning MRP7 to ABCC7 (CFTR) instead of ABCC10 and
    overclaiming tumor multidrug-resistance efflux across all MRP1-MRP9 members (PMID:16984901).
  target_ids:
  - CDD:cd18601
  field_paths:
  - data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml#/definition
  evidence_ids:
  - ev-cd18601
  - ev-mrp-tmd1-siblings
  - ev-cdd-errata-infrastructure
  - ev-cycle3-stage4-cohort
  - ev-cycle3-stage5-cohort
  - ev-cycle3-stage5-evidence
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
    scripts/repair_cdd_errata.py (#1210, PR #1211): corrected MRP7=ABCC10 / CFTR=ABCC7
    nomenclature, qualified the MRP1-MRP9 efflux claim, added PMID:16984901 evidence,
    and recorded curation_history action source_erratum_cd18601.'
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
    finding_id: F24
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
    finding_id: F24
- finding_id: F25
  issue_key: cdd-cd17071-dcx1-dcdc2-like-typo-and-ubiquitin-modifier-digression
  category: consistency
  severity: minor
  status: open
  certainty: confirmed
  title: CDD:cd17071 (DCX1_DCDC2_like) starts its definition with typo 'Dublecortin-like'
    and interpolates an off-target ubiquitin protein-modifier sentence into a microtubule-binding
    DCX repeat profile
  description: CDD:cd17071 (label=DCX1_DCDC2_like, parent_traits=[CDD:cl28922], 0
    canonical_examples) models the N-terminal first doublecortin-like domain subfamily
    of DCDC2 and similar proteins (grouping child profiles CDD:cd17149 on DCDC2, CDD:cd17150
    on DCDC2B, and CDD:cd17151 on DCDC2C), microtubule-associated proteins with tandem
    ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated
    with reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition
    starts with the typographical error 'Dublecortin-like domain 1 found in doublecortin
    domain-containing protein 2 (DCDC2) and similar proteins.', interpolates the off-target
    sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved
    in various cellular processes, including transcriptional regulation, cell cycle
    control, and DNA repair.' even though DCX domains only adopt a ubiquitin-like
    beta-grasp fold and do not function as ubiquitin protein modifiers, and lacks
    an evidence block citing PMID:16278295.
  target_ids:
  - CDD:cd17071
  field_paths:
  - data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml#/definition
  evidence_ids:
  - ev-cd17071
  - ev-dcx-child-siblings
  - ev-cdd-errata-infrastructure
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
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F26
  issue_key: cdd-cd16113-dcx2-dcdc2-like-ubiquitin-modifier-digression
  category: consistency
  severity: minor
  status: open
  certainty: confirmed
  title: CDD:cd16113 (DCX2_DCDC2_like) interpolates an off-target ubiquitin protein-modifier
    definition sentence into a microtubule-binding DCX repeat profile
  description: CDD:cd16113 (label=DCX2_DCDC2_like, parent_traits=[CDD:cl28922], 0
    canonical_examples) models the C-terminal second doublecortin-like domain subfamily
    of DCDC2 and similar proteins (grouping child profiles CDD:cd17152 on DCDC2, CDD:cd17153
    on DCDC2B, and CDD:cd17154 on DCDC2C), microtubule-associated proteins with tandem
    ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated
    with reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition
    interpolates the off-target sentence 'Ubiquitin (Ub) is a protein modifier in
    eukaryotes that is involved in various cellular processes including transcriptional
    regulation, cell cycle control, and DNA repair.' even though DCX domains only
    adopt a ubiquitin-like beta-grasp fold and do not function as ubiquitin protein
    modifiers, and lacks an evidence block citing PMID:16278295.
  target_ids:
  - CDD:cd16113
  field_paths:
  - data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml#/definition
  evidence_ids:
  - ev-cd16113
  - ev-cd17152
  - ev-dcx-child-siblings
  - ev-cdd-errata-infrastructure
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
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F27
  issue_key: cdd-cd15855-snap25c-23c-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd15855 (SNARE_SNAP25C_23C) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP25 and SNAP23 are membrane-anchored via palmitoylated cysteines
  description: CDD:cd15855 (label=SNARE_SNAP25C_23C, parent_traits=[CDD:cl22856],
    0 canonical_examples) models the combined C-terminal Qc SNARE motif subfamily
    of SNAP25 and SNAP23 (grouping child profiles CDD:cd15885 and CDD:cd15884), but
    its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices
    (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the
    Qc subgroup), which mediate the interactions with other SNARE proteins, and a
    transmembrane domain.' SNAP25/SNAP23-family Qb/Qc t-SNAREs lack a transmembrane
    domain and attach to membranes via palmitoylated cysteine residues in the central
    linker between their N-terminal Qb and C-terminal Qc SNARE motifs (PMID:9759094,
    PMID:9159129).
  target_ids:
  - CDD:cd15855
  field_paths:
  - data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml#/definition
  evidence_ids:
  - ev-cd15855
  - ev-cd15884
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
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
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F28
  issue_key: cdd-cd15889-snap25n-23n-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd15889 (SNARE_SNAP25N_23N) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP25 and SNAP23 are membrane-anchored via palmitoylated cysteines
  description: CDD:cd15889 (label=SNARE_SNAP25N_23N, parent_traits=[CDD:cl22856],
    unpromoted seed example Drosophila melanogaster Snap25 UniProtKB:P36975) models
    the combined N-terminal Qb SNARE motif subfamily of SNAP25 and SNAP23 (grouping
    child profiles CDD:cd15894 and CDD:cd15895), but its upstream CDD definition states
    'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging
    to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and a transmembrane domain.' SNAP25/SNAP23-family Qb/Qc
    t-SNAREs lack a transmembrane domain and attach to membranes via palmitoylated
    cysteine residues in the central linker between their N-terminal Qb and C-terminal
    Qc SNARE motifs (PMID:9759094, PMID:9159129).
  target_ids:
  - CDD:cd15889
  field_paths:
  - data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml#/definition
  evidence_ids:
  - ev-cd15889
  - ev-cd15895
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
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
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F29
  issue_key: cdd-cd15856-snap29c-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd15856 (SNARE_SNAP29C) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane
    anchors
  description: CDD:cd15856 (label=SNARE_SNAP29C, parent_traits=[CDD:cl22856], unpromoted
    seed examples Homo sapiens SNAP29 UniProtKB:O95721, Mus musculus Snap29 UniProtKB:Q9ERB0,
    and Allochromatium vinosum UniProtKB:P83351) models the C-terminal Qc SNARE motif
    of SNAP29, but its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil
    helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging
    to the Qc subgroup), which mediate the interactions with other SNARE proteins,
    and a transmembrane domain.' Qb/Qc SNAREs lack a transmembrane domain, and SNAP29
    specifically lacks both a transmembrane domain and the palmitoylated cysteine
    cluster of SNAP25/SNAP23, associating with membranes via protein-protein interactions
    with syntaxins and Rab GTPases (PMID:9736707, PMID:9759094).
  target_ids:
  - CDD:cd15856
  field_paths:
  - data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml#/definition
  evidence_ids:
  - ev-cd15856
  - ev-cd15884
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
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
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
- finding_id: F30
  issue_key: cdd-cd15887-snap29n-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd15887 (SNARE_SNAP29N) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane
    anchors
  description: CDD:cd15887 (label=SNARE_SNAP29N, parent_traits=[CDD:cl22856], unpromoted
    seed examples Homo sapiens SNAP29 UniProtKB:O95721, Mus musculus Snap29 UniProtKB:Q9ERB0,
    and Allochromatium vinosum UniProtKB:P83351) models the N-terminal Qb SNARE motif
    of SNAP29, and propagates the identical false upstream CDD template claim 'Qb/Qc
    SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to
    the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and a transmembrane domain.' Qb/Qc SNAREs lack a transmembrane
    domain, and SNAP29 lacks both a transmembrane domain and palmitoylated membrane-anchoring
    cysteines (PMID:9736707, PMID:9759094).
  target_ids:
  - CDD:cd15887
  field_paths:
  - data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml#/definition
  evidence_ids:
  - ev-cd15887
  - ev-cd15895
  - ev-snap25-siblings
  - ev-cdd-errata-infrastructure
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
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
actions:
- action_id: extend-cdd-errata-and-repair-cycle4-sibling-records
  description: Add accession-keyed errata entries for CDD:cd17071 (F25), CDD:cd16113
    (F26), CDD:cd15855 (F27), CDD:cd15889 (F28), CDD:cd15856 (F29), and CDD:cd15887
    (F30) to scripts/cdd_errata.py and apply them in place via scripts/repair_cdd_errata.py
    with literature-backed evidence and curation_history entries.
  finding_ids:
  - F25
  - F26
  - F27
  - F28
  - F29
  - F30
  target_ids:
  - CDD:cd15855
  - CDD:cd15856
  - CDD:cd15887
  - CDD:cd15889
  - CDD:cd16113
  - CDD:cd17071
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
  acceptance_checks:
  - All 6 parent/paralog sibling CDD records (cd17071, cd16113, cd15855, cd15889,
    cd15856, cd15887) carry accurate, paralog- and repeat-specific definitions and
    grounded literature citations.
  - scripts/seed_cdd.py and scripts/repair_cdd_errata.py replay all 30 CDD errata
    entries deterministically and idempotently.
  - scripts/validate_strict.py, scripts/validate_uniprot_grounding.py, and scripts/audit_writers.py
    pass with 0 errors.
limitations:
- This cohort review covers the frozen 12-record Cycle 4 Stage 4 CDD SEQ_DOMAIN inventory
  (6 resolved Cycle 3 G4 records and 6 newly audited parent/paralog sibling records).
- No scientific trait records under data/traits/ were edited during Stage 4; findings
  F25-F30 remain open for Stage 5 grouped remediation.
related_reviews:
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261031T043800Z-cdd-cd17071-record-review
  relationship: Companion Cycle 4 Stage 4 single-record deep review of CDD:cd17071
    (finding F25).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261030T115500Z-cdd-cycle3-stage5-remediation-review
  relationship: 'Cycle 3 Stage 5 post-remediation cohort review resolving F19-F24
    (#1210, PR #1211).'
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review
  relationship: Cycle 3 Stage 4 cohort review of the 14-record CDD sibling inventory
    (findings F19-F24).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261025T233000Z-cdd-cycle2-stage5-remediation-review
  relationship: Cycle 2 Stage 5 post-remediation cohort review resolving F13-F18 (#1188).
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261022T081000Z-cdd-stage5-remediation-review
  relationship: 'Cycle 1 Stage 5 post-remediation review resolving F3-F12 (#1171,
    #1172).'
links:
- https://github.com/CultureBotAI/proteintraitsmech/issues/1210
- https://github.com/CultureBotAI/proteintraitsmech/issues/1188
- https://github.com/CultureBotAI/proteintraitsmech/issues/1172
- https://github.com/CultureBotAI/proteintraitsmech/issues/605
```
