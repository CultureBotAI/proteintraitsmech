# Cycle 5 Stage 4 — Record & Cohort Review Report (`mech-goal-sequence-20261019`)

## 1. Executive Summary & Scope

- **Workflow Run / Cycle / Stage**: `mech-goal-sequence-20261019` / Cycle `5` / Stage `4` (`record_review`)
- **Evaluated Git Revision**: `568e78869fb08b86849d13f6a23b3a32ec27cd08` (`origin/main` after Cycle 5 Stage 3 PR `#1228`)
- **Previous Stage 5 Remediation Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000004/stage-05/revision-0001/evidence.yaml` (`sha256: 4ed8158706ad65bd802596086d51931750fb470b2c580228bc3224d5f16b70b7`)
- **Latest Tracked Workflow Index**: `reviews/workflow/latest.yaml` (`sha256: 173e1bd2757e0c2af19741626b8de394872407a6747dfb15325e26ff72072d16`; latest verified closure entry `reviews/workflow/mech-goal-sequence-20261019/cycle-000004/stage-06/revision-0001/evidence.yaml`, `sha256: 77a7b0bbf736852ba6ae2bb9ee656a5f5cfffbbbfddd691f10a91c1807378188`)
- **Repository-Local Skills Invoked**:
  - `.claude/skills/review-yaml-record/SKILL.md`:
    - `reviews/structured/20261104T072000Z-cdd-cd15854-record-review/review.yaml` (`sha256: 17af0701972082f308bd9fe27f189bc0b18df3f102f6b993dfa906db00b67db7`)
    - `reviews/structured/20261104T072000Z-cdd-cd15854-record-review/review.md` (`sha256: ef4efa590f8bb78396acc2f66c852eb42677f2d68fcac22df43e5251df49d245`)
  - `.claude/skills/review-yaml-category/SKILL.md`:
    - `reviews/structured/20261104T072100Z-cdd-cycle5-sibling-domain-cohort-review/review.yaml` (`sha256: 0d3c39044a19ff7d80cb1d4a97e17f09c691c2cce83599aa839a7a7b4b00d9db`)
    - `reviews/structured/20261104T072100Z-cdd-cycle5-sibling-domain-cohort-review/review.md` (`sha256: 57edd6ddf94d40e252c22e20b9719e5976d3e1136dc800428afcbe8bb898b5a3`)
- **Stage 4 Read-Only Guarantee**: Zero modifications were made to `data/traits/**/*.yaml`, seeder/repair scripts (`scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/seed_cdd.py`), or GitHub issues for record-review findings. All 6 newly identified open findings (`F31`–`F36`) are preserved with `status: open` and `disposition: action_required` (`carry_forward_ids: [F31, F32, F33, F34, F35, F36]`) for Cycle 5 Stage 5 grouped remediation.

### Frozen Inventory Summary (12 Eligible Records, 100% Coverage)

The Cycle 5 Stage 4 frozen inventory covers `population_size: 12` `SEQ_DOMAIN` (`SEQUENCE`) CDD records under `data/traits/sequence/domain/cdd/`, partitioned into two analytical sub-cohorts alongside 10 boundary-contrast context records (`CDD:cd15884`, `CDD:cd15885`, `CDD:cd15894`, `CDD:cd15895`, `CDD:cd17149`, `CDD:cd17152`, `CDD:cd18592`, `CDD:cd18593`, `CDD:cd18599`, `CDD:cd18601`):

1. **Sub-Cohort A — Cycle 4 Stage 5 Remediated Records (6 records: `CDD:cd17071`, `CDD:cd16113`, `CDD:cd15855`, `CDD:cd15889`, `CDD:cd15856`, `CDD:cd15887`)**:
   - Re-audited at `568e78869fb08b86849d13f6a23b3a32ec27cd08` to verify post-remediation stability of Cycle 4 findings `F25`–`F30` (remediated in PR `#1218` under issue `#1217`).
   - All 6 records pass strict LinkML schema validation, UniProt semantic grounding replay, and scientific prose review (`verdict: pass`, `native_verdict: PASS_WITH_NOTES`, `mapping_status: PROPOSED`; `F25`–`F30` verified `resolved`).
