# One-per-(axis,category) snapshot — 48 cells

PER=1 snapshot mode: one random record per (trait_axis, trait_category) cell, reviewed individually against Part A (A1–A9), then Part B taxonomy overview.

| axis | category | total | picked record | verdict | note |
|------|----------|------:|---------------|---------|------|
| EVOLUTION | EVO_CONSERVATION | 3 | proteintraitsmech:EVO_VARIABLE (variable-protein) | PASS | Curator-minted CURIE; genuine def; `evolutionary_scope` present (A8). Clean. |
| EVOLUTION | EVO_PANGENOME | 6 | proteintraitsmech:EVO_PANGENOME_CORE (core-genome-protein) | PASS | Good def; `evolutionary_scope` with prevalence bands + Roary method (A8). Clean. |
| FUNCTION | FUNC_ENVIRONMENTAL_RESPONSE | 49 | METPO:1000601 (oxygen preference) | minor | Def is organism-level ("organism's oxygen requirements"), not protein-level; category OK but trait subject drifts toward phenotype. RELATED synonym "metabolism" loose. |
| FUNCTION | FUNC_ENZYMATIC_ACTIVITY | 26003 | RHEA:29471 | PASS | Rhea reaction; `chemical_participants` (CHEBI) supply the EC/Rhea representation (A8). Model. |
| FUNCTION | FUNC_INTERACTION_PARTNER | 147 | MI:0220 (ubiquitination reaction) | major | Category mismatch: a PSI-MI interaction *type/reaction*, not an interaction *partner*. Def also ungrammatical ("reaction that create"). Systemic to psi_mi seeder. |
| FUNCTION | FUNC_ORTHOLOG_GROUP | 9728 | COG:COG1949 (oligoribonuclease) | PASS | Real def; member_of COG_CATEGORY_A. Parent-category grounding (curator-minted) worth spot-check but plausible. |
| FUNCTION | FUNC_PATHWAY | 3969 | Reactome:R-HSA-5083635 | minor | Def = label + boilerplate ("a Reactome pathway; the protein participates..."). Disease-pathway ("Defective B3GALTL causes PpS") is a real Reactome node; part_of parent OK. |
| FUNCTION | FUNC_PROTEIN_FAMILY | 20313 | NCBIfam:NF040143 (DUF5682) | minor | Boilerplate template def; DUF = unknown function so thin is expected, but no grounding/xref beyond id. ncbifam seeder pattern. |
| FUNCTION | FUNC_RESISTANCE | 7452 | ARO:3004595 (erm(45)) | PASS | Substantive mechanistic def; parent ARO:3000560; PMID xref. Model. |
| FUNCTION | FUNC_TRANSPORT | 2285 | TCDB:1.D.78 (ACOC family) | minor | Def = label + boilerplate ("proteins in this family mediate membrane transport"); parent TCDB:1.D OK. tcdb seeder pattern. |
| SEQUENCE | SEQ_CLEAVAGE_SITE | 11 | ELM:ELME000103 (CLV_PCSK_PC7_1) | PASS | Real def + `sequence_pattern` (A8) + canonical example. Label is raw ELM class name (minor style; synonym rescues it). |
| SEQUENCE | SEQ_CONSERVATION | 775 | InterPro:IPR019817 (IRF conserved site) | PASS | Full authored InterPro definition; interpro2go mapped_xrefs. Model record. |
| SEQUENCE | SEQ_CROSSLINK_SITE | 69 | MOD:00877 | minor | Terse import def ("dimethyl pimelimidate modification from Unimod"); real PSI-MOD term, parent + Unimod xref present. psi-mod seeder. |
| SEQUENCE | SEQ_DISORDER | 202 | Pfam:PF03154 (Atrophin-1) | minor | Boilerplate "X. Pfam disordered family Y" template def; rich canonical_examples. pfam seeder pattern. |
| SEQUENCE | SEQ_DOMAIN | 88742 | NCBIfam:NF017413 (DUF771) | minor | Boilerplate DUF template def; no xref. Note NCBIfam split: this→SEQ_DOMAIN vs NF040143→FUNC_PROTEIN_FAMILY (type-driven). |
| SEQUENCE | SEQ_FAMILY | 14424 | Pfam:PF05321 (HHA) | minor | Boilerplate def with "Pfam family **family** HHA" duplication bug; canonical_examples good. pfam seeder. |
| SEQUENCE | SEQ_GLYCOSYLATION_SITE | 85 | MOD:00760 | major | Def is an import artifact: "modification from Unimod N-linked glycosylation - **missing ref**". Fails A4. psi-mod seeder. |
| SEQUENCE | SEQ_HOMOLOGOUS_SUPERFAMILY | 5699 | InterPro:IPR016106 (His-decarboxylase N-term) | PASS | Full authored def; interpro2go. Model. |
| SEQUENCE | SEQ_INITIATOR_METHIONINE | 1 | proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE | PASS | Singleton justified: one UniProt FT type = one class; clean def; per-protein instances in canonical_examples (class-not-instance correct). |
| SEQUENCE | SEQ_LEADER_PEPTIDE | 20 | proteintraitsmech:RIPP_LEADER_LANTHIPEPTIDE | PASS | Rich curated RiPP-class def. Clean. |
| SEQUENCE | SEQ_LIPIDATION_SITE | 40 | MOD:01685 (α-amino palmitoyl) | PASS | Genuine PSI-MOD def; parents + synonyms. Good. |
| SEQUENCE | SEQ_MATURE_CHAIN | 1 | proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN | PASS | Singleton justified; good def; instances as examples. |
| SEQUENCE | SEQ_MODIFIED_RESIDUE | 618 | MOD:01814 | PASS | Genuine def; parents, xrefs (PMIDs/RESID). Good. |
| SEQUENCE | SEQ_MOTIF | 3121 | PROSITE:PS00492 (Clusterin signature 1) | major | Def = label restated verbatim ("Clusterin signature 1"). Fails A4 despite excellent `sequence_pattern`/parent/canonical_examples. Systemic to prosite seeder. |
| SEQUENCE | SEQ_PROPEPTIDE | 1 | proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE | PASS | Singleton justified; good def. |
| SEQUENCE | SEQ_PTM_SITE | 1251 | MOD:01688 (3-hydroxy-L-asn) | PASS | Genuine def. Synonym typo "hydroxylationn" (from source). Overlaps SEQ_MODIFIED_RESIDUE — see granularity note. |
| SEQUENCE | SEQ_REPEAT | 2073 | Pfam:PF29002 (YNL193W middle) | minor | Boilerplate "Pfam repeat family" template def; parent CL0020. pfam seeder. |
| SEQUENCE | SEQ_SIGNAL_PEPTIDE | 1 | proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE | PASS | Singleton justified; good def. |
| SEQUENCE | SEQ_TARGETING_SIGNAL | 28 | ELM:ELME000278 (TRG_NLS_MonoExtC_3) | PASS | Real def + `sequence_pattern` (A8) + examples. Label raw ELM name (minor style). |
| SEQUENCE | SEQ_TRANSIT_PEPTIDE | 1 | proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE | PASS | Singleton justified; good def. |
| SEQUENCE_STRUCTURE | MIXED_COILED_COIL | 315 | Pfam:PF07926 (TPR/MLP1/2) | minor | Boilerplate "Pfam coiled-coil family" def; pfam2go + interpro2go mapped_xrefs present. No dedicated coiled-coil representation slot. pfam seeder. |
| SEQUENCE_STRUCTURE | MIXED_STRUCTURAL_REPEAT | 122 | RepeatsDB:5 (Beads-on-a-string) | PASS | Real def (run-on: two sentences merged, minor). Class-level RepeatsDB structural class; PDB xref is example. |
| STRUCTURE | STRUCT_ACTIVE_SITE | 1137 | MCSA:824 (mono-ADP-ribosyltransferase C3) | minor | Excellent mechanistic def + evidence PMIDs + features, BUT contains HTML `<i>` tags (A4 import artifact) and "boltulinum" typo. Content is otherwise a model. |
| STRUCTURE | STRUCT_ARCHITECTURE | 64 | ECOD:A.mixed-a-b-and-a-b | minor | Boilerplate ECOD-node def; no license/provenance beyond source string. ecod seeder. |
| STRUCTURE | STRUCT_BINDING_SITE | 83 | InterPro:IPR019780 (germin Mn site) | minor | Rich def but carries stripped-citation artifacts "oxalate oxidases ( ) ... superoxide dismutases ( )" (A4). interpro seeder. |
| STRUCTURE | STRUCT_CAVITY | 5 | proteintraitsmech:TUNNEL | PASS | Clean LinkML-LSF def + valuesets xref. |
| STRUCTURE | STRUCT_CLASS | 17 | SCOP:51349 (α/β proteins) | minor | Boilerplate "SCOPe cl-level node" def; no license. scope seeder. |
| STRUCTURE | STRUCT_DISULFIDE | 1 | proteintraitsmech:DISULFIDE_BOND | PASS | Singleton justified; clean def + SO xref. |
| STRUCTURE | STRUCT_DOMAIN | 13514 | SCOP:55133 (Archaeal L30) | minor | Boilerplate "SCOPe dm-level node" def; parent SCOP:55130 OK; no geometry rep/license. scope seeder. |
| STRUCTURE | STRUCT_DYNAMICS | 18 | PATO:0001171 (elastic) | PASS | Genuine PATO def; parent. Generic quality repurposed as structural-dynamics trait (acceptable fit). |
| STRUCTURE | STRUCT_FOLD | 55735 | ECOD:F.109.4.1.2461 (TPR_6/8/11/16) | minor | Boilerplate ECOD-node def; no `structural_geometry_representations` (A8 expects one for folds); no license. Label = member-family list. ecod seeder. |
| STRUCTURE | STRUCT_HOMOLOGOUS_SUPERFAMILY | 15177 | CATH:1.20.58.1310 (PRONE subdomain 2) | minor | Boilerplate "CATH homologous superfamily N: label" def; parent OK; no geometry rep. cath seeder. |
| STRUCTURE | STRUCT_INTERFACE | 1 | proteintraitsmech:INTERFACE | PASS | Singleton justified; clean def + SO xref. |
| STRUCTURE | STRUCT_METAL_SITE | 1 | proteintraitsmech:METAL_BINDING_SITE | PASS | Singleton justified; clean def + GO:0046872. |
| STRUCTURE | STRUCT_SECONDARY | 33 | proteintraitsmech:HELIX_TURN_HELIX | PASS | Good def; `secondary_structure_representations` (topology_string) present (A8); parent SUPER_SECONDARY_MOTIF. Model. |
| STRUCTURE | STRUCT_STABILITY | 37 | proteintraitsmech:STABILITY_PRESSURE_DECREASED | PASS | Good curated def; dual parents incl PATO:0015028. Clean. |
| STRUCTURE | STRUCT_SURFACE | 14 | PATO:0001986 (dissolved) | major | Poor category fit: generic PATO "passing into solution" (solubility state) is not a structural *surface* trait; not protein-specific. Category-content mismatch. |
| STRUCTURE | STRUCT_TOPOLOGY | 5427 | ECOD:T.3166.1.1 (rpL36/L36e) | minor | Boilerplate ECOD-node def; parent OK; no geometry rep/license. ecod seeder. |

