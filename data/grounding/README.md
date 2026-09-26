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
- `iedb_peptide_source_snapshot.json` contains native IEDB rows, the exact export
  and fetch-receipt checksums, complete ProteinReferences, and the meaning of each
  corresponding peptide trait. The provider checks an independently reviewed file
  checksum fixed in code. It qualifies a `PATTERN_MATCH` only for an unmodified
  peptide with one literal match on its exact existing parent protein. Overlapping
  repeats, changed parents, and conflicting native coordinates are rejected. The
  claim is limited to peptide identity and position on that sequence. Source and
  license metadata remain in the snapshot and trait records.
- `interpro_native/<sha256>.json` retains complete native InterPro response bodies,
  header receipts, acquisition plans, protein references and corresponding record
  meanings. The full snapshot and each acquisition have independently registered
  checksums. Each native location produces one occurrence and evidence row; a
  discontinuous location retains all its fragments in that occurrence. Validation
  requires the entire location set and rejects omitted or duplicate members.
- `mcsa_native_source_snapshot.json` retains the complete captured M-CSA entry
  set, acquisition manifest, complete ProteinReferences, and every non-example
  field of each corresponding trait record. Its independently reviewed file
  checksum is fixed in the provider. `SOURCE_NATIVE_COORDINATES` requires the
  complete catalytic residue set from native `residue_sequences` rows marked
  `is_reference`, mapped to the exact existing UniProt accession. Every residue
  identity and position must agree with that release-pinned sequence, including
  selenocysteine. Discontinuous positions stay explicit. PDB chain numbering,
  offsets, homologues, and partial sites cannot satisfy this contract. The native
  source is attributed to [M-CSA, Thornton group, EMBL-EBI](https://www.ebi.ac.uk/thornton-srv/m-csa/)
  under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); source and
  license metadata remain in the snapshot and trait records.
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

Native InterPro acquisition uses `just fetch-interpro-native` with `--registry`,
`--protein UniProtKB:<accession>`, `--expect-release`, `--expect-minor` and an
`--out data/raw/interpro_native/<run>/<accession>` directory. Save the dry-run JSON
plan and repeat with `--request-plan <plan.json> --apply` to capture that exact
reference. The route saves complete pagination and each response's body and
release headers, then replays the saved files before publishing `bundle.json`.
It preserves independent match locations and the fragments within each location.
Failed runs retain partial files with `failure.json`; use a new output directory
for a retry. These bundles do not qualify coordinates.

Prepare an independently registered portable snapshot with
`just prepare-interpro-native-source <snapshot.json>`, inspect the dry run, then
add `--apply`. Preparation installs only immutable source input. Resolve with
`--providers protein-registry,interpro-native`; each candidate identifies its
`native_source`, `native_location_set_sha256` and complete `native_locations`.
The resolver regenerates every occurrence and evidence row from the source.
Review all locations as one protein alternative, then use the central promoter.
The review table shows the grouped locations; separate evidence and record bindings
are written for every occurrence. Repeated promotion is idempotent, and incomplete
or conflicting sets fail before a record or registry write. Legacy flattened
InterPro locations retain their original restrictions.

Source registration does not approve a trait definition, biological scope or
publication license. Preserve member-database provenance and missing license
fields, complete source-specific review, and resolve release blockers before
publication.

To add coordinates to several proteins already listed on one trait, use the central
promoter's optional `--enrich-existing-examples` flag. Each approved protein must
already occur exactly once in the current record, and only one source alternative
may be approved for each trait/protein pair. Every alternative still needs an
explicit review decision. The default remains one approved alternative per trait.
Enrichment preserves example order and generic features, keeps the 1,000-approved-
candidate cap, and replays the same sequence, source, schema, evidence and record
checks before its transaction. It cannot append a new example protein.

Prepare the reviewed IEDB input with
`just prepare-iedb-peptide-source <snapshot.json>`; add `--apply` after inspecting the
dry run. Preparation creates no qualified evidence or coordinates. Resolve candidates
with `--providers protein-registry,iedb-peptide`, then use the same bounded review and
central promotion workflow as the other sources. Repeated preparation accepts only
identical bytes; a different native release requires review of its new fixed checksum.

Prepare the reviewed M-CSA input with
`just prepare-mcsa-native-source <snapshot.json>` and inspect the dry run before
adding `--apply`. Preparation installs only the immutable source input. Resolve
with `--providers protein-registry,mcsa-native`, review the complete native residue
set for each existing example, and use the central promoter. Promotion replays the
current full record and reference, rechecks the source bytes, and updates the
evidence and record bindings transactionally. Other M-CSA assertions retain their
existing provider requirements.

The durable protein registry can contain proteins pinned to different UniProt releases.
Execution contracts that require one release, including SFLD HMMER receipts, must receive
a release-specific staging registry through `--registry`. The eLife ingest preserves the
126 existing `2026_02` protein rows and adds 33 `2026_03` rows; it does not upgrade the
older references or relax the SFLD single-release check.

See [`research/uniprot-organism-protein-grounding-plan.md`](../../research/uniprot-organism-protein-grounding-plan.md)
for the state machine, evidence tiers, review protocol, and completion criteria.