2. **Sub-Cohort B — Uncurated Paralog-Sibling & Tandem-Domain Clade Records (6 records: `CDD:cd15854`, `CDD:cd15888`, `CDD:cd15857`, `CDD:cd15886`, `CDD:cd18598`, `CDD:cd18605`)**:
   - Audited against their Cycle 2–4 remediated siblings (`CDD:cd15855`, `CDD:cd15889`, `CDD:cd15856`, `CDD:cd15887`, `CDD:cd15884`, `CDD:cd15885`, `CDD:cd15894`, `CDD:cd15895`, `CDD:cd18592`, `CDD:cd18593`, `CDD:cd18599`, `CDD:cd18601`) and primary literature (`PMID:16565078`, `PMID:7929585`, `PMID:9759094`, `PMID:16984901`).
   - All 6 records pass structural schema validation (`validate_strict.py` exit `0`) and UniProt grounding replay (`validate_uniprot_grounding.py` exit `0`), and represent distinct, non-synonymous class-level sequence domain profiles (`DISTINCT` / `KEEP_BOTH`).
   - All 6 records exhibit upstream CDD template prose defects (`verdict: needs_curation`, `native_verdict: NEEDS_CURATION`, `mapping_status: SEEDED`), recorded as stable open findings `F31`–`F36` (`major`, `status: open`).

---

## 2. Frozen Inventory, Input Hashes & Per-Record Verdicts

