---
name: curate-yaml-record
description: Review and curate one ProteinTraitsMech trait YAML record for protein-trait identity, axis/category placement, definitions, hierarchy, representations, examples, evidence, causal mechanisms, completeness, and resolvable gaps. Use for a named record audit or improvement; do not use for bulk source ingestion, unreviewed protein promotion, or as permission to spend credits, contact anyone, or mutate GitHub.
allowed-tools: Bash, Read, Grep, Glob, WebSearch, WebFetch, Edit, Write
metadata:
  category: curation
  requires_database: false
  requires_internet: true
  version: 2.0.0
---

# Curate one ProteinTraitsMech YAML record

Produce a defensible `ProteinTraitRecord` and an explicit account of what is
supported, corrected, unresolved, and genuinely unknown. Search results and
research reports are leads; inspect source-native records and cited literature
before using them.

## The Contract

<!-- canonical:begin the-contract -->
Produce a defensible record and an explicit account of four things: what is
**supported**, what was **corrected**, what is **still unresolved**, and what is
**genuinely unknown**. The last two are different — a gap you searched for and
could not close is a finding; a gap you did not look at is not.

**One target.** Resolve exactly one record before touching anything. If a label
matches several, or a request names a family rather than a member, stop and
disambiguate. Silently substituting a similar record is the error that no later
check catches, because everything downstream is then correct about the wrong
thing.

**Audit preserves scientific inputs. Curation authorises edits to the named
record only.** A review or audit request changes no scientific record, status,
or curation history. It does save a new timestamped structured review through
`docs/record-reviews.md` and the native rubric in `docs/record-review-profile.md`.
A curate, improve, complete, correct or add-evidence request authorises local edits to that record and the smallest
maintained path its provenance requires — not to neighbours, not to whatever
else looked wrong on the way.

**Search results are leads. Only an inspected source supports a claim.** A
search hit, a deep-research report, a rendered page, and a generated artifact are
each somewhere to look, and none is evidence. Evidence is text you read in the
source, attached to the narrowest assertion it actually supports.
<!-- canonical:end the-contract -->

## Boundaries

<!-- canonical:begin boundaries -->
- **A generated artifact is never the fix.** Pages, merged products, exports and
  derived indexes are outputs. Correct the input or rule that owns the value and
  regenerate; patching the output makes it look right once and diverge on the
  next build.
- **No outbound action without explicit authorisation for that action.** Do not
  launch paid research, contact an author, or create or edit a GitHub issue, PR
  or comment because curation seemed to call for it. Authorisation to curate a
  record is not authorisation to spend or to speak.
- **Absence is not evidence of falsity, and coverage is not a goal.** Never
  infer that an unstated optional property is false. Never fill an optional
  slot to make the record look more complete. An empty field the source does
  not address is correct.
- **Search before declaring anything absent — and search past `.gitignore`.**
  Before treating a record, evidence source, decision row or overlay as missing,
  search for its identifier, label and slug with an ignore-independent tool
  (`rg --no-ignore --hidden`, `grep -r`, or `find`). Ordinary search skips
  ignored files, so an ordinary miss is a search over a subset, not a result.
- **Preserve unrelated work.** Use a branch, and a separate worktree when the
  checkout is dirty or occupied by something else.
<!-- canonical:end boundaries -->

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

## Evidence Standard

<!-- canonical:begin evidence-standard -->
- Each claim is its own object. A definition, an example, a relation and a
  mechanism edge are separate assertions; attach a source to the narrowest one
  it supports, never to the record as a whole.
- Resolve every DOI, PMID and CURIE, and read enough of the source to establish
  support for the *exact* claim and scope. A matching string from the wrong
  paper, or an unrelated sentence from the right one, is not support.
- A snippet is short verbatim text from the source. Interpretation belongs in a
  notes field, never inside the quotation.
- **The kind of source is part of the citation.** A database assertion, a
  primary experiment, a review, a prediction and a search snippet are different
  strengths of support. Cite each as what it is; never present a database row
  or a review as if it were the primary study.
- Association and prediction do not establish mechanism or causality. Do not
  let a co-occurrence or a computed score become a mechanism edge.
- **A near-miss is not a match.** Never ground to a CURIE or canonical label
  because it looks plausible, and never use a broader or related term as an
  exact identity. Unresolved stays unresolved, recorded as such, until a source
  resolves it.
- **Evidence about one thing supports a claim about that thing.** Do not
  generalise one organism, strain, protein instance, construct or experiment
  into a family-wide, universal or "optimal" claim. Scope inflation is the most
  common way a true observation becomes a false record.
- Keep conflicts. When sources disagree, record both and the disagreement; do
  not resolve it by omission.
- A bounded search that found nothing is a result. Report it as "not found,
  searched X" rather than leaving the field silently empty.
<!-- canonical:end evidence-standard -->

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

## Writing Back

<!-- canonical:begin writing-back -->
**Write only through the path that preserves formatting and records history.**
Never hand-edit a curated YAML with a text editor or a generic dump: canonical
key order, quoting and derived metadata are what make the corpus diffable, and a
dump destroys them in one save.

Repositories in this fleet do this in three different, equally correct ways, and
which one applies is a property of the corpus:

- **Direct guarded write** — a narrowly scoped mutator loads the record, asserts
  its identity, changes only the reviewed nodes, appends a curation event, and
  writes through the repository's validated writer.
- **Registered editor** — no generic writer exists on purpose; in-place changes
  use text-preserving operations through an editor that is registered and
  behaviourally tested, and the writer audit rejects anything else.
- **Regenerate from inputs** — the record is a build product. The fix goes into
  the decision row, term request, overlay or source inventory that owns the
  value, and the record is regenerated; the YAML is never edited directly.

The section below says which one this repository uses and names the exact
functions or files. Do not guess from a sibling.

Inspect the diff before committing. Whole-file presentation churn — reordered
keys, requoted strings, a hundred lines changed to alter one value — means the
write path was bypassed; abandon and repair rather than commit it.
<!-- canonical:end writing-back -->

## History And Attribution

<!-- canonical:begin history-and-attribution -->
- Use `curator="claude"` when no curator identity was supplied. **Never
  attribute an agent's judgement to the user.** The history entry is a record
  of who decided, and it will be read when the decision is questioned.
- Mark LLM assistance where the schema records it.
- **Do not append a history event when nothing substantive changed.** A
  no-op event is noise that makes real events harder to find.
- The history entry describes the actual diff. If the corpus derives status or
  history from inputs, never set them directly — change the input.
- A REVIEWED status means a human reviewed it. Do not invent one, and do not
  promote to it on the strength of an agent pass.
<!-- canonical:end history-and-attribution -->

## Workflow

For an audit-only request, follow
[docs/record-reviews.md](../../../docs/record-reviews.md) and the
[native profile](../../../docs/record-review-profile.md). Capture exact targets
and inspected inputs before judgement with `scripts/record_review.py inspect`.
Apply steps 1-4 as assessments/proposed actions, skip step 5, and run only
applicable read-only validation from step 6. Save a `kind: record` YAML plus
derived Markdown through `uv run python scripts/record_review.py save --content
<review.yaml>` after validation. Link both saved files; retain partial/blocked
coverage when required checks are unavailable. The review itself authorizes
no record edits, generated products, history event or status promotion.

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
