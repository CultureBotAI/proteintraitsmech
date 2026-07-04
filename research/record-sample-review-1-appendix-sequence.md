# SEQUENCE axis — record sample review

## SEQ_CLEAVAGE_SITE  (11 records; 5 sampled)
- data/traits/sequence/cleavage_site/elm/clv-separin-metazoa-elme000331.yaml — PASS
- data/traits/sequence/cleavage_site/elm/clv-taspase1-elme000192.yaml — PASS
- data/traits/sequence/cleavage_site/elm/clv-pcsk-ski1-1-elme000146.yaml — PASS
- data/traits/sequence/cleavage_site/elm/clv-nrd-nrd-1-elme000102.yaml — PASS
- data/traits/sequence/cleavage_site/elm/clv-pcsk-pc7-1-elme000103.yaml — PASS
- SET: PASS — consistent ELM shape; real defs, sequence_pattern, per-protein instances kept in canonical_examples (not as classes), license present. Exemplary.

## SEQ_CONSERVATION  (775 records; 5 sampled)
- data/traits/sequence/conservation/interpro/air2-like-cchc-type-1-zinc-finger-4-ipr049024.yaml — PASS
- data/traits/sequence/conservation/interpro/terpene-synthase-conserved-site-ipr002365.yaml — minor: A4 stripped-citation `( )` artifacts (EC numbers removed leaving empty parens)
- data/traits/sequence/conservation/interpro/alcohol-dehydrogenase-iron-type-conserved-site-ipr018211.yaml — minor: A4 stripped-citation `( )` artifacts
- data/traits/sequence/conservation/interpro/flagellar-motor-protein-mota-conserved-site-ipr000540.yaml — PASS
- data/traits/sequence/conservation/interpro/urocanase-conserved-site-ipr023636.yaml — PASS
- SET: PASS — consistent InterPro shape, rich real defs, interpro2go mapped_xrefs. Systemic minor: seed_interpro.py leaves `( )` where EC/citations were stripped.

## SEQ_CROSSLINK_SITE  (69 records; 5 sampled)
- data/traits/sequence/crosslink/o-l-isoaspartyl-l-threonine-cross-link-mod01947.yaml — PASS
- data/traits/sequence/crosslink/3-3-5-5-tertyr-crosslink-mod00959.yaml — MAJOR: A4 placeholder def "modification from DeltaMass"; junk xref `DeltaMass:0`
- data/traits/sequence/crosslink/pyrrolidione-ring-crosslinked-residues-mod01943.yaml — PASS
- data/traits/sequence/crosslink/crosslinked-l-cysteine-residue-mod02044.yaml — PASS
- data/traits/sequence/crosslink/crosslinked-d-asparagine-residue-mod02060.yaml — PASS
- SET: PASS (4/5) — consistent PSI-MOD shape, MOD-CURIE parent_traits, PMID xrefs. One placeholder-def record where PSI-MOD imports from DeltaMass without def text (seed_psimod.py).

## SEQ_DISORDER  (202 records; 5 sampled)
- data/traits/sequence/disorder/methylation-display-site-idpo-0000042.yaml — PASS (rich IDPO class, curator instances)
- data/traits/sequence/disorder/pfam/aim21-pf11489.yaml — MAJOR: A4 boilerplate def (label restated + "Pfam disordered family X")
- data/traits/sequence/disorder/pfam/asr-pf06392.yaml — MAJOR: A4 boilerplate def
- data/traits/sequence/disorder/pfam/mac-assoc-pf16628.yaml — MAJOR: A4 boilerplate def
- data/traits/sequence/disorder/pfam/mfa1-pf17445.yaml — MAJOR: A4 boilerplate def
- SET: MAJOR (systemic) — 4/5 Pfam records share identical boilerplate definition template; seed_pfam.py does not pull the Pfam family description text (B4/B6). IDPO record is the good counter-example.

## SEQ_DOMAIN  (88742 records; 5 sampled)
- data/traits/sequence/domain/interpro/resp18-domain-ipr029403.yaml — PASS
- data/traits/sequence/domain/interpro/domain-of-unknown-function-duf5619-ipr041145.yaml — PASS
- data/traits/sequence/domain/ncbifam/big-3-4-nf025129.yaml — MAJOR: A4 thin boilerplate def ("PF13754 domain-containing protein — an NCBIfam family…"); does not define trait
- data/traits/sequence/domain/cdd/rna-recognition-motif-2-rrm2-found-in-hiv-tat-specific-factor-1-tat-sf-cd12282.yaml — MAJOR: A3 label is the ENTIRE description paragraph (short name "RRM2_TatSF1_like" is only in synonyms); def restates it + boilerplate
- data/traits/sequence/domain/interpro/x-tfes-xvipcd-ipr046519.yaml — PASS
- SET: mixed — InterPro records good; CDD label bug (paragraph-as-label) and NCBIfam thin defs are systemic seeder defects across the largest category in the corpus.