| Target ID | Label | Path | SHA-256 (`568e78869fb08b86849d13f6a23b3a32ec27cd08`) | `mapping_status` | Sub-Cohort | Native Verdict | Finding ID (`status`) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CDD:cd15854` | `SNARE_SNAP47C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml` | `fb37dabacc4f6c4f10e99ff638b2e76c36427c397ba7ee485d767b0ce06658a8` | `SEEDED` | Sub-Cohort B (SNAP47/SEC9 Qb/Qc SNARE) | `NEEDS_CURATION` | `F31` (`open`) |
| `CDD:cd15888` | `SNARE_SNAP47N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap47-n-terminal-snare-motif-of-snap47-a-me-cd15888.yaml` | `5efe3d638e0e2553214d45509996fd6ced8e0cf4d336eb1fee3988ab415a54db` | `SEEDED` | Sub-Cohort B (SNAP47/SEC9 Qb/Qc SNARE) | `NEEDS_CURATION` | `F32` (`open`) |
| `CDD:cd15857` | `SNARE_SEC9C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-sec9-c-terminal-snare-motif-of-fungal-sec9-a-cd15857.yaml` | `69d841bb6da236a30c02b81fbf0708146b3990591a3a41741a3cab2a248ca9c2` | `SEEDED` | Sub-Cohort B (SNAP47/SEC9 Qb/Qc SNARE) | `NEEDS_CURATION` | `F33` (`open`) |
| `CDD:cd15886` | `SNARE_SEC9N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-sec9-n-terminal-snare-motif-of-fungal-sec9-a-cd15886.yaml` | `5fa48242c7a2fd0003ebdd908526675e43c8c3539430e142a77c257cd82e7bb1` | `SEEDED` | Sub-Cohort B (SNAP47/SEC9 Qb/Qc SNARE) | `NEEDS_CURATION` | `F34` (`open`) |
| `CDD:cd18598` | `ABC_6TM_MRP7_D1_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18598.yaml` | `1dfa8217dad328d5dce76325c19c8068f57f254be6c7d32f3e3d47c6e8c26857` | `SEEDED` | Sub-Cohort B (ABCC MRP7/ABCC10 6TM) | `NEEDS_CURATION` | `F35` (`open`) |
| `CDD:cd18605` | `ABC_6TM_MRP7_D2_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18605.yaml` | `b3b65c3771652b48ea340b2dcb16a69228a1e5994d97b8c5044fb21412b34486` | `SEEDED` | Sub-Cohort B (ABCC MRP7/ABCC10 6TM) | `NEEDS_CURATION` | `F36` (`open`) |
| `CDD:cd17071` | `DCX1_DCDC2_like` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml` | `1aff2abcd815c6155a36d63abf731f22dc6644f6f673e5286f407d0476f35266` | `PROPOSED` | Sub-Cohort A (Cycle 4 G5 Remediated) | `PASS_WITH_NOTES` | `F25` (`resolved`) |
| `CDD:cd16113` | `DCX2_DCDC2_like` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml` | `2ddc254725899c6217899f51342f7d9b86610b95d0c2a3df0dd2943d715f7a4b` | `PROPOSED` | Sub-Cohort A (Cycle 4 G5 Remediated) | `PASS_WITH_NOTES` | `F26` (`resolved`) |
| `CDD:cd15855` | `SNARE_SNAP25C_23C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml` | `fd7dc3af4c9120523b0d00017a4c8b631bcd635468f031a23fc9ef480646ab06` | `PROPOSED` | Sub-Cohort A (Cycle 4 G5 Remediated) | `PASS_WITH_NOTES` | `F27` (`resolved`) |
| `CDD:cd15889` | `SNARE_SNAP25N_23N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml` | `e01a1f77672ae59b19218bc22b8d7970c2cc3bc2517b6bad56e5ed3c19453b4a` | `PROPOSED` | Sub-Cohort A (Cycle 4 G5 Remediated) | `PASS_WITH_NOTES` | `F28` (`resolved`) |
| `CDD:cd15856` | `SNARE_SNAP29C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml` | `c5c11e86520d19d5bd1fccc934f8d80f4fa927e64cbd53e8d0f8e3ffa8315c0a` | `PROPOSED` | Sub-Cohort A (Cycle 4 G5 Remediated) | `PASS_WITH_NOTES` | `F29` (`resolved`) |
| `CDD:cd15887` | `SNARE_SNAP29N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml` | `5fb03c07b2e0d6dd1bea53f4c87b478dd9021fb9a970f64876c5d3a26e4519a4` | `PROPOSED` | Sub-Cohort A (Cycle 4 G5 Remediated) | `PASS_WITH_NOTES` | `F30` (`resolved`) |

### Boundary-Contrast Context Inputs & Writer Ownership Hashes

| Context Path | SHA-256 (`568e78869fb08b86849d13f6a23b3a32ec27cd08`) | Role |
| --- | --- | --- |
| `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml` | `e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510` | Cycle 3 G4 remediated `SNARE_SNAP23C` sibling |
| `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml` | `78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b` | Cycle 1/2 G1 remediated `SNARE_SNAP25C` sibling |
| `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml` | `d11a67560ebb84bf867f67027f23109a5631b72953aa870075b96116cd599368` | Cycle 1/2 G1 remediated `SNARE_SNAP25N` sibling |
| `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml` | `5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b` | Cycle 3 G4 remediated `SNARE_SNAP23N` sibling |
| `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml` | `47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5` | Cycle 2 G2 remediated `DCX1_DCDC2` sibling |
| `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml` | `082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c` | Cycle 3 G4 remediated `DCX2_DCDC2` sibling |
| `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml` | `fad0b6039c5386b3caf40fc650099ec7bfd126ff7854d42aeb805708a18c3f9a` | Cycle 2 G3 remediated `ABC_6TM_MRP5_8_9_D1` sibling |
| `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml` | `5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb` | Cycle 2 G3 remediated `ABC_6TM_MRP4_D1_like` sibling |
| `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml` | `ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585` | Cycle 3 G4 remediated `ABC_6TM_MRP5_8_9_D2` sibling |
| `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml` | `d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099` | Cycle 3 G4 remediated `ABC_6TM_MRP4_D2_like` sibling |
| `scripts/cdd_errata.py` | `5528121218bde822769aebbc1a886200dcb6841087d4f445e757624f18cbdb6d` | Canonical accession-keyed CDD source-definition errata table |
| `scripts/repair_cdd_errata.py` | `9af19aa9a592e7c34272db5bbe58b5aa5d7e8bbca8b299fd10945d1caeb07c0c` | Registered in-place CDD errata repair writer |
| `scripts/seed_cdd.py` | `4fd337316239794623aaa2ad8afed44bb96ead33a1b387921272f26f8731365a` | Maintained CDD seeder transform wired to `cdd_errata` |
| `scripts/record_io.py` | `ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf` | Guarded validated record writer |
| `src/proteintraitsmech/schema/proteintraitsmech.yaml` | `7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418` | Authoritative LinkML schema |

---

## 3. Diagnostic Validation Harness Results

All required diagnostic checks were executed against the 12 target records at `568e78869fb08b86849d13f6a23b3a32ec27cd08`:

1. **Strict LinkML Schema & OAK Binding Validation**:
   - Command: `.venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv <12 target files>`
   - Exit code: `0` (`Files scanned: 12`, `Files with ERROR: 0`, `Total ERROR rows: 0`, `Total WARN rows: 0`).
2. **Release-Pinned UniProt Grounding & Binding Replay**:
   - Command: `.venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_failures.tsv <12 target files>`
   - Exit code: `0` (`Files scanned: 12`, `Registry proteins: 14024`, `Source evidence objects: 24026`, `Qualified record bindings: 24026`, `UniProt membership objects: 431`, `Semantic findings: 0`).
3. **Causal-Graph Structural & Semantic Audit**:
   - Command: `.venv/bin/python scripts/audit_causal_graphs.py <12 target files>`
   - Exit code: `0` (`Records scanned: 12`, `Records with causal_graphs: 0`, `Errors: 0`, `Warnings: 0`).
4. **Writer-Path & Curation-Bypass Audit**:
   - Command: `.venv/bin/python scripts/audit_writers.py`
   - Exit code: `0` (`621` scripts examined: `52` seeders, `9` registered editors, `2` transactional promoters, `52` declared bypasses; `OK: all record writers route through record_io.py or a registered editor/bypass`).
5. **Curation History Validation**:
   - Command: `.venv/bin/python -c "import glob, subprocess, sys; files = sorted(glob.glob('history/**/*.yaml', recursive=True)); ..."`
   - Exit code: `0` (`Validated 26 history files`).
6. **Native Structured Review Contract Check**:
   - Command: `.venv/bin/pytest -q tests/test_record_review_contract.py`
   - Exit code: `0` (`4 passed`; all persisted structured review bundles in `reviews/structured/` validate against `record_review.yaml` with byte-identical rendered `review.md`).

---

## 4. Detailed Findings (`F25`–`F36`)

### 4.1 Verified Resolved Findings Carried Forward from Cycle 4 (`F25`–`F30`)

| Finding ID | Key | Target Record | Severity | Status | Verification Summary at `568e78869fb08b86849d13f6a23b3a32ec27cd08` |
| --- | --- | --- | --- | --- | --- |
| `F25` | `cdd-cd17071-dcx1-dcdc2-like-typo-and-ubiquitin-modifier-digression` | `CDD:cd17071` (`DCX1_DCDC2_like`) | `minor` | `resolved` | Verified resolved by PR `#1218` (`#1217`): corrected `Dublecortin-like` to `Doublecortin-like`, replaced off-target ubiquitin protein-modifier digression with tandem DCX ubiquitin-like beta-grasp repeat description, added `PMID:16278295` evidence, and advanced `mapping_status` to `PROPOSED`. |
| `F26` | `cdd-cd16113-dcx2-dcdc2-like-ubiquitin-modifier-digression` | `CDD:cd16113` (`DCX2_DCDC2_like`) | `minor` | `resolved` | Verified resolved by PR `#1218` (`#1217`): replaced off-target ubiquitin protein-modifier digression with tandem DCX ubiquitin-like beta-grasp repeat description, added `PMID:16278295` evidence, and advanced `mapping_status` to `PROPOSED`. |
| `F27` | `cdd-cd15855-snap25c-23c-transmembrane-domain-overclaim` | `CDD:cd15855` (`SNARE_SNAP25C_23C`) | `major` | `resolved` | Verified resolved by PR `#1218` (`#1217`): false Qb/Qc SNARE transmembrane-domain claim replaced with accurate palmitoylated central inter-motif linker membrane-anchoring prose, added `PMID:9759094` evidence, and advanced `mapping_status` to `PROPOSED`. |
| `F28` | `cdd-cd15889-snap25n-23n-transmembrane-domain-overclaim` | `CDD:cd15889` (`SNARE_SNAP25N_23N`) | `major` | `resolved` | Verified resolved by PR `#1218` (`#1217`): false Qb/Qc SNARE transmembrane-domain claim replaced with accurate palmitoylated central inter-motif linker membrane-anchoring prose, added `PMID:9759094` evidence, and advanced `mapping_status` to `PROPOSED`. |
| `F29` | `cdd-cd15856-snap29c-transmembrane-domain-overclaim` | `CDD:cd15856` (`SNARE_SNAP29C`) | `major` | `resolved` | Verified resolved by PR `#1218` (`#1217`): false Qb/Qc SNARE transmembrane-domain claim replaced with accurate SNAP29 cytosolic/membrane-associated prose, added `PMID:9736707` evidence, and advanced `mapping_status` to `PROPOSED`. |
| `F30` | `cdd-cd15887-snap29n-transmembrane-domain-overclaim` | `CDD:cd15887` (`SNARE_SNAP29N`) | `major` | `resolved` | Verified resolved by PR `#1218` (`#1217`): false Qb/Qc SNARE transmembrane-domain claim replaced with accurate SNAP29 cytosolic/membrane-associated prose, added `PMID:9736707` evidence, and advanced `mapping_status` to `PROPOSED`. |