**Severity tally:** PASS 24 · minor 20 · major 4 · blocker 0.
Majors: FUNC_INTERACTION_PARTNER (MI:0220, type≠partner), SEQ_GLYCOSYLATION_SITE (MOD:00760, "missing ref" artifact def), SEQ_MOTIF (PS00492, def=label), STRUCT_SURFACE (PATO dissolved, category mismatch).

## Taxonomy overview

- **model categories** (rich, self-defining, correctly represented): SEQ_CONSERVATION and SEQ_HOMOLOGOUS_SUPERFAMILY (InterPro — full authored definitions + interpro2go), FUNC_ENZYMATIC_ACTIVITY (Rhea + CHEBI participants), FUNC_RESISTANCE (ARO — mechanistic def + PMID), STRUCT_ACTIVE_SITE (M-CSA — mechanism + evidence, modulo HTML), STRUCT_SECONDARY (curated + `secondary_structure_representations`), and the whole curated/hand-minted tier: the five UniProt-FT `proteintraitsmech:*` singletons (SIGNAL/TRANSIT/PROPEPTIDE/MATURE_CHAIN/INITIATOR_METHIONINE), the LSF cavity/interface/metal/disulfide singletons, EVO_* and STRUCT_STABILITY. These are the cleanest cells in the corpus — real definitions, correct class-not-instance modelling, right representation slots.

