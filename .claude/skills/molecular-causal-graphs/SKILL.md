---
name: molecular-causal-graphs
description: Create residue- and molecule-level ProteinTraitsMech causal_graphs for one protein trait by wiring active-site residues, binding interfaces, ligands, substrates, products, protein partners, DNA/RNA targets, conformational states, and molecular functions into a small evidence-backed directed graph. Use when asked to model a specific molecular binding, transport/movement, catalytic, allosteric, or macromolecular-interaction mechanism; use edison-causal-graphs for broad Edison gap-filling rounds.
---

# Molecular causal graphs

Build the molecular mechanism inside a `ProteinTraitRecord.causal_graphs` block:
the residues, motifs, domains, partner molecules, local states, and molecular
functions that explain one trait. This is the low-level companion to
`edison-causal-graphs`: use it when the graph must mention residue positions or
specific small/macromolecular participants, and keep Edison round reporting in
force when the work is part of a causal-graph batch.

## Scope and stopping rules

- **One local molecular mechanism.** Keep the graph focused on the trait in the
  target record: a binding pocket, catalytic step series, transport cycle,
  allosteric switch, or residue/RNA/DNA/protein contact. Do not turn a local
  pocket into the protein's entire pathway.
- **Every edge is evidence-backed.** A directed edge is a claim. Add it only
  when a PMID, DOI, source database record, or URL provides a verbatim snippet
  that supports that exact relation.
- **Ground concrete participants first.** Ground proteins and complexes with PR
  or UniProtKB, small molecules with CHEBI, DNA/RNA sites with source CURIEs
  when a stable one exists, molecular functions with GO, PTMs with MOD/PSI-MOD,
  and KB-local trait nodes with their existing `ProteinTraitRecord.identifier`.
- **Make ungrounded nodes explicit.** Use `local: true` plus a `description` for
  unavoidable intermediates, conformations, local bound complexes, or abstract
  locations with no stable CURIE. Prefer a grounded CHEBI/GO/PR/MOD node
  whenever the source entity has one.
- **Residue labels carry their frame.** Label residues in the numbering frame the
  target record uses, preferably full UniProt coordinates. If the paper or PDB
  uses a different frame, cite the SIFTS/source mapping that reconciles it.
- **No unsupported class upgrades.** Binding a ligand, transporting a substrate,
  or mutating a residue in one protein instance is not automatically evidence
  that every member of a broad family has the same edge.

## Graph design

Start from the sources and draft a node/edge table before writing YAML.

### Choose node types

| Participant | `node_type` | Grounding hints |
| --- | --- | --- |
| enzyme, transporter, channel, receptor, protein complex | `PROTEIN` | `UniProtKB`, `PR`, or the target trait CURIE for a class-level determinant |
| domain, transmembrane segment, active-site loop, binding pocket | `DOMAIN` or `MOTIF` | existing Pfam/InterPro/PROSITE/CATH/SCOP/TED/BioLiP/MetalPDB/M-CSA trait CURIE |
| catalytic, binding, gating, or mutated residue | `RESIDUE` | full-sequence UniProt position in the label; source/PDB residue IDs in `description` or `xrefs` |
| substrate, product, ligand, cofactor, ion, drug | `CHEMICAL` or `LIGAND` | CHEBI where possible; source-local chemical only when no CHEBI term exists |
| protein partner or bound protein substrate | `PROTEIN` | UniProtKB/PR for the partner; describe species or complex scope |
| DNA or RNA hairpin, promoter, rRNA nucleotide, codon, editing target | `NUCLEIC_ACID` | RNAcentral, Rfam, SO, source record, or a local node with the exact sequence/context |
| methylated base, phosphorylated residue, glycosylated residue | `PTM` | MOD/PSI-MOD for the modification plus a residue node when position matters |
| acyl-enzyme, closed gate, outward-open state, bound complex | `STATE` | usually `local: true`, with a scoped description |
| catalytic, binding, transport, exchange, or regulatory activity | `MOLECULAR_FUNCTION` | GO or EC/Rhea when the function is curated as an activity |
| resistance, loss of activity, altered localization | `PHENOTYPE` or `TRAIT` | HP/MONDO/ARO/GO or another ProteinTraitsMech record |