### 4.2 Open Findings Preserved for Cycle 5 Stage 5 Grouped Remediation (`F31`–`F36`)

#### Finding `F31` — `cdd-cd15854-snap47c-transmembrane-domain-overclaim` (`CDD:cd15854`, `major`, `open`)
- **Record**: `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml` (`CDD:cd15854`, `SNARE_SNAP47C`, `sha256: fb37dabacc4f6c4f10e99ff638b2e76c36427c397ba7ee485d767b0ce06658a8`)
- **Category**: `claim_scope` (`mechanism` / `evidence`)
- **Scientific Defect**: The upstream CDD-seeded `definition` states: *"Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain."* Tandem Qb/Qc SNAREs (the SNAP-25 family: SNAP25, SNAP23, SNAP29, SNAP47, and fungal Sec9p/Spo20p) do not possess a transmembrane domain (`PMID:9759094`), and SNAP47 (`UniProtKB:Q6RHT0` in *Rattus norvegicus*, `UniProtKB:Q8R570` in *Mus musculus*) specifically lacks both a transmembrane domain and the palmitoylated cysteine cluster found in SNAP25/SNAP23 (`PMID:16565078`). In addition, `CDD:cd15854` lacks a literature `evidence` block.
- **Remediation Target**: Add `cd15854` to `CDD_DEFINITION_ERRATA` in `scripts/cdd_errata.py` and `CDD_ERRATA_EVIDENCE` in `scripts/repair_cdd_errata.py` (`PMID:16565078`, `PMID:9759094`) in Cycle 5 Stage 5.

