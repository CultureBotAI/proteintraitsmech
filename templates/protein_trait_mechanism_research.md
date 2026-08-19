# ProteinTraitsMech Mechanism Research Template

## Target Protein Trait
- **Record:** {record_path}
- **Identifier:** {trait_identifier}
- **Label:** {trait_label}
- **Axis / category:** {trait_axis} / {trait_category}
- **Term kind / mapping status:** {term_kind} / {mapping_status}
- **Definition:** {definition}
- **Layered definitions:** {definitions}
- **Synonyms:** {synonyms}
- **Parents:** {parent_traits}
- **Direct xrefs:** {xrefs}
- **Mapping-product xrefs:** {mapped_xrefs}
- **Chemical participants:** {chemical_participants}
- **Canonical examples:** {canonical_examples}
- **Trait relations:** {trait_relations}
- **Causal graphs:** {causal_graph_summary}
- **Existing evidence:** {existing_evidence}

## Research Objective

Research **{trait_label}** as a ProteinTraitsMech sequence/structure/function trait.
Focus on evidence that can improve the exact record above: scope and hierarchy,
sequence or structural determinants, molecular mechanism, reaction chemistry,
cofactors and participants, representative proteins, and evidence-backed causal edges.

## Required Findings

1. **Identity and scope** — distinguish equivalent terms from parents, children,
   overlapping families, co-membership, and externally asserted mappings.
2. **Mechanism** — connect sequence features or residues to structure, chemistry,
   molecular function, and downstream outcome. Preserve residue numbering scheme,
   construct, protein accession, species, and experimental context.
3. **Grounding** — use source-resolvable identifiers from UniProtKB, PDB/PDBe,
   InterPro, Pfam, CATH, SCOP, PROSITE, MEROPS, CAZy, NCBIfam, EC, Rhea, GO,
   ChEBI, M-CSA, and NCBITaxon. Do not invent or silently normalize identifiers.
4. **Evidence** — every proposed causal edge needs a PMID/DOI/database reference,
   a short supporting snippet, and notes explaining its scope. Database assertions
   must name the source record and release/page where possible.
5. **Generalization guard** — do not generalize one protein's residue, mechanism,
   ligand, or conformation to an entire family unless the source supports that scope.

## Output Format

Return a curation-focused Markdown report with:

- an overall record verdict (`CONFIRMED`, `NEEDS_CORRECTION`, or `INSUFFICIENT_EVIDENCE`);
- scope/hierarchy and identifier corrections;
- candidate definitions, relations, chemical participants, and canonical examples;
- candidate causal nodes and edges with reference, snippet, protein/structure context,
  and confidence;
- a DOI/PMID-first bibliography plus authoritative database records;
- explicit warnings for claims that must not yet be curated.