## SEQ_FAMILY  (14424 records; 5 sampled)
- data/traits/sequence/family/pfam/duf627-pf04781.yaml — MAJOR: A4 boilerplate def with "Pfam family family" double-word typo
- data/traits/sequence/family/pfam/duf6326-pf19851.yaml — MAJOR: A4 boilerplate def + "family family" typo
- data/traits/sequence/family/pfam/pac1-pf16094.yaml — MAJOR: A4 boilerplate def + "family family" typo (else well-grounded: pfam2go, clan parent)
- data/traits/sequence/family/prosite/carboxylesterases-type-b-signature-pdoc00112.yaml — minor: thin def (describes it as a PROSITE doc group), acceptable
- data/traits/sequence/family/pfam/duf1392-pf07154.yaml — MAJOR: A4 boilerplate def + "family family" typo
- SET: MAJOR (systemic) — 4/5 Pfam records boilerplate defs with template typo "Pfam family family"; seed_pfam.py bug affecting 14k-record category.

## SEQ_GLYCOSYLATION_SITE  (85 records; 5 sampled)
- data/traits/sequence/glycosylation/hex3hexnac2p1-n4-glycosylated-asparagine-mod00529.yaml — MAJOR: A4 placeholder def "modification from Unimod N-linked glycosylation"
- data/traits/sequence/glycosylation/glycosylated-residue-mod00693.yaml — PASS
- data/traits/sequence/glycosylation/asn-glycosylation.yaml — minor: A4 def restates label "N-glycosylation site"; A9 no license field (other PROSITE records have one). Good: sequence_pattern present
- data/traits/sequence/glycosylation/o-n-acetylamino-fucosyl-l-serine-mod00834.yaml — PASS
- data/traits/sequence/glycosylation/monomannosylated-residue-mod00595.yaml — PASS
- SET: PASS (mostly) — MOD + PROSITE mixed but coherent (all glycosylation sites). One PSI-MOD placeholder def; PROSITE record missing license.

## SEQ_HOMOLOGOUS_SUPERFAMILY  (5699 records; 5 sampled)
- data/traits/sequence/homologous_superfamily/interpro/abc-transporter-type-1-transmembrane-domain-superfamily-ipr036640.yaml — minor: A4 def truncated with trailing "…" (import truncation)
- data/traits/sequence/homologous_superfamily/cdd/n-a-a-dimer-of-the-beta-subunit-of-dna-polymerase-beta-forms-a-ring-wh-cl42470.yaml — MAJOR: A3 label is "N/A. <full sentence>" (short name "beta_clamp" only in synonyms)
- data/traits/sequence/homologous_superfamily/interpro/atg6-beclin-c-terminal-domain-superfamily-ipr038274.yaml — PASS
- data/traits/sequence/homologous_superfamily/cdd/n-a-this-fibronectin-type-iii-domain-is-found-in-fungal-chitin-biosynt-cl21522.yaml — MAJOR: A3 label is "N/A. <full sentence>" (short name "FN3" only in synonyms)
- data/traits/sequence/homologous_superfamily/interpro/cucumovirus-coat-protein-subunit-a-superfamily-ipr037137.yaml — PASS
- SET: mixed — InterPro good (one truncated def); CDD "N/A. <sentence>"-as-label bug recurs (same seed_cdd.py defect as SEQ_DOMAIN).

## SEQ_INITIATOR_METHIONINE  (1 record; 1 sampled)
- data/traits/sequence/initiator_methionine/uniprot-seq_initiator_methionine.yaml — PASS (exemplary: proteintraitsmech: FT class, real def, per-protein instances in canonical_examples)
- SET: PASS — singleton UniProt-FT class, correct instance/class separation.

## SEQ_LEADER_PEPTIDE  (20 records; 5 sampled)
- data/traits/sequence/leader_peptide/proteusin-leader.yaml — PASS
- data/traits/sequence/leader_peptide/sactipeptide-leader.yaml — PASS
- data/traits/sequence/leader_peptide/linear-azol-in-e-containing-peptide-leader.yaml — PASS
- data/traits/sequence/leader_peptide/head-to-tail-cyclized-bacteriocin-leader.yaml — PASS
- data/traits/sequence/leader_peptide/lasso-peptide-leader.yaml — PASS
- SET: PASS — curated RiPP-class taxonomy, distinct real defs per class, curator-minted proteintraitsmech: IDs. Exemplary hand-curation.

