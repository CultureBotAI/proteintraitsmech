# FUNCTION axis — record sample review

## FUNC_ENVIRONMENTAL_RESPONSE  (49 records; 5 sampled)
- data/traits/function/environmental_response/metpo/mesophilic-metpo1000615.yaml — MINOR: coherence — organism-level phenotype ("mesophilic"), not a protein function; else clean class w/ real def + parent
- data/traits/function/environmental_response/metpo/halotolerant-metpo1000622.yaml — MINOR: organism-level phenotype; real def, parent, term_kind CLASS
- data/traits/function/environmental_response/metpo/extreme-hyperthermophilic-metpo1000721.yaml — PASS (real def, synonyms, parent)
- data/traits/function/environmental_response/metpo/thermotolerant-metpo1000619.yaml — PASS
- data/traits/function/environmental_response/metpo/non-halophilic-metpo1000624.yaml — PASS
- SET: PASS-with-caveat — internally consistent (all METPO, seed_traitontomap/obo), good distinct defs, CLASS-level; coherent as a set but the whole category is organism/cell phenotypes rather than protein-level environmental response. Systemic modelling question, not a per-record defect. Anchor: no EC/GO — acceptable for phenotype terms. License CC-BY-4.0 correct for METPO.

## FUNC_ENZYMATIC_ACTIVITY  (26003 records; 5 sampled)
- data/traits/function/enzymatic_activity/rhea/a-1-o-1z-alkenyl...rhea37763.yaml — PASS (RHEA anchor, ChEBI participants, def restates reaction — acceptable for a reaction class)
- data/traits/function/enzymatic_activity/ec/1-5-3-18-ec1-5-3-18.yaml — PASS (EC anchor, parent EC:1.5.3.-, ec2go + rhea2ec xrefs, canonical example)
- data/traits/function/enzymatic_activity/rhea/2e-7z-hexadecadienoyl...rhea86587.yaml — PASS
- data/traits/function/enzymatic_activity/rhea/l-tryptophan-fadh2-o2...rhea85799.yaml — PASS
- data/traits/function/enzymatic_activity/rhea/tetradecamide...rhea62992.yaml — PASS
- SET: PASS — strong. EC/Rhea anchors present, ChEBI participants typed (chebi+role), mapped_xrefs carry predicate+source (EC record). Consistent seeders seed_rhea.py/seed_ec.py. License "CC-BY 4.0" correct for Rhea/ExPASy. Def diversity low by design (reaction-string templating) but each is a distinct reaction — fine.

## FUNC_INTERACTION_PARTNER  (147 records; 5 sampled)
- data/traits/function/interaction_partner/psi_mi/synthetic-haploinsufficiency-sensu-biogrid-mi2372.yaml — PASS (MI CURIE, real def, parent)
- data/traits/function/interaction_partner/psi_mi/direct-interaction-mi0407.yaml — PASS
- data/traits/function/interaction_partner/psi_mi/genetic-interaction-mi2402.yaml — MINOR: A4 def has trailing OBO artifact "\nab (not=) E"
- data/traits/function/interaction_partner/psi_mi/aminoacylation-reaction-mi1143.yaml — MINOR: coherence — "aminoacylation reaction" is an interaction/reaction-type term, not an interaction partner; real def
- data/traits/function/interaction_partner/psi_mi/synthetic-lethality-sensu-biogrid-mi2370.yaml — PASS (two parents)
- SET: PASS-with-caveat — coherent as PSI-MI interaction vocabulary (seed_obo.py), all CLASS-level with real defs + parents. Mixed sub-kinds (interaction types, genetic-interaction phenotypes, a reaction type) but all legitimately under "interaction". Fix the one def artifact.

## FUNC_ORTHOLOG_GROUP  (9728 records; 5 sampled)
- data/traits/function/ortholog_group/cdd/kog4437-...-kog4437.yaml — MINOR: A4 def = label + boilerplate ("members share this curated model")
- data/traits/function/ortholog_group/cdd/kog3324-...-kog3324.yaml — MINOR: same def-is-label pattern
- data/traits/function/ortholog_group/cdd/kog2582-...-kog2582.yaml — MINOR: same
- data/traits/function/ortholog_group/cog/glutamate-mutase-epsilon-subunit-cog4865.yaml — PASS (COG CURIE, parent COG category, member_of relation, synonym) — better modelled than KOG siblings
- data/traits/function/ortholog_group/cdd/kog0857-...-kog0857.yaml — MINOR: def = label + boilerplate
- SET: PASS-with-caveat — consistent CLASS-level ortholog groups. CDD/KOG records (seed_obo/seed cdd) restate the label in the definition and, unlike COG, lack parent/category linkage; COG records (seed_cog.py) carry parent_traits + trait_relations. Systemic: CDD seeder should attach a KOG functional-category parent and a non-restating gloss. License "US Government public domain" correct.

## FUNC_PATHWAY  (3969 records; 5 sampled)
- data/traits/function/pathway/seed/seed-subsystem-urea-cycle.yaml — PASS (EC participant set, GO-BP anchor, parent subclass; def boilerplate but participants carry it)
- data/traits/function/pathway/seed/seed-subsystem-pyridoxin-vitamin-b6-degradation-pathway.yaml — PASS (rich curated def, EC set)
- data/traits/function/pathway/seed/seed-subsystem-dna-replication-bacterial.yaml — MINOR: A4 def = label + boilerplate (only 1 EC participant)
- data/traits/function/pathway/reactome/regulation-of-ifng-signaling-r-hsa-877312.yaml — PASS (parent, part_of, GO-BP anchor; def boilerplate)
- data/traits/function/pathway/reactome/signaling-by-fgfr-r-hsa-190236.yaml — PASS
- SET: PASS — best-modelled bucket. All CLASS-level, parent_traits, has_participant EC sets and/or GO-BP anchors (A8 satisfied), typed mapped_xrefs. Two seeders (seed_seed_subsystems.py PD, seed_reactome.py CC0) — licenses correct. Def boilerplate on the SEED short-role subsystems is the only minor.