#### Finding `F32` — `cdd-cd15888-snap47n-transmembrane-domain-overclaim` (`CDD:cd15888`, `major`, `open`)
- **Record**: `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap47-n-terminal-snare-motif-of-snap47-a-me-cd15888.yaml` (`CDD:cd15888`, `SNARE_SNAP47N`, `sha256: 5efe3d638e0e2553214d45509996fd6ced8e0cf4d336eb1fee3988ab415a54db`)
- **Category**: `claim_scope` (`mechanism` / `evidence`)
- **Scientific Defect**: Identical upstream CDD Qb/Qc SNARE template overclaim on the N-terminal Qb SNARE motif profile of SNAP47 (*"Qb/Qc SNAREs consist of 2 coiled-coil helices ... and a transmembrane domain"*), plus missing literature `evidence` (`PMID:16565078`, `PMID:9759094`).
- **Remediation Target**: Add `cd15888` to `CDD_DEFINITION_ERRATA` in `scripts/cdd_errata.py` and `CDD_ERRATA_EVIDENCE` in `scripts/repair_cdd_errata.py` in Cycle 5 Stage 5.

#### Finding `F33` — `cdd-cd15857-sec9c-transmembrane-domain-overclaim` (`CDD:cd15857`, `major`, `open`)
- **Record**: `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-sec9-c-terminal-snare-motif-of-fungal-sec9-a-cd15857.yaml` (`CDD:cd15857`, `SNARE_SEC9C`, `sha256: 69d841bb6da236a30c02b81fbf0708146b3990591a3a41741a3cab2a248ca9c2`)
- **Category**: `claim_scope` (`mechanism` / `evidence`)
- **Scientific Defect**: The upstream CDD-seeded `definition` of the C-terminal Qc SNARE motif of fungal Sec9 (`SNARE_SEC9C`; carriers `UniProtKB:Q7S4P6`, `UniProtKB:Q5B5C7`, `UniProtKB:O74423`) asserts that *"Qb/Qc SNAREs consist of 2 coiled-coil helices ... and a transmembrane domain."* Fungal Sec9p (`PMID:7929585`) is a hydrophilic peripheral plasma-membrane SNAP-25 homolog lacking any transmembrane domain (`PMID:9759094`), and `CDD:cd15857` lacks a literature `evidence` block.
- **Remediation Target**: Add `cd15857` to `CDD_DEFINITION_ERRATA` in `scripts/cdd_errata.py` and `CDD_ERRATA_EVIDENCE` in `scripts/repair_cdd_errata.py` (`PMID:7929585`, `PMID:9759094`) in Cycle 5 Stage 5.

