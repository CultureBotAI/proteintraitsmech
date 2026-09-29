# Grounding registries

This directory is the durable, reviewed half of the UniProt grounding workflow.
Generated audit, resolver, and review staging files live under the gitignored
`reports/uniprot-grounding/` directory.

Release-stamped JSONL registries accompany trait records containing a `QUALIFIED`
canonical example:

- `protein_registry.jsonl` contains one schema `ProteinReference` per exact UniProt
  accession or explicitly resolved isoform. A full sequence is stored once, with its
  UniProt release, sequence version, length, checksum, protein name, and organism.
- `occurrence_evidence.jsonl.d/` contains the normalized source snapshot for each
  qualified `TraitOccurrence`. Its content-addressed evidence identifier binds the record
  assertion to exact provider facts and release. It is sharded; see below.
- `qualified_record_bindings.jsonl.d/` holds one receipt per durable evidence row, keyed
  by the same `evidence_id`. A receipt binds the evidence to the trait record that
  carries it (`record_path`, `record_sha256`) and to the record-content gate projection
  that admitted it (`content_gate_projection`, `content_gate_digest`). The evidence and
  binding key sets must be equal: the promoter and the semantic validator both refuse
  an evidence row without a receipt, or a receipt without evidence. It is sharded too.
- `uniprot_memberships.jsonl` is present when a whole-protein occurrence is supported by
  an exact UniProt database cross-reference. Each content-addressed fact is captured from
  the same exact-accession response as its `ProteinReference` and is bound to that release
  and sequence checksum; a discovery query or generic search hit is never membership
  evidence.
- `elife109154_source_assertions.jsonl` records reviewed seed-alignment membership or
  explicit reference-BGC profile annotations from the pinned Zenodo 18866949 deposit.
  `elife109154_acquisition_receipt.json` binds those assertions to source archive and
  exact-accession UniProt response hashes. Its version 2 receipt also hashes the durable
  `data/curation/elife109154_example_decisions.jsonl` ledger and binds every assertion
  to an approved resolution with matching model, protein, and organism. Promotion
  installs that ledger transactionally and retains prior review coverage across batches.
  A version 1 receipt requires replay and approval of the complete existing panel to
  upgrade; ordinary validation does not accept an unbound legacy receipt.
  The source-specific contract accepts only
  whole-protein sequence families with exact source/UniProt sequence agreement; it
  does not qualify cropped domains without coordinates. `QUALIFIED` here describes
  sequence classification, not experimentally demonstrated activity. See the
  [publication analysis](../../research/elife-109154-metallophores.md) and use the
  registered `ground_uniprot_examples.py elife-promote` route for reviewed changes.
  Since #801, `elife-promote` cannot write qualified-record bindings, so it refuses any
  batch that would add evidence while the bindings registry exists (always, in this
  repository). It can still replay an unchanged panel; adding a new eLife example waits
  for eLife promotion to write bindings.

Do not hand-edit these registries. Build staging outputs from pinned providers, review the
source-stratified ledger, install the approved rows with the grounding promoter, and run
`just validate-all` before committing the registry and trait changes together. A
`QUALIFIED` record whose registry row is absent or inconsistent fails semantic validation.

## Sharded evidence and bindings registries (#801)

Every promotion grows the evidence and bindings registries, so each is a directory of
JSONL shards rather than one ever-growing file (layout `evidence-id-hex2`, version 1,
implemented in `scripts/grounding_registry_layout.py`). For current row counts and shard
sizes, run `just check-grounding-registries` rather than trusting a figure written here.
The layout rules:

- A row lives in `<hh>.jsonl`, where `<hh>` is the two hex digits right after
  `ug-evidence:` in its `evidence_id`, so there are at most 256 shards. Only non-empty
  shards exist.
- Every line is canonical JSON (sorted keys, compact separators, raw UTF-8) plus `\n`,
  and rows ascend strictly by `evidence_id`. There are no blank lines, no CR, and no BOM.
- `manifest.json` records each shard's bytes, rows, and sha256, the totals, and the
  registry's `logical_sha256`. It is a pure function of the shard bytes, so exactly one
  valid manifest exists for a set of shards, and it is written last: a directory whose
  manifest does not match its shards was torn or edited and fails closed.
