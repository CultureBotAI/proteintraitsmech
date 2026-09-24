PTMech should expand its support for biophysical protein properties. The most useful change is to connect reusable property concepts to **quantitative, scoped, condition-qualified observations**, then fill selected vocabulary gaps. Positive charge, negative charge, hydrophobicity, and solubility already have records. A large new list of adjectives would add less value than making those concepts computable, measurable, and interpretable.

This assessment was prepared on **2026-09-23** from the current local worktree and primary scientific papers or official method documentation. The local audit includes gitignored files. It describes this worktree, not a separately verified remote branch. The accompanying [inventory](inventory.tsv) contains **40 descriptor concepts in nine families**, including **12 recommended pilot descriptors**. That is an explicit proposed inventory, not a claim that biology has exactly 40 independent biophysical traits.

**The requested examples are partly covered already.** The reproducible [audit](audit.json), produced by [audit_existing.py](audit_existing.py), found 429,291 YAML files under `data/traits/`. Of these, 35 are PATO imports:

| Existing PATO family | Records | Examples |
|---|---:|---|
| Electric charge | 4 | electric charge; positive; negative; neutral |
| Hydrophobicity | 2 | hydrophobicity; hydrophobic |
| Solubility | 7 | solubility; soluble in; insoluble in; increased/decreased/normal solubility; dissolved |
| Stability | 3 | stability; increased; decreased |
| Flexibility | 6 | flexibility; flexible/inflexible; increased/decreased/normal |
| Elasticity | 6 | elasticity; elastic/inelastic; increased/decreased/normal |
| Generic hierarchy scaffolding | 7 | physical quality; molecular quality; structure; other broad ancestors |
| **Total** | **35** | **28 property-oriented records plus seven broad ancestors** |

These records cover six broad property families. There are also **33 condition-specific stability records**, generated as 11 stressor contexts with three labels per context. They include thermal, acidic, alkaline, saline, oxidative, proteolytic, mechanical, pressure, osmotic, desiccation, and chemical-denaturant conditions. Therefore, 35 + 33 = 68 related records does not mean 68 independent physical properties. The count includes ancestors, qualitative states, and condition combinations. See the [PATO import routes](../../scripts/seed_obo.py) and [stability seeder](../../scripts/seed_stability.py).

All 68 records have `mapping_status: SEEDED`; their `canonical_examples`, `evidence`, and `detection_methods` lists are absent or empty in this audit. They do retain definition/source attribution. Their presence establishes vocabulary coverage, not a set of protein-level measurements or reviewed exemplar assignments.

The existing [positive-charge record](../../data/traits/structure/surface/pato/positive-charge-pato0002195.yaml) is `PATO:0002195`; negative charge is `PATO:0002196`, neutral charge `PATO:0002194`, and the electric-charge quality `PATO:0002193`. Hydrophobicity and hydrophobic are `PATO:0001884` and `PATO:0001885`.

**Hydrophilicity is a small, concrete import gap.** The repository's downloaded [PATO release](../../data/raw/PATO.obo), dated 2025-05-14, already includes `PATO:0001886` (hydrophilicity) and `PATO:0001887` (hydrophilic). Neither exact label appears as a record in the complete ignored-file-inclusive search. The importer selects the hydrophobicity root but not the hydrophilicity root; they are sibling branches. Reuse those identifiers when adding the missing vocabulary. The same pinned ontology contains molecular polarity (`PATO:0002186`) and polar/nonpolar states (`PATO:0002187/0002188`). Their scope needs review before reuse: a count of polar residues is not the same thing as the dipole of an entire molecule. `PATO:0002420` (amphiphilic) has an anatomical-histological parent in this release, so its appealing label alone is insufficient for an automatic exact mapping to a protein hydrophobic-moment descriptor.

The schema defines `SEQ_COMPOSITION` and `SEQ_LOW_COMPLEXITY`, but this audit found **zero root trait records** in either category. It found 202 `SEQ_DISORDER` root records. These are record counts, not counts of nested UniProt features: a `COMPBIAS` feature on a protein does not by itself instantiate a general PTMech trait class. Searches were limited to the stated category values and exact generic labels; a lack of an exact label is not proof that no family-specific record has related biology.

**There is no single natural total for “how many biophysical traits.”** A useful count must distinguish four levels:

