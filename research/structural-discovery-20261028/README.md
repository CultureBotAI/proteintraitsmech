# Structural trait discovery, 2026-10-28

This is the standalone discovery goal accepted in conversation
`01a183c4-7ea5-7943-9580-927303425d81`, on branch
`discover/structural-traits-20261028-04f08f`, based on
`7276814bdf3bed73569a202c5e2c4b404e43d8f1`. UTC work dates may be 2026-10-29.
Existing PR #1202 and issues #1200/#1201 provide context and duplicate exclusions.
The goal permits up to ten genuinely missing PROPOSED structural classes, a
complete canary before batching, validation, independent review, findings/fixes,
and a PR. It does not authorize merging, queue entry, cleanup or session changes.

The owned worktree is the preserved `ptm-structure-20261028-029cc7/worktree`.
Only this worker writes trait records and shared files. The scientific evidence
delegates own only `motifs/` and `cavities/`; the coordination reviewer owns only
`preflight/`. All other live workers, including pane %5/PID 92825, are preserved.
There is no workflow run/cycle/stage binding; none is synthesized here.

## Coordination and provenance

Native add-record allows absence-checked taxonomy IDs. The supported coordination
contract is isolated worktree ownership, fresh corpus/alias/open-work collision
checks, short repository leases where required for shared transitions, and Git/PR
handoff. The preflight report records its exact sources and limits. A candidate
list or GitHub snapshot is not a durable ID reservation or cross-machine lock.
Record IDs and shared paths must be recorded and checked before creation.

Task helpers are retained in `scripts/adhoc/structural_discovery_20261028/` or
these evidence directories. No executable helper is kept only in `/tmp`.

| Helper | Purpose and inputs | Outputs | Date/reference |
| --- | --- | --- | --- |
| `scripts/adhoc/structural_discovery_20261028/observe_open_work.py` | Read-only authenticated `gh` snapshot of current main, all open PR/issue titles and bodies, and paginated PR file patches | JSON supplied with `--output`; includes helper hash and coverage limits | 2026-10-29 UTC; this standalone goal; #1200/#1201 context |
| `scripts/seed_structural_discovery.py` | Current manifest and every corpus YAML; closed native validation and parsed identity preflight | Three owned records only with `--apply`; default dry-run; optional new JSON receipt in this evidence directory | 2026-10-29; #1204 guards, #1200/#1201 discovery context |
| `tests/test_seed_structural_discovery.py` | Synthetic temporary record trees and real native validation | Thirteen behavioral guard tests; no corpus mutation | 2026-10-29; #1204 |
| `scripts/adhoc/structural_discovery_20261028/package_evidence.py` | This task directory including ignored files, helper sources, frozen public GitHub snapshot | Lossless compressed snapshot, exact file/hash/retention inventory; optional hash-verified restoration | 2026-10-29; #1200/#1201/#1204 |

Delegate helper details are retained in the `preflight/`, `motifs/` and `cavities/`
provenance documents. Historical guard sources are reconstructed copies verified
against the hashes recorded before the fix. Their negative probes demonstrate
old acceptance and are expected to fail against fixed code; the separate fixed
probes establish current behavior. Original relative-path assumptions and
temporary source/log dependencies are documented, not presented as portable
automatic replays.

## Publication retention

`publication-manifest.json` inventories this task with ignored files included.
Every Python helper/source used for the task is retained with results. Large
initial broad-search outputs remain locally preserved; compact refined searches,
adjudications, source hashes and the search reproducer are published. The full
ontology release and HBPLUS archive/extracted manual remain local under native
release/rights rules. No input is deleted by packaging.

The 21-MiB public open-work snapshot is retained losslessly as
`open-work-prewrite.json.gz`. Restore the original byte-identical JSON path with:

```sh
python3 scripts/adhoc/structural_discovery_20261028/package_evidence.py --restore-open-work
```

Historical search replay may also require ignored source/staging inputs recorded
in its manifest; a fresh live GitHub query will not reproduce historical issue
bodies. Use the frozen archive for the original coordination observation.

## Accepted first batch

Three new-to-PTM classes were emitted: one supersecondary motif and two tertiary
geometric features. All remain **PROPOSED**. These are established literature
concepts missing from the inspected catalog, not new-to-science discoveries.
No elementary secondary-structure class was accepted in this first batch.

