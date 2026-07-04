# SEQUENCE_STRUCTURE + EVOLUTION — record sample review

## MIXED_COILED_COIL  (315 records; 5 sampled)
- data/traits/mixed/coiled_coil/pfam/t4ss-legc2c7-pf28175.yaml — minor: A4 boilerplate definition (label restated + "Pfam coiled-coil family <name> (PFxxxxx)"); A8 no sequence/structure representation slot. Otherwise well-formed CLASS, correct Pfam: CURIE, axis/category agree.
- data/traits/mixed/coiled_coil/pfam/tsc22-pf01166.yaml — minor: A4 boilerplate definition. Otherwise rich (pfam2go GO:0006357, InterPro xref, 3 canonical_examples). Good groundings.
- data/traits/mixed/coiled_coil/pfam/ccdc178-cc2-pf30876.yaml — minor: A4 boilerplate definition; A8 no representation slot.
- data/traits/mixed/coiled_coil/pfam/tnp-22-trimer-pf17489.yaml — minor: A4 boilerplate definition. InterPro xref + canonical example present.
- data/traits/mixed/coiled_coil/pfam/fez1-pf06818.yaml — minor: A4 boilerplate definition ("Fez1. Pfam coiled-coil family Fez1."); A3 terse cryptic label "Fez1". Canonical examples present.
- SET: PASS-with-caveats — consistent CLASS modelling, correct Pfam:/InterPro groundings, axis⇄category correct. Systemic weakness: every definition is seed_pfam.py boilerplate (restates label + family tag; no structural description of the coiled-coil trait), and no MIXED record carries the sequence/structure representation slot A8 expects (relies on InterPro/GO xrefs + canonical_examples instead). Coherent bucket.

## MIXED_STRUCTURAL_REPEAT  (122 records; 5 sampled)
- data/traits/sequence_structure/structural_repeat/repeatsdb/alpha-beta-prism-4-5.yaml — PASS. Genuine structural definition (triangular cross-section, helix+3-strand sheet units), parent RepeatsDB:4, PDB xref.
- data/traits/sequence_structure/structural_repeat/repeatsdb/alpha-beta-barrel-4-7.yaml — PASS. Genuine unit-topology definition, parent RepeatsDB:4, PDB xref.
- data/traits/sequence_structure/structural_repeat/repeatsdb/10-blade-propeller-4-4-7.yaml — minor: A4 boilerplate definition ("10-blade propeller — a RepeatsDB structural tandem-repeat fold (4.4.7). A structural tandem repeat with demonstrated 3D periodicity."), label restated + generic sentence. Deep-node with no source prose.
- data/traits/sequence_structure/structural_repeat/repeatsdb/beta-beads-5-2.yaml — PASS. Genuine definition (beta globular repetitive beads), parent RepeatsDB:5, PDB xref.
- data/traits/sequence_structure/structural_repeat/repeatsdb/dnase-4-1-1-5.yaml — minor: A4 boilerplate definition (deep clan node); A3 "DNase" (an enzyme name) used as a repeat-topology clan label; A9/B5 no PDB xref (others carry one).
- SET: PASS-with-caveats — correct CLASS, RepeatsDB: CURIEs, real same-axis parent_traits (numeric RepeatsDB nodes), axis⇄category correct. Definition quality bimodal: named topologies get genuine 3D descriptions, deeper numeric nodes (4.4.7, 4.1.1.5) fall back to seed_repeatsdb.py boilerplate. A8 structure representation slot unused (PDB xrefs stand in).

## EVO_CONSERVATION  (3 records; 3 sampled)
- data/traits/evolution/conservation/variable-protein.yaml — PASS. proteintraitsmech:EVO_VARIABLE, genuine definition, evolutionary_scope.conservation_metric populated, good synonyms.
- data/traits/evolution/conservation/clade-specific-protein.yaml — PASS. Genuine definition; evolutionary_scope present. Minor note: definition references "the NCBITaxon xref gives the clade" but a class record carries no xref (phrasing is instance-oriented) — not a flag.
- data/traits/evolution/conservation/conserved-protein.yaml — PASS. Genuine definition, evolutionary_scope present, diverse synonyms.
- SET: PASS — consistent, coherent, class-level. All three carry evolutionary_scope (A8 satisfied). Definitions genuinely distinct (conserved / variable / clade-specific span the retention gradient). Coherent post-collapse bucket.

## EVO_PANGENOME  (6 records; 5 sampled)
- data/traits/evolution/pangenome/core-genome-protein.yaml — PASS. Frequency band 0.99–1.0 + Roary definition_method; full evolutionary_scope.
- data/traits/evolution/pangenome/cloud-protein.yaml — PASS. Band 0.0–0.15, Roary method.
- data/traits/evolution/pangenome/persistent-genome-protein.yaml — PASS. PPanGGOLiN statistical partition (no numeric band, appropriately).
- data/traits/evolution/pangenome/singleton-protein.yaml — PASS. definition_method "present in exactly 1 genome".
- data/traits/evolution/pangenome/soft-core-protein.yaml — PASS. Band 0.95–0.99, Roary method. (Minor: 0.99 boundary touches core's min 0.99 — negligible.)
- SET: PASS — exemplary. Consistent CURIEs, genuine distinct definitions, every record carries a populated evolutionary_scope (min/max_prevalence + definition_method + conservation_metric). Bands tile the frequency axis coherently. Best-modelled category in this sweep.

## MIXED+EVOLUTION systemic issues (ranked)
1. **Pfam coiled-coil boilerplate definitions (seed_pfam.py)** — major-systemic across all 315 MIXED_COILED_COIL records: definition only restates the label + "Pfam coiled-coil family <name> (PFxxxxx)", giving no definitional content for a definition-governed KB. Fix at seeder (pull Pfam family free-text/InterPro description).
2. **RepeatsDB deep-node boilerplate definitions (seed_repeatsdb.py)** — minor-systemic: named topologies get real 3D descriptions but deeper numeric clan/fold nodes (4.4.7, 4.1.1.5, …) fall back to "<label> — a RepeatsDB structural tandem-repeat <fold/clan> (n.n.n). A structural tandem repeat with demonstrated 3D periodicity." Only affects nodes RepeatsDB provides no prose for.
3. **Directory inconsistency for the SEQUENCE_STRUCTURE axis** — coiled_coil lives under `data/traits/mixed/…` while structural_repeat lives under `data/traits/sequence_structure/…`; two path roots for one axis (CLAUDE.md prescribes `data/traits/<axis>/…`). Cosmetic but breaks the axis→dir convention.
4. **A8 representation-slot coverage gap on MIXED records** — neither coiled_coil nor structural_repeat records populate the sequence/structure representation slots the skill expects for these bridge categories; they rely on InterPro/GO/PDB xrefs and canonical_examples instead. Consistent, but the intended representation slots are empty corpus-wide.
5. **EVOLUTION axis is the positive model** — no issues: 2-category collapse (EVO_CONSERVATION vs EVO_PANGENOME) is coherent (cross-taxon retention vs within-species frequency partition), every EVO record carries a populated evolutionary_scope, and definitions are genuine and diverse. seed_evolution.py output needs no remediation.