1. A property concept, such as electric charge or water affinity.
2. A qualitative state, such as positively charged at a specified pH.
3. An operational descriptor or measurement, such as a calculated charge, a hydropathy score, or a measured solubility.
4. A method, scale, threshold, or experimental condition used to obtain that descriptor.

Positive and negative charge are states of one signed property. Hydrophobic and hydrophilic describe opposing tendencies in water affinity, but published hydrophobicity/hydrophilicity scales are not all numerical sign reversals of one another. PTMech can retain distinct ontology quality classes without treating every scale or adjective as an independent physical dimension.

For scale, the official **AAindex release 9.2 documentation lists 566 amino-acid indices, 94 substitution matrices, and 47 contact-potential matrices**. The 566 indices are sets of residue-level values, often correlated and measuring related properties; they are not 566 independent whole-protein trait classes. The database explicitly records correlations between indices. [AAindex documentation](https://www.genome.jp/aaindex/aaindex_help.html)

For planning, **roughly 30–50 commonly useful descriptor concepts** is a defensible starting scope. That range is this assessment's design judgment, illustrated by the following explicit 40-entry inventory; it is not a literature census or an upper bound. More specialized photophysics, mechanics, membrane systems, redox centers, and environmental dependencies can extend it substantially. Binning values into high/low/positive/negative classes multiplies labels without adding the same number of independent properties.

| Family | Inventory entries | Representative properties | Main evidence route |
|---|---:|---|---|
| Electrostatics and ionization | 7 | charge at pH; pI; charged-residue fractions; charge patterning; surface potential | Sequence titration models, structural electrostatics, experiments |
| Water and membrane affinity | 5 | mean/local hydropathy; amphipathicity; exposed hydrophobic area; membrane transfer energy | Named sequence scales, 3-D surfaces, partition experiments |
| Composition and heterogeneity | 4 | amino-acid composition; aromatic/polar fractions; complexity | Sequence calculation |
| Size and shape | 4 | length; mass; radius of gyration; hydrodynamic radius | Sequence metadata, structures/ensembles, solution experiments |
| Conformation and dynamics | 4 | secondary-structure content; disorder; mobility; compactness | Structure assignment, prediction, ensemble/dynamics experiments |
| Stability and folding | 5 | Tm; unfolding free energy; denaturant midpoint; folding/unfolding rates | Defined thermodynamic and kinetic experiments |
| Solution and assembly | 6 | solubility; aggregation; amyloid formation; self-association; phase separation; oligomeric state | Concentration- and condition-qualified assays |
| Reactivity and mechanics | 3 | proteolytic resistance; redox potential; mechanical unfolding force | Specialized experiments |
| Optical properties | 2 | absorption coefficient; fluorescence quantum yield | Sequence estimates where valid and spectroscopy |
| **Total** | **40** | **Descriptor concepts, not 40 independent axes or 40 proposed new YAML classes** | |

The [TSV inventory](inventory.tsv) gives a primary source, evidence mode, scope, conditions, existing PTMech overlap, and recommendation for every row. Some entries are deliberately families of operational observables: an aggregation score, aggregation lag time, and aggregation rate must remain different quantities within their family. The 20-component amino-acid composition vector is counted as one descriptor concept, not 20 trait classes.

**Charge, hydropathy, and solubility require different definitions.** For protein charge, the subject must be a specified sequence/proteoform or region, and the result must state pH and ionization assumptions. A sequence titration calculation depends on the pKa set, terminal groups, and titratable residues. It does not automatically account for modifications, ligands, or structure-dependent pKa shifts. Biopython exposes both pI and charge-at-pH calculations; structural pKa modeling is a separate method family. [Biopython API](https://biopython.org/docs/latest/api/Bio.SeqUtils.ProtParam.html), [PROPKA3](https://pubmed.ncbi.nlm.nih.gov/26596171/)

Under the common K/R/D/E compositional convention, `f+ = (K+R)/L`, `f- = (D+E)/L`, `FCR = f+ + f-`, and signed compositional `NCPR = f+ - f-`. This convention is not identical to a full pH-dependent charge calculation that includes histidine, other titratable groups, and termini. Equal positive and negative residue counts can give zero compositional net charge while retaining many charged residues. Charge ordering supplies additional information: a block of positive residues followed by a block of negative residues differs from an alternating sequence even when composition is identical. Das and Pappu demonstrated effects of charge patterning on disordered-chain ensembles; localCIDER provides explicit definitions and calculations. These results should not be generalized into a universal folded-protein classification without validation. [Primary study](https://pubmed.ncbi.nlm.nih.gov/23901099/), [localCIDER methods](https://pappulab.github.io/localCIDER/)

A whole-chain mean hydropathy score can conceal a hydrophobic transmembrane segment or a short hydrophilic region. A local profile needs a scale and window definition. Amphipathicity adds arrangement information: the hydrophobic moment describes whether hydrophobic residues preferentially face one side of an assumed helix or other specified geometry. Experiments have varied peptide amphiphilicity while keeping total hydrophobicity fixed, demonstrating that these descriptors are not interchangeable. [Hydrophobic moment](https://pubmed.ncbi.nlm.nih.gov/7110359/), [membrane-partition experiment](https://pubmed.ncbi.nlm.nih.gov/17532340/)

Hydrophilicity is not a sufficient solubility measurement. Solubility concerns a defined construct in a solvent under specified conditions; sequence and structural features can support predictions, but model outputs should retain their identity as scores. Primary solubility studies explicitly consider pH and ionic strength and distinguish models from experimental outcomes. [CamSol study](https://pubmed.ncbi.nlm.nih.gov/25451785/), [pH-dependent solubility models](https://pmc.ncbi.nlm.nih.gov/articles/PMC8996476/)

Likewise, experimental Tm, unfolding free energy, and folding/unfolding rates are different observables. ProThermDB records several thermodynamic quantities together with conditions, while PFDB treats folding kinetics and temperature normalization. A sequence “instability index” should not be relabeled as measured thermodynamic stability. [ProThermDB](https://pubmed.ncbi.nlm.nih.gov/33196841/), [PFDB](https://pmc.ncbi.nlm.nih.gov/articles/PMC6367381/), [ProtParam definitions](https://web.expasy.org/protparam/protparam-doc.html)

Specialized properties can be valuable when their bearers and assays are clear. Titin mechanical-unfolding forces depend on pulling speed; redox potential belongs to a specified redox center/couple; phase separation involves a construct in a defined mixture, often including partners. Those facts argue for qualified observations rather than unconditional protein labels. [Titin experiment](https://pubmed.ncbi.nlm.nih.gov/9148804/), [thioredoxin redox experiment](https://pubmed.ncbi.nlm.nih.gov/12816947/), [PhaSePro](https://pubmed.ncbi.nlm.nih.gov/31612960/)

**The benefit to PTMech is substantial if class definitions and protein observations stay separate.** These properties provide interpretable comparisons across protein families and sources, connect sequence/structure to mechanisms, and support useful questions such as whether an exposed charged patch or amphipathic segment explains a binding behavior. They can also supply interpretable overlays for the sequence map. Correlation with a cloud or source collection would be a hypothesis-generating observation, not proof of the mechanism causing that map structure.

The present [schema](../../src/proteintraitsmech/schema/proteintraitsmech.yaml) already supplies protein references, exact sequence hashes, localized/whole-protein occurrences, evidence citations, detection-method descriptions, and structural representations. It does **not** provide a general typed biophysical observation carrying a numerical value, unit, experimental conditions, uncertainty, and calculation provenance on those protein/occurrence objects. `EvidenceItem` has reference/snippet/notes, and `DetectionMethod` describes a recipe; neither stores the result of a run. Putting all values in prose would prevent reliable comparison and filtering.

Retain the PATO imports as quality **classes**. Do not convert a PATO class into a datatype property just because it can be quantified. A proposed separate `BiophysicalObservation` model should link a protein or localized occurrence to a property/descriptor definition and carry:

- Subject accession, sequence hash/version, proteoform or mature-chain definition, scope, and residue coordinates where applicable.
- Descriptor identity, numerical value/profile/category, unit, scale, normalization, and explicit missing/undefined status.
- Evidence mode: direct experimental observation, sequence calculation, structure calculation, or model prediction.
- Method and version, parameter set, pKa/AAindex scale identifiers where applicable, and structural model/chain/conformer provenance.
- Relevant conditions: pH, temperature, buffer/ionic strength, concentration, solvent, redox state, partners, ligands, and assay-specific factors.
- Source evidence, uncertainty, and a comparator/baseline for claims such as “increased,” “decreased,” or “normal.”

This is a design recommendation, not an existing schema-valid object. Changes to the closed schema and validation would precede production observations. An illustration is “calculated net charge of this exact unmodified chain at pH 7 using this pKa set”; a blanket “this protein is positively charged” omits the information that makes the claim reproducible. A sign close to zero also needs an explicit tolerance or uncertainty policy before a categorical assignment.

Biophysical properties cut across the current axes, so a sixth `BIOPHYSICAL` axis is not necessary for the pilot. Use a cross-cutting property family and keep calculation/evidence provenance distinct. Composition-defined classes fit `SEQ_COMPOSITION`; actual surface descriptors fit `STRUCT_SURFACE`; stability and dynamics can reuse their existing categories. A whole-protein solution property should not be forced into `STRUCT_SURFACE` merely because that is where the PATO importer put it. Typed protein observations can be piloted without pretending that every numerical output requires a new axis-bound class. Any later general physicochemical category needs an explicit scope and corresponding schema/routing review. An [earlier repository review](../record-sample-review-1-appendix-structure.md) independently flagged the current surface-category use as too broad.

**Start with 12 descriptor families, reusing existing classes wherever they fit.** The pilot rows are B01–B06, B08–B10, B13, B16, and B22:

| Pilot group | Descriptor families |
|---|---|
| Charge and composition of charge | Q(pH); pI; f(K+R); f(D+E); FCR; charge patterning |
| Water affinity and arrangement | Mean hydropathy; local hydropathy profile; hydrophobic moment |
| Broader sequence characterization | Amino-acid composition; complexity; predicted disordered fraction/segments |

Counts/fractions, charge estimates, and profiles can use documented local algorithms. Kappa or another patterning metric needs its defined applicability and undefined-case behavior. Hydrophobic moment needs an explicit geometry assumption. Disorder requires a named predictor and threshold rather than simply counting “disorder-promoting” residues. IUPred documents context-sensitive disorder prediction; observed disorder remains a separate evidence mode. [localCIDER](https://pappulab.github.io/localCIDER/), [IUPred](https://iupred3.elte.hu/)

For a reproducible first application, choose a stated reference pH such as 7.0, retaining the ability to calculate a pH curve; do not call one pH universally physiological. Pin a hydropathy scale rather than mixing outputs from differently normalized scales. Keep precursor, mature-chain, and region calculations distinguishable. Masked or nonstandard residues need a declared handling policy. Use continuous values for plots and filters first; reserve class thresholds for externally justified or explicitly dataset-relative definitions.

The remaining inventory comprises **19 later additions/enrichments**, **five derived-metadata descriptors**, and **four specialized descriptors**. Structure-dependent priorities include exposed hydrophobic area and surface electrostatics. Experimental priorities include solubility and stability observations linked to existing terms. Optical, redox, and mechanical branches should follow concrete use cases. Length and composition-derived summaries should not generate a proliferation of arbitrary trait classes.

A useful pilot would verify algorithm outputs against documented examples, preserve record/protein provenance, and examine redundancy among descriptors before using them together in a distance metric. It would add color/filter overlays to the existing sequence map, examine associations within source and length strata, and avoid interpreting an ESM-derived property predictor as independent validation of the same ESM embedding. That pilot is a proposed follow-on, not an analysis already performed in this assessment.

**The adoption recommendation is a focused extension:** enrich the existing charge, hydrophobicity, solubility, stability, and dynamics concepts; add the two missing PATO hydrophilicity terms after routing review; introduce typed descriptor observations; and begin with the 12-family sequence pilot. Keep the broader 40-entry inventory as a prioritized roadmap. The research supports adding usable biophysical information to PTMech, with substantially more emphasis on definitions, scope, evidence, and values than on increasing the number of names.

Reproduce the local evidence audit with `python research/biophysical-traits-2026-09-23/audit_existing.py` in an environment with PyYAML. It reads the worktree and regenerates only `audit.json`. The assessment and inventory are research artifacts; this work did not add trait records, modify the schema, or run a protein-annotation pipeline.