| Class | Owned record | Primary support and whole-structure representative | Independent native review |
| --- | --- | --- | --- |
| Protein tunnel bottleneck | [tunnel-bottleneck.yaml](../../data/traits/structure/cavity/tunnel-bottleneck.yaml) | DOI:10.1371/journal.pcbi.1002708; PDB:1CQW v1.4 | [Canary review](../../reviews/structured/20261029T071028Z-independent-tunnel-bottleneck-canary/) |
| Beta arch | [beta-arch.yaml](../../data/traits/structure/secondary/beta-arch.yaml) | DOI:10.1038/s41467-022-33004-6; PDB:7SKO v1.2 | [Beta-arch review](../../reviews/structured/20261029T071846Z-independent-beta-arch/) |
| Membrane-facing lateral channel fenestration | [membrane-facing-channel-fenestration.yaml](../../data/traits/structure/cavity/membrane-facing-channel-fenestration.yaml) | DOI:10.1073/pnas.2401591121; PDB:7WLI v1.2 | [Fenestration review](../../reviews/structured/20261029T072012Z-independent-membrane-fenestration/) |

The tunnel bottleneck is a geometric **part of** a tunnel; the fenestration is a
tunnel subtype. Beta arches exclude mutual hydrogen-bond pairing of their two
flanking strands. These distinctions prevent conflating whole paths, enclosed
voids, hairpins, complete folds and functional mechanisms. CAVER/DSSP recipes are
documented external screening steps followed by explicit geometric review; they
were not run on these representative structures. No radius, residue boundary,
qualified protein occurrence, causal graph, permeability or binding function is
newly asserted. There are three whole-structure anchors and **zero** new canonical
or qualified protein examples.

The [ranked frontier](candidate-frontier.md) records all eleven candidate groups
and the final selection. Five generic classes were rejected as already present:
beta bulge, alpha turn, pi turn, alpha-alpha corner and beta meander. Asx and ST
turns retain their possible exact SO identifiers but await compatible exemplar
and executable-detection support. Schellman, beta-bulge-loop and psi-loop motifs,
subpockets, intersubunit/interdomain cavities and generic cryptic pockets remain
deferred for the specific scope/evidence gaps in that report and delegate cards.
The earlier 24-record enrichment contributes zero to this new-record count.

## Writer, canary and validation

The native writer consumes [the maintained manifest](../../data/curation/structural_trait_discovery.yaml),
validates the complete selected batch, parses all corpus YAML including ignored
files for primary-ID/xref collisions, and refuses different existing record bytes.
It is registered as a local taxonomy generator in `scripts/source_helpers.yaml`.
The [dry-run](canary-dry-run.json), [canary application](canary-apply.json), native
canary review, then [batch application](batch-apply.json) establish the ordering.
[Final replay](final-replay.json) parsed 429397 records and left all three owned
files byte-identical. This local coordination does not claim a durable global ID
reservation or atomic transaction across unrelated writers.

[Issue #1204](https://github.com/CultureBotAI/proteintraitsmech/issues/1204)
records escaped-YAML identity, CRLF hash and report-clobber defects found by
independent review and fixed before the first corpus write. The
[native writer review](../../reviews/structured/20261029T070848Z-independent-structural-discovery-writer/)
pins the fixed seeder/tests. The later packaging review and source-registry gate
also prompted a Python 3.10-compatible hashing loop and a local-generator entry.
Initial failure evidence remains retained alongside fixed results.
The [independent package assessment](preflight/package-provenance-assessment-20261029T072931430230Z.json)
passed with documented historical/replay limits and verified all 26 retained
Python sources, including exact historical sources. Its inventory was provisional;
the final publication manifest is refreshed after that assessment and completed logs.

- [Focused suite](focused-tests.log): 40 passed, including 13 seeder guard tests,
  method coverage, docs consistency and the native review contract.
- [Registry tests](source-registry-tests.log): 26 passed after registry classification;
  [sources-check](sources-check-final.log) passed with 27 existing reviewed notices,
  zero warnings and zero errors.
- [Strict validation](final-strict.log) and [grounding validation](final-grounding.log):
  all three records passed; independent reviews also audited their graph scope.
- [Native review check](native-review-check.log): 29 valid reviews, including the
  four new immutable review artifacts. Each science verdict is pass with limitations.
- [Writer audit](writer-audit.log), [lint](final-lint.log),
  [history](history-validation.log), and [internal-ID baseline](internal-id-baseline.log)
  passed. Baseline mismatch count/fingerprint are unchanged; only the corpus count
  increases by three to 429397.
- [Docs rebuild](build-docs.log) passed. Tracked landing counts increase by three;
  regenerated ignored browser data have 746 detail buckets totaling 480.14 MB.
- [Full suite](full-tests.log): **8616 passed, 52 skipped, 2 warnings** in 487.12 s.
  The two warnings are existing dependency deprecations; no test failed.

The final pre-commit remote read still found main at `7276814b…` and the same 32
open PR heads as the pre-batch snapshot (`precommit-pr-heads.json`). The native
source-helper registry has no path owner in the frozen open-PR file lists.

Full-corpus validation remains a pre-merge gate. This task ends at a reviewed PR;
merge, queue entry, cleanup and changes to other sessions remain unauthorized.
