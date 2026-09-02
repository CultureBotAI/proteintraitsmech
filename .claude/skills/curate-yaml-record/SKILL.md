---
name: curate-yaml-record
description: Review and curate one ProteinTraitsMech trait YAML record for protein-trait identity, axis/category placement, definitions, hierarchy, representations, examples, evidence, causal mechanisms, completeness, and resolvable gaps. Use for a named record audit or improvement; do not use for bulk source ingestion, unreviewed protein promotion, or as permission to spend credits, contact anyone, or mutate GitHub.
allowed-tools: Bash, Read, Grep, Glob, WebSearch, WebFetch, Edit, Write
metadata:
  category: curation
  requires_database: false
  requires_internet: true
  version: 1.0.0
---

# Curate one ProteinTraitsMech YAML record

Produce a defensible `ProteinTraitRecord` and an explicit account of what is
supported, corrected, unresolved, and genuinely unknown. Search results and
research reports are leads; inspect source-native records and cited literature
before using them.

## Boundaries

- Resolve one target under
  `data/traits/{sequence,structure,sequence_structure,function,evolution}/`.
  Stop and disambiguate if a label matches several families, domains, motifs,
  structural classes, functions, or evolutionary concepts.
- Review/audit requests are read-only. Curate, improve, complete, correct, or
  add-evidence requests authorize local edits to the named record and the
  smallest necessary registered writer/history/generated artifacts.
- Do not promote an unreviewed protein, inferred family membership, predicted
  structure, or profile hit as verified record-specific evidence.
- Never launch a paid provider, contact anyone, or create/edit a GitHub item or
  other outbound message without explicit authorization.
- Preserve unrelated work and use a dedicated branch/worktree.
- Do not fill optional fields merely for coverage or infer false from absence.

## Read before judging the record

Read the complete target plus:

- `CLAUDE.md`;
- the relevant `ProteinTraitRecord`, definition, relation, representation,
  canonical-example, evidence, causal-graph, discussion, and history classes in
  `src/proteintraitsmech/schema/proteintraitsmech.yaml`;
- the provenance/grounding plan relevant to the record's source and
  `history/README.md`;
- [references/review-checklist.md](references/review-checklist.md).

Inspect parent/child records, equivalence ledgers, source-native database
records, release sidecars, and existing research. Generated pages, embeddings,
and provider prose are not independent evidence.

## Workflow

### 1. Establish the baseline

Read the full YAML. Record identifier, label, axis/category, definition/source,
synonyms, parents, xrefs/mapped xrefs, representations, examples, relations,
mapping status, evidence, causal graphs, license, discussions, datasets, and
curation history. Run:

```bash
just validate <record-path>
just validate-all <record-path>
```

Run the relevant representation, UniProt-grounding, hierarchy, and graph
audits for the fields present. A green schema gate proves shape, not that the
record represents the right protein trait.

### 2. Verify trait identity, axis, and source scope first

Confirm the record denotes one class-level protein trait and is placed by how
that trait is represented: sequence, structure, sequence-structure, function,
or evolution. Check source accession/release, label, synonym scope, category,
term kind, parents, replacements, xrefs, and license.

Distinguish exact equivalence, hierarchy, co-membership, overlap, functional
association, and shared sequence/structure evidence. Never collapse these into
an exact xref. Never generalize one protein instance, construct, isoform, or
taxon to a family-wide claim without supporting evidence.

### 3. Review every scientific claim

Verify each definition, alternate definition, chemical participant, trait
relation, detection method, representation, evolutionary-scope assertion,
pattern/residue sequence, canonical example, and causal edge against the exact
source record or literature. Check residue numbering, isoform/construct, taxon,
experimental context, source release, and evidence method.

Every causal edge needs claim-level evidence. Predictions and profile matches
must remain predictions/candidates unless independently qualified by the
repository's promotion workflow. Snippets are short exact source text;
interpretation and limitations belong in notes.

### 4. Assess completeness and resolve supported gaps

Apply the checklist and use bounded searches for consequential gaps. Prioritize:

1. wrong identity, source accession, axis/category, or hierarchy;
2. overbroad definitions, family claims, and exact mappings;
3. unqualified canonical examples or protein occurrences;
4. inconsistent sequence/structure/function representations;
5. unsupported causal edges, residue claims, or chemical participants.

Do not manufacture a mechanism for a classification or representation-only
trait. Add a discussion only for a concrete conflict or consequential curation
task whose resolution condition can be stated.

### 5. Use the registered guarded write path

ProteinTraitsMech intentionally has no generic dict-dump curator. In-place
record changes must use text-preserving operations and finish with
`scripts.record_io.write_validated_record`. Use an existing registered editor
or validated promoter when its semantics match. Otherwise add a narrowly
scoped editor, its behavioral tests, and its registration in
`tests/test_inplace_editor_guards.py`; do not evade `just audit-writers` with an
unregistered ad hoc writer.

Append a schema-valid `CurationEvent` describing the exact change and marking
LLM assistance. Use curator `claude` when no human identity was supplied; never
attribute agent judgement to the user. Create the repository history record
with `just new-history`. Do not add either event when content is unchanged.

`mapping_status: REVIEWED` requires human curator sign-off on label,
definition, and parents. Agent-produced work remains `PROPOSED` without that
sign-off; do not downgrade an already reviewed record solely because a new gap
was found.

### 6. Verify and report

```bash
just validate-all <record-path>
just audit-graphs <record-path>
just audit-writers
just validate-history
just lint
just test
git diff --check
git diff -- <record-path> history scripts tests docs
```

Run source- and representation-specific validators required by the changed
fields. Re-read the result and confirm record formatting, evidence, status,
writer registration, and history match the actual diff.

Report corrections/additions and sources, retained claims checked, unresolved
gaps and bounded searches, human REVIEWED sign-off status, writer route,
history artifact, and all validation results.
