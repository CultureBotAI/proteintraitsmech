# Grounding registries

This directory is the durable, reviewed half of the UniProt grounding workflow.
Generated audit, resolver, and review staging files live under the gitignored
`reports/uniprot-grounding/` directory.

Release-stamped JSONL registries accompany trait records containing a `QUALIFIED`
canonical example:

- `protein_registry.jsonl` contains one schema `ProteinReference` per exact UniProt
  accession or explicitly resolved isoform. A full sequence is stored once, with its
  UniProt release, sequence version, length, checksum, protein name, and organism.
- `occurrence_evidence.jsonl` contains the normalized source snapshot for each qualified
  `TraitOccurrence`. Its content-addressed evidence identifier binds the record assertion
  to exact provider facts and release.
- `uniprot_memberships.jsonl` is present when a whole-protein occurrence is supported by
  an exact UniProt database cross-reference. Each content-addressed fact is captured from
  the same exact-accession response as its `ProteinReference` and is bound to that release
  and sequence checksum; a discovery query or generic search hit is never membership
  evidence.

Do not hand-edit these registries. Build staging outputs from pinned providers, review the
source-stratified ledger, install the approved rows with the grounding promoter, and run
`just validate-all` before committing the registry and trait changes together. A
`QUALIFIED` record whose registry row is absent or inconsistent fails semantic validation.

See [`research/uniprot-organism-protein-grounding-plan.md`](../../research/uniprot-organism-protein-grounding-plan.md)
for the state machine, evidence tiers, review protocol, and completion criteria.
