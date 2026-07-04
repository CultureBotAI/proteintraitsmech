# STRUCTURE axis — record sample review

## STRUCT_ACTIVE_SITE  (1137 records; 5 sampled)
- .../mcsa/3-4-dihydroxy-2-butanone-4-phosphate-synthase-mcsa648.yaml — MAJOR: enzyme-level record — label=enzyme name, definition describes the catalysed reaction, not the active site; canonical_examples carry a full per-protein feature dump. Really FUNCTION/enzyme scoped, filed STRUCT_ACTIVE_SITE.
- .../mcsa/prostaglandin-e-synthase-mcsa192.yaml — MAJOR: same — def is enzyme mechanism, `<p>` HTML markup left in definition; not active-site-specific.
- .../mcsa/nucleoside-deoxyribosyltransferase-mcsa554.yaml — MAJOR: same enzyme-level pattern (def = reaction).
- .../mcsa/carboxypeptidase-a-mcsa171.yaml — MAJOR: same; label=enzyme, def=activity description.
- .../mcsa/resorcylate-decarboxylase-mcsa992.yaml — MAJOR: same.
- SET: coherent (all M-CSA reference enzymes) but systematically mis-scoped — these are enzyme/mechanism entries whose identity is the M-CSA reaction, not a class-level active-site trait. Real defs + CURIEs + evidence, so identity is sound; the axis/category is the defect. Systemic (seed_mcsa.py).

## STRUCT_ARCHITECTURE  (64 records; 5 sampled)
- .../cath/3-solenoid-2-160.yaml — minor: definition restates label ("CATH architecture 2.160: 3 Solenoid.").
- .../cath/8-propeller-2-140.yaml — minor: boilerplate def restates label.
- .../cath/7-propeller-2-130.yaml — minor: boilerplate def restates label.
- .../architecture/a-b-four-layers-a-b-four-layers.yaml — minor: ECOD A-group boilerplate def; no parent_traits/xrefs/license (thin vs CATH siblings).
- .../cath/helix-non-globular-6-10.yaml — minor: boilerplate def restates label.
- SET: consistent, class-level, correct category/axis. Uniform weakness = definitions add nothing beyond the label (seed_cath.py/seed_ecod.py).

## STRUCT_BINDING_SITE  (83 records; 5 sampled)
- .../interpro/2-oxo-acid-dehydrogenase-lipoyl-binding-site-ipr003016.yaml — minor: def is the family abstract (describes the multienzyme complex), not the lipoyl-binding site itself.
- .../interpro/cytochrome-b5-heme-binding-site-ipr018506.yaml — PASS (def does reach the conserved His heme ligand; GO grounding present).
- .../interpro/cep192-aurora-a-binding-region-ipr057662.yaml — minor: a protein–protein "binding region", not a small-molecule site; def good but STRUCT_BINDING_SITE is a loose fit (closer to interface).
- .../interpro/cep152-plk4-binding-region-ipr057664.yaml — minor: same PPI binding-region-as-binding-site fit.
- .../interpro/hexokinase-binding-site-ipr019807.yaml — minor: def is whole-enzyme abstract and is truncated ("This entry represent…").
- SET: consistent InterPro import, class-level, real defs. Recurring: def = protein-family abstract rather than site-specific text; occasional truncation. InterPro conserved/binding-site signatures placed on STRUCTURE per repo convention (acceptable).

## STRUCT_CAVITY  (5 records; 5 sampled)
- .../cavity/pocket.yaml — PASS
- .../cavity/groove.yaml — PASS
- .../cavity/tunnel.yaml — PASS
- .../cavity/cavity.yaml — PASS
- .../cavity/cleft.yaml — PASS
- SET: exemplary — distinct real definitions, class-level, proteintraitsmech: CVs, consistent source. Model set (seed_localstructuralfeature.py).

## STRUCT_CLASS  (17 records; 5 sampled)
- .../scope/membrane-and-cell-surface-proteins-and-peptides-sunid56835.yaml — minor: def restates label + sccs code.
- .../cath/mainly-alpha-1.yaml — minor: boilerplate def ("CATH class 1: Mainly Alpha.").
- .../scope/multi-domain-proteins-alpha-and-beta-sunid56572.yaml — minor: boilerplate def.
- .../cath/alpha-beta-3.yaml — minor: boilerplate def.
- .../cath/special-6.yaml — minor: boilerplate def; "Special" is an intrinsically opaque CATH bucket.
- SET: consistent, correct axis/category, class-level. Same boilerplate-definition weakness (seed_cath.py/seed_scope.py).

