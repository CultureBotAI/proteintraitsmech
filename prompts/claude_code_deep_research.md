# Claude Code task: one ProteinTraitsMech deep-research curation

**Use:** hand to the Claude Code agent working in this repository to research and
curate one protein-trait record end to end.

Work from the ProteinTraitsMech repository root. Read `CLAUDE.md`, any applicable
`AGENTS.md`, the LinkML schema, and the selected protein-trait record before
editing.

## Mission

Select exactly one high-value protein sequence/structure/function mechanism
question, research it with the `claude_code` deep-research provider, and save
supported findings in one schema-compliant `ProteinTraitRecord` YAML file.

The Markdown report in `research/traits/` is a raw audit artifact, not the final
structured result. The accepted research must also be curated into the canonical
protein-trait YAML and pass the schema and graph gates.

## Constraints

- Use only `claude_code`; do not invoke or fall back to Cyberian or another
  provider. Run at most one new deep-research job.
- Check for an equivalent existing Claude Code report and choose another target
  instead of duplicating it.
- Do not expose or alter credentials or `.env`.
- Never modify the schema, generated datamodel, or validators to fit output.
- Do not infer function solely from a family name, motif hit, domain presence,
  predicted structure, or sequence similarity. Distinguish experimental evidence
  from computational annotation and family-level evidence from protein-specific
  evidence.
- Never invent accession CURIEs, residue positions, catalytic mechanisms,
  predicate directions, citations, or snippets.

## 1. Pick one question

Inspect the local corpus before researching:

- `data/analysis/semantic_merge_candidates.yaml`
- repository planning/backlog documents, if present
- records under `data/traits/` with absent or weak definitions, evidence, family
  grounding, or causal graphs
- existing `research/traits/**/*claude_code*` reports

Choose one existing, scientifically consequential record for which primary
literature can plausibly connect a sequence/structure feature to molecular
function or phenotype. Prefer a reviewed/seeded family, motif, active site,
domain, or resistance determinant with a specific missing mechanistic link.

State the YAML path, identifier, label, rationale, and one precise question:

> How does **<protein trait>** mechanistically connect sequence or structural
> features to molecular function and downstream phenotype, and which directed,
> source-backed steps belong in a ProteinTraitsMech causal graph?

Do not merge records or edit during question selection.

## 2. Check provider fit and run one job

Run:

```bash
just deep-research-provider claude_code mechanism
```

If unavailable, stop; do not switch providers. Otherwise run exactly once —
`research-protein-trait` is dry-run by default, so pass `--apply` to actually
invoke the provider:

```bash
just research-protein-trait claude_code <target-yaml-path> --apply
```

Capture the report and citations paths printed by the runner. Verify that the
report is non-empty and its key claims are traceable. Do not retry a failed or
inconclusive run and do not compensate with speculative annotations.

## 3. Curate into ProteinTraitRecord YAML

Use the schema and comparable reviewed records as authority. Edit the selected
file only, except for provenance artifacts explicitly required by repo policy.

- Improve the definition/source, xrefs, examples, or evidence only when directly
  supported at the correct family/protein scope.
- In a causal graph, keep the determinant/feature, molecular mechanism, function,
  and phenotype as distinct nodes where the evidence supports that distinction.
- Add only directed edges supported by the cited source. A domain association or
  sequence match alone is not proof of catalysis or phenotype causation.
- Use schema-allowed node types and established predicates. Verify identifiers
  and labels; omit uncertain grounding rather than inventing it.
- Attach stable citations and short verbatim snippets to the exact edge or claim.
- Preserve source provenance, license, mapping/review status, and existing correct
  annotations. Mark LLM-assisted curation using the record's existing
  `curation_history` convention when applicable.

Do not put report headings or free-form conclusions into undeclared YAML fields.

## 4. Validate

Run:

```bash
just validate <target-yaml-path>
just validate-all <target-yaml-path>
just audit-graphs
```

Run any additional source-specific checks named by the record or repository
instructions. Fix the data, not the schema, validator, or audit baseline. Do not
launch another research job. Finish with `git diff --check` and inspect the
focused diff.

## Completion report

Report the selected question and rationale, provider check, the one research
command, raw report/citations paths, canonical YAML path, accepted and rejected
claims, validation outcomes, and remaining family-versus-protein or mechanistic
uncertainty.