Verify any claimed KB-local grounding exists before using it:

```bash
rg --no-ignore --hidden -l '^identifier: <CURIE>$' data/traits -g '*.yaml' -g '*.yml'
```

If that gitignore-independent search returns nothing, either choose another
grounding or make the node explicitly local; do not cite a non-existent trait.

### Choose predicates

Use a readable `predicate` and the closest stable `predicate_id`.

| Relation in the molecular story | Preferred `predicate_id` |
| --- | --- |
| residue/domain/site is part of a protein, RNA, motif, pocket, or complex | `BFO:0000050` |
| local bound complex has the ligand or partner as a constituent | `BFO:0000051` |
| residue/site/ligand/protein/DNA/RNA physically binds or contacts another molecule | `RO:0002436` |
| molecular function consumes a substrate, donor, cargo, or prodrug | `RO:0002233` |
| molecular function produces a product or downstream molecular state | `RO:0002234` |
| domain, motif, or active site enables an activity | `RO:0002327` |
| state, contact, or activity causes a downstream mechanism or phenotype | `RO:0002411` |
| mutation, PTM, allosteric state, or bound molecule regulates an activity | `RO:0002211`, `RO:0002212`, or `RO:0002213` |

Direction is causal or constitutive, not visual layout. For a symmetric binding
fact, point from the residue/site or bound molecule that explains the trait to
the interaction partner and spell the evidence scope out in `description`.

## Modeling patterns

- **Ligand or macromolecule binding:** connect the local residue/pocket to the
  ligand, protein partner, DNA site, or RNA site with `RO:0002436`; connect the
  residue to its pocket/domain with `BFO:0000050`; then connect the pocket or
  function to the downstream trait when the source supports that consequence.
- **Catalysis:** model the activity as a `MOLECULAR_FUNCTION`; add
  `RO:0002233` edges from the activity to each substrate/donor and
  `RO:0002234` edges to products or key local intermediates; add explicit
  residue→substrate/intermediate contacts only for residues whose role is
  stated.
- **Transport or movement:** model the transporter/channel state or molecular
  function, the cargo as a `CHEMICAL`, `LIGAND`, `PROTEIN`, or `NUCLEIC_ACID`,
  and the transported molecule as an input; add directional downstream edges
  only for a source-stated export/import/localization outcome.
- **Allostery or gating:** represent ligand-bound, phosphorylated, open, closed,
  or oligomeric forms as scoped `STATE` nodes; connect the molecular event that
  produces the state to the activity it positively or negatively regulates.
- **DNA/RNA mechanisms:** keep the nucleotide, codon, promoter, or rRNA site as
  a `NUCLEIC_ACID` node and connect the protein residue/domain that recognizes
  it with `RO:0002436`; add a `BFO:0000050` edge to the larger nucleic-acid
  molecule only when the cited source gives the part-whole claim or the source
  record explicitly defines it.

## Write and validate

1. Read the target record and any existing `causal_graphs` in full.
2. Read the schema for `CausalGraph`, `CausalNode`, `CausalEdge`,
   `EvidenceItem`, and `CausalNodeTypeEnum`; do not guess fields.
3. Find nearby graph examples with the same node types or predicates and copy
   their conservative modeling shape, not their identifiers or snippets.
4. Draft the node inventory, with `node_id`, `label`, `node_type`,
   `grounding`/`local`, and the source that justifies every participant.
5. Draft the edge inventory, with subject→predicate→object, `predicate_id`, a
   mechanism-specific `description`, and at least one reference + verbatim
   snippet per edge.
6. Write YAML only after unsupported edges have been dropped or downgraded to
   knowledge gaps. If the graph upgrades a `SEEDED` record to `REVIEWED`, append
   a `curation_history` event with `llm_assisted: true`.
7. Run:

```bash
just validate <record.yaml>
just audit-graphs <record.yaml>
```

If a script produced the graph, also run:

```bash
just audit-writers
```

Report the exact gates and any deliberately local nodes or unresolved gaps.