## STRUCT_DISULFIDE  (1 record; 1 sampled)
- .../disulfide/disulfide-bond.yaml — PASS (real def, SO + valuesets grounding, class-level).

## STRUCT_DOMAIN  (13514 records; 5 sampled)
- .../scope/chondroitin-abc-lyase-i-sunid89113.yaml — minor: boilerplate def; no structural_geometry_representations (A8 expects it for STRUCT_DOMAIN).
- .../scope/automated-matches-sunid190425.yaml — MAJOR: label "automated matches" is an uninformative SCOPe placeholder node, not a human-readable trait; def restates it.
- .../scope/paramyxovirus-sv5-fusion-protein-core-sunid58078.yaml — minor: boilerplate def; no representation slot.
- .../scope/automated-matches-sunid226849.yaml — MAJOR: same "automated matches" placeholder-as-trait problem.
- .../scope/cyclin-a-sunid47956.yaml — minor: boilerplate def; no representation slot.
- SET: consistent SCOPe import with correct hierarchy/parents, but two systemic defects: (a) "automated matches" placeholder nodes seeded as traits, (b) STRUCT_DOMAIN records lack structural_geometry_representations (only TED carries them). seed_scope.py.

## STRUCT_DYNAMICS  (18 records; 5 sampled)
- .../pato/normal-elasticity-pato0045016.yaml — minor: generic PATO elasticity quality, not protein-structure-specific.
- .../dynamics/elbow.yaml — PASS (real def, CV, parent).
- .../pato/increased-elasticity-pato0002287.yaml — minor: generic elasticity quality.
- .../pato/elastic-pato0001171.yaml — minor: generic elasticity quality.
- .../pato/increased-object-quality-pato0002305.yaml — MAJOR: generic upper-level PATO quality ("increased object quality") dragged in — off-topic, not a dynamics trait.
- SET: mixes a genuine structural motif (elbow) with abstract PATO qualities incl. an ontology-parent artifact — B2 kind-mixing. PATO-quality seeder.

## STRUCT_FOLD  (55735 records; 5 sampled)
- .../fold/high_symmetry/af-a0z017-ted04.yaml — PASS-minor: strong record (structural_geometry_representations, groundings, evidence); note TED per-AlphaFold-model domain instance treated as a CLASS (repo convention).
- .../fold/ecod/yxzc-109_4_1_3063.yaml — minor: boilerplate def restates label+count; no structural_geometry_representations.
- .../fold/ecod/arc1p-n-like-109_1_1_11.yaml — minor: boilerplate def; has PDB/ECOD xrefs but no representation slot.
- .../fold/ecod/zf-b-box-376_1_4_5.yaml — minor: boilerplate def; no representation.
- .../fold/ecod/duf818-7579_1_1_52.yaml — minor: boilerplate def; no representation.
- SET: inconsistent representation coverage — TED folds carry structural_geometry_representations, ECOD F-group folds do not (A8 gap). Also ECOD F-group = sequence/family level mapped to STRUCT_FOLD (granularity questionable). seed_ecod.py vs seed_ted.py.

## STRUCT_HOMOLOGOUS_SUPERFAMILY  (15177 records; 5 sampled)
- .../sporulation-related-repeat-sunid110997.yaml — minor: SCOPe sf boilerplate def; no representation slot.
- .../colicin-m-related-3173_1.yaml — minor: ECOD H-group boilerplate def; no representation.
- .../uncharacterized-protein-rv3902c-3842.yaml — MAJOR: ECOD **X-group** (architecture-level "possible homology") filed as HOMOLOGOUS_SUPERFAMILY alongside H-groups — wrong hierarchy level; also opaque label.
- .../highly-disulfide-linked-beta-sandwich-region-of-p43-7084_1.yaml — minor: H-group boilerplate def.
- .../cath/aspartate-aminotransferase-domain-1-3-90-1150-10.yaml — minor: CATH boilerplate def; no representation.
- SET: mixes ECOD X- and H-group levels under one category (B3 granularity), boilerplate defs, no structural_geometry_representations (A8). seed_ecod.py/seed_scope.py/seed_cath.py.

## STRUCT_INTERFACE  (1 record; 1 sampled)
- .../interface/interface.yaml — PASS (real def, SO grounding, class-level).

## STRUCT_METAL_SITE  (1 record; 1 sampled)
- .../metal_site/metal-binding-site.yaml — PASS (real def, GO:0046872 grounding).

