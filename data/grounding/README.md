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

Do not hand-edit these registries. Build staging outputs from pinned providers, review the
source-stratified ledger, install the approved rows with the grounding promoter, and run
`just validate-all` before committing the registry and trait changes together. A
`QUALIFIED` record whose registry row is absent or inconsistent fails semantic validation.

## Sharded evidence and bindings registries (#801)

Every promotion grows the evidence and bindings registries (the flat bindings file was
19,008,589 bytes at 12,577 rows), so each is a directory of JSONL shards instead of one
file (layout `evidence-id-hex2`, version 1, implemented in
`scripts/grounding_registry_layout.py`):

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
installed directories, and rolls back on any failure or interrupt.

**Lock.** `promote --apply`, eLife `--apply`, and the migration hold an exclusive
advisory lock on the gitignored `data/grounding/.grounding-registries.lock`. A second
writer fails fast with `registry_locked`, naming the holder's pid. The kernel releases
the lock when its process exits, so it never goes stale; dry runs do not lock.

**Torn install recovery.** In-process failures roll back exactly. A power loss or
`kill -9` mid-install can leave a manifest mismatch or hidden
`.<hh>.jsonl.<random>` / `.manifest.json.<random>` temporary files, which validation
names as `registry_manifest_mismatch` or "interrupted atomic write residue". After
confirming no writer is running, restore the committed image with
`git restore --source=HEAD -- data/grounding`, delete the residue files named in the
error, and replay the promotion.

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