- Joining the shards in name order reproduces the legacy flat file byte for byte, so the
  logical sha256 equals the flat file's sha256. Check any registry with:

  ```bash
  LC_ALL=C cat data/grounding/occurrence_evidence.jsonl.d/[0-9a-f][0-9a-f].jsonl | shasum -a 256
  ```

  The printed digest must equal that directory's `manifest.json` `logical_sha256`.
  `just check-grounding-registries` verifies both directories, their equal key sets, and
  the shard-size tripwire in one read-only pass.
- `X.jsonl` and `X.jsonl.d` never coexist. A leftover flat file beside its directory, or
  a flat path passed where the registry is sharded, is a `registry_layout_conflict`.
  The one-time conversion from the flat files is `just migrate-grounding-registries`.
  An absent evidence or bindings directory is an error for the promoter, never a fresh
  start; restore it from git.

`protein_registry.jsonl` stays one flat file: its sha256 is pinned as `registry_sha256`
in `data/biophysical/pilot.observations.manifest.json`. `uniprot_memberships.jsonl` stays
flat because its path is recorded in membership evidence (`provider_source`), so moving it
would change evidence identifiers.

**Never hand-edit a shard or a manifest**, and never regenerate a manifest to make an
edit verify. Every change goes through the grounding promoter, whose transaction plans
all shard writes before the first one, writes each manifest last, re-verifies the
installed directories, and rolls back on any in-process failure, Ctrl-C included. A
further Ctrl-C is held from the rollback's first step until it finishes, and a restore
that still fails is reported as an incomplete rollback naming its paths.

**Lock.** `promote --apply`, eLife `--apply`, and the migration hold an exclusive
advisory lock on the gitignored `data/grounding/.grounding-registries.lock`. When
`promote --apply` is pointed at other durable paths, it first validates them and then
locks `.grounding-registries.lock` in every directory it writes a durable registry
into; it never creates one inside a sharded registry or a trait tree. A second
writer fails fast with `registry_locked`, naming the holder's pid. The kernel releases
the lock when its holder exits, so a crashed writer never leaves it held; the lock file
itself is never deleted. A lock file another user created (mode 0644) is locked through
a read-only descriptor. If the file cannot be opened or locked at all (a symlink, no
permission, or a network filesystem without `flock` support), the writer stops with
`registry_lock_unavailable` before writing anything. Between machines sharing a network
checkout, `flock` exclusion is not guaranteed. Dry runs do not lock.

**Torn install recovery.** In-process failures roll back exactly. A power loss,
`kill -9`, or a signal Python does not turn into an exception (such as an unhandled
SIGTERM) mid-install is never rolled back. It can leave a manifest mismatch, a shard
the commit does not have, or hidden `.<hh>.jsonl.<random>` / `.manifest.json.<random>`
temporary files, which validation names as `registry_manifest_mismatch` or
"interrupted atomic write residue".
`git restore` alone brings back tracked files but never deletes an untracked shard,
residue file or directory, so after confirming no writer is running:

```bash
git restore --source=HEAD --staged --worktree -- data/grounding
git clean -n -d -- data/grounding   # review what would be removed
git clean -f -d -- data/grounding   # without -x, keeps the gitignored lock file
```

Then replay the promotion. An interrupted `just migrate-grounding-registries --apply`,
or one whose post-apply check failed after the install, recovers the same way: until
the migration is committed its `.jsonl.d` directories are untracked, so `git clean`
removes them and `git restore` brings back both flat files. The migration's refusal
prints these commands.

**Merge conflicts.** Registry shards, manifests, `protein_registry.jsonl`, and the
biophysical pilot pin are never hand-merged. When a branch conflicts under
`data/grounding/`, take `origin/main`'s `data/grounding/` unchanged and replay the
branch's promotions with the promoter from their retained staging ledgers.

The durable protein registry can contain proteins pinned to different UniProt releases.
Execution contracts that require one release, including SFLD HMMER receipts, must receive
a release-specific staging registry through `--registry`. The eLife ingest preserves the
126 existing `2026_02` protein rows and adds 33 `2026_03` rows; it does not upgrade the
older references or relax the SFLD single-release check.

See [`research/uniprot-organism-protein-grounding-plan.md`](../../research/uniprot-organism-protein-grounding-plan.md)
for the state machine, evidence tiers, review protocol, and completion criteria.