- **weak / systemic patterns** (seeder-named):
  - **pfam seeder** — templated definitions "`<label>`. Pfam `<type>` family `<name>` (Pfam:PFxxxxx)." across SEQ_DISORDER / SEQ_FAMILY / SEQ_REPEAT / MIXED_COILED_COIL; SEQ_FAMILY shows a "Pfam family **family**" duplication bug. Not wrong, just non-defining boilerplate.
  - **ncbifam seeder** — DUF template defs ("`DUF####` … members share this conserved family signature"), thin grounding (FUNC_PROTEIN_FAMILY, SEQ_DOMAIN).
  - **prosite seeder** — definition is the label verbatim (SEQ_MOTIF PS00492) → A4 fail despite excellent pattern/example payload. Likely corpus-wide for PROSITE signatures.
  - **psi-mod seeder** — raw import fragments as definitions ("modification from Unimod", "N-linked glycosylation - missing ref") in SEQ_GLYCOSYLATION_SITE / SEQ_CROSSLINK_SITE; the "missing ref" string is a hard artifact.
  - **ecod / scope / cath seeders** — one-line "`<db>` `<node-level>` node '`<label>`'" defs, no `license`, and — for STRUCT_FOLD / STRUCT_TOPOLOGY / STRUCT_HOMOLOGOUS_SUPERFAMILY / STRUCT_DOMAIN — no `structural_geometry_representations` even though A8 expects fold/domain geometry (the recent TED 3D-geometry populate did not reach ECOD/SCOP/CATH cells).
  - **interpro seeder** — stripped-citation artifacts "( )" survive into definitions (STRUCT_BINDING_SITE germin); some InterPro entries carry unresolved reference parens.
  - **psi_mi seeder** — interaction *method/reaction-type* terms land in FUNC_INTERACTION_PARTNER, which is meant for partners; the whole category footprint is worth auditing.
  - **PATO-sourced STRUCT_* cells** — generic qualities repurposed as protein traits; "elastic"→DYNAMICS is a fair fit, "dissolved"→SURFACE is not (solubility state, not surface geometry).

- **granularity / singletons**: eight 1-record categories — the five UniProt-FT sequence-feature classes plus STRUCT_DISULFIDE / STRUCT_INTERFACE / STRUCT_METAL_SITE. All are **justified**: each is a single well-scoped class-level trait (one feature type / one local structural feature) with per-protein occurrences carried as `canonical_examples`, not as separate records — the correct class/instance split. They are, notably, among the highest-quality records. Real granularity concern is the opposite end: the PSI-MOD subtree is fragmented across SEQ_MODIFIED_RESIDUE / SEQ_PTM_SITE / SEQ_CROSSLINK_SITE / SEQ_GLYCOSYLATION_SITE / SEQ_LIPIDATION_SITE by MOD sub-branch — closely related modification terms can split across cells (e.g. a modified residue vs a "PTM site"), and the two MOD-derived hydroxylation/modified-residue buckets risk near-duplicate classes. The ECOD/SCOP/CATH structural cells (ARCHITECTURE/CLASS/FOLD/DOMAIN/HOMOLOGOUS_SUPERFAMILY/TOPOLOGY) also carry three parallel hierarchies for overlapping structural granularity — coherent per-source but not cross-reconciled.
