# Experimental stability and solubility

This bounded slice of [#755](https://github.com/CultureBotAI/proteintraitsmech/issues/755),
tracked in [#793](https://github.com/CultureBotAI/proteintraitsmech/issues/793),
contains **14 observations for four descriptor families**, with source-qualified
construct mappings. The other roadmap entries remain open. Measurements use a
separate catalog and reference store; they do not create whole-protein map overlays,
new trait classes or canonical-example qualifications.

| Family | Construct / reference coordinates | Values | Conditions / assay |
|---|---|---|---|
| B25 thermal unfolding midpoint | Human ubiquitin / P0CG47 1–76 | 54.9, 56.9, 58.5, 64.2, 68.3, 73.3, 75.4, 78.6 °C | pH 1.8, 2.0, 2.2, 2.6, 2.8, 2.95, 3.05, 3.25 respectively; 15 µM; CD at 200 nm; 60 °C/h |
| B26 unfolding free energy | Human ubiquitin / P0CG47 1–76 | +26.16 kJ/mol | pH 2, 25 °C, 10 mM glycine/HCl; global three-state U–I–N fit, extrapolated to zero guanidinium chloride |
| B27 chemical-denaturation midpoint | Human ubiquitin / P0CG47 1–76 | 3.33 and 4.09 mol/L guanidinium chloride | pH 2 fluorescence and pH 5 CD respectively; 25 °C; 2 h equilibration |
| B30 equilibrium solubility | Mature hen egg-white lysozyme / P00698 19–147 | 3.68, 4.22, 2.30 g/L | 22.3, 23.6, 18.2 °C respectively; pH 4.6; 0.1 M sodium acetate; 4% w/v NaCl; tetragonal crystals |

## Source and construct decisions

[Crespo and Rubini (2011)](https://doi.org/10.1371/journal.pone.0019425) identifies
the wild-type recombinant human ubiquitin construct as a 76-residue chain, with
intact mass 8564.0 Da. Only its `wt-ub` results are imported; fluoroproline variants
are excluded. The exact canonical ubiquitin sequence is mapped to residues 1–76
of release-pinned P0CG47 as a coordinate reference. This does not identify the
genomic origin of the study construct, and the full polyubiquitin precursor is
not the measured sample.

The source's Table 2 free-energy value is **−26.16 kJ/mol** under its stated
`−RT ln(K_ui × k_in/k_ni)` convention, corresponding to G(native)−G(unfolded).
PTM defines B26 as G(unfolded)−G(native), so the importer explicitly negates that
value. The original number, formula, sign conversion, model and reference state
remain in each observation's method parameters. No value is inferred from Tm.

Lysozyme values are the three **Forsythe 1999** rows in Table 1 of
[Neugebauer et al. (2015)](https://doi.org/10.1021/cg501359h). The evidence chain
names the [original study](https://doi.org/10.1021/je980316a); its
[author abstract](https://ntrs.nasa.gov/citations/19990069901) describes the
miniature-column measurement and tetragonal crystals. The 2015 reactor outlet
concentrations are excluded. Study-named native hen egg-white material is mapped
to the reviewed UniProt mature chain, P00698 residues 19–147. The signal peptide
is excluded, and lot-specific sequence or PTM verification is not claimed.

Both references retain full and analyzed sequence hashes, sequence versions,
release IDs and exact inclusive region coordinates. The lysozyme reference comes
from the retained official UniProt response with captured `X-UniProt-Release`;
the ubiquitin reference is copied from the committed release-pinned registry.
The global registry and existing canonical-example ledger are unchanged.

## Conditions, uncertainty and interpretation

Tm has the source's estimated ±0.1 °C error; the source does not identify it as
SD or SE. Buffer/ionic strength and scan reversibility for that table are not
imputed from other assays. Chemical midpoints retain their differing pH and
readout. Complete solution composition and value-specific uncertainty are not
reported for those extracted values. Solubility records identify the crystalline
phase and salt concentration; total ionic strength is not equated with NaCl
concentration. Missing sample-lot, uncertainty and equilibration details remain
explicit reporting gaps. Values are neither pooled nor promoted into universal
protein adjectives.

The existing PATO solution-property routing through `STRUCT_SURFACE` is too broad
to establish these measurement semantics. These operational descriptors carry no
trait-axis assignment or surface-area assertion. Importing them therefore does
not extend that legacy route; ontology routing remains a separate review.

## Licensing and reproduction

The retained PLOS and ACS/Europe PMC article XML state Creative Commons
Attribution reuse terms; no version is asserted where the article does not give
one. Author, article and DOI attribution are preserved above and in the records.
UniProt sequences are attributed to the UniProt Consortium under CC BY 4.0.
This slice uses those openly licensed article snapshots, not a bulk FireProtDB
import whose separate terms require the disposition tracked in #517.

```bash
just import-biophysical-experiments          # preview
just import-biophysical-experiments --apply  # reproduce from retained XML
just check-biophysical-experiments          # exact source-table and schema replay
```

`observations.tsv` includes regions, units, pH, temperature, buffer, assay,
uncertainty and reporting gaps. JSONL retains the full provenance. `manifest.json`
binds every source, acquisition receipt, catalog and importer. Reviewed article
hashes are fixed in the importer; altered tables require explicit source review.
The CI check rejects changed measurements even if their content IDs are recomputed.