#### Finding `F34` — `cdd-cd15886-sec9n-transmembrane-domain-overclaim` (`CDD:cd15886`, `major`, `open`)
- **Record**: `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-sec9-n-terminal-snare-motif-of-fungal-sec9-a-cd15886.yaml` (`CDD:cd15886`, `SNARE_SEC9N`, `sha256: 5fa48242c7a2fd0003ebdd908526675e43c8c3539430e142a77c257cd82e7bb1`)
- **Category**: `claim_scope` (`mechanism` / `evidence`)
- **Scientific Defect**: Identical upstream CDD Qb/Qc SNARE template overclaim on the N-terminal Qb SNARE motif profile of fungal Sec9 (`SNARE_SEC9N`; *"Qb/Qc SNAREs consist of 2 coiled-coil helices ... and a transmembrane domain"*), plus missing literature `evidence` (`PMID:7929585`, `PMID:9759094`).
- **Remediation Target**: Add `cd15886` to `CDD_DEFINITION_ERRATA` in `scripts/cdd_errata.py` and `CDD_ERRATA_EVIDENCE` in `scripts/repair_cdd_errata.py` in Cycle 5 Stage 5.

#### Finding `F35` — `cdd-cd18598-mrp7-d1-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` (`CDD:cd18598`, `major`, `open`)
- **Record**: `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18598.yaml` (`CDD:cd18598`, `ABC_6TM_MRP7_D1_like`, `sha256: 1dfa8217dad328d5dce76325c19c8068f57f254be6c7d32f3e3d47c6e8c26857`)
- **Category**: `claim_scope` (`ontology_grounding` / `evidence`)
- **Scientific Defect**: The upstream CDD-seeded `definition` of `CDD:cd18598` (N-terminal 6TM domain TMD1 of MRP7/ABCC10; carrier *Mus musculus* Abcc10 `UniProtKB:Q8R4P9`) states: *"In humans, there are 13 ABCC proteins, nine of which belong to the MRP family (MRPs 1-9, or ABCC1-6, ABCC7 and ABCC10-12). The MRPs play roles in multidrug resistance (MDR) in tumor cells bydecreasing the intracellular concentration of toxic compounds through stimulating the efflux of anticancer drugs out of cancer cells."* As previously established for sibling ABCC 6TM profiles `cd18592`, `cd18593`, `cd18599`, and `cd18601` in Cycles 2–3 (`#1188`, `#1210`), `ABCC7` is `CFTR` (cystic fibrosis transmembrane conductance regulator, an ATP-gated chloride channel rather than an MRP), whereas the nine human MRPs are `MRP1`–`MRP9` (`ABCC1`–`ABCC6` and `ABCC10`–`ABCC12`, with `MRP7` = `ABCC10`; `PMID:16984901`); furthermore, not all nine MRPs mediate tumor multidrug resistance (and the sentence contains the upstream typo `bydecreasing`). `CDD:cd18598` also lacks a literature `evidence` block.
- **Remediation Target**: Add `cd18598` to `CDD_DEFINITION_ERRATA` in `scripts/cdd_errata.py` and `CDD_ERRATA_EVIDENCE` in `scripts/repair_cdd_errata.py` (`PMID:16984901`) in Cycle 5 Stage 5.