## SEQ_LIPIDATION_SITE  (40 records; 5 sampled)
- data/traits/sequence/lipidation/s-palmitoyl-l-cysteine-mod00115.yaml — PASS (minor: `DeltaMass:0` placeholder xref)
- data/traits/sequence/lipidation/s-farnesyl-l-cysteine-methyl-ester-mod01116.yaml — PASS
- data/traits/sequence/lipidation/s-geranylgeranyl-l-cysteine-mod00113.yaml — PASS (minor: `DeltaMass:0` xref)
- data/traits/sequence/lipidation/farnesylated-residue-mod00437.yaml — PASS (minor: `DeltaMass:0` xref)
- data/traits/sequence/lipidation/isoprenylated-tryptophan-mod01115.yaml — PASS
- SET: PASS — consistent PSI-MOD shape, real defs, MOD hierarchy. Minor systemic `DeltaMass:0` junk xrefs.

## SEQ_MATURE_CHAIN  (1 record; 1 sampled)
- data/traits/sequence/mature_chain/uniprot-seq_mature_chain.yaml — PASS (exemplary UniProt-FT class)
- SET: PASS — singleton, correct instance/class separation.

## SEQ_MODIFIED_RESIDUE  (618 records; 5 sampled)
- data/traits/sequence/modified_residue/n-acetylaminohexosylated-residue-mod01673.yaml — PASS
- data/traits/sequence/modified_residue/n-methylated-proline-mod01462.yaml — PASS
- data/traits/sequence/modified_residue/n-formylated-residue-mod00409.yaml — PASS
- data/traits/sequence/modified_residue/nitrosylated-residue-mod02077.yaml — PASS
- data/traits/sequence/modified_residue/methylthiolated-residue-mod01153.yaml — PASS
- SET: PASS — clean PSI-MOD; real defs, MOD parent hierarchy, PMID/Unimod xrefs.

## SEQ_MOTIF  (3121 records; 5 sampled)
- data/traits/sequence/profile/lon-proteolytic.yaml — minor: A4 def restates label; A9 no license; borderline A5 ("domain profile" arguably SEQ_DOMAIN)
- data/traits/sequence/pattern/prpp-synthase.yaml — minor: A4 def restates label; A9 no license (good: sequence_pattern + examples)
- data/traits/sequence/pattern/dna-photolyases-1-2.yaml — minor: A4 def restates label; A9 no license (good: sequence_pattern)
- data/traits/sequence/profile/sant.yaml — minor: A4 def restates label; A9 no license; borderline A5 ("domain profile")
- data/traits/sequence/motif/elm/doc-usp7-math-2-elme000240.yaml — PASS
- SET: minor (systemic) — PROSITE pattern/profile records: seed_prosite.py copies the .prf name to both label and definition (no PDOC description pulled) and omits license. ELM record is the good counter-example.

## SEQ_PROPEPTIDE  (1 record; 1 sampled)
- data/traits/sequence/propeptide/uniprot-seq_propeptide.yaml — PASS (exemplary UniProt-FT class)
- SET: PASS — singleton, correct instance/class separation.

## SEQ_PTM_SITE  (1251 records; 5 sampled)
- data/traits/sequence/ptm_ontology/flavin-modified-residue-mod00697.yaml — PASS
- data/traits/sequence/ptm_ontology/ribosylated-residue-mod00731.yaml — PASS
- data/traits/sequence/ptm_ontology/l-methionine-removal-mod01643.yaml — PASS
- data/traits/sequence/ptm_site/elm/mod-prodkin-1-elme000159.yaml — PASS
- data/traits/sequence/ptm_ontology/glucosylated-residue-mod00726.yaml — PASS
- SET: PASS — MOD + ELM mixed but coherent. Minor: SEQ_PTM_SITE / SEQ_MODIFIED_RESIDUE / SEQ_GLYCOSYLATION_SITE overlap conceptually (glucosylated/ribosylated could be glycosylation) — a PSI-MOD-routing granularity question, not a per-record defect.

## SEQ_REPEAT  (2073 records; 5 sampled)
- data/traits/sequence/repeat/interpro/bacteriophage-lambda-tail-fiber-protein-repeat-1-ipr005003.yaml — PASS
- data/traits/sequence/repeat/interpro/hemagglutinin-repeat-ipr025157.yaml — PASS
- data/traits/sequence/repeat/pfam/duf285-pf03382.yaml — MAJOR: A4 boilerplate def (label restated + "Pfam repeat family X")
- data/traits/sequence/repeat/pfam/gbp-repeat-pf02526.yaml — MAJOR: A4 boilerplate def
- data/traits/sequence/repeat/pfam/duf6109-pf19604.yaml — MAJOR: A4 boilerplate def
- SET: mixed — InterPro real defs; 3/5 Pfam boilerplate (same seed_pfam.py defect). Sources otherwise consistent/coherent (all repeats).

