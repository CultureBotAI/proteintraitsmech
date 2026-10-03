# YAML Record Review: 7tmA_UII-R

- Repository: CultureBotAI/proteintraitsmech, local base `f7364a8495612517dc3887ff2d73a34f14603fdc`.
- Record: `data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml`.
- Started UTC: 2026-10-03T17:52:11Z.
- Finished UTC: 2026-10-03T17:58:30Z.
- Verdict: **needs curation** — three major findings and one minor provenance gap; no schema blocker. This is a read-only review, not promotion approval.

## Target

The complete YAML denotes `CDD:cd14999`, label `7tmA_UII-R`, a `ProteinTraitRecord` with axis `SEQUENCE`, category `SEQ_DOMAIN`, term kind `CLASS`, status `SEEDED`, and NCBI CDD provenance. Its SHA-256 is `29cb639a3bbf2158faa5680b179a1d1e4c6c392928321359db55344eb23e5df5`.

This is a source-seeded, subsequently example-enriched record, not a rendered page. `scripts/seed_cdd.py` owns the original source transform; it reads the CDD abstract and preserves existing files unless forced. `download.yaml` identifies its CDD source and US Government public-domain disposition. A reviewed correction belongs in this record through a registered text-preserving editor, with explicit curator provenance; never alter a raw source cache to conceal a disagreement.

## Validation

Executed against the unchanged target:

| Check | Result |
| --- | --- |
| `UV_NO_SYNC=1 just validate <record>` | One file, zero strict errors. |
| `UV_NO_SYNC=1 just validate-all <record>` | One file, zero strict errors and zero semantic findings; 12,462 durable protein references, 20,617 evidence objects and matching bindings loaded. This is migration-safe validation, not qualification of legacy examples. |
| `UV_NO_SYNC=1 just validate-reference <record>` | No issues; open-mode LinkML diagnostic only. |
| `UV_NO_SYNC=1 just audit-graphs <record>` | Zero graphs, errors or warnings; does not prove the prose mechanism. |
| `UV_NO_SYNC=1 just check-grounding-registries` | Both sharded registries structurally valid, 20,617 rows each, equal key sets. |
| `UV_NO_SYNC=1 just validate-history` | Whole history tree: no issues. No history or curation event added. |

Initial registry/history attempts could not read the sandboxed uv dependency cache; authorized read-only reruns succeeded. `--require-qualified` was not run: both examples visibly lack qualification fields, so the migration-safe success cannot establish completion. Full-corpus validation, OAK external-term checks, browser generation and full tests were not run for this read-only review. The internal-label gate concerns `proteintraitsmech:` identities and is not an external-accession verifier for these CDD/UniProt IDs. Source-native checks below provide the relevant identity evidence.

## Identity and Grounding

The ID, label, axis and category agree with the [CDD sequence-profile model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cd14999). Its live page identifies PSSM 320130, updated 2021-10-25, and superfamily `cl28897`. The complete local parent file, `data/traits/sequence/homologous_superfamily/cdd/seven-transmembrane-g-protein-coupled-receptor-superfamily-chemorecept-cl28897.yaml`, exists and bears that ID. The source confirms superfamily membership; this is not exact equivalence. The parent's nematode-centric prose is outside this single-record verdict and must not narrow the human receptor to nematode chemoreception.

Official exact-accession UniProt JSON was inspected at release `2026_03`:

