---
layout: default
title: Biophysical sequence descriptors
---

The biophysical pilot adds continuous protein properties to the
[sequence map](map.html#sequences). Choose **Color by** to compare charge at a
stated pH, isoelectric point, residue fractions, charge patterning, mean
hydropathy, or compositional entropy. Minimum and maximum values filter the
selected descriptor; the existing organism-domain, CATH and length filters
remain available. The CSV includes numerical values and observation identifiers.

The cohort contains 256 reviewed proteins, selected across taxon, length and
source-release groups with exact sequence matches. Coverage is shown beside the
controls, and proteins without values are initially filtered out. The map's
positions still come from the existing sequence embeddings. A colored region
of the plot is exploratory evidence, not a demonstrated biological mechanism.

The underlying observation store also includes hydropathy profiles, candidate
hydrophobic-moment profiles and amino-acid composition vectors. Every result
identifies its exact protein sequence, scope, calculation method and parameters.
Whole-chain charge at pH 7 uses a sequence ionization model; it is not a surface
potential measurement. Local hydrophobic moments assume a stated geometry and
do not establish that a segment forms a helix.

The sequence bundle contains 3,072 observations, including disorder scores from
metapredict 3.0.2 (V3). The disorder fraction counts residues whose score is
strictly greater than 0.5. These are model predictions; they do not establish
experimentally observed disorder or independently validate the map's embeddings.

A separate [experimental collection](https://github.com/CultureBotAI/proteintraitsmech/blob/main/data/biophysical/experimental/README.md)
contains 14 published stability and solubility measurements on human ubiquitin
and mature hen egg-white lysozyme. Their construct mappings, pH, temperature,
assay and reporting gaps travel with each value. These measurements refer to
specific protein regions and conditions, so they are not whole-protein map colors.

The [implementation and reproduction guide](https://github.com/CultureBotAI/proteintraitsmech/blob/main/data/biophysical/README.md)
contains the method table, scope conventions, predictor-input contract and
commands. The [40-entry inventory](https://github.com/CultureBotAI/proteintraitsmech/blob/main/research/biophysical-traits-2026-09-23/inventory.tsv)
distinguishes the 12 pilot families from later additions and derived metadata.
The continuous observations reuse relevant ontology quality anchors without
turning each numerical value into a new trait class.

Follow-up work is tracked in [#753 (disorder predictions)](https://github.com/CultureBotAI/proteintraitsmech/issues/753),
[#754 (cohort expansion)](https://github.com/CultureBotAI/proteintraitsmech/issues/754),
and [#755 (remaining inventory)](https://github.com/CultureBotAI/proteintraitsmech/issues/755).