## FUNC_PROTEIN_FAMILY  (20313 records; 5 sampled)
- data/traits/function/protein_family/ncbifam/limlp-15305-fam-nf047596.yaml — MINOR: A3 label opaque (LIMLP_15305_fam); def gives readable name + boilerplate
- data/traits/function/protein_family/ncbifam/prk01130-1-nf002231.yaml — MINOR: A3 label "PRK01130.1" opaque; has EC xref (good)
- data/traits/function/protein_family/ncbifam/signal-int-sinm-nf037948.yaml — MINOR: label opaque; synonym present
- data/traits/function/protein_family/ncbifam/mag3240-fam-nf045963.yaml — MINOR: label opaque
- data/traits/function/protein_family/ncbifam/prk08329-1-nf006205.yaml — MINOR: label opaque; def "threonine synthase" + boilerplate
- SET: PASS-with-caveat — consistent CLASS-level NCBIfam families (seed_ncbifam.py). Two recurring minors: (1) label is the raw HMM accession/tag not the human-readable family name (which lives in the definition); (2) def = readable-name + fixed boilerplate. No anchor (EC/GO) on most; EC xref only when NCBIfam supplies one. Modelling note: a protein-family signature is arguably SEQUENCE, parked in FUNCTION by design — consistent across the bucket.

## FUNC_RESISTANCE  (7452 records; 5 sampled)
- data/traits/function/resistance/aro/oxa-1136-aro3008554.yaml — MINOR: A4 def restates label ("OXA-2 family class D beta-lactamase OXA-1136")
- data/traits/function/resistance/aro/fosa4-aro3003210.yaml — PASS (real mechanism def, PMID xref, parent)
- data/traits/function/resistance/aro/oxa-898-aro3005094.yaml — PASS (mechanism + origin, PMID)
- data/traits/function/resistance/aro/dfra16-aro3003014.yaml — PASS (real def, PMID)
- data/traits/function/resistance/aro/cfia29-aro3009099.yaml — MINOR: A4 def restates label ("Subclass B1 metallo-beta-lactamase CfiA29")
- SET: PASS — consistent ARO CLASS-level determinants (seed_traitontomap/aro), correct ARO: CURIEs, parent_traits, PMID xrefs where curated, CC-BY 4.0. Def quality bimodal (rich vs. label-paraphrase) but never empty.

## FUNC_TRANSPORT  (2285 records; 5 sampled)
- data/traits/function/transport/tcdb/the-amphipathic-peptide-mastoparan...1-c-32.yaml — PASS (TCDB CURIE, parent TC class, ChEBI TRANSPORTED participants)
- data/traits/function/transport/tcdb/the-cytotoxic-amylin...1-c-49.yaml — PASS
- data/traits/function/transport/tcdb/the-synthetic-isophthalamide...2-b-78.yaml — MINOR: A8 no chemical_participants (no transported substrate anchor); def = label + boilerplate
- data/traits/function/transport/tcdb/the-putative-channel-forming-3-tmss-mamf...9-b-89.yaml — PASS (1 participant)
- data/traits/function/transport/tcdb/the-membrane-protein-mlc1...9-b-129.yaml — MINOR: A8 no substrate anchor; def boilerplate
- SET: PASS — consistent TCDB CLASS-level families (seed_tcdb.py), correct hierarchy (parent TC subclass), CC-BY-SA 3.0. Def = label + fixed boilerplate throughout (low diversity); substrate participants present only when TCDB supplies them (9.B / 2.B families lack them).

## FUNCTION systemic issues (ranked)
1. **Definition = label + fixed boilerplate** (major, cross-source): CDD/KOG, NCBIfam, TCDB, Reactome, and short-role SEED subsystems template the definition as "<label> — a <source> <thing>; members/proteins share/mediate …". Never empty (label carries meaning), but low informational value and near-zero def diversity within a bucket. Highest-impact fix: enrich seeder glosses (esp. seed cdd/KOG and seed_tcdb.py).
2. **Opaque labels on NCBIfam** (minor, systemic): `label` is the raw model accession/tag (PRK01130.1, MAG3240_fam, LIMLP_15305_fam) while the human-readable family name sits only in the definition. Consider promoting the readable name to `label` (or a display synonym).
3. **Bucket-vs-axis modelling drift** (minor, by-design, worth a decision): FUNC_PROTEIN_FAMILY (signature families) and FUNC_ENVIRONMENTAL_RESPONSE (organism phenotypes: mesophilic/halotolerant) are not protein *functions* in the strict sense — one leans SEQUENCE, the other organism/cell-level. Consistent within each category; flag only as an axis-scoping question.
4. **One def artifact**: genetic-interaction MI:2402 carries a trailing OBO cross-ref fragment "\nab (not=) E" in the definition (seed_obo.py sanitisation gap).

No blockers. No instance-as-class, no wrong-axis, no broken identifiers. All 40 are CLASS-level with source-anchored CURIEs and correct axis/category; groundings (EC/Rhea/ChEBI/GO/parents/xrefs) and licenses are correct where present.