## STRUCT_SECONDARY  (33 records; 5 sampled)
- .../secondary/greek-key.yaml — PASS (def + secondary_structure_representations + parent).
- .../secondary/ppii-helix.yaml — PASS
- .../secondary/beta-bridge.yaml — PASS
- .../secondary/gamma-turn.yaml — PASS
- .../secondary/helix-cap.yaml — PASS (also SO grounding)
- SET: exemplary — distinct real defs, correct secondary_structure_representations (A8), internal parent hierarchy, DSSP provenance. Best-modeled set in the axis.

## STRUCT_STABILITY  (37 records; 5 sampled)
- .../pato/structure-pato0000141.yaml — MAJOR: PATO "structure" (generic morphology quality) mis-filed as STRUCT_STABILITY; not a stability trait at all.
- .../conditions/increased-desiccation-stability.yaml — PASS (rich def, synonyms, parents).
- .../conditions/desiccation-stability.yaml — PASS
- .../conditions/increased-saline-stability.yaml — PASS
- .../conditions/increased-mechanical-stability.yaml — PASS
- SET: curated stability taxonomy is excellent and coherent; one imported PATO upper-level quality pollutes the category (B2). Curated seeder vs PATO import.

## STRUCT_SURFACE  (14 records; 5 sampled)
- .../pato/soluble-in-pato0001537.yaml — minor: solubility quality, not a surface property; loose fit for STRUCT_SURFACE.
- .../pato/dissolved-pato0001986.yaml — minor: solubility quality, not surface.
- .../pato/negative-charge-pato0002196.yaml — minor: physicochemical charge quality bucketed as surface.
- .../pato/hydrophobicity-pato0001884.yaml — minor: physicochemical quality (defensible as surface hydrophobicity).
- .../pato/hydrophobic-pato0001885.yaml — minor: physicochemical quality.
- SET: real PATO defs but STRUCT_SURFACE is a catch-all for physicochemical qualities incl. solubility (not surface) — B2 kind-mixing. PATO-quality seeder.

## STRUCT_TOPOLOGY  (5427 records; 5 sampled)
- .../cath/pcra-domain-4-1-10-486.yaml — minor: boilerplate def; no structural_geometry_representations (A8).
- .../fas-type-i-helical-domain-3294_1_1.yaml — minor: ECOD T-group boilerplate def; no representation.
- .../non-structural-protein-3-3825_1_1.yaml — minor: boilerplate def; no representation.
- .../aminomethyltransferase-beta-barrel-domain-1_1_8.yaml — minor: boilerplate def; no representation.
- .../get5-carboxyl-domain-3443_1_1.yaml — minor: boilerplate def; no representation.
- SET: consistent, class-level, correct hierarchy/parents. Uniform boilerplate defs + missing representation slot. seed_cath.py/seed_ecod.py.

## STRUCTURE systemic issues
1. **Boilerplate definitions that restate the label** — pervasive across every CATH/SCOPe/ECOD classification seeder (architecture, class, domain, fold[ECOD], homologous_superfamily, topology): defs of the form "CATH topology X: Y." / "ECOD T-group 'Y' (code)." / "SCOPe dm-level node 'Y' (sccs)." add no information. (seed_cath.py, seed_scope.py, seed_ecod.py) — MAJOR by volume, minor per record.
2. **Missing structural_geometry_representations on classification records** — A8 expects it for STRUCT_FOLD/DOMAIN/HOMOLOGOUS_SUPERFAMILY/TOPOLOGY, but only TED folds carry it; all sampled CATH/SCOPe/ECOD domain/fold/superfamily/topology records lack the slot. (seed_cath.py, seed_scope.py, seed_ecod.py) — MAJOR, systemic.
3. **M-CSA active-site records are enzyme/mechanism entries** — label = enzyme name, definition = catalysed reaction, giant per-protein canonical_examples; scoped STRUCT_ACTIVE_SITE but effectively FUNCTION-level. Affects the full 1137-record M-CSA set. (seed_mcsa.py) — MAJOR.
4. **Generic/mis-bucketed PATO qualities** — PATO:0000141 "structure" → STRUCT_STABILITY and PATO:0002305 "increased object quality" → STRUCT_DYNAMICS are plainly wrong; solubility qualities under STRUCT_SURFACE. Upper-level PATO import artifacts leaking into STRUCTURE buckets. (PATO-quality seeder) — MAJOR for the clear mis-files, else minor.
5. **SCOPe "automated matches" placeholder nodes seeded as traits** — uninformative labels, no real definition; pollute STRUCT_DOMAIN. (seed_scope.py) — MAJOR.
6. **ECOD hierarchy-level conflation** — X-group and H-group both mapped to STRUCT_HOMOLOGOUS_SUPERFAMILY; F-group mapped to STRUCT_FOLD. Level-to-category mapping is inconsistent. (seed_ecod.py) — MAJOR/minor granularity.
