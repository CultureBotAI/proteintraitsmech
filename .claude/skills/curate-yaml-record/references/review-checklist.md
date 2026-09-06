# ProteinTraitRecord review checklist

Use this checklist for one protein trait. It does not require every optional
representation or a causal graph.

## Evidence standard

- Source-native database entries establish their own accession and release
  assertions; literature establishes only the claims actually tested.
- Attach evidence separately to definitions, examples, relations, residues,
  participants, and causal edges.
- A prediction, sequence hit, structure model, or co-membership relation is not
  direct functional or mechanistic evidence.
- Confirm DOI/PMID/accession identity, protein form, taxon, construct, residue
  frame, and source version.
- Preserve conflicts and describe negative searches as bounded “not found.”

## Field-by-field audit

| Area | Verify | Complete enough when |
|---|---|---|
| Identity | Identifier, label, synonyms, source/release, and license denote one class-level trait. | Instance, family, domain, motif, function, and structural-class boundaries are explicit. |
| Axis/category | Axis follows representation and category matches the schema vocabulary. | Placement is justified by the record's defining evidence, not biology alone. |
| Definition | Definition/source and alternate source definitions are accurate and scoped. | Source wording and curator synthesis remain distinguishable. |
| Hierarchy/equivalence | Parents, replacements, xrefs, mapped xrefs, and relation predicates have the right semantics. | Identity is not inferred from overlap, co-membership, or functional association. |
| Representations | Sequence, profile, secondary structure, geometry, residue, and method claims include provenance and coordinate/frame context. | Representations can be traced and compared without mixing numbering schemes. |
| Chemistry/function | Participants, role, reaction/function, and evidence concern the exact trait scope. | Family-wide claims are not extrapolated from one instance without support. |
| Examples | Protein accession, taxon, sequence/release, qualification status, and occurrence evidence agree. | Newly promoted examples passed the repository's reviewed workflow. |
| Causal graph | Node identities/types, edge direction/predicate, scope, and edge evidence agree. | Every edge is supported and predicted mechanisms remain labeled as such. |
| Discussions/datasets | Each item is durable, relevant, and actionable. | No placeholder task or bibliography dump remains. |
| Status/audit | Mapping status, record event, writer registration, and repository history match the review. | REVIEWED has human sign-off and LLM assistance is explicit. |