## SEQ_SIGNAL_PEPTIDE  (1 record; 1 sampled)
- data/traits/sequence/signal_peptide/uniprot-seq_signal_peptide.yaml — PASS (exemplary UniProt-FT class)
- SET: PASS — singleton, correct instance/class separation.

## SEQ_TARGETING_SIGNAL  (28 records; 5 sampled)
- data/traits/sequence/targeting_signal/elm/trg-dileu-baen-4-elme000526.yaml — PASS
- data/traits/sequence/targeting_signal/elm/trg-dileu-balyen-6-elme000528.yaml — PASS
- data/traits/sequence/targeting_signal/elm/trg-nls-bipartite-1-elme000276.yaml — PASS
- data/traits/sequence/targeting_signal/elm/trg-nes-crm1-1-elme000193.yaml — PASS
- data/traits/sequence/targeting_signal/elm/trg-dileu-baen-1-elme000523.yaml — PASS
- SET: PASS — consistent ELM; real per-variant defs, sequence_pattern, examples, license. Three DiLeu records share a synonym but defs are appropriately distinct.

## SEQ_TRANSIT_PEPTIDE  (1 record; 1 sampled)
- data/traits/sequence/transit_peptide/uniprot-seq_transit_peptide.yaml — PASS (exemplary UniProt-FT class)
- SET: PASS — singleton, correct instance/class separation.

## SEQUENCE systemic issues
(ranked by blast radius)

1. **seed_pfam.py — boilerplate definitions (MAJOR, ~17k+ records).** Every Pfam record's definition is `"<label>. Pfam <disordered|repeat|family> family <NAME> (Pfam:PFxxxxx)."` — the label restated plus a template tail; the actual Pfam family description text is never pulled. Includes a literal template typo **"Pfam family family"** in SEQ_FAMILY. Hits SEQ_FAMILY (14424), plus the Pfam subsets of SEQ_DOMAIN, SEQ_REPEAT (2073), and SEQ_DISORDER (202). Largest-impact defect on the axis. (Note: DUF families have little to define, but the template + typo apply to all Pfam records, incl. named families like PAC1.)

2. **seed_cdd.py — label = full description paragraph / "N/A." prefix (MAJOR).** CDD records put the entire curated description sentence(s) into `label` (e.g. "N/A. A dimer of the beta subunit…"), while the real short name (RRM2_TatSF1_like, beta_clamp, FN3) sits only in `synonyms`. The definition then restates that paragraph + boilerplate tail. Class labels are unusable for display/identity. Hits CDD records in SEQ_DOMAIN and SEQ_HOMOLOGOUS_SUPERFAMILY (5699).

3. **seed_prosite.py — definition restates label + missing license (minor→major).** PROSITE pattern/profile records copy the .prf name into both `label` and `definition` (the PDOC description text is not pulled) and omit the `license` field that PROSITE PDOC (family) records carry. Hits SEQ_MOTIF (3121) and the PROSITE entries in SEQ_GLYCOSYLATION_SITE. Some domain-scale PROSITE profiles ("Lon proteolytic domain profile", "SANT domain profile") also sit in SEQ_MOTIF (borderline SEQ_DOMAIN).

4. **seed_psimod.py — placeholder definitions + junk xrefs (minor→major, small subset).** MOD terms that PSI-MOD imported from DeltaMass/Unimod without def text get `"modification from DeltaMass"` / `"modification from Unimod …"` as the definition (e.g. MOD:00959, MOD:00529). Separately, many MOD records carry a placeholder `DeltaMass:0` xref. Most PSI-MOD records (modified_residue, lipidation, ptm_site) have proper real definitions — this affects only the import-stub minority.

5. **seed_ncbifam.py — thin boilerplate definitions (minor→major).** NCBIfam records read `"<X> domain-containing protein — an NCBIfam protein family (NFxxxxx, domain); members share this conserved family signature."` — no real definition of the trait. SEQ_DOMAIN subset.

6. **seed_interpro.py — stripped-citation `( )` and truncation artifacts (minor).** InterPro defs (otherwise the richest in the axis) show empty `( )` where EC numbers/citations were removed, and occasional trailing "…" truncation on long entries. Hits SEQ_CONSERVATION, SEQ_DOMAIN, SEQ_HOMOLOGOUS_SUPERFAMILY.

No blocker-severity records found (all validate; identifiers/axis/category correct; no instance-as-class). The CDD label defect (#2) is the closest to identity-breaking but each such record retains a correct CURIE identifier and the real name in synonyms, so it is graded MAJOR.