| Protein | Gene / identity | Length | CDD identity |
| --- | --- | ---: | --- |
| [Q9UKP6](https://rest.uniprot.org/uniprotkb/Q9UKP6.json) | Human UTS2R, synonym GPR14, urotensin-2 receptor | 389 | cd14999 |
| [Q8VIH9](https://rest.uniprot.org/uniprotkb/Q8VIH9.json) | Mouse Uts2r/Gpr14, urotensin-2 receptor | 385 | cd14999 |
| [O43613](https://rest.uniprot.org/uniprotkb/O43613.json) | Human HCRTR1, orexin/hypocretin receptor type 1 | 425 | cd15208 |
| [O43614](https://rest.uniprot.org/uniprotkb/O43614.json) | Human HCRTR2, hypocretin receptor type 2 | 444 | cd15208 |

The distinct [CDD orexin-receptor model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cd15208) also includes O43613/O43614. Therefore the hypocretin alias in cd14999 conflates distinct receptor identities; common GPCR topology or calcium signaling does not make them synonyms.

The two stored exemplar identities and lengths are correct, but `reviewed: true` means Swiss-Prot review, not record-specific qualification. Both are `LEGACY_UNVERIFIED` by schema convention. The staged human occurrence is 53–326 on Q9UKP6, from pinned InterPro 110.0 in the canonical UniProt frame; the live CDD representative alignment independently displays those endpoints. The staging qualification is held for prose repair and is not installed. Its exact sequence checksum is `d087ceef1b9278da30c4e4aa15657f94a18bc54ec5dd93f52a9a349a2ce314a6`.

UniProt confirms the stored InterPro IPR017452, Pfam PF00001 and PROSITE PS00237/PS50262 example cross-references. [CATH 1.20.1070.10](https://www.cathdb.info/version/latest/superfamily/1.20.1070.10) resolves to the broad rhodopsin seven-helix superfamily; its historical assignment to these exact example sequences was not independently replayed. These are example classifications, not trait-level exact-equivalence claims.

## Evidence

The entire local definition faithfully repeats the inspected CDD abstract, including the error. Source fidelity establishes provenance, not scientific correctness.

- The urotensin ligand/GPR14 identity and calcium response are supported by Ames et al., [PMID 10499587, DOI 10.1038/45809](https://doi.org/10.1038/45809). The primary abstract was inspected through the Europe PMC core API. Short evidence excerpt: “the binding is functionally coupled to calcium mobilization.” Its vascular experiments concern isolated non-human-primate arteries and anesthetized non-human primates. An erratum is listed for Nature 402:898; its contents were not inspected.
- The class-wide, time-unbounded potency wording needs experimental scope. Douglas et al., [PMID 11078367, DOI 10.1097/00005344-200036051-00051](https://doi.org/10.1097/00005344-200036051-00051), report substantial species/anatomical dependence and describe human peptide as “inactive in mice” in their tested in-vitro vascular preparations. This does not mean mice lack the receptor, or that every mouse tissue is unresponsive.
- The PLC/contraction link has narrower primary support: [PMID 11020490, DOI 10.1016/S0014-2999(00)00672-5](https://doi.org/10.1016/S0014-2999(00)00672-5) studied isolated rabbit thoracic aorta. Inhibitor and phosphoinositide results support PLC involvement; the abstract infers Gq coupling rather than directly establishing every human G-protein subunit interaction.
- The inspected human UniProt FUNCTION annotation supports Gq/11–PLC–calcium signaling with cited experiments. The mouse annotation explicitly uses transfer by similarity. Neither is grounds for treating every class member, tissue, or downstream effect as experimentally tested.
- The fish neurosecretory history, non-homology to somatostatin/cortistatin, full expression-site list and broader endocrine/CNS implications were traced to CDD but not independently verified against each underlying primary study. Keep them source-attributed or remove them from a concise corrected definition pending targeted verification; do not present this review as a primary-literature audit of all those claims.

The IUPHAR UT and OX2 pages redirected to login in this pass. Search-index text was not used as inspected authoritative evidence. Direct UniProt JSON and CDD pages supplied the independent identity checks. PubMed page opens were uninformative/challenged; the three abstracts above were instead retrieved from the official Europe PMC API. No access restriction was bypassed.

## Completeness

The current goal is not satisfied for the human example: its ID is present but qualified sequence and occurrence annotations are not yet attached. No E. coli or yeast occurrence is established by this receptor review, and this is not a claim of absence in either species. The mouse example is outside the requested target taxa and must remain intact.

No causal graph, residue model, discussion, alternate definition or literature evidence list is required merely to fill optional fields. The full target contains none; no placeholder should be added for coverage. CDD's putative ligand-pocket features derive from other class-A receptor structures and are not direct experimental residue evidence for UTS2R.

Ignored-file-inclusive searches covered the target filename under `data/traits`, the CDD raw path, and `cd14999|hypocretin receptor` under `data/curation`, `research`, `scripts` and `history`. No matching maintained correction was found in those latter directories. `data/raw/cdd` itself is absent locally; live CDD was inspected instead. These bounded searches do not assert that no relevant evidence exists elsewhere. The ignored grounding staging and checkpoint do contain this hold.

## Findings

1. **Major — incorrect identity alias.** The definition equates the urotensin receptor with a hypocretin receptor. Independent accession/model evidence above disproves that equivalence. Owner: the target YAML's `definition`, changed only through a registered validated editor. Preserve a note that this corrects source text rather than silently claiming the revised text is verbatim CDD.
2. **Major — unqualified cross-species physiology.** The current potency/contraction narrative reads as a general mammalian property without experimental date, species or vascular-bed scope. Primary studies demonstrate important context dependence. Owner: the target definition and claim-specific evidence, not the protein-coordinate ledger. Restrict or remove the overgeneralization.
3. **Major for goal completion — target example remains unqualified.** Q9UKP6 is biologically appropriate, but its stored legacy metadata does not carry the pinned sequence or source-backed occurrence. Owner: the approved candidate→resolve→review→promote route, with durable `data/grounding/` evidence and bindings; never a manual example edit. Fixing prose changes the preimage and requires re-resolution before any later promotion. This is not a strict-schema violation.
4. **Minor — source-version provenance gap.** The definition gives only `NCBI CDD`, with no preserved source-version citation on the record. A future correction should cite the stable model page, inspected metadata and independent evidence, while distinguishing curation from the original abstract. Owner: target provenance/evidence and an append-only curation event when an actual edit occurs.

No wrong accession, malformed YAML, broken parent reference or required-graph omission was found. The incorrect alias is localized to prose; the core ID and examples still identify the intended urotensin receptor class.

## Recommended Edits

1. Through a registered editor ending in `write_validated_record`, replace the false alias with a concise UTS2R/GPR14-specific definition and explicit evidence. Keep cd14999, label, axis/category, parent, existing example identities and source license. Do not rename the record to cd15208.
2. Scope any retained physiology to the cited experiments; do not turn a domain match into a universal vascular phenotype. Attribute synthesized text and leave agent curation `PROPOSED`, not human `REVIEWED`.
3. Append an LLM-assisted curation event and create history with `just new-history` only when the record is actually changed. Guard against a forced source reseed restoring the known error; raw CDD data remains immutable source evidence.
4. Re-resolve this record inside its legitimate bounded cohort after the preimage changes, repeat scientific adjudication and dry promotion, and obtain explicit promotion approval. The other 69 approved records in cohort 066 do not include this held record.

## Follow-up Checks

- After prose curation: scoped `just validate-all <record>`, manual comparison against exact source entries, writer tests/`just audit-writers`, and `just validate-history`.
- After authorized grounding: verify the exact Q9UKP6 sequence, UniProt release and 53–326 InterPro occurrence through semantic validation and binding checks. A whole-record `--require-qualified` test will still report an untouched legacy mouse example; report that residual honestly rather than counting a migration-safe pass as full qualification.
- Before any merge of changed trait data: repository-required full validation and relevant test/lint gates. No such edit or merge was performed by this review.
- Resolve the Ames erratum and independently verify any retained fish, tissue-expression, peptide-homology or detailed coupling claims that go beyond the evidence inspected here.

## Additional Notes

iModulonDB was not applicable to this vertebrate receptor-identity review; no transcriptomic module evidence was needed or used. Missing module coverage would not prove biological absence.

Exact-accession JSON response SHA-256 values at UniProt 2026_03: Q9UKP6 `3f64dcc677b3fef2511919b60d767f9fae506b350cb2a608eb25f5656c7e2581`; Q8VIH9 `a0a0f9f7605f6f263ac408edac6dae51d4507e33804c7832bc174f90f8843c15`; O43613 `212c097de381f89b613543680c644ba81b0866e4033e43b8e3eb120c5d20ccf7`; O43614 `4fa5326bcf4faf377702baef06068dfab998ea9df44e12c68c6131087679abc9`. Responses were parsed read-only; these hashes do not claim a new raw-response archive was saved.

No trait, registry, review status, history entry or GitHub object was changed. This report is a new untracked local review artifact (the single-record report path is not gitignored), not a published correction or evidence of species-wide completeness.