#### Finding `F36` — `cdd-cd18605-mrp7-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` (`CDD:cd18605`, `major`, `open`)
- **Record**: `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18605.yaml` (`CDD:cd18605`, `ABC_6TM_MRP7_D2_like`, `sha256: b3b65c3771652b48ea340b2dcb16a69228a1e5994d97b8c5044fb21412b34486`)
- **Category**: `claim_scope` (`ontology_grounding` / `evidence`)
- **Scientific Defect**: Identical upstream CDD ABCC template defect on the C-terminal 6TM domain TMD2 of MRP7/ABCC10 (`ABC_6TM_MRP7_D2_like`, carrier *Mus musculus* Abcc10 `UniProtKB:Q8R4P9`): misassigns `MRP1`–`MRP9` to `ABCC1-6, ABCC7 and ABCC10-12` (`ABCC7` is `CFTR`; `MRP7` is `ABCC10`), overclaims tumor MDR efflux across all nine MRPs (`bydecreasing`), and lacks a literature `evidence` block (`PMID:16984901`).
- **Remediation Target**: Add `cd18605` to `CDD_DEFINITION_ERRATA` in `scripts/cdd_errata.py` and `CDD_ERRATA_EVIDENCE` in `scripts/repair_cdd_errata.py` (`PMID:16984901`) in Cycle 5 Stage 5.

---

## 5. Boundary & Cohort Lumping/Splitting Matrix

All 12 target records and 10 boundary-contrast context records represent distinct class-level CDD sequence domain profiles (`DISTINCT` / `KEEP_BOTH`, 0 merge candidates):

1. **Qb/Qc SNARE Tandem-Motif & Paralog Subfamily Matrix**:
   - **Tandem domain boundary (N-terminal Qb vs C-terminal Qc)**: `CDD:cd15888` (`SNARE_SNAP47N`, Qb) vs `CDD:cd15854` (`SNARE_SNAP47C`, Qc); `CDD:cd15886` (`SNARE_SEC9N`, Qb) vs `CDD:cd15857` (`SNARE_SEC9C`, Qc); `CDD:cd15889` (`SNARE_SNAP25N_23N`, Qb) vs `CDD:cd15855` (`SNARE_SNAP25C_23C`, Qc); `CDD:cd15887` (`SNARE_SNAP29N`, Qb) vs `CDD:cd15856` (`SNARE_SNAP29C`, Qc). Each pair models non-overlapping N-terminal and C-terminal coiled-coil SNARE motifs on the same tandem Qb/Qc SNARE polypeptide (`DISTINCT`).
   - **Paralog subfamily boundary**: `SNAP47` (`cd15888`/`cd15854`, parent `CDD:cl22856`), fungal `Sec9` (`cd15886`/`cd15857`, parent `CDD:cl22856`), `SNAP25/SNAP23` clade (`cd15889`/`cd15855` with child profiles `cd15894`/`cd15884` and `cd15895`/`cd15885`), and `SNAP29` (`cd15887`/`cd15856`, parent `CDD:cl22856`) model non-equivalent phylogenetic clades with distinct domain architectures and membrane-association mechanisms (`DISTINCT`).
2. **ABCC MRP7/ABCC10 6TM Domain Matrix**:
   - **Tandem domain boundary (TMD1 vs TMD2)**: `CDD:cd18598` (`ABC_6TM_MRP7_D1_like`, *Mus musculus* Abcc10 `UniProtKB:Q8R4P9` aa `221-518`) vs `CDD:cd18605` (`ABC_6TM_MRP7_D2_like`, *Mus musculus* Abcc10 `UniProtKB:Q8R4P9` aa `855-1143`) model non-overlapping N-terminal and C-terminal six-transmembrane helical domains under `CDD:cl00249` (`DISTINCT`).
   - **Paralog subfamily boundary**: `MRP7_D1_like` (`cd18598`) and `MRP7_D2_like` (`cd18605`) are sibling models to `MRP5_8_9_D1` (`cd18592`), `MRP4_D1_like` (`cd18593`), `MRP5_8_9_D2` (`cd18599`), and `MRP4_D2_like` (`cd18601`) under `CDD:cl00249` (`DISTINCT`).
3. **Doublecortin Tandem-Domain Matrix (Sub-Cohort A Verification)**:
   - `CDD:cd17071` (`DCX1_DCDC2_like`, N-terminal DCX1) vs `CDD:cd16113` (`DCX2_DCDC2_like`, C-terminal DCX2) and child profiles `CDD:cd17149` (`DCX1_DCDC2`) / `CDD:cd17152` (`DCX2_DCDC2`) under `CDD:cl28922` (`DISTINCT`).

---

## 6. Limitations, Provenance & Stage 5 Handoff

- **Limitations**:
  1. Stage 4 is strictly read-only on `data/traits/`; all 6 newly identified open findings (`F31`–`F36`) are preserved as `status: open` in `review_findings.yaml` and `evidence.yaml` for Cycle 5 Stage 5 grouped remediation.
  2. None of the 6 Sub-Cohort B records (`CDD:cd15854`, `CDD:cd15888`, `CDD:cd15857`, `CDD:cd15886`, `CDD:cd18598`, `CDD:cd18605`) have a `qualified_record_bindings` entry in the release-pinned UniProt grounding registry (`data/grounding/uniprot_protein_registry.yaml`); their `canonical_examples` remain unpromoted CDD seed annotations until upstream InterPro/CDD member-database grounding coverage expands.
  3. All 12 target records are sequence-domain (`SEQ_DOMAIN`) profiles without residue-level catalytic mechanisms in M-CSA or experimental ligand-binding coordinates; `causal_graphs` is legitimately unpopulated (`0` records).
- **Stage 5 Handoff**:
  - Carry-forward open findings: `F31`, `F32`, `F33`, `F34`, `F35`, `F36` (all owned by `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py`).
  - Infrastructure tasks logged to `INFRA_TASKS.md`: `0` (existing `scripts/cdd_errata.py` + `scripts/repair_cdd_errata.py` architecture handles all 6 open findings cleanly without infrastructure changes).
